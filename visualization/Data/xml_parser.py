import xml.etree.ElementTree as ET

from enum import Enum

from visualization.Enums.riscv_enum import Opcode, Reg, Symbolic_Beh, Opcode_type
from visualization.Data.instructions import Analysis_Data, Run, Instruction, Arith_Instruction, Jump, Branch, LoadStore, CSR
from visualization.Data.blocks import CFBlock

from visualization.utils.utils import open_file, read_xml

def parse_ptrace_xml(root):
    """ Takes a runs xml root node as input and returns a list of Run objects
    """

    run_list = []

    for run in root[0]: #in runs
        run_id = int(run.attrib.get('id'))
        start = int(run.attrib.get('start'))
        end = int(run.attrib.get('end'))
        num_steps = int(run.attrib.get('steps'))

        parent_id = int(run.attrib.get('parent'))
        start_step = int(run.attrib.get('start_step'))
        start_pc = int(run.attrib.get('start_pc'))
        children = [] #TODO

        """list of instructions in this run """
        intruction_list = [] #[id]=[Instruction]

        for instruction in run:
            pc = int(instruction.attrib.get('pc'),16)
            run_id = int(instruction.attrib.get('run_id'))
            opcode = Opcode[instruction.attrib.get('opcode')]

            depth = int(instruction.attrib.get('depth'))

            type = Opcode_type[instruction.attrib.get('type')]

            current_instruction = None
            if(type==Opcode_type.ECALL):
                current_instruction = Instruction(pc, run_id, opcode, depth, type)
            elif(type==Opcode_type.Arith):
                reg_rs1 = Reg[instruction.attrib.get('rs1')]
                reg_rs2 = Reg[instruction.attrib.get('rs2')]
                reg_rd = Reg[instruction.attrib.get('rd')]

                imm1_s = instruction.attrib.get('imm1')
                imm2_s = instruction.attrib.get('imm2')

                imm1 = None
                imm2 = None

                if(imm1_s!="None"):
                    imm1 = int(instruction.attrib.get('imm1'))

                if(imm2_s!="None"):
                    imm2 = int(instruction.attrib.get('imm2'))

                current_instruction = Arith_Instruction(pc, run_id, opcode, reg_rs1, reg_rs2, reg_rd, 
                    imm1, imm2, depth)
            elif(type==Opcode_type.Jump):
                target = int(instruction.attrib.get('target'))
                link_reg = Reg[instruction.attrib.get('link')]
                link_address = int(instruction.attrib.get('link_address'))
                current_instruction = Jump(pc, run_id, opcode, target, link_reg, link_address,depth)
            elif(type==Opcode_type.Branch):
                target = int(instruction.attrib.get('target'))
                reg_rs1 = Reg[instruction.attrib.get('rs1')]
                reg_rs2 = Reg[instruction.attrib.get('rs2')]
                condition = instruction.attrib.get('condition')=="True"

                current_instruction = Branch(pc, run_id, opcode, target, reg_rs1, reg_rs2, condition,depth)
            elif(type==Opcode_type.Load or type==Opcode_type.Store):
                target = int(instruction.attrib.get('target')[2:],16)
                reg_rs1 = Reg[instruction.attrib.get('rs1')]

                imm1_s = instruction.attrib.get('imm1')
                imm1 = None
                if(imm1_s!="None"):
                    imm1 = int(instruction.attrib.get('imm1'))

                reg_rs2d = Reg[instruction.attrib.get('rs2d')]
                current_instruction = LoadStore(pc, run_id, opcode, target, reg_rs1, imm1, reg_rs2d, depth)
            elif(type==Opcode_type.CSR):
                current_instruction = CSR(pc, run_id, opcode, -1,depth)
            else:
                print(f"ERROR: unknown opcode type RUN {run_id} PC {hex(pc)}")
            

            if(type==Opcode_type.Branch):
                for step in instruction:
                    current_instruction.add_active_step(int(step.attrib.get('id')), Symbolic_Beh[step.attrib.get('beh')], int(step.attrib.get('edge')))
            else:
                for step in instruction:
                    current_instruction.add_active_step(int(step.attrib.get('id')), Symbolic_Beh[step.attrib.get('beh')])
            intruction_list.append(current_instruction)
        current_run = Run(run_id, start, end, num_steps)
        current_run.set_parent(parent_id, start_step,start_pc)
        current_run.intruction_list = intruction_list
        for child in children:
            current_run.add_child(child)
        run_list.append(current_run)
    return run_list

def parse_analysis_xml(root):
    """ Takes a runs xml root node as input and returns the analysis data
    """
    analysis = root[1] #Analysis

    global_start = int(analysis.attrib.get('global_start'),16)
    min_pc = int(analysis.attrib.get('min_pc'),16)
    max_pc = int(analysis.attrib.get('max_pc'),16)

    num_runs = int(analysis.attrib.get('num_runs'))
    timeline_forks = [0] #TODO

    runs_start = [] #[run]
    runs_parent = [] #[run]
    potential_child_branches = [] #[run][potential child branches]
    memory_list = [] #TODO

    discovered_links = []
    
    for run in analysis[0]:
        runs_start.append(int(run.attrib.get('run_start'),16))
        runs_parent.append(int(run.attrib.get('run_parent')))
        cr_potential_child_branches = [] #[potential child branches]
        for child in run:
            cr_potential_child_branches.append(int(child.attrib.get('branch'),16))
        potential_child_branches.append(cr_potential_child_branches)
    for run in analysis[1]:
        dc_run_list = []
        for child in run:
            child_id = int(child.attrib.get('id'))
            child_step_start = int(child.attrib.get('step'))
            dc_run_list.append((child_id, child_step_start))
        discovered_links.append(dc_run_list)

    memory_list = []
    for address in analysis[2]:
        memory_list.append(int(address.attrib.get('value')))
    memory_list_per_run = []
    #print("Parsing analysis memory list per run")
    for an_run in analysis[3]:
        memory_list_current_run = []
        for per_run_address in an_run:
            #print(f"per_run_address.tag {per_run_address.tag} {per_run_address.attrib.get('value')}")
            memory_list_current_run.append(int(per_run_address.attrib.get('value')))
        memory_list_per_run.append(memory_list_current_run)
    #print(f"mem list per run {memory_list_per_run}")

    analysis_data = Analysis_Data(global_start, min_pc, max_pc, num_runs, timeline_forks, runs_start, 
                    runs_parent, potential_child_branches, memory_list, memory_list_per_run)
    analysis_data.discovered_run_links = discovered_links
    return analysis_data


