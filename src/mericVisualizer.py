import os
import textwrap
import collections

import numpy
import json
from collections import OrderedDict as ordDict
import abc
import sklearn.cluster

import utils

# import psutil
# import time
import pprint

# from config import time_energy_vars

pp = pprint.PrettyPrinter(indent=4, compact=False).pprint


class TexFile:
    def __init__(self, file_path='results.tex', landscape=True, main_file=True):
        self.__landscape = landscape
        self.__main_file = main_file

        # Opening file for writing – overwrites the file
        # noinspection PyBroadException
        try:
            self.__file = open(utils.expand_path(file_path), mode='w')

        except FileNotFoundError:
            utils.print_err("Couldn't create TexFile object - wrong file_path parameter!")
        except:
            utils.print_err("Couldn't open file for writing! Maybe missing writing permissions?")

        # Flag indicating whether the beginning of the document has already been inserted
        self.__is_doc_begin_inserted = False

        if self.is_main_file():
            self.__add_header()

    def close_file(self):
        if self.is_main_file():
            self.__add_footer()
        self.__file.close()

    def __add_header(self):
        header = (r'''
                   \documentclass{{article}}

                   \usepackage[a4paper,margin=1in{0}]{{geometry}}

                   \usepackage{{caption}}
                   \usepackage{{amsmath}}
                   \usepackage{{pgfplots}}
                   \usepackage{{graphicx}}
                   \usepackage{{underscore}}
                   \usepackage{{adjustbox}}
                   \usepackage{{filecontents}}
                   \usepackage{{pbox}}
                   \usepackage{{tikz}}
                   \usepackage{{environ}}
                   \usepackage{{longtable}}
                   \usepackage{{colortbl}}
                   \usepackage{{pgfplotstable}}
                   \usepackage{{multirow}}
                   \usepackage{{makecell}}
                   \usepackage{{titling}}
                   \usepackage{{hhline}}
                   \usepackage{{float}}
                   \usepackage[justification=centering]{{caption}}

                   \pgfplotsset{{compat=newest}}

                   \pgfplotstableset{{
                       /color cells/min/.initial=0,
                       /color cells/max/.initial=1000,
                       /color cells/textcolor/.initial=,
                       %
                       % Usage: 'color cells={{min=<value which is mapped to lowest color>,
                       %   max = <value which is mapped to largest>}}
                       color cells/.code={{%
                           \pgfqkeys{{/color cells}}{{#1}}%
                           \pgfkeysalso{{%
                               postproc cell content/.code={{%
                                   %
                                   \begingroup
                                   %
                                   % acquire the value before any number printer changed
                                   % it:
                                   \pgfkeysgetvalue{{/pgfplots/table/@preprocessed cell content}}\value
                                   \ifx\value\empty
                                       \endgroup
                                   \else
                                   \pgfmathfloatparsenumber{{\value}}%
                                   \pgfmathfloattofixed{{\pgfmathresult}}%
                                   \let\value=\pgfmathresult
                                   %
                                   % map that value:
                                   \pgfplotscolormapaccess
                                       [\pgfkeysvalueof{{/color cells/min}}:\pgfkeysvalueof{{/color cells/max}}]
                                       {{\value}}
                                       {{\pgfkeysvalueof{{/pgfplots/colormap name}}}}%
                                   % now, \pgfmathresult contains {{<R>,<G>,<B>}}
                                   %
                                   % acquire the value AFTER any preprocessor or
                                   % typesetter (like number printer) worked on it:
                                   \pgfkeysgetvalue{{/pgfplots/table/@cell content}}\typesetvalue
                                   \pgfkeysgetvalue{{/color cells/textcolor}}\textcolorvalue
                                   %
                                   % tex-expansion control
                                   % see http://tex.stackexchange.com/questions/12668...
                                   %/where-do-i-start-latex-programming/27589#27589
                                   \toks0=\expandafter{{\typesetvalue}}%
                                   \xdef\temp{{%
                                       \noexpand\pgfkeysalso{{%
                                           @cell content={{%
                                               \noexpand\cellcolor[rgb]{{\pgfmathresult}}%
                                               \noexpand\definecolor{{mapped color}}{{rgb}}{{\pgfmathresult}}%
                                               \ifx\textcolorvalue\empty
                                               \else
                                                   \noexpand\color{{\textcolorvalue}}%
                                               \fi
                                               \the\toks0 %
                                           }}%
                                       }}%
                                   }}%
                                   \endgroup
                                   \temp
                                   \fi
                               }}%
                           }}%
                       }}
                   }}

                   \makeatletter
                   \protected\def\tikz@nonactivecolon{{\ifmmode\mathrel{{\mathop\ordinarycolon}}\else:\fi}}
                   \newsavebox{{\measure@tikzpicture}}
                   \NewEnviron{{scaletikzpicturetowidth}}[1]{{%
                       \def\tikz@width{{#1}}%
                       \def\tikzscale{{1}}\begin{{lrbox}}{{\measure@tikzpicture}}%
                       \BODY
                           \end{{lrbox}}%
                           \pgfmathparse{{#1/\wd\measure@tikzpicture}}%
                           \edef\tikzscale{{\pgfmathresult}}%
                       \BODY
                   }}
                   \makeatother
                   '''
                  '\n\n')

        # Orientation of page
        orientation = ''
        if self.__landscape:
            orientation = 'landscape'

        self.__file.write(textwrap.dedent(header).lstrip().format(',{0}'.format(orientation)))

    def __add_footer(self):
        footer = ('\n\n'
                  r'\end{document}')

        self.__file.write(footer)

    def is_landscape(self):
        return self.__landscape

    def is_main_file(self):
        return self.__main_file

    def add_begin_doc(self):
        if self.__main_file:
            begin_doc = ('\n\n'
                         r'''
                         \begin{document}'''
                         '\n'
                         )
            self.__file.write(textwrap.dedent(begin_doc).lstrip())

            # Change the flag to indicate that the beginning of the document has already been inserted
            self.__is_doc_begin_inserted = True
        else:
            print('WARNING: Beginning of TeX document will not be inserted,'
                  'because this file is not main document!')

    def add_shell_command(self, command_str):
        code = ('\n\n'
                r'''
                \immediate\write18{{ {0} }}'''
                '\n'
                )

        self.__file.write(textwrap.dedent(code).lstrip().format(command_str))

    def is_doc_begin_inserted(self):
        return self.__is_doc_begin_inserted

    def insert_text(self, text):
        self.__file.write(text)

    def insert_new_page(self):
        self.__file.write(r'\newpage')

    def insert_tex_doc(self, path):
        code = r'''
                \input{{ {} }}
                '''
        code = textwrap.dedent(code)
        self.__file.write(code.format(path))


class LabeledCSVParser:
    def __init__(self, csv_file, not_parse_args_lst=list(), data_label=None, test_csv_init=False):
        """
        Input:
            csv_file - string, nazev CSV souboru
        """
        self.__parsed_file = open(csv_file, 'r')
        self.__not_parse_args_lst = not_parse_args_lst
        self.__data_label = data_label
        self.__test_csv_init = test_csv_init
        # self.__detailed_info = detailed_info

        # Dictionary with the acquired data
        #
        # Structure:
        #
        #   { 'label 1':[[(...),(...)],...], 'label 2': [[(...),(...)],...] }
        #
        #   label
        #       -> list of lists of individual records
        #           -> lists of tuples for each record
        #               -> tuple containing data from a single row
        self.__dic_data = list()  # {'all': list()}

    def __del__(self):
        del self.__dic_data
        self.__parsed_file.close()

    def _parse_block(self, lst):
        """
        Funkce pro parsovani 'ostitkovaneho' CSV.

        Predpoklada CSV ve tvaru:

            # Label 1
            data1, data2
            data3, data4

            # Label 2
            data5, data6
            data7, data8
            ...

        Labely se mohou opakovat, ziskane hodnoty
        se ulozi do ruznych listu ve slovniku __dicData,
        kde jejich spolecnym klicem bude label.
        """

        data_block = None
        dic_data = dict()
        
        # Parsing depending on whether the current
        # label is disabled or not
        is_parsing = True

        for row in lst:
            # Check whether it is a label or a data row
            if row.__contains__('#'):
                # Create new datablock
                data_block = list()

                # Extract the label name from the row
                tmp_label = row.split('#')[1].strip()

                # The label becomes 'current' – the following
                # data will be assigned to it
                current_label = tmp_label

                # If the label is disabled, set
                # is_parsing = False
                if current_label in self.__not_parse_args_lst:
                    is_parsing = False
                    continue

                dic_data[current_label] = data_block
                is_parsing = True
            else:
                # Add the parsed row to the current
                # data block as a tuple, if the label
                # is not disabled
                if is_parsing:
                    data_block.append(tuple(row.strip().split(',')))

        return dic_data

    # @profile
    def parse(self, detailed_info=None):
        """
        Funkce pro parsovani 'ostitkovaneho' CSV.

        Predpoklada CSV ve tvaru:

            # Label 1
            data1, data2
            data3, data4

            # Label 2
            data5, data6
            data7, data8
            ...

        Labely se mohou opakovat, ziskane hodnoty
        se ulozi do ruznych listu ve slovniku __dicData,
        kde jejich spolecnym klicem bude label.
        """

        # Check the "init" index in the CSV file – warning if
        # they are too large (RAM consumption, significant slowdown)
        if self.__test_csv_init:
            for line_ind, line in enumerate(self.__parsed_file):
                if "CALLTREE;init" in line:
                    tmp = int(line.rsplit('_')[-1])
                    if tmp > 5 and line_ind == 0:
                        utils.print_warning('CSV file {file} begins with "init" {init}. Is it really correct?'
                                            .format(file=self.__data_label,
                                                    init=tmp))
                    elif tmp > 20:
                        utils.print_warning('CSV file {file} contains "init" {init}. Is it really correct? It could '
                                            'significantly slow the run-time of RADAR report generator and consume large'
                                            ' amounts of RAM.'
                                            .format(file=self.__data_label,
                                                    init=tmp))
            self.__parsed_file.seek(0)

        one_call_data_block = list()

        curr_lst = None
        parent_call_lvl = None

        last_calltree = None

        for line in self.__parsed_file:

            if line.__contains__('# CALLTREE'):
                last_calltree = line

                if one_call_data_block:
                    parsed_block_dic = self._parse_block(one_call_data_block)

                    # If detailed info is also being recorded (all region calls),
                    # then add the calltree to the structure for the given call
                    if detailed_info is not None:
                        detailed_info.append((line.strip(), [e for l in parsed_block_dic.values() for e in l]))

                    # Write data into the call structure
                    if len(curr_lst) == parent_call_lvl:
                        curr_lst.append({'vals': []})
                        # noinspection PyTypeChecker
                        curr_lst[parent_call_lvl]['vals'].append(parsed_block_dic)

                    elif len(curr_lst) > parent_call_lvl:
                        # noinspection PyTypeChecker
                        curr_lst[parent_call_lvl]['vals'].append(parsed_block_dic)
                    else:
                        for i in range(parent_call_lvl - len(curr_lst) + 1):
                            curr_lst.append({'vals': []})
                        # noinspection PyTypeChecker
                        curr_lst[parent_call_lvl]['vals'].append(parsed_block_dic)

                    one_call_data_block = list()

                call_tree_lst = line.strip().split(';')[1:]
                curr_lst = self.__dic_data
                parent_call_lvl = 0

                for call_lvl in call_tree_lst:
                    call_lvl_name, call_lvl_ind = call_lvl.rsplit('_', 1)
                    call_lvl_ind = int(call_lvl_ind)

                    # If there are 0 elements, add an element at
                    # position 0, and so on
                    if len(curr_lst) == parent_call_lvl:
                        new_lst = list()
                        dic_tmp = {call_lvl_name: new_lst}
                        curr_lst.append(dic_tmp)
                        curr_lst = new_lst
                        parent_call_lvl = call_lvl_ind
                    elif len(curr_lst) > parent_call_lvl:
                        if call_lvl_name in curr_lst[parent_call_lvl]:
                            curr_lst = curr_lst[parent_call_lvl][call_lvl_name]
                            parent_call_lvl = call_lvl_ind
                        else:
                            new_lst = list()
                            curr_lst[parent_call_lvl][call_lvl_name] = new_lst
                            curr_lst = curr_lst[parent_call_lvl][call_lvl_name]
                            parent_call_lvl = call_lvl_ind
                    else:
                        new_lst = None
                        for i in range(parent_call_lvl - len(curr_lst) + 1):
                            new_lst = list()
                            dic_tmp = {call_lvl_name: new_lst}
                            curr_lst.append(dic_tmp)
                        curr_lst = new_lst
                        parent_call_lvl = call_lvl_ind

            else:
                one_call_data_block.append(line)

        # Loading of data from last block
        if one_call_data_block:
            parsed_block_dic = self._parse_block(one_call_data_block)

            # Write data into the call structure
            if len(curr_lst) == parent_call_lvl:
                curr_lst.append({'vals': []})
                # noinspection PyTypeChecker
                curr_lst[parent_call_lvl]['vals'].append(parsed_block_dic)

            elif len(curr_lst) > parent_call_lvl:
                # noinspection PyTypeChecker
                curr_lst[parent_call_lvl]['vals'].append(parsed_block_dic)
            else:
                for i in range(parent_call_lvl - len(curr_lst) + 1):
                    curr_lst.append({'vals': []})
                # noinspection PyTypeChecker
                curr_lst[parent_call_lvl]['vals'].append(parsed_block_dic)

            
            
            # If detailed info is also being recorded (all region calls),
            # then add the calltree to the structure for the given call
            if detailed_info is not None:
                detailed_info.append((last_calltree.strip(), [e for l in parsed_block_dic.values() for e in l]))

    def get_dic_data(self):
        return self.__dic_data


class SlideshowCreator:
    def __init__(self, tex_file, evaluator, first_data_source_ind=0):
        """
        Input:
            tex_file - objekt typu TexFile
        """
        self.__t_file = tex_file

        self.__first_data_source_ind = first_data_source_ind
        self.__last_data_source_ind = first_data_source_ind

        # Number of inputs for the graphs (1 input = 1 function call)
        self.__num_of_data_sources = 0

        self.__evaluator = evaluator

    def get_ind_of_first_data_source(self):
        return self.__first_data_source_ind

    def get_ind_of_last_data_source(self):
        return self.__last_data_source_ind

    def __add_content_to_tex_file(self, content):
        self.__t_file.insert_text(content)

    def __get2d_plot_header_code(self,
                                 title,
                                 x_label,
                                 y_label,
                                 nth_point=1):

        title = textwrap.dedent(title)

        # TODO add xTick and yTick to header
        code = (r'''
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
                each nth point = {},
                filter discard warning=false
                ]
                \addlegendimage{{empty legend}}
                '''.format(title, x_label, y_label, nth_point))

        return textwrap.dedent(code)

    def __get2d_plot_tex_code(self, data_source_ind):
        """
        Musi byt volano po __prepareInpudDataForPlot!

        Args:
            data_source_ind - index zdroje dat
        """

        code = (r'''\addplot table [x=ind, y=val, col sep=comma] {{data{}.csv}};{}'''.format(data_source_ind,
                                                                                             '\n'))


        code = textwrap.dedent(code)
        return code

    def __get2d_plot_tex_code_coords(self, lst_of_coords, only_marks=False):

        code = (r'''\addplot+ [mark=triangle*{}] coordinates {{ {}
                 }};
                 '''.format(',only marks' if only_marks else '', '\n'.join([str(e) for e in lst_of_coords])))
        code = textwrap.dedent(code)
        return code

    def __get2d_plot_node_tex_code(self, x_coord, y_coord, title='', title_angle=280, title_distance=3):
        code = r'''
                \addplot [only marks] table {{
                    {0} {1}
                }} node [pin={{[pin distance={4}pt]{3}:{{( {2} )}}}}]{{}};
                '''
        code = textwrap.dedent(code)
        code = code.format(x_coord, y_coord,
                           title,
                           title_angle, title_distance)
        return code

    def __get2d_plot_footer(self):
        code = (r'''
                \end{axis}
                \end{tikzpicture}
                \end{adjustbox}'''
                '\n')
        code = textwrap.dedent(code)
        return code

    def __prepare_input_data_for_plot(self, data, border, data_index, shift_to_zero=True, ind1=0, ind2=1):
        """
        Builds data into the filecontents environment,
        so it can be used for plotting graphs.

        Args:
            data - list of tuples with 3 elements
            border - integer
            data_index - integer, index of the data source
            shift_to_zero - boolean, whether the indices
                            should be aligned from 0
                            based on the first element of 'data'
        """

        # Adjust data for writing into the graph
        # -> Subtract ('index' of the 0th sample + border) from all,
        #    so that each graph can be plotted starting at 0, or 0 - border
        if shift_to_zero:
            first_ind = int(data[0][0])
            call_str = ['{},{}\n'.format(float(tup[ind1]) - (first_ind + border), float(tup[ind2])) for tup in data]
        else:
            call_str = ['{},{}\n'.format(tup[ind1], tup[ind2]) for tup in data]

        code = r'''
               \begin{{filecontents*}}{{data{}.csv}}
               ind,val
               {}\end{{filecontents*}}
               '''

        code = textwrap.dedent(code)
        # Add data to code
        code = code.format(data_index, ''.join(call_str))

        return code

    def __prepare_input_data_for_plot_to_csv(self, data, border, shift_to_zero=True, ind1=0, ind2=1):
        """
        Builds data into a CSV file,
        so it can be used for plotting graphs.

        Args:
            data - list of tuples with 3 elements
            border - integer
            dataIndex - integer, index of the data source
            shift_to_zero - boolean, whether the indices
                            should be aligned from 0
                            based on the first element of 'data'
        """

        # Adjust data for writing into the graph
        # -> Subtract ('index' of the 0th sample + border) from all,
        #    so that each graph can be plotted starting at 0, or 0 - border
        if shift_to_zero:
            first_ind = int(data[0][0])
            call_str = ['{},{}\n'.format(float(tup[ind1]) - (first_ind + border), float(tup[ind2])) for tup in data]
        else:
            call_str = ['{},{}\n'.format(tup[ind1], tup[ind2]) for tup in data]

        code = 'ind,val\n{0}'


        code = textwrap.dedent(code)


        code = code.format(''.join(call_str))

        return code

    def __get_plot_legend(self,
                          legend,
                          legend_title=None):
        """
        Args:
            legend - integer/list - number of graphs to be included in this "figure" / names of the graphs
        """

        legend_title = r'\hspace{{-.6cm}} {} '.format(legend_title)

        ret = ''
        if type(legend) is int:
            ret = '\legend{{ {} }}'.format(','.join(filter(None, [legend_title] + [str(i) for i in range(legend)])))
        elif type(legend) is list:
            ret = '\legend{{ {} }}'.format(','.join(filter(None, [legend_title] + [str(item) for item in legend])))

        return ret

    def __get_simple_tree_tex_code(self,
                                   root_title_arg,
                                   children_titles_lst_arg,
                                   sibling_dist=20):

        child_code = r'''child {{ node {{ {0} }} }}'''

        code = r'''
                     \begin{{scaletikzpicturetowidth}}{{\textwidth}}
                     \begin{{tikzpicture}}[scale=\tikzscale,
                                           sibling distance={2}em,
                                           every node/.style = {{scale=\tikzscale,
                                                                 shape=rectangle,
                                                                 rounded corners,
                                                                 draw,
                                                                 align=center}}]]

                             \node{{ {0} }}
                                     {1}
                             ;
                     \end{{tikzpicture}}
                     \end{{scaletikzpicturetowidth}}
                     \pagebreak
                 '''

        child_code = textwrap.dedent(child_code)
        code = textwrap.dedent(code)

        child_codes_lst = []
        for child_title in children_titles_lst_arg:
            child_code_tmp = child_code.format(child_title)
            child_codes_lst.append(child_code_tmp)

        code = code.format(root_title_arg,
                           '\n'.join(child_codes_lst),
                           sibling_dist)

        return code

    def get_section_title_tex_code(self, title):
        code = '\section{{ {} }}\n'
        code = textwrap.dedent(code)
        code = code.format(title)

        return code

    def get_not_numbered_section_title_tex_code(self, title):
        code = '\section*{{ {} }}\n'
        code = textwrap.dedent(code)
        code = code.format(title)

        return code

    def get_sub_section_title_tex_code(self, title):
        code = '\subsection{{ {} }}\n'
        code = textwrap.dedent(code)
        code = code.format(title)

        return code

    def get_not_numbered_sub_section_title_tex_code(self, title):
        code = '\subsection*{{ {} }}\n'
        code = textwrap.dedent(code)
        code = code.format(title)

        return code

    def get_heading_tex_code(self, heading):
        code = r'''
                \begin{{center}}
                    \begin{{Large}}
                        \textbf{{ {0} }}
                    \end{{Large}}
                \end{{center}}
                '''
        code = textwrap.dedent(code).format(heading)

        return code

    def get_num_of_data_sources(self):
        return self.__num_of_data_sources

    def get_func_tree_tex_code(self, root_func_dic, nested_funcs_dic):
        tree_code = self.__get_simple_tree_tex_code(r'{0}\\ \scriptsize{{ {1} }}'.format(tuple(root_func_dic.keys())[0],
                                                                                         tuple(root_func_dic.values())[0]),
                                                    [r'{0}\\ {1}'.format(pos,
                                                                         r'\\ '.join([r'\scriptsize{{ {0} }}'.format(i)
                                                                                      for i in namesLst]))
                                                     for pos, namesLst in nested_funcs_dic.items()]
                                                    )
        return tree_code

    def create_and_add_data_sources_tex_code(self, vals_lst, border, shift_plots_to_zero, ind1, ind2):
        """
        Args:
            border - integer - okraj grafu "mimo funkci" (musi
                               korespondovat s offsetem nastavenym
                               pri mereni!)
            vals_lst - list listu n-tic - souradnice bodu v grafu
            shift_plots_to_zero - boolean
            ind1 - integer - index 1. hodnoty z n-tice
            ind2 - integer - index 2. hodnoty z n-tice
        """
        # From valsList, create additional lists of sources for the graphs
        for func_call_lst in vals_lst:
            # Create a string with point coordinates for the graph
            input_data_str = self.__prepare_input_data_for_plot(func_call_lst, border, self.__last_data_source_ind,
                                                                shift_plots_to_zero, ind1, ind2)
            self.__add_content_to_tex_file(input_data_str)
            self.__last_data_source_ind += 1
            self.__num_of_data_sources += 1

    def create_and_add_data_source(self, vals_lst, border, shift_plots_to_zero, ind1, ind2):
        """
        Args:
            border - integer - okraj grafu "mimo funkci" (musi
                               korespondovat s offsetem nastavenym
                               pri mereni!)
            vals_lst - list listu n-tic - souradnice bodu v grafu
            shift_plots_to_zero - boolean
            ind1 - integer - index 1. hodnoty z n-tice
            ind2 - integer - index 2. hodnoty z n-tice
        """
        # From valsList, create additional lists of sources for the graphs
        for func_call_lst in vals_lst:
            # Create a string with point coordinates for the graph
            input_data_str = self.__prepare_input_data_for_plot_to_csv(func_call_lst, border,
                                                                       shift_plots_to_zero, ind1, ind2)

            f = open('data{}.csv'.format(self.__last_data_source_ind), 'w+')
            f.write(input_data_str)
            f.close()

            self.__last_data_source_ind += 1
            self.__num_of_data_sources += 1

    def create_samples_plot_tex_code(self,
                                     title,
                                     data_source_inds,
                                     nth_point=1,
                                     legend_title=None):
        """
        Input:
            title - string - graph title
            data_source_inds - list - indices of sources
            nth_point - int - which element to plot (every nth) – used to "thin out" dense graphs
        """

        # Create the header of the graph code
        code = self.__get2d_plot_header_code(title, 'Number of samples', 'Power [W]', nth_point)

        self.__add_content_to_tex_file(code)

        for ind in data_source_inds:
            plot_tex_code = self.__get2d_plot_tex_code(ind)
            self.__add_content_to_tex_file(plot_tex_code)

        plot_legend = self.__get_plot_legend(len(data_source_inds), legend_title)
        self.__add_content_to_tex_file(plot_legend)

        code = self.__get2d_plot_footer()

        self.__add_content_to_tex_file(code)

    def create_summary_plot_tex_code(self,
                                     title,
                                     x_axis_title,
                                     y_axis_title,
                                     data_source_inds,
                                     func_label_arg,
                                     highlight=None,
                                     highlight_title=None,
                                     legend_title=None):
        """
        Input:
            title - string - titulek grafu
            data_source_inds - list - indexy zdroju
            func_label_arg - list - pouzite pocty jader (slouzi jako labely ke grafum)
            highlight - tuple - souradnice vyznacneho bodu
            highlight_title - string - titulek zvyrazneneho bodu
        """

        code = self.__get2d_plot_header_code(title, x_axis_title, y_axis_title)

        self.__add_content_to_tex_file(code)

        for ind in data_source_inds:
            plot_tex_code = self.__get2d_plot_tex_code(ind)
            self.__add_content_to_tex_file(plot_tex_code)

        plot_legend = self.__get_plot_legend(list(func_label_arg), legend_title)
        self.__add_content_to_tex_file(plot_legend)


        if highlight:
            code = self.__get2d_plot_node_tex_code(highlight[0],
                                                   highlight[1],
                                                   highlight_title,
                                                   270,
                                                   0)
            self.__add_content_to_tex_file(code)

        code = self.__get2d_plot_footer()

        self.__add_content_to_tex_file(code)

    def get_summary_plot_tex_code_coords(self,
                                         title,
                                         x_axis_title,
                                         y_axis_title,
                                         data_lst,
                                         func_label_arg,
                                         highlight=None,
                                         highlight_title=None,
                                         legend_title=None,
                                         only_marks=False):
        code_lst = []

        code_lst.append(self.__get2d_plot_header_code(title, x_axis_title, y_axis_title))

        for lst_of_coords in data_lst:
            plot_tex_code = self.__get2d_plot_tex_code_coords(lst_of_coords, only_marks)
            code_lst.append(plot_tex_code)

        code_lst.append(self.__get_plot_legend(list(func_label_arg),
                                               legend_title if legend_title is not None else ''))


        if highlight:
            code_lst.append(self.__get2d_plot_node_tex_code(highlight[0],
                                                            highlight[1],
                                                            highlight_title,
                                                            240,
                                                            1))

        code_lst.append(self.__get2d_plot_footer())

        return '\n'.join(code_lst)

    def create_summary_plot_tex_code_coords(self,
                                            title,
                                            x_axis_title,
                                            y_axis_title,
                                            data_lst,
                                            func_label_arg,
                                            highlight=None,
                                            highlight_title=None,
                                            legend_title=None,
                                            only_marks=False):

        code = self.__get2d_plot_header_code(title, x_axis_title, y_axis_title)

        self.__add_content_to_tex_file(code)

        for lst_of_coords in data_lst:
            plot_tex_code = self.__get2d_plot_tex_code_coords(lst_of_coords, only_marks)
            self.__add_content_to_tex_file(plot_tex_code)

        plot_legend = self.__get_plot_legend(list(func_label_arg), legend_title)
        self.__add_content_to_tex_file(plot_legend)


        if highlight:
            code = self.__get2d_plot_node_tex_code(highlight[0],
                                                   highlight[1],
                                                   highlight_title,
                                                   240,
                                                   1)
            self.__add_content_to_tex_file(code)

        code = self.__get2d_plot_footer()

        self.__add_content_to_tex_file(code)

    def create_heat_map(self,
                        x_labels,
                        func_labels,
                        vals_lst,
                        x_label_unit='',
                        func_label_unit='',
                        title=''):
        code = r'''
                \begin{{table}}[H]
                \centering
                {0}
                \begin{{adjustbox}}{{max width=\textwidth}}
                \def\tablePrec{{3}}
                \def\labelPrec{{1}}
                \pgfplotstabletypeset[
                    col sep=comma,
                    row sep=\\,
                    color cells={{min={1}, max={2}, textcolor=black}},
                    /pgfplots/colormap={{CM}}{{rgb255=(0,204,0) rgb255=(255,255,51)  rgb255=(255,51,51)}},
                    /pgf/number format/fixed,
                    /pgf/number format/precision=\the\numexpr\tablePrec,
                    columns/xLabels/.style={{
                        column name={{ {3} }},
                        preproc cell content/.style={{
                            /pgf/number format/precision=\the\numexpr\labelPrec
                        }},
                        postproc cell content/.style={{
                            /pgfplots/table/@cell content.add={{\cellcolor{{white}}}}
                        }}
                    }}
                ]
                {{
                {4}\\
                }}
                \end{{adjustbox}}                
                \end{{table}}
                '''
        code = textwrap.dedent(code)

        table_header_line = ','.join(['xLabels'] + list(func_labels))
        table_data_lines = [','.join([str(e) for e in tup]) for tup in list(zip(*[x_labels] + vals_lst))]

        code = code.format(r'\caption*{{ {} }}'.format(title) if title != '' else '',
                           min(min(vals_lst)),
                           max(max(vals_lst)),
                           r''
                           if all(e == '' for e in (x_label_unit, func_label_unit))
                           else r'$\frac{{ \text{{ {} }} }}{{ \text{{ {} }} }}$'.format(func_label_unit, x_label_unit),
                           '\\\ \n'.join([table_header_line] + table_data_lines)
                           )

        self.__add_content_to_tex_file(code)

    def create_cluster_analysis_tex_code(self, y_labels, detail_data):
        code = '''\newpage
                {}
                {{}}'''

        code.format(self.get_section_title_tex_code('Cluster analysis'))

        code_lst = []

        clustered_detail_data = self.__evaluator.perform_DBSCAN(y_labels, detail_data)

        for ind, dic in enumerate(clustered_detail_data.values()):
            code_lst.append(self.get_heading_tex_code(r'{}'.format(y_labels[ind]['arg'])))
            for reg, lst in dic.items():
                code_lst.append(self.get_heading_tex_code(r'Region: {}'.format(reg)))
                cluster_ind = 0  # Actual index  of cluster
                code_lst.append(self.get_heading_tex_code(r'Cluster {}:'.format(cluster_ind)))

                for tup in lst:
                    # Reading and update of index of cluster
                    if tup[2] != cluster_ind:
                        cluster_ind = tup[2]
                        code_lst.append(self.get_heading_tex_code(r'Cluster {}:'.format(cluster_ind)))

                    # tup[0] - calltree, tup[1] - value,
                    # tup[2] - index of cluster
                    code_lst.append(r'{}\\ {}\\'.format(tup[0].replace('#', '\#'), tup[1]))

                code_lst.append(self.get_summary_plot_tex_code_coords('',
                                                                      '{} [{}]'.format(y_labels[ind]['arg'],
                                                                                       y_labels[ind]['unit']),
                                                                      '',
                                                                      [list(zip([e[1] for e in lst], [1] * len(lst)))],
                                                                      ['Values'],
                                                                      only_marks=True))

        return '\n'.join(code_lst)


class FilenameArgsContainer:
    def __init__(self, args_lst):
        # argsTup example:
        # [['xLabel', 'Frequency'],
        #  ['config', 'Preconditioner'],
        #  ['funcLabel', 'Num of cores'],
        #  ['config', 'Schur complement']
        # ]

        self.__params_values_dic = args_lst.copy()
        self.__params_values_dic_len = len(self.__params_values_dic)

        for e in self.get_lst_of_position_names():
            if e not in ['key', 'config', 'xLabel', 'funcLabel', 'ignore']:
                utils.print_err('Bad category "{}" in the "filename args" variable! The only allowed categories are '
                                '"config", "key", "xLabel", "funcLabel" and "ignore".'.format(e))

        x_label_num = len(self.__get_lst_of_vals_from_args_tup('xLabel'))
        func_label_num = len(self.__get_lst_of_vals_from_args_tup('funcLabel'))
        config_lst_len = len(self.__get_lst_of_vals_from_args_tup('config'))
        # commonKeysNum = len(self.__get_lst_of_vals_from_args_tup('key'))

        # Add None for missing config and funcLabel
        # TODO handle consistently with 'keys'
        if func_label_num == 0:
            self.__params_values_dic.append(['funcLabel', None])

        if config_lst_len == 0:
            self.__params_values_dic.append(['config', None])

        # Check error inputs
        if x_label_num == 0:
            utils.print_err('Compulsory xLabel parameter is missing!')

        elif x_label_num > 1 or func_label_num > 1:
            utils.print_err('Both x_label_num and func_label_num must have only one value!')

        elif not self.__get_lst_of_vals_from_args_tup('xLabel')[0]:
            utils.print_err('xLabel is obligatory - its value can\'t be None!')

        if not self.__is_set('funcLabel'):
            for tup in self.__params_values_dic:
                if tup[0] == 'funcLabel':
                    tup[1] = ''
                    break

        if not self.__is_set('config'):
            for tup in self.__params_values_dic:
                if tup[0] == 'config':
                    tup[1] = ()
                    break

    def __is_set(self, key):
        return bool(self.__get_lst_of_vals_from_args_tup(key)[0])

    def __get_lst_of_vals_from_args_tup(self, key):
        return [tup[1] for tup in self.__params_values_dic if tup[0] == key]

    def get_x_label(self):
        return self.__get_lst_of_vals_from_args_tup('xLabel')[0]

    def get_func_label(self):
        return self.__get_lst_of_vals_from_args_tup('funcLabel')[0]

    def get_config_lst(self):
        return self.__get_lst_of_vals_from_args_tup('config')

    def get_common_keys_lst(self):
        return self.__get_lst_of_vals_from_args_tup('key')

    def get_lst_of_params(self):
        key_lst = []
        for arg in [tup[1] for tup in self.__params_values_dic]:
            if isinstance(arg, (list, tuple)):
                if len(arg) == 0:
                    key_lst.append(arg)
                else:
                    key_lst.extend(arg)
            else:
                key_lst.append(arg)

        return key_lst

    def get_lst_of_position_names(self):
        key_lst = []
        for arg in [tup[0] for tup in self.__params_values_dic]:
            if isinstance(arg, (list, tuple)):
                if len(arg) == 0:
                    key_lst.append(arg)
                else:
                    key_lst.extend(arg)
            else:
                key_lst.append(arg)

        return key_lst

    def get_keys_vals_from_dic(self, dic):
        return [dic[k] for k in self.get_common_keys_lst()]

    def get_x_label_val_from_dic(self, dic):
        return dic[self.get_x_label()]

    def get_func_label_val_from_dic(self, dic):
        return dic[self.get_func_label()]

    def get_num_of_params(self):
        return self.__params_values_dic_len

    def get_pattern_for_params(self, x_lab=None, func_lab=None, keys_lst=None, config_lst=None):
        #TODO finish
        pass


class OptimalAndDefaultValsContainer:
    def __init__(self,
                 region_name,
                 dic_arg,
                 data_category):
        self.__region_name = region_name
        self.__dic = dic_arg
        self.__data_category = data_category

    def get_region_name(self):
        return self.__region_name

    def get_data_category(self):
        return self.__data_category

    def get_raw_data_dic(self):
        return self.__dic


class DataContainer:
    def __init__(self,
                 region_name,
                 summary_sources_dic_arg,
                 evaluated_vars):
        self.__summary_sources_dic = summary_sources_dic_arg
        # self.__sampleSourcesIndsDic = sampleSourcesIndsDicArg
        self.__region_name = region_name
        self.__evaluated_vars = evaluated_vars
        self.__evaluated_vars_num = len(self.__evaluated_vars)
        self.__baseline_strategy = None

    def get_evaluated_vars(self):
        return self.__evaluated_vars

    def get_ith_evaluated_var(self, ind):
        return self.__evaluated_vars[ind]

    def get_evaluated_vars_num(self):
        return self.__evaluated_vars_num

    def get_region_name(self):
        return self.__region_name

    def get_raw_summary_sources_dic(self):
        return self.__summary_sources_dic

    # def getRawSampleSourcesIndsDic(self):
    #    return self.__sampleSourcesIndsDic

    def get_avg_vals_dic(self):
        return self.__summary_sources_dic['avg']['vals']

    def get_full_vals_dic(self):
        return self.__summary_sources_dic['full']['vals']

    def get_min_vals_dic(self):
        return self.__summary_sources_dic['min']['vals']

    def get_max_vals_dic(self):
        return self.__summary_sources_dic['max']['vals']

    def get_configurations(self):
        return list(self.get_avg_vals_dic().keys())

    def set_baseline_strategy(self, strategy):
        self.__baseline_strategy = strategy

    def apply_baseline_strategy(self, baseline, data, eng_ind, time_ind, settings_lst):
        self.__baseline_strategy.apply_base(baseline, data, eng_ind, time_ind, settings_lst)

    def __get_optimal_and_default_full_vals_per_func_label(self,
                                                           conf,
                                                           path,
                                                           items,
                                                           optim_func,
                                                           ret_dic_wrapper):
        optim_tmp_avg_program_start = list()
        optim_tmp_single_program_starts = list()  # List of listu (for each runtime)
        func_label_ind = -1
        for func_label, vals in items.items():
            func_label_ind += 1

            # Getting optimum for each average runtime
            num_of_iters = len(vals['avgProgramStart'][0][1])

            for iter_ind in range(num_of_iters):
                if len(optim_tmp_avg_program_start) < num_of_iters or \
                        (len(optim_tmp_avg_program_start) == num_of_iters and func_label_ind == 0):
                    optim_tmp_avg_program_start.append(list())

                try:
                    tmp = [optim_func([(e[0], e[1][iter_ind][i])
                                       for e
                                       in vals['avgProgramStart']
                                       if e[1][iter_ind][i] is not None and e[1][iter_ind][i] > 0],
                                      key=lambda e: e[1])
                           for i in range(self.get_evaluated_vars_num())]
                except ValueError:
                    # If all settings in the iteration are 0 (the region
                    # does not "run" in the iteration, etc.)

                    tmp = tuple((None, None) for _ in range(self.get_evaluated_vars_num()))

                optim_tmp_avg_program_start[iter_ind].append([(func_label,) + e for e in tmp])

            # Obtaining the optimum for each iteration
            # from individual program runs
            for single_program_start_ind, single_program_start in enumerate(vals['singleProgramStarts']):
                optim_tmp_single_program_start = list()
                max_num_of_iters_in_program_start = len(max(single_program_start, key=lambda e: len(e[1]))[1])

                # Iterating through the records of one program run
                # across individual iterations
                for single_iter_ind in range(max_num_of_iters_in_program_start):
                    if len(optim_tmp_single_program_start) <= single_iter_ind:
                        optim_tmp_single_program_start.append(list())

                    try:
                        tmp = [optim_func([(e[0], e[1][single_iter_ind][i]['sumVal'])
                                           for e
                                           in single_program_start
                                           if len(e[1]) > single_iter_ind and e[1][single_iter_ind][i]['sumVal']],
                                          key=lambda e: e[1])
                               for i in range(self.get_evaluated_vars_num())]
                    except ValueError:
                        # Missing values for the iteration in all settings
                        tmp = tuple((None, None) for _ in range(self.get_evaluated_vars_num()))

                    optim_tmp_single_program_start[single_iter_ind].append([(func_label,) + e for e in tmp])

                if len(optim_tmp_single_program_starts) <= single_program_start_ind:
                    optim_tmp_single_program_starts.append([list()]*max_num_of_iters_in_program_start)

                for e_ind, e in enumerate(optim_tmp_single_program_start):
                    try:
                        optim_tmp_single_program_starts[single_program_start_ind][e_ind].extend(e)
                    except IndexError:
                        # When the number of iterations differs for func_label
                        optim_tmp_single_program_starts[single_program_start_ind].append(list())
                        optim_tmp_single_program_starts[single_program_start_ind][e_ind].extend(e)

        avg_tmp = []
        for single_iter in optim_tmp_avg_program_start:
            try:
                avg_tmp.append([optim_func([el[i] for el in single_iter],
                                           key=lambda e: e[2])
                                for i in range(self.get_evaluated_vars_num())])
            except TypeError:
                avg_tmp.append([(None, None, None) for _ in range(self.get_evaluated_vars_num())])

        single_tmp = []
        for single_program_start in optim_tmp_single_program_starts:
            tmp = list()
            for single_iter in single_program_start:
                try:
                    tmp.append([optim_func([el[i] for el in single_iter],
                                           key=lambda e: e[2])
                                for i in range(self.get_evaluated_vars_num())])
                except TypeError:
                    tmp.append([(None, None, None) for _ in range(self.get_evaluated_vars_num())])

            single_tmp.append(tmp)

        def_optim_dic = {'avgProgramStart': avg_tmp,
                         'singleProgramStarts': single_tmp}

        ret_dic_wrapper[conf][tuple(path)] = def_optim_dic

    def __get_optimal_and_default_vals_per_func_label(self,
                                                      conf,
                                                      path,
                                                      items,
                                                      optim_func,
                                                      ret_dic_wrapper):

        # Obtaining the optimum and default value
        # for each func_label separately
        optim_tmp_avg_program_start = list()
        optim_tmp_single_program_starts = list()  
        for func_label, vals in items.items():
            try:
                # noinspection PyTypeChecker
                tmp = tuple(optim_func(((v[0], v[1][i])
                                        for v
                                        in vals['avgProgramStart']
                                        if v[1][i] > 0),
                                       key=lambda e: e[1])
                            for i
                            in range(self.get_evaluated_vars_num()))
                optim_tmp_avg_program_start.append((func_label,) + (tmp,))
            except ValueError:
                utils.print_err('Computing optimal values - check your defaultLabelVal '
                                'variable and CSV files with measured data (possibly no samples saved?).\n\n'
                                ''
                                'Check especially CSV file for region {regName} with configuration {config} and '
                                'func_label '
                                '{func_label}'.format(regName=self.get_region_name(),
                                                      config=conf,
                                                      func_label=func_label))

            for prog_start_ind, progStart in enumerate(vals['singleProgramStarts']):
                if len(optim_tmp_single_program_starts) <= prog_start_ind:
                    optim_tmp_single_program_starts.append(list())

                try:
                    # noinspection PyTypeChecker
                    tmp = tuple(optim_func(((v[0], v[1][i])
                                            for v
                                            in vals['avgProgramStart']
                                            if v[1][i] > 0),
                                           key=lambda e: e[1])
                                for i
                                in range(self.get_evaluated_vars_num()))
                    optim_tmp_single_program_starts[prog_start_ind].append((func_label,) + (tmp,))
                except ValueError:
                    utils.print_err('Computing optimal values - check your defaultLabelVal '
                                    'variable and CSV files with measured data (possibly no samples saved?).\n\n'
                                    'Check especially CSV file for region {regName} with configuration {config} '
                                    'and func_label {func_label}'.format(regName=self.get_region_name(),
                                                                         config=conf,
                                                                         func_label=func_label))

        # Getting optimum of all labels
        def_optim_dic = {'avgProgramStart': [optim_func(((v[0], *v[1][i])
                                                         for v
                                                         in optim_tmp_avg_program_start),
                                                        key=lambda e: e[2])
                                             for i
                                             in range(self.get_evaluated_vars_num())],
                         'singleProgramStarts': [[optim_func(((v[0], *v[1][i])
                                                              for v
                                                              in progStart),
                                                             key=lambda e: e[2])
                                                  for i
                                                  in range(self.get_evaluated_vars_num())]
                                                 for progStart in optim_tmp_single_program_starts]}

        ret_dic_wrapper[conf][tuple(path)] = def_optim_dic

    def __process_keys_optims(self,
                              nested,
                              path,
                              conf,
                              optim_func,
                              ret_dic_wrapper,
                              get_optim_and_default_function):

        for ind, item in enumerate(nested):
            if 'avgProgramStart' in nested[item]:
                get_optim_and_default_function(conf,
                                               path,
                                               nested,
                                               optim_func,
                                               ret_dic_wrapper)
            elif 'avgProgramStart' in list(nested[item].values())[0]:
                get_optim_and_default_function(conf,
                                               path + [item],
                                               nested[item],
                                               optim_func,
                                               ret_dic_wrapper)

            else:
                self.__process_keys_optims(nested[item],
                                           path + [item],
                                           conf,
                                           optim_func,
                                           ret_dic_wrapper,
                                           get_optim_and_default_function)

    def get_optimal_and_default_vals(self,
                                     data_category,
                                     default_label_val_or_parent_reg,
                                     default_keys=None,
                                     default_x_val=None,
                                     global_default_label=None,
                                     global_default_x_val=None,
                                     optim_func=min,
                                     filename_args=None):
        # TODO rewrite using the Strategy design pattern!

        # TODO verify input for global*** parameters

        # Round default values to avoid inaccuracies during multiplication
        try:
            default_x_val = round(default_x_val, 2)
        except TypeError:
            pass

        try:
            default_label_val_or_parent_reg = round(default_label_val_or_parent_reg, 2)
        except TypeError:
            pass

        # Check of inputs
        if optim_func not in (min, max):
            utils.print_err('Bad value of \'optim_func\' parameter - acceptable values '
                            'are (min, max).')

        if data_category not in ('avg', 'full', 'min', 'max'):
            utils.print_err('Bad value of \'data_category\' parameter - acceptable values '
                            'are (\'avg\', \'full\', \'min\', \'max\').')

        # Loaded values
        src_data_dic = self.__summary_sources_dic[data_category]['vals']

        # Dictionary with optima and default values
        # returned by this method
        ret_dic = dict()


        parent_reg_oa_d = None
        default_label_val = None
        if default_x_val:
            default_keys = [default_keys]*self.get_evaluated_vars_num()
            default_x_val = [default_x_val]*self.get_evaluated_vars_num()
            default_label_val = [default_label_val_or_parent_reg]*self.get_evaluated_vars_num()
        else:
            assert (isinstance(default_label_val_or_parent_reg, OptimalAndDefaultValsContainer))
            assert (default_label_val_or_parent_reg.get_data_category() in ('avg', 'min', 'max'))
            parent_reg_oa_d = default_label_val_or_parent_reg.get_raw_data_dic()

        if data_category == 'full':
            ret_dic_wrapper = {}

            for conf in src_data_dic:
                ret_dic_wrapper[conf] = {}

                if parent_reg_oa_d:
                    default_label_val = [parent_reg_oa_d[conf]['optimalVal']['avgProgramStart'][i]['funcLabel']
                                         for i in range(self.get_evaluated_vars_num())]
                    default_x_val = [parent_reg_oa_d[conf]['optimalVal']['avgProgramStart'][i]['xVal']
                                     for i in range(self.get_evaluated_vars_num())]
                    default_keys = [parent_reg_oa_d[conf]['optimalVal']['avgProgramStart'][i]['keys']
                                    for i in range(self.get_evaluated_vars_num())]

                self.__process_keys_optims(src_data_dic[conf],
                                           [],
                                           conf,
                                           optim_func,
                                           ret_dic_wrapper,
                                           self.__get_optimal_and_default_full_vals_per_func_label)

                # Get the optimal value from optima for individual "branches"
                def_optim_dic = {'avgProgramStart': [],
                                 'singleProgramStarts': []}

                for keys_tup, localOptimVals in ret_dic_wrapper[conf].items():
                    # Get the optimum over average iterations
                    for iter_ind, avgIter in enumerate(localOptimVals['avgProgramStart']):
                        if len(def_optim_dic['avgProgramStart']) == iter_ind:
                            def_optim_dic['avgProgramStart'].append([{'keys': keys_tup,
                                                                      'funcLabel': avgIter[i][0],
                                                                      'xVal': avgIter[i][1],
                                                                      'yVal': avgIter[i][2]}
                                                                     for i in range(self.get_evaluated_vars_num())])

                        else:
                            try:
                                for i in range(self.get_evaluated_vars_num()):
                                    if avgIter[i][-1] == optim_func(def_optim_dic['avgProgramStart'][iter_ind][i]['yVal'],
                                                                    avgIter[i][-1]):
                                        def_optim_dic['avgProgramStart'][iter_ind][i] = {'keys': keys_tup,
                                                                                         'funcLabel': avgIter[i][0],
                                                                                         'xVal': avgIter[i][1],
                                                                                         'yVal': avgIter[i][2]}
                            except TypeError:
                                utils.print_err('Zero values in CSV! Maybe the region \'{}\' is too short?\n'
                                                'Configuration: {}\n'
                                                'Keys: {}\n'
                                                'Iteration index: {}'
                                                .format(self.get_region_name(),
                                                        conf,
                                                        keys_tup,
                                                        iter_ind))

                    # Get the optimum for individual iterations
                    for start_ind, singleStart in enumerate(localOptimVals['singleProgramStarts']):
                        if len(def_optim_dic['singleProgramStarts']) == start_ind:
                            def_optim_dic['singleProgramStarts'].append(list())

                        for iter_ind, singleIter in enumerate(singleStart):
                            if len(def_optim_dic['singleProgramStarts'][start_ind]) == iter_ind:
                                def_optim_dic['singleProgramStarts'][start_ind].append([{'keys': keys_tup,
                                                                                         'funcLabel': str(singleIter[i][0]),
                                                                                         'xVal': singleIter[i][1],
                                                                                         'yVal': singleIter[i][2]}
                                                                                        for i in range(self.get_evaluated_vars_num())])

                            else:
                                for i in range(self.get_evaluated_vars_num()):
                                    if singleIter[i][-1] == optim_func(def_optim_dic['singleProgramStarts'][start_ind][iter_ind][i]['yVal'],
                                                                       singleIter[i][-1]):
                                        def_optim_dic['singleProgramStarts'][start_ind][iter_ind][i] = {'keys': keys_tup,
                                                                                                        'funcLabel': str(singleIter[i][0]),
                                                                                                        'xVal': singleIter[i][1],
                                                                                                        'yVal': singleIter[i][2]}

                # Get default value
                def_default_dic = None

                # Iterate over the "default" keys
                # TODO rewrite like for avg values to improve the error message
                try:
                    # TODO DO NOT DUPLICATE the tree – it already contains all variables
                    data = [utils.get_obj_from_path(default_keys[i], src_data_dic[conf])
                            for i in range(self.get_evaluated_vars_num())]
                except KeyError:
                    utils.print_err("Bad defKeyVals value!")

                try:
                    single_program_starts_tmp = list()
                    for prog_start_ind, singleProgramStart in enumerate(def_optim_dic['singleProgramStarts']):
                        single_prog_start_data_tmp = list()

                        for iter_ind in range(len(singleProgramStart)):

                            def_label = default_label_val
                            try:
                                def_label_tmp = [data[i][str(default_label_val[i])]
                                                 for i in range(self.get_evaluated_vars_num())]
                            except KeyError:
                                def_label_tmp = [data[i][str(global_default_label)]
                                                 for i in range(self.get_evaluated_vars_num())]
                                def_label = [global_default_label]*self.get_evaluated_vars_num()

                            # Select data for the default x value for each iteration
                            # If there is no iteration for the optimum from the parent region,
                            # the global optimum (from the config file) is used

                            def_x_val_tmp = []
                            for i in range(self.get_evaluated_vars_num()):
                                try:
                                    def_x_val_tmp.append(def_label_tmp[i]['singleProgramStarts'][prog_start_ind])
                                except IndexError:
                                    utils.print_err('Loading default values - check your CSV files with measured '
                                                    'data \n'
                                                    'corresponding to following settings. Data for {}. program start '
                                                    '(init_{}) '
                                                    'are probably missing.\n\n'
                                                    ''
                                                    'Region: {}\n'
                                                    'Func-value: {}'.format(prog_start_ind+1,
                                                                            prog_start_ind,
                                                                            self.get_region_name(),
                                                                            def_label[i]))

                                # TODO add auto-detection of files with missing data
                                #if filename_args:
                                #    pattern_tmp = filename_args.get_pattern_for_params(func_lab=def_label[i_tmp])
                                #tmp = utils.find_str_in_files('{}/{}'self.get_region_name())


                            def_x_val_tup = []
                            for i in range(self.get_evaluated_vars_num()):
                                item_added = False
                                for tup in def_x_val_tmp[i]:
                                    if tup[0] == default_x_val[i]:
                                        def_x_val_tup.append(tup)
                                        item_added = True

                                # Check whether values were found for all evaluated variables
                                if not item_added:
                                    utils.print_err('\nProblem with loading default values in the region {}. '
                                                    'Maybe missing data for {}. program start (init_{} in '
                                                    'CSV CALLTREE)?\n\n'
                                                    'File:\n'
                                                    'x-value: {}\n'
                                                    'func-value: {}\n'
                                                    'keys: {}'
                                                    .format(self.get_region_name(),
                                                            prog_start_ind+1,
                                                            prog_start_ind,
                                                            default_x_val[i],
                                                            def_label[i],
                                                            default_keys[i]))

                            try:
                                single_prog_start_data_tmp.append([{'keys': default_keys[i],
                                                                    'funcLabel': str(def_label[i]),
                                                                    'xVal': default_x_val[i],
                                                                    'yVal': def_x_val_tup[i][1][iter_ind][i]['sumVal']}
                                                                   for i in range(self.get_evaluated_vars_num())])
                            except IndexError:
                                # If there is no iteration for the given default configuration (for the static optimum), try
                                # using the global default settings (from config.py)
                                try:
                                    def_x_val_tup = [[tup for tup in def_x_val_tmp[i] if tup[0] == global_default_x_val][0]
                                                     for i in range(self.get_evaluated_vars_num())]
                                    single_prog_start_data_tmp.append([{'keys': default_keys[i],
                                                                        'funcLabel': str(def_label[i]),
                                                                        'xVal': default_x_val[i],
                                                                        'yVal': def_x_val_tup[i][1][iter_ind][i]['sumVal']}
                                                                       for i in range(self.get_evaluated_vars_num())])
                                except IndexError:
                                    # If there is no iteration even for the global default settings, the iteration will not be evaluated
                                    # (the column in the report will be filled with dashes)
                                    single_prog_start_data_tmp.append([{'keys': (None,),
                                                                        'funcLabel': None,
                                                                        'xVal': None,
                                                                        'yVal': None}
                                                                       for _ in range(self.get_evaluated_vars_num())])

                        single_program_starts_tmp.append(single_prog_start_data_tmp)

                    def_default_dic = {'avgProgramStart': [[{'keys': default_keys[i],
                                                             'funcLabel': str(default_label_val[i]),
                                                             'xVal': tup[0],
                                                             'yVal': tup[1][iter_ind][i]}
                                                            for tup
                                                            in data[i][str(default_label_val[i])]['avgProgramStart']
                                                            for iter_ind
                                                            in range(len(tup[1]))
                                                            if tup[0] == default_x_val[i]]
                                                           for i in range(self.get_evaluated_vars_num())],
                                       'singleProgramStarts': single_program_starts_tmp}
                except IndexError:
                    utils.print_err('Loading default values - check your def_x_val '
                                    'variable and CSV file with measured data.\n\n'
                                    ''
                                    'Region: {}\n'
                                    'Default x-value: {}'.format(self.get_region_name(), default_x_val))
                except KeyError:
                    utils.print_err('Loading default values - check your def_label_val '
                                    'variable and CSV file with measure data.\n\n'
                                    ''
                                    'Region: {}\n'
                                    'Default x-value: {}'.format(self.get_region_name(), default_label_val))

                ret_dic[conf] = dict(defaultVal=def_default_dic,
                                     optimalVal=def_optim_dic)
        else:
            ret_dic_wrapper = {}

            for conf in src_data_dic:
                ret_dic_wrapper[conf] = {}

                if parent_reg_oa_d:
                    default_label_val = [parent_reg_oa_d[conf]['optimalVal']['avgProgramStart'][i]['funcLabel']
                                         for i in range(self.get_evaluated_vars_num())]
                    default_x_val = [parent_reg_oa_d[conf]['optimalVal']['avgProgramStart'][i]['xVal']
                                     for i in range(self.get_evaluated_vars_num())]
                    default_keys = [parent_reg_oa_d[conf]['optimalVal']['avgProgramStart'][i]['keys']
                                    for i in range(self.get_evaluated_vars_num())]

                self.__process_keys_optims(src_data_dic[conf],
                                           [],
                                           conf,
                                           optim_func,
                                           ret_dic_wrapper,
                                           self.__get_optimal_and_default_vals_per_func_label)

                # Get the optimal value from the optima for individual "branches"

                def_optim_dic = {'avgProgramStart': [None]*self.get_evaluated_vars_num(),
                                 'singleProgramStarts': []}
                for keys_tup, localOptimVals in ret_dic_wrapper[conf].items():
                    # Get the optimum for the average program run
                    for i in range(self.get_evaluated_vars_num()):
                        # noinspection PyTypeChecker
                        if def_optim_dic['avgProgramStart'][i] is None \
                                or localOptimVals['avgProgramStart'][i][-1] == optim_func(localOptimVals['avgProgramStart'][i][-1],
                                                                                          def_optim_dic['avgProgramStart'][i]['yVal']):
                            tmp = localOptimVals['avgProgramStart'][i]
                            def_optim_dic['avgProgramStart'][i] = {'keys': keys_tup,
                                                                   'funcLabel': tmp[0],
                                                                   'xVal': tmp[1],
                                                                   'yVal': tmp[2]}

                    # Get the optimum for individual program runs
                    for start_ind, singleStart in enumerate(localOptimVals['singleProgramStarts']):
                        if start_ind == len(def_optim_dic['singleProgramStarts']):
                            tmp = [None]*self.get_evaluated_vars_num()
                            def_optim_dic['singleProgramStarts'].append(tmp)
                            for i in range(self.get_evaluated_vars_num()):
                                tmp[i] = {'keys': keys_tup,
                                          'funcLabel': singleStart[i][0],
                                          'xVal': singleStart[i][1],
                                          'yVal': singleStart[i][2]}
                        else:
                            for i in range(self.get_evaluated_vars_num()):
                                if singleStart[i][-1] == optim_func(singleStart[i][-1],
                                                                    def_optim_dic['singleProgramStarts'][start_ind][i]['yVal']):
                                    def_optim_dic['singleProgramStarts'][start_ind][i] = {'keys': keys_tup,
                                                                                          'funcLabel': singleStart[i][0],
                                                                                          'xVal': singleStart[i][1],
                                                                                          'yVal': singleStart[i][2]}

                # Get the default value
                def_default_dic = None

                # Go through the "default" keys
                # TODO DO NOT DUPLICATE the tree - it already contains all variables
                data = []
                for i in range(self.get_evaluated_vars_num()):
                    try:
                        data.append(utils.get_obj_from_path(default_keys[i], src_data_dic[conf]))
                    except KeyError:
                        utils.print_err("There are no data for keys \'{}\' in \n"
                                        "Region: {}\n"
                                        "Configuration: {}"
                                        .format(', '.join(default_keys[i]),
                                                self.get_region_name(),
                                                ', '.join(conf)))

                try:
                    # TODO remove commented code snippet
                    '''
                    avg_prog_start_vals_tmp = tuple([(e[0], e[1][i])
                                                     for e
                                                     in data[i][str(default_label_val[i])]['avgProgramStart']
                                                     if e[0] == default_x_val[i] and e[1][i] > 0][0]
                                                    for i
                                                    in range(self.get_evaluated_vars_num()))
                    '''
                    tmp = [None] * self.get_evaluated_vars_num()
                    for i in range(self.get_evaluated_vars_num()):
                        for e in data[i][str(default_label_val[i])]['avgProgramStart']:
                            if e[0] == default_x_val[i] and e[1][i] > 0:
                                tmp[i] = (e[0], e[1][i])

                        if tmp[i] is None:
                            utils.print_err('Loading default values problem - missing or zero values in CSV? \n'
                                            'Settings:\n'
                                            'Region: {reg}\n'
                                            'Configuration: {conf}\n'
                                            'x-label: {x}\n'
                                            'func-label: {f}\n'
                                            'keys: {k}\n'
                                            'Variable evaluated: {vars}\n'.format(conf=conf,
                                                                                  x=default_x_val[i],
                                                                                  f=default_label_val[i],
                                                                                  k=' '.join([str(e)
                                                                                              for e
                                                                                              in default_keys[i]]),
                                                                                  vars=self.get_evaluated_vars()[i],
                                                                                  reg=self.get_region_name()))

                    avg_prog_start_vals_tmp = tuple(tmp)

                    # Prepare the structure for storing default values
                    num_of_prog_starts = len(data[0][str(default_label_val[0])]['singleProgramStarts'])
                    single_prog_start_vals_tmp = [[None] * self.get_evaluated_vars_num() for _ in
                                                  range(num_of_prog_starts)]
                    
                    # Save the default values
                    for i in range(self.get_evaluated_vars_num()):
                        for prog_start_ind, prog_start in enumerate(
                                data[i][str(default_label_val[i])]['singleProgramStarts']):
                            for e in prog_start:
                                if e[0] == default_x_val[0] and e[1][i] > 0:
                                    single_prog_start_vals_tmp[prog_start_ind][i] = (e[0], e[1][i])

                    # Raise an exception in case data for the default settings
                    # are missing in some program run
                    for prog_start_ind, prog_start in enumerate(single_prog_start_vals_tmp):
                        if None in prog_start:
                            utils.print_err('Loading default values - check your default_x_val '
                                            'variable and CSV file with measured data (bad yLabel missing samples etc.). \n\n'
                                            'Possibly data for {}. program run are missing in the file with default '
                                            'configuration. It means, that some configuration were measured more than '
                                            '{} times.\n Try looking for string "init_{}" (inits are indexed from 0) in '
                                            'other CSV files to localize the problem. \n\n'
                                            'Configuration: {}\n'
                                            'Region: {}\n'
                                            'Default x-value: {}\n'
                                            'Default label-value: {}'.format(prog_start_ind + 1,
                                                                             prog_start_ind,
                                                                             prog_start_ind,
                                                                             conf,
                                                                             self.get_region_name(),
                                                                             default_x_val,
                                                                             default_label_val))

                    def_default_dic = {'avgProgramStart': [{'keys': default_keys[i],
                                                            'funcLabel': default_label_val[i],
                                                            'xVal': avg_prog_start_vals_tmp[i][0],
                                                            'yVal': avg_prog_start_vals_tmp[i][1]}
                                                           for i in range(self.get_evaluated_vars_num())],
                                       'singleProgramStarts': [[{'keys': default_keys[i],
                                                                 'funcLabel': default_label_val[i],
                                                                 'xVal': prog_start[i][0],
                                                                 'yVal': prog_start[i][1]}
                                                                for i in range(self.get_evaluated_vars_num())]
                                                               for prog_start in single_prog_start_vals_tmp]}
                except IndexError:
                    # TODO rewrite so that the index of default values can be distinguished (i.e., the index of the independent variable)
                    if parent_reg_oa_d:
                        utils.print_err('Loading default values - check your default_x_val '
                                        'variable and CSV file with measured data (missing samples etc.).\n'
                                        'Possibly the configuration for main region doesn\'t '
                                        'exist in the nested ones. \n\n'
                                        'Configuration: {}\n'
                                        'Region: {}\n'
                                        'Default x-value: {}\n'
                                        'Default label-value: {}'.format(conf, self.get_region_name(), default_x_val,
                                                                         default_label_val))
                    utils.print_err('Loading default values - check your default_x_val '
                                    'variable and CSV file with measured data (bad yLabel missing samples etc.). \n\n'
                                    'Configuration: {}\n'
                                    'Region: {}\n'
                                    'Default x-value: {}\n'
                                    'Default label-value: {}'.format(conf, self.get_region_name(), default_x_val,
                                                                     default_label_val))
                except KeyError:
                    utils.print_err('Loading default values - check your default_label_val '
                                    'variable and CSV file with measured data (bad yLabel or missing samples etc.). \n\n'
                                    'Configuration: {}\n\n'
                                    'Region: {}\n'
                                    'Default x-value: {}\n'
                                    'Default label-value: {}'.format(conf, self.get_region_name(), default_x_val,
                                                                     default_label_val))

                ret_dic[conf] = dict(optimalVal=def_optim_dic,
                                     defaultVal=def_default_dic)

        return OptimalAndDefaultValsContainer(self.get_region_name(), ret_dic, data_category)

    def apply_eng_baseline(self,
                           baseline,
                           eng_ind,
                           time_ind):
        # Apply the baseline to the energy variable for
        # individual program runs ('singleProgramStarts')

        utils.print_info('Applying the baseline on the region {}...'.format(self.get_region_name()))

        # Function for applying the baseline

        def apply_baseline(d, settings_lst=list()):
            for k, v in d.items():
                if 'singleProgramStarts' in v.keys():
                    self.apply_baseline_strategy(baseline, v, eng_ind, time_ind, settings_lst + [k])
                else:
                    apply_baseline(v, settings_lst + [k])

        # Iteration over individual configurations
        for cat, vals1 in self.get_raw_summary_sources_dic().items():
            if cat == 'full':
                self.set_baseline_strategy(BaseLineChangeStrategyFull())
            else:
                self.set_baseline_strategy(BaseLineChangeStrategyGeneral())

            for vals2 in vals1.values():
                apply_baseline(vals2)

        utils.print_info('Baseline was succesfully applied.')


class PlotNode:
    def __init__(self,
                 x_val_or_dic, y_val=None,
                 func_label=None,
                 keys=None):
        # TODO implement robust parameter checking
        if isinstance(x_val_or_dic, dict):
            self.__x_val = x_val_or_dic['xVal']
            self.__y_val = x_val_or_dic['yVal']
            self.__func_label = x_val_or_dic['funcLabel']
            self.__keys = x_val_or_dic['keys']
        else:
            self.__x_val = x_val_or_dic
            self.__y_val = y_val
            self.__keys = keys
            self.__func_label = func_label

    def get_x_val(self):
        return self.__x_val

    def get_y_val(self):
        return self.__y_val

    def get_func_label(self):
        return self.__func_label

    def get_keys(self):
        return self.__keys


class DataReader:
    def __init__(self, evaluated_vars, smooth_avg=False):
        utils.print_info('Creating DataReader object...')

        self.__evaluated_vars = evaluated_vars
        self.__evaluated_vars_num = len(self.__evaluated_vars)

        self.__smooth_avg = smooth_avg

        utils.print_info('DataReader object successfully created.')

    def get_evaluated_vars(self):
        return self.__evaluated_vars

    def get_ith_evaluated_var(self, ind):
        return self.__evaluated_vars[ind]

    def get_evaluated_vars_num(self):
        return self.__evaluated_vars_num

    @staticmethod
    def __find_dic_recursively(lst, main_reg, out_lst):
        """
        Nalezne rekurzivne vyskyty funkce ve stromu nactenem
        z CSV

        :param lst: strom volani vygen. z CSV
        :param main_reg: nazev hledane fce / regionu
        :param (out) out_lst: List hodnot pro kazdy klic=nazev fce
        """

        for dic in lst:
            for key, vals in dic.items():
                if key == main_reg:
                    out_lst.extend(vals)
                elif not key == 'vals':
                    DataReader.__find_dic_recursively(vals, main_reg, out_lst)

    # Function for retrieving values from CSV,
    # which are used as yLabelArg.
    @staticmethod
    def __get_y_label_vals(values_lst, y_label_cat, y_label_arg, dirpath, filename, summate=True):
        ret_lst = list()
        try:
            for dic in values_lst:
                for key, lst in dic.items():
                    if key == y_label_cat:
                        for tup in lst:
                            if tup[0] == y_label_arg:
                                try:
                                    ret_lst.append(float(tup[1]))
                                except ValueError:
                                    utils.print_err('Bad value {val} of y_label "{lab}" in the file {file} in the'
                                                    ' region {reg}! Is "{lab}" the correct y_label?'
                                                    .format(val=tup[1], file=filename, reg=dirpath, lab=y_label_arg))
        except KeyError:
            utils.print_err('y-label category not found - check your settings and contents of your CSV files!')

        if not summate:
            return [{'sumVal': oneCall, 'numOfNestedCalls': 1} for oneCall in ret_lst]

        return {'sumVal': sum(ret_lst),
                'numOfNestedCalls': len(ret_lst)}

    # @info construction of the sumarySources structure
    # @param items (dictionary) dictioray of results for this settings, key funcLabel with a list of results
    #              as a value of the key
    # @param path  (list) list of keys, that must be added as a path to this settings in final structure
    # @return (void)
    # @note edits global structure summarySources
    def __construct_summary_sources(self,
                                    items,
                                    path,
                                    summary_sources,
                                    conf,
                                    used_data_categories=('avg', 'full', 'min', 'max')):

        for dic in summary_sources.values():
            if conf not in dic['vals']:
                dic['vals'][conf] = dict()
            tmp = dic['vals'][conf]

            for key in path:
                if key not in tmp:
                    tmp[key] = dict()
                tmp = tmp[key]

            for func_label, val in items:
                tmp[func_label] = {'singleProgramStarts': list(),
                                   'avgProgramStart': list()}

        for func_label, val in items:
            for cat in used_data_categories:
                # Write data for the given configuration into the list - for percentage calculations etc.
                # 1 list item = 1 program call (init)
                for dic in val:
                    summary_sources_tmp = utils.get_obj_from_path(path, summary_sources[cat]['vals'][conf])
                    summary_sources_tmp[func_label]['singleProgramStarts'].append(dic[cat])

                # Get x-labels from all calls (to find out which occur in at least one)
                x_label_keys = dict()

                # Get the maximum number of iterations per call
                # function - only for 'full'!
                max_num_of_iters_per_start = 1
                for single_program_start in utils.get_obj_from_path(path, summary_sources[cat]['vals'][conf]) \
                        [func_label]['singleProgramStarts']:

                    for xy_vals in single_program_start:
                        if cat == 'full':
                            if len(xy_vals[1]) > max_num_of_iters_per_start:
                                max_num_of_iters_per_start = len(xy_vals[1])
                        x_label_keys[xy_vals[0]] = 1

                x_label_keys = x_label_keys.keys()

                # Calculate the average over all program runs
                # for individual configurations
                for x_label_key in x_label_keys:
                    # List for values with the same x-label
                    # from all calls
                    avg_val_from_all_starts_per_one_x_label_key = list()

                    for single_program_start \
                            in utils.get_obj_from_path(path,
                                                       summary_sources[cat]['vals'][conf])[func_label]['singleProgramStarts']:

                        if cat == 'full':
                            xy_val = [[None
                                       for i
                                       in range(self.__evaluated_vars_num)]
                                      for j
                                      in range(max_num_of_iters_per_start)]
                            for xy_vals in single_program_start:
                                if xy_vals[0] == x_label_key:
                                    for iter_ind, xyValTmp in enumerate(xy_vals[1]):
                                        for evaluated_var_ind, evaluated_var in enumerate(xyValTmp):
                                            if evaluated_var['numOfNestedCalls'] > 0:
                                                xy_val[iter_ind][evaluated_var_ind] = evaluated_var['sumVal']
                                    break
                            avg_val_from_all_starts_per_one_x_label_key.append(xy_val)

                        else:
                            # Default value in case the function with this configuration
                            # is not called at all during this program run
                            xy_val = None

                            for xy_vals in single_program_start:
                                if xy_vals[0] == x_label_key:
                                    xy_val = xy_vals[1]
                                    break
                            avg_val_from_all_starts_per_one_x_label_key.append(xy_val)

                    # Get the average over all program starts
                    # TODO is it really all program starts or region calls?
                    if cat == 'full':
                        vals_tmp = [[e[i] for e in avg_val_from_all_starts_per_one_x_label_key if None not in e[i]]
                                    for i in range(max_num_of_iters_per_start)]

                        if vals_tmp:
                            tmp = []
                            for lst in vals_tmp:
                                avg_tmp = []
                                for i in range(self.__evaluated_vars_num):
                                    tmp2 = [e[i] for e in lst]
                                    avg_tmp.append(numpy.mean(tmp2) if tmp2 else None)
                                tmp.append(avg_tmp)

                            utils.get_obj_from_path(path, summary_sources[cat]['vals'][conf])[func_label]['avgProgramStart'] \
                                .append((x_label_key, tmp))
                    else:
                        vals_tmp = [e for e in avg_val_from_all_starts_per_one_x_label_key if e is not None]
                        if vals_tmp[0]:
                            if self.__smooth_avg:
                                tmp = [numpy.mean(utils.remove_outliers([lst[i] for lst in vals_tmp])) for i in
                                       range(self.__evaluated_vars_num)]
                            else:
                                tmp = [numpy.mean([lst[i] for lst in vals_tmp]) for i in
                                       range(self.__evaluated_vars_num)]
                            utils.get_obj_from_path(path, summary_sources[cat]['vals'][conf])[func_label][
                                'avgProgramStart'] \
                                .append((x_label_key, tmp))

    # @info recursively goes through the dict until it reaches its last dict the results
    # @param nested (dict) dictionary with another key or results
    # @param path (list) path of previous keys
    # @return (void)
    def __process_keys(self,
                       nested,
                       path,
                       summary_sources,
                       conf,
                       used_data_categories):
        for ind, item in enumerate(nested):
            if type(nested[item]) is dict:
                self.__process_keys(nested[item],
                                    path + [item],
                                    summary_sources,
                                    conf,
                                    used_data_categories)
            else:
                self.__construct_summary_sources(sorted(nested.items()),
                                                 path,
                                                 summary_sources,
                                                 conf,
                                                 used_data_categories)

    def get_data_from_folder(self,
                             measured_func_folder_arg,
                             filename_args,
                             iter_call_reg=None,
                             not_parse_args_lst=list(),
                             used_data_categories=('avg', 'full', 'min', 'max'),
                             x_val_multiplier=1,
                             func_label_multiplier=None,
                             def_vals_dic=None,
                             samples_args=None,
                             test_csv_init=False):
        # def_vals_dic = {'keys': [***], 'x_lab': ***, 'func_lab': ***}

        # TODO maybe split into 'load' and 'classify'
        # TODO describe in comments the structure of folder_data,
        # folder_data_groups, and the output object

        # sampleSourcesInds = {}
        summary_sources = {key: {'vals': {}} for key in used_data_categories}

        # Complete data for files with default settings (for each region)
        folder_default_detail = {}

        for dirpath, dirnames, filenames in os.walk(measured_func_folder_arg, topdown=True):
            # Ignore hidden folders because of GIT, .swp, etc.
            # filenames = [f for f in filenames if not f[0] == '.']
            # dirnames[:] = [d for d in dirnames if not d[0] == '.']

            ##########################
            # Parsing a single folder #
            ##########################

            # All data from a single folder (function at a specific line)
            #
            # List in the format

            # [ {'funcLabel': '***',
            #    'xLabel': '***',
            #    'conf': '***',
            #    'Data': {***}
            #   },
            #   {***},
            #   *** ]
            folder_data = []

            # Loading parameters given in the CSV filename

            func_label_arg = filename_args.get_func_label()
            x_label_arg = filename_args.get_x_label()
            config_args = filename_args.get_config_lst()
            common_keys_args = filename_args.get_common_keys_lst()

            # 'Split' the config argument into individual values
            key_lst = filename_args.get_lst_of_params()

            ###############################################
            # Load data from individual files in the folder
            ###############################################
            for filename in filenames:
                # Get parameter names from the filename
                args = filename[0:filename.rfind('.')].split('_')

                # Check the parameter specification
                if len(args) != filename_args.get_num_of_params():
                    utils.print_err('Number of specified filename parameters ({}) does not '
                                    'correspond to the filename {}!'.format(filename_args.get_num_of_params(),
                                                                            filename))

                # Assign specific values from the CSV filename
                # to the given parameters in filename_args

                d = {key: (args[i] if i < len(args) else '') for i, key in enumerate(key_lst)}

                # Determine whether the data are for the default settings
                is_default_settings = False

                try:
                    if self.apply_x_val_multiplier(float(filename_args.get_x_label_val_from_dic(d)), x_val_multiplier) \
                            == def_vals_dic['x_lab'] and \
                            float(
                                self.apply_func_val_multiplier(float(filename_args.get_func_label_val_from_dic(d)),
                                                               func_label_multiplier)) \
                            == def_vals_dic['func_lab'] and \
                            bool([1 for e in zip(def_vals_dic['keys'], filename_args.get_keys_vals_from_dic(d)) if
                                  e[0] == e[1]]):
                        is_default_settings = True
                except ValueError:
                    utils.print_err(
                        'Non-numerical x_label or func_label!\n Is the filename \'{}\' correct?'.format(filename))

                # Detailed data about each call for the default settings
                def_settings_detail = None
                if is_default_settings:
                    def_settings_detail = []


                p = LabeledCSVParser('{}/{}'.format(dirpath, filename),
                                     not_parse_args_lst,
                                     '{}: {}'.format(dirpath, filename),
                                     test_csv_init)
                p.parse(def_settings_detail)

                data = None
                try:
                    data = p.get_dic_data()[0]  # Index 0 proto, abych se zbavil "obalujiciho" listu okolo slovniku
                except IndexError:
                    utils.print_err("No data were loaded from {0}/{1}. Maybe the CSV file is empty?".format(dirpath,
                                                                                                            filename))

                # Create and record 'samples' if specified
                # by the 'samples_args' parameter
                # TODO implement plotting of graphs from samples
                if samples_args:
                    raise NotImplementedError
                #   sampleSourcesInds[filename] = {}
                #    for sampleArg in samples_args:
                #        prevNumOfSources = slideshowCreator.getIndOfLastDataSource()
                #        slideshowCreator.createAndAddDataSource(data[sampleArg], 100, True, 0, 2)
                #        sampleSourcesInds[filename][sampleArg] = list(range(prevNumOfSources,
                #                                                            slideshowCreator.getIndOfLastDataSource()))

                # Pridam do slovniku nactena data ze souboru
                d['Data'] = data
                folder_data.append(d)

                # If the data are for the default settings, add complete data (neither summed nor averaged)
                # for cluster analysis
                if is_default_settings:
                    folder_default_detail[dirpath] = def_settings_detail

            ###############################################################
            # Split the loaded data from the folder into groups based on  #
            # optional arguments (preconditioner, schur complement...)    #
            ###############################################################

            # Stored yLabel values from all function calls
            folder_data_groups = {}

            # Function for retrieving data for individual categories
            # d ... data

            # mean_func = numpy.mean if not avg_with_outliers else lambda dd: numpy.mean(utils.remove_outliers(dd))
            # TODO remove outliers also for min and max?
            func_dic = {'avg': lambda data_inp: numpy.mean(data_inp),
                        'min': lambda data_inp: min(data_inp),
                        'max': lambda data_inp: max(data_inp)}

            # Iterating through the folder data "file by file"

            for file_ind, val in enumerate(folder_data):
                # Get the values of configuration arguments
                # and store them as a tuple, or None if
                # no configuration is specified

                current_config = tuple([str(val[arg]) for arg in config_args]) if config_args[0] else tuple()

                # Current value of the function "label"

                current_func_label_value = folder_data[file_ind][func_label_arg]
                if func_label_multiplier:
                    current_func_label_value = self.apply_func_val_multiplier(current_func_label_value,
                                                                              func_label_multiplier)

                # Current value for the X-axis - MUST be numeric!

                if x_val_multiplier:
                    current_x_label_value = self.apply_x_val_multiplier(folder_data[file_ind][x_label_arg],
                                                                        x_val_multiplier)

                # If not already present, add a tuple with configuration
                # parameters as a key for the dictionary with average
                # consumption values, all values, maximum, and minimum

                if current_config not in folder_data_groups:
                    folder_data_groups[current_config] = dict()

                # Create a "tree" from the "common keys"

                current_dic = folder_data_groups[current_config]
                for i, currCommonKey in enumerate(common_keys_args):
                    if val[currCommonKey] not in current_dic:
                        tmp_dic = dict()
                        current_dic[val[currCommonKey]] = tmp_dic
                        current_dic = tmp_dic
                    else:
                        current_dic = current_dic[val[currCommonKey]]

                # Add funcLabel to the dictionary under the current configuration,
                # if it is not already present.
                #
                # funcLabel is the key for a list containing data for individual
                # program runs.

                if current_func_label_value not in current_dic:
                    current_dic[current_func_label_value] = list()

                # Evaluation of data for each program run (init) and each
                # iteration/call of the main function
                # TODO rewrite oneProgStartData to snake_case

                for program_start_ind, oneProgStartData in enumerate(folder_data[file_ind]['Data']['init']):
                    # Data structure for a single program run (init) for one file

                    data_tmp = {'avg': None,
                                'full': list(),
                                'max': None,
                                'min': None}

                    # When we want to store data for individual iterations/calls of the main function
                    # (i.e., for nested functions) or for individual calls of the processed
                    # function (i.e., for the main function)

                    data_per_iterations = list()  # Data for individual iterations/calls of the main function

                    if iter_call_reg:
                        # If the parent region is specified as "iteration", otherwise the main region is taken as iter_call_reg
                        self.__find_dic_recursively([oneProgStartData], iter_call_reg, data_per_iterations)

                        if not data_per_iterations:
                            utils.print_err('The nested region {} is NOT located inside the iteration region {} or '
                                            'maybe there are missing data for {}. program start!\n'
                                            'Region: {}\n'
                                            'Config: {}\n'
                                            'x-label: {}\n'
                                            'func-label: {}\n'
                                            'keys: {}'
                                            .format(dirpath,
                                                    iter_call_reg,
                                                    program_start_ind,
                                                    dirpath,
                                                    ', '.join(current_config),
                                                    folder_data[file_ind][filename_args.get_x_label()],
                                                    folder_data[file_ind][filename_args.get_func_label()],
                                                    ', '.join([folder_data[file_ind][k] for k in
                                                               filename_args.get_common_keys_lst()])))

                        # Processing data for individual iterations
                        # (sum of values from individual calls of nested functions)

                        lst_of_iter_data_per_one_x_label = list()
                        for one_iter_dic in data_per_iterations:
                            tmp = list()
                            self.__find_dic_recursively([one_iter_dic] if one_iter_dic is not list else one_iter_dic,
                                                        'vals', tmp)

                            tmp2 = list()
                            lst_of_iter_data_per_one_x_label.append(tmp2)
                            for evaluated_var in self.__evaluated_vars:
                                tmp2.append(self.__get_y_label_vals(tmp,
                                                                    evaluated_var['category'],
                                                                    evaluated_var['arg'],
                                                                    dirpath,
                                                                    filename))

                        # Check when the nested function is never called
                        # in the region specified by the 'iter_call_reg' parameter

                        if not lst_of_iter_data_per_one_x_label[0]:
                            utils.print_err('The region \'{0}\' is not inside the region \'{1}\'!'
                                            ' - check parameters \'measured_func_folder_arg\''
                                            ' and \'iter_call_reg\'.'.format(measured_func_folder_arg, iter_call_reg))
                    else:
                        # If no parent region is specified as an iteration,
                        # the function call itself is treated as the iteration

                        self.__find_dic_recursively([oneProgStartData], 'vals', data_per_iterations)

                        tmp = [None] * self.__evaluated_vars_num
                        lst_of_iter_data_per_one_x_label = [tmp]

                        for evaluated_var_ind, evaluated_var in enumerate(self.__evaluated_vars):
                            t = self.__get_y_label_vals(data_per_iterations,
                                                        evaluated_var['category'],
                                                        evaluated_var['arg'],
                                                        dirpath,
                                                        filename,
                                                        summate=True)

                            tmp[evaluated_var_ind] = t  
                            if (isinstance(t, dict) and t['numOfNestedCalls'] == 0) or (isinstance(t, list) and t[0]['numOfNestedCalls'] == 0):
                                utils.print_err('Bad data category or argument - compare \'y_label\' variable in the '
                                                'config file with your CSV files!\n'
                                                'Category: {cat}\n'
                                                'Arg: {arg}\n'
                                                '{pars}'.format(cat=evaluated_var['category'],
                                                                arg=evaluated_var['arg'],
                                                                pars=', '.join(
                                                                    ['{}: {}'.format(k, folder_data[file_ind][k])
                                                                     for k in folder_data[file_ind].keys()
                                                                     if k != 'Data'])))

                        for evaluated_var_ind, evaluated_var in enumerate(self.__evaluated_vars):
                            if not lst_of_iter_data_per_one_x_label[0][evaluated_var_ind]:
                                utils.print_err('Error loading data from CSV file for region {0}!\n\n'
                                                'Check parameters \'yLabelCategory\' ({1})'
                                                ' and \'yLabelArg\' ({2}).\n'
                                                '{3}'.format(measured_func_folder_arg,
                                                             evaluated_var['category'],
                                                             evaluated_var['arg'],
                                                             ', '.join(['{}: {}'.format(k, folder_data[file_ind][k])
                                                                        for k in folder_data[file_ind].keys()
                                                                        if k != 'Data'])
                                                             ))

                    data_tmp['full'].append((current_x_label_value, lst_of_iter_data_per_one_x_label))

                    # Calculation of average, minimum, and maximum values
                    # per iteration (calculated with values in 'full' - i.e., sums
                    # of nested function values for 1 iteration)

                    # noinspection PyTypeChecker
                    vals_lst_tmp = [[dic['sumVal'] for dic in lst] for tup in data_tmp['full'] for lst in tup[1]]

                    for category in [cat for cat in used_data_categories if cat != 'full']:
                        data_tmp[category] = (
                        current_x_label_value, [func_dic[category]([lst[i] for lst in vals_lst_tmp])
                                                for i
                                                in range(len(vals_lst_tmp[0]))])

                    # Store data for 1 call from 1 file into the folder_data_groups structure
                    # at the corresponding index (init).
                    #
                    # If the call index is greater than what is currently stored
                    # in FolderDataGroups, add a new dictionary.

                    if len(current_dic[current_func_label_value]) <= program_start_ind:
                        current_dic[current_func_label_value].append({key: list()
                                                                      for key
                                                                      in used_data_categories})

                    for category in used_data_categories:
                        if category == 'full':
                            current_dic[current_func_label_value][program_start_ind]['full'].extend(data_tmp['full'])
                        else:
                            current_dic[current_func_label_value][program_start_ind][category].append(
                                data_tmp[category])

            #############################################################
            # Retrieving data from folder_data_groups and writing them   #
            # as a source                                               #
            #############################################################

            # Iteration over individual configurations

            for conf, vals in sorted(folder_data_groups.items()):
                # Add a summary_sources list for the specific configuration.
                # The list will contain results for individual program runs.

                self.__process_keys(vals,
                                    [],
                                    summary_sources,
                                    conf,
                                    used_data_categories)

        # Check whether any data were loaded
        # TODO consider adding more checks for multiple evaluated variables

        if not dict(collections.ChainMap(*[summary_sources[cat]['vals'] for cat in summary_sources])):
            utils.print_err("No data were loaded - check your region name: {0}".format(measured_func_folder_arg))

        return {'data': DataContainer(measured_func_folder_arg, summary_sources, self.__evaluated_vars),
                'default_detail': folder_default_detail}

    def apply_x_val_multiplier(self, current_x_val, x_val_multiplier):
        try:
            return round(float(current_x_val) * float(x_val_multiplier), 2)
        except ValueError:
            utils.print_err('X-label {} or its multiplier is not a number and so it can not be '
                            'multiplied by {}!'.format(current_x_val, x_val_multiplier))

    def apply_func_val_multiplier(self, current_func_label_value, func_label_multiplier):
        try:
            return utils.get_round_num_str(float(current_func_label_value) * float(func_label_multiplier), 1)
        except ValueError:
            utils.print_err('Function label {} or its multiplier {} is not a number!'
                            .format(current_func_label_value, func_label_multiplier))


class Evaluator:
    def __init__(self):
        utils.print_info('Creating Evaluator object...')

    @staticmethod
    def __get_nested_regions_report_vals(func_lst,
                                         summary_sources_nested,
                                         default_optimal_vals_nested,
                                         all_nested_funcs,
                                         conf,
                                         ind_of_prog_start=None,
                                         ind_of_iter_ind=None):
        # TODO test input validation ('full'/'avg', etc.) for all functions

        # Function for retrieving static and dynamic optima
        # noinspection PyUnusedLocal
        stat_optim = None
        # noinspection PyUnusedLocal

        dyn_optim = None

        default_optimal_vals_nested_tmp = default_optimal_vals_nested[func_lst[0]].get_raw_data_dic()

        num_of_vars = len(default_optimal_vals_nested_tmp[conf]['defaultVal']['avgProgramStart'])

        if ind_of_prog_start is not None:
            # Individual program runs as well as individual iterations

            # Validate input

            for func in func_lst:
                if default_optimal_vals_nested[func].get_data_category() != 'full':
                    utils.print_err('Type of \'default_optimal_vals_nested\' parameter is not \'full\'!')

            vals_tmp = default_optimal_vals_nested_tmp[conf]['defaultVal']['singleProgramStarts'][ind_of_prog_start][
                ind_of_iter_ind]

            main_optim_keys = [e['keys'] for e in vals_tmp]
            main_optim_func_label = [e['funcLabel'] for e in vals_tmp]
            main_optim_x_val = [e['xVal'] for e in vals_tmp]

            def stat_optim(f):
                ret_lst = []
                for i in range(num_of_vars):
                    tmp = [tup
                           for tup
                           in utils.get_obj_from_path(main_optim_keys[i],
                                                      summary_sources_nested[f][conf])[str(main_optim_func_label[i])][
                               'singleProgramStarts'][ind_of_prog_start]
                           if tup[0] == main_optim_x_val[i]][0][1]

                    ret_lst.append([lst[i] for lst in tmp])

                return list(zip(*ret_lst))

            dyn_optim = lambda f: default_optimal_vals_nested[f].get_raw_data_dic()[conf]['optimalVal']['singleProgramStarts'][ind_of_prog_start]

        else:
            if ind_of_iter_ind is not None:
                # Average program run and individual iterations

                # Validate input

                for func in func_lst:
                    if default_optimal_vals_nested[func].get_data_category() != 'full':
                        utils.print_err('Type of \'default_optimal_vals_nested\' parameter is not \'full\'!')

                main_optim_keys = [
                    default_optimal_vals_nested_tmp[conf]['defaultVal']['avgProgramStart'][i][ind_of_iter_ind]['keys']
                    for i in range(num_of_vars)]
                main_optim_func_label = [
                    default_optimal_vals_nested_tmp[conf]['defaultVal']['avgProgramStart'][i][ind_of_iter_ind][
                        'funcLabel']
                    for i in range(num_of_vars)]
                main_optim_x_val = [
                    default_optimal_vals_nested_tmp[conf]['defaultVal']['avgProgramStart'][i][ind_of_iter_ind]['xVal']
                    for i in range(num_of_vars)]

            else:
                # Average program run + average over iterations

                # Validate input

                for func in func_lst:
                    if default_optimal_vals_nested[func].get_data_category() != 'avg':
                        utils.print_err('Type of \'default_optimal_vals_nested\' parameter is not \'avg\'!')

                main_optim_keys = [default_optimal_vals_nested_tmp[conf]['defaultVal']['avgProgramStart'][i]['keys']
                                   for i in range(num_of_vars)]
                main_optim_func_label = [
                    default_optimal_vals_nested_tmp[conf]['defaultVal']['avgProgramStart'][i]['funcLabel']
                    for i in range(num_of_vars)]
                main_optim_x_val = [default_optimal_vals_nested_tmp[conf]['defaultVal']['avgProgramStart'][i]['xVal']
                                    for i in range(num_of_vars)]

            def stat_optim(f):
                ret_lst = []
                for i in range(num_of_vars):
                    tmp = [tup
                           for tup
                           in utils.get_obj_from_path(main_optim_keys[i],
                                                      summary_sources_nested[f][conf])[str(main_optim_func_label[i])][
                               'avgProgramStart']
                           if tup[0] == main_optim_x_val[i]][0][1]

                    if isinstance(tmp[0], list):
                        ret_lst.append(tuple(lst[i] for lst in tmp))
                    else:
                        ret_lst.append(tmp[i])

                if isinstance(ret_lst[0], tuple):
                    return list(zip(*ret_lst))
                else:
                    return ret_lst

            dyn_optim = lambda f: default_optimal_vals_nested[f].get_raw_data_dic()[conf]['optimalVal'][
                'avgProgramStart']

        if None not in (ind_of_prog_start, ind_of_iter_ind):
            # Individual program runs as well as individual iterations


            stat_optims = []
            for nested_func_lst in all_nested_funcs:
                for func in nested_func_lst:
                    try:
                        stat_optims.append(tuple(e['sumVal'] for e in stat_optim(func)[ind_of_iter_ind]))
                    except IndexError:
                        stat_optims.append(tuple([0] * num_of_vars))
                    except KeyError:
                        stat_optims.append(tuple([0] * num_of_vars))

            sum_stat_optims = [sum(e) if e else None for e in zip(*stat_optims)]
            sum_stat_optims = [e if e else None for e in sum_stat_optims]

            # LIST of optimal function values (in case of multiple nested
            # functions at the same position)

            curr_dyn_optims = [[{'keys': dyn_optim(func)[ind_of_iter_ind][i]['keys'],
                                 'funcLabel': dyn_optim(func)[ind_of_iter_ind][i]['funcLabel'],
                                 'xVal': dyn_optim(func)[ind_of_iter_ind][i]['xVal'],
                                 'yVal': dyn_optim(func)[ind_of_iter_ind][i]['yVal']}
                                for i in range(num_of_vars)]
                               for func in func_lst]

            # Getting the current static optimum
            #  - sum because there may be multiple
            #    functions at the same position
            # TODO maybe the previously obtained stat_optims can be used

            stat_optims = []
            for func in func_lst:
                try:
                    stat_optims.append(tuple(e['sumVal'] for e in stat_optim(func)[ind_of_iter_ind]))
                except IndexError:
                    stat_optims.append(tuple([0] * num_of_vars))
                except KeyError:
                    stat_optims.append(tuple([0] * num_of_vars))

            curr_stat_optim = [sum(e) if e else None for e in zip(*stat_optims)]
            curr_stat_optim = [e if e else None for e in curr_stat_optim]

        elif ind_of_iter_ind is not None:
            # Average program run and individual iterations
            curr_dyn_optims = [[{'keys': dyn_optim(func)[ind_of_iter_ind][i]['keys'],
                                 'funcLabel': dyn_optim(func)[ind_of_iter_ind][i]['funcLabel'],
                                 'xVal': dyn_optim(func)[ind_of_iter_ind][i]['xVal'],
                                 'yVal': dyn_optim(func)[ind_of_iter_ind][i]['yVal']}
                                for i in range(num_of_vars)]
                               for func in func_lst]

            tmp = []
            for nested_func_lst in all_nested_funcs:
                for func in nested_func_lst:
                    try:
                        tmp.append(stat_optim(func)[ind_of_iter_ind])
                    except IndexError:
                        utils.print_err('There are no data for region {} in the {}. iteration!\n\n'
                                        'Settings:\n'
                                        'Configuration: {}\n'
                                        'x-value: {}\n'
                                        'func-label: {}\n'
                                        'keys: {}\n'.format(func,
                                                            ind_of_iter_ind,
                                                            conf,
                                                            main_optim_x_val,
                                                            main_optim_func_label,
                                                            main_optim_keys))

            tmp = [e for e in tmp if None not in e]
            sum_stat_optims = [sum(e) if e else None for e in zip(*tmp)]

            tmp = [stat_optim(func)[ind_of_iter_ind] for func in func_lst]
            tmp = [e for e in tmp if None not in e]
            curr_stat_optim = [sum(e) if e else None for e in zip(*tmp)]

        else:
            # Average program run + average over iterations
            curr_dyn_optims = [dyn_optim(func) for func in func_lst]

            tmp = [stat_optim(func) for nested_func_lst in all_nested_funcs for func in nested_func_lst]
            tmp = [e for e in tmp if None not in e]
            sum_stat_optims = [sum(e) if e else None for e in zip(*tmp)]

            tmp = [stat_optim(func) for func in func_lst]
            tmp = [e for e in tmp if None not in e]
            curr_stat_optim = [sum(e) if e else None for e in zip(*tmp)]

        tmp = [tuple(varE['yVal'] for varE in e) for e in curr_dyn_optims]
        tmp = [e for e in tmp if None not in e]
        curr_dyn_optims_sum_val = [sum(e) if e else None for e in zip(*tmp)]

        # TODO write this better
        if not curr_stat_optim:
            curr_stat_optim = [None] * num_of_vars

        if not curr_dyn_optims_sum_val:
            curr_dyn_optims_sum_val = [None] * num_of_vars

        if not sum_stat_optims:
            sum_stat_optims = [None] * num_of_vars

        # Output values
        res = dict()
        res['mainOptimKeys'] = main_optim_keys
        res['mainOptimFuncLabel'] = main_optim_func_label
        res['mainOptimXValue'] = main_optim_x_val

        # Element for each region at the position, each element is a list of dictionaries for each variable
        res['currDynOptimsLst'] = curr_dyn_optims

        res['currDynOptimsSumVal'] = curr_dyn_optims_sum_val

        try:
            res['currStatOptim'] = curr_stat_optim
            res['percentsOfOneIter'] = [curr_stat_optim[i] / sum_stat_optims[i] * 100 for i in range(num_of_vars)]
            res['percentsOfStatOptim'] = [curr_dyn_optims_sum_val[i] / curr_stat_optim[i] * 100
                                          for i in range(num_of_vars)]
            res['dynSavingPercents'] = [100 - (curr_dyn_optims_sum_val[i] / curr_stat_optim[i] * 100)
                                        for i in range(num_of_vars)]
            res['dynSavingsVal'] = [curr_stat_optim[i] - curr_dyn_optims_sum_val[i] for i in range(num_of_vars)]

            res['percentsOfOneIterRound'] = [utils.get_round_num_str(curr_stat_optim[i] / sum_stat_optims[i] * 100)
                                             for i in range(num_of_vars)]
            res['currStatOptimRound'] = [utils.get_round_num_str(curr_stat_optim[i]) for i in range(num_of_vars)]
            res['dynSavingsValRound'] = [utils.get_round_num_str(curr_stat_optim[i] - curr_dyn_optims_sum_val[i])
                                         for i in range(num_of_vars)]
            res['percentsOfStatOptimRound'] = [
                utils.get_round_num_str(curr_dyn_optims_sum_val[i] / curr_stat_optim[i] * 100)
                for i in range(num_of_vars)]
            res['dynSavingPercentsRound'] = [
                utils.get_round_num_str(100 - (curr_dyn_optims_sum_val[i] / curr_stat_optim[i] * 100))
                for i in range(num_of_vars)]

            res['currDynOptimsSumValRound'] = [utils.get_round_num_str(curr_dyn_optims_sum_val[i])
                                               for i in range(num_of_vars)]

        except TypeError:
            res['currStatOptim'] = ['-'] * num_of_vars
            res['percentsOfOneIter'] = ['-'] * num_of_vars
            res['percentsOfStatOptim'] = ['-'] * num_of_vars
            res['dynSavingPercents'] = ['-'] * num_of_vars
            res['dynSavingsVal'] = ['-'] * num_of_vars

            res['percentsOfOneIterRound'] = ['-'] * num_of_vars
            res['currStatOptimRound'] = ['-'] * num_of_vars
            res['dynSavingsValRound'] = ['-'] * num_of_vars
            res['percentsOfStatOptimRound'] = ['-'] * num_of_vars
            res['dynSavingPercentsRound'] = ['-'] * num_of_vars

            res['currDynOptimsSumValRound'] = ['-'] * num_of_vars

            res['currDynOptimsLst'] = [[{'keys': ['-'],
                                         'funcLabel': '-',
                                         'xVal': '-',
                                         'yVal': '-'}] * num_of_vars] * len(res['currDynOptimsLst'])
            res['currDynOptimsSumVal'] = ['-'] * num_of_vars

        return res

    @staticmethod
    def __assemble_optim_settings_struct(file_content,
                                         region,
                                         conf,
                                         config_file,
                                         file_name_args,
                                         y_labels,
                                         x_val_multiplier,
                                         func_label_multiplier):
        optim_vals = region.get_raw_data_dic()[conf]['optimalVal']['avgProgramStart']
        region_name = region.get_region_name()

        # Key processing
        tmp_data = [{config_file['generate_optim_settings_file'][e[0]]: str(e[1])
                     for e
                     in zip(file_name_args.get_common_keys_lst(), optim_vals[i]['keys'])
                     if e[0] in config_file['generate_optim_settings_file']}
                    for i in range(len(y_labels))]

        for i in range(len(y_labels)):
            # X-label processing
            x_val_label = None
            try:
                x_val_label = config_file['generate_optim_settings_file'][file_name_args.get_x_label()]
            except KeyError:
                utils.print_err('Unknown variable {}!\n The only variables listed in config file are: {}.'
                                .format(file_name_args.getXLabel(),
                                        ', '.join(config_file['generate_optim_settings_file'].keys())))
            tmp_data[i][x_val_label] = str(int(round(optim_vals[i]['xVal'] / x_val_multiplier)))

            # Processing of func label
            if file_name_args.get_func_label():
                tmp_key = config_file['generate_optim_settings_file'][file_name_args.get_func_label()]
                try:
                    tmp_data[i][tmp_key] = str(int(round(float(optim_vals[i]['funcLabel']) / func_label_multiplier))) \
                        if func_label_multiplier \
                        else str(optim_vals[i]['funcLabel'])
                except ValueError:
                    tmp_data[i][tmp_key] = str(optim_vals[i]['funcLabel'])

        file_content[region_name] = tmp_data

    @staticmethod
    def get_nested_region_report_itemize_tex_code(func_lst,
                                                  summary_sources_nested,
                                                  default_optimal_vals_nested,
                                                  all_nested_funcs,
                                                  conf,
                                                  keys_units,
                                                  func_label_units,
                                                  x_val_units,
                                                  y_labels):

        res_dic = Evaluator.__get_nested_regions_report_vals(func_lst,
                                                             summary_sources_nested,
                                                             default_optimal_vals_nested,
                                                             all_nested_funcs,
                                                             conf)

        return_dic = {'statSave': [],
                      'dynSave': [],
                      'code': [],
                      'data': []}

        for ind, yLabel in enumerate(y_labels):
            code = r'''
                    ({0} \% per 1 phase)
                        \begin{{itemize}}
                            \item {1} - {2}\,{8}
                            \item Optimal: {3}
                            \item {4}\,{8} per phase - {5}\% of {2}\,{8}
                            \item Dynamic savings: {6}\% - {7}\,{8}
                        \end{{itemize}}
                    '''
            code = textwrap.dedent(code)

            code = code.format(res_dic['percentsOfOneIterRound'][ind],

                               ', '.join(filter(None, (
                               ', '.join([''.join(e) for e in zip(res_dic['mainOptimKeys'][ind], keys_units)]),
                               ''.join((str(res_dic['mainOptimFuncLabel'][ind]), func_label_units)),
                               ''.join((str(res_dic['mainOptimXValue'][ind]), x_val_units))))),

                               res_dic['currStatOptimRound'][ind],

                               '; '.join([', '.join(
                                   filter(None, (', '.join([''.join(e) for e in zip(i[ind]['keys'], keys_units)]),
                                                 ''.join((str(i[ind]['funcLabel']), func_label_units)),
                                                 ''.join((str(i[ind]['xVal']), x_val_units)))))
                                          for i in res_dic['currDynOptimsLst']]),

                               res_dic['currDynOptimsSumValRound'][ind],
                               res_dic['percentsOfStatOptimRound'][ind],
                               res_dic['dynSavingPercentsRound'][ind],
                               res_dic['dynSavingsValRound'][ind],
                               yLabel['unit'])

            data = {'y_label': yLabel,
                    'percentsOfOneIter': res_dic['percentsOfOneIterRound'][ind],
                    'mainOptim': (', '.join([''.join(e) for e in zip(res_dic['mainOptimKeys'][ind], keys_units)]),
                                  ''.join((str(res_dic['mainOptimFuncLabel'][ind]), func_label_units)),
                                  ''.join((str(res_dic['mainOptimXValue'][ind]), x_val_units))),
                    'currStatOptim': res_dic['currStatOptimRound'][ind],
                    'currDynOptims': [
                        ', '.join(filter(None, (', '.join([''.join(e) for e in zip(i[ind]['keys'], keys_units)]),
                                                ''.join((str(i[ind]['funcLabel']), func_label_units)),
                                                ''.join((str(i[ind]['xVal']), x_val_units)))))
                        for i in res_dic['currDynOptimsLst']],
                    'currDynOptimsSumVal': res_dic['currDynOptimsSumValRound'][ind],
                    'percentsOfStatOptim': res_dic['percentsOfStatOptimRound'][ind],
                    'dynSavingPercents': res_dic['dynSavingPercentsRound'][ind],
                    'dynSavingsVal': res_dic['dynSavingsValRound'][ind],
                    'yLabelUnit': yLabel['unit']}

            return_dic['statSave'].append(res_dic['currStatOptim'][ind])
            return_dic['dynSave'].append(res_dic['dynSavingsVal'][ind])
            return_dic['code'].append(code)
            return_dic['data'].append(data)

        return return_dic

    @staticmethod
    def get_nested_region_report_tex_code(func_lst,
                                          summary_sources_nested,
                                          default_optimal_vals_nested,
                                          all_nested_funcs,
                                          conf,
                                          keys_units_lst,
                                          func_label_units,
                                          x_val_units,
                                          y_labels):

        res_dic = Evaluator.__get_nested_regions_report_vals(func_lst,
                                                             summary_sources_nested,
                                                             default_optimal_vals_nested,
                                                             all_nested_funcs,
                                                             conf)

        return_dic = {'statSave': [],
                      'dynSave': [],
                      'code': [],
                      'dynOptimSettings': [],
                      'table_lines': []}

        for y_label_ind, yLabel in enumerate(y_labels):
            code = r'''
                    \\ \hline
                    {0} & {1} & {2} & {3} & {4} & {5} & {6}
                    '''

            code = textwrap.dedent(code)

            code = code.format(r'\makecell[{{{{p{{.15\textwidth}}}}}}]{{ {0} }}'
                               .format(',\\\ '.join(func_lst)),

                               r'\makecell[{{{{p{{.05\textwidth}}}}}}]{{ {0} }}'
                               .format(res_dic['percentsOfOneIterRound'][y_label_ind]),

                               r'\makecell[{{{{p{{.15\textwidth}}}}}}]{{ {0} }}'
                               .format(',\\\ '.join(filter(None, (',\\\ '.join([r'\,'.join(el)
                                                                                for el
                                                                                in zip(res_dic['mainOptimKeys'][y_label_ind],
                                                                                       keys_units_lst)]),
                                                                  r'\,'.join(
                                                                      (str(res_dic['mainOptimFuncLabel'][y_label_ind]),
                                                                       func_label_units)),
                                                                  r'\,'.join(
                                                                      (str(res_dic['mainOptimXValue'][y_label_ind]),
                                                                       x_val_units)))))),
                               r'\makecell[{{{{p{{.10\textwidth}}}}}}]{{ {0} {1} }}'
                               .format(res_dic['currStatOptimRound'][y_label_ind], yLabel['unit']),

                               r'\makecell[{{{{p{{.15\textwidth}}}}}}]{{ {0} }}'
                               .format(';\\\ '.join([',\\\ '.join(filter(None, (',\\\ '.join([r'\,'.join(el)
                                                                                              for el
                                                                                              in zip(
                                       i[y_label_ind]['keys'], keys_units_lst)]),
                                                                                r'\,'.join(
                                                                                    (str(i[y_label_ind]['funcLabel']),
                                                                                     func_label_units)),
                                                                                r'\,'.join((str(i[y_label_ind]['xVal']),
                                                                                            x_val_units)))))
                                                     for i in res_dic['currDynOptimsLst']])),

                               r'\makecell[{{{{p{{.10\textwidth}}}}}}]{{ {0}\,{1} }}'
                               .format(res_dic['currDynOptimsSumValRound'][y_label_ind], yLabel['unit']),

                               r'\makecell[{{{{p{{.10\textwidth}}}}}}]{{ {0}\,{1} ({2}\%) }}'
                               .format(res_dic['dynSavingsValRound'][y_label_ind],
                                       yLabel['unit'],
                                       res_dic['dynSavingPercentsRound'][y_label_ind])
                               )

            return_dic['statSave'].append(res_dic['currStatOptim'][y_label_ind])
            return_dic['dynSave'].append(res_dic['dynSavingsVal'][y_label_ind])
            return_dic['code'].append(code)
            return_dic['dynOptimSettings'].append([res_dic['currDynOptimsLst'][i][y_label_ind]
                                                   for i in range(len(func_lst))])

            dynamic_configuration_key_unit = []
            dynamic_func_label_unit = []
            dynamic_x_label_unit = []
            for i in res_dic['currDynOptimsLst']:
                tmp = []
                for el in zip(i[y_label_ind]['keys'], keys_units_lst):
                    tmp.append(el)
                dynamic_configuration_key_unit.append(tmp)
                dynamic_func_label_unit.append((str(i[y_label_ind]['funcLabel']), func_label_units))
                dynamic_x_label_unit.append((str(i[y_label_ind]['xVal']), x_val_units))

            line_data = {'region': func_lst,
                         'percent_of_1_phase': res_dic['percentsOfOneIterRound'][y_label_ind],
                         'static_config_key_unit': [el
                                                    for el
                                                    in zip(res_dic['mainOptimKeys'][y_label_ind],
                                                           keys_units_lst)],
                         'static_func_label_unit': (str(res_dic['mainOptimFuncLabel'][y_label_ind]),
                                                    func_label_units),
                         'static_x_label_unit': (str(res_dic['mainOptimXValue'][y_label_ind]),
                                                 x_val_units),
                         'static_config_value': (res_dic['currStatOptimRound'][y_label_ind], yLabel['unit']),
                         'dynamic_configuration_key_unit': dynamic_configuration_key_unit,
                         'dynamic_func_label_unit': dynamic_func_label_unit,
                         'dynamic_x_label_unit': dynamic_x_label_unit,
                         'dynamic_config_value': (res_dic['currDynOptimsSumValRound'][y_label_ind], yLabel['unit']),
                         'dynamic_savings': (res_dic['dynSavingsValRound'][y_label_ind],
                                             yLabel['unit'],
                                             res_dic['dynSavingPercentsRound'][y_label_ind])
                         }

            return_dic['table_lines'].append(line_data)

        return return_dic

    @staticmethod
    def get_static_optims(conf,
                          default_optimal_vals_main_lst):
        # Static optima for individual dependent variables
        stat_optims_lst = []

        avg_prog_start_optim = default_optimal_vals_main_lst.get_raw_data_dic()[conf]['optimalVal']['avgProgramStart']

        for var_data in avg_prog_start_optim:
            stat_optims_lst.append(var_data['yVal'])

        return stat_optims_lst

    @staticmethod
    def get_static_eval(conf,
                        default_optimal_vals_main,
                        keys_units,
                        func_label_units,
                        x_val_units,
                        y_label_list,
                        dyn_savings_lst=None,
                        time_energy_vars=None,
                        time_for_eng_optims=None,
                        nested_funcs_dic=None,
                        loaded_data_nested=None,
                        loaded_data_main=None):

        if time_energy_vars and None in (time_for_eng_optims, nested_funcs_dic, loaded_data_nested):
            assert loaded_data_main

        table_cols = 5
        if dyn_savings_lst:
            table_cols = 6
            text = r'''
                    \noindent
                    \begin{{table}}[H]
                    \centering
                    \begin{{adjustbox}}{{max width=\textwidth}}
                    \begin{{tabular}}{{lccccc}}
                    \multicolumn{{6}}{{c}}{{ \textbf{{Overall application evaluation}} }} \\
                    \hline
                    \makecell[{{{{p{{.22\textwidth}}}}}}]{{\textbf{{}}}}
                     & \makecell[{{{{p{{.18\textwidth}}}}}}]{{\textbf{{Default}}\\ \textbf{{settings}}}}
                     & \makecell[{{{{p{{.10\textwidth}}}}}}]{{\textbf{{Default}}\\ \textbf{{values}}}}
                     & \makecell[{{{{p{{.18\textwidth}}}}}}]{{\textbf{{Best static}}\\ \textbf{{configuration}}}}
                     & \makecell[{{{{p{{.10\textwidth}}}}}}]{{\textbf{{Static}}\\ \textbf{{Savings}}}}
                     & \makecell[{{{{p{{.10\textwidth}}}}}}]{{\textbf{{Dynamic}}\\ \textbf{{Savings}}}}
                    {0}
                    \\ \hline
                    \end{{tabular}}
                    \end{{adjustbox}}
                    \end{{table}}
                    '''
        else:
            text = r'''
                    \noindent
                    \begin{{table}}[H]
                    \centering
                    \begin{{adjustbox}}{{max width=\textwidth}}
                    \begin{{tabular}}{{lcccc}}
                    \multicolumn{{5}}{{c}}{{ \textbf{{Overall application evaluation}} }} \\
                    \hline
                    \makecell[{{{{p{{.22\textwidth}}}}}}]{{\textbf{{}}}}
                     & \makecell[{{{{p{{.18\textwidth}}}}}}]{{\textbf{{Default}}\\ \textbf{{settings}}}}
                     & \makecell[{{{{p{{.10\textwidth}}}}}}]{{\textbf{{Default}}\\ \textbf{{values}}}}
                     & \makecell[{{{{p{{.18\textwidth}}}}}}]{{\textbf{{Best static}}\\ \textbf{{configuration}}}}
                     & \makecell[{{{{p{{.10\textwidth}}}}}}]{{\textbf{{Static}}\\ \textbf{{Savings}}}}
                    {0}
                    \\ \hline
                    \end{{tabular}}
                    \end{{adjustbox}}
                    \end{{table}}
                    '''

        text = textwrap.dedent(text)

        table_lines = []

        # Static optima for individual dependent variables
        stat_optims_lst = []

        default_optimal_vals_main_dic = default_optimal_vals_main.get_raw_data_dic()

        # All values in the "overall application evaluation table"
        all_table_vals = []
        for i in range(len(y_label_list)):
            table_line = r'''
                         \\ \hline
                         {0}
                         '''
            table_line = textwrap.dedent(table_line)

            avg_prog_start_default = default_optimal_vals_main_dic[conf]['defaultVal']['avgProgramStart'][i]
            avg_prog_start_optim = default_optimal_vals_main_dic[conf]['optimalVal']['avgProgramStart'][i]

            # Values in a table row
            f_tmp = utils.replace_nth
            f2_tmp = utils.replace_every_nth
            tmp_dyn_savings = f_tmp(f_tmp(f_tmp(dyn_savings_lst[i].replace('\\', ''), ' ', '\n', 2), ' ', '\n', 2) \
                                    , ",", '', 1) if dyn_savings_lst else ''
            line_vals = (',\n'.join((y_label_list[i]['arg'], y_label_list[i]['category'])),
                         ',\n'.join(filter(None,
                                           ('\n'
                                            .join([''.join(i)
                                                   for i
                                                   in zip(avg_prog_start_default['keys'],
                                                          keys_units)]),
                                            ''
                                            .join((str(avg_prog_start_default['funcLabel']),
                                                   func_label_units)),
                                            ''.join((str(avg_prog_start_default['xVal']),
                                                     x_val_units))))),

                         ''.join((utils.get_round_num_str(avg_prog_start_default['yVal']),
                                  y_label_list[i]['unit'])),
                         ',\n'
                         .join(filter(None,
                                      ('\n'.join([''.join(i)
                                                  for i
                                                  in zip(avg_prog_start_optim['keys'],
                                                         keys_units)]),
                                       ''.join((str(avg_prog_start_optim['funcLabel']),
                                                func_label_units)),
                                       ''.join((str(avg_prog_start_optim['xVal']),
                                                x_val_units))))),

                         '{0}{1} ({2}%)'.format(str(utils.get_round_num_str(
                             avg_prog_start_default['yVal'] -
                             avg_prog_start_optim['yVal'])),
                             y_label_list[i]['unit'],
                             str(utils.get_round_num_str(100 -
                                                         (avg_prog_start_optim['yVal'] /
                                                          avg_prog_start_default['yVal'] *
                                                          100)))),
                         format(tmp_dyn_savings.replace(",", "")))

            all_table_vals.append(line_vals)

            table_line_vals = ' & '.join(filter(None, (r'\makecell[{{{{p{{.22\textwidth}}}}}}]{{ {0} }}'
                                                       .format(',\\\ '.join((y_label_list[i]['arg'],
                                                                             y_label_list[i]['category']))),

                                                       r'\makecell[{{{{p{{.18\textwidth}}}}}}]{{ {0} }}'
                                                       .format(',\\\ '
                                                               .join(filter(None,
                                                                            (',\\\ '
                                                                             .join([r'\,'.join(i)
                                                                                    for i
                                                                                    in
                                                                                    zip(avg_prog_start_default['keys'],
                                                                                        keys_units)]),
                                                                             r'\,'
                                                                             .join((str(
                                                                                 avg_prog_start_default['funcLabel']),
                                                                                    func_label_units)),
                                                                             r'\,'.join(
                                                                                 (str(avg_prog_start_default['xVal']),
                                                                                  x_val_units)))))),

                                                       r'\makecell[{{{{p{{.10\textwidth}}}}}}]{{ {0} }}'
                                                       .format(
                                                           '\,'.join(
                                                               (utils.get_round_num_str(avg_prog_start_default['yVal']),
                                                                y_label_list[i]['unit']))),

                                                       r'\makecell[{{{{p{{.18\textwidth}}}}}}]{{ {0} }}'
                                                       .format(',\\\ '
                                                               .join(filter(None,
                                                                            (',\\\ '.join([r'\,'.join(i)
                                                                                           for i
                                                                                           in zip(
                                                                                    avg_prog_start_optim['keys'],
                                                                                    keys_units)]),
                                                                             r'\,'.join((str(
                                                                                 avg_prog_start_optim['funcLabel']),
                                                                                         func_label_units)),
                                                                             r'\,'.join(
                                                                                 (str(avg_prog_start_optim['xVal']),
                                                                                  x_val_units)))))),

                                                       r'\makecell[{{{{p{{.10\textwidth}}}}}}]{{ {0} }}'
                                                       .format('{0}\,{1} ({2}\%)'.format(str(utils.get_round_num_str(
                                                           avg_prog_start_default['yVal'] -
                                                           avg_prog_start_optim['yVal'])),
                                                           y_label_list[i]['unit'],
                                                           str(utils.get_round_num_str(100 -
                                                                                       (avg_prog_start_optim['yVal'] /
                                                                                        avg_prog_start_default['yVal'] *
                                                                                        100))))),

                                                       r'\makecell[{{{{p{{.10\textwidth}}}}}}]{{ {0} }}'
                                                       .format(dyn_savings_lst[i]) if dyn_savings_lst else '')))

            table_line = table_line.format(table_line_vals)

            stat_optims_lst.append(avg_prog_start_optim['yVal'])

            table_lines.append(table_line)

        if time_energy_vars is not None:
            time_cat = time_energy_vars['time'][0]
            time_arg = time_energy_vars['time'][1]
            eng_cat = time_energy_vars['energy'][0]
            eng_arg = time_energy_vars['energy'][1]

            time_ind = [yLab for yLab in y_label_list if (yLab['category'] == time_cat and yLab['arg'] == time_arg)][0][
                'index']
            eng_ind = [yLab for yLab in y_label_list if (yLab['category'] == eng_cat and yLab['arg'] == eng_arg)][0][
                'index']

            eng_optim = default_optimal_vals_main_dic[conf]['optimalVal']['avgProgramStart'][eng_ind]
            time_def_val = default_optimal_vals_main_dic[conf]['defaultVal']['avgProgramStart'][time_ind]['yVal']
            time_u = y_label_list[time_ind]['unit']

            # Verification whether nested regions are specified - if not, 
            # the time change for eng. optimal settings is not evaluated
            single_reg = False
            if None in (time_for_eng_optims, loaded_data_nested, nested_funcs_dic):
                single_reg = True

            # Sum of times for individual regions with default settings (NOT static optimum!)

            default_settings = default_optimal_vals_main_dic[conf]['defaultVal']['avgProgramStart'][time_ind]
            if not single_reg:
                default_times = []
                # Sum of times for individual regions with energy-optimal settings

                time_with_eng_optim_settings = sum(time_for_eng_optims) if not single_reg else loaded_data_main
                for pos, reg_lst in nested_funcs_dic.items():
                    for reg in reg_lst:
                        tmp = utils.get_obj_from_path(default_settings['keys'], loaded_data_nested[reg][conf])
                        try:
                            tmp = [e for e in tmp[str(default_settings['funcLabel'])]['avgProgramStart'] if
                                   e[0] == default_settings['xVal']][0]
                        except IndexError:
                            utils.print_err('Missing data for default settings x_value ({}) in the region {}!'
                                            .format(default_settings['xVal'], reg))

                        tmp = tmp[1][time_ind]  # Default run-time (NOT static optimum)

                        default_times.append(tmp)

                sum_def_times = sum(default_times)
            else:
                time_with_eng_optim_settings = [e for e in utils.get_obj_from_path(default_settings['keys'],
                                                                                   loaded_data_main[conf])[
                    eng_optim['funcLabel']]['avgProgramStart'] if
                                                e[0] == eng_optim['xVal']][0][1][time_ind]

                tmp = utils.get_obj_from_path(default_settings['keys'], loaded_data_main[conf])
                tmp = [e for e in tmp[str(default_settings['funcLabel'])]['avgProgramStart'] if
                       e[0] == default_settings['xVal']][0]
                sum_def_times = tmp[1][time_ind]

            table_lines.append(r'\\ \hhline{{*{{ {table_cols} }}{{=}}}}'
                               r' \makecell[{{{{p{{.22\textwidth}}}}}}]{{\textbf{{Run-time change with the energy '
                               r'optimal settings:}}}}'
                               r' & \multicolumn{{ {sub_table_cols} }}{{l}}{{ {absDiff}{timeUnit} ({percentDiff}\% of default time) }}'
                               .format(absDiff=utils.get_round_num_str(time_with_eng_optim_settings - sum_def_times,
                                                                       with_sign=True),
                                       percentDiff=utils.get_round_num_str(
                                           (time_with_eng_optim_settings / sum_def_times) * 100),
                                       timeUnit=time_u,
                                       table_cols=table_cols,
                                       sub_table_cols=table_cols - 2))

            all_table_vals.append(('{absDiff}{timeUnit} ({percentDiff} % of default time)'.format(
                absDiff=utils.get_round_num_str(time_with_eng_optim_settings - sum_def_times,
                                                with_sign=True),
                timeUnit=time_u,
                percentDiff=utils.get_round_num_str(
                    (time_with_eng_optim_settings / sum_def_times) * 100)
            ),))

        text = text.format(''.join(table_lines))

        return {'code': text,
                'optimsLst': stat_optims_lst,
                'allVals': all_table_vals}

    @staticmethod
    def get_overall_savings_str(conf,
                                summary_sources_nested,
                                default_optimal_vals_nested,
                                stat_optims_lst,
                                nested_funcs_dic,
                                keys_units_lst,
                                func_label_units,
                                x_val_units,
                                y_labels,
                                time_energy_vars=None,
                                loaded_data=None):

        # TODO improve verification
        if time_energy_vars is not None:
            assert loaded_data

        reports = ordDict()

        for position, nested_funcs_lst in nested_funcs_dic.items():
            reports[position] = Evaluator.get_nested_region_report_tex_code(nested_funcs_lst,
                                                                            summary_sources_nested,
                                                                            default_optimal_vals_nested,
                                                                            list(nested_funcs_dic.values()),
                                                                            conf,
                                                                            keys_units_lst,
                                                                            func_label_units,
                                                                            x_val_units,
                                                                            y_labels)

        dyn_saves = []
        dyn_optims_settings = []
        for ind, y_label in enumerate(y_labels):
            dyn_saves.append([report['dynSave'][ind] for report in reports.values()])
            dyn_optims_settings.append([report['dynOptimSettings'][ind] for report in reports.values()])

        # Get run-time for energy-optimal settings

        times_for_optimal_eng = None
        if time_energy_vars is not None:
            times_for_optimal_eng = []
            time_cat = time_energy_vars['time'][0]
            time_arg = time_energy_vars['time'][1]
            eng_cat = time_energy_vars['energy'][0]
            eng_arg = time_energy_vars['energy'][1]

            time_ind = None
            eng_ind = None

            try:
                time_ind = \
                [y_lab for y_lab in y_labels if (y_lab['category'] == time_cat and y_lab['arg'] == time_arg)][0][
                    'index']
            except IndexError:
                utils.print_err('Your \'time_energy_vars\' variable in the config file is not consistent '
                                'with \'y_labels\'!\n'
                                'Energy category: {cat}\n'
                                'Energy argument: {arg}'.format(cat=time_cat, arg=time_arg))

            try:
                eng_ind = \
                [y_lab for y_lab in y_labels if (y_lab['category'] == eng_cat and y_lab['arg'] == eng_arg)][0]['index']
            except IndexError:
                utils.print_err('Your \'time_energy_vars\' variable in the config file is not consistent '
                                'with \'y_labels\'!\n'
                                'Energy category: {cat}\n'
                                'Energy argument: {arg}'.format(cat=eng_cat, arg=eng_arg))

            eng_optim_settings = dyn_optims_settings[eng_ind]
            eng_optim_settings = [ee for e in eng_optim_settings for ee in e]

            reg_ind = 0
            for pos, reg_lst in nested_funcs_dic.items():
                for reg in reg_lst:
                    tmp_set = eng_optim_settings[reg_ind]  # Energy-optimal settings for the region


                    tmp = utils.get_obj_from_path(tmp_set['keys'], loaded_data[reg][conf])[tmp_set['funcLabel']]
                    tmp = [e for e in tmp['avgProgramStart'] if e[0] == tmp_set['xVal']][0]
                    tmp = tmp[1][time_ind]  # Run-time of the region for energy-optimal settings


                    times_for_optimal_eng.append(tmp)

                    reg_ind += 1

        line = '{0}\,{1} of {2}\,{1} ({3}\,\%)'

        ret_lst = []
        for ind, y_label in enumerate(y_labels):
            ret_lst.append(line.format(utils.get_round_num_str(sum(dyn_saves[ind])),
                                       y_label['unit'],
                                       utils.get_round_num_str(stat_optims_lst[ind]),
                                       utils.get_round_num_str(sum(dyn_saves[ind]) / stat_optims_lst[ind] * 100)))
        return {'savingsStrLst': ret_lst,
                'timeForEngOptim': times_for_optimal_eng}

    @staticmethod
    def get_single_iter_report_itemize_tex_code(conf,
                                                loaded_data_nested,
                                                default_optimal_vals_main,
                                                default_optimal_vals_nested,
                                                stat_optims_lst,
                                                nested_funcs_dic,
                                                keys_units_lst,
                                                func_label_units,
                                                x_val_units,
                                                y_labels,
                                                time_energy_vars=None,
                                                return_tex_code=True):

        reports = ordDict()

        for position, nested_funcs_lst in sorted(nested_funcs_dic.items()):
            reports[position] = Evaluator.get_nested_region_report_tex_code(nested_funcs_lst,
                                                                            loaded_data_nested,
                                                                            default_optimal_vals_nested,
                                                                            list(nested_funcs_dic.values()),
                                                                            conf,
                                                                            keys_units_lst,
                                                                            func_label_units,
                                                                            x_val_units,
                                                                            y_labels)
        table_data = {}
        full_text = list()

        text = r'''
                    \noindent
                    \begin{{longtable}}{{lcccccc}}
                    \multicolumn{{7}}{{c}}{{ \textbf{{ {0} }} }} \\
                    \hline
                    \textbf{{Region}} & \textbf{{\% of 1 phase}} & \makecell{{\textbf{{Best static}} \\ \textbf{{configuration}}}} &
                    \makecell{{\textbf{{Value}}}} &
                    \makecell{{\textbf{{Best dynamic}} \\ \textbf{{configuration}}}} &
                    \makecell{{\textbf{{Value}}}} &
                    \makecell{{\textbf{{Dynamic}} \\ \textbf{{savings}}}}
                    {1}
                    \\ \hline
                    \multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.3\textwidth}}}}}}]{{\textbf{{Total value for static tuning for
                    significant regions}}}}}}
                    & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {2} = {3}\,{7} }} }}\\
                    \hline
                    \multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.3\textwidth}}}}}}]{{\textbf{{Total savings for dynamic tuning
                    for significant regions}} }}}}
                    & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {4} = {5}\,{7} of {3}\,{7} ({6}\,\%) }}}}
                    \\ \hline
                    \multicolumn{{3}}{{l}}{{\makecell[{{{{p{{.3\textwidth}}}}}}]{{\textbf{{Dynamic savings for application
                    runtime}}}}}}
                    & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {5}\,{7} of {8}\,{7} ({9}\,\%) }}}}
                    \\ \hline
                    \multicolumn{{3}}{{l}}{{\makecell[{{{{p{{.3\textwidth}}}}}}]{{\textbf{{Total value after savings}}}}}}
                    & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {10}\,{7} ({11}\,\% of {12}\,{7}) }}}}
                    {13}
                    \end{{longtable}}
                    '''

        text = textwrap.dedent(text)

        stat_saves = list()
        dyn_saves = list()
        func_evals_code = list()
        evals_lines_data = list()
        for ind, y_label in enumerate(y_labels):
            stat_saves.append([report['statSave'][ind] for report in reports.values()])
            dyn_saves.append([report['dynSave'][ind] for report in reports.values()])
            func_evals_code.append('\n'.join([val['code'][ind] for val in reports.values()]))
            evals_lines_data.append([val['table_lines'][ind] for val in reports.values()])

        time_u = None
        if time_energy_vars is not None:
            time_cat = time_energy_vars['time'][0]
            time_arg = time_energy_vars['time'][1]
            eng_cat = time_energy_vars['energy'][0]
            eng_arg = time_energy_vars['energy'][1]

            time_ind = [y_lab for y_lab in y_labels if (y_lab['category'] == time_cat and y_lab['arg'] == time_arg)][0][
                'index']
            eng_ind = [y_lab for y_lab in y_labels if (y_lab['category'] == eng_cat and y_lab['arg'] == eng_arg)][0][
                'index']

            time_u = y_labels[time_ind]['unit']

        run_times_for_optimal_eng = []  # Run-times for individual regions with energy-optimal settings


        # Times for individual regions with default settings (NOT static optimum!)

        default_optimal_vals_main_dic = default_optimal_vals_main.get_raw_data_dic()
        default_times = []

        if time_energy_vars:
            default_settings = default_optimal_vals_main_dic[conf]['defaultVal']['avgProgramStart'][time_ind]
            for pos, reg_lst in nested_funcs_dic.items():
                for reg in reg_lst:
                    tmp = utils.get_obj_from_path(default_settings['keys'], loaded_data_nested[reg][conf])
                    tmp = [e for e in tmp[str(default_settings['funcLabel'])]['avgProgramStart'] if
                           e[0] == default_settings['xVal']][0]
                    tmp = tmp[1][time_ind]  # Default run-time (NOT static optimum)


                    default_times.append(tmp)

        for ind, y_label in enumerate(y_labels):
            tmp = None
            if time_energy_vars is not None and eng_cat == y_label['category'] and eng_arg == y_label['arg']:
                for pos, reg_lst in sorted(nested_funcs_dic.items()):
                    # Get optimal energy settings for
                    # individual regions

                    dyn_optim_settings_eng = reports[pos]['dynOptimSettings'][eng_ind]

                    # Get run-time for energy-optimal settings
                    for reg_ind, reg in enumerate(reg_lst):
                        do = dyn_optim_settings_eng[reg_ind]
                        tmp = utils.get_obj_from_path(do['keys'], loaded_data_nested[reg][conf])[do['funcLabel']]
                        tmp = tmp['avgProgramStart']
                        tmp = [tup[1][time_ind] for tup in tmp if tup[0] == do['xVal']][0]
                        run_times_for_optimal_eng.append(tmp)

                # Extension of run-time with energy-optimal settings
                time_diff = [utils.get_round_num_str(run_times_for_optimal_eng[i] - default_times[i], with_sign=True)
                             for i in range(len(default_times))]

                grns = utils.get_round_num_str
                rtfe = run_times_for_optimal_eng
                tmp = r'\\ \hhline{{*{{7}}{{=}}}}' \
                      r' \multicolumn{{3}}{{l}}{{ \makecell[{{{{p{{.3\textwidth}}}}}}]{{ ' \
                      r'\textbf{{Run-time change with the energy optimal settings against the default time ' \
                      r'settings (region-wise):}} }} }}' \
                      r' & \multicolumn{{4}}{{r}}{{ \makecell[{{{{p{{.6\textwidth}}}}}}]{{ {} }}}}' \
                    .format('; '.join(['{}{}\,({}\%)'.format(e,
                                                             time_u,
                                                             grns(rtfe[i] / default_times[i] * 100))
                                       for i, e in enumerate(time_diff)]))
                tmp_data = (['{}{},({}%)'.format(e,
                                                 time_u,
                                                 grns(rtfe[i] / default_times[i] * 100))
                             for i, e in enumerate(time_diff)])
            else:
                tmp = ''

            full_text.append(text.format('{}, {}'.format(y_label['category'], y_label['arg']),
                                         func_evals_code[ind],
                                         ' + '.join([utils.get_round_num_str(i) for i in stat_saves[ind]]),
                                         utils.get_round_num_str(sum(stat_saves[ind])),
                                         ' + '.join([utils.get_round_num_str(i) for i in dyn_saves[ind]]),
                                         utils.get_round_num_str(sum(dyn_saves[ind])),
                                         utils.get_round_num_str(sum(dyn_saves[ind]) / sum(stat_saves[ind]) * 100),
                                         y_label['unit'],
                                         utils.get_round_num_str(stat_optims_lst[ind]),
                                         utils.get_round_num_str(sum(dyn_saves[ind]) / stat_optims_lst[ind] * 100),
                                         utils.get_round_num_str(stat_optims_lst[ind] - sum(dyn_saves[ind])),
                                         utils.get_round_num_str((stat_optims_lst[ind] - sum(dyn_saves[ind])) /
                                                                 default_optimal_vals_main.get_raw_data_dic()[conf][
                                                                     'defaultVal']['avgProgramStart'][ind][
                                                                     'yVal'] * 100),
                                         utils.get_round_num_str(
                                             default_optimal_vals_main.get_raw_data_dic()[conf]['defaultVal']
                                             ['avgProgramStart'][ind]['yVal']),
                                         tmp
                                         ))

            table_data['{}, {}'.format(y_label['category'], y_label['arg'])] = {
                'stat_saves_values': [utils.get_round_num_str(i) for i in stat_saves[ind]],
                'table_lines': evals_lines_data[ind],
                'stat_saves_sum': utils.get_round_num_str(sum(stat_saves[ind])),
                'dyn_saves_values': [utils.get_round_num_str(i) for i in dyn_saves[ind]],
                'dyn_saves_sum': utils.get_round_num_str(sum(dyn_saves[ind])),
                'sig_region_dyn_saves_percent': utils.get_round_num_str(
                    sum(dyn_saves[ind]) / sum(stat_saves[ind]) * 100),
                'y_label_unit': y_label['unit'],
                'app_dyn_saves': utils.get_round_num_str(stat_optims_lst[ind]),
                'app_dyn_saves_percent': utils.get_round_num_str(sum(dyn_saves[ind]) / stat_optims_lst[ind] * 100),
                'total_savings': utils.get_round_num_str(stat_optims_lst[ind] - sum(dyn_saves[ind])),
                'total_savings_percent': utils.get_round_num_str((stat_optims_lst[ind] - sum(dyn_saves[ind])) /
                                                                 default_optimal_vals_main.get_raw_data_dic()[conf][
                                                                     'defaultVal']['avgProgramStart'][ind][
                                                                     'yVal'] * 100),
                'total_val': utils.get_round_num_str(
                    default_optimal_vals_main.get_raw_data_dic()[conf]['defaultVal']
                    ['avgProgramStart'][ind]['yVal'])}

            if tmp:
                table_data['runtime_change'] = tmp_data
        if not return_tex_code:
            return table_data
        return '\\'.join(full_text)

    @staticmethod
    def get_all_iter_report_table_tex_code(conf,
                                           nested_func_pos,
                                           loaded_data_full_nested,
                                           default_optimal_vals_nested,
                                           nested_funcs_dic,
                                           y_labels,
                                           keys_units_lst,
                                           func_label_name,
                                           func_label_units,
                                           x_val_name,
                                           x_val_units,
                                           single_program_starts=True,
                                           num_iters_in_one_line=10,
                                           time_energy_vars=None,
                                           default_optimal_vals_main=None,
                                           return_tex_code=True):
        # TODO improve verification
        if time_energy_vars is not None:
            assert default_optimal_vals_main

        # List of functions at the given position

        nested_func_lst = nested_funcs_dic[nested_func_pos]

        # List of TeX code for individual program runs

        text_per_single_program_start = list()
        data_per_single_program_start = dict()

        keys_tmp = \
        default_optimal_vals_nested[nested_func_lst[0]].get_raw_data_dic()[conf]['optimalVal']['avgProgramStart'][0][0][
            'keys']

        # Get data about time and energy variables,
        # if specified

        default_settings = None
        if time_energy_vars is not None:
            time_cat = time_energy_vars['time'][0]
            time_arg = time_energy_vars['time'][1]
            eng_cat = time_energy_vars['energy'][0]
            eng_arg = time_energy_vars['energy'][1]

            time_ind = [y_lab for y_lab in y_labels if (y_lab['category'] == time_cat and y_lab['arg'] == time_arg)][0][
                'index']
            eng_ind = [y_lab for y_lab in y_labels if (y_lab['category'] == eng_cat and y_lab['arg'] == eng_arg)][0][
                'index']

            time_u = y_labels[time_ind]['unit']

            # Get default settings
            default_settings = default_optimal_vals_main.get_raw_data_dic()[conf]['defaultVal']['avgProgramStart'][
                time_ind]

        # Draw groups of tables for each program start

        num_of_program_starts = len(
            list(utils.get_obj_from_path(keys_tmp, loaded_data_full_nested[nested_func_lst[0]][conf]).values())
            [0]['singleProgramStarts']) if single_program_starts else 1

        for single_program_start_ind in range(num_of_program_starts):
            # Number of calls of each function in an iteration

            keys_path_tmp = default_optimal_vals_nested[nested_func_lst[0]].get_raw_data_dic()[conf]['optimalVal'] \
                ['singleProgramStarts'][single_program_start_ind][0][0]['keys']

            # Find the smallest number of iterations for all regions at the given position
            num_of_iters_lst = []

            for f in nested_func_lst:
                for it in list(utils.get_obj_from_path(keys_path_tmp,
                                                       loaded_data_full_nested[f][conf]).values()):
                    num_of_iters_lst.append(len(it['avgProgramStart'][0][1]))

            max_num_of_iters = max(num_of_iters_lst)
            min_num_of_iters = min(num_of_iters_lst)

            num_of_iters = min_num_of_iters

            tmp = (str(single_program_start_ind + 1) + '.') if single_program_starts else 'average'

            if min_num_of_iters != max_num_of_iters:
                utils.print_warning('Number of iterations for region position {pos}({regs}) '
                                    'in {startI} program start'
                                    ' ranges from {minIt} to {maxIt}.\n'
                                    'The minimal number will be evaluated in the report.'
                                    .format(pos=nested_func_pos,
                                            regs=', '.join(nested_func_lst),
                                            startI=tmp,
                                            minIt=min_num_of_iters,
                                            maxIt=max_num_of_iters))

            text = r'''
                    \large{{ \textbf{{ {1} }} }}
                    \begingroup
                    \footnotesize
                    \noindent
                    \begin{{longtable}}[l]{{ {0} }}
                        {2}
                    \end{{longtable}}
                    \endgroup
                    \clearpage
                '''

            text = textwrap.dedent(text)

            # List with indices of the last iterations in the row + 0 at the beginning
            line_ends_lst = list(range(0, num_of_iters, num_iters_in_one_line))
            if num_of_iters not in line_ends_lst:
                line_ends_lst.append(num_of_iters)

            # Sums of default values over all iterations (phases)
            default_vals_sum = [0] * len(y_labels)
            # Sums of dynamic savings over all iterations (phases)
            dyn_optims_vals_sum = [0] * len(y_labels)

            # TODO test whether it really doesn’t need to be inside the following loop
            reports_tmp = []
            for k in range(line_ends_lst[-1]):
                reports_tmp.append(Evaluator.__get_nested_regions_report_vals(nested_func_lst,
                                                                              loaded_data_full_nested,
                                                                              default_optimal_vals_nested,
                                                                              list(nested_funcs_dic.values()),
                                                                              conf,
                                                                              single_program_start_ind if single_program_starts else None,
                                                                              k))

            # TODO test whether it really doesn’t need to be inside the following loop
            tabulars_lst = []
            tabulars_data_no_tex_lst = []
            for i, lineEnd in enumerate(line_ends_lst[1:]):
                i += 1  # "compensation of indices - iterating only from the 1st element
                prev_line_end = line_ends_lst[i - 1]

                '''
                #TODO maybe move reports_tmp also above the loop with "lineEnds"
                reports_tmp = []
                for k in range(line_ends_lst[-1]):
                    reports_tmp.append(Evaluator.__get_nested_regions_report_vals(nested_func_lst,
                                                                                  loaded_data_full_nested,
                                                                                  default_optimal_vals_nested,
                                                                                  list(nested_funcs_dic.values()),
                                                                                  conf,
                                                                                  single_program_start_ind if single_program_starts else None,
                                                                                  k))
                '''

                # Iteration over all dependent variables
                # TODO rewrite .format using labels instead of indices

                for y_lab_ind, y_label in enumerate(y_labels):

                    is_eng_var = False  # Switch for warning whether there is an energy variable in the current iteration
                    if time_energy_vars is not None and y_label['category'] == eng_cat and y_label['arg'] == eng_arg:
                        is_eng_var = True

                        # Getting run-time for default settings
                        # TODO maybe move into a higher-level loop

                        run_time_default_settings = []
                        for func in nested_func_lst:
                            gofp = utils.get_obj_from_path
                            ds = default_settings
                            tmp = gofp(ds['keys'], loaded_data_full_nested[func][conf])[str(ds['funcLabel'])]
                            tmp = tmp['singleProgramStarts'][single_program_start_ind]
                            tmp = [e for e in tmp if e[0] == ds['xVal']][0][1]
                            run_time_default_settings.append(tmp)

                    if y_lab_ind == 0:
                        tabular_code = r'''
                                                     \cline{{1-{6}}}
                                                     \textbf{{Phase ID}} & {0} \\
                                                     \hhline{{*{{{6}}}{{=}}}}
                                                     \textbf{{Default {7} {8}}} & {2} \\
                                                     \cline{{1-{6}}}
                                                     \textbf{{\% per 1 phase}} & {1} \\
                                                     \cline{{1-{6}}}
                                                     \textbf{{Per phase optimal settings}} & {3} \\
                                                     \cline{{1-{6}}}
                                                     \textbf{{Dynamic savings {8}}} & {4} \\
                                                     \cline{{1-{6}}}
                                                     \textbf{{Dynamic savings [\%]}} & {5} \\ {9}
                                                     \hhline{{*{{{6}}}{{=}}}}'''
                    else:
                        tabular_code = r'''
                                                     \textbf{{Default {6} {7}}} & {1} \\
                                                     \cline{{1-{5}}}
                                                     \textbf{{\% per 1 phase}} & {0} \\
                                                     \cline{{1-{5}}}
                                                     \textbf{{Per phase optimal settings}} & {2} \\
                                                     \cline{{1-{5}}}
                                                     \textbf{{Dynamic savings {7}}} & {3} \\
                                                     \cline{{1-{5}}}
                                                     \textbf{{Dynamic savings [\%]}} & {4} \\ {8}
                                                     \hhline{{*{{{5}}}{{=}}}}'''

                    tabular_code = textwrap.dedent(tabular_code)

                    # Iteration over 1 row (i.e. numOfItersInOneLine or
                    # number until the end of the row)
                    #
                    # Create a row for each variable and finally merge them

                    reports = []
                    reports_no_tex=[]

                    run_times_diff = []  # Differences between default run-time and time for energy optimum

                    for k in range(prev_line_end, lineEnd):
                        report_tmp = reports_tmp[k]

                        # Optimal settings in the table column
                        optim_lst = []
                        optim_lst_no_tex = []

                        # Structure 'currDynOptimsLst':
                        # List of lists of dictionaries - each list corresponds to one region at the position,
                        # each dictionary then corresponds to one independent variable
                        for ii in report_tmp['currDynOptimsLst']:
                            ii = ii[y_lab_ind]
                            if all(e == '-' for e in ([ii['xVal'], ii['yVal'], ii['funcLabel']] + list(ii['keys']))):
                                optim_lst.append('-')
                                optim_lst_no_tex.append('-')
                            else:
                                optim_lst.append(r',\\ '.join(filter(None, (r',\\ '.join([' '.join(e)
                                                                                          for e
                                                                                          in zip(ii['keys'],
                                                                                                 keys_units_lst)]),
                                                                            ' '.join((str(ii['funcLabel']),
                                                                                      func_label_units)),
                                                                            ' '.join((str(ii['xVal']), x_val_units))
                                                                            ))))
                                optim_lst_no_tex.append([[' '.join(e) for e  in zip(ii['keys'],keys_units_lst)],
                                                ' '.join((str(ii['funcLabel']),func_label_units)),
                                                ' '.join((str(ii['xVal']), x_val_units))])

                        if is_eng_var:
                            # Run-time values with default settings for all functions at the position
                            run_times_def = [run_time_default_settings[i][k][time_ind]['sumVal']
                                             for i in range(len(nested_func_lst))]

                            # Energy-optimal settings for individual regions
                            eng_optim_sett = [e[eng_ind] for e in report_tmp['currDynOptimsLst']]
                            eos = eng_optim_sett

                            # Get run-time for individual energy-optimal settings
                            run_times_eng_optim = []
                            for func_ind, func in enumerate(nested_func_lst):
                                gofp = utils.get_obj_from_path
                                eos = eos[func_ind]
                                tmp = gofp(eos['keys'], loaded_data_full_nested[func][conf])[eos['funcLabel']]
                                tmp = tmp['singleProgramStarts'][single_program_start_ind]
                                tmp = [e for e in tmp if e[0] == eos['xVal']][0][1]
                                run_times_eng_optim.append(tmp)

                            run_times_eng_opt = [run_times_eng_optim[i][k][time_ind]['sumVal']
                                                 for i in range(len(nested_func_lst))]

                            # Differences in run-times (default/energy optimum) for individual regions at the position
                            run_times_diff.append([i - j for i, j in zip(run_times_eng_opt, run_times_def)])

                        # Table column
                        reports.append([report_tmp['percentsOfOneIterRound'],
                                        report_tmp['currStatOptimRound'],
                                        [r'\makecell{{ {0} }}'
                                       .format(r';\\ \\ '
                                               .join(optim_lst))] * len(report_tmp['currStatOptimRound']),
                                        report_tmp['dynSavingsValRound'],
                                        report_tmp['dynSavingPercentsRound']
                                        ])
                        reports_no_tex.append([report_tmp['percentsOfOneIterRound'],
                                               report_tmp['currStatOptimRound'],
                                               optim_lst_no_tex* len(report_tmp['currStatOptimRound']),
                                               report_tmp['dynSavingsValRound'],
                                               report_tmp['dynSavingPercentsRound']
                                               ])

                    table_lines = list(zip(*reports))
                    table_lines_no_tex = list(zip(*reports_no_tex))


                    '''
                    tabular_code = \
                        tabular_code.format(' & '.join([r'\textbf{{ {0} }}'.format(str(i))
                                                        for i in range(prev_line_end + 1, lineEnd + 1)]),
                                            ' & '.join([str(i[y_lab_ind]) for i in table_lines[0]]),
                                            ' & '.join([str(i[y_lab_ind]) for i in table_lines[1]]),
                                            ' & '.join([str(i[y_lab_ind]) for i in table_lines[2]]),
                                            ' & '.join([str(i[y_lab_ind]) for i in table_lines[3]]),
                                            ' & '.join([str(i[y_lab_ind]) for i in table_lines[4]]),
                                            len(reports) + 1,
                                            y_label['arg'], '[{}]'.format(y_label['unit']),
                                            func_label_name, '[{}]'.format(func_label_units) if func_label_units else '',
                                            x_val_name, '[{}]'.format(x_val_units) if x_val_units else ''
                                            ) \
                            if y_lab_ind == 0 else \
                            tabular_code.format(' & '.join([str(i[y_lab_ind]) for i in table_lines[0]]),
                                                ' & '.join([str(i[y_lab_ind]) for i in table_lines[1]]),
                                                ' & '.join([str(i[y_lab_ind]) for i in table_lines[2]]),
                                                ' & '.join([str(i[y_lab_ind]) for i in table_lines[3]]),
                                                ' & '.join([str(i[y_lab_ind]) for i in table_lines[4]]),
                                                len(reports) + 1,
                                                y_label['arg'], '[{}]'.format(y_label['unit']),
                                                func_label_name, '[{}]'.format(func_label_units) if func_label_units else '',
                                                x_val_name, '[{}]'.format(x_val_units) if x_val_units else ''
                                                )
                    '''

                    line_tmp = ''
                    line_tmp_no_tex = ''
                    if is_eng_var:
                        # Join with semicolons the values of individual regions at the same position
                        grns = utils.get_round_num_str
                        tmp = [';'.join([grns(e, with_sign=True) for e in it]) for it in run_times_diff]

                        # Create a table row
                        # '\\ \hhline{{*{{ {it_per_line} }}{{=}}}} \n' \
                        line_tmp = '\n\\cline{{1-{it_per_line}}}\n' \
                                   '\\textbf{{Def. and eng. optima diff[{unit}]}} & {vals} \\\\' \
                            .format(it_per_line=len(tmp) + 1,
                                    vals=' & '.join(tmp),
                                    unit=time_u)
                        line_tmp_no_tex = {'it_per_line': len(tmp) + 1, 'vals': tmp, 'unit': time_u}

                    if y_lab_ind == 0:
                        tabular_data = {
                            'phase_id': ['{0}'.format(str(i)) for i in range(prev_line_end + 1, lineEnd + 1)],
                            'default': [str(i[y_lab_ind]) for i in table_lines[1]],
                            'percent_per_one _phase': [str(i[y_lab_ind]) for i in table_lines[0]],
                            'dynamic_savings': [str(i[y_lab_ind]) for i in table_lines[3]],
                            'dynamic_saving_percent': [str(i[y_lab_ind]) for i in table_lines[4]],
                            'per_phase_optim_settings': [str(i[y_lab_ind]) for i in table_lines_no_tex[2]],
                            'y_label': y_label['arg'],
                            'y_label_unit': '[{}]'.format(y_label['unit']),
                            'reports_number': len(reports) + 1,
                            'def_and_eng_opt_diff': line_tmp_no_tex}
                        tabular_code = tabular_code.format(' & '.join([r'\textbf{{ {0} }}'.format(str(i))
                                                                       for i in range(prev_line_end + 1, lineEnd + 1)]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[0]]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[1]]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[2]]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[3]]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[4]]),
                                                           len(reports) + 1,
                                                           y_label['arg'],
                                                           '[{}]'.format(y_label['unit']),
                                                           line_tmp)
                        # func_label_name,
                        # '[{}]'.format(func_label_units) if func_label_units else '',
                        # x_val_name,
                        # '[{}]'.format(x_val_units) if x_val_units else ''
                        # )
                    else:
                        tabular_data = {'default': [str(i[y_lab_ind]) for i in table_lines[1]],
                                        'percent_per_one _phase': [str(i[y_lab_ind]) for i in table_lines[0]],
                                        'dynamic_savings': [str(i[y_lab_ind]) for i in table_lines[3]],
                                        'dynamic_saving_percent': [str(i[y_lab_ind]) for i in table_lines[4]],
                                        'per_phase_optim_settings': [str(i[y_lab_ind]) for i in table_lines_no_tex[2]],
                                        'y_label': y_label['arg'],
                                        'y_label_unit': '[{}]'.format(y_label['unit']),
                                        'reports_number':len(reports) + 1,
                                        'def_and_eng_opt_diff': line_tmp_no_tex}
                        tabular_code = tabular_code.format(' & '.join([str(i[y_lab_ind]) for i in table_lines[0]]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[1]]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[2]]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[3]]),
                                                           ' & '.join([str(i[y_lab_ind]) for i in table_lines[4]]),
                                                           len(reports) + 1,
                                                           y_label['arg'],
                                                           '[{}]'.format(y_label['unit']),
                                                           line_tmp)
                        # func_label_name,
                        # '[{}]'.format(func_label_units) if func_label_units else '',
                        # x_val_name,
                        # '[{}]'.format(x_val_units) if x_val_units else '')

                    default_vals_sum[y_lab_ind] += sum([float(i[y_lab_ind])
                                                        for i in table_lines[1] if i[y_lab_ind] != '-'])
                    dyn_optims_vals_sum[y_lab_ind] += sum([float(i[y_lab_ind])
                                                           for i in table_lines[3] if i[y_lab_ind] != '-'])

                    tabulars_lst.append(tabular_code)
                    tabulars_data_no_tex_lst.append(tabular_data)

            # Total dynamic saving over all iterations (phases)
            total_dyn_savings_lst = [(default_vals_sum[i] - dyn_optims_vals_sum[i]) for i in range(len(y_labels))]

            # Total dynamic saving in percent
            total_dyn_savings_percent_lst = []
            for i in range(len(y_labels)):
                try:
                    total_dyn_savings_percent_lst.append(100 - (total_dyn_savings_lst[i] / default_vals_sum[i] * 100))
                except ZeroDivisionError:
                    total_dyn_savings_percent_lst.append(0)

            # String for the table
            total_dyn_savings_str = '\multicolumn{{ {0} }}{{|l|}}{{\\makecell[l]{{ {1} }}}} \\\ \n\cline{{ 1-{0} }}' \
                .format(len(reports) + 1,
                        r'\textbf{{Total sum of values from dynamic savings from all phases}}\\\\{}'
                        .format(r'\\'.join([r'\textbf{{{0}}}\\'
                                            r'{1} {unit} $\rightarrow$ {2} {unit} (savings {3}\%)'
                                           .format(yLabel['arg'],
                                                   utils.get_round_num_str(default_vals_sum[i], 2),
                                                   utils.get_round_num_str(total_dyn_savings_lst[i], 2),
                                                   utils.get_round_num_str(total_dyn_savings_percent_lst[i], 2),
                                                   unit=yLabel['unit'])
                                            for i, yLabel in enumerate(y_labels)])),
                        len(reports) + 1)

            total_dyn_savings_data = []
            for i, yLabel in enumerate(y_labels):
                total_dyn_savings_data.append({'y_label':yLabel['arg'],
                                               'def_vals_sum': utils.get_round_num_str(default_vals_sum[i], 2),
                                               'total_dyn_savings': utils.get_round_num_str(total_dyn_savings_lst[i], 2),
                                               'total_dyn_savings_percent': utils.get_round_num_str(total_dyn_savings_percent_lst[i], 2),
                                               'y_label_unit': yLabel['unit']})

            text = text.format(r'| p{{.23\textwidth}} |{0}|'.format('|'.join([' c '] * num_iters_in_one_line)),
                               '{0} - {1}. program start'.format(nested_func_pos, single_program_start_ind)
                               if single_program_starts else '{0} - average program start'.format(nested_func_pos),
                               '{}\n{}'.format(''.join(tabulars_lst), total_dyn_savings_str))

            text_per_single_program_start.append(text)

            if single_program_starts:
                data_per_single_program_start[single_program_start_ind] = {'nested_func': nested_func_pos,
                                                                           'table_data': tabulars_data_no_tex_lst,
                                                                           'total_dyn_savings': total_dyn_savings_data}
            else:
                data_per_single_program_start['average_program_start'] = {'nested_func': nested_func_pos,
                                                                          'table_data': tabulars_data_no_tex_lst,
                                                                          'total_dyn_savings': total_dyn_savings_data}

        if not return_tex_code:
            return data_per_single_program_start
        return '\n'.join(text_per_single_program_start)

    @staticmethod
    def create_optimal_settings_files(root_folder,
                                      loaded_data_main,
                                      default_optimal_vals_main,
                                      default_optimal_vals_avg_nested,
                                      file_name_args,
                                      x_val_multiplier,
                                      func_label_multiplier,
                                      y_labels,
                                      config_file):

        utils.print_info('Creating optimSettings file...')

        for conf in sorted(loaded_data_main.get_configurations()):
            file_content = {}

            # Main region
            Evaluator.__assemble_optim_settings_struct(file_content,
                                                       default_optimal_vals_main,
                                                       conf,
                                                       config_file,
                                                       file_name_args,
                                                       y_labels,
                                                       x_val_multiplier,
                                                       func_label_multiplier)

            # Inner regions
            for reg in default_optimal_vals_avg_nested.values():
                Evaluator.__assemble_optim_settings_struct(file_content,
                                                           reg,
                                                           conf,
                                                           config_file,
                                                           file_name_args,
                                                           y_labels,
                                                           x_val_multiplier,
                                                           func_label_multiplier)

            # Write JSON structure with optimal settings to a file
            for y_label_ind, y_label in enumerate(y_labels):
                # Creating a JSON structure from the dictionary
                json_struct = json.dumps(utils.get_ith_el_from_dic(file_content, y_label_ind),
                                         sort_keys=True,
                                         indent=4)

                with open(utils.expand_path(root_folder) + '/{}.opts'.format('-'.join(filter(None, (y_label['category'],
                                                                                                    y_label['arg'],
                                                                                                    '-'.join(conf
                                                                                                             if conf is not None
                                                                                                             else ()))))),
                          mode='w') as file:
                    file.write(json_struct)

        utils.print_info('OptimSettings file succesfully created.')

    @staticmethod
    def perform_DBSCAN(y_labels, detail_data):
        # Detailed data for individual regions - filtered
        # from data that are not y_label
        filtered_detail_data = ordDict()

        for y_label in [e['arg'] for e in y_labels]:
            filtered_detail_data[y_label] = ordDict()
            # Loading measured values for the given y_label
            for reg, lst in detail_data.items():
                utils.print_info('Performing cluster analysis (DBSCAN) of {} for the region {}.'.format(y_label, reg))
                all_vals_per_reg = []  # Data for all calls of one region in default settings
                calltree_lst = []      # List with calltree for all calls of one region

                # It happens that 'lst' contains the same callpaths repeatedly
                # - I will unify all data under one callpath
                dic = ordDict()

                for tup in lst:
                    # tup - jedno volani regionu
                    # tup[0] - calltree, tup[1] - list namerenych hodnot
                    if tup[0] not in dic:
                        dic[tup[0]] = []

                    dic[tup[0]].extend(tup[1])

                for tup in list(dic.items()):
                    # tup - one region call
                    # tup[0] - calltree, tup[1] - list of measured values
                    all_vals_per_reg.append(float([e for e in tup[1] if e[0] == y_label][0][1]))
                    calltree_lst.append(tup[0])

                # Perform cluster analysis using the DBSCAN algorithm
                std = numpy.std(all_vals_per_reg)

                # Estimate the distance between values within one cluster

                # TODO consider whether there is a better way than a multiple
                # of the standard deviation

                tmp = sorted(all_vals_per_reg)
                eps_estimate = 1
                if len(tmp) > 1:
                    eps_estimate = std * 0.3
                if eps_estimate == 0:
                    eps_estimate = 1

                db = sklearn.cluster.DBSCAN(eps=eps_estimate, min_samples=1) \
                    .fit(numpy.array(all_vals_per_reg).reshape(-1, 1))

                # Add filtered data with indices of individual clusters for the region into the dictionary
                sorted_lst = sorted(list(zip(calltree_lst, all_vals_per_reg, db.labels_)), key=lambda e: e[2])
                filtered_detail_data[y_label][reg] = sorted_lst

        return filtered_detail_data


class BaselineChangeStrategy(abc.ABC):
    @abc.abstractmethod
    def __apply_to_single_prog_starts(self, baseline, data, eng_ind, time_ind, settings):
        pass

    @abc.abstractmethod
    def __recompute_avg_prog_start(self, data, eng_ind):
        pass

    def apply_base(self, baseline, data, eng_ind, time_ind, settings_lst):
        # Process settings for the baseline given by an arithmetic expression
        settings = {}
        if isinstance(baseline, str):
            settings['conf'] = settings_lst[0]
            settings['keys'] = [float(e) for e in settings_lst[1:-1]]
            settings['funcLab'] = float(settings_lst[-1])

        self.__apply_to_single_prog_starts(baseline, data, eng_ind, time_ind, settings)
        self.__recompute_avg_prog_start(data, eng_ind)


class BaseLineChangeStrategyFull(BaselineChangeStrategy):
    def _BaselineChangeStrategy__apply_to_single_prog_starts(self, baseline, data, eng_ind, time_ind, settings):
        if settings:
            conf = settings['conf']
            keys = settings['keys']
            func_lab = settings['funcLab']

        for prog_start in data['singleProgramStarts']:
            for x_val_tup in prog_start:
                x_lab = x_val_tup[0]  # For possible baseline evaluation

                for it in x_val_tup[1]:
                    time_tmp = it[time_ind]['sumVal']
                    try:
                        if isinstance(baseline, str):
                            baseline = eval(baseline)
                        it[eng_ind]['sumVal'] += time_tmp * baseline
                    except TypeError:
                        utils.print_err('Some of the values listed in config.baseline variable is not numerical\n'
                                        'or it can not be indexed!')
                    except IndexError:
                        utils.print_err('Non-existent index listed in config.baseline!')
                    except NameError:
                        utils.print_err('Some variable listed in config.baseline does not exist!')

    def _BaselineChangeStrategy__recompute_avg_prog_start(self, data, eng_ind):
        tmp_dic = {}  # Dictionary with "collected" values for individual calls

        for prog_start in data['singleProgramStarts']:
            for x_val_tup in prog_start:
                for it_ind, it in enumerate(x_val_tup[1]):
                    try:
                        tmp_dic[x_val_tup[0]][it_ind].append(it[eng_ind]['sumVal'])
                    except KeyError:
                        tmp_dic[x_val_tup[0]] = [[it[eng_ind]['sumVal']]]
                    except IndexError:
                        tmp_dic[x_val_tup[0]].append([it[eng_ind]['sumVal']])

        # Calculate averages
        for x_val in tmp_dic:
            for it_ind, it in enumerate(tmp_dic[x_val]):
                tmp_dic[x_val][it_ind] = numpy.mean(it)

        # Write new average values
        for tup_ind, tup in enumerate(data['avgProgramStart']):
            for it_ind in range(len(tup[1])):
                try:
                    # Handling missing iterations
                    # TODO do it better (more clearly)

                    tmp = tmp_dic[tup[0]][it_ind]
                except IndexError:
                    tmp = None

                data['avgProgramStart'][tup_ind][1][it_ind][eng_ind] = tmp


class BaseLineChangeStrategyGeneral(BaselineChangeStrategy):
    def _BaselineChangeStrategy__apply_to_single_prog_starts(self, baseline, data, eng_ind, time_ind, settings):
        if settings:
            conf = settings['conf']
            keys = settings['keys']
            func_lab = settings['funcLab']

        for prog_start in data['singleProgramStarts']:
            for x_val_tup in prog_start:
                x_lab = x_val_tup[0]  # For possible baseline evaluation

                time_tmp = x_val_tup[1][time_ind]
                try:
                    if isinstance(baseline, str):
                        baseline = eval(baseline)
                    x_val_tup[1][eng_ind] += time_tmp * baseline
                except TypeError:
                    utils.print_err('Some of the values listed in config.baseline variable is not numerical\n'
                                    'or it can not be indexed!')
                except IndexError:
                    utils.print_err('Non-existent index listed in config.baseline!')
                except NameError:
                    utils.print_err('Some variable listed in config.baseline does not exist!')

    def _BaselineChangeStrategy__recompute_avg_prog_start(self, data, eng_ind):
        tmp_dic = {}  # Dictionary with "collected" values for individual calls
        for prog_start in data['singleProgramStarts']:
            for x_val_tup in prog_start:
                try:
                    tmp_dic[x_val_tup[0]].append(x_val_tup[1][eng_ind])
                except KeyError:
                    tmp_dic[x_val_tup[0]] = [x_val_tup[1][eng_ind]]

        # Calculate averages
        for x_val, vals in tmp_dic.items():
            tmp_dic[x_val] = numpy.mean(vals)

        # Write new average values
        for tup_ind, tup in enumerate(data['avgProgramStart']):
            data['avgProgramStart'][tup_ind][1][eng_ind] = tmp_dic[tup[0]]
