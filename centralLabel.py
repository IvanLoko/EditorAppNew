import cv2
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap, QBrush, QPen, QTransform, QColor
from PyQt5.QtWidgets import QLabel, QApplication, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsRectItem, \
    QGraphicsItem

from SimpleObjects import SimpleRect, SimplePoint
from canvas import Canvas
import numpy as np
from errors import *


class GraphicsScene(QGraphicsScene):
    """Интерактивная область для разметки и работы с элементами на отдельном фото ОД"""
    itemClicked = pyqtSignal(QGraphicsItem)
    itemMoved = pyqtSignal(dict)

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

        self.setObjectName("GraphicsView")
        with open("src/style/dark/graphics_view.css") as style:
            self.setStyleSheet(style.read())

        self.transform_func = QTransform()
        # Ширина прямоугольника для тела микросхемы
        self.div = 0
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
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        """В режиме standard:
                - Pass
           В режиме AI:
                - Задает стартовую точку отрисовки прямоугольника"""

        if self.mod == 'standard':
            self.start = self.mapToScene(event.pos())

        elif self.mod == 'AI' and type(self.itemAt(event.pos())) == QGraphicsPixmapItem:
            if event.button() == Qt.LeftButton:
                self.start = self.mapToScene(event.pos())
                self.finish = self.start
                self.update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Правая кнопка мыши Всегда отвечает за перемеения по фото, внезависимости от выбранного мода
            В режиме standard:
                - Pass
            В режиме AI:
                Отрисовка прямоугольника при выделении области"""

        if event.buttons() == Qt.RightButton:
            self.transform_func.translate(-event.pos().x(), -event.pos().y())
            self.setTransform(self.transform_func)

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

                # Дорисовать второй четырехугольник меньшей ширины для тела микросхемы
                self.div = finish_x * 0.25
                circ_rect = QGraphicsRectItem(QRectF(start_x + self.div, start_y, finish_x - (self.div*2), finish_y))
                circ_rect.setPen(QPen(Qt.red, 2))
                self.scene().addItem(circ_rect)

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
                    # Достать информацию о кол-ве пинов из points для проверки
                    name = self.parent().elements_list.currentItem().text()
                    total_points = len(self.parent().dict['Elements'][name]['Pins'].keys())
                    # Поиск пинов
                    dots = self.scene().canvas.pins2json(self.points)
                    # Создание SimpleRect
                    self.add_rect()
                    # Создание SimplePoint
                    self.add_points(points=dots)
                    self.parent().next_item()

                    if len(dots) == total_points:
                        self.parent().set_line(
                            f'Placed object {name} at {self.start.x(), self.start.y()} with {len(dots)} out of total {total_points} points',
                            Qt.darkGreen)
                    else:
                        self.parent().set_line(
                            f'Placed object {name} at {self.start.x(), self.start.y()} with {len(dots)} out of total {total_points} points (Wrong element or prediction)',
                            Qt.red)
                except NonePointError:
                    self.parent().set_line('There is no points in area', Qt.red)
                except cv2.error:
                    self.parent().set_line('Incorrect area', Qt.red)
                except IndexError:
                    # IndexError = index 0 is out of bounds for axis 0 with size 0)
                    self.parent().set_line('smth wrong but idk what', Qt.red)
                except TypeError:
                    self.parent().set_line('(x_start <= x_finish or y_start <= y_finish) == True,  vpadlu fixitj :)',
                                           Qt.red)
                except AttributeError:
                    self.parent().set_line('Set element in element list', Qt.darkYellow)

            self.start = QPoint()
            self.finish = QPoint()
        print('sssss_')
        super().mouseReleaseEvent(event)

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
        if self.start.x() > self.finish.x():
            self.div = -self.div
        self.rect = SimpleRect(self.start.x() + self.div, self.start.y(), self.finish.x() - self.div, self.finish.y(),
                          object_name=name)
        print(self.start.x(), self.finish.x())
        self.rect.z_rect = QRectF(min(self.start.x(), self.finish.x()),
                                  min(self.start.y(), self.finish.y()),
                                  np.abs(self.start.x() - self.finish.x()),
                                  np.abs(self.start.y() - self.finish.y()))
        self.scene().addItem(self.rect)

    def add_points(self, points: list):
        """Создание SimplePoint"""
        for num, point in enumerate(points):
            name = f'{self.parent().elements_list.currentItem().text()}_{num + 1}'
            self.scene().addItem(
                SimplePoint(point, object_name=name, visible_status=self.parent().tool_bar.visible_status, parent_rect=self.rect))
