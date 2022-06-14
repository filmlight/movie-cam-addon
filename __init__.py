# HB Movie-Cam V0.2.0
# V20220613B-EP4 by HBG
# Blender Version = 3.2.0
# Blender built-in python version = 3.10.2
# fake-bpy-module-latest version = 20220602


# SECTION 1.0
# Blender Add-on Metadata
bl_info = {
    "name": "HB Movie-Cam",
    "author": "Hu Bing",
    "version": (0, 2, 0),
    "blender": (3, 2, 0),
    "location": "View3D > Sidebar > Movie-Cam",
    "description": "HB Movie-Cam Add-on V020 EP4",
    "warning": "",
    "doc_url": "www.ditchina.com",
    "category": "3D View"
}


# SECTION 1.1
# Import Blender Python Library
import bpy
import mathutils
from bpy.utils import resource_path
from pathlib import Path


# SECTION 1.2
# Define Global Variables
startFrameNum = 1
out_frame_set = 101


# Section 2.0 - Operator Subclasses Definition
# SECTION 2.1
# Append Movie-Cam Collection from external .blend file
class CAM_OT_fun_1(bpy.types.Operator):
    bl_idname = "hb.fun_1"
    bl_label = "导入跟踪摄影机"

    def execute(self, context):

        # Acquire Blender USER resource path
        USER_PATH = Path(resource_path('USER'))
        ADDON_NAME = "HB_Movie-Cam"
        ASSET_NAME = "HB_Cam_Asset.blend"
        ASSET_PATH = USER_PATH / "scripts/addons" / ADDON_NAME / "asset" / ASSET_NAME / "Collection"
        ASSET_PATH_str = str(ASSET_PATH)

        OBJECT_NAME = "Cam_Collection"

        if 'Cam_Box' not in bpy.data.objects.keys():
            
            bpy.ops.wm.append(
                directory = ASSET_PATH_str,
                filename = OBJECT_NAME
                )
            
            # Set Cam_Camera as Scene Active Camera
            bpy.data.scenes['Scene'].camera = bpy.data.objects['Cam_Camera']
            
            self.report({'INFO'}, f"跟踪摄影机已成功导入")

        else:
            self.report({'WARNING'}, f"跟踪摄影机已存在")
            
        return {'FINISHED'}


# SECTION 2.4.1
# Camera Movement Preset Enum Functions
class CAM_OT_fun_2(bpy.types.Operator):
    bl_idname = "hb.fun_2"
    bl_label = "创建摄影机动画预置"

    def execute(self, context):

        if 'Cam_Box' in bpy.data.objects.keys():

            # Initialize Cam_Box OUT-Point Space Vector
            camBox_out_Vector = mathutils.Vector()

            if bpy.context.scene.cam_move_presets_enum == 'OP1':
                
                camBox_Vector = bpy.data.scenes['Scene'].objects['Cam_Box'].location.xyz
                followEmpty_Vector = bpy.data.scenes['Scene'].objects['Cam_Follow_Empty'].location.xyz

                # Original distance between Cam_Box and FollowEmpty
                o_length = (camBox_Vector - followEmpty_Vector).length

                # Cam_Box movement length ratio
                length_ratio = 1.0 + (bpy.context.scene.cam_move_duration_frames / 125)

                # Calculate CamBox OUT-Point Space Vector
                camBox_out_Vector[0] = length_ratio * (camBox_Vector[0] - followEmpty_Vector[0]) + followEmpty_Vector[0]
                camBox_out_Vector[1] = length_ratio * (camBox_Vector[1] - followEmpty_Vector[1]) + followEmpty_Vector[1]
                camBox_out_Vector[2] = length_ratio * (camBox_Vector[2] - followEmpty_Vector[2]) + followEmpty_Vector[2]

                # Distance after movement - for debug only
                f_length = (camBox_out_Vector - followEmpty_Vector).length
                print(f"f_length = {f_length}")
                print(f"f_length type: {type(f_length)}\n")

                # Create timeline animation
                startFrameNum = bpy.context.scene.frame_current

                # Insert IN-Point Keyframe
                CamBox_obj = bpy.data.objects['Cam_Box']
                CamBox_obj.keyframe_insert(data_path="location", index=-1, frame=startFrameNum)

                CamHB_Camera = bpy.data.cameras['Camera.hb']
                CamHB_Camera.keyframe_insert(data_path="lens", index=-1, frame=startFrameNum)

                # Place Cam_Box to OUT-Point position
                bpy.data.scenes['Scene'].objects['Cam_Box'].location = camBox_out_Vector

                # Define Camera.hb lens original value
                o_lens_flength = bpy.data.cameras['Camera.hb'].lens

                # Define Cam_Box movement distance
                m_length = o_length * length_ratio

                # Calculate Camera.hb OUT-Point lens value
                bpy.data.cameras['Camera.hb'].lens = o_lens_flength * ((o_length + m_length) / o_length)

                duration_frames_set = bpy.context.scene.cam_move_duration_frames
                out_frame_set = startFrameNum + duration_frames_set

                # Insert OUT-Point Keyframe
                CamBox_obj.keyframe_insert(data_path="location", index=-1, frame=out_frame_set)
                CamHB_Camera.keyframe_insert(data_path="lens", index=-1, frame=out_frame_set)

                self.report({'INFO'}, f"Dolly Zoom动画已创建")
                
            elif bpy.context.scene.cam_move_presets_enum == 'OP2':
                bpy.ops.mesh.primitive_cube_add()
                self.report({'INFO'}, f"预置操作已完成")
                
            elif bpy.context.scene.cam_move_presets_enum == 'OP3':
                bpy.ops.mesh.primitive_uv_sphere_add()
                self.report({'INFO'}, f"预置操作已完成")

        else:
            self.report({'WARNING'}, f"请先导入跟踪摄影机")
            
        return {'FINISHED'}


# SECTION 3.1 Create Cable for Camera to Clamp to
class CAM_OT_fun_11(bpy.types.Operator):
    bl_idname = "hb.fun_11"
    bl_label = "创建摄影机绳索"

    def execute(self, context):

        if 'Cam_Box' in bpy.data.objects.keys():
            
            if bpy.context.active_object != None and bpy.context.active_object.name == 'Cam_Box':
                
                bpy.data.objects['Cam_Box'].constraints.clear()
                bpy.data.objects['Cam_Box'].location = [0, 0, 0]
                
                bpy.ops.curve.primitive_nurbs_path_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                # Rename the NURBS Path immediately
                bpy.context.active_object.name = 'CamCablePath'
                
                # Add constraints to Cam_Box
                bpy.data.objects['Cam_Box'].constraints.new('CLAMP_TO')
                bpy.data.objects['Cam_Box'].constraints['Clamp To'].target = bpy.data.objects['CamCablePath']
                
                # TRACK_TO AFTER CLAMP_TO
                bpy.data.objects['Cam_Box'].constraints.new('TRACK_TO')
                bpy.data.objects['Cam_Box'].constraints['Track To'].target = bpy.data.objects['Cam_Follow_Empty']
                
                bpy.data.objects['Cam_Box'].constraints['Track To'].track_axis = 'TRACK_NEGATIVE_Y'
                bpy.data.objects['Cam_Box'].constraints['Track To'].up_axis = 'UP_Z'
                
                self.report({'INFO'}, f"摄影机绳索已创建")

            else:
                self.report({'WARNING'}, f"请先单独选中跟踪摄影机")

        else:
            self.report({'WARNING'}, f"请先导入跟踪摄影机")

        return {'FINISHED'}


# SECTION 3.2 In Keyframe Set Button
class TIMELINE_OT_fun_12(bpy.types.Operator):
    bl_idname = "hb.fun_12"
    bl_label = "设置入点"

    def execute(self, context):

        if 'Cam_Box' in bpy.data.objects.keys():
            
            startFrameNum = bpy.context.scene.frame_current

            # Set Object Location            
            CamBox_Obj = bpy.data.objects['Cam_Box']
            CamBox_Obj.keyframe_insert(data_path="location", index=-1, frame=startFrameNum)

            # Set Camera Lens
            CamHB_Camera = bpy.data.cameras['Camera.hb']
            CamHB_Camera.keyframe_insert(data_path="lens", index=-1, frame=startFrameNum)

            self.report({'INFO'}, f"入点关键帧已设置在第{startFrameNum}帧")

        else:
            self.report({'WARNING'}, f"请先导入跟踪摄影机")
            
        return {'FINISHED'}


# SECTION 3.3 Out keyframe Set Button
class TIMELINE_OT_fun_13(bpy.types.Operator):
    bl_idname = "hb.fun_13"
    bl_label = "设置出点"

    def execute(self, context):

        if 'Cam_Box' in bpy.data.objects.keys():
            
            duration_frames_set = bpy.context.scene.cam_move_duration_frames
            out_frame_set = startFrameNum + duration_frames_set
            print(f"Global Variable <out_frame_set>: {out_frame_set}")

            # Set Object Location            
            CamBox_obj = bpy.data.objects['Cam_Box']
            CamBox_obj.keyframe_insert(data_path="location", index=-1, frame=out_frame_set)

            # Set Camera Lens            
            CamHB_Camera = bpy.data.cameras['Camera.hb']
            CamHB_Camera.keyframe_insert(data_path="lens", index=-1, frame=out_frame_set)
            
            self.report({'INFO'}, f"出点关键帧已设置在第{out_frame_set}帧")

        else:
            self.report({'WARNING'}, f"请先导入跟踪摄影机")
            
        return {'FINISHED'}


# SECTION 3.4 Timeline Playback Control
class TIMELINE_OT_fun_14(bpy.types.Operator):
    bl_idname = "hb.fun_14"
    bl_label = "播放时间线动画"

    def execute(self, context):
        
        # Change 3D Viewport to Camera View
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'

        # Set Playhead to specific frame
        bpy.context.scene.frame_set(startFrameNum)
        # Toggle Animation Playback
        bpy.ops.screen.animation_play()

        return {'FINISHED'}


# SECTION 3.6 Remove all Movie-Cam Animation
class ANI_OT_fun_15(bpy.types.Operator):
    bl_idname = "hb.fun_15"
    bl_label = "清除全部摄影机动画"

    def execute(self, context):

        if 'Cam_BoxAction' in bpy.data.actions.keys():
            CamBox_Action = bpy.data.actions['Cam_BoxAction']
            CameraHB_Action = bpy.data.actions['Camera.hbAction']
            
            bpy.data.actions.remove(CamBox_Action)
            bpy.data.actions.remove(CameraHB_Action)
            bpy.data.cameras['Camera.hb'].animation_data_clear()
            bpy.context.scene.linear_interpolation_bool = False
            self.report({'INFO'}, f"摄影机动画已全部清除")

        else:
            self.report({'WARNING'}, f"摄影机动画不存在")
            
        return {'FINISHED'}


# Section 31.0 - Functions Definition
def set_to_linear(self, context):

    if 'Cam_BoxAction' in bpy.data.actions.keys():
        print('Cam_BoxAction found')

        if bpy.context.scene.linear_interpolation_bool == True:
            print('FCurve set to True')
            fcurves_cam = bpy.data.actions['Cam_BoxAction'].fcurves

            for fc in fcurves_cam:
                for kfp in fc.keyframe_points:
                    kfp.interpolation = 'LINEAR'

        else:
            print('FCurve set to False')
            fcurves_cam = bpy.data.actions['Cam_BoxAction'].fcurves

            for fc in fcurves_cam:
                for kfp in fc.keyframe_points:
                    kfp.interpolation = 'BEZIER'

    else:
        print('Cam_BoxAction Not Defined!')


# SECTION 4.0 Define Camera Lens Focal Length Operator Subclasses
# 4.1 Set Camera Lens to 27mm
class LENS_OT_fun_21(bpy.types.Operator):
    bl_idname = "camlens.mp27"
    bl_label = "Set to 27mm"

    def execute(self, context):
        if 'Cam_Camera' in bpy.data.objects.keys():
            bpy.data.cameras['Camera.hb'].lens = 27

        else:
            self.report({'WARNING'}, f"请先创建跟踪摄影机")

        return {'FINISHED'}

# 4.2 Set Camera Lens to 40mm
class LENS_OT_fun_22(bpy.types.Operator):
    bl_idname = "camlens.mp40"
    bl_label = "Set to 40mm"

    def execute(self, context):
        if 'Cam_Camera' in bpy.data.objects.keys():
            bpy.data.cameras['Camera.hb'].lens = 40

        else:
            self.report({'WARNING'}, f"请先创建跟踪摄影机")

        return {'FINISHED'}

# 4.3 Set Camera Lens to 75mm
class LENS_OT_fun_23(bpy.types.Operator):
    bl_idname = "camlens.mp75"
    bl_label = "Set to 75mm"

    def execute(self, context):
        if 'Cam_Camera' in bpy.data.objects.keys():
            bpy.data.cameras['Camera.hb'].lens = 75

        else:
            self.report({'WARNING'}, f"请先创建跟踪摄影机")

        return {'FINISHED'}

# 4.4 Set Camera Lens to 100mm
class LENS_OT_fun_24(bpy.types.Operator):
    bl_idname = "camlens.mp100"
    bl_label = "Set to 100mm"

    def execute(self, context):
        if 'Cam_Camera' in bpy.data.objects.keys():
            bpy.data.cameras['Camera.hb'].lens = 100

        else:
            self.report({'WARNING'}, f"请先创建跟踪摄影机")

        return {'FINISHED'}


# Section 20.0 - Build the Side Panel
class HB_PT_SidePanel_1(bpy.types.Panel):
    bl_idname = "HB_PT_SidePanel1"
    bl_label = "HB Movie-Cam EP"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Movie-Cam'
    bl_order: 231

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="HB Movie-Cam  V0.2.0", icon='FUND')
        row = layout.row()
        row = layout.row()
        
        row.operator(CAM_OT_fun_1.bl_idname, icon='OUTLINER_OB_CAMERA')
        row = layout.row()
        row = layout.row()
        row.label(text="选择摄影机运动预置")
        row = layout.row()
        row.prop(context.scene, "cam_move_presets_enum", text="")
        row = layout.row()
        layout.prop(context.scene, "cam_move_duration_frames")
        row = layout.row()
        row.operator(CAM_OT_fun_2.bl_idname, text="创建摄影机预置动画")
        row = layout.row()
        layout.row().separator()

        row = layout.row()
        row = layout.row()
        row.operator(CAM_OT_fun_11.bl_idname, icon='CURVE_DATA')
        row = layout.row()
        layout.prop(context.scene, "cam_move_duration_frames")
        row = layout.row()
        row.operator(TIMELINE_OT_fun_12.bl_idname)
        row.operator(TIMELINE_OT_fun_13.bl_idname)
        row = layout.row()
        row.operator(TIMELINE_OT_fun_14.bl_idname)
        row = layout.row()
        layout.prop(context.scene, "linear_interpolation_bool")

        row = layout.row()
        layout.separator()
        row.operator(ANI_OT_fun_15.bl_idname)
        row = layout.row()

        row = layout.row()
        row.split()
        row.label(text="使用 Shift+F 切换镜头焦距")
        row = layout.row()


# Section 21.0 - Create Pie Menu for Lens Selection
class HB_MT_PieMenu_1(bpy.types.Menu):
    bl_idname = "HB_MT_PieMenu1"
    bl_label = "选择镜头焦距"

    def draw(self, context):
        layout = self.layout

        # Create the pie menu for lens selection
        pie_menu_lens = layout.menu_pie()
        pie_menu_lens.operator("camlens.mp27", icon="VIEW_CAMERA")
        pie_menu_lens.operator("camlens.mp40", icon="VIEW_CAMERA")
        pie_menu_lens.operator("camlens.mp75", icon="VIEW_CAMERA")
        pie_menu_lens.operator("camlens.mp100", icon="VIEW_CAMERA")


# Section 80.0 - Add-on Classes Registration
classes = (CAM_OT_fun_1, CAM_OT_fun_2, CAM_OT_fun_11, 
TIMELINE_OT_fun_12, TIMELINE_OT_fun_13, TIMELINE_OT_fun_14, 
ANI_OT_fun_15, LENS_OT_fun_21, LENS_OT_fun_22, LENS_OT_fun_23, LENS_OT_fun_24, 
HB_PT_SidePanel_1, HB_MT_PieMenu_1)

# Initialize Add-on Keymaps list
addon_keymaps = []

def register():

    # Define custom properties
    # CP1. 创建 [摄影机动画预置] 场景属性 - 枚举型
    bpy.types.Scene.cam_move_presets_enum = bpy.props.EnumProperty(
        name="摄影机运动预置",
        description="选择预置运动方式",
        items=[
            ('OP1', "Dolly Zoom", "生成Dolly Zoom运动效果"),
            ('OP2', "Cube", "新创建一个立方体"),
            ('OP3', "球体", "新创建一个球体")
        ]
    )

    # CP2. 创建 [摄影机动画持续帧数] 场景属性 - 整型
    bpy.types.Scene.cam_move_duration_frames = bpy.props.IntProperty(
        name = "摄影机动画持续帧数", 
        default=100, 
        max=1000, 
        min=10, 
        description="用户自定义摄影机动画持续帧数"
        )

    # CP3. 创建 [应用线性插值方式] 场景属性 - 布尔型
    bpy.types.Scene.linear_interpolation_bool = bpy.props.BoolProperty(
        name="应用线性插值方式", 
        default=False, 
        update=set_to_linear, 
        description="切换摄影机动画曲线插值方式"
        )

    for cls in classes:
        bpy.utils.register_class(cls)

    # Add keymap entry for Add-on Shortcut
    keyConfig = bpy.context.window_manager.keyconfigs.addon
    keyMapping = keyConfig.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi_mnu = keyMapping.keymap_items.new("wm.call_menu_pie", type='F', value='PRESS', shift=True)
    kmi_mnu.properties.name = HB_MT_PieMenu_1.bl_idname
    addon_keymaps.append((keyMapping, kmi_mnu))


def unregister():
    for cls in classes:

        bpy.utils.unregister_class(cls)
    
    # Remove keyMapping
    for keyMapping, kmi_mnu in addon_keymaps:
        keyMapping.keymap_items.remove(kmi_mnu)
    
    addon_keymaps.clear()

    # Remove custom properties
    del bpy.types.Scene.cam_move_presets_enum
    del bpy.types.Scene.cam_move_duration_frames
    del bpy.types.Scene.linear_interpolation_bool


if __name__=="__main__":
    register()

