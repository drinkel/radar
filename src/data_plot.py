#!/usr/bin/env python3
import sys
from PyQt6 import QtGui, QtCore, QtWidgets
import time
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


warnings.filterwarnings('ignore', category=matplotlib.MatplotlibDeprecationWarning)

pp = pprint.PrettyPrinter(indent=4)

class Window(QtWidgets.QDialog):
    sendInfo = QtCore.pyqtSignal(object)
    def __init__(self, ownData = None, parent=None):
        super(Window, self).__init__(parent)

        
        # a figure instance to plot on
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)

        
        
        self.sw = False
        self.use_logscaleX = False
        self.use_logscaleY = False
        self.setWindowTitle("Plot")

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
        self.mult.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.mult.setValidator(QtGui.QDoubleValidator())

        # data loading, we can have more than one y_data! TODO

        self.d = ownData


        self.data = self.d["plot_summary_data"]

        self.combo_reg = QtWidgets.QComboBox(self)
        self.combo_reg.addItem('Overall summary')
        #TODO - multiple measurements handling (2 in range is ad hoc)
        if "nested_regions_report_data" in self.d.keys():
            for i in range(0,len(self.d["nested_regions_report_data"])):
                comboItem = "REGION - {}".format(self.d["nested_regions_report_data"][i]["nested_region"])
                if comboItem not in [self.combo_reg.itemText(i) for i in range(self.combo_reg.count())]:
                    self.combo_reg.addItem(comboItem)

        if len(self.data) > 1:
            self.combo = QtWidgets.QComboBox(self)
            for i in range(0,len(self.data)):
                self.combo.addItem("{}, {}".format(self.data[i][0]["category"],self.data[i][0]["arg"]))

        # set the layout
        layout = QtWidgets.QVBoxLayout()

        self.plot_data = self.data[0]
        self.keyList = list(self.plot_data[1]["key"])
        for i in range(0,len(self.keyList)):
            self.keyList[i] = self.keyList[i].replace(';',' ')

        self.lab_reg = QtWidgets.QLabel('Choose Area: ')
        self.lab_reg.setFont(self.bf)
        hl_reg = QtWidgets.QHBoxLayout()
        hl_reg.addWidget(self.lab_reg)
        hl_reg.addWidget(self.combo_reg)

        self.combo.activated.connect(lambda index: self.chooseData(self.combo.itemText(index)))
        layout.addLayout(hl_reg)

        if len(self.data) > 1:
            self.label = QtWidgets.QLabel('Choose quantity: ')
            self.label.setFont(self.bf)
            hl = QtWidgets.QHBoxLayout()
            hl.addWidget(self.label)
            hl.addWidget(self.combo)
            self.combo.activated.connect(lambda index: self.chooseData(self.combo.itemText(index)))
            layout.addLayout(hl)


        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.button2)
        hlayout.addWidget(self.maxBox)
        hlayout.addWidget(self.logscaleX)
        hlayout.addWidget(self.logscaleY)
        layout.addLayout(hlayout)
        hlayout3 = QtWidgets.QHBoxLayout()
        hlayout3.addWidget(self.typeButton)
        hlayout3.addWidget(self.button4)
        hlayout3.addWidget(self.addButton)


        layout.addLayout(hlayout3)


        self.setLayout(layout)
       
        self.resizeEvent = self.onResize

        self.plot()
        
        

    def changeType(self):
        self.plotType = not self.plotType
        if self.plotType:
            self.typeButton.setText('Line plot')
        else:
            self.typeButton.setText('Scatter plot ')
        self.plot()

    def emitTeXInfo(self):
        if str(self.combo_reg.currentText()) == "Overall summary":
            reg = list(self.d['config']['main_reg'][0].keys())[0]
        else:
            reg = str(self.combo_reg.currentText())[9:]
        for i in range(len(self.data)):
            if self.data[i][0]['arg'] in str(self.combo.currentText()):
                q = self.data[i][0]['arg']
                c = self.data[i][0]['category']
        self.sendInfo.emit({'quantity': q, 'category': c, 'region': reg, 'multiplier': float(self.mult.text()), 'switched': self.sw, 'dot': self.plotType})
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
        #save_file_path = "/home/david/SGS18-READEX/graf.tex"
        target_file = '/'.join(save_file_path.split('/')[0:-1])+'/readex_header.tex'
        copyfile(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/input/readex_header.tex',target_file)

        tex_file = open(save_file_path,"w")
        tex_file.write(r'\documentclass{article}')
        tex_file.write(r'''\n\input{readex_header}\n''')
        tex_file.write(r'\begin{document}')

        title = '{}, {}'.format(str(self.combo_reg.currentText()),str(self.combo.currentText()))
        x_lab = r"{}\,[{}{}]".format(self.plot_data[1]["x_label_name"], '' if self.numMultiplier.is_integer() and int(self.numMultiplier) == 1 else 1/self.numMultiplier,
                                    self.plot_data[1]["x_label_unit"])
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

        for i in range(0,self.n):
            code = (r'''\addplot+ [mark=triangle*{}] coordinates {{ {}
                     }};
                     '''.format(',only marks' if only_marks else '', '\n'.join([str((self.numMultiplier*e[a],e[b])) for e in self.K[i]])))
            tex_file.write(code)

        legend_title = r'\hspace{{-.6cm}} {} '.format("{} [{}]".format(self.plot_data[1]["func_label_name"],self.plot_data[1]["func_label_unit"]))

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
        title_angle = title_angle = 210 if self.optx > 0.5*(min(self.ky)+max(self.ky)) else 330
        title_distance = 2
        optim_title = 'optimal settings are {}: {} {}, {}: {} {}'.format(self.plot_data[1]["x_label_name"],self.optx,self.plot_data[1]["x_label_unit"],
                                                                    self.plot_data[1]["func_label_name"],self.optf,self.plot_data[1]["func_label_unit"])
        optim_code = optim_code.format(self.ymin if self.sw else self.numMultiplier*self.optx, self.numMultiplier*self.optx if self.sw else self.ymin,
                           optim_title,
                           title_angle, title_distance)

        tex_file.write(optim_code)
        tex_file.write(r'\n\end{axis}\n\end{tikzpicture}\n\end{adjustbox}\n\n\end{document}')

        tex_file.close()

    def chooseReg(self, dataLabel):
        if dataLabel == "Overall summary":
            self.data = self.d["plot_summary_data"]
        else:
            for i in range(0,len(self.d["nested_regions_report_data"])):
                tmp = "REGION - {}".format(self.d["nested_regions_report_data"][i]["nested_region"])
                if dataLabel == tmp:
                    self.data = self.d["nested_regions_report_data"][i]["plot_data"]
        self.plot_data = self.data[0]
        if len(self.data) > 1:
            for i in range(0,len(self.data)):
                if str(self.combo.currentText()) == "{}, {}".format(self.data[i][0]["category"],self.data[i][0]["arg"]):
                    self.plot_data = self.data[i]
        self.keyList = list(self.plot_data[1]['key'])
        for i in range(0,len(self.keyList)):
            self.keyList[i] = self.keyList[i].replace(';',' ')
        self.plot()
        return dataLabel


    def chooseData(self, dataLabel):
        for i in range(0,len(self.data)):
            if dataLabel == "{}, {}".format(self.data[i][0]["category"],self.data[i][0]["arg"]):
                self.plot_data = self.data[i]
        self.plot()
        '''p = self.grab()
        print(p)
        p.save('/home/david/SGS18-READEX/plotGUI.png')'''


    def change_sw(self):
        self.sw = not self.sw
        self.plot()

    def change_logscaleX(self):
        self.use_logscaleX = not self.use_logscaleX
        self.plot()

    def change_logscaleY(self):
        self.use_logscaleY = not self.use_logscaleY
        self.plot()
        
    def onResize(self, event):
        
        self.figure.tight_layout()
        
        self.canvas.draw()



    def plot(self):
        self.ax.clear()
        self.ax.set

        self.isCanvasClear = False


        if self.mult.text() in ["e","."] or "," in self.mult.text() or self.mult.text().endswith('e') or self.mult.text().startswith('e'):
            self.numMultiplier = 1.0
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Wrong multiplier format!\nPlease write the multiplier in form AeB (e.g. 1e-4).")
            msg.setWindowTitle("Invalid multiplier")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            self.mult.setText("1")
        elif not float(self.mult.text()):
            self.numMultiplier = 1.0
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('Multiplier should be a positive number!\nPlease choose non-zero multiplier.')
            msg.setWindowTitle("Invalid multiplier")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            self.mult.setText("1")
        else:
            self.numMultiplier = float(self.mult.text())

        self.k = list(self.plot_data[1]["lines"])


        self.keyStr = ""

        for i in range(len(self.keyList)):
            if i == 0:
                self.keyStr = ", key: "
            self.keyStr = self.keyStr + self.keyList[i]
            if i < len(self.keyList)-1:
                self.keyStr = self.keyStr + ", "


        self.K = self.plot_data[1]["heat_data"]
        self.ky = [h[0] for h in self.K[0]] ### pole s uncore frekvencemi
        self.n = len(self.k)
        self.optx = self.plot_data[1]["optim_x_val"]
        self.optf = self.plot_data[1]["optim_func_label_value"]
        self.ymin = min([y[1] for y in self.K[0]])
        ymax = 0

        for i in range(0,len(self.K)):
            for j in range(0,len(self.K[i])):
                tmp = list(self.K[i][j])
                tmp[0] = self.numMultiplier*tmp[0]
                self.K[i][j] = tuple(tmp)


        self.funcmax = 0
        colors = pl.cm.jet(np.linspace(0, 1, self.n))


        for m in range(0,self.n):
            X = [x[0] for x in self.K[m]]
            x = X[0]
            
            Y = [x[1] for x in self.K[m]]
            y = Y[0]
            
            hasDefault = 0
            for x in range(0, len(self.K[m])):
                one = self.K[m][x]
                if (one[0] == 0.0):
                    hasDefault = 1

            if self.use_logscaleX:
                self.ax.set_xscale('log')

            if self.use_logscaleY:
                self.ax.set_yscale('log')

            if (hasDefault):
                if (len(X) != 1): ###test
                    X.pop(0)
                if (len(Y) != 1): ###test
                    Y.pop(0)
            

            xmin = min(X)
            xmax = max(X)
            xm = max(X)
            ymin0 = min(Y)
            ymax0 = max(Y)
            self.avx = 0.5*(xmin+xmax)


            if self.ymin > ymin0:
                self.ymin = ymin0
            for idx,it in enumerate(Y):
                if it == ymax0 and it > ymax:
                    ymax = ymax0
                    xmax = X[idx]
                    self.funcmax = self.k[m]



            # axis conversion from scientific notation to float

            for i in range(0, len(X)):
                if (str(X[i]) != "0.0"):
                    X[i] = X[i] / 1000000000


            # Axes
            if (str(self.k[m]) != "0.0"):
                labelval = float(self.k[m]) / 1000000000 # Hz to GHz, if Hz needed, change all labelval for self.k[m]

            else:
                labelval = float(0.0)
            if self.sw: #s witched
                if self.plotType: # scatter
                    self.ax.plot(Y, X, 'o', label=labelval, color=colors[m])
                    if(hasDefault):
                        valstring = str(self.k[m])
                        if (valstring == "0.0"):
                            self.ax.axvline(x=y, ymin=0.04, ymax=0.96, label="def CF, def UnCF", color=colors[m])
                        else:
                            self.ax.axvline(x=y, ymin=0.04, ymax=0.96, label=str(labelval) + ", def " + str(self.plot_data[1]["x_label_name"]), color=colors[m])
                else: # line
                    self.ax.plot(Y, X, label=labelval, color=colors[m])
                    if(hasDefault):
                        valstring = str(self.k[m])
                        if (valstring == "0.0"):
                            self.ax.axvline(x=y, ymin=0.04, ymax=0.96, linestyle='--', color=colors[m], label="def CF, def UnCF")
                        else:
                            self.ax.axvline(x=y, ymin=0.04, ymax=0.96, linestyle='--', color=colors[m], label=str(labelval) + ", def " + str(self.plot_data[1]["x_label_name"]))
            else: # not switched
                if self.plotType: # scatter
                    self.ax.plot(X, Y, 'o', label=labelval, color=colors[m])
                    if(hasDefault):
                        valstring = str(self.k[m])
                        if (valstring == "0.0"):
                            self.ax.axhline(y=y, xmin=0.04, xmax=0.96, label="def CF, def UnCF", color=colors[m])
                        else:
                            self.ax.axhline(y=y, xmin=0.04, xmax=0.96, label=str(labelval) + ", def " + str(self.plot_data[1]["x_label_name"]), color=colors[m])
                else: # line
                    self.ax.plot(X, Y, label=labelval, color=colors[m])
                    if(hasDefault):
                        valstring = str(self.k[m])
                        if (valstring == "0.0"):
                            self.ax.axhline(y=y, xmin=0.04, xmax=0.96, linestyle='--', label="def CF, def UnCF", color=colors[m])
                        else:
                            self.ax.axhline(y=y, xmin=0.04, xmax=0.96, linestyle='--', label=str(labelval) + ", def " + str(self.plot_data[1]["x_label_name"]), color=colors[m])
                               

        # plot structure
        self.xlab = "{} [{}{}]".format(self.plot_data[1]["x_label_name"],'' if self.numMultiplier == 1 else 1/self.numMultiplier,self.plot_data[1]["x_label_unit"])
        self.ylab = self.plot_data[0]["arg"]

        if self.maxBox.isChecked():
            optStr = 'optimal settings are {}: {} {}, {}: {} {}{}\nMaximum value is at settings {}: {} {}, {}: {} {}'.format(self.plot_data[1]["x_label_name"],
                                                                                                        self.optx,self.plot_data[1]["x_label_unit"],
                                                                                                        self.plot_data[1]["func_label_name"],
                                                                                                        self.optf,self.plot_data[1]["func_label_unit"],self.keyStr,
                                                                                                        self.plot_data[1]["x_label_name"],xmax,self.plot_data[1]["x_label_unit"],
                                                                                                        self.plot_data[1]["func_label_name"],
                                                                                                        self.funcmax,self.plot_data[1]["func_label_unit"])
        else:
            optStr = 'optimal settings are {}: {} {}, {}: {} {}{}'.format(self.plot_data[1]["x_label_name"],
                                                                self.optx,self.plot_data[1]["x_label_unit"],
                                                                self.plot_data[1]["func_label_name"],
                                                                self.optf,self.plot_data[1]["func_label_unit"],self.keyStr)
        self.ax.set_title(optStr)

        if self.sw:
            self.ax.set_ylabel(self.xlab, fontsize = 13)
            self.ax.set_xlabel(self.ylab, fontsize = 13)
        else:
            self.ax.set_xlabel(self.xlab, fontsize = 13)
            self.ax.set_ylabel(self.ylab, fontsize = 13)

        self.ax.tick_params(labelsize = 11)
        self.ax.grid(linestyle = '--')

        handles, labels = self.ax.get_legend_handles_labels()

        lgd = self.ax.legend(handles,labels,loc=2,bbox_to_anchor=(1.015,1.025),ncol=1, borderaxespad = 0.,prop={'size': 11})
        lgd.set_title("{}\n[{}]".format(self.plot_data[1]["func_label_name"],self.plot_data[1]["func_label_unit"]))


        for i in range(0,len(self.K)):
            for j in range(0,len(self.K[i])):
                tmp = list(self.K[i][j])
                tmp[0] = 1/self.numMultiplier*tmp[0]

                self.K[i][j] = tuple(tmp)
        



        # Size of plot (inches)
        self.figure.set_figheight(7)
        self.figure.set_figwidth(7)
        self.canvas.draw()
        self.addButton.setEnabled(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window(1)
    main.show()

    sys.exit(app.exec_())
