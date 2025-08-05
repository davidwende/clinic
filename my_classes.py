from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout

class HoverButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.defaultStyleSheet = """
            background-color: lightgray;
            border: 2px solid gray;
            border-radius: 10px;
        """
        self.hoverStyleSheet = """
            background-color: green;
            border: 2px solid gray;
            border-radius: 10px;
        """
        self.setStyleSheet(self.defaultStyleSheet)

    def enterEvent(self, event):
        self.setStyleSheet(self.hoverStyleSheet)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.defaultStyleSheet)
        super().leaveEvent(event)

class HoverButtonVisit(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.defaultStyleSheet = """
            background-color: lightgray;
            border: 2px solid gray;
            border-radius: 10px;
        """
        self.hoverStyleSheet = """
            background-color: green;
            border: 2px solid gray;
            border-radius: 10px;
        """
        self.setStyleSheet(self.defaultStyleSheet)

    def enterEvent(self, event):
        self.setStyleSheet(self.hoverStyleSheet)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.defaultStyleSheet)
        super().leaveEvent(event)

