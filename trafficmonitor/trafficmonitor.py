import sys
from PyQt5.QtWidgets import QApplication
from trafficmonitor.gui.primary import Primary


def run():
    app = QApplication(sys.argv)
    win = Primary()
    win.show()
    sys.exit(app.exec())