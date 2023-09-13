from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from errors import NonePointError
from simple_objects import SimplePoint


class ConfDialog(QDialog):

    def __init__(self, pins, view):

        super(ConfDialog, self).__init__()
        uic.loadUi('ConfDialog.ui', self)

        self.pins = pins
        self.scene = view.scene()
        self.points = view.points
        self.mainwindow = view.mainwindow
        self.status = True

        self.grip_position = QPoint(0, 0)

        # Fix alignment
        self.horizontalLayout_2.setAlignment(Qt.AlignRight | Qt.AlignHCenter)
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Set starting position
        self.ConfSlider.setValue(25)
        self.ConfSpinBox.setValue(25)

        # Show pins
        for pin in self.pins:
            pin.setVisible(True)

        # Connect widgets
        self.OkayButton.clicked.connect(self.okay)
        self.CancelButton.clicked.connect(self.close_window)
        self.CloseButton.clicked.connect(self.close_window)
        self.ConfSlider.valueChanged.connect(self.re_predict)
        self.ScreenshotButton.clicked.connect(self.screenshot)

        self.TitleBar.mousePressEvent = self.press_window
        self.TitleBar.mouseMoveEvent = self.move_window

    def okay(self):
        """ Set points visibility and close """

        visibility = self.mainwindow.pins_status

        for pin in self.pins:
            pin.setVisible(visibility)

        self.close()

    def close_window(self):
        """ Clear pins and close window """

        for pin in self.pins:
            self.scene.removeItem(pin)

        self.pins.clear()
        self.close()
        self.status = False

    def press_window(self, event):
        """ Get grip position before moving """

        self.grip_position = event.pos()

    def move_window(self, event):
        """ Move ConfDialog when gripped """

        self.move(
            self.pos().x() + event.pos().x() - self.grip_position.x(),
            event.pos().y() + self.pos().y() - self.grip_position.y()
        )

    def re_predict(self):
        self.ConfSpinBox.setValue(self.ConfSlider.value())

        for pin in self.pins:
            self.scene.removeItem(pin)

        self.pins.clear()

        try:
            dots = self.scene.canvas.pins2json(self.points, confidence=self.ConfSlider.value() / 100)

        except NonePointError:
            return

        except Exception:
            return

        for num, point in enumerate(dots):
            name = f'{self.mainwindow.TreeListWidget.currentItem().text(0)}_{num + 1}'
            pin = SimplePoint(point, object_name=name, visible_status=True)
            self.scene.addItem(pin)
            self.pins.append(pin)

    def screenshot(self):

        rect = QRect(min(self.points[0], self.points[2]),
                     min(self.points[1], self.points[3]),
                     abs(self.points[0] - self.points[2]),
                     abs(self.points[1] - self.points[3]))

        image = self.scene.pixmap.copy(rect)
        image.save(f"screenshots/{self.points[0], self.points[1], self.points[2], self.points[3]}.png", "PNG")
