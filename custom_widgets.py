from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from simple_objects import SimpleRect, SimplePoint, AnchorRect
from conf_dialog import ConfDialog

import numpy as np

from canvas import Canvas


class TreeWidgetItem(QTreeWidgetItem):

    def __init__(self, el: str = "Ошибка", el_type: str = "Ошибка"):

        super().__init__()

        self.widget = QWidget()
        self.widget.setFixedSize(200, 20)
        self.setSizeHint(0, QSize(200, 20))

        self.name = el
        self.type = el_type

        self.status = False

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.el_label = ELLabel(self.name)
        self.el_label.setFixedSize(80, 20)

        self.el_type_label = ELTypeLabel(self.type)
        self.el_type_label.setFixedSize(120, 20)

        layout.addWidget(self.el_label)
        layout.addWidget(self.el_type_label)

        self.widget.setLayout(layout)

    def change_status(self, status: bool):
        if status:
            self.status = True
            self.el_label.setText(self.name + " ✓")
        else:
            self.status = False
            self.el_label.setText(self.name)


class TreeWidgetChild(QTreeWidgetItem):

    def __init__(self, name="Ошибка"):

        super().__init__()

        self.setText(0, name)

        self.name = name
        self.status = False

    def change_status(self, status: bool):
        if status:
            self.status = True
            self.setText(0, self.name + " ✓")
        else:
            self.status = False
            self.setText(0, self.name)


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
        self.pixmap = QPixmap(canvas.path)
        w = self.pixmap.width()
        h = self.pixmap.height()
        self.kw = 4800 / w
        self.kh = 3200 / h
        self.pic.setPixmap(self.pixmap)
        self.addItem(self.pic)
        self.setSceneRect(QRectF(0, 0, w, h))


class GraphicsBlueprintItem(QGraphicsPixmapItem):

    def __init__(self, path):
        super().__init__()

        self.path = path
        self.pixmap = QPixmap(path)
        self.setPixmap(self.pixmap)


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
        self.flipped = False
        self.mirrored = False
        self.rotation = 0
        self.shift = QPoint()
        self.start = QPoint()
        self.finish = QPoint()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.points = None
        self.blueprint = None
        self.current_el = []
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def leaveEvent(self, event):

        if self.mainwindow.mod == "ZOOM":
            [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete:

            for item in self.current_el:

                self.scene().removeItem(item.sl)
                self.scene().removeItem(item)

                if type(item) == SimpleRect:

                    self.mainwindow.TreeListWidget.findItems(item.object_name, Qt.MatchExactly)[0].change_status(False)

                else:

                    try:

                        l_item = self.mainwindow.TreeListWidget.findItems(item.object_name.split("_")[0], Qt.MatchExactly)[0]
                        l_item.child(int(item.object_name.split("_")[-1]) - 1).change_status(False)

                    except AttributeError:

                        continue

            self.current_el.clear()

    def mousePressEvent(self, event):

        self.mainwindow.cur_view = self

        if type(self.itemAt(event.pos())) in [QGraphicsPixmapItem, GraphicsBlueprintItem]:

            if event.button() == Qt.LeftButton:

                if self.mainwindow.mod == "AI":

                    if type(self.mainwindow.TreeListWidget.currentItem()) == TreeWidgetChild:

                        self.mainwindow.log("Can't place pins in AI mode, change current item or mode!")
                        return

                    else:

                        self.start = self.mapToScene(event.pos())
                        self.finish = self.start

                elif self.mainwindow.mod == "AXE":

                    self.start = self.mapToScene(event.pos())
                    self.finish = self.start

                elif self.mainwindow.mod == "CROP":

                    self.start = self.mapToScene(event.pos())
                    self.finish = self.start

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

        elif self.mainwindow.mod in ["AXE", "CROP", "AI"]:

            if self.mainwindow.mod in ["AXE", "AI"] and type(self.mainwindow.TreeListWidget.currentItem()) == TreeWidgetChild:
                super().mouseMoveEvent(event)
                return

            if not self.start.isNull() and not self.finish.isNull():

                self.finish = self.mapToScene(event.pos())

                if self.items():

                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

                start_x = min(self.start.x(), self.finish.x())
                start_y = min(self.start.y(), self.finish.y())
                finish_x = abs(self.finish.x() - self.start.x())
                finish_y = abs(self.finish.y() - self.start.y())

                rect = QGraphicsRectItem(start_x, start_y, finish_x, finish_y)
                self.scene().addItem(rect)

                if self.mainwindow.mod == 'AI' and event.modifiers() != Qt.AltModifier:

                    if self.rotation not in [90, 270]:

                        circ_rect = QGraphicsRectItem(QRectF(
                            start_x + (finish_x * 0.15), start_y,
                            finish_x - (finish_x * 0.3), finish_y
                        ))

                        circ_rect.setPen(QPen(Qt.red, 2))
                        self.scene().addItem(circ_rect)

                    else:

                        circ_rect = QGraphicsRectItem(QRectF(
                            start_x, start_y + (finish_y * 0.15),
                            finish_x, finish_y - (finish_y * 0.3)
                        ))

                        circ_rect.setPen(QPen(Qt.red, 2))
                        self.scene().addItem(circ_rect)

                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.points = np.array([self.start.x(),
                                    self.start.y(),
                                    self.finish.x(),
                                    self.finish.y()]).astype('int16')

            if self.mainwindow.mod in ["AXE", "AI"] and self.start == self.finish and \
                    type(self.itemAt(event.pos())) in [QGraphicsPixmapItem, GraphicsBlueprintItem]:

                for item in self.current_el:

                    if item.object_name.split('_')[-1] != '1':
                        pen = QPen()
                        pen.setColor(QColor("#11ab22"))
                        pen.setWidth(2)
                        item.setPen(pen)

                self.current_el.clear()

            if self.mainwindow.mod == "ZOOM":

                self.transform_func.scale(1.2, 1.2)
                self.setTransform(self.transform_func)

            elif self.mainwindow.mod in ["AXE", "AI"] and event.modifiers() == Qt.AltModifier:

                if self.start == self.finish:

                    self.start = QPoint()
                    self.finish = QPoint()

                    return

                start_x = min(self.start.x(), self.finish.x())
                start_y = min(self.start.y(), self.finish.y())
                finish_x = abs(self.finish.x() - self.start.x())
                finish_y = abs(self.finish.y() - self.start.y())

                rect = QRectF(start_x, start_y, finish_x, finish_y)

                for item in self.current_el:

                    if item.object_name.split('_')[-1] != '1':
                        pen = QPen()
                        pen.setColor(QColor("#11ab22"))
                        pen.setWidth(2)
                        item.setPen(pen)

                self.current_el.clear()

                [item.set_current(True) for item in self.scene().items(rect) if type(item) in [SimpleRect, SimplePoint]]

                [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

            elif self.mainwindow.mod == "AI":

                if self.start == self.finish:

                    self.start = QPoint()
                    self.finish = QPoint()

                    return

                try:
                    dots = self.scene().canvas.pins2json(self.points)

                except RuntimeWarning:

                    self.mainwindow.log("Error: no points found")
                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                    self.start = QPoint()
                    self.finish = QPoint()
                    return

                except Exception:

                    self.mainwindow.log("Error: unknown error")
                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                    self.start = QPoint()
                    self.finish = QPoint()
                    return

                # Add rect
                name = self.mainwindow.TreeListWidget.currentItem().text(0)

                rect = SimpleRect(self.start.x(), self.start.y(), self.finish.x(), self.finish.y(),
                                    object_name=name, mod=self.mainwindow.mod)

                self.scene().addItem(rect)

                # Add pins

                pins = []
                for num, point in enumerate(dots):
                    name = f'{self.mainwindow.TreeListWidget.currentItem().text(0)}_{num + 1}'
                    pin = SimplePoint(point, object_name=name, visible_status=self.mainwindow.pins_status)
                    self.scene().addItem(pin)
                    pins.append(pin)

                [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]
                self.mainwindow.log(f"Placed element: {self.mainwindow.TreeListWidget.currentItem().text(0)}")

                dialog = ConfDialog(pins=pins, view=self)
                dialog.exec()

                if dialog.status:

                    self.mainwindow.next_item(len(dots))

                else:

                    self.scene().removeItem(rect)

            elif self.mainwindow.mod == "AXE":

                name = self.mainwindow.TreeListWidget.currentItem().text(0).replace(" ✓", "")

                if type(self.mainwindow.TreeListWidget.currentItem()) == TreeWidgetItem and self.start != self.finish:

                    [self.scene().removeItem(it) for it in self.items() if type(it) == SimpleRect and it.object_name == name]

                    rect = SimpleRect(self.start.x(), self.start.y(), self.finish.x(), self.finish.y(),
                                      object_name=name, mod=self.mainwindow.mod)

                    self.scene().addItem(rect)
                    self.mainwindow.log(f"Placed body: {name}")
                    self.mainwindow.next_item()

                else:

                    if type(self.itemAt(event.pos())) in [QGraphicsPixmapItem, GraphicsBlueprintItem] and \
                            type(self.mainwindow.TreeListWidget.currentItem()) == TreeWidgetChild:

                        [self.scene().removeItem(it) for it in self.items() if type(it) == SimplePoint and it.object_name == name]

                        size = self.sceneRect().width() / 200
                        self.scene().addItem(
                            SimplePoint((self.finish.x() - (size / 2), self.finish.y() - (size / 2), size, size),
                                        object_name=name,
                                        visible_status=self.mainwindow.pins_status))

                        self.mainwindow.log(f"Placed point: {name}")
                        self.mainwindow.next_item()

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

            else:

                if self.items():

                    [self.scene().removeItem(it) for it in self.items() if type(it) == QGraphicsRectItem]

                _event = QMouseEvent(event.type(), event.pos(), Qt.LeftButton, Qt.LeftButton, event.modifiers())
                super().mouseReleaseEvent(_event)
                event.accept()
                self.setDragMode(QGraphicsView.NoDrag)

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
