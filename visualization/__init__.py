bl_info = {
    "name": "Symex Import",
    "blender": (2, 92, 0),
    "category": "Import-Export",
    "location": "File > Import",
}

if "bpy" in locals():
    import importlib
    reloadable_modules = [
        'create_scene_from_processed_trace',
    ]
    for module_name in reloadable_modules:
        if module_name in locals():
            importlib.reload(locals()[module_name])
else:
    from visualization import create_scene_from_processed_trace
    #from visualization import create_scene_from_processed_trace
    #from visualization import create_scene_from_processed_trace
    #from visualization import create_scene_from_processed_trace


import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty
from bpy.types import Operator, OperatorFileListElement
from bpy_extras.io_utils import ImportHelper

import os
from pathlib import Path


class ObjectImportSymex(Operator, ImportHelper):
    """Imports a ptrace xml file""" 
    bl_idname = "import.symex"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Import SymEx Trace"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    filename_ext = ".ptrace"
    """filter_glob = StringProperty(
        default="*.xml",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
        )"""

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Auto select .blk file",
        description="Automatically select the matching .blk file for the currently highlighted .ptrace",
        default=False,
    )
    max_steps: IntProperty(
        name="Max Steps", #MAX_STEPS_TO_GENERATE
        default=300, 
        min=1, 
        max=3000
    )
    cube_size: FloatProperty(
        name="Size", #CUBE_SIZE
        default=1, 
        min=0.01, 
        max=10.0
    )

    trace_blocks_path: StringProperty(
      name = "(Optional) Path to Blocks.blk",
      default = "",
      description = "Path to the location of blocks.blk",
      subtype = 'FILE_PATH'
    )

    source_code: StringProperty(
      name = "(Optional) Path to single source code file",
      default = "",
      description = "Path to single source code file used to annotate Function Blocks",
      subtype = 'FILE_PATH'
    )

    filepath: StringProperty(
      name = "Path to .ptrace xml file",
      default = "",
      maxlen = 1024,
      description = "Specify the location of the trace to visualize",
      subtype = 'FILE_PATH'
    )

    do_smth: EnumProperty(
            name="Split",
            items=(('ON', "Create Scene", "Run the script as normal"),
                   ('OFF', "Just check the script", "Don't do anything and exit"),
                   ),
            )

    def __init__(self):
        self.last_blocks_path = ""
        super().__init__()

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Settings")
        rowsub = col.row()
        rowsub.prop(self, "max_steps")
        rowsub = col.row()
        rowsub.prop(self, "cube_size")


        box = layout.box()
        box.label(text="Additional Files")
        col = box.column()
        #col.label(text="Files")
        rowsub = col.row()
        rowsub.prop(self, "use_setting")
        rowsub = col.row()
        rowsub.prop(self, "trace_blocks_path")
        rowsub = col.row()
        rowsub.prop(self, "source_code")

        filebrowser_params = context.space_data.params
        filename  = Path(filebrowser_params.filename)
        directory = Path(filebrowser_params.directory.decode())

        if(self.use_setting):
            if filename.suffix == ".ptrace":
                if self.trace_blocks_path == "" or self.trace_blocks_path == self.last_blocks_path:
                    auto_path = directory / (filename.stem + ".blk")
                    if auto_path.is_file():
                        self.trace_blocks_path = str(auto_path)
                        self.last_blocks_path = self.trace_blocks_path
                    else:
                        self.trace_blocks_path = ""
            else:
                self.trace_blocks_path = ""

    """Alternative file selection dialogue
        
        def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.label(text="Files")
        rowsub = col.row()
        rowsub.prop(self, "filepath")
        rowsub = col.row()
        rowsub.prop(self, "trace_path1")
        rowsub = col.row()
        rowsub.prop(self, "trace_path2")
      

        box = layout.box()
        col = box.column()
        col.label(text="Settings")
        rowsub = col.row(align=True)
        rowsub.prop(self, "use_setting")
        rowsub.prop(self, "do_smth")
        rowsub = col.row()
        rowsub.prop(self, "total_test")"""

    def execute(self, context):        # execute() is called when running the operator.

        if(self.do_smth == 'OFF'):
            return {'FINISHED'} 

        # The original script
        scene = context.scene

        path_dir_ptrace = self.filepath
        path_dir_blocks = self.trace_blocks_path
        path_dir_source = self.source_code

        if(len(path_dir_ptrace)>0):
            create_scene_from_processed_trace.main(path_dir_ptrace, path_dir_blocks, path_dir_source, self.max_steps, self.cube_size)
        else:
            print("[ERROR] Path not specified")

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.

def menu_func(self, context):
    self.layout.operator(ObjectImportSymex.bl_idname)



def register():
    bpy.utils.register_class(ObjectImportSymex)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)  # Adds the new operator to an existing menu.

def unregister():
    bpy.utils.unregister_class(ObjectImportSymex)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)
