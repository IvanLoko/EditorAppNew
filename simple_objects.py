from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np


class SimpleRect(QGraphicsRectItem):
    """Обозначение корпуса микросхемы"""

    def __init__(self, x_start, y_start, x_finish, y_finish, object_name='', mod='AI'):

        super().__init__()
        self.object_name = object_name
        self.setRect(min(x_start, x_finish),
                     min(y_start, y_finish),
                     np.abs(x_start - x_finish),
                     np.abs(y_start - y_finish))
        pen = QPen()
        pen.setColor(QColor("#33bd44"))
        pen.setWidth(2)
        self.setPen(pen)
        self.setCursor(Qt.SizeAllCursor)
        self.rect_mod = mod

        if self.rect_mod == 'AI':
            self.setRect(self.rect().adjusted(
                self.rect().width() * 0.25, 0,
                self.rect().width() * -0.25, 0
            ))

        self.setAcceptHoverEvents(True)

        self.start, self.finish = None, None
        self.status = None
        self.anchors = {
            "topLeft": [QRectF(self.boundingRect().x(), self.boundingRect().y(), 5, 5), Qt.SizeFDiagCursor],
            "topRight": [QRectF(self.boundingRect().x() + self.boundingRect().width() - 5, self.boundingRect().y(), 5, 5), Qt.SizeBDiagCursor],
            "bottomRight": [QRectF(self.boundingRect().x() + self.boundingRect().width() - 5, self.boundingRect().y() + self.boundingRect().height() - 5, 5, 5), Qt.SizeFDiagCursor],
            "bottomLeft": [QRectF(self.boundingRect().x(), self.boundingRect().y() + self.boundingRect().height() - 5, 5, 5), Qt.SizeBDiagCursor],
            "left": [QRectF(self.boundingRect().x(), self.boundingRect().y() + 5, 5, self.boundingRect().height() - 10), Qt.SizeHorCursor],
            "top": [QRectF(self.boundingRect().x() + 5, self.boundingRect().y(), self.boundingRect().width() - 10, 5), Qt.SizeVerCursor],
            "right": [QRectF(self.boundingRect().x() + self.boundingRect().width() - 5, self.boundingRect().y() + 5, 5, self.boundingRect().height() - 10), Qt.SizeHorCursor],
            "bottom": [QRectF(self.boundingRect().x() + 5, self.boundingRect().y() + self.boundingRect().height() - 5, self.boundingRect().width() - 10, 5), Qt.SizeVerCursor],
        }

        for rect in self.anchors.keys():
            self.anchor = AnchorRect(self, rect, self.anchors.get(rect))

    def anchor_drag(self, anchor, pos):

        self.anchors = {
            "topLeft": [QRectF(self.boundingRect().x(), self.boundingRect().y(), 5, 5), Qt.SizeFDiagCursor],
            "topRight": [QRectF(self.boundingRect().x() + self.boundingRect().width() - 5, self.boundingRect().y(), 5, 5), Qt.SizeBDiagCursor],
            "bottomRight": [QRectF(self.boundingRect().x() + self.boundingRect().width() - 5, self.boundingRect().y() + self.boundingRect().height() - 5, 5, 5),  Qt.SizeFDiagCursor],
            "bottomLeft": [QRectF(self.boundingRect().x(), self.boundingRect().y() + self.boundingRect().height() - 5, 5, 5), Qt.SizeBDiagCursor],
            "left": [QRectF(self.boundingRect().x(), self.boundingRect().y() + 5, 5, self.boundingRect().height() - 10), Qt.SizeHorCursor],
            "top": [QRectF(self.boundingRect().x() + 5, self.boundingRect().y(), self.boundingRect().width() - 10, 5), Qt.SizeVerCursor],
            "right": [QRectF(self.boundingRect().x() + self.boundingRect().width() - 5, self.boundingRect().y() + 5, 5, self.boundingRect().height() - 10), Qt.SizeHorCursor],
            "bottom": [QRectF(self.boundingRect().x() + 5, self.boundingRect().y() + self.boundingRect().height() - 5, self.boundingRect().width() - 10, 5), Qt.SizeVerCursor],
        }
        x, y = pos.x(), pos.y()

        if anchor.location == "left":
            self.setRect(self.rect().adjusted(x - self.rect().x(), 0, 0, 0))
            self.flip_checker(side1="left")
        if anchor.location == "top":
            self.setRect(self.rect().adjusted(0, y - self.rect().y(), 0, 0))
            self.flip_checker(side2="top")
        if anchor.location == "right":
            self.setRect(self.rect().adjusted(0, 0, x - self.rect().x() - self.rect().width(), 0))
            self.flip_checker(side1="right")
        if anchor.location == "bottom":
            self.setRect(self.rect().adjusted(0, 0, 0, y - self.rect().y() - self.rect().height()))
            self.flip_checker(side2="bottom")
        if anchor.location == "topLeft":
            self.setRect(self.rect().adjusted(x - self.rect().x(), y - self.rect().y(), 0, 0))
            self.flip_checker("left", "top")
        if anchor.location == "topRight":
            self.setRect(self.rect().adjusted(0, y - self.rect().y(), x - self.rect().x() - self.rect().width(), 0))
            self.flip_checker("right", "top")
        if anchor.location == "bottomRight":
            self.setRect(self.rect().adjusted(0, 0, x - self.rect().x() - self.rect().width(),
                                              y - self.rect().y() - self.rect().height()))
            self.flip_checker("right", "bottom")
        if anchor.location == "bottomLeft":
            self.setRect(self.rect().adjusted(x - self.rect().x(), 0, 0, y - self.rect().y() - self.rect().height()))
            self.flip_checker("left", "bottom")

        for el in self.childItems():
            # if type(el) == AnchorRect:
            el.setRect(self.anchors[el.location][0])

        [item.setPos(self.rect().x(), self.rect().y() - 30) for item in self.scene().items() if isinstance(item, SL)]

    def flip_checker(self, side1=None, side2=None):
        if side1 == "left" and self.rect().width() < 10:
            rect = self.rect()
            rect.setLeft(rect.right() - 10)
            self.setRect(rect)

        elif side1 == "right" and self.rect().width() < 10:
            rect = self.rect()
            rect.setRight(rect.left() + 10)
            self.setRect(rect)

        if side2 == "top" and self.rect().height() < 10:
            rect = self.rect()
            rect.setTop(rect.bottom() - 10)
            self.setRect(rect)

        if side2 == "bottom" and self.rect().height() < 10:
            rect = self.rect()
            rect.setBottom(rect.top() + 10)
            self.setRect(rect)

    def hoverEnterEvent(self, event) -> None:
        """При наведении курсора мыши на объект, будет показано его имя"""

        x = self.mapRectToScene(self.rect()).x()
        y = self.mapRectToScene(self.rect()).y() - 30
        self.scene().addItem(SL((x, y), text=self.object_name, size=10))

        pen = QPen()
        pen.setColor(QColor("#44ce55"))
        pen.setWidth(2)
        self.setPen(pen)

    def hoverLeaveEvent(self, event):
        """Как только курсор покидает область объекта, удаляет текст его имени"""

        [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, SL)]

        pen = QPen()
        pen.setColor(QColor("#33bd44"))
        pen.setWidth(2)
        self.setPen(pen)


class SimplePoint(QGraphicsRectItem):
    """Обозначение выводов микросхемы"""

    def __init__(self, geom, object_name='', visible_status=True):
        super().__init__()

        self.setVisible(visible_status)

        self.setRect(geom[0] - 4, geom[1] - 4, 8, 8)
        self.object_name = object_name
        self.setCursor(Qt.SizeAllCursor)

        self.font_size = 6
        self.shift_right = 10
        self.shift_left = -10 - (len(self.object_name) * 3)
        self.shift_y = -3

        self.font_size = 6
        self.shift = (10, -3)

        pen = QPen()
        if self.object_name.split('_')[-1] == '1':
            pen.setColor(QColor("#FF2222"))
        else:
            pen.setColor(QColor("#33bd44"))

        pen.setWidth(2)
        self.setPen(pen)

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event) -> None:
        """При наведении курсора мыши на объект, будет показано его имя"""

        x = self.mapRectToScene(self.rect()).x() + self.shift_right
        y = self.mapRectToScene(self.rect()).y() + self.shift_y
        if self.isVisible():
            self.scene().addItem(SL((x, y), text=self.object_name, size=self.font_size))

        if self.object_name.split('_')[-1] == '1':
            return

        pen = QPen()
        pen.setColor(QColor("#44ce55"))
        pen.setWidth(2)
        self.setPen(pen)

    def hoverLeaveEvent(self, event):
        """Как только курсор покидает область объекта, удаляет текст его имени"""

        [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, SL)]

        if self.object_name.split('_')[-1] == '1':
            return

        pen = QPen()
        pen.setColor(QColor("#33bd44"))
        pen.setWidth(2)
        self.setPen(pen)


class SL(QGraphicsSimpleTextItem):
    """Класс для отображения имени объекта"""

    def __init__(self, pos=None, text=None, size=6):
        super().__init__()
        self.setText(text)
        self.setPos(*pos)
        self.setBrush(QBrush(QColor("#33bd44")))
        self.setFont(QFont("Cascadia", size))
        self.show()


class AnchorRect(QGraphicsRectItem):
    def __init__(self, parent, location, properties):
        super().__init__(parent=parent)

        self.location = location

        self.setRect(properties[0])
        self.setCursor(properties[1])
        self.setPen(QPen(Qt.gray, 0))
        self.setOpacity(0.01)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        self.parentItem().anchor_drag(self, event.pos())

    def mouseReleaseEvent(self, event):
        pass
