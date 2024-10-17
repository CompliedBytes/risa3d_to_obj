import math
import re
from dataclasses import dataclass
#import numpy as np

@dataclass
class Node:
    label: str
    x: float
    y: float
    z: float

@dataclass
class Member:
    label: str
    design_list: str
    shape_label: str
    # These are the node numbers in sequential order and not the node label for some reason in the RISA format
    inode: int
    jnode: int
    knode: int
    rotation: float
    offset: int
    material: int

def GetUnits(data):
    # Unit Format: length_units  dim_units
    units_text = {}
    data = data[0].split(' ')
    #Check length_units and translate into text-based flags.
    match data[1]:
        case '0':
            units_text['length_units'] = 'ft'
        case '1':
            units_text['length_units'] = 'in'
        case '2':
            units_text['length_units'] = 'm'
        case '3':
            units_text['length_units'] = 'cm'
        case '4':
            units_text['length_units'] = 'mm'
    
    #Check dim_units and translate into text-based flags.
    match data[2]:
        case'0':
            units_text['dim_units'] = 'in'
        case '1':
            units_text['dim_units'] = 'cm'
        case '2':
            units_text['dim_units'] = 'mm'
    
    return units_text


# This function is used to extract the float from the scientific notation
# This probably won't be needed since you can directly convert the string to float
def extract_float(numStr):
    sci = numStr.split('e+')
    num = float(sci[0])*10**(int(sci[1]))
    return num

# This function is used to get the nodes from the risa file
def get_nodes(data):
    # Node Format: Name/ID  X coord, Y coord, Z coord
    nodes = []
    for line in data:
        line = line[1:-2].strip().split('"')
        line[0] = line[0].strip()
        label = line[0]
        line = line[1].split()
        x = float(line[0])
        y = float(line[1])
        z = float(line[2])
        node = Node(label, x, y, z)
        nodes.append(node)
    return nodes

# This function is used to get the memebers from the risa file
def get_members(data):
    members = []
    for line in data:
        line = line[1:-2].strip().split('"')
        for i,s in enumerate(line):
            line[i] = s.strip('"')
            line[i] = s.strip()
        line.pop(1)
        line.pop(2)
        temp = line[3].split()

        label = line[0]
        design_list = line[1]
        shape_label = line[2]
        inode = temp[0]
        jnode = temp[1]
        knode = temp[2]
        rotation = temp[3]
        offset = temp[4]
        material = temp[7]

        member = Member(label, design_list, shape_label, inode, jnode, knode, rotation, offset, material)
        members.append(member)
    return members


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

def Translate_Points(Nodes, Members):
        line_no = -1
        while line_no < len(Members) - 1:
            line_no += 1
            NodePos1 = GetNodePos(Nodes, Members[line_no][3])
            NodePos2 = GetNodePos(Nodes, Members[line_no][4])
            MemberAxis = GetMemberAxis(NodePos1, NodePos2)
            if 1 == 1:#MemberAxis == 'X-Axis' and int(NodePos1['z']) == 0:
                Offset = GetOffsets(Members[line_no][2], Members[line_no][6])
                XYTheta = GetXYTheta(NodePos1, NodePos2)
                XZTheta = GetXZTheta(NodePos1, NodePos2)
                ZYTheta = GetZYTheta(NodePos1, NodePos2)
                RotNodePos1 = RotPos(NodePos1, Offset, XYTheta, XZTheta, ZYTheta)
                RotNodePos2 = RotPos(NodePos2, Offset, -XYTheta, -XZTheta, -ZYTheta)
                print('Member ' + Members[line_no][0] + ': ')
                print('Axis: ' + MemberAxis)
                print('NodePos1: ' + str(NodePos1))
                #print('NodePos2: ' + str(NodePos2))
                print('Offsets: ' + str(Offset))
                print('XYTheta: ' + str(XYTheta * 180/math.pi))
                print('XZTheta: ' + str(XZTheta * 180/math.pi))
                print('ZYTheta: ' + str(ZYTheta * 180/math.pi))
                print(str(RotNodePos1))
                print(str(RotNodePos2))
            #print('Node ' + Node1['label'] + ': X: ' + Node1['x'] + ': Y: ' + Node1['y'] + ': Z: ' + Node1['z'])
            #print('Node ' + Node2['label'] + ': X: ' + Node2['x'] + ': Y: ' + Node2['y'] + ': Z: ' + Node2['z'])
            
            

def extractHeadings(file):
    data = file.read()
    pattern = r'\[(?!\.{0,2}END)[^\]]*\]'
    # this regex matches all strings inside brackets that dont have "END" at the begining
    matches = re.findall(pattern,data)
    headings = [match[1:-1] for match in matches]
    return headings


HEADINGS = ['UNITS', 'NODES','.MEMBERS_MAIN_DATA']
END = 'END'


def main():
    nodes = []
    members = []
    with open("2024 SB V4.5.r3d","r") as file:
        for line in file:
            for heading in HEADINGS:
                if heading in line and "END" not in line:
                    line = line.strip()
                    #print(f"heading, {heading}, found in line \"{line}\"")
                    len = int(line.split('<')[-1].strip('>'))
                    data = []
                    match heading:
                        case 'UNITS':
                            for i in range(len):
                                data.append(file.readline().strip())
                        case 'NODES':
                            for i in range(len):
                                data.append(file.readline().strip())
                            nodes = get_nodes(data)
                        case '.MEMBERS_MAIN_DATA':
                            for i in range(len):
                                data.append(file.readline())
                            members = get_members(data)


if __name__=="__main__":
    main()