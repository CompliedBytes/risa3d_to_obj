import math
import re
from dataclasses import dataclass
import numpy as np

from tkinter import ttk
from tkinter import *
from tkinter import filedialog

@dataclass
class Point:
    x: float
    y: float
    z: float

@dataclass
class Face:
    v1: Point
    v2: Point
    v3: Point


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
            self.width = float(dimensions[0])
            self.height = float(dimensions[1])
            self.thickness = float(dimensions[2])
    
    def get_i_coordinates(self,nodes):
        x = nodes[self.inode-1].x
        y = nodes[self.inode-1].y
        z = nodes[self.inode-1].z
        #print(f"x:{x} y:{y} z:{z}")
        return [x,y,z]
    
    def get_j_coordinates(self,nodes):
        x = nodes[self.jnode-1].x
        y = nodes[self.jnode-1].y
        z = nodes[self.jnode-1].z
        #print(f"x:{x} y:{y} z:{z}")
        return [x,y,z]

# Constants
BACKGROUND_COLOR = 'lightblue'
HEADINGS = ['UNITS', 'NODES','.MEMBERS_MAIN_DATA']
END = 'END'

def get_units(data):
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

def get_memberID_by_name(nodeLabel, memberList):
    for i in range(memberList.__len__()):
        member = memberList[i]
        if member.label == nodeLabel:
            idx = i
    return idx

def get_ortho_vectors(vector):
    i_norm = vector / np.linalg.norm(vector)   
    if np.allclose(i_norm, [1, 0, 0]) or np.allclose(i_norm, [-1, 0, 0]):
        temp_vector = np.array([0, 1, 0])  # Use y-axis if normal is x-axis
    else:
        temp_vector = np.array([1, 0, 0])
    v1 = np.cross(i_norm, temp_vector)
    v1 = v1 / np.linalg.norm(v1)
    v2 = np.cross(i_norm, v1)
    v2 = v2 / np.linalg.norm(v2)

    return v1,v2

def gen_rect_face_verticies(member, nodes):
    i = nodes[member.inode-1]
    j = nodes[member.jnode-1]

    dir = np.array([j.x - i.x, j.y - i.y, j.z - i.z])

    i_vec = np.array([i.x,i.y,i.z])
    j_vec = np.array([j.x,j.y,j.z])
    
    v1,v2 = get_ortho_vectors(dir)
    half_width_vec = member.width / 2*v1
    half_height_vec = member.height / 2*v2

    corners = []

    # Create the four corners of the face
    

    corners.append(i_vec + half_width_vec + half_height_vec)
    corners.append(i_vec - half_width_vec + half_height_vec)
    corners.append(i_vec - half_width_vec - half_height_vec)
    corners.append(i_vec + half_width_vec - half_height_vec) 

    corners.append(j_vec + half_width_vec + half_height_vec)
    corners.append(j_vec - half_width_vec + half_height_vec)
    corners.append(j_vec - half_width_vec - half_height_vec)
    corners.append(j_vec + half_width_vec - half_height_vec)

    faces = [
            [1, 2, 3, 4],  # Bottom face
            [5, 6, 7, 8],  # Top face
            [1, 2, 6, 5],  # Side face
            [2, 3, 7, 6],  # Side face
            [3, 4, 8, 7],  # Side face
            [4, 1, 5, 8]   # Side face
        ]

    return np.array(corners), faces

def gen_circ_face_verticies(member, nodes):
    i = nodes[member.inode-1]
    j = nodes[member.jnode-1]

    dir = np.array([j.x - i.x, j.y - i.y, j.z - i.z])

    i_vec = np.array([i.x,i.y,i.z])
    j_vec = np.array([j.x,j.y,j.z])
    
    v1, v2 = get_ortho_vectors(dir)
    half_width_vect = v1 * member.radius/2
    half_height_vect = v2 * member.radius/2
   
    circle_size = 16
    arc_range = int(circle_size/4)
    arc_deg = 2*np.pi/circle_size

    corners = []
    # Create the i-node vertices
    corners.append(i_vec)
    corners.append(i_vec + half_width_vect)
    for i in range(1, circle_size):
        corners.append(i_vec + np.cos(i*arc_deg)*half_width_vect + np.sin(i*arc_deg)*half_height_vect)
    # Create the j-node vertices
    corners.append(j_vec)
    corners.append(j_vec + half_width_vect)
    for i in range(1, circle_size):
        corners.append(j_vec + np.cos(i*arc_deg)*half_width_vect + np.sin(i*arc_deg)*half_height_vect)

    faces = []
    # Create the i-node meshes
    for i in range(2, circle_size+1):
        faces.append([1, i, i+1])
        if i == 16:
            faces.append([1, i+1, 2])
    # Create the j-node meshes
    for i in range(2+circle_size, 2*circle_size+2):
        faces.append([18, i, i+1])
        if i == 33:
            faces.append([18, i+1, 19])
    # Create the i->j meshes
    for i in range(2, circle_size+2):
        if i == circle_size+1:
            faces.append([i, 2, i+1+circle_size])
        else:
            faces.append([i, i+1, i+1+circle_size])
    # Create the j->i meshes
    for i in range(3+circle_size, 2*circle_size+3):
        if i == 2*circle_size + 2:
            faces.append([2, i, circle_size+3])
        else:
            faces.append([i-circle_size, i, i+1])

    return np.array(corners), faces

def print_prism_obj(verticies, faces):
    obj_file = open("output.obj", "w")


    for i, vertex in enumerate(verticies, start=1):
        obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

    for face in faces:
        obj_file.write(f"f {' '.join(map(str, face))}\n")

def on_select(file,file_label):
    selected_file = filedialog.askopenfilename()
    if selected_file:
        file.set(selected_file)
        file_label.config(text=selected_file)

def convert(file):
    nodes = []
    members = []
    with open(file.get()) as file:
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
    
    #idx=get_memberID_by_name("M90",members)

    all_verticies =[]
    all_faces = []
    vertex_count = 0

    for member in members:
        if(member.radius == 0):
            corners, faces = gen_rect_face_verticies(member,nodes)
            faces = [[vertex_count +idx for idx in face] for face in faces]
        else:
            corners, faces = gen_circ_face_verticies(member,nodes)
            faces = [[vertex_count +idx for idx in face] for face in faces]
        all_verticies.extend(corners)
        all_faces.extend(faces)
        vertex_count += corners.__len__()
        
    print_prism_obj(all_verticies, all_faces)
    print("file converted!")



def main():
    root = Tk()
    root.title("RISA-3D to OBJ Converter")
    style = ttk.Style(root)
    style.configure('UFrame', background=BACKGROUND_COLOR, foreground='black')
    style.configure('TFrame', background=BACKGROUND_COLOR, foreground='black')
    style.configure('TLabel', background=BACKGROUND_COLOR, foreground='black')
    style.configure('TCheckbutton', background=BACKGROUND_COLOR)

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text="UAA 3D File Conversion Tool", font=("Arial", 15)).grid(column=0, row = 0, padx=(25,25), pady=(5,10))

    file = StringVar()
    file_frame = ttk.Frame(mainframe)
    file_button = ttk.Button(file_frame, text="Select File", command=lambda: on_select(file,file_label))
    file_label = ttk.Label(file_frame, text="                                                         ", background="white", relief='sunken')
    file_button.grid(column=0, row=0, sticky = 'W')# side='left')
    file_label.grid(column=1, row=0, padx=(5,0), pady=(0,0))
    file_frame.grid(column=0, row=1, padx=(25,25), pady=(10,10))

    dimvar = StringVar()
    dim_frame = ttk.Frame(mainframe)
    dim_label = ttk.Label(dim_frame, text="2D/3D:", foreground="black").grid(column=0, row=0, padx=(0,5), pady=(0,0))
    dim_box = ttk.Combobox(dim_frame, textvariable=dimvar)
    # Add the values to the combobox
    dim_box['values'] = ('2D', '3D','Both')
    # Do not allow the user to edit the values
    dim_box.state(["readonly"])
    # Set the default value to Both
    dim_box.set('Both')
    # Place the combobox
    dim_box.grid(column=1, row=0, padx=(5,0), pady=(0,0))
    dim_frame.grid(column=0, row=2, padx=(0,0), pady=(10,10))


    side = IntVar()
    top = IntVar()
    bottom = IntVar()
    options_label = ttk.Label(mainframe, text="Advanced 2D Options", foreground="black").grid(column=0, row=3, padx=(0,0), pady=(10,0))
    options_frame = ttk.Frame(mainframe)
    side_button = ttk.Checkbutton(options_frame, text="Side", variable=side, onvalue=1, offvalue=0).grid(column=0, row=0, padx=(0,10))
    top_button = ttk.Checkbutton(options_frame, text="Top", variable=side, onvalue=1, offvalue=0).grid(column=1, row=0, padx=(10,10))
    bottom_button = ttk.Checkbutton(options_frame, text="Bottom", variable=side, onvalue=1, offvalue=0).grid(column=2, row=0, padx=(10,0))
    options_frame.grid(column=0, row=4, padx=(0,0), pady=(10,10))

    bottom_frame = ttk.Frame(mainframe)
    convert_button = ttk.Button(bottom_frame, text="Convert", command =lambda: convert(file)).grid(column=0, row=0, padx=(0,25), pady=(0,0))
    exit_button = ttk.Button(bottom_frame, text="Exit", command=root.destroy).grid(column=1, row=0, padx=(25,0), pady=(0,0))
    bottom_frame.grid(column=0, row=5, padx=(0,0), pady=(10,5))

    root.mainloop()


if __name__=="__main__":
    main()