from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt
from PyQt5.QtCore import QDateTime


class Filter(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Traffic Monitor")
        self.image_path = str(Path(__file__).absolute().parent.parent / "images")
        self.setWindowIcon(QIcon(str(Path(self.image_path)/"logo.ico")))
        self.resize(500, 500)

        self.check_box_http_get = QCheckBox("Show GET")
        self.check_box_http_post = QCheckBox("Show POST")
        self.check_box_http_put = QCheckBox("Show PUT")
        self.check_box_http_delete = QCheckBox("Show DELETE")
        self.check_box_http_options = QCheckBox("Show OPTIONS")
        self.check_box_http_trace = QCheckBox("Show TRACE")
        self.check_box_http_connect = QCheckBox("Show CONNECT")
        self.check_box_http_head = QCheckBox("Show HEAD")

        self.check_box_image_extn = QCheckBox("Hide Image File Extensions")
        self.check_box_font_extn = QCheckBox("Hide Font File Extensions")
        self.check_box_css_extn = QCheckBox("Hide CSS Files")
        self.check_box_javascript_extn = QCheckBox("Hide Javascript Files")

        self.check_box_url_contains = QCheckBox("Show if URL Contains")
        self.check_box_status_code_contains = QCheckBox("Show if Status Code Contains")

        self.edit_url_contains = QLineEdit()
        self.edit_url_contains.setDisabled(True)
        self.edit_status_code_contains = QLineEdit()
        self.edit_status_code_contains.setDisabled(True)

        self.check_box_start_date_time = QCheckBox("Start Datetime")
        self.check_box_end_date_time = QCheckBox("End Datetime")

        self.start_date_time_picker = QDateTimeEdit()
        self.start_date_time_picker.setCalendarPopup(True)
        self.start_date_time_picker.setDisabled(True)
        self.start_date_time_picker.setDateTime(QDateTime.currentDateTime().addSecs(-3600*2))

        self.end_date_time_picker = QDateTimeEdit()
        self.end_date_time_picker.setCalendarPopup(True)
        self.end_date_time_picker.setDisabled(True)
        self.end_date_time_picker.setDateTime(QDateTime.currentDateTime())

        self.button_set = QPushButton("Set")
        self.button_clear = QPushButton("Clear All")

        # initialize variables
        # dictionary to save all filters
        self.filter_dict = {
            "GET": False,
            "POST": False,
            "PUT": False,
            "DELETE": False,
            "OPTIONS": False,
            "TRACE": False,
            "CONNECT": False,
            "HEAD": False,
            "IMAGE_FILE_EXTENSIONS": False,
            "FONT_FILE_EXTENSIONS": False,
            "CSS_FILES": False,
            "JAVASCRIPT_FILES": False,
            "FILTER_URL": "",
            "FILTER_STATUS_CODES": "",
            "START_DATE_TIME": "",
            "END_DATE_TIME": "",
        }

        self.center()
        self.init_signals()
        self.init_ui()

    def center(self):
        """Method to center the QMainWindow"""
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def init_ui(self):
        vertical_box_main = QVBoxLayout()
        horizontal_box1 = QHBoxLayout()
        horizontal_box2 = QHBoxLayout()
        horizontal_box3 = QHBoxLayout()
        horizontal_box4 = QHBoxLayout()

        response_type_vertical_box = QVBoxLayout()

        grid_box_http_methods = QGridLayout()
        group_box_http_methods = QGroupBox("HTTP Methods")

        grid_box_http_methods.addWidget(self.check_box_http_get, 0, 0)
        grid_box_http_methods.addWidget(self.check_box_http_options, 0, 1)
        grid_box_http_methods.addWidget(self.check_box_http_post, 1, 0)
        grid_box_http_methods.addWidget(self.check_box_http_trace, 1, 1)
        grid_box_http_methods.addWidget(self.check_box_http_put, 2, 0)
        grid_box_http_methods.addWidget(self.check_box_http_connect, 2, 1)
        grid_box_http_methods.addWidget(self.check_box_http_delete, 3, 0)
        grid_box_http_methods.addWidget(self.check_box_http_head, 3, 1)

        group_box_http_methods.setLayout(grid_box_http_methods)

        group_box_response_type = QGroupBox("Response Type")
        response_type_vertical_box.addWidget(self.check_box_image_extn)
        response_type_vertical_box.addWidget(self.check_box_font_extn)
        response_type_vertical_box.addWidget(self.check_box_css_extn)
        response_type_vertical_box.addWidget(self.check_box_javascript_extn)
        group_box_response_type.setLayout(response_type_vertical_box)

        horizontal_box1.addWidget(group_box_http_methods)
        horizontal_box1.addWidget(group_box_response_type)

        group_box_filter_url = QGroupBox("Filter Urls")
        form_box_filter_url = QFormLayout()

        form_box_filter_url.addRow(self.check_box_url_contains, self.edit_url_contains)

        group_box_filter_url.setLayout(form_box_filter_url)

        horizontal_box2.addWidget(group_box_filter_url)

        group_box_filter_status_code = QGroupBox("Filter Status Code")
        form_box_filter_status_code = QFormLayout()

        form_box_filter_status_code.addRow(self.check_box_status_code_contains, self.edit_status_code_contains)
        group_box_filter_status_code.setLayout(form_box_filter_status_code)

        horizontal_box3.addWidget(group_box_filter_status_code)

        group_box_date_time = QGroupBox("DateTime")
        form_box_date_time = QFormLayout()

        form_box_date_time.addRow(self.check_box_start_date_time,  self.start_date_time_picker)
        form_box_date_time.addRow(self.check_box_end_date_time,  self.end_date_time_picker)

        group_box_date_time.setLayout(form_box_date_time)

        group_box_buttons = QGroupBox()
        vertical_buttons = QVBoxLayout()

        vertical_buttons.addWidget(self.button_set)
        vertical_buttons.addWidget(self.button_clear)

        group_box_buttons.setLayout(vertical_buttons)

        horizontal_box4.addWidget(group_box_date_time)
        horizontal_box4.addWidget(group_box_buttons)

        vertical_box_main.addStretch()
        vertical_box_main.addLayout(horizontal_box1)
        vertical_box_main.addStretch()
        vertical_box_main.addLayout(horizontal_box2)
        vertical_box_main.addStretch()
        vertical_box_main.addLayout(horizontal_box3)
        vertical_box_main.addStretch()
        vertical_box_main.addLayout(horizontal_box4)
        vertical_box_main.addStretch()

        self.setLayout(vertical_box_main)

        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    def init_signals(self):
        self.check_box_url_contains.stateChanged.connect(self.evt_url_state)
        self.check_box_status_code_contains.stateChanged.connect(self.evt_status_code_state)
        self.check_box_start_date_time.stateChanged.connect(self.evt_start_date_time_state)
        self.check_box_end_date_time.stateChanged.connect(self.evt_end_date_time_state)

        self.button_set.clicked.connect(self.evt_btn_set)
        self.button_clear.clicked.connect(self.evt_btn_clear_all)

    def evt_url_state(self):
        if self.check_box_url_contains.isChecked():
            self.edit_url_contains.setDisabled(False)
        else:
            self.edit_url_contains.setDisabled(True)

    def evt_status_code_state(self):
        if self.check_box_status_code_contains.isChecked():
            self.edit_status_code_contains.setDisabled(False)
        else:
            self.edit_status_code_contains.setDisabled(True)

    def evt_start_date_time_state(self):
        if self.check_box_start_date_time.isChecked():
            self.start_date_time_picker.setDisabled(False)
        else:
            self.start_date_time_picker.setDisabled(True)

    def evt_end_date_time_state(self):
        if self.check_box_end_date_time.isChecked():
            self.end_date_time_picker.setDisabled(False)
        else:
            self.end_date_time_picker.setDisabled(True)

    def evt_btn_set(self):
        self.filter_dict['GET'] = self.check_box_http_get.isChecked()
        self.filter_dict['OPTIONS'] = self.check_box_http_options.isChecked()
        self.filter_dict['POST'] = self.check_box_http_post.isChecked()
        self.filter_dict['TRACE'] = self.check_box_http_trace.isChecked()
        self.filter_dict['PUT'] = self.check_box_http_put.isChecked()
        self.filter_dict['CONNECT'] = self.check_box_http_connect.isChecked()
        self.filter_dict['DELETE'] = self.check_box_http_delete.isChecked()
        self.filter_dict['HEAD'] = self.check_box_http_head.isChecked()

        self.filter_dict['IMAGE_FILE_EXTENSIONS'] = self.check_box_image_extn.isChecked()
        self.filter_dict['FONT_FILE_EXTENSIONS'] = self.check_box_font_extn.isChecked()
        self.filter_dict['CSS_FILES'] = self.check_box_css_extn.isChecked()
        self.filter_dict['JAVASCRIPT_FILES'] = self.check_box_javascript_extn.isChecked()

        if self.check_box_url_contains.isChecked():
            self.filter_dict['FILTER_URL'] = self.edit_url_contains.text()
        else:
            self.filter_dict['FILTER_URL'] = ''

        if self.check_box_status_code_contains.isChecked():
            self.filter_dict['FILTER_STATUS_CODES'] = self.edit_status_code_contains.text()
        else:
            self.filter_dict['FILTER_STATUS_CODES'] = ''

        if self.check_box_start_date_time.isChecked() and self.check_box_end_date_time.isChecked():

            start_date_time = self.start_date_time_picker.dateTime()
            end_date_time = self.end_date_time_picker.dateTime()

            if start_date_time <= end_date_time:

                self.filter_dict['START_DATE_TIME'] = start_date_time.toString("yyyy-MM-dd hh:mm:ss")
                self.filter_dict['END_DATE_TIME'] = end_date_time.toString("yyyy-MM-dd hh:mm:ss")

            else:
                QMessageBox.information(self, "Warning", "Start Date time should be lesser than current Date time")
        else:

            if self.check_box_start_date_time.isChecked():

                start_date_time = self.start_date_time_picker.dateTime().toString("yyyy-MM-dd hh:mm:ss")
                self.filter_dict['START_DATE_TIME'] = start_date_time

            else:
                self.filter_dict['START_DATE_TIME'] = ''

            if self.check_box_end_date_time.isChecked():

                end_date_time = self.end_date_time_picker.dateTime().toString("yyyy-MM-dd hh:mm:ss")
                self.filter_dict['END_DATE_TIME'] = end_date_time

            else:
                self.filter_dict['END_DATE_TIME'] = ''
        self.close()

    def evt_btn_clear_all(self):
        self.check_box_http_get.setChecked(False)
        self.check_box_http_options.setChecked(False)
        self.check_box_http_post.setChecked(False)
        self.check_box_http_trace.setChecked(False)
        self.check_box_http_put.setChecked(False)
        self.check_box_http_connect.setChecked(False)
        self.check_box_http_delete.setChecked(False)
        self.check_box_http_head.setChecked(False)

        self.check_box_image_extn.setChecked(False)
        self.check_box_font_extn.setChecked(False)
        self.check_box_css_extn.setChecked(False)
        self.check_box_javascript_extn.setChecked(False)

        self.check_box_url_contains.setChecked(False)
        self.edit_url_contains.setDisabled(True)

        self.check_box_status_code_contains.setChecked(False)
        self.edit_status_code_contains.setDisabled(True)

        self.check_box_start_date_time.setChecked(False)
        self.start_date_time_picker.setDisabled(True)

        self.check_box_end_date_time.setChecked(False)
        self.end_date_time_picker.setDisabled(True)