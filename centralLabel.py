import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import QRect, Qt, QEvent, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QBrush, QPen, QColor
from PyQt5.QtWidgets import QLabel

from SimpleObjects import SimpleRect, SimplePoint, SL

import numpy as np
from errors import *


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
        self.lab = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            pos = obj.pos()
            pos = QPoint(pos.x(), pos.y() - 20)
            print(obj)
            self.lab = SL(self, pos=pos, name=obj.objectName())
            self.lab.show()
            return True
        if event.type() == QEvent.Leave:
            self.lab.deleteLater()
            self.update()
        return False

    def add_widget(self):
        name = self.parent().elements_list.currentItem().text()
        self.objects.append(SimpleRect(self, *self.points, object_name=name))
        self.current_object = -1

    def add_points(self, points: list):
        for num, point in enumerate(points):
            name = f'{self.parent().elements_list.currentItem().text()}_{num + 1}'
            self.objects.append(SimplePoint(self, point, name))

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.start = event.pos()
            self.finish = self.start
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() and QtCore.Qt.LeftButton:
            self.finish = event.pos()
            self.borderCheck()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() and QtCore.Qt.LeftButton:
            self.points = np.array([self.start.x(),
                                    self.start.y(),
                                    self.finish.x(),
                                    self.finish.y()])
            if self.start == self.finish:
                return
            self.start, self.finish = QtCore.QPoint(), QtCore.QPoint()
            try:
                dots = self.image.pins2json(self.points * 4)
                self.parent().next_item()
                self.add_widget()
                self.add_points(points=dots)
            except NonePointError:
                self.parent().set_line('There is no points in area', 'rgb(237, 28, 36)')
            except cv2.error:
                self.parent().set_line('Incorrect area', 'rgb(237, 28, 36)')
            except IndexError:
                self.parent().set_line('smth wrong but idk what', 'rgb(237, 28, 36)')
            except AttributeError:
                self.parent().set_line('Set element in element list', 'rgb(237, 28, 36)')

    def borderCheck(self):
        if self.finish.x() < 1:
            self.finish.setX(1)
        elif self.finish.x() > self.width() - 3:
            self.finish.setX(self.width() - 3)
        if self.finish.y() < 1:
            self.finish.setY(1)
        elif self.finish.y() > self.height() - 3:
            self.finish.setY(self.height() - 3)

    def paintEvent(self, event):
        super(Label, self).paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, Qt.SolidLine, ))
        painter.setBrush(QBrush(Qt.black, Qt.DiagCrossPattern))
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
