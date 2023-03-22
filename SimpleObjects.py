from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsSimpleTextItem

import numpy as np


class SimpleRect(QGraphicsRectItem):
    """Обозначение корпуса микросхемы"""

    def __init__(self, x_start, y_start, x_finish, y_finish, object_name=''):
        super().__init__()
        self.object_name = object_name
        self.setRect(min(x_start, x_finish),
                     min(y_start, y_finish),
                     np.abs(x_start - x_finish),
                     np.abs(y_start - y_finish))
        pen = QPen()
        pen.setColor(Qt.white)
        pen.setWidth(2)
        self.setPen(pen)

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event) -> None:
        """При наведении курсора мыши на объект, будет показано его имя"""
        x = self.rect().x() + self.pos().x()
        y = self.rect().y() - 20 + self.pos().y()
        self.scene().addItem(SL((x, y), text=self.object_name))

    def hoverLeaveEvent(self, event):
        """Как только курсор покидает область объекта, удаляет текст его имени"""
        [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, SL)]

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        """Перемещение объекта по сцене"""
        pos = event.lastScenePos()
        upd_pos = event.scenePos()

        orig_pos = self.scenePos()

        upd_x = upd_pos.x() - pos.x() + orig_pos.x()
        upd_y = upd_pos.y() - pos.y() + orig_pos.y()
        [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, SL)]
        self.setPos(QPointF(upd_x, upd_y))

    def mouseReleaseEvent(self, event):
        pass


class SimplePoint(QGraphicsRectItem):
    """Обозначение выводов микросхемы"""

    def __init__(self, geom, object_name=''):
        super().__init__()

        self.setRect(int(geom[0] / 4), int(geom[1] / 4), 7, 7)
        self.object_name = object_name

        pen = QPen()
        if self.object_name.split('_')[-1] == '1':
            pen.setColor(Qt.red)
        else:
            pen.setColor(Qt.white)
        pen.setWidth(2)
        self.setPen(pen)

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event) -> None:
        """При наведении курсора мыши на объект, будет показано его имя"""
        x = self.rect().x() + self.pos().x()
        y = self.rect().y() - 20 + self.pos().y()
        self.scene().addItem(SL((x, y), text=self.object_name))

    def hoverLeaveEvent(self, event):
        """Как только курсор покидает область объекта, удаляет текст его имени"""
        [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, SL)]

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        """Перемещение объекта по сцене"""
        pos = event.lastScenePos()
        upd_pos = event.scenePos()

        orig_pos = self.scenePos()

        upd_x = upd_pos.x() - pos.x() + orig_pos.x()
        upd_y = upd_pos.y() - pos.y() + orig_pos.y()
        [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, SL)]
        self.setPos(QPointF(upd_x, upd_y))

    def mouseReleaseEvent(self, event):
        pass


class SL(QGraphicsSimpleTextItem):
    """Класс для отображения имени объекта"""

    def __init__(self, pos=None, text=None):
        super().__init__()
        self.setText(text)
        self.setPos(*pos)
        self.setBrush(QBrush(Qt.red))
        self.show()
