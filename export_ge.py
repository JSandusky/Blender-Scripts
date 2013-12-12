import bpy
import inspect
import collections

bl_info = {
    "name": "Game XML Exporter",
    "author": "Jonathan Sandusky",
    "version": (0, 2, 0),
    "blender": (2, 6, 9),
    "location": "File > Export",
    "description": "Export objects to XML with properties needed for game engine import",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

def write_field(o, f, name, depth):
    if not hasattr(o,name):
        return
    for i in range(0,depth):
        f.write("\t")
    f.write("<" + name + ">")
    f.write(str(getattr(o,name)))
    f.write("</" + name + ">\n")

def write_state(o, f, s, name,depth):
    for i in range(0,depth):
        f.write("\t")
    f.write("<" + name + ">")
    for val in s:
        if val:
            f.write("1,")
        else:
            f.write("0,")
    f.write("</" + name + ">\n")

def write_some_data(context, filepath):
    f = open(filepath, 'w', encoding='utf-8')
    f.write("<game>\n")
    for o in context.scene.objects:
        if not o.game is None:
            f.write("\t<object name=\"" + o.name + "\" type=\"" + o.type + "\">\n")
            f.write("\t\t<transform>\n")
            f.write("\t\t\t<position x=\"" + str(o.location.x) + "\" y=\"" + str(o.location.y) + "\" z=\"" + str(o.location.z) + "\" />\n")
            f.write("\t\t\t<rotation x=\"" + str(o.rotation_euler.x * 360.0) + "\" y=\"" + str(o.rotation_euler.y * 360.0) + "\" z=\"" + str(o.rotation_euler.z * 360.0) + "\" />\n")
            f.write("\t\t\t<scale x=\"" + str(o.scale.x) + "\" y=\"" + str(o.scale.y) + "\" z=\"" + str(o.scale.z) + "\" />\n")
            f.write("\t\t</transform>\n")
            
            if o.type == "LAMP":
                f.write("\t\t<light>\n")
                f.write("\t\t\t<type>" + str(o.data.type) + "</type>\n")
                f.write("\t\t\t<energy>" + str(o.data.energy) + "</energy>\n")
                f.write("\t\t\t<use_shadow>" + str(o.data.use_shadow) + "</use_shadow>\n")
                f.write("\t\t\t<use_diffuse>" + str(o.data.use_diffuse) + "</use_diffuse>\n")
                f.write("\t\t\t<use_specular>" + str(o.data.use_specular) + "</use_specular>\n")
                f.write("\t\t\t<color r=\"" + str(o.data.color.r) + "\" g=\"" + str(o.data.color.g) + "\" b=\"" + str(o.data.color.b) + "\"/>\n")
                f.write("\t\t</light>\n")
                
            if o.type == "CURVE":
                f.write("\t\t<curve>\n")
                for spline in o.data.splines:
                    f.write("\t\t\t<spline type=\"" + str(spline.type) + "\">\n")
                    if len(spline.points) > 0:
                        for point in spline.points:
                            f.write("\t\t\t\t<point x=\"" + str(point.co.x) + "\" y=\"" + str(point.co.y) + "\" z=\"" + str(point.co.z) + "\" w=\"" + str(point.co.w) + "\"/>\n")
                    elif len(spline.bezier_points) > 0:
                        for point in spline.bezier_points:
                            f.write("\t\t\t\t<point x=\"" + str(point.co.x) + "\" y=\"" + str(point.co.y) + "\" z=\"" + str(point.co.z) + "\">\n")
                            f.write("\t\t\t\t\t<handle_left x=\"" + str(point.handle_left.x) + "\" y=\"" + str(point.handle_left.y) + "\" z=\"" + str(point.handle_left.z) + "\"/>\n")
                            f.write("\t\t\t\t\t<handle_right x=\"" + str(point.handle_right.x) + "\" y=\"" + str(point.handle_right.y) + "\" z=\"" + str(point.handle_right.z) + "\"/>\n")
                            f.write("\t\t\t\t</point>\n")
                        
                    f.write("\t\t\t</spline>\n")
                f.write("\t\t</curve>\n")
            
            f.write("\t\t<properties>\n")
                
            for item in o.items(): #write out magical enum values
                if hasattr(o,item[0]):
                    write_field(o,f,str(item[0]),3)
            for item in o.items():
                if not hasattr(o,item[0]) and not item[0].find("RNA") > -1: #RNA is for Blender bullshit
                    f.write("\t\t\t<" + str(item[0]) + ">" + str(item[1]) + "</" + str(item[0]) + ">\n")
            
            for prop in o.game.properties:
                write_field(o,f,prop.name,3)
            f.write("\t\t</properties>\n")
            
            if o.type == "LAMP" or o.type == "CAMERA" or o.type == "CURVE":
                f.write("\t</object>\n")
                continue
                
            #write attributes
            write_field(o.game, f, "collision_bounds_type",2)
            write_field(o.game, f, "physics_type",2)
            write_field(o.game, f, "collision_margin",2)
            write_field(o.game, f, "form_factor",2)
            write_field(o.game, f, "damping",2)
            write_field(o.game, f, "rotation_damping",2)
            write_field(o.game, f, "fall_speed",2)
            write_field(o.game, f, "jump_speed",2)
            write_field(o.game, f, "step_height",2)
            write_field(o.game, f, "mass",2)
            write_field(o.game, f, "radius",2)
            write_field(o.game, f, "obstacle_radius",2)
            write_field(o.game, f, "use_collision_bounds",2)
            write_field(o.game, f, "use_collision_compound",2)
            write_field(o.game, f, "use_ghost",2)
            write_field(o.game, f, "use_sleep",2)
            write_field(o.game, f, "velocity_min",2)
            write_field(o.game, f, "velocity_max",2)
            write_field(o.game, f, "use_actor",2)
            write_state(o.game, f, o.game.collision_group,"collision_group",2)
            write_state(o.game, f, o.game.collision_mask,"collision_mask",2)
            for sensor in o.game.sensors:
                f.write("\t\t<sensor type=\"" + sensor.type + "\" name=\"" + sensor.name + "\">\n")
                write_field(sensor,f,"property",3)
                write_field(sensor,f,"material",3)
                write_field(sensor,f,"frequency",3)
                write_field(sensor,f,"duration",3)
                write_field(sensor,f,"delay",3)
                write_field(sensor,f,"axis",3)
                write_field(sensor,f,"angle",3)
                write_field(sensor,f,"distance",3)
                write_field(sensor,f,"invert",3)
                write_field(sensor,f,"use_pulse",3)
                write_field(sensor,f,"use_pulse_false_level",3)
                write_field(sensor,f,"use_pulse_true_level",3)
                write_field(sensor,f,"use_tap",3)
                write_field(sensor,f,"axis_direction",3)
                write_field(sensor,f,"axis_number",3)
                write_field(sensor,f,"button_number",3)
                write_field(sensor,f,"event_type",3)
                write_field(sensor,f,"hat_direction",3)
                write_field(sensor,f,"hat_number",3)
                write_field(sensor,f,"joystick_index",3)
                write_field(sensor,f,"key",3)
                write_field(sensor,f,"modifier_key_1",3)
                write_field(sensor,f,"modifier_key_2",3)
                write_field(sensor,f,"log",3)
                write_field(sensor,f,"target",3)
                write_field(sensor,f,"mouse_event",3)
                write_field(sensor,f,"evaluation_type",3)
                write_field(sensor,f,"use_x_ray",3)
                write_field(sensor,f,"range",3)
                write_field(sensor,f,"use_level",3)
                write_field(sensor,f,"value",3)
                write_field(sensor,f,"value_min",3)
                write_field(sensor,f,"value_max",3)
                if hasattr(sensor,"states"):
                    write_state(sensor,f,sensor.states,"states",3)
                for controller in sensor.controllers:
                    f.write("\t\t\t<controller name=\"" + controller.name + "\"/>\n")
                f.write("\t\t</sensor>\n")
                
            for controller in o.game.controllers:
                f.write("\t\t<controller type=\"" + controller.type + "\" name=\"" + controller.name + "\">\n")
                write_field(controller,f,"states",3)
                write_field(controller,f,"expression",3)
                for actuator in controller.actuators:
                    f.write("\t\t\t<actuator name=\"" + actuator.name + "\"/>\n")
                f.write("\t\t</controller>\n")
                
            for actuator in o.game.actuators:
                f.write("\t\t<actuator type=\"" + actuator.type + "\" name=\"" + actuator.name + "\">\n")
                if hasattr(actuator,"states"):
                    write_state(actuator,f,actuator.states,"states",3)
                write_field(actuator,f,"body_message",3)
                write_field(actuator,f,"body_property",3)
                write_field(actuator,f,"body_type",3)
                write_field(actuator,f,"subject",3)
                write_field(actuator,f,"to_property",3)
                write_field(actuator,f,"operation",3)
                write_field(actuator,f,"angular_velocity",3)
                write_field(actuator,f,"mass",3)
                write_field(actuator,f,"mesh",3)
                write_field(actuator,f,"linear_velocity",3)
                write_field(actuator,f,"mode",3)
                write_field(actuator,f,"track_object",3)
                write_field(actuator,f,"time",3)
                write_field(actuator,f,"object",3)
                write_field(actuator,f,"object_property",3)
                write_field(actuator,f,"use_3d_tracking",3)
                write_field(actuator,f,"use_local_angular_velocity",3)
                write_field(actuator,f,"use_local_linear_velocity",3)
                write_field(actuator,f,"use_replace_display_mesh",3)
                write_field(actuator,f,"use_replace_physics_mesh",3)
                write_field(actuator,f,"axis",3)
                write_field(actuator,f,"damping",3)
                write_field(actuator,f,"height",3)
                write_field(actuator,f,"max",3)
                write_field(actuator,f,"min",3)
                write_field(actuator,f,"action",3)
                write_field(actuator,f,"apply_to_children",3)
                write_field(actuator,f,"blend_mode",3)
                write_field(actuator,f,"frame_blend_in",3)
                write_field(actuator,f,"frame_property",3)
                write_field(actuator,f,"frame_start",3)
                write_field(actuator,f,"frame_end",3)
                write_field(actuator,f,"layer",3)
                write_field(actuator,f,"layer_weight",3)
                write_field(actuator,f,"play_mode",3)
                write_field(actuator,f,"priority",3)
                write_field(actuator,f,"property",3)
                write_field(actuator,f,"use_additive",3)
                write_field(actuator,f,"use_continue_last_frame",3)
                write_field(actuator,f,"use_force",3)
                write_field(actuator,f,"use_local",3)
                write_field(actuator,f,"angle_max",3)
                write_field(actuator,f,"angle_min",3)
                write_field(actuator,f,"damping_rotation",3)
                write_field(actuator,f,"direction",3)
                write_field(actuator,f,"direction_axis",3)
                write_field(actuator,f,"direction_axis_pos",3)
                write_field(actuator,f,"fh_damping",3)
                write_field(actuator,f,"distance",3)
                write_field(actuator,f,"fh_force",3)
                write_field(actuator,f,"fh_height",3)
                write_field(actuator,f,"limit",3)
                write_field(actuator,f,"limit_max",3)
                write_field(actuator,f,"limit_min",3)
                write_field(actuator,f,"rotation_max",3)
                write_field(actuator,f,"use_fh_normal",3)
                write_field(actuator,f,"use_fh_paralel_axis",3)
                write_field(actuator,f,"use_material_detect",3)
                write_field(actuator,f,"use_normal",3)
                write_field(actuator,f,"use_persitent",3)
                write_field(actuator,f,"filename",3)
                write_field(actuator,f,"force",3)
                write_field(actuator,f,"force_max_x",3)
                write_field(actuator,f,"force_max_y",3)
                write_field(actuator,f,"derivate_coefficient",3)
                write_field(actuator,f,"force_max_z",3)
                write_field(actuator,f,"force_min_x",3)
                write_field(actuator,f,"force_min_y",3)
                write_field(actuator,f,"force_min_z",3)
                write_field(actuator,f,"integral_coefficient",3)
                write_field(actuator,f,"offset_location",3)
                write_field(actuator,f,"offset_rotation",3)
                write_field(actuator,f,"reference_object",3)
                write_field(actuator,f,"torque",3)
                write_field(actuator,f,"proportional_coefficient",3)
                write_field(actuator,f,"use_add_character_location",3)
                write_field(actuator,f,"use_character_jump",3)
                write_field(actuator,f,"use_add_linear_velocity",3)
                write_field(actuator,f,"use_local_linear_velocity",3)
                write_field(actuator,f,"use_local_location",3)
                write_field(actuator,f,"use_local_rotation",3)
                write_field(actuator,f,"use_local_torque",3)
                write_field(actuator,f,"use_servo_limit_x",3)
                write_field(actuator,f,"use_servo_limit_y",3)
                write_field(actuator,f,"use_servo_limit_z",3)
                write_field(actuator,f,"use_compound",3)
                write_field(actuator,f,"use_ghost",3)
                write_field(actuator,f,"value",3)
                write_field(actuator,f,"chance",3)
                write_field(actuator,f,"distribution",3)
                write_field(actuator,f,"float_max",3)
                write_field(actuator,f,"float_mean",3)
                write_field(actuator,f,"float_min",3)
                write_field(actuator,f,"float_value",3)
                write_field(actuator,f,"half_life_time",3)
                write_field(actuator,f,"int_max",3)
                write_field(actuator,f,"int_mean",3)
                write_field(actuator,f,"int_min",3)
                write_field(actuator,f,"int_value",3)
                write_field(actuator,f,"use_always_true",3)
                write_field(actuator,f,"seed",3)
                write_field(actuator,f,"camera",3)
                write_field(actuator,f,"scene",3)
                write_field(actuator,f,"acceleration",3)
                write_field(actuator,f,"facing",3)
                write_field(actuator,f,"facing_axis",3)
                write_field(actuator,f,"navmesh",3)
                write_field(actuator,f,"normal_up",3)
                write_field(actuator,f,"self_terminated",3)
                write_field(actuator,f,"show_visualization",3)
                write_field(actuator,f,"target",3)
                write_field(actuator,f,"turn_speed",3)
                write_field(actuator,f,"velocity",3)
                write_field(actuator,f,"cone_inner_angle_3d",3)
                write_field(actuator,f,"cone_outer_angle_3d",3)
                write_field(actuator,f,"cone_outer_gain_3d",3)
                write_field(actuator,f,"distance_3d_max",3)
                write_field(actuator,f,"distance_3d_reference",3)
                write_field(actuator,f,"gain_3d_max",3)
                write_field(actuator,f,"gain_3d_min",3)
                write_field(actuator,f,"sound",3)
                write_field(actuator,f,"pitch",3)
                write_field(actuator,f,"use_sound_3d",3)
                write_field(actuator,f,"rolloff_factor_3d",3)
                write_field(actuator,f,"use_visible",3)
                write_field(actuator,f,"use_occlusion",3)
                f.write("\t\t</actuator>\n")
            
            f.write("\t</object>\n")
    f.write("</game>")
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportBlenderData(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Game Engine Data"

    # ExportHelper mixin class uses this
    filename_ext = ".xml"

    filter_glob = StringProperty(
            default="*.xml",
            options={'HIDDEN'},
            )

    def execute(self, context):
        return write_some_data(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportBlenderData.bl_idname, text="Export Game Engine")


def register():
    bpy.utils.register_class(ExportBlenderData)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportBlenderData)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')
