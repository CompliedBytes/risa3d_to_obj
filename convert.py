import os
import math
import tkinter
from tkinter import filedialog

def GetUnits(lines):
    units_num = []
    units_text = []
    num_lines = len(lines)
    curr_line = 0
    for line in lines:
        if '[UNITS]' in lines[curr_line]:
            units_num = lines[curr_line + 1].split(' ')
            break
        curr_line += 1
    
    #Check length_units and translate into text-based flags.
    if units_num[1] == '0':
        units_text.append('ft')
    elif units_num[1] == '1':
        units_text.append('in')
    elif units_num[1] == '2':
        units_text.append('m')
    elif units_num[1] == '3':
        units_text.append('cm')
    elif units_num[1] == '4':
        units_text.append('mm')
    
    #Check dim_units and translate into text-based flags.
    if units_num[1] == '0':
        units_text.append('in')
    elif units_num[1] == '1':
        units_text.append('cm')
    elif units_num[1] == '2':
        units_text.append('mm')
    
    return units_text

def GetNodes(lines):
    node_arr = []
    node_flag = False
    for line in lines:
        if '[NODES]' in line:
            node_flag = True
        elif '[END_NODES]' in line:
            node_flag = False
        elif node_flag == True:
            curr_node = line.split('   ')
            curr_len = len(curr_node)
            flag_num = 0
            while (flag_num < curr_len):    
                if curr_node[flag_num] == '' or curr_node[flag_num] == '  ':
                    curr_node.remove(curr_node[flag_num])
                    curr_len -= 1
                elif '"' in curr_node[flag_num]:
                    curr_node[flag_num] = curr_node[flag_num].replace('"', '')
                else:
                    flag_num += 1
            end_of_curr_node = curr_node[flag_num - 1].split(' ')
            curr_node.remove(curr_node[flag_num - 1])
            for flag in end_of_curr_node:
                if ';' in flag:
                    flag = flag.split(';')[0]
                curr_node.append(flag)
            node_arr.append(curr_node)
    return node_arr

with open("2024 SB V4.5.r3d") as file:
    data=file.read().split('\n')
    print(GetUnits(data))
    print(GetNodes(data))

    #print(data)