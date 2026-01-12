#!/usr/bin/env python3
import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel
from runpy import run_path
import pprint
import os
import json
import textwrap
from shutil import copyfile
from pathlib import Path
import re
from runRadarGUI_analyze import Ui_MainWindow
pp = pprint.PrettyPrinter(indent=4)
import runRadarGUI_analyze
from importlib import reload

obj = Ui_MainWindow()

class IndicSelectWindow(QtWidgets.QDialog, Ui_MainWindow):
	sendInfo = QtCore.pyqtSignal(object)
	def __init__(self, table = "overall", ownData = None, parent=None):

		super(IndicSelectWindow, self).__init__(parent=parent)


		self.mainLayout = QtWidgets.QVBoxLayout(self)
		
		self.scrollArea = QtWidgets.QScrollArea(self)
		self.scrollArea.setWidgetResizable(True)
		self.scrollAreaWidgetContents = QtWidgets.QWidget()
		self.layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
		self.gridLayout = QtWidgets.QGridLayout()
		self.scrollArea.setWidget(self.scrollAreaWidgetContents)

		self.genTeXButton = QtWidgets.QPushButton('Generate LaTeX code')
		self.genTeXButton.clicked.connect(self.getTeX)
		self.addButton = QtWidgets.QPushButton('Add to LaTeX report')
		self.addButton.clicked.connect(self.emitTeXInfo)
		self.radio1 = QtWidgets.QRadioButton("Show data with positive and negative impact")
		self.radio2 = QtWidgets.QRadioButton("Show data with positive impact only")
		self.radio3 = QtWidgets.QRadioButton("Show data with negative impact only")
		self.radio4 = QtWidgets.QRadioButton("Show all data")
		self.csvfileexport = QtWidgets.QPushButton('Export to *.CSV file')
		self.csvterminalexport = QtWidgets.QPushButton('Export to *.CSV in terminal')


		# self.bf = QtGui.QFont("Arial",13,QtGui.QFont.Bold)
		self.bf = QtGui.QFont("Arial",10)
		self.nf = QtGui.QFont("Arial",10)
		self.tabtype = table
		self.str = "string"
		self.cell_max_width = 250
		self.cell_max_height = 70
		self.cell_max_height_2 = 90

		# self.myStyleSheet = "border: 2px solid black; border-radius: 0px; background-color: rgb(0,0,0); color: rgb(255,255,255);max-width: {}px; max-height: {}px;".format(self.cell_max_width,self.cell_max_height)
		# self.myStyleSheet_2 = "border: 2px solid black; border-radius: 0px; background-color: rgb(255,255,255); max-width: {}px; max-height: {}px;".format(self.cell_max_width,self.cell_max_height_2)
		self.myStyleSheet = "border: none; border-radius: 0px; color: rgb(0,0,0);max-width: {}px; max-height: {}px;".format(self.cell_max_width,self.cell_max_height)
		self.myStyleSheet_2 = "border: none; border-radius: 0px; background-color: rgb(255,255,255); max-width: {}px; max-height: {}px;".format(self.cell_max_width,self.cell_max_height_2)
		self.myStyleSheet_3 = "border: 2px solid black; border-radius: 0px; background-color: rgb(255,255,255); max-height:{}px;".format(self.cell_max_height_2)

		self.data = ownData

		list = self.data["root_folder"]
		for i in list:

			self.root_folder = i
		measurement_info_path = Path(self.root_folder + '/measurementInfo.json')
		if measurement_info_path.exists():
			with open(measurement_info_path) as f:
				try:
					measurement_info_file_data = json.load(f)
					self.measurement_params = measurement_info_file_data['DataFormat'].split("_")
				except json.decoder.JSONDecodeError:
					self.__print_error_msg('measurementInfo.json file is not in valid format')
		param_names = self.measurement_params

		self.meric_opts_path = ""
		meric_path = self.data["meric_config_path"]
		for i in meric_path:

			self.meric_opts_path = i

		root = self.data["parameter_len"]
		root_folder = root[0]
		deflist = []
		for i in range(root_folder):
			deflist.append(str(0))
		self.default = '_'.join(deflist)

		self.meric_data_param = self.data["config_param"]


		self.data_csv = self.data["_csv_"]
		list = self.data_csv
		a = []
		self.def_path = []

		for i in list:
			a = a + i
		for i in a:
			if self.default in i or "default.csv" in i or "log.csv" in i:
				self.def_path.append(i)
		self.runtime_reg_sumary = [[], []]
		self.percent_reg = []
		self.number_caltree = []
		#self.load_csv()



	def emitTeXInfo(self):
		if self.tabtype == "overall":
			self.sendInfo.emit(True)
		elif self.tabtype == "regions":
			if len(self.table_data) > 1:
				title = str(self.combo.currentText())
			else:
				title = list(self.table_data.keys())[0]
			self.sendInfo.emit(title.split(',')[-1][1:])
		elif self.tabtype == "onereg":
			self.sendInfo.emit(str(self.combo.currentText()))

		self.addButton.setEnabled(False)
		msg = QtWidgets.QMessageBox()
		msg.setIcon(QtWidgets.QMessageBox.Information)
		msg.setText("Current table was added to LaTeX report.")
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
		target_file = '/'.join(save_file_path.split('/')[0:-1])+'/readex_header.tex'
		copyfile(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/input/readex_header.tex',target_file)

		if self.tabtype == "overall":
			tex_file = open(save_file_path,"w")
			tex_file.write(r'\documentclass{article}')
			tex_file.write(r'''\n\input{readex_header}\n''')
			tex_file.write(r'\begin{document}')
			fixed_part = r'''
					\begin{table}
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
			tex_file.write(fixed_part)
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

			tex_file.write(table_content_part)

			if len(self.table_contents[-1]) == 1:
				rtc = self.table_contents[-1][0].replace("%",r'''\%''')
				run_time = r'''
							\\ \hline \makecell[{{{{p{{.22\textwidth}}}}}}]{{\textbf{{Run-time change with the energy optimal settings:}}}} & \multicolumn{{ 4 }}{{l}}{{ {} }}
							\\ \hline
							'''.format(rtc)
				tex_file.write(run_time)

			tex_file.write(r'''
				\end{tabular}
				\end{adjustbox}
				\end{table}
				\end{document}
				''')


		elif self.tabtype == "regions":
			tex_file = open(save_file_path,"w")
			tex_file.write(r'\documentclass{article}')
			tex_file.write(r'''\n\input{readex_header}\n''')
			tex_file.write(r'\begin{document}')
			if len(self.table_data) > 1:
				title = str(self.combo.currentText())
			else:
				title = list(self.table_data.keys())[0]
			tex_file.write((r'''
							\begin{{longtable}}{{lcccccc}}
							\multicolumn{{7}}{{c}}{{ \textbf{{ {} }} }} \\
							\hline
							''').format(title))
			table_head = r'''
							\textbf{Region} & \textbf{\% of 1 phase} & \makecell{\textbf{Best static} \\ \textbf{configuration}} &
							\makecell{\textbf{Value}} &
							\makecell{\textbf{Best dynamic} \\ \textbf{configuration}} &
							\makecell{\textbf{Value}} &
							\makecell{\textbf{Dynamic} \\ \textbf{savings}}

							\\ \hline
							'''
			tex_file.write(table_head)
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
				reg_line = r'''\makecell[{{{{p{{.15\textwidth}}}}}}]{{ {} }} & \makecell[{{{{p{{.05\textwidth}}}}}}]{{ {} }} &
				\makecell[{{{{p{{.15\textwidth}}}}}}]{{ {} }} & \makecell[{{{{p{{.10\textwidth}}}}}}]{{ {} }} &
				\makecell[{{{{p{{.15\textwidth}}}}}}]{{ {} }} & \makecell[{{{{p{{.10\textwidth}}}}}}]{{ {} }} &
				\makecell[{{{{p{{.10\textwidth}}}}}}]{{ {} }}
				\\ \hline
				'''.format(*line['region'], line['percent_of_1_phase'], c3lab, stat_val, c5lab, dyn_val, dyn_savings)
				region_lines = region_lines + reg_line

			tex_file.write(region_lines)

			yl = self.table_contents['y_label_unit']
			l23lab = r'''{} = {}\,{} '''.format(" + ".join(tuple(self.table_contents['stat_saves_values'])),self.table_contents['stat_saves_sum'],yl)
			l25lab = r'''{} = {}\,{} \\of {}\,{}\,({}\%) '''.format(" + ".join(tuple(self.table_contents['dyn_saves_values'])),self.table_contents['dyn_saves_sum'],yl,
																	self.table_contents['stat_saves_sum'],yl, self.table_contents['sig_region_dyn_saves_percent'])
			l27lab = r'''{}\,{} of {}\,{}\,({}\%) '''.format(self.table_contents['dyn_saves_sum'],yl,self.table_contents['app_dyn_saves'],yl,self.table_contents['app_dyn_saves_percent'])
			l29lab = r'''{}\,{}\,({}\% of {}\,{})'''.format(self.table_contents['total_savings'],yl,self.table_contents['total_savings_percent'],self.table_contents['total_val'],yl)
			ending_lines = r'''\multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.3\textwidth}}}}}}]{{\textbf{{Total value for static tuning for
								significant regions}} }} }}
								& \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {} }} }}\\
								\hline
								\multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.3\textwidth}}}}}}]{{\textbf{{Total savings for dynamic tuning
								for significant regions}} }} }}
								& \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {} }} }}
								\\ \hline
								\multicolumn{{3}}{{l}}{{\makecell[{{{{p{{.3\textwidth}}}}}}]{{\textbf{{Dynamic savings for application
								runtime}} }} }}
								& \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {} }} }}
								\\ \hline
								\multicolumn{{3}}{{l}}{{\makecell[{{{{p{{.3\textwidth}}}}}}]{{\textbf{{Total value after savings}} }} }}
								& \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {} }} }}
								'''.format(l23lab, l25lab, l27lab, l29lab)

			tex_file.write(ending_lines)
			if self.rtc:
				rtc_vals = r''''''
				for i in range(len(self.rtc)):
						rtc_vals = rtc_vals + r''' {};\,'''.format(self.rtc[i].replace("%",r'''\%'''))
				rctext = r'''\\ \hline \multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.3\textwidth}}}}}}]{{ \textbf{{Run-time change with the energy optimal settings against the default time settings (region-wise):}} }} }} &
							\multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {} }}}}
							'''.format(rtc_vals)
				tex_file.write(rctext)

			tex_file.write(r'''\n\end{longtable}\n\n\end{document}''')


		elif self.tabtype == "onereg":
			tex_file = open(save_file_path,"w")
			tex_file.write(r'\documentclass{article}')
			tex_file.write(r'''\n\input{readex_header}\n''')
			tex_file.write(r'\begin{document}')
			title = str(self.combo.currentText())
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
			tex_file.write(fixed_part)

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
															\hline\\ \hline
															'''.format(self.table_contents[0][i]['def_and_eng_opt_diff']['unit'],
																*self.table_contents[0][i]['def_and_eng_opt_diff']['vals'])

				tex_file.write(current_quantity)

			total_cell = r'''\multicolumn{ 2 }{|l|}{\makecell[l]{ \textbf{Total sum of values from dynamic savings from all phases}\\'''
			for i in range(0,len(self.table_contents[1])):
				total_cell = total_cell + r'''\\                           
											\textbf{{ {} }}\\{} {} $\rightarrow$ {} {} (savings {}\%)
											'''.format(self.table_contents[1][i]['y_label'],
														self.table_contents[1][i]['def_vals_sum'],
														self.table_contents[1][i]['y_label_unit'],
														self.table_contents[1][i]['total_dyn_savings'],
														self.table_contents[1][i]['y_label_unit'],
														self.table_contents[1][i]['total_dyn_savings_percent'])

			tex_file.write(total_cell+r'''}''')
			tex_file.write(r'''} \\
				\cline{ 1-2 }
				\end{longtable}
				\endgroup

				\end{document}
				''')
			self.sendInfo.emit(title)

		else:
			print('Unknown table type!')
		tex_file.close()

	def createComputeValuesStorage(self):
		newdict = {
			"AVG_time" : 0.0,
			"BLADE_energy" : 0.0,
			"BLADE_avg_power" : 0.0,
			"BLADE_max_power" : 0.0,
			"BLADE_min_power" : 0.0,
			"CPU0_energy" : 0.0,
			"CPU0_avg_power" : 0.0,
			"CPU0_max_power" : 0.0,
			"CPU0_min_power" : 0.0,
			"CPU1_energy" : 0.0,
			"CPU1_avg_power" : 0.0,
			"CPU1_max_power" : 0.0,
			"CPU1_min_power" : 0.0,
			"DDRABC_energy" : 0.0,
			"DDRABC_avg_power" : 0.0,
			"DDRABC_max_power" : 0.0,
			"DDRABC_min_power" : 0.0,
			"DDRDEF_energy" : 0.0,
			"DDRDEF_avg_power" : 0.0,
			"DDRDEF_max_power" : 0.0,
			"DDRDEF_min_power" : 0.0,
			"DDRGHJ_energy" : 0.0,
			"DDRGHJ_avg_power" : 0.0,
			"DDRGHJ_max_power" : 0.0,
			"DDRGHJ_min_power" : 0.0,
			"DDRKLM_energy" : 0.0,
			"DDRKLM_avg_power" : 0.0,
			"DDRKLM_max_power" : 0.0,
			"DDRKLM_min_power" : 0.0,
			"MEZZA_energy" : 0.0,
			"MEZZA_avg_power" : 0.0,
			"MEZZA_max_power" : 0.0,
			"MEZZA_min_power" : 0.0,
			"RAPL_energy" : 0.0
		}
		return newdict
		
	def translateComputeValuesStorage(self):
		self.correctlyNamedValues = {
			"AVG_time" : "Runtime of function [s]",
			"BLADE_energy" : "HDEEM (BLADE)\nenergy consumption [J]",
			"BLADE_avg_power" : "HDEEM (BLADE)\naverage power [W]",
			"BLADE_max_power" : "HDEEM (BLADE)\nmaximal power [W]",
			"BLADE_min_power" : "HDEEM (BLADE)\nminimal power [W]",
			"CPU0_energy" : "HDEEM (CPU0)\nenergy consumption [J]",
			"CPU0_avg_power" : "HDEEM (CPU0)\naverage power [W]",
			"CPU0_max_power" : "HDEEM (CPU0)\nmaximal power [W]",
			"CPU0_min_power" : "HDEEM (CPU0)\nminimal power [W]",
			"CPU1_energy" : "HDEEM (CPU1)\nenergy consumption [J]",
			"CPU1_avg_power" : "HDEEM (CPU1)\naverage power [W]",
			"CPU1_max_power" : "HDEEM (CPU1)\nmaximal power [W]",
			"CPU1_min_power" : "HDEEM (CPU1)\nminimal power [W]",
			"DDRABC_energy" : "HDEEM (DDR ABC)\nenergy consumption [J]",
			"DDRABC_avg_power" : "HDEEM (DDR ABC)\naverage power [W]",
			"DDRABC_max_power" : "HDEEM (DDR ABC)\nmaximal power [W]",
			"DDRABC_min_power" : "HDEEM (DDR ABC)\naminimal power [W]",
			"DDRDEF_energy" : "HDEEM (DDR DEF)\nenergy consumption [J]",
			"DDRDEF_avg_power" : "HDEEM (DDR DEF)\naverage power [W]",
			"DDRDEF_max_power" : "HDEEM (DDR DEF)\nmaximal power [W]",
			"DDRDEF_min_power" : "HDEEM (DDR DEF)\nminimal power [W]",
			"DDRGHJ_energy" : "HDEEM (DDR GHJ)\nenergy consumption [J]",
			"DDRGHJ_avg_power" : "HDEEM (DDR GHJ)\naverage power [W]",
			"DDRGHJ_max_power" : "HDEEM (DDR GHJ)\nmaximal power [W]",
			"DDRGHJ_min_power" : "HDEEM (DDR GHJ)\nminimal power [W]",
			"DDRKLM_energy" : "HDEEM (DDR KLM)\nenergy consumption [J]",
			"DDRKLM_avg_power" : "HDEEM (DDR KLM)\naverage power [W]",
			"DDRKLM_max_power" : "HDEEM (DDR KLM)\nmaximal power [W]",
			"DDRKLM_min_power" : "HDEEM (DDR KLM)\nminimal power [W]",
			"MEZZA_energy" : "HDEEM (MEZZA)\nenergy consumption [J]",
			"MEZZA_avg_power" : "HDEEM (MEZZA)\naverage power [W]",
			"MEZZA_max_power" : "HDEEM (MEZZA)\nmaximal power [W]",
			"MEZZA_min_power" : "HDEEM (MEZZA)\nminimal power [W]",
			"RAPL_energy" : "RAPL\nenergy consumption [J]"
		}

	
	def findDefVals(self):
		### finding values for default run
		self.pathToDir = ""
		statDirsCnt = 0
		self.defdata = self.createComputeValuesStorage() #dictionary with default data
		all_items = os.listdir(self.root_folder)
		dirs = [item for item in all_items if os.path.isdir(os.path.join(self.root_folder, item))]
		for item in dirs:
			itemSplit = item.split("_")
			if ("static" in itemSplit):
				self.pathToDir = self.root_folder + "/" + item
				if (os.path.isdir(self.pathToDir)):
					statDirsCnt = statDirsCnt + 1
					# print("static item:", item, "cnt", statDirsCnt)

		if (statDirsCnt == 1):
			### find default runs 0_0
			defaultMeasurements = [] ### files with default measurements 0_0
			exid_cnt = 0 ### number of all execution IDs across all default measurement files
			all_measurements = os.listdir(self.pathToDir)
			for item in all_measurements:
				measurements_split = item.split("_")
				for i in range(0, len(measurements_split)):
					if (measurements_split[i] == "0" and measurements_split[i+1] == "0.csv"): ### saving just default measurements with 0_0
						defaultMeasurements.append(item)
						# self.defdata[item] = {}
			
			### now checking default data and saving necessary info
			### iterate through defdata dic, open these files, and add exids + parameters to this dic

			for i in range(0, len(defaultMeasurements)):
				path = self.pathToDir + "/" + defaultMeasurements[i]
				filename = defaultMeasurements[i]
				filedata = []
				csv_file = open(path, "r")
				actualblock = ""
				exidkey = ""
				for line in csv_file:
					if "Blade" in line:
						actualblock = "BLADE"
						if "(Blade):" in line:
							exid_cnt += 1
					elif "CPU0" in line:
						actualblock = "CPU0"
					elif "CPU1" in line:
						actualblock = "CPU1"
					elif "DDR_ABC" in line:
						actualblock = "DDRABC"
					elif "DDR_DEF" in line:
						actualblock = "DDRDEF"
					elif "DDR_GHJ" in line:
						actualblock = "DDRGHJ"
					elif "DDR_KLM" in line:
						actualblock = "DDRKLM"
					elif "MEZZA" in line:
						actualblock = "MEZZA"
					elif "RAPL" in line:
						actualblock = "RAPL"
					if "Energy consumption" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.defdata[actualblock + "_energy"] += tempdata
					elif "MAX power" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.defdata[actualblock + "_max_power"] += tempdata
					elif "MIN power" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.defdata[actualblock + "_min_power"] += tempdata
					elif "AVG power" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.defdata[actualblock + "_avg_power"] += tempdata						
					elif "Runtime of function" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.defdata["AVG_time"] += tempdata

			### total energy for each "region" (CPU0, RAM KLM ...) per number of measurements
			for key in self.defdata:
				self.defdata[key] /= exid_cnt



		else:
			print("Multiple or any _static regions found!")

	def findOptimalVal(self):
		### finding average values from measurements in optimal configuration
		### TODO: dynamic loading of OPTS file, now its static
		file_name = ".optspath"

		try:
			with open(file_name, "r", encoding="utf-8") as file:
				file_content = file.read().strip()  # Read and remove leading/trailing whitespace
			print("File content:", file_content)  # Output for verification
		except FileNotFoundError:
			print(f"Error: {file_name} not found.")
		except Exception as e:
			print(f"Error reading {file_name}: {e}")





		self.optdata = self.createComputeValuesStorage()
		optsPath = file_content
		#optsPath = "/home/okozinski/Desktop/radar/siesta_test/opts.opts"
		statRegName = ""
		nameParam1 = 999 ### first configured parameter (CF)
		nameParam2 = 999 ### second configured parameter (UnCF)
		keyParam1 = ""   ### name of first configured parameter in opts (FREQUENCY)
		keyParam2 = ""   ### name of second configured parameter in opts (UNCORE_FREQUENCY)
		self.nameKeys = []
		with open(optsPath, "r") as file:
			opts = json.load(file)
		for key, value in opts.items():
			if "_static" in key:
				statRegName = key

		statRegKeys = opts.get(statRegName, [])
		statRegList = list(statRegKeys.items())
		
		if len(statRegList) >= 2:
			(keyParam1, nameParam1), (keyParam2, nameParam2) = statRegList[:2]
			nameParam1 = str(nameParam1)
			nameParam2 = str(nameParam2)
			### now looking for files with measurements containing cofigured parameters in their names in self.pathToDir
			optimalMeasFiles = []
			for root, dirs, files in os.walk(self.pathToDir):
				for file in files:
					if "_" + nameParam1 + "_" + nameParam2 in file:
						optimalMeasFiles.append(self.pathToDir + "/" + file)


			exid_cnt = 0
			for i in range(0, len(optimalMeasFiles)):
				path = optimalMeasFiles[i]
				csv_file = open(path, "r")
				actualblock = ""

				for line in csv_file:
					if "Blade" in line:
						actualblock = "BLADE"
						if "(Blade):" in line:
							exid_cnt += 1
					elif "CPU0" in line:
						actualblock = "CPU0"
					elif "CPU1" in line:
						actualblock = "CPU1"
					elif "DDR_ABC" in line:
						actualblock = "DDRABC"
					elif "DDR_DEF" in line:
						actualblock = "DDRDEF"
					elif "DDR_GHJ" in line:
						actualblock = "DDRGHJ"
					elif "DDR_KLM" in line:
						actualblock = "DDRKLM"
					elif "MEZZA" in line:
						actualblock = "MEZZA"
					elif "RAPL" in line:
						actualblock = "RAPL"
					if "Energy consumption" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.optdata[actualblock + "_energy"] += tempdata
					elif "MAX power" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.optdata[actualblock + "_max_power"] += tempdata
					elif "MIN power" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.optdata[actualblock + "_min_power"] += tempdata
					elif "AVG power" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.optdata[actualblock + "_avg_power"] += tempdata						
					elif "Runtime of function" in line:
						tempdata = line.split(",")
						tempdata = float(tempdata[1])
						self.optdata["AVG_time"] += tempdata

			if exid_cnt != 0:
				for key in self.optdata:
					self.optdata[key] /= exid_cnt

		else:
		 	print("Too many parameters in *.opts file.")

	def findDifferences(self):
		### difference between self.defdata and self.optdata for each key in these directories
		self.diffdata = self.createComputeValuesStorage()
		for key in self.defdata:
			if key in self.optdata:
				if self.defdata[key] != 0:
					self.diffdata[key] = ((self.defdata[key] - self.optdata[key]) / self.defdata[key]) * (-100)

		

	def createOldTable(self):
		#overall application summary
		self.findDefVals()
		self.findOptimalVal()
		self.findDifferences()
		self.translateComputeValuesStorage()

		self.basic_style = "background-color: #D2D2D2;"
		self.header_style = "background-color: #BABABA; font-weight: bold;"
		self.init_style = "font-weight: bold; color: red;"
		self.header_style_length = 160
		self.header_style_height = 40
		self.csvstring = ";Default execution;Tuned execution;Impact [%];\n"
		self.csvleftcol = []
		self.resize(640, 800)
		
		if self.tabtype == "overall":
			self.setWindowTitle("Overall application summary")
			self.table_contents = self.data["overall_vals"]

			self.frm = QtWidgets.QFrame()
			self.label = QtWidgets.QLabel()
			self.label.setObjectName("label")
			self.label_2 = QtWidgets.QLabel()
			self.label_2.setObjectName("label_2")
			self.label_5 = QtWidgets.QLabel()
			self.label_5.setObjectName("label_5")
			self.label_init = QtWidgets.QLabel()
			self.label_init.setObjectName("label_init")
			self.label.setStyleSheet(self.header_style)
			self.label_2.setStyleSheet(self.header_style)
			self.label_5.setStyleSheet(self.header_style)
			self.label_init.setStyleSheet(self.init_style)

			### X axis titles
			self.label.setText("Default execution")

			self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
			self.label.setFixedWidth(self.header_style_length)
			self.label.setFixedHeight(self.header_style_height)

			self.label_2.setText("Tuned execution")
			self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
			self.label_2.setFixedWidth(self.header_style_length)
			self.label_2.setFixedHeight(self.header_style_height)

			self.label_5.setText("Impact [%]")
			self.label_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
			self.label_5.setFixedWidth(self.header_style_length)
			self.label_5.setFixedHeight(self.header_style_height)

			
			self.label_init.setText("Choose which data\nyou would like to show")
			self.label_init.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
			self.label_init.setFixedWidth(self.header_style_length)
			self.label_init.setFixedHeight(self.header_style_height)

			self.label.setVisible(False)
			self.label_2.setVisible(False)
			self.label_5.setVisible(False)

			self.gridLayout.setSpacing(1)
			self.gridLayout.setHorizontalSpacing(1)
			self.gridLayout.setVerticalSpacing(1)
			self.gridLayout.addWidget(self.label, 0, 1)
			self.gridLayout.addWidget(self.label_2, 0, 2)
			self.gridLayout.addWidget(self.label_5, 0, 3)
			self.gridLayout.addWidget(self.label_init, 1, 2)
			deflist = list(self.defdata)
			tunedlist = list(self.optdata)
			difflist = list(self.diffdata)

			####################################################
			############## SUPPORT FUNCTIONS ###################
			####################################################
			def _findAndRemoveWidgetsFromLayout():
				self.label.setVisible(True)
				self.label_2.setVisible(True)
				self.label_5.setVisible(True)
				while(self.gridLayout.count() != 3):
					for i in reversed(range(self.gridLayout.count())):
						item = self.gridLayout.itemAt(i)
						if item is not None:
							widget = item.widget()
							#if widget is not None and isinstance(widget, QLabel): ##funguje
							if widget.text() not in ("Default execution", "Tuned execution", "Impact [%]"):
								self.gridLayout.removeWidget(widget)
								widget.deleteLater()

			def _printCsvToTerminal():
				print("Required *.csv file to direct copy:")
				print("##############################################")
				print(self.csvstring)
				print("##############################################")
			
			def _getCsv():
				form = "{:." + str(1000)+"f}"
				dlg = QtWidgets.QFileDialog()
				save_file_path = str(dlg.getSaveFileName(filter='CSV file (*.csv)')[0])
				if save_file_path and not save_file_path.endswith('.csv'):
					save_file_path = save_file_path + '.csv'
				if not save_file_path:
					return 0
				target_file = '/'.join(save_file_path.split('/')[0:-1])+'/overall.csv'
				input_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

				csv_file = open(save_file_path, "w")
				csv_file.write(self.csvstring)

			####################################################
			############## END OF SUPPORT FUNCTIONS ############
			####################################################
			
			def _showAnyImpactData():
				_findAndRemoveWidgetsFromLayout()
				self.genTeXButton.setEnabled(True) 
				self.addButton.setEnabled(True)

				self.csvfileexport.setEnabled(True) 
				self.csvterminalexport.setEnabled(True)
				self.csvstring = ";Default execution;Tuned execution;Impact [%];\n"
				self.csvleftcol.clear()

				### Make empty table just with XY axis
				for it, t in enumerate(self.defdata):
					if len(t) > 1 and (self.diffdata[t] > 0.0 or self.diffdata[t] < 0.0):
						ldiff = QtWidgets.QLabel(self.correctlyNamedValues[t]) ### converting short representation of label to full (or l = QtWidgets.QLabel(t))
						ldiff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						ldiff.setStyleSheet(self.header_style)
						ldiff.setFixedWidth(self.header_style_length)
						ldiff.setFixedHeight(self.header_style_height)
						self.gridLayout.addWidget(ldiff, it+1, 0)
						self.csvleftcol.append(str(t))


				off = 0
				### fill columns
				for i in range(0, len(difflist)):
					iterdifflist = difflist[i]
					lab_impact = self.diffdata[iterdifflist]
					lab_impact = round(lab_impact, 3)

					lab_def = self.defdata[iterdifflist]
					lab_def = round(lab_def, 3)

					lab_opt = self.optdata[iterdifflist]
					lab_opt = round(lab_opt, 3)
					
					if lab_impact > 0.0 or lab_impact < 0.0:

						lab_impact = str(lab_impact)
						ldiff = QtWidgets.QLabel(lab_impact)
						ldiff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						ldiff.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(ldiff, i+1, 3)

						lab_def = str(lab_def)
						ldef = QtWidgets.QLabel(lab_def)
						ldef.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						ldef.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(ldef, i+1, 1)

						lab_opt = str(lab_opt)
						lopt = QtWidgets.QLabel(lab_opt)
						lopt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						lopt.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(lopt, i+1, 2)
						
						if (i < len(difflist) - 1):
							self.csvstring += self.csvleftcol[off] + ";" + lab_def + ";" + lab_opt + ";" + lab_impact + "\n"
						else:
							self.csvstring += self.csvleftcol[off] + ";" + lab_def + ";" + lab_opt + ";" + lab_impact

						off += 1

			def _showAllData():
				_findAndRemoveWidgetsFromLayout()
				self.genTeXButton.setEnabled(True) 
				self.addButton.setEnabled(True) 
				self.csvfileexport.setEnabled(True) 
				self.csvterminalexport.setEnabled(True)

				self.csvstring = ";Default execution;Tuned execution;Impact [%];\n"
				self.csvleftcol.clear()

				### Make empty table just with XY axis
				for it, t in enumerate(self.defdata):
					if len(t) > 1:
						ldiff = QtWidgets.QLabel(self.correctlyNamedValues[t]) ### converting short representation of label to full (or l = QtWidgets.QLabel(t))
						ldiff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						ldiff.setStyleSheet(self.header_style)
						ldiff.setFixedWidth(self.header_style_length)
						ldiff.setFixedHeight(self.header_style_height)
						self.gridLayout.addWidget(ldiff, it+1, 0)
						self.csvleftcol.append(str(t))

				off = 0
				### fill columns
				for i in range(0, len(difflist)):
					iterdifflist = difflist[i]
					lab_impact = self.diffdata[iterdifflist]
					lab_impact = round(lab_impact, 3)

					lab_def = self.defdata[iterdifflist]
					lab_def = round(lab_def, 3)

					lab_opt = self.optdata[iterdifflist]
					lab_opt = round(lab_opt, 3)
					

					lab_impact = str(lab_impact)
					ldiff = QtWidgets.QLabel(lab_impact)
					ldiff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
					ldiff.setStyleSheet(self.basic_style)
					self.gridLayout.addWidget(ldiff, i+1, 3)

					lab_def = str(lab_def)
					ldef = QtWidgets.QLabel(lab_def)
					ldef.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
					ldef.setStyleSheet(self.basic_style)
					self.gridLayout.addWidget(ldef, i+1, 1)

					lab_opt = str(lab_opt)
					lopt = QtWidgets.QLabel(lab_opt)
					lopt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
					lopt.setStyleSheet(self.basic_style)
					self.gridLayout.addWidget(lopt, i+1, 2)
				
					if (i < len(difflist) - 1):
						self.csvstring += self.csvleftcol[off] + ";" + lab_def + ";" + lab_opt + ";" + lab_impact + "\n"
					else:
						self.csvstring += self.csvleftcol[off] + ";" + lab_def + ";" + lab_opt + ";" + lab_impact

					off += 1
			
			def _showPositiveImpactData():
				_findAndRemoveWidgetsFromLayout()
				self.genTeXButton.setEnabled(True) 
				self.addButton.setEnabled(True) 
				self.csvfileexport.setEnabled(True) 
				self.csvterminalexport.setEnabled(True)

				self.csvstring = ";Default execution;Tuned execution;Impact [%];\n"
				self.csvleftcol.clear()

				### Make empty table just with XY axis
				for it, t in enumerate(self.defdata):
					if len(t) > 1 and self.diffdata[t] > 0.0:
						ldiff = QtWidgets.QLabel(self.correctlyNamedValues[t]) ### converting short representation of label to full (or l = QtWidgets.QLabel(t))
						ldiff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						ldiff.setStyleSheet(self.header_style)
						ldiff.setFixedWidth(self.header_style_length)
						ldiff.setFixedHeight(self.header_style_height)
						self.gridLayout.addWidget(ldiff, it+1, 0)
						self.csvleftcol.append(str(t))

				off = 0
				### fill columns
				for i in range(0, len(difflist)):
					iterdifflist = difflist[i]
					lab_impact = self.diffdata[iterdifflist]
					lab_impact = round(lab_impact, 3)

					lab_def = self.defdata[iterdifflist]
					lab_def = round(lab_def, 3)

					lab_opt = self.optdata[iterdifflist]
					lab_opt = round(lab_opt, 3)
					
					if lab_impact > 0.0:
						lab_impact = str(lab_impact)
						l = QtWidgets.QLabel(lab_impact)
						l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						l.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(l, i+1, 3)

						lab_def = str(lab_def)
						ldef = QtWidgets.QLabel(lab_def)
						ldef.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						ldef.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(ldef, i+1, 1)

						lab_opt = str(lab_opt)
						lopt = QtWidgets.QLabel(lab_opt)
						lopt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						lopt.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(lopt, i+1, 2)

						if (i < len(difflist) - 1):
							self.csvstring += self.csvleftcol[off] + ";" + lab_def + ";" + lab_opt + ";" + lab_impact + "\n"
						else:
							self.csvstring += self.csvleftcol[off] + ";" + lab_def + ";" + lab_opt + ";" + lab_impact

						off += 1

			def _showNegativeImpactData():
				_findAndRemoveWidgetsFromLayout()
				self.genTeXButton.setEnabled(True) 
				self.addButton.setEnabled(True) 
				self.csvfileexport.setEnabled(True) 
				self.csvterminalexport.setEnabled(True)

				self.csvstring = ";Default execution;Tuned execution;Impact [%];\n"
				self.csvleftcol.clear()

				### Make empty table just with XY axis
				for it, t in enumerate(self.defdata):
					if len(t) > 1 and self.diffdata[t] < 0.0:
						ldiff = QtWidgets.QLabel(self.correctlyNamedValues[t]) ### converting short representation of label to full (or l = QtWidgets.QLabel(t))
						ldiff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						ldiff.setStyleSheet(self.header_style)
						ldiff.setFixedWidth(self.header_style_length)
						ldiff.setFixedHeight(self.header_style_height)
						self.gridLayout.addWidget(ldiff, it+1, 0)
						self.csvleftcol.append(str(t))

				off = 0
				### fill columns
				for i in range(0, len(difflist)):
					iterdifflist = difflist[i]
					lab_impact = self.diffdata[iterdifflist]
					lab_impact = round(lab_impact, 3)

					lab_def = self.defdata[iterdifflist]
					lab_def = round(lab_def, 3)

					lab_opt = self.optdata[iterdifflist]
					lab_opt = round(lab_opt, 3)
					
					if lab_impact < 0.0:
						lab_impact = str(lab_impact)
						l = QtWidgets.QLabel(lab_impact)
						l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						l.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(l, i+1, 3)

						lab_def = str(lab_def)
						ldef = QtWidgets.QLabel(lab_def)
						ldef.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						ldef.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(ldef, i+1, 1)

						lab_opt = str(lab_opt)
						lopt = QtWidgets.QLabel(lab_opt)
						lopt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						lopt.setStyleSheet(self.basic_style)
						self.gridLayout.addWidget(lopt, i+1, 2)

						if (i < len(difflist) - 1):
							self.csvstring += self.csvleftcol[off] + ";" + lab_def + ";" + lab_opt + ";" + lab_impact + "\n"
						else:
							self.csvstring += self.csvleftcol[off] + ";" + lab_def + ";" + lab_opt + ";" + lab_impact

						off += 1

			self.radio1.clicked.connect(_showAnyImpactData)
			self.radio2.clicked.connect(_showPositiveImpactData)
			self.radio3.clicked.connect(_showNegativeImpactData)
			self.radio4.clicked.connect(_showAllData)
			self.csvterminalexport.clicked.connect(_printCsvToTerminal)
			self.csvfileexport.clicked.connect(_getCsv)



			self.layout.addLayout(self.gridLayout)


			self.mainLayout.addWidget(self.genTeXButton)
			self.mainLayout.addWidget(self.addButton)
			self.mainLayout.addWidget(self.csvfileexport)
			self.mainLayout.addWidget(self.csvterminalexport)

			self.mainLayout.addWidget(self.scrollArea)

			self.mainLayout.addWidget(self.radio1)
			self.mainLayout.addWidget(self.radio2)
			self.mainLayout.addWidget(self.radio3)
			self.mainLayout.addWidget(self.radio4)

			if len(self.csvstring) == 47:
				self.genTeXButton.setEnabled(False) 
				self.addButton.setEnabled(False) 
				self.csvfileexport.setEnabled(False) 
				self.csvterminalexport.setEnabled(False)


		

		elif self.tabtype == "regions":
			print("REGIONS")

			self.region = self.data["region"]

			self.setWindowTitle("Average program start")
			self.table_data = self.data["average_program_start_table_data"]

			self.rtc = self.table_data.pop('runtime_change', None)

			if len(self.table_data) > 1:
				self.combo = QtWidgets.QComboBox(self)
				for i in range(0, len(self.table_data)):
					self.combo.addItem(list(self.table_data.keys())[i])
			self.titile = str(self.combo.currentText())

			self.table_contents = self.table_data[list(self.table_data.keys())[0]]
			self.load_csv()

			def drawRegTab():
				self.displayedExtra = False
				self.frm = QtWidgets.QFrame()

				self.label = QtWidgets.QLabel("Region")
				self.label.setFont(self.bf)
				self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self.label_5 = QtWidgets.QLabel("# Calls")
				self.label_5.setFont(self.bf)
				self.label_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self.label_2 = QtWidgets.QLabel("% of runtime default")
				self.label_2.setFont(self.bf)
				self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self.label_3 = QtWidgets.QLabel("Optimal\nconfiguration")
				self.label_3.setFont(self.bf)
				self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self.label_6 = QtWidgets.QLabel("Value")
				self.label_6.setFont(self.bf)
				self.label_6.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self.label_7 = QtWidgets.QLabel("Dynamic\nsavings 123")
				self.label_7.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self.label_7.setFont(self.bf)

				self.label.setStyleSheet(self.myStyleSheet)
				self.label_2.setStyleSheet(self.myStyleSheet)
				self.label_3.setStyleSheet(self.myStyleSheet)
				self.label_5.setStyleSheet(self.myStyleSheet)
				self.label_6.setStyleSheet(self.myStyleSheet)
				self.label_7.setStyleSheet(self.myStyleSheet)

				self.gridLayout.setHorizontalSpacing(5)
				self.gridLayout.setVerticalSpacing(5)

				self.gridLayout.addWidget(self.label, 1, 0)
				self.gridLayout.addWidget(self.label_2, 1, 1)
				self.gridLayout.addWidget(self.label_3, 1, 2)
				self.gridLayout.addWidget(self.label_5, 1, 3)
				self.gridLayout.addWidget(self.label_6, 1, 4)
				self.gridLayout.addWidget(self.label_7, 1, 5)

				yl = self.table_contents['y_label_unit']
				row_idx = 2

				self.opt_path = [[], []]
				a = 0
				for p_id, p_info in self.meric_config_energy_data.items():
					row_idx = row_idx + 1
					tmp = ""

					if a == len(self.percent_reg) or a > len(self.percent_reg):
						print("br")
						
					else:
						c1 = QtWidgets.QLabel(p_id)
						c1.setFont(self.bf)
						c1.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						c1.setStyleSheet(self.myStyleSheet_2)
						self.gridLayout.addWidget(c1, row_idx, 0)

						proc = self.percent_reg[a]
						proc = proc.split("/")[0]
						proc = round(float(proc), 2)
						c2 = QtWidgets.QLabel(str(proc))
						c2.setFont(self.bf)
						c2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						c2.setStyleSheet(self.myStyleSheet_2)
						self.gridLayout.addWidget(c2, row_idx, 1)

						cal = self.number_caltree[a]
						cal = cal.split("/")[0]
						c4 = QtWidgets.QLabel(str(cal))
						c4.setFont(self.bf)
						c4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						c4.setStyleSheet(self.myStyleSheet_2)
						self.gridLayout.addWidget(c4, row_idx, 3)

						real_time = round(self.runtime_reg_sumary[a] - self.timeopt[a], 2)
						c5 = QtWidgets.QLabel(str(real_time))
						c5.setFont(self.bf)
						c5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						c5.setStyleSheet(self.myStyleSheet_2)
						self.gridLayout.addWidget(c5, row_idx, 5)
						opt_str = round(self.timeopt[a], 2)
						c6 = QtWidgets.QLabel(str(opt_str) + " " + str(self.value))
						c6.setFont(self.bf)
						c6.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						c6.setStyleSheet(self.myStyleSheet_2)
						self.gridLayout.addWidget(c6, row_idx, 4)

						for key in p_info:
							tmp = tmp + str(p_info[key]) + "\n"

						c3 = QtWidgets.QLabel(str(tmp))
						c3.setFont(self.bf)
						c3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						c3.setStyleSheet(self.myStyleSheet_2)
						self.gridLayout.addWidget(c3, row_idx, 2)
					a = a + 1

				realtime = 0
				for i in self.timeopt:
					realtime = realtime + i
				realtime = round(realtime - float(self.opt_static_value[0]), 2)
				deftime = 0

				for i in self.runtime_reg_sumary:
					deftime = deftime + float(i)

				deftime = round(deftime - float(self.opt_static_value[0]), 2)

				self.label_24 = QtWidgets.QLabel(" Total savings for dynamic \n tuning for significant regions ")
				self.label_24.setFont(self.bf)
				self.label_24.setStyleSheet(self.myStyleSheet_2)

				l25lab = round(deftime - realtime, 2)
				self.label_25 = QtWidgets.QLabel(str(self.total_saving) + str(self.value))
				self.label_25.setStyleSheet(self.myStyleSheet_3)
				self.label_25.setFont(self.nf)
				self.label_26 = QtWidgets.QLabel(" Dynamic savings for \n application runtime ")
				self.label_26.setFont(self.bf)
				self.label_26.setStyleSheet(self.myStyleSheet_2)
				l27lab = str(realtime)
				self.label_27 = QtWidgets.QLabel(str(self.dynamic_saving) + str(self.value))
				self.label_27.setStyleSheet(self.myStyleSheet_3)
				self.label_27.setFont(self.nf)

				self.gridLayout.addWidget(self.label_24, row_idx + 1, 0)
				self.gridLayout.addWidget(self.label_25, row_idx + 1, 1, 1, 5)
				self.gridLayout.addWidget(self.label_26, row_idx + 2, 0)
				self.gridLayout.addWidget(self.label_27, row_idx + 2, 1, 1, 5)

				if self.rtc:
					self.rcLabel = QtWidgets.QLabel(" Run-time change with the \n energy optimal settings \n against the default time \n settings (region-wise): ")
					self.rcLabel.setStyleSheet(self.myStyleSheet_2)
					self.rcLabel.setFont(self.bf)
					self.runtimeString = "\t"
					for i in range(0, row_idx - 2):
						self.runtimeString = self.runtimeString + " {};".format(self.rtc[i])
						if i % 3 == 2:
							self.runtimeString = self.runtimeString + " \n\t"

					self.rcValLabel = QtWidgets.QLabel(self.runtimeString)
					self.rcValLabel.setStyleSheet(self.myStyleSheet_3)
					self.rcValLabel.setFont(self.nf)

					self.gridLayout.addWidget(self.rcLabel, row_idx + 4, 0)
					self.gridLayout.addWidget(self.rcValLabel, row_idx + 4, 1, 1, 6)
					self.displayedExtra = True
					self.scrollArea.setMaximumSize(7 * 250 + 6 * 5, (row_idx + 4) * 90 + 70 + (row_idx + 4) * 5 + 30)
				else:
					self.scrollArea.setMaximumSize(7 * 250 + 6 * 5, (row_idx + 3) * 90 + 70 + (row_idx + 3) * 5 + 30)

			def chooseData(dataLabel):
				for i in range(0, len(self.table_data)):
					if dataLabel == list(self.table_data.keys())[i]:
						self.table_contents = self.table_data[list(self.table_data.keys())[i]]
				self.addButton.setEnabled(True)
				drawRegTab()

			def resizeOnClick():
				self.scrollArea.setMinimumWidth(self.gridLayout.sizeHint().width() + 40)
				self.resize(self.gridLayout.sizeHint().width(), self.height())

			def chooseAndResize(dataLabel):
				str_p = str(self.combo.currentText())
				self.load_saving(str_p)
				self.titile = str(self.combo.currentText())

				self.opt_path = []
				self.def_path = []
				self.timeopt = []
				self.runtime_reg_sumary = [[], []]
				self.percent_reg = []
				self.number_caltree = []
				self.load_csv()
				chooseData(dataLabel)
				resizeOnClick()




			self.layout.addWidget(self.genTeXButton)
			self.layout.addWidget(self.addButton)

			if len(self.table_data) > 1:
				self.Choose_Label = QtWidgets.QLabel("Choose quantity: ")
				self.Choose_Label.setFont(self.bf)
				self.combo.activated[str].connect(chooseAndResize)
				self.hlay = QtWidgets.QHBoxLayout()
				self.hlay.addWidget(self.Choose_Label)
				self.hlay.addWidget(self.combo)
				self.layout.addLayout(self.hlay)
			drawRegTab()

			self.layout.addLayout(self.gridLayout)
			self.scrollArea.setMinimumWidth(self.gridLayout.sizeHint().width() + 40)
			self.mainLayout.addWidget(self.scrollArea)
			self.resize(self.gridLayout.sizeHint().width(), self.height())
			#nested regions

		elif self.tabtype == "onereg":
			print("ONEREG")
			self.setWindowTitle("Nested regions")
			self.table_data = self.data["dynamic_savings_tables"]
			self.table_contents = [self.table_data[0]['average_program_start']["table_data"], self.table_data[0]['average_program_start']["total_dyn_savings"]]

			self.label = QtWidgets.QLabel("Phase ID")
			self.label.setFont(self.bf)
			self.label.setStyleSheet(self.myStyleSheet_2)

			self.gridLayout.setVerticalSpacing(5)
			self.gridLayout.setHorizontalSpacing(2)

			if len(self.table_data) > 1:
				self.combo = QtWidgets.QComboBox(self)
				for i in range(0, len(self.table_data)):
					self.combo.addItem(self.table_data[i]['average_program_start']['nested_func'])

			def drawAvgTab():
				self.id = QtWidgets.QLabel()
				self.id.setStyleSheet(self.myStyleSheet_2)
				self.id.setFont(self.nf)
				self.id.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

				self.gridLayout.addWidget(self.label, 0, 0)
				self.gridLayout.addWidget(self.id, 0, 1)
				row_idx = 0
				for i in range(0, len(self.table_contents[0])):
					self.label_2 = QtWidgets.QLabel("Default \n {} {}".format(self.table_contents[0][i]["y_label"], self.table_contents[0][i]["y_label_unit"]))
					self.label_2.setFont(self.bf)
					self.label_2.setStyleSheet(self.myStyleSheet_2)

					self.dflt = QtWidgets.QLabel(*self.table_contents[0][i]["default"])
					self.dflt.setStyleSheet(self.myStyleSheet_2)
					self.dflt.setFont(self.nf)
					self.dflt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

					self.label_5 = QtWidgets.QLabel("Dynamic savings {}".format(self.table_contents[0][i]["y_label_unit"]))
					self.label_5.setFont(self.bf)
					self.label_5.setStyleSheet(self.myStyleSheet_2)

					self.percent_per_phase = QtWidgets.QLabel(*self.table_contents[0][i]['percent_per_one _phase'])
					self.percent_per_phase.setStyleSheet(self.myStyleSheet_2)
					self.percent_per_phase.setFont(self.nf)
					self.percent_per_phase.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

					tmp_str = (self.table_contents[0][i]['per_phase_optim_settings'][0].translate({ord(c): None for c in '[]\''})).split(',')
					pp_optim_lab = " {}, \n {}, \n {} ".format(*tmp_str)
					if pp_optim_lab.startswith(" , \n"):
						pp_optim_lab = pp_optim_lab[4:]
					self.pp_optim = QtWidgets.QLabel(pp_optim_lab)
					self.pp_optim.setStyleSheet(self.myStyleSheet_2)
					self.pp_optim.setFont(self.nf)
					self.pp_optim.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

					self.dyn_sav = QtWidgets.QLabel(*self.table_contents[0][i]['dynamic_savings'])
					self.dyn_sav.setStyleSheet(self.myStyleSheet_2)
					self.dyn_sav.setFont(self.nf)
					self.dyn_sav.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

					self.dyn_sav_pc = QtWidgets.QLabel(*self.table_contents[0][i]['dynamic_saving_percent'])
					self.dyn_sav_pc.setFont(self.nf)
					self.dyn_sav_pc.setStyleSheet(self.myStyleSheet_2)
					self.dyn_sav_pc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

					self.label_per_phase = QtWidgets.QLabel("% per 1 phase")
					self.label_per_phase.setFont(self.bf)
					self.label_per_phase.setStyleSheet(self.myStyleSheet_2)
					self.label_optim = QtWidgets.QLabel("Per phase\noptimal settings")
					self.label_optim.setFont(self.bf)
					self.label_optim.setStyleSheet(self.myStyleSheet_2)
					self.label_dyn_pc = QtWidgets.QLabel("Dynamic savings [%]")
					self.label_dyn_pc.setFont(self.bf)
					self.label_dyn_pc.setStyleSheet(self.myStyleSheet_2)

					self.gridLayout.addWidget(self.label_2, row_idx + 1, 0)
					self.gridLayout.addWidget(self.dflt, row_idx + 1, 1)
					self.gridLayout.addWidget(self.label_per_phase, row_idx + 2, 0)
					self.gridLayout.addWidget(self.percent_per_phase, row_idx + 2, 1)
					self.gridLayout.addWidget(self.label_optim, row_idx + 3, 0)
					self.gridLayout.addWidget(self.pp_optim, row_idx + 3, 1)
					self.gridLayout.addWidget(self.label_5, row_idx + 4, 0)
					self.gridLayout.addWidget(self.dyn_sav, row_idx + 4, 1)
					self.gridLayout.addWidget(self.label_dyn_pc, row_idx + 5, 0)
					self.gridLayout.addWidget(self.dyn_sav_pc, row_idx + 5, 1)

					row_idx = row_idx + 5

					if self.table_contents[0][i]['def_and_eng_opt_diff']:
						self.label_7 = QtWidgets.QLabel("Def. and eng.\noptima diff [{}]".format(self.table_contents[0][i]['def_and_eng_opt_diff']['unit']))
						self.label_7.setFont(self.bf)
						self.label_7.setStyleSheet(self.myStyleSheet_2)

						self.def_eng_diff = QtWidgets.QLabel(*self.table_contents[0][i]['def_and_eng_opt_diff']['vals'])
						self.def_eng_diff.setStyleSheet(self.myStyleSheet_2)
						self.def_eng_diff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
						self.def_eng_diff.setFont(self.nf)

						self.gridLayout.addWidget(self.label_7, row_idx + 1, 0)
						self.gridLayout.addWidget(self.def_eng_diff, row_idx + 1, 1)

						row_idx = row_idx + 1

				self.endLabel = "Total sum of values from dynamic savings from all phases\n"
				height = 40
				for i in range(0, len(self.table_contents[1])):
					self.endLabel = self.endLabel + "\n{} \n{} {} \u279c {} {} (savings {} %)".format(self.table_contents[1][i]['y_label'],
																										self.table_contents[1][i]['def_vals_sum'],
																										self.table_contents[1][i]['y_label_unit'],
																										self.table_contents[1][i]['total_dyn_savings'],
																										self.table_contents[1][i]['y_label_unit'],
																										self.table_contents[1][i]['total_dyn_savings_percent'])
					height = height + 40

				self.endCell = QtWidgets.QLabel(self.endLabel)
				self.endCell.setFont(self.bf)
				self.endCell.setStyleSheet("border: 2px solid black; border-radius: 0px; background-color: rgb(255,255,255); max-height:{}px;".format(height))
				self.gridLayout.addWidget(self.endCell, row_idx + 1, 0, 2, 2)

			def chooseData(dataLabel):
				for i in range(0, len(self.table_data)):
					if dataLabel == self.table_data[i]['average_program_start']['nested_func']:
						self.table_contents = [self.table_data[i]['average_program_start']["table_data"], self.table_data[i]['average_program_start']["total_dyn_savings"]]
				self.addButton.setEnabled(True)
				drawAvgTab()

			self.layout.addWidget(self.genTeXButton)
			self.layout.addWidget(self.addButton)
			if len(self.table_data) > 1:
				self.Choose_Label = QtWidgets.QLabel("Choose region: ")
				self.Choose_Label.setFont(self.bf)
				self.combo.activated[str].connect(chooseData)
				self.hlay = QtWidgets.QHBoxLayout()
				self.hlay.addWidget(self.Choose_Label)
				self.hlay.addWidget(self.combo)

			self.scrollArea.setMaximumSize(2 * self.cell_max_width + 2, 13 * self.cell_max_height_2 + 12 * 5 + 30)
			drawAvgTab()

			self.layout.addLayout(self.hlay)
			self.layout.addLayout(self.gridLayout)
			self.scrollArea.setMinimumWidth(self.gridLayout.sizeHint().width() + 35)
			self.mainLayout.addWidget(self.scrollArea)

		else:
			print("Unknown table type!")

	def load_csv(self):

		static_runtime = 0
		reg_sum = [[], []]
		calltr = [[],[]]
		meric_data = self.data["meric_config_path"]
		root = self.data["root_folder"]
		for i in root:
			root = i
			break
		for i in meric_data:
			meric_data = i
			break
		meric_config_energy_file = open(meric_data)
		meric_config_energy_str = meric_config_energy_file.read()
		self.meric_config_energy_data = json.loads(meric_config_energy_str)
		self.opt_path = []
		self.def_path = []
		self.timeopt = []
		for p_id, p_info in self.meric_config_energy_data.items():
			tmp = ""
			def_tmp = ""
			for key in p_info:
				tmp = tmp + str(p_info[key]) +"_"
				def_tmp = def_tmp + str(0) + "_"
			path = root +"/"+p_id +"/" + tmp.strip("_")+".csv"
			if os.path.exists(path):
				self.opt_path.append(path)
			path = root + "/" + p_id + "/" + def_tmp.strip("_") + ".csv"
			if os.path.exists(path):
				self.def_path.append(path)
			path = root + "/" + p_id + "/"  + "default.csv"
			if os.path.exists(path):
				self.def_path.append(path)

		self.time_data()
		self.key_data()

	def time_data(self):
		static_runtime = 0
		reg_sum = [[], []]
		calltr = [[], []]

		for i in self.def_path:

			data_file = []
			runtime = [[], []]
			num_calltree = 0

			with open(i, "r") as file:
				for line in file:
					data_file.append(line)

			str_prev = ""
			#if self.t_como and len(self.stringCombo)>1:
			for line in data_file:
				if "CALLTREE" in line:
					str_prev = line
				elif "Runtime" in line and "CALLTREE" in str_prev: #and "#" in str_prev:
					runtime[0].append(float(line.split(",")[1].split("\n")[0]))
				elif "timestamp" in line and "CALLTREE" in str_prev:# and "#" in str_prev:
					runtime[1].append(float(line.split(",")[1].split("\n")[0]))
					num_calltree = num_calltree + 1
					str_prev = ""
				# else:
					# str_prev = ""
			runtime[0] = runtime[0][:len(runtime[1])]

			runtime = [[runtime[0][i], runtime[1][i]] for i in range(len(runtime[0]))]
			cas = 0
			for j in runtime:
				a = j[0]
				cas = cas + a

			path = i.split('/')
			reg = path[-2]


			if reg.endswith("_static"):
				static_runtime = cas
				self.runtime_reg_sumary[0].append(cas)
				reg_sum[0].append(cas)
				# self.number_caltree[0].append(num_calltree)
				calltr[0].append(num_calltree)
				self.runtime_reg_sumary[1].append(reg)
				reg_sum[1].append(reg)
				# self.number_caltree[1].append(reg)
				calltr[1].append(reg)
			else:
				self.runtime_reg_sumary[0].append(cas)
				reg_sum[0].append(cas)
				#self.number_caltree[0].append(num_calltree)
				calltr[0].append(num_calltree)
				self.runtime_reg_sumary[1].append(reg)
				reg_sum[1].append(reg)
				#self.number_caltree[1].append(reg)
				calltr[1].append(reg)


		reg_sum[0] = reg_sum[0][:len(reg_sum[1])]

		reg_sum = [[reg_sum[0][i], reg_sum[1][i]] for i in range(len(reg_sum[0]))]

		calltr[0] = calltr[0][:len(calltr[1])]

		calltr = [[calltr[0][i], calltr[1][i]] for i in range(len(calltr[0]))]
		for i in calltr:
			self.number_caltree.append(str(i[0])+"/"+ str(i[1]))
		for i in reg_sum:
			cislo = float(i[0])
			percent = float(cislo/static_runtime*100)
			self.percent_reg.append(str(percent)+"/"+i[1])
			#self.percent_reg[1].append(i[1])

		for i in self.opt_path:

			data_file = []
			runtime = [[], []]
			num_calltree = 0

			with open(i, "r") as file:
				for line in file:
					data_file.append(line)
			str_prev = ""
			for line in data_file:
				if "CALLTREE" in line:
					str_prev = line
				elif "Runtime" in line and "CALLTREE" in str_prev: #and "#" in str_prev:
					runtime[0].append(float(line.split(",")[1].split("\n")[0]))
				elif "timestamp" in line and "CALLTREE" in str_prev:# and "#" in str_prev:
					runtime[1].append(float(line.split(",")[1].split("\n")[0]))
					num_calltree = num_calltree + 1
					str_prev = ""
				# else:
					# str_prev = ""
			runtime[0] = runtime[0][:len(runtime[1])]

			runtime = [[runtime[0][i], runtime[1][i]] for i in range(len(runtime[0]))]
			cas = 0
			for j in runtime:
				a = j[0]
				cas = cas + a
				#self.timeopt.append(cas)

	def key_data(self):
		self.total_saving = ""
		self.dynamic_saving = ""
		self.value = ""
		self.runtime_reg_sumary = []
		self.timeopt = []
		self.opt_static_value =[]
		self.def_static_value = []
		key = self.titile.split(",")
		key_lab = key[1]
		key_part = key[0]
		if key[1].startswith(' '):
			key_lab = key[1].split(" ")
			#self.value = key_lab[-1]
			key_lab = key_lab[1:]
			key_lab = ' '.join(key_lab)

		list_def_wo_st = []
		list_opt_wo_st = []
		for i in range(len(self.def_path)):
			#for i in self.def_path:

				data_file = []

				#runtime = [[], []]
				num_calltree = 0
			#default
				with open(self.def_path[i], "r") as file_def:
					for line in file_def:
						data_file.append(line)
					for line in data_file:
						if key_part in line:
							tmp = line
						elif key_lab in line and key_part in tmp:
							self.runtime_reg_sumary.append(float(line.split(",")[1].split("\n")[0]))
							tmp = ""
							if "static" in self.opt_path[i]:
								self.def_static_value.append(float(line.split(",")[1].split("\n")[0]))
							else:
								list_def_wo_st.append(float(line.split(",")[1].split("\n")[0]))

			#optimum
				data_file = []
				with open(self.opt_path[i], "r") as file_opt:
					for line in file_opt:
						data_file.append(line)
					for line in data_file:
						if key_part in line:
							tmp = line
						elif key_lab in line and key_part in tmp:
							self.timeopt.append(float(line.split(",")[1].split("\n")[0]))
							res = re.search(r"\[([A-Za-z0-9_]+)\]", line)
							# res = str(re.findall('\(.*?\)', str_prev))
							result = res.group(1)
							# x = re.search("\[\S\]", txt)
							# result = x.group(0)
							self.value = result
							tmp = ""
							if "static" in self.opt_path[i]:
								self.opt_static_value.append(float(line.split(",")[1].split("\n")[0]))
							else:
								list_opt_wo_st.append(float(line.split(",")[1].split("\n")[0]))



		num_opt = 0
		num_def = 0
		for i in list_opt_wo_st:
			num_opt = num_opt + i
		for i in list_def_wo_st:
			num_def = num_def + i
		a = round(num_def - num_opt, 2)
		self.total_saving = a
		b = round(num_opt, 2)
		self.dynamic_saving = b

	def load_saving(self,str):

		self.str = str.split(",")[1]
if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	w = IndicSelectWindow(table="onereg")
	w.createTable()
	w.createNewTable()
	w.show()
	sys.exit(app.exec_())
