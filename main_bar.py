from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy


class MainBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

    def setupUI(self):
        self.setFixedSize(1520, 30)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.setLayout(layout)

        self.load_button = QPushButton()
        self.load_button.setObjectName("Load")
        self.load_button.setFixedSize(30, 30)
        self.load_button.setIcon(QIcon("src/icons/dark/load.png"))
        self.load_button.setIconSize(QSize(30, 30))

        self.rewrite_button = QPushButton()
        self.rewrite_button.setObjectName("Rewrite")
        self.rewrite_button.setFixedSize(30, 30)
        self.rewrite_button.setIcon(QIcon('src/icons/dark/rewrite.png'))
        self.rewrite_button.setIconSize(QSize(30, 30))

        self.image_line = QWidget()
        self.image_line.setObjectName("ImageLine")
        self.image_line.setFixedHeight(30)
        self.image_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.image_line_layout = QHBoxLayout()
        self.image_line_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.image_line_layout.setSpacing(0)
        self.image_line_layout.setContentsMargins(0, 0, 0, 0)

        self.image_line.setLayout(self.image_line_layout)

        layout.addWidget(self.load_button)
        layout.addWidget(self.rewrite_button)
        layout.addWidget(self.image_line)

        self.load_button.clicked.connect(self.parent().load_project)
        self.rewrite_button.clicked.connect(self.parent().rewrite)

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
        self.setFixedSize(180, 30)

        self.update()
