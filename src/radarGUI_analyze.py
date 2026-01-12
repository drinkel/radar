# # -*- coding: utf-8 -*-
import csv
import glob
import os
import sys
import json
from src import main_menu_analyze
from src import pydot_example
from src import design_radarGUI_analyze
from collections import OrderedDict as ordDict
from runpy import run_path
from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
import pprint
from PyQt6.QtCore import Qt

from collections import OrderedDict

pp = pprint.PrettyPrinter(indent=4)


class CustomStepSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self):
        QtWidgets.QDoubleSpinBox.__init__(self)

    def stepBy(self, steps: int):
        if steps == 1:
            self.setValue(self.value()*10)
            if self.decimals() > 0:
                self.setDecimals(self.decimals()-1)
        if steps == -1:
            if self.decimals() < 324 and (self.value()/10) % 1 != 0:  # maximum value for decimals is 323
                self.setDecimals(self.decimals()+1)
            self.setValue(self.value()/10)

class TabWidget(QtWidgets.QTabWidget, design_radarGUI_analyze.Ui_TabWidget):
    def __init__(self, DataPath, ConfigPath, runRadar=False, main_menu_instance=None, meric_config_path=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.WindowCloseButtonHint | QtCore.Qt.WindowType.WindowTitleHint |
                            QtCore.Qt.WindowType.WindowMinimizeButtonHint)
        self.setFixedSize(self.size())
        self.current_labels_dic = {'xLabel': None, 'funcLabel': None}
        self.tab_widget = None
        self.data_path = ''
        self.config_path = ''
        self.tab_Regions = None
        self.regions = []
        self.ylabel_dic = dict()
        self.parameters_count = 0
        self.possible_time_vars = []
        self.possible_energy_vars = []
        self.time_var = ''
        self.energy_var = ''
        self.measurement_params = []

        self.possible_meric_parameters = []
        self.opt_settings_items_dic = {}
        self.current_opt_items_dic = {}
        self.selected_y_labels = []
        self.onlyFloat = QtGui.QDoubleValidator()
        self.all_nested_regs_selected = False
        self.save_file_path = ''
        self.config_dic = {}
        self.tree_data_selected = dict()

        self.tab_widget = self
        self.data_path = DataPath
        self.config_path = ConfigPath
        self.main_menu_instance = main_menu_instance
        self.meric_config_path = meric_config_path

        if self.config_path:
            print("Error radarGUI_analyze - missing config_dic")
            self.config_dic = run_path(self.config_path)

        if 'root_' \
           'folder' in self.config_dic and self.config_dic['root_folder'][0][0] and not self.data_path:
            self.data_path = self.config_dic['root_folder'][0][0]

        for region in os.listdir(self.data_path):
            if os.path.isdir(self.data_path + "/" + region):
                if glob.glob(glob.escape(self.data_path) + '/' + glob.escape(region) + '/*.csv'):
                    self.regions.append(region)
        self.regions = sorted(self.regions, key=lambda s: s.lower())

        csv_names = glob.glob(glob.escape(self.data_path) + '/' + glob.escape(self.regions[0]) + '/*.csv')
        first_csv_path = csv_names[0]
        for i in csv_names:
            if i.endswith("_static"):
                first_csv_path = i
                continue
        dkey = ''
        reading_samples = False
        with open(first_csv_path) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for i, line in enumerate(reader):
                if not line[0].startswith('#') and reading_samples:
                    continue
                if line[0].startswith('#') and 'samples' in line[0]:
                    reading_samples = True
                if line[0].startswith('#') and not line[0].startswith("# CALLTREE") and 'samples' not in line[0] and \
                        'Store CONTINUAL' not in line[0]:
                    line[0] = line[0].split('#')[1]
                    dkey = line[0].strip()
                    reading_samples = False
                elif dkey and line[0] is not dkey and not line[0].startswith("# CALLTREE") and 'samples' not in line[0]\
                    and 'Store CONTINUAL' not in line[0]:
                    self.ylabel_dic.setdefault(dkey, []).append(line[0].strip())

        for k, v in self.ylabel_dic.items():
            self.ylabel_dic[k] = sorted(list(set(v)))

        first_csv_name = first_csv_path.split('/')[-1]
        self.parameters_count = first_csv_name.count('_')+1
        self.parameter_values_dic = {}

        for i in range(self.parameters_count):
            self.parameter_values_dic[i] = []
        pocet = csv_names[0].split('/')[-1]
        pocet = pocet.split('_')
        pocet = len(pocet)

        for n, item in enumerate(csv_names):
            item = item.split('/')[-1]
            item = os.path.splitext(item)[0]
            item = item.split('_')

            if item[0] == "log" or item[0] == "default":
                deflist = []
                for i in range(pocet):
                    deflist.append(str(0))
                item = deflist


            for i in range(self.parameters_count):
                self.parameter_values_dic[i].append(item[i])

        for k, v in self.parameter_values_dic.items():
            if v[0].isdigit():
                self.parameter_values_dic[k] = sorted(list(set(v)), key=lambda s: int(s), reverse=True)
            else:
                self.parameter_values_dic[k] = sorted(list(set(v)), reverse=True)

        measurement_info_path = Path(self.data_path + '/measurementInfo.json')

        if measurement_info_path.exists():
            with open(measurement_info_path) as f:
                try:
                    measurement_info_file_data = json.load(f)
                    self.measurement_params = measurement_info_file_data['DataFormat'].split("_")

                except json.decoder.JSONDecodeError:
                    self.__print_error_msg('measurementInfo.json file is not in valid format')

        i = 0
        self.reg_times = {}
        for subdir, dirs, files in os.walk(self.data_path):
            if not i:
                i += 1
                continue

            with open('{}/{}'.format(subdir, files[0])) as f:
                for line in f:
                    line = line.strip()
                    if 'Runtime of function' in line or 'AVG runtime of function' in line:
                        tmp2 = float(line.split(',')[-1])
                        self.reg_times[subdir.split('/')[-1]] = tmp2
                        break

        myform_param = QtWidgets.QFormLayout()
        label_parameters_list = []
        self.lineEdit_parameters_list = []
        self.comboBox_parameters_list = []
        self.comboBox_default_vals_list = []
        self.spinBox_default_multp_list = []
        self.lineEdit_default_unit_list = []
        self.all_parameters = ['key', 'config', 'funcLabel', 'xLabel']
        self.parameters_combobox_items_dic = {}

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)

        head_label1 = QtWidgets.QLabel()
        head_label1.setFixedWidth(150)
        head_label1.setFont(font)
        head_label2 = QtWidgets.QLabel('Role')
        head_label2.setFixedWidth(100)
        head_label2.setFont(font)
        head_label3 = QtWidgets.QLabel('Default value')
        head_label3.setFixedWidth(150)
        head_label3.setFont(font)
        head_label4 = QtWidgets.QLabel('Multiplier')
        head_label4.setFixedWidth(100)
        head_label4.setFont(font)
        head_label5 = QtWidgets.QLabel('Unit')
        head_label5.setFixedWidth(100)
        head_label5.setFont(font)
        new_row = QtWidgets.QHBoxLayout()
        new_row.addWidget(head_label1)
        new_row.addWidget(head_label2)
        new_row.addWidget(head_label3)
        new_row.addWidget(head_label4)
        new_row.addWidget(head_label5)
        myform_param.addRow(new_row)

        self.isFake = False
        if ("fake" in self.measurement_params):
            self.isFake = True
        for i in range(self.parameters_count):
            if (self.measurement_params[i] != "fake"):
                label_parameters_list.append(QtWidgets.QLabel('Parameter {}'.format(i+1)))
            else:
                label_parameters_list.append(QtWidgets.QLabel(''))
            label_parameters_list[i].setFont(font)
            myform_param.addRow(label_parameters_list[i])
            self.lineEdit_parameters_list.append(QtWidgets.QLineEdit())
            self.comboBox_parameters_list.append(QtWidgets.QComboBox())
            self.comboBox_default_vals_list.append(QtWidgets.QComboBox())
            self.spinBox_default_multp_list.append(CustomStepSpinBox())
            self.lineEdit_default_unit_list.append(QtWidgets.QLineEdit())

            self.parameters_combobox_items_dic[self.comboBox_parameters_list[-1]] = list(self.all_parameters)
            self.comboBox_default_vals_list[i].addItems(self.parameter_values_dic[i])
            self.comboBox_parameters_list[i].addItems(self.all_parameters)

            func_list = []
            func_list.append((lambda tmp: lambda: self.__parameters_combobox(self.comboBox_parameters_list[tmp]))(i))

            self.comboBox_parameters_list[i].activated.connect(func_list[-1])
            self.lineEdit_parameters_list[i].textChanged.connect(self.__parameter_name_changed)

            if self.measurement_params and i < len(self.measurement_params):
                self.lineEdit_parameters_list[i].setText(self.measurement_params[i])
                self.lineEdit_parameters_list[i].setReadOnly(True)
                self.lineEdit_parameters_list[i].setStyleSheet("QLineEdit {background-color: #f4f4f4; color: #606060;}")


            if (self.measurement_params[i] != "fake"):
                self.lineEdit_parameters_list[i].setFixedWidth(150)
                self.comboBox_parameters_list[i].setFixedWidth(100)
                self.comboBox_default_vals_list[i].setFixedWidth(150)
                self.spinBox_default_multp_list[i].setFixedWidth(100)
                self.spinBox_default_multp_list[i].setEnabled(False)
                self.spinBox_default_multp_list[i].setValue(1)
                self.spinBox_default_multp_list[i].setDecimals(0)
                self.spinBox_default_multp_list[i].setRange(sys.float_info.min, sys.float_info.max)
                self.lineEdit_default_unit_list[i].setFixedWidth(100)
            else:
                ### pokud je parameter fake, tak se nezobrazuje - osa je automaticky prirazena
                ### jako opacna vuci ladenemu parametru
                self.lineEdit_parameters_list[i].setFixedWidth(0)
                self.comboBox_parameters_list[i].setFixedWidth(0)
                self.comboBox_default_vals_list[i].setFixedWidth(0)
                self.spinBox_default_multp_list[i].setFixedWidth(0)
                self.spinBox_default_multp_list[i].setEnabled(False)
                self.spinBox_default_multp_list[i].setValue(1)
                self.spinBox_default_multp_list[i].setDecimals(0)
                self.spinBox_default_multp_list[i].setRange(sys.float_info.min, sys.float_info.max)
                self.lineEdit_default_unit_list[i].setFixedWidth(0)



            new_row = QtWidgets.QHBoxLayout()
            new_row.addWidget(self.lineEdit_parameters_list[i])
            new_row.addWidget(self.comboBox_parameters_list[i])
            new_row.addWidget(self.comboBox_default_vals_list[i])
            new_row.addWidget(self.spinBox_default_multp_list[i])
            new_row.addWidget(self.lineEdit_default_unit_list[i])

            myform_param.addRow(new_row)


        self.frame_parameters.setLayout(myform_param)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.frame_parameters)
        scroll.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout(self.widget_parameters)
        layout.addWidget(scroll)



        self.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

        myform = QtWidgets.QFormLayout()
        self.nested_regs_list = []

        self.nested_regs_selected_dic = ordDict()


        for i, region in enumerate(self.regions):
            self.nested_regs_list.append(QtWidgets.QCheckBox(region))
            if 'all_nested_regs' in self.config_dic and region in self.config_dic['all_nested_regs']:
                self.nested_regs_list[i].setCheckState(2)
            self.nested_regs_list[i].toggled.connect(self.__nested_region_check_changed)
            myform.addRow(self.nested_regs_list[i])
        self.frame_nested_regions.setLayout(myform)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.frame_nested_regions)
        scroll.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout(self.widget_nested_regions)
        layout.addWidget(scroll)
        self.frame_time_energy.setEnabled(False)
        self.doubleSpinBox.setSingleStep(0.1)
        self.pushButton_Regions_Next.clicked.connect(self.__next)
        self.pushButton_DataParam_Prev.clicked.connect(self.__previous)
        self.pushButton_Regions_All.clicked.connect(self.__select_all_nested_regions)
        self.pushButton_run.clicked.connect(self.__save_and_run)
        self.pushButton_tree.clicked.connect(self.__show_tree)
        self.pushButton_filter.clicked.connect(self.__filter)
        

        self.comboBox_MainRegion.addItems(self.regions)
        for region in self.regions:
            if region.endswith('_static'):
                self.comboBox_MainRegion.setCurrentText(region)
        
        self.comboBox_MainRegion.setEditable(False)
        self.comboBox_MainRegion.activated.connect(self.__update_nested_regions)
        self.comboBox_IterationRegion.addItems(['None'] + self.regions)
        self.comboBox_IterationRegion.setEditable(False)
        self.checkBox_time_energy_vars.stateChanged.connect(self.__opt_time_eneregy)
        self.treeWidget_ylabel.itemChanged.connect(self.__tree_select)
        self.comboBox_time.activated.connect(self.__combo_time_energy)
        self.comboBox_energy.activated.connect(self.__combo_time_energy)
        self.lineEdit_baseline.setValidator(self.onlyFloat)

        if 'main_reg' in self.config_dic and self.config_dic['main_reg'][0]:
            if self.config_dic['main_reg'][0][list(self.config_dic['main_reg'][0].keys())[0]] in self.regions:
                self.comboBox_MainRegion.setCurrentText(self.config_dic['main_reg'][0][list(self.config_dic['main_reg'][0].keys())[0]])

        if 'iter_call_region' in self.config_dic and self.config_dic['iter_call_region'] in self.regions:
            self.comboBox_IterationRegion.setCurrentText(self.config_dic['iter_call_region'])

        for i in self.ylabel_dic.keys():
            parent = QtWidgets.QTreeWidgetItem(self.treeWidget_ylabel)
            parent.setText(0, i)
            parent.setFlags(parent.flags() | QtCore.Qt.ItemFlag.ItemIsAutoTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            
            for x in self.ylabel_dic[i]:

                child = QtWidgets.QTreeWidgetItem(parent)
                child.setFlags(child.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                child.setText(0, x)
                if 'y_label' in self.config_dic and i in self.config_dic['y_label'] and x in [item for sublist in self.config_dic['y_label'][i] for item in sublist]:
                    child.setCheckState(0, QtCore.Qt.CheckState.Checked)
                else:
                    child.setCheckState(0, QtCore.Qt.CheckState.Unchecked)



        if 'file_name_args_tup' in self.config_dic:
            key_num = 0
            for i in range(self.parameters_count):
                self.lineEdit_parameters_list[i].setText(self.config_dic['file_name_args_tup'][i][1])
                role = self.config_dic['file_name_args_tup'][i][0]
                self.comboBox_parameters_list[i].setCurrentText(role)
                self.__parameters_combobox(self.comboBox_parameters_list[i])
                if role == 'xLabel':
                    if 'def_x_val' in self.config_dic:
                        self.comboBox_default_vals_list[i].setCurrentText(str(self.config_dic['def_x_val']))

                    if 'x_val_unit' in self.config_dic:
                        self.lineEdit_default_unit_list[i].setText(self.config_dic['x_val_unit'])
                    if 'x_val_multiplier' in self.config_dic:
                        multiplier_string = str(self.config_dic['x_val_multiplier'])
                        if "." in multiplier_string:
                            decimals = multiplier_string[::-1].find('.')
                        elif "e" in multiplier_string:
                            decimals = abs(int(multiplier_string.split("e")[-1]))
                        self.spinBox_default_multp_list[i].setDecimals(decimals)
                        self.spinBox_default_multp_list[i].setValue(self.config_dic['x_val_multiplier'])
                if role == 'funcLabel':
                    if 'def_label_val' in self.config_dic:
                        self.comboBox_default_vals_list[i].setCurrentText(str(self.config_dic['def_label_val']))
                    if 'func_label_unit' in self.config_dic:
                        self.lineEdit_default_unit_list[i].setText(self.config_dic['func_label_unit'])
                    if 'label_val_multiplier' in self.config_dic:
                        multiplier_string = str(self.config_dic['label_val_multiplier'])
                        if "." in multiplier_string:
                            decimals = multiplier_string[::-1].find('.')
                        elif "e" in multiplier_string:
                            decimals = abs(int(multiplier_string.split("e")[-1]))
                        self.spinBox_default_multp_list[i].setDecimals(decimals)
                        self.spinBox_default_multp_list[i].setValue(self.config_dic['label_val_multiplier'])
                if role == 'key':
                    if 'def_keys_vals' in self.config_dic and self.config_dic['def_keys_vals'][key_num]:
                        self.comboBox_default_vals_list[i].setCurrentText(str(self.config_dic['def_keys_vals'][key_num]))
                    if 'keys_units' in self.config_dic and self.config_dic['keys_units'][key_num]:
                        self.lineEdit_default_unit_list[i].setText(self.config_dic['keys_units'][key_num])
                    key_num += 1


        if 'time_energy_vars' in self.config_dic and self.config_dic['time_energy_vars']:
            self.checkBox_time_energy_vars.setCheckState(2)
            time_string = self.config_dic['time_energy_vars']['time'][0]+ " " +self.config_dic['time_energy_vars']['time'][1]
            if time_string in self.possible_time_vars:
                self.comboBox_time.setCurrentText(time_string)
                self.time_var = self.comboBox_time.currentText()
                self.__combo_time_energy()
            energy_string = self.config_dic['time_energy_vars']['energy'][0]+ " " +self.config_dic['time_energy_vars']['energy'][1]
            if energy_string in self.possible_energy_vars:
                self.comboBox_energy.setCurrentText(energy_string)
                self.energy_var = self.comboBox_energy.currentText()
                self.__combo_time_energy()



        if 'x_val_multiplier' in self.config_dic:
            xLabel_multiplier = self.config_dic['x_val_multiplier']
        else:
            self.config_dic['x_val_multiplier'] = float(0.0)

        if 'label_val_multiplier' in self.config_dic:
            funcLabel_multiplier = self.config_dic['label_val_multiplier']
        else:
            self.config_dic['label_val_multiplier'] = float(0.0)

        if 'y_label' in self.config_dic:
            y_label = self.config_dic['y_label']
        else:
            self.config_dic['def_x_val'] = float(0.0)

        if 'x_val_unit' in self.config_dic:
            xLabel_unit = self.config_dic['x_val_unit']
        else:
            self.config_dic['x_val_unit'] = float(0.0)

 

        if 'baseline' in self.config_dic and self.config_dic['baseline']:
            self.lineEdit_baseline.setText(str(self.config_dic['baseline']))

        self.__nested_region_check_changed()
        self.__update_nested_regions()

        if (self.isFake):
            self.comboBox_parameters_list[1].currentIndexChanged.connect(self._swap_axis)




        if runRadar:
            self.__save_and_run()

    def recursive_count(self, item):
        ### checks if some measurement from area "y label" was chosen
        count = 0
        if item.checkState(0) == QtCore.Qt.CheckState.Checked:
            count += 1
        for i in range(item.childCount()):
            count += self.recursive_count(item.child(i))
        return count
    

    def count_checked_items(self):
        ### checks if some measurement from area "y label" was chosen
        checked_count = self.recursive_count(self.treeWidget_ylabel.invisibleRootItem())
        return checked_count

    def check_selected_axes(self):
        ### checks if axes were correctly chosen
        sum = 0
        for i in range(0, len(self.comboBox_parameters_list)):
            if (self.comboBox_parameters_list[i].currentText() == "xLabel"):
                sum += 1
            if (self.comboBox_parameters_list[i].currentText() == "funcLabel"):
                sum +=1
        return sum

    def _swap_axis(self, index):
        ### prepina osy tak, aby osa s fake parametrem byla opacna vuci ose ladeneho parametru
        if (self.comboBox_parameters_list[1].currentText() == "xLabel"):
            ### pokud xlabel, fake funclabel
            self.comboBox_parameters_list[2].setCurrentText("funcLabel")
        if (self.comboBox_parameters_list[1].currentText() == "funcLabel"):
            ### pokud funclabel, fake xlabel
            self.comboBox_parameters_list[2].setCurrentText("xLabel")
        if (self.comboBox_parameters_list[1].currentText() == self.comboBox_parameters_list[2].currentText()):
            ### pokud jsou si rovny
            if (self.comboBox_parameters_list[1].currentText() == "xLabel"):
                self.comboBox_parameters_list[2].clear()
                self.comboBox_parameters_list[2].addItems(["funcLabel"])
                self.comboBox_parameters_list[2].setCurrentText("funcLabel")
            elif (self.comboBox_parameters_list[1].currentText() == "funcLabel"):
                self.comboBox_parameters_list[2].clear()
                self.comboBox_parameters_list[2].addItems(["xLabel"])
                self.comboBox_parameters_list[2].setCurrentText("xLabel")




    def __show_tree(self):
        if len(self.regions) > 1:

            self.tree_window = pydot_example.regionTree(pathToData=self.data_path, ownData=self.tree_data_selected,
                                                        addButtonIncluded = False)
            self.tree_window.show()
        else:
            self.__print_info_msg('Unable to show region tree because there is only one region available'
                                        ' in selected measurement.')

    def __filter(self):
        threshold = float(self.doubleSpinBox.text().replace(',', '.'))

        if self.nested_regs_selected_dic:
            for check_box in self.nested_regs_list:
                region = check_box.text()
                if region == self.comboBox_MainRegion.currentText():
                    continue
                act_region_time = self.reg_times[region]
                if check_box.isChecked() and act_region_time < threshold:
                    check_box.setCheckState(QtCore.Qt.CheckState.Unchecked)
        else:
            for check_box in self.nested_regs_list:
                region = check_box.text()
                if region == self.comboBox_MainRegion.currentText():
                    continue
                act_region_time = self.reg_times[region]
                if act_region_time >= threshold:
                    check_box.setCheckState(2)


    def __print_error_msg(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("USER INPUT ERROR")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.exec()

    def __print_success_msg(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Configure file saved")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.exec()

    def __print_info_msg(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Unable to show region tree.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.exec()

    def __next(self):
        self.tab_widget.setCurrentIndex(self.tab_widget.currentIndex() + 1)

    def __previous(self):
        self.tab_widget.setCurrentIndex(self.tab_widget.currentIndex() - 1)

    def __update_nested_regions(self):
        for check_box in self.nested_regs_list:
            check_box.setEnabled(True)
            if check_box.text() == self.comboBox_MainRegion.currentText():
                check_box.setEnabled(False)
                check_box.setCheckState(QtCore.Qt.CheckState.Unchecked)

    def __nested_region_check_changed(self):
        self.all_nested_regs_selected = True
        self.atleast_one_reg_selected = False
        for check_box in self.nested_regs_list:
            if check_box.text() == self.comboBox_MainRegion.currentText():
                check_box.setCheckState(0)
                continue
            if not check_box.isChecked():
                self.all_nested_regs_selected = False
                self.pushButton_Regions_All.setText('Select All')
                break


        if self.all_nested_regs_selected:
            self.pushButton_Regions_All.setText('Deselect All')

        for check_box in self.nested_regs_list:
            if check_box.isChecked() and check_box.text() not in self.nested_regs_selected_dic.keys():
                self.nested_regs_selected_dic[check_box.text()] = [check_box.text()]
            if not check_box.isChecked() and check_box.text() in self.nested_regs_selected_dic.keys():
                self.nested_regs_selected_dic.pop(check_box.text())
            self.tree_data_selected['all_nested_funcs_dic'] = self.nested_regs_selected_dic

    def __select_all_nested_regions(self):
        new_state = 2
        if self.all_nested_regs_selected:
            new_state = 0
        for check_box in self.nested_regs_list:
            if check_box.text() == self.comboBox_MainRegion.currentText():
                continue
            check_box.setCheckState(new_state)

    def __opt_time_eneregy(self):
        if self.checkBox_time_energy_vars.isChecked():
            self.frame_time_energy.setEnabled(True)
        else:
            self.frame_time_energy.setEnabled(False)

    def __combo_time_energy(self):
        if self.time_var and self.time_var not in self.possible_energy_vars:
            self.possible_energy_vars.append(self.time_var)
        if self.energy_var and self. energy_var not in self.possible_time_vars:
            self.possible_time_vars.append(self.energy_var)
        if self.comboBox_time.currentText():
            self.time_var = self.comboBox_time.currentText()
            if self.time_var in self.possible_energy_vars:
                self.possible_energy_vars.remove(self.time_var)
        if self.comboBox_energy.currentText():
            self.energy_var = self.comboBox_energy.currentText()
            if self.energy_var in self.possible_time_vars:
                self.possible_time_vars.remove(self.energy_var)
        act_energy_label = self.comboBox_energy.currentText()
        act_time_label = self.comboBox_time.currentText()
        self.comboBox_energy.clear()
        self.comboBox_time.clear()
        self.comboBox_time.addItems(self.possible_time_vars)
        self.comboBox_energy.addItems(self.possible_energy_vars)
        self.comboBox_energy.setCurrentIndex(self.comboBox_energy.findText(act_energy_label))
        self.comboBox_time.setCurrentIndex(self.comboBox_time.findText(act_time_label))

    def __tree_select(self, item, column):
        def refresh_items():
            act_time_label = self.comboBox_time.currentText()
            self.comboBox_time.clear()
            self.comboBox_time.addItems(self.possible_time_vars)
            self.comboBox_time.setCurrentIndex(self.comboBox_time.findText(act_time_label))

            act_energy_label = self.comboBox_energy.currentText()
            self.comboBox_energy.clear()
            self.comboBox_energy.addItems(self.possible_energy_vars)
            self.comboBox_energy.setCurrentIndex(self.comboBox_energy.findText(act_energy_label))

        if item.text(0) not in self.ylabel_dic.keys():
            new_item = item.parent().text(0) + ' ' + item.text(0)
            if item.checkState(column) == QtCore.Qt.CheckState.Checked:
                self.possible_time_vars.append(new_item)
                self.possible_energy_vars.append(new_item)
                self.selected_y_labels.append(item)
                refresh_items()
            elif item.checkState(column) == QtCore.Qt.CheckState.Unchecked:
                if item in self.selected_y_labels:
                    self.selected_y_labels.remove(item)
                if new_item in self.possible_time_vars:
                    self.possible_time_vars.remove(new_item)
                if new_item == self.time_var:
                    self.time_var = ''
                if new_item in self.possible_energy_vars:
                    self.possible_energy_vars.remove(new_item)
                if new_item == self.energy_var:
                    self.energy_var = ''
                refresh_items()

    def __parameters_combobox(self, current_combo_box):
        if current_combo_box.currentText() in ['xLabel', 'funcLabel']:
            if self.current_labels_dic[current_combo_box.currentText()] != current_combo_box:
                tmp_key = None
                if current_combo_box in self.current_labels_dic.values():
                    tmp_key = [k for k, v in self.current_labels_dic.items() if v == current_combo_box][0]
                    self.current_labels_dic[tmp_key] = None
                self.current_labels_dic[current_combo_box.currentText()] = current_combo_box
                for key, val in self.parameters_combobox_items_dic.items():
                    if key == current_combo_box:
                        continue
                    act_label = key.currentText()
                    if tmp_key is not None:
                        self.parameters_combobox_items_dic[key].append(tmp_key)
                    self.parameters_combobox_items_dic[key].remove(current_combo_box.currentText())
                    key.clear()
                    key.addItems(self.parameters_combobox_items_dic[key])
                    key.setCurrentIndex(key.findText(act_label))
        else:
            if current_combo_box in self.current_labels_dic.values():
                add_item = None
                for key, val in self.current_labels_dic.items():
                    if val == current_combo_box:
                        add_item = key
                        self.current_labels_dic[key] = None
                for key, val in self.parameters_combobox_items_dic.items():
                    if key == current_combo_box:
                        continue
                    act_label = key.currentText()
                    self.parameters_combobox_items_dic[key].append(add_item)
                    key.clear()
                    key.addItems(self.parameters_combobox_items_dic[key])
                    key.setCurrentIndex(key.findText(act_label))

        for i, item in enumerate(self.comboBox_parameters_list):
            has_default_value = False
            if item in self.current_labels_dic.values() or item.currentText() == 'key':
                has_default_value = True
            self.comboBox_default_vals_list[i].setEnabled(has_default_value)
            self.lineEdit_default_unit_list[i].setEnabled(has_default_value)
            if item.currentText() == 'key':
                has_default_value = False
            self.spinBox_default_multp_list[i].setEnabled(has_default_value)

    def __parameter_name_changed(self):
        self.possible_meric_parameters = ['']
        for e in self.lineEdit_parameters_list:
            self.possible_meric_parameters.append(e.text())

    def __save_and_run(self):
        chosenparameters = self.count_checked_items()
        correctaxes = self.check_selected_axes()
        if (chosenparameters > 0 and correctaxes == 2):
            if self.__generate():

                self.main_menu = main_menu_analyze.MainMenu(self.save_file_path, self.meric_config_path, self.tree_data_selected)


                if self.main_menu_instance:
                    self.main_menu_instance.close()
                self.main_menu_instance = self.main_menu
                self.tab_widget.close()
        elif (chosenparameters == 0):
            self.label_note.setText("Choose  at least 1 parameter first from \"y label\"!")
            # print("Choose at least 1 parameter first")
        elif (correctaxes < 2):
            self.label_note.setText("Choose funcLabel and xLabel!\nIf you have only 1 tuned parameter, choose axis only for this parameter.")
            
    def __generate(self):
        error_string = ''
        user_input_error = False
        if not self.current_labels_dic['xLabel']:
            error_string += '• xLabel is not specified. One of parameters must be xLabel.\n'
            #user_input_error = True

        if not self.current_labels_dic['funcLabel']:
            error_string += '• funcLabel is not specified. One of parameters must be funcLabel.\n'
            #user_input_error = True

        if len(self.selected_y_labels) == 0:
            error_string += '• yLabel is not specified. Atleast one yLabel must be checked.\n'
            #user_input_error = True

        parameters_name_unique = True
        for parameter in self.lineEdit_parameters_list:
            if not parameters_name_unique:
                user_input_error = True
                break
            parameter_name = parameter.text()
            for other_parameter in self.lineEdit_parameters_list:
                if parameter == other_parameter:
                    continue
                if parameter_name == other_parameter.text():
                    error_string += '• Parameter names must be unique. Check parameter names.\n'
                    parameters_name_unique = False
                    break

        if user_input_error:
            error_string += '\nPlease fix errors and try to generate config file again.'
            self.__print_error_msg(error_string)
            return False
        self.save_file_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))\
                              + '/.gui_tmp_config_{}.py'.format(os.getpid())


        if self.save_file_path:
            ### create shared dictionary
            self.__create_config_NEW(self.save_file_path)
            
            ### create temporary file
            # self.__create_config(self.save_file_path) #create temporary file
            return True
        else:
            return False

    def __generate_btn(self):
        if self.__generate():
            sys.exit()

    # def __create_config(self, save_file_path):

    #     config_file = open(save_file_path, "w")

    #     config_file.write("import collections\n")
    #     config_file.write("from collections import OrderedDict as ordDict\n\n")
    #     config_file.write("root_folder = [('"+self.data_path+"', None)]\n\n")
    #     config_file.write("main_reg = [{'" + self.comboBox_MainRegion.currentText() + "': '" + self.comboBox_MainRegion.currentText() + "'}]\n\n")

    #     act_parent = None
    #     one_y_label_key=True
    #     for i, item in enumerate(self.selected_y_labels):
    #         if i == 0:
    #             act_parent = item.parent().text(0)
    #         if 1!= 0 and act_parent != item.parent().text(0):
    #             one_y_label_key = False
    #             break

    #     if not one_y_label_key:
    #         act_parent = None
    #         for i, item in enumerate(self.selected_y_labels):
    #             unit = ''
    #             if item.text(0).find("[") != -1 and item.text(0).find("]") != -1:
    #                 unit = item.text(0)[item.text(0).find("[") + 1:item.text(0).find("]")]
    #             if act_parent != item.parent().text(0):
    #                 act_parent = item.parent().text(0)
    #                 if i == 0:
    #                     config_file.write("y_label = ordDict((('" + act_parent + "', [('" + item.text(0) + "', '" + unit + "')")
    #                 else:
    #                     config_file.write("]),\n('" + act_parent + "', [('" + item.text(0) + "', '" + unit + "')")
    #             else:
    #                 config_file.write(",\n ('" + item.text(0) + "', '" + unit + "')")
    #         config_file.write("])))\n\n")
    #     else:
    #         for i, item in enumerate(self.selected_y_labels):
    #             unit = ''
    #             if item.text(0).find("[") != -1 and item.text(0).find("]") != -1:
    #                 unit = item.text(0)[item.text(0).find("[") + 1:item.text(0).find("]")]
    #             if i == 0:
    #                 config_file.write("y_label = {'" + item.parent().text(0) + "': [('" + item.text(0) + "', '" + unit + "')")
    #             else:
    #                 config_file.write(",\n('" + item.text(0) + "', '" + unit + "')")
    #         config_file.write(']}\n\n')



    #     if self.checkBox_time_energy_vars.isChecked():
    #         for item in self.selected_y_labels:
    #             if self.comboBox_time.currentText() == item.parent().text(0) + ' ' + item.text(0):
    #                 config_file.write("time_energy_vars = {'time': ('" + item.parent().text(0) + "', '" + item.text(0) + "'),\n")
    #         for item in self.selected_y_labels:
    #             if self.comboBox_energy.currentText() == item.parent().text(0) + ' ' + item.text(0):
    #                 config_file.write("'energy': ('" + item.parent().text(0) + "', '" + item.text(0) + "')}")
    #     else:
    #         config_file.write("time_energy_vars = None")

    #     config_file.write("\n\nfile_name_args_tup = [")
    #     for i, item in enumerate(self.comboBox_parameters_list):
    #         if i == 0:
    #             config_file.write("\n['" + item.currentText() + "', '" + self.lineEdit_parameters_list[i].text() + "']")
    #         else:
    #             config_file.write(",\n['" + item.currentText() + "', '" + self.lineEdit_parameters_list[i].text() + "']")
    #     config_file.write("\n]\n\n")

    #     config_file.write("smooth_runs_average = True\n\n")

    #     config_file.write("def_keys_vals = [")
    #     first_item = True
    #     for i, item in enumerate(self.comboBox_parameters_list):
    #         if item.currentText() == 'key':
    #             if first_item:
    #                 config_file.write("'" + self.comboBox_default_vals_list[i].currentText() + "'")
    #                 first_item = False
    #             else:
    #                 config_file.write(", '" + self.comboBox_default_vals_list[i].currentText() + "'")
    #     config_file.write("]\n")

    #     config_file.write("keys_units = [")
    #     first_item = True
    #     for i, item in enumerate(self.comboBox_parameters_list):
    #         if item.currentText() == 'key':
    #             if first_item:
    #                 config_file.write("'" + self.lineEdit_default_unit_list[i].text() + "'")
    #                 first_item = False
    #             else:
    #                 config_file.write(", '" + self.lineEdit_default_unit_list[i].text() + "'")
    #     config_file.write("]\n\n")

    #     for i, item in enumerate(self.comboBox_parameters_list):
    #         if item.currentText() == 'xLabel':
    #             config_file.write("def_x_val = " + self.comboBox_default_vals_list[i].currentText() + "\n")
    #             config_file.write("x_val_unit = '" + self.lineEdit_default_unit_list[i].text() + "'\n")
    #             config_file.write("x_val_multiplier = " + str(self.spinBox_default_multp_list[i].value()) + "\n\n")
    #         if item.currentText() == 'funcLabel':
    #             config_file.write("def_label_val = " + self.comboBox_default_vals_list[i].currentText() + "\n")
    #             config_file.write("func_label_unit = '" + self.lineEdit_default_unit_list[i].text() + "'\n")
    #             config_file.write("label_val_multiplier = " + str(self.spinBox_default_multp_list[i].value()) + "\n\n")

    #     config_file.write("all_nested_regs = [")
    #     first_item = True
    #     for item in self.nested_regs_list:
    #         if item.isChecked():
    #             if first_item:
    #                 config_file.write("'" + item.text() + "'")
    #                 first_item = False
    #             else:
    #                 config_file.write(", '" + item.text() + "'")
    #     config_file.write("]\n\n")

    #     if self.comboBox_IterationRegion.currentText() == 'None':
    #         config_file.write("iter_call_region = None\n\n")
    #     else:
    #         config_file.write("iter_call_region = '" + self.comboBox_IterationRegion.currentText() + "'\n\n")

    #     config_file.write("detailed_info = True\n\n")

    #     config_file.write("optim_settings_file_path = None\n")
    #     config_file.write("generate_optim_settings_file = None\n\n")

    #     if self.lineEdit_baseline.text() and self.checkBox_time_energy_vars.isChecked():
    #         config_file.write("baseline = " + self.lineEdit_baseline.text() + "\n\n")
    #     else:
    #         config_file.write("baseline = None\n\n")

    #     config_file.write("test_csv_init = True")

    #     config_file.close()


    def __create_config_NEW(self, save_file_path):
        global config_data
        config_data = {}

        # Root folder and main region
        config_data['root_folder'] = [(self.data_path, None)]
        config_data['main_reg'] = [{self.comboBox_MainRegion.currentText(): self.comboBox_MainRegion.currentText()}]

        act_parent = None
        one_y_label_key = True
        y_label = OrderedDict()

        # Check y_label structure
        for i, item in enumerate(self.selected_y_labels):
            if i == 0:
                act_parent = item.parent().text(0)
            if act_parent != item.parent().text(0):
                one_y_label_key = False
                break

        if not one_y_label_key:
            act_parent = None
            for i, item in enumerate(self.selected_y_labels):
                unit = ''
                if "[" in item.text(0) and "]" in item.text(0):
                    unit = item.text(0).split("[")[1].split("]")[0]
                if act_parent != item.parent().text(0):
                    act_parent = item.parent().text(0)
                    y_label[act_parent] = [(item.text(0), unit)]
                else:
                    y_label[act_parent].append((item.text(0), unit))
        else:
            for i, item in enumerate(self.selected_y_labels):
                unit = ''
                if "[" in item.text(0) and "]" in item.text(0):
                    unit = item.text(0).split("[")[1].split("]")[0]
                if i == 0:
                    y_label[item.parent().text(0)] = [(item.text(0), unit)]
                else:
                    y_label[item.parent().text(0)].append((item.text(0), unit))

        config_data['y_label'] = y_label

        # Time and energy variables
        if self.checkBox_time_energy_vars.isChecked():
            time_energy_vars = {}
            for item in self.selected_y_labels:
                if self.comboBox_time.currentText() == item.parent().text(0) + ' ' + item.text(0):
                    time_energy_vars['time'] = (item.parent().text(0), item.text(0))
            for item in self.selected_y_labels:
                if self.comboBox_energy.currentText() == item.parent().text(0) + ' ' + item.text(0):
                    time_energy_vars['energy'] = (item.parent().text(0), item.text(0))
            config_data['time_energy_vars'] = time_energy_vars
        else:
            config_data['time_energy_vars'] = None

        # File name arguments
        file_name_args_tup = []
        for i, item in enumerate(self.comboBox_parameters_list):
            file_name_args_tup.append([item.currentText(), self.lineEdit_parameters_list[i].text()])
        config_data['file_name_args_tup'] = file_name_args_tup

        # Additional configurations
        config_data['smooth_runs_average'] = True

        # Default keys and values
        def_keys_vals = [self.comboBox_default_vals_list[i].currentText() for i, item in enumerate(self.comboBox_parameters_list) if item.currentText() == 'key']
        config_data['def_keys_vals'] = def_keys_vals

        # Key units
        keys_units = [self.lineEdit_default_unit_list[i].text() for i, item in enumerate(self.comboBox_parameters_list) if item.currentText() == 'key']
        config_data['keys_units'] = keys_units

        # X-label and function label values
        for i, item in enumerate(self.comboBox_parameters_list):
            if item.currentText() == 'xLabel':
                config_data['def_x_val'] = int(self.comboBox_default_vals_list[i].currentText())
                config_data['x_val_unit'] = self.lineEdit_default_unit_list[i].text()
                config_data['x_val_multiplier'] = self.spinBox_default_multp_list[i].value()
            if item.currentText() == 'funcLabel':
                config_data['def_label_val'] = int(self.comboBox_default_vals_list[i].currentText())
                config_data['func_label_unit'] = self.lineEdit_default_unit_list[i].text()
                config_data['label_val_multiplier'] = self.spinBox_default_multp_list[i].value()

        # Nested regions
        all_nested_regs = [item.text() for item in self.nested_regs_list if item.isChecked()]
        config_data['all_nested_regs'] = all_nested_regs

        # Iteration call region
        config_data['iter_call_region'] = None if self.comboBox_IterationRegion.currentText() == 'None' else self.comboBox_IterationRegion.currentText()

        config_data['detailed_info'] = True
        config_data['optim_settings_file_path'] = None
        config_data['generate_optim_settings_file'] = None

        # Baseline
        if self.lineEdit_baseline.text() and self.checkBox_time_energy_vars.isChecked():
            config_data['baseline'] = self.lineEdit_baseline.text()
        else:
            config_data['baseline'] = None

        config_data['test_csv_init'] = True



    def closeEvent(self, event):
#        print("close radargui")
        if self.main_menu_instance:
            self.main_menu_instance.show()

