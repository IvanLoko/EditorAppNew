# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data\untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import glob

from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtGui import QColor, QPixmap, QPalette
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMessageBox, \
    QPushButton, QFileDialog, QApplication, QHBoxLayout, QGraphicsPixmapItem
    
import json

from canvas import Canvas
from centralLabel import GraphicsScene
from SimpleObjects import SimplePoint, SimpleRect
from model import build_model
from centralLabel import GraphicsView

from title_bar import TitleWidget
from main_bar import MainBar, ImageTab
from tool_bar import ToolBar
from side_panel import SidePanel, SB, ElementLabel, ListWidget, ListWidgetItem
from info_line import InfoLine


class Ui_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.images_list = []

        self.setObjectName("MainWindow")
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.central_widget = CentralWidget(self)
        self.central_widget.setObjectName("centralwidget")

        self.setCentralWidget(self.central_widget)
        self.showFullScreen()

    def minimize(self):
        self.showMinimized()

    def maximize(self):
        self.showMaximized()
        self.central_widget.title_bar.MaxButton.setVisible(False)
        self.central_widget.title_bar.RestoreButton.setVisible(True)

    def restore(self):
        self.showNormal()
        self.central_widget.title_bar.MaxButton.setVisible(True)
        self.central_widget.title_bar.RestoreButton.setVisible(False)

    def close(self):
        sys.exit(app.exec_())


class CentralWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.w = 510
        self.dict = None
        self.elements_list = ListWidget(self)
        self.circuit_map = ElementLabel(self)
        self.dirlist = None
        self.setupUI()
        self.graphics_view = GraphicsView(self)
        self.graphics_view.setGeometry(150, 100, 1200, 800)

        self.image_tabs = []
        self.tab = None
        self.sb = None

        self.load_project()

    def load_project(self):

        self.dirlist = QFileDialog.getExistingDirectory(None, "Выбрать папку", ".")

        if self.dirlist:
            try:
                with open(self.dirlist + r'/Контрольные точки/Points', 'r') as ff:
                    self.dict = json.loads(ff.read(), strict=False)
            except FileNotFoundError:
                message = QMessageBox()
                message.setText('Файл Points не найден,\n найти вручную?')
                message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                answer = message.exec_()
                if answer == QMessageBox.Yes:
                    dirlist_points, _ = QFileDialog.getOpenFileName(None, "Выбрать папку",
                                                                    self.dirlist + '/Контрольные точки/')
                    if dirlist_points:
                        with open(dirlist_points, 'r') as ff:
                            self.dict = json.loads(ff.read(), strict=False)
                elif answer in (QMessageBox.No, QMessageBox.Close):
                    return

            if self.dict:
                self.elements_list.clear()
                for el in self.dict['Elements'].keys():
                    try:
                        item = ListWidgetItem(el, self.dict['Elements'][el]['Type'])
                    except KeyError:
                        item = ListWidgetItem(el)

                    item.setText(el)

                    self.elements_list.addItem(item)
                    self.elements_list.setItemWidget(item, item.widget)

                self.elements_list.setCurrentRow(0)

            for file in glob.glob(self.dirlist + r'\Виды\*'):
                self.create_scene(file)
                self.create_tab(file.split('\\')[-1])
                self.sb = SB(self, file.split('\\')[-1])
                self.side_panel.layout.addWidget(self.sb)
                
            self.tab_clicked(self.tab)

            self.set_line(f'Elements & images loaded from {self.dirlist}', Qt.darkGreen)
        else:
            self.set_line('Project are not loaded', Qt.red)

    def next_item(self):
        self.elements_list.currentItem().setBackground(QColor("#07A707"))
        self.elements_list.setCurrentRow(self.elements_list.currentRow() + 1)
        if self.elements_list.currentItem() is None:
            raise AttributeError

    def elements_list_clicked(self):
        print(f'item clicked {self.elements_list.currentItem().text()}')

    def tab_clicked(self, tab):
        self.sb.hide()
        for element in self.findChildren(GraphicsScene):
            if element.objectName() == tab.text():
                # noinspection PyTypeChecker
                self.graphics_view.setScene(element)
        for element in self.side_panel.findChildren(SB):
            if element.image_name == tab.text():
                self.sb = element
                self.sb.show()
                self.side_panel.slider.setSliderPosition(self.sb.opacity.value())
                return

    def rewrite(self):
        self_dict = self.dict
        for scene in self.findChildren(GraphicsScene):
            for element in scene.items():

                if isinstance(element, SimpleRect):
                    if element.object_name in self_dict['Elements']:
                        self_dict['Elements'][element.object_name] \
                            ['Views'][str(scene.canvas.index)] = \
                            [{'L': int(element.rect().topLeft().x()),
                              'T': int(element.rect().topLeft().y()),
                              'R': int(element.rect().bottomRight().x()),
                              'B': int(element.rect().bottomRight().y()),
                              'Section': element.object_name}]

                if isinstance(element, SimplePoint):
                    if element.object_name in self_dict['Dots']:
                        self_dict['Dots'][element.object_name] \
                            ['Views'][str(scene.canvas.index)] = \
                            {'L': int(element.rect().topLeft().x()),
                             'T': int(element.rect().topLeft().y()),
                             'R': int(element.rect().bottomRight().x()),
                             'B': int(element.rect().bottomRight().y()),
                             'Section': element.object_name}

        with open(self.dirlist + r'/Контрольные точки/Points', 'w') as ff:
            json.dump(self_dict, ff, indent=1)
            
        self.set_line(f'File {self.dirlist}/Контрольные точки/Points rewrote', Qt.darkGreen)

    def create_tab(self, name="Empty"):
        self.tab = ImageTab(self)
        self.tab.setText(name)
        self.main_bar.image_line_layout.addWidget(self.tab)

    def create_scene(self, path):
        canvas = Canvas(path, model=model)
        scene = GraphicsScene(self.graphics_view, canvas)
        scene.setObjectName(path.split('\\')[-1])
        self.graphics_view.setScene(scene)

    def set_line(self, text=None, color=None):
        self.info_line.setText(text)
        if color:
            palette = QPalette()
            palette.setColor(QPalette.Text, color)
            self.info_line.setPalette(palette)

    def setupUI(self):
        self.tool_bar = ToolBar(self)
        self.tool_bar.move(0, 60)

        self.side_panel = SidePanel(self)
        self.side_panel.move(1520, 30)

        self.title_bar = TitleWidget(self)
        self.title_bar.setGeometry(0, 0, 1920, 30)
        self.title_bar.MinButton.clicked.connect(self.parent().minimize)
        self.title_bar.MaxButton.clicked.connect(self.parent().maximize)
        self.title_bar.RestoreButton.clicked.connect(self.parent().restore)
        self.title_bar.CloseButton.clicked.connect(self.parent().close)

        self.main_bar = MainBar(self)
        self.main_bar.setGeometry(0, 30, 1520, 30)

        self.info_line = InfoLine(self)
        self.info_line.setGeometry(0, 1050, 1920, 30)
        self.info_line.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.elements_list.clicked.connect(self.elements_list_clicked)


if __name__ == "__main__":
    import sys

    model = build_model()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.load_weights('data/U-net/weights.hdf5')

    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())
