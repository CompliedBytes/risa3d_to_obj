from dataclasses import dataclass
import logging


HEADINGS = ['UNITS', 'NODES','.MEMBERS_MAIN_DATA','SHAPES_LIST']
END = 'END'

@dataclass
class Node:
    label: str
    x: float
    y: float
    z: float
    
    def get_coordinates(self) -> list[float]:
        return [self.x, self.y, self.z]


@dataclass
class Shape:
    name: str
    height: float
    thickness: float
    width: float
    radius: float = 0

    def get_coordinates(self) -> list[float]:
        return [self.x, self.y, self.z]
    
def clean_dimension_input(dimension):
    return ''.join(char for char in dimension if char.isdigit() or char == '.' or char == '-')

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

    def __post_init__(self) -> None:
        dimensions = self.shape_label.upper().split('X')
        if len(dimensions) == 2:
            self.radius = float(clean_dimension_input(dimensions[0]))
        elif len(dimensions) == 3:
            self.height = float(clean_dimension_input(dimensions[0]))
            self.width = float(clean_dimension_input(dimensions[1]))
            self.thickness = float(clean_dimension_input(dimensions[2]))
        else:
            logging.warning(f"Dimesions not found for member: {self.label}, shape: {self.shape_label}")
    
    def get_i_coordinates(self,nodes) -> list[float]:
        x,y,z = nodes[self.inode-1].get_coordinates()
        return [x,y,z]
    
    def get_j_coordinates(self,nodes) -> list[float]:
        x,y,z = nodes[self.jnode-1].get_coordinates()
        return [x,y,z]
    
    def set_views(self,nodes: list[Node], extreme_coords: tuple) -> None:
        ix, iy, iz = nodes[self.inode-1].get_coordinates()
        jx, jy, jz = nodes[self.jnode-1].get_coordinates()

        if ix == extreme_coords[0] and jx == extreme_coords[0]:
            self.views.append('YZ_1')
        if ix == extreme_coords[3] and jx == extreme_coords[3]:
            self.views.append('YZ_2')
        if iy == extreme_coords[1] and jy == extreme_coords[1]:
            self.views.append('XZ_1')
        if iy == extreme_coords[4] and jy == extreme_coords[4]:
            self.views.append('XZ_2')
        if iz == extreme_coords[2] and jz == extreme_coords[2]:
            self.views.append('XY_1')
        if iz == extreme_coords[5] and jz == extreme_coords[5]:
            self.views.append('XY_2')

# Constants
BACKGROUND_COLOR = 'lightblue'
HEADINGS = ['UNITS', 'NODES','.MEMBERS_MAIN_DATA','SHAPES_LIST']
END = 'END'

def get_units(data) -> dict[str, str]:
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

# This function is used to get the nodes from the risa file
def get_nodes(data) -> list[Node]:
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
def get_members(data: list[str]) -> list[Member]:
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

def get_shapes_list(data: list[str]) -> dict[str, Shape]:
    shapes = {}
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
        shapes[shape_name] = shape

    return shapes

def set_member_dimensions(members: list[Member], shapes: dict[str, Shape]) -> None:
    for member in members:
        if member.shape_label in shapes:
            shape: Shape = shapes[member.shape_label]
            member.height = shape.height
            member.width = shape.width
            member.thickness = shape.thickness
            member.radius = shape.radius
        else:
            logging.error(f"Shape not found: {member.shape_label}")


def parse_file(filename):
    nodes = []
    members = []
    shapes = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                for heading in HEADINGS:
                    if heading in line and "END" not in line:
                        line = line.strip()
                        num_entries = int(line.split('<')[-1].strip('>'))
                        data = []
                        match heading:
                            case 'UNITS':
                                for i in range(num_entries):
                                    data.append(file.readline().strip())
                                units = get_units(data)
                            case 'NODES':
                                for i in range(num_entries):
                                    data.append(file.readline().strip())
                                nodes = get_nodes(data)
                            case '.MEMBERS_MAIN_DATA':
                                for i in range(num_entries):
                                    data.append(file.readline())
                                members = get_members(data)
                            case 'SHAPES_LIST':
                                for i in range(num_entries):
                                    data.append(file.readline())
                                shapes = get_shapes_list(data)
    except FileNotFoundError:
        logging.error("File not found")
        return
    except PermissionError:
        logging.error("Permission denied, could not read file")
        return
    except Exception as e:
        logging.error("An unknown error occurred")
        return
    
    set_member_dimensions(members, shapes)

    logging.info("RISA file parsed")
    return nodes, members
