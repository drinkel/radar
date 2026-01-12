#!/usr/bin/env python3
import sys
from PyQt6 import QtGui, QtCore, QtWidgets
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from packaging import version
if version.parse(matplotlib.__version__) < version.parse("2.0.3"):
        raise Exception("Matplotlib version must be >= 2.0.3, while yours is {}!".format(matplotlib.__version__))
from matplotlib import pyplot as pp
pp.switch_backend('QtAgg')
from matplotlib import image as mpimg
from matplotlib import patches as mp
import os

try:
	import pydot
except Exception as e:
	sys.path.append(os.getcwd()+"/src/modules")
	import pydot

from src import pyyed_tree
from runpy import run_path
import pprint

ppr = pprint.PrettyPrinter(indent=4)


class regionTree(QtWidgets.QDialog):
    sendInfo = QtCore.pyqtSignal(object)
    def __init__(self, pathToData, ownData = None, defaultDPI='300', addButtonIncluded = True, parent=None):
        super(regionTree, self).__init__(parent)

        self.d = ownData
        # a figure instance to plot on
        self.setWindowTitle("Region structure")
        self.figure = Figure()
        self.ax = self.figure.add_axes([0.15,0.15,0.68,0.75])   # left,bottom edge, width, height
        self.G = None

        self.canvas = FigureCanvas(self.figure)
        self.path = pathToData

        self.button_png = QtWidgets.QPushButton('Export to PNG')
        self.button_pdf = QtWidgets.QPushButton('Export to PDF')
        self.button_yed = QtWidgets.QPushButton('Export to yEd')
        self.label_dpi = QtWidgets.QLabel('Set DPI (max. 1200):')
        self.label_dpi.setFont(QtGui.QFont("Arial",13,QtGui.QFont.Bold))
        self.dpi_edit = QtWidgets.QLineEdit(defaultDPI)
        self.dpi_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.dpi_edit.setMaxLength(4)
        self.dpi_edit.setFont(QtGui.QFont("Arial",13))
        self.dpi_edit.setValidator(QtGui.QIntValidator(50,1200))
        self.dpi_edit.setMinimumWidth(250)
        self.dpi_edit.setMaximumWidth(500)

        self.dpi_edit.textChanged.connect(self.plot_tree)
        self.button_yed.clicked.connect(self.yEd_export)
        self.button_png.clicked.connect(self.png_export)
        self.button_pdf.clicked.connect(self.pdf_export)
        self.addButton = QtWidgets.QPushButton('Add to LaTeX report')
        self.addButton.clicked.connect(self.emitTeXInfo)

        self.resize(900,600)

        self.hl = QtWidgets.QHBoxLayout()
        self.hl.addWidget(self.label_dpi)
        self.hl.addWidget(self.dpi_edit)
        self.hl2 = QtWidgets.QHBoxLayout()
        self.hl2.addWidget(self.button_png)
        self.hl2.addWidget(self.button_pdf)
        self.hl2.addWidget(self.button_yed)
        if addButtonIncluded:
            self.hl2.addWidget(self.addButton)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.hl)
        self.layout.addWidget(self.canvas)
        self.layout.addLayout(self.hl2)
        self.setLayout(self.layout)

        self.make_reg_structure()

    def emitTeXInfo(self):
        currDPI = self.dpi_edit.text()
        self.sendInfo.emit({'dpi': currDPI})
        self.addButton.setEnabled(False)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Current image was added to LaTeX report.")
        msg.setWindowTitle("LaTeX file created")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.buttonClicked.connect(msg.close)
        msg.exec_()

    def png_export(self):
        dlg = QtWidgets.QFileDialog()
        self.save_file_path = str(dlg.getSaveFileName(filter='Portable Network Graphics (*.png)')[0])

        if self.save_file_path and not self.save_file_path.endswith('.png'):
            self.save_file_path = self.save_file_path + '.png'
        if self.save_file_path:
            self.G.write_png(self.save_file_path)

    def pdf_export(self):
        dlg = QtWidgets.QFileDialog()
        self.save_file_path = str(dlg.getSaveFileName(filter='Portable Document format (*.pdf)')[0])

        if self.save_file_path and not self.save_file_path.endswith('.pdf'):
            self.save_file_path = self.save_file_path + '.pdf'
        if self.save_file_path:
            self.G.write_pdf(self.save_file_path)

    def yEd_export(self):
        timeYN = QtWidgets.QMessageBox.question(self, 'Time included?', 'Do you want to include time information within nodes?', QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        dlg = QtWidgets.QFileDialog()
        self.save_file_path = str(dlg.getSaveFileName(filter='yEd graphs (*.graphml)')[0])

        if self.save_file_path and not self.save_file_path.endswith('.graphml'):
            self.save_file_path = self.save_file_path + '.graphml'
        if self.save_file_path:
            if timeYN == QtWidgets.QMessageBox.Yes:
                pyyed_tree.browse_dir(self.path, ownData = self.d, destFilePath = self.save_file_path, givenRegStruct = self.reg_structure, givenRegTimes = self.reg_times, timeIncl = True)
            else:
                pyyed_tree.browse_dir(self.path, ownData = self.d, destFilePath = self.save_file_path, givenRegStruct = self.reg_structure, givenRegTimes = self.reg_times, timeIncl = False)


    def make_reg_structure(self):
        D = self.d["all_nested_funcs_dic"]

        self.chs_regs = list(D.keys())

        i = 0
        self.main_reg = None
        self.reg_structure = {}
        self.reg_times = {}

        for subdir, dirs, files in os.walk(self.path):
            if not i:
                i += 1
                continue

            call_list = []

            with open('{}/{}'.format(subdir,files[0])) as f:
                for line in f:
                    line = line.strip()
                    line2 = line.split(';')
                    if line.startswith('# CALLTREE'):
                        tmp = line2[-1].rsplit('_',1)[0]
                        if tmp not in call_list and tmp != 'init':
                            call_list.append(tmp)
                        if self.main_reg is None and line.endswith('init_0'):
                            self.main_reg = subdir.split('/')[-1]
                    if 'Runtime of function' in line or 'Average runtime of function' in line and subdir.split('/')[-1]\
                            not in self.reg_times.keys():
                        tmp2 = float(line.split(',')[-1])
                        self.reg_times[subdir.split('/')[-1]] = tmp2

            self.reg_structure[subdir.split('/')[-1]] = call_list

        removed_value = self.reg_structure.pop('samples', 'No Key found')
        self.plot_tree()

    def build_pydot(self):
        given_dpi = self.dpi_edit.text()
        self.G = pydot.Dot(graph_type='digraph',dpi=given_dpi)
        for k in self.reg_structure.keys():
            if k == self.main_reg:
                n = pydot.Node("{0}\n{1:.4f} s".format(k,self.reg_times[k]), style = "filled", fillcolor = '#ccaaff', shape = 'ellipse')
            else:
                if k in self.chs_regs:
                    n = pydot.Node("{0}\n{1:.4f} s".format(k,self.reg_times[k]), style = 'filled', fillcolor = '#fff000', shape = 'rectangle')
                else:
                    n = pydot.Node("{0}\n{1:.4f} s".format(k,self.reg_times[k]), style = 'filled', fillcolor = '#d5e4f5', shape = 'rectangle')
            self.G.add_node(n)

        for k,v in self.reg_structure.items():
            for e in v:
                self.G.add_edge(pydot.Edge("{0}\n{1:.4f} s".format(e,self.reg_times[e]),"{0}\n{1:.4f} s".format(k,self.reg_times[k]), arrowsize = 0.5))

    def plot_tree(self):
        self.build_pydot()
        matplotlib.rcParams['toolbar'] = 'None'
        #matplotlib.rcParams['figure.dpi'] = given_dpi

        self.G.write_png(os.path.abspath('.tmpImage.png'))
        tree_img = mpimg.imread(os.path.abspath('.tmpImage.png'))

        uselp = mp.Patch(color = '#d5e4f5', label = 'Unselected regions')
        selp = mp.Patch(color = '#fff000', label = 'Selected regions')
        mainp = mp.Patch(color = '#ccaaff', label = 'Main region')

        self.ax.imshow(tree_img)
        self.ax.legend(handles = [selp,uselp,mainp],loc="upper left",bbox_to_anchor=(0,1.1),fontsize = 'small')

        self.ax.axis('off')
        #pp.show()
        self.canvas.draw()
        self.addButton.setEnabled(True)


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = regionTree(pathToData = '/home/david/SGS18-READEX/DATA/KRIPKE')
    main.show()

    sys.exit(app.exec_())

