from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from custom_widgets import TreeWidgetItem, TreeWidgetChild, TabWidget
from simple_objects import SimpleRect, SimplePoint

from win32api import GetMonitorInfo, MonitorFromPoint

import sys
import json
import glob
from datetime import datetime
from model import build_model
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
        self.normalized_geometry = self.geometry()
        self.grip_position = QPoint(0, 0)

        self.setupUi()

    def setupUi(self):

        # Show idle mode until project loaded
        self.GraphicsTabWidget.hide()
        self.BlueprintTabWidget.hide()
        self.TabResizeFrame.hide()
        self.SidePanel.hide()

        # Remove test objects
        self.BlueprintTabWidget.clear()
        self.GraphicsTabWidget.clear()
        self.TreeListWidget.clear()
        self.GraphicsLogger.clear()

        # Window properties
        self.setWindowTitle("Editor App")
        self.setWindowIcon(QIcon("src/icons/TestLogo.png"))
        self.setWindowFlag(Qt.FramelessWindowHint, True)

        # Window grip
        self.grip_frame = QFrame(self)
        self.grip_frame.setFixedSize(12, 12)
        self.grip_frame.move(self.width() - 12, self.height() - 12)

        self.SizeGrip = QSizeGrip(self.grip_frame)

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
                    self.ProjectName.setText(f"{self.dirlist.split('/')[-1]}  -  Editor App")
                    self.setWindowTitle(self.dirlist.split('/')[-1] + "  -  Editor App")

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

            # Add image tab
            for file in glob.glob(self.dirlist + r'\Виды\*'):

                tab_widget = TabWidget(file, model, self)

                self.detect_color(file).addTab(tab_widget, file.split('\\')[-1])

            self.TreeListWidget.setCurrentIndex(self.TreeListWidget.indexAt(QPoint(0, 0)))

            # Show graphic elements
            self.GraphicsTabWidget.show()
            self.BlueprintTabWidget.show()
            self.TabResizeFrame.show()
            self.SidePanel.show()

            # Set current view
            self.cur_view = self.GraphicsTabWidget.currentWidget().scene().canvas.path

            # Log loading
            self.log(f"Project {self.dirlist} successfully opened")

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


if __name__ == '__main__':

    model = build_model()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.load_weights('data/U-net/weights.hdf5')

    app = QApplication(sys.argv)

    ui = UI()
    ui.show()

    sys.exit(app.exec_())
