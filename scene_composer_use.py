"""
Scene Composer - Blender Addon
================================
Creates artistic compositions of geometric primitives with professional
studio lighting, advanced materials, and architectural composition rules.

Author: TechnoRiver CheckPrixa
Version: 1.0
================================

Primitive Composition Generator for Blender - FULL FEATURED
============================================================
Creates an artistic composition of geometric primitives on a backplane
with cohesive color schemes, professional studio lighting, architectural
composition rules, collision detection, and advanced materials.

Features:
- Interactive UI panel in the 3D Viewport sidebar (N-panel)
- Choose primitive types, color palettes, and distribution settings
- COMPOSITION RULES: Grouping, Sorting, Contrast, Linearity
- COLLISION DETECTION: Objects adjusted to touch without overlapping
- ADVANCED MATERIALS: Wood, Glass, Metal, Plastic, Rubber, Skin, Wax, Marble
- Primitives positioned on the plane for proper shadow casting
- Camera automatically frames the entire composition
- Production-ready render settings

Usage:
1. Open Blender
2. Go to Scripting workspace
3. Open/paste this script
4. Click "Run Script"
5. Open the sidebar (N key) in 3D Viewport
6. Find "Primitives" tab
7. Adjust settings and click "Generate Scene"
8. Click "Render" or press F12

"""

bl_info = {
    "name": "Scene Composer",
    "author": "TechnoRiver CheckPrixa",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Primitives Tab",
    "description": "Creates artistic compositions of geometric primitives with advanced materials and composition rules",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}



import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix
from bpy.props import (
    BoolProperty, 
    IntProperty, 
    FloatProperty, 
    EnumProperty,
    FloatVectorProperty,
    StringProperty,
)
from bpy.types import Panel, Operator, PropertyGroup


# ===========================================
# PROPERTY GROUP - Stores all settings
# ===========================================

class PrimitiveCompositionSettings(PropertyGroup):
    """Stores all user-configurable settings"""
    
    # ===== PRIMITIVE TYPES =====
    use_cube: BoolProperty(name="Cube", default=True)
    use_sphere: BoolProperty(name="Sphere", default=True)
    use_cylinder: BoolProperty(name="Cylinder", default=True)
    use_cone: BoolProperty(name="Cone", default=True)
    use_torus: BoolProperty(name="Torus", default=True)
    use_ico_sphere: BoolProperty(name="Ico Sphere", default=False)
    use_capsule: BoolProperty(name="Capsule", default=True)
    use_rounded_cube: BoolProperty(name="Rounded Cube", default=True)
    
    # ===== COLOR PALETTE =====
    color_palette: EnumProperty(
        name="Color Palette",
        items=[
            ('warm_sunset', "Warm Sunset", "Coral, peach, terracotta"),
            ('ocean_calm', "Ocean Calm", "Teal, seafoam, steel blue"),
            ('forest_moss', "Forest Moss", "Forest green, olive, sage"),
            ('dusty_rose', "Dusty Rose", "Mauve, blush, plum"),
            ('monochrome', "Monochrome", "Charcoal to silver grays"),
            ('earth_tones', "Earth Tones", "Brown, tan, sienna"),
            ('candy_pop', "Candy Pop", "Vibrant pastels"),
            ('nordic_winter', "Nordic Winter", "Cool blues and whites"),
            ('golden_hour', "Golden Hour", "Amber, honey, warm gold"),
            ('midnight_jazz', "Midnight Jazz", "Deep indigo, plum, navy"),
            ('desert_sand', "Desert Sand", "Sandstone, ochre, burnt orange"),
            ('arctic_aurora', "Arctic Aurora", "Emerald, violet, cyan"),
            ('vintage_cream', "Vintage Cream", "Ivory, khaki, muted rose"),
            ('tropical_punch', "Tropical Punch", "Mango, fuchsia, lime"),
            ('slate_storm', "Slate Storm", "Gunmetal, ash, dark teal"),
        ],
        default='warm_sunset'
    )
    
    # ===== BASIC DISTRIBUTION =====
    num_primitives: IntProperty(
        name="Number of Primitives",
        default=30, min=5, max=150
    )
    
    spread_x: FloatProperty(
        name="Spread X",
        default=4.0, min=1.0, max=15.0
    )
    
    spread_y: FloatProperty(
        name="Spread Y",
        default=4.0, min=1.0, max=15.0
    )
    
    min_scale: FloatProperty(
        name="Min Scale",
        default=0.3, min=0.1, max=2.0
    )
    
    max_scale: FloatProperty(
        name="Max Scale",
        default=1.0, min=0.2, max=3.0
    )
    
    height_above_plane: FloatProperty(
        name="Height Above Plane",
        default=0.05, min=0.0, max=1.0
    )
    
    # ===== COLLISION SETTINGS =====
    enable_collision_detection: BoolProperty(
        name="Collision Detection",
        description="Detect and resolve overlapping objects",
        default=True
    )
    
    collision_iterations: IntProperty(
        name="Resolution Iterations",
        description="Number of iterations to resolve collisions",
        default=10, min=1, max=50
    )
    
    collision_padding: FloatProperty(
        name="Collision Padding",
        description="Extra space between objects (0 = touching)",
        default=0.02, min=0.0, max=0.5
    )
    
    # ===== COMPOSITION LAYOUT MODE =====
    layout_mode: EnumProperty(
        name="Layout Mode",
        description="How primitives are arranged spatially",
        items=[
            ('RANDOM', "Random", "Randomly distributed with minimum spacing"),
            ('GROUPED', "Grouped by Type", "Same primitive types clustered together"),
            ('LINEAR', "Linear", "Arranged along lines"),
            ('GRID', "Grid", "Regular grid pattern with variations"),
            ('RADIAL', "Radial", "Circular/spiral arrangement"),
            ('RULE_OF_THIRDS', "Rule of Thirds", "Key elements at third intersections"),
            ('GOLDEN_SPIRAL', "Golden Spiral", "Fibonacci spiral placement"),
            ('DIAGONAL', "Diagonal Flow", "Arranged along diagonal lines"),
            ('CLUSTERED', "Organic Clusters", "Natural clustering with varied density"),
        ],
        default='RANDOM'
    )
    
    # ===== GROUPING OPTIONS =====
    enable_grouping: BoolProperty(
        name="Enable Grouping",
        description="Group same primitive types together",
        default=False
    )
    
    group_spacing: FloatProperty(
        name="Group Spacing",
        default=1.5, min=0.5, max=5.0
    )
    
    group_tightness: FloatProperty(
        name="Group Tightness",
        default=0.8, min=0.3, max=2.0
    )
    
    # ===== SORTING OPTIONS =====
    enable_sorting: BoolProperty(
        name="Enable Sorting",
        default=False
    )
    
    sort_by: EnumProperty(
        name="Sort By",
        items=[
            ('HEIGHT', "Height (Scale)", "Smaller to larger"),
            ('COLOR', "Color (Luminance)", "Dark to light"),
            ('ANGLE', "Rotation Angle", "Sort by Z rotation"),
            ('DISTANCE', "Distance from Center", "Inside to outside"),
        ],
        default='HEIGHT'
    )
    
    sort_direction: EnumProperty(
        name="Direction",
        items=[
            ('ASCENDING', "Ascending", "Small to large"),
            ('DESCENDING', "Descending", "Large to small"),
            ('ALTERNATING', "Alternating", "Alternate extremes"),
        ],
        default='ASCENDING'
    )
    
    sort_axis: EnumProperty(
        name="Sort Axis",
        items=[
            ('X', "Left to Right (X)", "Sort along X axis"),
            ('Y', "Front to Back (Y)", "Sort along Y axis"),
            ('RADIAL', "Center Outward", "Sort radially"),
            ('DIAGONAL', "Diagonal", "Sort along diagonal"),
        ],
        default='X'
    )
    
    # ===== CONTRAST RULE =====
    enable_contrast: BoolProperty(
        name="Enable Contrast",
        default=False
    )
    
    contrast_mode: EnumProperty(
        name="Contrast Mode",
        items=[
            ('SIZE', "Size Contrast", "Alternate large and small"),
            ('COLOR', "Color Contrast", "Alternate light and dark"),
            ('BOTH', "Size + Color", "Contrast both"),
            ('TYPE', "Type Contrast", "Avoid same types adjacent"),
            ('MATERIAL', "Material Contrast", "Alternate materials"),
        ],
        default='SIZE'
    )
    
    contrast_strength: FloatProperty(
        name="Contrast Strength",
        default=0.7, min=0.1, max=1.0
    )
    
    # ===== LINEARITY RULE =====
    enable_linearity: BoolProperty(
        name="Enable Linearity",
        default=False
    )
    
    line_type: EnumProperty(
        name="Line Type",
        items=[
            ('STRAIGHT', "Straight Lines", "Parallel straight lines"),
            ('CURVED', "Curved Lines", "Gentle curves"),
            ('ZIGZAG', "Zigzag", "Zigzag pattern"),
            ('WAVE', "Wave", "Sinusoidal wave"),
            ('CONVERGING', "Converging", "Lines converging"),
            ('RADIATING', "Radiating", "Lines from center"),
        ],
        default='STRAIGHT'
    )
    
    num_lines: IntProperty(
        name="Number of Lines",
        default=3, min=1, max=10
    )
    
    line_angle: FloatProperty(
        name="Line Angle",
        default=0.0, min=-90.0, max=90.0
    )
    
    # ===== ADVANCED COMPOSITION =====
    use_focal_point: BoolProperty(
        name="Focal Point",
        default=False
    )
    
    focal_point_position: EnumProperty(
        name="Focal Position",
        items=[
            ('CENTER', "Center", "Center of composition"),
            ('THIRDS_TL', "Top-Left Third", "Upper left"),
            ('THIRDS_TR', "Top-Right Third", "Upper right"),
            ('THIRDS_BL', "Bottom-Left Third", "Lower left"),
            ('THIRDS_BR', "Bottom-Right Third", "Lower right"),
            ('GOLDEN', "Golden Ratio Point", "Golden ratio"),
        ],
        default='THIRDS_BR'
    )
    
    density_falloff: EnumProperty(
        name="Density Falloff",
        items=[
            ('NONE', "Uniform", "Even density"),
            ('CENTER', "Center Dense", "Denser in center"),
            ('EDGE', "Edge Dense", "Denser at edges"),
            ('GRADIENT', "Gradient", "Gradual change"),
            ('FOCAL', "Around Focal", "Dense around focal"),
        ],
        default='NONE'
    )
    
    # ===== MATERIAL SETTINGS =====
    material_mode: EnumProperty(
        name="Material Mode",
        description="How materials are assigned",
        items=[
            ('RANDOM', "Random Mix", "Random selection of all materials"),
            ('SINGLE', "Single Type", "Use only one material type"),
            ('WEIGHTED', "Weighted", "Weighted probability distribution"),
        ],
        default='RANDOM'
    )
    
    single_material_type: EnumProperty(
        name="Material Type",
        description="Material type when using single mode",
        items=[
            ('MATTE', "Matte", "Flat, non-reflective"),
            ('SATIN', "Satin", "Soft sheen"),
            ('GLOSSY', "Glossy", "Shiny reflective"),
            ('PLASTIC', "Plastic", "Plastic with clear coat"),
            ('METAL', "Metal", "Metallic finish"),
            ('BRUSHED_METAL', "Brushed Metal", "Anisotropic metal"),
            ('WOOD', "Wood", "Wood grain texture"),
            ('GLASS', "Glass", "Transparent glass"),
            ('FROSTED_GLASS', "Frosted Glass", "Translucent glass"),
            ('CERAMIC', "Ceramic", "Ceramic/porcelain"),
            ('RUBBER', "Rubber", "Soft rubber with SSS"),
            ('SKIN', "Skin", "Skin-like SSS"),
            ('WAX', "Wax", "Waxy translucent"),
            ('MARBLE', "Marble", "Marble with veins"),
            ('JADE', "Jade", "Jade stone SSS"),
            ('FABRIC', "Fabric", "Cloth-like material"),
        ],
        default='MATTE'
    )
    
    # Material weights (for weighted mode)
    weight_matte: FloatProperty(name="Matte", default=20, min=0, max=100)
    weight_glossy: FloatProperty(name="Glossy", default=15, min=0, max=100)
    weight_plastic: FloatProperty(name="Plastic", default=15, min=0, max=100)
    weight_metal: FloatProperty(name="Metal", default=10, min=0, max=100)
    weight_glass: FloatProperty(name="Glass", default=5, min=0, max=100)
    weight_wood: FloatProperty(name="Wood", default=10, min=0, max=100)
    weight_ceramic: FloatProperty(name="Ceramic", default=10, min=0, max=100)
    weight_rubber: FloatProperty(name="Rubber", default=5, min=0, max=100)
    weight_sss: FloatProperty(name="SSS (Skin/Wax)", default=10, min=0, max=100)
    
    # ===== LIGHTING SETTINGS =====
    lighting_mode: EnumProperty(
        name="Lighting Mode",
        description="Preset lighting setup",
        items=[
            ('DEFAULT', "Default", "Balanced 4-point studio lighting"),
            ('CINEMATIC', "Cinematic", "Dramatic contrast with strong key light"),
            ('HDR', "HDR", "High dynamic range with multiple fill lights"),
            ('STADIUM', "Stadium Flood", "Intense multi-light array surrounding the scene"),
            ('GALLERY', "Gallery Exhibition", "Multiple directional spots like an art gallery"),
           
        ],
        default='CINEMATIC'
    )
    
    shadow_softness: FloatProperty(
        name="Shadow Softness",
        default=4.0, min=1.0, max=10.0
    )
    
    key_light_intensity: FloatProperty(
        name="Key Light Intensity",
        default=800, min=100, max=2000
    )
    
    # ===== FBM TEXTURE SETTINGS =====
    use_backdrop_fbm: BoolProperty(
        name="Backdrop Bump",
        description="Add subtle creases/wrinkles to backdrop using FBM noise",
        default=False
    )
    
    backdrop_fbm_strength: FloatProperty(
        name="Bump Strength",
        description="Strength of backdrop bump effect",
        default=0.1, min=0.01, max=1.0
    )
    
    backdrop_fbm_scale: FloatProperty(
        name="Bump Scale",
        description="Scale of backdrop bump pattern",
        default=3.0, min=0.5, max=20.0
    )
    
    backdrop_fbm_octaves: IntProperty(
        name="Bump Detail",
        description="Detail level of bump (octaves)",
        default=4, min=1, max=8
    )
    
    use_object_fbm: BoolProperty(
        name="Object Texturing",
        description="Add FBM-based surface variation to some objects",
        default=True
    )
    
    object_fbm_chance: FloatProperty(
        name="Texture Chance",
        description="Probability of object getting FBM texture",
        default=0.3, min=0.0, max=1.0
    )
    
    object_fbm_mode: EnumProperty(
        name="Texture Mode",
        description="How FBM affects object materials",
        items=[
            ('BUMP', "Bump Only", "Add surface bumps"),
            ('COLOR', "Color Variation", "Vary base color"),
            ('BOTH', "Bump + Color", "Both effects"),
            ('ROUGHNESS', "Roughness Variation", "Vary surface roughness"),
        ],
        default='BUMP'
    )
    
    object_fbm_strength: FloatProperty(
        name="Object Texture Strength",
        description="Strength of object texture effect",
        default=0.15, min=0.01, max=1.0
    )
    
    object_fbm_scale: FloatProperty(
        name="Object Texture Scale",
        description="Scale of object texture pattern",
        default=5.0, min=0.5, max=30.0
    )
    
    # ===== BACKDROP SETTINGS =====
    backdrop_type: EnumProperty(
        name="Backdrop Type",
        description="Type of backdrop/backplane surface",
        items=[
            ('DEFAULT', "Default Cyclorama", "Smooth curved studio backdrop"),
             ('METALLIC_PLATE', "Metallic Plate", "Brushed metal surface with dull reflections"),
            ('SSS_SKIN', "Subsurface Skin", "Organic skin-like surface with subsurface scattering"),
            ('LAKE_SURFACE', "Lake Surface", "Water surface with ripples"),
            ('CREASED_PAPER', "Creased Paper", "Paper backdrop with wrinkles and creases"),
           
        ],
        default='DEFAULT'
    )
    
    # Backdrop customization
    backdrop_use_custom_color: BoolProperty(
        name="Custom Color",
        description="Override backdrop color instead of using palette",
        default=False
    )
    
    backdrop_custom_color: FloatVectorProperty(
        name="Backdrop Color",
        description="Custom backdrop albedo color",
        subtype='COLOR',
        default=(0.8, 0.8, 0.8),
        min=0.0, max=1.0
    )
    
    backdrop_texture_scale: FloatProperty(
        name="Texture Scale",
        description="Scale of backdrop texture pattern",
        default=1.0, min=0.1, max=10.0
    )
    
    backdrop_bump_strength: FloatProperty(
        name="Bump Strength",
        description="Strength of backdrop surface bumps/displacement",
        default=0.5, min=0.0, max=2.0
    )
    
    backdrop_roughness: FloatProperty(
        name="Roughness",
        description="Surface roughness of backdrop",
        default=0.5, min=0.0, max=1.0
    )
    
    backdrop_glossy_amount: FloatProperty(
        name="Glossy Amount",
        description="Amount of glossy reflection (for applicable materials)",
        default=0.3, min=0.0, max=1.0
    )
    
    backdrop_use_displacement: BoolProperty(
        name="Use Displacement",
        description="Use actual mesh displacement (slower but more realistic)",
        default=False
    )
    
    # ===== SCAFFOLDING SETTINGS =====
    enable_scaffolding: BoolProperty(
        name="Enable Scaffolding",
        description="Add scaffolding network around clusters of nearby primitives",
        default=False
    )
    
    scaffolding_type: EnumProperty(
        name="Scaffolding Type",
        description="Type of scaffolding pattern",
        items=[
            ('FENCE', "Fence", "Vertical fence-like wires around clusters"),
            ('NET', "Net", "Net/mesh pattern wrapping around clusters"),
            ('SPIRAL_NET', "Spiral Net", "Spiraling net pattern"),
            ('GEODESIC_NET', "Geodesic Net", "Geodesic dome-like network"),
            ('RANDOM_WEB', "Random Web", "Organic web-like connections"),
            ('CAGE', "Wire Cage", "Simple cage around cluster bounds"),
        ],
        default='SPIRAL_NET'
    )
    
    scaffolding_material: EnumProperty(
        name="Scaffolding Material",
        description="Material type for scaffolding",
        items=[
            ('METAL', "Metal", "Metallic finish"),
            ('BRUSHED_METAL', "Brushed Metal", "Brushed metallic finish"),
            ('RUBBER', "Rubber", "Rubber material with SSS"),
            ('WOOD', "Wood", "Wood grain texture"),
            ('PLASTIC', "Plastic", "Plastic with clear coat"),
        ],
        default='METAL'
    )
    
    scaffolding_color: FloatVectorProperty(
        name="Scaffolding Color",
        description="Color of the scaffolding material",
        subtype='COLOR',
        default=(0.7, 0.7, 0.75),
        min=0.0, max=1.0
    )
    
    scaffolding_roughness: FloatProperty(
        name="Scaffolding Roughness",
        description="Surface roughness of scaffolding",
        default=0.3, min=0.0, max=1.0
    )
    
    scaffolding_wire_thickness: FloatProperty(
        name="Wire Thickness",
        description="Thickness of scaffolding wires",
        default=0.03, min=0.003, max=0.08
    )
    
    scaffolding_density: IntProperty(
        name="Wire Density",
        description="Number of wires in the scaffolding",
        default=4, min=4, max=32
    )
    
    scaffolding_cluster_distance: FloatProperty(
        name="Cluster Distance",
        description="Maximum distance between primitives to be grouped together",
        default=1.4, min=0.3, max=5.0
    )
    
    scaffolding_deviation: FloatProperty(
        name="Wire Deviation",
        description="Random deviation/wobble in wire paths",
        default=0.05, min=0.0, max=0.3
    )
    
    scaffolding_height_layers: IntProperty(
        name="Height Layers",
        description="Number of horizontal layers in the scaffolding",
        default=4, min=2, max=15
    )
    
    scaffolding_padding: FloatProperty(
        name="Padding",
        description="Extra space around primitives",
        default=0.2, min=0.0, max=0.5
    )
    
    # ===== GEMS SETTINGS =====
    enable_gems: BoolProperty(
        name="Enable Gems",
        description="Add gemstones to the scene",
        default=True
    )
    
    gem_count: IntProperty(
        name="Gem Count",
        description="Number of gems to generate",
        default=5, min=1, max=100
    )
    
    gem_ratio: FloatProperty(
        name="Gem Ratio",
        description="Gems as percentage of primitive count (0=use fixed count)",
        default=0.0, min=0.0, max=2.0
    )
    
    gem_type: EnumProperty(
        name="Gem Type",
        description="Type of gemstone to generate",
        items=[
            ('MIXED', "Mixed", "Random mix of all gem types"),
            ('DIAMOND', "Diamond", "Clear diamond (IOR 2.42)"),
            ('RUBY', "Ruby", "Red ruby (IOR 1.76)"),
            ('SAPPHIRE', "Sapphire", "Blue sapphire (IOR 1.76)"),
            ('EMERALD', "Emerald", "Green emerald (IOR 1.58)"),
            ('TOPAZ', "Topaz", "Yellow/orange topaz (IOR 1.63)"),
            ('AMETHYST', "Amethyst", "Purple amethyst (IOR 1.54)"),
            ('AQUAMARINE', "Aquamarine", "Light blue aquamarine (IOR 1.58)"),
            ('CITRINE', "Citrine", "Yellow citrine (IOR 1.55)"),
            ('PERIDOT', "Peridot", "Green peridot (IOR 1.67)"),
            ('GARNET', "Garnet", "Deep red garnet (IOR 1.74)"),
            ('OPAL', "Opal", "Iridescent opal (IOR 1.45)"),
            ('TANZANITE', "Tanzanite", "Blue-violet tanzanite (IOR 1.69)"),
        ],
        default='MIXED'
    )
    
    gem_cut: EnumProperty(
        name="Cut Style",
        description="Cut style for the gems",
        items=[
            ('MIXED', "Mixed", "Random mix of all cuts"),
            ('ROUND_BRILLIANT', "Round Brilliant", "Classic round brilliant cut"),
            ('PRINCESS', "Princess", "Square princess cut"),
            ('EMERALD_CUT', "Emerald Cut", "Rectangular step cut"),
            ('OVAL', "Oval", "Oval brilliant cut"),
            ('PEAR', "Pear", "Teardrop pear cut"),
            ('MARQUISE', "Marquise", "Football-shaped marquise cut"),
            ('CUSHION', "Cushion", "Square with rounded corners"),
            ('HEART', "Heart", "Heart-shaped cut"),
            ('TRILLION', "Trillion", "Triangular cut"),
        ],
        default='MIXED'
    )
    
    gem_min_size: FloatProperty(
        name="Min Size",
        description="Minimum gem size (carat equivalent)",
        default=0.3, min=0.1, max=2.0
    )
    
    gem_max_size: FloatProperty(
        name="Max Size",
        description="Maximum gem size (carat equivalent)",
        default=0.8, min=0.2, max=3.0
    )
    
    gem_quality: EnumProperty(
        name="Quality",
        description="Gem clarity and quality",
        items=[
            ('FLAWLESS', "Flawless", "Perfect clarity, maximum brilliance"),
            ('EXCELLENT', "Excellent", "Very high clarity"),
            ('GOOD', "Good", "Good clarity with minor inclusions"),
            ('FAIR', "Fair", "Visible inclusions, less brilliance"),
        ],
        default='EXCELLENT'
    )
    
    gem_dispersion: FloatProperty(
        name="Dispersion",
        description="Rainbow fire effect intensity",
        default=0.05, min=0.0, max=0.15
    )
    
    gem_saturation: FloatProperty(
        name="Color Saturation",
        description="Intensity of gem color",
        default=0.8, min=0.0, max=1.0
    )
    
    # ===== RENDER SETTINGS =====
    render_samples: IntProperty(
        name="Render Samples",
        default=256, min=32, max=1024
    )
    
    use_denoising: BoolProperty(
        name="Use Denoising",
        default=True
    )
    
    random_seed: IntProperty(
        name="Random Seed",
        default=0, min=0, max=9999
    )


# ===========================================
# COLOR PALETTES
# ===========================================

PALETTES = {
    'warm_sunset': {
        'background': (0.95, 0.92, 0.88),
        'colors': [
            (0.91, 0.45, 0.32), (0.96, 0.65, 0.45), (0.85, 0.35, 0.25),
            (0.98, 0.78, 0.55), (0.75, 0.28, 0.22), (0.92, 0.55, 0.38),
        ]
    },
    'ocean_calm': {
        'background': (0.94, 0.96, 0.97),
        'colors': [
            (0.25, 0.55, 0.65), (0.45, 0.72, 0.78), (0.18, 0.42, 0.55),
            (0.65, 0.82, 0.85), (0.35, 0.62, 0.72), (0.55, 0.75, 0.80),
        ]
    },
    'forest_moss': {
        'background': (0.92, 0.94, 0.90),
        'colors': [
            (0.35, 0.50, 0.35), (0.55, 0.65, 0.45), (0.28, 0.42, 0.30),
            (0.68, 0.72, 0.55), (0.45, 0.55, 0.38), (0.75, 0.78, 0.65),
        ]
    },
    'dusty_rose': {
        'background': (0.96, 0.94, 0.94),
        'colors': [
            (0.78, 0.55, 0.58), (0.88, 0.72, 0.72), (0.65, 0.42, 0.48),
            (0.92, 0.80, 0.78), (0.55, 0.35, 0.40), (0.82, 0.65, 0.65),
        ]
    },
    'monochrome': {
        'background': (0.95, 0.95, 0.95),
        'colors': [
            (0.25, 0.25, 0.28), (0.45, 0.45, 0.48), (0.60, 0.60, 0.62),
            (0.75, 0.75, 0.77), (0.35, 0.35, 0.38), (0.85, 0.85, 0.87),
        ]
    },
    'earth_tones': {
        'background': (0.94, 0.92, 0.88),
        'colors': [
            (0.55, 0.40, 0.30), (0.72, 0.58, 0.45), (0.45, 0.32, 0.25),
            (0.82, 0.72, 0.58), (0.62, 0.48, 0.35), (0.38, 0.28, 0.22),
        ]
    },
    'candy_pop': {
        'background': (0.98, 0.97, 0.96),
        'colors': [
            (0.95, 0.60, 0.70), (0.70, 0.85, 0.95), (0.95, 0.90, 0.60),
            (0.75, 0.95, 0.75), (0.85, 0.70, 0.95), (0.95, 0.80, 0.65),
        ]
    },
    'nordic_winter': {
        'background': (0.97, 0.98, 0.99),
        'colors': [
            (0.70, 0.80, 0.88), (0.55, 0.65, 0.75), (0.82, 0.88, 0.92),
            (0.45, 0.55, 0.68), (0.90, 0.92, 0.95), (0.60, 0.72, 0.82),
        ]
    },
    'golden_hour': {
        'background': (0.18, 0.12, 0.08),
        'colors': [
            (0.95, 0.75, 0.30), (0.90, 0.65, 0.20), (0.85, 0.55, 0.15),
            (0.98, 0.85, 0.50), (0.80, 0.50, 0.10), (0.95, 0.80, 0.40),
        ]
    },
    'midnight_jazz': {
        'background': (0.05, 0.04, 0.10),
        'colors': [
            (0.18, 0.12, 0.45), (0.30, 0.15, 0.50), (0.10, 0.10, 0.35),
            (0.45, 0.20, 0.55), (0.15, 0.18, 0.50), (0.25, 0.10, 0.40),
        ]
    },
    'desert_sand': {
        'background': (0.96, 0.92, 0.85),
        'colors': [
            (0.85, 0.72, 0.50), (0.78, 0.58, 0.32), (0.90, 0.55, 0.20),
            (0.92, 0.80, 0.60), (0.70, 0.48, 0.25), (0.88, 0.68, 0.38),
        ]
    },
    'arctic_aurora': {
        'background': (0.04, 0.06, 0.12),
        'colors': [
            (0.15, 0.85, 0.55), (0.40, 0.25, 0.80), (0.20, 0.80, 0.90),
            (0.10, 0.65, 0.45), (0.55, 0.30, 0.90), (0.30, 0.90, 0.75),
        ]
    },
    'vintage_cream': {
        'background': (0.96, 0.94, 0.90),
        'colors': [
            (0.95, 0.92, 0.82), (0.72, 0.68, 0.55), (0.82, 0.65, 0.62),
            (0.88, 0.85, 0.75), (0.75, 0.72, 0.60), (0.90, 0.78, 0.72),
        ]
    },
    'tropical_punch': {
        'background': (0.98, 0.98, 0.95),
        'colors': [
            (0.95, 0.70, 0.20), (0.92, 0.25, 0.55), (0.45, 0.90, 0.25),
            (0.98, 0.55, 0.15), (0.85, 0.20, 0.60), (0.55, 0.95, 0.40),
        ]
    },
    'slate_storm': {
        'background': (0.10, 0.11, 0.13),
        'colors': [
            (0.30, 0.32, 0.35), (0.45, 0.47, 0.50), (0.20, 0.35, 0.38),
            (0.38, 0.40, 0.43), (0.55, 0.57, 0.58), (0.25, 0.30, 0.35),
        ]
    },
}


# ===========================================
# MATERIAL CREATION FUNCTIONS
# ===========================================

def create_material_matte(color, name):
    """Create a flat matte material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.75, 0.95)
    principled.inputs['Specular IOR Level'].default_value = 0.2
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_satin(color, name):
    """Create a satin finish material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.35, 0.55)
    principled.inputs['Specular IOR Level'].default_value = 0.4
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_glossy(color, name):
    """Create a glossy reflective material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.05, 0.2)
    principled.inputs['Specular IOR Level'].default_value = 0.5
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_plastic(color, name):
    """Create a plastic material with clear coat"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.25, 0.45)
    principled.inputs['Specular IOR Level'].default_value = 0.5
    principled.inputs['Coat Weight'].default_value = 0.4
    principled.inputs['Coat Roughness'].default_value = 0.1
    # Slight subsurface for plastic
    principled.inputs['Subsurface Weight'].default_value = 0.05
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_metal(color, name):
    """Create a polished metal material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    # Metals tint the reflection with their color
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Metallic'].default_value = 1.0
    principled.inputs['Roughness'].default_value = random.uniform(0.1, 0.35)
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_brushed_metal(color, name):
    """Create a brushed metal with anisotropic reflections"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Metallic'].default_value = 1.0
    principled.inputs['Roughness'].default_value = random.uniform(0.25, 0.4)
    principled.inputs['Anisotropic'].default_value = 0.8
    principled.inputs['Anisotropic Rotation'].default_value = random.uniform(0, 0.5)
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_wood(color, name):
    """Create a wood material with procedural grain"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (500, 0)
    
    # Wood grain using wave texture
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-400, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-200, 0)
    mapping.inputs['Scale'].default_value = (8, 8, 8)
    
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (0, 100)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 2.0
    wave.inputs['Distortion'].default_value = 8.0
    wave.inputs['Detail'].default_value = 2.0
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (0, -100)
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 6.0
    
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (200, 0)
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.3
    
    # Wood colors (darker and lighter versions)
    wood_base = (color[0] * 0.6, color[1] * 0.4, color[2] * 0.25)
    wood_light = (color[0] * 0.9, color[1] * 0.7, color[2] * 0.45)
    
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (200, 200)
    color_ramp.color_ramp.elements[0].color = (*wood_base, 1.0)
    color_ramp.color_ramp.elements[1].color = (*wood_light, 1.0)
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(wave.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], mix.inputs['Color1'])
    links.new(noise.outputs['Fac'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], principled.inputs['Base Color'])
    
    principled.inputs['Roughness'].default_value = random.uniform(0.4, 0.7)
    principled.inputs['Specular IOR Level'].default_value = 0.3
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_glass(color, name):
    """Create a transparent glass material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    # Tinted glass - ensure color is properly formatted
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = 0.0
    principled.inputs['IOR'].default_value = 1.45
    principled.inputs['Transmission Weight'].default_value = 1.0
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Enable transparency in material settings (Blender 4.x compatible)
    mat.blend_method = 'HASHED'
    # shadow_method removed in Blender 4.0+, use try/except for compatibility
    try:
        mat.shadow_method = 'HASHED'
    except AttributeError:
        pass  # Blender 4.0+ handles shadows automatically
    
    return mat


def create_material_frosted_glass(color, name):
    """Create a frosted/translucent glass material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.3, 0.5)
    principled.inputs['IOR'].default_value = 1.45
    principled.inputs['Transmission Weight'].default_value = 0.9
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Blender 4.x compatible transparency settings
    mat.blend_method = 'HASHED'
    try:
        mat.shadow_method = 'HASHED'
    except AttributeError:
        pass  # Blender 4.0+ handles shadows automatically
    
    return mat


def create_material_ceramic(color, name):
    """Create a ceramic/porcelain material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.15, 0.35)
    principled.inputs['Specular IOR Level'].default_value = 0.6
    principled.inputs['Coat Weight'].default_value = 0.5
    principled.inputs['Coat Roughness'].default_value = 0.05
    # Ceramic SSS
    principled.inputs['Subsurface Weight'].default_value = 0.15
    principled.inputs['Subsurface Radius'].default_value = Vector((0.5, 0.3, 0.2))
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_rubber(color, name):
    """Create a rubber material with strong SSS"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.6, 0.85)
    principled.inputs['Specular IOR Level'].default_value = 0.3
    # Strong SSS for rubber
    principled.inputs['Subsurface Weight'].default_value = 0.4
    principled.inputs['Subsurface Radius'].default_value = Vector((0.8, 0.5, 0.3))
    principled.inputs['Subsurface Scale'].default_value = 0.1
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_skin(color, name):
    """Create a skin-like material with realistic SSS"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    
    # Skin-like color adjustment
    skin_color = (
        min(1.0, color[0] * 1.1),
        color[1] * 0.85,
        color[2] * 0.75
    )
    principled.inputs['Base Color'].default_value = (skin_color[0], skin_color[1], skin_color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.4, 0.6)
    principled.inputs['Specular IOR Level'].default_value = 0.4
    # Skin SSS settings
    principled.inputs['Subsurface Weight'].default_value = 0.5
    principled.inputs['Subsurface Radius'].default_value = Vector((1.0, 0.35, 0.15))
    principled.inputs['Subsurface Scale'].default_value = 0.05
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_wax(color, name):
    """Create a waxy translucent material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.3, 0.5)
    principled.inputs['Specular IOR Level'].default_value = 0.4
    # Strong SSS for wax
    principled.inputs['Subsurface Weight'].default_value = 0.7
    principled.inputs['Subsurface Radius'].default_value = Vector((1.2, 0.8, 0.4))
    principled.inputs['Subsurface Scale'].default_value = 0.15
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_marble(color, name):
    """Create a marble material with veins"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (500, 0)
    
    # Marble veins using noise
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-400, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-200, 0)
    mapping.inputs['Scale'].default_value = (3, 3, 3)
    
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (0, 100)
    noise1.inputs['Scale'].default_value = 4.0
    noise1.inputs['Detail'].default_value = 8.0
    noise1.inputs['Distortion'].default_value = 1.5
    
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (0, -100)
    noise2.inputs['Scale'].default_value = 12.0
    noise2.inputs['Detail'].default_value = 4.0
    
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (200, 0)
    # Base marble color (lighter)
    base_color = tuple(min(1.0, c * 1.3) for c in color)
    # Vein color (darker)
    vein_color = tuple(c * 0.4 for c in color)
    color_ramp.color_ramp.elements[0].color = (*base_color, 1.0)
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[1].color = (*vein_color, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.6
    
    mix = nodes.new('ShaderNodeMath')
    mix.location = (100, 0)
    mix.operation = 'MULTIPLY'
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(noise1.outputs['Fac'], mix.inputs[0])
    links.new(noise2.outputs['Fac'], mix.inputs[1])
    links.new(mix.outputs['Value'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    
    principled.inputs['Roughness'].default_value = random.uniform(0.1, 0.3)
    principled.inputs['Specular IOR Level'].default_value = 0.5
    principled.inputs['Subsurface Weight'].default_value = 0.2
    principled.inputs['Subsurface Radius'].default_value = Vector((0.6, 0.4, 0.3))
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_jade(color, name):
    """Create a jade stone material with deep SSS"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    
    # Jade green tint
    jade_color = (
        color[0] * 0.5,
        min(1.0, color[1] * 1.2),
        color[2] * 0.6
    )
    principled.inputs['Base Color'].default_value = (jade_color[0], jade_color[1], jade_color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.15, 0.35)
    principled.inputs['Specular IOR Level'].default_value = 0.5
    # Deep SSS for jade
    principled.inputs['Subsurface Weight'].default_value = 0.6
    principled.inputs['Subsurface Radius'].default_value = Vector((0.3, 0.8, 0.3))
    principled.inputs['Subsurface Scale'].default_value = 0.2
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_material_fabric(color, name):
    """Create a fabric/cloth material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (500, 0)
    
    # Fabric texture
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-200, 0)
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (0, 0)
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 4.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (200, -100)
    bump.inputs['Strength'].default_value = 0.3
    
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = random.uniform(0.7, 0.95)
    principled.inputs['Specular IOR Level'].default_value = 0.15
    principled.inputs['Sheen Weight'].default_value = 0.5
    
    # Sheen Tint changed from float to color in Blender 4.0
    # Check input type and assign accordingly
    sheen_tint = principled.inputs.get('Sheen Tint')
    if sheen_tint is not None:
        if sheen_tint.type == 'RGBA':
            # Blender 4.0+ expects a color
            sheen_tint.default_value = (color[0], color[1], color[2], 1.0)
        else:
            # Blender 3.x expects a float
            sheen_tint.default_value = 0.5
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


# ===========================================
# FBM (FRACTAL BROWNIAN MOTION) FUNCTIONS
# ===========================================

def create_fbm_node_group():
    """Create a reusable FBM noise node group"""
    # Remove existing if present (to ensure fresh state)
    if "FBM_Noise" in bpy.data.node_groups:
        # Check if it's being used - if so, return it
        ng = bpy.data.node_groups["FBM_Noise"]
        if ng.users > 0:
            return ng
        else:
            bpy.data.node_groups.remove(ng)
    
    # Create new node group
    fbm_group = bpy.data.node_groups.new("FBM_Noise", 'ShaderNodeTree')
    
    # Create group inputs/outputs
    group_inputs = fbm_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-800, 0)
    
    group_outputs = fbm_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (600, 0)
    
    # Define inputs
    fbm_group.interface.new_socket(name="Vector", in_out='INPUT', socket_type='NodeSocketVector')
    fbm_group.interface.new_socket(name="Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    fbm_group.interface.new_socket(name="Octaves", in_out='INPUT', socket_type='NodeSocketFloat')
    fbm_group.interface.new_socket(name="Roughness", in_out='INPUT', socket_type='NodeSocketFloat')
    
    # Define outputs
    fbm_group.interface.new_socket(name="Value", in_out='OUTPUT', socket_type='NodeSocketFloat')
    fbm_group.interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
    
    # Set default values for inputs
    for item in fbm_group.interface.items_tree:
        if item.name == "Scale" and hasattr(item, 'default_value'):
            item.default_value = 5.0
        elif item.name == "Octaves" and hasattr(item, 'default_value'):
            item.default_value = 4.0
        elif item.name == "Roughness" and hasattr(item, 'default_value'):
            item.default_value = 0.5
    
    # Create noise layers (simulating FBM with multiple noise textures)
    noise1 = fbm_group.nodes.new('ShaderNodeTexNoise')
    noise1.location = (-400, 200)
    noise1.inputs['Detail'].default_value = 2.0
    noise1.inputs['Roughness'].default_value = 0.5
    
    noise2 = fbm_group.nodes.new('ShaderNodeTexNoise')
    noise2.location = (-400, 0)
    noise2.inputs['Detail'].default_value = 4.0
    noise2.inputs['Roughness'].default_value = 0.5
    
    noise3 = fbm_group.nodes.new('ShaderNodeTexNoise')
    noise3.location = (-400, -200)
    noise3.inputs['Detail'].default_value = 8.0
    noise3.inputs['Roughness'].default_value = 0.5
    
    noise4 = fbm_group.nodes.new('ShaderNodeTexNoise')
    noise4.location = (-400, -400)
    noise4.inputs['Detail'].default_value = 16.0
    noise4.inputs['Roughness'].default_value = 0.5
    
    # Scale multipliers for each octave
    scale_mult1 = fbm_group.nodes.new('ShaderNodeMath')
    scale_mult1.location = (-600, 200)
    scale_mult1.operation = 'MULTIPLY'
    scale_mult1.inputs[1].default_value = 1.0
    
    scale_mult2 = fbm_group.nodes.new('ShaderNodeMath')
    scale_mult2.location = (-600, 0)
    scale_mult2.operation = 'MULTIPLY'
    scale_mult2.inputs[1].default_value = 2.0
    
    scale_mult3 = fbm_group.nodes.new('ShaderNodeMath')
    scale_mult3.location = (-600, -200)
    scale_mult3.operation = 'MULTIPLY'
    scale_mult3.inputs[1].default_value = 4.0
    
    scale_mult4 = fbm_group.nodes.new('ShaderNodeMath')
    scale_mult4.location = (-600, -400)
    scale_mult4.operation = 'MULTIPLY'
    scale_mult4.inputs[1].default_value = 8.0
    
    # Weight each octave (decreasing amplitude)
    weight1 = fbm_group.nodes.new('ShaderNodeMath')
    weight1.location = (-200, 200)
    weight1.operation = 'MULTIPLY'
    weight1.inputs[1].default_value = 0.5
    
    weight2 = fbm_group.nodes.new('ShaderNodeMath')
    weight2.location = (-200, 0)
    weight2.operation = 'MULTIPLY'
    weight2.inputs[1].default_value = 0.25
    
    weight3 = fbm_group.nodes.new('ShaderNodeMath')
    weight3.location = (-200, -200)
    weight3.operation = 'MULTIPLY'
    weight3.inputs[1].default_value = 0.125
    
    weight4 = fbm_group.nodes.new('ShaderNodeMath')
    weight4.location = (-200, -400)
    weight4.operation = 'MULTIPLY'
    weight4.inputs[1].default_value = 0.0625
    
    # Add octaves together
    add1 = fbm_group.nodes.new('ShaderNodeMath')
    add1.location = (0, 100)
    add1.operation = 'ADD'
    
    add2 = fbm_group.nodes.new('ShaderNodeMath')
    add2.location = (0, -100)
    add2.operation = 'ADD'
    
    add3 = fbm_group.nodes.new('ShaderNodeMath')
    add3.location = (200, 0)
    add3.operation = 'ADD'
    
    # Normalize result
    normalize = fbm_group.nodes.new('ShaderNodeMath')
    normalize.location = (400, 0)
    normalize.operation = 'MULTIPLY'
    normalize.inputs[1].default_value = 1.0667  # Normalize to ~0-1 range
    
    # Create color output via color ramp
    color_ramp = fbm_group.nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (400, -150)
    color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    color_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    
    # Link nodes
    links = fbm_group.links
    
    # Connect scale to noise nodes
    links.new(group_inputs.outputs['Scale'], scale_mult1.inputs[0])
    links.new(group_inputs.outputs['Scale'], scale_mult2.inputs[0])
    links.new(group_inputs.outputs['Scale'], scale_mult3.inputs[0])
    links.new(group_inputs.outputs['Scale'], scale_mult4.inputs[0])
    
    links.new(scale_mult1.outputs[0], noise1.inputs['Scale'])
    links.new(scale_mult2.outputs[0], noise2.inputs['Scale'])
    links.new(scale_mult3.outputs[0], noise3.inputs['Scale'])
    links.new(scale_mult4.outputs[0], noise4.inputs['Scale'])
    
    # Connect vector
    links.new(group_inputs.outputs['Vector'], noise1.inputs['Vector'])
    links.new(group_inputs.outputs['Vector'], noise2.inputs['Vector'])
    links.new(group_inputs.outputs['Vector'], noise3.inputs['Vector'])
    links.new(group_inputs.outputs['Vector'], noise4.inputs['Vector'])
    
    # Connect roughness
    links.new(group_inputs.outputs['Roughness'], noise1.inputs['Roughness'])
    links.new(group_inputs.outputs['Roughness'], noise2.inputs['Roughness'])
    links.new(group_inputs.outputs['Roughness'], noise3.inputs['Roughness'])
    links.new(group_inputs.outputs['Roughness'], noise4.inputs['Roughness'])
    
    # Weight the outputs
    links.new(noise1.outputs['Fac'], weight1.inputs[0])
    links.new(noise2.outputs['Fac'], weight2.inputs[0])
    links.new(noise3.outputs['Fac'], weight3.inputs[0])
    links.new(noise4.outputs['Fac'], weight4.inputs[0])
    
    # Sum the weighted octaves
    links.new(weight1.outputs[0], add1.inputs[0])
    links.new(weight2.outputs[0], add1.inputs[1])
    links.new(weight3.outputs[0], add2.inputs[0])
    links.new(weight4.outputs[0], add2.inputs[1])
    links.new(add1.outputs[0], add3.inputs[0])
    links.new(add2.outputs[0], add3.inputs[1])
    
    # Normalize and output
    links.new(add3.outputs[0], normalize.inputs[0])
    links.new(normalize.outputs[0], group_outputs.inputs['Value'])
    links.new(normalize.outputs[0], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], group_outputs.inputs['Color'])
    
    return fbm_group


def add_fbm_to_material(mat, settings, color):
    """Add FBM-based effects to an existing material"""
    if not settings.use_object_fbm:
        return
    
    if random.random() > settings.object_fbm_chance:
        return
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Find the principled BSDF
    principled = None
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled = node
            break
    
    if not principled:
        return
    
    # Create FBM node group instance
    fbm_group = create_fbm_node_group()
    fbm_node = nodes.new('ShaderNodeGroup')
    fbm_node.node_tree = fbm_group
    fbm_node.location = (-400, -200)
    fbm_node.inputs['Scale'].default_value = settings.object_fbm_scale
    fbm_node.inputs['Roughness'].default_value = 0.5
    
    # Texture coordinate
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, -200)
    
    links.new(tex_coord.outputs['Object'], fbm_node.inputs['Vector'])
    
    mode = settings.object_fbm_mode
    strength = settings.object_fbm_strength
    
    if mode in ['BUMP', 'BOTH']:
        # Add bump mapping
        bump = nodes.new('ShaderNodeBump')
        bump.location = (-100, -300)
        bump.inputs['Strength'].default_value = strength
        
        links.new(fbm_node.outputs['Value'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    
    if mode in ['COLOR', 'BOTH']:
        # Add color variation
        mix_color = nodes.new('ShaderNodeMix')
        mix_color.data_type = 'RGBA'
        mix_color.location = (-100, 100)
        mix_color.inputs['Factor'].default_value = strength * 0.5
        
        # Get current base color
        base_color = principled.inputs['Base Color'].default_value
        darker_color = tuple(max(0, c * 0.7) for c in base_color[:3]) + (1.0,)
        
        mix_color.inputs['A'].default_value = base_color
        mix_color.inputs['B'].default_value = darker_color
        
        links.new(fbm_node.outputs['Value'], mix_color.inputs['Factor'])
        links.new(mix_color.outputs['Result'], principled.inputs['Base Color'])
    
    if mode == 'ROUGHNESS':
        # Add roughness variation
        current_roughness = principled.inputs['Roughness'].default_value
        
        map_range = nodes.new('ShaderNodeMapRange')
        map_range.location = (-100, -100)
        map_range.inputs['From Min'].default_value = 0.0
        map_range.inputs['From Max'].default_value = 1.0
        map_range.inputs['To Min'].default_value = max(0, current_roughness - strength)
        map_range.inputs['To Max'].default_value = min(1, current_roughness + strength)
        
        links.new(fbm_node.outputs['Value'], map_range.inputs['Value'])
        links.new(map_range.outputs['Result'], principled.inputs['Roughness'])


def create_material(color, name, material_type):
    """Create material based on type"""
    creators = {
        'MATTE': create_material_matte,
        'SATIN': create_material_satin,
        'GLOSSY': create_material_glossy,
        'PLASTIC': create_material_plastic,
        'METAL': create_material_metal,
        'BRUSHED_METAL': create_material_brushed_metal,
        'WOOD': create_material_wood,
        'GLASS': create_material_glass,
        'FROSTED_GLASS': create_material_frosted_glass,
        'CERAMIC': create_material_ceramic,
        'RUBBER': create_material_rubber,
        'SKIN': create_material_skin,
        'WAX': create_material_wax,
        'MARBLE': create_material_marble,
        'JADE': create_material_jade,
        'FABRIC': create_material_fabric,
    }
    
    creator = creators.get(material_type, create_material_matte)
    return creator(color, name)


def get_random_material_type(settings):
    """Get a random material type based on settings"""
    if settings.material_mode == 'SINGLE':
        return settings.single_material_type
    
    elif settings.material_mode == 'WEIGHTED':
        weights = [
            ('MATTE', settings.weight_matte),
            ('GLOSSY', settings.weight_glossy),
            ('PLASTIC', settings.weight_plastic),
            ('METAL', settings.weight_metal),
            ('GLASS', settings.weight_glass),
            ('WOOD', settings.weight_wood),
            ('CERAMIC', settings.weight_ceramic),
            ('RUBBER', settings.weight_rubber),
            ('SKIN', settings.weight_sss / 2),
            ('WAX', settings.weight_sss / 2),
        ]
        total = sum(w for _, w in weights)
        if total == 0:
            return 'MATTE'
        
        r = random.uniform(0, total)
        cumulative = 0
        for mat_type, weight in weights:
            cumulative += weight
            if r <= cumulative:
                return mat_type
        return 'MATTE'
    
    else:  # RANDOM
        all_types = [
            'MATTE', 'SATIN', 'GLOSSY', 'PLASTIC', 'METAL', 'BRUSHED_METAL',
            'WOOD', 'GLASS', 'FROSTED_GLASS', 'CERAMIC', 'RUBBER', 'SKIN',
            'WAX', 'MARBLE', 'JADE', 'FABRIC'
        ]
        return random.choice(all_types)


# ===========================================
# COLLISION DETECTION AND RESOLUTION
# ===========================================

def get_object_bounding_sphere(obj):
    """Get bounding sphere (center and radius) for an object"""
    # Get world-space bounding box corners
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    
    # Calculate center
    center = sum(bbox_corners, Vector()) / 8
    
    # Calculate radius (max distance from center to any corner)
    radius = max((corner - center).length for corner in bbox_corners)
    
    return center, radius


def get_object_bounding_box(obj):
    """Get axis-aligned bounding box in world space"""
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    
    min_x = min(c.x for c in bbox_corners)
    max_x = max(c.x for c in bbox_corners)
    min_y = min(c.y for c in bbox_corners)
    max_y = max(c.y for c in bbox_corners)
    min_z = min(c.z for c in bbox_corners)
    max_z = max(c.z for c in bbox_corners)
    
    return (min_x, max_x, min_y, max_y, min_z, max_z)


def check_sphere_collision(center1, radius1, center2, radius2, padding=0):
    """Check if two spheres collide"""
    distance = (center1 - center2).length
    min_distance = radius1 + radius2 + padding
    
    if distance < min_distance:
        overlap = min_distance - distance
        return True, overlap
    return False, 0


def check_box_collision(box1, box2, padding=0):
    """Check if two axis-aligned boxes collide"""
    min_x1, max_x1, min_y1, max_y1, min_z1, max_z1 = box1
    min_x2, max_x2, min_y2, max_y2, min_z2, max_z2 = box2
    
    # Add padding
    min_x1 -= padding
    max_x1 += padding
    min_y1 -= padding
    max_y1 += padding
    
    # Check overlap on all axes
    x_overlap = max_x1 > min_x2 and max_x2 > min_x1
    y_overlap = max_y1 > min_y2 and max_y2 > min_y1
    z_overlap = max_z1 > min_z2 and max_z2 > min_z1
    
    return x_overlap and y_overlap and z_overlap


def resolve_collision(obj1, obj2, settings):
    """Resolve collision between two objects by moving obj2"""
    center1, radius1 = get_object_bounding_sphere(obj1)
    center2, radius2 = get_object_bounding_sphere(obj2)
    
    collides, overlap = check_sphere_collision(center1, radius1, center2, radius2, settings.collision_padding)
    
    if not collides:
        return False
    
    # Calculate separation direction
    direction = center2 - center1
    if direction.length < 0.001:
        # Objects at same position, push in random direction
        direction = Vector((random.uniform(-1, 1), random.uniform(-1, 1), 0))
    direction.normalize()
    
    # Move obj2 away by the overlap amount plus a small margin
    separation = direction * (overlap + 0.01)
    
    # Only move in XY plane (keep Z as is for sitting on plane)
    obj2.location.x += separation.x
    obj2.location.y += separation.y
    
    return True


def resolve_all_collisions(objects, settings):
    """Iteratively resolve all collisions"""
    if not settings.enable_collision_detection:
        return 0
    
    total_adjustments = 0
    
    for iteration in range(settings.collision_iterations):
        collisions_found = 0
        
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i + 1:]:
                if resolve_collision(obj1, obj2, settings):
                    collisions_found += 1
        
        total_adjustments += collisions_found
        
        if collisions_found == 0:
            break
    
    # Ensure objects stay within bounds
    for obj in objects:
        obj.location.x = max(-settings.spread_x * 1.2, min(settings.spread_x * 1.2, obj.location.x))
        obj.location.y = max(-settings.spread_y * 1.2, min(settings.spread_y * 1.2, obj.location.y))
    
    return total_adjustments


# ===========================================
# COMPOSITION RULE FUNCTIONS
# ===========================================

def get_color_luminance(color):
    """Calculate perceived luminance"""
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]


def get_focal_point_position(settings):
    """Get focal point position"""
    sx, sy = settings.spread_x, settings.spread_y
    positions = {
        'CENTER': (0, 0),
        'THIRDS_TL': (-sx * 0.33, sy * 0.33),
        'THIRDS_TR': (sx * 0.33, sy * 0.33),
        'THIRDS_BL': (-sx * 0.33, -sy * 0.33),
        'THIRDS_BR': (sx * 0.33, -sy * 0.33),
        'GOLDEN': (sx * 0.382, -sy * 0.382),
    }
    return positions.get(settings.focal_point_position, (0, 0))


def generate_grouped_positions(settings, enabled_types):
    """Generate positions with primitives grouped by type"""
    positions = []
    type_assignments = []
    
    num_types = len(enabled_types)
    prims_per_type = settings.num_primitives // num_types
    remainder = settings.num_primitives % num_types
    
    if num_types <= 3:
        group_centers = [
            Vector((-settings.spread_x * 0.5 + i * settings.spread_x / max(1, num_types - 1), 0, 0))
            if num_types > 1 else Vector((0, 0, 0))
            for i in range(num_types)
        ]
    else:
        cols = math.ceil(math.sqrt(num_types))
        rows = math.ceil(num_types / cols)
        group_centers = []
        for i in range(num_types):
            col = i % cols
            row = i // cols
            x = -settings.spread_x * 0.5 + col * settings.spread_x / max(1, cols - 1) if cols > 1 else 0
            y = -settings.spread_y * 0.5 + row * settings.spread_y / max(1, rows - 1) if rows > 1 else 0
            group_centers.append(Vector((x, y, 0)))
    
    for type_idx, prim_type in enumerate(enabled_types):
        center = group_centers[type_idx]
        count = prims_per_type + (1 if type_idx < remainder else 0)
        
        for i in range(count):
            angle = random.uniform(0, math.pi * 2)
            radius = random.uniform(0, settings.group_tightness)
            offset = Vector((math.cos(angle) * radius, math.sin(angle) * radius, 0))
            pos = center + offset
            pos.x = max(-settings.spread_x, min(settings.spread_x, pos.x))
            pos.y = max(-settings.spread_y, min(settings.spread_y, pos.y))
            positions.append(pos)
            type_assignments.append(prim_type)
    
    return positions, type_assignments


def generate_linear_positions(settings, count):
    """Generate positions along lines"""
    positions = []
    angle_rad = math.radians(settings.line_angle)
    num_lines = settings.num_lines
    prims_per_line = count // num_lines
    remainder = count % num_lines
    
    for line_idx in range(num_lines):
        line_count = prims_per_line + (1 if line_idx < remainder else 0)
        line_offset = (line_idx - (num_lines - 1) / 2) * (settings.spread_y * 2 / max(1, num_lines))
        
        for i in range(line_count):
            t = (i / max(1, line_count - 1)) - 0.5 if line_count > 1 else 0
            
            if settings.line_type == 'STRAIGHT':
                x, y = t * settings.spread_x * 2, line_offset
            elif settings.line_type == 'CURVED':
                x = t * settings.spread_x * 2
                y = line_offset + math.sin(t * math.pi) * settings.spread_y * 0.3
            elif settings.line_type == 'ZIGZAG':
                x = t * settings.spread_x * 2
                y = line_offset + (1 if i % 2 == 0 else -1) * settings.spread_y * 0.2
            elif settings.line_type == 'WAVE':
                x = t * settings.spread_x * 2
                y = line_offset + math.sin(t * math.pi * 3) * settings.spread_y * 0.25
            elif settings.line_type == 'CONVERGING':
                convergence = 1 - abs(t) * 0.6
                x, y = t * settings.spread_x * 2, line_offset * convergence
            elif settings.line_type == 'RADIATING':
                angle = (line_idx / num_lines) * math.pi * 2
                dist = (i / max(1, line_count - 1)) * settings.spread_x if line_count > 1 else 0
                x, y = math.cos(angle) * dist, math.sin(angle) * dist
            else:
                x, y = t * settings.spread_x * 2, line_offset
            
            rx = x * math.cos(angle_rad) - y * math.sin(angle_rad) + random.uniform(-0.1, 0.1)
            ry = x * math.sin(angle_rad) + y * math.cos(angle_rad) + random.uniform(-0.1, 0.1)
            positions.append(Vector((rx, ry, 0)))
    
    return positions


def generate_grid_positions(settings, count):
    """Generate positions on a grid"""
    positions = []
    cols = math.ceil(math.sqrt(count * settings.spread_x / settings.spread_y))
    rows = math.ceil(count / cols)
    cell_width = settings.spread_x * 2 / cols
    cell_height = settings.spread_y * 2 / rows
    
    idx = 0
    for row in range(rows):
        for col in range(cols):
            if idx >= count:
                break
            x = -settings.spread_x + (col + 0.5) * cell_width + random.uniform(-cell_width * 0.2, cell_width * 0.2)
            y = -settings.spread_y + (row + 0.5) * cell_height + random.uniform(-cell_height * 0.2, cell_height * 0.2)
            positions.append(Vector((x, y, 0)))
            idx += 1
    
    return positions


def generate_radial_positions(settings, count):
    """Generate positions in radial pattern"""
    positions = []
    rings = math.ceil(math.sqrt(count / math.pi))
    placed = 0
    
    for ring in range(rings):
        if placed >= count:
            break
        radius = (ring + 1) / rings * min(settings.spread_x, settings.spread_y)
        circumference = 2 * math.pi * radius
        prims_in_ring = max(1, int(circumference / 0.8))
        prims_in_ring = min(prims_in_ring, count - placed)
        
        for i in range(prims_in_ring):
            angle = (i / prims_in_ring) * math.pi * 2 + ring * 0.5
            x = math.cos(angle) * radius + random.uniform(-0.1, 0.1)
            y = math.sin(angle) * radius + random.uniform(-0.1, 0.1)
            positions.append(Vector((x, y, 0)))
            placed += 1
    
    return positions


def generate_golden_spiral_positions(settings, count):
    """Generate positions along golden spiral"""
    positions = []
    golden_angle = math.pi * (3 - math.sqrt(5))
    max_radius = min(settings.spread_x, settings.spread_y)
    
    for i in range(count):
        angle = i * golden_angle
        radius = math.sqrt(i / count) * max_radius
        positions.append(Vector((math.cos(angle) * radius, math.sin(angle) * radius, 0)))
    
    return positions


def generate_rule_of_thirds_positions(settings, count):
    """Generate positions emphasizing rule of thirds"""
    positions = []
    thirds_points = [
        Vector((-settings.spread_x * 0.33, settings.spread_y * 0.33, 0)),
        Vector((settings.spread_x * 0.33, settings.spread_y * 0.33, 0)),
        Vector((-settings.spread_x * 0.33, -settings.spread_y * 0.33, 0)),
        Vector((settings.spread_x * 0.33, -settings.spread_y * 0.33, 0)),
    ]
    
    key_count = min(count // 4, 4)
    for i in range(key_count):
        point = thirds_points[i % 4]
        positions.append(point + Vector((random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), 0)))
    
    for i in range(count - key_count):
        if random.random() < 0.6:
            if random.random() < 0.5:
                x = random.choice([-1, 1]) * settings.spread_x * 0.33
                y = random.uniform(-settings.spread_y, settings.spread_y)
            else:
                x = random.uniform(-settings.spread_x, settings.spread_x)
                y = random.choice([-1, 1]) * settings.spread_y * 0.33
        else:
            x = random.uniform(-settings.spread_x, settings.spread_x)
            y = random.uniform(-settings.spread_y, settings.spread_y)
        positions.append(Vector((x + random.uniform(-0.2, 0.2), y + random.uniform(-0.2, 0.2), 0)))
    
    return positions


def generate_diagonal_positions(settings, count):
    """Generate positions along diagonals"""
    positions = []
    num_diagonals = 5
    prims_per_diag = count // num_diagonals
    remainder = count % num_diagonals
    
    for diag_idx in range(num_diagonals):
        diag_count = prims_per_diag + (1 if diag_idx < remainder else 0)
        offset = (diag_idx - (num_diagonals - 1) / 2) * 1.5
        
        for i in range(diag_count):
            t = (i / max(1, diag_count - 1)) - 0.5 if diag_count > 1 else 0
            x = max(-settings.spread_x, min(settings.spread_x, t * settings.spread_x * 2 + offset * 0.5 + random.uniform(-0.2, 0.2)))
            y = max(-settings.spread_y, min(settings.spread_y, t * settings.spread_y * 2 - offset * 0.5 + random.uniform(-0.2, 0.2)))
            positions.append(Vector((x, y, 0)))
    
    return positions


def generate_clustered_positions(settings, count):
    """Generate organic clusters"""
    positions = []
    num_clusters = random.randint(3, 6)
    cluster_centers = [(Vector((random.uniform(-settings.spread_x * 0.7, settings.spread_x * 0.7),
                                random.uniform(-settings.spread_y * 0.7, settings.spread_y * 0.7), 0)),
                        random.uniform(0.5, 1.5)) for _ in range(num_clusters)]
    
    for i in range(count):
        total_size = sum(c[1] for c in cluster_centers)
        r = random.uniform(0, total_size)
        cumulative = 0
        chosen_cluster = cluster_centers[0]
        for center, size in cluster_centers:
            cumulative += size
            if r <= cumulative:
                chosen_cluster = (center, size)
                break
        
        center, size = chosen_cluster
        angle = random.uniform(0, math.pi * 2)
        radius = abs(random.gauss(0, size * 0.5))
        x = max(-settings.spread_x, min(settings.spread_x, center.x + math.cos(angle) * radius))
        y = max(-settings.spread_y, min(settings.spread_y, center.y + math.sin(angle) * radius))
        positions.append(Vector((x, y, 0)))
    
    return positions


def apply_sorting(primitives_data, settings):
    """Sort primitives based on settings"""
    if settings.sort_by == 'HEIGHT':
        key_func = lambda p: p['scale']
    elif settings.sort_by == 'COLOR':
        key_func = lambda p: get_color_luminance(p['color'])
    elif settings.sort_by == 'ANGLE':
        key_func = lambda p: p['rotation']
    else:
        key_func = lambda p: p['position'].length
    
    sorted_data = sorted(primitives_data, key=key_func)
    
    if settings.sort_direction == 'DESCENDING':
        sorted_data = list(reversed(sorted_data))
    elif settings.sort_direction == 'ALTERNATING':
        result = []
        left, right = 0, len(sorted_data) - 1
        toggle = True
        while left <= right:
            result.append(sorted_data[left] if toggle else sorted_data[right])
            left, right = (left + 1, right) if toggle else (left, right - 1)
            toggle = not toggle
        sorted_data = result
    
    positions = [p['position'] for p in primitives_data]
    if settings.sort_axis == 'X':
        positions.sort(key=lambda p: p.x)
    elif settings.sort_axis == 'Y':
        positions.sort(key=lambda p: p.y)
    elif settings.sort_axis == 'RADIAL':
        positions.sort(key=lambda p: p.length)
    else:
        positions.sort(key=lambda p: p.x + p.y)
    
    for i, data in enumerate(sorted_data):
        data['position'] = positions[i]
    
    return sorted_data


def apply_contrast(primitives_data, settings, palette_colors):
    """Apply contrast rules"""
    for i, data in enumerate(primitives_data):
        if i == 0:
            continue
        prev_data = primitives_data[i - 1]
        
        if settings.contrast_mode in ['SIZE', 'BOTH']:
            mid = (settings.min_scale + settings.max_scale) / 2
            target = settings.min_scale + (settings.max_scale - settings.min_scale) * (0.25 if prev_data['scale'] > mid else 0.75)
            data['scale'] = data['scale'] * (1 - settings.contrast_strength) + target * settings.contrast_strength
        
        if settings.contrast_mode in ['COLOR', 'BOTH']:
            prev_lum = get_color_luminance(prev_data['color'])
            best_color, best_diff = data['color'], 0
            for color in palette_colors:
                diff = abs(get_color_luminance(color) - prev_lum)
                if diff > best_diff:
                    best_diff, best_color = diff, color
            data['color'] = best_color
        
        if settings.contrast_mode == 'MATERIAL':
            data['force_material_contrast'] = True
    
    return primitives_data


def apply_density_falloff(positions, settings):
    """Filter positions based on density falloff"""
    if settings.density_falloff == 'NONE':
        return positions
    
    result = []
    for pos in positions:
        keep_prob = 1.0
        dist = pos.length / max(settings.spread_x, settings.spread_y)
        
        if settings.density_falloff == 'CENTER':
            keep_prob = 1.0 - dist * 0.5
        elif settings.density_falloff == 'EDGE':
            keep_prob = 0.5 + dist * 0.5
        elif settings.density_falloff == 'GRADIENT':
            keep_prob = 0.5 + pos.x / settings.spread_x * 0.5
        elif settings.density_falloff == 'FOCAL' and settings.use_focal_point:
            focal = Vector(get_focal_point_position(settings))
            keep_prob = 1.0 - (pos.xy - focal).length / max(settings.spread_x, settings.spread_y) * 0.6
        
        if random.random() < keep_prob:
            result.append(pos)
    
    return result


# ===========================================
# HELPER FUNCTIONS
# ===========================================

def cleanup_scene():
    """Remove all objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.node_groups:
        if block.users == 0:
            bpy.data.node_groups.remove(block)
    for col in bpy.data.collections:
        if col.name in ["Primitives", "Lights"]:
            bpy.data.collections.remove(col)


def get_enabled_primitives(settings):
    """Get list of enabled primitive types"""
    enabled = []
    if settings.use_cube: enabled.append('cube')
    if settings.use_sphere: enabled.append('sphere')
    if settings.use_cylinder: enabled.append('cylinder')
    if settings.use_cone: enabled.append('cone')
    if settings.use_torus: enabled.append('torus')
    if settings.use_ico_sphere: enabled.append('ico_sphere')
    if settings.use_capsule: enabled.append('capsule')
    if settings.use_rounded_cube: enabled.append('rounded_cube')
    return enabled if enabled else ['cube', 'sphere']


def create_backdrop_material(color, settings=None):
    """Create backdrop material based on backdrop type"""
    if settings is None:
        return create_backdrop_material_default(color, settings)
    
    backdrop_type = settings.backdrop_type
    
    # Use custom color if enabled
    if settings.backdrop_use_custom_color:
        color = tuple(settings.backdrop_custom_color)
    
    creators = {
        'DEFAULT': create_backdrop_material_default,
        'CREASED_PAPER': create_backdrop_material_paper,
        'CEMENTED_GROUND': create_backdrop_material_cement,
        'LAWN_GRASS': create_backdrop_material_grass,
        'METALLIC_PLATE': create_backdrop_material_metal,
        'SSS_SKIN': create_backdrop_material_skin,
        'LAKE_SURFACE': create_backdrop_material_water,
        'RUBBER_MAT': create_backdrop_material_rubber,
    }
    
    creator = creators.get(backdrop_type, create_backdrop_material_default)
    return creator(color, settings)


def create_backdrop_material_default(color, settings=None):
    """Create default smooth cyclorama backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (300, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    
    roughness = settings.backdrop_roughness if settings else 0.9
    principled.inputs['Roughness'].default_value = roughness
    principled.inputs['Specular IOR Level'].default_value = 0.1
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Add FBM bump if enabled
    if settings and settings.use_backdrop_fbm:
        fbm_group = create_fbm_node_group()
        fbm_node = nodes.new('ShaderNodeGroup')
        fbm_node.node_tree = fbm_group
        fbm_node.location = (-200, -200)
        fbm_node.inputs['Scale'].default_value = settings.backdrop_fbm_scale
        fbm_node.inputs['Roughness'].default_value = 0.6
        
        tex_coord = nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (-400, -200)
        
        bump = nodes.new('ShaderNodeBump')
        bump.location = (100, -200)
        bump.inputs['Strength'].default_value = settings.backdrop_fbm_strength
        bump.inputs['Distance'].default_value = 0.1
        
        links.new(tex_coord.outputs['Object'], fbm_node.inputs['Vector'])
        links.new(fbm_node.outputs['Value'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    
    return mat


def create_backdrop_material_curtain(color, settings):
    """Create folded curtain/fabric backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Curtain")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (500, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = max(0.6, settings.backdrop_roughness)
    principled.inputs['Specular IOR Level'].default_value = 0.2
    principled.inputs['Sheen Weight'].default_value = 0.4
    
    # Sheen Tint - handle Blender 4.x color type
    sheen_tint = principled.inputs.get('Sheen Tint')
    if sheen_tint is not None:
        if sheen_tint.type == 'RGBA':
            sheen_tint.default_value = (color[0], color[1], color[2], 1.0)
        else:
            sheen_tint.default_value = 0.5
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    # Create vertical fold pattern using wave texture
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-300, 200)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 3.0 * settings.backdrop_texture_scale
    wave.inputs['Distortion'].default_value = 2.5
    wave.inputs['Detail'].default_value = 4.0
    wave.inputs['Detail Scale'].default_value = 1.5
    
    # Add noise for fabric weave texture
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-300, -100)
    noise.inputs['Scale'].default_value = 80.0 * settings.backdrop_texture_scale
    noise.inputs['Detail'].default_value = 10.0
    noise.inputs['Roughness'].default_value = 0.7
    
    # Combine wave and noise for bumps
    mix_bump = nodes.new('ShaderNodeMath')
    mix_bump.location = (-100, 100)
    mix_bump.operation = 'ADD'
    
    multiply = nodes.new('ShaderNodeMath')
    multiply.location = (-100, -50)
    multiply.operation = 'MULTIPLY'
    multiply.inputs[1].default_value = 0.1
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (200, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength
    bump.inputs['Distance'].default_value = 0.15
    
    # Color variation from folds (shadows in creases)
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (0, 300)
    color_ramp.color_ramp.elements[0].position = 0.2
    color_ramp.color_ramp.elements[0].color = (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.8
    color_ramp.color_ramp.elements[1].color = (color[0], color[1], color[2], 1.0)
    
    links.new(tex_coord.outputs['Object'], wave.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(wave.outputs['Fac'], mix_bump.inputs[0])
    links.new(noise.outputs['Fac'], multiply.inputs[0])
    links.new(multiply.outputs[0], mix_bump.inputs[1])
    links.new(mix_bump.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(wave.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop_material_paper(color, settings):
    """Create creased paper backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Paper")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (500, 0)
    # Paper is usually lighter
    paper_color = (min(1.0, color[0] * 1.1), min(1.0, color[1] * 1.1), min(1.0, color[2] * 1.1))
    principled.inputs['Base Color'].default_value = (*paper_color, 1.0)
    principled.inputs['Roughness'].default_value = max(0.7, settings.backdrop_roughness)
    principled.inputs['Specular IOR Level'].default_value = 0.15
    # Slight subsurface for paper
    principled.inputs['Subsurface Weight'].default_value = 0.05
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-700, 0)
    
    # Large-scale creases using voronoi
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-400, 200)
    voronoi.feature = 'DISTANCE_TO_EDGE'
    voronoi.inputs['Scale'].default_value = 2.5 * settings.backdrop_texture_scale
    
    # Medium wrinkles using noise
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-400, 0)
    noise1.inputs['Scale'].default_value = 10.0 * settings.backdrop_texture_scale
    noise1.inputs['Detail'].default_value = 8.0
    noise1.inputs['Roughness'].default_value = 0.7
    noise1.inputs['Distortion'].default_value = 0.8
    
    # Fine paper fiber texture
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-400, -200)
    noise2.inputs['Scale'].default_value = 150.0 * settings.backdrop_texture_scale
    noise2.inputs['Detail'].default_value = 5.0
    noise2.inputs['Roughness'].default_value = 0.5
    
    # Combine crease patterns
    add1 = nodes.new('ShaderNodeMath')
    add1.location = (-150, 100)
    add1.operation = 'ADD'
    
    mult1 = nodes.new('ShaderNodeMath')
    mult1.location = (-150, -100)
    mult1.operation = 'MULTIPLY'
    mult1.inputs[1].default_value = 0.1
    
    add2 = nodes.new('ShaderNodeMath')
    add2.location = (0, 0)
    add2.operation = 'ADD'
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (200, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength * 0.8
    bump.inputs['Distance'].default_value = 0.08
    
    # Slight color variation from creases (shadows in folds)
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (0, 300)
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = (paper_color[0] * 0.88, paper_color[1] * 0.88, paper_color[2] * 0.88, 1.0)
    color_ramp.color_ramp.elements[1].position = 1.0
    color_ramp.color_ramp.elements[1].color = (*paper_color, 1.0)
    
    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], noise1.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], noise2.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], add1.inputs[0])
    links.new(noise1.outputs['Fac'], add1.inputs[1])
    links.new(noise2.outputs['Fac'], mult1.inputs[0])
    links.new(add1.outputs[0], add2.inputs[0])
    links.new(mult1.outputs[0], add2.inputs[1])
    links.new(add2.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(voronoi.outputs['Distance'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop_material_wood(color, settings):
    """Create wooden table/surface backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Wood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (600, 0)
    principled.inputs['Roughness'].default_value = settings.backdrop_roughness
    principled.inputs['Specular IOR Level'].default_value = 0.35
    
    # Add clear coat for varnished wood look
    if settings.backdrop_glossy_amount > 0.2:
        principled.inputs['Coat Weight'].default_value = settings.backdrop_glossy_amount
        principled.inputs['Coat Roughness'].default_value = 0.15
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (settings.backdrop_texture_scale * 2, settings.backdrop_texture_scale * 0.4, 1)
    
    # Wood grain using wave texture
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-350, 200)
    wave.wave_type = 'RINGS'
    wave.rings_direction = 'Y'
    wave.inputs['Scale'].default_value = 4.0
    wave.inputs['Distortion'].default_value = 12.0
    wave.inputs['Detail'].default_value = 4.0
    wave.inputs['Detail Scale'].default_value = 0.6
    
    # Noise for grain variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-350, -100)
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.65
    
    # Mix wave and noise
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-100, 100)
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.35
    
    # Wood color ramp
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (150, 200)
    # Wood colors based on input color
    wood_dark = (color[0] * 0.35, color[1] * 0.22, color[2] * 0.12)
    wood_mid = (color[0] * 0.7, color[1] * 0.5, color[2] * 0.3)
    wood_light = (min(1, color[0] * 1.1), color[1] * 0.75, color[2] * 0.45)
    color_ramp.color_ramp.elements[0].color = (*wood_dark, 1.0)
    color_ramp.color_ramp.elements[0].position = 0.2
    color_ramp.color_ramp.elements.new(0.5)
    color_ramp.color_ramp.elements[1].color = (*wood_mid, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.5
    color_ramp.color_ramp.elements[2].color = (*wood_light, 1.0)
    color_ramp.color_ramp.elements[2].position = 0.8
    
    # Bump for wood grain
    bump = nodes.new('ShaderNodeBump')
    bump.location = (350, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength * 0.4
    bump.inputs['Distance'].default_value = 0.015
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(wave.outputs['Fac'], mix.inputs['Color1'])
    links.new(noise.outputs['Fac'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(wave.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop_material_marble(color, settings):
    """Create marbled floor backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Marble")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (600, 0)
    principled.inputs['Roughness'].default_value = max(0.08, settings.backdrop_roughness * 0.4)
    principled.inputs['Specular IOR Level'].default_value = 0.5
    # Marble SSS
    principled.inputs['Subsurface Weight'].default_value = 0.2
    principled.inputs['Subsurface Radius'].default_value = Vector((0.6, 0.5, 0.4))
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (settings.backdrop_texture_scale * 2.5, settings.backdrop_texture_scale * 2.5, 1)
    
    # Primary vein pattern
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-350, 200)
    noise1.inputs['Scale'].default_value = 4.0
    noise1.inputs['Detail'].default_value = 10.0
    noise1.inputs['Roughness'].default_value = 0.65
    noise1.inputs['Distortion'].default_value = 2.0
    
    # Secondary detail noise
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-350, -50)
    noise2.inputs['Scale'].default_value = 15.0
    noise2.inputs['Detail'].default_value = 5.0
    noise2.inputs['Roughness'].default_value = 0.5
    
    # Wave for vein direction
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-350, -300)
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 2.5
    wave.inputs['Distortion'].default_value = 5.0
    wave.inputs['Detail'].default_value = 3.0
    
    # Combine patterns
    mix1 = nodes.new('ShaderNodeMath')
    mix1.location = (-100, 100)
    mix1.operation = 'MULTIPLY'
    
    mix2 = nodes.new('ShaderNodeMath')
    mix2.location = (50, 50)
    mix2.operation = 'ADD'
    
    # Marble color ramp with veins
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (200, 200)
    # Base marble color (lighter)
    marble_base = (min(1, color[0] * 1.35), min(1, color[1] * 1.35), min(1, color[2] * 1.35))
    # Vein color (darker)
    vein_color = (color[0] * 0.25, color[1] * 0.3, color[2] * 0.35)
    color_ramp.color_ramp.elements[0].color = (*marble_base, 1.0)
    color_ramp.color_ramp.elements[0].position = 0.35
    color_ramp.color_ramp.elements[1].color = (*vein_color, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.65
    
    # Bump for polished surface
    bump = nodes.new('ShaderNodeBump')
    bump.location = (350, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength * 0.15
    bump.inputs['Distance'].default_value = 0.008
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    links.new(noise1.outputs['Fac'], mix1.inputs[0])
    links.new(wave.outputs['Fac'], mix1.inputs[1])
    links.new(mix1.outputs[0], mix2.inputs[0])
    links.new(noise2.outputs['Fac'], mix2.inputs[1])
    links.new(mix2.outputs[0], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(noise2.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop_material_cement(color, settings):
    """Create cemented ground backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Cement")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (600, 0)
    # Cement is grayish
    cement_color = (color[0] * 0.65 + 0.25, color[1] * 0.65 + 0.25, color[2] * 0.65 + 0.25)
    principled.inputs['Base Color'].default_value = (*cement_color, 1.0)
    principled.inputs['Roughness'].default_value = max(0.7, settings.backdrop_roughness)
    principled.inputs['Specular IOR Level'].default_value = 0.2
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (settings.backdrop_texture_scale, settings.backdrop_texture_scale, 1)
    
    # Large aggregate texture
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-350, 200)
    voronoi.feature = 'F1'
    voronoi.inputs['Scale'].default_value = 10.0
    voronoi.inputs['Randomness'].default_value = 0.85
    
    # Medium surface texture
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-350, 0)
    noise1.inputs['Scale'].default_value = 25.0
    noise1.inputs['Detail'].default_value = 10.0
    noise1.inputs['Roughness'].default_value = 0.75
    
    # Fine surface detail
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-350, -200)
    noise2.inputs['Scale'].default_value = 120.0
    noise2.inputs['Detail'].default_value = 5.0
    noise2.inputs['Roughness'].default_value = 0.55
    
    # Combine textures
    mix1 = nodes.new('ShaderNodeMath')
    mix1.location = (-100, 100)
    mix1.operation = 'ADD'
    
    mult = nodes.new('ShaderNodeMath')
    mult.location = (-100, -100)
    mult.operation = 'MULTIPLY'
    mult.inputs[1].default_value = 0.25
    
    mix2 = nodes.new('ShaderNodeMath')
    mix2.location = (50, 0)
    mix2.operation = 'ADD'
    
    # Color variation
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (200, 200)
    color_ramp.color_ramp.elements[0].color = (cement_color[0] * 0.82, cement_color[1] * 0.82, cement_color[2] * 0.82, 1.0)
    color_ramp.color_ramp.elements[1].color = (cement_color[0] * 1.08, cement_color[1] * 1.08, cement_color[2] * 1.08, 1.0)
    
    # Bump
    bump = nodes.new('ShaderNodeBump')
    bump.location = (350, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength
    bump.inputs['Distance'].default_value = 0.05
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], mix1.inputs[0])
    links.new(noise1.outputs['Fac'], mix1.inputs[1])
    links.new(noise2.outputs['Fac'], mult.inputs[0])
    links.new(mix1.outputs[0], mix2.inputs[0])
    links.new(mult.outputs[0], mix2.inputs[1])
    links.new(mix2.outputs[0], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(mix2.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop_material_grass(color, settings):
    """Create lawn grass backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Grass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (600, 0)
    principled.inputs['Roughness'].default_value = max(0.55, settings.backdrop_roughness)
    principled.inputs['Specular IOR Level'].default_value = 0.25
    # Grass SSS for translucency
    principled.inputs['Subsurface Weight'].default_value = 0.15
    principled.inputs['Subsurface Radius'].default_value = Vector((0.3, 0.5, 0.1))
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (settings.backdrop_texture_scale * 4, settings.backdrop_texture_scale * 4, 1)
    
    # Grass blade pattern using voronoi
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-350, 200)
    voronoi.feature = 'F1'
    voronoi.inputs['Scale'].default_value = 80.0
    voronoi.inputs['Randomness'].default_value = 1.0
    
    # Noise for color variation (patches)
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-350, 0)
    noise1.inputs['Scale'].default_value = 8.0
    noise1.inputs['Detail'].default_value = 6.0
    noise1.inputs['Roughness'].default_value = 0.5
    
    # Fine detail
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-350, -200)
    noise2.inputs['Scale'].default_value = 100.0
    noise2.inputs['Detail'].default_value = 5.0
    
    # Grass color ramp (green variations)
    grass_dark = (color[0] * 0.25, min(1, color[1] * 0.7 + 0.25), color[2] * 0.15)
    grass_light = (color[0] * 0.45, min(1, color[1] * 0.9 + 0.35), color[2] * 0.25)
    grass_yellow = (color[0] * 0.65 + 0.25, color[1] * 0.75 + 0.18, color[2] * 0.08)
    
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (200, 200)
    color_ramp.color_ramp.elements[0].color = (*grass_dark, 1.0)
    color_ramp.color_ramp.elements[0].position = 0.0
    # Add middle element for variation
    color_ramp.color_ramp.elements.new(0.5)
    color_ramp.color_ramp.elements[1].color = (*grass_light, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.5
    color_ramp.color_ramp.elements[2].color = (*grass_yellow, 1.0)
    color_ramp.color_ramp.elements[2].position = 1.0
    
    # Combine for bump
    mix = nodes.new('ShaderNodeMath')
    mix.location = (0, 0)
    mix.operation = 'ADD'
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (350, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength * 0.9
    bump.inputs['Distance'].default_value = 0.025
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(noise1.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(voronoi.outputs['Distance'], mix.inputs[0])
    links.new(noise2.outputs['Fac'], mix.inputs[1])
    links.new(mix.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop_material_metal(color, settings):
    """Create brushed metallic plate backdrop material with dull reflections"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Metal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (600, 0)
    # Metal color (grayish with tint)
    metal_color = (color[0] * 0.75 + 0.2, color[1] * 0.75 + 0.2, color[2] * 0.75 + 0.2)
    principled.inputs['Base Color'].default_value = (*metal_color, 1.0)
    principled.inputs['Metallic'].default_value = 1.0
    # Dull reflective - higher roughness
    base_rough = max(0.25, settings.backdrop_roughness * 0.6)
    principled.inputs['Roughness'].default_value = base_rough
    # Anisotropic for brushed look
    principled.inputs['Anisotropic'].default_value = 0.7
    principled.inputs['Anisotropic Rotation'].default_value = 0.25
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (settings.backdrop_texture_scale, settings.backdrop_texture_scale * 8, 1)
    
    # Brushed lines
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-350, 200)
    noise1.inputs['Scale'].default_value = 300.0
    noise1.inputs['Detail'].default_value = 3.0
    noise1.inputs['Roughness'].default_value = 0.25
    
    # Surface imperfections (scratches, smudges)
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-350, -50)
    noise2.inputs['Scale'].default_value = 40.0
    noise2.inputs['Detail'].default_value = 8.0
    noise2.inputs['Roughness'].default_value = 0.55
    
    # Roughness variation
    mix = nodes.new('ShaderNodeMath')
    mix.location = (0, 100)
    mix.operation = 'ADD'
    
    map_range = nodes.new('ShaderNodeMapRange')
    map_range.location = (200, 100)
    map_range.inputs['From Min'].default_value = 0.0
    map_range.inputs['From Max'].default_value = 1.0
    map_range.inputs['To Min'].default_value = base_rough * 0.75
    map_range.inputs['To Max'].default_value = base_rough * 1.3
    
    # Subtle bump for surface texture
    bump = nodes.new('ShaderNodeBump')
    bump.location = (350, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength * 0.25
    bump.inputs['Distance'].default_value = 0.004
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(noise1.outputs['Fac'], mix.inputs[0])
    links.new(noise2.outputs['Fac'], mix.inputs[1])
    links.new(mix.outputs[0], map_range.inputs['Value'])
    links.new(map_range.outputs['Result'], principled.inputs['Roughness'])
    links.new(noise2.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop_material_skin(color, settings):
    """Create SSS skin-like backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Skin")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (600, 0)
    # Skin-like color (warmer tones)
    skin_color = (min(1, color[0] * 1.15), color[1] * 0.82, color[2] * 0.7)
    principled.inputs['Base Color'].default_value = (*skin_color, 1.0)
    principled.inputs['Roughness'].default_value = max(0.3, settings.backdrop_roughness * 0.65)
    principled.inputs['Specular IOR Level'].default_value = 0.4
    # Strong SSS for skin
    principled.inputs['Subsurface Weight'].default_value = 0.75
    principled.inputs['Subsurface Radius'].default_value = Vector((1.0, 0.35, 0.15))
    principled.inputs['Subsurface Scale'].default_value = 0.12
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (settings.backdrop_texture_scale * 6, settings.backdrop_texture_scale * 6, 1)
    
    # Pore texture
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-350, 200)
    voronoi.feature = 'F1'
    voronoi.inputs['Scale'].default_value = 150.0
    voronoi.inputs['Randomness'].default_value = 1.0
    
    # Skin variation (freckles, discoloration)
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-350, 0)
    noise1.inputs['Scale'].default_value = 12.0
    noise1.inputs['Detail'].default_value = 6.0
    noise1.inputs['Roughness'].default_value = 0.55
    
    # Fine detail
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-350, -200)
    noise2.inputs['Scale'].default_value = 80.0
    noise2.inputs['Detail'].default_value = 5.0
    
    # Color variation
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (200, 200)
    color_ramp.color_ramp.elements[0].color = (skin_color[0] * 0.88, skin_color[1] * 0.82, skin_color[2] * 0.82, 1.0)
    color_ramp.color_ramp.elements[1].color = (*skin_color, 1.0)
    
    # Combine for bump
    mix = nodes.new('ShaderNodeMath')
    mix.location = (0, 0)
    mix.operation = 'ADD'
    
    mult = nodes.new('ShaderNodeMath')
    mult.location = (-100, -100)
    mult.operation = 'MULTIPLY'
    mult.inputs[1].default_value = 0.25
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (350, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength * 0.35
    bump.inputs['Distance'].default_value = 0.008
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(noise1.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(voronoi.outputs['Distance'], mult.inputs[0])
    links.new(mult.outputs[0], mix.inputs[0])
    links.new(noise2.outputs['Fac'], mix.inputs[1])
    links.new(mix.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop_material_water(color, settings):
    """Create lake surface/water backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Water")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (600, 0)
    # Water color (blue-ish tint with depth)
    water_color = (color[0] * 0.5, color[1] * 0.75, min(1, color[2] * 1.25 + 0.25))
    principled.inputs['Base Color'].default_value = (*water_color, 1.0)
    principled.inputs['Roughness'].default_value = max(0.01, settings.backdrop_roughness * 0.08)
    principled.inputs['Specular IOR Level'].default_value = 0.5
    principled.inputs['IOR'].default_value = 1.33
    # Some transmission for water depth
    principled.inputs['Transmission Weight'].default_value = 0.6
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (settings.backdrop_texture_scale * 2.5, settings.backdrop_texture_scale * 2.5, 1)
    
    # Large ripples/waves
    wave1 = nodes.new('ShaderNodeTexWave')
    wave1.location = (-350, 200)
    wave1.wave_type = 'RINGS'
    wave1.inputs['Scale'].default_value = 4.0
    wave1.inputs['Distortion'].default_value = 2.0
    wave1.inputs['Detail'].default_value = 3.0
    
    # Medium ripples
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-350, 0)
    noise1.inputs['Scale'].default_value = 10.0
    noise1.inputs['Detail'].default_value = 8.0
    noise1.inputs['Roughness'].default_value = 0.55
    noise1.inputs['Distortion'].default_value = 0.6
    
    # Fine ripples/caustics
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-350, -200)
    noise2.inputs['Scale'].default_value = 30.0
    noise2.inputs['Detail'].default_value = 5.0
    noise2.inputs['Roughness'].default_value = 0.45
    
    # Combine ripples
    mix1 = nodes.new('ShaderNodeMath')
    mix1.location = (-100, 100)
    mix1.operation = 'ADD'
    
    mult = nodes.new('ShaderNodeMath')
    mult.location = (-100, -50)
    mult.operation = 'MULTIPLY'
    mult.inputs[1].default_value = 0.25
    
    mix2 = nodes.new('ShaderNodeMath')
    mix2.location = (50, 0)
    mix2.operation = 'ADD'
    
    # Normal map for ripples
    bump = nodes.new('ShaderNodeBump')
    bump.location = (350, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength * 0.55
    bump.inputs['Distance'].default_value = 0.018
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(wave1.outputs['Fac'], mix1.inputs[0])
    links.new(noise1.outputs['Fac'], mix1.inputs[1])
    links.new(noise2.outputs['Fac'], mult.inputs[0])
    links.new(mix1.outputs[0], mix2.inputs[0])
    links.new(mult.outputs[0], mix2.inputs[1])
    links.new(mix2.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Enable transparency
    mat.blend_method = 'HASHED'
    try:
        mat.shadow_method = 'HASHED'
    except AttributeError:
        pass
    
    return mat


def create_backdrop_material_rubber(color, settings):
    """Create rubber mat backdrop material"""
    mat = bpy.data.materials.new(name="BackdropMaterial_Rubber")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (600, 0)
    principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    principled.inputs['Roughness'].default_value = max(0.45, settings.backdrop_roughness * 0.85)
    principled.inputs['Specular IOR Level'].default_value = 0.3
    # Rubber SSS
    principled.inputs['Subsurface Weight'].default_value = 0.35
    principled.inputs['Subsurface Radius'].default_value = Vector((0.7, 0.45, 0.3))
    principled.inputs['Subsurface Scale'].default_value = 0.1
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (settings.backdrop_texture_scale * 3.5, settings.backdrop_texture_scale * 3.5, 1)
    
    # Rubber texture pattern (diamond/grid pattern)
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-350, 200)
    voronoi.feature = 'F1'
    voronoi.inputs['Scale'].default_value = 25.0
    voronoi.inputs['Randomness'].default_value = 0.25
    
    # Surface noise
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-350, 0)
    noise1.inputs['Scale'].default_value = 50.0
    noise1.inputs['Detail'].default_value = 8.0
    noise1.inputs['Roughness'].default_value = 0.65
    
    # Fine texture
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-350, -200)
    noise2.inputs['Scale'].default_value = 150.0
    noise2.inputs['Detail'].default_value = 4.0
    noise2.inputs['Roughness'].default_value = 0.55
    
    # Combine textures
    mix1 = nodes.new('ShaderNodeMath')
    mix1.location = (-100, 100)
    mix1.operation = 'ADD'
    
    mult = nodes.new('ShaderNodeMath')
    mult.location = (-100, -50)
    mult.operation = 'MULTIPLY'
    mult.inputs[1].default_value = 0.15
    
    mix2 = nodes.new('ShaderNodeMath')
    mix2.location = (50, 0)
    mix2.operation = 'ADD'
    
    # Color variation
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (200, 200)
    color_ramp.color_ramp.elements[0].color = (color[0] * 0.88, color[1] * 0.88, color[2] * 0.88, 1.0)
    color_ramp.color_ramp.elements[1].color = (color[0], color[1], color[2], 1.0)
    
    # Bump
    bump = nodes.new('ShaderNodeBump')
    bump.location = (350, -100)
    bump.inputs['Strength'].default_value = settings.backdrop_bump_strength * 0.55
    bump.inputs['Distance'].default_value = 0.018
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], mix1.inputs[0])
    links.new(noise1.outputs['Fac'], mix1.inputs[1])
    links.new(noise2.outputs['Fac'], mult.inputs[0])
    links.new(mix1.outputs[0], mix2.inputs[0])
    links.new(mult.outputs[0], mix2.inputs[1])
    links.new(noise1.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(mix2.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_backdrop(settings):
    """Create backdrop plane"""
    backdrop_size = max(settings.spread_x, settings.spread_y) * 3
    
    bpy.ops.mesh.primitive_plane_add(size=backdrop_size, location=(0, 0, 0))
    backdrop = bpy.context.active_object
    backdrop.name = "Backdrop"
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=20)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mesh = backdrop.data
    curve_start = backdrop_size * 0.2
    for vert in mesh.vertices:
        if vert.co.y > curve_start:
            curve_factor = (vert.co.y - curve_start) / (backdrop_size * 0.3)
            vert.co.z = min(curve_factor ** 2 * 4, backdrop_size * 0.5)
    
    bpy.ops.object.shade_smooth()
    
    palette = PALETTES[settings.color_palette]
    mat = create_backdrop_material(palette['background'], settings)
    backdrop.data.materials.append(mat)
    
    return backdrop, backdrop_size


def get_primitive_height(prim_type, scale):
    """Get height offset for primitive"""
    base_heights = {
        'cube': 0.5, 'sphere': 0.5, 'cylinder': 0.5, 'cone': 0.5,
        'torus': 0.15, 'ico_sphere': 0.5, 'capsule': 0.65, 'rounded_cube': 0.5,
    }
    return base_heights.get(prim_type, 0.5) * scale


def create_primitive_object(prim_type, position, scale, rotation, settings, index):
    """Create primitive mesh object"""
    height_offset = get_primitive_height(prim_type, scale)
    adjusted_position = (position[0], position[1], height_offset + settings.height_above_plane)
    
    if prim_type == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=1, location=adjusted_position)
        obj = bpy.context.active_object
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width, bevel.segments = 0.05, 3
    elif prim_type == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=32, ring_count=16, location=adjusted_position)
        obj = bpy.context.active_object
    elif prim_type == 'cylinder':
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1, vertices=32, location=adjusted_position)
        obj = bpy.context.active_object
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width, bevel.segments = 0.03, 2
    elif prim_type == 'cone':
        bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0, depth=1, vertices=32, location=adjusted_position)
        obj = bpy.context.active_object
    elif prim_type == 'torus':
        bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.15, major_segments=48, minor_segments=16, location=adjusted_position)
        obj = bpy.context.active_object
    elif prim_type == 'ico_sphere':
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.5, subdivisions=2, location=adjusted_position)
        obj = bpy.context.active_object
    elif prim_type == 'capsule':
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.8, vertices=32, location=adjusted_position)
        obj = bpy.context.active_object
        obj.modifiers.new(name="Subsurf", type='SUBSURF').levels = 2
    elif prim_type == 'rounded_cube':
        bpy.ops.mesh.primitive_cube_add(size=1, location=adjusted_position)
        obj = bpy.context.active_object
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width, bevel.segments = 0.15, 5
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=adjusted_position)
        obj = bpy.context.active_object
    
    obj.name = f"Primitive_{index:03d}"
    scale_var = 0.15
    obj.scale = tuple(scale * random.uniform(1 - scale_var, 1 + scale_var) for _ in range(3))
    obj.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), rotation)
    bpy.ops.object.shade_smooth()
    
    return obj




# ===========================================
# SCAFFOLDING CREATION FUNCTIONS
# ===========================================

def create_scaffolding_material(settings):
    """Create material for scaffolding based on settings"""
    mat = bpy.data.materials.new(name="ScaffoldingMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (300, 0)
    
    color = settings.scaffolding_color
    roughness = settings.scaffolding_roughness
    mat_type = settings.scaffolding_material
    
    if mat_type == 'METAL':
        principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
        principled.inputs['Metallic'].default_value = 1.0
        principled.inputs['Roughness'].default_value = roughness
        
    elif mat_type == 'BRUSHED_METAL':
        principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
        principled.inputs['Metallic'].default_value = 1.0
        principled.inputs['Roughness'].default_value = max(0.25, roughness)
        principled.inputs['Anisotropic'].default_value = 0.7
        principled.inputs['Anisotropic Rotation'].default_value = random.uniform(0, 0.5)
        
    elif mat_type == 'RUBBER':
        principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
        principled.inputs['Roughness'].default_value = max(0.5, roughness)
        principled.inputs['Specular IOR Level'].default_value = 0.3
        principled.inputs['Subsurface Weight'].default_value = 0.3
        principled.inputs['Subsurface Radius'].default_value = Vector((0.6, 0.4, 0.25))
        
    elif mat_type == 'WOOD':
        wood_color = (color[0] * 0.6, color[1] * 0.4, color[2] * 0.25)
        principled.inputs['Base Color'].default_value = (*wood_color, 1.0)
        principled.inputs['Roughness'].default_value = max(0.4, roughness)
        principled.inputs['Specular IOR Level'].default_value = 0.3
        
    elif mat_type == 'PLASTIC':
        principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
        principled.inputs['Roughness'].default_value = roughness
        principled.inputs['Specular IOR Level'].default_value = 0.5
        principled.inputs['Coat Weight'].default_value = 0.4
        principled.inputs['Coat Roughness'].default_value = 0.1
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def find_primitive_clusters(primitives, cluster_distance):
    """Group primitives into clusters based on proximity"""
    if not primitives:
        return []
    
    prim_data = []
    for obj in primitives:
        loc = obj.location.copy()
        radius = max(obj.scale) * 0.5
        prim_data.append({'obj': obj, 'loc': loc, 'radius': radius, 'cluster': -1})
    
    cluster_id = 0
    for i, p1 in enumerate(prim_data):
        if p1['cluster'] == -1:
            p1['cluster'] = cluster_id
            stack = [i]
            while stack:
                curr_idx = stack.pop()
                curr = prim_data[curr_idx]
                for j, p2 in enumerate(prim_data):
                    if p2['cluster'] == -1:
                        dist = (curr['loc'] - p2['loc']).length
                        if dist < cluster_distance + curr['radius'] + p2['radius']:
                            p2['cluster'] = cluster_id
                            stack.append(j)
            cluster_id += 1
    
    clusters = {}
    for p in prim_data:
        cid = p['cluster']
        if cid not in clusters:
            clusters[cid] = []
        clusters[cid].append(p)
    
    return list(clusters.values())


def get_cluster_bounds(cluster, padding):
    """Get bounding box and center of a cluster"""
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    for p in cluster:
        loc = p['loc']
        r = p['radius'] + padding
        min_x = min(min_x, loc.x - r)
        max_x = max(max_x, loc.x + r)
        min_y = min(min_y, loc.y - r)
        max_y = max(max_y, loc.y + r)
        min_z = min(min_z, loc.z - r)
        max_z = max(max_z, loc.z + r)
    
    center = Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))
    size = Vector((max_x - min_x, max_y - min_y, max_z - min_z))
    
    return center, size, (min_x, max_x, min_y, max_y, min_z, max_z)


def add_wire_deviation(point, deviation):
    """Add random deviation to a point"""
    if deviation <= 0:
        return point
    return Vector((
        point.x + random.uniform(-deviation, deviation),
        point.y + random.uniform(-deviation, deviation),
        point.z + random.uniform(-deviation, deviation)
    ))


def create_wire_curve(points, thickness, name, deviation=0):
    """Create a curve object from points with thickness and optional deviation"""
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = thickness
    curve_data.bevel_resolution = 3
    curve_data.fill_mode = 'FULL'
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    
    for i, point in enumerate(points):
        bp = spline.bezier_points[i]
        if 0 < i < len(points) - 1 and deviation > 0:
            bp.co = add_wire_deviation(point, deviation)
        else:
            bp.co = point
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    return curve_obj


def trace_cluster_perimeter(cluster, height, padding, num_points=32):
    """Trace the outer perimeter of a cluster at a given height"""
    center, size, bounds = get_cluster_bounds(cluster, padding)
    
    perimeter_points = []
    for i in range(num_points):
        angle = (i / num_points) * math.pi * 2
        direction = Vector((math.cos(angle), math.sin(angle), 0))
        
        max_dist = 0
        for p in cluster:
            loc = p['loc']
            r = p['radius'] + padding
            to_prim = Vector((loc.x - center.x, loc.y - center.y, 0))
            proj_len = to_prim.dot(direction)
            if proj_len > 0:
                perp_dist = (to_prim - direction * proj_len).length
                if perp_dist < r:
                    edge_dist = proj_len + math.sqrt(max(0, r*r - perp_dist*perp_dist))
                    max_dist = max(max_dist, edge_dist)
        
        if max_dist < 0.1:
            max_dist = max(size.x, size.y) * 0.5
        
        point = Vector((
            center.x + direction.x * max_dist,
            center.y + direction.y * max_dist,
            height
        ))
        perimeter_points.append(point)
    
    perimeter_points.append(perimeter_points[0].copy())
    return perimeter_points


def create_fence_scaffolding(cluster, settings):
    """Create fence-like vertical wire scaffolding"""
    wires = []
    center, size, bounds = get_cluster_bounds(cluster, settings.scaffolding_padding)
    min_z, max_z = bounds[4], bounds[5]
    
    thickness = settings.scaffolding_wire_thickness
    deviation = settings.scaffolding_deviation
    num_wires = settings.scaffolding_density
    num_layers = settings.scaffolding_height_layers
    
    for layer in range(num_layers):
        t = layer / (num_layers - 1) if num_layers > 1 else 0.5
        height = min_z + t * (max_z - min_z)
        
        perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires)
        wire = create_wire_curve(perimeter, thickness, f"Scaff_Ring_{layer}", deviation)
        wires.append(wire)
    
    for i in range(num_wires):
        points = []
        for layer in range(num_layers + 2):
            t = layer / (num_layers + 1)
            height = min_z + t * (max_z - min_z)
            perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires)
            idx = i % len(perimeter)
            points.append(perimeter[idx])
        
        wire = create_wire_curve(points, thickness, f"Scaff_Vert_{i}", deviation)
        wires.append(wire)
    
    return wires


def create_net_scaffolding(cluster, settings):
    """Create net/mesh pattern scaffolding"""
    wires = []
    center, size, bounds = get_cluster_bounds(cluster, settings.scaffolding_padding)
    min_z, max_z = bounds[4], bounds[5]
    
    thickness = settings.scaffolding_wire_thickness
    deviation = settings.scaffolding_deviation
    num_wires = settings.scaffolding_density
    num_layers = settings.scaffolding_height_layers
    
    for layer in range(num_layers):
        t = layer / (num_layers - 1) if num_layers > 1 else 0.5
        height = min_z + t * (max_z - min_z)
        perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires * 2)
        wire = create_wire_curve(perimeter, thickness, f"Scaff_HRing_{layer}", deviation)
        wires.append(wire)
    
    for i in range(num_wires):
        points = []
        for layer in range(num_layers):
            t = layer / (num_layers - 1) if num_layers > 1 else 0.5
            height = min_z + t * (max_z - min_z)
            perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires * 2)
            idx = (i * 2 + int(layer * 2)) % len(perimeter)
            points.append(perimeter[idx])
        wire = create_wire_curve(points, thickness * 0.8, f"Scaff_DiagR_{i}", deviation)
        wires.append(wire)
    
    for i in range(num_wires):
        points = []
        for layer in range(num_layers):
            t = layer / (num_layers - 1) if num_layers > 1 else 0.5
            height = min_z + t * (max_z - min_z)
            perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires * 2)
            idx = (i * 2 - int(layer * 2)) % len(perimeter)
            points.append(perimeter[idx])
        wire = create_wire_curve(points, thickness * 0.8, f"Scaff_DiagL_{i}", deviation)
        wires.append(wire)
    
    return wires


def create_spiral_net_scaffolding(cluster, settings):
    """Create spiraling net scaffolding"""
    wires = []
    center, size, bounds = get_cluster_bounds(cluster, settings.scaffolding_padding)
    min_z, max_z = bounds[4], bounds[5]
    
    thickness = settings.scaffolding_wire_thickness
    deviation = settings.scaffolding_deviation
    num_spirals = max(2, settings.scaffolding_density // 4)
    num_layers = settings.scaffolding_height_layers
    
    for spiral in range(num_spirals):
        points = []
        start_angle = (spiral / num_spirals) * math.pi * 2
        total_segments = num_layers * 8
        
        for seg in range(total_segments + 1):
            t = seg / total_segments
            height = min_z + t * (max_z - min_z)
            angle = start_angle + t * math.pi * 4
            perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, 32)
            idx = int((angle / (math.pi * 2)) * len(perimeter)) % (len(perimeter) - 1)
            points.append(perimeter[idx])
        
        wire = create_wire_curve(points, thickness, f"Scaff_Spiral_{spiral}", deviation)
        wires.append(wire)
    
    for layer in range(0, num_layers, 2):
        t = layer / (num_layers - 1) if num_layers > 1 else 0.5
        height = min_z + t * (max_z - min_z)
        perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, settings.scaffolding_density * 2)
        wire = create_wire_curve(perimeter, thickness * 0.7, f"Scaff_SpiralRing_{layer}", deviation)
        wires.append(wire)
    
    return wires


def create_geodesic_net_scaffolding(cluster, settings):
    """Create geodesic dome-like network scaffolding"""
    wires = []
    center, size, bounds = get_cluster_bounds(cluster, settings.scaffolding_padding)
    min_z, max_z = bounds[4], bounds[5]
    
    thickness = settings.scaffolding_wire_thickness
    deviation = settings.scaffolding_deviation
    num_wires = settings.scaffolding_density
    num_layers = settings.scaffolding_height_layers
    
    for layer in range(num_layers):
        t = layer / (num_layers - 1) if num_layers > 1 else 0.5
        height = min_z + t * (max_z - min_z)
        perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires * 2)
        wire = create_wire_curve(perimeter, thickness, f"Scaff_Lat_{layer}", deviation)
        wires.append(wire)
    
    for i in range(num_wires):
        points = []
        for layer in range(num_layers + 2):
            t = layer / (num_layers + 1)
            height = min_z + t * (max_z - min_z)
            perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires)
            idx = i % (len(perimeter) - 1)
            points.append(perimeter[idx])
        wire = create_wire_curve(points, thickness, f"Scaff_Long_{i}", deviation)
        wires.append(wire)
    
    for i in range(num_wires // 2):
        points = []
        for layer in range(num_layers):
            t = layer / (num_layers - 1) if num_layers > 1 else 0.5
            height = min_z + t * (max_z - min_z)
            perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires)
            idx = (i * 2 + layer) % (len(perimeter) - 1)
            points.append(perimeter[idx])
        wire = create_wire_curve(points, thickness * 0.7, f"Scaff_GeoDiag_{i}", deviation)
        wires.append(wire)
    
    return wires


def create_random_web_scaffolding(cluster, settings):
    """Create organic web-like scaffolding with random connections"""
    wires = []
    center, size, bounds = get_cluster_bounds(cluster, settings.scaffolding_padding)
    min_z, max_z = bounds[4], bounds[5]
    
    thickness = settings.scaffolding_wire_thickness
    deviation = settings.scaffolding_deviation * 1.5
    num_wires = settings.scaffolding_density
    num_layers = settings.scaffolding_height_layers
    
    anchor_points = []
    for layer in range(num_layers):
        t = layer / (num_layers - 1) if num_layers > 1 else 0.5
        height = min_z + t * (max_z - min_z)
        perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires)
        for p in perimeter[:-1]:
            anchor_points.append(p)
    
    used_pairs = set()
    num_connections = num_wires * num_layers
    
    for _ in range(num_connections):
        idx1 = random.randint(0, len(anchor_points) - 1)
        p1 = anchor_points[idx1]
        
        nearby = []
        for idx2, p2 in enumerate(anchor_points):
            if idx2 != idx1:
                dist = (p1 - p2).length
                if 0.1 < dist < size.length * 0.5:
                    nearby.append((idx2, p2, dist))
        
        if nearby:
            idx2, p2, _ = random.choice(nearby)
            pair = (min(idx1, idx2), max(idx1, idx2))
            
            if pair not in used_pairs:
                used_pairs.add(pair)
                mid1 = p1.lerp(p2, 0.33)
                mid2 = p1.lerp(p2, 0.67)
                points = [p1, mid1, mid2, p2]
                wire = create_wire_curve(points, thickness * random.uniform(0.7, 1.0), 
                                        f"Scaff_Web_{len(wires)}", deviation)
                wires.append(wire)
    
    for layer in range(0, num_layers, 2):
        t = layer / (num_layers - 1) if num_layers > 1 else 0.5
        height = min_z + t * (max_z - min_z)
        perimeter = trace_cluster_perimeter(cluster, height, settings.scaffolding_padding, num_wires)
        wire = create_wire_curve(perimeter, thickness * 0.6, f"Scaff_WebRing_{layer}", deviation * 0.5)
        wires.append(wire)
    
    return wires


def create_cage_scaffolding(cluster, settings):
    """Create simple cage scaffolding around cluster bounds"""
    wires = []
    center, size, bounds = get_cluster_bounds(cluster, settings.scaffolding_padding)
    min_x, max_x, min_y, max_y, min_z, max_z = bounds
    
    thickness = settings.scaffolding_wire_thickness
    deviation = settings.scaffolding_deviation
    
    corners = [
        (min_x, min_y), (max_x, min_y),
        (max_x, max_y), (min_x, max_y)
    ]
    
    for i, (x, y) in enumerate(corners):
        points = [
            Vector((x, y, min_z)),
            Vector((x, y, (min_z + max_z) / 2)),
            Vector((x, y, max_z))
        ]
        wire = create_wire_curve(points, thickness * 1.2, f"Scaff_Post_{i}", deviation * 0.5)
        wires.append(wire)
    
    heights = [min_z, (min_z + max_z) / 2, max_z]
    for h_idx, h in enumerate(heights):
        frame_points = [Vector((x, y, h)) for x, y in corners]
        frame_points.append(frame_points[0].copy())
        wire = create_wire_curve(frame_points, thickness, f"Scaff_Frame_{h_idx}", deviation)
        wires.append(wire)
    
    for i in range(4):
        x1, y1 = corners[i]
        x2, y2 = corners[(i + 1) % 4]
        points = [
            Vector((x1, y1, min_z)),
            Vector(((x1 + x2) / 2, (y1 + y2) / 2, (min_z + max_z) / 2)),
            Vector((x2, y2, max_z))
        ]
        wire = create_wire_curve(points, thickness * 0.8, f"Scaff_Brace_{i}", deviation)
        wires.append(wire)
    
    return wires


def create_cluster_scaffolding(cluster, settings):
    """Create scaffolding for a cluster of primitives"""
    scaffolding_type = settings.scaffolding_type
    
    creators = {
        'FENCE': create_fence_scaffolding,
        'NET': create_net_scaffolding,
        'SPIRAL_NET': create_spiral_net_scaffolding,
        'GEODESIC_NET': create_geodesic_net_scaffolding,
        'RANDOM_WEB': create_random_web_scaffolding,
        'CAGE': create_cage_scaffolding,
    }
    
    creator = creators.get(scaffolding_type, create_net_scaffolding)
    return creator(cluster, settings)


def create_scaffolding_for_scene(primitives, settings):
    """Create scaffolding network for all primitive clusters"""
    if not settings.enable_scaffolding or not primitives:
        return []
    
    all_scaffolding = []
    clusters = find_primitive_clusters(primitives, settings.scaffolding_cluster_distance)
    valid_clusters = [c for c in clusters if len(c) >= 2]
    
    if not valid_clusters:
        return []
    
    mat = create_scaffolding_material(settings)
    
    for cluster in valid_clusters:
        wires = create_cluster_scaffolding(cluster, settings)
        for wire in wires:
            wire.data.materials.append(mat)
            all_scaffolding.append(wire)
    
    return all_scaffolding


# ===========================================
# GEM CREATION FUNCTIONS
# ===========================================

# Gem data: color (RGB), IOR, dispersion
GEM_DATA = {
    'DIAMOND': {
        'color': (1.0, 1.0, 1.0),
        'ior': 2.417,
        'dispersion': 0.044,
    },
    'RUBY': {
        'color': (0.85, 0.1, 0.15),
        'ior': 1.762,
        'dispersion': 0.018,
    },
    'SAPPHIRE': {
        'color': (0.15, 0.25, 0.85),
        'ior': 1.762,
        'dispersion': 0.018,
    },
    'EMERALD': {
        'color': (0.15, 0.7, 0.3),
        'ior': 1.577,
        'dispersion': 0.014,
    },
    'TOPAZ': {
        'color': (0.95, 0.7, 0.2),
        'ior': 1.629,
        'dispersion': 0.014,
    },
    'AMETHYST': {
        'color': (0.6, 0.3, 0.8),
        'ior': 1.544,
        'dispersion': 0.013,
    },
    'AQUAMARINE': {
        'color': (0.5, 0.8, 0.95),
        'ior': 1.577,
        'dispersion': 0.014,
    },
    'CITRINE': {
        'color': (0.95, 0.8, 0.3),
        'ior': 1.550,
        'dispersion': 0.013,
    },
    'PERIDOT': {
        'color': (0.6, 0.8, 0.2),
        'ior': 1.670,
        'dispersion': 0.020,
    },
    'GARNET': {
        'color': (0.5, 0.1, 0.15),
        'ior': 1.740,
        'dispersion': 0.027,
    },
    'OPAL': {
        'color': (0.95, 0.95, 0.98),
        'ior': 1.450,
        'dispersion': 0.010,
    },
    'TANZANITE': {
        'color': (0.35, 0.3, 0.85),
        'ior': 1.692,
        'dispersion': 0.021,
    },
}

GEM_TYPES = list(GEM_DATA.keys())
GEM_CUTS = ['ROUND_BRILLIANT', 'PRINCESS', 'EMERALD_CUT', 'OVAL', 'PEAR', 'MARQUISE', 'CUSHION', 'HEART', 'TRILLION']


def create_gem_material(gem_type, settings):
    """Create realistic gem material with proper IOR and color"""
    gem_info = GEM_DATA.get(gem_type, GEM_DATA['DIAMOND'])
    
    mat = bpy.data.materials.new(name=f"Gem_{gem_type}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (400, 0)
    
    # Base color with saturation adjustment
    base_color = gem_info['color']
    saturation = settings.gem_saturation
    
    # Adjust color saturation
    gray = 0.299 * base_color[0] + 0.587 * base_color[1] + 0.114 * base_color[2]
    adjusted_color = tuple(gray + saturation * (c - gray) for c in base_color)
    
    principled.inputs['Base Color'].default_value = (*adjusted_color, 1.0)
    
    # IOR and transmission for gem-like appearance
    principled.inputs['IOR'].default_value = gem_info['ior']
    principled.inputs['Transmission Weight'].default_value = 0.95
    
    # Quality affects roughness
    quality_roughness = {
        'FLAWLESS': 0.0,
        'EXCELLENT': 0.02,
        'GOOD': 0.05,
        'FAIR': 0.1,
    }
    principled.inputs['Roughness'].default_value = quality_roughness.get(settings.gem_quality, 0.02)
    
    # Specular for brilliance
    principled.inputs['Specular IOR Level'].default_value = 0.5
    
    # Subsurface for colored gems
    if gem_type != 'DIAMOND':
        principled.inputs['Subsurface Weight'].default_value = 0.1
        principled.inputs['Subsurface Radius'].default_value = Vector((0.1, 0.1, 0.1))
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    mat.blend_method = 'HASHED'
    
    return mat


def create_round_brilliant_gem(location, size):
    """Create a round brilliant cut gem"""
    bm = bmesh.new()
    
    table_radius = size * 0.53
    crown_height = size * 0.14
    girdle_height = size * 0.02
    pavilion_depth = size * 0.43
    num_facets = 16
    
    # Table vertices
    table_verts = []
    for i in range(num_facets):
        angle = 2 * math.pi * i / num_facets
        x = table_radius * math.cos(angle)
        y = table_radius * math.sin(angle)
        z = crown_height + girdle_height / 2
        table_verts.append(bm.verts.new((x, y, z)))
    
    # Crown vertices
    crown_verts = []
    for i in range(num_facets * 2):
        angle = 2 * math.pi * i / (num_facets * 2)
        if i % 2 == 0:
            r = size * 0.5
            z = girdle_height / 2
        else:
            r = size * 0.5 * 0.85
            z = crown_height * 0.5 + girdle_height / 2
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        crown_verts.append(bm.verts.new((x, y, z)))
    
    # Girdle vertices
    girdle_top = []
    girdle_bottom = []
    for i in range(num_facets * 2):
        angle = 2 * math.pi * i / (num_facets * 2)
        x = size * 0.5 * math.cos(angle)
        y = size * 0.5 * math.sin(angle)
        girdle_top.append(bm.verts.new((x, y, girdle_height / 2)))
        girdle_bottom.append(bm.verts.new((x, y, -girdle_height / 2)))
    
    # Pavilion vertices
    pavilion_verts = []
    for i in range(num_facets):
        angle = 2 * math.pi * i / num_facets + math.pi / num_facets
        r = size * 0.5 * 0.4
        z = -pavilion_depth * 0.5
        pavilion_verts.append(bm.verts.new((r * math.cos(angle), r * math.sin(angle), z)))
    
    # Culet
    culet = bm.verts.new((0, 0, -pavilion_depth))
    
    bm.verts.ensure_lookup_table()
    
    # Table face
    bm.faces.new(table_verts)
    
    # Crown faces
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([table_verts[i], table_verts[next_i], crown_verts[i * 2 + 1]])
        bm.faces.new([table_verts[i], crown_verts[i * 2 + 1], crown_verts[i * 2]])
        bm.faces.new([table_verts[next_i], crown_verts[(i * 2 + 2) % (num_facets * 2)], crown_verts[i * 2 + 1]])
    
    # Girdle faces
    for i in range(num_facets * 2):
        next_i = (i + 1) % (num_facets * 2)
        bm.faces.new([girdle_top[i], girdle_top[next_i], girdle_bottom[next_i], girdle_bottom[i]])
    
    # Pavilion faces
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([girdle_bottom[i * 2], pavilion_verts[i], culet])
        bm.faces.new([girdle_bottom[i * 2], girdle_bottom[i * 2 + 1], pavilion_verts[i]])
        bm.faces.new([girdle_bottom[i * 2 + 1], girdle_bottom[(i * 2 + 2) % (num_facets * 2)], pavilion_verts[next_i], pavilion_verts[i]])
    
    mesh = bpy.data.meshes.new("RoundBrilliant")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_RoundBrilliant", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_princess_gem(location, size):
    """Create a princess cut (square) gem"""
    bm = bmesh.new()
    
    half_size = size * 0.5
    crown_height = size * 0.15
    pavilion_depth = size * 0.45
    table_inset = size * 0.15
    
    t_half = half_size - table_inset
    table_verts = [
        bm.verts.new((-t_half, -t_half, crown_height)),
        bm.verts.new((t_half, -t_half, crown_height)),
        bm.verts.new((t_half, t_half, crown_height)),
        bm.verts.new((-t_half, t_half, crown_height)),
    ]
    
    crown_verts = [
        bm.verts.new((-half_size, -half_size, 0)),
        bm.verts.new((half_size, -half_size, 0)),
        bm.verts.new((half_size, half_size, 0)),
        bm.verts.new((-half_size, half_size, 0)),
    ]
    
    culet = bm.verts.new((0, 0, -pavilion_depth))
    
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(table_verts)
    
    for i in range(4):
        next_i = (i + 1) % 4
        bm.faces.new([table_verts[i], table_verts[next_i], crown_verts[next_i], crown_verts[i]])
    
    for i in range(4):
        bm.faces.new([table_verts[i], crown_verts[i], table_verts[(i - 1) % 4]])
    
    for i in range(4):
        next_i = (i + 1) % 4
        bm.faces.new([crown_verts[i], crown_verts[next_i], culet])
    
    mesh = bpy.data.meshes.new("PrincessCut")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_Princess", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_emerald_cut_gem(location, size):
    """Create an emerald cut (rectangular step cut) gem"""
    bm = bmesh.new()
    
    width = size * 0.7
    length = size
    height_crown = size * 0.12
    height_pavilion = size * 0.4
    steps = 3
    step_inset = size * 0.08
    
    layers = []
    for step in range(steps + 1):
        t = step / steps
        w = width - step_inset * step * 0.7
        l = length - step_inset * step * 0.7
        z = height_crown * (1 - t)
        layer = [
            bm.verts.new((-w/2, -l/2, z)),
            bm.verts.new((w/2, -l/2, z)),
            bm.verts.new((w/2, l/2, z)),
            bm.verts.new((-w/2, l/2, z)),
        ]
        layers.append(layer)
    
    for step in range(1, steps + 1):
        t = step / steps
        w = width * (1 - t * 0.8)
        l = length * (1 - t * 0.8)
        z = -height_pavilion * t
        layer = [
            bm.verts.new((-w/2, -l/2, z)),
            bm.verts.new((w/2, -l/2, z)),
            bm.verts.new((w/2, l/2, z)),
            bm.verts.new((-w/2, l/2, z)),
        ]
        layers.append(layer)
    
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(layers[0])
    
    for i in range(len(layers) - 1):
        for j in range(4):
            next_j = (j + 1) % 4
            bm.faces.new([layers[i][j], layers[i][next_j], layers[i+1][next_j], layers[i+1][j]])
    
    bm.faces.new(reversed(layers[-1]))
    
    mesh = bpy.data.meshes.new("EmeraldCut")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_EmeraldCut", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_oval_gem(location, size):
    """Create an oval cut gem"""
    bm = bmesh.new()
    
    width = size * 0.65
    length = size
    crown_height = size * 0.13
    pavilion_depth = size * 0.42
    num_facets = 16
    
    table_verts = []
    for i in range(num_facets):
        angle = 2 * math.pi * i / num_facets
        x = width * 0.6 * math.cos(angle)
        y = length * 0.6 * math.sin(angle)
        table_verts.append(bm.verts.new((x, y, crown_height)))
    
    girdle_verts = []
    for i in range(num_facets):
        angle = 2 * math.pi * i / num_facets
        x = width * math.cos(angle)
        y = length * math.sin(angle)
        girdle_verts.append(bm.verts.new((x, y, 0)))
    
    culet = bm.verts.new((0, 0, -pavilion_depth))
    
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(table_verts)
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([table_verts[i], table_verts[next_i], girdle_verts[next_i], girdle_verts[i]])
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([girdle_verts[i], girdle_verts[next_i], culet])
    
    mesh = bpy.data.meshes.new("OvalCut")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_Oval", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_pear_gem(location, size):
    """Create a pear (teardrop) cut gem"""
    bm = bmesh.new()
    
    width = size * 0.6
    length = size
    crown_height = size * 0.12
    pavilion_depth = size * 0.4
    num_facets = 20
    
    table_verts = []
    girdle_verts = []
    
    for i in range(num_facets):
        angle = 2 * math.pi * i / num_facets
        r = 1 + 0.3 * math.cos(angle)
        
        x = width * r * math.sin(angle) * 0.5
        y = length * (i / num_facets - 0.5) * r * 0.8
        girdle_verts.append(bm.verts.new((x, y, 0)))
        
        x_t = x * 0.6
        y_t = y * 0.6
        table_verts.append(bm.verts.new((x_t, y_t, crown_height)))
    
    culet = bm.verts.new((0, -length * 0.3, -pavilion_depth))
    
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(table_verts)
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([table_verts[i], table_verts[next_i], girdle_verts[next_i], girdle_verts[i]])
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([girdle_verts[i], girdle_verts[next_i], culet])
    
    mesh = bpy.data.meshes.new("PearCut")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_Pear", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_marquise_gem(location, size):
    """Create a marquise (football-shaped) cut gem"""
    bm = bmesh.new()
    
    width = size * 0.45
    length = size
    crown_height = size * 0.12
    pavilion_depth = size * 0.38
    num_facets = 20
    
    table_verts = []
    girdle_verts = []
    
    for i in range(num_facets):
        angle = 2 * math.pi * i / num_facets
        r = 1.0 / (1 + 0.3 * abs(math.cos(angle)))
        x = width * r * math.cos(angle)
        y = length * 0.5 * r * math.sin(angle)
        girdle_verts.append(bm.verts.new((x, y, 0)))
        
        r_table = 0.55 / (1 + 0.3 * abs(math.cos(angle)))
        x_t = width * r_table * math.cos(angle)
        y_t = length * 0.5 * r_table * math.sin(angle)
        table_verts.append(bm.verts.new((x_t, y_t, crown_height)))
    
    culet = bm.verts.new((0, 0, -pavilion_depth))
    
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(table_verts)
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([table_verts[i], table_verts[next_i], girdle_verts[next_i], girdle_verts[i]])
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([girdle_verts[i], girdle_verts[next_i], culet])
    
    mesh = bpy.data.meshes.new("MarquiseCut")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_Marquise", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_cushion_gem(location, size):
    """Create a cushion cut gem (rounded square)"""
    bm = bmesh.new()
    
    half_size = size * 0.5
    crown_height = size * 0.14
    pavilion_depth = size * 0.42
    num_facets = 24
    
    table_verts = []
    girdle_verts = []
    
    for i in range(num_facets):
        angle = 2 * math.pi * i / num_facets
        n = 3
        x = half_size * math.copysign(abs(math.cos(angle)) ** (2/n), math.cos(angle))
        y = half_size * math.copysign(abs(math.sin(angle)) ** (2/n), math.sin(angle))
        girdle_verts.append(bm.verts.new((x, y, 0)))
        table_verts.append(bm.verts.new((x * 0.6, y * 0.6, crown_height)))
    
    culet = bm.verts.new((0, 0, -pavilion_depth))
    
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(table_verts)
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([table_verts[i], table_verts[next_i], girdle_verts[next_i], girdle_verts[i]])
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([girdle_verts[i], girdle_verts[next_i], culet])
    
    mesh = bpy.data.meshes.new("CushionCut")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_Cushion", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_heart_gem(location, size):
    """Create a heart-shaped cut gem"""
    bm = bmesh.new()
    
    width = size
    height = size * 0.9
    crown_height = size * 0.12
    pavilion_depth = size * 0.38
    num_facets = 32
    
    table_verts = []
    girdle_verts = []
    
    for i in range(num_facets):
        t = i / num_facets
        angle = t * 2 * math.pi
        x = width * 0.5 * (16 * math.sin(angle) ** 3) / 16
        y = height * 0.5 * (13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle)) / 16
        girdle_verts.append(bm.verts.new((x, y, 0)))
        table_verts.append(bm.verts.new((x * 0.55, y * 0.55, crown_height)))
    
    culet = bm.verts.new((0, -height * 0.2, -pavilion_depth))
    
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(table_verts)
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([table_verts[i], table_verts[next_i], girdle_verts[next_i], girdle_verts[i]])
    
    for i in range(num_facets):
        next_i = (i + 1) % num_facets
        bm.faces.new([girdle_verts[i], girdle_verts[next_i], culet])
    
    mesh = bpy.data.meshes.new("HeartCut")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_Heart", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_trillion_gem(location, size):
    """Create a trillion (triangular) cut gem"""
    bm = bmesh.new()
    
    side = size
    h = side * math.sqrt(3) / 2
    crown_height = size * 0.13
    pavilion_depth = size * 0.4
    num_per_side = 6
    
    v1 = (0, h * 2/3)
    v2 = (-side/2, -h * 1/3)
    v3 = (side/2, -h * 1/3)
    
    def curved_edge(p1, p2, bulge=0.15):
        points = []
        mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx*dx + dy*dy)
        nx = -dy / length * bulge * side
        ny = dx / length * bulge * side
        
        for i in range(num_per_side):
            t = i / num_per_side
            x = (1-t)**2 * p1[0] + 2*(1-t)*t * (mid[0] + nx) + t**2 * p2[0]
            y = (1-t)**2 * p1[1] + 2*(1-t)*t * (mid[1] + ny) + t**2 * p2[1]
            points.append((x, y))
        return points
    
    girdle_points = []
    girdle_points.extend(curved_edge(v1, v2))
    girdle_points.extend(curved_edge(v2, v3))
    girdle_points.extend(curved_edge(v3, v1))
    
    girdle_verts = [bm.verts.new((p[0], p[1], 0)) for p in girdle_points]
    table_verts = [bm.verts.new((p[0] * 0.5, p[1] * 0.5, crown_height)) for p in girdle_points]
    culet = bm.verts.new((0, 0, -pavilion_depth))
    
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(table_verts)
    
    num_verts = len(girdle_verts)
    for i in range(num_verts):
        next_i = (i + 1) % num_verts
        bm.faces.new([table_verts[i], table_verts[next_i], girdle_verts[next_i], girdle_verts[i]])
    
    for i in range(num_verts):
        next_i = (i + 1) % num_verts
        bm.faces.new([girdle_verts[i], girdle_verts[next_i], culet])
    
    mesh = bpy.data.meshes.new("TrillionCut")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Gem_Trillion", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_gem_object(gem_type, cut_type, location, size, settings, index):
    """Create a gem with specified type, cut, and size"""
    cut_creators = {
        'ROUND_BRILLIANT': create_round_brilliant_gem,
        'PRINCESS': create_princess_gem,
        'EMERALD_CUT': create_emerald_cut_gem,
        'OVAL': create_oval_gem,
        'PEAR': create_pear_gem,
        'MARQUISE': create_marquise_gem,
        'CUSHION': create_cushion_gem,
        'HEART': create_heart_gem,
        'TRILLION': create_trillion_gem,
    }
    
    creator = cut_creators.get(cut_type, create_round_brilliant_gem)
    gem_obj = creator(location, size)
    gem_obj.name = f"Gem_{gem_type}_{cut_type}_{index:03d}"
    
    gem_obj.rotation_euler = (
        random.uniform(-0.1, 0.1),
        random.uniform(-0.1, 0.1),
        random.uniform(0, math.pi * 2)
    )
    
    mat = create_gem_material(gem_type, settings)
    gem_obj.data.materials.append(mat)
    
    return gem_obj


def create_gems(settings):
    """Create and distribute gems in the scene"""
    if not settings.enable_gems:
        return []
    
    gems = []
    
    # Calculate gem count: use ratio if > 0, otherwise use fixed count
    if settings.gem_ratio > 0:
        gem_count = max(1, int(settings.num_primitives * settings.gem_ratio))
    else:
        gem_count = settings.gem_count
    
    if settings.gem_type == 'MIXED':
        gem_types = GEM_TYPES
    else:
        gem_types = [settings.gem_type]
    
    if settings.gem_cut == 'MIXED':
        cut_types = GEM_CUTS
    else:
        cut_types = [settings.gem_cut]
    
    for i in range(gem_count):
        x = random.uniform(-settings.spread_x * 0.8, settings.spread_x * 0.8)
        y = random.uniform(-settings.spread_y * 0.8, settings.spread_y * 0.6)
        
        size = random.uniform(settings.gem_min_size, settings.gem_max_size)
        z = size * 0.15 + settings.height_above_plane
        
        gem_type = random.choice(gem_types)
        cut_type = random.choice(cut_types)
        
        location = Vector((x, y, z))
        
        gem = create_gem_object(gem_type, cut_type, location, size, settings, i)
        gems.append(gem)
    
    return gems


def distribute_primitives(settings):
    """Create and distribute all primitives"""
    palette = PALETTES[settings.color_palette]
    enabled_types = get_enabled_primitives(settings)
    
    type_assignments = None
    if settings.layout_mode == 'GROUPED' or settings.enable_grouping:
        positions, type_assignments = generate_grouped_positions(settings, enabled_types)
    elif settings.layout_mode == 'LINEAR' or settings.enable_linearity:
        positions = generate_linear_positions(settings, settings.num_primitives)
    elif settings.layout_mode == 'GRID':
        positions = generate_grid_positions(settings, settings.num_primitives)
    elif settings.layout_mode == 'RADIAL':
        positions = generate_radial_positions(settings, settings.num_primitives)
    elif settings.layout_mode == 'RULE_OF_THIRDS':
        positions = generate_rule_of_thirds_positions(settings, settings.num_primitives)
    elif settings.layout_mode == 'GOLDEN_SPIRAL':
        positions = generate_golden_spiral_positions(settings, settings.num_primitives)
    elif settings.layout_mode == 'DIAGONAL':
        positions = generate_diagonal_positions(settings, settings.num_primitives)
    elif settings.layout_mode == 'CLUSTERED':
        positions = generate_clustered_positions(settings, settings.num_primitives)
    else:
        positions = []
        min_distance = (settings.min_scale + settings.max_scale) / 2 * 1.0
        for i in range(settings.num_primitives):
            for attempt in range(100):
                pos = Vector((random.uniform(-settings.spread_x, settings.spread_x),
                             random.uniform(-settings.spread_y, settings.spread_y * 0.8), 0))
                if all((pos.xy - ex.xy).length >= min_distance for ex in positions) or attempt == 99:
                    positions.append(pos)
                    break
    
    positions = apply_density_falloff(positions, settings)
    while len(positions) < settings.num_primitives:
        positions.append(Vector((random.uniform(-settings.spread_x, settings.spread_x),
                                random.uniform(-settings.spread_y, settings.spread_y), 0)))
    positions = positions[:settings.num_primitives]
    
    # Build primitives data
    primitives_data = []
    last_material_type = None
    
    for i, pos in enumerate(positions):
        prim_type = type_assignments[i] if type_assignments and i < len(type_assignments) else random.choice(enabled_types)
        
        # Get material type
        mat_type = get_random_material_type(settings)
        
        data = {
            'position': pos,
            'type': prim_type,
            'scale': random.uniform(settings.min_scale, settings.max_scale),
            'rotation': random.uniform(0, math.pi * 2),
            'color': random.choice(palette['colors']),
            'material_type': mat_type,
            'force_material_contrast': False,
        }
        primitives_data.append(data)
    
    if settings.enable_sorting:
        primitives_data = apply_sorting(primitives_data, settings)
    if settings.enable_contrast:
        primitives_data = apply_contrast(primitives_data, settings, palette['colors'])
    
    # Apply material contrast if enabled
    if settings.enable_contrast and settings.contrast_mode == 'MATERIAL':
        mat_types_glossy = ['GLOSSY', 'METAL', 'GLASS', 'PLASTIC']
        mat_types_matte = ['MATTE', 'RUBBER', 'FABRIC', 'WOOD']
        
        for i, data in enumerate(primitives_data):
            if i > 0 and data.get('force_material_contrast'):
                prev_type = primitives_data[i-1]['material_type']
                if prev_type in mat_types_glossy:
                    data['material_type'] = random.choice(mat_types_matte)
                else:
                    data['material_type'] = random.choice(mat_types_glossy)
    
    if settings.use_focal_point:
        focal_pos = get_focal_point_position(settings)
        primitives_data.insert(0, {
            'position': Vector((focal_pos[0], focal_pos[1], 0)),
            'type': random.choice(enabled_types),
            'scale': settings.max_scale * 1.5,
            'rotation': 0,
            'color': palette['colors'][0],
            'material_type': get_random_material_type(settings),
        })
    
    # Create objects
    primitives = []
    for i, data in enumerate(primitives_data):
        obj = create_primitive_object(data['type'], data['position'], data['scale'], data['rotation'], settings, i)
        mat = create_material(data['color'], f"Mat_{i:03d}", data['material_type'])
        
        # Apply FBM texturing if enabled
        add_fbm_to_material(mat, settings, data['color'])
        
        obj.data.materials.append(mat)
        primitives.append(obj)
    
    # Create cluster-based scaffolding after all primitives are created
    if settings.enable_scaffolding:
        scaffolding_objects = create_scaffolding_for_scene(primitives, settings)
    
    return primitives


def setup_camera(backdrop_size, settings):
    """Create camera"""
    camera_distance = backdrop_size * 0.8
    camera_height = backdrop_size * 0.4
    
    bpy.ops.object.camera_add(location=(0, -camera_distance, camera_height))
    camera = bpy.context.active_object
    camera.name = "MainCamera"
    
    angle = math.atan2(camera_height, camera_distance)
    camera.rotation_euler = (math.radians(90) - angle + math.radians(5), 0, 0)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = max(settings.spread_x, settings.spread_y) * 2.5
    bpy.context.scene.camera = camera
    
    return camera


def setup_lighting(settings, backdrop_size):
    """Create lighting based on selected mode"""
    lights = []
    ld = backdrop_size * 0.6
    
    mode = settings.lighting_mode
    
    if mode == 'DEFAULT':
        # Balanced 4-point studio lighting
        lights = setup_lighting_default(settings, ld)
    elif mode == 'CINEMATIC':
        lights = setup_lighting_cinematic(settings, ld)
    elif mode == 'BACKLIGHTING':
        lights = setup_lighting_backlighting(settings, ld)
    elif mode == 'HDR':
        lights = setup_lighting_hdr(settings, ld)
    elif mode == 'IBL':
        lights = setup_lighting_ibl(settings, ld)
    elif mode == 'STADIUM':
        lights = setup_lighting_stadium(settings, ld)
    elif mode == 'GALLERY':
        lights = setup_lighting_gallery(settings, ld)
    
    # Setup world/environment
    setup_world_environment(settings, mode)
    
    return lights


def setup_lighting_default(settings, ld):
    """Default balanced 4-point studio lighting"""
    lights = []
    
    bpy.ops.object.light_add(type='AREA', location=(ld, -ld * 0.5, ld))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = settings.key_light_intensity
    key.data.size = settings.shadow_softness
    key.data.size_y = settings.shadow_softness * 0.8
    key.data.color = (1.0, 0.98, 0.95)
    key.rotation_euler = (math.radians(50), math.radians(15), math.radians(40))
    lights.append(key)
    
    bpy.ops.object.light_add(type='AREA', location=(-ld * 1.2, -ld * 0.4, ld * 0.6))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = settings.key_light_intensity * 0.35
    fill.data.size = settings.shadow_softness * 1.5
    fill.data.color = (0.95, 0.97, 1.0)
    fill.rotation_euler = (math.radians(55), math.radians(-10), math.radians(-35))
    fill.data.use_shadow = False
    lights.append(fill)
    
    bpy.ops.object.light_add(type='AREA', location=(0, ld, ld * 0.7))
    rim = bpy.context.active_object
    rim.name = "RimLight"
    rim.data.energy = settings.key_light_intensity * 0.25
    rim.data.size = settings.shadow_softness * 0.8
    rim.rotation_euler = (math.radians(120), 0, 0)
    lights.append(rim)
    
    bpy.ops.object.light_add(type='AREA', location=(0, 0, ld * 1.5))
    top = bpy.context.active_object
    top.name = "TopLight"
    top.data.energy = settings.key_light_intensity * 0.15
    top.data.size = settings.shadow_softness * 2.5
    lights.append(top)
    
    return lights


def setup_lighting_cinematic(settings, ld):
    """Cinematic dramatic lighting with strong contrast"""
    lights = []
    
    # Strong key light from side
    bpy.ops.object.light_add(type='AREA', location=(ld * 1.5, -ld * 0.3, ld * 0.8))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = settings.key_light_intensity * 1.5
    key.data.size = settings.shadow_softness * 0.6
    key.data.size_y = settings.shadow_softness * 1.2
    key.data.color = (1.0, 0.95, 0.85)  # Warm
    key.rotation_euler = (math.radians(45), math.radians(25), math.radians(60))
    lights.append(key)
    
    # Subtle fill - much weaker for drama
    bpy.ops.object.light_add(type='AREA', location=(-ld * 1.0, -ld * 0.5, ld * 0.4))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = settings.key_light_intensity * 0.1
    fill.data.size = settings.shadow_softness * 2.0
    fill.data.color = (0.85, 0.90, 1.0)  # Cool
    fill.rotation_euler = (math.radians(60), math.radians(-15), math.radians(-40))
    fill.data.use_shadow = False
    lights.append(fill)
    
    # Strong rim/hair light
    bpy.ops.object.light_add(type='AREA', location=(-ld * 0.5, ld * 0.8, ld * 1.0))
    rim = bpy.context.active_object
    rim.name = "RimLight"
    rim.data.energy = settings.key_light_intensity * 0.6
    rim.data.size = settings.shadow_softness * 0.5
    rim.data.color = (1.0, 0.98, 0.92)
    rim.rotation_euler = (math.radians(110), math.radians(-20), math.radians(-30))
    lights.append(rim)
    
    return lights


def setup_lighting_backlighting(settings, ld):
    """Backlighting setup for silhouettes and rim effects"""
    lights = []
    
    # Main backlight
    bpy.ops.object.light_add(type='AREA', location=(0, ld * 1.2, ld * 0.6))
    back = bpy.context.active_object
    back.name = "BackLight"
    back.data.energy = settings.key_light_intensity * 2.0
    back.data.size = settings.shadow_softness * 2.0
    back.data.size_y = settings.shadow_softness * 1.5
    back.data.color = (1.0, 0.98, 0.95)
    back.rotation_euler = (math.radians(130), 0, 0)
    lights.append(back)
    
    # Secondary backlight from side
    bpy.ops.object.light_add(type='AREA', location=(ld * 0.8, ld * 0.6, ld * 0.8))
    back2 = bpy.context.active_object
    back2.name = "BackLight2"
    back2.data.energy = settings.key_light_intensity * 0.8
    back2.data.size = settings.shadow_softness * 1.2
    back2.data.color = (1.0, 0.95, 0.90)
    back2.rotation_euler = (math.radians(115), math.radians(10), math.radians(30))
    lights.append(back2)
    
    # Subtle front fill to prevent complete silhouette
    bpy.ops.object.light_add(type='AREA', location=(0, -ld * 1.5, ld * 0.5))
    fill = bpy.context.active_object
    fill.name = "FrontFill"
    fill.data.energy = settings.key_light_intensity * 0.15
    fill.data.size = settings.shadow_softness * 3.0
    fill.data.color = (0.9, 0.95, 1.0)
    fill.rotation_euler = (math.radians(20), 0, 0)
    fill.data.use_shadow = False
    lights.append(fill)
    
    return lights


def setup_lighting_hdr(settings, ld):
    """Cinematic dramatic lighting with strong contrast and gem sparkle"""
    lights = []
    
    # Strong key light from side
    bpy.ops.object.light_add(type='AREA', location=(ld * 1.5, -ld * 0.3, ld * 0.8))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = settings.key_light_intensity * 1.5
    key.data.size = settings.shadow_softness * 0.6
    key.data.size_y = settings.shadow_softness * 1.2
    key.data.color = (1.0, 0.95, 0.85)  # Warm
    key.rotation_euler = (math.radians(45), math.radians(25), math.radians(60))
    lights.append(key)
    
    # Subtle fill - much weaker for drama
    bpy.ops.object.light_add(type='AREA', location=(-ld * 1.0, -ld * 0.5, ld * 0.4))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = settings.key_light_intensity * 0.1
    fill.data.size = settings.shadow_softness * 2.0
    fill.data.color = (0.85, 0.90, 1.0)  # Cool
    fill.rotation_euler = (math.radians(60), math.radians(-15), math.radians(-40))
    fill.data.use_shadow = False
    lights.append(fill)
    
    # Strong rim/hair light
    bpy.ops.object.light_add(type='AREA', location=(-ld * 0.5, ld * 0.8, ld * 1.0))
    rim = bpy.context.active_object
    rim.name = "RimLight"
    rim.data.energy = settings.key_light_intensity * 0.6
    rim.data.size = settings.shadow_softness * 0.5
    rim.data.color = (1.0, 0.98, 0.92)
    rim.rotation_euler = (math.radians(110), math.radians(-20), math.radians(-30))
    lights.append(rim)
    
    # === SPARKLE LIGHTS FOR GEMS ===
    # Small bright point lights from multiple angles to create gem sparkle/fire
    sparkle_intensity = settings.key_light_intensity * 0.8
    
    # Front-top sparkle light
    bpy.ops.object.light_add(type='POINT', location=(ld * 0.3, -ld * 0.8, ld * 1.2))
    sparkle1 = bpy.context.active_object
    sparkle1.name = "SparkleLight_1"
    sparkle1.data.energy = sparkle_intensity
    sparkle1.data.shadow_soft_size = 0.02  # Very sharp shadows for crisp highlights
    sparkle1.data.color = (1.0, 1.0, 1.0)  # Pure white
    lights.append(sparkle1)
    
    # Side sparkle light
    bpy.ops.object.light_add(type='POINT', location=(ld * 1.0, -ld * 0.2, ld * 0.5))
    sparkle2 = bpy.context.active_object
    sparkle2.name = "SparkleLight_2"
    sparkle2.data.energy = sparkle_intensity * 0.7
    sparkle2.data.shadow_soft_size = 0.02
    sparkle2.data.color = (1.0, 0.98, 0.95)  # Slightly warm
    lights.append(sparkle2)
    
    # Opposite side sparkle
    bpy.ops.object.light_add(type='POINT', location=(-ld * 0.8, -ld * 0.4, ld * 0.7))
    sparkle3 = bpy.context.active_object
    sparkle3.name = "SparkleLight_3"
    sparkle3.data.energy = sparkle_intensity * 0.5
    sparkle3.data.shadow_soft_size = 0.02
    sparkle3.data.color = (0.95, 0.98, 1.0)  # Slightly cool
    lights.append(sparkle3)
    
    # Top-down sparkle for table facet highlights
    bpy.ops.object.light_add(type='SPOT', location=(0, 0, ld * 1.5))
    sparkle_top = bpy.context.active_object
    sparkle_top.name = "SparkleLight_Top"
    sparkle_top.data.energy = sparkle_intensity * 1.2
    sparkle_top.data.spot_size = math.radians(60)
    sparkle_top.data.spot_blend = 0.3
    sparkle_top.data.shadow_soft_size = 0.01
    sparkle_top.data.color = (1.0, 1.0, 1.0)
    sparkle_top.rotation_euler = (0, 0, 0)
    lights.append(sparkle_top)
    
    # Back sparkle for fire effect through gems
    bpy.ops.object.light_add(type='POINT', location=(0, ld * 0.5, ld * 0.3))
    sparkle_back = bpy.context.active_object
    sparkle_back.name = "SparkleLight_Back"
    sparkle_back.data.energy = sparkle_intensity * 0.4
    sparkle_back.data.shadow_soft_size = 0.03
    sparkle_back.data.color = (1.0, 0.95, 0.9)
    lights.append(sparkle_back)
    
    return lights



def setup_lighting_stadium(settings, ld):
    """Stadium flood lighting - intense multi-light array from all directions"""
    lights = []
    base_energy = settings.key_light_intensity

    # === OVERHEAD RING - 6 bright area lights in a circle above the scene ===
    ring_count = 6
    ring_radius = ld * 1.2
    ring_height = ld * 1.4
    for i in range(ring_count):
        angle = (2 * math.pi / ring_count) * i
        x = ring_radius * math.cos(angle)
        y = ring_radius * math.sin(angle)
        bpy.ops.object.light_add(type='AREA', location=(x, y, ring_height))
        light = bpy.context.active_object
        light.name = f"StadiumRing_{i+1}"
        light.data.energy = base_energy * 0.8
        light.data.size = settings.shadow_softness * 1.2
        light.data.size_y = settings.shadow_softness * 0.8
        light.data.color = (1.0, 0.99, 0.96)
        # Aim towards center
        dir_x = -x
        dir_y = -y
        dir_z = -ring_height
        light.rotation_euler = (
            math.atan2(math.sqrt(dir_x**2 + dir_y**2), -dir_z),
            0,
            math.atan2(dir_x, -dir_y)
        )
        lights.append(light)

    # === MID-LEVEL FILL RING - 4 softer lights at mid height ===
    mid_count = 4
    mid_radius = ld * 0.9
    mid_height = ld * 0.7
    for i in range(mid_count):
        angle = (2 * math.pi / mid_count) * i + math.radians(45)  # offset from ring above
        x = mid_radius * math.cos(angle)
        y = mid_radius * math.sin(angle)
        bpy.ops.object.light_add(type='AREA', location=(x, y, mid_height))
        light = bpy.context.active_object
        light.name = f"StadiumMid_{i+1}"
        light.data.energy = base_energy * 0.4
        light.data.size = settings.shadow_softness * 2.0
        light.data.color = (0.97, 0.98, 1.0)
        light.rotation_euler = (
            math.atan2(math.sqrt(x**2 + y**2), mid_height),
            0,
            math.atan2(-x, y)
        )
        light.data.use_shadow = False
        lights.append(light)

    # === GROUND KICK LIGHTS - 4 low point lights for under-fill ===
    kick_count = 4
    kick_radius = ld * 1.0
    kick_height = ld * 0.08
    for i in range(kick_count):
        angle = (2 * math.pi / kick_count) * i + math.radians(22)
        x = kick_radius * math.cos(angle)
        y = kick_radius * math.sin(angle)
        bpy.ops.object.light_add(type='POINT', location=(x, y, kick_height))
        light = bpy.context.active_object
        light.name = f"StadiumKick_{i+1}"
        light.data.energy = base_energy * 0.25
        light.data.shadow_soft_size = settings.shadow_softness * 0.3
        light.data.color = (1.0, 0.98, 0.94)
        lights.append(light)

    # === OVERHEAD SPOTS - 2 bright spots pointing straight down ===
    for i, offset_x in enumerate([-ld * 0.3, ld * 0.3]):
        bpy.ops.object.light_add(type='SPOT', location=(offset_x, 0, ld * 1.8))
        spot = bpy.context.active_object
        spot.name = f"StadiumSpot_{i+1}"
        spot.data.energy = base_energy * 1.2
        spot.data.spot_size = math.radians(55)
        spot.data.spot_blend = 0.4
        spot.data.shadow_soft_size = 0.05
        spot.data.color = (1.0, 1.0, 0.98)
        spot.rotation_euler = (0, 0, 0)
        lights.append(spot)

    return lights


def setup_lighting_gallery(settings, ld):
    """Gallery exhibition lighting - multiple directed spots like a museum or art gallery"""
    lights = []
    base_energy = settings.key_light_intensity

    # === CEILING TRACK SPOTS - 8 focused spots from a grid above ===
    spot_positions = [
        ( ld * 0.6,  -ld * 0.6, ld * 1.5),
        (-ld * 0.6,  -ld * 0.6, ld * 1.5),
        ( ld * 0.6,   ld * 0.6, ld * 1.5),
        (-ld * 0.6,   ld * 0.6, ld * 1.5),
        ( ld * 0.0,  -ld * 0.9, ld * 1.4),
        ( ld * 0.9,   ld * 0.0, ld * 1.4),
        (-ld * 0.9,   ld * 0.0, ld * 1.4),
        ( ld * 0.0,   ld * 0.9, ld * 1.4),
    ]
    spot_colors = [
        (1.0, 0.98, 0.94),   # warm white
        (0.96, 0.98, 1.0),   # cool white
        (1.0, 0.97, 0.92),   # warm
        (0.95, 0.97, 1.0),   # cool
        (1.0, 0.99, 0.96),   # neutral warm
        (1.0, 0.96, 0.90),   # amber tint
        (0.94, 0.96, 1.0),   # blue tint
        (1.0, 0.98, 0.95),   # neutral
    ]

    for i, (pos, color) in enumerate(zip(spot_positions, spot_colors)):
        bpy.ops.object.light_add(type='SPOT', location=pos)
        spot = bpy.context.active_object
        spot.name = f"GallerySpot_{i+1}"
        spot.data.energy = base_energy * 0.7
        spot.data.spot_size = math.radians(40)
        spot.data.spot_blend = 0.35
        spot.data.shadow_soft_size = 0.04
        spot.data.color = color
        # Aim towards center-ground
        dx, dy, dz = -pos[0], -pos[1], -pos[2] * 0.8
        spot.rotation_euler = (
            math.atan2(math.sqrt(dx**2 + dy**2), -dz),
            0,
            math.atan2(dx, -dy)
        )
        lights.append(spot)

    # === ACCENT WASH - 3 wide area lights for ambient fill ===
    wash_positions = [
        (-ld * 1.3, -ld * 0.2, ld * 1.0),
        ( ld * 1.3, -ld * 0.2, ld * 1.0),
        ( ld * 0.0,  ld * 1.3, ld * 0.8),
    ]
    for i, pos in enumerate(wash_positions):
        bpy.ops.object.light_add(type='AREA', location=pos)
        wash = bpy.context.active_object
        wash.name = f"GalleryWash_{i+1}"
        wash.data.energy = base_energy * 0.15
        wash.data.size = settings.shadow_softness * 3.0
        wash.data.color = (0.98, 0.98, 1.0)
        wash.rotation_euler = (
            math.atan2(math.sqrt(pos[0]**2 + pos[1]**2), pos[2]),
            0,
            math.atan2(-pos[0], pos[1])
        )
        wash.data.use_shadow = False
        lights.append(wash)

    # === PEDESTAL UPLIGHTS - 3 small point lights near ground for drama ===
    up_positions = [
        ( ld * 0.0,  -ld * 0.3, ld * 0.02),
        ( ld * 0.3,   ld * 0.15, ld * 0.02),
        (-ld * 0.3,   ld * 0.15, ld * 0.02),
    ]
    for i, pos in enumerate(up_positions):
        bpy.ops.object.light_add(type='POINT', location=pos)
        up = bpy.context.active_object
        up.name = f"GalleryUplight_{i+1}"
        up.data.energy = base_energy * 0.2
        up.data.shadow_soft_size = settings.shadow_softness * 0.2
        up.data.color = (1.0, 0.97, 0.92)
        lights.append(up)

    return lights


def setup_lighting_ibl(settings, ld):
    """Image-based lighting setup - uses world environment as primary light"""
    lights = []
    
    # Only add subtle fill lights - environment does the heavy lifting
    bpy.ops.object.light_add(type='AREA', location=(ld * 0.8, -ld * 0.5, ld * 0.8))
    key = bpy.context.active_object
    key.name = "KeyAccent"
    key.data.energy = settings.key_light_intensity * 0.3
    key.data.size = settings.shadow_softness * 1.5
    key.data.color = (1.0, 0.98, 0.95)
    key.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    lights.append(key)
    
    # Rim accent
    bpy.ops.object.light_add(type='AREA', location=(0, ld * 0.8, ld * 0.6))
    rim = bpy.context.active_object
    rim.name = "RimAccent"
    rim.data.energy = settings.key_light_intensity * 0.2
    rim.data.size = settings.shadow_softness
    rim.rotation_euler = (math.radians(115), 0, 0)
    lights.append(rim)
    
    return lights


def setup_world_environment(settings, mode):
    """Setup world/environment based on lighting mode"""
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    bg_color = PALETTES[settings.color_palette]['background']
    
    if mode == 'IBL':
        # Create gradient environment for IBL
        output = nodes.new('ShaderNodeOutputWorld')
        output.location = (400, 0)
        
        bg = nodes.new('ShaderNodeBackground')
        bg.location = (200, 0)
        bg.inputs['Strength'].default_value = 1.0
        
        # Sky gradient
        gradient = nodes.new('ShaderNodeTexGradient')
        gradient.location = (-200, 0)
        gradient.gradient_type = 'SPHERICAL'
        
        tex_coord = nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (-400, 0)
        
        color_ramp = nodes.new('ShaderNodeValToRGB')
        color_ramp.location = (0, 0)
        # Sky colors based on palette
        sky_bottom = tuple(min(1.0, c * 1.1) for c in bg_color)
        sky_top = tuple(c * 0.85 for c in bg_color)
        color_ramp.color_ramp.elements[0].color = (*sky_bottom, 1.0)
        color_ramp.color_ramp.elements[0].position = 0.3
        color_ramp.color_ramp.elements[1].color = (*sky_top, 1.0)
        color_ramp.color_ramp.elements[1].position = 0.7
        
        links.new(tex_coord.outputs['Generated'], gradient.inputs['Vector'])
        links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bg.inputs['Color'])
        links.new(bg.outputs['Background'], output.inputs['Surface'])
        
    else:
        # Simple background color
        output = nodes.new('ShaderNodeOutputWorld')
        output.location = (200, 0)
        
        bg = nodes.new('ShaderNodeBackground')
        bg.location = (0, 0)
        bg.inputs['Color'].default_value = (bg_color[0], bg_color[1], bg_color[2], 1.0)
        
        # Adjust strength based on mode
        if mode == 'CINEMATIC':
            bg.inputs['Strength'].default_value = 0.1
        elif mode == 'BACKLIGHTING':
            bg.inputs['Strength'].default_value = 0.15
        elif mode == 'HDR':
            bg.inputs['Strength'].default_value = 0.4
        elif mode == 'STADIUM':
            bg.inputs['Strength'].default_value = 0.05
        elif mode == 'GALLERY':
            bg.inputs['Strength'].default_value = 0.08
        else:
            bg.inputs['Strength'].default_value = 0.25
        
        links.new(bg.outputs['Background'], output.inputs['Surface'])


def setup_render_settings(settings):
    """Configure render"""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = settings.render_samples
    scene.cycles.use_denoising = settings.use_denoising
    if settings.use_denoising:
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.max_bounces = 12
    scene.cycles.transmission_bounces = 8
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'


def organize_scene():
    """Organize into collections"""
    for name in ["Primitives", "Lights"]:
        if name not in bpy.data.collections:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
    
    prims_col = bpy.data.collections["Primitives"]
    lights_col = bpy.data.collections["Lights"]
    
    # All possible light names from different lighting modes
    light_names = [
        "KeyLight", "FillLight", "RimLight", "TopLight",
        "BackLight", "BackLight2", "FrontFill",
        "FillLight_1", "FillLight_2", "FillLight_3",
        "RimLight1", "RimLight2",
        "KeyAccent", "RimAccent"
    ]
    
    for obj in bpy.data.objects:
        if obj.name.startswith("Primitive_"):
            if obj.name not in prims_col.objects:
                try:
                    bpy.context.scene.collection.objects.unlink(obj)
                except: pass
                prims_col.objects.link(obj)
        elif obj.name in light_names or obj.type == 'LIGHT':
            if obj.name not in lights_col.objects:
                try:
                    bpy.context.scene.collection.objects.unlink(obj)
                except: pass
                lights_col.objects.link(obj)


# ===========================================
# OPERATORS
# ===========================================

class PRIMS_OT_generate_scene(Operator):
    """Generate scene"""
    bl_idname = "prims.generate_scene"
    bl_label = "Generate Scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.prim_comp_settings
        
        if settings.random_seed > 0:
            random.seed(settings.random_seed)
        else:
            random.seed()
        
        cleanup_scene()
        backdrop, backdrop_size = create_backdrop(settings)
        primitives = distribute_primitives(settings)
        
        # Create gems if enabled
        gems = create_gems(settings)
        
        # Collision resolution (include gems)
        all_objects = primitives + gems
        if settings.enable_collision_detection:
            adjustments = resolve_all_collisions(all_objects, settings)
            self.report({'INFO'}, f"Resolved {adjustments} collisions")
        
        camera = setup_camera(backdrop_size, settings)
        lights = setup_lighting(settings, backdrop_size)
        setup_render_settings(settings)
        organize_scene()
        
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
        
        gem_msg = f" and {len(gems)} gems" if gems else ""
        self.report({'INFO'}, f"Scene generated with {len(primitives)} primitives{gem_msg}!")
        return {'FINISHED'}


class PRIMS_OT_render_scene(Operator):
    """Render scene"""
    bl_idname = "prims.render_scene"
    bl_label = "Render Scene"
    
    def execute(self, context):
        bpy.ops.render.render('INVOKE_DEFAULT')
        return {'FINISHED'}


class PRIMS_OT_randomize_seed(Operator):
    """Randomize seed"""
    bl_idname = "prims.randomize_seed"
    bl_label = "Randomize"
    
    def execute(self, context):
        import time
        context.scene.prim_comp_settings.random_seed = int(time.time()) % 10000
        return {'FINISHED'}


# ===========================================
# UI PANELS
# ===========================================

class PRIMS_PT_main_panel(Panel):
    bl_label = "Primitive Composition"
    bl_idname = "PRIMS_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    
    def draw(self, context):
        box = self.layout.box()
        box.scale_y = 1.5
        box.operator("prims.generate_scene", icon='MESH_ICOSPHERE')


class PRIMS_PT_primitives_panel(Panel):
    bl_label = "Primitive Types"
    bl_idname = "PRIMS_PT_primitives_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        col = self.layout.column(align=True)
        for row_items in [("use_cube", "use_sphere"), ("use_cylinder", "use_cone"),
                          ("use_torus", "use_ico_sphere"), ("use_capsule", "use_rounded_cube")]:
            row = col.row(align=True)
            for item in row_items:
                row.prop(settings, item, toggle=True)


class PRIMS_PT_colors_panel(Panel):
    bl_label = "Color Palette"
    bl_idname = "PRIMS_PT_colors_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    
    def draw(self, context):
        self.layout.prop(context.scene.prim_comp_settings, "color_palette", text="")


class PRIMS_PT_distribution_panel(Panel):
    bl_label = "Distribution"
    bl_idname = "PRIMS_PT_distribution_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
   
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        layout.prop(settings, "num_primitives")
        col = layout.column(align=True)
        col.prop(settings, "spread_x")
        col.prop(settings, "spread_y")
        layout.separator()
        col = layout.column(align=True)
        col.prop(settings, "min_scale")
        col.prop(settings, "max_scale")
        layout.prop(settings, "height_above_plane")


class PRIMS_PT_collision_panel(Panel):
    bl_label = "Collision Detection"
    bl_idname = "PRIMS_PT_collision_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        layout.prop(settings, "enable_collision_detection")
        if settings.enable_collision_detection:
            col = layout.column(align=True)
            col.prop(settings, "collision_iterations")
            col.prop(settings, "collision_padding")


class PRIMS_PT_layout_panel(Panel):
    bl_label = "Layout Mode"
    bl_idname = "PRIMS_PT_layout_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        layout.prop(settings, "layout_mode", text="")
        
        if settings.layout_mode == 'GROUPED':
            box = layout.box()
            box.label(text="Group Settings:", icon='GROUP')
            box.prop(settings, "group_spacing")
            box.prop(settings, "group_tightness")
        elif settings.layout_mode in ['LINEAR', 'DIAGONAL']:
            box = layout.box()
            box.label(text="Line Settings:", icon='IPO_LINEAR')
            if settings.layout_mode == 'LINEAR':
                box.prop(settings, "line_type")
                box.prop(settings, "num_lines")
            box.prop(settings, "line_angle")


class PRIMS_PT_composition_panel(Panel):
    bl_label = "Composition Rules"
    bl_idname = "PRIMS_PT_composition_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        
        box = layout.box()
        box.prop(settings, "enable_grouping", text="Grouping")
        if settings.enable_grouping:
            box.prop(settings, "group_spacing")
            box.prop(settings, "group_tightness")
        
        box = layout.box()
        box.prop(settings, "enable_sorting", text="Sorting")
        if settings.enable_sorting:
            col = box.column(align=True)
            col.prop(settings, "sort_by", text="")
            col.prop(settings, "sort_direction", text="")
            col.prop(settings, "sort_axis", text="")
        
        box = layout.box()
        box.prop(settings, "enable_contrast", text="Contrast")
        if settings.enable_contrast:
            box.prop(settings, "contrast_mode", text="")
            box.prop(settings, "contrast_strength", slider=True)
        
        box = layout.box()
        box.prop(settings, "enable_linearity", text="Linearity")
        if settings.enable_linearity:
            box.prop(settings, "line_type", text="")
            box.prop(settings, "num_lines")
            box.prop(settings, "line_angle")


class PRIMS_PT_advanced_panel(Panel):
    bl_label = "Advanced Composition"
    bl_idname = "PRIMS_PT_advanced_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        
        box = layout.box()
        box.prop(settings, "use_focal_point", text="Focal Point")
        if settings.use_focal_point:
            box.prop(settings, "focal_point_position", text="")
        
        layout.prop(settings, "density_falloff")


class PRIMS_PT_materials_panel(Panel):
    bl_label = "Materials"
    bl_idname = "PRIMS_PT_materials_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        
        layout.prop(settings, "material_mode")
        
        if settings.material_mode == 'SINGLE':
            layout.prop(settings, "single_material_type", text="")
        
        elif settings.material_mode == 'WEIGHTED':
            box = layout.box()
            box.label(text="Material Weights:", icon='MATERIAL')
            col = box.column(align=True)
            col.prop(settings, "weight_matte", slider=True)
            col.prop(settings, "weight_glossy", slider=True)
            col.prop(settings, "weight_plastic", slider=True)
            col.prop(settings, "weight_metal", slider=True)
            col.prop(settings, "weight_glass", slider=True)
            col.prop(settings, "weight_wood", slider=True)
            col.prop(settings, "weight_ceramic", slider=True)
            col.prop(settings, "weight_rubber", slider=True)
            col.prop(settings, "weight_sss", slider=True)


class PRIMS_PT_lighting_panel(Panel):
    bl_label = "Lighting"
    bl_idname = "PRIMS_PT_lighting_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
   
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        
        layout.prop(settings, "lighting_mode")
        layout.separator()
        layout.prop(settings, "shadow_softness")
        layout.prop(settings, "key_light_intensity")


class PRIMS_PT_backdrop_panel(Panel):
    bl_label = "Backdrop Settings"
    bl_idname = "PRIMS_PT_backdrop_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
  
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        
        # Backdrop type selector
        layout.prop(settings, "backdrop_type")
        
        layout.separator()
        
        # Color customization
        box = layout.box()
        box.label(text="Color:", icon='COLOR')
        box.prop(settings, "backdrop_use_custom_color")
        if settings.backdrop_use_custom_color:
            box.prop(settings, "backdrop_custom_color", text="")
        
        # Texture settings
        # box = layout.box()
        # box.label(text="Texture:", icon='TEXTURE')
        # col = box.column(align=True)
        # col.prop(settings, "backdrop_texture_scale")
        # col.prop(settings, "backdrop_bump_strength")
        
        # Surface properties
        # box = layout.box()
        # box.label(text="Surface:", icon='SHADING_RENDERED')
        # col = box.column(align=True)
        # col.prop(settings, "backdrop_roughness")
        
        # Show glossy amount for applicable materials
        if settings.backdrop_type in ['WOODEN_TABLE', 'MARBLED_FLOOR', 'METALLIC_PLATE']:
            col.prop(settings, "backdrop_glossy_amount")
        
        # Displacement option
        # layout.prop(settings, "backdrop_use_displacement")


class PRIMS_PT_fbm_panel(Panel):
    bl_label = "FBM Textures"
    bl_idname = "PRIMS_PT_fbm_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        
        # Backdrop FBM
        box = layout.box()
        box.prop(settings, "use_backdrop_fbm")
        if settings.use_backdrop_fbm:
            col = box.column(align=True)
            col.prop(settings, "backdrop_fbm_strength")
            col.prop(settings, "backdrop_fbm_scale")
            col.prop(settings, "backdrop_fbm_octaves")
        
        # Object FBM
        box = layout.box()
        box.prop(settings, "use_object_fbm")
        if settings.use_object_fbm:
            col = box.column(align=True)
            col.prop(settings, "object_fbm_chance", slider=True)
            col.prop(settings, "object_fbm_mode")
            col.prop(settings, "object_fbm_strength")
            col.prop(settings, "object_fbm_scale")


class PRIMS_PT_scaffolding_panel(Panel):
    bl_label = "Scaffolding (Experimental)"
    bl_idname = "PRIMS_PT_scaffolding_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        
        # Enable toggle
        layout.prop(settings, "enable_scaffolding")
        
        if settings.enable_scaffolding:
            layout.separator()
            
            # Pattern type
            box = layout.box()
            box.label(text="Pattern:", icon='MOD_LATTICE')
            box.prop(settings, "scaffolding_type", text="")
            
            # Clustering settings
            box = layout.box()
            box.label(text="Clustering:", icon='GROUP_VERTEX')
            col = box.column(align=True)
            col.prop(settings, "scaffolding_cluster_distance")
            col.prop(settings, "scaffolding_padding")
            
            # Wire geometry settings
            box = layout.box()
            box.label(text="Wire Geometry:", icon='MESH_CYLINDER')
            col = box.column(align=True)
            col.prop(settings, "scaffolding_wire_thickness")
            col.prop(settings, "scaffolding_density")
            col.prop(settings, "scaffolding_height_layers")
            col.prop(settings, "scaffolding_deviation")
            
            # Material settings
            box = layout.box()
            box.label(text="Material:", icon='MATERIAL')
            box.prop(settings, "scaffolding_material", text="")
            box.prop(settings, "scaffolding_color", text="")
            box.prop(settings, "scaffolding_roughness", slider=True)


class PRIMS_PT_gems_panel(Panel):
    bl_label = "Gems (Experimental)"
    bl_idname = "PRIMS_PT_gems_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        
        # Enable toggle
        layout.prop(settings, "enable_gems")
        
        if settings.enable_gems:
            layout.separator()
            
            # Gem type and count
            box = layout.box()
            box.label(text="Gem Selection:", icon='SHADING_RENDERED')
            box.prop(settings, "gem_type", text="")
            box.prop(settings, "gem_cut", text="")
            
            # Count settings
            box = layout.box()
            box.label(text="Count:", icon='PARTICLES')
            box.prop(settings, "gem_ratio", slider=True)
            if settings.gem_ratio > 0:
                box.label(text=f"  (~{int(settings.num_primitives * settings.gem_ratio)} gems)")
            else:
                box.prop(settings, "gem_count")
            
            # Size settings
            box = layout.box()
            box.label(text="Size:", icon='ARROW_LEFTRIGHT')
            col = box.column(align=True)
            col.prop(settings, "gem_min_size")
            col.prop(settings, "gem_max_size")
            
            # Quality and appearance
            box = layout.box()
            box.label(text="Appearance:", icon='MATERIAL')
            box.prop(settings, "gem_quality", text="")
            box.prop(settings, "gem_saturation", slider=True)
            box.prop(settings, "gem_dispersion", slider=True)


class PRIMS_PT_render_panel(Panel):
    bl_label = "Render"
    bl_idname = "PRIMS_PT_render_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Primitives'
    bl_parent_id = "PRIMS_PT_main_panel"
    
    def draw(self, context):
        settings = context.scene.prim_comp_settings
        layout = self.layout
        layout.prop(settings, "render_samples")
        layout.prop(settings, "use_denoising")
        layout.separator()
        row = layout.row(align=True)
        row.prop(settings, "random_seed")
        row.operator("prims.randomize_seed", text="", icon='FILE_REFRESH')
        layout.separator()
        box = layout.box()
        box.scale_y = 1.3
        box.operator("prims.render_scene", icon='RENDER_STILL')


# ===========================================
# REGISTRATION
# ===========================================

classes = [
    PrimitiveCompositionSettings,
    PRIMS_OT_generate_scene,
    PRIMS_OT_render_scene,
    PRIMS_OT_randomize_seed,
    PRIMS_PT_main_panel,
    PRIMS_PT_lighting_panel,
    PRIMS_PT_backdrop_panel,
    PRIMS_PT_primitives_panel,
    PRIMS_PT_colors_panel,
    PRIMS_PT_distribution_panel,
    PRIMS_PT_collision_panel,
    PRIMS_PT_layout_panel,
    PRIMS_PT_composition_panel,
    PRIMS_PT_advanced_panel,
    PRIMS_PT_materials_panel,
    PRIMS_PT_scaffolding_panel,
    PRIMS_PT_gems_panel,
    PRIMS_PT_render_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.prim_comp_settings = bpy.props.PointerProperty(type=PrimitiveCompositionSettings)
    
    print("\n" + "=" * 65)
    print("SCENE COMPOSER - FULL FEATURED")
    print("=" * 65)
    print("\nFEATURES:")
    print("  • Collision Detection - Objects automatically separated")
    print("  • 16 Material Types including SSS materials")
    print("  • 7 Lighting Modes:")
    print("    - Default: Balanced 4-point studio lighting")
    print("    - Cinematic: Dramatic contrast with strong key")
    print("    - Backlighting: Strong rim/back light for silhouettes")
    print("    - HDR: High dynamic range with multiple fills")
    print("    - IBL: Environment-based lighting")
    print("    - Stadium Flood: 16-light array from all directions")
    print("    - Gallery Exhibition: 14 museum-style spots and washes")
    print("  • 11 Backdrop Types:")
    print("    - Default Cyclorama, Folded Curtain, Creased Paper")
    print("    - Wooden Table, Marbled Floor, Cemented Ground")
    print("    - Lawn Grass, Metallic Plate, SSS Skin")
    print("    - Lake Surface, Rubber Mat")
    print("  • Scaffolding Networks (6 types):")
    print("    - Fence, Net, Spiral Net, Geodesic Net")
    print("    - Random Web, Wire Cage")
    print("    - Clusters nearby primitives automatically")
    print("    - Adjustable wire thickness & deviation")
    print("  • Gems (12 types, 9 cuts):")
    print("    - Diamond, Ruby, Sapphire, Emerald, Topaz")
    print("    - Amethyst, Aquamarine, Citrine, Peridot")
    print("    - Garnet, Opal, Tanzanite")
    print("    - Round Brilliant, Princess, Emerald Cut, Oval")
    print("    - Pear, Marquise, Cushion, Heart, Trillion")
    print("    - Accurate IOR and color per gem type")
    print("  • FBM Textures:")
    print("    - Backdrop bump mapping (creases/wrinkles)")
    print("    - Object texturing (bump, color, roughness)")
    print("\nOpen sidebar (N) → 'Primitives' tab")
    print("=" * 65 + "\n")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.prim_comp_settings


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
