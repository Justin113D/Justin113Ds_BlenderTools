# meta info
bl_info = {
    "name": "Justin's Blender Tools",
    "author": "Justin113D",
    "version": (1,0,1),
    "blender": (2, 81, 0),
    "location": "",
    "description": "Several tools to make life in blender easier",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "General"}

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

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active is not None and active.type == "MESH" and len(active.vertex_groups) > 0 and active.data.use_paint_mask or active.data.use_paint_mask_vertex and active.vertex_groups.active is not None

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

class RemoveUnusedWeights(bpy.types.Operator):
    """Removes all groups that are not used in the armature/s"""
    bl_idname = "object.removeunusedweights"
    bl_label = "Remove Unused"
    bl_description = "Removes all groups that are not used in the assigned armature/s (from the object's armature modifier/s)"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active is None:
            return False
        hasArmature = False
        for m in active.modifiers:
            if m.type == 'ARMATURE':
                if m.object is not None:
                    hasArmature = True
                    break

        return len(active.vertex_groups) > 0 and hasArmature

    def execute(self, context):

        active = context.active_object

        armatures = list()
        for m in active.modifiers:
            if m.type == 'ARMATURE':
                if m.object is not None:
                    armatures.append(m.object.data)

        used = list()
        for a in armatures:
            for b in a.bones:
                if b.use_deform:
                    used.append(b.name)

        weights = list()
        groups = active.vertex_groups
        for w in groups:
            weights.append(w.name)

        for w in weights:
            if w not in used:
                g = groups[groups.find(w)]
                groups.remove(g)

        return {'FINISHED'}

class RemoveEmptyWeights(bpy.types.Operator):
    """Removes all empty weights from vertices"""
    bl_idname = "object.removeemptygroups"
    bl_label = "Remove Empty"
    bl_description = "Removes all groups with no weights"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active is not None and len(active.vertex_groups) > 0

    def execute(self, context):
        active = context.active_object
        mesh = active.data

        toRemove = list()

        for g in active.vertex_groups:
            vCount = 0
            for v in mesh.vertices:
                try:
                    if g.weight(v.index) > 0:
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

class SymmetryizeLattice(bpy.types.Operator):
    """Symmetrizes a lattice"""
    bl_idname = "object.symmetrize"
    bl_label = "Symmetrize lattice"
    bl_description = "Symmetrizes a lattice"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return  bpy.context.object.mode == "OBJECT" and active is not None and active.type == "LATTICE"

    def execute(self, context):
        lattice = bpy.context.active_object
        data = lattice.data

        right = []
        left = []

        for p in lattice.data.points:
            if p.co[0] < 0:
                right.append(p)
            elif p.co[0] > 0:
                left.append(p)

        for r in right:
            for l in left:
                if r.co[1] == l.co[1] and r.co[2] == l.co[2]:
                    rC = round(r.co[0], 4)
                    lC = round(-l.co[0], 4)
                    if rC == lC:
                        r.co_deform[0] = -l.co_deform[0]
                        r.co_deform[1] = l.co_deform[1]
                        r.co_deform[2] = l.co_deform[2]
                        break

        return {'FINISHED'}

class CopyActiveCMs(bpy.types.Operator):
    """Copies active modifiers / constraints to buffer"""
    bl_idname = "screen.copyactivecms"
    bl_label = "Copy Active Modifiers/Constraints"
    bl_description = "Copies opened modifiers/constraints into a buffer, ready to be pasted"

    @classmethod
    def poll(cls, context):
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
    def poll(cls, context):
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
    RemoveEmptyWeights,
    RemoveUnusedWeights,
    CopyActiveCMs,
    PasteActiveCMs,
    SymmetryizeLattice,
    )

def weightPaintFunc(self, context):
    self.layout.operator(AverageWeight.bl_idname)

def weightMenuFunc(self, context):
    self.layout.separator()
    self.layout.operator(RemoveEmptyWeights.bl_idname)
    self.layout.operator(RemoveUnusedWeights.bl_idname)

def latticeContextMenuFunc(self, context):
    active = context.active_object
    if bpy.context.object.mode == "OBJECT" and active is not None and active.type == "LATTICE":
        self.layout.operator(SymmetryizeLattice.bl_idname)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_paint_weight.append(weightPaintFunc)
    bpy.types.MESH_MT_vertex_group_context_menu.append(weightMenuFunc)
    bpy.types.VIEW3D_MT_object.append(latticeContextMenuFunc)
    bpy.types.VIEW3D_MT_object_context_menu.append(latticeContextMenuFunc)

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