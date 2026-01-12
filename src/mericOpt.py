# -*- coding: utf-8 -*-

import os
import sys
import glob
import shutil
import json
from runpy import run_path
from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
from collections import OrderedDict as ordDict
from src import radarGUI_analyze

class Ui_mericOptSettings(object):

    def setupUi(self, mericOptSettings_p):
        self.mericOptSettings = mericOptSettings_p
        ### loading from temporary file
        # self.config_dic = run_path(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))\
                                #    + '/.gui_tmp_config_{}.py'.format(os.getpid()))
        
        ### loading from shared dictionary
        self.config_dic = radarGUI_analyze.config_data

        self.mericOptSettings.setObjectName("mericOptSettings")
        self.mericOptSettings.resize(500, 357)
        self.centralwidget = QtWidgets.QWidget(self.mericOptSettings)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_opt_settings = QtWidgets.QFrame(self.centralwidget)
        self.frame_opt_settings.setGeometry(QtCore.QRect(30, 30, 451, 271))
        self.frame_opt_settings.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_opt_settings.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_opt_settings.setObjectName("frame_opt_settings")
        self.pushButton_BrowseOptSettings = QtWidgets.QPushButton(self.frame_opt_settings)
        self.pushButton_BrowseOptSettings.setEnabled(True)
        self.pushButton_BrowseOptSettings.setGeometry(QtCore.QRect(320, 80, 99, 27))
        self.pushButton_BrowseOptSettings.setObjectName("pushButton_BrowseOptSettings")
        self.label_Role = QtWidgets.QLabel(self.frame_opt_settings)
        self.label_Role.setEnabled(True)
        self.label_Role.setGeometry(QtCore.QRect(10, 130, 241, 23))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_Role.setFont(font)
        self.label_Role.setObjectName("label_Role")
        self.comboBox_UncoreFreq = QtWidgets.QComboBox(self.frame_opt_settings)
        self.comboBox_UncoreFreq.setEnabled(True)
        self.comboBox_UncoreFreq.setGeometry(QtCore.QRect(160, 195, 111, 27))
        self.comboBox_UncoreFreq.setEditable(False)
        self.comboBox_UncoreFreq.setObjectName("comboBox_UncoreFreq")
        self.lineEdit_OptSettingsFilePath = QtWidgets.QLineEdit(self.frame_opt_settings)
        self.lineEdit_OptSettingsFilePath.setEnabled(True)
        self.lineEdit_OptSettingsFilePath.setGeometry(QtCore.QRect(10, 80, 300, 27))
        self.lineEdit_OptSettingsFilePath.setObjectName("lineEdit_OptSettingsFilePath")
        self.comboBox_NumThreads = QtWidgets.QComboBox(self.frame_opt_settings)
        self.comboBox_NumThreads.setEnabled(True)
        self.comboBox_NumThreads.setGeometry(QtCore.QRect(160, 230, 111, 27))
        self.comboBox_NumThreads.setEditable(False)
        self.comboBox_NumThreads.setObjectName("comboBox_NumThreads")
        self.label_NumThreads = QtWidgets.QLabel(self.frame_opt_settings)
        self.label_NumThreads.setEnabled(True)
        self.label_NumThreads.setGeometry(QtCore.QRect(10, 230, 141, 27))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_NumThreads.setFont(font)
        self.label_NumThreads.setObjectName("label_NumThreads")
        self.label_CoreFreq = QtWidgets.QLabel(self.frame_opt_settings)
        self.label_CoreFreq.setEnabled(True)
        self.label_CoreFreq.setGeometry(QtCore.QRect(10, 160, 111, 27))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_CoreFreq.setFont(font)
        self.label_CoreFreq.setObjectName("label_CoreFreq")
        self.label_UncoreFreq = QtWidgets.QLabel(self.frame_opt_settings)
        self.label_UncoreFreq.setEnabled(True)
        self.label_UncoreFreq.setGeometry(QtCore.QRect(10, 195, 125, 27))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_UncoreFreq.setFont(font)
        self.label_UncoreFreq.setObjectName("label_UncoreFreq")
        self.label_PathToOptSetting = QtWidgets.QLabel(self.frame_opt_settings)
        self.label_PathToOptSetting.setEnabled(True)
        self.label_PathToOptSetting.setGeometry(QtCore.QRect(10, 50, 211, 27))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_PathToOptSetting.setFont(font)
        self.label_PathToOptSetting.setObjectName("label_PathToOptSetting")
        self.comboBox_CoreFreq = QtWidgets.QComboBox(self.frame_opt_settings)
        self.comboBox_CoreFreq.setEnabled(True)
        self.comboBox_CoreFreq.setGeometry(QtCore.QRect(160, 160, 111, 27))
        self.comboBox_CoreFreq.setEditable(False)
        self.comboBox_CoreFreq.setObjectName("comboBox_CoreFreq")
        self.label = QtWidgets.QLabel(self.frame_opt_settings)
        self.label.setGeometry(QtCore.QRect(10, 10, 301, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pushButton_run = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_run.setGeometry(QtCore.QRect(330, 310, 151, 27))
        self.pushButton_run.setObjectName("pushButton_run")

        self.retranslateUi(self.mericOptSettings)
        QtCore.QMetaObject.connectSlotsByName(self.mericOptSettings)

        self.pushButton_run.clicked.connect(self.__create_meric_opt)
        self.pushButton_BrowseOptSettings.clicked.connect(self.__opt_settings_path)

        self.comboBox_opt_settings_list = [self.comboBox_CoreFreq, self.comboBox_UncoreFreq, self.comboBox_NumThreads]
        func_list = []
        for i, e in enumerate(self.comboBox_opt_settings_list):
            func_list.append((lambda tmp: lambda: self.__combo_opt_settings(self.comboBox_opt_settings_list[tmp]))(i))
            self.comboBox_opt_settings_list[i].activated.connect(func_list[-1])

        self.possible_meric_parameters=['']

        for e in self.config_dic['file_name_args_tup']:
            self.possible_meric_parameters.append(e[1])

        self.__get_possible_paramters()

    def retranslateUi(self, mericOptSettings_p):
        _translate = QtCore.QCoreApplication.translate
        mericOptSettings_p.setWindowTitle(_translate("mericOptSettings", "MERIC optimal settings file"))
        self.pushButton_BrowseOptSettings.setText(_translate("mericOptSettings", "Browse.."))
        self.label_Role.setText(_translate("mericOptSettings", "Set roles of parameters in MERIC"))
        self.label_NumThreads.setText(_translate("mericOptSettings", "Number of threads"))
        self.label_CoreFreq.setText(_translate("mericOptSettings", "Core frequency"))
        self.label_UncoreFreq.setText(_translate("mericOptSettings", "Uncore frequency"))
        self.label_PathToOptSetting.setText(_translate("mericOptSettings", "Save path"))
        self.label.setText(_translate("mericOptSettings", "Optimal settings file options"))
        self.pushButton_run.setText(_translate("mericOptSettings", "Generate"))

    def __print_error_msg(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("USER INPUT ERROR")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.exec_()

    def __print_success_msg(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Created Successfully")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


    def __opt_settings_path(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        path = dlg.getExistingDirectory()
        self.lineEdit_OptSettingsFilePath.setText(str(path))

    def __create_meric_opt(self):
        if self.lineEdit_OptSettingsFilePath.text():
            if self.comboBox_CoreFreq.currentText() or self.comboBox_NumThreads.currentText() or\
                    self.comboBox_UncoreFreq.currentText():
                self.__create_config(self.lineEdit_OptSettingsFilePath.text())
        else:
            self.__print_error_msg('Please input required settings')

    def __create_config(self, save_file_path):
        tmp_config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))\
                                   + '/.gui_tmp_config_MERIC_opt_{}.py'.format(os.getpid())
        config_file = open(tmp_config_path, "w")

        config_file.write("import collections\n")
        config_file.write("from collections import OrderedDict as ordDict\n\n")
        config_file.write("root_folder = " + str(self.config_dic['root_folder']) + "\n\n")
        config_file.write("main_reg = " + str(self.config_dic['main_reg']) + "\n\n")
        config_file.write("y_label = " + str(self.config_dic['y_label']).replace("OrderedDict","ordDict") + "\n\n")
        config_file.write("time_energy_vars = " + str(self.config_dic['time_energy_vars']) + "\n\n")
        config_file.write("file_name_args_tup = " + str(self.config_dic['file_name_args_tup']) + "\n\n")
        config_file.write("smooth_runs_average = " + str(self.config_dic['smooth_runs_average']) + "\n\n")
        config_file.write("def_keys_vals = " + str(self.config_dic['def_keys_vals']) + "\n")
        config_file.write("keys_units = " + str(self.config_dic['keys_units']) + "\n\n")
        config_file.write("def_x_val = " + str(self.config_dic['def_x_val']) + "\n")
        config_file.write("x_val_unit = '" + str(self.config_dic['x_val_unit']) + "'\n")
        config_file.write("x_val_multiplier = " + str(self.config_dic['x_val_multiplier']) + "\n\n")
        config_file.write("def_label_val = " + str(self.config_dic['def_label_val']) + "\n")
        config_file.write("func_label_unit = '" + str(self.config_dic['func_label_unit']) + "'\n")
        config_file.write("label_val_multiplier = " + str(self.config_dic['label_val_multiplier']) + "\n\n")
        config_file.write("all_nested_regs = " + str(self.config_dic['all_nested_regs']) + "\n\n")
        config_file.write("iter_call_region = " + str(self.config_dic['iter_call_region']) + "\n\n")
        config_file.write("detailed_info = " + str(self.config_dic['detailed_info']) + "\n\n")
        config_file.write("optim_settings_file_path = None\n")

        config_file.write("generate_optim_settings_file = {")
        first_item = True
        for i, item in enumerate(self.comboBox_opt_settings_list):
            act_label = ''
            if i == 0:
                act_label = 'FREQUENCY'
            elif i == 1:
                act_label = 'UNCORE_FREQUENCY'
            elif i == 2:
                act_label = 'NUM_THREADS'
            if item.currentText() and first_item:
                first_item = False
                config_file.write("'" + item.currentText() + "': '" + act_label + "'")
            elif item.currentText():
                config_file.write(",\n'" + item.currentText() + "': '" + act_label + "'")
        config_file.write("}\n\n")

        config_file.write("baseline = " + str(self.config_dic['baseline']) + "\n\n")
        config_file.write("test_csv_init = " + str(self.config_dic['test_csv_init']))

        config_file.close()

        path_to_radar = Path(sys.path[0] + ('/pathToRadar.json'))
        if path_to_radar.exists():
            with open(path_to_radar) as f:
                try:
                    data = json.load(f)
                    path_to_radar = data['pathToRadar']
                    sys.path.append(path_to_radar)
                    sys.argv = ['', '-configFile', '{}'.format(tmp_config_path)]
                    dlg = QtWidgets.QFileDialog()
                    radar_return = os.system(
                        path_to_radar + "printFullReport.py -configFile {}".format(tmp_config_path))
                    if radar_return == 0:
                        root_folder_lst = [e[0] for e in self.config_dic['root_folder']]
                        for root_folder_ind, root_folder in enumerate(root_folder_lst):
                            # Expanze cesty ke slozce s daty
                            root_folder = os.path.abspath(root_folder)

                            files = glob.iglob(os.path.join(root_folder, "*.opts"))
                            for file in files:
                                if os.path.isfile(file):
                                    if str(os.path.dirname(file)) != save_file_path:
                                        shutil.move(file, save_file_path)
                        self.__print_success_msg('Files with Meric optimal settings has been created.')
                    else:
                        self.__print_error_msg('Radar error.')
                except json.decoder.JSONDecodeError:
                    self.__print_error_msg('pathToRadar.json file is not in valid format')
        else:
            self.__print_error_msg('pathToRadar.json not found')


        os.remove(tmp_config_path)
        self.mericOptSettings.close()

    def __refresh_opt_combos(self):
        for key, val in self.opt_settings_items_dic.items():
            act_val = key.currentText()
            if act_val in self.current_opt_items_dic.keys():
                if self.current_opt_items_dic[act_val] is None and act_val != '':
                    self.current_opt_items_dic[act_val] = key
                    for key2, val2 in self.opt_settings_items_dic.items():
                        if key == key2:
                            continue
                        if act_val in val2:
                            val2.remove(act_val)
            else:
                key.setCurrentText('')

        for key, val in self.opt_settings_items_dic.items():
            act_val = key.currentText()
            key.clear()
            key.addItems(val)
            if key.findText(act_val) != -1:
                key.setCurrentIndex(key.findText(act_val))
            else:
                key.setCurrentIndex(0)

    def __get_possible_paramters(self):
        self.opt_settings_items_dic = {}
        self.current_opt_items_dic = {}
        for e in self.comboBox_opt_settings_list:
            self.opt_settings_items_dic[e] = self.possible_meric_parameters[:]
        for e in self.possible_meric_parameters:
            self.current_opt_items_dic[e] = None
        self.__refresh_opt_combos()

    def __combo_opt_settings(self, current_combo_box):
        selected_item = current_combo_box.currentText()

        if self.current_opt_items_dic[selected_item] != current_combo_box:
            tmp_key = None
            if current_combo_box in self.current_opt_items_dic.values():
                tmp_key = [k for k, v in self.current_opt_items_dic.items() if v == current_combo_box][0]
                self.current_opt_items_dic[tmp_key] = None
            self.current_opt_items_dic[selected_item] = current_combo_box

            if tmp_key is not None and tmp_key != '':
                for key, val in self.opt_settings_items_dic.items():
                    if key == current_combo_box:
                        continue
                    val.append(tmp_key)

            if selected_item != '':
                for key, val in self.opt_settings_items_dic.items():
                    if key == current_combo_box:
                        continue
                    val.remove(selected_item)

        self.__refresh_opt_combos()

