#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6 import QtCore, QtGui, QtWidgets
from src import radarGUI_analyze
import os
import glob
import errno
import sys
from PyQt6.QtGui import QCloseEvent
optsfilepath = "asd"
from src.ui_base import Ui_MainWindow

def main():
    # Мы переносим import sys внутрь, чтобы он точно был доступен
    import sys
    
    # Создаем приложение (обязательно должно быть внутри функции)
    global app 
    app = QtWidgets.QApplication(sys.argv)

    global MainWindow
    MainWindow = QtWidgets.QMainWindow()
    
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()





