import cv2
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap, QBrush, QPen, QTransform, QColor, QMouseEvent
from PyQt5.QtWidgets import QLabel, QApplication, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsRectItem, \
    QGraphicsItem

from SimpleObjects import SimpleRect, SimplePoint, CropItem
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
        # scaledToWidth(self.parent().width())
        w = pixmap.width()
        h = pixmap.height()
        self.kw = 4800 / w
        self.kh = 3200 / h
        self.pic.setPixmap(pixmap)
        self.addItem(self.pic)
        self.setSceneRect(QRectF(0, 0, w, h))

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
        # Выбранные элементы
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

        if event.button() == Qt.RightButton:
            _event = QMouseEvent(event.type(), event.pos(), Qt.LeftButton, Qt.LeftButton, event.modifiers())
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().mousePressEvent(_event)
            event.accept()

        if self.mod == 'standard' and event.button() == Qt.LeftButton:
            self.start = self.mapToScene(event.pos())
            self.finish = self.start

        elif self.mod == 'AI' and type(self.itemAt(event.pos())) == QGraphicsPixmapItem:
            if event.button() == Qt.LeftButton:
                self.start = self.mapToScene(event.pos())
                self.finish = self.start
                self.cropItem = CropItem(self.scene().pic, event.pos(), event.pos())

        elif event.buttons() == Qt.RightButton | Qt.LeftButton:
            [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
            [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, CropItem)]
            return

        elif self.mod == 'Axe':
            if event.button() == Qt.LeftButton:

                pos = self.mapToScene(event.pos())
                name = self.parent().elements_list.currentItem().text()

                if '_' not in name:
                    self.parent().set_line('Select wrong elemet', Qt.red)
                    return

                try:

                    PARENT = [it for it in [it for it in self.scene().items() if isinstance(it, SimpleRect)]
                              if it.object_name == name.split('_')[0]][0]
                except IndexError:
                    self.parent().set_line(f'Switch mod on AI and mark {name.split("_")[0]}', Qt.red)
                    return

                point = SimplePoint((pos.x() * 4, pos.y() * 4), object_name=name,
                                    visible_status=self.parent().tool_bar.visible_status,
                                    parent_rect=PARENT)
                points = self.scene().items(PARENT.z_rect)
                for p in points:
                    if isinstance(p, SimplePoint):
                        if int(p.object_name.split('_')[-1]) >= int(name.split('_')[-1]):
                            p.object_name = PARENT.object_name + '_' + str(int(p.object_name.split('_')[-1]) + 1)
                self.scene().addItem(point)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Правая кнопка мыши Всегда отвечает за перемеения по фото, внезависимости от выбранного мода
            В режиме standard:
                - Pass
            В режиме AI:
                Отрисовка прямоугольника при выделении области"""

        if event.buttons() == Qt.LeftButton and self.mod == 'standard':

            if not self.start.isNull() and not self.finish.isNull():


                self.finish = self.mapToScene(event.pos())
                self.border_check()
                [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, CropItem)]

                self.cropItem = CropItem(self.scene().pic, self.start, self.mapToScene(event.pos()))
                self.cropItem.setBrush(QBrush(QColor(10, 0, 0, 80)))
                pen = QPen()
                pen.setColor(QColor(Qt.white))
                pen.setStyle(Qt.DotLine)
                self.cropItem.setPen(pen)

        if event.buttons() == Qt.LeftButton and self.mod == 'AI':

            if not self.start.isNull() and not self.finish.isNull():

                self.finish = self.mapToScene(event.pos())
                self.border_check()
                if self.items():
                    # Удаление всех объектов типа QGraphicsRectItem, иначе при движении мыши будут отрисовываться все
                    # прямоугольники начиная от начальной точки
                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                    [self.scene().removeItem(item) for item in self.scene().items() if isinstance(item, CropItem)]

                start_x = min(self.start.x(), self.finish.x())
                start_y = min(self.start.y(), self.finish.y())
                finish_x = abs(self.finish.x() - self.start.x())
                finish_y = abs(self.finish.y() - self.start.y())

                self.cropItem = CropItem(self.scene().pic, self.start, self.mapToScene(event.pos()))

                # Дорисовать второй четырехугольник меньшей ширины для тела микросхемы
                circ_rect = QGraphicsRectItem(QRectF(
                    start_x + (finish_x * 0.25), start_y,
                    finish_x - (finish_x * 0.5), finish_y
                ))
                circ_rect.setPen(QPen(Qt.red, 2))
                self.scene().addItem(circ_rect)

        super(GraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """В режиме standard:
                - Pass
            В режиме AI:
                - Создание экземпляров SimpleRect, SimplePoint
                - """

        if event.button() == Qt.RightButton:
            _event = QMouseEvent(event.type(), event.pos(), Qt.LeftButton, Qt.LeftButton, event.modifiers())
            super().mouseReleaseEvent(_event)
            event.accept()
            self.setDragMode(QGraphicsView.NoDrag)

        if event.button() == Qt.LeftButton:

            self.scene().removeItem(self.cropItem)
            rect = QRectF(
                min(self.start.x(), self.finish.x()),
                min(self.start.y(), self.finish.y()),
                abs(self.finish.x() - self.start.x()),
                abs(self.finish.y() - self.start.y()))
            self.parent().selected_items = [it for it in self.scene().items(rect)
                                            if isinstance(it, (SimpleRect, SimplePoint))]


        if self.mod == 'AI':

            if event.button() == Qt.LeftButton:
                # Координаты будущего SimpleRect
                self.points = np.array([self.start.x() * self.scene().kw,
                                        self.start.y() * self.scene().kh,
                                        self.finish.x() * self.scene().kw,
                                        self.finish.y() * self.scene().kh]).astype('int32')
                # обработка обычного клика мышью
                if self.start == self.finish:
                    self.scene().removeItem(self.cropItem)
                    return

                try:
                    # Достать информацию о кол-ве пинов из points для проверки
                    name = self.parent().elements_list.currentItem().text()
                    total_points = len(self.parent().dict['Elements'][name]['Pins'].keys())
                    self.scene().removeItem(self.cropItem)
                    # Поиск пинов
                    dots = self.scene().canvas.pins2json(self.points)
                    # Создание SimpleRect
                    self.add_rect()
                    # Создание SimplePoint
                    self.add_points(points=dots)
                    self.parent().next_item()
                    self.scene().itemClicked.emit(self.rect)

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
                except KeyError:
                    self.parent().set_line('Wrong point', Qt.red)

                finally:
                    print('done')

        # Удаляем отрисованный прямоугольник из mouseMoveEvent
        [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

        self.start = QPoint()
        self.finish = QPoint()
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

    def border_check(self):
        if self.finish.x() > self.sceneRect().width() - 1:
            self.finish.setX(self.sceneRect().width() - 1)
        elif self.finish.x() < 1:
            self.finish.setX(1)
        if self.finish.y() > self.sceneRect().height() - 1:
            self.finish.setY(self.sceneRect().height() - 1)
        elif self.finish.y() < 1:
            self.finish.setY(1)

    def add_rect(self):
        """Создание SimpleRect"""
        name = self.parent().elements_list.currentItem().text()

        if self.mod == 'AI':
            self.rect = SimpleRect(self.start.x(), self.start.y(), self.finish.x(), self.finish.y(),
                                   object_name=name, mod=self.mod)
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
                SimplePoint(point, object_name=name, visible_status=self.parent().tool_bar.visible_status,
                            parent_rect=self.rect))
