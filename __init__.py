# meta info
bl_info = {
    "name": "Justin's Blender Tools",
    "author": "Justin113D",
    "version": (1,0,0),
    "blender": (2, 81, 0),
    "location": "",
    "description": "Several tools to make blender easier",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Rigging"}

import bpy

constraintBuffer = None
modifierBuffer = None

class AttributeBuffer():

    def __init__(self, name, bType, attributes):
        self.name = name
        self.bType = bType
        self.attributes = attributes

class AverageWeight(bpy.types.Operator):
    """Average the weights of the selected vertices"""
    bl_idname = "paint_weight.average"
    bl_label = "Average weight"
    bl_description = "Average the weights of the selected vertices"

    def execute(self, context):

        active = context.active_object
        if active.data.use_paint_mask or active.data.use_paint_mask_vertex:
            group = active.vertex_groups.active

            selected_verts = list(filter(lambda v: v.select, active.data.vertices))

            weight = 0
            indices = []
            for v in selected_verts:
                try:
                    weight += group.weight(v.index)
                except RuntimeError:
                    weight = weight
                indices.append(v.index)

            weight /= len(selected_verts)

            for v in selected_verts:
                group.add(indices, weight, 'REPLACE')

        return {'FINISHED'}

class CleanWeights(bpy.types.Operator):
    """Removes all empty weights from vertices"""
    bl_idname = "object.clearweights"
    bl_label = "Clean Weights"
    bl_description = "Removes all empty weights from vertices"

    def execute(self, context):
        active = context.active_object
        mesh = active.data

        for v in mesh.vertices:
            for g in active.vertex_groups:
                try:
                    if g.weight(v.index) < 0.001:
                        g.remove([v.index])
                except RuntimeError:
                    pass

        return {'FINISHED'}

class RemoveUnusedWeights(bpy.types.Operator):
    """Removes all groups that are not used in the armature/s"""
    bl_idname = "object.removeunusedweights"
    bl_label = "Remove unused"
    bl_description = "Removes all groups that are not used in the armature/s"

    def execute(self, context):

        active = context.active_object
        used = list()



        return {'FINISHED'}

class RemoveEmptyWeights(bpy.types.Operator):
    """Removes all empty weights from vertices"""
    bl_idname = "object.removeemptygroups"
    bl_label = "Remove Empty"
    bl_description = "Removes all groups with no weights"

    def execute(self, context):
        active = context.active_object
        mesh = active.data

        toRemove = list()

        for g in active.vertex_groups:
            vCount = 0
            for v in mesh.vertices:
                try:
                    if g.weight(v.index) != 0:
                        vCount += 1
                        break
                except RuntimeError:
                    pass
            if vCount > 0:
                continue
            toRemove.append(g)

        for r in toRemove:
            active.vertex_groups.remove(r)

        return {'FINISHED'}

class CopyActiveCMs(bpy.types.Operator):
    """Copies active modifiers / constraints to buffer"""
    bl_idname = "screen.copyactivecms"
    bl_label = "Copy Active Modifiers/Constraints"
    bl_description = "Copies opened modifiers/constraints into a buffer, ready to be pasted"

    @classmethod
    def poll(self, context):
        cnt = context.area.spaces.active.context
        self.areaType = cnt
        return cnt == 'MODIFIER' or cnt == 'CONSTRAINT' or cnt == 'BONE_CONSTRAINT'

    def execute(self, context):

        if self.areaType == 'BONE_CONSTRAINT':
            activeObj = context.active_pose_bone
        else:
            activeObj = context.active_object

        containers = list()
        ignore = (  "bl_rna", "__doc__", "__module__", "__slots__",
            "active", "error_location", "error_rotation",
            "is_proxy_local", "is_valid", "show_expanded",
            "type", "rna_type", "name")


        if self.areaType == 'MODIFIER':
            for  m in activeObj.modifiers:
                if m.show_expanded:
                    containers.append(m)

            global modifierBuffer
            modifierBuffer = list()
            buffer = modifierBuffer

            print("Copied {} modifiers!".format(len(containers)))

        else:
            for c in activeObj.constraints:
                if c.show_expanded:
                    containers.append(c)

            global constraintBuffer
            constraintBuffer = list()
            buffer = constraintBuffer

            print("Copied {} constraints!".format(len(containers)))

        for c in containers:
            props = dict()
            for p in dir(c):
                if p in ignore:
                    continue
                props[p] = getattr(c, p)

            buffer.append(AttributeBuffer(c.name, c.type, props))


        return {'FINISHED'}

class PasteActiveCMs(bpy.types.Operator):
    """Pastes active modifiers / constraints to buffer"""
    bl_idname = "screen.pasteactivecms"
    bl_label = "Paste Active Modifiers/Constraints"
    bl_description = "Pastes buffered modifiers/constraints from buffer"

    @classmethod
    def poll(self, context):
        cnt = context.area.spaces.active.context
        self.areaType = cnt
        return cnt == 'MODIFIER' or cnt == 'CONSTRAINT' or cnt == 'BONE_CONSTRAINT'

    def execute(self, context):

        if self.areaType == 'BONE_CONSTRAINT':
            activeObj = context.active_pose_bone
        else:
            activeObj = context.active_object

        if self.areaType == 'MODIFIER':
            global modifierBuffer
            print("Pasting {} modifiers".format(len(modifierBuffer)))

            for b in modifierBuffer:
                newConstr = activeObj.modifiers.new(name=b.name, type=b.bType)
                for k, v in b.attributes.items():
                    setattr(newConstr, k, v)

        else:
            global constraintBuffer
            print("Pasting {} constraints".format(len(constraintBuffer)))

            for b in constraintBuffer:
                newConstr = activeObj.constraints.new(type=b.bType)
                newConstr.name = b.name
                for k, v in b.attributes.items():
                    setattr(newConstr, k, v)

        return {'FINISHED'}

classes = (
    AverageWeight,
    CleanWeights,
    RemoveEmptyWeights,
    RemoveUnusedWeights,
    CopyActiveCMs,
    PasteActiveCMs,
    )

def weightPaintFunc(self, context):
    self.layout.operator(AverageWeight.bl_idname)

def weightMenuFunc(self, context):
    self.layout.separator()
    self.layout.operator(CleanWeights.bl_idname)
    self.layout.operator(RemoveEmptyWeights.bl_idname)
    self.layout.operator(RemoveUnusedWeights.bl_idname)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_paint_weight.append(weightPaintFunc)
    bpy.types.MESH_MT_vertex_group_context_menu.append(weightMenuFunc)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name="Property Editor", space_type='PROPERTIES')

        kmi = km.keymap_items.new(CopyActiveCMs.bl_idname, type='C', ctrl=True, value='PRESS')
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(PasteActiveCMs.bl_idname, type='V', ctrl=True, value='PRESS')
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.types.VIEW3D_MT_paint_weight.remove(weightPaintFunc)
    bpy.types.MESH_MT_vertex_group_context_menu.remove(weightMenuFunc)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()