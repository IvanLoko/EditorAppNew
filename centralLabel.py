import cv2
from PyQt5.QtCore import QRect, Qt, QEvent, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QBrush, QPen, QTransform, QColor
from PyQt5.QtWidgets import QLabel, QApplication, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsRectItem

from SimpleObjects import SimpleRect, SimplePoint
from canvas import Canvas
import numpy as np
from errors import *


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent, canvas: Canvas):
        super().__init__(parent=parent)
        self.canvas = canvas
        self.pic = QGraphicsPixmapItem()
        pixmap = QPixmap(canvas.path)
        w = pixmap.width()
        h = pixmap.height()
        self.kw = 4800 / w
        self.kh = 3200 / h
        self.pic.setPixmap(pixmap)
        self.addItem(self.pic)

    def roll_back(self):
        print(self.items())
        for item in self.items():
            print(item == self.pic)
            if item != self.pic and isinstance(item, QGraphicsPixmapItem):
                self.removeItem(item)
        print(self.items())


class GraphicsView(QGraphicsView):

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.transform_func = QTransform()
        self.zoom = 0
        self.start = QPoint()
        self.finish = QPoint()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.mod = 'AI'
        self.points = None

    def mouseMoveEvent(self, event):
        # item = self.itemAt(event.pos())
        # if item and not event.buttons():
        #     pen = QPen()
        #     pen.setWidth(2)
        #     pen.setColor(Qt.red)
        #
        #     for el in self.items():
        #         try:
        #             if el.object_name.split("_")[0] == item.object_name.split("_")[0]:
        #                 el.setPen(pen)
        #                 item_list = self.parent().elements_list.findItems(el.object_name.split("_")[0], Qt.MatchExactly)[0]
        #                 item_list.setBackground(QColor("#CC3322"))
        #         except AttributeError:
        #             continue

        if event.buttons() == Qt.RightButton:
            self.transform_func.translate(-event.pos().x(), -event.pos().y())
            self.setTransform(self.transform_func)

        if event.buttons() == Qt.LeftButton and self.mod == 'AI':
            if not self.start.isNull() and not self.finish.isNull():
                self.finish = self.mapToScene(event.pos())
                if self.items():
                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

                rect = QGraphicsRectItem(self.start.x(), self.start.y(),
                                         self.finish.x() - self.start.x(), self.finish.y() - self.start.y())
                self.scene().addItem(rect)
        super(GraphicsView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):

        if self.mod == 'standard':
            self.start = self.mapToScene(event.pos())

        elif self.mod == 'AI':
            if event.button() == Qt.LeftButton:
                self.start = self.mapToScene(event.pos())
                self.finish = self.start
                self.update()

    def mouseReleaseEvent(self, event) -> None:
        if self.mod == 'AI':
            if event.button() == Qt.LeftButton:
                [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                self.add_rect()

                self.points = np.array([self.start.x() * self.scene().kw,
                                        self.start.y() * self.scene().kh,
                                        self.finish.x() * self.scene().kw,
                                        self.finish.y() * self.scene().kh]).astype('int32')
                self.add_rect()

                if self.start == self.finish:
                    return

                try:
                    dots = self.scene().canvas.pins2json(self.points)
                    self.add_rect()
                    self.add_points(points=dots)
                    self.parent().next_item()
                except NonePointError:
                    self.parent().set_line('There is no points in area', Qt.red)
                except cv2.error:
                    self.parent().set_line('Incorrect area', Qt.red)
                except IndexError:
                    # IndexError = index 0 is out of bounds for axis 0 with size 0)
                    self.parent().set_line('smth wrong but idk what', Qt.red)
                except TypeError:
                    self.parent().set_line('(x_start <= x_finish or y_start <= y_finish) == True,  vpadlu fixitj :)', Qt.red)
                except AttributeError:
                    self.parent().set_line('Set element in element list', Qt.darkYellow)

            self.start = QPoint()
            self.finish = QPoint()

    def wheelEvent(self, event) -> None:
        scale = 1 + event.angleDelta().y() / 1200
        self.transform_func.scale(scale, scale)
        self.zoom += event.angleDelta().y()
        # if self.zoom < 0:
        #     self.resetTransform()
        #     self.transform_func = QTransform()
        #     self.zoom = 0
        #     return
        self.setTransform(self.transform_func)

    def add_rect(self):
        name = self.parent().elements_list.currentItem().text()
        rect = SimpleRect(self.start.x(), self.start.y(), self.finish.x(), self.finish.y(),
                          object_name=name)
        self.scene().addItem(rect)

    def add_points(self, points: list):
        for num, point in enumerate(points):
            name = f'{self.parent().elements_list.currentItem().text()}_{num + 1}'
            self.scene().addItem(SimplePoint(point, object_name=name))

    def borderCheck(self):
        if self.finish.x() < 1:
            self.finish.setX(1)
        elif self.finish.x() > self.width() - 3:
            self.finish.setX(self.width() - 3)
        if self.finish.y() < 1:
            self.finish.setY(1)
        elif self.finish.y() > self.height() - 3:
            self.finish.setY(self.height() - 3)
