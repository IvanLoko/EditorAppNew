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
        self.setFixedSize(50, 1020)
        self.setObjectName("ToolBar")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

        self.load_button = ToolBarButton("SectionButton")
        self.load_button.clicked.connect(self.parent().load_project)
        self.load_button.setIcon(QIcon("src/icons/dark/new_dark/load.png"))
        self.load_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.load_button)

        self.rewrite_button = ToolBarButton("SectionButton")
        self.rewrite_button.clicked.connect(self.parent().rewrite)
        self.rewrite_button.setIcon(QIcon("src/icons/dark/new_dark/save.png"))
        self.rewrite_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.rewrite_button)

        self.AI_button = ToolBarButton("StartSectionButton")
        self.AI_button.setIcon(QIcon("src/icons/dark/new_dark/AI.png"))
        self.AI_button.setIconSize(QSize(40, 40))
        self.AI_button.clicked.connect(self.parent().mod_AI)

        layout.addWidget(self.AI_button)

        self.AXE_button = ToolBarButton("SectionButton")
        self.AXE_button.setIcon(QIcon("src/icons/dark/new_dark/AXE.png"))
        self.AXE_button.setIconSize(QSize(40, 40))
        self.AXE_button.clicked.connect(self.parent().mod_AXE)

        layout.addWidget(self.AXE_button)

        self.STANDARD_button = ToolBarButton("SectionButton")
        self.STANDARD_button.setIcon(QIcon("src/icons/dark/new_dark/STD.png"))
        self.STANDARD_button.setIconSize(QSize(40, 40))
        self.STANDARD_button.clicked.connect(self.parent().mod_STANDARD)

        layout.addWidget(self.STANDARD_button)

        self.rotation_button = ToolBarButton("StartSectionButton")
        self.rotation_button.setIcon(QIcon("src/icons/dark/new_dark/rotate.png"))
        self.rotation_button.setIconSize(QSize(30, 30))
        self.rotation_button.clicked.connect(self.rotation)

        layout.addWidget(self.rotation_button)

        self.mirrorX_button = ToolBarButton("SectionButton")
        self.mirrorX_button.setIcon(QIcon("src/icons/dark/new_dark/mirX.png"))
        self.mirrorX_button.setIconSize(QSize(40, 40))
        self.mirrorX_button.clicked.connect(self.reflect_x)

        layout.addWidget(self.mirrorX_button)

        self.mirrorY_button = ToolBarButton("SectionButton")
        self.mirrorY_button.setIcon(QIcon("src/icons/dark/new_dark/mirY.png"))
        self.mirrorY_button.setIconSize(QSize(40, 40))
        self.mirrorY_button.clicked.connect(self.reflect_y)

        layout.addWidget(self.mirrorY_button)

        self.crop_button = ToolBarButton("SectionButton")
        self.crop_button.setIcon(QIcon("src/icons/dark/new_dark/crop.png"))
        self.crop_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.crop_button)

        self.scale_button = ToolBarButton("SectionButton")
        self.scale_button.setIcon(QIcon("src/icons/dark/new_dark/zoom.png"))
        self.scale_button.setIconSize(QSize(30, 30))

        layout.addWidget(self.scale_button)

        self.pins_button = ToolBarButton("StartSectionButton")
        self.pins_button.setIcon(QIcon("src/icons/dark/new_dark/pins.png"))
        self.pins_button.setIconSize(QSize(40, 40))
        self.pins_button.clicked.connect(self.hide_pins)

        layout.addWidget(self.pins_button)

        self.pins_names_button = ToolBarButton("SectionButton")
        self.pins_names_button.setIcon(QIcon("src/icons/dark/new_dark/pins_names.png"))
        self.pins_names_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.pins_names_button)

        self.el_search_button = ToolBarButton("SectionButton")
        self.el_search_button.setIcon(QIcon("src/icons/dark/new_dark/find_element.png"))
        self.el_search_button.setIconSize(QSize(40, 40))
        layout.addWidget(self.el_search_button)

        self.not_filled_button = ToolBarButton("SectionButton")
        self.not_filled_button.setIcon(QIcon("src/icons/dark/new_dark/find_missing_pins.png"))
        self.not_filled_button.setIconSize(QSize(40, 40))

        layout.addWidget(self.not_filled_button, Qt.AlignBottom)

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


class ToolBarButton(QPushButton):
    
    def __init__(self, section):
        
        super().__init__()

        self.section = section

        self.setFixedSize(50, 50)
        self.setObjectName(self.section)
