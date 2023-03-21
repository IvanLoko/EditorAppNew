from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel


class ToolBar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

    def setupUI(self):
        self.setFixedSize(60, 990)
        self.setObjectName("ToolBar")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.setLayout(layout)

        self.AI_button = QPushButton("1")
        self.AI_button.setObjectName("AIButton")
        self.AI_button.setFixedSize(30, 30)

        layout.addWidget(self.AI_button)

        self.AXE_button = QPushButton("2")
        self.AXE_button.setObjectName("AXEButton")
        self.AXE_button.setFixedSize(30, 30)

        layout.addWidget(self.AXE_button)

        self.selection_button = QPushButton("3")
        self.selection_button.setObjectName("SelectionButton")
        self.selection_button.setFixedSize(30, 30)

        layout.addWidget(self.selection_button)

        self.pins_button = QPushButton("4")
        self.pins_button.setObjectName("PinsButton")
        self.pins_button.setFixedSize(30, 30)

        layout.addWidget(self.pins_button)

        self.rotation_button = QPushButton("5")
        self.rotation_button.setObjectName("RotationButton")
        self.rotation_button.setFixedSize(30, 30)

        layout.addWidget(self.rotation_button)

        self.mirror_button = QPushButton("6")
        self.mirror_button.setObjectName("MirrorButton")
        self.mirror_button.setFixedSize(30, 30)

        layout.addWidget(self.mirror_button)

        with open("src/style/dark/tool_bar.css") as style:
            self.setStyleSheet(style.read())

        self.update()
