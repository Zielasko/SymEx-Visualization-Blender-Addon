import bpy


def delete_material(name):
    bpy.data.materials.remove(bpy.data.materials[name])


def create_ground_material(material_name):
    mat = bpy.data.materials.get(material_name)
    if(mat):
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    

    nodes.new("ShaderNodeTexCoord")
    node_tex_coord = nodes["Texture Coordinate"]
    node_tex_coord.location = (-1200, 0)
    #node_tex_coord.label = "Texture Coordinates"

    nodes.new(type="ShaderNodeMapping")
    node_mapping = nodes["Mapping"]
    node_mapping.location = (-1000, 0)
    #node_mapping.label = "ShaderNodeMapping"

    nodes.new("ShaderNodeSeparateXYZ")
    node_separatexyz = nodes["Separate XYZ"]
    node_separatexyz.location = (-800, 0)

    nodes.new("ShaderNodeMath")
    node_math1 = nodes["Math"]
    node_math1.location = (-600, 0)
    node_math1.operation = 'ADD'
    node_math1.inputs[1].default_value = 0

    nodes.new("ShaderNodeMath")
    node_math_wrap = nodes["Math.001"]
    node_math_wrap.location = (-400, 0)
    node_math_wrap.operation = 'WRAP'
    node_math_wrap.inputs[1].default_value = 0
    node_math_wrap.inputs[2].default_value = 4.8 #TODO multiple of pc_dist

    nodes.new("ShaderNodeMath")
    node_math_gt = nodes["Math.002"]
    node_math_gt.location = (-200, 0)
    node_math_gt.operation = 'GREATER_THAN'
    node_math_gt.inputs[1].default_value = 2.4 #TODO half of wrap

    nodes.new("ShaderNodeMixRGB")
    node_rgb = nodes["Mix"]
    node_rgb.location = (0, 0)
    node_rgb.inputs[1].default_value = (0.1,0.1,0.15,1)
    node_rgb.inputs[2].default_value = (0.4,0.4,0.4,1)



    out = nodes.get('Material Output') 
    nodes.remove(nodes.get('Principled BSDF'))

    #link nodes
    links.new(node_tex_coord.outputs[3], node_mapping.inputs[0])
    links.new(node_mapping.outputs[0], node_separatexyz.inputs[0])
    links.new(node_separatexyz.outputs[0], node_math1.inputs[0])
    links.new(node_math1.outputs[0], node_math_wrap.inputs[0])
    links.new(node_math_wrap.outputs[0], node_math_gt.inputs[0])
    links.new(node_math_gt.outputs[0], node_rgb.inputs[0])
    links.new(node_rgb.outputs[0], out.inputs[0])



create_ground_material("pc_ground_test1")