bl_info = {
    "name": "Game Property Injector",
    "author": "Jonathan Sandusky",
    "version": (0, 2, 0),
    "blender": (2, 6, 9),
    "location": "Properties > Object",
    "description": "Property injection and exporting for games",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Game Engine"}

import bpy
from bpy.props import *

def loadTypes(filePath):
    f = open(filePath,'r')
    types = []
    getTypes(f,types)
    return types

def getTypes(f,types):
    line = f.readline()
    if not line: return
    
    line = line.replace("\n","")
    types.append(line)
    
    getTypes(f,types)
    
    #if string.find(line,"\t") == -1:
    #    parts = string.split(line)
    #    typeName = ""
    #    typeType = ""
    #    if typeName == "entity":
    #        readClass(f,types)
            
def readClass(f,types, name):
    line = f.readLine();
    line = string.replace(line,"\t","")
    line = string.replace(line,"\n","")
    parts = string.split(line);
    
    types.append((name,parts[0],parts[1]))
    
    #call the parent
    getTypes(f,types)

def bindScene():
    types = loadTypes("C:\entities.txt")
    print(types)
    objects = []
    
    start = 0
    for o in types:
        objects.append((str(o), str(o), str(o)))
        start += 1
        
    bpy.types.Object.entity_type = EnumProperty(
        items = objects,
        name = "Entity Type")
    bpy.types.Object.difficulty = EnumProperty(
        items = [("0","Easy","0"),
            ("1","Medium","1"),
            ("2","Hard","2")],
        name = "Difficulty")
    #bpy.types.Scene.EnumProperty( attr="entity_type", name="types", description="Choose an object", items=objects, default='0')

def main(context):
    context.active_object["GameObjectName"] = ""
    

class InjectGameTypes(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.inject_game"
    bl_label = "Inject Game Types"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}

class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Game Settings"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.operator("object.inject_game")
        row = layout.row()
        row.prop(obj, '["GameObjectName"]', text = "Name")
        row = layout.row()
        row.prop(obj, "entity_type")
        row = layout.row()
        row.prop(obj, "difficulty")

def register():
    bindScene()
    bpy.utils.register_class(InjectGameTypes)
    bpy.utils.register_class(HelloWorldPanel)

def unregister():
    bpy.utils.unregister_class(InjectGameTypes)
    bpy.utils.unregister_class(HelloWorldPanel)

if __name__ == "__main__":
    register()
    bindScene()
