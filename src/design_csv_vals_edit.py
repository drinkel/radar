# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'csv_vals_edit.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_csv_vals_edit(object):
    def setupUi(self, csv_vals_edit):
        csv_vals_edit.setObjectName("csv_vals_edit")
        csv_vals_edit.resize(392, 509)
        self.centralwidget = QtWidgets.QWidget(csv_vals_edit)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 10, 350, 450))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.horizontalHeader().setDefaultSectionSize(350)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(230)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.verticalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setDefaultSectionSize(31)
        self.tableWidget.verticalHeader().setSortIndicatorShown(False)
        self.pushButton_save = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_save.setGeometry(QtCore.QRect(280, 470, 89, 25))
        self.pushButton_save.setObjectName("pushButton_save")

        self.retranslateUi(csv_vals_edit)
        QtCore.QMetaObject.connectSlotsByName(csv_vals_edit)

    def retranslateUi(self, csv_vals_edit):
        _translate = QtCore.QCoreApplication.translate
        csv_vals_edit.setWindowTitle(_translate("csv_vals_edit", "Source CSV values edit"))
        self.pushButton_save.setText(_translate("csv_vals_edit", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    csv_vals_edit = QtWidgets.QMainWindow()
    ui = Ui_csv_vals_edit()
    ui.setupUi(csv_vals_edit)
    csv_vals_edit.show()
    sys.exit(app.exec_())

