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

class Ui_MainWindow(object):
    #optsfilepath = "asd"
    def setupUi(self, MainWindow):
        

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(470, 280)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_BrowseData = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_BrowseData.setEnabled(True)
        self.pushButton_BrowseData.setGeometry(QtCore.QRect(340, 45, 99, 27))
        self.pushButton_BrowseData.setObjectName("pushButton_BrowseData")
        self.label_PathToData = QtWidgets.QLabel(self.centralwidget)
        self.label_PathToData.setEnabled(True)
        self.label_PathToData.setGeometry(QtCore.QRect(30, 15, 241, 27))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_PathToData.setFont(font)
        self.label_PathToData.setObjectName("label_PathToData")
        self.pushButton_BrowseConfigFile = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_BrowseConfigFile.setEnabled(True)
        self.pushButton_BrowseConfigFile.setGeometry(QtCore.QRect(340, 175, 99, 27))
        self.pushButton_BrowseConfigFile.setObjectName("pushButton_BrowseConfigFile")
        self.label_PathToConfig = QtWidgets.QLabel(self.centralwidget)
        self.label_PathToConfig.setEnabled(True)
        self.label_PathToConfig.setGeometry(QtCore.QRect(30, 145, 241, 27))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_PathToConfig.setFont(font)
        self.label_PathToConfig.setObjectName("label_PathToConfig")
        self.pushButton_Configure = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_Configure.setGeometry(QtCore.QRect(30, 230, 99, 27))
        self.pushButton_Configure.setObjectName("pushButton_Configure")
        self.lineEdit_DataPath = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_DataPath.setGeometry(QtCore.QRect(30, 45, 300, 27))
        self.lineEdit_DataPath.setObjectName("lineEdit_DataPath")
        self.lineEdit_ConfigFilePath = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_ConfigFilePath.setGeometry(QtCore.QRect(30, 175, 300, 27))
        self.lineEdit_ConfigFilePath.setObjectName("lineEdit_ConfigFilePath")
        self.pushButton_run = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_run.setGeometry(QtCore.QRect(140, 230, 171, 27))
        self.pushButton_run.setObjectName("pushButton_run")
        self.lineEdit_MericConfigPath = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_MericConfigPath.setGeometry(QtCore.QRect(30, 110, 300, 27))
        self.lineEdit_MericConfigPath.setObjectName("lineEdit_MericConfigPath")
        self.label_PathToMericConfig = QtWidgets.QLabel(self.centralwidget)
        self.label_PathToMericConfig.setEnabled(True)
        self.label_PathToMericConfig.setGeometry(QtCore.QRect(30, 80, 241, 27))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_PathToMericConfig.setFont(font)
        self.label_PathToMericConfig.setObjectName("label_PathToMericConfig")
        self.pushButton_BrowseMericConfig = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_BrowseMericConfig.setEnabled(True)
        self.pushButton_BrowseMericConfig.setGeometry(QtCore.QRect(340, 110, 99, 27))
        self.pushButton_BrowseMericConfig.setObjectName("pushButton_BrowseMericConfig")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)



        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        MainWindow.setWindowFlags(QtCore.Qt.WindowType.WindowCloseButtonHint |
                          QtCore.Qt.WindowType.WindowTitleHint |
                          QtCore.Qt.WindowType.WindowMinimizeButtonHint)
        MainWindow.setFixedSize(MainWindow.size())

        self.pushButton_BrowseData.clicked.connect(self.__getDataPath)
        self.pushButton_BrowseMericConfig.clicked.connect(self.__getMericConfigFilePath)
        self.pushButton_BrowseConfigFile.clicked.connect(self.__getConfigFilePath)
        self.pushButton_Configure.clicked.connect(self.__Configure)
        self.pushButton_run.clicked.connect(self.__runRadar)
        #app.aboutToQuit.connect(self.closeEvent)
        app.aboutToQuit.connect(lambda: self.closeEvent(QCloseEvent()))


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RADAR configuration"))
        self.pushButton_BrowseData.setText(_translate("MainWindow", "Browse.."))
        self.label_PathToData.setText(_translate("MainWindow", "Path to MERIC measurement data"))
        self.pushButton_BrowseConfigFile.setText(_translate("MainWindow", "Browse.."))
        self.label_PathToConfig.setText(_translate("MainWindow", "<html><head/><body><p>Path to RADAR configuration file</p></body></html>"))
        self.pushButton_Configure.setText(_translate("MainWindow", "Configure"))
        self.pushButton_run.setText(_translate("MainWindow", "Run RADAR analysis"))
        self.label_PathToMericConfig.setText(_translate("MainWindow", "Path to MERIC configuration file"))
        self.pushButton_BrowseMericConfig.setText(_translate("MainWindow", "Browse.."))

    def __print_error_msg(self, text, title):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Close)
        msg.exec()

    def __runRadar(self):
        if self.lineEdit_ConfigFilePath.text() and os.path.isfile(
                self.lineEdit_ConfigFilePath.text()) and self.lineEdit_ConfigFilePath.text().endswith(
                ".py") and self.lineEdit_DataPath.text() == '':
            if self.lineEdit_MericConfigPath.text() and os.path.isfile(self.lineEdit_MericConfigPath.text()) and self.lineEdit_MericConfigPath.text().endswith(".opts"):
                radarGUI_analyze.TabWidget('', self.lineEdit_ConfigFilePath.text(), runRadar=True,
                                           meric_config_path=self.lineEdit_MericConfigPath.text())
            elif self. lineEdit_MericConfigPath.text() and (not(os.path.isfile(self.lineEdit_MericConfigPath.text())) or not(self.lineEdit_MericConfigPath.text().endswith(".opts"))):
                self.__print_error_msg("MERIC config not found. Using old version of RADAR!", "MERIC config not found")
                radarGUI_analyze.TabWidget('', self.lineEdit_ConfigFilePath.text(), runRadar=True)
            else:
                radarGUI_analyze.TabWidget('', self.lineEdit_ConfigFilePath.text(), runRadar=True)
            MainWindow.close()
        elif self.lineEdit_ConfigFilePath.text() and self.lineEdit_DataPath.text():
            self.__print_error_msg('Unable to run RADAR analysis with current settings. Please press "Configure"'
                                   ' button instead.', "Input error")
        elif self.lineEdit_ConfigFilePath.text():
            self.__print_error_msg("Config file does not exists or path to config file is invalid.", "Input error")

    def closeEvent(self, event):
        act_dir = os.path.dirname(os.path.realpath(__file__))
        hidden_config_path = act_dir + '/.gui_tmp_config_{}.py'.format(os.getpid())
        if os.path.exists(hidden_config_path):
            os.remove(hidden_config_path)

        other_tmp_confs = [i for i in os.listdir(act_dir) if os.path.isfile(os.path.join(act_dir, i)) and
                           '.gui_tmp_config' in i]
        for conf in other_tmp_confs:
            pid = int(conf.split("_")[-1].split(".")[0])
            if not self.pid_exists(pid):
                os.remove(act_dir + '/' + conf)

        #sys.exit(0)

    def pid_exists(self, pid):
        """Check whether pid exists in the current process table.
        UNIX only.
        """
        if pid < 0:
            return False
        if pid == 0:
            raise ValueError('invalid PID 0')
        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                # ESRCH == No such process
                return False
            elif err.errno == errno.EPERM:
                # EPERM clearly means theres a process to deny access to
                return True
            else:
                # According to "man 2 kill" possible error values are
                # (EINVAL, EPERM, ESRCH)
                raise
        else:
            return True

    def __getDataPath(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        #self.lineEdit_DataPath.setText("/home/okozinski/Desktop/radar/siesta_test")
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory")
        if directory:  # Ensure the user selected a directory
            self.lineEdit_DataPath.setText(directory)




    def __getConfigFilePath(self):
        dlg = QtWidgets.QFileDialog()

        self.lineEdit_ConfigFilePath.setText(QtWidgets.QFileDialog.getOpenFileName(filter='Python files (*.py)')[0]) #QT6

    def __getMericConfigFilePath(self):
        dlg = QtWidgets.QFileDialog()
        #self.lineEdit_MericConfigPath.setText("/home/okozinski/Desktop/radar/siesta_test/opts.opts")
        self.lineEdit_MericConfigPath.setText(QtWidgets.QFileDialog.getOpenFileName(filter='Text files (*.opts)')[0]) #QT6

        file_path = ".optspath"
        path = self.lineEdit_MericConfigPath.text()
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "w") as file:
            file.write(path)


    def __Configure(self):

        if self.lineEdit_DataPath.text() and not self.lineEdit_ConfigFilePath.text():
            self.lineEdit_DataPath.setText(os.path.abspath(self.lineEdit_DataPath.text()))
            if os.path.isdir(self.lineEdit_DataPath.text()):
                if not glob.glob(glob.escape(self.lineEdit_DataPath.text()) + '/*/*.csv'):
                    self.__print_error_msg("MERIC measurement does not exists or path to measurement is invalid.",
                                           "Input error")
                    return
                if self.lineEdit_MericConfigPath.text() and os.path.isfile(self.lineEdit_MericConfigPath.text()) and self.lineEdit_MericConfigPath.text().endswith(".opts"):
                    config_window = radarGUI_analyze.TabWidget(self.lineEdit_DataPath.text(), '',
                                                               meric_config_path=self.lineEdit_MericConfigPath.text())
                elif self.lineEdit_MericConfigPath.text() and (not (os.path.isfile(self.lineEdit_MericConfigPath.text())) or not (self.lineEdit_MericConfigPath.text().endswith(".opts"))):
                    self.__print_error_msg("MERIC config not found. Using old version of RADAR!",
                                           "MERIC config not found")
                    config_window = radarGUI_analyze.TabWidget(self.lineEdit_DataPath.text(), '')
                else:
                    config_window = radarGUI_analyze.TabWidget(self.lineEdit_DataPath.text(), '')
                config_window.show()
                MainWindow.close()

        if self.lineEdit_ConfigFilePath.text() and os.path.isfile(self.lineEdit_ConfigFilePath.text()) and\
                self.lineEdit_ConfigFilePath.text().endswith(".py") and self.lineEdit_DataPath.text() != '':
            self.lineEdit_DataPath.setText(os.path.abspath(self.lineEdit_DataPath.text()))
            if os.path.isdir(self.lineEdit_DataPath.text()):
                if not glob.glob(glob.escape(self.lineEdit_DataPath.text()) + '/*/*.csv'):
                    self.__print_error_msg("MERIC measurement does not exists or path to measurement is invalid.",
                                           "Input error")
                    return
                if self.lineEdit_MericConfigPath.text() and os.path.isfile(self.lineEdit_MericConfigPath.text()) and self.lineEdit_MericConfigPath.text().endswith(".opts"):
                    config_window = radarGUI_analyze.TabWidget(self.lineEdit_DataPath.text(),
                                                               self.lineEdit_ConfigFilePath.text(),
                                                               meric_config_path=self.lineEdit_MericConfigPath.text())
                elif self.lineEdit_MericConfigPath.text() and (not (os.path.isfile(self.lineEdit_MericConfigPath.text())) or not (self.lineEdit_MericConfigPath.text().endswith(".opts"))):
                    self.__print_error_msg("MERIC config not found. Using old version of RADAR!",
                                           "MERIC config not found")
                    config_window = radarGUI_analyze.TabWidget(self.lineEdit_DataPath.text(), self.lineEdit_ConfigFilePath.text())
                else:
                    config_window = radarGUI_analyze.TabWidget(self.lineEdit_DataPath.text(),
                                                               self.lineEdit_ConfigFilePath.text())
                config_window.show()
                MainWindow.close()
            else:
                self.__print_error_msg("MERIC measurement does not exists or path to measurement is invalid.",
                                       "Input error")
                return

        elif self.lineEdit_ConfigFilePath.text() and os.path.isfile(self.lineEdit_ConfigFilePath.text()) and \
                self.lineEdit_ConfigFilePath.text().endswith(".py") and self.lineEdit_DataPath.text() == '':
            if self.lineEdit_MericConfigPath.text()  and os.path.isfile(self.lineEdit_MericConfigPath.text()) and self.lineEdit_MericConfigPath.text().endswith(".opts"):
                config_window = radarGUI_analyze.TabWidget('', self.lineEdit_ConfigFilePath.text(),
                                                           meric_config_path=self.lineEdit_MericConfigPath.text())
            elif self.lineEdit_MericConfigPath.text() and (not (os.path.isfile(self.lineEdit_MericConfigPath.text())) or not (self.lineEdit_MericConfigPath.text().endswith(".opts"))):
                self.__print_error_msg("MERIC config not found. Using old version of RADAR!", "MERIC config not found")
                config_window = radarGUI_analyze.TabWidget('', self.lineEdit_ConfigFilePath.text())
            else:
                config_window = radarGUI_analyze.TabWidget('', self.lineEdit_ConfigFilePath.text())
            config_window.show()
            MainWindow.close()

        elif self.lineEdit_ConfigFilePath.text():
            self.__print_error_msg("Config file does not exists or path to config file is invalid.", "Input error")
        '''else:
            ui.setupUi(TabWidget, self.lineEdit_DataPath.text(), '')
            TabWidget.show()
            MainWindow.hide()'''

    def main():
        import sys

        app = QtWidgets.QApplication(sys.argv)

        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()

        sys.exit(app.exec())

if __name__ == "__main__":
    main()



