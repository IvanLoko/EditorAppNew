from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout,QPushButton


class TitleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hide()

        # Building UI

        self.setupUI()
        self.show()

    def setupUI(self):

        # Свойства

        self.setObjectName("TitleWidget")
        self.setMinimumWidth(800)
        self.setFixedHeight(30)

        # Расположение элементов

        GlobalLayout = QHBoxLayout()
        GlobalLayout.setAlignment(Qt.AlignLeft)
        GlobalLayout.setSpacing(0)
        GlobalLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(GlobalLayout)

        # Название окна

        self.title = QWidget()
        self.title.setObjectName("Title")
        self.title.setFixedSize(1800, 30)

        icon = QLabel()
        icon.setFixedSize(30, 30)
        icon.setObjectName("Icon")
        icon.setPixmap(QPixmap("src/icons/TestLogo.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setContentsMargins(0, 0, 0, 0)
        icon.setAlignment(Qt.AlignCenter)

        self.title_text = QLabel("Editor App")
        self.title_text.setObjectName("TitleText")
        self.title_text.setAlignment(Qt.AlignCenter)
        self.title_text.setFixedSize(90, 30)

        # Расположение иконки + названия

        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        title_layout.addWidget(icon)
        title_layout.addWidget(self.title_text)

        self.title.setLayout(title_layout)

        GlobalLayout.addWidget(self.title)

        # Минимизация, Максимизация, Восстановление, Закрытие

        self.MinButton = QPushButton()
        self.MinButton.setObjectName("MinButton")
        self.MinButton.setFixedSize(40, 30)
        self.MinButton.setIcon(QIcon("src/icons/dark/min.png"))
        self.MinButton.setIconSize(QSize(30, 30))

        self.MaxButton = QPushButton()
        self.MaxButton.setObjectName("MaxButton")
        self.MaxButton.setFixedSize(40, 30)
        self.MaxButton.setVisible(True)
        self.MaxButton.setIcon(QIcon("src/icons/dark/rect.png"))
        self.MaxButton.setIconSize(QSize(30, 30))

        self.RestoreButton = QPushButton()
        self.RestoreButton.setObjectName("RestoreButton")
        self.RestoreButton.setFixedSize(40, 30)
        self.RestoreButton.setVisible(False)
        self.RestoreButton.setIcon(QIcon("src/icons/dark/layer.png"))
        self.RestoreButton.setIconSize(QSize(30, 30))

        self.CloseButton = QPushButton()
        self.CloseButton.setObjectName("CloseButton")
        self.CloseButton.setFixedSize(40, 30)
        self.CloseButton.setIcon(QIcon("src/icons/dark/close.png"))
        self.CloseButton.setIconSize(QSize(30, 30))

        GlobalLayout.addWidget(self.MinButton)
        GlobalLayout.addWidget(self.MaxButton)
        GlobalLayout.addWidget(self.RestoreButton)
        GlobalLayout.addWidget(self.CloseButton)

        # Стиль

        with open("src/style/dark/title_bar.css") as style:
            self.setStyleSheet(style.read())

        # Комманды

        self.update()
