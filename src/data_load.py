import os
import glob
import csv
import sys
from runpy import run_path
from pathlib import Path
import json
# import h5py
import numpy as np
from src import radarGUI_analyze
from src import timeline_visualisation

# data_load.py description:
# This application works with the new radar. It is used to load data from files that the user selects at the beginning.
# The actual loading is handled by the function __load_data_from_csv(), which first loads measurementinfo.json. From its DataFormat, it extracts the tuned values.
# It then goes through all optimal configurations in all regions and reads the required information.
# After that, it iterates through all regions and configurations to collect the desired information into a list.
# The already extracted data are combined using the zip library and stored in a tuple. They are then type-casted to floats so they can be sorted. After sorting, the inverse zip* function is used to convert them back into a list, and they are type-casted again into strings.
# The loaded data are stored in self.data, which looks as follows:

# {
#   'plot_summary_data': [
#     [
#       {
#         'arg': 'Runtime of function [s]',
#         'category': 'Job info',
#         'index': 0,
#         'unit': 's'
#       },
#       {
#         'config': (),
#         'func_label_name': 'thrds',
#         'func_label_unit': '',
#         'heat_data': ([
#           (5.0, 71.3632), (11.0, 43.0427), (12.0, 41.3547), (13.0, 39.5132),
#           (16.0, 36.5126), (17.0, 35.4305), (18.0, 34.8616), (25.0, 30.8228),
#           (30.0, 29.5283), (36.0, 28.6212)
#         ],),
#         'key': '',
#         'opt_key': '',
#         'lines': ('1.0',),
#         'optim_func_label_value': 36,
#         'optim_x_val': 1,
#         'optim_y_val': 28.6212,
#         'def_val': 28.6212,
#         'x_label_name': 'CF',
#         'x_label_unit': ''
#       }
#     ],
#     [
#       {
#         'arg': 'Energy consumption [J]',
#         'category': 'Blade summary',
#         'index': 0,
#         'unit': 'J'
#       },
#       {
#         'config': (),
#         'func_label_name': 'thrds',
#         'func_label_unit': '',
#         'heat_data': ([
#           (5.0, 17350.8), (11.0, 11493.6), (12.0, 11160.7), (13.0, 10791.7),
#           (16.0, 10207.1), (17.0, 9981.92), (18.0, 9899.35), (25.0, 9159.55),
#           (30.0, 8967.47), (36.0, 8790.08)
#         ],),
#         'key': '',
#         'opt_key': '',
#         'lines': ('1.0',),
#         'optim_func_label_value': 36,
#         'optim_x_val': 1,
#         'optim_y_val': 8790.08,
#         'def_val': 8790.08,
#         'x_label_name': 'CF',
#         'x_label_unit': ''
#       }
#     ]
#   ],
#   'nested_regions_report_data': [
#     {
#       'nested_region': 'collide',
#       'plot_data': [...]
#     },
#     {
#       'nested_region': 'propagate',
#       'plot_data': [...]
#     }
#   ]
# }


import pprint
pp = pprint.PrettyPrinter(indent=4)


class DataLoad:
    def __init__(self, config_path, meric_config_path):
        self.config_path = config_path
        self.default_csv = False
        self.meric_config_path = meric_config_path
        # self.config_dic = run_path(config_path) ### loading from temporary file
        ###test
        self.config_dic = radarGUI_analyze.config_data ### loading from shared dictionary

        self.data_path = self.config_dic['root_folder'][0][0]
        self.main_reg = self.config_dic['main_reg'][0].values()
        
        if 'x_val_multiplier' in self.config_dic:
            self.xLabel_multiplier = self.config_dic['x_val_multiplier']
        else:
            self.xLabel_multiplier = float(0.0)

        if 'label_val_multiplier' in self.config_dic:
            self.funcLabel_multiplier = self.config_dic['label_val_multiplier']
        else:
            self.funcLabel_multiplier = float(0.0)

        self.regions = list(self.main_reg) + self.config_dic['all_nested_regs']

        meric_config_energy_file = open(meric_config_path)
        meric_config_energy_str = meric_config_energy_file.read()
        self.meric_config_energy_data = json.loads(meric_config_energy_str)
        self.y_label = self.config_dic['y_label']
        self.file_name_args = self.config_dic['file_name_args_tup']
        self.all_nested_regs = self.config_dic['all_nested_regs']
        self.data = {"plot_summary_data": [], "nested_regions_report_data": [], "config": self.config_dic,
                     "overall_vals": [], "average_program_start_table_data": {}, "dynamic_savings_tables": [], "_csv_": [], "root_folder": [], 'file_name_args':[], "region": [], "parameter_len":[], "csv_all":[], "tab_enable":[],"config_param":[],"meric_config_path":[],"optimal_time_config":[],"opts":[]}
        self.data["meric_config_path"].append(meric_config_path)
        # TODO: Multiple keys
        try:
            self.default_key = self.config_dic['def_keys_vals'][0]
            self.key_unit = self.config_dic['keys_units'][0]
        except IndexError:
            self.key_unit = ''
            self.default_key = ''

        if 'def_label_val' in self.config_dic:
            self.default_funcLabel_val = self.config_dic['def_label_val']
        else:
            self.default_funcLabel_val = float(0.0)


        self.default_funcLabel_str = str(round(float(self.default_funcLabel_val) * self.funcLabel_multiplier, 2))

        if 'func_label_unit' in self.config_dic:
            self.funcLabel_unit = self.config_dic['func_label_unit']
        else:
            self.funcLabel_unit = float(0.0)


        if 'def_x_val' in self.config_dic:
            self.default_xLabel_val = self.config_dic['def_x_val']
        else:
            self.default_xLabel_val = float(0.0)
        if 'x_val_unit' in self.config_dic:
            self.xLabel_unit = self.config_dic['x_val_unit']
        else:
            self.xLabel_unit = float(0.0)


        self.default_xLabel_str = str(round(float(self.default_xLabel_val) * self.funcLabel_multiplier, 2))

        self.static_config_per_y_label = {}  # optimal values for main reg
        self.default_config_total_value_per_y_label = {}

        self.__load_data_from_csv()

        self.lis = []

    ###tabulky vypnout
        self.__compute_overall_table()
        self.__compute_nested_region_table()

    #@staticmethod
    def _extend_parameter_shortcut(self,slabel):
        if slabel == 'CF':
            return 'FREQUENCY'
        elif slabel == 'UnCF':
            return 'UNCORE_FREQUENCY'
        elif slabel == 'thrds':
            return 'NUM_THREADS'
        elif slabel == 'CPUPWR':
            return 'PWRCAP_POWER'
        elif slabel == 'CPUPWRtw':
            return 'PWRCAP_TIME'
        elif slabel == 'GPUF':
            return 'GPU_FREQUENCY'
        elif slabel == 'GPUMEMF':
            return 'GPU_MEM_FREQUENCY'
        elif slabel == 'GPUPWR':
            return 'PWRCAP_GPU'
        elif slabel == "fake" or slabel == "FAKE":
            return 'fake'
        elif slabel == ' ' or slabel == '':
            for i in self.file_name_args:
                slabel = self._extend_parameter_shortcut(i[1])
                break
            return slabel
        else:
            return slabel
    
    def __compute_overall_table(self):
        main_region_data = self.data["plot_summary_data"]


        for y_label_data in main_region_data:

            # TODO: time no data for default config and static config

            static_savings = float(y_label_data[1]['def_val'] - y_label_data[1]['optim_y_val'])

            if ((y_label_data[1]['def_val']) * 0.01) == 0:
                static_savings_percentage = static_savings / int(1)
            else:
                static_savings_percentage = static_savings / (float(y_label_data[1]['def_val']) * 0.01)

            table_line = [y_label_data[0]['arg'] + ',\n' + y_label_data[0]['category'],
                          self.default_key + self.key_unit + ',\n' + self.default_funcLabel_str +
                          self.funcLabel_unit + ',\n' + self.default_xLabel_str + self.xLabel_unit,
                          str(round(y_label_data[1]['def_val'], 2)) + y_label_data[0]['unit'],
                          y_label_data[1]['opt_key'] + self.key_unit + ',\n' +
                          str(round(float(y_label_data[1]['optim_func_label_value']) * self.funcLabel_multiplier, 2))
                          + self.funcLabel_unit + ',\n' +
                          str(round(float(y_label_data[1]['optim_x_val']) * self.xLabel_multiplier,
                                    2)) + self.xLabel_unit,
                          str(round(static_savings, 2)) + y_label_data[0]['unit'] + ' (' + str(
                              round(static_savings_percentage, 2)) + '%)',
                          '']  # TODO  dynamic savings

            self.static_config_per_y_label[y_label_data[0]['category'] + ', ' + y_label_data[0]['arg']] = \
                {'func_label': str(
                    round(float(y_label_data[1]['optim_func_label_value']) * self.funcLabel_multiplier, 2)),
                    'x_label': str(round(float(y_label_data[1]['optim_x_val']) * self.xLabel_multiplier, 2)),
                    'key': y_label_data[1]['opt_key'],
                    'value': y_label_data[1]['optim_y_val']}

            self.default_config_total_value_per_y_label[y_label_data[0]['category'] + ', ' + y_label_data[0]['arg']] = \
                y_label_data[1]['def_val']

            self.data['overall_vals'].append(table_line)

    def __compute_average_start_table(self):
        nested_regions_data = self.data['nested_regions_report_data']
        average_table_data = self.data["average_program_start_table_data"]

        dic_dyn_saves_sum = {}
        dic_stat_saves_sum = {}
        dic_stat_opt_val_ylabel_reg = {}
        # Fill structure 'average_table_data' with data for calculation of total savings

        for region_data in nested_regions_data:
            region_name = region_data['nested_region']

            for y_label_plot_data in region_data['plot_data']:
                y_label_name = y_label_plot_data[0]['category'] + ", " + y_label_plot_data[0]['arg']

                if y_label_name in average_table_data.keys():

                    if y_label_name not in dic_dyn_saves_sum.keys():
                        dic_dyn_saves_sum[y_label_name] = 0

                    if y_label_name not in dic_stat_saves_sum.keys():
                        dic_stat_saves_sum[y_label_name] = 0

                    if y_label_name not in dic_stat_opt_val_ylabel_reg.keys():
                        dic_stat_opt_val_ylabel_reg[y_label_name] = {}
                    optimal_line_index = y_label_plot_data[1]['lines'].index(
                        self.static_config_per_y_label[y_label_name]['x_label'])

                    for item in y_label_plot_data[1]['heat_data'][optimal_line_index]:
                        if str(item[0]) == self.static_config_per_y_label[y_label_name]['func_label']:
                            act_static_config_value = item[1]
                            break
                        elif str(item[1]) == self.static_config_per_y_label[y_label_name]['func_label']:
                            act_static_config_value = item[0]

                        else:
                            act_static_config_value = 1

                    act_dynamic_savings_value = act_static_config_value - y_label_plot_data[1]['optim_y_val']
                    act_dynamic_savings_percentage = act_dynamic_savings_value / (act_static_config_value / 100)

                    table_line = {'dynamic_config_value': (str(round(y_label_plot_data[1]['optim_y_val'], 2))
                                                           , y_label_plot_data[0]['unit']),
                                  'dynamic_configuration_key_unit': [[(y_label_plot_data[1]['opt_key'],
                                                                       self.key_unit)]],
                                  'dynamic_func_label_unit': [(str(round(float(
                                      y_label_plot_data[1]['optim_func_label_value']) * self.funcLabel_multiplier, 2))
                                                               , self.funcLabel_unit)],
                                  'dynamic_savings': (str(round(act_dynamic_savings_value, 2)),
                                                      y_label_plot_data[0]['unit'],
                                                      str(round(act_dynamic_savings_percentage, 2))),
                                  'dynamic_x_label_unit': [(str(round(float(
                                      y_label_plot_data[1]['optim_x_val']) * self.xLabel_multiplier, 2)),
                                                            self.xLabel_unit)],
                                  'percent_of_1_phase': '',
                                  'region': [region_name],
                                  'static_config_key_unit': [(self.static_config_per_y_label[y_label_name]['key'],
                                                              self.key_unit)],
                                  'static_config_value': (str(round(act_static_config_value, 2)),
                                                          y_label_plot_data[0]['unit']),
                                  'static_func_label_unit': (self.static_config_per_y_label[y_label_name]['func_label'],
                                                             self.funcLabel_unit),
                                  'static_x_label_unit': (self.static_config_per_y_label[y_label_name]['x_label'],
                                                          self.xLabel_unit)}

                    average_table_data[y_label_name]['table_lines'].append(table_line)
                    average_table_data[y_label_name]['stat_saves_values'].append(str(round(act_static_config_value, 2)))
                    dic_stat_saves_sum[y_label_name] += act_static_config_value
                    average_table_data[y_label_name]['dyn_saves_values'].append(
                        str(round(act_dynamic_savings_value, 2)))
                    dic_dyn_saves_sum[y_label_name] += act_dynamic_savings_value
                    average_table_data[y_label_name]['app_dyn_saves'] = str(round(
                        self.static_config_per_y_label[y_label_name]['value'], 2))
                    average_table_data[y_label_name]['total_val'] = str(round(
                        self.default_config_total_value_per_y_label[y_label_name], 2))
                    dic_stat_opt_val_ylabel_reg[y_label_name][region_name] = act_static_config_value

        # calculate total savings and their percentages
        for y_label in average_table_data.keys():
            average_table_data[y_label]['dyn_saves_sum'] = dic_dyn_saves_sum[y_label]
            average_table_data[y_label]['stat_saves_sum'] = dic_stat_saves_sum[y_label]

            for line in average_table_data[y_label]['table_lines']:
                precent_of_phase = dic_stat_opt_val_ylabel_reg[y_label][line['region'][0]] / (
                        average_table_data[y_label]['stat_saves_sum'] / 100)
                line['percent_of_1_phase'] = str(round(precent_of_phase, 2))

            if self.static_config_per_y_label[y_label]['value']==0:
                divisor_stac_config = 1
            else:
                divisor_stac_config = self.static_config_per_y_label[y_label]['value']
            average_table_data[y_label]['app_dyn_saves_percent'] = round(
                average_table_data[y_label]['dyn_saves_sum'] / (divisor_stac_config / 100)
                , 2)

            average_table_data[y_label]['sig_region_dyn_saves_percent'] = round(
                average_table_data[y_label]['dyn_saves_sum'] / (average_table_data[y_label]['stat_saves_sum'] / 100)
                , 2)

            average_table_data[y_label]['total_savings'] = divisor_stac_config - \
                                                           average_table_data[y_label]['dyn_saves_sum']
            if self.default_config_total_value_per_y_label[y_label]==0:
                divisor_default_config_total=1
            else:
                divisor_default_config_total = self.default_config_total_value_per_y_label[y_label]
            average_table_data[y_label]['total_savings_percent'] = round(
                average_table_data[y_label]['total_savings'] /
                (divisor_default_config_total / 100), 2)

            for line in self.data['overall_vals']:
                act_y_label = y_label.split(',')
                reordered_y_label = act_y_label[1].strip()+',\n'+ act_y_label[0]
                if line[0] == reordered_y_label:
                    dynamic_savings_string = str(round(dic_dyn_saves_sum[y_label],2)) + \
                                             average_table_data[y_label]['y_label_unit'] +\
                                             ' of\n' + str(average_table_data[y_label]['app_dyn_saves']) + \
                                             average_table_data[y_label]['y_label_unit'] + '\n(' +\
                                             str(average_table_data[y_label]['app_dyn_saves_percent']) + '%)'
                    line[-1] = dynamic_savings_string


    def __compute_nested_region_table(self):
        nested_regions_data = self.data['nested_regions_report_data']
        average_table_data = self.data["average_program_start_table_data"]

        for region_data in nested_regions_data:
            region_name = region_data['nested_region']
            act_table_data = []
            act_total_dyn_savings = []
            for y_label, dic_values in average_table_data.items():
                for line in dic_values['table_lines']:
                    if line['region'][0] is region_name:
                        act_table_data.append({'def_and_eng_opt_diff': '',
                                                'default': [line['static_config_value'][0]],
                                                'dynamic_saving_percent': [line['dynamic_savings'][2]],
                                                'dynamic_savings': [line['dynamic_savings'][0]],
                                                'per_phase_optim_settings': ["[['"+
                                                                             line['dynamic_configuration_key_unit'][0][0][0]+' '+
                                                                             line['dynamic_configuration_key_unit'][0][0][1]+"'], '"+
                                                                             line['dynamic_func_label_unit'][0][0]+' '+
                                                                             line['dynamic_func_label_unit'][0][1]+"', '"+
                                                                             line['dynamic_x_label_unit'][0][0]+' '+
                                                                             line['dynamic_x_label_unit'][0][1]+"']"],
                                                'percent_per_one _phase': [line['percent_of_1_phase']],
                                                'phase_id': ['1'], #TODO: why only one phase???
                                                'reports_number': 2, #this parameter has no use now???
                                                'y_label': dic_values['y_label_arg_name'],
                                                'y_label_unit': dic_values['y_label_unit']})
                        act_total_dyn_savings.append({'def_vals_sum': line['static_config_value'][0],
                                                   'total_dyn_savings': line['dynamic_config_value'],
                                                   'total_dyn_savings_percent': line['dynamic_savings'][2],
                                                   'y_label': dic_values['y_label_arg_name'],
                                                   'y_label_unit': dic_values['y_label_unit']})



            self.data["dynamic_savings_tables"].append({'average_program_start': {'nested_func': region_name,
                                                                                   'table_data': act_table_data,
                                                                                   'total_dyn_savings': act_total_dyn_savings}})


    def __load_data_from_csv(self):
        self.hasFakeAxis = False
        csv_path_for_timeline = []
        args = []
        categories = []
        funcLabel_pos = -1
        xLabel_pos = -1
        key_pos = None
        data_path = self.data_path
        self.data["root_folder"].append(data_path)

        measurement_info_path = Path(self.data_path + '/measurementInfo.json')
        self.data["opts"].append(measurement_info_path)
        if measurement_info_path.exists():
            with open(measurement_info_path) as f:
                try:
                    measurement_info_file_data = json.load(f)
                    self.measurement_params = measurement_info_file_data['DataFormat'].split("_")
                    for i in self.measurement_params:
                        param_name = i

                    parameter_len = len(measurement_info_file_data['DataFormat'].split("_"))
                    self.data["parameter_len"].append(parameter_len)
                except json.decoder.JSONDecodeError:
                    self.__print_error_msg('measurementInfo.json file is not in valid format')

        for key, value in self.y_label.items():
            for val in value:
                args.append(val[0])
                # Prepare structure for average start table.
                self.data["average_program_start_table_data"][key + ", " + val[0]] = {'app_dyn_saves': '0',
                                                                                      'app_dyn_saves_percent': '0',
                                                                                      'dyn_saves_sum': '0',
                                                                                      'dyn_saves_values': [],
                                                                                      'sig_region_dyn_saves_percent': '0',
                                                                                      'stat_saves_sum': '0',
                                                                                      'stat_saves_values': [],
                                                                                      'table_lines': [],
                                                                                      'total_savings': '0',
                                                                                      'total_savings_percent': '0',
                                                                                      'total_val': '0',
                                                                                      'y_label_arg_name': val[0],
                                                                                      'y_label_unit': val[1]}
            categories.append(key)

        for i in self.file_name_args:
            for j in i:
                self.data['file_name_args'].append(j)
        funcLabel_data = ""
        xLabel_data = ""
        key_data = ""

        for i, item in enumerate(self.file_name_args):
            if item[0] == 'funcLabel':
                funcLabel_pos = i
                funcLabel_data = self.measurement_params[i]
            if item[0] == 'xLabel':
                xLabel_pos = i
                xLabel_data = self.measurement_params[i]
            if item[0] == 'key':  # TODO: Multiple keys
                key_pos = i
                key_data = self.measurement_params[i]

        if not funcLabel_data:
            funcLabel_data == np.nan
        if not xLabel_data:
            xLabel_data == np.nan
        if not key_data:
            key_data == np.nan

        funcLabel_meric_param = self._extend_parameter_shortcut(funcLabel_data)
        xLabel_meric_param = self._extend_parameter_shortcut(xLabel_data)
        key_meric_param = self._extend_parameter_shortcut(key_data) # TODO multiple keys


        meric_data_param = []

        meric_conf = self.meric_config_energy_data
        a = meric_conf.items()

        b = meric_conf.values()

        for i in b:
            vec = i.values()
            new_list = list(vec)

            self.data["config_param"].append(new_list)
            break
        # Optimal config
        for region in self.regions:

            csv_paths = glob.glob(glob.escape(self.data_path) + '/' + glob.escape(region) + '/*.csv')
            csv_paths_witout_def = glob.glob(glob.escape(self.data_path) + '/' + glob.escape(region) + '/*.csv')

            try:
                opt_key = self.meric_config_energy_data[region][key_meric_param]
            except KeyError:
                opt_key = ""

            data_region = []
            # When csv_path_for_timeline is used, the columns are organized by region,
            # whereas now the columns are organized by configuration, e.g. 17_1_1

            self.data["_csv_"].append(csv_paths)
            self.data["csv_all"].append(csv_paths)
            deflist = []
            for i in range(parameter_len):
                deflist.append(str(0))
            default = '_'.join(deflist)
            
            for key, vals in self.y_label.items():
                for i, val in enumerate(vals):


                    ### These two conditions are met only when tuning a single parameter
                    if (funcLabel_meric_param not in self.meric_config_energy_data[region]):
                        self.meric_config_energy_data[region][funcLabel_meric_param] = 0

                    if (xLabel_meric_param not in self.meric_config_energy_data[region]):
                        self.meric_config_energy_data[region][xLabel_meric_param] = 0

                    data_region.append([{'arg': vals[i][0],
                                         'category': key,
                                         'index': i,
                                         'unit': vals[i][1]},
                                        {'config': (),  # leave this empty, ignore config parameter
                                         'func_label_name': self.file_name_args[funcLabel_pos][1],
                                         'func_label_unit': self.funcLabel_unit,
                                         'heat_data': [],
                                         # list of lists one of lists contains tuples -> (xLabel, value_in_heatmap)
                                         'key':  (str(opt_key) + ';' + self.key_unit,),
                                         # optimal key from mericConfig, TODO: multiple keys
                                         'opt_key': "", #opt_key,
                                         'opt_key': "", #opt_key,
                                         'lines': [],  # funcLabel values
                                         'optim_func_label_value': self.meric_config_energy_data[region][
                                              str(funcLabel_meric_param)],  # optim vals
                                         'optim_x_val': self.meric_config_energy_data[region][xLabel_meric_param],
                                         'optim_y_val': sys.maxsize,
                                         'def_val': None,
                                         'x_label_name': self.file_name_args[xLabel_pos][1],
                                         'x_label_unit': self.xLabel_unit}])

            self.data["region"].append(region)

            act_category = None

            csv_paths_def_log = []
            real_name = ""

            for csv_path in csv_paths_witout_def:
                csv_path_for_timeline.append(csv_path)
                last_calltree = ""
                run_num = 0
                csv_name = csv_path.split('/')[-1]
                csv_name = os.path.splitext(csv_name)[0]

                if default == csv_name or "default.csv" == csv_name or "log.csv" == csv_name or csv_name == "default":
                    csv_path  = csv_path.split("/")
                    real_name = csv_path[-1]
                    csv_path[-1] = default + ".csv"
                    csv_path = "/".join(csv_path)
                    csv_paths_def_log.append(csv_path)
                    csv_name = default
                    csv_name = csv_name.split('_')
                    self.default_csv = True
                else:
                    csv_paths_def_log.append(i)
                    csv_name = csv_name.split('_')
                    self.default_csv = False

                xlabel_val = csv_name[xLabel_pos]
                funclabel_val = csv_name[funcLabel_pos]
                if key_pos:
                    key_val = csv_name[key_pos]
                else:
                    key_val = ''

                dict_plot_data_ylabel = {}
                for key, vals in self.y_label.items():
                    for i, val in enumerate(vals):
                        new_dict_key = key + " " + val[0]
                        dict_plot_data_ylabel[new_dict_key] = 0

                if key_val == opt_key or key_val == self.default_key:


                    if self.default_csv:
                        csv_path = csv_path.split("/")
                        csv_path[-1] = real_name
                        csv_path = "/".join(csv_path)
                    else:
                        csv_path = csv_path
                    with open(csv_path) as csv_file:
                        reader = csv.reader(csv_file, delimiter=',')
                        for line in reader:
                            if len(line) == 0:
                                continue
                            if "# CALLTREE" in line[0] and not (last_calltree == line[0]):
                                last_calltree = line[0]
                                run_num += 1
                                act_category = None
                                continue
                            if line[0].startswith("#") and "CALLTREE" not in line[0]:
                                act_category = line[0][2:]
                                continue
                            if line[0] in args and act_category.strip() in categories:
                                try:
                                    float(line[1])
                                except:
                                    line[1] = 0
                                dict_plot_data_ylabel[act_category.strip() + " " + line[0]] += float(line[1])

                        for key in dict_plot_data_ylabel.keys():
                            dict_plot_data_ylabel[key] = dict_plot_data_ylabel[key] / float(run_num)

                        for key, value in dict_plot_data_ylabel.items():
                            for data in data_region:
                                str_funclabel_val = str(round(float(funclabel_val) * self.funcLabel_multiplier, 2))
                                if data[0]['arg'] in key and data[0]['category'] in key:
                                    if str_funclabel_val not in data[1]['lines']:
                                        data[1]['lines'].append(str_funclabel_val)


                                    index_of_line = data[1]['lines'].index(str_funclabel_val)
                                    if len(data[1]['heat_data']) - 1 < index_of_line:
                                        data[1]['heat_data'].append([])

                                    # check if xlabel is existing in heat_data
                                    new_xLabel_val = round(float(xlabel_val) * self.xLabel_multiplier, 2)
                                    if len(data[1]['heat_data'][index_of_line]) > 0:
                                        val_exists = False
                                        for num, xLabel_val_tup in enumerate(data[1]['heat_data'][index_of_line]):
                                            if xLabel_val_tup[0] == new_xLabel_val:
                                                val_exists = True
                                                new_xLabel_val_tup = (new_xLabel_val, (xLabel_val_tup[1] + value) / 2)
                                                data[1]['heat_data'][index_of_line][num] = new_xLabel_val_tup
                                                value = new_xLabel_val_tup[1]

                                        if not val_exists:
                                            data[1]['heat_data'][index_of_line].append(
                                                (new_xLabel_val, value))
                                    else:
                                        data[1]['heat_data'][index_of_line].append(
                                            (new_xLabel_val, value))

                                    if xlabel_val == str(self.default_xLabel_val) and funclabel_val == str(
                                            self.default_funcLabel_val):
                                        data[1]['def_val'] = value

                                    if value < data[1]['optim_y_val']:  # optimal value is just minimum
                                        data[1]['optim_y_val'] = value
                                        self.data["optimal_time_config"] = csv_path
                else:
                    continue

            # sort data
            for y_label_data in data_region:
                for i, heat_data_list in enumerate(y_label_data[1]['heat_data']):
                    y_label_data[1]['heat_data'][i] = sorted(heat_data_list)

                lines_heat_data = zip([ float(i) for i in y_label_data[1]['lines']], y_label_data[1]['heat_data'])
                lines_heat_data = sorted(lines_heat_data)
                lines_heat_data = list(zip(*lines_heat_data))

                y_label_data[1]['lines'] = tuple([str(i) for i in lines_heat_data[0]])
                y_label_data[1]['heat_data'] = lines_heat_data[1]

            if region == list(self.main_reg)[0]:
                self.data["plot_summary_data"] = data_region

            else:
                self.data["nested_regions_report_data"].append({'nested_region': region, 'plot_data': data_region})

        self.csvdata = csv_path_for_timeline


    def csv_cesta_paths(self):
        csv = []

        for region in self.regions:
            csv_paths = glob.glob(glob.escape(self.data_path) + '/' + glob.escape(region) + '/*.csv')
            csv.append(csv_paths)
        return csv

    def index(self):
        data = self.data["plot_summary_data"]
        for i in data:

            for j in i:
                a = j.values('heat_data')



    # def __load_data_from_hdf5(self):
    #     # HDF5
    #     h5file = h5py.File(self.data_path + '_data.h5', 'r')
    #     measurement_info_string = str(h5file.attrs.get("/measurementInfo"), encoding='ascii')

    #     try:
    #         measurement_info_file_data = json.loads(measurement_info_string)
    #         self.measurement_params = measurement_info_file_data['DataFormat'].split("_")
    #     except json.decoder.JSONDecodeError:
    #         self.__print_error_msg('measurementInfo in HDF5 file is not in valid format')

    #     args = []
    #     categories = []
    #     funcLabel_pos = -1
    #     xLabel_pos = -1
    #     key_pos = None

    #     for key, value in self.y_label.items():
    #         for val in value:
    #             args.append(val[0])
    #             # Prepare structure for average start table.
    #             self.data["average_program_start_table_data"][key + ", " + val[0]] = {'app_dyn_saves': '0',
    #                                                                                   'app_dyn_saves_percent': '0',
    #                                                                                   'dyn_saves_sum': '0',
    #                                                                                   'dyn_saves_values': [],
    #                                                                                   'sig_region_dyn_saves_percent': '0',
    #                                                                                   'stat_saves_sum': '0',
    #                                                                                   'stat_saves_values': [],
    #                                                                                   'table_lines': [],
    #                                                                                   'total_savings': '0',
    #                                                                                   'total_savings_percent': '0',
    #                                                                                   'total_val': '0',
    #                                                                                   'y_label_unit': val[1]}
    #         categories.append(key)

    #     for i, item in enumerate(self.file_name_args):
    #         if item[0] == 'funcLabel':
    #             funcLabel_pos = i
    #             funcLabel_data = self.measurement_params[i]
    #         if item[0] == 'xLabel':
    #             xLabel_pos = i
    #             xLabel_data = self.measurement_params[i]
    #         if item[0] == 'key':  # TODO: Multiple keys
    #             key_pos = i
    #             key_data = self.measurement_params[i]

    #     funcLabel_meric_param = self._extend_parameter_shortcut(funcLabel_data)
    #     xLabel_meric_param = self._extend_parameter_shortcut(xLabel_data)
    #     key_meric_param = self._extend_parameter_shortcut(key_data) # TODO multiple keys

    #     for region in self.regions:
    #         # csv_paths = glob.glob(glob.escape(self.data_path) + '/' + glob.escape(region) + '/*.csv')

    #         try:
    #             opt_key = self.meric_config_energy_data[region][key_meric_param]
    #         except KeyError:
    #             opt_key = ''

    #         data_region = []

    #         for key, vals in self.y_label.items():
    #             for i, val in enumerate(vals):
    #                 data_region.append([{'arg': vals[i][0],
    #                                      'category': key,
    #                                      'index': i,
    #                                      'unit': vals[i][1]},
    #                                     {'config': (),  # leave this empty, ignore config parameter
    #                                      'func_label_name': self.file_name_args[funcLabel_pos][1],
    #                                      'func_label_unit': self.funcLabel_unit,
    #                                      'heat_data': [],
    #                                      # list of lists one of lists contains tuples -> (xLabel, value_in_heatmap)
    #                                      'key': (opt_key + ';' + self.key_unit,),
    #                                      # optimal key from mericConfig, TODO: multiple keys
    #                                      'opt_key': opt_key,
    #                                      'lines': [],  # funcLabel values
    #                                      'optim_func_label_value': self.meric_config_energy_data[region][
    #                                          funcLabel_meric_param],  # optim vals
    #                                      'optim_x_val': self.meric_config_energy_data[region][xLabel_meric_param],
    #                                      'optim_y_val': sys.maxsize,
    #                                      'def_val': None,
    #                                      'x_label_name': self.file_name_args[xLabel_pos][1],
    #                                      'x_label_unit': self.xLabel_unit}])

    #         act_category = None

    #         h5region = h5file[region]
    #         for nodeName in h5region.keys():
    #             h5node = h5region[nodeName]

    #             for CFname in sorted(h5node.keys(), reverse=True):
    #                 h5CF = h5node[CFname]
    #                 h5_name = []
    #                 h5_name.append(CFname)

    #                 for UnCFname in sorted(h5CF.keys(), reverse=True):
    #                     h5UnCF = h5CF[UnCFname]
    #                     h5_name.append(UnCFname)

    #                     for ThrdName in sorted(h5UnCF.keys(), reverse=True):
    #                         h5Thrd = h5UnCF[ThrdName]
    #                         h5_name.append(ThrdName)

    #                         h5_xlabel_val = h5_name[xLabel_pos]
    #                         h5_funclabel_val = h5_name[funcLabel_pos]

    #                         if key_pos:
    #                             h5_key_val = h5_name[key_pos]
    #                         else:
    #                             h5_key_val = ''

    #                         h5_dict_plot_data_ylabel = {}
    #                         for key, vals in self.y_label.items():
    #                             for i, val in enumerate(vals):
    #                                 new_dict_key = key + " " + val[0]
    #                                 h5_dict_plot_data_ylabel[new_dict_key] = 0

    #                         if h5_key_val == opt_key or h5_key_val == self.default_key:

    #                             for CategName in sorted(h5Thrd.keys()):
    #                                 h5categ = h5Thrd[CategName]
    #                                 h5_act_category = CategName
    #                                 h5_run_num = 0
    #                                 h5_last_calltree = ""

    #                                 for MeasureNumber in sorted(h5categ.keys(), reverse=True):
    #                                     h5number = h5categ[MeasureNumber]
    #                                     h5string = str(h5number[()], encoding='ascii').split("\n")

    #                                     if not (h5_last_calltree == h5string[0]):
    #                                         h5_last_calltree = h5string.pop(0)
    #                                         h5_run_num += 1

    #                                     for elem in h5string:
    #                                         line = elem.split(",")

    #                                         if line[0] in args and h5_act_category.strip() in categories:
    #                                             h5_dict_plot_data_ylabel[
    #                                                 h5_act_category.strip() + " " + line[0]] += float(line[1])

    #                             for key in h5_dict_plot_data_ylabel.keys():
    #                                 h5_dict_plot_data_ylabel[key] = h5_dict_plot_data_ylabel[key] / float(h5_run_num)

    #                             for key, value in h5_dict_plot_data_ylabel.items():
    #                                 for data in data_region:
    #                                     str_funclabel_val = str(
    #                                         round(float(h5_funclabel_val) * self.funcLabel_multiplier, 2))

    #                                     if data[0]['arg'] in key and data[0]['category'] in key:
    #                                         if str_funclabel_val not in data[1]['lines']:
    #                                             data[1]['lines'].append(str_funclabel_val)

    #                                         index_of_line = data[1]['lines'].index(str_funclabel_val)
    #                                         if len(data[1]['heat_data']) - 1 < index_of_line:
    #                                             data[1]['heat_data'].append([])

    #                                         # check if xlabel is existing in heat_data
    #                                         new_xLabel_val = round(float(h5_xlabel_val) * self.xLabel_multiplier, 2)
    #                                         if len(data[1]['heat_data'][index_of_line]) > 0:
    #                                             val_exists = False
    #                                             for num, xLabel_val_tup in enumerate(
    #                                                     data[1]['heat_data'][index_of_line]):
    #                                                 if xLabel_val_tup[0] == new_xLabel_val:
    #                                                     val_exists = True
    #                                                     new_xLabel_val_tup = (
    #                                                         new_xLabel_val, (xLabel_val_tup[1] + value) / 2)
    #                                                     data[1]['heat_data'][index_of_line][num] = new_xLabel_val_tup
    #                                                     value = new_xLabel_val_tup[1]

    #                                             if not val_exists:
    #                                                 data[1]['heat_data'][index_of_line].append(
    #                                                     (new_xLabel_val, value))
    #                                         else:
    #                                             data[1]['heat_data'][index_of_line].append(
    #                                                 (new_xLabel_val, value))

    #                                         if h5_xlabel_val == str(
    #                                                 self.default_xLabel_val) and h5_funclabel_val == str(
    #                                             self.default_funcLabel_val):
    #                                             data[1]['def_val'] = value

    #                                         if value < data[1]['optim_y_val']:  # optimal value is just minimum
    #                                             data[1]['optim_y_val'] = value

    #                         else:
    #                             continue

    #                         h5_name.pop()

    #                     h5_name.pop()

    #         # sort data
    #         for y_label_data in data_region:
    #             for i, heat_data_list in enumerate(y_label_data[1]['heat_data']):
    #                 y_label_data[1]['heat_data'][i] = sorted(heat_data_list)

    #             lines_heat_data = zip(y_label_data[1]['lines'], y_label_data[1]['heat_data'])
    #             lines_heat_data = sorted(lines_heat_data)
    #             lines_heat_data = list(zip(*lines_heat_data))
    #             y_label_data[1]['lines'] = lines_heat_data[0]
    #             y_label_data[1]['heat_data'] = lines_heat_data[1]

    #         if region == list(self.main_reg)[0]:
    #             self.data["plot_summary_data"] = data_region
    #         else:
    #             self.data["nested_regions_report_data"].append({'nested_region': region, 'plot_data': data_region})

    #     h5file.close()



