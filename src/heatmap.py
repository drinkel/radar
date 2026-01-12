#!/usr/bin/env python3
import sys
import copy
import matplotlib
from packaging import version
if version.parse(matplotlib.__version__) < version.parse("2.0.3"):
	raise Exception("Matplotlib version must be >= 2.0.3, while yours is {}!".format(matplotlib.__version__))

from PyQt6 import QtGui, QtCore, QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as pp

pp.switch_backend('QtAgg')
import matplotlib.pyplot as mat
import numpy as np
import matplotlib.colors as mpc
import matplotlib as mpl
from runpy import run_path
import seaborn as sb; sb.set()
import textwrap
import os
from src import csv_vals_edit
from shutil import copyfile
import pprint

from typing import Tuple
import numpy as np
import matplotlib.colors as mpc

pp = pprint.PrettyPrinter(indent=4)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)




def radar_color(value: float, vmin: float, vmax: float) -> Tuple[int, int, int]:
    if vmax <= vmin:
        return (255, 255, 51)  # yellow

    t = (value - vmin) / (vmax - vmin)
    if t < 0.0: t = 0.0
    if t > 1.0: t = 1.0

    G0 = (0.0,   204.0, 0.0)   # green
    Y  = (255.0, 255.0, 51.0)  # yellow
    Rf = (255.0,  51.0, 51.0)  # red

    if t <= 0.5:
        u = t / 0.5
        r = G0[0] + (Y[0] - G0[0]) * u
        g = G0[1] + (Y[1] - G0[1]) * u
        b = G0[2] + (Y[2] - G0[2]) * u
    else:
        u = (t - 0.5) / 0.5
        r = Y[0] + (Rf[0] - Y[0]) * u
        g = Y[1] + (Rf[1] - Y[1]) * u
        b = Y[2] + (Rf[2] - Y[2]) * u

    return (int(round(r)), int(round(g)), int(round(b)))

# Creates 256-color palette of same size as previous colormap.txt file
palette = np.array([radar_color(i, 0, 255) for i in range(256)], dtype=float) / 255.0
cm = mpc.ListedColormap(palette)

class Window(QtWidgets.QDialog):
    sendInfo = QtCore.pyqtSignal(object)
    def __init__(self, main_menu_instance, ownData = None, parent = None, radar_data = False):
        super(Window, self).__init__(parent)

        self.main_menu_instance = main_menu_instance
        self.d = ownData
        self.D = ownData["plot_summary_data"]

        self.setWindowTitle("Heatmap")
        self.radar_data = radar_data
        self.switch_axis = False
        self.bf = QtGui.QFont("Arial", 10, QtGui.QFont.Weight.Bold)

        self.nf = QtGui.QFont("Arial",10)

        self.switch_unit = True # switch unit of axes Hz/GHz


        self.button2 = QtWidgets.QPushButton('Switch axes')
        self.button2.setFont(self.nf)
        self.plotType = 0
        self.button2.clicked.connect(self.change_sw)
        self.button3 = QtWidgets.QPushButton('Generate LaTeX code')
        self.button3.clicked.connect(self.getTeX)
        self.buttonMult = QtWidgets.QPushButton('Apply multiplier')
        self.buttonMult.clicked.connect(self.draw_heatmap)
        self.addButton = QtWidgets.QPushButton('Add to LaTeX report')
        self.addButton.clicked.connect(self.emitTeXInfo)
        self.buttonUnit = QtWidgets.QPushButton('Axes to Hz')
        self.buttonUnit.setFont(self.nf)
        self.buttonUnit.clicked.connect(self.change_axis_unit)
        self.button4 = QtWidgets.QPushButton('Export to CSV')
        self.button4.setFont(self.nf)
        self.button4.clicked.connect(self.getCsv)
        self.nDecimals = QtWidgets.QSpinBox()
        self.nDecimals.setValue(3)
        self.nDecimals.setMinimum(0)
        self.nDecimals.setMaximum(12)
        self.nDecimals.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.nDecimals.setFont(self.nf)

        self.mult = QtWidgets.QLineEdit('1')
        self.mult.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.mult.setFont(self.nf)
        self.doubleValid = QtGui.QDoubleValidator(0.000000001,1000000.0,6)
        self.mult.setValidator(self.doubleValid)
        self.multLab = QtWidgets.QLabel('Set multiplier')
        self.multLab.setFont(self.bf)
        self.unitLab = QtWidgets.QLabel('Current unit: {}'.format(self.D[0][0]["unit"]))
        self.unitLab.setFont(self.nf)

        self.combo_reg = QtWidgets.QComboBox(self)
        self.combo_reg.addItem('Overall summary')
        # TODO - multiple measurements handling (2 in range is ad hoc)
        if "nested_regions_report_data" in self.d.keys():
            for i in range(0,len(self.d["nested_regions_report_data"])):
                comboItem = "REGION - {}".format(self.d["nested_regions_report_data"][i]["nested_region"])
                if comboItem not in [self.combo_reg.itemText(i) for i in range(self.combo_reg.count())]:
                    self.combo_reg.addItem(comboItem)

        if len(self.D) >= 1:
            self.combo = QtWidgets.QComboBox(self)
            for i in range(0,len(self.D)):
                self.combo.addItem("{}, {}".format(self.D[i][0]["category"],self.D[i][0]["arg"]))

        # set the layout
        self.layout = QtWidgets.QVBoxLayout()

        self.plot_data = self.D[0]
        self.keyList = self.plot_data[1]["key"]

        self.gl = QtWidgets.QGridLayout()

        self.lab_reg = QtWidgets.QLabel('Choose Area: ')
        self.lab_reg.setFont(self.bf)
        hl_reg = QtWidgets.QHBoxLayout()
        hl_reg.addWidget(self.lab_reg)
        hl_reg.addWidget(self.combo_reg)
        hl_reg.addWidget(self.button2)
        hl_reg.addWidget(self.buttonUnit)

        self.combo_reg.activated.connect(self.chooseReg) #PYQT6
        self.gl.addWidget(self.lab_reg,0,0)
        self.gl.addWidget(self.combo_reg,0,1)
        self.gl.addWidget(self.button2,0,2)

        self.tmp_idx = 1

        self.label = QtWidgets.QLabel('Choose quantity: ')
        self.label.setFont(self.bf)
        self.gl.addWidget(self.label,self.tmp_idx,0)
        self.gl.addWidget(self.combo,self.tmp_idx,1)

        self.combo.activated.connect(self.chooseData) #PYQT6
        self.tmp_idx = self.tmp_idx+1
        self.nDecimals.valueChanged.connect(self.draw_heatmap)

        # Getting xLabel values (frequencies)
        self.heat_data = self.plot_data[1]["heat_data"]
        self.xlabel= list(self.plot_data[1]["lines"])
        self.len_xlabel= len(self.xlabel)

        # Getting funcLabel values (frequencies)
        self.funclabel = []
        for i in range(self.len_xlabel):
            for j in range(len(self.heat_data[i])):
                if not self.heat_data[i][j][0] in self.funclabel:
                    self.funclabel.append(self.heat_data[i][j][0])
        self.len_funclabel = len(self.funclabel)

        # Cell font size based on number of columns and rows
        if self.len_xlabel> 20 or self.len_funclabel > 20:
            self.cell_font_size = 8
        elif self.len_xlabel> 13 or self.len_funclabel > 13:
            self.cell_font_size = 9
        elif self.len_xlabel> 7 or self.len_funclabel > 7:
            self.cell_font_size = 12
        else:
            self.cell_font_size = 16

        self.figwidth =  14
        self.figheight = 10
        self.figure = Figure(figsize=(self.figwidth, self.figheight))
        self.figure.tight_layout(pad=2.2)

        self.figure.set_size_inches(15, 15)

        # Changing the size of cells, [left_margin, bottom_margin, cell_width, cell_height]
        # Offset of axes from sides + size of cells
        self.ax = self.figure.add_axes([0.11, 0.05, 0.85, 0.8])

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.h2 = QtWidgets.QHBoxLayout()
        self.l1 = QtWidgets.QLabel("Clicked cell info: ")
        self.l1.setFont(self.bf)
        self.l2 = QtWidgets.QLabel("Clicked cell value: ")
        self.l2.setFont(self.bf)
        self.l3 = QtWidgets.QLabel()
        self.l3.setFont(self.nf)
        self.l4 = QtWidgets.QLabel()
        self.l4.setFont(self.nf)

        self.h2.addWidget(self.l1)
        self.h2.addWidget(self.l3)
        self.h2.addWidget(self.l2)
        self.h2.addWidget(self.l4)

        self.nDecLabel = QtWidgets.QLabel('Number of decimals:')
        self.nDecLabel.setFont(self.bf)
        self.keyLab = QtWidgets.QLabel("Key:")
        self.keyLab.setFont(self.bf)
        self.keyLabVal = QtWidgets.QLabel(" ")
        self.keyLabVal.setFont(self.nf)

        self.gl.addWidget(self.nDecLabel,self.tmp_idx,0)
        self.gl.addWidget(self.nDecimals,self.tmp_idx,1)
        self.gl.addWidget(self.multLab,self.tmp_idx+1,0)
        self.gl.addWidget(self.mult,self.tmp_idx+1,1)
        self.gl.addWidget(self.buttonMult,self.tmp_idx+1,2)
        self.gl.addWidget(self.unitLab,self.tmp_idx+2,2)
        self.gl.addWidget(self.keyLab,self.tmp_idx+2,0)
        self.gl.addWidget(self.keyLabVal,self.tmp_idx+2,1)
        self.gl.addWidget(self.buttonUnit, self.tmp_idx+2, 2)
        self.gl.setVerticalSpacing(5)
        self.gl.setHorizontalSpacing(50)

        self.layout.addLayout(self.gl)
        self.layout.addWidget(self.canvas)
        self.layout.addLayout(self.h2)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.button3)
        self.layout.addWidget(self.addButton)
        self.layout.addWidget(self.button4)
        self.setLayout(self.layout)


        self.draw_heatmap()







    def emitTeXInfo(self):
        if str(self.combo_reg.currentText()) == "Overall summary":
            reg = list(self.d['config']['main_reg'][0].keys())[0]
        else:
            reg = str(self.combo_reg.currentText())[9:]

        for i in range(len(self.D)):
            if self.D[i][0]['arg'] in str(self.combo.currentText()):
                q = self.D[i][0]['arg']
                c = self.D[i][0]['category']
        self.sendInfo.emit({'quantity': q, 'category': c, 'region': reg, 'multiplier': self.numMult, 'decimals': self.nD, 'switched': self.switch_axis})
        self.addButton.setEnabled(False)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Current heatmap was added to LaTeX report.")
        msg.setWindowTitle("LaTeX report info")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.buttonClicked.connect(msg.close)
        msg.exec()

    def getCsv(self):
         form = "{:." + str(self.nD)+"f}"
         dlg = QtWidgets.QFileDialog()
         save_file_path = str(dlg.getSaveFileName(filter='CSV file (*.csv)')[0])
         if save_file_path and not save_file_path.endswith('.csv'):
             save_file_path = save_file_path + '.csv'
         if not save_file_path:
             return 0
         target_file = '/'.join(save_file_path.split('/')[0:-1])+'/heatmap.csv'
         input_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

         csv_file = open(save_file_path, "w")

         if not self.switch_axis:
             csv_file.write("X-axis: ")
             csv_file.write(str(self.plot_data[1]["func_label_name"]))
             csv_file.write(" [")
             csv_file.write(str(self.plot_data[1]["func_label_unit"]))
             csv_file.write("]")
             csv_file.write(", Y-axis: ")
             csv_file.write(str(self.plot_data[1]["x_label_name"], ))
             csv_file.write(" [")
             csv_file.write(str(self.plot_data[1]["x_label_unit"]))
             csv_file.write("]")
             csv_file.write(str('\n'))

             # write top line of csv table
             csv_file.write(";")
             for x in self.xlabel:
                 csv_file.write(str(x))
                 csv_file.write(';')
             csv_file.write('\n')

            # write other lines
             for i in range(0, self.len_funclabel):
                  for x in range(0, self.len_xlabel):
                      if (x == 0):
                          csv_file.write(str(self.funclabel[i]))
                          csv_file.write(str(';'))
                      if (np.isnan(self.data[i][x]) == False):
                          # csv_file.write(str(self.numMult * self.data[i][x]))
                          val = str(form.format(self.numMult * self.data[i][x]))
                          csv_file.write(val)
                      csv_file.write(';')
                  csv_file.write('\n')
         else:
             csv_file.write("X-axis: ")
             csv_file.write(str(self.plot_data[1]["x_label_name"]))
             csv_file.write(" [")
             csv_file.write(str(self.plot_data[1]["x_label_unit"]))
             csv_file.write("]")
             csv_file.write(", Y-axis: ")
             csv_file.write(str(self.plot_data[1]["func_label_name"], ))
             csv_file.write(" [")
             csv_file.write(str(self.plot_data[1]["func_label_unit"]))
             csv_file.write("]")
             csv_file.write(str('\n'))
             csv_file.write("x;")
             for x in self.funclabel:
                 csv_file.write(str(x))
                 csv_file.write(';')
             csv_file.write('\n')

             for i in range(0, self.len_xlabel):
                 for x in range(0, self.len_funclabel):
                     if (x == 0):
                         csv_file.write(str(self.xlabel[i]))
                         csv_file.write(';')
                     if (np.isnan(self.data[x][i]) == False):
                         # csv_file.write(str(self.numMult * self.data[x][i]))
                         val = str(form.format(self.numMult * self.data[x][i]))
                         csv_file.write(val)
                     csv_file.write(';')
                 csv_file.write('\n')
             csv_file.close()
             return 0



    def getTeX(self):
        dlg = QtWidgets.QFileDialog()
        save_file_path = str(dlg.getSaveFileName(filter='LaTeX code (*.tex)')[0])
        if save_file_path and not save_file_path.endswith('.tex'):
            save_file_path = save_file_path + '.tex'

        if not save_file_path:
            return 0
        target_file = '/'.join(save_file_path.split('/')[0:-1]) + '/readex_header.tex'
        copyfile(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/input/readex_header.tex', target_file)
        input_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        x_label_unit = r"{}\,[{}]".format(self.plot_data[1]["x_label_name"], self.plot_data[1]["x_label_unit"])
        func_label_unit = r"{}\,[{}]".format(self.plot_data[1]["func_label_name"], self.plot_data[1]["func_label_unit"])

        tex_file = open(save_file_path, "w")
        tex_file.write(r'\documentclass{article}')
        tex_file.write(r'''\n\input{readex_header}\n''')
        tex_file.write(r'\begin{document}')
        code = r'''
                \begin{{table}}
                \centering
                {0}
                \begin{{adjustbox}}{{max width=\textwidth}}
                \def\tablePrec{{ {1} }}
                \def\labelPrec{{1}}
                \pgfplotstabletypeset[
                    col sep=comma,
                    row sep=\\,
                    color cells={{min={2}, max={3}, textcolor=black}},
                    /pgfplots/colormap={{CM}}{{rgb255=(0,204,0) rgb255=(255,255,51)  rgb255=(255,51,51)}},
                    /pgf/number format/fixed,
                    /pgf/number format/precision=\the\numexpr\tablePrec,
                    columns/xLabels/.style={{
                        column name={{ {4} }},
                        preproc cell content/.style={{
                            /pgf/number format/precision=\the\numexpr\labelPrec
                        }},
                        postproc cell content/.style={{
                            /pgfplots/table/@cell content.add={{\cellcolor{{white}}}}
                        }}
                    }}
                ]
                {{
                {5}\\
                }}
                \end{{adjustbox}}
                \end{{table}}
                '''
        code = textwrap.dedent(code)

        hd2 = []


        for i in range(0, self.len_xlabel):
            hd = [t[1] for t in self.heat_data[i][:]]
            hd2.append(self.numMult * np.asarray(hd))

        


        ### Adding NaN to empty spaces
        # for x in range(0, self.len_xlabel):
        #     dh = []
        #     for i in range(0, len(self.heat_data[x])):
        #         if (self.heat_data[x][i][0] == float(i)+1):
        #             print("ano 0 i:", self.heat_data[x][i][0], float(i))
        #             dh.append(self.heat_data[x][i][0])
        #         else:
        #             print("ne 0 i:", self.heat_data[x][i][0], float(i))
        #             dh.append(float(i))
        #     print("DH ", dh)
        ###



        self.validmatrix = True
        for arr in hd2:
            if (len(hd2[0]) != len(arr)):
                self.validmatrix = False

        if (self.validmatrix):
            if self.switch_axis:
                hd2 = [l for l in np.transpose(hd2)]
                table_header_line = ','.join(['xLabels'] + [str(x) for x in self.funclabel])
                table_data_lines = [','.join([str(e) for e in tup]) for tup in list(zip(*[list(self.xlabel)] + hd2))]
            else:
                table_header_line = ','.join(['xLabels'] + list(self.xlabel))
                table_data_lines = [','.join([str(e) for e in tup]) for tup in list(zip(*[self.funclabel] + hd2))]

            code = code.format(r'\caption{{ {} }}'.format(title) if title != '' else '',
                            self.nDecimals.value(),
                            np.min(np.min(np.asarray(hd2))),
                            np.max(np.max(np.asarray(hd2))),
                            r''
                            if all(e == '' for e in (x_label_unit, func_label_unit))
                            else r'$\frac{{ {} }}{{ {} }}$'.format(x_label_unit if self.switch_axis else func_label_unit, func_label_unit if
                            self.switch_axis else x_label_unit),
                            r'\\ \n'.join([table_header_line] + table_data_lines)
                            )
            tex_file.write(code)
            tex_file.write(r'''\n\end{document}''')
            tex_file.close()
        else:
            print("Not valid matrix resolution")

    def chooseReg(self, dataLabel):
        if dataLabel == "Overall summary":
            self.D = self.d["plot_summary_data"]
        else:
            for i in range(0,len(self.d["nested_regions_report_data"])):
                tmp = "REGION - {}".format(self.d["nested_regions_report_data"][i]["nested_region"])
                if dataLabel == tmp:
                    self.D = self.d["nested_regions_report_data"][i]["plot_data"]
        self.plot_data = self.D[0]
        if len(self.D) > 1:
            for i in range(0,len(self.D)):
                if str(self.combo.currentText()) == "{}, {}".format(self.D[i][0]["category"],self.D[i][0]["arg"]):
                    self.plot_data = self.D[i]
        if dataLabel == "Overall summary":
            self.keyList = self.plot_data[1]["key"]
        else:
            self.keyList = self.plot_data[1]['key']
        self.draw_heatmap()


    def change_sw(self):
        if self.switch_axis == False:
            self.switch_axis = not self.switch_axis
        elif self.switch_axis == True:
            self.switch_axis = not self.switch_axis

        self.draw_heatmap()


    def onclick(self,event):
        # Coordinates from left/top of heatmap
        idx = int(np.floor(event.xdata))
        idy = int(np.floor(event.ydata))

        if not self.switch_axis:
            self.l3.setText("{}: {} {}, {}: {} {}".format(self.plot_data[1]["func_label_name"],list(self.xlabel)[idx],
                                                    self.plot_data[1]["func_label_unit"],self.plot_data[1]["x_label_name"],
                                                    self.funclabel[idy],self.plot_data[1]["x_label_unit"]))
        if self.switch_axis:
            self.l4.setText(str(self.numMult*self.data[idx,idy]))
        else:
            self.l4.setText(str(self.numMult*self.data[idy,idx]))



        if str(self.combo_reg.currentText()) == "Overall summary":
            reg = list(self.d['config']['main_reg'][0].keys())[0]
        else:
            reg = str(self.combo_reg.currentText())[9:]


        # TODO: for editing values in heatmap uncomment this - works with function get_vals_from_csv_NEW
        self.csv_vals_edit_dialog = csv_vals_edit.csv_vals_edit_window(
            reg, 
            self.plot_data[1]["x_label_name"], 
            str(self.funclabel[idy]),
            self.plot_data[1]["func_label_name"], 
            list(self.xlabel)[idx],
            (self.plot_data[0]['category'], 
            self.plot_data[0]['arg']), 
            self.keyList, 
            self.main_menu_instance)
        self.csv_vals_edit_dialog.show()


    def chooseData(self, dataLabel):
        for i in range(0,len(self.D)):
            if dataLabel == "{}, {}".format(self.D[i][0]["category"],self.D[i][0]["arg"]):
                self.plot_data = self.D[i]
                self.unitLab.setText("Current unit: {}{}".format("" if self.numMult.is_integer() and int(self.numMult) == 1 else (1/self.numMult if self.numMult != 0 or self.numMult != "e" else ""), self.plot_data[0]["unit"]))
        self.addButton.setEnabled(True)
        self.draw_heatmap()

    def change_axis_unit(self):
        ### true == GHz, false == Hz
        if (self.switch_unit == True):
            self.switch_unit = False
            self.ax.tick_params(axis = 'x', rotation=15)
            self.buttonUnit.setText("Axes to GHz")
        else:
            self.switch_unit = True
            self.ax.tick_params(axis = 'x', rotation=0)
            self.buttonUnit.setText("Axes to Hz")
        self.draw_heatmap()
        self.figure.tight_layout()

    def draw_heatmap(self):
        
        tick_and_label_font_size = 11

        # Set print options to use decimal notation instead of scientific notation
        np.set_printoptions(suppress=True)

        self.ax.clear()
        self.nD = self.nDecimals.value()

        self.heat_data = self.plot_data[1]["heat_data"]

        # Getting xLabel values
        self.xlabel = list(self.plot_data[1]["lines"])
        self.len_xlabel= len(self.xlabel)


        # Getting funcLabel values
        self.funclabel = []
        for i in range(self.len_xlabel):
            for j in range(len(self.heat_data[i])):
                if not self.heat_data[i][j][0] in self.funclabel:
                    self.funclabel.append(self.heat_data[i][j][0])

        self.len_funclabel = len(self.funclabel)

        self.keyStr = "None"
        for i in range(len(self.keyList)):
            if i == 0:
                self.keyStr = ""
            self.keyStr = self.keyStr + self.keyList[i].replace("\\,", " ")
            if i < len(self.keyList)-1:
                self.keyStr = self.keyStr + ", "

        self.keyLabVal.setText(self.keyStr)

        # Creating numpy object to store heatmap data
        self.data = np.zeros([self.len_funclabel,self.len_xlabel])
        self.ax.clear()
        self.problem = False

        # Formatting data to fit heatmap desired format
        for i in range(0,self.len_xlabel):
            tmp = []
            pointer = 0
            j = 0

            # Passing data from heat_data to tmp[]
            while j < len(self.heat_data[i]):
                if self.funclabel[j+pointer] == self.heat_data[i][j][0]:
                    tmp.append(self.heat_data[i][j][1])
                    j = j + 1
                # Append placeholder value if there is missing value for specific core frequency
                else:
                    tmp.append(np.nan)
                    pointer = pointer + 1
            
            # Append placeholder values if missing
            while len(tmp) != self.len_funclabel:
                tmp.append(np.nan)

            # Placing heat_data values by columns
            self.data[:,i] = tmp

        ### Converting Hz to GHz, ELSE removing decimal part
        if (self.switch_unit):
            for i in range(0, len(self.xlabel)):
                if (str(self.xlabel[i]) != "0.0" and str(self.xlabel[i]) != "default"):
                    self.xlabel[i] = float(self.xlabel[i]) / 1000000000
                    self.xlabel[i] = str(self.xlabel[i])

            for i in range(0, len(self.funclabel)):
                if (str(self.funclabel[i]) != "0.0" and str(self.funclabel[i]) != "default"):
                    self.funclabel[i] = float(self.funclabel[i]) / 1000000000
                    self.funclabel[i] = str(self.funclabel[i])
        else:
            for i in range(0, len(self.xlabel)):
                if (str(self.xlabel[i]) != "0.0" and str(self.xlabel[i]) != "default"):
                    if(self.xlabel[i][-2] == "."):
                        spl = self.xlabel[i].split('.')
                        self.xlabel[i] = spl[0]
            for i in range(0, len(self.funclabel)):
                if (str(self.funclabel[i]) != "0.0" and str(self.funclabel[i]) != "default"):
                    self.funclabel[i] = str(self.funclabel[i])
                    spl = self.funclabel[i].split('.')
                    self.funclabel[i] = spl[0]


        # Shifting axes in case [0.0] core frequency exists
        if 0.0 in self.funclabel:

            # Shifting rows "up" (the highest one will be the lowest one now)
            self.data = np.roll(self.data, -1, axis=0)

            # Renaming [0.0] to default
            self.funclabel.append('default')
            self.funclabel.pop(0)

        if '0.0' in self.xlabel:

            # Shifting columns "left" (the very left one is now on right)
            self.data = np.roll(self.data, -1, axis=1)

            # Renaming [0.0] to default
            self.xlabel.append('default')
            self.xlabel.pop(0)
        if self.len_funclabel == len(self.data):
            self.problem == False

        if self.problem:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Missing value in data!")
            msg.setWindowTitle("Problem")
            msg.setStandardButtons(QtWidgets.QMessageBox.Close)
            msg.buttonClicked.connect(self.close)
            msg.exec()
            return 1
        else:
            cid = self.figure.canvas.mpl_connect('button_press_event', self.onclick)

            if self.mult.text() in ["e","."] or "," in self.mult.text() or self.mult.text().endswith('e') or self.mult.text().startswith('e'):
                self.numMult = 1.0
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText("Wrong multiplier format!\nPlease write the multiplier in form AeB (e.g. 1e-4).")
                msg.setWindowTitle("Invalid multiplier")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec()
                self.mult.setText("1")
            elif not float(self.mult.text()):
                self.numMult = 1.0
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Multiplier should be positive number!\nPlease choose non-zero multiplier.')
                msg.setWindowTitle("Invalid multiplier")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec()
                self.mult.setText("1")
            else:
                self.numMult = float(self.mult.text())

            sb.set_context('talk')

            # If statements for "switch axes"
            if self.switch_axis == False:
                # Creating heatmap
                hm = sb.heatmap(self.numMult*self.data, annot=True, annot_kws = {"size": self.cell_font_size}, fmt=".{}f".format(self.nD), cmap=cm, square=False, cbar=False, ax = self.ax)
                hm.xaxis.tick_top()

                # Setting ticks and their labels
                self.ax.set_xticks([(i+0.5) for i in range(self.len_xlabel)])
                self.ax.set_yticks([(i+0.5) for i in range(self.len_funclabel)])
                self.ax.set_xticklabels([*self.xlabel], fontsize=tick_and_label_font_size)
                self.ax.set_yticklabels([*self.funclabel], fontsize=tick_and_label_font_size)
        
                #self.ax.set_xlabel("{} [{}]".format(self.plot_data[1]["func_label_name"],self.plot_data[1]["func_label_unit"]), fontsize=tick_and_label_font_size)
                self.ax.set_ylabel("{} [{}]".format(self.plot_data[1]["x_label_name"],self.plot_data[1]["x_label_unit"]), fontsize=tick_and_label_font_size)

                title = str(self.plot_data[1]["func_label_name"]) + " [" + str(self.plot_data[1]["func_label_unit"]) + "]"
                self.ax.set_title(title, fontsize=tick_and_label_font_size)


            elif self.switch_axis == True:
                # Creating heatmap
                hm = sb.heatmap(np.transpose(self.numMult*self.data), annot=True, annot_kws = {"size": self.cell_font_size}, fmt=".{}f".format(self.nD), cmap=cm, square=False, cbar=False, ax = self.ax)
                hm.xaxis.tick_top()

                # Setting ticks and their labels
                self.ax.set_xticks([(i+0.5) for i in range(self.len_funclabel)])
                self.ax.set_yticks([(i+0.5) for i in range(self.len_xlabel)])
                self.ax.set_xticklabels([*self.funclabel], fontsize=tick_and_label_font_size)
                self.ax.set_yticklabels([*self.xlabel], fontsize=tick_and_label_font_size)

                self.ax.set_ylabel("{} [{}]".format(self.plot_data[1]["func_label_name"],self.plot_data[1]["func_label_unit"]), fontsize=tick_and_label_font_size)
                #self.ax.set_xlabel("{} [{}]".format(self.plot_data[1]["x_label_name"],self.plot_data[1]["x_label_unit"]), fontsize=tick_and_label_font_size)
                title = str(self.plot_data[1]["x_label_name"]) + " [" + str(self.plot_data[1]["x_label_unit"]) + "]"
                self.ax.set_title(title, fontsize=tick_and_label_font_size)

            # rotation of x axis is configured at change_axis_unit()
            self.ax.tick_params(axis = 'y', rotation=0)

            self.unitLab.setText("Current unit: {}{}".format("" if self.numMult.is_integer() and int(self.numMult) == 1 else (1/self.numMult if self.numMult != 0 or self.numMult != "e" else ""), self.plot_data[0]["unit"]))

            #self.ax.set_position()
            self.canvas.draw()
            self.addButton.setEnabled(True)

            return 0


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec())
