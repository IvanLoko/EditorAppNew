from PyQt5.QtCore import QMimeData, Qt
from PyQt5.QtWidgets import QLabel
from qtpy import QtGui

import numpy as np


class SimpleRect(QLabel):

    def __init__(self, parent, x_start, y_start, x_finish, y_finish, object_name: str):
        super(QLabel, self).__init__(parent)
        self.setStyleSheet('border: 3px solid white')
        self.setGeometry(min(x_start, x_finish),
                         min(y_start, y_finish),
                         np.abs(x_start - x_finish),
                         np.abs(y_start - y_finish))
        self.setObjectName(object_name)
        self.installEventFilter(parent)
        self.show()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.buttons() != Qt.RightButton:
            mime_data = QMimeData()
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(ev.pos() - self.rect().topLeft())

            drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, ev):

        if ev.button() == Qt.LeftButton:
            self.setStyleSheet('border: 3px solid black')

        self.parent().call(self)


class SimplePoint(QLabel):

    def __init__(self, parent, geom, object_name: str):
        super(QLabel, self).__init__(parent)
        self.setStyleSheet('border: 1px solid red; background-color: rgb(100,100,100);')
        self.setGeometry(geom[0] / 4, geom[1] / 4, 7, 7)
        self.setObjectName(object_name)
        self.installEventFilter(parent)
        self.show()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.buttons() != Qt.RightButton:
            mime_data = QMimeData()

            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(ev.pos() - self.rect().topLeft())

            drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, ev):
        QLabel.mousePressEvent(self, ev)

        if ev.button() == Qt.LeftButton:
            self.setStyleSheet('border: 3px solid black')

        self.parent().call(self)


class SL(QLabel):

    def __init__(self,parent=None, pos=None, name=None):
        super().__init__(parent=parent)
        self.setText(name)
        self.setStyleSheet('background-color: white')
        self.move(pos)
        self.show()