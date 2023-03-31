from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QSizePolicy, QDialogButtonBox


class TitleWidget(QLabel):
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

        # Иконка окна

        icon = QLabel()
        icon.setFixedSize(30, 30)
        icon.setObjectName("Icon")
        icon.setPixmap(QPixmap("src/icons/TestLogo.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setContentsMargins(0, 0, 0, 0)
        icon.setAlignment(Qt.AlignCenter)

        GlobalLayout.addWidget(icon)

        # Диалоговые кнопки

        self.file_button = QPushButton("Project")
        self.file_button.setFixedSize(len(self.file_button.text()) * 10, 24)
        self.file_button.setObjectName("DialogueButton")

        self.edit_button = QPushButton("Edit")
        self.edit_button.setFixedSize(len(self.edit_button.text()) * 10, 24)
        self.edit_button.setObjectName("DialogueButton")

        self.selection_button = QPushButton("Selection")
        self.selection_button.setFixedSize(len(self.selection_button.text()) * 10, 24)
        self.selection_button.setObjectName("DialogueButton")

        self.view_button = QPushButton("View")
        self.view_button.setFixedSize(len(self.view_button.text()) * 10, 24)
        self.view_button.setObjectName("DialogueButton")

        self.help_button = QPushButton("Help")
        self.help_button.setFixedSize(len(self.help_button.text()) * 10, 24)
        self.help_button.setObjectName("DialogueButton")

        GlobalLayout.addWidget(self.file_button)
        GlobalLayout.addWidget(self.edit_button)
        GlobalLayout.addWidget(self.selection_button)
        GlobalLayout.addWidget(self.view_button)
        GlobalLayout.addWidget(self.help_button)

        # Название текущего проекта

        self.project_name = QLabel("Editor App")
        self.project_name.setFixedHeight(30)
        self.project_name.setObjectName("ProjectName")
        self.project_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.project_name.setAlignment(Qt.AlignCenter)
        self.project_name.setContentsMargins(0, 0, 200, 0)

        GlobalLayout.addWidget(self.project_name)

        # Минимизация, Максимизация, Восстановление, Закрытие

        self.MinButton = QPushButton()
        self.MinButton.setObjectName("WindowButton")
        self.MinButton.setFixedSize(45, 30)
        self.MinButton.setIcon(QIcon("src/icons/dark/new_dark/minimize.png"))
        self.MinButton.setIconSize(QSize(45, 30))

        self.MaxButton = QPushButton()
        self.MaxButton.setObjectName("WindowButton")
        self.MaxButton.setFixedSize(45, 30)
        self.MaxButton.setVisible(False)
        self.MaxButton.setIcon(QIcon("src/icons/dark/new_dark/maximize.png"))
        self.MaxButton.setIconSize(QSize(45, 30))

        self.RestoreButton = QPushButton()
        self.RestoreButton.setObjectName("WindowButton")
        self.RestoreButton.setFixedSize(45, 30)
        self.RestoreButton.setVisible(True)
        self.RestoreButton.setIcon(QIcon("src/icons/dark/new_dark/restore.png"))
        self.RestoreButton.setIconSize(QSize(45, 30))

        self.CloseButton = QPushButton()
        self.CloseButton.setObjectName("WindowCloseButton")
        self.CloseButton.setFixedSize(45, 30)
        self.CloseButton.setIcon(QIcon("src/icons/dark/new_dark/close.png"))
        self.CloseButton.setIconSize(QSize(45, 30))

        GlobalLayout.addWidget(self.MinButton)
        GlobalLayout.addWidget(self.MaxButton)
        GlobalLayout.addWidget(self.RestoreButton)
        GlobalLayout.addWidget(self.CloseButton)

        # Стиль

        with open("src/style/dark/title_bar.css") as style:
            self.setStyleSheet(style.read())

        self.update()
