import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from custom_widgets import TreeWidgetItem, TreeWidgetChild, TabWidget, GraphicsBlueprintItem
from simple_objects import SimpleRect, SimplePoint

from win32api import GetMonitorInfo, MonitorFromPoint

import sys
import json
import glob
from datetime import datetime
from ultralytics import YOLO
from PIL import Image, ImageStat


class UI(QMainWindow):

    def __init__(self):

        super(UI, self).__init__()
        uic.loadUi('EditorApp.ui', self)

        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setEasingCurve(QEasingCurve.Linear)

        # Properties
        self.dirlist = None
        self.dict = None
        self.mod = "AI"
        self.pins_status = True
        self.cur_view = None
        self.bp_view = None
        self.normalized_geometry = self.geometry()
        self.grip_position = QPoint(0, 0)

        self.setupUi()

    def setupUi(self):

        # Show idle mode until project loaded
        self.GraphicsLogger.clear()
        self.go_idle()

        # Window properties
        self.setWindowTitle("Editor App")
        self.setWindowIcon(QIcon("src/icons/TestLogo.png"))
        self.setWindowFlag(Qt.FramelessWindowHint, True)

        # Window grip
        self.grip_frame = QFrame(self)
        self.grip_frame.setFixedSize(12, 12)
        self.grip_frame.move(self.width() - 12, self.height() - 12)

        self.SizeGrip = QSizeGrip(self.grip_frame)

        # Opacity input
        self.OpacityBox.valueChanged.connect(self.opacity_trim)

        # Blueprint load button
        self.BLButton.clicked.connect(self.bp_load)
        self.BLVisibleButton.clicked.connect(self.bp_visible)

        # Connect current view change
        self.GraphicsTabWidget.currentChanged.connect(self.change_bpview)
        self.BlueprintTabWidget.currentChanged.connect(self.change_curview)

        # Necessary and not elements
        self.show()
        self.GraphicsLoggerFrame.hide()
        self.RestoreButton.hide()

        # Connect ToolBar Buttons
        self.AIButton.clicked.connect(lambda: self.change_mode("AI"))
        self.AXEButton.clicked.connect(lambda: self.change_mode("AXE"))
        self.MOVEButton.clicked.connect(lambda: self.change_mode("STD"))
        self.ZoomButton.clicked.connect(lambda: self.change_mode("ZOOM"))
        self.CropButton.clicked.connect(lambda: self.change_mode("CROP"))
        self.LogButton.clicked.connect(lambda: self.GraphicsLoggerFrame.setHidden(not self.GraphicsLoggerFrame.isHidden()))
        self.LoadButton.clicked.connect(self.load_project)
        self.SaveButton.clicked.connect(self.save_project)
        self.PinsButton.clicked.connect(self.pins_status_change)
        self.RotateButton.clicked.connect(self.view_rotation)
        self.MirrorYButton.clicked.connect(self.reflect_y)
        self.MirrorXButton.clicked.connect(self.reflect_x)

        # Connect LoggerAnchor
        self.GraphicsLoggerAnchor.mouseMoveEvent = self.logger_anchoring

        # Connect TabAnchor
        self.TabResizeFrame.mouseMoveEvent = self.tab_anchoring

        # Change parent (Qt Designer issue)
        self.verticalLayout_7.setAlignment(Qt.AlignBottom)
        self.verticalLayout_7.addWidget(self.GraphicsLoggerFrame)

        # Connect navigation buttons
        self.CloseButton.clicked.connect(app.exit)
        self.MaximizeButton.clicked.connect(self.nav_maxmin)
        self.RestoreButton.clicked.connect(self.nav_maxmin)
        self.MinimizeButton.clicked.connect(self.showMinimized)

        # Connect TitleBar
        self.TitleBar.mousePressEvent = self.press_window
        self.TitleBar.mouseMoveEvent = self.move_window

        # Log opening
        self.log("App opened")

    def resizeEvent(self, event):

        # Move SizeGrip
        self.grip_frame.move(self.width() - 12, self.height() - 12)

        if self.MaximizeButton.isHidden():

            self.grip_frame.hide()

        elif not self.MaximizeButton.isHidden():

            self.grip_frame.show()

    def load_project(self):
        """ Load button pressed """

        self.dirlist = QFileDialog.getExistingDirectory(None, "Выбрать папку", ".")

        if self.dirlist:
            try:

                with open(self.dirlist + r'/Контрольные точки/Points', 'r') as ff:
                    self.dict = json.loads(ff.read(), strict=False)

            except FileNotFoundError:
                self.log("Project file not found")
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
                    self.log("Canceled project loading")
                    return

            except UnicodeDecodeError:
                self.log("Codec can't decode Points (Project may be corrupted)")
                return

        else:
            self.log("Canceled project loading")
            return

        if self.dict:

            # Clear last project
            self.GraphicsTabWidget.clear()
            self.BlueprintTabWidget.clear()
            self.TreeListWidget.clear()

            # Load elements
            for el in self.dict['Elements'].keys():
                try:
                    item = TreeWidgetItem(el, self.dict['Elements'][el]['Type'])

                except KeyError:
                    item = TreeWidgetItem()

                item.setText(0, el)
                self.TreeListWidget.addTopLevelItem(item)
                self.TreeListWidget.setItemWidget(item, 0, item.widget)

                for pin in self.dict['Elements'][el]['Pins'].keys():
                    pin_item = TreeWidgetChild(pin)

                    item.addChild(pin_item)

            grayscale = None
            color = None

            # Add image tab
            for file in glob.glob(self.dirlist + r'\Виды\*'):

                tab_widget = TabWidget(file, model, self)

                if self.detect_color(file) == self.BlueprintTabWidget:

                    grayscale = True

                else:

                    color = True

                self.detect_color(file).addTab(tab_widget, file.split('\\')[-1])

            self.TreeListWidget.setCurrentIndex(self.TreeListWidget.indexAt(QPoint(0, 0)))

            # Show graphic elements
            self.go_work()

            # Check empty widgets
            if not color:
                self.TabResizeFrame.hide()
                self.GraphicsTabWidget.hide()

            elif not grayscale:
                self.TabResizeFrame.hide()
                self.BlueprintTabWidget.hide()

            elif not color and not grayscale:
                self.log("No images found")
                self.go_idle()
                return

            if not self.TreeListWidget.currentItem():
                self.log("No elements found")
                self.go_idle()
                return

            # Set current view
            self.cur_view = self.GraphicsTabWidget.currentWidget()
            self.bp_view = self.GraphicsTabWidget.currentWidget()

            # Change window name
            self.ProjectName.setText(f"{self.dirlist.split('/')[-1]}  -  Editor App")
            self.setWindowTitle(self.dirlist.split('/')[-1] + "  -  Editor App")

            # Log loading
            self.log(f"Project {self.dirlist} successfully opened")

    def go_idle(self):

        # Hide and clear graphics
        self.GraphicsTabWidget.hide()
        self.BlueprintTabWidget.hide()
        self.TabResizeFrame.hide()
        self.SidePanel.hide()

        self.GraphicsTabWidget.clear()
        self.BlueprintTabWidget.clear()
        self.TreeListWidget.clear()

        # Hide toolbar
        self.ProjectLine.hide()
        self.ToolsLine.hide()
        self.ImageLine.hide()
        self.SaveButton.hide()
        self.AIButton.hide()
        self.AXEButton.hide()
        self.MOVEButton.hide()
        self.RotateButton.hide()
        self.MirrorYButton.hide()
        self.MirrorXButton.hide()
        self.CropButton.hide()
        self.ZoomButton.hide()
        self.PinsButton.hide()
        self.NamesButton.hide()

    def go_work(self):

        # Show graphics
        self.GraphicsTabWidget.show()
        self.BlueprintTabWidget.show()
        self.TabResizeFrame.show()
        self.SidePanel.show()

        # Show toolbar
        self.ProjectLine.show()
        self.ToolsLine.show()
        self.ImageLine.show()
        self.SaveButton.show()
        self.AIButton.show()
        self.AXEButton.show()
        self.MOVEButton.show()
        self.RotateButton.show()
        self.MirrorYButton.show()
        self.MirrorXButton.show()
        self.CropButton.show()
        self.ZoomButton.show()
        self.PinsButton.show()
        self.NamesButton.show()

    def save_project(self):

        if not self.dirlist:
            return

        self_dict = self.dict
        for view in (self.GraphicsTabWidget.findChildren(TabWidget) + self.BlueprintTabWidget.findChildren(TabWidget)):
            for element in view.scene().items():

                if isinstance(element, SimpleRect):
                    if element.object_name in self_dict['Elements']:
                        self_dict['Elements'][element.object_name] \
                            ['Views'][str(view.scene().canvas.index)] = \
                            [{'L': int(element.rect().topLeft().x()),
                              'T': int(element.rect().topLeft().y()),
                              'R': int(element.rect().bottomRight().x()),
                              'B': int(element.rect().bottomRight().y()),
                              'Section': element.object_name}]

                if isinstance(element, SimplePoint):
                    if element.object_name in self_dict['Dots']:
                        self_dict['Dots'][element.object_name] \
                            ['Views'][str(view.scene().canvas.index)] = \
                            {'L': int(element.rect().topLeft().x()),
                             'T': int(element.rect().topLeft().y()),
                             'R': int(element.rect().bottomRight().x()),
                             'B': int(element.rect().bottomRight().y()),
                             'Section': element.object_name}

        with open(self.dirlist + '/Контрольные точки/Points', 'w') as ff:
            json.dump(self_dict, ff, indent=1)
        self.log(f'File {self.dirlist}/Контрольные точки/Points saved successfully!')

    def detect_color(self, file):
        pil_img = Image.open(file)

        thumb = pil_img.resize((40, 40))
        SSE, bias = 0, [0, 0, 0]
        bias = ImageStat.Stat(thumb).mean[:3]
        bias = [b - sum(bias) / 3 for b in bias]
        for pixel in thumb.getdata():
            mu = sum(pixel)/3
            SSE += sum((pixel[i] - mu - bias[i])*(pixel[i] - mu - bias[i]) for i in [0, 1, 2])
        MSE = float(SSE) / (40 * 40)
        if MSE <= 22:
            # Grayscale
            return self.BlueprintTabWidget
        else:
            # Color
            return self.GraphicsTabWidget

    def nav_maxmin(self):
        """ Max/Min button pressed """

        if self.RestoreButton.isHidden():

            self.RestoreButton.show()
            self.MaximizeButton.hide()

            # Save geometry for future restore
            self.normalized_geometry = self.geometry()

            # Get current screen geometry
            middle = QPoint(self.pos().x() + int(self.width() / 2), self.pos().y() + int(self.height() / 2))
            geom = app.screenAt(middle).geometry()

            # Change height according to Windows Taskbar Height
            monitor_info = GetMonitorInfo(MonitorFromPoint((middle.x(), middle.y())))

            taskbar_height = monitor_info.get("Monitor")[3] - monitor_info.get("Work")[3]

            geom.setHeight(app.screenAt(QPoint(self.pos().x() + int(self.width() / 2),
                                        self.pos().y() + int(self.height() / 2))).geometry().height() - taskbar_height)

            # Animate resize
            self.animation.setDuration(75)
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(geom)
            self.animation.start()

        else:

            self.MaximizeButton.show()
            self.RestoreButton.hide()

            # Animate resize
            self.animation.setDuration(75)
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.normalized_geometry)
            self.animation.start()

    def tab_anchoring(self, event):
        """ Resize grip for QTabWidget """

        self.BlueprintTabWidget.setFixedHeight(self.BlueprintTabWidget.height() + event.pos().y())

        if self.BlueprintTabWidget.height() < 30:

            self.BlueprintTabWidget.setFixedHeight(30)

        elif self.GraphicsLoggerFrame.isHidden() and self.BlueprintTabWidget.height() > self.GraphicsFrame.height() - 30:

            self.BlueprintTabWidget.setFixedHeight(self.GraphicsFrame.height() - 30)

        elif not self.GraphicsLoggerFrame.isHidden() and self.BlueprintTabWidget.height() > self.GraphicsFrame.height() - 30 - self.GraphicsLoggerFrame.height():

            self.BlueprintTabWidget.setFixedHeight(self.GraphicsFrame.height() - 30 - self.GraphicsLoggerFrame.height())

    def logger_anchoring(self, event):
        """ Top resize grip for GraphicsLogger """

        self.GraphicsLoggerFrame.setFixedHeight(self.GraphicsLoggerFrame.height() - event.pos().y())

        if self.GraphicsLoggerFrame.height() < 25:

            self.GraphicsLoggerFrame.setFixedHeight(25)

        elif self.GraphicsLoggerFrame.height() > int(self.GraphicsFrame.height() / 2):

            self.GraphicsLoggerFrame.setFixedHeight(int(self.GraphicsFrame.height() / 2))

    def press_window(self, event):
        """ Get grip position if not maximized """

        if not self.MaximizeButton.isHidden():

            self.grip_position = event.pos()

    def move_window(self, event):
        """ Move grip for MainWindow if not maximized """

        if not self.MaximizeButton.isHidden():

            self.move(
                self.pos().x() + event.pos().x() - self.grip_position.x(),
                event.pos().y() + self.pos().y() - self.grip_position.y()
            )

    def log(self, text: str):
        """ Append text in logger """
        
        self.GraphicsLogger.appendPlainText(f"<{str(datetime.now().time()).split('.')[0]}> " + text)

    def change_mode(self, mode: str):

        self.mod = mode
        self.log(f"Mouse mode changed -> {self.mod}")

    def pins_status_change(self):

        self.pins_status = not self.pins_status

        for view in (self.GraphicsTabWidget.findChildren(TabWidget) + self.BlueprintTabWidget.findChildren(TabWidget)):

            [item.setVisible(self.pins_status) for item in view.scene().items() if type(item) == SimplePoint]

        self.log(f"Points visibility set to {self.pins_status}")

    def view_rotation(self):

        if self.cur_view:

            self.cur_view.transform_func.rotate(90)
            self.cur_view.setTransform(self.cur_view.transform_func)

    def reflect_y(self):

        if self.cur_view:

            self.cur_view.transform_func.scale(-1, 1)
            self.cur_view.setTransform(self.cur_view.transform_func)

    def reflect_x(self):

        if self.cur_view:

            self.cur_view.transform_func.scale(1, -1)
            self.cur_view.setTransform(self.cur_view.transform_func)

    def opacity_trim(self):

        nosuff = self.OpacityBox.text()[:-1]

        if len(nosuff) > 1 and nosuff[0] == "0":

            self.OpacityBox.setValue(int(nosuff[1:]))

        elif self.OpacityBox.value() > 100:

            self.OpacityBox.setValue(100)

        if self.bp_view.blueprint:

            self.bp_view.blueprint.setOpacity(self.OpacityBox.value() / 100)

    def bp_load(self):

        file_path = QFileDialog.getOpenFileName(None, "Выберите изображение", '', "Images (*.png *.jpg)")[0].replace('/', '\\')

        if file_path:

            if self.bp_view.blueprint:

                self.bp_view.scene().removeItem(self.bp_view.blueprint)

            self.bp_view.blueprint = GraphicsBlueprintItem(file_path)
            self.bp_view.blueprint.setOpacity(self.OpacityBox.value() / 100)
            self.BLButton.setText(self.bp_view.blueprint.path.split('\\')[-1])
            self.bp_view.scene().addItem(self.bp_view.blueprint)
            self.OpacityBox.setReadOnly(False)

    def bp_visible(self):

        if not self.bp_view.blueprint:

            return

        if self.bp_view.blueprint.isVisible():

            self.bp_view.blueprint.setVisible(False)
            self.BLVisibleButton.setIcon(QIcon("src/icons/free/eye-off.svg"))

        else:

            self.bp_view.blueprint.setVisible(True)
            self.BLVisibleButton.setIcon(QIcon("src/icons/free/eye.svg"))

    def change_curview(self):

        self.cur_view = self.GraphicsTabWidget.currentWidget()

    def change_bpview(self):

        if self.GraphicsTabWidget.currentWidget():

            self.bp_view = self.GraphicsTabWidget.currentWidget()

        else:

            return

        self.change_curview()

        if self.bp_view.blueprint:

            if not self.bp_view.blueprint.isVisible():

                self.BLVisibleButton.setIcon(QIcon("src/icons/free/eye-off.svg"))

            else:

                self.BLVisibleButton.setIcon(QIcon("src/icons/free/eye.svg"))

            self.BLButton.setText(self.bp_view.blueprint.path.split('\\')[-1])
            self.OpacityBox.setValue(int(self.bp_view.blueprint.opacity() * 100))
            self.OpacityBox.setReadOnly(False)

        else:

            self.BLVisibleButton.setIcon(QIcon("src/icons/free/eye.svg"))
            self.BLButton.setText("No Image")
            self.OpacityBox.setReadOnly(True)
            self.OpacityBox.setValue(30)

    def next_item(self, count=0):

        if self.mod == "AI":

            self.TreeListWidget.currentItem().change_status(True)

            for index in range(0, count):

                try:

                    self.TreeListWidget.currentItem().child(index).change_status(True)

                except AttributeError:

                    break

            if self.TreeListWidget.currentItem().childCount() <= count:

                self.TreeListWidget.currentItem().setExpanded(False)
                next_item = self.TreeListWidget.topLevelItem(self.TreeListWidget.currentIndex().row() + 1)
                self.TreeListWidget.setCurrentItem(next_item)

            else:

                last_item = self.TreeListWidget.currentItem().child(count)
                self.TreeListWidget.setCurrentItem(last_item)

        elif self.mod == "AXE":

            if type(self.TreeListWidget.currentItem()) == TreeWidgetItem:

                self.TreeListWidget.currentItem().change_status(True)

                if self.TreeListWidget.currentItem().child(0):

                    self.TreeListWidget.currentItem().setExpanded(True)
                    self.TreeListWidget.setCurrentItem(self.TreeListWidget.currentItem().child(0))

                else:

                    next_item = self.TreeListWidget.topLevelItem(self.TreeListWidget.currentIndex().row() + 1)
                    self.TreeListWidget.setCurrentItem(next_item)

            elif type(self.TreeListWidget.currentItem()) == TreeWidgetChild:

                item = self.TreeListWidget.currentItem()
                item_index = item.parent().indexOfChild(item)

                if item.parent().child(item_index + 1):

                    self.TreeListWidget.currentItem().change_status(True)
                    self.TreeListWidget.setCurrentItem(item.parent().child(item_index + 1))

                else:

                    self.TreeListWidget.currentItem().change_status(True)
                    self.TreeListWidget.currentItem().parent().setExpanded(False)

                    self.TreeListWidget.setCurrentItem(item.parent())
                    next_item = self.TreeListWidget.topLevelItem(self.TreeListWidget.currentIndex().row() + 1)
                    self.TreeListWidget.setCurrentItem(next_item)


if __name__ == '__main__':

    model = YOLO('data/best.pt', task='predict')
    model(np.zeros((256, 256, 3)), verbose=False)

    app = QApplication(sys.argv)

    ui = UI()
    ui.show()

    sys.exit(app.exec_())
