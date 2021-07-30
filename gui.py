import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi


class Window(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("te.ui", self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.button.clicked.connect(self.print_something)

    def print_something(self):
        print("HAHAH")


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
