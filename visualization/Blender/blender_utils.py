import bpy
import math

import visualization.Blender.config as cfg
from visualization.Enums.riscv_enum import Symbolic_Beh

## -- Blender related functions -- ##
def delete_material(name):
    bpy.data.materials.remove(bpy.data.materials[name])


def create_ground_material(material_name):
    mat = bpy.data.materials.get(material_name)
    if(mat):
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'


    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    node_location = -1800
    node_distance = 200

    nodes.new("ShaderNodeTexCoord")
    node_tex_coord = nodes["Texture Coordinate"]
    node_tex_coord.location = (node_location, 0)
    #node_tex_coord.label = "Texture Coordinates"
    node_location+=node_distance

    nodes.new(type="ShaderNodeMapping")
    node_mapping = nodes["Mapping"]
    node_mapping.location = (node_location, 0)
    #node_mapping.label = "ShaderNodeMapping"
    node_location+=node_distance

    nodes.new("ShaderNodeSeparateXYZ")
    node_separatexyz = nodes["Separate XYZ"]
    node_separatexyz.location = (node_location, 0)
    node_location+=node_distance

    nodes.new("ShaderNodeMath")
    node_math1 = nodes["Math"]
    node_math1.location = (node_location, 0)
    node_math1.operation = 'ADD'
    node_math1.inputs[1].default_value = 0
    node_location+=node_distance

    nodes.new("ShaderNodeMath")
    node_math_wrap = nodes["Math.001"]
    node_math_wrap.location = (node_location, 0)
    node_math_wrap.operation = 'WRAP'
    node_math_wrap.inputs[1].default_value = 0
    node_math_wrap.inputs[2].default_value = cfg.INSTRUCTION_DISTANCE * 8 #4.8
    node_location+=node_distance

    nodes.new("ShaderNodeMath")
    node_math_gt = nodes["Math.002"]
    node_math_gt.location = (node_location, 0)
    node_math_gt.operation = 'GREATER_THAN'
    node_math_gt.inputs[1].default_value = cfg.INSTRUCTION_DISTANCE * 4 #half of wrap
    node_location+=node_distance

    nodes.new("ShaderNodeMixRGB")
    node_rgb = nodes["Mix"]
    node_rgb.location = (node_location, 0)
    node_rgb.inputs[1].default_value = (0.15,0.15,0.15,1)
    node_rgb.inputs[2].default_value = (0.4,0.4,0.4,1)
    node_location+=node_distance

    nodes.new("ShaderNodeBsdfTransparent")
    node_transparent = nodes["Transparent BSDF"]
    node_transparent.location = (node_location, 100)
    node_location+=node_distance

    nodes.new("ShaderNodeMixShader")
    node_mixshader = nodes["Mix Shader"]
    node_mixshader.location = (node_location, 0)
    node_mixshader.inputs[0].default_value = 0.1




    out = nodes.get('Material Output') 
    nodes.remove(nodes.get('Principled BSDF'))

    #link nodes
    links.new(node_tex_coord.outputs[3], node_mapping.inputs[0])
    links.new(node_mapping.outputs[0], node_separatexyz.inputs[0])
    links.new(node_separatexyz.outputs[0], node_math1.inputs[0])
    links.new(node_math1.outputs[0], node_math_wrap.inputs[0])
    links.new(node_math_wrap.outputs[0], node_math_gt.inputs[0])
    links.new(node_math_gt.outputs[0], node_rgb.inputs[0])
    links.new(node_rgb.outputs[0], node_transparent.inputs[0])
    links.new(node_transparent.outputs[0], node_mixshader.inputs[1])
    links.new(node_rgb.outputs[0], node_mixshader.inputs[2])
    links.new(node_mixshader.outputs[0], out.inputs[0])

    return mat

def create_materials():
    create_material_arith("INSTRUCTION")
    create_material_ecall()
    create_material_arith("LOAD")
    create_material_arith("STORE")
    create_material_arith("TEST")
    create_material_jump()
    create_material_text()

    return

#deprecated
def __create_material_instruction():
    mat_name = "mat_instruction"
    mat = bpy.data.materials.get(mat_name)
    if(mat):
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    mat.blend_method = 'OPAQUE'


    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    node_start = -1800 #x
    node_location = -1800
    node_distance = 200
    node_y = 0

    """
    Shader
    """
    node_Obj_info = nodes.new("ShaderNodeObjectInfo")
    node_Obj_info.location = (node_location, 0)
    node_location+=node_distance


    node_separatergb = nodes.new("ShaderNodeSeparateRGB")
    #node_separatergb = nodes["Separate RGB"]
    node_separatergb.location = (node_location, 0)
    node_location+=node_distance

    links.new(node_Obj_info.outputs[1], node_separatergb.inputs[0]) #Color to input

    #process RGB
    rgb_node_split_location = node_location #save current location to kepp branches stacked

    #Red
    node_y -= cfg.Y_DIST
    node_math_red = nodes.new("ShaderNodeMath")
    node_math_red.label = "IS ACTIVE (Red Greater Than)"
    node_math_red.name = "IS ACTIVE (Red Greater Than)"
    node_math_red.location = (node_location, node_y)
    node_math_red.operation = 'GREATER_THAN'
    node_math_red.inputs[1].default_value = 0.9
    node_location+=node_distance

    links.new(node_separatergb.outputs[0], node_math_red.inputs[0])

    node_math_active_strength = nodes.new("ShaderNodeMath")
    node_math_active_strength.label = "ACTIVE STRENGTH MULTIPLY"
    node_math_active_strength.name = "ACTIVE STRENGTH MULTIPLY"
    node_math_active_strength.location = (node_location, node_y)
    node_math_active_strength.operation = 'MULTIPLY'
    node_math_active_strength.inputs[1].default_value = 2
    #node_location+=node_distance other node is at same x

    links.new(node_math_red.outputs[0], node_math_active_strength.inputs[0])


    node_y -= cfg.Y_DIST
    node_saturation_active = nodes.new("ShaderNodeHueSaturation")
    #node_saturation_active = nodes["Hue Saturation Value"]
    node_saturation_active.inputs['Color'].default_value = (0.5,0,0,1)
    node_saturation_active.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_math_red.outputs[0], node_saturation_active.inputs['Saturation'])

    node_y += cfg.Y_DIST

    nodes.new("ShaderNodeEmission")
    node_emission = nodes["Emission"]
    node_emission.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_saturation_active.outputs[0], node_emission.inputs['Color'])
    links.new(node_math_active_strength.outputs[0], node_emission.inputs['Strength'])





    #Green
    node_location = rgb_node_split_location
    node_y += cfg.Y_DIST

    #G1
    node_math_sym = nodes.new("ShaderNodeMath")
    node_math_sym.label = "SYMBOLIC TYPE"
    node_math_sym.name = "SYMBOLIC TYPE"
    node_math_sym.location = (node_location, node_y)
    node_math_sym.operation = 'SUBTRACT'
    node_math_sym.inputs[1].default_value = 2
    #node_location+=node_distance other node is at same x

    links.new(node_separatergb.outputs[1], node_math_sym.inputs[1])

    #G2
    node_y += cfg.Y_DIST

    node_math_green = nodes.new("ShaderNodeMath")
    node_math_green.label = "IS SYMBOLIC (GREEN Greater Than)"
    node_math_green.name = "IS SYMBOLIC (GREEN Greater Than)"
    node_math_green.location = (node_location, node_y)
    node_math_green.operation = 'GREATER_THAN'
    node_math_green.inputs[1].default_value = 0.4
    node_location+=node_distance

    links.new(node_separatergb.outputs[1], node_math_green.inputs[0])
    node_y -= cfg.Y_DIST


    
    node_mix_sym = nodes.new("ShaderNodeMixRGB")
    node_mix_sym.location = (node_location, node_y)
    node_mix_sym.inputs[1].default_value = (0.5,0,0,1)
    node_mix_sym.inputs[2].default_value = (0,1,0,1)
    node_location+=node_distance

    links.new(node_math_sym.outputs[0], node_mix_sym.inputs[0])

    node_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    #node_bsdf = nodes["Principled BSDF"]
    node_bsdf.name = "Main Principled"
    node_bsdf.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_mix_sym.outputs[0], node_bsdf.inputs['Emission'])
    links.new(node_math_green.outputs[0], node_bsdf.inputs['Emission Strength'])



    """
    Fac
    """
    node_location = node_start #reset location
    node_y += 400

    node_tex_coord = nodes.new("ShaderNodeTexCoord")
    #node_tex_coord = nodes["Texture Coordinate"]
    node_tex_coord.location = (node_location, node_y)
    node_location+=node_distance

    node_mapping = nodes.new(type="ShaderNodeMapping")
    #node_mapping = nodes["Mapping"]
    node_mapping.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_tex_coord.outputs[3], node_mapping.inputs[0])

    node_length = nodes.new("ShaderNodeVectorMath")
    #node_length = nodes["Vector Math"]
    node_length.location = (node_location, node_y)
    node_length.operation = 'LENGTH'
    node_length.label = "Length"
    node_length.name = "Length"
    node_location+=node_distance

    links.new(node_mapping.outputs[0], node_length.inputs[0])


    node_fac_greater = nodes.new("ShaderNodeMath")
    #node_fac_greater = nodes["Math"]
    node_fac_greater.label = "FAC GREATER THAN"
    node_fac_greater.name = "FAC GREATER THAN"
    node_fac_greater.location = (node_location, node_y)
    node_fac_greater.operation = 'GREATER_THAN'
    node_fac_greater.inputs[1].default_value = 1.3 #may be bugged
    node_location+=node_distance

    links.new(node_length.outputs['Value'], node_fac_greater.inputs['Value'])


    """
    Mix Shaders
    """
    node_mixshader = nodes.new("ShaderNodeMixShader")
    #node_mixshader = nodes["Mix Shader"]
    node_mixshader.location = (node_location, node_y)
    node_mixshader.inputs[0].default_value = 0.1

    links.new(node_fac_greater.outputs[0], node_mixshader.inputs[0])
    links.new(node_bsdf.outputs[0], node_mixshader.inputs[1])
    links.new(node_emission.outputs[0], node_mixshader.inputs[2])




    out = nodes.get('Material Output') 
    nodes.remove(nodes.get('Principled BSDF'))

    links.new(node_mixshader.outputs[0], out.inputs[0])

    return mat

def create_material_arith(type="INSTRUCTION"):
    if(type not in ("INSTRUCTION", "LOAD", "STORE")):
        print(f"[WARNING] Can't create material. Unknown material type {type}")
        return
    mat_name = "mat_store"
    if(type=="LOAD"):
        mat_name = "mat_load"
    if(type=="INSTRUCTION"):
        mat_name = "mat_instruction"
    mat = bpy.data.materials.get(mat_name)
    if(mat):
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    mat.blend_method = 'OPAQUE'


    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    node_start = -1800 #x
    node_location = -1800
    node_distance = 200
    node_y = 0

    """
    Shader
    """
    node_Obj_info = nodes.new("ShaderNodeObjectInfo")
    node_Obj_info.location = (node_location, 0)
    node_location+=node_distance


    node_separatergb = nodes.new("ShaderNodeSeparateRGB")
    #node_separatergb = nodes["Separate RGB"]
    node_separatergb.location = (node_location, 0)
    node_location+=node_distance

    links.new(node_Obj_info.outputs[1], node_separatergb.inputs[0]) #Color to input

    #process RGB
    rgb_node_split_location = node_location #save current location to kepp branches stacked

    #Red
    node_y -= cfg.Y_DIST
    node_math_red = nodes.new("ShaderNodeMath")
    node_math_red.label = "IS ACTIVE (Red Greater Than)"
    node_math_red.name = "IS ACTIVE (Red Greater Than)"
    node_math_red.location = (node_location, node_y)
    node_math_red.operation = 'GREATER_THAN'
    node_math_red.inputs[1].default_value = 0.9
    node_location+=node_distance

    links.new(node_separatergb.outputs[0], node_math_red.inputs[0])

    node_math_active_strength = nodes.new("ShaderNodeMath")
    node_math_active_strength.label = "ACTIVE STRENGTH MULTIPLY"
    node_math_active_strength.name = "ACTIVE STRENGTH MULTIPLY"
    node_math_active_strength.location = (node_location, node_y)
    node_math_active_strength.operation = 'MULTIPLY'
    node_math_active_strength.inputs[1].default_value = 2
    #node_location+=node_distance other node is at same x

    links.new(node_math_red.outputs[0], node_math_active_strength.inputs[0])


    node_y -= cfg.Y_DIST
    node_saturation_active = nodes.new("ShaderNodeHueSaturation")
    #node_saturation_active = nodes["Hue Saturation Value"]
    node_saturation_active.inputs['Color'].default_value = cfg.COLOR_ACTIVE
    node_saturation_active.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_math_red.outputs[0], node_saturation_active.inputs['Saturation'])

    node_y += cfg.Y_DIST

    node_bsdf2 = nodes.new("ShaderNodeBsdfPrincipled")
    node_bsdf2.name = "Main Principled"
    node_bsdf2.location = (node_location, node_y)
    node_bsdf2.inputs[0].default_value = cfg.COLOR_ARITH_MAIN
    node_location+=node_distance

    links.new(node_saturation_active.outputs[0], node_bsdf2.inputs['Emission'])
    links.new(node_math_active_strength.outputs[0], node_bsdf2.inputs['Emission Strength'])





    #Green
    node_location = rgb_node_split_location
    node_y += cfg.Y_DIST

    #G1
    node_math_sym = nodes.new("ShaderNodeMath")
    node_math_sym.label = "SYMBOLIC TYPE NORMALIZE"
    node_math_sym.name = "SYMBOLIC TYPE NORMALIZE"
    node_math_sym.location = (node_location, node_y)
    node_math_sym.operation = 'DIVIDE'
    node_math_sym.inputs[1].default_value = Symbolic_Beh.special.value
    #node_location+=node_distance other node is at same x

    links.new(node_separatergb.outputs[1], node_math_sym.inputs[0])

    #G2
    node_y += cfg.Y_DIST

    node_math_green = nodes.new("ShaderNodeMath")
    node_math_green.label = "IS SYMBOLIC (GREEN Greater Than)"
    node_math_green.name = "IS SYMBOLIC (GREEN Greater Than)"
    node_math_green.location = (node_location, node_y)
    node_math_green.operation = 'GREATER_THAN'
    node_math_green.inputs[1].default_value = 0.4
    node_location+=node_distance

    links.new(node_separatergb.outputs[1], node_math_green.inputs[0])
    node_y -= cfg.Y_DIST


    #normalized positions
    n_update=Symbolic_Beh.update.value/Symbolic_Beh.special.value
    n_create=Symbolic_Beh.create.value/Symbolic_Beh.special.value
    n_overwrite=Symbolic_Beh.overwrite.value/Symbolic_Beh.special.value
    n_destroy=Symbolic_Beh.destroy.value/Symbolic_Beh.special.value
    n_special = 1.0

    node_ramp_sym = nodes.new("ShaderNodeValToRGB")
    node_ramp_sym.location = (node_location, node_y)
    node_ramp_sym.color_ramp.elements.new(n_update)
    node_ramp_sym.color_ramp.elements.new(n_create)
    node_ramp_sym.color_ramp.elements.new(n_overwrite)
    node_ramp_sym.color_ramp.elements[0].color = cfg.COLOR_UPDATE
    node_ramp_sym.color_ramp.elements[1].color = cfg.COLOR_CREATE
    node_ramp_sym.color_ramp.elements[2].color = cfg.COLOR_OVERWRITE
    node_ramp_sym.color_ramp.elements[3].color = cfg.COLOR_DESTROY
    node_ramp_sym.color_ramp.elements[4].color = cfg.COLOR_SPECIAL
    node_ramp_sym.color_ramp.interpolation = 'CONSTANT'
    node_location+=node_distance


    links.new(node_math_sym.outputs[0], node_ramp_sym.inputs[0])

    node_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    #node_bsdf = nodes["Principled BSDF"]
    node_bsdf.name = "Main Principled"
    node_bsdf.location = (node_location, node_y)
    node_bsdf.inputs[0].default_value = cfg.COLOR_ARITH_SUB
    node_location+=node_distance

    links.new(node_ramp_sym.outputs[0], node_bsdf.inputs['Emission'])
    links.new(node_math_green.outputs[0], node_bsdf.inputs['Emission Strength'])



    """
    Fac
    """
    node_location = node_start #reset location
    node_y += 400

    node_tex_coord = nodes.new("ShaderNodeTexCoord")
    #node_tex_coord = nodes["Texture Coordinate"]
    node_tex_coord.location = (node_location, node_y)
    node_location+=node_distance

    node_mapping = nodes.new(type="ShaderNodeMapping")
    #node_mapping = nodes["Mapping"]
    node_mapping.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_tex_coord.outputs[3], node_mapping.inputs[0])

    if(type=="LOAD" or type=="STORE"):#load and store use an additional color at the top
        #Color Fac
        node_y -= cfg.Y_DIST
        color_fac_location = node_location

        node_separatexyz = nodes.new("ShaderNodeSeparateXYZ")
        node_separatexyz.location = (node_location, node_y)
        node_location+=node_distance

        links.new(node_mapping.outputs[0], node_separatexyz.inputs[0])

        node_fac_greater_c = nodes.new("ShaderNodeMath")
        node_fac_greater_c.label = "FAC GREATER THAN COLOR"
        node_fac_greater_c.name = "FAC GREATER THAN COLOR"
        node_fac_greater_c.location = (node_location, node_y)
        node_fac_greater_c.operation = 'GREATER_THAN'
        node_fac_greater_c.inputs[1].default_value = 0.3
        node_location+=node_distance

        links.new(node_separatexyz.outputs[2], node_fac_greater_c.inputs[0])

        color_type = (0,0.5,1,1)
        if(type=="LOAD"):
            color_type = (1,0.5,0,1)
        node_mix_type_color = nodes.new("ShaderNodeMixRGB")
        node_mix_type_color.location = (node_location, node_y)
        node_mix_type_color.inputs[1].default_value = (0,0,0,1)
        node_mix_type_color.inputs[2].default_value = color_type
        node_location+=node_distance

        links.new(node_fac_greater_c.outputs[0], node_mix_type_color.inputs[0])
        links.new(node_mix_type_color.outputs[0], node_bsdf.inputs['Base Color'])

        node_y += cfg.Y_DIST
        node_location = color_fac_location
    #Length FAC
    node_length = nodes.new("ShaderNodeVectorMath")
    #node_length = nodes["Vector Math"]
    node_length.location = (node_location, node_y)
    node_length.operation = 'LENGTH'
    node_length.label = "Length"
    node_length.name = "Length"
    node_location+=node_distance

    links.new(node_mapping.outputs[0], node_length.inputs[0])


    node_fac_greater = nodes.new("ShaderNodeMath")
    #node_fac_greater = nodes["Math"]
    node_fac_greater.label = "FAC GREATER THAN"
    node_fac_greater.name = "FAC GREATER THAN"
    node_fac_greater.location = (node_location, node_y)
    node_fac_greater.operation = 'GREATER_THAN'
    if(type=="INSTRUCTION"):
        node_fac_greater.inputs[1].default_value = 0.55*cfg.BASE_SIZE #cube has different dimensions
    else:
        node_fac_greater.inputs[1].default_value = 0.55*cfg.BASE_SIZE
    node_location+=node_distance

    links.new(node_length.outputs['Value'], node_fac_greater.inputs['Value'])


    """
    Mix Shaders
    """
    node_mixshader = nodes.new("ShaderNodeMixShader")
    #node_mixshader = nodes["Mix Shader"]
    node_mixshader.location = (node_location, node_y)
    node_mixshader.inputs[0].default_value = 0.1

    links.new(node_fac_greater.outputs[0], node_mixshader.inputs[0])
    links.new(node_bsdf.outputs[0], node_mixshader.inputs[1])
    links.new(node_bsdf2.outputs[0], node_mixshader.inputs[2])




    out = nodes.get('Material Output') 
    nodes.remove(nodes.get('Principled BSDF'))

    links.new(node_mixshader.outputs[0], out.inputs[0])

    return mat

def create_material_ecall():
    mat_name = "mat_ecall"
    mat = bpy.data.materials.get(mat_name)
    if(mat):
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    mat.blend_method = 'OPAQUE'


    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    node_start = -1800 #x
    node_location = -1800
    node_distance = 200
    node_y = 0

    """
    Emission Active
    """
    node_Obj_info = nodes.new("ShaderNodeObjectInfo")
    node_Obj_info.location = (node_location, node_y)
    node_location+=node_distance


    node_separatergb = nodes.new("ShaderNodeSeparateRGB")
    node_separatergb.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_Obj_info.outputs[1], node_separatergb.inputs[0]) #Color to input


    #Red
    node_math_red = nodes.new("ShaderNodeMath")
    node_math_red.label = "IS ACTIVE (Red Greater Than)"
    node_math_red.name = "IS ACTIVE (Red Greater Than)"
    node_math_red.location = (node_location, node_y)
    node_math_red.operation = 'GREATER_THAN'
    node_math_red.inputs[1].default_value = 0.9
    node_location+=node_distance

    links.new(node_separatergb.outputs[0], node_math_red.inputs[0])

    node_y -= cfg.Y_DIST
    node_math_active_fac = nodes.new("ShaderNodeMath")
    node_math_active_fac.label = "ACTIVE STRENGTH MULTIPLY"
    node_math_active_fac.name = "ACTIVE STRENGTH MULTIPLY"
    node_math_active_fac.location = (node_location, node_y)
    node_math_active_fac.operation = 'MULTIPLY'

    links.new(node_math_red.outputs[0], node_math_active_fac.inputs[1])#input 0 still missing at this point

    """
    Color
    """
    node_location = node_start #reset location
    node_y -= cfg.Y_DIST

    node_tex_coord = nodes.new("ShaderNodeTexCoord")
    node_tex_coord.location = (node_location, node_y)
    node_location+=node_distance

    node_length = nodes.new("ShaderNodeVectorMath")
    node_length.location = (node_location, node_y)
    node_length.operation = 'LENGTH'
    node_length.label = "Length"
    node_length.name = "Length"
    node_location+=node_distance

    links.new(node_tex_coord.outputs['Object'], node_length.inputs[0])


    node_y -= cfg.Y_DIST
    node_math_scale = nodes.new("ShaderNodeMath")
    node_math_scale.label = "SCALE TO SIZE"
    node_math_scale.name = "SCALE TO SIZE"
    node_math_scale.location = (node_location, node_y)
    node_math_scale.operation = 'DIVIDE'
    node_math_scale.inputs[1].default_value = 2*cfg.BASE_SIZE

    links.new(node_length.outputs['Value'], node_math_scale.inputs[0])

    node_y -= cfg.Y_DIST
    node_fac_less = nodes.new("ShaderNodeMath")
    node_fac_less.label = "FAC LESS THAN"
    node_fac_less.name = "FAC LESS THAN"
    node_fac_less.location = (node_location, node_y)
    node_fac_less.operation = 'LESS_THAN'
    node_fac_less.inputs[1].default_value = 0.31

    links.new(node_math_scale.outputs['Value'], node_fac_less.inputs['Value'])
    links.new(node_fac_less.outputs[0], node_math_active_fac.inputs[0])

    node_y += cfg.Y_DIST/2
    node_fac_greater = nodes.new("ShaderNodeMath")
    node_fac_greater.label = "FAC GREATER THAN"
    node_fac_greater.name = "FAC GREATER THAN"
    node_fac_greater.location = (node_location, node_y)
    node_fac_greater.operation = 'GREATER_THAN'
    node_fac_greater.inputs[1].default_value = 0.34
    node_location+=node_distance

    links.new(node_math_scale.outputs['Value'], node_fac_greater.inputs['Value'])


    node_mix1 = nodes.new("ShaderNodeMixRGB")
    node_mix1.location = (node_location, node_y)
    node_mix1.inputs[1].default_value = (0,0,0,1)
    node_mix1.inputs[2].default_value = (2,2,2,1)
    node_location+=node_distance

    links.new(node_fac_less.outputs[0], node_mix1.inputs[0])

    node_mix2 = nodes.new("ShaderNodeMixRGB")
    node_mix2.location = (node_location, node_y)
    node_mix2.inputs[2].default_value = (1,0.7,0,1)
    node_location+=node_distance

    links.new(node_fac_greater.outputs[0], node_mix2.inputs[0])
    links.new(node_mix1.outputs[0], node_mix2.inputs[1])

    node_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    node_bsdf.name = "Main Principled"
    node_bsdf.location = (node_location, node_y)
    node_bsdf.inputs['Emission'].default_value = cfg.COLOR_ACTIVE
    node_location+=node_distance

    links.new(node_mix2.outputs[0], node_bsdf.inputs[0])
    links.new(node_math_active_fac.outputs[0], node_bsdf.inputs['Emission Strength'])


    out = nodes.get('Material Output') 
    nodes.remove(nodes.get('Principled BSDF'))

    links.new(node_bsdf.outputs[0], out.inputs[0])

    return mat

def create_material_jump():
    mat_name = "mat_jump"
    mat = bpy.data.materials.get(mat_name)
    if(mat):
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    mat.blend_method = 'OPAQUE'


    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    node_start = -1800 #x
    node_location = -1800
    node_distance = 200
    node_y = 0

    """
    Emission Active
    """
    node_Obj_info = nodes.new("ShaderNodeObjectInfo")
    node_Obj_info.location = (node_location, node_y)
    node_location+=node_distance


    node_separatergb = nodes.new("ShaderNodeSeparateRGB")
    node_separatergb.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_Obj_info.outputs[1], node_separatergb.inputs[0]) #Color to input


    #Red
    node_math_red = nodes.new("ShaderNodeMath")
    node_math_red.label = "IS ACTIVE (Red Greater Than)"
    node_math_red.name = "IS ACTIVE (Red Greater Than)"
    node_math_red.location = (node_location, node_y)
    node_math_red.operation = 'GREATER_THAN'
    node_math_red.inputs[1].default_value = 0.9
    node_location+=node_distance

    links.new(node_separatergb.outputs[0], node_math_red.inputs[0])

    node_y -= cfg.Y_DIST
    node_math_active_fac = nodes.new("ShaderNodeMath")
    node_math_active_fac.label = "ACTIVE STRENGTH MULTIPLY"
    node_math_active_fac.name = "ACTIVE STRENGTH MULTIPLY"
    node_math_active_fac.location = (node_location, node_y)
    node_math_active_fac.operation = 'MULTIPLY'

    links.new(node_math_red.outputs[0], node_math_active_fac.inputs[1])#input 0 still missing at this point

    """
    Color
    """
    node_location = node_start #reset location
    node_y -= cfg.Y_DIST

    node_tex_coord = nodes.new("ShaderNodeTexCoord")
    node_tex_coord.location = (node_location, node_y)
    node_location+=node_distance

    node_abs = nodes.new("ShaderNodeVectorMath")
    node_abs.location = (node_location, node_y)
    node_abs.operation = 'ABSOLUTE'
    node_abs.label = "Abs"
    node_abs.name = "Abs"
    node_location+=node_distance

    links.new(node_tex_coord.outputs['Object'], node_abs.inputs[0])

    node_separatexyz = nodes.new("ShaderNodeSeparateXYZ")
    #node_separatexyz = nodes["Separate XYZ"]
    node_separatexyz.location = (node_location, node_y)
    node_location+=node_distance

    links.new(node_abs.outputs['Vector'], node_separatexyz.inputs[0])

    node_y -= cfg.Y_DIST
    node_fac_sm = nodes.new("ShaderNodeMath")
    node_fac_sm.label = "FAC SMOOTH_MIN"
    node_fac_sm.name = "FAC SMOOTH_MIN"
    node_fac_sm.location = (node_location, node_y)
    node_fac_sm.operation = 'SMOOTH_MIN'
    node_fac_sm.inputs[2].default_value = 0.6

    links.new(node_separatexyz.outputs['X'], node_fac_sm.inputs[0])
    links.new(node_separatexyz.outputs['Y'], node_fac_sm.inputs[1])

    node_fac_less = nodes.new("ShaderNodeMath")
    node_fac_less.label = "FAC LESS"
    node_fac_less.name = "FAC LESS"
    node_fac_less.location = (node_location, node_y)
    node_fac_less.operation = 'LESS_THAN'
    node_fac_less.inputs[1].default_value = 0.0
    node_location+=node_distance

    links.new(node_fac_sm.outputs['Value'], node_fac_less.inputs[0])


    links.new(node_fac_less.outputs[0], node_math_active_fac.inputs[0])#TODO maybe invert this with a sub node


    node_mix1 = nodes.new("ShaderNodeMixRGB")
    node_mix1.location = (node_location, node_y)
    node_mix1.inputs[1].default_value = cfg.COLOR_JUMP_MAIN
    node_mix1.inputs[2].default_value = cfg.COLOR_JUMP_SUB
    node_location+=node_distance

    links.new(node_fac_less.outputs[0], node_mix1.inputs[0])

    node_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    node_bsdf.name = "Main Principled"
    node_bsdf.location = (node_location, node_y)
    node_bsdf.inputs['Emission'].default_value = cfg.COLOR_ACTIVE
    node_location+=node_distance

    links.new(node_mix1.outputs[0], node_bsdf.inputs[0])
    links.new(node_math_active_fac.outputs[0], node_bsdf.inputs['Emission Strength'])


    out = nodes.get('Material Output') 
    nodes.remove(nodes.get('Principled BSDF'))

    links.new(node_bsdf.outputs[0], out.inputs[0])

    return mat

def create_material_text():
    mat_name = "mat_text"
    mat = bpy.data.materials.get(mat_name)
    if(mat):
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    mat.blend_method = 'OPAQUE'


    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    node_start = -1800 #x
    node_location = -1800
    node_distance = 200
    node_y = 0

    node_color1 = nodes.new("ShaderNodeHueSaturation")
    node_color1.location = (node_location, node_y)
    node_color1.inputs["Color"].default_value = cfg.COLOR_TEXT
    node_location+=node_distance

    out = nodes.get('Material Output') 
    nodes.remove(nodes.get('Principled BSDF'))

    links.new(node_color1.outputs[0], out.inputs[0])

    return mat



def create_ground(run, global_start, min_pc, max_pc):
    bpy.ops.mesh.primitive_plane_add(size=cfg.BASE_SIZE, enter_editmode=False, align='WORLD', 
                                        location=(0, 0, cfg.TEXT_HEIGHT-0.1), 
                                        scale=(1, 1, 1))
    #maybe sub INSTRUCTION_DISTANCE offset to make the edge stand out a little
    x_range = (max_pc-min_pc)*cfg.INSTRUCTION_DISTANCE
    y_range = run*cfg.RUN_DISTANCE
    center_offset = -(global_start-min_pc)*cfg.INSTRUCTION_DISTANCE
    print(f"xr{x_range} yr {y_range} center {center_offset}")#347
    bpy.ops.transform.resize(value=(x_range, y_range, 1), 
                                orient_type='GLOBAL', 
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                                orient_matrix_type='GLOBAL', 
                                constraint_axis=(True, False, False), mirror=True, 
                                use_proportional_edit=False, proportional_edit_falloff='SMOOTH', 
                                proportional_size=1, use_proportional_connected=False, 
                                use_proportional_projected=False)
    
    bpy.ops.transform.translate(value=(x_range/2+center_offset, y_range/2, 0), orient_type='GLOBAL', 
                                    orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                                    orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), 
                                    mirror=True, use_proportional_edit=False, 
                                    proportional_edit_falloff='SMOOTH', proportional_size=1, 
                                    use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    ground = bpy.context.selected_objects[0]
    mat = bpy.data.materials.get("pc_ground")
    if mat is None:
        # create material
        mat = create_ground_material("pc_ground")
        cfg.GROUND_MAT_WAS_CREATED = True
    else:
        if(not cfg.GROUND_MAT_WAS_CREATED):
            delete_material("pc_ground")
            mat = create_ground_material("pc_ground")
            cfg.GROUND_MAT_WAS_CREATED = True

    if ground.data.materials:
        # assign to 1st material slot
        ground.data.materials[0] = mat
    else:
        # no slots
        ground.data.materials.append(mat)
    return ground

def set_frame(step):
    """set the current frame to the beginning when step is active"""
    bpy.context.scene.frame_current = step*cfg.FRAME_STEP

def set_keyframe(obj,obj_data,data_p,ind,frame_p,value):
    """sets the obj_data of obj at index ind to value and inserts a keyframe at frame_p"""
    frame_backup = bpy.context.scene.frame_current
    set_frame(frame_p)
    obj_data[ind] = value
    obj.keyframe_insert(data_path=data_p, frame=frame_p, index=ind)
    set_frame(frame_backup)

def keyframe_preserve(obj,data_p,ind,frame_p, offset=2):
    """ Add a keyframe for the specified object data to preseve any old value that might have been set previously
        and prevent unwanted long interpolations between old and new values
    """
    frame_backup = bpy.context.scene.frame_current
    set_frame(frame_p-offset)
    obj.keyframe_insert(data_path=data_p, frame=frame_p, index=ind)
    set_frame(frame_backup)

def set_keyframe_for_duration(obj,obj_data,data_p,ind,start_frame,end_frame,value,value_post):
    frame_backup = bpy.context.scene.frame_current
    """Add two keyframes for the specified object data 
       one at frame_start with value and the 
       second at end_frame with value_post"""

    bpy.context.scene.frame_current = (start_frame-1)*cfg.FRAME_STEP
    obj.keyframe_insert(data_path=data_p, frame=(start_frame-1)*cfg.FRAME_STEP, index=ind)
    #bpy.ops.action.interpolation_type(type='CONSTANT')
    bpy.context.scene.frame_current = start_frame #step*FRAME_STEP
    obj_data[ind] = value
    obj.keyframe_insert(data_path=data_p, frame=start_frame*cfg.FRAME_STEP, index=ind)
    #bpy.ops.action.interpolation_type(type='CONSTANT')
    if(end_frame>0):#TODO check this again
        if(cfg.FRAME_STEP>1):#if a step lasts more than 1 frame, add an additional keyframe to keep the value until end of duration
            obj.keyframe_insert(data_path=data_p, frame=start_frame*cfg.FRAME_STEP+cfg.FRAME_STEP-1, index=ind)
        obj_data[ind] = value_post
        obj.keyframe_insert(data_path=data_p, frame=(end_frame)*cfg.FRAME_STEP, index=ind)

    bpy.context.scene.frame_current = frame_backup


def assign_material(obj,mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        # create material
        missing_name = mat_name + "_missing"
        mat = bpy.data.materials.get(missing_name)
        if(mat is None): #check if _missing material was already created
            mat = bpy.data.materials.new(name=missing_name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            nodes.new("ShaderNodeMixRGB")
            node_rgb = nodes["Mix"]
            node_rgb.location = (0, 0)
            node_rgb.inputs[1].default_value = (1,0,1,1)
            node_rgb.inputs[2].default_value = (1,0,1,1)

            out = nodes.get('Material Output') 
            links.new(node_rgb.outputs[0], out.inputs[0])
        else:
            pass
    if obj.data.materials:
        # assign to 1st material slot
        obj.data.materials[0] = mat
    else:
        # no slots
        obj.data.materials.append(mat)

def set_curve_bezier_point(curve, index, axis, value):
    curve.data.splines.active.bezier_points[index].co[axis] = value

#def set_curve_bezier_rotation(curve, index, axis, value):
#    curve.data.splines.active.bezier_points[index].co[axis] = value

def set_curve_path_point(curve, index, point):
    set_curve_path_axis(curve,index,0,point[0])
    set_curve_path_axis(curve,index,1,point[1])
    set_curve_path_axis(curve,index,2,point[2])

def set_curve_path_axis(curve, index, axis, value):
    curve.data.splines.active.points[index].co[axis]=value

def connect_points_with_curve(curve, point_start, point_end):
    """set individual points to connect start and end points
       dist in x
       offset in y (input should always be zero)
       depth diff in z
       currently works hardcoded with the default of 5 curve points
    """
    set_curve_path_point(curve,0,point_start)
    
    dist = point_end[0]-point_start[0]#maybe take absolute for offset
    offset = 0.05*dist+0.1
    target_x = 0
    target_y = (point_start[1]+point_end[1])/2-offset/2
    target_z = max(point_start[2],point_end[2])+(abs(point_start[2]-point_end[2])/2)+0.1
    target_point = (target_x,target_y,target_z)

    for i in range(1,4):
        target_point = tuple(map(sum,zip(target_point,(dist/5,offset,0))))
        set_curve_path_point(curve,i,target_point)

    set_curve_path_point(curve,4,point_end)

def connect_runs_with_curve(curve, point_start, point_end):
    """set individual points to connect start and end points
       step dist in x (always 1)
       run distance
       depth diff in z
       currently works hardcoded with the default of 5 curve points
    """
    dist_x = point_end[0]-point_start[0]
    dist_y = point_end[1]-point_start[1]

    for i in range(0,5):
        target_x = (dist_x/4)*i
        target_y = (dist_y/4)*i
        target_point = (target_x, target_y, point_end[2])
        set_curve_path_point(curve,i,target_point)

def create_text(location, name, text, scale, material):
    bpy.ops.object.text_add(enter_editmode=False, align='WORLD', 
                            location=(location), 
                            rotation=(0, 0, math.radians(90)), scale=(1, 1, 1))
    text_obj = bpy.context.selected_objects[0]
    text_obj.name = name
    text_obj.data.body = text
    bpy.ops.transform.resize(value=(cfg.TEXT_SCALE*scale, cfg.TEXT_SCALE*scale, cfg.TEXT_SCALE*scale), 
                                orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                                orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, 
                                proportional_edit_falloff='SMOOTH', proportional_size=1, 
                                use_proportional_connected=False, use_proportional_projected=False)
    assign_material(text_obj,material)
    return text_obj

def init_scene():
    bpy.context.scene.frame_current = 0
    cfg.GROUND_MAT_WAS_CREATED =False