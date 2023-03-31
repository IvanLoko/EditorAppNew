from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QLabel


class MainBar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

    def setupUI(self):
        self.setObjectName("MainBar")

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.setLayout(self.layout)

        with open("src/style/dark/main_bar.css") as style:
            self.setStyleSheet(style.read())

        self.update()


class ImageTab(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

        true_parent = parent

        self.clicked.connect(lambda: true_parent.tab_clicked(self))

    def setupUI(self):
        self.setObjectName("ImageTab")
        self.setText("Empty")
        self.setFixedSize(180, 35)

        self.update()
