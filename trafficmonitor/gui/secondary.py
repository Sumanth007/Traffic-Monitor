from pathlib import Path

from PyQt5.QtWidgets import QDialog, QLineEdit, QCheckBox, QPushButton, QApplication
from PyQt5.QtWidgets import QLabel, QMessageBox, QHBoxLayout, QFormLayout
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt

from trafficmonitor.helper_functions import create_path, ping


class Secondary(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Traffic Monitor")
        self.image_path = str(Path(__file__).absolute().parent.parent/"images")
        self.setWindowIcon(QIcon(str(Path(self.image_path)/"logo.ico")))
        self.resize(400, 200)

        self.center()

        # initialize values
        self.path = create_path()
        self.data = {}

        # initialize all widgets
        self.edit_execution_name = QLineEdit()
        self.edit_ip_address = QLineEdit()
        self.edit_proxy_address = QLineEdit("127.0.0.1")
        self.edit_proxy_port = QLineEdit("9090")
        self.check_box_upstream_proxy = QCheckBox("Enable Upstream proxy")
        self.button_start = QPushButton("Start")

        self.bind_signals()
        self.check_upstream_proxy()
        self.init_ui()

    def center(self):
        """Method to center the QMainWindow"""
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def init_ui(self):
        form_layout = QFormLayout()
        horizontal_box1 = QHBoxLayout()
        horizontal_box2 = QHBoxLayout()

        form_layout.addRow(QLabel("Execution Name: "), self.edit_execution_name)
        form_layout.addRow(QLabel("Host Address: "), self.edit_ip_address)

        horizontal_box1.addStretch()
        horizontal_box1.addWidget(self.check_box_upstream_proxy)
        horizontal_box1.addStretch()

        form_layout.addRow(horizontal_box1)

        form_layout.addRow(QLabel("Proxy Address: "), self.edit_proxy_address)
        form_layout.addRow(QLabel("Proxy Port: "), self.edit_proxy_port)

        horizontal_box2.addStretch()
        horizontal_box2.addWidget(self.button_start)
        horizontal_box2.addStretch()

        form_layout.addRow(horizontal_box2)

        self.setLayout(form_layout)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    def bind_signals(self):
        self.check_box_upstream_proxy.stateChanged.connect(self.check_upstream_proxy)
        self.button_start.clicked.connect(self.evt_button_start)

    def check_upstream_proxy(self):
        if self.check_box_upstream_proxy.isChecked():
            self.edit_proxy_address.setDisabled(False)
            self.edit_proxy_port.setDisabled(False)
        else:
            self.edit_proxy_address.setDisabled(True)
            self.edit_proxy_port.setDisabled(True)

    def evt_button_start(self):
        execution_name = self.edit_execution_name.text()
        ip_address = self.edit_ip_address.text()
        proxy_address = self.edit_proxy_address.text()
        proxy_port = self.edit_proxy_port.text()
        empty_values = [None, '']

        # validate the values
        if execution_name not in empty_values:

            is_file_exists = Path(f"{self.path}/{execution_name}.db")

            if not is_file_exists.exists():

                if ip_address not in empty_values:

                    if ping(ip_address):

                        if self.check_box_upstream_proxy.isChecked():

                            if proxy_address not in empty_values:

                                if proxy_port not in empty_values:
                                    self.data['UPSTREAM_PROXY_IP'] = proxy_address
                                    self.data['UPSTREAM_PROXY_PORT'] = proxy_port
                                    self.data['EXECUTION_NAME'] = execution_name
                                    self.data['IP_ADDRESS'] = ip_address
                                    self.close()

                                else:
                                    QMessageBox.information(self, "Warning", "Please enter proxy port")
                            else:
                                QMessageBox.information(self, "Warning", "Please enter proxy address")
                        else:
                            self.data['EXECUTION_NAME'] = execution_name
                            self.data['IP_ADDRESS'] = ip_address
                            self.close()
                    else:
                        QMessageBox.information(self, "Warning", f"'{ip_address} is unreachable!!'")
                else:
                    QMessageBox.information(self, "Warning", "Please enter host address")
            else:
                QMessageBox.information(self, "Warning", f"'{execution_name}' already exists!!")
        else:
            QMessageBox.information(self, "Warning", "Please enter execution name")

