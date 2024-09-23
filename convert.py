import os
import math
import tkinter
from tkinter import filedialog
import re

def GetUnits(lines):
    # Unit Format: length_units  dim_units
    units_num = []
    units_text = {}
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
    #print('Node Dict Length: ' + str(len(node_dict)))
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
    #print('Member Dict Length: ' + str(len(member_dict)))
    return member_dict

def GetNodePos(Nodes, ID):
    #print(Nodes)
    Pos = {'label': Nodes[int(ID)][0],'x': float(Nodes[int(ID)][1]), 'y': float(Nodes[int(ID)][2]), 'z': float(Nodes[int(ID)][3])}
    return Pos

def GetMemberAxis(Node1, Node2):
    if Node1['y'] == Node2['y'] and Node1['z'] == Node2['z']:
        return 'X-Axis'
    elif Node1['x'] == Node2['x'] and Node1['z'] == Node2['z']:
        return 'Y-Axis'
    elif Node1['x'] == Node2['x'] and Node1['y'] == Node2['y'] :
        return 'Z-Axis'
    else:
        return 'No Axis'

def GetOffsets(Shape, MemberRot):
    # Splits into Height, Width, and Wall Thickness (if applicable)
    MatDim = Shape.split('X')
    Temp = MatDim[0]
    Temp = Temp.replace('RE', '')
    MatDim[0] = Temp
    if float(MemberRot) == 90.0 or float(MemberRot) == 270.0:
        temp_height = MatDim[0]
        temp_width = MatDim[1]
        MatDim[0] = float(temp_width)/2
        MatDim[1] = float(temp_height)/2
    else:
        MatDim[0] = float(MatDim[0])/2
        MatDim[1] = float(MatDim[1])/2
    if len(MatDim) == 3:
        MatDim[2] = float(MatDim[2])
    return MatDim

def GetXYTheta(Node1, Node2):
    if ((Node2['x'] - Node1['x']) != 0):
        Theta = math.atan2((Node2['y'] - Node1['y']), (Node2['x'] - Node1['x'])) % math.pi
    else:
        Theta = 0
    return Theta

def GetXZTheta(Node1, Node2):
    if ((Node2['x'] - Node1['x']) != 0):
        Theta = math.atan2((Node2['z'] - Node1['z']), (Node2['x'] - Node1['x'])) % math.pi
    else:
        Theta = 0
    return Theta

def GetZYTheta(Node1, Node2):
    if ((Node2['z'] - Node1['z']) != 0):
        Theta = math.atan2((Node2['y'] - Node1['y']), (Node2['z'] - Node1['z'])) % math.pi
    else:
        Theta = 0
    return Theta

def RotPos(Node, Offset, XYT, XZT, ZYT):
    Rotated = {}
    #                           Changes due to XY angle   Changes due to ZY angle   Changes due to XZ angle
    Rotated['X1'] = Node['x'] - Offset[0]*math.sin(XYT)                           + Offset[1]*math.sin(XZT)
    Rotated['X2'] = Node['x'] - Offset[0]*math.sin(XYT)                           - Offset[1]*math.sin(XZT)
    Rotated['X3'] = Node['x'] + Offset[0]*math.sin(XYT)                           + Offset[1]*math.sin(XZT)
    Rotated['X4'] = Node['x'] + Offset[0]*math.sin(XYT)                           - Offset[1]*math.sin(XZT)
    Rotated['Y1'] = Node['y'] - Offset[0]*math.cos(XYT) - Offset[1]*math.sin(ZYT) 
    Rotated['Y2'] = Node['y'] - Offset[0]*math.cos(XYT) + Offset[1]*math.sin(ZYT) 
    Rotated['Y3'] = Node['y'] + Offset[0]*math.cos(XYT) - Offset[1]*math.sin(ZYT) 
    Rotated['Y4'] = Node['y'] + Offset[0]*math.cos(XYT) + Offset[1]*math.sin(ZYT) 
    Rotated['Z1'] = Node['z']                           - Offset[1]*math.cos(ZYT) - Offset[1]*math.sin(XZT)
    Rotated['Z2'] = Node['z']                           + Offset[1]*math.cos(ZYT) + Offset[1]*math.sin(XZT)
    Rotated['Z3'] = Node['z']                           - Offset[1]*math.cos(ZYT) - Offset[1]*math.sin(XZT)
    Rotated['Z4'] = Node['z']                           + Offset[1]*math.cos(ZYT) + Offset[1]*math.sin(XZT)
    return Rotated

def GetFaces(face_arr, line_no):
    face_arr.append('skip')
    face_arr.append([8*line_no + 1, 8*line_no + 2, 8*line_no + 3])
    face_arr.append([8*line_no + 2, 8*line_no + 3, 8*line_no + 4])
    face_arr.append([8*line_no + 5, 8*line_no + 6, 8*line_no + 7])
    face_arr.append([8*line_no + 6, 8*line_no + 7, 8*line_no + 8])
    face_arr.append([8*line_no + 3, 8*line_no + 4, 8*line_no + 7])
    face_arr.append([8*line_no + 4, 8*line_no + 7, 8*line_no + 8])
    face_arr.append([8*line_no + 1, 8*line_no + 3, 8*line_no + 5])
    face_arr.append([8*line_no + 3, 8*line_no + 5, 8*line_no + 7])
    face_arr.append([8*line_no + 1, 8*line_no + 2, 8*line_no + 5])
    face_arr.append([8*line_no + 2, 8*line_no + 5, 8*line_no + 6])
    face_arr.append([8*line_no + 2, 8*line_no + 4, 8*line_no + 6])
    face_arr.append([8*line_no + 4, 8*line_no + 6, 8*line_no + 8])
    return face_arr

def Translate_Points(Nodes, Members):
    vertex_arr = []
    face_arr = []
    line_no = -1
    while line_no < len(Members) - 1:
        line_no += 1
        NodePos1 = GetNodePos(Nodes, Members[line_no][3])
        NodePos2 = GetNodePos(Nodes, Members[line_no][4])
        MemberAxis = GetMemberAxis(NodePos1, NodePos2)

        Offset = GetOffsets(Members[line_no][2], Members[line_no][6])

        XYTheta = GetXYTheta(NodePos1, NodePos2)
        XZTheta = GetXZTheta(NodePos1, NodePos2)
        ZYTheta = GetZYTheta(NodePos1, NodePos2)

        RotNodePos1 = RotPos(NodePos1, Offset, XYTheta, XZTheta, ZYTheta)
        RotNodePos2 = RotPos(NodePos2, Offset, XYTheta, XZTheta, ZYTheta)

        vertex_arr.append([RotNodePos1['X1'], RotNodePos1['Y1'], RotNodePos1['Z1']])
        vertex_arr.append([RotNodePos1['X2'], RotNodePos1['Y2'], RotNodePos1['Z2']])
        vertex_arr.append([RotNodePos1['X3'], RotNodePos1['Y3'], RotNodePos1['Z3']])
        vertex_arr.append([RotNodePos1['X4'], RotNodePos1['Y4'], RotNodePos1['Z4']])
        vertex_arr.append([RotNodePos2['X1'], RotNodePos2['Y1'], RotNodePos2['Z1']])
        vertex_arr.append([RotNodePos2['X2'], RotNodePos2['Y2'], RotNodePos2['Z2']])
        vertex_arr.append([RotNodePos2['X3'], RotNodePos2['Y3'], RotNodePos2['Z3']])
        vertex_arr.append([RotNodePos2['X4'], RotNodePos2['Y4'], RotNodePos2['Z4']])

        face_arr = GetFaces(face_arr, line_no)

        print('Member ' + Members[line_no][0] + ': ')
        print('Axis: ' + MemberAxis)
        print('NodePos1: ' + str(NodePos1))
        print('NodePos2: ' + str(NodePos2))
        print('Offsets: ' + str(Offset))
        print('XYTheta: ' + str(XYTheta * 180/math.pi))
        print('XZTheta: ' + str(XZTheta * 180/math.pi))
        print('ZYTheta: ' + str(ZYTheta * 180/math.pi))
        print(str(RotNodePos1))
        print(str(RotNodePos2))

        #print('Node ' + Node1['label'] + ': X: ' + Node1['x'] + ': Y: ' + Node1['y'] + ': Z: ' + Node1['z'])
        #print('Node ' + Node2['label'] + ': X: ' + Node2['x'] + ': Y: ' + Node2['y'] + ': Z: ' + Node2['z'])
    return vertex_arr, face_arr
            
            

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
    #print(data)
    Units = GetUnits(data)
    #print(Units)
    Nodes = GetNodes(data)
    #print(Nodes)
    Members = GetMembers(data)
    #print(Members)
    Vertices = Translate_Points(Nodes, Members)
    #print(Vertices[0])
    with open("test.obj", 'w') as f:
        f.write("# OBJ file\n")
        f.write("o obj_0\n") 
        for vertex in Vertices[0]:
            f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
        i=1
        for face in Vertices[1]:
            if isinstance(face, str) and face.startswith('skip'):
                f.write('\n')
                i=i+1
            else:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")