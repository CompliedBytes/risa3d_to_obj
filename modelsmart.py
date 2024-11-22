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
    
    def get_coordinates(self) -> list[float]:
        return [self.x,self.y,self.z]

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
    rotation: float
    use_torsion_flag: bool
    fix_my1: bool
    fix_mz1: bool
    fix_my2: bool
    fix_mz2: bool
    memb_color_red: float 
    memb_color_green: float
    memb_color_blue: float
    views: list[str] = None
    radius: float = 0
    height: float = 0
    width: float = 0

    def __post_init__(self) -> None:
        self.views = ['3D']

    def __repr__(self):
        return (
            f"Member(memb_no={self.memb_no}, start_joint={self.start_joint}, end_joint={self.end_joint}, "
            f"effective_length_yy={self.effective_length_yy:.3f}, effective_length_zz={self.effective_length_zz:.3f}, "
            f"memb_length_zz_flag={self.memb_length_zz_flag!r}, memb_length_yy_flag={self.memb_length_yy_flag!r}, "
            f"offset_y={self.offset_y:.3f}, offset_z={self.offset_z:.3f}, shape_no={self.shape_no}, "
            f"material_no={self.material_no}, subtype={self.subtype}, rotation={self.rotation:.3f}, "
            f"use_torsion_flag={self.use_torsion_flag!r}, fix_my1={self.fix_my1!r}, fix_mz1={self.fix_mz1!r}, "
            f"fix_my2={self.fix_my2!r}, fix_mz2={self.fix_mz2!r}, memb_color_red={self.memb_color_red}, "
            f"memb_color_green={self.memb_color_green}, memb_color_blue={self.memb_color_blue})"
        )
    
    def get_i_coordinates(self,joints) -> list[float]:
        x = joints[self.start_joint-1].x
        y = joints[self.start_joint-1].y
        z = joints[self.start_joint-1].z
        return [x,y,z]
    
    def get_j_coordinates(self,joints) -> list[float]:
        x = joints[self.end_joint-1].x
        y = joints[self.end_joint-1].y
        z = joints[self.end_joint-1].z
        return [x,y,z]
    
    def set_views(self,joints: list[Joint], extreme_coords: tuple) -> None:
        ix, iy, iz = joints[self.start_joint-1].get_coordinates()
        jx, jy, jz = joints[self.end_joint-1].get_coordinates()

        if iy == extreme_coords[4] and jy == extreme_coords[4]:
            self.views.append('top')
        if iy == extreme_coords[1] and jy == extreme_coords[1]:
            self.views.append('bottom')
        if iz == extreme_coords[2] and jz == extreme_coords[2]:
            self.views.append('side1')
        if iz == extreme_coords[5] and jz == extreme_coords[5]:
            self.views.append('side2')

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
                  rotation=float(data[12]),
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


def set_member_dimensions(members: list[Member], shapes: dict[str, Shape]) -> None:
    for member in members:
        shape = shapes[member.shape_no-1]
        member.height = shape.height
        member.width = shape.width

def parse_file(file_name):
    joints = []
    members = []
    shapes = []
    with open(file_name,'r') as file:
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

    set_member_dimensions(members, shapes)

    print("modelsmart file parsed")
    return joints, members, shapes
        