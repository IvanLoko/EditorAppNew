from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel


class ToolBar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

    def setupUI(self):
        self.setFixedSize(60, 1020)
        self.setObjectName("ToolBar")
        self.setStyleSheet("#ToolBar {background-color: #646464; border: 1px solid #727272;}")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.setLayout(layout)

        self.AI_button = QPushButton()
        self.AI_button.setObjectName("AIButton")
        self.AI_button.setFixedSize(40, 40)
        self.AI_button.setIcon(QIcon("src/icons/dark/rect.png"))
        self.AI_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.AI_button)

        self.AXE_button = QPushButton()
        self.AXE_button.setObjectName("AXEButton")
        self.AXE_button.setFixedSize(40, 40)
        self.AXE_button.setIcon(QIcon("src/icons/dark/rewrite.png"))
        self.AXE_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.AXE_button)

        self.selection_button = QPushButton()
        self.selection_button.setObjectName("SelectionButton")
        self.selection_button.setFixedSize(40, 40)
        self.selection_button.setIcon(QIcon("src/icons/dark/select.png"))
        self.selection_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.selection_button)

        self.pins_button = QPushButton()
        self.pins_button.setObjectName("PinsButton")
        self.pins_button.setFixedSize(40, 40)
        self.pins_button.setIcon(QIcon("src/icons/dark/square.png"))
        self.pins_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.pins_button)

        self.rotation_button = QPushButton()
        self.rotation_button.setObjectName("RotationButton")
        self.rotation_button.setFixedSize(40, 40)
        self.rotation_button.setIcon(QIcon("src/icons/dark/zoom.png"))
        self.rotation_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.rotation_button)

        self.mirror_button = QPushButton()
        self.mirror_button.setObjectName("MirrorButton")
        self.mirror_button.setFixedSize(40, 40)
        self.mirror_button.setIcon(QIcon("src/icons/dark/zoom.png"))
        self.mirror_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.mirror_button)

        with open("src/style/dark/tool_bar.css") as style:
            self.setStyleSheet(style.read())

        self.update()
