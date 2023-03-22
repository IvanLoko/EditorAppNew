import cv2
from PyQt5.QtCore import QRect, Qt, QEvent, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QBrush, QPen, QTransform, QColor
from PyQt5.QtWidgets import QLabel, QApplication, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsRectItem

from SimpleObjects import SimpleRect, SimplePoint
from canvas import Canvas
import numpy as np
from errors import *


class GraphicsScene(QGraphicsScene):
    """Интерактивная область для разметки и работы с элементами на отдельном фото ОД"""
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
        """Возвращает исходное состояние сцены, как до наложения сборочного чертежа"""
        for item in self.items():
            if item != self.pic and isinstance(item, QGraphicsPixmapItem):
                self.removeItem(item)


class GraphicsView(QGraphicsView):
    """Класс для работы с множественными сценами GraphicsScene"""

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.transform_func = QTransform()
        # Угол поворота колеса мыши
        self.zoom = 0
        self.start = QPoint()
        self.finish = QPoint()
        # Все трансформации с помощью self.transform_func выполняются относительно местоположения курсора
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # AI - выделение объектов для сегментации пинов, standard - перемещение объектов по сцене, изменине размеров
        # объектов SimpleRect, SimplePoint
        self.mod = 'AI'
        self.points = None

    def mousePressEvent(self, event):
        """В режиме standard:
                - Pass
           В режиме AI:
                - Задает стартовую точку отрисовки прямоугольника"""

        if self.mod == 'standard':
            self.start = self.mapToScene(event.pos())
            super().mousePressEvent(event)

        elif self.mod == 'AI':
            if event.button() == Qt.LeftButton:
                self.start = self.mapToScene(event.pos())
                self.finish = self.start
                self.update()
        super().mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        """Правая кнопка мыши Всегда отвечает за перемеения по фото, внезависимости от выбранного мода
            В режиме standard:
                - Pass
            В режиме AI:
                Отрисовка прямоугольника при выделении области"""

        if event.buttons() == Qt.RightButton:
            self.transform_func.translate(-event.pos().x(), -event.pos().y())
            self.setTransform(self.transform_func)
        elif event.buttons() == Qt.LeftButton and self.mod == 'standard':
            super().mouseMoveEvent(event)

        elif event.buttons() == Qt.LeftButton and self.mod == 'AI':
            if not self.start.isNull() and not self.finish.isNull():
                self.finish = self.mapToScene(event.pos())
                if self.items():
                    # Удаление всех объектов типа QGraphicsRectItem, иначе при движении мыши будут отрисовываться все
                    # прямоугольники начиная от начальной точки
                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                start_x = min(self.start.x(), self.finish.x())
                start_y = min(self.start.y(), self.finish.y())
                finish_x = abs(self.finish.x() - self.start.x())
                finish_y = abs(self.finish.y() - self.start.y())
                rect = QGraphicsRectItem(start_x, start_y, finish_x, finish_y)
                self.scene().addItem(rect)
        super(GraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """В режиме standard:
                - Pass
            В режиме AI:
                - Создание экземпляров SimpleRect, SimplePoint
                - """
        if self.mod == 'AI':
            if event.button() == Qt.LeftButton:
                # Удаляем отрисованный прямоугольник из mouseMoveEvent
                [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                # Координаты будущего SimpleRect
                self.points = np.array([self.start.x() * self.scene().kw,
                                        self.start.y() * self.scene().kh,
                                        self.finish.x() * self.scene().kw,
                                        self.finish.y() * self.scene().kh]).astype('int32')
                # обработка обычного клика мышью
                if self.start == self.finish:
                    return

                try:
                    # Поиск пинов
                    dots = self.scene().canvas.pins2json(self.points)
                    # Создание SimpleRect
                    self.add_rect()
                    # Создание SimplePoint
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
        """Мастабирование с помощью колеса мыши внезависимости от режима"""

        scale = 1 + event.angleDelta().y() / 1200
        self.transform_func.scale(scale, scale)
        self.zoom += event.angleDelta().y()
        # Раскоментировать, если вкл. не отдалять дальше исходного размера
        # if self.zoom < 0:
        #     self.resetTransform()
        #     self.transform_func = QTransform()
        #     self.zoom = 0
        #     return
        self.setTransform(self.transform_func)

    def add_rect(self):
        """Создание SimpleRect"""
        name = self.parent().elements_list.currentItem().text()
        rect = SimpleRect(self.start.x(), self.start.y(), self.finish.x(), self.finish.y(),
                          object_name=name)
        self.scene().addItem(rect)

    def add_points(self, points: list):
        """Создание SimplePoint"""
        for num, point in enumerate(points):
            name = f'{self.parent().elements_list.currentItem().text()}_{num + 1}'
            self.scene().addItem(SimplePoint(point, object_name=name))
