# -*- coding: utf-8 -*-

import os
import glob
import csv
from src import main_menu_analyze
from src import design_csv_vals_edit
from runpy import run_path
from PyQt6 import QtCore, QtGui, QtWidgets
from src import radarGUI_analyze
from src import heatmap

class csv_vals_edit_window(QtWidgets.QDialog, design_csv_vals_edit.Ui_csv_vals_edit):
    def __init__(self, region, xLabel, xLabelVal, funcLabel, funcLabelVal, yLabel, keys, main_menu_instance):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.main_menu_instance = main_menu_instance
        self.all_csv_lines = []
        self.target_csv_path = ''

        self.tableWidget.setHorizontalHeaderLabels([yLabel[0] + " " + yLabel[1]])


        self.get_vals_from_csv_NEW(region, xLabel, xLabelVal, funcLabel, funcLabelVal, yLabel, keys)
        
        num_vals = 0
        for val_file in self.vals:
            num_vals += len(val_file)
        self.tableWidget.setRowCount(num_vals)

        row = -1
        for file in self.vals:
            for item in file:
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(item[1], 0))
                row += 1

        self.tableWidget.setSortingEnabled(True)
        self.pushButton_save.clicked.connect(self._save)

    def get_vals_from_csv_NEW(self, region, xLabel, xLabelVal, funcLabel, funcLabelVal, yLabel, keys):
        config_dic = radarGUI_analyze.config_data

        # Retrieve indices for xLabel and funcLabel from the config dictionary
        xLabelInd = [i for i, x in enumerate(config_dic['file_name_args_tup']) if xLabel in x]
        funcLabelInd = [i for i, x in enumerate(config_dic['file_name_args_tup']) if funcLabel in x]
        
        # Get multipliers from the config dictionary
        xLabel_multiplier = config_dic['x_val_multiplier']
        funcLabel_multiplier = config_dic['label_val_multiplier']

        # Construct the data path
        data_path = config_dic['root_folder'][0][0] + "/" + region
        csv_names = glob.glob(data_path + '/*.csv')
        if not csv_names:
            raise FileNotFoundError(f"No CSV files found in {data_path}")
        
        # Extract the first CSV file's name and use it as a template
        first_csv_path = csv_names[0]
        first_csv_name = first_csv_path.split('/')[-1].rsplit('.', 1)[0].split('_')
        
        # Modify the CSV name based on xLabel and funcLabel values
        target_csv_name = first_csv_name


        # If axes are in Hz 
        if True:
            if xLabelVal != "default":
                target_csv_name[xLabelInd[0]] = str(int(round(float(xLabelVal) * 1000000000)))#/ xLabel_multiplier)))
            else:
                target_csv_name[xLabelInd[0]] = str(int(round(float(0.0) * 1000000000)))#/ xLabel_multiplier)))
            
            if funcLabelVal != "default":
                target_csv_name[funcLabelInd[0]] = str(int(round(float(funcLabelVal) * 1000000000)))#/ funcLabel_multiplier)))
            else:
                target_csv_name[funcLabelInd[0]] = str(int(round(float(0.0) * 1000000000)))#/ funcLabel_multiplier)))
        else:
        # if axes are in GHz TODO
            if xLabelVal != "default":
                target_csv_name[xLabelInd[0]] = str(int(round(float(xLabelVal))))#/ xLabel_multiplier)))
            else:
                target_csv_name[xLabelInd[0]] = str(int(round(float(0.0))))#/ xLabel_multiplier)))
            
            if funcLabelVal != "default":
                target_csv_name[funcLabelInd[0]] = str(int(round(float(funcLabelVal))))#/ funcLabel_multiplier)))
            else:
                target_csv_name[funcLabelInd[0]] = str(int(round(float(0.0))))#/ funcLabel_multiplier)))

        # Handle additional keys if provided
        if keys:
            keyInd = [i for i, x in enumerate(config_dic['file_name_args_tup']) if 'key' in x]
            keyVal = [key.split(';')[0] for key in keys]
            for i, index in enumerate(keyInd):
                if keyVal[i] != '':
                    target_csv_name[index] = keyVal[i]

            # Fill in wildcard values for other parameters
            for i in range(len(target_csv_name)):
                if i not in keyInd and i != funcLabelInd[0] and i != xLabelInd[0]:
                    target_csv_name[i] = '*'
        else:
            # If no keys, fill wildcard values for parameters other than xLabel and funcLabel
            for i in range(len(target_csv_name)):
                if i != funcLabelInd[0] and i != xLabelInd[0]:
                    target_csv_name[i] = '*'

        target_csv_name = '_'.join(target_csv_name) + ".csv"
        self.target_csv_path = glob.glob(data_path + '/' + target_csv_name)
        if not self.target_csv_path:
            raise FileNotFoundError(f"Target CSV {target_csv_name} not found in {data_path}")

        self.vals_ind = []
        self.vals = []
        self.all_csv_lines = []

        # Loop through the matching CSV files and read their contents
        for j, csv_name in enumerate(self.target_csv_path):
            vals_ind = []
            vals = []
            with open(csv_name) as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                yLabel_category = False
                self.all_csv_lines.append([])

                # Read each line in the CSV and process it
                for i, line in enumerate(reader):
                    self.all_csv_lines[j].append(line)
                    
                    if line[0].startswith('#') and not line[0].startswith("# CALLTREE"):
                        line_tmp = line[0].split('#')[1].strip()
                        if line_tmp == yLabel[0]:
                            yLabel_category = True
                        else:
                            yLabel_category = False
                    
                    # Find the line with the specific yLabel value
                    if line[0] == yLabel[1] and yLabel_category:
                        vals_ind.append(i)

                csvfile.seek(0)
                all_vals_lst = list(enumerate(reader))

                # Append the matching values to the list
                for i in vals_ind:
                    vals.append(all_vals_lst[i][1])
            
            self.vals.append(vals)
            self.vals_ind.append(vals_ind)
        


    def __print_success_msg(self, text, title):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.addButton(QtWidgets.QPushButton("Restart later"), QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        msg.addButton(QtWidgets.QPushButton("Restart now"), QtWidgets.QMessageBox.ButtonRole.YesRole)
        result = msg.exec()
        if result == 1:
            self.close()
            self.main_menu_instance.restart()


    def _save(self):
        table_index = 0
        for j, csv_name in enumerate(self.target_csv_path):
            with open(csv_name, 'w') as csvfile:
                writer = csv.writer(csvfile)
                for line, row in enumerate(self.all_csv_lines[j]):
                    if line in self.vals_ind[j]:
                        new_item = self.tableWidget.item(table_index, 0).text()
                        new_row = row
                        new_row[1] = new_item
                        table_index += 1
                        writer.writerow(new_row)
                    else:
                        writer.writerow(row)

        self.__print_success_msg('Changes saved to CSV files. To get updated results you must restart RADAR Analysis.','Saved to CSV')
