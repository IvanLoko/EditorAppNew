from PyQt5.QtCore import QMimeData, Qt, QPoint
from PyQt5.QtGui import QPen, QTransform, QBrush
from PyQt5.QtWidgets import QLabel, QGraphicsRectItem, QGraphicsView
from qtpy import QtGui

import numpy as np


class SimpleRect(QGraphicsRectItem):

    def __init__(self, x_start, y_start, x_finish, y_finish, object_name=''):
        super().__init__()
        self.objlect_name = object_name
        self.setRect(min(x_start, x_finish),
                     min(y_start, y_finish),
                     np.abs(x_start - x_finish),
                     np.abs(y_start - y_finish))
        pen = QPen()
        pen.setColor(Qt.white)
        pen.setWidth(2)
        self.setPen(pen)


class SimplePoint(QGraphicsRectItem):

    def __init__(self, geom, object_name=''):
        super().__init__()

        self.setRect(int(geom[0] / 4), int(geom[1] / 4), 7, 7)
        self.object_name = object_name
        pen = QPen()
        pen.setColor(Qt.white)
        pen.setWidth(2)
        self.setPen(pen)


class SL(QLabel):

    def __init__(self,parent=None, pos=None, name=None):
        super().__init__(parent=parent)
        self.setText(name)
        self.setStyleSheet('background-color: white')
        self.move(pos)
        self.show()
