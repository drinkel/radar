#!/usr/bin/env python3
import sys
from PyQt6 import QtWidgets,QtCore, QtGui
from runpy import run_path
import pprint
import os
import textwrap
import numpy as np
from collections import OrderedDict as ordDict
from functools import partial
from shutil import copyfile
import ast
from src import pydot_example
pp = pprint.PrettyPrinter(indent=4)

class Window(QtWidgets.QDialog):
    def __init__(self, ownData = None, infoFromApps = None, parent=None):
        super(Window, self).__init__(parent)

        self.data = ownData

        self.info = infoFromApps

        D = self.data["all_nested_funcs_dic"]
        self.chs_regs = list(D.keys())
        self.resize(800,500)
        self.setWindowTitle("LaTeX dialog")

        self.bf = QtGui.QFont("Arial",14,QtGui.QFont.Bold)
        self.nf = QtGui.QFont("Arial",13)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.headerItem().setText(0, "Choose components of report")
        self.tree.header().setVisible(False)
        self.tree.setFont(self.nf)

        #myform = QtWidgets.QFormLayout()
        #self.nested_regs_list = []

        self.region_tree = QtWidgets.QTreeWidgetItem(self.tree)
        self.region_tree.setText(0, "Region tree")
        self.region_tree.setFlags(self.region_tree.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        self.region_tree.setCheckState(0,QtCore.Qt.Unchecked)

        self.sum_table = QtWidgets.QTreeWidgetItem(self.tree)
        self.sum_table.setText(0, "Overall summary table")
        self.sum_table.setFlags(self.sum_table.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        self.sum_table.setCheckState(0,QtCore.Qt.Unchecked)

        self.regs = QtWidgets.QTreeWidgetItem(self.tree)
        self.regs.setText(0, "Regions")
        self.regs.setFlags(self.regs.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        self.regs.setCheckState(0,QtCore.Qt.Unchecked)

        self.main_reg = QtWidgets.QTreeWidgetItem(self.regs)
        self.main_name = list(self.data['config']['main_reg'][0].keys())[0]
        self.main_reg.setText(0, "Main - {}".format(self.main_name))
        self.main_reg.setFlags(self.main_reg.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        self.main_reg.setCheckState(0,QtCore.Qt.Unchecked)

        self.d = self.data['plot_summary_data']

        for i in range(len(self.d[0])):
            main_quant = QtWidgets.QTreeWidgetItem(self.main_reg)
            main_quant.setText(0, self.d[i][0]['arg'])
            main_quant.setFlags(main_quant.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            main_quant.setCheckState(0,QtCore.Qt.Unchecked)

            avg = QtWidgets.QTreeWidgetItem(main_quant)
            avg.setText(0, "Average program start table")
            avg.setFlags(avg.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            avg.setCheckState(0,QtCore.Qt.Unchecked)
            m_heat = QtWidgets.QTreeWidgetItem(main_quant)
            m_heat.setText(0, "Heatmap")
            m_heat.setFlags(m_heat.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            m_heat.setCheckState(0,QtCore.Qt.Unchecked)
            m_plot = QtWidgets.QTreeWidgetItem(main_quant)
            m_plot.setText(0, "Plot")
            m_plot.setFlags(m_plot.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            m_plot.setCheckState(0,QtCore.Qt.Unchecked)

        for i,r in enumerate(self.chs_regs):
            reg_box = QtWidgets.QTreeWidgetItem(self.regs)
            reg_box.setText(0, "Nested - {}".format(r))
            reg_box.setFlags(reg_box.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            reg_box.setCheckState(0,QtCore.Qt.Unchecked)

            nest = QtWidgets.QTreeWidgetItem(reg_box)
            nest.setText(0, "Nested region table")
            nest.setFlags(nest.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            nest.setCheckState(0,QtCore.Qt.Unchecked)

            for i in range(len(self.d[0])):
                nest_quant = QtWidgets.QTreeWidgetItem(reg_box)
                nest_quant.setText(0, self.d[i][0]['arg'])
                nest_quant.setFlags(nest_quant.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                nest_quant.setCheckState(0,QtCore.Qt.Unchecked)

                m_heat = QtWidgets.QTreeWidgetItem(nest_quant)
                m_heat.setText(0, "Heatmap")
                m_heat.setFlags(m_heat.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                m_heat.setCheckState(0,QtCore.Qt.Unchecked)
                m_plot = QtWidgets.QTreeWidgetItem(nest_quant)
                m_plot.setText(0, "Plot")
                m_plot.setFlags(m_plot.flags() | QtCore.Qt.ItemFlag.ItemIsTristate | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                m_plot.setCheckState(0,QtCore.Qt.Unchecked)

        self.head_label = QtWidgets.QLabel("Choose components of your report:")
        self.head_label.setFont(self.bf)

        self.all_items_button = QtWidgets.QPushButton("Select all")
        self.all_items_button.setFont(self.nf)
        self.all_items_button.clicked.connect(partial(self.checkAll, "All"))
        self.all_heat_button = QtWidgets.QPushButton("Select all heatmaps")
        self.all_heat_button.setFont(self.nf)
        self.all_heat_button.clicked.connect(partial(self.checkAll, "Heatmap"))
        self.all_plots_button = QtWidgets.QPushButton("Select all plots")
        self.all_plots_button.setFont(self.nf)
        self.all_plots_button.clicked.connect(partial(self.checkAll, "Plot"))
        self.all_tables_button = QtWidgets.QPushButton("Select all tables")
        self.all_tables_button.setFont(self.nf)
        self.all_tables_button.clicked.connect(partial(self.checkAll, "table"))

        self.vl = QtWidgets.QVBoxLayout()
        self.vl.addWidget(self.all_items_button)
        self.vl.addWidget(self.all_heat_button)
        self.vl.addWidget(self.all_plots_button)
        self.vl.addWidget(self.all_tables_button)

        self.hl = QtWidgets.QHBoxLayout()

        self.states = {'Heatmap': 0, 'Plot': 0, 'table': 0, 'All':0}

        if self.info:
            self.checkFromApps()


        self.genButton = QtWidgets.QPushButton("Generate LaTeX report")
        self.genButton.setFont(self.nf)
        self.genButton.clicked.connect(self.genTeX)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.tree)
        scroll.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.head_label)
        self.hl.addWidget(scroll)
        self.hl.addLayout(self.vl)
        layout.addLayout(self.hl)
        layout.addWidget(self.genButton)
        self.setLayout(layout)

    def getTreePath(self,node):
        path = []
        while node is not None:
            path.append(str(node.text(0)))
            node = node.parent()
        return ','.join(reversed(path))

    def checkFromApps(self):
        if self.info['tree']:
            self.tree.topLevelItem(0).setCheckState(0,QtCore.Qt.Checked)
        if self.info['overall']:
            self.tree.topLevelItem(1).setCheckState(0,QtCore.Qt.Checked)
        leaves = self.getTreeLeaves()
        for leaf in leaves:
            path = self.getTreePath(leaf)
            if self.info['heatmaps']:
                for i in range(len(self.info['heatmaps'])):
                    if self.info['heatmaps'][i]['quantity'] in path and self.info['heatmaps'][i]['region'] in path and leaf.text(0) == 'Heatmap':
                        currM = self.info['heatmaps'][i]['multiplier']
                        currMLab = ", Multiplier: {}".format(currM) if int(currM) != 1 else ""
                        currSw = self.info['heatmaps'][i]['switched']
                        currDec = self.info['heatmaps'][i]['decimals']
                        if currMLab or currSw or currDec != 3:
                            swLab = ", Switched" if currSw else ""
                            customHeatmap = QtWidgets.QTreeWidgetItem(leaf.parent())
                            customHeatmapLabel = "Heatmap ({}{}{})".format("Decimals: {}".format(currDec),currMLab,swLab)
                            customHeatmap.setText(0, customHeatmapLabel)
                            customHeatmap.setFlags(customHeatmap.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                            customHeatmap.setCheckState(0,QtCore.Qt.Checked)
                        else:
                            leaf.setCheckState(0,QtCore.Qt.Checked)
            if self.info['plots']:
                for i in range(len(self.info['plots'])):
                    if self.info['plots'][i]['quantity'] in path and self.info['plots'][i]['region'] in path and leaf.text(0) == 'Plot':
                        currM = self.info['plots'][i]['multiplier']
                        currMLab = "Multiplier: {}".format(currM) if int(currM) != 1 else ""
                        currSw = self.info['plots'][i]['switched']
                        currDot = self.info['plots'][i]['dot']
                        if currMLab or currSw or currDot:
                            swLab = "Switched" if self.info['plots'][i]['switched'] else ""
                            dotLab = "Dot plot" if currDot else ""
                            customPlot = QtWidgets.QTreeWidgetItem(leaf.parent())
                            customPlotLabel = "Plot ({}{}{}{}{})".format(currMLab,", " if currMLab and swLab else "",swLab,", " if (currMLab or swLab) and currDot else "",dotLab)
                            customPlot.setText(0, customPlotLabel)
                            customPlot.setFlags(customPlot.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                            customPlot.setCheckState(0,QtCore.Qt.Checked)
                        else:
                            leaf.setCheckState(0,QtCore.Qt.Checked)
            if self.info['regions']:
                for i in range(len(self.info['regions'])):
                    if self.info['regions'][i] in path and leaf.text(0) == 'Average program start table':
                        leaf.setCheckState(0,QtCore.Qt.Checked)
            if self.info['nested']:
                for i in range(len(self.info['nested'])):
                    if self.info['nested'][i] in path and leaf.text(0) == 'Nested region table':
                        leaf.setCheckState(0,QtCore.Qt.Checked)


    def getBranchLeaves(self, someBranch):
        leaves = []
        for i in range(someBranch.childCount()):
            if not someBranch.child(i).childCount():
                leaves.append(someBranch.child(i))
            else:
                leaves = leaves + self.getBranchLeaves(someBranch.child(i))
        return leaves

    def getTreeLeaves(self):
        leaves = []
        for i in range(self.tree.topLevelItemCount()):
            if not self.tree.topLevelItem(i).childCount():
                leaves.append(self.tree.topLevelItem(i))
            else:
                leaves = leaves + self.getBranchLeaves(self.tree.topLevelItem(i))

        return leaves

    def checkAll(self, whatToCheck):
        leaves = self.getTreeLeaves()
        if whatToCheck == "All":
            for leaf in leaves:
                leaf.setCheckState(0,QtCore.Qt.Unchecked) if self.states['All'] else leaf.setCheckState(0,QtCore.Qt.Checked)
        else:
            for leaf in leaves:
                if whatToCheck in leaf.text(0) and not self.states[whatToCheck]:
                    leaf.setCheckState(0,QtCore.Qt.Checked)
                elif whatToCheck in leaf.text(0) and self.states[whatToCheck]:
                    leaf.setCheckState(0,QtCore.Qt.Unchecked)

        self.states[whatToCheck] = not self.states[whatToCheck]


    def genTeX(self):
        dlg = QtWidgets.QFileDialog()
        save_file_path = str(dlg.getSaveFileName(filter='LaTeX code (*.tex)')[0])
        if save_file_path and not save_file_path.endswith('.tex'):
            save_file_path = save_file_path + '.tex' 

        if not save_file_path:
            return 0

        target_file = '/'.join(save_file_path.split('/')[0:-1])+'/readex_header.tex'
        copyfile(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/input/readex_header.tex',target_file)

        tex_file = open(save_file_path,"w")
        tex_file.write(r'\documentclass[11pt]{article}')
        tex_file.write(r'''
                        \usepackage{float} ''')
        tex_file.write(r'''\n\input{readex_header}\n''')
        tex_file.write(r'''\textwidth 6.5in
                            \evensidemargin 0in
                            \oddsidemargin 0in
                            ''')
        tex_file.write(r'\begin{document}')

        if self.tree.topLevelItem(0).checkState(0) == 2:
            tex_file.write(self.getTreeTex('/'.join(target_file.split('/')[0:-1])))
        if self.tree.topLevelItem(1).checkState(0) == 2:
            tex_file.write(self.getOvrTabTex())

        leaves = self.getBranchLeaves(self.tree.topLevelItem(2))
        currReg = leaves[0].parent().parent().text(0) if 'Nested' not in leaves[0].text(0) else leaves[0].parent().text(0)
        if leaves[0].checkState(0):
            tex_file.write(r'''
                            \begin{{center}}
                                \begin{{Large}}
                                    {}
                                \end{{Large}}
                            \end{{center}}
                            '''.format(currReg))
        for leaf in leaves:
            if leaf.parent().parent().text(0) != currReg and leaf.checkState(0):
                currReg = leaf.parent().parent().text(0) if 'Nested' not in leaf.text(0) else leaf.parent().text(0)
                tex_file.write(r'''
                        \begin{{center}}
                            \begin{{Large}}
                                {}
                            \end{{Large}}
                        \end{{center}}
                        '''.format(currReg))
            if "table" in leaf.text(0) and leaf.checkState(0):
                if leaf.parent().text(0).startswith('Nested'):
                    for i in range(len(self.data["dynamic_savings_tables"])):
                        if self.data['dynamic_savings_tables'][i]['average_program_start']['nested_func'] in leaf.parent().text(0):
                            tex_file.write(self.getOneRegTex(i))
                            break
                else:
                    for i in range(len(self.data["average_program_start_table_data"])):
                        if leaf.parent().text(0)[11:] in list(self.data["average_program_start_table_data"].keys())[i]:
                            tex_file.write(self.getAvgTabTex(i))
                            break
            elif "Heatmap" in leaf.text(0) and leaf.checkState(0):
                if currReg == "Main - {}".format(self.main_name):
                    for i in range(len(self.data["plot_summary_data"])):
                        if self.data["plot_summary_data"][i][0]['arg'] in leaf.parent().text(0):
                            tex_file.write(self.getHeatTex(-1,i,leaf.text(0)))
                            break
                else:
                    for i in range(len(self.data["nested_regions_report_data"])):
                        if self.data["nested_regions_report_data"][i]["nested_region"] in leaf.parent().parent().text(0):
                            for j in range(len(self.data["nested_regions_report_data"][i]["plot_data"])):
                                if self.data["nested_regions_report_data"][i]["plot_data"][j][0]['arg'] in leaf.parent().text(0):
                                    tex_file.write(self.getHeatTex(i,j,leaf.text(0)))
                                    break
                            break
            elif "Plot" in leaf.text(0) and leaf.checkState(0):
                if leaf.parent().parent().text(0) == "Main - {}".format(self.main_name):
                    for i in range(len(self.data["plot_summary_data"])):
                        if self.data["plot_summary_data"][i][0]['arg'] in leaf.parent().text(0):
                            tex_file.write(self.getPlotTex(-1,i,leaf.text(0)))
                            break
                else:
                    for i in range(len(self.data["nested_regions_report_data"])):
                        if self.data["nested_regions_report_data"][i]["nested_region"] in leaf.parent().parent().text(0):
                            for j in range(len(self.data["nested_regions_report_data"][i]["plot_data"])):
                                if self.data["nested_regions_report_data"][i]["plot_data"][j][0]['arg'] in leaf.parent().text(0):
                                    tex_file.write(self.getPlotTex(i,j,leaf.text(0)))
                                    break
                            break



        tex_file.write(r'''\n\end{document}''')
        tex_file.close()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Your report's LaTeX file was successfully created.")
        msg.setWindowTitle("LaTeX file created")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.buttonClicked.connect(self.close)
        msg.exec_()

    def getTreeTex(self,target):
        imgFile = target + '/TeXtree.png'
        myDPI = self.info['tree']['dpi'] if self.info['tree'] else '300'
        
        tmp_tree = pydot_example.regionTree(pathToData = self.data['root_folder_lst'][0], ownData = self.data, defaultDPI = myDPI)
        tmp_tree.G.write_png(imgFile)
        code = r'''
                \begin{figure}[H]
                    \centering
                    \includegraphics[width=1.0\textwidth]{TeXtree.png}
                    \caption{Structure of main and nested functions}
                \end{figure}
                '''
        return code

    def getHeatTex(self, idxReg, idxQuan, leafLabel):
        if idxReg == -1:
            self.plot_data = self.data["plot_summary_data"][idxQuan]
            regTitle = self.main_name
        else:
            self.plot_data = self.data["nested_regions_report_data"][idxReg]["plot_data"][idxQuan]
            regTitle = self.data["nested_regions_report_data"][idxReg]['nested_region']
        self.heat_data = self.plot_data[1]["heat_data"]
        self.k = self.plot_data[1]["lines"]
        self.ky = [h[0] for h in self.heat_data[0]]

        self.x = len(self.k)
        self.y = len(self.ky)
        if leafLabel == "Heatmap":
            numberOfDecimals = 3
            sw = False
            mult = 1
        else:
            tmpStr = "{{ {} }}".format((leafLabel[8:].replace('Switched',''' 'Switched': True''')).strip(' () '))
            tmpStr = tmpStr.replace('Decimals', ''' 'Decimals' ''').replace('Multiplier', ''' 'Multiplier' ''')
            infoDict = ast.literal_eval(tmpStr)
            numberOfDecimals = infoDict['Decimals'] if 'Decimals' in str(infoDict.keys()) else 3
            sw = infoDict['Switched'] if 'Switched' in str(infoDict.keys()) else False
            mult = infoDict['Multiplier'] if 'Multiplier' in str(infoDict.keys()) else 1
        '''for i,it in enumerate(self.info['heatmaps']):
            if it['quantity']==self.plot_data[0]['arg'] and it['region']==regTitle:
                numberOfDecimals = it['decimals']
                sw = it['switched']
                mult = it['multiplier']
                break
            else:
                numberOfDecimals = 3
                sw = False
                mult = 1'''

        tex_code = ""
        title = 'Heat map: {}, {}'.format(regTitle, self.plot_data[0]['arg'])
        x_label_unit = r"{}\,[{}]".format(self.plot_data[1]["x_label_name"], self.plot_data[1]["x_label_unit"])
        func_label_unit = r"{}\,[{}]".format(self.plot_data[1]["func_label_name"], self.plot_data[1]["func_label_unit"])
        code = r'''
                \begin{{table}}[H]
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
        for i in range(0,self.x):
            hd = [t[1] for t in self.heat_data[i][:]]
            hd2.append(mult*np.asarray(hd))

        if sw:
            hd2 = [l for l in np.transpose(hd2)]
            table_header_line = ','.join(['xLabels'] + [str(x) for x in self.ky])
            table_data_lines = [','.join([str(e) for e in tup]) for tup in list(zip(*[list(self.k)] + hd2))]
        else:
            table_header_line = ','.join(['xLabels'] + list(self.k))
            table_data_lines = [','.join([str(e) for e in tup]) for tup in list(zip(*[self.ky] + hd2))]

        code = code.format(r'\caption{{ {} }}'.format(title) if title != '' else '',
                            numberOfDecimals,
                           np.min(np.min(np.asarray(hd2))),
                           np.max(np.max(np.asarray(hd2))),
                           r''
                           if all(e == '' for e in (x_label_unit, func_label_unit))
                           else r'$\frac{{ {} }}{{ {} }}$'.format(x_label_unit if sw else func_label_unit, func_label_unit if sw else x_label_unit),
                           r'\\ \n'.join([table_header_line] + table_data_lines)
                           )
        tex_code = tex_code + code
        return tex_code

    def getPlotTex(self, idxReg, idxQuan,leafLabel):
        if idxReg == -1:
            self.plot_data = self.data["plot_summary_data"][idxQuan]
            regTitle = self.main_name
        else:
            self.plot_data = self.data["nested_regions_report_data"][idxReg]["plot_data"][idxQuan]
            regTitle = self.data["nested_regions_report_data"][idxReg]['nested_region']

        self.k = list(self.plot_data[1]["lines"])

        self.K = self.plot_data[1]["heat_data"]
        self.ky = [h[0] for h in self.K[0]]
        self.n = len(self.k)

        infoDict={}
        if leafLabel == "Plot":
            sw = False
            mult = 1
        else:
            tmpStr = "{{ {} }}".format((leafLabel[5:].replace('Switched',''' 'Switched': True''')).strip(' () '))
            tmpStr = tmpStr.replace('Multiplier', ''' 'Multiplier' ''')
            tmpStr = tmpStr.replace('Dot plot', ''' 'dot': True''')
            infoDict = ast.literal_eval(tmpStr)
            sw = infoDict['Switched'] if 'Switched' in list(infoDict.keys()) else False
            mult = infoDict['Multiplier'] if 'Multiplier' in list(infoDict.keys()) else 1

        self.optx = self.plot_data[1]["optim_x_val"]
        self.optf = self.plot_data[1]["optim_func_label_value"]
        self.ymin = min([y[1] for y in self.K[0]])

        for m in range(0,self.n):
            Y = [x[1] for x in self.K[m]]
            ymin0 = min(Y)
            if self.ymin > ymin0:
                self.ymin = ymin0

        tex_code = ""
        title = '{}, {}'.format(regTitle, self.plot_data[0]['arg'])
        x_lab = r"{}\,[{}{}]".format(self.plot_data[1]["x_label_name"], '' if mult == 1 else 1/mult, self.plot_data[1]["x_label_unit"])
        y_lab = "{} [{}]".format(self.plot_data[0]["arg"],self.plot_data[0]["unit"])
        func_lab = r"{}\,[{}]".format(self.plot_data[1]["func_label_name"], self.plot_data[1]["func_label_unit"])


        if 'dot' in infoDict.keys():
            only_marks = infoDict['dot']
        else:
            only_marks = None

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
                '''.format(title, y_lab if sw else x_lab, x_lab if sw else y_lab))

        tex_code = tex_code + textwrap.dedent(header_code) + '\n\n'

        if sw:
            a = 1
            b = 0
        else:
            a = 0
            b = 1

        for i in range(0,self.n):
            code = (r'''\addplot+ [mark=triangle*{}] coordinates {{ {}
                     }};
                     '''.format(',only marks' if only_marks else '', '\n'.join([str((mult*e[a],e[b])) for e in self.K[i]])))
            tex_code = tex_code + code

        legend_title = r'\hspace{{-.6cm}} {} '.format("{} [{}]".format(self.plot_data[1]["func_label_name"],self.plot_data[1]["func_label_unit"]))

        ret = ''
        if not self.k:
            ret = r'\legend{{ {} }}'.format(','.join(filter(None, [legend_title] + [str(i) for i in range(self.n)])))
        else:
            ret = r'\legend{{ {} }}'.format(','.join(filter(None, [legend_title] + [str(item) for item in self.k])))

        tex_code = tex_code + ret

        optim_code = r'''
                \addplot [only marks] table {{
                    {0} {1}
                }} node [pin={{[pin distance={4}pt]{3}:{{\footnotesize( {2} )}}}}]{{}};
                '''
        optim_code = textwrap.dedent(optim_code)
        title_angle = 210 if self.optx > 0.5*(min(self.ky)+max(self.ky)) else 330
        title_distance = 2
        optim_title = 'optimal settings are {}: {} {}, {}: {} {}'.format(self.plot_data[1]["x_label_name"],self.optx,self.plot_data[1]["x_label_unit"],
                                                                    self.plot_data[1]["func_label_name"],self.optf,self.plot_data[1]["func_label_unit"])
        optim_code = optim_code.format(self.ymin if sw else mult*self.optx, mult*self.optx if sw else self.ymin,
                           optim_title,
                           title_angle, title_distance)

        tex_code = tex_code + optim_code + r'\n\end{axis}\n\end{tikzpicture}\n\end{adjustbox}\n'
        return tex_code

    def getOvrTabTex(self):
        self.table_contents = self.data["overall_vals"]
        tex_code = ""
        fixed_part = r'''
                    \begin{table}[H]
                    \centering
                    \begin{adjustbox}{max width=\textwidth}
                    \begin{tabular}{lccccc}
                    \multicolumn{6}{c}{ \textbf{Overall application evaluation} } \\
                    \hline
                    \makecell[{{p{.22\textwidth}}}]{\textbf{}}
                    & \makecell[{{p{.18\textwidth}}}]{\textbf{Default}\\ \textbf{settings}}
                    & \makecell[{{p{.18\textwidth}}}]{\textbf{Default}\\ \textbf{values}}
                    & \makecell[{{p{.18\textwidth}}}]{\textbf{Best static}\\ \textbf{configuration}}
                    & \makecell[{{p{.18\textwidth}}}]{\textbf{Static}\\ \textbf{Savings}}
                    & \makecell[{{p{.18\textwidth}}}]{\textbf{Dynamic}\\ \textbf{Savings}}
                    '''
        tex_code = tex_code + fixed_part
        table_content_part = r''' '''
        for it, t in enumerate(self.table_contents):
            table_content_part = table_content_part + r'''
                                                        \\ \hline
                                                        '''
            if len(t) > 1:
                for ic, cell in enumerate(t):
                    cell = cell.replace("\n",r'''\\''')
                    cell = cell.replace("%", r'''\%''')
                    if ic==0:
                        cell_content = r'''\makecell[{{{{p{{.22\textwidth}}}}}}]{{ {} }}'''.format(cell)
                    else:
                        cell_content = r'''& \makecell[{{{{p{{.18\textwidth}}}}}}]{{ {} }} '''.format(cell)
                    table_content_part = table_content_part + cell_content
            
        tex_code = tex_code + table_content_part

        if len(self.table_contents[-1]) == 1:
            rtc = self.table_contents[-1][0].replace("%",r'''\%''')
            run_time = r'''
                        \makecell[{{{{p{{.22\textwidth}}}}}}]{{\textbf{{Run-time change with the energy optimal settings:}}}} & \multicolumn{{ 4 }}{{l}}{{ {} }}
                        \\ \hline
                        '''.format(rtc)
            tex_code = tex_code + run_time

        end_code = r'''
                \end{tabular}
                \end{adjustbox}
                \end{table}

                '''
        tex_code = tex_code + end_code
        return tex_code


    def getAvgTabTex(self, idx):
        tex_code = ""
        self.table_data = self.data["average_program_start_table_data"]
        self.table_contents = self.table_data[list(self.table_data.keys())[idx]]

        self.rtc = self.table_data.pop('runtime_change',None)

        title = list(self.table_data.keys())[idx]
        tex_code = tex_code + (r'''
                        \begin{{small}}
                        \setlength\LTleft{{-1cm}}
                        \begin{{longtable}}{{lcccccc}}
                        \multicolumn{{7}}{{c}}{{ \textbf{{ {} }} }} \\
                        \hline
                        ''').format(title)
        table_head = r'''
                        \textbf{Region} & \textbf{\% of 1 phase} & \makecell{\textbf{Best static} \\ \textbf{configuration}} &
                        \makecell{\textbf{Value}} &
                        \makecell{\textbf{Best dynamic} \\ \textbf{configuration}} &
                        \makecell{\textbf{Value}} &
                        \makecell{\textbf{Dynamic} \\ \textbf{savings}}

                        \\ \hline
                        '''
        tex_code = tex_code + table_head
        region_lines = r''''''
        for line in self.table_contents['table_lines']:
            if not line['static_config_key_unit']:
                    c3lab = r''' {}\,{},\\ {}\,{} '''.format(*line['static_func_label_unit'],
                                                            *line['static_x_label_unit'])
            else:
                c3lab = r''' {}\,{}, \\ {}\,{}, \\{}\,{}'''.format(*line['static_config_key_unit'][0],
                                                            *line['static_func_label_unit'],
                                                            *line['static_x_label_unit'])

            if not line['dynamic_configuration_key_unit'][0]:
                    c5lab = r''' {}\,{}, \\ {}\,{} '''.format(*line['dynamic_func_label_unit'][0],
                                                            *line['dynamic_x_label_unit'][0])
            else:
                c5lab = r''' {}\,{}, \\ {}\,{}, \\ {}\,{} '''.format(*line['dynamic_configuration_key_unit'][0][0],
                                                            *line['dynamic_func_label_unit'][0],
                                                            *line['dynamic_x_label_unit'][0])
            stat_val = r''' {}\,{} '''.format(*line['static_config_value'])
            dyn_val = r''' {}\,{} '''.format(line['dynamic_config_value'][0],line['dynamic_config_value'][1])
            dyn_savings = r''' {}\,{} \\({}\%)'''.format(*line['dynamic_savings'])
            reg_line = r'''\makecell[{{{{p{{.2\textwidth}}}}}}]{{ {} }} & \makecell[{{{{p{{.08\textwidth}}}}}}]{{ {} }} &
            \makecell[{{{{p{{.1\textwidth}}}}}}]{{ {} }} & \makecell[{{{{p{{.10\textwidth}}}}}}]{{ {} }} &
            \makecell[{{{{p{{.1\textwidth}}}}}}]{{ {} }} & \makecell[{{{{p{{.10\textwidth}}}}}}]{{ {} }} &
            \makecell[{{{{p{{.10\textwidth}}}}}}]{{ {} }}
            \\ \hline
            '''.format(*line['region'], line['percent_of_1_phase'], c3lab, stat_val, c5lab, dyn_val, dyn_savings)
            region_lines = region_lines + reg_line

        tex_code = tex_code + region_lines

        yl = self.table_contents['y_label_unit']
        l23lab = r'''{} = {}\,{} '''.format(" + ".join(tuple(self.table_contents['stat_saves_values'])),self.table_contents['stat_saves_sum'],yl)
        l25lab = r'''{} = {}\,{} \\of {}\,{}\,({}\%) '''.format(" + ".join(tuple(self.table_contents['dyn_saves_values'])),self.table_contents['dyn_saves_sum'],yl,
                                                                    self.table_contents['stat_saves_sum'],yl, self.table_contents['sig_region_dyn_saves_percent'])
        l27lab = r'''{}\,{} of {}\,{}\,({}\%) '''.format(self.table_contents['dyn_saves_sum'],yl,self.table_contents['app_dyn_saves'],yl,self.table_contents['app_dyn_saves_percent'])
        l29lab = r'''{}\,{}\,({}\% of {}\,{})'''.format(self.table_contents['total_savings'],yl,self.table_contents['total_savings_percent'],self.table_contents['total_val'],yl)
        ending_lines = r'''\multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.25\textwidth}}}}}}]{{\textbf{{Total value for static tuning for
                                significant regions}} }} }}
                                & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.5\textwidth}}}}}}]{{ {} }} }}\\
                                \hline
                                \multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.25\textwidth}}}}}}]{{\textbf{{Total savings for dynamic tuning
                                for significant regions}} }} }}
                                & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.5\textwidth}}}}}}]{{ {} }} }}
                                \\ \hline
                                \multicolumn{{3}}{{l}}{{\makecell[{{{{p{{.25\textwidth}}}}}}]{{\textbf{{Dynamic savings for application
                                runtime}} }} }}
                                & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.5\textwidth}}}}}}]{{ {} }} }}
                                \\ \hline
                                \multicolumn{{3}}{{l}}{{\makecell[{{{{p{{.25\textwidth}}}}}}]{{\textbf{{Total value after savings}} }} }}
                                & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.5\textwidth}}}}}}]{{ {} }} }}
                                '''.format(l23lab, l25lab, l27lab, l29lab)

        tex_code = tex_code + ending_lines
        if self.rtc:
            rtc_vals = r''''''
            for i in range(len(self.rtc)):
                rtc_vals = rtc_vals + r''' {};\,'''.format(self.rtc[i].replace("%",r'''\%'''))
            rctext = r'''\\ \hline \multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.3\textwidth}}}}}}]{{ \textbf{{Run-time change with the energy optimal settings against the default time settings (region-wise):}} }} }} &
                        \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {} }}}}
                        '''.format(rtc_vals)
            tex_code = tex_code + rctext

        tex_code = tex_code + r'''\n\end{longtable}\n\end{small}\n'''
        return tex_code

    def getOneRegTex(self,idx):
        tex_code = ""
        self.table_data = self.data["dynamic_savings_tables"]
        self.table_contents = [self.table_data[idx]['average_program_start']["table_data"],self.table_data[idx]['average_program_start']["total_dyn_savings"]]
        title = self.table_data[idx]['average_program_start']['nested_func']

        fixed_part = r'''
                        \large{{ \textbf{{ {} - average program start }} }}
                        \begingroup
                        \footnotesize
                        \noindent

                        \begin{{longtable}}[l]{{ | p{{.23\textwidth}} | c | c | c | c | c | }}
                        \cline{{1-2}}
                        \textbf{{Phase ID}} & \textbf{{ {} }} \\
                        \hline
                        \multicolumn{{1}}{{l}}{{}}\\
                        \hline
                        '''.format(title, *self.table_contents[0][0]["phase_id"])
        tex_code = tex_code + fixed_part

        for i in range(len(self.table_contents[0])):
            tmp_str = (self.table_contents[0][i]['per_phase_optim_settings'][0].translate({ord(c): None for c in '[]\''})).split(',')
            pp_optim_lab = " {}, \n {}, \n {} ".format(*tmp_str)
            if pp_optim_lab.startswith(" , \n"):
                pp_optim_lab = pp_optim_lab[4:]
            pp_optim_lab = pp_optim_lab.replace("\n","\\")
            #pp_optim_lab = "%r"%pp_optim_lab
            current_quantity = r'''\textbf{{Default {} {} }} & {} \\
                                \cline{{1-2}}
                                \textbf{{\% per 1 phase}} & {} \\
                                \cline{{1-2}}
                                \textbf{{Per phase optimal settings}} & \makecell{{ {} }} \\
                                \cline{{1-2}}
                                \textbf{{Dynamic savings [{}]}} & {} \\
                                \cline{{1-2}}
                                \textbf{{Dynamic savings [\%]}} & {} \\
                                \cline{{1-2}}
                                '''.format(self.table_contents[0][i]["y_label"], self.table_contents[0][i]["y_label_unit"],
                                        *self.table_contents[0][i]["default"], *self.table_contents[0][i]['percent_per_one _phase'],
                                        pp_optim_lab, self.table_contents[0][i]["y_label_unit"], *self.table_contents[0][i]['dynamic_savings'],
                                        *self.table_contents[0][i]['dynamic_saving_percent'])
            if self.table_contents[0][i]['def_and_eng_opt_diff']:
                current_quantity = current_quantity + r'''
                                                        \textbf{{Def. and eng. optima diff[{}]}} & {} \\
                                                        \hline
                                                        '''.format(self.table_contents[0][i]['def_and_eng_opt_diff']['unit'],
                                                            *self.table_contents[0][i]['def_and_eng_opt_diff']['vals'])

            tex_code = tex_code + current_quantity

        total_cell = r'''\multicolumn{ 2 }{|l|}{\makecell[l]{ \textbf{Total sum of values from dynamic savings from all phases}\\'''
        for i in range(0,len(self.table_contents[1])):
            total_cell = total_cell + r''' \\                          
                                        \textbf{{ {} }}\\{} {} $\rightarrow$ {} {} (savings {}\%)
                                        '''.format(self.table_contents[1][i]['y_label'],
                                                    self.table_contents[1][i]['def_vals_sum'],
                                                    self.table_contents[1][i]['y_label_unit'],
                                                    self.table_contents[1][i]['total_dyn_savings'],
                                                    self.table_contents[1][i]['y_label_unit'],
                                                    self.table_contents[1][i]['total_dyn_savings_percent'])

        tex_code = tex_code + total_cell
        tex_code = tex_code + r'''}} \\
                \cline{ 1-2 }
                \end{longtable}
                \endgroup

                '''
        return tex_code


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
