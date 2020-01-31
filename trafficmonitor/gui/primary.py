import re
import json
import datetime
from pathlib import Path
from uuid import uuid4

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt

from trafficmonitor.gui.secondary import Secondary
from trafficmonitor.gui.filter import Filter
from trafficmonitor.gui.replay import Replay

from trafficmonitor.mitm_proxy import MitmProxy
from trafficmonitor.database import MitmProxyDb
from trafficmonitor.http_requests import static_http_requests
from trafficmonitor.helper_functions import get_status_code_value, post_parser, put_parser, create_path, get_header_dict

from trafficmonitor.extenders.passiveheaderaudit.passiveheaderaudit import PassiveHeadersAudit
from trafficmonitor.extenders.passiveheaderaudit.reports import PassiveHeaderAuditReport


class Primary(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Traffic Monitor")
        self.image_path = str(Path(__file__).absolute().parent.parent / "images")
        self.setWindowIcon(QIcon(str(Path(self.image_path) / "logo.ico")))
        self.resize(1360, 768)

        # initialize values
        self.config_dict = create_path()
        self.filter_requests = {}
        self.secondary_form_data = {}
        self.saved_db_path = None
        self.current_db_path = None
        self.session_db = None
        self.proxy_ids = []
        self.execution_name = None

        # filter values
        self.filter_regular_exp = list()
        self.filter_values = dict()
        self.filter_methods = list()
        self.filter_responses = list()
        self.filter_hide_status_code = list()
        self.filter_hide_url = list()
        self.filter_start_datetime = ''
        self.filter_end_datetime = ''

        # change proxy settings
        # self.proxy = ProxySettings()

        # Create Instance of Mitm Proxy
        self.mitm_proxy = MitmProxy()

        # initialize all widgets
        self.tree_traffic_widget = QTreeWidget()
        self.tree_traffic_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_traffic_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.tree_traffic_widget.setFont(QFont("", ))
        self.text_request_widget = QTextEdit()
        # self.text_request_widget.setFont(QFont("", 6))
        self.text_response_widget = QTextEdit()
        # self.text_response_widget.setFont(QFont("", 6))

        # initialize menu
        menu_bar = self.menuBar()
        self.menu_file = menu_bar.addMenu("File")
        self.menu_edit = menu_bar.addMenu("Edit")
        self.menu_tools = menu_bar.addMenu("Tools")

        self.menu_capture_traffic = QAction("Capture Traffic", self)
        self.menu_open_db = QAction("Open", self)
        # self.menu_save_filtered_session = QAction("Save Filtered/All Request", self)
        self.menu_export_db_file = QAction("Db File", self)
        self.menu_export_txt_file = QAction("Text File", self)
        self.menu_export_json_file = QAction("Json File", self)
        # self.menu_export_headers = QAction("Headers", self)
        # self.menu_remove_sessions = QAction("Selected Sessions", self)
        # self.menu_remove_all_sessions = QAction("All Sessions", self)
        # self.menu_json_generator = QAction("Json Generator", self)
        self.menu_psv_header_adt = QAction("Passive Header Audit", self)

        # initialize toolbar
        self.tool_bar_start = QAction(QIcon(str(Path(self.image_path) / "start.png")), "Start", self)
        self.tool_bar_stop = QAction(QIcon(str(Path(self.image_path) / "stop.png")), "Stop", self)
        self.tool_bar_refresh = QAction(QIcon(str(Path(self.image_path) / "refresh.png")), "Refresh", self)
        self.tool_bar_filter = QAction(QIcon(str(Path(self.image_path) / "filter.png")), "Filter", self)

        # initialize menu and tool bar
        self.menu()
        self.tool()
        self.center()
        self.init_widgets()
        self.init_ui()
        self.init_signals()

    def menu(self):

        # sub menu items
        self.menu_file.addAction(self.menu_capture_traffic)
        self.menu_file.addAction(self.menu_open_db)
        # self.menu_file.addAction(self.menu_save_filtered_session)

        export = QMenu("Export", self)
        self.menu_edit.addMenu(export)

        export.addAction(self.menu_export_db_file)
        export.addAction(self.menu_export_txt_file)
        export.addAction(self.menu_export_json_file)
        # export.addAction(self.menu_export_headers)

        # remove = QMenu("Remove", self)
        # self.menu_edit.addMenu(remove)

        # remove.addAction(self.menu_remove_sessions)
        # remove.addAction(self.menu_remove_all_sessions)

        # self.menu_tools.addAction(self.menu_json_generator)
        self.menu_tools.addAction(self.menu_psv_header_adt)

    def tool(self):
        # tool bar
        tool_bar = QToolBar()
        tool_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        tool_bar.addAction(self.tool_bar_start)

        self.tool_bar_stop.setDisabled(True)
        tool_bar.addAction(self.tool_bar_stop)

        self.tool_bar_refresh.setDisabled(True)
        tool_bar.addAction(self.tool_bar_refresh)

        tool_bar.addAction(self.tool_bar_filter)

        self.addToolBar(Qt.LeftToolBarArea, tool_bar)

    def center(self):
        """Method to center the QMainWindow"""
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def init_widgets(self):
        self.tree_traffic_widget.setUniformRowHeights(True)
        self.tree_traffic_widget.setHeaderLabels(["SL No", "Datetime", "Host", "URL", "Status Code", "Method"])

    def init_ui(self):
        vertical_box = QVBoxLayout()
        grid_layout = QGridLayout()

        label_request = QLabel("Request")
        # label_request.setFont(QFont("", 8))

        label_response = QLabel("Response")
        # label_response.setFont(QFont("", 8))

        grid_layout.addWidget(label_request, 0, 0)
        grid_layout.addWidget(label_response, 0, 1)

        grid_layout.addWidget(self.text_request_widget, 1, 0)
        grid_layout.addWidget(self.text_response_widget, 1, 1)

        vertical_box.addWidget(self.tree_traffic_widget)
        vertical_box.addLayout(grid_layout)

        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(vertical_box)

        # self.show()

    def init_signals(self):
        # menu signals
        self.menu_capture_traffic.triggered.connect(self.start)
        self.menu_export_db_file.triggered.connect(lambda: self.export_db_file(self.proxy_ids))
        self.menu_export_txt_file.triggered.connect(lambda: self.export_text_file(self.proxy_ids))
        self.menu_export_json_file.triggered.connect(lambda: self.generate_json(self.proxy_ids))
        self.menu_open_db.triggered.connect(self.evt_menu_open)
        # self.menu_json_generator.triggered.connect(lambda: self.generate_json(self.proxy_ids))
        self.menu_psv_header_adt.triggered.connect(self.passive_header_audit)

        # tool bar signals
        self.tool_bar_start.triggered.connect(self.evt_tool_bar_start)
        self.tool_bar_stop.triggered.connect(self.evt_tool_bar_stop)
        self.tool_bar_filter.triggered.connect(self.evt_tool_bar_filter)
        self.tool_bar_refresh.triggered.connect(self.refresh)

        self.tree_traffic_widget.itemClicked.connect(self.display)
        self.tree_traffic_widget.customContextMenuRequested.connect(self.menu_context_tree)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            if not self.tool_bar_start.isEnabled():
                # stop mitm proxy process
                self.mitm_proxy.stop_proxy()

                # change default proxy settings
                # self.proxy.set_default_settings()

                if self.session_db not in [None, '']:
                    self.session_db.close_connection()
                    self.session_db = None
        else:
            event.ignore()

    def evt_tool_bar_start(self):
        self.start()

    def evt_tool_bar_stop(self):

        if not self.tool_bar_start.isEnabled():
            # stop mitm proxy process
            self.mitm_proxy.stop_proxy()

            # change default proxy settings
            # self.proxy.stop_proxy_address()

            # if self.session_db not in [None, '']:
            #     self.session_db.close_connection()
            #     self.session_db = None

        # disable start and activate the remaining toolbar
        self.tool_bar_start.setDisabled(False)
        self.tool_bar_stop.setDisabled(True)
        self.tool_bar_refresh.setDisabled(True)

        # disable all menu items
        self.menu_capture_traffic.setDisabled(False)
        self.menu_open_db.setDisabled(False)
        # self.menu_save_filtered_session.setDisabled(False)
        # self.menu_export_headers.setDisabled(False)
        self.menu_export_txt_file.setDisabled(False)
        self.menu_export_db_file.setDisabled(False)
        # self.menu_remove_sessions.setDisabled(False)
        # self.menu_remove_all_sessions.setDisabled(False)
        # self.menu_json_generator.setDisabled(False)
        self.menu_psv_header_adt.setDisabled(False)

    def evt_tool_bar_filter(self):
        filter_form = Filter()
        filter_form.exec_()
        self.filter_requests = filter_form.filter_dict
        self.filter_objects()
        self.refresh()

    def evt_menu_open(self):
        directory = self.config_dict
        filter = "db file (*.db)"

        self.saved_db_path = QFileDialog.getOpenFileName(self, "Open a file", directory=directory, filter=filter)[0]

        self.text_request_widget.clear()
        self.text_response_widget.clear()

        if len(self.saved_db_path) > 0:

            self.execution_name = str(self.saved_db_path).split('/')[-1].split('.')[0]

            if self.session_db not in [None, '']:
                self.session_db.close_connection()
                self.session_db = None

            self.tree_traffic_widget.clear()
            self.evt_tool_bar_stop()
            self.refresh()

        else:
            self.evt_tool_bar_stop()

    def start(self):
        secondary_form = Secondary(self)
        secondary_form.exec_()
        self.secondary_form_data = secondary_form.data
        if len(self.secondary_form_data) > 0:

            if self.session_db not in [None, '']:
                self.session_db.close_connection()
                self.session_db = None

            self.execution_name = self.secondary_form_data['EXECUTION_NAME']
            self.current_db_path = str(
                Path(f"{self.config_dict}/{self.secondary_form_data['EXECUTION_NAME']}.db")
            )

            self.tree_traffic_widget.clear()
            self.text_request_widget.clear()
            self.text_response_widget.clear()
            self.saved_db_path = None

            # disable start and activate the remaining toolbar
            self.tool_bar_start.setDisabled(True)
            self.tool_bar_stop.setDisabled(False)
            self.tool_bar_refresh.setDisabled(False)

            # disable all menu items
            self.menu_capture_traffic.setDisabled(True)
            self.menu_open_db.setDisabled(True)
            # self.menu_save_filtered_session.setDisabled(True)
            # self.menu_export_headers.setDisabled(True)
            self.menu_export_txt_file.setDisabled(True)
            self.menu_export_db_file.setDisabled(True)
            # self.menu_remove_sessions.setDisabled(True)
            # self.menu_remove_all_sessions.setDisabled(True)
            # self.menu_json_generator.setDisabled(True)
            self.menu_psv_header_adt.setDisabled(True)

            # self.proxy.set_settings()
            self.mitm_proxy.start_proxy(self.secondary_form_data)

        else:
            self.current_db_path = ''
            self.evt_tool_bar_stop()

    def filter_objects(self):
        self.filter_methods.clear()
        self.filter_responses.clear()
        self.filter_hide_status_code.clear()
        self.filter_hide_url = ''
        self.filter_start_datetime = ''
        self.filter_end_datetime = ''

        # code to filter responses
        if 'CSS_FILES' in self.filter_requests.keys():
            if self.filter_requests['CSS_FILES']:
                self.filter_responses.append(r"\.css")

        if 'IMAGE_FILE_EXTENSIONS' in self.filter_requests.keys():
            if self.filter_requests['IMAGE_FILE_EXTENSIONS']:
                self.filter_responses.append(
                    r"\.ai|\.bmp|\.gif|\.ico|\.jpeg|\.jpg|\.png|\.ps|\.psd|\.svg|\.tif|\.tiff"
                )

        if 'FONT_FILE_EXTENSIONS' in self.filter_requests.keys():
            if self.filter_requests['FONT_FILE_EXTENSIONS']:
                self.filter_responses.append(
                    r"\.fnt|\.fon|\.otf|\.ttf"
                )

        if 'JAVASCRIPT_FILES' in self.filter_requests.keys():
            if self.filter_requests['JAVASCRIPT_FILES']:
                self.filter_responses.append(
                    r"\.js"
                )

        # code to filter methods
        if 'GET' in self.filter_requests.keys():
            if self.filter_requests['GET']:
                self.filter_methods.append(r"GET")

        if 'POST' in self.filter_requests.keys():
            if self.filter_requests['POST']:
                self.filter_methods.append(r"POST")

        if 'PUT' in self.filter_requests.keys():
            if self.filter_requests['PUT']:
                self.filter_methods.append(r"PUT")

        if 'DELETE' in self.filter_requests.keys():
            if self.filter_requests['DELETE']:
                self.filter_methods.append(r"DELETE")

        if 'OPTIONS' in self.filter_requests.keys():
            if self.filter_requests['OPTIONS']:
                self.filter_methods.append(r"OPTIONS")

        if 'TRACE' in self.filter_requests.keys():
            if self.filter_requests['TRACE']:
                self.filter_methods.append(r"TRACE")

        if 'CONNECT' in self.filter_requests.keys():
            if self.filter_requests['CONNECT']:
                self.filter_methods.append(r"CONNECT")

        if 'HEAD' in self.filter_requests.keys():
            if self.filter_requests['HEAD']:
                self.filter_methods.append(r"HEAD")

        # filter status codes
        if 'FILTER_STATUS_CODES' in self.filter_requests.keys():
            if self.filter_requests['FILTER_STATUS_CODES'] != '':
                self.filter_hide_status_code = self.filter_requests['FILTER_STATUS_CODES'].split(";")

        # filter url
        if 'FILTER_URL' in self.filter_requests.keys():
            if self.filter_requests['FILTER_URL'] != '':
                self.filter_hide_url = self.filter_requests['FILTER_URL'].split(";")

        # filter start datetime
        if 'START_DATE_TIME' in self.filter_requests.keys():
            if self.filter_requests['START_DATE_TIME']:
                if 'START_DATE_TIME' != '':
                    self.filter_start_datetime = self.filter_requests['START_DATE_TIME']

        # filter end datetime
        if 'END_DATE_TIME' in self.filter_requests.keys():
            if self.filter_requests['END_DATE_TIME']:
                if 'END_DATE_TIME' != '':
                    self.filter_end_datetime = self.filter_requests['END_DATE_TIME']

    def check_filter_objects(self, data):
        # filter methods
        method_filtered_data = []

        if len(self.filter_methods) > 0:

            method_regex = re.compile("|".join(self.filter_methods))

            for d in data:
                if re.findall(method_regex, d[5]):
                    method_filtered_data.append(d)

            data.clear()
            data = method_filtered_data

        # filter status code
        status_code_filter_data = []

        if len(self.filter_hide_status_code) > 0:

            status_code_regex = re.compile("|".join(self.filter_hide_status_code))

            for d in data:
                if d[4] is None:
                    status_code_filter_data.append(d)
                else:
                    if re.findall(status_code_regex, d[4]):
                        status_code_filter_data.append(d)

            data.clear()
            data = status_code_filter_data

        # filter response
        response_filter_data = []

        if len(self.filter_responses) > 0:

            response_regex = re.compile("|".join(self.filter_responses))

            for d in data:
                if not re.findall(response_regex, d[3]):
                    response_filter_data.append(d)

            data.clear()
            data = response_filter_data

        # url filter data
        url_filter_data = []

        if len(self.filter_hide_url) > 0:
            url_regex = re.compile("|".join(self.filter_hide_url))

            for d in data:
                if re.findall(url_regex, d[3]):
                    url_filter_data.append(d)

            data.clear()
            data = url_filter_data

        return data

    def refresh(self):

        db_name_with_path = True

        if self.session_db in [None, '']:

            if self.saved_db_path is not None:
                db_name_with_path = self.saved_db_path
            elif self.current_db_path is not None:
                db_name_with_path = self.current_db_path
            else:
                db_name_with_path = False

            if db_name_with_path:
                self.session_db = MitmProxyDb(db_name_with_path)

        if db_name_with_path:

            if self.filter_start_datetime not in [None, ''] and self.filter_end_datetime not in [None, '']:
                refresh_data = self.session_db.refresh_data(
                    _from=self.filter_start_datetime, _to=self.filter_end_datetime
                )

            elif self.filter_start_datetime not in [None, '']:
                refresh_data = self.session_db.refresh_data(_from=self.filter_start_datetime)

            elif self.filter_end_datetime not in [None, '']:
                refresh_data = self.session_db.refresh_data(_to=self.filter_end_datetime)

            else:
                refresh_data = self.session_db.refresh_data()

            self.tree_traffic_widget.clear()

            if refresh_data not in [None, '']:

                filtered_data = self.check_filter_objects(refresh_data)

                self.proxy_ids = []

                progress = QProgressDialog("Loading Sessions...", "Abort", 0, len(filtered_data), self)
                progress.setWindowModality(Qt.WindowModal)

                for count, data in enumerate(filtered_data):
                    progress.setValue(count)

                    if progress.wasCanceled():
                        break

                    proxy_id = str(data[0])
                    self.proxy_ids.append(proxy_id)
                    sl_no = str(count + 1)
                    date_time = str(data[1])
                    host = str(data[2])
                    url = str(data[3]).split("||")[0]
                    status_code = "No Response" if data[4] is None else str(data[4])
                    method = str(data[5])

                    QTreeWidgetItem(self.tree_traffic_widget, [sl_no, date_time, host, url, status_code, method, proxy_id])

                progress.setValue(len(filtered_data))

            else:
                QMessageBox.warning(self, "Warning", "Unable to fetch data from database")

    def display(self, item):
        unique_proxy_id = item.text(6)

        req_row = self.session_db.display_request_data(unique_proxy_id)
        res_row = self.session_db.display_response_data(unique_proxy_id)

        req_header = str(req_row[0][0]).rstrip("\n")
        req_content = str(req_row[0][1]).rstrip("\n")
        req_url = str(req_row[0][2]).split("||")

        method = item.text(5).rstrip("\n")

        if len(res_row) > 0:
            res_header = str(res_row[0][0]).rstrip("\n")
            res_content = str(res_row[0][1]).rstrip("\n")
        else:
            res_header = ""
            res_content = ""

        status_code = item.text(4)

        request_final_view = f"{method} {req_url[0]} {req_url[1]}\n\n{req_header}\n\n{req_content}"
        response_final_view = f"{status_code} {get_status_code_value(status_code)}\n\n{res_header}\n\n{res_content}"

        self.text_request_widget.clear()
        self.text_request_widget.setText(request_final_view)

        self.text_response_widget.clear()
        self.text_response_widget.setText(response_final_view)

    def generate_json(self, proxy_ids):

        if len(proxy_ids) > 0:
            json_file_name = str(Path(f"{self.config_dict}/{self.execution_name}.json"))
            cancel = False
            temp_list = []

            progress = QProgressDialog("Generating JSON...", "Abort", 0, len(self.proxy_ids), self)
            progress.setWindowModality(Qt.WindowModal)

            for count, item in enumerate(proxy_ids):
                progress.setValue(count)

                if progress.wasCanceled():
                    cancel = True
                    break

                try:
                    _id = item.text(6)
                except AttributeError:
                    _id = item

                data = self.session_db.export_sessions(_id)
                temp_dict = {}
                url_data = str(data[0][0]).split(":", 1)[1][2:].split("/", 1)
                ip = url_data[0]
                url = f"/{url_data[1].split('||')[0]}"
                http_ver = url_data[1].split('||')[1]
                header = str(data[0][1]).split("\n")[:-1]
                method = str(data[0][3])
                raw_body = ""
                body_array = ""

                if str(method).upper() in ["GET", "HEAD", "CONNECT", "OPTIONS", "TRACE"]:
                    raw_body = ""
                    body_array = ""

                elif str(method).upper() in ["POST", "PUT", "PATCH", "DELETE"]:
                    content_type = ("application/x-www-form-urlencoded", "text/plain", "text/xml")
                    find = [i for i in header if i.startswith("Content-Type")]

                    if len(find) > 0:
                        find = "".join(find).split(":", 1)[1].strip()

                        if find.startswith(content_type):
                            raw_body = data[0][2]

                            if len(raw_body) > 0:
                                if find == "text/xml":
                                    body_array = put_parser(raw_body)
                                else:
                                    body_array = post_parser(raw_body)

                            else:
                                body_array = ""
                                raw_body = ""
                        else:
                            continue
                    else:
                        continue

                else:
                    continue

                redirect_url_exp = re.search(r"Location : (.*?)\n", data[0][1])

                if redirect_url_exp:
                    redirect_url_value = redirect_url_exp.group(1)
                else:
                    redirect_url_value = url

                header.insert(0, f"{method} {url} {http_ver}")

                temp_dict['bodyArray'] = body_array
                temp_dict['bodyRaw'] = raw_body
                temp_dict['headers'] = header
                temp_dict['ip'] = ip
                temp_dict['url'] = redirect_url_value

                temp_list.append(temp_dict)

            if not cancel:
                temp_dict = {"baseRequests": temp_list}

                with open(json_file_name, "w") as json_file:
                    json_file.write(json.dumps(temp_dict, indent=4, sort_keys=True))

                progress.setValue(len(self.proxy_ids))

                QMessageBox.information(self, "Information", f"HTTP Sessions exported to {json_file_name}")
        else:
            QMessageBox.information(self, "Information", "No data is present")

    def passive_header_audit(self):

        if len(self.proxy_ids) > 0:
            directory = f"/{self.config_dict}"
            filter = "json file (*.json)"

            passive_header_audit = QFileDialog.getOpenFileName(self, "Open a file", directory=directory, filter=filter)[
                0]

            if len(passive_header_audit) > 0:
                data = self.session_db.return_header_audit_data()
                cancel = False
                header_audit = PassiveHeadersAudit(passive_header_audit)

                progress = QProgressDialog("Passive Header Audit...", "Abort", 0, len(data), self)
                progress.setWindowModality(Qt.WindowModal)

                tmp_header_result_list = list()

                for count, item in enumerate(data):
                    progress.setValue(count)

                    if progress.wasCanceled():
                        cancel = True
                        break

                    op = header_audit.check_response_headers(item)
                    if op:
                        tmp_header_result_list.append(op)

                if not cancel:
                    if len(tmp_header_result_list) > 0:
                        PassiveHeaderAuditReport(tmp_header_result_list, self.config_dict)
                        progress.setValue(len(data))
                        QMessageBox.information(self, "Information", f"Passive header audit reports has been "
                                                                     f"generated in {str(Path(self.config_dict) / 'Passive Secure Header Audit.xlsx')}")
                    else:
                        QMessageBox.information(self, "Information", "No Secure header issues has been observed")

            else:
                QMessageBox.information(self, "Information", "Select a json header audit file")

        else:
            QMessageBox.information(self, "Information", "No data is present")

    def menu_context_tree(self, point):
        # info about nodes selected.
        index = self.tree_traffic_widget.indexAt(point)

        if not index.isValid():
            return

        # item = self.tree_traffic_widget.itemAt(point)

        proxy_ids = self.tree_traffic_widget.selectedItems()

        # build the menu
        menu = QMenu(self.tree_traffic_widget)
        export_menu = QMenu("Export")

        export_db_file = QAction("Db File")
        export_db_file.triggered.connect(lambda: self.export_db_file(proxy_ids))
        export_txt_file = QAction("Text File")
        export_txt_file.triggered.connect(lambda: self.export_text_file(proxy_ids))
        export_json_file = QAction("Json File")
        export_json_file.triggered.connect(lambda: self.generate_json(proxy_ids))
        run = QAction("Run")
        run.triggered.connect(lambda: self.run_sessions(proxy_ids))

        menu.addMenu(export_menu)
        export_menu.addAction(export_db_file)
        export_menu.addAction(export_txt_file)
        export_menu.addAction(export_json_file)
        menu.addAction(run)

        menu.exec_(self.tree_traffic_widget.viewport().mapToGlobal(point))

    def export_db_file(self, proxy_ids):

        if len(proxy_ids) > 0:
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d_%H-%M-%S")
            path = str(Path(self.config_dict)/f"data_{date}.db")
            cancel = False
            tmp_db_connection = MitmProxyDb(path)

            progress = QProgressDialog("Exporting data...", "Abort", 0, len(proxy_ids), self)
            progress.setWindowModality(Qt.WindowModal)

            for count, proxy_id in enumerate(proxy_ids):
                progress.setValue(count)

                if progress.wasCanceled():
                    cancel = True
                    break

                try:
                    req = self.session_db.export_request(proxy_id.text(6))
                    res = self.session_db.export_response(proxy_id.text(6))

                except AttributeError:
                    req = self.session_db.export_request(proxy_id)
                    res = self.session_db.export_response(proxy_id)

                tmp_db_connection.request_data(req[0])
                tmp_db_connection.response_data(res[0])

            if not cancel:
                progress.setValue(len(proxy_ids))
                tmp_db_connection.close_connection()
                QMessageBox.information(self, 'Information', f'Selected sessions has been exported to {path}')
            else:
                tmp_db_connection.close_connection()
        else:
            QMessageBox.information(self, 'Information', 'No data is present')

    def export_text_file(self, proxy_ids):
        if len(proxy_ids) > 0:
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d_%H-%M-%S")
            path = str(Path(self.config_dict)/f"data_{date}.txt")
            cancel = False

            progress = QProgressDialog("Exporting data...", "Abort", 0, len(proxy_ids), self)
            progress.setWindowModality(Qt.WindowModal)

            file = open(path, 'a+')

            for count, proxy_id in enumerate(proxy_ids):
                progress.setValue(count)

                if progress.wasCanceled():
                    cancel = True
                    break

                try:
                    exp_data = self.session_db.export_txt(proxy_id.text(6))

                except AttributeError:
                    exp_data = self.session_db.export_txt(proxy_id)

                method = str(exp_data[0][0])
                req_url = str(exp_data[0][1]).split("||")
                req_header = str(exp_data[0][2])
                req_content = str(exp_data[0][3])
                status_code = str(exp_data[0][4])
                rsp_header = str(exp_data[0][5])
                rsp_content = str(exp_data[0][6])

                request_final_view = f"\n{method} {req_url[0]} {req_url[1]}\n\n{req_header}\n\n{req_content}\n\n"\
                                     f"{status_code} {get_status_code_value(status_code)}\n\n{rsp_header}\n\n"\
                                     f"{rsp_content}\n{'*'*100}"

                file.write(request_final_view)

            if not cancel:
                progress.setValue(len(proxy_ids))
                file.close()
                QMessageBox.information(self, 'Information', f'Selected sessions has been exported to {path}')
            else:
                file.close()

        else:
            QMessageBox.information(self, 'Information', 'No data is present')

    def run_sessions(self, proxy_ids):
        db_path = Path(f"{self.config_dict}/temp.db")
        replay_db = MitmProxyDb(str(db_path))

        if len(proxy_ids) == 1:
            unique_id = str(uuid4())
            date = str(datetime.datetime.now())
            request_data = str(self.text_request_widget.toPlainText()).split("\n\n")
            method, url = request_data[0].split(" ", 1)
            host = str(url).split("//", 1)[1].split("/", 1)[0]

            http_id = url.find("HTTP")

            url_ = url[0:http_id - 1]
            http_type = url[http_id:]

            new_url = f"{url_}||{http_type}"

            header_dict = get_header_dict(request_data[1])

            content = request_data[-1]

            res_status_code, res_header, res_content = static_http_requests(
                method=method, url=url_, header=header_dict, content=content, timeout=10, num_of_retries=5
            )

            str_header = ''
            if type(res_header) is dict:
                for key, value in res_header.items():
                    str_header = str_header + f"{key} : {value}\n"

            replay_db = MitmProxyDb(str(db_path))
            replay_db.request_data([unique_id, date, host, new_url, method, request_data[1], content])
            replay_db.response_data([unique_id, str(res_status_code), str_header, res_content])

            replay_form = Replay(replay_db)
            replay_form.exec_()

            replay_db.close_connection()
            db_path.unlink()

        elif len(proxy_ids) > 1:
            cancel = False
            progress = QProgressDialog("Running sessions...", "Abort", 0, len(proxy_ids), self)
            progress.setWindowModality(Qt.WindowModal)

            for count, proxy_id in enumerate(proxy_ids):
                progress.setValue(count)

                if progress.wasCanceled():
                    cancel = True
                    break

                request_data = self.session_db.run_selected_request(proxy_id.text(6))

                unique_id = request_data[0]
                date = str(datetime.datetime.now())
                host = request_data[1]
                url, http_ver = request_data[2].split('||')
                header = request_data[3]
                method = request_data[4]
                content = request_data[5]
                header_dict = get_header_dict(header)

                res_status_code, res_header, res_content = static_http_requests(
                    method=method, url=url, header=header_dict, content=content, timeout=10, num_of_retries=5
                )

                str_header = ''
                if type(res_header) is dict:
                    for key, value in res_header.items():
                        str_header = str_header + f"{key} : {value}\n"

                replay_db.request_data([unique_id, date, host, request_data[2], method, header, content])
                replay_db.response_data([unique_id, str(res_status_code), str_header, res_content])

            if not cancel:
                progress.setValue(len(proxy_ids))
                replay_form = Replay(replay_db)
                replay_form.exec_()
            else:
                replay_db.close_connection()
                db_path.unlink()

        else:
            replay_db.close_connection()
            db_path.unlink()
            QMessageBox.information(self, 'Information', 'No data is present')

