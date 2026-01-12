# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainMenu.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainMenu(object):
    def setupUi(self, MainMenu):
        MainMenu.setObjectName("MainMenu")
        MainMenu.resize(267, 470)
        self.centralwidget = QtWidgets.QWidget(MainMenu)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_analysis = QtWidgets.QFrame(self.centralwidget)
        self.frame_analysis.setGeometry(QtCore.QRect(10, 10, 251, 210))
        self.frame_analysis.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_analysis.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_analysis.setObjectName("frame_analysis")
        self.pushButton_plot = QtWidgets.QPushButton(self.frame_analysis)
        self.pushButton_plot.setGeometry(QtCore.QRect(10, 10, 231, 40))
        self.pushButton_plot.setObjectName("pushButton_plot")

        #self.pushButton_timeline = QtWidgets.QPushButton(self.frame_analysis)
        #self.pushButton_timeline.setGeometry(QtCore.QRect(10, 110, 231, 40))
        #self.pushButton_timeline.setObjectName("pushButton_timeline")
        #self.pushButton_tree = QtWidgets.QPushButton(self.frame_analysis)
        #self.pushButton_tree.setGeometry(QtCore.QRect(10, 10, 231, 40))
        #self.pushButton_tree.setObjectName("pushButton_tree")
        self.pushButton_overall = QtWidgets.QPushButton(self.frame_analysis)
        self.pushButton_overall.setGeometry(QtCore.QRect(10, 60, 231, 40))
        self.pushButton_overall.setObjectName("pushButton_overall")
        self.pushButton_heatmap = QtWidgets.QPushButton(self.frame_analysis)
        self.pushButton_heatmap.setGeometry(QtCore.QRect(10, 110, 231, 40))
        self.pushButton_heatmap.setObjectName("pushButton_heatmap")
        #self.pushButton_average_start = QtWidgets.QPushButton(self.frame_analysis)
        #self.pushButton_average_start.setGeometry(QtCore.QRect(10, 360, 231, 40))
        #self.pushButton_average_start.setObjectName("pushButton_average_start")
        #self.pushButton_table_nested_region = QtWidgets.QPushButton(self.frame_analysis)
        #self.pushButton_table_nested_region.setGeometry(QtCore.QRect(10, 310, 231, 40))
        #self.pushButton_table_nested_region.setObjectName("pushButton_table_nested_region")
        self.pushButton_samples = QtWidgets.QPushButton(self.frame_analysis)
        self.pushButton_samples.setGeometry(QtCore.QRect(10, 160, 231, 40))
        self.pushButton_samples.setObjectName("pushButton_samples")



        self.frame_options = QtWidgets.QFrame(self.centralwidget)
        self.frame_options.setGeometry(QtCore.QRect(10, 230, 251, 160))
        self.frame_options.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_options.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_options.setObjectName("frame_options")
        #self.pushButton_generate_latex = QtWidgets.QPushButton(self.frame_options)
        #self.pushButton_generate_latex.setGeometry(QtCore.QRect(10, 10, 231, 40))
        #self.pushButton_generate_latex.setObjectName("pushButton_generate_latex")
        self.pushButton_generate_meric = QtWidgets.QPushButton(self.frame_options)
        self.pushButton_generate_meric.setGeometry(QtCore.QRect(10, 10, 231, 40))
        self.pushButton_generate_meric.setObjectName("pushButton_generate_meric")
        self.pushButton_edit_radar = QtWidgets.QPushButton(self.frame_options)
        self.pushButton_edit_radar.setGeometry(QtCore.QRect(10, 60, 231, 40))
        self.pushButton_edit_radar.setObjectName("pushButton_edit_radar")
        self.pushButton_save_radar = QtWidgets.QPushButton(self.frame_options)
        self.pushButton_save_radar.setGeometry(QtCore.QRect(10, 110, 231, 40))
        self.pushButton_save_radar.setObjectName("pushButton_save_radar")



        
        self.frame_restart = QtWidgets.QFrame(self.centralwidget)
        self.frame_restart.setGeometry(QtCore.QRect(10, 400, 251, 61))
        self.frame_restart.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_restart.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_restart.setObjectName("frame_restart")
        self.pushButton_restart = QtWidgets.QPushButton(self.frame_restart)
        self.pushButton_restart.setGeometry(QtCore.QRect(10, 10, 231, 40))
        self.pushButton_restart.setObjectName("pushButton_restart")
        self.frame_restart.raise_()
        self.frame_options.raise_()
        self.frame_analysis.raise_()
        # MainMenu.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainMenu)
        self.statusbar.setObjectName("statusbar")
        # MainMenu.setStatusBar(self.statusbar)

        self.retranslateUi(MainMenu)
        QtCore.QMetaObject.connectSlotsByName(MainMenu)

    def retranslateUi(self, MainMenu):
        _translate = QtCore.QCoreApplication.translate
        MainMenu.setWindowTitle(_translate("MainMenu", "Radar analysis"))
        self.pushButton_plot.setText(_translate("MainMenu", "Plots"))
        #self.pushButton_tree.setText(_translate("MainMenu", "Region tree"))
        #self.pushButton_timeline.setText(_translate("MainMenu", "Timeline"))

        self.pushButton_overall.setText(_translate("MainMenu", "Overall application evaluation"))
        self.pushButton_heatmap.setText(_translate("MainMenu", "Heatmaps"))
        #self.pushButton_average_start.setText(_translate("MainMenu", "Average program start"))
        #self.pushButton_table_nested_region.setText(_translate("MainMenu", "Nested region table"))
        self.pushButton_samples.setText(_translate("MainMenu", "Power samples timeline"))
        #self.pushButton_generate_latex.setText(_translate("MainMenu", "Generate LaTeX report"))
        self.pushButton_generate_meric.setText(_translate("MainMenu", "Generate MERIC config"))
        self.pushButton_edit_radar.setText(_translate("MainMenu", "Edit RADAR config"))
        self.pushButton_save_radar.setText(_translate("MainMenu", "Save current RADAR config"))
        self.pushButton_restart.setText(_translate("MainMenu", "Restart Radar analysis"))
