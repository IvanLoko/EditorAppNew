from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class InfoLine(QTextEdit):

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.setObjectName("InfoLine")

        self.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        with open("src/style/dark/info_line.css") as style:
            self.setStyleSheet(style.read())
            del style

        self.setText("Hellow!")

        self.setFixedSize(1920, 30)
