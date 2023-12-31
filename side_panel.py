from PyQt5.QtCore import Qt, QSize, QPointF, pyqtSignal, QRectF
from PyQt5.QtGui import QCursor, QPixmap, QIcon, QFont, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QPushButton, QSpinBox, QHBoxLayout, QSlider, QListWidgetItem, QCheckBox, QFileDialog, QGraphicsPixmapItem, QGraphicsObject, QListView


class SidePanel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setFixedSize(300, 1020)
        self.setObjectName("SidePanel")

        self.slider = Slider(self.parent())
        self.slider.move(1806, 975)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)

        self.setLayout(self.layout)

        # При перемещении в сетку родитель объекта !меняется! на владельца сетки

        self.layout.addWidget(SectionLabel("Список элементов", self))
        self.layout.addWidget(self.parent().elements_list)

        self.layout.addWidget(SectionLabel("Текущий элемент", self))
        self.layout.addWidget(self.parent().circuit_map)

        self.layout.addWidget(SectionLabel("Сборочный чертеж", self))

        with open("src/style/dark/side_panel.css") as style:
            self.setStyleSheet(style.read())

        self.update()

    def slider_change(self, status):
        self.slider.setVisible(status)

    def change_op(self):
        self.parent().sb.opacity.setValue(self.slider.sliderPosition())
        if self.parent().sb.hide_button.isChecked() and self.parent().sb.add_pic:
            self.parent().sb.add_pic.setOpacity(self.slider.sliderPosition() / 100)


class ListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setFixedSize(300, 615)
        self.setObjectName("ElementList")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAutoScroll(False)


class ElementLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # parent = SidePanel

        self.setupUI()

    def setupUI(self):

        self.setFixedSize(300, 240)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("ElementLabel")


class SB(QLabel):
    def __init__(self, parent=None, image_name=None):
        super().__init__(parent=parent)
        # parent() = SidePanel
        # true_parent = central_widget

        # image_name = scene img
        self.image_name = image_name

        self.true_parent = parent
        self.add_pic = None

        self.setupUI()
        self.hide()

    def setupUI(self):

        self.setFixedSize(300, 60)
        self.setObjectName("SB")

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(10, 0, 0, 0)

        self.setLayout(layout)

        # <LOAD BUTTON>

        self.SB_load = QPushButton()
        self.SB_load.setObjectName("SBLoad")
        self.SB_load.setFixedSize(100, 30)
        self.SB_load.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.SB_load.clicked.connect(self.sbLoad)

        icon = QPushButton(self.SB_load)
        icon.setObjectName("SBLoadIcon")
        icon.setGeometry(5, 5, 20, 20)
        icon.setIcon(QIcon("src/icons/dark/new_dark/SBLoad.png"))
        icon.setIconSize(QSize(20, 20))
        icon.clicked.connect(self.sbLoad)

        self.img = QLabel(self.SB_load)
        self.img.setObjectName("SBName")
        self.img.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.img.setText("None")
        self.img.setGeometry(30, 0, 150, 30)

        layout.addWidget(self.SB_load)

        # </LOAD BUTTON>

        # <HIDE BUTTON>

        self.hide_button = QCheckBox()
        self.hide_button.setObjectName("SBHide")
        self.hide_button.setFixedSize(15, 15)
        self.hide_button.setCheckable(False)

        layout.addWidget(self.hide_button)

        self.hide_button.clicked.connect(self.overlay)

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
        self.opacity.setValue(30)
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

    def sbLoad(self):
        # Загрузка сборочника к текущей сцене
        file_path = QFileDialog.getOpenFileName(None, "Выберите изображение", '', "Images (*.png *.jpg)")[0]. \
            replace('/', '\\')
        self.img.setText(file_path.split('\\')[-1])
        if self.add_pic:
            self.true_parent.graphics_view.scene().roll_back()
        self.add_pic = QGraphicsPixmapItem()
        add_pix = QPixmap(file_path)

        self.add_pic.setPixmap(add_pix)
        self.add_pic.setOpacity(self.opacity.value() / 100)
        self.true_parent.graphics_view.scene().addItem(self.add_pic)

        self.hide_button.setCheckable(True)
        self.hide_button.setChecked(True)

    def overlay(self):
        if self.add_pic:
            if self.hide_button.isChecked():
                # (self.opacity.value() = int(0:100); setOpacity(float(0:1))
                self.add_pic.setOpacity(self.opacity.value() / 100)
            else:
                self.add_pic.setOpacity(0)

    def trim(self):
        # nosuff = "x%".remove("%")
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

        for el in self.parent().findChildren(SB):
            el.sliderbutton.setText(self.sliderbutton.text())


class SectionLabel(QLabel):
    def __init__(self, name, parent=None):
        super().__init__(parent=parent)

        self.setText(name)
        self.setFixedSize(300, 35)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("SectionLabel")


class Slider(QSlider):
    def __init__(self, parent=None):
        # parent = central_widget
        super().__init__(parent=parent)
        self.hide()

        self.setFixedSize(100, 30)
        self.setObjectName("Slider")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setOrientation(Qt.Horizontal)
        self.setValue(20)
        self.valueChanged.connect(self.change_op)
        self.setMinimum(0)
        self.setMaximum(100)

        with open("src/style/dark/slider.css") as style:
            self.setStyleSheet(style.read())

        self.update()

    def change_op(self):
        self.parent().side_panel.change_op()


class ListWidgetItem(QListWidgetItem):
    def __init__(self, el: str = "Ошибка", el_type: str = "Тип не обнаружен", parent=None):

        super().__init__()

        self.widget = QWidget()
        self.widget.setFixedSize(300, 20)
        self.setSizeHint(QSize(300, 20))

        self.status = False
        self.status_color = self.background()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.el_label = ELLabel(el, parent)
        self.el_label.setFixedSize(100, 20)

        self.el_type_label = ELTypeLabel(el_type, parent)
        self.el_type_label.setFixedSize(200, 20)

        layout.addWidget(self.el_label)
        layout.addWidget(self.el_type_label)

        self.widget.setLayout(layout)


class ELLabel(QLabel):

    def __init__(self, el, parent):

        super().__init__()

        with open("src/style/neutral/item_el.css") as style:
            self.setStyleSheet(style.read())
            del style

        self.parent = parent

        self.setText(el)
        self.setObjectName("ItemWidgetEl")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setContentsMargins(3, 0, 0, 0)

    def enterEvent(self, event):
        """ Подсветить элемент, если он находится на текущей сцене """

        qitem = self.parent.elements_list.findItems(self.text(), Qt.MatchExactly)[0]
        if qitem.status:
            qitem.setBackground(QColor("#7AA5C2"))
        else:
            qitem.setBackground(QColor("#3661A0"))

        self.parent.highlight_graphic([qitem.text()], True)

    def leaveEvent(self, event):
        """ Отмена подсветки """
        qitem = self.parent.elements_list.findItems(self.text(), Qt.MatchExactly)[0]
        qitem.setBackground(qitem.status_color)

        self.parent.highlight_graphic([qitem.text()], False)


class ELTypeLabel(QLabel):

    def __init__(self, el_type, parent):
        
        super().__init__()

        with open("src/style/neutral/item_el.css") as style:
            self.setStyleSheet(style.read())
            del style

        self.parent = parent

        self.items = []

        self.setText(el_type)
        self.setObjectName("ItemWidgetElType")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setContentsMargins(3, 0, 0, 0)

    def enterEvent(self, event):
        """ Подсветить все элементы данного типа, находящиеся на текущей сцене """
        # Подсветка в листе элементов
        for item in range(self.parent.elements_list.count()):
            qitem = self.parent.elements_list.item(item)

            if isinstance(qitem, PinItem):
                continue

            if qitem.el_type_label.text() == self.text():
                if qitem.status:
                    qitem.setBackground(QColor("#7AA5C2"))
                    self.items.append(qitem.el_label.text())
                else:
                    qitem.setBackground(QColor("#3661A0"))

        # Подсветка QGraphicsView
        self.parent.highlight_graphic(self.items, True)

    def leaveEvent(self, event):
        """ Отмена подсветки """
        # Отмена подсветки в листе элементов
        for item in range(self.parent.elements_list.count()):
            qitem = self.parent.elements_list.item(item)

            if isinstance(qitem, PinItem):
                continue

            if qitem.el_type_label.text() == self.text():
                qitem.setBackground(qitem.status_color)

        # Отмена подсветки QGraphicsView
        self.parent.highlight_graphic(self.items, False)

        self.items.clear()


class PinItem(QListWidgetItem):

    def __init__(self, pin: str = "Ошибка", parent=None):
        
        super().__init__()

        self.parent = parent

        self.status = False
        self.status_color = self.background()

        self.setSizeHint(QSize(300, 15))

        self.pin_label = PinLabel(pin, parent)
        self.pin_label.setFixedSize(300, 15)


class PinLabel(QLabel):

    def __init__(self, pin, parent):
        
        super().__init__()

        with open("src/style/neutral/item_pin.css") as style:
            self.setStyleSheet(style.read())
            del style

        self.parent = parent

        self.items = []
        self.list_items = []

        self.setText(pin)
        self.setObjectName("PinLabel")
        self.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.setContentsMargins(20, 0, 0, 0)

    def enterEvent(self, event):
        pass

    def leaveEvent(self, event):
        pass
