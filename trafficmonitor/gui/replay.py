from pathlib import Path

from PyQt5.QtWidgets import QDialog, QAbstractItemView, QTreeWidget, QTextEdit, QApplication
from PyQt5.QtWidgets import QLabel, QMessageBox, QVBoxLayout, QGridLayout, QTreeWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt

from trafficmonitor.helper_functions import get_status_code_value


class Replay(QDialog):
    def __init__(self, db):
        super(Replay, self).__init__()

        self.center()
        self.session_db = db
        self.setWindowTitle("Traffic Monitor")
        self.image_path = str(Path(__file__).absolute().parent.parent / "images")
        self.setWindowIcon(QIcon(str(Path(self.image_path) / "logo.ico")))
        self.resize(1360, 768)
        self.proxy_ids = []

        # initialize all widgets
        self.tree_traffic_widget = QTreeWidget()
        self.tree_traffic_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_traffic_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.text_request_widget = QTextEdit()
        self.text_response_widget = QTextEdit()

        self.init_ui()
        self.init_widgets()
        self.init_signals()

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

        refresh_data = self.session_db.refresh_data()

        if refresh_data not in [None, '']:
            self.proxy_ids = []
            for count, data in enumerate(refresh_data):
                proxy_id = str(data[0])
                self.proxy_ids.append(proxy_id)
                sl_no = str(count + 1)
                date_time = str(data[1])
                host = str(data[2])
                url = str(data[3]).split("||")[0]
                status_code = "No Response" if data[4] is None else str(data[4])
                method = str(data[5])
                QTreeWidgetItem(self.tree_traffic_widget, [sl_no, date_time, host, url, status_code, method, proxy_id])
        else:
            QMessageBox.warning(self, "Warning", "Unable to fetch data from database")

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

        self.setLayout(vertical_box)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    def init_signals(self):
        # menu signals
        # self.menu_capture_traffic.triggered.connect(self.start)
        # self.menu_export_db_file.triggered.connect(lambda: self.export_db_file(self.proxy_ids))
        # self.menu_export_txt_file.triggered.connect(lambda: self.export_text_file(self.proxy_ids))
        # self.menu_open_db.triggered.connect(self.evt_menu_open)
        # self.menu_json_generator.triggered.connect(self.generate_json)
        # self.menu_psv_header_adt.triggered.connect(self.passive_header_audit)
        #
        # tool bar signals
        # self.tool_bar_start.triggered.connect(self.evt_tool_bar_start)
        # self.tool_bar_stop.triggered.connect(self.evt_tool_bar_stop)
        # self.tool_bar_filter.triggered.connect(self.evt_tool_bar_filter)
        # self.tool_bar_refresh.triggered.connect(self.refresh)
        #
        self.tree_traffic_widget.itemClicked.connect(self.display)
        # self.tree_traffic_widget.customContextMenuRequested.connect(self.menu_context_tree)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

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