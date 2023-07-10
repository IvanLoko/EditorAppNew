from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from errors import *

from simple_objects import SimpleRect, SimplePoint

import numpy as np

from canvas import Canvas


class TreeWidgetItem(QTreeWidgetItem):

    def __init__(self, el: str="Ошибка", el_type: str="Ошибка"):

        super().__init__()

        self.widget = QWidget()
        self.widget.setFixedSize(200, 20)
        self.setSizeHint(0, QSize(200, 20))

        self.status = "None"

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.el_label = ELLabel(el)
        self.el_label.setFixedSize(80, 20)

        self.el_type_label = ELTypeLabel(el_type)
        self.el_type_label.setFixedSize(120, 20)

        layout.addWidget(self.el_label)
        layout.addWidget(self.el_type_label)

        self.widget.setLayout(layout)


class TreeWidgetChild(QTreeWidgetItem):

    def __init__(self, name="Ошибка"):
        
        super().__init__()

        self.setText(0, name)

        self.status = "None"


class ELLabel(QLabel):

    def __init__(self, el):
        super().__init__()

        self.setText(el)
        self.setObjectName("ItemWidgetEl")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setContentsMargins(3, 0, 0, 0)


class ELTypeLabel(QLabel):

    def __init__(self, el_type):
        super().__init__()

        self.setText(el_type)
        self.setObjectName("ItemWidgetElType")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setContentsMargins(3, 0, 0, 0)


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
        self.setSceneRect(QRectF(0, 0, w, h))


class TabWidget(QGraphicsView):

    def __init__(self, path, model, window):
        
        super().__init__()

        # Setup
        self.mainwindow = window
        canvas = Canvas(path, model=model)
        scene = GraphicsScene(self, canvas)
        scene.setObjectName(path.split('\\')[-1])

        self.setScene(scene)
        self.setCursor(Qt.CrossCursor)

        self.transform_func = QTransform()
        self.div = 0
        self.zoom = 0
        self.shift = QPoint()
        self.start = QPoint()
        self.finish = QPoint()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.points = None
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def leaveEvent(self, event):

        if self.mainwindow.mod == "ZOOM":
            [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

    def mousePressEvent(self, event):

        self.mainwindow.cur_view = self

        if self.mainwindow.mod in ["AI", "AXE", "CROP", "STD"] and type(self.itemAt(event.pos())) == QGraphicsPixmapItem:

            if self.mainwindow.mod == "AI" and type(self.mainwindow.TreeListWidget.currentItem()) == TreeWidgetChild:
                self.mainwindow.log("Can't place pins in AI mode, change current item or mode!")
                return

            if event.button() == Qt.LeftButton:
                self.start = self.mapToScene(event.pos())
                self.finish = self.start
                self.update()

            elif event.button() == Qt.RightButton:
                _event = QMouseEvent(event.type(), event.pos(), Qt.LeftButton, Qt.LeftButton, event.modifiers())
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                super().mousePressEvent(_event)
                event.accept()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self.mainwindow.mod == "ZOOM":
            if self.items():
                [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
            center = self.mapToScene(event.pos())

            kx, ky = self.sceneRect().width() / 10, self.sceneRect().height() / 10

            rect = QGraphicsRectItem(center.x() - kx/2, center.y() - ky/2, kx, ky)
            self.scene().addItem(rect)
            return

        elif event.buttons() == Qt.LeftButton:
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

                if self.mainwindow.mod == 'AI':
                    # Дорисовать второй четырехугольник меньшей ширины для тела микросхемы
                    circ_rect = QGraphicsRectItem(QRectF(
                        start_x + (finish_x * 0.25), start_y,
                        finish_x - (finish_x * 0.5), finish_y
                    ))
                    circ_rect.setPen(QPen(Qt.red, 2))
                    self.scene().addItem(circ_rect)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            # Координаты будущего SimpleRect
            self.points = np.array([self.start.x() * self.scene().kw,
                                    self.start.y() * self.scene().kh,
                                    self.finish.x() * self.scene().kw,
                                    self.finish.y() * self.scene().kh]).astype('int32')

            if self.mainwindow.mod == 'ZOOM':

                self.transform_func.scale(1.2, 1.2)
                self.setTransform(self.transform_func)
                return

            if self.mainwindow.mod == 'AI':

                # обработка обычного клика мышью
                if self.start == self.finish:
                    return

                # Поиск пинов
                try:
                    dots = self.scene().canvas.pins2json(self.points)

                except NonePointError:
                    self.mainwindow.log("Error: no points in this area")
                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                    return

                except Exception:
                    self.mainwindow.log("Error: unknown error")
                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                    return

                # Add rect
                name = self.mainwindow.TreeListWidget.currentItem().text(0)

                rect = SimpleRect(self.start.x(), self.start.y(), self.finish.x(), self.finish.y(),
                                  object_name=name, mod=self.mainwindow.mod)

                self.scene().addItem(rect)

                # Add pins

                for num, point in enumerate(dots):
                    name = f'{self.mainwindow.TreeListWidget.currentItem().text(0)}_{num + 1}'
                    point[0] = point[0]
                    point[1] = point[1]
                    self.scene().addItem(
                        SimplePoint(point, object_name=name, visible_status=self.mainwindow.pins_status))

                [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                self.mainwindow.log(f"Placed element: {self.mainwindow.TreeListWidget.currentItem().text(0)}")

            elif self.mainwindow.mod == 'AXE':

                name = self.mainwindow.TreeListWidget.currentItem().text(0)

                if type(self.mainwindow.TreeListWidget.currentItem()) == TreeWidgetItem and self.start != self.finish:
                    rect = SimpleRect(self.start.x(), self.start.y(), self.finish.x(), self.finish.y(),
                                      object_name=name, mod=self.mainwindow.mod)

                    self.scene().addItem(rect)
                    self.mainwindow.log(f"Placed body: {name}")

                else:

                    if type(self.itemAt(event.pos())) != QGraphicsPixmapItem:
                        return

                    self.scene().addItem(
                        SimplePoint((self.finish.x(), self.finish.y()), object_name=name,
                                    visible_status=self.mainwindow.pins_status))

                    self.mainwindow.log(f"Placed point: {name}")

                [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

            elif self.mainwindow.mod == 'CROP':

                self.fitInView(min(self.start.x(), self.finish.x()),
                               min(self.start.y(), self.finish.y()),
                               np.abs(self.start.x() - self.finish.x()),
                               np.abs(self.start.y() - self.finish.y()),
                               Qt.KeepAspectRatio)

                self.transform_func = self.transform()

                [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

        elif event.button() == Qt.RightButton:

            if self.mainwindow.mod == 'ZOOM':

                self.transform_func.scale(0.8, 0.8)
                self.setTransform(self.transform_func)
                return

            else:

                _event = QMouseEvent(event.type(), event.pos(), Qt.LeftButton, Qt.LeftButton, event.modifiers())
                super().mouseReleaseEvent(_event)
                event.accept()
                self.setDragMode(QGraphicsView.NoDrag)
                return

        self.start = QPoint()
        self.finish = QPoint()
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event) -> None:
        """Мастабирование с помощью колеса мыши внезависимости от режима"""

        if event.modifiers() == Qt.ControlModifier:
            scale = 1 + event.angleDelta().y() / 1200
            self.transform_func.scale(scale, scale)
            # self.zoom += event.angleDelta().y()
            # Раскоментировать, если вкл. не отдалять дальше исходного размера
            # if self.zoom < 0:
            #     self.resetTransform()
            #     self.transform_func = QTransform()
            #     self.zoom = 0
            #     return
            self.setTransform(self.transform_func)

        else:

            super().wheelEvent(event)
