import os
import math
import tkinter
from tkinter import filedialog
import re

def GetUnits(lines):
    # Unit Format: length_units  dim_units
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
        units_text['length_units'] = 'ft'
    elif units_num[1] == '1':
        units_text['length_units'] = 'in'
    elif units_num[1] == '2':
        units_text['length_units'] = 'm'
    elif units_num[1] == '3':
        units_text['length_units'] = 'cm'
    elif units_num[1] == '4':
        units_text['length_units'] = 'mm'
    
    #Check dim_units and translate into text-based flags.
    if units_num[1] == '0':
        units_text['dim_units'] = 'in'
    elif units_num[1] == '1':
        units_text['dim_units'] = 'cm'
    elif units_num[1] == '2':
        units_text['dim_units'] = 'mm'
    
    return units_text

def GetNodes(lines):
    # Node Format: Name/ID  X coord, Y coord, Z coord
    node_dict = {}
    node_flag = False
    line_no = 1
    for line in lines:
        if '[NODES]' in line:
            node_flag = True
        elif '[END_NODES]' in line:
            node_flag = False
            break
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
            node_dict[line_no] = curr_node
            line_no += 1
    #print(node_dict)
    return node_dict

def GetMembers(lines):
    member_dict = {}
    member_flag = False
    curr_line = []
    line_no = 0
    for line in lines:
        if '[.MEMBERS_MAIN_DATA]' in line:
            member_flag = True
        elif '[.END_MEMBERS_MAIN_DATA]' in line:
            member_flag = False
            break
        elif member_flag == True:
            curr_line = line.split('" ')
            curr_len = len(curr_line)
            flag_num = 0
            while (flag_num < curr_len):
                if flag_num == 0:
                    curr_line[flag_num] = curr_line[flag_num].replace('"', '')
                    curr_line[flag_num] = curr_line[flag_num].replace(' ', '')
                    flag_num += 1
                elif flag_num == 1:
                    member_name = ''
                    temp_flag = curr_line[flag_num].split(' ')
                    temp_flag[0] = temp_flag[0].split('"')[1]
                    while ('' in temp_flag):
                        temp_flag.remove('')
                    temp_len = len(temp_flag)
                    curr_idx = 0
                    while (curr_idx < temp_len):
                        if curr_idx == temp_len - 1:
                            member_name += temp_flag[curr_idx]
                        else:
                            member_name += temp_flag[curr_idx]
                            member_name += ' '
                        curr_idx += 1
                    curr_line[flag_num] = member_name
                    flag_num += 1
                elif flag_num == 2:
                    temp_flag = curr_line[flag_num].split(' ')[0]
                    temp_flag = temp_flag.split('"')[1]
                    curr_line[flag_num] = temp_flag
                    flag_num += 1
                elif flag_num == 3:
                    temp_flag = curr_line[flag_num].split(' ')
                    while '' in temp_flag:
                        temp_flag.remove('')
                    temp_len = len(temp_flag)
                    curr_len += temp_len - 1
                    for flag in temp_flag:
                        if flag_num == 3:
                            curr_line[flag_num] = flag
                        else:
                            curr_line.insert(flag_num, flag)
                        flag_num += 1
                elif ' ' in curr_line[flag_num]:
                    temp_flag = curr_line[flag_num].replace(' ','')
                    if temp_flag == '':
                        curr_line.remove(curr_line[flag_num])
                        curr_len -= 1
                    else:
                        curr_line[flag_num] = temp_flag
                        flag_num += 1
                elif ';' in curr_line[flag_num]:
                    temp_flag = curr_line[flag_num].replace(';','')
                    curr_line[flag_num] = temp_flag
                    flag_num += 1
                else:
                    flag_num += 1
            member_dict[line_no] = curr_line
            line_no += 1
    return member_dict

def GetNodePos(Nodes, ID):
    #print(Nodes)
    Pos = {'label': Nodes[int(ID)][0],'x': Nodes[int(ID)][1], 'y': Nodes[int(ID)][2], 'z': Nodes[int(ID)][3]}
    return Pos

def Translate_Sides(Nodes, Members):
        for member in Members:
            Node1 = GetNodePos(Nodes, member[3])
            Node2 = GetNodePos(Nodes, member[4])
            print(str(member[0]) + ' Node 1: ' + str(Node1) + ' Node 2: ' + str(Node2))


def extractHeadings(file):
    data = file.read()
    pattern = r'\[(?!\.{0,2}END)[^\]]*\]'
    # this regex matches all strings inside brackets that dont have "END" at the begining
    matches = re.findall(pattern,data)
    headings = [match[1:-1] for match in matches]
    return headings

f = open("2024 SB V4.5.r3d","r")

#parseData(f)

with open("2024 SB V4.5.r3d","r") as file:
    data=file.read().split('\n')
    ##print(GetUnits(data))
    ##print(GetNodes(data))
    #print(GetMembers(data))
    #print(data)
    Nodes = GetNodes(data)
    Members = GetMembers(data)
    #Translate_Sides(Nodes, Members)
    Node1 = GetNodePos(Nodes, Members[0][3])
    Node2 = GetNodePos(Nodes, Members[0][4])
    print('Member ' + str(Members[0][0]) + ': ')
    print('Node ' + Node1['label'] + ': X: ' + Node1['x'] + ': Y: ' + Node1['y'] + ': Z: ' + Node1['z'])
    print('Node ' + Node2['label'] + ': X: ' + Node2['x'] + ': Y: ' + Node2['y'] + ': Z: ' + Node2['z'])