from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QCursor, QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QPushButton, QSpinBox, QHBoxLayout, QSlider


class SidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setFixedSize(400, 1020)
        self.setObjectName("SidePanel")

        self.slider = Slider(self.parent())
        self.slider.move(1801, 1005)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

        layout.addWidget(SectionLabel("Список элементов", self))
        layout.addWidget(self.parent().elements_list)

        layout.addWidget(SectionLabel("Текущий элемент", self))
        layout.addWidget(self.parent().circuit_map)

        layout.addWidget(SectionLabel("Сборочник", self))
        layout.addWidget(self.parent().sb)

        with open("src/style/dark/side_panel.css") as style:
            self.setStyleSheet(style.read())

        self.update()

    def slider_change(self, status):
        self.slider.setVisible(status)

    def change_op(self):
        self.parent().sb.opacity.setValue(self.slider.sliderPosition())


class ListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setFixedSize(400, 660)
        self.setObjectName("ElementList")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


class ElementLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

    def setupUI(self):

        self.setFixedSize(400, 240)
        self.setAlignment(Qt.AlignCenter)
        self.setText("None")
        self.setObjectName("ElementLabel")


class SB(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUI()

    def setupUI(self):

        self.setFixedSize(400, 60)
        self.setObjectName("SB")

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(10, 0, 0, 0)

        self.setLayout(layout)

        # <LOAD BUTTON>

        self.SB_load = QPushButton()
        self.SB_load.setObjectName("SBLoad")
        self.SB_load.setFixedSize(180, 30)
        self.SB_load.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # self.SB_load.clicked.connect()

        icon = QLabel(self.SB_load)
        icon.setGeometry(5, 5, 20, 20)
        icon.setPixmap(QPixmap("src/icons/dark/load.png").scaled(20, 20))

        self.img = QLabel(self.SB_load)
        self.img.setObjectName("SBName")
        self.img.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.img.setText("None")
        self.img.setGeometry(30, 0, 150, 30)

        layout.addWidget(self.SB_load)

        # </LOAD BUTTON>

        # <HIDE BUTTON>

        self.hide_button = QPushButton()
        self.hide_button.setObjectName("SBHide")
        self.hide_button.setFixedSize(30, 20)
        self.hide_button.setIcon(QIcon("src/icons/dark/close.png"))
        self.hide_button.setIconSize(QSize(30, 20))

        layout.addWidget(self.hide_button)

        # </HIDE BUTTON>

        # <OPACITY AREA>

        opWidget = QWidget()
        opWidget.setObjectName("opSB")
        opWidget.setFixedSize(150, 30)

        opLayout = QHBoxLayout()
        opLayout.setAlignment(Qt.AlignCenter)
        opLayout.setContentsMargins(0, 0, 0, 0)
        opLayout.setSpacing(0)

        opWidget.setLayout(opLayout)

        self.opacity = QSpinBox()
        self.opacity.setMinimum(0)
        self.opacity.setMaximum(999)
        self.opacity.setButtonSymbols(2)
        self.opacity.valueChanged.connect(self.trim)
        self.opacity.setObjectName("OpacityInput")
        self.opacity.setFixedSize(100, 30)
        self.opacity.setSuffix("%")
        self.opacity.setAlignment(Qt.AlignCenter)

        opacity_layout = QHBoxLayout()
        opacity_layout.setAlignment(Qt.AlignRight)
        opacity_layout.setSpacing(0)
        opacity_layout.setContentsMargins(0, 0, 0, 0)

        self.opacity.setLayout(opacity_layout)

        self.sliderbutton = QPushButton("↑")
        self.sliderbutton.setObjectName("SliderButton")
        self.sliderbutton.setFixedSize(30, 30)
        self.sliderbutton.clicked.connect(self.slider_status)

        opacity_layout.addWidget(self.sliderbutton)

        layout.addWidget(self.opacity)

        # </OPACITY AREA>

        self.update()

    def trim(self):
        nosuff = self.opacity.text()[-1:]
        if len(nosuff) > 1 and nosuff[0] == "0":
            self.opacity.setValue(int(nosuff[1:]))
        elif self.opacity.value() > 100:
            self.opacity.setValue(100)

        self.parent().slider.setSliderPosition(self.opacity.value())

    def slider_status(self):
        if self.sliderbutton.text() == "↑":
            self.parent().slider_change(1)
            self.sliderbutton.setText("↓")
        else:
            self.parent().slider_change(0)
            self.sliderbutton.setText("↑")


class SectionLabel(QLabel):
    def __init__(self, name, parent=None):
        super().__init__(parent=parent)

        self.setText(name)
        self.setFixedSize(400, 20)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("SectionLabel")


class Slider(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hide()

        self.setFixedSize(100, 30)
        self.setObjectName("Slider")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setOrientation(Qt.Horizontal)
        self.valueChanged.connect(self.change_op)
        self.setMinimum(0)
        self.setMaximum(100)

        with open("src/style/dark/slider.css") as style:
            self.setStyleSheet(style.read())

        self.update()

    def change_op(self):
        self.parent().side_panel.change_op()
