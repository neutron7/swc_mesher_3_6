import math
import mathutils
import time

import bpy
from bpy.props import *
import bmesh
from bpy_extras.io_utils import ExportHelper
from rna_prop_ui import PropertyPanel
from os.path import basename

bl_info = {
    "name": "SWC Mesher",
    "author": "Bob Kuczewski, Oliver Ernst, Kadir Simsek",
    "version": (1, 0, 1),
    "blender": (3, 6, 0),
    "location": "View 3D > Edit Mode > Tool Shelf",
    "description": "Generate a Neuron Mesh from an SWC formatted file",
    "warning": "",
    "wiki_url": "http://salk.edu",
    "tracker_url": "",
    "category": "Add Mesh",
}

class MakeNeuronMeta_Panel(bpy.types.Panel):

    bl_label = "SWC Mesher"
    bl_idname = "PT_MAKE_NEURON_META"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SWC Mesher"

    @classmethod
    def poll(cls, context):
        return (context.scene is not None)

    def draw(self, context):
        layout = self.layout
        mnm = context.scene.make_neuron_meta
        mnm.draw(layout)

class MakeNeuronStick_Operator(bpy.types.Operator):
    bl_idname = "mnm.make_line_mesh"
    bl_label = "Make Cable Model from File"
    bl_description = "Generate a skeleton of line segments from the SWC file directly"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mnm = context.scene.make_neuron_meta
        mnm.build_neuron_stick_from_file(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        mnm = context.scene.make_neuron_meta
        mnm.build_neuron_stick_from_file(context)
        return {"FINISHED"}

class MakeEmptyStick_Operator(bpy.types.Operator):
    bl_idname = "mnm.make_new_cable"
    bl_label = "Make New Cable Model"
    bl_description = "Make a new cable model from scratch"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mnm = context.scene.make_neuron_meta
        mnm.make_new_cable_model(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        mnm = context.scene.make_neuron_meta
        mnm.make_new_cable_model(context)
        return {"FINISHED"}



#######################################################
#######################################################
# Operators to update a cable model from recent edits
#######################################################
#######################################################


# Class to update the cable model post editing it
class UpdateCablePostEdit_Operator(bpy.types.Operator):
    bl_idname = "mnm.update_cable_from_cable"
    bl_label = "Update Cable Model from Geometry"
    bl_description = "Update the internal cable model from the current geometry"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mnm = context.scene.make_neuron_meta
        mnm.check_duplicate_verts(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        mnm = context.scene.make_neuron_meta
        mnm.check_duplicate_verts(context)
        return {"FINISHED"}


#######################################################
#######################################################
# Operators to export SWC file
#######################################################
#######################################################


# Export a cable model to SWC file
class ExportCableModel_Operator(bpy.types.Operator, ExportHelper):
    bl_idname = "mnm.export_swc"
    bl_label = "Export Cable Model to SWC file"
    bl_description = "Generate an SWC file of segments from the skeleton"
    bl_options = {"REGISTER"}

    filename_ext = ".swc"  # allowed extensions

    def execute(self, context):

        # Check that an object is selected
        if context.active_object is None:
            raise TypeError("Please select the cable model to export.")

        # Export the SWC file
        context.scene.make_neuron_meta.export_cable_model(context, self.filepath)

        return {"FINISHED"}

    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#######################################################
#######################################################
# Operators to edit cable model spheres
#######################################################
#######################################################

# Class to make spheres
class MakeSpheres_Operator( bpy.types.Operator ):
	bl_idname = "mnm.make_spheres"
	bl_label = "Make Spheres for each Vertex"
	bl_description = "Generate a sphere at each vertex of the cable model"
	bl_options = {"REGISTER", "UNDO"}
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "objectmode"

	def execute ( self, context ):
		context.scene.make_neuron_meta.make_spheres_from_object ( context )
		return {"FINISHED"}

	def invoke ( self, context, event ):
		context.scene.make_neuron_meta.make_spheres_from_object ( context )
		return {"FINISHED"}

# Class to update the cable model from the sphere locations/radii
class UpdateCableFromSpheres_Operator( bpy.types.Operator ):
	bl_idname = "mnm.update_cable_from_spheres"
	bl_label = "Update Cable Model from Spheres"
	bl_description = "Update the cable model from sphere locations/radii"
	bl_options = {"REGISTER", "UNDO"}
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "objectmode"

	def execute ( self, context ):
		context.scene.make_neuron_meta.update_cable_model_from_spheres ( context )
		return {"FINISHED"}

	def invoke ( self, context, event ):
		context.scene.make_neuron_meta.update_cable_model_from_spheres ( context )
		return {"FINISHED"}

# Class to show all vertex spheres
class ShowVertexSpheres_Operator( bpy.types.Operator ):
	bl_idname = "mnm.show_spheres"
	bl_label = "Show"
	bl_description = "Show all vertex spheres"
	bl_options = {"REGISTER", "UNDO"}
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "objectmode"

	def execute ( self, context ):
		context.scene.make_neuron_meta.hide_vertex_spheres ( context, False )
		return {"FINISHED"}

	def invoke ( self, context, event ):
		context.scene.make_neuron_meta.hide_vertex_spheres ( context, False )
		return {"FINISHED"}

# Class to hide all vertex spheres
class HideVertexSpheres_Operator( bpy.types.Operator ):
	bl_idname = "mnm.hide_spheres"
	bl_label = "Hide"
	bl_description = "Hide all vertex spheres"
	bl_options = {"REGISTER", "UNDO"}
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "objectmode"

	def execute ( self, context ):
		context.scene.make_neuron_meta.hide_vertex_spheres ( context, True )
		return {"FINISHED"}

	def invoke ( self, context, event ):
		context.scene.make_neuron_meta.hide_vertex_spheres ( context, True )
		return {"FINISHED"}

# Class to show all vertex spheres
class DeleteAllVertexSpheres_Operator( bpy.types.Operator ):
	bl_idname = "mnm.delete_all_spheres"
	bl_label = "Delete All"
	bl_description = "Delete all vertex spheres"
	bl_options = {"REGISTER", "UNDO"}
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "objectmode"

	def execute ( self, context ):
		mnm = context.scene.make_neuron_meta
		mnm.delete_vertex_spheres ( context )
		return {"FINISHED"}

	def invoke ( self, context, event ):
		mnm = context.scene.make_neuron_meta
		mnm.delete_vertex_spheres ( context )
		return {"FINISHED"}


#######################################################
#######################################################
# Cable model list operators: draw/add/remove/etc cable models to edit
#######################################################
#######################################################

# Class to hold the cable model
class CableModelObject(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="", description="Cable Model Name")

    # Draw in list of objects
    def draw_item_in_row(self, row):
        col = row.column()
        col.label(text=str(self.name))

# Cable model object item to draw in the list
class SWCMesher_UL_object(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # The item will be a CableModelObject
        # Let it draw itself in a new row:
        item.draw_item_in_row(layout.row())

# Button to add cable model
class CableModelAdd(bpy.types.Operator):
    bl_idname = "mnm.cable_model_add"
    bl_label = "Add Cable Model"
    bl_description = "Add a cable model to edit"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.make_neuron_meta.cable_model_add_func(context)
        return {'FINISHED'}

# Button to remove cable model
class CableModelRemove(bpy.types.Operator):
    bl_idname = "mnm.cable_model_remove"
    bl_label = "Remove Cable Model"
    bl_description = "Remove a cable model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.make_neuron_meta.cable_model_remove_func(context)
        return {'FINISHED'}

# Button to remove all cable models
class CableModelRemoveAll(bpy.types.Operator):
    bl_idname = "mnm.cable_model_remove_all"
    bl_label = "Remove all Cable Models"
    bl_description = "Remove all cable models"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.make_neuron_meta.cable_model_remove_all_func(context)
        return {'FINISHED'}


#######################################################
#######################################################
# Operators to make surface mesh
#######################################################
#######################################################


class MakeNeuronFromFile_Operator(bpy.types.Operator):
    bl_idname = "mnm.make_neuron_from_file"
    bl_label = "Make Surface Mesh from File"
    bl_description = "Generate a surface mesh from the SWC file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mnm = context.scene.make_neuron_meta
        segments = mnm.read_segments_from_file()
        mnm.build_neuron_meta_from_segments(context, segments)
        return {"FINISHED"}

    def invoke(self, context, event):
        mnm = context.scene.make_neuron_meta
        segments = mnm.read_segments_from_file()
        mnm.build_neuron_meta_from_segments(context, segments)
        return {"FINISHED"}

class MakeNeuronFromData_Operator(bpy.types.Operator):
    bl_idname = "mnm.make_neuron_from_data"
    bl_label = "Make Surface Mesh from Cable Model"
    bl_description = "Generate a surface mesh from the current skeleton"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mnm = context.scene.make_neuron_meta
        segments = mnm.read_segments_from_object(context)
        mnm.build_neuron_meta_from_segments(context, segments)
        return {"FINISHED"}

    def invoke(self, context, event):
        mnm = context.scene.make_neuron_meta
        segments = mnm.read_segments_from_object(context)
        mnm.build_neuron_meta_from_segments(context, segments)
        return {"FINISHED"}

class MakeNeuronMetaAnalyze_Operator(bpy.types.Operator):
    bl_idname = "mnm.analyze_file"
    bl_label = "Analyze File"
    bl_description = "Read the file to determine numbers of segments, nodes, and various size ranges"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.make_neuron_meta.read_segments_from_file()
        return {"FINISHED"}

    def invoke(self, context, event):
        context.scene.make_neuron_meta.read_segments_from_file()
        return {"FINISHED"}

def file_name_change(self, context):
    context.scene.make_neuron_meta.file_name_change()


#######################################################
#######################################################
# Main GUI property group
#######################################################
#######################################################

class MakeNeuronMetaPropGroup(bpy.types.PropertyGroup):
    neuron_file_name: bpy.props.StringProperty(subtype='FILE_PATH', default="", update=file_name_change)
    neuron_file_data: bpy.props.StringProperty(default="")

    convert_to_mesh: bpy.props.BoolProperty(name="Convert to Mesh", default=False)
    show_analysis: bpy.props.BoolProperty(default=False)
    show_stick: bpy.props.BoolProperty(default=False)
    file_analyzed: bpy.props.BoolProperty(default=False)
    num_lines_in_file: bpy.props.IntProperty(default=-1)
    num_segments_in_file: bpy.props.IntProperty(default=-1)
    num_nodes_in_file: bpy.props.IntProperty(default=-1)
    largest_radius_in_file: bpy.props.FloatProperty(default=-1)
    smallest_radius_in_file: bpy.props.FloatProperty(default=-1)
    min_x: bpy.props.FloatProperty(default=-1)
    max_x: bpy.props.FloatProperty(default=-1)
    min_y: bpy.props.FloatProperty(default=-1)
    max_y: bpy.props.FloatProperty(default=-1)
    min_z: bpy.props.FloatProperty(default=-1)
    max_z: bpy.props.FloatProperty(default=-1)

    scale_file_data: bpy.props.FloatProperty(default=1.0, precision=4, description="Scale factor applied to data read from a file")
    meta_ball_scale_factor: bpy.props.FloatProperty(default=1.0, precision=4, description="Scale factor applied to mesh radius")

    mesh_resolution: bpy.props.FloatProperty(default=0.1, precision=4, description="Intended resolution of the final mesh")
    min_forced_radius: bpy.props.FloatProperty(default=0.0, precision=4, description="Smallest radius allowed in all segments (smaller forced up to this radius)")
    num_segs_limit: bpy.props.IntProperty(default=0, description="Only generate this number of segments (useful for testing settings in large neurons)")

    new_sphere_radius: bpy.props.FloatProperty(default=1, description="Radius of new vertex spheres")

    # List of Cable Models
    cable_model_list: bpy.props.CollectionProperty(type=CableModelObject)
    active_object_index: bpy.props.IntProperty(name="Active Object Index", default=0)


    def draw(self, layout):
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'


        ###
		# Load, analyze and create a cable model from an SWC file
		###

        if not self.show_analysis:
            row.prop(self, "show_analysis", icon='TRIA_RIGHT_BAR', text="Import Cable Model from SWC File", emboss=False)
        else:
            row.prop(self, "show_analysis", icon='TRIA_DOWN_BAR', text="Import Cable Model from SWC File", emboss=False)

            row = box.row()
            row.prop(self, "neuron_file_name", text="")

            row = box.row()
            row.operator("mnm.analyze_file")

            row = box.row()
            row.operator("mnm.make_line_mesh")

            if self.file_analyzed:
                row = box.row()
                box = row.box()
                row = box.row()
                row.label(text="File contains " + str(self.num_lines_in_file) + " lines.")
                row = box.row()
                row.label(text="File contains " + str(self.num_segments_in_file) + " segments.")
                row = box.row()
                row.label(text="File contains " + str(self.num_nodes_in_file) + " nodes.")
                row = box.row()
                row.label(text="Largest radius is %g" % self.largest_radius_in_file)
                row = box.row()
                row.label(text="Smallest radius is %g" % self.smallest_radius_in_file)
                row = box.row()
                row.label(text="X range: %g to %g" % (self.min_x, self.max_x))
                row = box.row()
                row.label(text="Y range: %g to %g" % (self.min_y, self.max_y))
                row = box.row()
                row.label(text="Z range: %g to %g" % (self.min_z, self.max_z))

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'

        ###
		# Edit cable models and make surface mesh
		###


        if not self.show_stick:
            row.prop(self, "show_stick", icon='TRIA_RIGHT_BAR', text="Edit Cable Model", emboss=False)
        else:
            row.prop(self, "show_stick", icon='TRIA_DOWN_BAR', text="Edit Cable Model", emboss=False)

            ###
            # Cable model chooser
            ###

            row = box.row()
            row.label(text="List of Cable Models", icon='CURVE_DATA')

            row = box.row()
            row.operator("mnm.make_new_cable")

            row = box.row()
            col = row.column()

            col.template_list("SWCMesher_UL_object", "",
                            self, "cable_model_list",
                            self, "active_object_index",
                            rows=1)

            col = row.column(align=True)
            col.operator("mnm.cable_model_add", icon='ZOOM_IN', text="")
            col.operator("mnm.cable_model_remove", icon='ZOOM_OUT', text="")
            col.operator("mnm.cable_model_remove_all", icon='X', text="")

            ###
            # Edit the cable model
            ###

            row = box.row()
            row.label(text="Edit Selected Cable Model", icon='GREASEPENCIL')

            row = box.row()
            subbox = row.box()

            # Apply edits to cable model

            split = subbox.split()
            col = split.column(align=True)
            col.label(text="After editing the geometry:")
            col.operator("mnm.update_cable_from_cable")


            # Make spheres

            row = subbox.row()
            split = subbox.split()
            col = split.column(align=True)
            col.label(text="To edit the radii:")
            subrow = col.row()
            subrow.operator("mnm.make_spheres")
            subrow.prop(self, "new_sphere_radius", text="New Sphere Radius")
            rw = col.row()
            rw.operator("mnm.show_spheres")
            rw.operator("mnm.hide_spheres")
            rw.operator("mnm.delete_all_spheres")
            col.label(text="After editing the radii:")
            col.operator("mnm.update_cable_from_spheres")

            row = box.row()
            row.operator("mnm.export_swc")

            ###
            # Extrapolate surface mesh from cable model
            ###

            row = box.row()
            row.label(text="Extrapolate Surface Mesh", icon='SURFACE_NCYLINDER')

            row = box.row()
            subbox = row.box()

            row = subbox.row()
            row.prop(self, "scale_file_data", text="Scale File Factor")
            row = subbox.row()
            row.prop(self, "meta_ball_scale_factor", text="Scale Radius Factor")
            row = subbox.row()
            row.prop(self, "mesh_resolution", text="Resolution of the Final Mesh")
            row = subbox.row()
            row.prop(self, "min_forced_radius", text="Minimum Forced Radius")
            row = subbox.row()
            row.prop(self, "num_segs_limit", text="Limit Number of Segments")
            row = subbox.row()
            row.operator("mnm.make_neuron_from_file")
            row.operator("mnm.make_neuron_from_data")

    ###
	# Function to make a new cable model from scratch
	###

    def make_new_cable_model(self, context):
        # Get the current cursor location
        cursor_loc = context.scene.cursor.location

        # New vertex locations
        v1 = (cursor_loc[0] - 2.0, cursor_loc[1], cursor_loc[2])
        v2 = (cursor_loc[0] + 2.0, cursor_loc[1], cursor_loc[2])
        vs = [v1, v2]

        # Connecting line
        ls = [(0, 1)]

        # Make new mesh
        new_mesh = bpy.data.meshes.new("cable_model_mesh")
        new_mesh.from_pydata(vs, ls, [])
        new_mesh.update()
        new_obj = bpy.data.objects.new("cable_model_mesh", new_mesh)
        context.collection.objects.link(new_obj)

        # Add metadata
        mesh = new_obj.data
        index_number_layer = mesh.vertex_layers_float.new(name="index_number")
        parent_index_layer = mesh.vertex_layers_float.new(name="parent_index")
        segment_type_layer = mesh.vertex_layers_float.new(name="segment_type")
        radius_layer = mesh.vertex_layers_float.new(name="radius")

        # Indexes
        index_number_layer.data[0].value = 1
        index_number_layer.data[1].value = 2

        # Parents
        parent_index_layer.data[0].value = -1
        parent_index_layer.data[1].value = 1

        # Radii
        radius_layer.data[0].value = -1.0
        radius_layer.data[1].value = -1.0

        # Segment type - just make it a dendrite
        segment_type_layer.data[0].value = 3
        segment_type_layer.data[1].value = 3

        # Finally, add the new cable model to the list of cable models to edit

        # Deselect all objects currently selected
        bpy.ops.object.select_all(action='DESELECT')

        # Select the new obj and make it active
        new_obj.select_set(True)
        context.view_layer.objects.active = new_obj

        # Add to the list
        self.cable_model_add_func(context)

	#####
	# Functions to add/remove cable models from the list of cable models to edit
	#####

    # Add a cable model to the list
    def cable_model_add_func(self, context):
        print("Adding cable model to the list")

        # Get the active object
        obj_list = bpy.context.selected_objects
        if len(obj_list) > 0:
            for obj in obj_list:
                # Check that the object has the required layers
                lrs = obj.data.vertex_layers_float
                if not ('index_number' in lrs and 'parent_index' in lrs and 'segment_type' in lrs and 'radius' in lrs):
                    raise TypeError("Object: " + str(obj.name) + " is not a cable model (does not have the correct vertex_layers_float). Select a different object, or re-import the cable from the SWC file.")

                # Check by name if the object is already in the list
                current_object_names = [d.name for d in self.cable_model_list]
                if obj.name not in current_object_names:
                    new_obj = self.cable_model_list.add()
                    new_obj.name = obj.name

    # Remove a cable model 
    def cable_model_remove_func(self, context):
        print("Removing cable model from the list")

        if len(self.cable_model_list) > 0:
            self.cable_model_list.remove(self.active_object_index)
            if self.active_object_index > 0:
                self.active_object_index -= 1

    # Remove all cable models
    def cable_model_remove_all_func(self, context):
        print("Removing all cable models")

        while len(self.cable_model_list) > 0:
            self.cable_model_list.remove(0)
        self.active_object_index = 0


	###
	# Functions to edit the cable model
	###

    # Check that there are no duplicate vertices in the cable model (based on their id)
    def check_duplicate_verts(self, context):

        # Try to get the object
        if not len(self.cable_model_list) > 0:
            raise TypeError("List of cable models to edit is empty.")

        # Get the object
        ob = bpy.data.objects[(self.cable_model_list[self.active_object_index]).name]

        # Get the idxs
        index_number_layer = ob.data.vertex_layers_float['index_number']
        n_v = len(ob.data.vertices)
        idx_vals = [index_number_layer.data[i].value for i in range(0, n_v)]

        # Check against duplicates
        if len(idx_vals) != len(set(idx_vals)) or len(idx_vals) != max(idx_vals) or n_v != len(idx_vals) or n_v != max(idx_vals):
            # Duplicates exist OR deletion has occurred
            self.update_cable_model_post_edit(context)

        # No duplicates
        return
    
    	# Update cable model post extrusion/deletion
    def update_cable_model_post_edit(self, context):
        print("Updating cable model post editing.")

        # Try to get the object
        if not len(self.cable_model_list) > 0:
            raise TypeError("List of cable models to edit is empty.")

        # Get the object
        ob_name = (self.cable_model_list[self.active_object_index]).name
        ob = bpy.data.objects[ob_name]

        # Get the parent layer
        parent_index_layer = ob.data.vertex_layers_float['parent_index']

        # Get a list of all edge's vertex id pairs
        edge_vert_pair_list = [list(edge.vertices) for edge in ob.data.edges]

        # Get the idxs
        index_number_layer = ob.data.vertex_layers_float['index_number']

        # We need to start somewhere - pick any vertex to index number 1
        # Reassign the vertex i_start=0 to have index 1
        i_start = 0
        index_number_layer.data[i_start].value = 1

        # Number of vertices
        n_v = len(ob.data.vertices)

        # All vertices to check
        verts_check = [i_start]

        # Vertices we have already checked
        verts_done = []

        # Id dict from i in the object's vertex list to idx in the SWC file
        i_idx_dict = {}
        i_idx_dict[i_start] = 1

        # Current index number to assign
        idx_assign = 2

        # Go through all vertices
        while len(verts_check) > 0:

            # The vertex to check
            i_check = verts_check[0]
            idx_check = i_idx_dict[i_check]

            # Find all connecting edges
            i_conns = []
            for vs in edge_vert_pair_list:
                if vs[0] == i_check and not vs[1] in verts_done:
                    i_conns.append(vs[1])
                    verts_check.append(vs[1])
                elif vs[1] == i_check and not vs[0] in verts_done:
                    i_conns.append(vs[0])
                    verts_check.append(vs[0])

            # If there are any connecting vertices, store their index numbers and parent
            for i_conn in i_conns:
                # New index
                index_number_layer.data[i_conn].value = float(idx_assign)
                i_idx_dict[i_conn] = idx_assign
                idx_assign += 1

                # Get parent
                parent_index_layer.data[i_conn].value = float(idx_check)

            # Add to verts_done to ensure no repetition
            verts_done.append(i_check)

            # Delete this vertex to check
            del verts_check[0]

        # Delete all other data in the float layers, if any exists
        radius_layer = ob.data.vertex_layers_float['radius']
        n_v_new = len(i_idx_dict)
        for i_v in range(n_v_new, n_v):
            if i_v in index_number_layer.data:
                del index_number_layer.data[i_v]
            if i_v in parent_index_layer.data:
                del parent_index_layer.data[i_v]
            if i_v in radius_layer.data:
                del radius_layer.data[i_v]

        # Do spheres already exist
        v_name = "%0" + str(len(str(n_v))) + "d"
        sphere_name = (ob_name + "_vertex_" + v_name) % 1
        if not bpy.data.objects.get(sphere_name) is None:
            # Delete and remake all the spheres, since names changed
            self.delete_vertex_spheres(context)
            self.make_spheres_from_object(context)

            # POSSIBLE TO-DO HERE: PRESERVE THE RADIUS OF EXISTING SPHERES
            # Grab their radii, and upload onto the new spheres



    # Add spheres to the cable model for visualizing the vertices
    def make_spheres_from_object(self, context):
        # Try to get the object
        if not len(self.cable_model_list) > 0:
            raise TypeError("List of cable models to edit is empty.")

        # Get the object
        ob_name = (self.cable_model_list[self.active_object_index]).name
        ob = bpy.data.objects[ob_name]

        # Ensure that the object is ok post any extrusion/deletion of vertices that may have occured
        self.check_duplicate_verts(context)

        # Radius layer
        radius_layer = ob.data.vertex_layers_float["radius"]

        # Id layer
        index_number_layer = ob.data.vertex_layers_float["index_number"]

        # Get the number of vertices (for naming purposes)
        n_v = len(ob.data.vertices)
        v_name = "%0" + str(len(str(n_v))) + "d"

        # Get the transformation matrix of the object
        mat = ob.matrix_world

        # Go through each vertex
        for i_v, v in enumerate(ob.data.vertices):

            # Get the pos
            loc = v.co
            # Get the radius
            r = radius_layer.data[i_v].value
            if r < 0:
                r = self.new_sphere_radius
            # Get the id
            idx = int(index_number_layer.data[i_v].value)

            # Make a sphere
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=16,
                ring_count=8,
                size=r,
                enter_editmode=False,
                location=tuple(mat @ loc)  # Changed * to @ for matrix multiplication
            )

            # Get the new object
            new_ob = context.active_object

            # Rename it appropriately
            new_ob.name = (ob_name + "_vertex_" + v_name) % idx

    # Update the cable model based on the sphere locations
    def update_cable_model_from_spheres(self, context):
        # Try to get the object
        if not len(self.cable_model_list) > 0:
            raise TypeError("List of cable models to edit is empty.")

        # Get the object
        ob_name = (self.cable_model_list[self.active_object_index]).name
        ob = bpy.data.objects[ob_name]

        # Get the inverse matrix world
        mat_inv = ob.matrix_world.inverted()

        # Get the number of vertices (for naming purposes)
        n_v = len(ob.data.vertices)
        v_name = "%0" + str(len(str(n_v))) + "d"

        # New positions, radii of the vertices
        new_pos_dict = {}
        new_r_dict = {}

        # Go through all the vertices
        for i_v in range(1, n_v + 1):

            # Vertex sphere name
            sphere_name = (ob_name + "_vertex_" + v_name) % i_v

            # Get the sphere object
            if bpy.data.objects.get(sphere_name) is None:
                # Couldn't get the object; stop
                break

            # Get the object
            ob_sphere = bpy.data.objects[sphere_name]

            # Calculate its radius
            dim = ob_sphere.dimensions
            r = sum([0.5 * dim[i] for i in [0, 1, 2]]) / 3.0

            # Store
            new_pos_dict[i_v] = mat_inv @ ob_sphere.location  # Changed * to @ for matrix multiplication
            new_r_dict[i_v] = r

        # Update the vertex data on the cable model

        # Radius layer
        radius_layer = ob.data.vertex_layers_float["radius"]

        # Id layer
        index_number_layer = ob.data.vertex_layers_float["index_number"]

        # Go through all the vertices
        for i_v, v in enumerate(ob.data.vertices):

            # Get the index
            idx = int(index_number_layer.data[i_v].value)

            # Update the position
            v.co = mathutils.Vector(new_pos_dict[idx])

            # Update the radius - FOR WHATEVER REASON, WE ACTUALLY STORE TWICE THE RADIUS HERE
            radius_layer.data[i_v].value = new_r_dict[idx]



    # Export a cable model to an SWC file
    def export_cable_model(self, context, fpath):
        # Construct the file to open
        if not fpath.endswith(".swc"):
            fpath += ".swc"

        # Write things
        file_lines = self.get_swc_from_mesh_stick(context)
        if file_lines is None:
            print("Unable to save file")
        else:
            with open(fpath, "w") as f:
                for line in file_lines:
                    f.write(line + "\n")


    # Show/Hide all vertex spheres
    def hide_vertex_spheres(self, context, flag):
        # Try to get the object
        if not len(self.cable_model_list) > 0:
            raise TypeError("List of cable models to edit is empty.")

        # Get the object
        ob_name = (self.cable_model_list[self.active_object_index]).name
        ob = bpy.data.objects[ob_name]

        # Go through all objects
        lo = len(ob_name)
        for ob_vertex in bpy.data.objects:
            if len(ob_vertex.name) >= 7 + lo and ob_vertex.name[0:(7 + lo)] == ob_name + "_vertex":
                ob_vertex.hide = flag

    # Delete all vertex spheres
    def delete_vertex_spheres(self, context):

        # Try to get the object
        if not len(self.cable_model_list) > 0:
            raise TypeError("List of cable models to edit is empty.")

        # Get the object
        ob_name = (self.cable_model_list[self.active_object_index]).name
        ob = bpy.data.objects[ob_name]

        # Ensure there is (any) current active object
        ob_active = context.scene.objects.active
        print(ob_active)
        if ob_active is None:
            # Set the active object to the first one in the list
            vals = bpy.data.objects.values()
            context.scene.objects.active = vals[0]
            vals[0].hide = False
            vals[0].select = True
        else:
            # Ensure it is also visible and selected
            ob_active.hide = False
            ob_active.select = True

        # Ensure object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Current selection, and ensure everything is DE-selected
        ob_sel_list = []
        for ob_select in bpy.data.objects:
            if ob_select.select == True:
                ob_sel_list.append(ob_select.name)
                # Deselect the object
                ob_select.select = False

        # Go through all objects and delete
        lo = len(ob_name)
        for ob_delete in bpy.data.objects:
            if len(ob_delete.name) >= 7+lo and ob_delete.name[0:(7+lo)] == ob_name + "_vertex":
                ob_delete.hide = False
                ob_delete.select = True
                bpy.ops.object.delete()

        # Reselect the previously selected objects
        for ob_select in bpy.data.objects:
            if ob_select.name in ob_sel_list:
                ob_select.select = True


    ###
	# Functions to make the surface mesh
	###

    def file_name_change ( self ):
        self.read_segments_from_file()
        # self.file_analyzed = True

    def read_segments_from_object(self, context):
        # Read in the data
        segments = []

        # Read from the selected cable model in the list

        # Try to get the object
        if not len(self.cable_model_list) > 0:
            raise TypeError("List of cable models to edit is empty.")

        # Get the object
        obj_name = (self.cable_model_list[self.active_object_index]).name
        obj = bpy.data.objects[obj_name]

        # Make sure it's active and selected
        context.view_layer.objects.active = obj
        obj.select_set(True)

        mesh = obj.data
        verts = mesh.vertices
        print("Mesh has " + str(len(verts)) + " verts")

        index_number_layer = mesh.vertex_layers_float['index_number']
        parent_index_layer = mesh.vertex_layers_float['parent_index']
        segment_type_layer = mesh.vertex_layers_float['segment_type']
        radius_layer = mesh.vertex_layers_float['radius']

        self.num_nodes_in_file = 0
        num_total_segments = 0

        # Start by putting all points into a dictionary keyed by their label n
        point_dict = {}
        i = 0
        for v in verts:
            n = int(index_number_layer.data[i].value)
            T = int(segment_type_layer.data[i].value)
            x = v.co.x
            y = v.co.y
            z = v.co.z
            R = radius_layer.data[i].value
            if R < 0:
                R = self.new_sphere_radius
            P = int(parent_index_layer.data[i].value)

            fields = [str(int(n)), str(int(T)), str(x), str(y), str(z), str(R), str(int(P))]
            print("  Fields from " + obj.name + " = " + str(fields))
            point_dict[fields[0]] = fields
            i += 1

        sorted_int_keys = sorted([int(k) for k in point_dict.keys()])
        point_keys = [str(k) for k in sorted_int_keys]
        self.num_lines_in_file = len(point_keys)
        self.num_nodes_in_file = len(point_keys)

        # Next, create the list of segments - one for each child that has a parent
        for k in point_keys:
            child_fields = point_dict[k]
            print("  Sorted Fields from " + obj.name + " = " + str(child_fields))
            if child_fields[6] in point_keys:
                # This point has a parent, so make a segment from parent to child
                parent_fields = point_dict[child_fields[6]]
                px = float(parent_fields[2])
                py = float(parent_fields[3])
                pz = float(parent_fields[4])
                pr = float(parent_fields[5])
                cx = float(child_fields[2])
                cy = float(child_fields[3])
                cz = float(child_fields[4])
                cr = float(child_fields[5])
                segments.append([[px, py, pz, pr], [cx, cy, cz, cr]])
                num_total_segments += 1

        if self.num_segs_limit > 0:
            # Limit the number of segments
            segments = segments[:self.num_segs_limit]
            num_total_segments = len(segments)

        self.num_segments_in_file = num_total_segments

        self.perform_analysis(segments)

        return segments


    def read_segments_from_file(self):
        # Read in the data
        segments = []
        
        print("Reading from file " + self.neuron_file_name)

        self.num_nodes_in_file = 0
        num_total_segments = 0

        if (self.neuron_file_name[-4:] == ".nbf"):
			# Read Node Branch Format
			# Node Branch Format has explicit connections, but they're not needed with metaballs
            # Read Node Branch Format
            segment = []
            f = open(self.neuron_file_name, 'r')
            lines = f.readlines()
            self.num_lines_in_file = len(lines)
            for l in lines:
                l = l.strip()
                if len(l) > 0:
                    if l[0:6] == "Branch":
                        if len(segment) > 0:
                            segments = segments + [segment]
                            segment = []
                            num_total_segments += 1
                    if l[0:4] == "Node":
                        values = l.split()[1:]
                        segment = segment + [values]
                        self.num_nodes_in_file += 1
            if len(segment) > 0:
                segments = segments + [segment]
                segment = []
                num_total_segments += 1

        elif (self.neuron_file_name[-4:] == ".swc") or (self.neuron_file_name[-8:] == ".swc.txt"):
            # Read SWC Format
            # SWC format has explicit connections, but they're not needed with metaballs
            """
            The format of an SWC file is fairly simple. It is a text file consisting of 
            a header with various fields beginning with a # character, 
            and a series of three dimensional points containing 
            an index, radius, type, and connectivity information. 
            The lines in the text file representing points have the following layout.

                        n T x y z R P

                        n is an integer label that identifies the current point and 
                                increments by one from one line to the next.

                        T is an integer representing the type of neuronal segment, 
                                such as soma, axon, apical dendrite, etc. The standard 
                                accepted integer values are given below.

                                0 = undefined
                                1 = soma
                                2 = axon
                                3 = dendrite
                                4 = apical dendrite
                                5 = fork point
                                6 = end point
                                7 = custom

                        x, y, z gives the cartesian coordinates of each node.

                        R is the radius at that node.
                        P indicates the parent (the integer label) of the current 
                                point or -1 to indicate an origin (soma).
            """
            # Note that the SWC format could define cyclic references,
            #   However, since we just need to generate segments, this is not a problem.
            #   This is done by making each segment only one line (from parent to child)

            # Start by reading all the points into a dictionary keyed by their label n
            f = open ( self.neuron_file_name, 'r' )
            lines = f.readlines()
            point_dict = {}
            for l in lines:
                l = l.strip()
                print ( "Line: " + l )
                if len(l) > 0:
                    if l[0] != "#":
                        fields = l.split()
                        point_dict[fields[0]] = fields
            point_keys = sorted ( [ k for k in point_dict.keys() ] )
            self.num_lines_in_file = len(point_keys)
            self.num_nodes_in_file = len(point_keys)

            # Next create the list of segments - one for each child that has a parent
            for k in point_keys:
                child_fields = point_dict[k]
                if child_fields[6] in point_keys:
                    # This point has a parent, so make a segment from parent to child
                    parent_fields = point_dict[child_fields[6]]
                    px = float(parent_fields[2])
                    py = float(parent_fields[3])
                    pz = float(parent_fields[4])
                    pr = float(parent_fields[5])
                    cx = float(child_fields[2])
                    cy = float(child_fields[3])
                    cz = float(child_fields[4])
                    cr = float(child_fields[5])
                    segments = segments + [ [ [px, py, pz, pr], [cx, cy, cz, cr] ] ]
                    num_total_segments += 1

        else:
            # Read the legacy format found from early work with Neuron
            f = open ( self.neuron_file_name, 'r' )
            lines = f.readlines()
            self.num_lines_in_file = len(lines)
            num_entries_to_read = 0
            segment = []
            for l in lines:
                print ( "Line: " + l.strip() )
                if len(l.strip()) > 0:
                    # This is a real line
                    if num_entries_to_read == 0:
                        # Look for a line containing a 1 and the number of fields
                        fields = l.strip().split()
                        if len(fields) != 2:
                            print ( "Error: expected 2 values" )
                        else:
                            if int(fields[0]) != 1:
                                print ( "Unexpected first value for line" + l )
                            num_entries_to_read = int(fields[1])
                            print ( "Read " + str(num_entries_to_read) )
                            if len(segment) > 0:
                                segments = segments + [ segment ]
                                segment = []
                                num_total_segments += 1
                    else:
                        # This is another entry in the current segment
                        values = l.strip().split()
                        segment = segment + [ values ]
                        num_entries_to_read += -1
                        self.num_nodes_in_file += 1
                                                
            if len(segment) > 0:
                # Be sure to save the last segment
                segments = segments + [ segment ]
                num_total_segments += 1

        if self.num_segs_limit > 0:
            # Limit the number of segments
            segments = segments[0:self.num_segs_limit]
            num_total_segments = len(segments)

        self.num_segments_in_file = num_total_segments

        self.perform_analysis(segments)

        return segments

    
    def perform_analysis(self, segments):
        # Find the smallest radius

        seg_num = 1
        obj_name = None
        first_pass = True
        self.largest_radius_in_file = -1
        self.smallest_radius_in_file = -1
        self.min_x = self.max_x = self.min_y = self.max_y = self.min_z = self.max_z = -1
        for seg in segments:
            print("=== Finding bounds and smallest radius for segment " + str(seg_num) + " ===")
            seg_num += 1
            lc = None
            cap1 = True
            for c in seg:
                x = float(c[0])
                y = float(c[1])
                z = float(c[2])
                r = float(c[3])
                if first_pass or (r > self.largest_radius_in_file):
                    self.largest_radius_in_file = r
                if first_pass or (r < self.smallest_radius_in_file):
                    self.smallest_radius_in_file = r
                if first_pass or (x < self.min_x):
                    self.min_x = x
                if first_pass or (x > self.max_x):
                    self.max_x = x
                if first_pass or (y < self.min_y):
                    self.min_y = y
                if first_pass or (y > self.max_y):
                    self.max_y = y
                if first_pass or (z < self.min_z):
                    self.min_z = z
                if first_pass or (z > self.max_z):
                    self.max_z = z
                first_pass = False

        print("X range: %g to %g" % (self.min_x, self.max_x))
        print("Y range: %g to %g" % (self.min_y, self.max_y))
        print("Z range: %g to %g" % (self.min_z, self.max_z))
        print("Largest radius = " + str(self.largest_radius_in_file))
        print("Smallest radius = " + str(self.smallest_radius_in_file))

        self.file_analyzed = True


    # Convert the current stick mesh into an swc format file

    def get_swc_from_mesh_stick(self, context):
        # Check that each id is assigned to only one vertex
        self.check_duplicate_verts(context)

        # Store the SWC lines
        lines = []
        lines.append("# n T x y z R P")

        # Try to get the object
        if not len(self.cable_model_list) > 0:
            raise TypeError("List of cable models to edit is empty.")

        # Get the object, vertices
        ob_name = (self.cable_model_list[self.active_object_index]).name
        ob = bpy.data.objects[ob_name]
        vs = ob.data.vertices

        # Get the matrix world
        mat = ob.matrix_world

        # Get the data stored on the vertices
        radius_layer = ob.data.vertex_layers_float["radius"]
        index_number_layer = ob.data.vertex_layers_float["index_number"]
        parent_index_layer = ob.data.vertex_layers_float['parent_index']
        segment_type_layer = ob.data.vertex_layers_float['segment_type']

        # Index values
        n_idx = len(vs)
        id_value_list = [int(index_number_layer.data[i].value) for i in range(0, n_idx)]

        # Write all vertices
        idx = 1
        while idx < len(id_value_list) + 1:
            i_v = id_value_list.index(idx)
            co = mat * vs[i_v].co
            radius_from_layer = radius_layer.data[i_v].value
            if radius_from_layer < 0:
                radius_from_layer = self.new_sphere_radius
            if idx == 1:
                lines.append("1 " + str(int(segment_type_layer.data[i_v].value)) + " " + str(co.x) + " " + str(co.y) + " " + str(co.z) + " " + str(radius_from_layer) + " -1")
            else:
                lines.append(
                    str(idx) + " " + str(int(segment_type_layer.data[i_v].value)) + " " + str(co.x) + " " + str(
                        co.y) + " " + str(co.z) + " " + str(radius_from_layer) + " " + str(
                        int(parent_index_layer.data[i_v].value)))
            idx += 1

        return lines

    def build_neuron_stick_from_file(self, context):
        # Read once with standard code to update the display
        segments = self.read_segments_from_file()

        if (len(self.neuron_file_name) > 4 and self.neuron_file_name[-4:] == ".swc") or (len(self.neuron_file_name) > 8 and self.neuron_file_name[-8:] == ".swc.txt"):
            # Read again to get all the data needed for a stick figure

            # Base filename
            if self.neuron_file_name[-4:] == ".swc":
                swc_fname = basename(self.neuron_file_name)[:-4]
            else:
                swc_fname = basename(self.neuron_file_name)[:-8]

            # Start by reading all the points into a dictionary keyed by their label n

            f = open(self.neuron_file_name, 'r')
            file_lines = f.readlines();
            point_dict = {}
            point_keys = []
            point_num = 0
            for l in file_lines:
                l = l.strip()
                print("Line: " + l)
                if len(l) > 0:
                    if l[0] != "#":
                        fields = l.split() + [str(point_num)]
                        point_dict[fields[0]] = fields
                        point_keys.append(fields[0])
                        point_num += 1
            self.num_lines_in_file = len(point_keys)
            self.num_nodes_in_file = len(point_keys)

            # Build the Blender mesh starting with the vertices

            print("Making the verts:")

            verts = []
            for k in point_keys:
                p = point_dict[k]
                print(str(p))
                px = float(p[2])
                py = float(p[3])
                pz = float(p[4])
                verts.append([px, py, pz])

            print("Making the lines:")

            lines = []
            for k in point_keys:
                p = point_dict[k]
                print(str(p))
                ppkey = p[6]
                if int(ppkey) >= 0:
                    # This point has a parent, so make a line segment
                    pp = point_dict[ppkey]
                    lines.append([int(pp[7]), int(p[7])])

            print("Making the mesh:")

            new_mesh = bpy.data.meshes.new(swc_fname + "_mesh")
            new_mesh.from_pydata(verts, lines, [])
            new_mesh.update()
            new_obj = bpy.data.objects.new(swc_fname + "_cable_model", new_mesh)
            context.scene.collection.objects.link(new_obj)

            print("Adding the metadata to each vertex:")

            mesh = new_obj.data
            index_number_layer = mesh.vertex_layers_float.new(name="index_number")
            parent_index_layer = mesh.vertex_layers_float.new(name="parent_index")
            segment_type_layer = mesh.vertex_layers_float.new(name="segment_type")
            radius_layer = mesh.vertex_layers_float.new(name="radius")

            vert_index = 0
            for k in point_keys:
                p = point_dict[k]
                print("Adding metadata from " + str(p))
                index_number_layer.data[vert_index].value = int(p[0])
                parent_index_layer.data[vert_index].value = int(p[6])
                segment_type_layer.data[vert_index].value = int(p[1])
                radius_layer.data[vert_index].value = float(p[5])
                vert_index += 1

            # Finally, add the new cable model to the list of cable models to edit
            self.cable_model_list.add().name = new_obj.name

            # Deselect all objects currently selected
            bpy.ops.object.select_all(action='DESELECT')

            # Select the new obj and make it active
            new_obj.select_set(True)
            context.view_layer.objects.active = new_obj

            # Switch to Edit Mode
            bpy.ops.object.mode_set(mode='EDIT')

            # Select all vertices
            bpy.ops.mesh.select_all(action='SELECT')

            # Switch back to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Update the context to reflect changes
            bpy.context.view_layer.update()

            # Notify the user
            # self.report({'INFO'}, "Neuron stick figure created from file.")

    def build_neuron_meta_from_segments(self, context, segments):
        # Create the object to hold the metaballs
        scene = bpy.context.scene
        mball = bpy.data.metaballs.new('neuron')
        obj = bpy.data.objects.new('Neuron', mball)
        scene.collection.objects.link(obj)
        mball.resolution = self.mesh_resolution
        mball.render_resolution = self.mesh_resolution

        # Generate the metashape segments from the branch segments
        seg_num = 1
        obj_name = None
        for seg in segments:
            print("=== Building Branch " + str(seg_num) + " ===")
            seg_num += 1
            lc = None
            for c in seg:
                if lc is not None:

                    print("Building segment with radius of " + str(lc[3]) + " and " + str(c[3]))

                    x1 = float(lc[0]) * self.scale_file_data
                    y1 = float(lc[1]) * self.scale_file_data
                    z1 = float(lc[2]) * self.scale_file_data
                    r1 = float(lc[3]) * self.scale_file_data
                    x2 = float(c[0]) * self.scale_file_data
                    y2 = float(c[1]) * self.scale_file_data
                    z2 = float(c[2]) * self.scale_file_data
                    r2 = float(c[3]) * self.scale_file_data

                    # Make the segment from a series of meta balls

                    segment_vector = mathutils.Vector(((x2 - x1), (y2 - y1), (z2 - z1)))
                    segment_length = segment_vector.length

                    # Be sure that the radii are non-zero
                    if segment_length < 0:
                        segment_length = 0.01
                    if r1 < segment_length / 1000:
                        r1 = segment_length / 1000
                    if r2 < segment_length / 1000:
                        r2 = segment_length / 1000

                    if r1 < self.min_forced_radius:
                        r1 = self.min_forced_radius
                    if r2 < self.min_forced_radius:
                        r2 = self.min_forced_radius

                    dr = r2 - r1
                    dx = x2 - x1
                    dy = y2 - y1
                    dz = z2 - z1

                    r = r1
                    x = x1
                    y = y1
                    z = z1

                    length_so_far = 0
                    while length_so_far < segment_length:
                        # Make a sphere at this point
                        ele = mball.elements.new()
                        ele.radius = r * self.meta_ball_scale_factor
                        ele.co = (x, y, z)

                        # Move x, y, z, and r to the next point
                        length_so_far += r / 2
                        r = r1 + (length_so_far * dr / segment_length)
                        x = x1 + (length_so_far * dx / segment_length)
                        y = y1 + (length_so_far * dy / segment_length)
                        z = z1 + (length_so_far * dz / segment_length)

                    # Make the last one just to be sure

                    # ele = mball.elements.new()
                    # ele.radius = r2
                    # ele.co = (x2, y2, z2)

                    # obj_name = self.add_segment(obj_name, p1=mathutils.Vector((x1, y1, z1)), p2=mathutils.Vector((x2, y2, z2)), r1=r1, r2=r2, faces=10, cap1=cap1, cap2=True)
                lc = c

        if self.convert_to_mesh:
            bpy.ops.object.convert()

        obj.select_set(True)





classes = (
    MakeNeuronMeta_Panel,
    MakeNeuronStick_Operator,
    MakeEmptyStick_Operator,
    UpdateCablePostEdit_Operator,
    ExportCableModel_Operator,
    MakeSpheres_Operator,
    UpdateCableFromSpheres_Operator,
    ShowVertexSpheres_Operator,
    HideVertexSpheres_Operator,
    DeleteAllVertexSpheres_Operator,
    CableModelObject,
    SWCMesher_UL_object,
    CableModelAdd,
    CableModelRemove,
    CableModelRemoveAll,
    MakeNeuronFromFile_Operator,
    MakeNeuronFromData_Operator,
    MakeNeuronMetaAnalyze_Operator,
    MakeNeuronMetaPropGroup
)




def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.make_neuron_meta = bpy.props.PointerProperty(type=MakeNeuronMetaPropGroup)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.make_neuron_meta

if __name__ == "__main__":
    register()