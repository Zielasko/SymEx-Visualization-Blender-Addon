from enum import Enum
from visualization.Enums.riscv_enum import Opcode, Reg, Symbolic_Beh, Opcode_type

STORE_OPCODES = [Opcode.SB, Opcode.SH, Opcode.SW, Opcode.SC_W, Opcode.SC_D, Opcode.FSW]

class Analysis_Data:
    global_start = 0
    min_pc = 0xFFFFFF
    max_pc = 0

    num_runs = 0
    timeline_forks = [0]
    runs_start = [] #[run]
    runs_parent = [] #[run]
    potential_child_branches = [] #[run][potential child branches]
    memory_list = []
    memory_list_per_run = []

    discovered_run_links = []#[run_parent][(child,start_step)]



    def __init__(self, global_start, min_pc, max_pc, num_runs, timeline_forks, runs_start, 
                    runs_parent, potential_child_branches, memory_list, memory_list_per_run):
        self.global_start = global_start
        self.min_pc = min_pc
        self.max_pc = max_pc

        self.num_runs = num_runs
        self.timeline_forks = timeline_forks
        self.runs_start = runs_start
        self.runs_parent = runs_parent
        self.potential_child_branches = potential_child_branches
        self.memory_list = memory_list
        self.memory_list_per_run = memory_list_per_run

    def to_xml(self):
        xml_string = f'<Analysis global_start="{hex(self.global_start)}" min_pc="{hex(self.min_pc)}" '
        xml_string +=f'max_pc="{hex(self.max_pc)}" num_runs="{self.num_runs}" timeline_forks="{self.timeline_forks}">\n '
        xml_string += '<potential_children>'
        for run in range(self.num_runs):
            xml_string +=f'<run id="{run}" run_start="{hex(self.runs_start[run])}" run_parent="{self.runs_parent[run]}">\n'
            for potential_child in self.potential_child_branches[run]:
                xml_string +=f'     <potential_child branch="{hex(potential_child)}"></potential_child>\n'
            xml_string +=f'</run>\n'
        xml_string += '</potential_children>'

        xml_string += '<discovered_links>'
        dc_run_id = -1
        for run in self.discovered_run_links:
            dc_run_id+=1
            xml_string +=f'<run id="{dc_run_id}" >\n'
            for child,start_step in run:
                xml_string +=f'     <child id="{child}" step="{start_step}" ></child>\n'
            xml_string +='</run>\n'
        xml_string += '</discovered_links>'

        xml_string += '<memory>\n'
        i = 0
        for address in self.memory_list:
            i+=1
            xml_string +=f'  <address value="{address}"></address>'
            if(i%4==0):
                xml_string +="\n"
        xml_string += '</memory>\n'
        xml_string += '<memory_per_run>\n'
        for run_id, c_run in enumerate(self.memory_list_per_run):
            xml_string +=f'<run id="{run_id}">\n'
            for i, address in enumerate(c_run):
                i+=1
                xml_string +=f'  <address value="{address}"></address>'
                if(i%4==0):
                    xml_string +="\n"
            xml_string +='</run>\n'
        xml_string += '</memory_per_run>\n'

        xml_string += f'</Analysis>\n'

        return xml_string




class Run:
    run_id = -1
    start = -1
    end = -1
    num_steps = 0

    parent_id = -1
    start_step = 0
    start_pc = -1
    #children = [] #(run_id,step)

    """list of instructions in this run """
    intruction_list = [] #[id]=[Instruction]

    def __init__(self, run_id, start, end=-1, num_steps=0):
        self.run_id = run_id
        self.start = start
        self.end = end
        self.num_steps = num_steps

        #self.children = []
        self.intruction_list = []

    def set_parent(self, parent_id, start_step,start_pc):
        self.parent_id = parent_id
        self.start_step = start_step
        self.start_pc = start_pc

    #def add_child(self, child_id):
        #self.children.append(child_id)

    def to_xml(self):
        xml_string = f'<run id="{self.run_id}" start="{self.start}" '
        xml_string +=f'end="{self.end}" steps="{self.num_steps}" parent="{self.parent_id}" '
        xml_string +=f'start_step="{self.start_step}" start_pc="{self.start_pc}" >'

        for instruction in self.intruction_list:
            xml_string+=instruction.to_xml_p1() + instruction.to_xml_p2() + instruction.to_xml_p3()

        xml_string += "</run>"
        return xml_string

class Instruction:
    """ Basic Instruction
        Currently used by ECALL
    """
    pc = -1
    run_id = -1
    opcode = Opcode.ADD

    depth = 0

    steps_active = [] # (step, Symbolic_Beh)
    type = Opcode_type.none

    def __init__(self, pc, run_id, opcode, depth, type=Opcode_type.none):
        self.pc = pc
        self.run_id = run_id
        self.opcode = opcode
        self.depth = depth
        self.steps_active = []
        self.type=type

    def add_active_step(self, step, mode):
        if((step,mode) in self.steps_active):
            print("ERROR step was already added")
        self.steps_active.append((step,mode))

    def to_xml_p1(self):
        """ Base xml conversion function
            Should not be overridden
        """
        xml_string = f'<instruction pc="{hex(self.pc)}" '
        xml_string+= f'run_id="{self.run_id}" '
        xml_string+= f'opcode="{self.opcode.name}" '
        xml_string+= f'type="{self.type.name}" '
        xml_string+= f'depth="{self.depth}" '

        return xml_string

    def to_xml_p2(self):
        """ Instruction specific xml conversion function
            should be overridden to include instruction specific attributes
        """
        xml_string = ' >'
        return xml_string

    def to_xml_p3(self):
        """ Base xml conversion function
            Should not be overridden
            converts info for all active steps
        """
        xml_string = ""
        if(len(self.steps_active)>0):
            xml_string+="\n"
        for step in self.steps_active:
            xml_string+= '<step '
            xml_string+= f'id="{step[0]}" beh="{Symbolic_Beh(step[1]).name}" >'
            xml_string+= '</step>\n'
        xml_string += '</instruction>'
        return xml_string

class Arith_Instruction(Instruction):
    """ Basic Instruction with no direct influence on controlflow
        Class used by: 
            I:
                ADD
            M:
            A:    
    """

    reg_rs1 = Reg.none
    reg_rs2 = Reg.none
    reg_rd = Reg.none

    imm1 = None
    imm2 = None

    def __init__(self, pc, run_id, opcode, reg_rs1=Reg.none, reg_rs2=Reg.none, reg_rd=Reg.none, 
                    imm1=None, imm2=None, depth=0):
        super().__init__(pc, run_id, opcode,depth,type=Opcode_type.Arith)

        self.reg_rs1 = reg_rs1
        self.reg_rs2 = reg_rs2
        self.reg_rd = reg_rd

        self.imm1 = imm1
        self.imm2 = imm2

    def to_xml_p2(self):
        """ Instruction specific xml conversion function
        """
        xml_string = f'rs1="{self.reg_rs1.name}" '
        xml_string += f'rs2="{self.reg_rs2.name}" '
        xml_string += f'rd="{self.reg_rd.name}" '

        xml_string += f'imm1="{self.imm1}" '
        xml_string += f'imm2="{self.imm2}" '

        xml_string += ' >'
        return xml_string


class Jump(Instruction):
    target = -1
    link_reg = Reg.none
    link_address = -1

    def __init__(self, pc, run_id, opcode, target, link_reg, link_address,depth=0):
        super().__init__(pc, run_id, opcode,depth,type=Opcode_type.Jump)

        self.target = target
        self.link_reg = link_reg
        self.link_address = link_address
    
    def to_xml_p2(self):
        """ Instruction specific xml conversion function
        """
        xml_string = f'target="{self.target}" '
        xml_string += f'link="{self.link_reg.name}" '
        xml_string += f'link_address="{self.link_address}" '

        xml_string += ' >'
        return xml_string

class Branch(Instruction):
    target = -1
    reg_rs1 = Reg.none
    reg_rs2 = Reg.none

    condition = False

    def __init__(self, pc, run_id, opcode, target, reg_rs1, reg_rs2, condition,depth=0):
        super().__init__(pc, run_id, opcode,depth,type=Opcode_type.Branch)

        self.target = target
        self.reg_rs1 = reg_rs1
        self.reg_rs2 = reg_rs2
        self.condition = condition

    def add_active_step(self, step, mode, edge):
        if((step,mode,edge) in self.steps_active):
            print("ERROR step was already added")
        self.steps_active.append((step,mode,edge))

    def to_xml_p2(self):
        """ Instruction specific xml conversion function
        """
        xml_string = f'target="{self.target}" '
        xml_string += f'rs1="{self.reg_rs1.name}" '
        xml_string += f'rs2="{self.reg_rs2.name}" '
        xml_string += f'condition="{self.condition}" '

        xml_string += ' >'
        return xml_string

    def to_xml_p3(self):
        xml_string = ""
        if(len(self.steps_active)>0):
            xml_string+="\n"
        for step in self.steps_active:
            xml_string+= '<step '
            xml_string+= f'id="{step[0]}" beh="{Symbolic_Beh(step[1]).name}" edge="{step[2]}" >'
            xml_string+= '</step>\n'
        xml_string += '</instruction>'
        return xml_string

class LoadStore(Instruction):
    target = -1
    reg_rs1 = Reg.none
    imm1 = None
    reg_rs2d = Reg.none

    def __init__(self, pc, run_id, opcode, target, reg_rs1, imm1, reg_rs2d, depth=0):
        m_type = Opcode_type.Load
        if(opcode in STORE_OPCODES):
            m_type = Opcode_type.Store

        super().__init__(pc, run_id, opcode,depth,type=m_type)

        self.target = target
        self.reg_rs1 = reg_rs1
        self.imm1 = imm1
        self.reg_rs2d = reg_rs2d

    def to_xml_p2(self):
        """ Instruction specific xml conversion function
        """
        xml_string = f'target="{hex(self.target)}" '
        xml_string += f'rs1="{self.reg_rs1.name}" '
        xml_string += f'imm1="{self.imm1}" '
        xml_string += f'rs2d="{self.reg_rs2d.name}" '

        xml_string += ' >'
        return xml_string

class CSR(Instruction):
    flags = -1

    def __init__(self, pc, run_id, opcode, flags,depth=0):
        super().__init__(pc, run_id, opcode,depth,type=Opcode_type.CSR)

        self.flags = flags