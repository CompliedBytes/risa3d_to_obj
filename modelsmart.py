from dataclasses import dataclass
import numpy as np

class ModelSmartFile:
    def __init__(self,file_version: int,
                 num_shapes: int, 
                 num_materials: int,
                 num_joints: int, 
                 num_members: int,
                 metric_flag: bool) -> None:
        
        self.file_version =file_version
        self.num_shapes = num_shapes
        self.num_materials = num_materials
        self.num_joints = num_joints
        self.num_members = num_members
        self.metric_flag = metric_flag
    
    def __repr__(self) -> str:
        return (
            f"File Version: {self.file_version}, Metric Flag: {self.metric_flag} "
            f"Number of Shapes: {self.num_shapes}, "
            f"Number of Materials: {self.num_materials}, "
            f"Number of Joints: {self.num_joints}, "
            f"Number of Members: {self.num_members}"
        )

@dataclass
class Joint:
    num: int
    x: float
    y: float
    z: float
    trans_x: float
    trans_y: float
    trans_z: float
    rot_x: float
    rot_y: float
    rot_z: float
    joint_type: int
    sub_type: int

    def __repr__(self):
        return (
            f"Joint(num={self.num}, x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f}, "
            f"trans_x={self.trans_x:.3f}, trans_y={self.trans_y:.3f}, trans_z={self.trans_z:.3f}, "
            f"rot_x={self.rot_x:.3f}, rot_y={self.rot_y:.3f}, rot_z={self.rot_z:.3f}, "
            f"joint_type={self.joint_type!r}, sub_type={self.sub_type!r})"
        )

@dataclass
class Member:
    memb_no: int
    start_joint: int
    end_joint: int
    effective_length_yy: float
    effective_length_zz: float
    memb_length_zz_flag: int
    memb_length_yy_flag: int
    offset_y: float
    offset_z: float
    shape_no: int
    material_no: int
    subtype: int
    roll_angle: float
    use_torsion_flag: bool
    fix_my1: bool
    fix_mz1: bool
    fix_my2: bool
    fix_mz2: bool
    memb_color_red: float 
    memb_color_green: float
    memb_color_blue: float
    theta_yz: float = 0
    theta_xz: float = 0
    theta_xy: float = 0

    def __repr__(self):
        return (
            f"Member(memb_no={self.memb_no}, start_joint={self.start_joint}, end_joint={self.end_joint}, "
            f"effective_length_yy={self.effective_length_yy:.3f}, effective_length_zz={self.effective_length_zz:.3f}, "
            f"memb_length_zz_flag={self.memb_length_zz_flag!r}, memb_length_yy_flag={self.memb_length_yy_flag!r}, "
            f"offset_y={self.offset_y:.3f}, offset_z={self.offset_z:.3f}, shape_no={self.shape_no}, "
            f"material_no={self.material_no}, subtype={self.subtype}, roll_angle={self.roll_angle:.3f}, "
            f"use_torsion_flag={self.use_torsion_flag!r}, fix_my1={self.fix_my1!r}, fix_mz1={self.fix_mz1!r}, "
            f"fix_my2={self.fix_my2!r}, fix_mz2={self.fix_mz2!r}, memb_color_red={self.memb_color_red}, "
            f"memb_color_green={self.memb_color_green}, memb_color_blue={self.memb_color_blue})"
        )

@dataclass
class Shape:
    shape_number: int
    description: str
    si_flag: int
    round_flag: int
    height: float
    width: float
    area: float
    ix: float
    iy: float
    iz: float
    sy: float
    sz: float
    sep_distance: float

    def __repr__(self):
        return (
            f"Shape(shape_number={self.shape_number}, description={self.description}, si_flag={self.si_flag}, "
            f"round_flag={self.round_flag}, height={self.height:.3f}, width={self.width:.3f}, area={self.area:.3f}, "
            f"ix={self.ix:.3f}, iy={self.iy:.3f}, iz={self.iz:.3f}, sy={self.sy:.3f}, sz={self.sz:.3f}, "
            f"sep_distance={self.sep_distance:.3f})"
        )

def process_joint(joint_data: str) -> Joint:
    data = joint_data.strip().split(" ")
    return Joint(num=int(data[0]),
                 x=float(data[1]),
                 y=float(data[2]),
                 z=float(data[3]),
                 trans_x=int(data[4]),
                 trans_y=int(data[5]),
                 trans_z=int(data[6]),
                 rot_x=int(data[7]),
                 rot_y=int(data[8]),
                 rot_z=int(data[9]),
                 joint_type=int(data[10]),
                 sub_type=int(data[11]))

def process_member(member_data: str) -> Member:
    data = member_data.strip().split(" ")
    return Member(memb_no=int(data[0]),
                  start_joint=int(data[1]),
                  end_joint=int(data[2]),
                  effective_length_yy=float(data[3]),
                  effective_length_zz=float(data[4]),
                  memb_length_zz_flag=int(data[5]),
                  memb_length_yy_flag=int(data[6]),
                  offset_y=float(data[7]),
                  offset_z=float(data[8]),
                  shape_no=int(data[9]),
                  material_no=int(data[10]),
                  subtype=int(data[11]),
                  roll_angle=float(data[12]),
                  use_torsion_flag=bool(data[13]),
                  fix_my1=bool(data[14]),
                  fix_mz1=bool(data[15]),
                  fix_my2=bool(data[16]),
                  fix_mz2=bool(data[17]),
                  memb_color_red=float(data[18]),
                  memb_color_green=float(data[19]),
                  memb_color_blue=float(data[20]))

def process_shape(shape_data: list[str]) -> Shape:
        data1 = shape_data[2].strip().split(" ")
        data2 = shape_data[3].strip().split(" ")
        return Shape(int(shape_data[0]),
                     shape_data[1],
                     int(data1[0]),
                     int(data1[1]),
                     float(data1[2]),
                     float(data1[3]),
                     float(data1[4]),
                     float(data2[0]),
                     float(data2[1]),
                     float(data2[2]),
                     float(data2[3]),
                     float(data2[4]),
                     float(data2[5]))

file = "Test-truss.3dd"
joints = []
members = []
shapes = []
with open(file,'r') as file:
    file_type=file.readline().strip()
    file_version=file.readline().strip()
    data = file.readline().strip()
    data = data.strip().split(" ")
    model_file = ModelSmartFile(file_version,
                                int(data[0]),
                                int(data[1]),
                                int(data[2]),
                                int(data[3]),
                                int(data[4]))
    
    for i in range(model_file.num_joints):
        joint = process_joint(file.readline().strip())
        joints.append(joint)

    for i in range(model_file.num_members):
        member = process_member(file.readline().strip())
        members.append(member)

    #this data is unused skips joint load data
    for i in range(model_file.num_joints):
        file.readline()

    for i in range(model_file.num_shapes):
        shape_data = []
        shape_data.append(file.readline().strip())
        shape_data.append(file.readline().strip())
        shape_data.append(file.readline().strip())
        shape_data.append(file.readline().strip())
        shape = process_shape(shape_data)
        shapes.append(shape)

#exact same as r3d
def get_plane_angle(vector: np.array, normal: np.array) -> float:
    #check vector and normal are the right size

    flat = vector.flatten()
    dot = np.dot(flat,normal)

    vect_mag = np.linalg.norm(flat)
    norm_mag = np.linalg.norm(normal)

    if vect_mag == 0 or norm_mag == 0:
        print("Vector or Normal is of zero length")
    cos_theta = dot / (vect_mag*norm_mag)

    theta_rad = np.arccos(cos_theta)
    theta_plane = 90 - np.degrees(theta_rad)

    return theta_plane

#almost exact same as r3d
def compute_and_set_angles(members: list[Member], joints: list[Joint]) -> None:
    for member in members:
        # Creates a vector from the i and j nodes of the member
        start_joint = joints[member.start_joint-1]
        end_joint = joints[member.end_joint-1]
        member_vect = np.array([[end_joint.x - start_joint.x],[end_joint.y - start_joint.y],[end_joint.z - start_joint.z]])
        
        yz_normal = np.array([1,0,0])
        xz_normal = np.array([0,1,0])
        xy_normal = np.array([0,0,1])

        #The .item() here is used to convert from numpy flot to python flot
        member.theta_yz = get_plane_angle(member_vect, yz_normal).item()
        member.theta_xz = get_plane_angle(member_vect, xz_normal).item()
        member.theta_xy = get_plane_angle(member_vect, xy_normal).item()

#exact same as r3d
def get_ortho_vectors(vector: np.array) -> tuple[np.array, np.array]:
    #Check that array is the right size

    norm = np.linalg.norm(vector)
    if norm == 0:
        print("Vector is of zero length")

    i_norm = vector / norm
    
    if np.allclose(i_norm, [1, 0, 0]) or np.allclose(i_norm, [-1, 0, 0]):
        temp_vector = np.array([0, 1, 0])  # Use y-axis if aligned with x-axis
    elif np.allclose(i_norm, [0, 1, 0]) or np.allclose(i_norm, [0, -1, 0]):
        temp_vector = np.array([0, 0, 1])  # Use z-axis if aligned with y-axis
    else:
        temp_vector = np.array([1, 0, 0])  # Default to x-axis otherwise

    v1 = np.cross(i_norm, temp_vector)
    v1 = v1 / np.linalg.norm(v1)
    v2 = np.cross(i_norm, v1)
    v2 = v2 / np.linalg.norm(v2)

    return v1, v2

#almost exact same as r3d
def gen_rect_face_vertices(member: list[Member], joints: list[Joint],shapes: list[Shape]) -> tuple[np.array, list[list[int]]]:
    start_joint = joints[member.start_joint-1]
    end_joint = joints[member.end_joint-1]

    dir_vec = np.array([end_joint.x - start_joint.x, end_joint.y - start_joint.y, end_joint.z - start_joint.z])

    start_vec = np.array([start_joint.x, start_joint.y, start_joint.z])
    end_vec = np.array([end_joint.x, end_joint.y, end_joint.z])
    
    v1,v2 = get_ortho_vectors(dir_vec)
    half_width_vec = shapes[member.shape_no-1].width / 2 * v1
    half_height_vec = shapes[member.shape_no-1].width / 2 * v2

    corners = []

    # Create the four corners of the face
    corners.append(start_vec + half_width_vec + half_height_vec)
    corners.append(start_vec - half_width_vec + half_height_vec)
    corners.append(start_vec - half_width_vec - half_height_vec)
    corners.append(start_vec + half_width_vec - half_height_vec) 

    corners.append(end_vec + half_width_vec + half_height_vec)
    corners.append(end_vec - half_width_vec + half_height_vec)
    corners.append(end_vec - half_width_vec - half_height_vec)
    corners.append(end_vec + half_width_vec - half_height_vec)

    faces = [
            [1, 2, 3, 4],  # Bottom face
            [5, 6, 7, 8],  # Top face
            [1, 2, 6, 5],  # Side face
            [2, 3, 7, 6],  # Side face
            [3, 4, 8, 7],  # Side face
            [4, 1, 5, 8]   # Side face
        ]

    return np.array(corners), faces

def print_prism_obj(verticies, faces):
    obj_file = open("output.obj", "w")

    for i, vertex in enumerate(verticies, start=1):
        obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

    for face in faces:
        obj_file.write(f"f {' '.join(map(str, face))}\n")
    obj_file.close()

compute_and_set_angles(members, joints)


all_verticies =[]
all_faces = []
vertex_count = 0

for member in members:
    corners, faces = gen_rect_face_vertices(member,joints,shapes)
    faces = [[vertex_count +idx for idx in face] for face in faces]
    all_verticies.extend(corners)
    all_faces.extend(faces)
    vertex_count += corners.__len__()

print_prism_obj(all_verticies, all_faces)
print("file converted!")