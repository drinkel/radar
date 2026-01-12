#!/usr/bin/env python3
import sys
import colorsys
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtGui import QFontMetrics
import textwrap
from PyQt6.QtWidgets import QApplication, QWidget, QFormLayout, QGroupBox, QSizePolicy, QVBoxLayout, QHBoxLayout
import random
import copy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from pathlib import Path
import json
import matplotlib.pyplot as plt
from scipy import signal
from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pylab as pl
import copy as cp
from runpy import run_path
import numpy as np
import pprint
import os
import glob
import re
import textwrap
from shutil import copyfile
import warnings
import matplotlib.cbook
from datetime import datetime
import matplotlib

#### this application plots sample graphs
#### sampeles_plot.py works almost the same as in the old radar, it plots the same and behaves the same
#### the main difference is that it now loads a .json file from which it takes the DataFormat 
#### and the list of files is passed from data_load
#### another difference is that it works with the runtime of individual calls, individual functions are described below
#### otherwise this application again works independently, it loads samples from a file of files
#### added the option to display data stored in the default file, default.csv or log.csv, 
#### just select default/log in one combobox and the file default/log.csv will be displayed



# warnings.filterwarnings('ignore', category=matplotlib.cbook.mplDeprecation)
warnings.filterwarnings('ignore', category=matplotlib.MatplotlibDeprecationWarning)

pp = pprint.PrettyPrinter(indent=4)


def metric(x, y, c1, c2):
    return c1 * (x[0] - y[0]) ** 2 + c2 * (x[1] - y[1]) ** 2


def similarity(x, y): 
    return metric(x, y, 0.001, 0.85)


class Window(QtWidgets.QDialog):
    sendInfo = QtCore.pyqtSignal(object)
    

    def __init__(self, ownData=None, parent=None, main_menu_instance=None):
        super(Window, self).__init__(parent)
       
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        
        
        # a figure instance to plot on
        self.figure = Figure()
        self.figure.set_tight_layout(True)
        self.ax = self.figure.add_subplot(111)

        self.legend_x = 0.5
        self.legend_y = -0.15
        
        self.sw = False
        self.use_logscaleX = False
        self.use_logscaleY = False
        self.samples_data = []
        self.samples_time = []
        self.samples_data_null = []
        self.plot_data_samples = []
        self.number = []
        self.samples_data_lables = []
        self.max_data_len = 0
        self.samples_ylabel = "Power [W]"
        self.samples_xlabel = ""
        self.min_sample_val = float(sys.maxsize)
        self.max_sample_val = float(0)
        self.min_time_val = float(1000)
        self.max_time_val = float(0)
        self.setWindowTitle("Plot power samples")

        self.main_menu_instance = main_menu_instance
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, parent=self)

        self.checkbox_sw = QtWidgets.QCheckBox('Switch axes')
        self.checkbox_sw.clicked.connect(self.change_sw)
        self.maxBox = QtWidgets.QCheckBox('Show maximum')
        self.maxBox.clicked.connect(self.plot)
        self.logscaleX = QtWidgets.QCheckBox('log scale for axis X')
        self.logscaleX.clicked.connect(self.change_logscaleX)
        self.logscaleY = QtWidgets.QCheckBox('log scale for axis y')
        self.logscaleY.clicked.connect(self.change_logscaleY)

        self.typeButton = QtWidgets.QPushButton('Scatter plot')
        self.plotType = 0
        #self.typeButton.setFixedWidth(50)
        self.typeButton.clicked.connect(self.changeType)

        self.typeButton_id_time = QtWidgets.QPushButton('ID of samples')
        self.plotType_id_time = 0
        self.typeButton_id_time.clicked.connect(self.changeType_id_time)

        self.addButton = QtWidgets.QPushButton('Add to plot')
        self.addButton.clicked.connect(self.addToPlot)
        self.clearButton = QtWidgets.QPushButton('Clear plot')
        self.clearButton.clicked.connect(self.clearCanvas)
        
        self.sortButton = QtWidgets.QPushButton('Sort data')
        self.sortButton.clicked.connect(self.sortData)
        self.sortButtonValue = False
        
        self.smoothWindowSizeLabel = QtWidgets.QLabel("Window size:")
        self.smoothWindowSizeLabel.setFixedWidth(100)
        self.smoothWindowSizeSpinBox = QtWidgets.QSpinBox()
        self.smoothWindowSizeSpinBox.setValue(11)
        self.smoothWindowSizeSpinBox.setMinimum(3)
        self.smoothWindowSizeSpinBox.setSingleStep(2)
        self.smoothWindowSizeSpinBox.setMaximum(2147483647)  # TMP
        self.smoothpolyOrderLabel = QtWidgets.QLabel("Polynomial order:")
        self.smoothpolyOrderLabel.setFixedWidth(130)
        self.smoothpolyOrderSpinBox = QtWidgets.QSpinBox()
        self.smoothpolyOrderSpinBox.setMinimum(1)
        self.smoothpolyOrderSpinBox.setValue(3)
        self.smoothpolyOrderSpinBox.setMaximum(2147483647)
        self.smoothButton = QtWidgets.QPushButton('Smooth samples')
        self.smoothButton.clicked.connect(self.smoothSamples)
        self.smoothChartSizeLabel = QtWidgets.QLabel("Chart size:")
        self.smoothChartSizeLabel.setFixedWidth(80)
        
        self.static_dict = {} ### dictionary with static files

        self.combo_parameters = []
        self.id_min = 0
        self.id_max = 10
        self.static_ids = []
        self.bf = QtGui.QFont("Arial", 13, QtGui.QFont.Weight.Bold)
        self.mult = QtWidgets.QLineEdit("1")
        self.mult.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.mult.setValidator(QtGui.QDoubleValidator())
        self.colors = [(0, 0, 1.0),(1.0, 0, 0),(0, 1.0, 0),(1.0, 1.0, 0),(0, 1.0, 1.0),(1.0, 0, 1.0)]
        
        # data loading, we can have more than one y_data! TODO
        self.d = ownData
        self.data_csv = self.d["_csv_"]
        self.data = self.d["plot_summary_data"]
        self.combo_reg = QtWidgets.QComboBox(self)
        # self.root_folder = self.d['root_folder']
        list = self.d["root_folder"]
        for i in list:
            self.root_folder = i
        regions = []
        #change list of regions to receive only the regions that belongs to the same execution id
        for region in os.listdir(self.root_folder):
            if os.path.isdir(self.root_folder + "/" + region):
                if glob.glob(glob.escape(self.root_folder) + '/' + glob.escape(region) + '/*.csv'):
                    regions.append(region)
        regions = sorted(regions, key=lambda s: s.lower())
        self.allregions = []
        for region in regions:
            self.combo_reg.addItem(region)
            self.allregions.append(region)
        measurement_info_path = Path(self.root_folder + '/measurementInfo.json')
        if measurement_info_path.exists():
            with open(measurement_info_path) as f:
                try:
                    measurement_info_file_data = json.load(f)
                    self.measurement_params = measurement_info_file_data['DataFormat'].split("_")
                except json.decoder.JSONDecodeError:
                    self.__print_error_msg('measurementInfo.json file is not in valid format')
        param_names = self.measurement_params
        for i in regions:
            if i.endswith("_static"):
                static_name = i
                self.static_name = i
                continue
        
        # read parameters from csv names and their possible values
        csv_names = glob.glob(glob.escape(self.root_folder) + '/' + glob.escape(regions[0]) + '/*.csv')
        first_static_path = glob.glob(glob.escape(self.root_folder) + '/' + glob.escape(static_name) + '/*.csv')
        self.csv_for_if = csv_names
        first_csv_path = first_static_path[0]
        
        for i in Path((self.root_folder) + '/' + (static_name) + '/samples/').iterdir():
            exec2 = i.name.split("_")
            exec = exec2[1].split(".")
            if (exec[0] not in self.static_ids):
                self.static_ids.append(exec[0])
        for i in first_static_path:
                if "log" in i or "default" in i:
                    a = True
                elif i.endswith("_static"):
                    first_csv_path = i
                    continue

        first_csv_name = first_csv_path.split('/')[-1]
        self.parameters_count = first_csv_name.count('_') + 1
        calculus = len(first_csv_name.split("_"))
        self.parameter_values_dic = {}
        for i in range(self.parameters_count):
            self.parameter_values_dic[i] = []
        for n, item in enumerate(csv_names):
            item = item.split('/')[-1]
            
            item = os.path.splitext(item)[0]
            item = item.split('_')

            if item[0] == "log" or item[0] == "default" :
                
                for i in range(calculus):
                    self.parameter_values_dic[i].append(item[0])
            else:
                
                for i in range(self.parameters_count):
                    if not item[i] in self.parameter_values_dic[i]:
                        self.parameter_values_dic[i].append(item[i])
        
        # create combo box for each parameter
        self.combo_param_list = []
        for k, v in self.parameter_values_dic.items():
            self.combo_param_list.append(v)
        self.node_list = QtWidgets.QComboBox(self)
        node_names = self.parameter_values_dic[0]
        self.node_list.addItems(node_names)

        # create labels for region and each parameter combo box
        self.label_sensor = QtWidgets.QLabel('Power Sensor')
        self.label_reg = QtWidgets.QLabel('Region')
        self.labels_param_list = []
        
        parameter = self.d['file_name_args']
        
        para = self.d['file_name_args']
        ###### NODES
        self.labels_param_list.append(QtWidgets.QLabel(param_names[0]))

        # gather power sensors names from first csv
        possible_samples_names = []

        csv_file = open(first_csv_path, "r")
        for line in csv_file:
            if line.startswith("#") and "SAMPLES" in line: #or "samples" in line:
                if line.replace('#', '').strip("\n").lstrip(' ') not in possible_samples_names:
                    possible_samples_id_name = line.split(" - ")[-1].split(":")[0].strip("\n")
                    possible_samples_names.append(possible_samples_id_name)

        self.combo_sample = QtWidgets.QComboBox(self)
        self.multiple_samples = False
        self.legende_paramentr = []
        if len(possible_samples_names) > 1:
            self.multiple_samples = True
        
        for sample_name in possible_samples_names:
            self.combo_sample.addItem(sample_name)
            self.legende_paramentr.append(sample_name)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        self.plot_data = self.data[0]
        for label in self.labels_param_list:
            label.setFixedHeight(30)

        hl_reg = QtWidgets.QHBoxLayout()
        vl_sensor = QtWidgets.QVBoxLayout()
        vl_sensor.addWidget(self.label_sensor)
        vl_sensor.addWidget(self.combo_sample)
        hl_reg.addLayout(vl_sensor)
        vl_reg = QtWidgets.QVBoxLayout()
        vl_reg.addWidget(self.label_reg)
        vl_reg.addWidget(self.combo_reg)
        hl_reg.addLayout(vl_reg)


        vl_id = QtWidgets.QVBoxLayout()
        self.label_id = QtWidgets.QLabel('Execution ID')
        vl_id.addWidget(self.label_id)
        self.execution_id = QtWidgets.QComboBox()




        vl_param = QtWidgets.QVBoxLayout()
        vl_param.addWidget(self.labels_param_list[0])
        vl_param.addWidget(self.node_list)
        hl_reg.addLayout(vl_param)




        self.actual_id = self.execution_id.currentText()
        self.execution_id.currentTextChanged.connect(self.change_execution_id)
        vl_id.addWidget(self.execution_id)

        self.dictionary = {}
        self.exlist = []
        self.node_list_ = []
        

        ### test

        self.load_alldata()
        self.combo_reg.addItems(self.dictionary)
        self.combo_reg.currentTextChanged.connect(self.updatebox2)
        self.node_list.currentTextChanged.connect(self.updatebox3)
        self.execution_id.currentTextChanged.connect(self.updatebox3_background)
        self.updatebox2(self.combo_reg.currentText())

        #else:
        #    self.node_list.setStyleSheet('''QComboBox {color:white}''')

        #self.load_exids_init()
        #self.execution_id.clear()
        #self.execution_id.addItems(self.exids)
        #self.combo_reg.currentIndexChanged.connect(self.load_exids_regionchange)
        #self.combo_reg.currentIndexChanged.connect(lambda: self.execution_id.clear())
        #self.combo_reg.currentIndexChanged.connect(lambda: self.execution_id.addItems(self.exids))
        #self.combo_reg.currentIndexChanged.connect(lambda: self.node_list.clear())
        #self.combo_reg.currentIndexChanged.connect(lambda: self.node_list.addItems(self.node_list_))
        #self.execution_id.currentIndexChanged.connect(self.load_exids_exidchange)
        
        ####
        
        


        hl_reg.addLayout(vl_id)
        layout.addLayout(hl_reg)
        
        self.cluster_btn = QtWidgets.QPushButton('Cluster analysis')
        self.cluster_btn.clicked.connect(self.clustering)
        hlayout2 = QtWidgets.QHBoxLayout()
        self.cluster_btn.setFixedWidth(130)
        self.addButton.setFixedWidth(130)
        hlayout2.addWidget(self.addButton)
        hlayout2.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addLayout(hlayout2)
        
        hlayout3 = QtWidgets.QHBoxLayout()
        hlayout3.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.smoothButton.setFixedWidth(130)
        hlayout3.addWidget(self.smoothpolyOrderLabel)
        hlayout3.addWidget(self.smoothpolyOrderSpinBox)
        self.smoothpolyOrderSpinBox.editingFinished.connect(self.spinBoxCheck)
        hlayout3.addWidget(self.smoothWindowSizeLabel)
        hlayout3.addWidget(self.smoothWindowSizeSpinBox)
        self.smoothWindowSizeSpinBox.editingFinished.connect(self.spinBoxCheck)
        hlayout3.addWidget(self.smoothButton)
        layout.addLayout(hlayout3)
        
        # adding chart resizable
        hlayout5 = QtWidgets.QHBoxLayout()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setFixedWidth(500)
        self.slider.setMinimum(500)
        self.slider.setMaximum(800)
        self.slider.setSingleStep(5)
        hlayout5.addWidget(self.smoothChartSizeLabel)
        hlayout5.addWidget(self.slider)
        self.slider.setValue(600) 
        hlayout5.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(hlayout5)

        hlayout4 = QtWidgets.QHBoxLayout()
        self.clearButton.setFixedWidth(130)
        self.sortButton.setFixedWidth(130)
        hlayout4.addWidget(self.sortButton)
        hlayout4.addWidget(self.clearButton)
        hlayout4.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addLayout(hlayout4)
        layout.addWidget(self.toolbar)
                
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.canvas_widget = QtWidgets.QWidget()
        canvas_layout = QHBoxLayout()
        canvas_layout.addWidget(self.canvas)
        self.canvas_widget.setLayout(canvas_layout)
        self.canvas_widget.setFixedHeight(600)
        
        self.canvas_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.update_height(600)
        self.slider.valueChanged.connect(self.update_height)
        self.scroll_area.setWidget(self.canvas_widget)

        layout.addWidget(self.scroll_area)

        labelDotsize = QtWidgets.QLabel("Dot size: ")
        labelDotsize.setFixedWidth(60)
        self.dotSizeSpinBox = QtWidgets.QSpinBox()
        self.dotSizeSpinBox.setFixedWidth(100)
        self.dotSizeSpinBox.setMinimum(1)
        self.dotSizeSpinBox.setMaximum(2147483647)
        self.dotSizeSpinBox.valueChanged.connect(self.dotSizeChanged)
        self.dotSizeSpinBox.setEnabled(False)

        self.valsize = 11
        labelFontsize = QtWidgets.QLabel("Font size: ")
        labelFontsize.setFixedWidth(60)
        self.fontSize = QtWidgets.QSpinBox()
        self.fontSize.setFixedWidth(100)
        self.fontSize.setValue(self.valsize)
        self.fontSize.setMinimum(6)
        self.fontSize.setSingleStep(1)
        self.fontSize.setMaximum(50)
        self.fontSize.valueChanged.connect(self.fontSizeChanged)
        self.fontSize.setEnabled(False)
        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self.logscaleX)
        hlayout.addWidget(self.logscaleY)
        hlayout.addWidget(labelFontsize)
        hlayout.addWidget(self.fontSize)
        hlayout.addWidget(labelDotsize)
        hlayout.addWidget(self.dotSizeSpinBox)
        hlayout.addWidget(self.typeButton)
        hlayout.addWidget(self.typeButton_id_time)
        layout.addLayout(hlayout)



        self.setLayout(layout)
        self.typeButton_id_time.setEnabled(True)

        self.setMinimumSize(800,500)
        self.resize(900, 900)
        self.figure.tight_layout()
        self.resizeEvent = self.onResize
        self.canvas_widget.installEventFilter(self)
        self.canvas.draw()

    def updatebox2(self, selected):
        self.node_list.clear()
        if selected in self.dict:
            self.node_list.addItem("Choose value")
            self.node_list.addItems(self.dict[selected].keys())
            self.node_list.setStyleSheet('''QComboBox {color:red}''')
        self.updatebox3(self.node_list.currentText())


    def updatebox3(self, selected):
        self.execution_id.clear()
        category = self.combo_reg.currentText()
        if category in self.dict and selected in self.dict[category]:
            self.execution_id.addItem("Choose value")
            self.execution_id.addItems(self.dict[category][selected])
            self.node_list.setStyleSheet('''QComboBox {color:black}''')
            self.execution_id.setStyleSheet('''QComboBox {color:red}''')

    def updatebox3_background(self):
        if self.execution_id.currentText != "Choose value":
            self.execution_id.setStyleSheet('''QComboBox {color:black}''')
        else:
            self.execution_id.setStyleSheet('''QComboBox {color:red}''')

    def update_height(self, value):
        if hasattr(self, 'lgd'):
            self.legend()
        else:
            self.canvas_widget.setFixedHeight(value)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def onResize(self, event):
        self.canvas_widget.setMinimumWidth(self.scroll_area.width()-5)
        if hasattr(self, 'lgd'):
            self.legend()
        self.figure.tight_layout()
        
        self.canvas.draw()
        
    def sortData(self):
        self.sortButtonValue = True
        labels_sorted = []
        colors_sorted = []
        
        for coords in sorted(self.samples_data, key=lambda x: x[0][0]):
            indice_conjunto = self.samples_data.index(coords)
            labels_sorted.append(self.samples_data_lables[indice_conjunto])
            colors_sorted.append(self.colors[indice_conjunto])
        
        self.samples_data_lables = labels_sorted
        self.samples_data = sorted(self.samples_data, key=lambda x: x[0][0])
        
        for i in range(0,len(colors_sorted)):
            self.colors[i] = colors_sorted[i]
        
        self.plot()
        
    def spinBoxCheck(self):
        if self.samples_data:
            if self.smoothWindowSizeSpinBox.value() % 2 == 0:
                QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, 'Invalid input', 'Window size must be odd number.',
                                      QtWidgets.QMessageBox.StandardButton.Ok).exec()
                self.smoothWindowSizeSpinBox.setValue(self.smoothWindowSizeSpinBox.value() - 1)
                return 1
            if self.max_data_len < self.smoothWindowSizeSpinBox.value():
                QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, 'Invalid input',
                                      'Maximum window length is number of '
                                      'samples.',
                                      QtWidgets.QMessageBox.StandardButton.Ok).exec()
                self.smoothWindowSizeSpinBox.setValue(self.max_data_len)
                return 1
        if self.smoothWindowSizeSpinBox.value() <= self.smoothpolyOrderSpinBox.value():
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, 'Invalid input', 'Polynomial order must be less than '
                                                                                  'window length.',
                                  QtWidgets.QMessageBox.StandardButton.Ok).exec()
            self.smoothpolyOrderSpinBox.setValue(self.smoothWindowSizeSpinBox.value() - 1)
            return 1

        return 0

    def fontSizeChanged(self):
        if self.samples_data:
            self.plot()

    def dotSizeChanged(self):
        if self.samples_data:
            self.plot()
    # Change from line plot to scatter plot
    def changeType(self):
        if self.samples_data:
            self.plotType = not self.plotType
            if self.plotType:
                self.typeButton.setText('Line plot')
                self.dotSizeSpinBox.setEnabled(True)
            else:
                self.typeButton.setText('Scatter plot')
                self.dotSizeSpinBox.setEnabled(False)
            self.plot()
    # change of values on the x-axis where id and time change
    def changeType_id_time(self):
        self.plot_data_samples = self.samples_data
        if self.samples_data:
            self.plotType_id_time = not self.plotType_id_time
            if self.plotType_id_time:
                self.typeButton_id_time.setText('ID of samples')
                self.samples_data = self.samples_data
                self.samples_xlabel = ""
                self.samples_xlabel = "Time [s]"

            else:
                self.typeButton_id_time.setText('Time')
                # samples and time with np.null
                self.samples_data = self.samples_time
                self.samples_xlabel = ""
                self.samples_xlabel = "ID of samples"

            self.plot()
        self.samples_data = self.plot_data_samples
    # clearing data from the graph
    
    def change_execution_id(self, text):
        self.actual_id = text
    

    def load_exids_exidchange(self):
        region = str(self.combo_reg.currentText())
        curr_id = str(self.execution_id.currentText())
        if (curr_id in self.dictionary[region]):
            self.node_list_.clear()
            self.node_list_ = list(self.dictionary[region][curr_id])
            self.node_list.clear()
            self.node_list.addItems(self.node_list_)
        else:
            print("neni tu", self.node_list_)


    def load_exids_regionchange(self):
        ### function that is called when region is changed
        ### first check if this region already has been loaded (exids, nodes)
        ### if not, load it from csv, if yes, just load data from dictionary
        region = str(self.combo_reg.currentText())
        path = str(self.root_folder) + '/' + region
        files = [f for f in os.listdir(path)]
        curr_id = str(self.execution_id.currentText())
        nodes = []
        self.exids.clear()
        self.node_list_.clear()
        if (len(self.dictionary[region]) == 0):
            for i in range(0, len(files)):
                node = files[i].split('_')
                node = node[0]
                if (files[i] != "samples"):
                    _path = path + '/' + str(files[i])
                    with open(_path, "r") as file:
                        exec_read = []
                        for line in file:
                            ### save node
                            node = files[i].split('_')
                            node = node[0] 
                            exec_read.append(line)
                            for id in range(0, len(self.static_ids)):
                                execute_id = ";init_" + str(self.static_ids[id]) + ';'
                                execute_id2 = ";init_" + str(self.static_ids[id]) + '\n'
                                for line in exec_read:
                                    if (execute_id in line or execute_id2 in line):
                                        if (self.static_ids[id] not in self.dictionary[region]):
                                            self.dictionary[region][self.static_ids[id]] = []
                                            self.exids.append(self.static_ids[id])
                                            if (node not in self.dictionary[region][self.static_ids[id]]):
                                                self.dictionary[region][self.static_ids[id]].append(node)
                                                if (node not in self.node_list_):
                                                    self.node_list_.append(node)
                                        else:
                                            if (node not in self.dictionary[region][self.static_ids[id]]):
                                                    self.dictionary[region][self.static_ids[id]].append(node)
                                                    if (node not in self.node_list_):
                                                        self.node_list_.append(node)
        else:
            if (curr_id in self.dictionary[region]):
                self.exids = list(self.dictionary[region].keys())
                self.node_list_ = list(self.dictionary[region][self.exids[0]])
            else:
                self.execution_id.clear()
                self.exids = list(self.dictionary[region].keys())
                self.node_list_ = list(self.dictionary[region][self.exids[0]])

    
    def load_exids_init(self):
        ### dictionary [region][exec id][node]
        for region in range(0, len(self.allregions)):
            self.dictionary[self.allregions[region]] = {}
        self.exids = []
        self.node_list_.clear()
        region = str(self.combo_reg.currentText())
        path = str(self.root_folder) + '/' + region#self.allregions[region]
        files = [f for f in os.listdir(path)]

        ### first init - find and save all exec ids for actually chosen region
        for i in range(0, len(files)):
            ### save node
            node = files[i].split('_')
            node = node[0]
            if (files[i] != "samples"):
                _path = path + '/' + files[i]
                with open(_path, "r") as file:
                    exec_read = []
                    for line in file:
                        exec_read.append(line)
                        for id in range(0, len(self.static_ids)):
                            execute_id = "CALLTREE;init_" + str(self.static_ids[id]) + ';'
                            execute_id2 = "CALLTREE;init_" + str(self.static_ids[id]) + '\n'
                            for line in exec_read:
                                if (execute_id in line or execute_id2 in line):
                                    if (self.static_ids[id] not in self.dictionary[region]):
                                        self.dictionary[region][self.static_ids[id]] = []
                                        self.exids.append(str(self.static_ids[id]))
                                        if (node not in self.dictionary[region][self.static_ids[id]]):
                                            self.dictionary[region][self.static_ids[id]].append(node)
                                            if (node not in self.node_list_):
                                                self.node_list_.append(node)
                                        break
                                    else:
                                        if (node not in self.dictionary[region][self.static_ids[id]]):
                                            self.dictionary[region][self.static_ids[id]].append(node)
                                            if (node not in self.node_list_):
                                                self.node_list_.append(node)

    def load_alldata(self):
        """ Initialize self.dict[region][node] = [execution_id1, execution_id2, ...] """
        self.dict = {}  # Reset dictionary

        for region in self.allregions:
            self.dict[region] = {}  # Initialize empty dictionary for each region
        self.exids = []

        for region in self.allregions:

            #region = str(self.combo_reg.currentText())  # Get currently selected region
            path = os.path.join(self.root_folder, region)  # Path to the region directory
            files = [f for f in os.listdir(path) if f != "samples"]  # Exclude 'samples' folder

            # Scan files to extract execution IDs and nodes
            for filename in files:
                node = filename.split('_')[0]  # Extract node name from filename
                file_path = os.path.join(path, filename)

                with open(file_path, "r") as file:
                    for line in file:
                        for exec_id in self.static_ids:  # Check for all execution IDs
                            if f"init_{exec_id};" in line or f"init_{exec_id}\n" in line:
                                # If the node doesn't exist in the dictionary, initialize it
                                if node not in self.dict[region]:
                                    self.dict[region][node] = []

                                # Append execution ID if not already in the list
                                if exec_id not in self.dict[region][node]:
                                    self.dict[region][node].append(exec_id)

        # print("Updated Dictionary Structure:", self.dict)  # Debugging output

    def clearCanvas(self):
        self.samples_data = []
        self.samples_time = []
        self.samples_data_null = []
        self.samples_data_lables = []
        self.max_data_len = 0
        self.min_sample_val = float(99999999999999)
        self.max_sample_val = float(0)
        self.combo_parameters = []
        
        self.ax.clear()
        self.canvas_widget.setFixedHeight(int(self.slider.value()))
        self.legend_height = 0
        self.legend_width = 0
        self.sortButtonValue = False
        self.canvas_widget.setMinimumWidth(self.scroll_area.width()-5)
        self.colors = [(0, 0, 1.0),(1.0, 0, 0),(0, 1.0, 0),(1.0, 1.0, 0),(0, 1.0, 1.0),(1.0, 0, 1.0)]
        self.fontSize.setEnabled(False)

        self.figure.tight_layout()

        self.canvas.draw()

    # pridani dat do grafu
    def addToPlot(self):
        self.fontSize.setEnabled(True)
        self.number = []
        csv_name_string = ''

        self.checkExId()

        csv_name_string2 = self.fileToOpen
        csv_name_string = csv_name_string[:-1]

        current_id = []
        current_id = self.combo_sample.currentText() + ' ' + self.combo_reg.currentText() + ' ' + self.node_list.currentText() + ' ' + self.execution_id.currentText()
        if current_id not in self.combo_parameters:
            if "default" in csv_name_string:
                csv_name_string = "default"
            if "log" in csv_name_string:
                csv_name_string = "log"
            #path to csv: folder / region (static) / csvfile
            
            csv_path = self.root_folder + '/' + self.combo_reg.currentText() + '/' + csv_name_string + '.csv'
            self.csv_path2 = self.root_folder + '/' + self.combo_reg.currentText() + '/' + csv_name_string2 #+ '.csv'
            if self.multiple_samples:
                self.samples_data_lables.append(self.combo_sample.currentText() + ' ' + self.combo_reg.currentText() + ' '
                                                + self.node_list.currentText() + '  ' + self.execution_id.currentText())
            else:
                self.samples_data_lables.append(self.combo_reg.currentText() + ' ' + self.node_list.currentText() + '  ' + self.execution_id.currentText())
            self.combo_parameters.append(self.combo_sample.currentText() + ' ' + self.combo_reg.currentText() + ' ' + self.node_list.currentText() + ' ' + self.execution_id.currentText())
            if (os.path.isfile(self.csv_path2)):
                self.load_samples(self.csv_path2)
                # self.load_samples_from_csv_for_new_meric(self.csv_path2)
                self.plot()
            else:
                print("File not found!", self.csv_path2)
            
        else:
            self.figure.tight_layout()
            
        if self.sortButtonValue == True:
            
            labels_sorted = []
            handles_sorted = []
            colors_sorted = []
            
            for coords in sorted(self.samples_data, key=lambda x: x[0][0]):
                indice_conjunto = self.samples_data.index(coords)
                labels_sorted.append(self.samples_data_lables[indice_conjunto])
                
                colors_sorted.append(self.colors[indice_conjunto])
            
            self.samples_data_lables = labels_sorted
            self.samples_data = sorted(self.samples_data, key=lambda x: x[0][0])
           
            for i in range(0,len(colors_sorted)):
                self.colors[i] = colors_sorted[i]
                

    def change_sw(self):
        self.sw = not self.sw
        self.plot()

    def change_logscaleX(self):
        self.use_logscaleX = not self.use_logscaleX
        self.plot()

    def change_logscaleY(self):
        self.use_logscaleY = not self.use_logscaleY
        self.plot()

    def smoothSamples(self):
        if self.samples_data:
            if self.spinBoxCheck() == 0:
                window_length = self.smoothWindowSizeSpinBox.value()
                poly_order = self.smoothpolyOrderSpinBox.value()

                smooth_samples_data = []

                for line in self.samples_data:
                    tmp_line = []
                    sample_numbers = []
                    sample_vals = []
                    zero_numbers = []
                    for sample in line:
                        # Take out zeros
                        if sample[1] == 0:
                            zero_numbers.append((sample[0]))
                        else:
                            sample_numbers.append(sample[0])
                            sample_vals.append(sample[1])
                    smoothed_sample_vals = signal.savgol_filter(sample_vals, window_length, poly_order)
                    for i, number in enumerate(sample_numbers):
                        if smoothed_sample_vals[i] < self.min_sample_val and smoothed_sample_vals[i] != 0:
                            self.min_sample_val = smoothed_sample_vals[i]
                        if smoothed_sample_vals[i] > self.max_sample_val:
                            self.max_sample_val = smoothed_sample_vals[i]

                        if number - 1 in zero_numbers:  # Put zeros back
                            tmp_line.append((number - 1, 0))

                        tmp_line.append((number, smoothed_sample_vals[i]))

                        if number + 1 in zero_numbers:  # Put zeros back
                            tmp_line.append((number + 1, 0))
                    smooth_samples_data.append(tmp_line)

                self.samples_data = smooth_samples_data
                self.plot()
        else:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, 'Invalid input', 'Please add data to plot before '
                                                                                  'smoothing.',
                                  QtWidgets.QMessageBox.StandardButton.Ok).exec()


    # cluster analysis, data loaded from load_samples.... are passed into it and stored in self.samples_time
    # at index [0] => first loaded configuration, using DBSCAN an operation is performed 
    # that splits the samples into individual clusters
    # parameters can be changed by modifying the value of eps


    def clustering(self):
        self.typeButton_id_time.setEnabled(False)
        self.clearCanvas()
        self.addToPlot()
        self.number.append(-1)
        original_data = self.samples_data[0]
        samples = self.samples_time[0]
        nums = [e[0] for e in samples]
        engs = [e[1] for e in samples]
        avg = np.mean(engs)
        var = np.var(engs)
        std = np.std(engs)
        

        min_region_size = 100
        if 'Voltage regulator' in self.combo_sample.currentText():
            min_region_size = 10

        clustering = DBSCAN(eps=0.85 * std, min_samples=min_region_size,metric=similarity).fit(samples)
        unique_labels = set(clustering.labels_)
        
        if -1 in unique_labels:
            noisy_samples = True
        clusters = [[] for e in range(len(unique_labels))]
        
        for i, label in enumerate(clustering.labels_):
            clusters[label].append(samples[i])
            
        self.samples_data = []
        self.samples_data_lables = []
        self.samples_data.extend(clusters)
        for num, cluster in enumerate(clusters):
            if cluster is clusters[-1] and noisy_samples:
                self.samples_data_lables.append('Noisy samples')
            else:
                self.samples_data_lables.append('Cluster ' + str(num))

        self.samples_xlabel = ""
        self.samples_xlabel = "ID of samples"
        self.plot()

    def checkExId(self):
        listOfFiles = []

        regpath = self.root_folder + '/' + self.combo_reg.currentText()
        listOfFiles = os.listdir(regpath)
        samplefolder = 99999
        for i in range(0, len(listOfFiles)):
            if (listOfFiles[i] == "samples"):
                samplefolder = i
        if (samplefolder != 99999):
            listOfFiles.pop(samplefolder)

        #remove all files from different nodes
        filesToRm = []
        for i in range(0, len(listOfFiles)):
            if (str(self.node_list.currentText()) not in listOfFiles[i]):
                filesToRm.append(i)
        idx = 0

        for i in range(0, len(filesToRm)):
            listOfFiles.pop(filesToRm[i] + idx)
            idx -= 1

        #open and check exec id (init_x)
        execute_id = "init_" + str(self.execution_id.currentText()) + ';'
        execute_id2 = "init_" + str(self.execution_id.currentText()) + '\n'
        self.fileToOpen = ""
        fileFoundCheck = 0
        for f in range(0, len(listOfFiles)):
            path = self.root_folder + '/' + self.combo_reg.currentText() + '/' + listOfFiles[f]
            if (os.path.isfile(path)):
                with open(path, "r") as file:
                    measurements_read = []
                    for line in file:
                        measurements_read.append(line)
                    
                    for line in measurements_read:
                        if(str(execute_id) in line):
                            self.fileToOpen = listOfFiles[f]
                            fileFoundCheck = 1
                            return self.fileToOpen
                        elif(str(execute_id2) in line):
                            self.fileToOpen = listOfFiles[f]
                            fileFoundCheck = 1
                            return self.fileToOpen
        return "CSV_NOT_FOUND"
        
    # graf
    def plot(self):
        self.ax.clear()
        # self.ax = self.figure.add_axes([0.15,0.25,0.6,0.7])   # left,bottom edge, width, height
        if self.mult.text() in ["e", "."] or "," in self.mult.text() or self.mult.text().endswith(
                'e') or self.mult.text().startswith('e'):
            self.numMultiplier = 1.0
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setText("Wrong multiplier format!\nPlease write the multiplier in form AeB (e.g. 1e-4).")
            msg.setWindowTitle("Invalid multiplier")
            msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            msg.exec_()
            self.mult.setText("1")
        elif not float(self.mult.text()):
            self.numMultiplier = 1.0
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setText('Multiplier should be a positive number!\nPlease choose non-zero multiplier.')
            msg.setWindowTitle("Invalid multiplier")
            msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            msg.exec_()
            self.mult.setText("1")
        else:
            self.numMultiplier = float(self.mult.text())

        self.k = self.samples_data_lables

        # changing the first character of labels for matplot lib doens't unterstand they are excluded ones
        for i in range(len(self.k)):
            if self.k[i].startswith("_"):
                self.k[i] = " " + self.k[i]
            elif self.k[i].startswith("\u200c_"):
                continue
            else:
                self.k[i] = "\u200c" + " " + self.k[i]

        self.K = self.samples_data
        self.ky = [h[0] for h in self.K[0]] #popis osy x

        self.n = len(self.k)
        self.optx = self.plot_data[1]["optim_x_val"]
        self.optf = self.plot_data[1]["optim_func_label_value"]
        self.ymin = min([y[1] for y in self.K[0]])
        ymax = 0

        for i in range(0, len(self.K)):
            for j in range(0, len(self.K[i])):
                tmp = list(self.K[i][j])
                tmp[0] = self.numMultiplier * tmp[0]
                self.K[i][j] = tuple(tmp)

        self.funcmax = 0
        while self.n > len(self.colors):
            h = random.uniform(0, 1)
            s = random.uniform(0.4, 0.8)
            v = random.uniform(1, 1)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = tuple(round(x, 1) for x in (r, g, b)) 
            if color not in self.colors:
                self.colors.append(color)
            
        
        colors = self.colors
        #print("self.n", m, self.n)
        for m in (range(0, self.n)): #if reversed here, the first added samples come first
            X = [x[0] for x in self.K[m]]
            Y = [x[1] for x in self.K[m]]

            ### MIN MAX pro osy X a Y
            for i in range(0, len(Y)):
                if (self.max_sample_val < Y[i]):
                    self.max_sample_val = Y[i]
                if (self.min_sample_val > Y[i]):
                    self.min_sample_val = Y[i]
            for i in range(0, len(X)):
                if (self.max_time_val < X[i]):
                    self.max_time_val = X[i]
                if (self.min_time_val > X[i]):
                    self.min_time_val = X[i]

            if self.use_logscaleX:
                self.ax.set_xscale('log')

            if self.use_logscaleY:
                self.ax.set_yscale('log')

            xmin = min(X)
            xmax = max(X)
            ymin0 = min(Y)
            ymax0 = max(Y)
            self.avx = 0.5 * (xmin + xmax)
            if self.ymin > ymin0:
                self.ymin = ymin0

            for idx, it in enumerate(Y):
                if it == ymax0 and it > ymax:
                    ymax = ymax0
                    xmax = X[idx]
                    self.funcmax = self.k[m]

            if self.sw:
                if self.plotType:
                    self.ax.scatter(Y, X, label=self.k[m], color=colors[m], s=self.dotSizeSpinBox.value())
                else:
                    if self.k[m] == 'Noisy samples':
                        self.ax.scatter(Y, X, label=self.k[m], color=colors[m], s=self.dotSizeSpinBox.value())
                    else:
                        self.ax.plot(Y, X, label=self.k[m], color=colors[m])
            else:
                if self.plotType:
                    self.ax.scatter(X, Y, label=self.k[m], color=colors[m], s=self.dotSizeSpinBox.value())
                else:
                    if self.k[m] == 'Noisy samples':
                        self.ax.scatter(X, Y, label=self.k[m], color=colors[m], s=self.dotSizeSpinBox.value())
                    else:
                        self.ax.plot(X, Y, label=self.k[m], color=colors[m])
        
        # plot structure
        self.xlab = self.samples_xlabel
        self.ylab = self.samples_ylabel
        

        if self.maxBox.isChecked():
            optStr = 'Maximum value is at sample: {}.'.format(int(xmax))
        else:
            optStr = ''

        if self.sw:
            self.ax.set_ylabel(self.xlab, fontsize=self.fontSize.value())
            self.ax.set_xlabel(self.ylab, fontsize=self.fontSize.value())
            self.ax.text(1.1 * self.ymin - 0.1 * ymax, 1.3 * xmin - 0.3 * xmax, optStr)
        else:
            self.ax.set_xlabel(self.xlab, fontsize=self.fontSize.value())
            self.ax.set_ylabel(self.ylab, fontsize=self.fontSize.value())
            self.ax.text(1.1 * xmin - 0.1 * xmax, 1.3 * self.ymin - 0.3 * ymax, optStr)

        self.ax.tick_params(labelsize=self.fontSize.value())
        self.ax.grid(linestyle='--')



        ### alignment of the visible part of the graph
        ylim_max = self.max_sample_val + 10 #* 1.1
        ylim_min = self.min_sample_val - 10#* 0.9
        xlim_min = self.min_time_val - 1
        xlim_max = self.max_time_val + 1

        # print("mintime ", self.min_time_val, "maxtime", self.max_time_val)

        self.ax.set_ylim(bottom=ylim_min, top=ylim_max)
        self.ax.set_xlim(left=xlim_min, right=xlim_max)
 
        self.legend()

    def moveLegend(self):
        self.moveY = 0
        if (self.fontSize.value() <= 11):
            self.moveY = -0.15
        elif (self.fontSize.value() <= 20):
            self.moveY = -0.4
        elif (self.fontSize.value() <= 30):
            self.moveY = -0.4
        elif (self.fontSize.value() <= 35):
            self.moveY = -0.4
        elif (self.fontSize.value() <= 40):
            self.moveY = -0.4
        elif (self.fontSize.value() <= 45):
            self.moveY = -0.4
        elif (self.fontSize.value() <= 50):
            self.moveY = -0.4


    def legend(self):
        
        self.handles, self.labels = self.ax.get_legend_handles_labels()
                
        
        
        #colecting legend height before        
        if len(self.labels)>1:
            if hasattr(self, 'lgd'):
                b_legend_box = self.lgd.get_window_extent()
                b_legend_height = int(b_legend_box.height)
        
        
        # adding legend to figure
        self.moveLegend()
        #0.5, -0.15 #default coo of legend
        self.lgd = self.ax.legend(self.handles, self.labels, loc='upper center', bbox_to_anchor=(self.legend_x, self.moveY), ncol=1, borderaxespad=0.,prop = { "size": self.fontSize.value()})

        
        # adapting canvas area to be scrollable when it should be
        h = int(self.canvas_widget.height())
        legend_box = self.lgd.get_window_extent()
        self.legend_width = int(legend_box.width)
        self.legend_height = int(legend_box.height)
        
        
        max_label_width = self.scroll_area.width() - 180  # largura máxima permitida para cada label
        new_labels = []
        new_labels_formatted = []
        
        font = QtGui.QFont()
        font.setPointSize(self.fontSize.value())

        # itera pelas strings (labels) na lista
        for i in range(0,len(self.labels)):
            
            #if QFontMetrics(font).width(self.labels[i]) > max_label_width: #PYQT5
            if QFontMetrics(font).horizontalAdvance(self.labels[i]) > max_label_width: #PYQT6


                line1 = ""
                line2 = ""
                line3 = ""
                line4 = ""
                while QFontMetrics(font).width(self.labels[i]) > max_label_width:
                    line1 = self.labels[i][0:-1]
                    line2 = (self.labels[i][-1]) + line2
                    self.labels[i] = line1
                    if QFontMetrics(font).width(line2) > max_label_width:
                        while QFontMetrics(font).width(line2) > max_label_width:
                            line3 = (line2[-1]) + line3
                            line2 = line2[0:-1]
                        if QFontMetrics(font).width(line3) > max_label_width:
                            while QFontMetrics(font).width(line3) > max_label_width:
                                line4 = (line3[-1]) + line4
                                line3 = line3[0:-1]

                if line3 == "":
                    new_labels.append(line1 + '\n' + line2)
                    new_labels_formatted.append(line1 + '\n' + line2)
                else:
                    if line4 == "":
                        new_labels.append(line1 + '\n' + line2 + '\n' + line3)
                        new_labels_formatted.append(line1 + '\n' + line2 + '\n' + line3)
                    else:
                        new_labels.append(line1 + '\n' + line2 + '\n' + line3 + '\n' + line4)
                        new_labels_formatted.append(line1 + '\n' + line2 + '\n' + line3 + '\n' + line4)

            else:
                new_labels.append(self.labels[i])
                new_labels_formatted.append(self.labels[i])


            #### LEGEND
            new_labels_formatted = [(s.encode('ascii', 'ignore')).decode("utf-8") for s in new_labels_formatted] #funguje s mezerama
            for i in (0,len(new_labels_formatted)-1):
                new_labels_formatted[i] = new_labels_formatted[i].lstrip(' ')

            #self.lgd = self.ax.legend(self.handles, new_labels, loc='upper center', bbox_to_anchor=(self.legend_x, self.moveY), ncol=1, borderaxespad=0.,prop = { "size": self.fontSize.value()})
            self.lgd = self.ax.legend(self.handles, new_labels_formatted, loc='upper center', bbox_to_anchor=(self.legend_x, self.moveY), ncol=1, borderaxespad=0.,prop = { "size": self.fontSize.value()})

            self.figure.tight_layout()
            legend_box = self.lgd.get_window_extent()
            self.legend_width = int(legend_box.width)
            self.legend_height = int(legend_box.height)

        self.canvas_widget.setFixedHeight(self.slider.value() + self.legend_height )
        if self.canvas_widget.height() > self.scroll_area.height()-5:
            self.canvas_widget.setFixedWidth(self.scroll_area.width()-20)
        else:
            self.canvas_widget.setMinimumWidth(self.scroll_area.width()-5)

        self.figure.tight_layout()
        

        for i in range(0, len(self.K)):
            for j in range(0, len(self.K[i])):
                tmp = list(self.K[i][j])
                tmp[0] = 1 / self.numMultiplier * tmp[0]
                self.K[i][j] = tuple(tmp)
                

        
        self.canvas.draw()
        if self.main_menu_instance:
            self.main_menu_instance.show()



    def load_samples(self, csv_path):
        file = csv_path
        data_file = []
        execution_ids = [] # row with string "init_"
        jobid = []
        timestamps = []
        runtime = []

        minpower, maxpower, avgpower, firstsample, lastsample =  ([] for i in range(5))
        sampledir = ""
        ### path to samples
        ### dictionary with initial timestamps of static regions

        currnode = str(self.node_list.currentText())
        currid = str(self.execution_id.currentText())
        if (currnode not in self.static_dict):
            self.static_dict[currnode] = {}
        if (currid not in self.static_dict[currnode]):
            self.static_dict[currnode][currid] = ["null"]
        

        for i in range(0, len(self.allregions)):
            if (self.allregions[i].endswith("_static")):
                sampledir = str(self.allregions[i])
        sampfile = self.root_folder + '/' + sampledir + "/samples/" + str(self.node_list.currentText()) + '_' + str(self.execution_id.currentText()) + ".csv"
        measuringSensor = str(self.combo_sample.currentText()) #hdeem blade etc.
        with open(file, "r") as file:
            for line in file:
                data_file.append(line)
        file.close()

        ### start of the whole static region + calculation of the time offset
        static_file = csv_path.split("/")
        static_file = static_file[-1]
        static_path = self.root_folder + '/' + sampledir + '/' + static_file
        static_starttime = 0
        if (self.static_dict[currnode][currid][0] == "null"):
            with open(static_path, "r") as file:
                for line in file:
                    if ("Function start timestamp" in line):
                        timeline = line.split(",")
                        static_starttime = timeline[1]
                        self.static_dict[currnode][currid][0] = float(static_starttime)
                        break
            file.close()
        else:
            static_starttime = self.static_dict[currnode][currid][0]

        i = 0
        for line in data_file:
            if (measuringSensor in line):

                maxpower.append(data_file[i+2])
                minpower.append(data_file[i+3])
                avgpower.append(data_file[i+4])
                firstsample.append(data_file[i+5])
                lastsample.append(data_file[i+6])
            if ("JOB ID" in line):
                jobidline = line.split(",")
                jobid.append(jobidline[1].strip("\n"))
            if ("Runtime of function" in line):
                runtimeline = line.split(",")
                runtimefloat = float(runtimeline[1].strip("\n"))
                runtime.append(runtimefloat)
            if ("Function start timestamp" in line):
                timestampline = line.split(",")
                timestamps.append(float(timestampline[1].strip("\n")))
                timestamp = float(timestampline[1].strip("\n"))
            if ("init_" in line):
                if (line not in execution_ids):
                    execution_ids.append(line)
            i = i + 1

        for i in range(0, len(minpower)):
            #power
            tempmin = minpower[i].split(",")
            tempmax = maxpower[i].split(",")
            tempavg = avgpower[i].split(",")
            tempmin[1] = tempmin[1][:-1]
            tempmax[1] = tempmax[1][:-1]
            tempavg[1] = tempavg[1][:-1]
            minpower[i] = tempmin[1]
            maxpower[i] = tempmax[1]
            avgpower[i] = tempavg[1]
            
            #samples
            firstid = firstsample[i].split(",")
            lastid = lastsample[i].split(",")
            firstid[1] = firstid[1][:-1]
            lastid[1] = lastid[1][:-1]
            firstsample[i] = firstid[1]
            lastsample[i] = lastid[1]

        sampleindex = 0
        correctblock = 0 # start of parsing samples in the block of the correct sensor (Blade ...)

        correct_ids = 0
        samples = [[]]
        samples_line = []
        tupleline = []

        ### recalculation of the total number of ids

        totsamples = 0
        for i in range(0, len(firstsample)):
            totsamples += int(lastsample[i]) - int(firstsample[i]) + 1

        ### recalculation of total time / number of samples = time of 1 sample

        totruntime = 0

        for i in range(0, len(runtime)):
            totruntime += float(runtime[i])
        onesampletime = float(totruntime)/float(totsamples)
        timeoffset = 0 ### for adding samples





        ### pairing time on the x-axis with the size of samples
        ### if we want samples instead of time on the x-axis, replace timeoffset+onesampletime
        ### with float(row[0])


        timestampdiff = float(timestamps[sampleindex]) - float(static_starttime)
        with open(sampfile, "r") as sampfile:
            # print("opened")
            for sampline in sampfile:
                samples_line = []
                if(correctblock):
                    if ("#" in sampline):
                        break
                if (measuringSensor in sampline):
                    correctblock = 1
                if (correctblock == 1 ):
                    if (str(firstsample[sampleindex]) in sampline): # first sample
                        row = sampline.split(",")
                        if (str(row[0]) == str(firstsample[sampleindex])):
                            correct_ids = 1
                if (correct_ids == 1 & correctblock == 1):
                    row = sampline.split(",")
                    if (int(row[0]) < int(lastsample[sampleindex])):
                        samples_line.append(row[0])
                        samples_line.append(row[1][:-1])
                        samples.append(samples_line)
                        # tmp = (timestampdiff + timeoffset + onesampletime, float(row[1][:-1]))
                        tmp = ( timeoffset, float(row[1][:-1]))
                        timeoffset += onesampletime
                        tupleline.append(tmp)
                    elif (int(row[0]) == int(lastsample[sampleindex])):
                        samples_line.append(row[0])
                        samples_line.append(row[1][:-1])
                        samples.append(samples_line)
                        # tmp = (timestampdiff + timeoffset + onesampletime, float(row[1][:-1]))
                        tmp = ( timeoffset, float(row[1][:-1]))
                        timeoffset += onesampletime
                        tupleline.append(tmp)
                        if (sampleindex < len(lastsample) - 1):
                            sampleindex = sampleindex + 1
                            correct_ids = 0
                            timestampdiff = float(timestamps[sampleindex]) - float(static_starttime)
                            tmp2 = (timeoffset, float(np.nan))
                            tupleline.append(tmp2)
                        else:
                            tmp2 = (timeoffset, float(np.nan))
                            tupleline.append(tmp2)
                            break
                else:

                    continue
        sampfile.close()

        ### data for chart time/W
        if (len(tupleline) < 3):
            tupleline_short = []
            tmp1 = tupleline[0]
            tmp2 = (tupleline[0][0]*1.01, tupleline[0][1]*0.9)
            tmp3 = tupleline[1]
            tupleline_short.append(tmp1)
            tupleline_short.append(tmp2)
            tupleline_short.append(tmp3)
            self.samples_data.append(tupleline_short)
        else:
            self.samples_data.append(tupleline)

        self.samples_xlabel = ""
        self.samples_xlabel = "Time [s]"


    # load_samples_from_csv_for_new_meric:
    # loading samples for the new meter, where there is a change in saving samples,
    # which are stored only in the static region
    # in other regions there are only id_of_first/last_samples with runtime and start time of execution
    # after selecting a region and configuration (file), the start and call time are loaded along with
    # id of first and last samples, then the static is traversed and in it a file with the same configuration
    # (same name) is selected, from which the samples are cut out and attached to the time
    # this function replaces load_samples_from_csv(self, csv_path) which, unlike this new one,
    # loads samples from the selected region

    
    def load_samples_from_csv_for_new_meric(self, csv_path):
        new_samples_data = []
        new_samples_data_nul = []
        new_time_data = []
        new_time_data_zero = []
        data_samples = []
        samples_id = []
        calltree = ""
        execution_ids = []
        num = 0
        added_zeros_count = 0
        time = []
        run = []
        runtime = [[],[]]
        samples_firs_last = [[],[]]
        static_name = self.static_name


        static = float(static_start(csv_path,static_name))

        
        text = self.combo_sample.currentText()
        text = text.split(")")[0] +")"
        
        self.csv_name = csv_path.split("/")[-1]
        data_file = []
        with open(csv_path, "r") as file:
            for line in file:
                data_file.append(line)

        for line in data_file:
            if "CALLTREE" in line:
                calltree = line.split(";")[1]
                calltree = calltree.split("_")[-1].strip("\n")
                if calltree not in execution_ids:
                    execution_ids.append(calltree)

            if "JOB ID" in line:
                str_prev = line

            if "Runtime of function" in line and "JOB ID" in str_prev:
                line = line.split(",")
                runtime_a = float(line[1].strip("\n"))


                tmp = runtime_a
            if "Function start timestamp" in line and "JOB ID" in str_prev:
                line = line.split(",")
                timestamp = float(line[1].strip("\n"))
                runtime[1].append(timestamp-static)
                runtime[0].append(runtime_a+timestamp-static)
                time.append(timestamp - static)
                run.append(runtime_a+timestamp-static)
                self.number.append(num)
                num = num + 1
            continue
        

        for line in data_file:
            if "JOB ID" in line:# and calltree in str_prev_call:
                str_prev = line
            if "Runtime of function" in line and "JOB ID" in str_prev:# and calltree in str_prev_call:
                line = line.split(",")
                runtime_a = float(line[1].strip("\n"))
                tmp = runtime_a
            if "Function start timestamp" in line and "JOB ID" in str_prev: # and calltree in str_prev_call:
                line = line.split(",")
                timestamp = float(line[1].strip("\n"))
                runtime[1].append(timestamp-static)
                runtime[0].append(runtime_a+timestamp-static)
                time.append(timestamp - static)
                run.append(runtime_a+timestamp-static)
                self.number.append(num)
                num = num + 1
        pocet = 0
        str_prev = False
        for line in data_file:
            if text in line:
                str_prev = True
                pocet = pocet + 1
            if str_prev and "ID of first sample" in line:
                line = line.split(",")
                samples_firs_last[0].append(int(line[1].strip("\n")))
            if str_prev and "ID of last sample" in line:
                line = line.split(",")
                samples_firs_last[1].append(int(line[1].strip("\n")))
                str_prev = False

        runtime[0] = runtime[0][:len(runtime[1])]
        runtime = [[runtime[0][i], runtime[1][i]] for i in range(len(runtime[0]))]
        samples_firs_last[0] = samples_firs_last[0][:len(samples_firs_last[1])]
        samples_firs_last = [[samples_firs_last[0][i], samples_firs_last[1][i]] for i in range(len(samples_firs_last[0]))]

        path = csv_path.split("/")
        path[-2] = self.static_name
        #original

        path[-1] = "samples" + "/" + str(self.node_list.currentText()) + '_' + str(self.actual_id) + ".csv"
        csv_path = "/".join(path)

        csv_file = open(csv_path, "r")
        reading_samples = False
        next_call = False
        iter = 0
        text = text + " power [W]:"
        self.text = text

        data = []
        pocet_Textu = []
        power = 0
        for i in samples_firs_last:
            a = i[0]
            b = i[1]
            csv_file = open(csv_path, "r")
            line_data = (float(np.nan), float(np.nan))

            new_samples_data.append(line_data)
            for line in csv_file:
                line = line.strip("\n")
                if text in line:
                    reading_samples = True
                    samples_id.append(int(0))
                    pocet_Textu.append(line)
                    continue
                if "#" in line and text not in line:
                    reading_samples = False
                if reading_samples == True:
                    line = line.split(",")
                    line[0] = int(line[0])
                    line[1] = float(line[1].strip("\n"))
                    if line[0] >= a and b >= line[0]:
                        next_call = True
                        power_sample_number = int(line[0])
                        power = power_sample_number
                        power_sample_value = float(line[1])
                        data.append(power_sample_value)
                        if power_sample_value < self.min_sample_val and power_sample_value != 0:
                            self.min_sample_val = power_sample_value
                        if power_sample_value > self.max_sample_val:
                            self.max_sample_val = power_sample_value
                        line_data = (power_sample_number, power_sample_value)
                        line_data1 = (power_sample_number, power_sample_value)
                        line_data_zero = (power_sample_number, power_sample_value)
                        samples_id.append(power_sample_number)
                        new_samples_data.append(line_data)
                        
                        new_samples_data_nul.append(line_data_zero)
                        data_samples.append(line_data1)

                    if next_call and line[0] == a :
                        line_pokus = (line[0] - 1, float(0))
                        data_samples.append(line_pokus)
                        next_call = False
                    else:
                        continue
                else:
                    continue

            reading_samples = False
            line_data = (float(np.nan), float(np.nan))
            new_samples_data.append(line_data)

        pocet = len(new_samples_data)
        region_start_time = time[0]
        stop = region_start_time
        cas = 0
        real_time = []
        samples_time_val = [[], []]

        samples_id.append(int(0))
        c = 0
        sam = []

        for i in run:
            stop = stop + i
            cas = cas + i
        
        s = np.linspace(region_start_time, stop, pocet)
        #samples with time and np.nun
        samples_val = [[],[]]
        #samples with time and 0
        samples_val_zero = [[],[]]
        zero_if = []

        for i in samples_id:
            #c = 0
            if i == 0:
                tmp = i
                sam.append(c)
                c = 0
            if tmp == 0:
                c = c + 1
            else:
                c = 0

        sam.remove(0)
        sam1 =[]
        for i in sam:
            if not i == 1:
                sam1.append(i)
        

        len_s = []
        for i, j in enumerate(sam1):
            s = ""
            s = np.linspace(time[i], run[i], j)
            
            d = len(s)
            len_s.append(d)
            for j in s:
                real_time.append(j)
                samples_val[0].append(j)
                samples_val_zero[0].append(j)
            samples_val[0].append(run[i])
            samples_val_zero[0].append(run[i])
            s = ""

        for i in new_samples_data:
            j = list(i)
            a = j[1]
            samples_val[1].append(a)
            samples_val_zero[1].append(a)
            zero_if.append(a)

        item = 0
        
        index_of_zero = []
        for i, j in enumerate(zero_if):
            if j == item:
                index_of_zero.append(i)

        samples_val[0] = samples_val[0][:len(samples_val[1])]

        samples_val = [[samples_val[0][i], samples_val[1][i]] for i in range(len(samples_val[0]))]

        samples_val_zero[0] = samples_val_zero[0][:len(samples_val_zero[1])]
        samples_val_zero = [[samples_val_zero[0][i], samples_val_zero[1][i]] for i in range(len(samples_val_zero[0]))]
        
        for i in samples_val:
            tmp = (i[0],i[1])

            new_time_data.append(tmp)

        for i in samples_val_zero:
            tmp = (i[0],i[1])
            new_time_data_zero.append(tmp)

        csv_file.close()
        
        self.samples_xlabel = ""
        self.samples_xlabel = "Time [s]"
        if self.max_data_len < len(new_samples_data) - added_zeros_count:  # true length of data
            self.max_data_len = len(new_samples_data) - added_zeros_count
        # samples and time with np.null
        ### uncomment


        self.samples_data.append(new_time_data)


        self.samples_data_null.append(new_samples_data_nul)
        self.samples_time.append(data_samples)
    



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window(1)
    main.show()

    sys.exit(app.exec_())

# this is the only function that is not in the class, the parameter of this function is the path to the selected file
# then a file with the same name as the selected file is opened, but from the static region, 
# and then the first timestamp is selected
# which is the actual start time of the measurement and is also the return of this function (static_first)
# static_first is then used to calculate the time when samples are measured and when they are not


def static_start(path,name):
        path = path
        static = path.split("/")
        static[-2] = name
        static_path = "/".join(static)
        static_data = []
        with open(static_path, "r") as file:
            for line in file:
                static_data.append(line)
        runtime_area = []
        for line in static_data:
            if "timestamp" in line:
                runtime_area.append(float(line.split(",")[1].split("\n")[0]))
        static_first = runtime_area[0]
        return static_first
