from dataclasses import dataclass
import numpy as np

from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from tktooltip import ToolTip


def clean_dimension_input(dimension):
    return ''.join(char for char in dimension if char.isdigit() or char == '.' or char == '-')

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
class Shape:
    name: str
    height: float
    thickness: float
    width: float
    radius: float = 0

@dataclass
class Member:
    label: str
    design_list: str
    shape_label: str
    views: str
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
        dimensions = self.shape_label.upper().split('X')
        if len(dimensions) == 2:
            self.radius = float(clean_dimension_input(dimensions[0]))
        elif len(dimensions) == 3:
            self.height = float(clean_dimension_input(dimensions[0]))
            self.width = float(clean_dimension_input(dimensions[1]))
            self.thickness = float(clean_dimension_input(dimensions[2]))
        else:
            print(f"ERR: {self.label} | {self.shape_label} | {self.material} | Dim len: {len(dimensions)}")
    
    def get_i_coordinates(self,nodes):
        x = nodes[self.inode-1].x
        y = nodes[self.inode-1].y
        z = nodes[self.inode-1].z
        return [x,y,z]
    
    def get_j_coordinates(self,nodes):
        x = nodes[self.jnode-1].x
        y = nodes[self.jnode-1].y
        z = nodes[self.jnode-1].z
        return [x,y,z]

# Constants
BACKGROUND_COLOR = 'lightblue'
HEADINGS = ['UNITS', 'NODES','.MEMBERS_MAIN_DATA','SHAPES_LIST']
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
        views = ['3D']

        member = Member(label, design_list, shape_label, views, inode, jnode, knode, rotation, offset, material)
        members.append(member)
    return members

def get_shapes_list(data):
    shapes = []
    for line in data:
        line = line[1:-2].strip().split('"')
        shape_name = line[0].strip()
        shape_properties = line[1].strip().split()
        if float(shape_properties[6]) != float(0):
            shape = Shape(shape_name, 
                        float(shape_properties[4]), 
                        float(shape_properties[5]), 
                        float(shape_properties[6]))
        else:
            shape = Shape(shape_name, 
                        float(0), 
                        float(shape_properties[5]), 
                        float(shape_properties[6]),
                        float(shape_properties[4]))    
        shapes.append(shape)
    return shapes

def set_member_dimensions(members, shapes):
    for member in members:
        for shape in shapes:
            if member.shape_label == shape.name:
                member.width = shape.width
                member.height = shape.height
                member.thickness = shape.thickness
                member.radius = shape.radius

def get_extreme_coords(members, nodes):
    min_x = 10000
    min_y = 10000
    min_z = 10000
    max_x = 0
    max_y = 0
    max_z = 0

    for member in members:
        i_node = nodes[member.inode]
        j_node = nodes[member.jnode]

        if i_node.x <= min_x:
            min_x = i_node.x
        if j_node.x <= min_x:
            min_x = j_node.x
        if i_node.y <= min_y:
            min_y = i_node.y
        if j_node.y <= min_y:
            min_y = j_node.y
        if i_node.z <= min_z:
            min_z = i_node.z
        if j_node.z <= min_z:
            min_z = j_node.z
        
        if i_node.x >= max_x:
            max_x = i_node.x
        if j_node.x >= max_x:
            max_x = j_node.x
        if i_node.y >= max_y:
            max_y = i_node.y
        if j_node.y >= max_y:
            max_y = j_node.y
        if i_node.z >= max_z:
            max_z = i_node.z
        if j_node.z >= max_z:
            max_z = j_node.z
        
        return min_x, min_y, min_z, max_x, max_y, max_z


def get_views(members, nodes):
    ext_coords = get_extreme_coords(members, nodes)
    for member in members:
        i_node = nodes[member.inode-1]
        j_node = nodes[member.jnode-1]
        dir_vec = np.array([j_node.x - i_node.x, j_node.y - i_node.y, j_node.z - i_node.z])

        # if abs(dir_vec[0]) % 90 == 0:
        #     member.views.append('top')
        if i_node.y == ext_coords[4] and j_node.y == ext_coords[4]:
            member.views.append('top')
        if i_node.y == ext_coords[1] and j_node.y == ext_coords[1]:
            member.views.append('bottom')
        if i_node.z == ext_coords[2] and j_node.z == ext_coords[2]:
            member.views.append('side1')
        if i_node.z == ext_coords[5] and j_node.z == ext_coords[5]:
            member.views.append('side2')

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
def compute_and_set_angles(members, nodes):
    for member in members:
        # Creates a vector from the i and j nodes of the member
        i_node = nodes[member.inode-1]
        j_node = nodes[member.jnode-1]
        member_vect = np.array([[j_node.x - i_node.x],[j_node.y - i_node.y],[j_node.z - i_node.z]])
        
        yz_normal = np.array([1,0,0])
        xz_normal = np.array([0,1,0])
        xy_normal = np.array([0,0,1])

        #The .item() here is used to convert from numpy flot to python flot
        member.theta_yz = get_plane_angle(member_vect, yz_normal).item()
        member.theta_xz = get_plane_angle(member_vect, xz_normal).item()
        member.theta_xy = get_plane_angle(member_vect, xy_normal).item()

def get_memberID_by_name(nodeLabel, memberList):
    for idx in range(memberList.__len__()):
        member = memberList[idx]
        if member.label == nodeLabel:
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

    return v1, v2

def gen_rect_face_vertices(member, nodes, options):
    i_node = nodes[member.inode-1]
    j_node = nodes[member.jnode-1]

    dir_vec = np.array([j_node.x - i_node.x, j_node.y - i_node.y, j_node.z - i_node.z])

    i_vec = np.array([i_node.x, i_node.y, i_node.z])
    j_vec = np.array([j_node.x, j_node.y, j_node.z])
    
    v1,v2 = get_ortho_vectors(dir_vec)
    half_width_vec = member.width / 2 * v1
    half_height_vec = member.height / 2 * v2

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

def gen_circ_face_vertices(member, nodes, options):
    i_node = nodes[member.inode-1]
    j_node = nodes[member.jnode-1]

    dir_vec = np.array([j_node.x - i_node.x, j_node.y - i_node.y, j_node.z - i_node.z])

    i_vec = np.array([i_node.x, i_node.y, i_node.z])
    j_vec = np.array([j_node.x, j_node.y, j_node.z])
    
    v1, v2 = get_ortho_vectors(dir_vec)
    half_width_vect = v1 * member.radius/2
    half_height_vect = v2 * member.radius/2
   
    circle_size = int(options["cyl"])
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
        if i == circle_size:
            faces.append([1, i+1, 2])
    # Create the j-node meshes
    for i in range(2+circle_size, 2*circle_size+2):
        faces.append([circle_size+2, i, i+1])
        if i == 2*circle_size+1:
            faces.append([circle_size+2, i+1, 19])
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

#def get_extreme_coords(members)



def print_prism_obj(verticies, faces, filename):
    obj_file = open(filename + ".obj", "w")

    for i, vertex in enumerate(verticies, start=1):
        obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

    for face in faces:
        obj_file.write(f"f {' '.join(map(str, face))}\n")

def gen_view(members, nodes, filename, view, options):
    all_vertices =[]
    all_faces = []
    vertex_count = 0

    for member in members:
        if view in member.views:
            if(member.radius == 0):
                corners, faces = gen_rect_face_vertices(member, nodes, options)
            else:
                corners, faces = gen_circ_face_vertices(member, nodes, options)

            faces = [[vertex_count +idx for idx in face] for face in faces]
            all_vertices.extend(corners)
            all_faces.extend(faces)
            vertex_count += corners.__len__()
    if len(all_vertices) == 0:
        return "no members found"
    print_prism_obj(np.round(all_vertices, decimals=int(options["prec"])), all_faces, filename + '_' + view)

def convert(filepath, dim_var, side, top, bottom, cyl_vert, coord_prec):
    options = {"D" : dim_var.get(), "cyl": cyl_vert.get(), "prec": coord_prec.get()}
    
    full_filename = filepath.get().split('/')[-1]
    if ".r3d" in full_filename:
        filename = full_filename.strip('.r3d')
        nodes = []
        members = []
        with open(filepath.get()) as file:
            for line in file:
                for heading in HEADINGS:
                    if heading in line and "END" not in line:
                        line = line.strip()
                        len = int(line.split('<')[-1].strip('>'))
                        data = []
                        match heading:
                            case 'UNITS':
                                for i in range(len):
                                    data.append(file.readline().strip())
                                units = get_units(data)
                            case 'NODES':
                                for i in range(len):
                                    data.append(file.readline().strip())
                                nodes = get_nodes(data)
                            case '.MEMBERS_MAIN_DATA':
                                for i in range(len):
                                    data.append(file.readline())
                                members = get_members(data)
                            case 'SHAPES_LIST':
                                for i in range(len):
                                    data.append(file.readline())
                                shapes = get_shapes_list(data)

        compute_and_set_angles(members, nodes)
        # Comment the line below out to keep the dimensions extracted from the SHAPE LABEL
        set_member_dimensions(members, shapes)
        get_views(members, nodes)
        
        if dim_var.get() == '3D':
            gen_view(members, nodes, filename, '3D', options)
        elif dim_var.get() == 'Both':
            gen_view(members, nodes, filename, '3D', options)
            if side.get() == 1:
                gen_view(members, nodes, filename, 'side1', options)
                gen_view(members, nodes, filename, 'side2', options)
            if top.get() == 1:
                gen_view(members, nodes, filename, 'top' , options)
            if bottom.get() == 1:
                gen_view(members, nodes, filename, 'bottom', options)
        elif dim_var.get() == '2D':
            if side.get() == 1:
                gen_view(members, nodes, filename, 'side1', options)
                gen_view(members, nodes, filename, 'side2', options)
            if top.get() == 1:
                gen_view(members, nodes, filename, 'top' , options)
            if bottom.get() == 1:
                gen_view(members, nodes, filename, 'bottom', options)
        print("file converted!")

    elif ".3dd" in full_filename:
        filename = full_filename.strip('.3dd')
    else:
        # Invalid filetype,  give an error message here.
        print("Error: invalid file type")
        return

def on_select(file,file_label):
    selected_file = filedialog.askopenfilename(
        filetypes=[("RISA/Modelsmart Files", "*.3dd *.r3d"), ("All Files", "*.*")]
    )
    if selected_file:
        file.set(selected_file)
        file_label.config(text=selected_file)        

def main():
    # Advanced settings sub-page is in a callable function that is called when the user clicks on the "Advanced" button.
    def Advanced_Settings():
        advanced = Toplevel(root)
        advanced.grab_set()
        advanced.title("Advanced Settings")
        style = ttk.Style(advanced)
        style.configure('UFrame', background=BACKGROUND_COLOR, foreground='black')
        style.configure('TFrame', background=BACKGROUND_COLOR, foreground='black')
        style.configure('TLabel', background=BACKGROUND_COLOR, foreground='black')
        style.configure('TCheckbutton', background=BACKGROUND_COLOR)
        
        advframe = ttk.Frame(advanced, padding="3 3 12 12")
        advframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        ttk.Label(advframe, text="Advanced Settings", font=("Arial", 15)).grid(column=0, row = 0, padx=(25,25), pady=(5,10))

        # 2D View Options Section.
        dim_options_label = ttk.Label(advframe, text="Advanced 2D Options", foreground="black")
        dim_options_label.grid(column=0, row=1, padx=(0,0), pady=(10,0))
        ToolTip(dim_options_label, msg="Specify which 2D views you'd like generated.\nDefault is all of them.", delay=0.25)
        dim_options_frame = ttk.Frame(advframe)
        side_button = ttk.Checkbutton(dim_options_frame, text="Side", variable=side, onvalue=1, offvalue=0)
        top_button = ttk.Checkbutton(dim_options_frame, text="Top", variable=top, onvalue=1, offvalue=0)
        bottom_button = ttk.Checkbutton(dim_options_frame, text="Bottom", variable=bottom, onvalue=1, offvalue=0)
        side_button.grid(column=0, row=0, padx=(0,10))
        top_button.grid(column=1, row=0, padx=(10,10))
        bottom_button.grid(column=2, row=0, padx=(10,0))
        dim_options_frame.grid(column=0, row=2, padx=(0,0), pady=(10,10))

        # Cylinder Options Section.
        cyl_options_label = ttk.Label(advframe, text='Cylindrical Tube Detail', foreground="black")
        cyl_options_field = ttk.Entry(advframe, textvariable=cyl_vert, justify=LEFT)
        cyl_options_label.grid(column=0, row=3, padx=(10,0), pady=(10,0))
        cyl_options_field.grid(column=0, row=4, padx=(10,0), pady=(10,10))
        ToolTip(cyl_options_label, msg="Number of side faces for generated cylinders.\nThe more faces, the closer they will be to an actual cylinder.\n16 is recommended.", delay=0.25)

        # Coordinate Precision Section.
        prec_options_label = ttk.Label(advframe, text='Coordinate Precision', foreground="black")
        prec_options_field = ttk.Entry(advframe, textvariable=coord_prec, justify=LEFT)
        prec_options_label.grid(column=0, row=5, padx=(10,0), pady=(10,0))
        prec_options_field.grid(column=0, row=6, padx=(10,0), pady=(10,10))
        ToolTip(prec_options_label, msg="Number of decimal places to round to.\n3 (thousandths) is default.", delay=0.25)

        exit_button = ttk.Button(advframe, text="Exit", command=lambda: advanced.destroy())
        exit_button.grid(column=0, row=10, sticky=E)
        advanced.mainloop()
    

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

    file = StringVar()
    dim_var = StringVar(value='Both')
    side = IntVar(value=1)
    top = IntVar(value=1)
    bottom = IntVar(value=1)
    cyl_vert = StringVar(value="16")
    coord_prec = StringVar(value="3")

    ttk.Label(mainframe, text="UAA 3D File Conversion Tool", font=("Arial", 15)).grid(column=0, row=0, padx=(25,25), pady=(5,10))
    file_frame = ttk.Frame(mainframe)
    file_button = ttk.Button(file_frame, text="Select File", command=lambda: on_select(file,file_label))
    file_label = ttk.Label(file_frame, text="                                                         ", background="white", relief='sunken')
    file_button.grid(column=0, row=0, sticky = 'W')
    file_label.grid(column=1, row=0, padx=(5,0), pady=(0,0))
    file_frame.grid(column=0, row=1, padx=(25,25), pady=(10,10))

    
    dim_frame = ttk.Frame(mainframe)
    dim_label = ttk.Label(dim_frame, text="2D/3D:", foreground="black")
    dim_box = ttk.Combobox(dim_frame, textvariable=dim_var)   
    dim_box['values'] = ('2D', '3D','Both')
    dim_box.state(["readonly"])
    dim_box.set('Both')
    dim_label.grid(column=0, row=0, padx=(0,5), pady=(0,0))
    dim_box.grid(column=1, row=0, padx=(5,0), pady=(0,0))
    dim_frame.grid(column=0, row=2, padx=(0,0), pady=(10,10))


    bottom_frame = ttk.Frame(mainframe)
    advanced_button = ttk.Button(bottom_frame, text="Advanced", command = lambda: Advanced_Settings())
    convert_button = ttk.Button(bottom_frame, text="Convert", command =lambda: convert(file, dim_var, side, top, bottom, cyl_vert, coord_prec))
    exit_button = ttk.Button(bottom_frame, text="Exit", command=root.destroy)
    advanced_button.grid(column=0, row=0, padx=(0,20), pady=(0,0))
    convert_button.grid(column=1, row=0, padx=(20,20), pady=(0,0))
    exit_button.grid(column=2, row=0, padx=(20,0), pady=(0,0))
    bottom_frame.grid(column=0, row=5, padx=(10,0), pady=(10,5))

    root.mainloop()


if __name__=="__main__":
    main()