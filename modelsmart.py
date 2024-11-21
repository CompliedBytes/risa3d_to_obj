from dataclasses import dataclass

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
        return f"File Version: {self.file_version}\nNumber of Shapes: {self.num_shapes}\nNumber of Materials: {self.num_materials}\nNumber of Joints: {self.num_joints}\nNumber of Members: {self.num_members}\nMetric Flag: {self.metric_flag}"

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

file = "Test-truss.3dd"

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
    
    joints = []
    for i in range(model_file.num_joints):
        joint = process_joint(file.readline().strip())
        joints.append(joint)

    shape_data = []
    for i in range(model_file.num_shapes):
        shape_data.append(file.readline().strip())

    member_data = []
    for i in range(model_file.num_members):
        member_data.append(file.readline().strip())

    


    print(joints)



    print(model_file)

