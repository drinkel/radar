import os
import json
#import sip
import sys
import shutil
import glob
import traceback
from pathlib import Path
from src import data_plot
from src import samples_plot
from src import heatmap
from src import pyyed_tree
from src import pydot_example
from src import all_tables
from src import radarGUI_analyze
from src import mericOpt
from src import texReportDialog
from src import design_main_menu
from src import data_load
from src import timeline_visualisation
from runpy import run_path
from PyQt6 import QtCore, QtGui, QtWidgets
from functools import partial
from src import design_timeline_visualisation


class DataHandler:
    __instance = None
    raw_data = None

    def getInstance(self):
        if DataHandler.__instance is None:
            return None
        return DataHandler.__instance


    def __init__(self, config_path, meric_config_path):
        if DataHandler.__instance is not None:
            DataHandler.__instance = DataHandler.getInstance(self)
        else:
            DataHandler.__instance = self

        self.raw_data = data_load.DataLoad(config_path, meric_config_path).data


class MainMenu(QtWidgets.QFrame, design_main_menu.Ui_MainMenu):
    def __init__(self, config_path, meric_config_path, tree_data_selection):
        super(self.__class__, self).__init__()


        self.config_path = config_path
        self.meric_config_path = meric_config_path
        self.tree_data_selected = tree_data_selection
        # self.config = run_path(config_path) ### loading from temporary file

        self.config = radarGUI_analyze.config_data ### loading from shared dictionary

        self.dictForTex = {'tree': None, 'plots': [], 'heatmaps': [], 'overall': False, 'timeline':[], 'regions': [], 'nested': []}
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.WindowType.WindowCloseButtonHint | QtCore.Qt.WindowType.WindowTitleHint |
                                  QtCore.Qt.WindowType.WindowMinimizeButtonHint)
        self.setFixedSize(self.size())

        self.pushButton_overall.clicked.connect(self.__overall)
        self.pushButton_plot.clicked.connect(self.__plot)
        self.pushButton_heatmap.clicked.connect(self.__heatmap)
        #self.pushButton_tree.clicked.connect(self.__tree)
        #self.pushButton_timeline.clicked.connect(self.__timeline)
        #self.pushButton_average_start.clicked.connect(self.__average_start)
        #self.pushButton_table_nested_region.clicked.connect(self.__table_nested_region)
        self.pushButton_samples.clicked.connect(self.__samples)
        #self.pushButton_generate_latex.clicked.connect(self.__generate_latex)
        self.pushButton_save_radar.clicked.connect(self.__save_config)
        self.pushButton_edit_radar.clicked.connect(self.__edit_config)
        self.pushButton_generate_meric.clicked.connect(self.__meric_opt)
        self.pushButton_restart.clicked.connect(self.restart)

        self.radar_data = DataHandler(self.config_path, self.meric_config_path)
        self.sub_windows = []

        self.pushButton_samples.setEnabled(False)


        root_folder = self.config['root_folder'][0][0]
        self.cesta=root_folder
        for region in os.listdir(root_folder):
            region_path = os.path.join(root_folder, region)
            if os.path.isdir(region_path) and region.endswith("_static"):
                samples_path = os.path.join(region_path, "samples")
                if os.path.isdir(samples_path):
                    csv_files = glob.glob(os.path.join(samples_path, "*.csv"))
                    if csv_files:
                        self.pushButton_samples.setEnabled(True)
                    else:
                        self.pushButton_samples.setEnabled(False)
                else:
                    self.pushButton_samples.setEnabled(False)


    def __plot(self):
        self.plot_window = data_plot.Window(ownData=self.radar_data.raw_data)
        self.plot_window.show()
        self.plot_window.sendInfo.connect(partial(self.__getTeXInfo,'plots'))
        self.sub_windows.append(self.plot_window)


    def __timeline(self):
        self.timeline_window = timeline_visualisation.Window(ownData=self.radar_data.raw_data)
        self.timeline_window.show()
        self.timeline_window.sendInfo.connect(partial(self.__getTeXInfo, 'plots'))
        self.sub_windows.append(self.timeline_window)


    def __samples(self):
        self.samples_window = samples_plot.Window(ownData=self.radar_data.raw_data, main_menu_instance=self)
        #self.samples_window = samples_plot.Window(ownData=self.radar_data.raw_data)
        self.samples_window.show()
        #self.samples_window.canvas
        #self.samples_window_window.sendInfo.connect(partial(self.__getTeXInfo,'plots'))
        self.sub_windows.append(self.samples_window)


    def __heatmap(self):
        self.heatmap_window = heatmap.Window(self, ownData=self.radar_data.raw_data, radar_data=True)
        self.heatmap_window.show()
        self.heatmap_window.sendInfo.connect(partial(self.__getTeXInfo,'heatmaps'))
        self.sub_windows.append(self.heatmap_window)


    def __getTeXInfo(self,objType,entry):
        if objType == 'overall' or objType == 'tree':
            self.dictForTex[objType] = entry
        else:
            self.dictForTex[objType].append(entry)


    def __tree(self):
        #self.tree_window = radarGUI_analyze.__show_tree()
        # self.tree_window = pydot_example.regionTree(pathToData = self.radar_data.raw_data, ownData=self.radar_data.raw_data, defaultDPI='300')
        # self.tree_window.show()
        self.tree_window = pydot_example.regionTree(pathToData=self.cesta, ownData=self.tree_data_selected,
                                                    addButtonIncluded=False)
        self.tree_window.show()
        self.tree_window.sendInfo.connect(partial(self.__getTeXInfo,'tree'))
        #pydot_example.browse_dir(self.radar_data.raw_data['root_folder_lst'][0], ownData=self.radar_data.raw_data)
        self.sub_windows.append(self.tree_window)


    def __average_start(self):
        self.average_start_window = all_tables.IndicSelectWindow(table="regions", ownData=self.radar_data.raw_data)
        self.average_start_window.createTable()
        self.average_start_window.show()
        self.average_start_window.sendInfo.connect(partial(self.__getTeXInfo,'regions'))
        self.sub_windows.append(self.average_start_window)


    def __table_nested_region(self):
        self.nested_region_window = all_tables.IndicSelectWindow(table="onereg", ownData=self.radar_data.raw_data)
        self.nested_region_window.createTable()
        self.nested_region_window.show()
        self.nested_region_window.sendInfo.connect(partial(self.__getTeXInfo,'nested'))
        self.sub_windows.append(self.nested_region_window)


    def __overall(self):
        self.overall_window = all_tables.IndicSelectWindow(table="overall", ownData=self.radar_data.raw_data)
        self.overall_window.createOldTable()
        self.overall_window.show()
        self.overall_window.sendInfo.connect(partial(self.__getTeXInfo,'overall'))
        self.sub_windows.append(self.overall_window)


    def __print_error_msg(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("USER INPUT ERROR")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.exec_()


    def __print_success_msg(self, text, title):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


    def __generate_latex(self):
        self.latex_report_window = texReportDialog.Window(ownData=self.radar_data.raw_data, infoFromApps = self.dictForTex)
        self.latex_report_window.show()
        self.sub_windows.append(self.latex_report_window)


    def __save_config(self):
        ### saving of config - rewrite it to read from data structure with configuration and NOT from temporary file
        dlg = QtWidgets.QFileDialog()
        config_file_path = str(dlg.getSaveFileName(filter='Text files (*.py)')[0])
        if config_file_path and not config_file_path.endswith('.py'):
            config_file_path = config_file_path + '.py'
        if config_file_path:
            try:
                shutil.copyfile(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) +
                        '/.gui_tmp_config_{}.py'.format(os.getpid()), config_file_path)
                self.__print_success_msg('File has been saved successfully.', 'File Saved')
            except:
                self.__print_error_msg('Something went wrong. Config not saved.', 'Error')


    def close_sub_windows(self):
        if self.sub_windows:
            for item in self.sub_windows:
                item.close()


    def closeEvent(self, event):
        self.close_sub_windows()
        event.accept()
        sys.exit(0)

    def __edit_config(self):
        self.hide()
        self.close_sub_windows()
        config_window = radarGUI_analyze.TabWidget('', os.path.dirname(os.path.dirname(os.path.realpath(__file__))) +
                        '/.gui_tmp_config_{}.py'.format(os.getpid()), main_menu_instance=self,
                                                   meric_config_path=self.meric_config_path)
        config_window.show()


    def __meric_opt(self):
        widget = QtWidgets.QDialog()
        self.opt_ui = mericOpt.Ui_mericOptSettings()
        self.opt_ui.setupUi(widget)
        widget.setFixedSize(widget.size())
        widget.setWindowFlags(QtCore.Qt.WindowType.WindowCloseButtonHint | QtCore.Qt.WindowType.WindowTitleHint |
                                  QtCore.Qt.WindowType.WindowMinimizeButtonHint)
        widget.show()
        self.sub_windows.append(widget)


    def restart(self):
        self.close_sub_windows()
        self.radar_data = DataHandler(self.config_path)
        self.__print_success_msg("Restart completed. RADAR analysis results updated.", 'Restart completed')
        self.sub_windows = []


