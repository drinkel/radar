#!/usr/bin/env python3
import re, os
import pandas as pd
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import seaborn as sns
import datetime as dt
from pandas.plotting import table
import re
#import tkinter as tk
#from tkinter import filedialog
from pathlib import Path
import glob
from collections import Counter
import os
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.font_manager import FontProperties
import sys
import PyQt6
from PyQt6 import QtGui, QtCore, QtWidgets
from src import data_load
#from src import design_timeline_visualisation
# import os
# import json
# import sip
import sys
# import shutil
# import glob
# import traceback
# from pathlib import Path
# from src import data_plot
# from src import samples_plot
# from src import heatmap
# from src import pyyed_tree
# from src import pydot_example
# from src import all_tables
# from src import radarGUI_analyze
# from src import mericOpt
# from src import texReportDialog
# from src import design_main_menu
# from src import data_load
# from src import timeline_visualisation
# from runpy import run_path
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication,QMainWindow
from functools import partial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import matplotlib.pylab as pl
import numpy as np
import copy as cp
from runpy import run_path
import pprint
import os
import textwrap
from shutil import copyfile
import warnings
import matplotlib.cbook
import matplotlib
# warnings.filterwarnings('ignore', category=matplotlib.cbook.mplDeprecation)
warnings.filterwarnings('ignore', category=matplotlib.MatplotlibDeprecationWarning)
#from src import design_timeline_visualisation







##### this application plots graphs depending on time, under the timeline button, 
##### it plots several types of graphs depending on what is found in the selected files
#### the timeline_visualisation graph is always plotted, it is the graph see git issue #20 
#### on the y-axis regions and "" (empty string) are displayed, on the x-axis are runtimes (start and end)
#### to ensure that in line_plot individual calls are separated, np.null is added after the end of the call
#### other graphs depend on the input data, first the static region is traversed to see what was measured 
#### and based on that they are added into the combo box where you choose between graphs
####
#### functions under the class are still used in some cases but some can be deleted
#### for correct functionality it is necessary to specify the opts file when starting the radar
#### this application works relatively independently of other applications, with the path to the files 
#### passed from data_load, otherwise this application loads data itself


class Window(QtWidgets.QDialog):
    sendInfo = QtCore.pyqtSignal(object)
    plotlist = []
    def __init__(self, ownData=None, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()
        # self.ax = self.figure.add_subplot(111)
        self.ax = self.figure.add_axes([0.25, 0.25, 0.6, 0.7])  # left,bottom edge, width, height
        self.sw = False
        self.use_logscaleX = False
        self.use_logscaleY = False
        # self.isCanvasClear = True
        self.id_min = 0
        self.id_max = 10
        self.setWindowTitle("Timeline")

        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.button2 = QtWidgets.QCheckBox('Switch axes')
        self.button2.clicked.connect(self.change_sw)
        self.maxBox = QtWidgets.QCheckBox('Show maximum')
        self.maxBox.clicked.connect(self.plot)
        self.logscaleX = QtWidgets.QCheckBox('log scale for axis X')
        self.logscaleX.clicked.connect(self.change_logscaleX)
        self.logscaleY = QtWidgets.QCheckBox('log scale for axis y')
        self.logscaleY.clicked.connect(self.change_logscaleY)

        self.button3 = QtWidgets.QPushButton('Apply multiplier')
        self.button3.clicked.connect(self.plot)
        self.button4 = QtWidgets.QPushButton('Generate LaTeX code')
        self.button4.clicked.connect(self.getTeX)
        self.addButton = QtWidgets.QPushButton('Add to LaTeX report')
        self.addButton.clicked.connect(self.emitTeXInfo)
        self.typeButton = QtWidgets.QPushButton('Scatter plot')
        self.plotType = 0
        self.typeButton.clicked.connect(self.changeType)


        self.bf = QtGui.QFont("Arial", 13, QtGui.QFont.Weight.Bold)

        self.mult = QtWidgets.QLineEdit("1")
        self.mult.setAlignment(QtCore.Qt.AlignCenter)
        self.mult.setValidator(QtGui.QDoubleValidator())



        # data loading, we can have more than one y_data! TODO
        self.d = ownData

        self.data = self.d["plot_summary_data"]

        self.region = self.d["region"]
        for i in self.region:
            if i.endswith("_static"):

                static_name = i
        self.combo_reg = QtWidgets.QComboBox(self)
        self.combo_reg.addItem('Choose region')
        self.combo_reg.addItem(static_name)

        root = self.d["parameter_len"]
        root_folder = root[0]
        deflist = []

        for i in range(root_folder):
            deflist.append(str(0))
        self.default = '_'.join(deflist) + ".csv"


        # TODO - multiple measurements handling (2 in range is ad hoc)
        if "nested_regions_report_data" in self.d.keys():
            for i in range(0, len(self.d["nested_regions_report_data"])):
                comboItem = "{}".format(self.d["nested_regions_report_data"][i]["nested_region"])
                if comboItem not in [self.combo_reg.itemText(i) for i in range(self.combo_reg.count())]:
                    self.combo_reg.addItem(comboItem)
        self.combo_reg.addItem('All regions')


        self.combo = QtWidgets.QComboBox(self)
        data_for_combo = self.combo_add_universal()
        #data_for_combo = self.combo_graf_add()
        self.combo.addItem('Choose plot')
        #self.combo.addItem('Timeline visualisation')
        #self.combo.addItem('Runtime area graph')
        #self.combo.addItem('Term area graph')
        # self.combo.addItem('freq area graph')
        self.combo.addItems(data_for_combo)
        self.combo.activated[str].connect(self.onChanged)




        # set the layout
        layout = QtWidgets.QVBoxLayout()

        self.plot_data = self.data[0]
        self.keyList = list(self.plot_data[1]["key"])
        for i in range(0, len(self.keyList)):
            self.keyList[i] = self.keyList[i].replace(';', ' ')

        self.lab_reg = QtWidgets.QLabel('Choose Area: ')
        self.lab_reg.setFont(self.bf)
        hl_reg = QtWidgets.QHBoxLayout()
        hl_reg.addWidget(self.lab_reg)
        hl_reg.addWidget(self.combo_reg)
        self.combo_reg.activated[str].connect(self.onChanged)
        #self.combo_reg.activated[str].connect(self.onChangeded)
        layout.addLayout(hl_reg)




        self.label = QtWidgets.QLabel('Choose Graph Type: ')
        self.label.setFont(self.bf)
        hl = QtWidgets.QHBoxLayout()
        hl.addWidget(self.label)
        hl.addWidget(self.combo)
        #self.combo.activated[str].connect(self.chooseData)
        layout.addLayout(hl)

        self.combo_plot = QtWidgets.QComboBox(self)
        hl.addWidget(self.combo_plot)
        # self.combo_plot.addItem('Choose plot')
        # self.combo_plot.addItem('Timeline visualisation')
        self.combo_plot.activated[str].connect(self.onChanged)

        self.labelFontsize = QtWidgets.QLabel("Execution id: ")
        #self.labelFontsize.setFixedWidth(60)
        self.execution_ID = QtWidgets.QSpinBox()
        #self.execution_ID.setFixedWidth(100)
        self.execution_ID.setValue(self.id_min)
        self.execution_ID.setMinimum(self.id_min)
        self.execution_ID.setSingleStep(1)
        self.execution_ID.setMaximum(self.id_max)
        hl_font = QtWidgets.QHBoxLayout()
        hl_font.addWidget(self.labelFontsize)
        hl_font.addWidget(self.execution_ID)

        self.addButton_plot = QtWidgets.QPushButton('Add to plot')
        self.addButton_plot.clicked.connect(self.button_click)
        #self.addButton_plot.setFixedWidth(130)
        hl_button = QtWidgets.QHBoxLayout()
        hl_button.addWidget(self.addButton_plot)

        #self.execution_ID.valueChanged.connect(self.execution_IDChanged)
        #self.execution_ID.setEnabled(False)
        # layout.addWidget(self.execution_ID)
        layout.addLayout(hl_font)
        layout.addLayout(hl_button)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        hlayout = QtWidgets.QHBoxLayout()
        # tmp remove multiplier
        # hlayout.addWidget(self.mult)
        # hlayout.addWidget(self.button3)

        # hlayout2 = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.button2)
        hlayout.addWidget(self.maxBox)
        hlayout.addWidget(self.logscaleX)
        hlayout.addWidget(self.logscaleY)
        # hlayout2.addWidget(self.button4)

        layout.addLayout(hlayout)
        hlayout3 = QtWidgets.QHBoxLayout()
        hlayout3.addWidget(self.typeButton)
        hlayout3.addWidget(self.button4)
        hlayout3.addWidget(self.addButton)

        layout.addLayout(hlayout3)
        #self.start = self.static_start()
        # layout.addLayout(hlayout2)
        self.setLayout(layout)
        #self.combo_graf_add()
        self.combo_add_universal()
        self.onChanged()
        self.resize(800, 800)





    def button_click(self):
        self.id = self.execution_ID.value()

        reg = str(self.combo_reg.currentText())

        self.id = "init_"+ str(self.id)

        self.data_csv = self.d["_csv_"]
        list = self.data_csv
        a = []
        def_path = []
        reg_path = ""
        static_path = ""

        for i in list:
            a = a + i
        for i in a:
            j = i.split("/")
            if j[-1] == self.default or "default.csv" in j[-1] or "log.csv" in j[-1]:
                def_path.append(i)

        for i in def_path:
            if reg in i:
                reg_path = str(i)

        text = str(self.combo.currentText())
        plot = str(self.combo_plot.currentText())
        self.ax.clear()

        if plot == "Timeline visualisation":
            self.plot_timeline(def_path)
            combo_text_plot = plot




        if "START" in text or "STOP" in text:

            combo_text_plot = text
            #self.plot_term()reg_path
            self.plot_universal_start_stop(reg_path, text )

        elif plot == "Timeline visualisation":

            combo_text_plot = text
            self.plot_timeline(def_path)
            self.combo_plot.clearEditText()

        elif "Runtime of function [s]" in text:
            combo_text_plot = text
            self.plot_runtime(reg_path)


        elif text == "freq area graph":
            combo_text_plot = text
            self.plot_freq()
        elif text == "Choose plot":
            combo_text_plot = text
            self.plot()
        elif "ALL" in text:
            combo_text_plot = text
            self.plot_all_nova(def_path, text, self.id)
        else:
            combo_text_plot = text
            self.plot_universal_1(def_path, text, self.id)


        self.combo.clearEditText()
        self.combo_plot.clearEditText()


        return combo_text_plot
    # this function handles the change of the graph, it is probably the most important of all

    def onChanged(self):
        id = self.execution_ID.value()

        reg = str(self.combo_reg.currentText())

        if not "All regions" in reg:

            self.combo.show()
            self.combo_plot.hide()
            self.combo_plot.clearEditText()
            self.combo_plot.clear()


        else:
            self.combo.hide()
            self.combo_plot.show()
            self.combo.clearEditText()
            list = []
            if 'Choose plot' not in list:
                list.append('Choose plot')
            if 'Timeline visualisation' not in list:
                list.append('Timeline visualisation')
            #self.combo_plot.update('Choose plot')
            #if not self.combo_plot.item
            #self.combo_plot.addItem('Timeline visualisation')
            for i in list:
                self.combo_plot.addItem(i)


        self.combo.clearEditText()
        self.combo_plot.clearEditText()

    # button below changes the graph type from line plot to scatter plot
    def changeType(self):
        self.plotType = not self.plotType
        if self.plotType:
            #self.typeButton.setText('Scatter plot')
            self.typeButton.setText('Line plot')
        else:
            #self.typeButton.setText('Line plot')
            self.typeButton.setText('Scatter plot')
        self.onChanged()
        self.button_click()

    def emitTeXInfo(self):
        if str(self.combo_reg.currentText()) == "Overall summary":
            reg = list(self.d['config']['main_reg'][0].keys())[0]
        else:
            reg = str(self.combo_reg.currentText())[9:]
        for i in range(len(self.data)):
            if self.data[i][0]['arg'] in str(self.combo.currentText()):
                q = self.data[i][0]['arg']
                c = self.data[i][0]['category']
        self.sendInfo.emit(
            {'quantity': q, 'category': c, 'region': reg, 'multiplier': float(self.mult.text()), 'switched': self.sw,
             'dot': self.plotType})
        self.addButton.setEnabled(False)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Current plot was added to LaTeX report.")
        msg.setWindowTitle("LaTeX report info")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.buttonClicked.connect(msg.close)
        msg.exec_()

    def getTeX(self):
        dlg = QtWidgets.QFileDialog()
        save_file_path = str(dlg.getSaveFileName(filter='LaTeX code (*.tex)')[0])
        if save_file_path and not save_file_path.endswith('.tex'):
            save_file_path = save_file_path + '.tex'

        if not save_file_path:
            return 0
        # save_file_path = "/home/david/SGS18-READEX/graf.tex"
        target_file = '/'.join(save_file_path.split('/')[0:-1]) + '/readex_header.tex'
        copyfile(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/input/readex_header.tex', target_file)

        tex_file = open(save_file_path, "w")
        tex_file.write(r'\documentclass{article}')
        tex_file.write(r'''\n\input{readex_header}\n''')

        tex_file.write(r'\begin{document}')

        title = '{}, {}'.format(str(self.combo_reg.currentText()), str(self.combo.currentText()))
        x_lab = r"{}\,[{}{}]".format(self.plot_data[1]["x_label_name"], '' if self.numMultiplier.is_integer() and int(self.numMultiplier) == 1 else 1/self.numMultiplier, self.plot_data[1]["x_label_unit"])

        y_lab = self.plot_data[0]["arg"]
        func_lab = r"{}\,[{}]".format(self.plot_data[1]["func_label_name"], self.plot_data[1]["func_label_unit"])
        only_marks = self.plotType

        header_code = (r'''
                \begin{{adjustbox}}{{center, valign=t}}
                \begin{{tikzpicture}}
                \begin{{axis}}[
                align=center,
                title={{ {} }},
                xlabel={{ {} }},
                ylabel={{ {} }},
                legend pos=outer north east,
                xmajorgrids=true,
                ymajorgrids=true,
                grid style=dashed,
                width=\textwidth*0.9,
                height=\textwidth*0.6,
                cycle list name = color list,
                each nth point = 1,
                filter discard warning=false
                ]
                \addlegendimage{{empty legend}}
                '''.format(title, y_lab if self.sw else x_lab, x_lab if self.sw else y_lab))

        tex_file.write(textwrap.dedent(header_code))
        tex_file.write('\n\n')

        if self.sw:
            a = 1
            b = 0
        else:
            a = 0
            b = 1

        for i in range(0, self.n):
            code = (r'''\addplot+ [mark=triangle*{}] coordinates {{ {}
                     }};
                     '''.format(',only marks' if only_marks else '',
                                '\n'.join([str((self.numMultiplier * e[a], e[b])) for e in self.K[i]])))
            tex_file.write(code)

        legend_title = r'\hspace{{-.6cm}} {} '.format(
            "{} [{}]".format(self.plot_data[1]["func_label_name"], self.plot_data[1]["func_label_unit"]))

        ret = ''
        if not self.k:
            ret = r'\legend{{ {} }}'.format(','.join(filter(None, [legend_title] + [str(i) for i in range(self.n)])))
        else:
            ret = r'\legend{{ {} }}'.format(','.join(filter(None, [legend_title] + [str(item) for item in self.k])))


        tex_file.write(ret)

        optim_code = r'''
                \addplot [only marks] table {{
                    {0} {1}
                }} node [pin={{[pin distance={4}pt]{3}:{{\footnotesize( {2} )}}}}]{{}};
                '''
        optim_code = textwrap.dedent(optim_code)
        title_angle = title_angle = 210 if self.optx > 0.5 * (min(self.ky) + max(self.ky)) else 330
        title_distance = 2
        optim_title = 'optimal settings are {}: {} {}, {}: {} {}'.format(self.plot_data[1]["x_label_name"], self.optx,
                                                                         self.plot_data[1]["x_label_unit"],
                                                                         self.plot_data[1]["func_label_name"],
                                                                         self.optf,
                                                                         self.plot_data[1]["func_label_unit"])
        optim_code = optim_code.format(self.ymin if self.sw else self.numMultiplier * self.optx,
                                       self.numMultiplier * self.optx if self.sw else self.ymin,
                                       optim_title,
                                       title_angle, title_distance)

        tex_file.write(optim_code)
        tex_file.write(r'\n\end{axis}\n\end{tikzpicture}\n\end{adjustbox}\n\n\end{document}')


        tex_file.close()

    def chooseReg(self, dataLabel):
        if dataLabel == "Overall summary":
            self.data = self.d["plot_summary_data"]
        else:
            for i in range(0, len(self.d["nested_regions_report_data"])):
                tmp = "REGION - {}".format(self.d["nested_regions_report_data"][i]["nested_region"])

                if dataLabel == tmp:
                    self.data = self.d["nested_regions_report_data"][i]["plot_data"]
        self.plot_data = self.data[0]
        if len(self.data) > 1:
            for i in range(0, len(self.data)):
                if str(self.combo.currentText()) == "{}, {}".format(self.data[i][0]["category"],
                                                                    self.data[i][0]["arg"]):
                    self.plot_data = self.data[i]
        # self.keyList = list(self.plot_data[1]['key'])
        # for i in range(0, len(self.keyList)):
        #     self.keyList[i] = self.keyList[i].replace(';', ' ')
        #self.onChanged(dataLabel)
        return dataLabel

    def chooseData(self, dataLabel):
        for i in range(0, len(self.data)):
            if dataLabel == "{}, {}".format(self.data[i][0]["category"], self.data[i][0]["arg"]):
                self.plot_data = self.data[i]


    def change_sw(self):
        self.sw = self.sw
        self.onChanged()
        self.button_click()
    
    #radio button
    def change_logscaleX(self):
        self.use_logscaleX = not self.use_logscaleX
        #self.plot()
    
    #radio button
    def change_logscaleY(self):
        self.use_logscaleY = not self.use_logscaleY
        #self.plot()

    # function plotting the runtime graph
    def plot_runtime(self, path):
        self.ax.clear()
        self.isCanvasClear = False

        path = path
        data_file = []
        if not path:
            self.plot()

        else:
             with open(path, "r") as file:
                for line in file:
                     data_file.append(line)
        runtime_area = analyze_data(data_file, ["Runtime"])
        # mathplotlib dela automaticky jednotky na osu
        # self.ax = self.figure.add_axes([0.15,0.25,0.6,0.7])   # left,bottom edge, width, height
        self.numMultiplier = float(self.mult.text())



        if self.sw:
            if self.plotType:
                self.ax.plot(runtime_area)
            else:
                self.ax.plot(runtime_area, 'o')

        else:
            if self.plotType:
                self.ax.plot(runtime_area)
            else:
                self.ax.plot(runtime_area, 'o')
        self.ax.set_ylabel("Runtime of function [s]")
        self.ax.tick_params(labelsize=11)


        self.ax.grid(linestyle='--')
        self.ax.plot()

        self.canvas.draw()

    # function plotting an empty canvas at the initial press of the timeline button
    def plot(self):

        self.ax.clear()
        self.isCanvasClear = False
        self.ax.plot()
        self.canvas.draw()

    # frequency graph
    def plot_freq(self):
        #start, area = self.onChanged()
        self.ax.clear()
        self.isCanvasClear = False

        start = open_static_36()
        data = get_data_from_file_window()
        runtime_area = analyze_data_runtime_timestamp(data)

        term_list0 = [[], []]

        freq_PKG_all = analyze_data_freq(data)

        start_stop = []

        for i in runtime_area:
            a = i[1] - start
            b = i[0] + i[1] - start
            start_stop.append(float(a))
            start_stop.append(float(b))

        freq_PKG0 = []
        freq_PKG1 = []

        for i in freq_PKG_all:
            a = i[0]
            b = i[1]
            freq_PKG0.append(float(a))
            freq_PKG0.append(float(a))
            freq_PKG1.append(float(b))
            freq_PKG1.append(float(b))

        if self.sw:
            if self.plotType:
                self.ax.plot(start_stop, freq_PKG0)
                self.ax.plot(start_stop, freq_PKG1)
            else:
                self.ax.plot(start_stop, freq_PKG0, 'o')
                self.ax.plot(start_stop, freq_PKG1, 'o')
        else:
            if self.plotType:
                self.ax.plot(start_stop, freq_PKG0)
                self.ax.plot(start_stop, freq_PKG1)
            else:
                self.ax.plot(start_stop, freq_PKG0, 'o')
                self.ax.plot(start_stop, freq_PKG1, 'o')



        self.ax.plot()
        self.canvas.draw()

    # Chart of temperature
    def plot_term(self):
        self.ax.clear()
        self.isCanvasClear = False

        start = open_static_36()
        data = get_data_from_file_window()
        runtime_area = analyze_data_runtime_timestamp(data)
        # term_PKG_all = analyze_data_term(data)
        term_PKG_all = [[], []]
        for line in data:
            if "START_TEMP_PKG_0" in line:
                term_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
            if "STOP_TEMP_PKG_0" in line:
                term_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
            if "START_TEMP_PKG_1" in line:
                term_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))
            if "STOP_TEMP_PKG_1" in line:
                term_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))

        term_PKG_all[0] = term_PKG_all[0][:len(term_PKG_all[1])]

        term_PKG_all = [[term_PKG_all[0][i], term_PKG_all[1][i]] for i in range(len(term_PKG_all[0]))]

        start_stop = []

        # start = runtime_area[0][1]
        for i in runtime_area:
            a = i[1] - start
            b = i[0] + i[1] - start
            start_stop.append(float(a))
            start_stop.append(float(b))

        term_PKG0 = []
        term_PKG1 = []

        for i in term_PKG_all:
            a = i[0]
            b = i[1]
            term_PKG0.append(float(a))
            term_PKG1.append(float(b))



        if self.sw:
            if self.plotType:
                self.ax.plot(start_stop, term_PKG0)
                self.ax.plot(start_stop, term_PKG1)
            else:
                self.ax.plot(start_stop, term_PKG0,'o')
                self.ax.plot(start_stop, term_PKG1,'o')
        else:
            if self.plotType:
                self.ax.plot(start_stop, term_PKG0)
                self.ax.plot(start_stop, term_PKG1)
            else:
                self.ax.plot(start_stop, term_PKG0, 'o')
                self.ax.plot(start_stop, term_PKG1, 'o')


        self.canvas.draw()
    # function plotting the timeline, see link in the next issue,
    # this graph is always among the options, it loads all runtimes and start times 
    # from all def files from the regions specified in the input data
    #https://code.it4i.cz/vys0053/SGS18-READEX/-/issues/20
    def plot_timeline(self, path):
        # start, area = self.onChanged()


        self.ax.clear()
        self.isCanvasClear = False
        self.numMultiplier = float(self.mult.text())

        cesta = path
        area_number = 0
        data_for_graph = [[], []]
        list_statrt_stop = []
        list_area = []

        for i in path:

            if self.default in i or "default.csv" in i or "log.csv" in i:
                i = i.split("/")
                if i[-2].endswith("_static"):
                    i = "/".join(i)
                    static_path = i
        static = static_start(static_path)
        legend = []

        id = self.execution_ID.value()
        for i in path:
            path_ces = os.path.dirname(i)
            folders_name = os.path.basename(path_ces)
            area_number += 1
            data = []
            with open(i, "r") as file:
                for line in file:
                    data.append(line)
                runtime_area = analyze_data_runtime_timestamp(data,self.id)

            string = ""
            string = str(area_number) + "=" + folders_name

            legend.append(string)
            # print(runtime)
            for j in runtime_area:
                a = j[1] - static
                b = j[0] + j[1] - static

                list_statrt_stop.append(float(a))
                list_statrt_stop.append(float(b))
                list_statrt_stop.append(np.nan)
                list_area.append(folders_name)

                tmp = [float(b), area_number]
                list_area.append(folders_name)

                tmp = [np.nan, np.nan]
                list_area.append("")

        if self.sw:
            if self.plotType:

                self.typeButton.setText('Line plot')
                self.ax.plot(list_statrt_stop, list_area, 'o')
            else:
                self.typeButton.setText('Scatter plot')
                self.ax.plot(list_statrt_stop, list_area)

        else:
            if self.plotType:
                self.typeButton.setText('Line plot')
                self.ax.plot(list_statrt_stop, list_area, 'o')
            else:
                self.typeButton.setText('Scatter plot')
                self.ax.plot(list_statrt_stop, list_area)


        self.ax.set_xlabel("Time [s]")
        self.ax.plot()

        self.canvas.draw()

    # function of a universal graph, according to the selected label in the plotType combobox
    # not used
    def plot_universal(self, path, key):
        self.ax.clear()
        self.isCanvasClear = False
        self.data_csv = self.d["_csv_"]


        list = self.data_csv
        a = []
        def_path = []
        reg_path = ""
        static_path = ""

        for i in list:
            a = a + i
        for j in a:
            if self.default in j or "default.csv" in j or "log.csv" in j:
                j = j.split("/")
                if j[-2].endswith("_static"):
                    j = "/".join(j)
                    static_path = j

        static = static_start(static_path)
        path = path
        key = key
        time = []
        if not path:
            self.plot()
        else:
            data_file = []
            with open(path, "r") as file:
                for line in file:
                    data_file.append(line)
            runtime_area = analyze_data_for_plot(data_file, key, self.id)
            start = analyze_data_3(data_file)

            for i in start:
                t = i - static
                time.append(float(t))
            # matplotlib automatically creates units on the axis
            # self.ax = self.figure.add_axes([0.15,0.25,0.6,0.7])   # left,bottom edge, width, height
            self.numMultiplier = float(self.mult.text())

            if self.sw:
                if self.plotType:
                    self.ax.plot(time, runtime_area)
                else:
                    self.ax.plot(time, runtime_area, 'o')

            else:
                if self.plotType:
                    self.ax.plot(time, runtime_area)
                else:
                    self.ax.plot(time, runtime_area, 'o')

            self.ax.set_ylabel(key)
            self.ax.set_xlabel("Time [s]")

            self.ax.tick_params(labelsize=11)
            self.ax.set_title(key)

            self.ax.grid(linestyle='--')

            self.ax.plot()
            # self.line1 = self.ax.plot(x='area', y='time')
            self.canvas.draw()

    def plot_all(self, path, key):
        self.ax.clear()
        self.isCanvasClear = False
        self.data_csv = self.d["_csv_"]


        list = path
        a = []
        def_path = []
        reg_path = ""
        static_path = ""

        for i in list:

            a = a + i
        for j in a:
            if self.default in j or "default.csv" in j or "log.csv" in j:
                j = j.split("/")
                if j[-2].endswith("_static"):
                    j = "/".join(j)
                    static_path = j

        static = static_start(static_path)
        path = path
        key = key.split(",")[0]
        time = []
        if not path:
            self.plot()
        else:
            data_file = []
            runtime_area = []
            with open(path, "r") as file:
                for line in file:
                    data_file.append(line)
            runtime_area = analyze_data(data_file, [key])
            str_prev = ""
            d_list = [],[]
            seznam = []
            Blade_sum = []
            CPU0 = []
            CPU1 = []
            DDR_ABC = []
            DDR_DEF = []
            DDR_GHJ = []
            DDR_KLM = []
            MEZZA = []
            for line in data_file:
                if "#" in line and "summary" in line:
                    d_list[0].append(line)
                    str_prev = line
                    tmp_list = []
                elif key in line and "summary" in str_prev:
                    d_list[1].append(float(line.split(",")[1].split("\n")[0]))

                    if "blade" in str_prev:
                        Blade_sum.append(float(line.split(",")[1].split("\n")[0]))
                    elif "CPU0" in str_prev:
                        CPU0.append(float(line.split(",")[1].split("\n")[0]))
                    elif "CPU1" in str_prev:
                        CPU1.append(float(line.split(",")[1].split("\n")[0]))
                    elif "DDR_ABC" in str_prev:
                        DDR_ABC.append(float(line.split(",")[1].split("\n")[0]))
                    elif "DDR_DEF" in str_prev:
                        DDR_DEF.append(float(line.split(",")[1].split("\n")[0]))
                    elif "DDR_GHJ" in str_prev:
                        DDR_GHJ.append(float(line.split(",")[1].split("\n")[0]))
                    elif "DDR_KLM" in str_prev:
                        DDR_KLM.append(float(line.split(",")[1].split("\n")[0]))
                    elif "MEZZA" in str_prev:
                        MEZZA.append(float(line.split(",")[1].split("\n")[0]))



            start = []
            static = static_start(static_path)
            time = analyze_data_3(data_file)
            for i in time:
                t = i - static
                start.append(float(t))

            if self.sw:
                if self.plotType:
                    self.typeButton.setText('Scatter plot')
                    self.ax.plot(start, MEZZA)
                    self.ax.plot(start, DDR_KLM)
                    self.ax.plot(start, DDR_GHJ)
                    self.ax.plot(start, DDR_DEF)
                    self.ax.plot(start, DDR_ABC)
                    self.ax.plot(start, CPU0)
                    self.ax.plot(start, CPU1)
                else:
                    self.typeButton.setText('Line plot')
                    self.ax.plot(start, MEZZA, 'o')
                    self.ax.plot(start, DDR_KLM, 'o')
                    self.ax.plot(start, DDR_GHJ, 'o')
                    self.ax.plot(start, DDR_DEF, 'o')
                    self.ax.plot(start, DDR_ABC, 'o')
                    self.ax.plot(start, CPU0, 'o')
                    self.ax.plot(start, CPU1, 'o')

            else:
                if self.plotType:
                    self.typeButton.setText('Scatter plot')
                    self.ax.plot(start, MEZZA)
                    self.ax.plot(start, DDR_KLM)
                    self.ax.plot(start, DDR_GHJ)
                    self.ax.plot(start, DDR_DEF)
                    self.ax.plot(start, DDR_ABC)
                    self.ax.plot(start, CPU0)
                    self.ax.plot(start, CPU1)
                else:
                    self.typeButton.setText('Line plot')
                    self.ax.plot(start, MEZZA, 'o')
                    self.ax.plot(start, DDR_KLM, 'o')
                    self.ax.plot(start, DDR_GHJ, 'o')
                    self.ax.plot(start, DDR_DEF, 'o')
                    self.ax.plot(start, DDR_ABC, 'o')
                    self.ax.plot(start, CPU0, 'o')
                    self.ax.plot(start, CPU1, 'o')

            self.ax.legend()




            self.ax.set_ylabel(key)
            self.ax.set_xlabel("Time [s]")

            self.ax.plot()
            # self.line1 = self.ax.plot(x='area', y='time')
            self.canvas.draw()

    def plot_all_nova(self, path, key, id):
        self.ax.clear()
        self.isCanvasClear = False
        self.data_csv = self.d["_csv_"]

        list = path
        a = []
        def_path = []
        reg_path = ""
        static_path = ""


        reg = str(self.combo_reg.currentText())
        for j in list:
            if self.default in j or "default.csv" in j or "log.csv" in j:
                k = j.split("/")
                if k[-2].endswith("_static"):
                    #j = "/".join(j)
                    static_path = j
                if reg in k[-2]:
                    file_name = j

        static = static_start(static_path)
        path = path
        key = key.split(",")[0]
        time = []
        if not path:
            self.plot()
        else:
            data_file = []
            runtime_area = []
            with open(file_name, "r") as file:
                for line in file:
                    data_file.append(line)
            runtime_area = analyze_data(data_file, [key])
            str_prev = ""
            d_list = [], []
            seznam = []
            Blade_sum = []
            CPU0 = []
            CPU1 = []
            DDR_ABC = []
            DDR_DEF = []
            DDR_GHJ = []
            DDR_KLM = []
            MEZZA = []
            list_value = []
            time_val_list = []
            for line in data_file:
                if "#" in line and "CALLTREE" in line and id:
                   tmp = line

                elif "Function start timestamp" in line and "CALLTREE" in tmp and id in tmp:
                    time_val = float(line.split(",")[1].strip("\n"))

                elif "(" in line and "CALLTREE" in tmp and id in tmp:
                    tmp_find = line
                    res = re.search(r"\(([A-Za-z0-9_]+)\)", line)
                    result = res.group(1)
                elif id in tmp and key in line and result in tmp_find:
                    line = line.split(",")
                    d_list[0].append(line[1].strip("\n"))
                    d_list[1].append(result)
                    list_value.append(line[1].strip("\n"))
                    time_val_list.append(time_val)
                    tmp_find = ""

            d_list = sorted(d_list)
            d_list.sort()
            lista = sorted(list_value)
            start = []
            static = static_start(static_path)

            time = analyze_data_3(data_file)
            for i in time_val_list:
                t = i - static
                start.append(float(t))

            if self.sw:
                if self.plotType:
                    self.typeButton.setText('Scatter plot')
                    self.ax.plot(start, list_value)

                else:
                    self.typeButton.setText('Line plot')
                    self.ax.plot(start, list_value, 'o')


            else:
                if self.plotType:
                    self.typeButton.setText('Scatter plot')
                    self.ax.plot(start, list_value)

                else:
                    self.typeButton.setText('Line plot')
                    self.ax.plot(start, list_value, 'o')


            self.ax.legend()

            self.ax.set_ylabel(key)
            self.ax.set_xlabel("Time [s]")

            self.ax.plot()
            self.canvas.draw()

    # function of a universal graph, according to the selected label in the plotType combobox
    def plot_universal_1(self, path, key, id):
        self.ax.clear()
        self.isCanvasClear = False
        id = id

        def_path = []
        reg_path = ""
        static_path = ""


        reg = str(self.combo_reg.currentText())
        for j in path:
            if self.default in j or "default.csv" in j or "log.csv" in j:
                k = j.split("/")
                if "_static" in j:
                    static_path = j
                if k[-2].endswith("_static"):
                    k = "/".join(k)
                    static_path = k
                if reg in j:
                    file_name = j
                else:
                    self.plot()
            else:
                self.plot()

        static = static_start(static_path)
        path = path
        key = key

        time = []
        if not path:
            self.plot()
        else:
            data_file = []

            with open(file_name, "r") as file:
                for line in file:
                    data_file.append(line)
            runtime_area = analyze_data_for_plot(data_file, key, id)
            start = analyze_data_runtime_timestamp(data_file, id)
            data = []

            for j in start:
                t = j[1] - static
                t2 = j[0] + j[1] - static
                # a = j[1]
                # b = j[0] + j[1]
                time.append(float(t))
                time.append(float(t2))
                time.append(np.nan)
            for z in runtime_area:
                data.append(z)
                data.append(z)
                data.append(np.nan)

            self.numMultiplier = float(self.mult.text())

            if self.sw:
                if self.plotType:
                    self.typeButton.setText('Line plot')
                    self.ax.plot(time, data, 'o')
                    #self.ax.plot(time, data)
                else:
                    # self.ax.plot(time, data, 'o')
                    self.typeButton.setText('Scatter plot')
                    self.ax.plot(time, data)

            else:
                if self.plotType:
                    self.typeButton.setText('Line plot')
                    self.ax.plot(time, data, 'o')
                    #self.ax.plot(time, data)
                else:
                    # self.ax.plot(time, data, 'o')
                    self.typeButton.setText('Scatter plot')
                    self.ax.plot(time, data)


            self.ax.set_ylabel(key)
            self.ax.set_xlabel("Time [s]")

            self.ax.tick_params(labelsize=11)
            self.ax.set_title(key)
            self.ax.grid(linestyle='--')
            self.ax.plot()
            # self.line1 = self.ax.plot(x='area', y='time')
            self.canvas.draw()

    # function of a universal graph, according to the selected label in the plotType combobox
    # it is a universal plotting of start stop key
    def plot_universal_start_stop(self, path, key):
        self.ax.clear()
        self.isCanvasClear = False
        self.data_csv = self.d["_csv_"]
        list = path
        a = []
        def_path = []
        reg_path = ""
        static_path = ""

        # for i in list:
        #     a = a + i
        for j in list:
            if self.default in j or "default.csv" in j or "log.csv" in j:
                j = j.split("/")
                if j[-2].endswith("_static"):
                    j = "/".join(j)
                    static_path = j
                    #print(j)
                # static_path = j
            else:
                self.plot()
        static = static_start(static_path)
        path = path
        key = key
        time = []
        if not path:
            self.plot()
        else:
            data_file = []
            with open(path, "r") as file:
                for line in file:
                    data_file.append(line)
            runtime_area = analyze_data_for_plot(data_file, key, self.id)
            start = analyze_data_runtime_timestamp(data_file, self.id)

            data = []

            for j in start:
                t = j[1] - static
                t2 = j[0] + j[1] - static
                # a = j[1]
                # b = j[0] + j[1]
                time.append(float(t))
                time.append(float(t2))
                time.append(np.nan)
            for z in runtime_area:
                s = z[0]
                k = z[1]
                data.append(s)
                data.append(k)
                data.append(np.nan)

            self.numMultiplier = float(self.mult.text())
   
            if self.sw:
                if self.plotType:
                    self.ax.plot(time, data)
                else:
                    self.ax.plot(time, data, 'o')

            else:
                if self.plotType:
                    self.ax.plot(time, data)
                else:
                    self.ax.plot(time, data, 'o')

            self.ax.set_ylabel(key)
            self.ax.set_xlabel("Time [s]")

            self.ax.tick_params(labelsize=11)
            self.ax.set_title(key)

            self.ax.grid(linestyle='--')

            self.ax.plot()
            # self.line1 = self.ax.plot(x='area', y='time')
            self.canvas.draw()



    # function that adds into the combobox the data found in the file
    def combo_add_universal(self):
        self.data_csv = self.d["_csv_"]
        list = self.data_csv
        a = []
        def_path = ""


        for i in list:
            a = a + i
        for i in a:
            j = i.split("/")
            if (j[-1] == self.default or "default.csv" in j[-1] or "log.csv" in j[-1]) and "static" in j[-2]:
                def_path = str(i)
        data_file = []

        combo_data_all = []
        data_for_combo_null_one = [[], []]
        data_for_combo_start_stop = []
        data_all_in_file = []
        with open(def_path, "r") as file:
            for line in file:
                data_file.append(line)
        tmp = ""
        str_prev = ""
        id_list = []
        boolen_calltree = False
        for line in data_file:
            if "# " in line and "CALLTREE" in line:
                tmp_find = line

                boolen_calltree = True
                id_ex = line.strip("\n")
                id_ex = id_ex.split(";")[1]
                id_ex = int(id_ex.split("_")[1])
                if not id_ex in id_list:
                    id_list.append(id_ex)
            if "(" in line and boolen_calltree:
                tmp_find = line
                res = re.search(r"\(([A-Za-z0-9_]+)\)", line)
                    # res = str(re.findall('\(.*?\)', str_prev))
                    # print(res.group(1))
                result = res.group(1)

            if "[" in line and "(" in tmp_find and boolen_calltree:
                tmp = line.split(",")[0] + "," + result #+ "," + evolve
                data_all_in_file.append(tmp)
                tmp = ""
                combo_data_all.append(line.split(",")[0].strip("\n"))


        self.id_max = max(id_list)
        self.id_min = min(id_list)

        rus = []
        data_for_combo_plot = []
        for i in combo_data_all:
            if i not in rus:
                #a = i+",ALL"
                rus.append(i)
        list=[]
        for i in rus:
            if i not in list:
                a = i+",ALL"
                data_for_combo_plot.append(a)

        for i in data_all_in_file:
            if i not in data_for_combo_plot:
                data_for_combo_plot.append(i)

        return data_for_combo_plot

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window(1)
    main.show()

    sys.exit(app.exec_())

# automatic opening of LBM_DEF/LBM_DEF/TEST_DEF/d2q37-bench_static/36.csv
# returns the first timestamp, which is then used in further functions

def static_start(file_name):
    file_name = file_name

    static_data = []
    with open(file_name, "r") as file:
        for line in file:
            static_data.append(line)
    runtime_area = []
    for line in static_data:
        if "timestamp" in line:
            runtime_area.append(float(line.split(",")[1].split("\n")[0]))
    static_first = runtime_area[0]
    # print(static_first)
    return static_first


# universal function that, based on input parameters, returns the specified keywords 
# (for example (cpu1) energy con)
def analyze_data_for_plot(data, key, id):
    id = id
    key_a = key.split(",")
    if len(key_a) > 2:
        evolve = key_a[-1].strip("\n")

    if "START" in key_a[0] or "STOP" in key_a[0]:
        runtime_area = [[], []]
        neorez = key_a[0]
        find_key_start = ""
        find_key_stop = ""
        if "START" in neorez:
            orez = neorez.split("START")[1]
            find_key_start = "START"+orez
            find_key_stop = "STOP" + orez
        elif "STOP" in neorez:
            orez = neorez.split("STOP")[1]
            find_key_start = "START" + orez
            find_key_stop = "STOP" + orez
        tmp = ""
        str_prev = ""
        for line in data:
            if key_a[1] in line:
                str_prev = line
            elif find_key_start in line and key_a[1] in str_prev:
                blade = float(line.split(",")[1])
                runtime_area[0].append(float(line.split(",")[1]))
                tmp = str_prev
                str_prev = ""
            elif find_key_stop in line and key_a[1] in tmp:
                runtime_area[1].append(float(line.split(",")[1]))
            else:
                tmp = ""
                str_prev = ""

    else:
        runtime_area = []
        orez = key_a[0]
        str_prev = ""
        tmp_calltree = ""
        for line in data:
            if id in line:
                tmp_calltree = line

            if key_a[1] in line and id in tmp_calltree:
                str_prev = line

            if key_a[0] in line and key_a[1] in str_prev:
                blade = float(line.split(",")[1])
                runtime_area.append(float(line.split(",")[1]))

                str_prev = ""
                tmp_calltree = ""
            if "# COUNTERS" in line:
                tmp_calltree = ""

    return runtime_area










def plot_type(text):
    text = text

    return text

def open_static_36():
    static_data = []
    pwd = os.getcwd()
    file_name = "/home/hynek/SGS18-READEX/LBM_DEF/LBM_DEF/TEST_DEF/d2q37-bench_static/36.csv"
    #file_name = pwd + "/../LBM_DEF/LBM_DEF/TEST_DEF/d2q37-bench_static/36.csv"
    with open(file_name, "r") as file:
        for line in file:
            static_data.append(line)
    runtime_area = []
    for line in static_data:
        if "timestamp" in line:
            runtime_area.append(float(line.split(",")[1].split("\n")[0]))
    static_first = runtime_area[0]
    return  static_first

# automatic opening of DATA/LBMok+/d2q37-bench_meric_static/1200000000_1200000000_12.csv
# returns the first timestamp, which is then used in further functions
def open_static_12():
    static_data = []
    pwd = os.getcwd()
    #file_name = pwd + "/../DATA/LBMok+/d2q37-bench_meric_static/1200000000_1200000000_12.csv"
    file_name = "/home/hynek/SGS18-READEX/DATA/LBMok+/d2q37-bench_meric_static/1200000000_1200000000_12.csv"
    with open(file_name, "r") as file:
        for line in file:
            static_data.append(line)
    runtime_area = []
    for line in static_data:
        if "timestamp" in line:
            runtime_area.append(float(line.split(",")[1].split("\n")[0]))
    static_first = runtime_area[0]
    return  static_first

# automatic opening of the static file chosen by the user by entering the path as an input parameter
# returns the first timestamp, which is then used in further functions

def open_static_gui(file_name):
    static_data = []
    with open(file_name, "r") as file:
        for line in file:
            static_data.append(line)
    runtime_area = []
    for line in static_data:
        if "timestamp" in line:
            runtime_area.append(float(line.split(",")[1].split("\n")[0]))
    static_first = runtime_area[0]
    return  static_first

# Automatic opening of a static file chosen by the user 
# by entering the path during the runtime of this function
# Returns the first timestamp, which is then used in the following functions

def open_static_gui_terminal():
    static_data = []
    print("zadej cestu ke statiku ")
    file_name = input()
    with open(file_name, "r") as file:
        for line in file:
            static_data.append(line)
    runtime_area = []
    for line in static_data:
        if "timestamp" in line:
            runtime_area.append(float(line.split(",")[1].split("\n")[0]))

    static_first = runtime_area[0]
    return  static_first

# Automatic opening of all files located in the directory 
# /../LBM_DEF/LBM_DEF/TEST_DEF/*/36.csv with the name 36.csv
# Can be replaced by automatic_open_file_gui, where the user can choose a new path
# Returns the selected file stored in data_file (list)
def automatic_open_files():
    data_file = []
    pwd = os.getcwd()

    cesta = (glob.glob(pwd + "/../LBM_DEF/LBM_DEF/TEST_DEF/*/36.csv"))
    for i in cesta:
       with open(i, "r") as file:
            for line in file:
                data_file.append(line)

    return data_file

# Automatic opening of all files located in the given directory,  
# the user can choose whether to use the default path or enter a new one  
# Returns the selected file stored in data_file (list)  
# This function is not used anywhere, but it is a possible replacement for automatic_open_files

def automatic_open_file_gui():
    data_file = []
    # upravit cestu
    pwd = os.getcwd()


    menuinput = int(input())
    if menuinput == 1:
        cesta = (glob.glob(pwd + "/../LBM_DEF/LBM_DEF/TEST_DEF/*/36.csv"))

    elif menuinput == 2:
        pathinput = input()
        cesta = (glob.glob(pathinput))
    else:
        cesta = (glob.glob(pwd + "/../LBM_DEF/LBM_DEF/TEST_DEF/*/36.csv"))
    for i in cesta:
        with open(i, "r") as file:
            for line in file:
                data_file.append(line)

    return data_file

# Graph of runtime from the selected region
# Input parameter is the path and the name of the region

def analyze_runtime_area_graph(file_name: str, name):
    data_area_graph = get_data_from_file(file_name)
    runtime_area = analyze_data(data_area_graph, ["Runtime"])

    fig = plt.figure()
    fig.suptitle('graf runtime '+name, fontsize=20)
    plt.ylabel('doba trvání', fontsize=16)
    plt.plot(runtime_area,'o')
    plt.show()
    d = {'Runtime': runtime_area}
    return d

# Graph of runtime from the selected region
# The user selects in a dialog window which file to use

def analyze_runtime_area_graph_gui_input():
    data = get_data_from_file_window()
    runtime_area = analyze_data(data, ["Runtime"])

    fig = plt.figure()
    fig.suptitle('graf runtime ', fontsize=20)
    plt.ylabel('doba trvání [s]   y', fontsize=16)
    plt.xlabel('x', fontsize=16)
    plt.plot(runtime_area,'o')
    plt.show()

# Graph of CPU temperature PKG0 and PKG1 in a single region
def termp():
    start=open_static_36()
    data = get_data_from_file_window()
    runtime_area = analyze_data_runtime_timestamp(data)
    #term_PKG_all = analyze_data_term(data)
    term_PKG_all = [[], []]
    for line in data:
        if "START_TEMP_PKG_0" in line:
            term_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
        if "STOP_TEMP_PKG_0" in line:
            term_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
        if "START_TEMP_PKG_1" in line:
            term_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))
        if "STOP_TEMP_PKG_1" in line:
            term_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))

    term_PKG_all[0] = term_PKG_all[0][:len(term_PKG_all[1])]

    term_PKG_all = [[term_PKG_all[0][i], term_PKG_all[1][i]] for i in range(len(term_PKG_all[0]))]

    pokus = []


    for i in runtime_area:
        a = i[1]-start
        b = i[0] + i[1]-start
        pokus.append(float(a))
        pokus.append(float(b))


    term_PKG0 = []
    term_PKG1 = []

    for i in term_PKG_all:
        a = i[0]
        b = i[1]
        term_PKG0.append(float(a))
        term_PKG1.append(float(b))



    d = { 'Cas': pokus, 'TEMP_PKG_0': term_PKG0,'TEMP_PKG_1':term_PKG1}
    df = pd.DataFrame(d)
    pd.set_option("display.max.columns", None)
    pd.set_option('float_format', '{:f}'.format)
    df.head()
    df.head()
    ax =plt.gca()
    df.plot(x ='Cas', y='TEMP_PKG_0', ax=ax)
    df.plot(x='Cas', y='TEMP_PKG_1', color='red', ax=ax)
    plt.ylabel('TEMP_PKG[C]', fontsize=16)
    plt.xlabel('Time [s]', fontsize=16)
    plt.suptitle('graf Teploty procesoru TEMP_PKG_', fontsize=20)
    plt.show()


# Graph of average CPU frequency in a single region
def frequency():
    start = open_static_36()
    data=get_data_from_file_window()
    runtime_area = analyze_data_runtime_timestamp(data)

    term_list0 = [[],[]]

    freq_PKG_all = analyze_data_freq(data)

    start_stop = []

    for i in runtime_area:

        a = i[1] - start
        b = i[0] + i[1] -start
        start_stop.append(float(a))
        start_stop.append(float(b))

    freq_PKG0 =[]
    freq_PKG1 =[]

    for i in freq_PKG_all:
        a = i[0]
        b = i[1]
        freq_PKG0.append(float(a))
        freq_PKG0.append(float(a))
        freq_PKG1.append(float(b))
        freq_PKG1.append(float(b))



    d = { 'Cas': start_stop, 'CPU_UNCORE_FREQ_0': freq_PKG0,'CPU_UNCORE_FREQ_1':freq_PKG1}
    df = pd.DataFrame(d)
    pd.set_option("display.max.columns", None)
    pd.set_option('float_format', '{:f}'.format)
    df.head()
    df.head()
    ax =plt.gca()
    df.plot(x ='Cas', y='CPU_UNCORE_FREQ_0', ax=ax)
    df.plot(x='Cas', y='CPU_UNCORE_FREQ_1', color='red', ax=ax)
    plt.ylabel('CPU_UNCORE_FREQ [GHz]', fontsize=16)
    plt.xlabel('TIME [s]', fontsize=16)
    plt.suptitle('graph CPU_UNCORE_FREQ', fontsize=20)
    plt.show()

# Text output of the start (timestamp), application runtime, and calculated end  
# The input parameter is the file path and the name of the region

def text_vypis(file_name: str):
    data_area = []
    with open(file_name, "r") as file:
        for line in file:
            data_area.append(line)
    runtime_area = analyze_data_runtime_timestamp(data_area)


# Text output of the start (timestamp), application runtime, and calculated end  
# The user selects in a dialog window which file to use
def text_vypis_gui_input():

    data_area = get_data_from_file_window()
    runtime_area = analyze_data_runtime_timestamp(data_area)

# Universal function that returns the specified keywords (e.g., Runtime) 
# based on the input parameters
def analyze_data(data, keywords):
    runtime_area = []
    for line in data:
        for keyword in keywords:
            if keyword in line:
                runtime_area.append(float(line.split(",")[1]))
    return runtime_area


# Function that iterates through already loaded and stored data from the file,  
# extracts the runtime, and returns the runtime
def analyze_data_2(data_file):
    runtime_area = []
    for line in data_file:
        if "Runtime" in line:
            runtime_area.append(float(line.split(",")[1]))
    return runtime_area

# Function that iterates through already loaded and stored data from the file,  
# extracts the timestamp, and returns the timestamp
def analyze_data_3(data_file):
    runtime_area = []
    for line in data_file:
        if "timestamp" in line:
            runtime_area.append(float(line.split(",")[1]))
    return runtime_area

# Function that iterates through already loaded and stored data from the file,  
# extracts the timestamp and runtime, and returns both timestamp and runtime
def analyze_data_runtime_timestamp(data_file, id):
    runtime = [[], []]
    #id = "init_0;"

    id = str(id)

    for line in data_file:

        if "CALLTREE" in line:
            tmp = ""
            a = line.split(";")
            for i in a:
                if i == id:
                    tmp = i
        if "Runtime" in line and id in tmp:
            runtime[0].append(float(line.split(",")[1].split("\n")[0]))
        if "timestamp" in line and id in tmp:
            runtime[1].append(float(line.split(",")[1].split("\n")[0]))
            tmp = ""
        if "# COUNTERS" in line:
            tmp = ""
    runtime[0] = runtime[0][:len(runtime[1])]

    runtime = [[runtime[0][i], runtime[1][i]] for i in range(len(runtime[0]))]

    return runtime


# Function that opens a file specified by the user based on the input parameters (path)  
# Returns data_file containing the selected file

def get_data_from_file(file_name):
    data_file = []
    with open(file_name, "r") as file:
        for line in file:
            data_file.append(line)
    return data_file

# Function that analyzes already stored data provided through the input parameter  
# Returns the start and end of the application runtime
def analyze_data_start_stop(data_file):
    runtime_area = [[], []]
    for line in data_file:
        if "Runtime" in line:
            runtime_area[0].append(float(line.split(",")[1].split("\n")[0]))
        if "timestamp" in line:
            runtime_area[1].append(float(line.split(",")[1].split("\n")[0]))

    runtime_area[0] = runtime_area[0][:len(runtime_area[1])]

    runtime_area = [[runtime_area[0][i], runtime_area[1][i]] for i in range(len(runtime_area[0]))]
    start_stop = [[],[]]
    for i in runtime_area:
        a = i[1]
        b = i[0] + i[1]
        start_stop.append(float(a))
        start_stop.append(float(b))

    return start_stop

# Function that analyzes already stored data provided through the input parameter  
# Returns CPU_UNCORE_FREQ_1 and CPU_UNCORE_FREQ_0 in a single list called freq_PKG_all  
# (data are preprocessed for graphs)

def analyze_data_freq(data_file):
    freq_PKG_all = [[], []]
    for line in data_file:
            if "CPU_UNCORE_FREQ_0" in line:
                freq_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
            if "CPU_UNCORE_FREQ_1" in line:
                freq_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))

    freq_PKG_all[0] = freq_PKG_all[0][:len(freq_PKG_all[1])]

    freq_PKG_all = [[freq_PKG_all[0][i], freq_PKG_all[1][i]] for i in range(len(freq_PKG_all[0]))]

    return freq_PKG_all

# Function that analyzes already stored data provided through the input parameter  
# Returns START_TEMP_PKG_0 and STOP_TEMP_PKG_0, START_TEMP_PKG_1 and STOP_TEMP_PKG_1  
# in a single list called term_PKG_all (data are preprocessed for graphs)
def analyze_data_term(data_file):
    term_PKG_all = [[], []]
    for line in data_file:

        if "START_TEMP_PKG_0" in line:
            term_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
        if "STOP_TEMP_PKG_0" in line:
            term_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
        if "START_TEMP_PKG_1" in line:
            term_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))
        if "STOP_TEMP_PKG_1" in line:
            term_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))

        term_PKG_all[0] = term_PKG_all[0][:len(term_PKG_all[1])]

        term_PKG_all = [[term_PKG_all[0][i], term_PKG_all[1][i]] for i in range(len(term_PKG_all[0]))]

        return term_PKG_all

# Graph of CPU temperature PKG0 and PKG1 across all regions  
# The input parameter of the function is the paths to the files

def graph_term_all(files):

    start = open_static_36()
    data_term_PKG0 = []
    data_term_PKG1 = []
    time = []

    for file in files:
        data = get_data_from_file(file)
        runtime_area = analyze_data_runtime_timestamp(data)
        term_PKG_all = [[], []]
        for line in data:
            if "START_TEMP_PKG_0" in line:
                term_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
            if "STOP_TEMP_PKG_0" in line:
                term_PKG_all[0].append(float(line.split(",")[1].split("\n")[0]))
            if "START_TEMP_PKG_1" in line:
                term_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))
            if "STOP_TEMP_PKG_1" in line:
                term_PKG_all[1].append(float(line.split(",")[1].split("\n")[0]))

        term_PKG_all[0] = term_PKG_all[0][:len(term_PKG_all[1])]

        term_PKG_all = [[term_PKG_all[0][i], term_PKG_all[1][i]] for i in range(len(term_PKG_all[0]))]
        pokus = []
        #start = runtime_area[0][1]
        for i in runtime_area:
            a = i[1] - start
            b = i[0] + i[1] - start
            time.append(float(a))
            time.append(float(b))

        term_PKG0 = []
        term_PKG1 = []

        for i in term_PKG_all:
            a = i[0]
            b = i[1]
            data_term_PKG0.append(float(a))
            data_term_PKG1.append(float(b))


    d = { 'Cas': time, 'TEMP_PKG_0': data_term_PKG0,'TEMP_PKG_1':data_term_PKG1}
    df = pd.DataFrame(d)
    df.sort_values(by=['Cas'], inplace=True)
    pd.set_option("display.max.columns", None)
    pd.set_option('float_format', '{:f}'.format)
    ax =plt.gca()
    df.plot(x ='Cas', y='TEMP_PKG_0', ax=ax)
    df.plot(x='Cas', y='TEMP_PKG_1', color='red', ax=ax)
    plt.ylabel('TEMP_PKG[C]', fontsize=16)
    plt.xlabel('Time [s]', fontsize=16)
    plt.suptitle('graf teploty procesoru TEMP_PKG', fontsize=20)
    plt.show()

# Graph of average CPU frequency across all regions
def graph_freq_all():
    start = open_static_36()
    data_term_PKG0 = []
    data_term_PKG1 = []
    time = []
    freq_PKG0 = []
    freq_PKG1 = []

    data = automatic_open_file_gui()
    #data=automatic_open_files()
    runtime_area = analyze_data_runtime_timestamp(data)

    freq_PKG_all = analyze_data_freq(data)

    start_stop = []
    for i in runtime_area:
            a = i[1] - start
            b = i[0] + i[1] - start
            time.append(float(a))
            time.append(float(b))



    for i in freq_PKG_all:
            a = i[0]
            b = i[1]
            freq_PKG0.append(float(a))
            freq_PKG0.append(float(a))
            freq_PKG1.append(float(b))
            freq_PKG1.append(float(b))



    d = {'Cas': time, 'CPU_UNCORE_FREQ_0': freq_PKG0, 'CPU_UNCORE_FREQ_1': freq_PKG1}
    df = pd.DataFrame(d)
    df.sort_values(by=['Cas'], inplace=True)
    pd.set_option("display.max.columns", None)
    pd.set_option('float_format', '{:f}'.format)
    df.head()
    df.head()
    ax = plt.gca()
    df.plot(x='Cas', y='CPU_UNCORE_FREQ_0', ax=ax)
    df.plot(x='Cas', y='CPU_UNCORE_FREQ_1', color='red', ax=ax)
    plt.ylabel('CPU_UNCORE_FREQ [GHz]', fontsize=16)
    plt.xlabel('TIME [s]', fontsize=16)
    plt.suptitle('graph CPU_UNCORE_FREQ', fontsize=20)
    plt.show()
    return df

# Bar chart of the total runtime of all regions  
# The input parameter of the function is the paths to the files

def graph_all(files):
    runtime_sum = []

    for file in files:
        data = get_data_from_file(file)
        runtime = analyze_data_2(data)
        Sum = sum(runtime)
        runtime_sum.append(Sum)

    fig = plt.figure()
    fig.suptitle('graf kumulativní runtime všechny oblasti', fontsize=20)
    plt.ylabel('doba trvání [s]     y ', fontsize=16)
    bars = ('Collide', 'static', 'Init', 'Main', 'Propagate')
    y_pos = np.arange(len(bars))
    plt.bar(y_pos, runtime_sum, color='red')
    plt.xticks(y_pos, bars)
    plt.grid(True)
    plt.show()

# Graph and text output of application calls  
# The graph shows at what time each region was called  
# The graph is outlined in issues #20 on GitHub

def graph_timeline_visualisation(file_name):

    #cesta = (glob.glob(file_name))
    cesta = file_name
    area_number = 0
    data_for_graph = [[], []]
    list_statrt_stop = []
    list_area = []
    #start = open_static_12()
    for i in file_name:
        if ("0_0_0.csv" in i or "default.csv" in i) and i.endswith("_static"):
            static_path = i
    static = static_start(static_path)

    legend = []
    for i in cesta:
        path = os.path.dirname(i)
        folders_name = os.path.basename(path)
        area_number += 1
        data = []
        with open(i, "r") as file:
            for line in file:
                data.append(line)
            runtime_area = analyze_data_runtime_timestamp(data)
        string = ""
        string = str(area_number) + "=" + folders_name

        #tmp = [area_number, folders_name]
        legend.append(string)
            #print(runtime)
        for j in runtime_area:
                #a = j[1] - start
                #b = j[0] + j[1] - start
                a = j[1] - static
                b = j[0] + j[1] - static
                #tmp = [float(a), area_number]
                # tmp1 = [float(a)]
                # list_statrt_stop.append(tmp1)
                # tmp1 = [float(b)]
                # list_statrt_stop.append(tmp1)
                # tmp1 = [np.nan]
                # list_statrt_stop.append(tmp1)
                list_statrt_stop.append(float(a))
                list_statrt_stop.append(float(b))
                list_statrt_stop.append(np.nan)
                # tmp2 = [area_number]
                # list_area.append(tmp2)
                # tmp2 = [area_number]
                # list_area.append(tmp2)
                # tmp2 = [np.nan]
                #list_area.append(tmp2)
                list_area.append(folders_name)
                #data_for_graph.append(tmp)
                tmp = [float(b), area_number]
                list_area.append(folders_name)
                #data_for_graph.append(tmp)
                tmp = [np.nan, np.nan]
                list_area.append("")
                #data_for_graph.append(tmp)

    return  list_statrt_stop, list_area


# This is no longer needed, it is the same function as graph_timeline_visualisation  
# Can be deleted, it was only used for testing

def graph_timeline_visualisation_1():
    start = open_static_12()
    data = []
    pokus = [[], []]

    area_number = 0
    with open("/home/hynek/SGS18-READEX/DATA/LBMok+/d2q37-bench_meric_static/1200000000_1200000000_12.csv", "r") as file:
        for line in file:
            data.append(line)

        area_number += 1

    runtime = [[], []]
    for line in data:
        if "Runtime" in line:
            runtime[0].append(float(line.split(",")[1].split("\n")[0]))
        if "timestamp" in line:
            runtime[1].append(float(line.split(",")[1].split("\n")[0]))

    runtime[0] = runtime[0][:len(runtime[1])]

    runtime = [[runtime[0][i], runtime[1][i]] for i in range(len(runtime[0]))]

    for i in runtime:
        a=i[1] - start
        b=i[0]+i[1] - start
        pokus[0].append(float(a))
        pokus[0].append(float(b))
        pokus[0].append(np.nan)
        pokus[1].append(1)
        pokus[1].append(1)
        pokus[1].append(np.nan)

    pokus[0] = pokus[0][:len(pokus[1])]
    pokus = [[pokus[0][i], pokus[1][i]] for i in range(len(pokus[0]))]


    data2 = []

    with open("/home/hynek/SGS18-READEX/DATA/LBMok+/Collide/1200000000_1200000000_12.csv",
              "r") as file:
        for line in file:
            data2.append(line)

        area_number += 1

    runtime2 = [[], []]
    for line in data2:
        if "Runtime" in line:
            runtime2[0].append(float(line.split(",")[1].split("\n")[0]))
        if "timestamp" in line:
            runtime2[1].append(float(line.split(",")[1].split("\n")[0]))

    runtime2[0] = runtime2[0][:len(runtime2[1])]

    runtime2 = [[runtime2[0][i], runtime2[1][i]] for i in range(len(runtime2[0]))]


    for i in runtime2:
        a = i[1] - start
        b = i[0] + i[1] - start
        tmp = [float(a), area_number]
        pokus.append(tmp)
        tmp = [float(b), area_number]
        pokus.append(tmp)
        tmp = [np.nan, np.nan]
        pokus.append(tmp)



    data3 = []

    with open("/home/hynek/SGS18-READEX/DATA/LBMok+/Init/1200000000_1200000000_12.csv",
              "r") as file:
        for line in file:
            data3.append(line)

        area_number+=1

    runtime3 = [[], []]
    for line in data3:
        if "Runtime" in line:
            runtime3[0].append(float(line.split(",")[1].split("\n")[0]))
        if "timestamp" in line:
            runtime3[1].append(float(line.split(",")[1].split("\n")[0]))

    runtime3[0] = runtime3[0][:len(runtime3[1])]

    runtime3 = [[runtime3[0][i], runtime3[1][i]] for i in range(len(runtime3[0]))]

    for i in runtime3:
        a = i[1] - start
        b = i[0] + i[1] - start
        tmp = [float(a), area_number]
        pokus.append(tmp)
        tmp = [float(b), area_number]
        pokus.append(tmp)
        tmp = [np.nan, np.nan]
        pokus.append(tmp)

    data4 = []

    with open("/home/hynek/SGS18-READEX/DATA/LBMok+/Main/1200000000_1200000000_12.csv",
              "r") as file:
        for line in file:
            data4.append(line)

        area_number+=1

    runtime4 = [[], []]
    for line in data4:
        if "Runtime" in line:
            runtime4[0].append(float(line.split(",")[1].split("\n")[0]))
        if "timestamp" in line:
            runtime4[1].append(float(line.split(",")[1].split("\n")[0]))

    runtime4[0] = runtime4[0][:len(runtime4[1])]

    runtime4 = [[runtime4[0][i], runtime4[1][i]] for i in range(len(runtime4[0]))]


    for i in runtime4:
        a = i[1] - start
        b = i[0] + i[1] - start
        tmp = [float(a), area_number]
        pokus.append(tmp)
        tmp = [float(b), area_number]
        pokus.append(tmp)
        tmp = [np.nan, np.nan]
        pokus.append(tmp)

    data5 = []

    with open("/home/hynek/SGS18-READEX/DATA/LBMok+/Propagate/1200000000_1200000000_12.csv",
              "r") as file:
        for line in file:
            data5.append(line)

        area_number+=1

    runtime5 = [[], []]
    for line in data5:
        if "Runtime" in line:
            runtime5[0].append(float(line.split(",")[1].split("\n")[0]))
        if "timestamp" in line:
            runtime5[1].append(float(line.split(",")[1].split("\n")[0]))

    runtime5[0] = runtime5[0][:len(runtime5[1])]

    runtime5 = [[runtime5[0][i], runtime5[1][i]] for i in range(len(runtime5[0]))]

    for i in runtime5:
        a = i[1] - start
        b = i[0] + i[1] - start
        tmp = [float(a), area_number]
        pokus.append(tmp)
        tmp = [float(b), area_number]
        pokus.append(tmp)
        tmp = [np.nan, np.nan]
        pokus.append(tmp)


    df = pd.DataFrame(pokus,columns=['time', 'area'])
    df.plot(x='time', y='area')
    plt.ylabel('area 1 = Static, 2 = Collide, 3 = Init, 4 = Main, 5 = Propagate ', fontsize=16)
    plt.xlabel('TIME', fontsize=16)
    plt.suptitle('Graph Timeline visualisation', fontsize=20)
    plt.legend(['Runtime'])
    plt.show()
    return pokus

# Example of a gap in pandas and a non-continuous graph  
# Not needed

def mising_data_graph():
    dict = {'time': [1, 2, 3, 4, 5, 6],
            'first': [30, 45, 56, np.nan, 65, 85],
            'second': [10,np.nan, 40, 80, 98, 120]}

    df = pd.DataFrame(dict)
    ax = plt.gca()
    df.plot(x='time', y='first', ax=ax)
    df.plot(x='time', y='second', color='red', ax=ax)
    # plt.ylabel('CPU_UNCORE_FREQ [GHz]', fontsize=16)
    # plt.xlabel('TIME [s]', fontsize=16)
    plt.suptitle('score', fontsize=20)
    plt.show()
    return df


# Not needed, this is a test version of the calltree function where loops were not used  
# Can be deleted

def calltree():
    calltree = []
    job_id =[]
    cesta = (glob.glob("/home/hynek/SGS18-READEX/LBM_DEF/LBM_DEF/TEST_DEF/*/36.csv"))
    #data = automatic_open_files()
    pocet_init = 0
    pocet_static = 0
    pocet_propagate = 0
    pocet_collide = 0
    pocet_init_0 = 0
    pocet_static_0 = 0
    pocet_propagate_0 = 0
    pocet_collide_0 = 0
    init_0 = []
    static_0 = []
    job_static_0 = []
    propagate_0 = []
    job_propagate_0 = []
    collide_0 = []
    collide = []
    job_collide_0 = []
    data_cesta = []
    data1=[]
    data2=[]
    data3=[]
    area = []
    pocet = 0
    with open("/home/hynek/SGS18-READEX/LBM_DEF/LBM_DEF/TEST_DEF/collide/36.csv", "r") as file:
        for line in file:
            data1.append(line)
    str_prev = ""
    for line in data1:
        if "CALLTREE" in line:
            str_prev = line
        if ("Job info" in line or "JOB ID" in line) and "CALLTREE" in str_prev:
            collide_0.append(str_prev.split("CALLTREE;")[1].split("\n")[0])

            str_prev=""


    c = Counter(collide_0)

    with open("/home/hynek/SGS18-READEX/LBM_DEF/LBM_DEF/TEST_DEF/d2q37-bench_static/36.csv", "r") as file:
        for line in file:
            data2.append(line)
    str_prev2 = ""
    for line in data2:
        if "CALLTREE" in line:
            str_prev2 = line
        elif ("Job info" in line or "JOB ID" in line) and "CALLTREE" in str_prev2:
            static_0.append(str_prev2.split("CALLTREE;")[1].split("\n")[0])

            str_prev2=""

    s = Counter(static_0)

    with open("/home/hynek/SGS18-READEX/LBM_DEF/LBM_DEF/TEST_DEF/propagate/36.csv", "r") as file:
        for line in file:
            data3.append(line)
    str_prev3 = ""
    for line in data3:
        if "CALLTREE" in line:
            str_prev3 = line
        elif ("Job info" in line or "JOB ID" in line) and "CALLTREE" in str_prev3:
            propagate_0.append(str_prev3.split("CALLTREE;")[1].split("\n")[0])

            str_prev3 = ""
    p = Counter(propagate_0)

# Calltree output  
# The function returns a pandas table where the first column is the region,  
# the second column is how many times the region was called,  
# and the third column is the configuration
def calltree_met():
    pathinput = input()
    cesta = (glob.glob(pathinput))
    caltree = []

    for i in cesta:
        data = []
        path = os.path.dirname(i)
        folders_name = os.path.basename(path)
        with open(i, "r") as file:
            for line in file:
                data.append(line)

        str_prev = ""
        for line in data:
            if "CALLTREE" in line:
                str_prev = line
            elif ("Job info" in line or "JOB ID" in line) and "CALLTREE" in str_prev:
                a = str_prev.split("CALLTREE;")[1].split("\n")[0]
                b = folders_name
                tmp = [a, b]
                caltree.append(tmp)
                str_prev = ""



    df=pd.DataFrame(caltree,columns=['Calltree', 'area'])
    df = (df.fillna('') \
          .groupby(df.columns.tolist()).apply(len) \
          .rename('group_count') \
          .reset_index() \
          .replace('', np.nan) \
          .sort_values(by=['group_count'], ascending=False))
    df = df[['area','group_count','Calltree']]



def start_menu():

     print("""
     START MENU
     ******************
     stisknutím 1 zvolite ciselne zobrazeni dat podle oblasti
     stisknutím 2 zvolite graficke zobrazeni dat podle oblasti
     stisknutím 3 zvolite graficke zobrazeni vsech dat
     stisknutím 4 zvolite graficke zobrazeni behu aplikace
     stisknutím 5 zvolite zobrazeni teploty procesoru podle oblasti
     stisknutím 6 zvolite zobrazeni průměrné frekvence procesoru podle oblasti
     stisknutím 7 zvolite graficke zobrazeni teploty procesoru za cely beh aplikace
     stisknutím 8 zvolite graficke zobrazeni frekvence procesoru za cely beh aplikace
     stisknutím 9 zvolite zobrazeni Calltree""")
     startmenuinput = int(input())

     if startmenuinput == 1:

         text_vypis_gui_input()
         start_menu()

     elif startmenuinput == 2 :

         analyze_runtime_area_graph_gui_input()
         start_menu()

     elif startmenuinput ==3 :

          pwd=os.getcwd()
          graph_all([pwd+"/../DATA/LBMok+/Collide/1200000000_1200000000_12.csv",
              pwd+"/../DATA/LBMok+/d2q37-bench_meric_static/1200000000_1200000000_12.csv",
              pwd+"/../DATA/LBMok+/Init/1200000000_1200000000_12.csv",
              pwd+"/../DATA/LBMok+/Main/1200000000_1200000000_12.csv",
              pwd+"/../DATA/LBMok+/Propagate/1200000000_1200000000_12.csv"])
          start_menu()

     elif startmenuinput == 4:

         pwd = os.getcwd()
         graph_timeline_visualisation(pwd+"/../DATA/LBMok+/*/1200000000_1200000000_12.csv")
         start_menu()

     elif startmenuinput == 5 :

         termp()
         start_menu()

     elif startmenuinput == 6 :

         frequency()
         start_menu()

     elif startmenuinput == 7:

        pwd=os.getcwd()
        graph_term_all([pwd+"/../LBM_DEF/LBM_DEF/TEST_DEF/collide/36.csv",
                        pwd+"/../LBM_DEF/LBM_DEF/TEST_DEF/d2q37-bench_static/36.csv",
                        pwd+"/../LBM_DEF/LBM_DEF/TEST_DEF/propagate/36.csv"])

     elif startmenuinput == 8:

        graph_freq_all()
        start_menu()

     elif startmenuinput == 9:
        calltree_met()
        start_menu()


     else:

         print("musis zvolit neco v rozsahu")
         start_menu()

#start_menu()



# The functions are tested on data /../DATA/LBMok+/*/1200000000_1200000000_12.csv 
# and /../LBM_DEF/LBM_DEF/TEST_DEF/*/36.csv  
# That is why some functions contain open_static_36or12. If needed, these functions 
# can be replaced with universal functions, see the following two lines:  
# open_static_gui("/home/hynek/SGS18-READEX/DATA/LBMok+/d2q37-bench_meric_static/1200000000_1200000000_12.csv")  
# open_static_gui_terminal()  
# A similar example to open_static_36or12 is automatic_open_files, which can be repl
