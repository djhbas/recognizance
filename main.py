import os
import sys

import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtGui import QFontDatabase

import paths
import windows

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QFontDatabase.addApplicationFont(':/Resource/font/HelveticaNowDisplay-Black.otf')
    QFontDatabase.addApplicationFont(':/Resource/font/HelveticaNowDisplay-Light.otf')
    QFontDatabase.addApplicationFont(':/Resource/font/HelveticaNowDisplay-Regular.otf')
    QFontDatabase.addApplicationFont(':/Resource/font/HelveticaNowDisplay-Black.otf')

    if os.path.exists(paths.resource_add):
        pass
    else:
        os.mkdir(paths.resource_add)
    if os.path.exists(paths.data_add):
        pass
    else:
        os.mkdir(paths.data_add)
    if os.path.exists(paths.tmp_add):
        pass
    else:
        os.mkdir(paths.tmp_add)
    if os.path.exists(paths.img_add):
        pass
    else:
        os.mkdir(paths.img_add)

    window = windows.Login()
    window.show()
    app.exec()
