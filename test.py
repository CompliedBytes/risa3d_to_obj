import math
import re
from dataclasses import dataclass
import numpy as np

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
    height: float = 0
    width: float = 0
    thickness: float = 0
    radius: float = 0
    theta_yz: float = 0
    theta_xz: float = 0
    theta_xy: float = 0

    def __post_init__(self):
        dimensions = self.shape_label.split('X')
        if len(dimensions) == 2:
            cleaned_value = ''.join(char for char in dimensions[0] if char.isdigit() or char == '.' or char == '-')
            self.radius = float(cleaned_value)
        else:
            self.height = float(dimensions[0])
            self.width = float(dimensions[1])

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
        inode = int(temp[0])
        jnode = int(temp[1])
        knode = int(temp[2])
        rotation = float(temp[3])
        offset = int(temp[4])
        material = int(temp[7])

        member = Member(label, design_list, shape_label, inode, jnode, knode, rotation, offset, material)
        members.append(member)
    return members

# This function takes in a vector and a plane normal
# Then it finds the angle the vector makes with that plane and returns it in degrees
def get_plane_angle(vector, normal):
    flat = vector.flatten()
    dot = np.dot(flat,normal)

    vect_mag = np.linalg.norm(flat)
    norm_mag = np.linalg.norm(normal)
    cos_theta = dot / (vect_mag*norm_mag)
    theta_rad = np.arccos(cos_theta)
    theta_plane = 90 - np.degrees(theta_rad)

    return theta_plane

# This function takes in a member and the set of nodes
# Then it will compute the angles made with each axis (yz,xz,xy)
# It will update the member object with the new angles found
def compute_and_set_angles(member, nodes):
    
    #print(member.label,nodes[member.inode-1],nodes[member.jnode-1])

    # Creates a vector from the i and j nodes of the member
    i = nodes[member.inode-1]
    j = nodes[member.jnode-1]
    member_vect = np.array([[j.x - i.x],[j.y - i.y],[j.z - i.z]])
    
    yz_normal = np.array([1,0,0])
    xz_normal = np.array([0,1,0])
    xy_normal = np.array([0,0,1])

    #The .item() here is used to convert from numpy flot to python flot
    member.theta_yz = get_plane_angle(member_vect, yz_normal).item()
    member.theta_xz = get_plane_angle(member_vect, xz_normal).item()
    member.theta_xy = get_plane_angle(member_vect, xy_normal).item()

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

    for member in members:
        compute_and_set_angles(member,nodes)
        print(member)


if __name__=="__main__":
    main()