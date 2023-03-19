from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy


class MainBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

    def setupUI(self):
        self.setFixedSize(1920, 30)

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

        self.newtab_button = QPushButton("+")
        self.newtab_button.setObjectName("AddProjectButton")
        self.newtab_button.setFixedSize(12, 12)
        self.newtab_button.setContentsMargins(0, 0, 0, 0)

        image_line_layout = QHBoxLayout()
        image_line_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        image_line_layout.setSpacing(5)
        image_line_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs_layout = QHBoxLayout()
        self.tabs_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.tabs_layout.setSpacing(0)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)

        image_line_layout.addLayout(self.tabs_layout)
        image_line_layout.addWidget(self.newtab_button)

        self.image_line.setLayout(image_line_layout)

        layout.addWidget(self.load_button)
        layout.addWidget(self.rewrite_button)
        layout.addWidget(self.image_line)

        self.load_button.clicked.connect(self.parent().load_project)
        self.rewrite_button.clicked.connect(self.parent().rewrite)
        self.newtab_button.clicked.connect(self.add_tab)

        with open("src/style/dark/main_bar.css") as style:
            self.setStyleSheet(style.read())

        self.update()

    def add_tab(self):
        self.tabs_layout.addWidget(ImageTab())


class ImageTab(QPushButton):
    def __init__(self):
        super().__init__()

        self.setupUI()

    def setupUI(self):
        self.setObjectName("ImageTab")
        self.setText("Tab")
        self.setFixedSize(100, 30)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignRight)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 8, 0)

        self.setLayout(layout)

        self.CloseTabButton = QPushButton("x")
        self.CloseTabButton.setObjectName("CloseTabButton")
        self.CloseTabButton.setFixedSize(10, 10)

        layout.addWidget(self.CloseTabButton)

        self.CloseTabButton.clicked.connect(self.close)

        self.update()
