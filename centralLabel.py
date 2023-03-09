import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import QRect, Qt, QEvent, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QBrush, QPen, QColor
from PyQt5.QtWidgets import QLabel, QApplication

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
        self.modifiers = None
        self.selected_objects = []
        self.enter = None

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

    def clear_selection(self):
        self.selected_objects = []
        # Restore Simple objects' stylesheet
        pass

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.modifiers = QApplication.keyboardModifiers()
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
            self.clear_selection()
            if self.start == self.finish:
                return
            self.start, self.finish = QtCore.QPoint(), QtCore.QPoint()

            if self.modifiers == Qt.ShiftModifier:

                for el in self.objects:
                    # Диапазоны горизонтальных и вертикальных сторон четырехугольника
                    rangex = range(min(self.points[0], self.points[2]), max(self.points[0], self.points[2]))
                    rangey = range(min(self.points[1], self.points[3]), max(self.points[1], self.points[3]))

                    # Проверить, пересекается ли х,y Simple объекта с x,y зоны выделения
                    if set(range(el.x(), el.x() + el.width())).intersection(rangex) \
                            and set(range(el.y(), el.y() + el.height())).intersection(rangey):
                        el.setStyleSheet('border: 3px solid black; font-size: 12pt; color: #AEE8F5;')
                        self.selected_objects.append(el)

            # Если ни одна клавиша не была нажата, выполнить разметку
            else:
                try:
                    dots = self.image.pins2json(self.points * 4)
                    self.add_widget()
                    self.add_points(points=dots)
                    self.parent().next_item()
                except NonePointError:
                    self.parent().set_line('There is no points in area', 'rgb(237, 28, 36)')
                except cv2.error:
                    self.parent().set_line('Incorrect area', 'rgb(237, 28, 36)')
                except IndexError:
                    self.parent().set_line('smth wrong but idk what', 'rgb(237, 28, 36)')
                except TypeError:
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
        self.enter = QPoint(e.pos().x() - self.objects[self.current_object].x(),
                            e.pos().y() - self.objects[self.current_object].y())

    def dragMoveEvent(self, e):

        position = e.pos()
        last_position = QPoint(self.objects[self.current_object].x() + self.enter.x(),
                               self.objects[self.current_object].y() + self.enter.y())

        # Если перенесенный элемент является выделенным, то перенести остальные выделенные элементы
        if self.objects[self.current_object] in self.selected_objects:
            for el in self.selected_objects:
                el.move(position.x() + (el.x() - last_position.x()),
                        position.y() + (el.y() - last_position.y()))
        else:
            self.objects[self.current_object].move(position.x() + (self.objects[self.current_object].x() - last_position.x()),
                                                   position.y() + (self.objects[self.current_object].y() - last_position.y()))
            self.clear_selection()

    def dropEvent(self, e):

        e.setDropAction(QtCore.Qt.MoveAction)
        e.accept()

    def call(self, child_class=None):
        self.current_object = self.objects.index(child_class)
