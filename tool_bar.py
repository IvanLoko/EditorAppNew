from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel

from SimpleObjects import SimplePoint
from centralLabel import GraphicsScene


class ToolBar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

        self.visible_status = True

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
        self.AI_button.clicked.connect(self.parent().mod_AI)

        layout.addWidget(self.AI_button)

        self.AXE_button = QPushButton("2")
        self.AXE_button.setObjectName("AXEButton")
        self.AXE_button.setFixedSize(30, 30)

        layout.addWidget(self.AXE_button)

        self.STANDARD_button = QPushButton("3")
        self.STANDARD_button.setObjectName("STANDARD")
        self.STANDARD_button.setFixedSize(30, 30)

        self.STANDARD_button.clicked.connect(self.parent().mod_STANDARD)

        layout.addWidget(self.STANDARD_button)

        self.pins_button = QPushButton("4")
        self.pins_button.setObjectName("PinsButton")
        self.pins_button.setFixedSize(30, 30)
        self.pins_button.clicked.connect(self.hide_pins)

        layout.addWidget(self.pins_button)

        self.rotation_button = QPushButton("5")
        self.rotation_button.setObjectName("RotationButton")
        self.rotation_button.setFixedSize(30, 30)
        self.rotation_button.clicked.connect(self.rotation)

        layout.addWidget(self.rotation_button)

        self.mirrorX_button = QPushButton("6")
        self.mirrorX_button.setObjectName("MirrorXButton")
        self.mirrorX_button.setFixedSize(30, 30)
        self.mirrorX_button.clicked.connect(self.reflect_x)

        layout.addWidget(self.mirrorX_button)

        self.mirrorY_button = QPushButton("7")
        self.mirrorY_button.setObjectName("MirrorYButton")
        self.mirrorY_button.setFixedSize(30, 30)
        self.mirrorY_button.clicked.connect(self.reflect_y)

        layout.addWidget(self.mirrorY_button)

        with open("src/style/dark/tool_bar.css") as style:
            self.setStyleSheet(style.read())

        self.update()

    def hide_pins(self):
        self.visible_status = not self.visible_status
        for scene in self.parent().graphics_view.findChildren(GraphicsScene):
            [el.setVisible(self.visible_status) for el in scene.items() if isinstance(el, SimplePoint)]
        self.parent().set_line(f"Points visible is set to: {self.visible_status}", Qt.darkYellow)

    def rotation(self):
        self.parent().graphics_view.transform_func.rotate(90)
        self.parent().graphics_view.setTransform(self.parent().graphics_view.transform_func)

    def reflect_x(self):
        self.parent().graphics_view.transform_func.scale(-1, 1)
        self.parent().graphics_view.setTransform(self.parent().graphics_view.transform_func)

    def reflect_y(self):
        self.parent().graphics_view.transform_func.scale(1, -1)
        self.parent().graphics_view.setTransform(self.parent().graphics_view.transform_func)