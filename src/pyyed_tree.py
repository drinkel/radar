#!/usr/bin/env python3
#import pydot

from __future__ import print_function
import sys
sys.path.append('lib/')
import pyyed
import matplotlib
from packaging import version
if version.parse(matplotlib.__version__) < version.parse("2.0.3"):
        raise Exception("Matplotlib version must be >= 2.0.3, while yours is {}!".format(matplotlib.__version__))    
from matplotlib import pyplot as pp
pp.switch_backend('QtAgg')
from matplotlib import image as mpimg
import os

from runpy import run_path


def browse_dir(path,ownData=None,destFilePath = None, givenRegStruct = None, givenRegTimes = None, timeIncl = False):
    d = ownData
    D = d["all_nested_funcs_dic"]
    chs_regs = list(D.keys())

    if givenRegTimes and givenRegStruct:
        reg_structure = givenRegStruct
        reg_times = givenRegTimes
        main_reg = None
        i = 0
        for subdir, dirs, files in os.walk(path):
            if not i:
                i += 1
                continue

            with open('{}/{}'.format(subdir,files[0])) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('# CALLTREE') and main_reg is None and line.endswith('init_0'):
                        main_reg = subdir.split('/')[-1]
                        break
            if main_reg:
                break
       
    elif givenRegTimes and not givenRegStruct:
        reg_times = givenRegTimes
        i = 0
        main_reg = None
        reg_structure = {}
        for subdir, dirs, files in os.walk(path):
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
                        if main_reg is None and line.endswith('init_0'):
                            main_reg = subdir.split('/')[-1]

            reg_structure[subdir.split('/')[-1]] = call_list
    elif givenRegStruct and not givenRegTimes:
        reg_structure = givenRegStruct
        i = 0
        main_reg = None
        reg_times = {}
        for subdir, dirs, files in os.walk(path):
            if not i:
                i += 1
                continue

            with open('{}/{}'.format(subdir,files[0])) as f:
                for line in f:
                    line = line.strip()
                    line2 = line.split(';')
                    if line.startswith('# CALLTREE') and main_reg is None and line.endswith('init_0'):
                        main_reg = subdir.split('/')[-1]
                    if line.startswith('Runtime of function'):
                        tmp2 = float(line.split(',')[-1])
                        reg_times[subdir.split('/')[-1]] = tmp2

    else:
        i = 0
        main_reg = None
        reg_structure = {}
        reg_times = {}
        for subdir, dirs, files in os.walk(path):
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
                        if main_reg is None and line.endswith('init_0'):
                            main_reg = subdir.split('/')[-1]
                    if line.startswith('Runtime of function'):
                        tmp2 = float(line.split(',')[-1])
                        reg_times[subdir.split('/')[-1]] = tmp2

            reg_structure[subdir.split('/')[-1]] = call_list

    G = pyyed.Graph()
    for k in reg_structure.keys():
        if timeIncl:
            nodeStr = "{0}\n{1:.4f} s".format(k,reg_times[k])
        else:
            nodeStr = str(k)
        if k == main_reg:
            G.add_node(nodeStr,shape="roundrectangle", font_style="bolditalic",width = "90",height="40")
        else:
            if k in chs_regs:
                G.add_node(nodeStr, shape_fill= "#ffff00", font_style="bolditalic", width="90", height="40")
            else:
                G.add_node(nodeStr, font_style="bolditalic", width="90", height="40")

    for k,v in reg_structure.items():
        for e in v:
            if timeIncl:
                G.add_edge("{0}\n{1:.4f} s".format(e,reg_times[e]),"{0}\n{1:.4f} s".format(k,reg_times[k]))
            else:
                G.add_edge(str(e),str(k))

    if destFilePath:
        yEd_file = open(destFilePath, "w")
        yEd_file.write(G.get_graph())
        yEd_file.close()
    


if __name__=='__main__':
    browse_dir('/home/david/Documents/SGS18-READEX/DATA/ESPRESO')

