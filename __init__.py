### This addon allows you to color objects with link diffuse shader ###


bl_info = {
    "name": "Color Picker",
    "author": "dono",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "description": "Color the world",
    "location": "UV/ImageEditor > Color Picker",
    "warning": "",
    "wiki_url": "",
    "category": "User",
    }

## COLOR PICKER

import bpy
from mathutils import Vector

ispicking = False
i = 0
list_obj =[]

class StartColorPicker(bpy.types.Operator):
    bl_idname = "colorpicker.startpicking"
    bl_label = "Start Color Picker"
    
    
    @classmethod
    def poll(self,context):
        return  context.selected_objects
    
    def execute (self, context):
        global ispicking
        ispicking = True
        
        ob = context.active_object

        ## LINK the node diffuse
        filepath = r"T:\PRODUCTIONS\HAPPY_HAND\02_PROD\lib\materials\diffuse\diffuse.blend"
        with bpy.data.libraries.load(filepath, link = True) as (data_from, data_to):
            data_to.node_groups = ["diffuse"]

        node_tree_diffuse = data_to.node_groups[0]

        ## CREATE materials for all objects
        for ob in context.selected_objects:
            
            if ob.type == "MESH":
                # Assign it to object
                if not ob.data.materials:
                
                    # Create a new material diffuse
                    material = bpy.data.materials.new(name="diffuse")
                    material.use_nodes = True

                    # Remove default and create nodegroup diffuse
                    material.node_tree.nodes.remove(material.node_tree.nodes.get('Diffuse BSDF'))
                    material_output = material.node_tree.nodes.get('Material Output')
                    diffuse_node = material.node_tree.nodes.new('ShaderNodeGroup')
                    diffuse_node.node_tree = node_tree_diffuse

                    # link shader to material
                    material.node_tree.links.new(material_output.inputs[0], diffuse_node.outputs[0])

                    # set material to object
                    ob.data.materials.append(material)


        ## START

        ## LIST of objects
        global list_obj
        list_obj = []
        i = 0
        for ob in context.selected_objects:
            if ob.type == "MESH":
                list_obj.append(ob)

        ## SELECT first object of the list
        for x in bpy.data.objects:
            x.select = False
        ob = list_obj[i]
        ob.select = True

        return{'FINISHED'}
    
## CLASS Execute "Next object"
class DialogOperator(bpy.types.Operator):

    bl_idname = "object.color_operator"
    bl_label = "Next object"

## CLASS to execute       

    ## EXECUTE
    def execute(self, context):
        
        ## COLOR
        for x in bpy.data.objects:
            x.select = False
        global i
        i +=1  
        if i<((len(list_obj))):
            ob = list_obj[i]           
            ob.select = True
        
        ## When finished, color all shader as viewport color 
        else:           
            for ob in list_obj:
                for mat in ob.data.materials:                
                    color = mat.diffuse_color
                    try:
                        mat.node_tree.nodes['Group'].inputs[0].default_value = [color[0],color[1],color[2],1]   
                    except:
                        pass
                    try:
                        mat.node_tree.nodes['Diffuse BSDF'].inputs[0].default_value = [color[0],color[1],color[2],1] 
                    except:
                        pass
            ## COMPARE diffuse color
            ## IF the same, keep one material
            for ob in bpy.data.objects:
                if ob.type == "MESH":
                    if ob.data.materials:
                        for a in range (len(ob.data.materials)):
                            for list_objmat in bpy.data.objects:
                                if not ob == list_objmat and ob=='MESH':           
                                    for b in range(len(list_objmat.data.materials)):
                                        color_a = ob.data.materials[a].diffuse_color
                                        color_b = list_objmat.data.materials[b].diffuse_color
                                        difference_color= Vector(color_a) - Vector(color_b)
                                        thresold = difference_color.length
                                        if thresold < 0.01:
                                            ob.data.materials[a]=list_objmat.data.materials[b]
                                
                            
            ## Message finished
            self.report({'INFO'}, 'FINISHED!')
            global ispicking
            ispicking = False
            
            def draw(self, context):
                self.layout.label("FINISHED!")
            context.window_manager.popup_menu(draw, title="Color Picker", icon='COLOR')
    
        
        return {'FINISHED'}

### Panel Color Picker launch ###
class CleanerPanel(bpy.types.Panel):

    bl_label = "Color picker"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Color picker"

    def draw_color_object(self, context):       
        global i
        layout = self.layout
        
        if i<(len(list_obj)):
            ob = list_obj[i]
            row = layout.row()
            row.label(text="Color the world !", icon='COLOR')
            row = layout.row()
            #row.label(text="Active object is: " + ob.name)
            row = layout.row()
            row.prop(ob, "name", text="Object")
            
            # Material Property Added
            for mat in ob.data.materials:                
                row = layout.row()             
                row.prop(mat, "diffuse_color", text=mat.name)
                row = layout.row()                
            layout.operator("object.color_operator", icon = "TRIA_RIGHT") #Create button Assign

    
    def draw(self,context):
        
        ## PANEL        
        layout = self.layout
        
        if ispicking == True:
            self.draw_color_object(context)
        else:
            layout.operator("colorpicker.startpicking", icon = "SOLO_ON") #Create button Assign
            
        


## REGISTER UNREGISTER
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()