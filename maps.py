import paths

from PyQt6 import QtWidgets, QtCore, uic
from PyQt6.QtGui import QFont, QPalette, QColor


class LocoutMaps(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowMinMaxButtonsHint |
                            QtCore.Qt.WindowType.WindowCloseButtonHint)
        uic.loadUi(paths.LOCOUT, self)
        self.locout_maps.setHtml(open(paths.MAP_HTML).read())
        self.blist.setFont(QFont(paths.HND_LIGHT, 14))
        self.blist.setAutoFillBackground(False)
        self.blist.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        palette = self.blist.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        self.blist.setPalette(palette)
        self.show()
        self.backbutt.clicked.connect(self.back)

    def back(self):
        self.hide()
