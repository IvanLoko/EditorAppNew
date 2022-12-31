from time import sleep

import matplotlib.pyplot as plt
from PyQt5 import QtCore
from PyQt5.QtCore import QRect, QMimeData, Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QListWidget
from qtpy import QtGui

import numpy as np

from canvas import Canvas


class simpleRect(QLabel):

    def __init__(self, parent=None, parent_class=None, x=None, y=None, w=None, h=None):
        self.label = parent_class
        super(QLabel, self).__init__(parent)
        self.setStyleSheet('border: 3px solid white')
        self.setGeometry(x, y, w - x, h - y)
        self.show()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.buttons() != Qt.RightButton:
            mimeData = QMimeData()
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(ev.pos() - self.rect().topLeft())

            drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, ev):

        if ev.button() == Qt.LeftButton:
            self.setStyleSheet('border: 3px solid black')

        self.label.call(self)


class simplePoint(QLabel):

    def __init__(self, parent=None, parent_class=None, geom=None):
        super(QLabel, self).__init__(parent)
        self.parent_class = parent_class
        self.setStyleSheet('border: 1px solid red; background-color: rgb(100,100,100);')
        self.setGeometry(geom[0] / 4, geom[1] / 4, 7, 7)
        self.show()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.buttons() != Qt.RightButton:
            mimeData = QMimeData()

            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(ev.pos() - self.rect().topLeft())

            drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, ev):
        QLabel.mousePressEvent(self, ev)

        if ev.button() == Qt.LeftButton:
            self.setStyleSheet('border: 3px solid black')

        self.parent_class.call(self)
        print(self.parent_class.current_object)


class Label(QLabel):

    def __init__(self, image, parent=None, ):
        super().__init__(parent=parent)

        self.image = image
        pixmap = QPixmap(self.image.path).scaled(1200, 800)
        self.setPixmap(pixmap)
        self.objects = []
        self.current_object = None
        self.start, self.finish = QtCore.QPoint(), QtCore.QPoint()
        self.points = None
        self.setAcceptDrops(True)

    def add_widget(self):
        self.objects.append(simpleRect(self, self, *self.points))
        self.current_object = -1

    def add_points(self, points: list):
        for point in points:
            self.objects.append(simplePoint(self, self, point))

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.start = event.pos()
            self.finish = self.start
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() and QtCore.Qt.LeftButton:
            self.finish = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() and QtCore.Qt.LeftButton:

            rect = QRect(self.start, self.finish)
            painter = QPainter(self)
            painter.drawRect(rect.normalized())
            self.points = np.array([self.start.x(),
                                    self.start.y(),
                                    self.finish.x(),
                                    self.finish.y()])
            self.start, self.finish = QtCore.QPoint(), QtCore.QPoint()

            self.add_widget()

            dots = self.image.pins2json(self.points * 4)
            self.add_points(points=dots)
            self.parent().to_points_elements(self.points)
            self.parent().to_points_dots(dots)
            self.parent().next_item()


    def paintEvent(self, event):
        super(Label, self).paintEvent(event)
        painter = QPainter(self)
        if not self.start.isNull() and not self.finish.isNull():
            rect = QRect(self.start, self.finish)
            painter.drawRect(rect.normalized())

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):

        position = e.pos()
        self.objects[self.current_object].move(position)

        e.setDropAction(QtCore.Qt.MoveAction)
        e.accept()

    def call(self, child_class=None):
        self.current_object = self.objects.index(child_class)



