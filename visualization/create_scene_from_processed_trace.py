#from process_trace import process_trace
from os import read
import bpy

import random
import math
import xml.etree.ElementTree as ET

from enum import Enum

from datetime import datetime, timedelta

from visualization.Enums.riscv_enum import Opcode, Reg, Symbolic_Beh, Opcode_type
from visualization.Data.instructions import Analysis_Data, Run, Instruction, Arith_Instruction, Jump, Branch, LoadStore, CSR
from visualization.Data.blocks import CFBlock
from visualization.Data.xml_parser import parse_ptrace_xml, parse_analysis_xml

from visualization.utils.utils import open_file, read_xml
import visualization.Blender.blender_utils as bu 
import visualization.Blender.data_blocks as bd
import visualization.Blender.config as cfg

## -- CF analysis and processing -- ##

def create_control_flow_blocks(blocks_xml_root, code_string, global_start):
    print("[Creating Control Flow Blocks]")
    cf_blocks_root = blocks_xml_root[0]
    functions_root = blocks_xml_root[1]

    run_id = 0
    for run in cf_blocks_root:
        for block in run:
            block_start = int(block.attrib.get('block_start'))
            block_end = int(block.attrib.get('block_end'))
            file_name = block.attrib.get('file_name')
            line_start = int(block.attrib.get('line_start'))
            line_end = int(block.attrib.get('line_end'))
            function_name = block.attrib.get('function_name')
            code = ""

            current_block = CFBlock(block_start, block_end, file_name, line_start, line_end, function_name, code)
            bd.create_block(current_block, run_id+1, global_start)
            location_t = ((block_start - global_start)*cfg.INSTRUCTION_DISTANCE+cfg.INSTRUCTION_DISTANCE, run_id*cfg.RUN_DISTANCE-cfg.CUBE_SIZE, cfg.BLOCK_Z+cfg.CUBE_SIZE)
            name_t = f"cf_code_{hex(block_start)}_{hex(block_end)}_{run_id}"
            text = f"{function_name}"
            text_obj = bu.create_text(location_t, name_t, text, 2, "mat_text")

        run_id +=1

    #create function blocks
    for function in functions_root:
        function_name = function.attrib.get('name')
        function_start = int(function.attrib.get('start'))
        function_end = int(function.attrib.get('end'))

        bd.create_function(function_name, function_start, function_end, global_start)
    #read labels and create annotations
    print("-----------------------------------------------------------------------------------")




def create_scene_from_processed_trace(runs, analysis_data):

    global_start = analysis_data.global_start
    min_pc = analysis_data.min_pc
    max_pc = analysis_data.max_pc

    num_runs = analysis_data.num_runs
    timeline_forks = analysis_data.timeline_forks
    runs_start = analysis_data.runs_start
    runs_parent = analysis_data.runs_parent
    potential_child_branches = analysis_data.potential_child_branches
    memory_list = analysis_data.memory_list
    memory_list_per_run = analysis_data.memory_list_per_run

    discovered_links = analysis_data.discovered_run_links


    objects = bpy.data.objects

    bu.init_scene()
    bu.create_materials()

    run_count = 0

    time_create_start = datetime.now()
    time_average_run_duration = timedelta(seconds=0)
    time_average_object_creation = timedelta(seconds=0)
    print("-----------------------------------------------------------------------------------")
    print(f'[Building scene from processed trace] ({time_create_start.strftime("%H:%M:%S")}):')
    print("-----------------------------------------------------------------------------------")

    for run in runs:
        run_count +=1

        time_run_start = datetime.now()

        run_id = run.run_id
        start = run.start
        end = run.end
        num_steps = run.num_steps

        parent_id = run.parent_id
        start_step = run.start_step
        start_pc = run.start_pc
        #children = run.children

        print(f"RUN[{run.run_id}] start:{run.start} parent_id:{run.parent_id} start_step:{run.start_step} start_pc:{run.start_pc}")

        #branch_start = runs_start[run-1]

        cam = bd.create_camera(run_id)

        active_marker = bd.create_active_marker(f"marker_{run_id}", run_id)

        location_t = (0, run_id*cfg.RUN_DISTANCE, 4)
        name_t = f"text_run_of_parent {parent_id}"
        text_t = f"parent {parent_id}"
        parent_text_obj = bu.create_text(location_t, name_t, text_t, 4, "mat_text")

        if(parent_id!=-1):
            #create run_start marker
            run_actual_start = run.intruction_list[0].pc
            run_start_location = ((run_actual_start-global_start)*cfg.INSTRUCTION_DISTANCE, run_id*cfg.RUN_DISTANCE, run.intruction_list[0].depth*cfg.DEPTH_MULT)
            bpy.ops.mesh.primitive_cube_add(size=cfg.BASE_SIZE, enter_editmode=False, align='WORLD', 
                                    location=run_start_location, scale=(1, 1, 1))
            cube = bpy.context.selected_objects[0]
            cube.name = "run start"
            bu.assign_material(cube,"mat_start")
            bpy.ops.transform.resize(value=(cfg.CUBE_SIZE*2, cfg.CUBE_SIZE*2, cfg.CUBE_SIZE*8), 
                                        orient_type='GLOBAL', 
                                        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                                        orient_matrix_type='GLOBAL', 
                                        constraint_axis=(True, False, False), mirror=True, 
                                        use_proportional_edit=False, proportional_edit_falloff='SMOOTH', 
                                        proportional_size=1, use_proportional_connected=False, 
                                        use_proportional_projected=False)
        
        for instruction in run.intruction_list:
            pc = instruction.pc
            run_id = instruction.run_id
            opcode = instruction.opcode

            depth = instruction.depth

            steps_active = instruction.steps_active
            type = instruction.type

            current_location = ((pc-global_start)*cfg.INSTRUCTION_DISTANCE, run_id*cfg.RUN_DISTANCE, depth*cfg.DEPTH_MULT)
            obj = bpy.context.selected_objects[0] #declare for this scope
            new_obj_name = f"{pc} {run_id} {depth} {opcode.name}" #{step} 

            curve_obj = None #used by some types of instructions (Branch, Jump)


            #create block   
            if(type == Opcode_type.none):
                obj = bd.create_instruction(new_obj_name, current_location)
            elif(type == Opcode_type.Arith):
                obj = bd.create_instruction(new_obj_name, current_location)
                #nothing more to do for arith as all default values are 0
            elif(type == Opcode_type.ECALL):
                obj = bd.create_ecall(new_obj_name,current_location)
            elif(type == Opcode_type.Jump):
                jump_target = instruction.target
                link_reg = instruction.link_reg
                link_address = instruction.link_address

                obj, curve_obj = bd.create_jump(new_obj_name, current_location, jump_target, pc, depth, global_start)
                    
                bu.set_keyframe(curve_obj, curve_obj.color,"color",0,0,0)
                bu.set_keyframe(curve_obj, curve_obj.color,"color",1,0,0)
                bu.set_keyframe(curve_obj, curve_obj.color,"color",2,0,0)
            elif(type == Opcode_type.Branch):
                jump_target = instruction.target
                branch_edge =  instruction.condition
                reg_rs1 =  instruction.reg_rs1
                reg_rs2 =  instruction.reg_rs2

                obj, curve_obj = bd.create_branch(new_obj_name, current_location, jump_target, pc, depth, branch_edge, global_start)
                if(branch_edge): # or curve_obj!=None
                    bu.set_keyframe(curve_obj, curve_obj.color, "color", ind=0, frame_p=0, value=0)
                    bu.set_keyframe(curve_obj, curve_obj.color, "color", ind=1, frame_p=0, value=0)
                    bu.set_keyframe(curve_obj, curve_obj.color, "color", ind=2, frame_p=0, value=0)
            elif(type == Opcode_type.Load):
                obj = bd.create_load(new_obj_name, current_location)
            elif(type == Opcode_type.Store):
                obj = bd.create_store(new_obj_name, current_location)
            elif(type == Opcode_type.CSR):
                pass
            else:
                print("ERROR: Unknown opcode")

            #set keyframes for active steps
            if(type==Opcode_type.Branch):
                #set default value for frame 0
                #set initial branch taken color to unknown (0.5)
                bu.set_keyframe(obj, obj.color, "color", ind=0, frame_p=0, value=0)
                bu.set_keyframe(obj, obj.color, "color", ind=1, frame_p=0, value=0)
                bu.set_keyframe(obj, obj.color, "color", ind=2, frame_p=0, value=0.5)
                for step, sym_beh, edge in instruction.steps_active:
                    #preserve old value
                    bu.keyframe_preserve(obj,"color",0,step, offset=1)
                    bu.keyframe_preserve(obj,"color",2,step, offset=1)

                    #set active for one step
                    bu.set_keyframe_for_duration(obj,obj.color,"color",0,step,step+1,1,0)
                    bu.set_keyframe(obj,obj.color,"color",2,step, int(edge))
                    if(curve_obj!=None):
                        #make fully opaque when active (red), stay slightly visible afterwards
                        bu.set_keyframe_for_duration(curve_obj,curve_obj.color,"color",0,step,step+1,1,0)
                        bu.set_keyframe_for_duration(curve_obj,curve_obj.color,"color",1,step,step+3,1,0.1)
            elif(type == Opcode_type.Jump):
                #set frame 0
                bu.set_keyframe(obj, obj.color,"color",0,0,0)
                bu.set_keyframe(obj, obj.color,"color",1,0,0)
                bu.set_keyframe(obj, obj.color,"color",2,0,0)
                for step, sym_beh in instruction.steps_active:
                    #preserve old value
                    bu.keyframe_preserve(obj,"color",0,step, offset=1)
                    bu.keyframe_preserve(obj,"color",2,step, offset=1)

                    #set active for one step
                    bu.set_keyframe_for_duration(obj,obj.color,"color",0,step,step+1,1,0)
                    #make fully opaque when active (red)
                    bu.set_keyframe_for_duration(curve_obj,curve_obj.color,"color",0,step,step+1,1,0)
                    #remain 10% visible afterwards
                    bu.set_keyframe_for_duration(curve_obj,curve_obj.color,"color",1,step,step+3,1,0.1)
            else:
                bu.set_keyframe(obj, obj.color,"color",0,0,0)
                bu.set_keyframe(obj, obj.color,"color",1,0,0)
                bu.set_keyframe(obj, obj.color,"color",2,0,0)
                for step,sym_beh in instruction.steps_active:

                    #preserve old value
                    bu.keyframe_preserve(obj,"color",0,step, offset=1) #probably zero
                    bu.keyframe_preserve(obj,"color",2,step, offset=1)

                    #set active for one step
                    bu.set_keyframe_for_duration(obj,obj.color,"color",0,step,step+1,1,0)

                    if(sym_beh!=Symbolic_Beh.none):
                        symbolic_type = 0
                        data_index = 2
                        if(sym_beh==Symbolic_Beh.update):
                            symbolic_type=sym_beh.value #1
                            data_index = -1
                        elif(sym_beh==Symbolic_Beh.create):
                            symbolic_type=sym_beh.value #2
                            data_index = 0
                        elif(sym_beh==Symbolic_Beh.overwrite):
                            symbolic_type=sym_beh.value #3
                            data_index = 2
                        elif(sym_beh==Symbolic_Beh.destroy):
                            symbolic_type=sym_beh.value #4
                            data_index = 1
                        elif(sym_beh==Symbolic_Beh.special):
                            symbolic_type=sym_beh.value #5
                            data_index = 0
                        bu.set_keyframe_for_duration(obj,obj.color,"color",1,step,0,symbolic_type,0)

                        #set_keyframe(obj, obj.rotation_euler,"rotation_euler",0,frame_p=0,value=0)
                        #set_keyframe(obj, obj.rotation_euler,"rotation_euler",1,frame_p=0,value=0)
                        if(data_index>-1):
                            bu.keyframe_preserve(obj,"rotation_euler",data_index,frame_p=step*cfg.FRAME_STEP)
                            bu.set_keyframe(obj, obj.rotation_euler,"rotation_euler",data_index,frame_p=(step+1)*cfg.FRAME_STEP,value=math.radians(45)) #it shouldn't be necessary to reset the other angles
                        else:
                            bu.keyframe_preserve(obj,"rotation_euler",0,frame_p=step*cfg.FRAME_STEP)
                            bu.set_keyframe(obj, obj.rotation_euler,"rotation_euler",0,frame_p=(step+1)*cfg.FRAME_STEP,value=0)
                            bu.keyframe_preserve(obj,"rotation_euler",1,frame_p=step*cfg.FRAME_STEP)
                            bu.set_keyframe(obj, obj.rotation_euler,"rotation_euler",1,frame_p=(step+1)*cfg.FRAME_STEP,value=0)
                            bu.keyframe_preserve(obj,"rotation_euler",2,frame_p=step*cfg.FRAME_STEP)
                            bu.set_keyframe(obj, obj.rotation_euler,"rotation_euler",2,frame_p=(step+1)*cfg.FRAME_STEP,value=0)
                    else:
                        bu.keyframe_preserve(obj,"rotation_euler",0,frame_p=step*cfg.FRAME_STEP)
                        bu.set_keyframe(obj, obj.rotation_euler,"rotation_euler",0,frame_p=(step+1)*cfg.FRAME_STEP,value=0)
                        bu.keyframe_preserve(obj,"rotation_euler",1,frame_p=step*cfg.FRAME_STEP)
                        bu.set_keyframe(obj, obj.rotation_euler,"rotation_euler",1,frame_p=(step+1)*cfg.FRAME_STEP,value=0)
                        bu.keyframe_preserve(obj,"rotation_euler",2,frame_p=step*cfg.FRAME_STEP)
                        bu.set_keyframe(obj, obj.rotation_euler,"rotation_euler",2,frame_p=(step+1)*cfg.FRAME_STEP,value=0)
                for step,sym_beh in instruction.steps_active:
                    #for each active step set marker and camera location
                    bu.set_keyframe(cam, cam.location, "location", ind=0, frame_p=step*cfg.FRAME_STEP, value=(pc-global_start)*cfg.INSTRUCTION_DISTANCE)
                    bu.set_keyframe(cam, cam.location, "location", ind=1, frame_p=step*cfg.FRAME_STEP, value=run_id*cfg.RUN_DISTANCE)
                    bu.set_keyframe(cam, cam.location, "location", ind=2, frame_p=step*cfg.FRAME_STEP, value=cfg.CAM_DISTANCE+instruction.depth*cfg.INSTRUCTION_DISTANCE)

                    bu.set_keyframe(active_marker, active_marker.location, "location", ind=0, frame_p=step*cfg.FRAME_STEP, value=(pc-global_start)*cfg.INSTRUCTION_DISTANCE)
                    bu.set_keyframe(active_marker, active_marker.location, "location", ind=1, frame_p=step*cfg.FRAME_STEP, value=run_id*cfg.RUN_DISTANCE)
                    bu.set_keyframe(active_marker, active_marker.location, "location", ind=2, frame_p=step*cfg.FRAME_STEP, value=cfg.CUBE_SIZE*2 * (depth + 1))

        #print(f"Creating memory blocks for run {run_id}")
        memory_list_current_run = memory_list_per_run[run_count-1]
        for id, address in enumerate(memory_list_current_run):
            global_relative_position = memory_list.index(address)
            z_offset = global_relative_position * cfg.INSTRUCTION_DISTANCE*3
            mem_location = (0, 
                            run_id*cfg.RUN_DISTANCE, 
                            0-z_offset)
            bd.create_memory(f"Memory {hex(address)}", mem_location)
        #processed all instruction blocks    
        bu.set_keyframe(active_marker, active_marker.rotation_euler,"rotation_euler",2,frame_p=num_steps*cfg.FRAME_STEP,value=0.3 * num_steps)
        
        time_delta_current_run = datetime.now()-time_run_start
        print(f'[RUN {run_id} completed] (Duration: {time_delta_current_run})')
        time_average_run_duration += time_delta_current_run
    #print(entry.tag)

    time_all_runs_completed = datetime.now()
    time_average_run_duration = time_average_run_duration/run_count
    time_total_time = time_all_runs_completed-time_create_start
    print(f'[All runs completed] (Duration: {time_total_time} Average: {time_average_run_duration})')

    bd.create_pc_text(global_start, min_pc, max_pc)
    
    #create ground plane
    bu.create_ground(run_id, global_start, min_pc, max_pc)

    for parent_id, run in enumerate(discovered_links):
        for child in run:
            bu.create_text(location=(0,0,0), name=f"dc {parent_id}: {child[0]} s {child[1]}", text=f"dc {parent_id}: {child[0]} s {child[1]}", scale=1, material="mat_text")
            #create connection between parent and child
            c_run_id = child[0]
            c_step = child[1]
            print(f"Creating link for parent {parent_id} and child {c_run_id} for step {c_step}")
            x_address = get_address_for_step(runs[c_run_id], c_step)
            x_parent_address = get_address_for_step(runs[parent_id], c_step-1)# start the link from one step prior
            if(x_parent_address==-1): #if parent doesn't contain any steps prior, the child run was actually spawned by the first instruction
                x_parent_address=x_address
            x_target_offset = (x_address-x_parent_address)*cfg.INSTRUCTION_DISTANCE+cfg.INSTRUCTION_DISTANCE
            y_start = (parent_id+1)*cfg.RUN_DISTANCE-cfg.CUBE_SIZE
            y_target_offset = (c_run_id+1)*cfg.RUN_DISTANCE-cfg.CUBE_SIZE-y_start
            location_t = ((x_address - global_start)*cfg.INSTRUCTION_DISTANCE+cfg.INSTRUCTION_DISTANCE, 
                            y_start, 
                            cfg.BLOCK_Z+cfg.CUBE_SIZE)
            name = f"timeline_branch {c_run_id}"
            timeline_branch = bd.create_timeline_branch(name, location_t, x_target_offset, y_target_offset)
            
    bu.set_frame(1)

def get_address_for_step(run, step):
    for instruction in run.intruction_list:
        for a_step in instruction.steps_active:
            if(a_step[0]==step):
                return instruction.pc
    return -1

def main(path_dir_ptrace, path_dir_blocks, path_dir_source_code, max_steps, cube_size):
    if(max_steps>0):
        cfg.MAX_STEPS_TO_GENERATE = max_steps
    if(cube_size>0):
        cfg.CUBE_SIZE=cube_size

    tree,root = read_xml(path_dir_ptrace)

    run_list = parse_ptrace_xml(root)
    analysis_data = parse_analysis_xml(root)

    create_scene_from_processed_trace(run_list, analysis_data)
    if(len(path_dir_blocks)>0):
        tree_blocks, root_blocks = read_xml(path_dir_blocks)

        source_code = None
        if(len(path_dir_source_code)>0):
            source_code = open_file(source_code)

        create_control_flow_blocks(root_blocks, code_string=source_code, global_start=analysis_data.global_start)