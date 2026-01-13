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
    import sys
    # 1. Создаем приложение ПЕРВЫМ делом
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    # 2. Создаем окно
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    # 3. Показываем
    MainWindow.show()
    
    # 4. Запускаем цикл обработки событий
    print("RADAR GUI запущен. Нажмите Ctrl+C для выхода, если окно не появилось.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()






