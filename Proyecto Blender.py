bl_info = {
    "name": "SMART Objectives Addon",
    "author": "Gonzalo Munoz",
    "version": (1, 4),
    "blender": (4, 0, 0),
    "location": "View3D > N-panel > SMART",
    "description": "Mover objetos aleatoriamente, Renombrar objetos y mover el origen al origen del mundo",
    "category": "Object",
}

import bpy
import random
import math



#Mover objetos aleatoriamente

class SMART_OT_randomize_position(bpy.types.Operator):
    bl_idname = "smart.randomize_position"
    bl_label = "Mover Objetos Aleatoriamente"
    bl_description = "Importa un OBJ y lo dispersa aleatoriamente con variación de altura"
    bl_options = {'REGISTER', 'UNDO'}

    min_distance: bpy.props.FloatProperty(
        name="Distancia mínima",
        default=5.0,
        min=0.0
    )
    iterations: bpy.props.IntProperty(
        name="Número de objetos",
        default=20,
        min=1
    )
    max_attempts: bpy.props.IntProperty(
        name="Intentos por objeto",
        default=10,
        min=1
    )
    random_range: bpy.props.IntProperty(
        name="Rango aleatorio",
        default=20,
        min=0
    )
    random_height: bpy.props.FloatProperty(
        name="Altura aleatoria",
        default=0.0,
        min=0.0
    )
    filepath: bpy.props.StringProperty(
        name="Ruta OBJ",
        default="C:/Users/gonza/Documents/Untitled.obj",
        subtype='FILE_PATH'
    )

    def execute(self, context):

        coords = []

        def is_too_close(new_x, new_y, coords, min_dist):
            for (cx, cy) in coords:
                if math.hypot(new_x - cx, new_y - cy) < min_dist:
                    return True
            return False

        for i in range(self.iterations):

            valid = False
            attempts = 0

            while attempts < self.max_attempts:
                x = random.randint(-self.random_range, self.random_range)
                y = random.randint(-self.random_range, self.random_range)

                if not is_too_close(x, y, coords, self.min_distance):
                    coords.append((x, y))
                    valid = True
                    break

                attempts += 1

            if not valid:
                self.report({'WARNING'}, f"No se encontró posición válida para objeto {i}")
                continue

            # Importar OBJ
            bpy.ops.wm.obj_import(filepath=self.filepath)
            objs = bpy.context.selected_objects

            # Crear un empty raíz
            root = bpy.data.objects.new(f"Object_{i}", None)
            context.scene.collection.objects.link(root)

            for obj in objs:
                obj.parent = root

            # Variación de altura
            height_offset = random.uniform(0.0, self.random_height)

            trunk = None
            for obj in objs:
                if "Cylinder" in obj.name:
                    trunk = obj
                    break

            if trunk:
                trunk.scale.y += height_offset
                trunk.location.z += height_offset

                for obj in objs:
                    if obj != trunk:
                        obj.location.z += height_offset * 2

            # Posicionar el grupo entero
            root.location.x = x
            root.location.y = y
            root.location.z = 0

        return {'FINISHED'}


#Renombrar Objetos

class SMART_OT_batch_rename(bpy.types.Operator):
    bl_idname = "smart.batch_rename"
    bl_label = "Renombrar Objetos"
    bl_description = "Renombra los objetos seleccionados con un nombre base"
    bl_options = {'REGISTER', 'UNDO'}

    base_name: bpy.props.StringProperty(
        name="Nombre base",
        default="Object"
    )

    def execute(self, context):
        selected = context.selected_objects

        if not selected:
            self.report({'WARNING'}, "No hay objetos seleccionados")
            return {'CANCELLED'}

        for i, obj in enumerate(selected, start=1):
            obj.name = f"{self.base_name}_{i}"

        return {'FINISHED'}


#Origen al origen del mundo

class SMART_OT_origin_to_world(bpy.types.Operator):
    bl_idname = "smart.origin_to_world"
    bl_label = "Origen al Mundo"
    bl_description = "Mueve el origen del objeto activo al origen del mundo sin mover la geometría"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object

        if obj is None:
            self.report({'WARNING'}, "No hay objeto activo")
            return {'CANCELLED'}

        original_matrix = obj.matrix_world.copy()

        obj.matrix_world.translation = (0.0, 0.0, 0.0)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        obj.matrix_world = original_matrix

        return {'FINISHED'}



#   Panel principal

class SMART_PT_panel(bpy.types.Panel):
    bl_label = "SMART Objectives"
    bl_idname = "SMART_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SMART'

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        
        #Mover objetos aleatoriamente

        col.label(text="1. Mover objetos aleatoriamente:")
        col.prop(context.scene, "smart_min_distance")
        col.prop(context.scene, "smart_iterations")
        col.prop(context.scene, "smart_max_attempts")
        col.prop(context.scene, "smart_random_range")
        col.prop(context.scene, "smart_random_height")
        col.prop(context.scene, "smart_filepath")

        op = col.operator("smart.randomize_position", text="Generar Objetos Aleatorios")
        op.min_distance = context.scene.smart_min_distance
        op.iterations = context.scene.smart_iterations
        op.max_attempts = context.scene.smart_max_attempts
        op.random_range = context.scene.smart_random_range
        op.random_height = context.scene.smart_random_height
        op.filepath = context.scene.smart_filepath

        col.separator()

        #Renombrar objetos
        
        col.label(text="2. Renombrar objetos:")
        col.prop(context.scene, "smart_rename_base")

        op2 = col.operator("smart.batch_rename", text="Renombrar")
        op2.base_name = context.scene.smart_rename_base

        col.separator()


        #Origen al mundo

        col.label(text="3. Origen del objeto:")
        col.operator("smart.origin_to_world", text="Mover origen al mundo")



# Registro

classes = (
    SMART_OT_randomize_position,
    SMART_OT_batch_rename,
    SMART_OT_origin_to_world,
    SMART_PT_panel,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.smart_min_distance = bpy.props.FloatProperty(
        name="Distancia mínima",
        default=5.0
    )
    bpy.types.Scene.smart_iterations = bpy.props.IntProperty(
        name="Número de objetos",
        default=20
    )
    bpy.types.Scene.smart_max_attempts = bpy.props.IntProperty(
        name="Intentos por objeto",
        default=10
    )
    bpy.types.Scene.smart_random_range = bpy.props.IntProperty(
        name="Rango aleatorio",
        default=20
    )
    bpy.types.Scene.smart_random_height = bpy.props.FloatProperty(
        name="Altura aleatoria",
        default=0.0,
        min=0.0
    )
    bpy.types.Scene.smart_filepath = bpy.props.StringProperty(
        name="Ruta OBJ",
        default="C:/Users/gonza/Documents/Untitled.obj",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.smart_rename_base = bpy.props.StringProperty(
        name="Nombre base",
        default="Object"
    )


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.smart_min_distance
    del bpy.types.Scene.smart_iterations
    del bpy.types.Scene.smart_max_attempts
    del bpy.types.Scene.smart_random_range
    del bpy.types.Scene.smart_random_height
    del bpy.types.Scene.smart_filepath
    del bpy.types.Scene.smart_rename_base


if __name__ == "__main__":
    register()
