import base64
import math
from lxml.etree import _Element
from pycadsx.cadtypes import CadTypes


class BaseGeometry:
    def __init__(self, element: _Element) -> None:
        self.id   = int(element.get('id', 0))
        self.type = self._type(element)

    def _type(self, element: _Element):
        return CadTypes.Geometry.Type.get_value( int( element.get('type', '767') ) )

    def _origin(self, element: _Element):
        return [ float( element.get(i) ) for i in ['x', 'y', 'z'] ]

    def _matrix(self, element: _Element):
        return [ [ float( element.get(f'{a0}{a1}') ) for a1 in ['x', 'y', 'z'] ] for a0 in ['x', 'y', 'z'] ]
    
    def _base64_string_to_string(self, base64_string: str):
        return base64.urlsafe_b64decode(base64_string).decode('utf-16le')


class BaseDimensionGeometry(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin                    = self._origin(element)
        self.matrix                    = self._matrix(element)
        self.text_info: DimensionValue = None
        self.line_info: DimensionLine  = None


class Line3D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin = self._origin(element)
        self.vector = [ float(element.get(i)) for i in ['vx', 'vy', 'vz'] ]
        self.length = float(element.get('leng'))
        self.csgsol = int(element.get('csgsol'))
        self.prmno  = int(element.get('prmno'))
        self.edgeno = int(element.get('edgeno'))


class Line2D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin = self._origin(element)
        self.vector = [ float(element.get(i)) for i in ['vx', 'vy', 'vz'] ]
        self.length = float(element.get('leng'))


class Point3D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin = self._origin(element)


class Point2D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin = self._origin(element)


class Arc3D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.radius       = float(element.get('r'))
        self.origin       = self._origin(element)
        self.vector       = [ float(element.get(i)) for i in ['vx', 'vy', 'vz'] ]
        self.vector_start = [ float(element.get(i)) for i in ['sx', 'sy', 'sz'] ]
        self.vector_end   = [ float(element.get(i)) for i in ['ex', 'ey', 'ez'] ]
        self.csgsol       = int(element.get('csgsol'))
        self.prmno        = int(element.get('prmno'))
        self.edgeno       = int(element.get('edgeno'))


class Arc2D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin       = self._origin(element)
        self.radius       = float(element.get('r'))
        self.angle_start = float(element.get('sang')) / math.pi * 180.0
        self.angle_end   = float(element.get('eang')) / math.pi * 180.0


class Circle3D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin = self._origin(element)
        self.radius = float(element.get('r'))
        self.vector = [ float(element.get(i)) for i in ['vx', 'vy', 'vz'] ]
        self.csgsol = int(element.get('csgsol'))
        self.prmno  = int(element.get('prmno'))
        self.edgeno = int(element.get('edgeno'))


class Circle2D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.radius      = float(element.get('r'))
        self.angle_start = float(element.get('sang')) / math.pi * 180.0
        self.angle_end   = float(element.get('eang')) / math.pi * 180.0


class Ellipse2D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.radius1     = float(element.get('r1'))
        self.radius2     = float(element.get('r2'))
        self.angle       = float(element.get('ang')) / math.pi * 180.0
        self.angle_start = float(element.get('sang')) / math.pi * 180.0
        self.angle_end   = float(element.get('eang')) / math.pi * 180.0


class EllipseArc2D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.radius1     = float(element.get('r1'))
        self.radius2     = float(element.get('r2'))
        self.angle       = float(element.get('ang')) / math.pi * 180.0
        self.angle_start = float(element.get('sang')) / math.pi * 180.0
        self.angle_end   = float(element.get('eang')) / math.pi * 180.0


class Spline2D(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.kind        = CadTypes.Entity.SplineKind.get_value( int(element.get('kind')) )
        self.angle_start = float(element.get('sang')) / math.pi * 180.0
        self.angle_end   = float(element.get('eang')) / math.pi * 180.0


class OtherCurve(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.csgsol      = int(element.get('csgsol'))
        self.prmno       = int(element.get('prmno'))
        self.edgeno      = int(element.get('edgeno'))


class Cap(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.radius1     = float(element.get('r1'))
        self.radius2     = float(element.get('r2'))
        self.orient      = element.get('orient') != '0'
        self.csgsol      = int(element.get('csgsol'))
        self.prmno       = int(element.get('prmno'))
        self.edgeno      = int(element.get('edgeno'))


class Plane(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.csgsol      = int(element.get('csgsol'))
        self.prmno       = int(element.get('prmno'))
        self.edgeno      = int(element.get('edgeno'))


class Cone(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.radius      = float(element.get('r'))
        self.half_angle  = float(element.get('half_ang')) / math.pi * 180.0
        self.orient      = element.get('orient') != '0'
        self.csgsol      = int(element.get('csgsol'))
        self.prmno       = int(element.get('prmno'))
        self.faceno      = int(element.get('faceno'))


class Cylinder(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.radius      = float(element.get('r'))
        self.half_angle  = float(element.get('half_ang')) / math.pi * 180.0
        self.orient      = element.get('orient') != '0'
        self.csgsol      = int(element.get('csgsol'))
        self.prmno       = int(element.get('prmno'))
        self.faceno      = int(element.get('faceno'))


class Sphere(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.radius      = float(element.get('r'))
        self.half_angle  = float(element.get('half_ang')) / math.pi * 180.0
        self.orient      = element.get('orient') != '0'
        self.csgsol      = int(element.get('csgsol'))
        self.prmno       = int(element.get('prmno'))
        self.faceno      = int(element.get('faceno'))


class Torus(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.max_radius  = float(element.get('maxr'))
        self.min_radius  = float(element.get('minr'))
        self.orient      = element.get('orient') != '0'
        self.csgsol      = int(element.get('csgsol'))
        self.prmno       = int(element.get('prmno'))
        self.faceno      = int(element.get('faceno'))


class OtherSurf(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.orient      = element.get('orient') != '0'
        self.csgsol      = int(element.get('csgsol'))
        self.prmno       = int(element.get('prmno'))
        self.faceno      = int(element.get('faceno'))


class Text(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin    = self._origin(element)
        self.matrix    = self._matrix(element)
        self.base_pnt  = int(element.get('base_pnt'))
        self.way       = int(element.get('way'))
        self.lres      = [ int( element.get(f'lres{i:02d}') ) for i in range(2, 10) ]
        self.dres      = [ float( element.get(f'dres{i:02d}') ) for i in range(10) ]
        self.position  = [ float( element.get(f'pntx') ), float( element.get(f'pnty') ), float( element.get(f'pntz') ) ]
        self.texts     = [ self._base64_string_to_string( element.get(f'str{i:02d}') ) for i in range(1, 21) ]
        self.attribute = TextAttribute(element.xpath('./sx_draft_atr_text')[0])


class LeadLine(BaseGeometry):
    def __init__(self, element: _Element) -> None:
        super().__init__(element)
        self.arrow_type = CadTypes.Geometry.DimensionLine.Arrow.get_value( int(element.get('arrow_type')) )
        self.pnt_num = element.get('pnt_num')
        self.point = [ [ float( sx_pos.get(i) ) for i in ['x', 'y', 'z'] ] for sx_pos in element.xpath('./sx_pos') ]


class Note(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)

        self.origin   = self._origin(element)
        self.matrix   = self._matrix(element)

        self.verline = int(element.get('verlin')) != '2'
        self.underline = int(element.get('underlin')) != '2'
        self.lead_line_count = int(element.get('lead_line_num'))
        self.text_line_num = int(element.get('text_line_num'))

        self.texts = [ self._base64_string_to_string( element.get(f'str{i:02d}') ) for i in range(1, 21) ]

        self.lres05 = int(element.get('lres05'))
        self.lres06 = int(element.get('lres06'))
        self.lres07 = int(element.get('lres07'))
        self.lres08 = int(element.get('lres08'))
        self.lres09 = int(element.get('lres09'))

        self.dres00 = float(element.get('dres00'))
        self.dres01 = float(element.get('dres01'))
        self.dres02 = float(element.get('dres02'))
        self.dres03 = float(element.get('dres03'))
        self.dres04 = float(element.get('dres04'))
        self.dres05 = float(element.get('dres05'))
        self.dres06 = float(element.get('dres06'))
        self.dres07 = float(element.get('dres07'))
        self.dres08 = float(element.get('dres08'))
        self.dres09 = float(element.get('dres09'))

        self.lead_lines = []
        leadline = element.get('./sx_inf_geom_draft_leadline')
        if leadline is not None:
            self.lead_lines = [ LeadLine(i) for i in leadline ]
        
        self.attribute = None
        sx_draft_atr_text = element.get('./sx_draft_atr_text')
        if sx_draft_atr_text is not None:
            self.attribute = TextAttribute(sx_draft_atr_text[0])


class Balloon(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin            = self._origin(element)
        self.matrix            = self._matrix(element)
        self.scale             = float(element.get('scale'))
        self.text_count        = int(element.get('tbl'))
        self.lead_line_count   = int(element.get('lead_line_num'))
        self.diam              = float(element.get('diam'))
        self.text1             = element.get('txt1')
        self.text2             = element.get('txt2')
        self.point             = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.auto_size         = element.get('auto_size') != '0'
        self.line_color        = int(element.get('lres03'))
        self.line_width        = CadTypes.Line.Width.get_value( int(element.get('lres04')) )
        self.use_count         = int(element.get('lres05'))
        self.add_balloon_count = int(element.get('lres06'))
        self.lres07            = int(element.get('lres07'))
        self.lres08            = int(element.get('lres08'))
        self.lres09            = int(element.get('lres09'))

        self.dres02            = float(element.get('dres02'))
        self.dres03            = float(element.get('dres03'))
        self.dres04            = float(element.get('dres04'))
        self.dres05            = float(element.get('dres05'))
        self.dres06            = float(element.get('dres06'))
        self.dres07            = float(element.get('dres07'))
        self.dres08            = float(element.get('dres08'))
        self.dres09            = float(element.get('dres09'))

        self.lres07            = int(element.get('lres07'))
        self.lres08            = int(element.get('lres08'))
        self.lres09            = int(element.get('lres09'))

        self.cres02            = element.get('cres02')
        self.cres03            = element.get('cres03')
        self.cres04            = element.get('cres04')
        self.cres05            = element.get('cres05')
        self.cres06            = element.get('cres06')
        self.cres07            = element.get('cres07')
        self.cres08            = element.get('cres08')
        self.cres09            = element.get('cres09')

        leadline = element.get('./sx_inf_geom_draft_leadline')
        if leadline is not None:
            self.lead_lines = [ LeadLine(leadline) for leadline in element.get('./sx_inf_geom_draft_leadline') ]


class SMark(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin            = self._origin(element)
        self.matrix            = self._matrix(element)
        self.remove_type       = CadTypes.Entity.SMark.RemoveType.get_value( int(element.get('removtyp')) )
        self.streak_dir        = CadTypes.Entity.SMark.LaySymbol.get_value( int(element.get('streakdir')) )
        self.arrow_type        = CadTypes.Geometry.DimensionLine.Arrow.get_value( int(element.get('arrow_type', '0')) )
        self.point             = [ float(element.get('pntx')), float(element.get('pnty')), float(element.get('pntz')) ]
        self.val1              = element.get('val1')
        self.val2              = element.get('val2')
        self.val3              = element.get('val3')
        self.val4              = element.get('val4')
        self.proway            = element.get('proway')
        self.lead_line_count   = int(element.get('lead_line_num'))
        self.circle_mark       = element.get('circle_mark') != '1'
        self.format            = CadTypes.Entity.SMark.Format.get_value( int(element.get('format')) )
        self.cut_word          = element.get('cut_word')
        self.parm1             = element.get('parm1')
        self.parm2             = element.get('parm2')
        self.parm3             = element.get('parm3')

        self.lres06            = int(element.get('lres06'))
        self.lres07            = int(element.get('lres07'))
        self.lres08            = int(element.get('lres08'))
        self.lres09            = int(element.get('lres09'))
        
        self.dres00            = float(element.get('dres00'))
        self.dres01            = float(element.get('dres01'))
        self.dres02            = float(element.get('dres02'))
        self.dres03            = float(element.get('dres03'))
        self.dres04            = float(element.get('dres04'))
        self.dres05            = float(element.get('dres05'))
        self.dres06            = float(element.get('dres06'))
        self.dres07            = float(element.get('dres07'))
        self.dres08            = float(element.get('dres08'))
        self.dres09            = float(element.get('dres09'))
        
        self.cres09            = element.get('cres09')

        leadline = element.get('./sx_inf_geom_draft_leadline')
        if leadline is not None:
            self.lead_lines = [ LeadLine(leadline) for leadline in element.get('./sx_inf_geom_draft_leadline') ]


class Delta(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin            = self._origin(element)
        self.matrix            = self._matrix(element)
        self.sidelen           = float(element.get('sidelen'))
        self.text              = element.get('txt')
        self.point             = [ float(element.get('pntx')), float(element.get('pnty')), float(element.get('pntz')) ]

        self.lres00            = int(element.get('lres00'))
        self.lres01            = int(element.get('lres01'))
        self.lres02            = int(element.get('lres02'))
        self.lres03            = int(element.get('lres03'))
        self.lres05            = int(element.get('lres04'))
        self.lres05            = int(element.get('lres05'))
        self.lres06            = int(element.get('lres06'))
        self.lres07            = int(element.get('lres07'))
        self.lres08            = int(element.get('lres08'))
        self.lres09            = int(element.get('lres09'))
        
        self.dres01            = float(element.get('dres01'))
        self.dres02            = float(element.get('dres02'))
        self.dres03            = float(element.get('dres03'))
        self.dres04            = float(element.get('dres04'))
        self.dres05            = float(element.get('dres05'))
        self.dres06            = float(element.get('dres06'))
        self.dres07            = float(element.get('dres07'))
        self.dres08            = float(element.get('dres08'))
        self.dres09            = float(element.get('dres09'))
        
        self.cres09            = element.get('cres09')


class Welding(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin                    = self._origin(element)
        self.matrix                    = self._matrix(element)
        self.weld_place                = int(element.get('weld_place'))
        self.upper_mark_type           = int(element.get('upper_mark_type'))
        self.lower_mark_type           = int(element.get('lower_mark_type'))
        self.circum_mark               = int(element.get('circum_mark'))
        self.upper_face_form           = int(element.get('upper_face_form'))
        self.lower_face_form           = int(element.get('lower_face_form'))
        self.back_side                 = int(element.get('back_side'))
        self.is_panel_fit              = element.get('is_panel_fit') == '2'
        self.upper_groove_depth1       = element.get('str01')
        self.lower_groove_depth1       = element.get('str02')
        self.weld_note                 = [ element.get('str05'), element.get('str06'), element.get('str07'), element.get('str08') ]
        self.upper_length_width_pitch1 = element.get('str09')
        self.lower_length_width_pitch1 = element.get('str10')
        self.upper_roude_space         = element.get('str11')
        self.lower_roude_space         = element.get('str12')
        self.upper_groove_angle        = element.get('str13')
        self.lower_groove_angle        = element.get('str14')
        self.upper_finish_way          = element.get('str15')
        self.lower_finish_way          = element.get('str16')
        self.upper_groove_depth2       = element.get('str17')
        self.lower_groove_depth2       = element.get('str18')
        self.upper_length_width_pitch2 = element.get('str19')
        self.lower_length_width_pitch2 = element.get('str20')
        self.lead_line_count             = int(element.get('lead_line_num'))
        self.lres11                    = int(element.get('lres11'))
        self.lres12                    = int(element.get('lres12'))
        self.lres13                    = int(element.get('lres13'))
        self.lres14                    = int(element.get('lres14'))
        self.lres15                    = int(element.get('lres15'))
        self.lres16                    = int(element.get('lres16'))
        self.lres17                    = int(element.get('lres17'))
        self.lres18                    = int(element.get('lres18'))
        self.lres19                    = int(element.get('lres19'))
        self.dres07                    = float(element.get('dres07'))
        self.dres08                    = float(element.get('dres08'))
        self.dres09                    = float(element.get('dres09'))
        
        if (self.weld_place == 1):
            self.weld_points = int(element.get('upper_weld_points'))
            self.upper_weld_points = 0
            self.lower_weld_points = 0
        elif (self.weld_place == 2):
            self.weld_points = int(element.get('lower_weld_points'))
            self.upper_weld_points = 0
            self.lower_weld_points = 0
        else:
            self.weld_points = 0
            self.upper_weld_points = int(element.get('upper_weld_points'))
            self.lower_weld_points = int(element.get('lower_weld_points'))
        
        leadline = element.get('./sx_inf_geom_draft_leadline')
        if leadline is not None:
            self.lead_lines = [ LeadLine(leadline) for leadline in element.get('./sx_inf_geom_draft_leadline') ]


class SimpleWelding(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin    = self._origin(element)
        self.matrix    = self._matrix(element)
        self.color     = int(element.get('color'))
        self.width     = CadTypes.Line.Width.get_value( int(element.get('width')) )
        self.tilte     = int(element.get('tilt'))
        self.mark_type = int(element.get('mark_type'))
        self.pnt_num   = int(element.get('pnt_num'))
        self.height    = float(element.get('height'))
        self.point     = [ float(element.get('pntx')), float(element.get('pnty')), float(element.get('pntz')) ]
        self.point1    = [ float(element.get('pnt1x')), float(element.get('pnt1y')), float(element.get('pnt1z')) ]


class GeometricTolerance(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin        = self._origin(element)
        self.matrix        = self._matrix(element)
        self.frame_num     = int(element.get('frame_num'))
        self.lead_line_count = int(element.get('lead_line_num'))
        self.refline1_type = int(element.get('refline1_type'))
        self.refline2_type = int(element.get('refline2_type'))
        self.refline3_type = int(element.get('refline3_type'))
        self.refline4_type = int(element.get('refline4_type'))
        self.refline5_type = int(element.get('refline5_type'))
        self.refline6_type = int(element.get('refline6_type'))
        self.point         = [ float(element.get('pntx')),   float(element.get('pnty')),   float(element.get('pntz')) ]
        self.point1        = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point2        = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point3        = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]
        self.point4        = [ float(element.get('pnt4x')),  float(element.get('pnt4y')),  float(element.get('pnt4z')) ]
        self.point5        = [ float(element.get('pnt5x')),  float(element.get('pnt5y')),  float(element.get('pnt5z')) ]
        self.point6        = [ float(element.get('pnt6x')),  float(element.get('pnt6y')),  float(element.get('pnt6z')) ]
        self.point7        = [ float(element.get('pnt7x')),  float(element.get('pnt7y')),  float(element.get('pnt7z')) ]
        self.point8        = [ float(element.get('pnt8x')),  float(element.get('pnt8y')),  float(element.get('pnt8z')) ]
        self.point9        = [ float(element.get('pnt9x')),  float(element.get('pnt9y')),  float(element.get('pnt9z')) ]
        self.point10       = [ float(element.get('pnt10x')), float(element.get('pnt10y')), float(element.get('pnt10z')) ]
        self.point11       = [ float(element.get('pnt11x')), float(element.get('pnt11y')), float(element.get('pnt11z')) ]
        self.point12       = [ float(element.get('pnt12x')), float(element.get('pnt12y')), float(element.get('pnt12z')) ]
        self.point13       = [ float(element.get('pnt13x')), float(element.get('pnt13y')), float(element.get('pnt13z')) ]
        self.point14       = [ float(element.get('pnt14x')), float(element.get('pnt14y')), float(element.get('pnt14z')) ]
        self.point15       = [ float(element.get('pnt15x')), float(element.get('pnt15y')), float(element.get('pnt15z')) ]
        self.point16       = [ float(element.get('pnt16x')), float(element.get('pnt16y')), float(element.get('pnt16z')) ]
        self.point17       = [ float(element.get('pnt17x')), float(element.get('pnt17y')), float(element.get('pnt17z')) ]
        self.point18       = [ float(element.get('pnt18x')), float(element.get('pnt18y')), float(element.get('pnt18z')) ]
        self.frame         = [ ToleranceFrame(e) for e in element.xpath('./sx_inf_geom_draft_tolframe') ]
        leadline = element.get('./sx_inf_geom_draft_leadline')
        if leadline is not None:
            self.lead_lines = [ LeadLine(leadline) for leadline in element.get('./sx_inf_geom_draft_leadline') ]


class ToleranceFrame:
    def __init__(self, element: _Element):
        self.no              = int(element.get('frameno'))
        self.is_one_step     = element.get('is_one_step') != '3'
        self.tol_mark        = int(element.get('tol_mark'))
        self.tol_area_mark   = int(element.get('tol_area_mark'))
        self.datum1_mark     = int(element.get('datum1_mark'))
        self.datum2_mark     = int(element.get('datum2_mark'))
        self.datum3_mark     = int(element.get('datum3_mark'))
        self.tol_value_mark1 = int(element.get('tol_value_mark1'))
        self.tol_value_mark2 = int(element.get('tol_value_mark2'))
        self.tol_value_mark3 = int(element.get('tol_value_mark3'))
        self.tol_value_mark4 = int(element.get('tol_value_mark4'))
        self.str_tolvalue    = element.get('str_tolvalue')
        self.str_range       = element.get('str_range')
        self.str_part_tol    = element.get('str_part_tol')
        self.str_datum1      = element.get('str_datum1')
        self.str_datum2      = element.get('str_datum2')
        self.str_datum3      = element.get('str_datum3')
        self.str_tol_note    = element.get('str_tol_note')
        self.str_tol_utext   = element.get('str_tol_utext')
        self.circle_mark     = element.get('circle_mark') != '0'


class Datum(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin        = self._origin(element)
        self.matrix        = self._matrix(element)
        self.is_datum      = element.get('is_detamu') == '1'
        self.refline_type  = CadTypes.Entity.Datum.ReflineType.get_value( int(element.get('refline_type')) )
        self.point         = [ float(element.get('pntx')),   float(element.get('pnty')),   float(element.get('pntz')) ]
        self.point1        = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point2        = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point3        = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]
        self.text          = element.get('text')
        leadline = element.get('./sx_inf_geom_draft_leadline')
        if leadline is not None:
            self.lead_lines = [ LeadLine(leadline) for leadline in element.get('./sx_inf_geom_draft_leadline') ]


class CutLine(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin = self._origin(element)
        self.matrix = self._matrix(element)
        self.name   = element.get('name')
        self.arrow  = element.get('arrow') == '1'
        self.point1 = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point2 = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.lres01 = int( element.get('lres01') )
        self.lres02 = int( element.get('lres02') )
        self.lres03 = int( element.get('lres03') )
        self.lres04 = int( element.get('lres04') )
        self.dres00 = float( element.get('dres00') )
        self.dres01 = float( element.get('dres01') )
        self.dres02 = float( element.get('dres02') )


class ArrowView(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.place       = element.get('place') == '1'
        self.name        = element.get('name')
        self.point1      = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point2      = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]


class Arrow(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.color       = int(element.get('color'))
        self.width       = int(element.get('width'))
        self.style       = int(element.get('style'))
        self.arrow_type  = CadTypes.Geometry.DimensionLine.Arrow.get_value( int(element.get('arrow_type')) )
        self.pnt_num     = int(element.get('pnt_num'))
        self.arrow_width = float(element.get('arrow_width'))
        self.arrow_angle = float(element.get('arrow_ang'))
        self.dot_diam    = float(element.get('dot_diam'))
        self.points      = [ [ float( sx_pos.get(i) ) for i in ['x', 'y', 'z'] ] for sx_pos in element.xpath('./sx_pos') ]


class Symbol(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.symbol_type = CadTypes.Entity.Symbol.get_value( int(element.get('symbol_type')) )
        self.height      = float(element.get('height'))
        self.width_ratio = float(element.get('width_ratio'))
        self.space_ratio = float(element.get('space_ratio'))
        self.point       = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]


class SymbolMetal(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.symbol_type = 6 if element.get('symbol_type') == '1' else 7
        self.color       = int(element.get('color'))
        self.width       = CadTypes.Line.Width.get_value( int(element.get('width')) )
        self.point1      = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point2      = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point3      = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]


class Indicator(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.arrow_type  = CadTypes.Geometry.DimensionLine.Arrow.get_value( int(element.get('arrow_type')) )
        self.pnt_num     = int(element.get('pnt_num'))
        self.height      = float(element.get('height'))
        self.width_ratio = float(element.get('width_ratio'))
        self.space_ratio = float(element.get('space_ratio'))
        self.arrow_width = float(element.get('arrow_width'))
        self.arrow_angle = float(element.get('arrow_ang'))
        self.dot_diam    = float(element.get('dot_diam'))
        self.point1      = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point2      = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point3      = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]
        self.point4      = [ float(element.get('pnt4x')),  float(element.get('pnt4y')),  float(element.get('pnt4z')) ]
        self.points      = [ [ float( sx_pos.get(i) ) for i in ['x', 'y', 'z'] ] for sx_pos in element.xpath('./sx_pos') ]


class FinishMark(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.origin      = self._origin(element)
        self.matrix      = self._matrix(element)
        self.mark_type   = CadTypes.Entity.FinishMark.get_value( int(element.get('mark_type')) )
        self.color       = int(element.get('color'))
        self.width       = CadTypes.Line.Width.get_value( int(element.get('width')) )
        self.side_leng   = float(element.get('side_leng'))
        self.point       = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]


class Other(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)


class Hatch(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.pattern  = CadTypes.Entity.Hatch.get_value( int(element.get('pattern')) )
        self.angle    = float(element.get('ang')) / math.pi * 180.0
        self.dist     = float(element.get('dist'))
        self.pitch    = float(element.get('pitch'))
        self.ex_scale = float(element.get('ex_scale'))
        self.ex_name  = element.get('ex_name')


class Mark(BaseGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.name     = element.get('name')
        self.angle    = float(element.get('ang_deg'))
        self.height   = float(element.get('height'))
        self.point    = [ float(element.get('x')),  float(element.get('y')),  float(element.get('z')) ]


class DimensionLength(BaseDimensionGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.dvec        = [ float(element.get('dvecx')), float(element.get('dvecy')), float(element.get('dvecz')) ]
        self.point_place = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point_start = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point_end   = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]
        self.point4      = [ float(element.get('pnt4x')),  float(element.get('pnt4y')),  float(element.get('pnt4z')) ]
        self.point5      = [ float(element.get('pnt5x')),  float(element.get('pnt5y')),  float(element.get('pnt5z')) ]
        self.point6      = [ float(element.get('pnt6x')),  float(element.get('pnt6y')),  float(element.get('pnt6z')) ]
        self.point7      = [ float(element.get('pnt7x')),  float(element.get('pnt7y')),  float(element.get('pnt7z')) ]
        self.point8      = [ float(element.get('pnt8x')),  float(element.get('pnt8y')),  float(element.get('pnt8z')) ]
        self.point9      = [ float(element.get('pnt9x')),  float(element.get('pnt9y')),  float(element.get('pnt9z')) ]
        self.point10     = [ float(element.get('pnt10x')), float(element.get('pnt10y')), float(element.get('pnt10z')) ]


class DimensionAngle(BaseDimensionGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.point_place       = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point_start       = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point_end         = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]
        self.point_center      = [ float(element.get('pnt4x')),  float(element.get('pnt4y')),  float(element.get('pnt4z')) ]
        self.point_arc_start   = [ float(element.get('pnt5x')),  float(element.get('pnt5y')),  float(element.get('pnt5z')) ]
        self.point_arc_end     = [ float(element.get('pnt6x')),  float(element.get('pnt6y')),  float(element.get('pnt6z')) ]
        self.point7            = [ float(element.get('pnt7x')),  float(element.get('pnt7y')),  float(element.get('pnt7z')) ]
        self.point8            = [ float(element.get('pnt8x')),  float(element.get('pnt8y')),  float(element.get('pnt8z')) ]
        self.point9            = [ float(element.get('pnt9x')),  float(element.get('pnt9y')),  float(element.get('pnt9z')) ]
        self.point10           = [ float(element.get('pnt10x')), float(element.get('pnt10y')), float(element.get('pnt10z')) ]


class DimensionDiameter(BaseDimensionGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.point_place       = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point_start       = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point_end         = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]
        self.point_center      = [ float(element.get('pnt4x')),  float(element.get('pnt4y')),  float(element.get('pnt4z')) ]
        self.point5            = [ float(element.get('pnt5x')),  float(element.get('pnt5y')),  float(element.get('pnt5z')) ]
        self.point6            = [ float(element.get('pnt6x')),  float(element.get('pnt6y')),  float(element.get('pnt6z')) ]
        self.point7            = [ float(element.get('pnt7x')),  float(element.get('pnt7y')),  float(element.get('pnt7z')) ]
        self.point8            = [ float(element.get('pnt8x')),  float(element.get('pnt8y')),  float(element.get('pnt8z')) ]
        self.point9            = [ float(element.get('pnt9x')),  float(element.get('pnt9y')),  float(element.get('pnt9z')) ]
        self.point10           = [ float(element.get('pnt10x')), float(element.get('pnt10y')), float(element.get('pnt10z')) ]


class DimensionCham(BaseDimensionGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.point_place       = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point_start       = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point_end         = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]
        self.point4            = [ float(element.get('pnt4x')),  float(element.get('pnt4y')),  float(element.get('pnt4z')) ]
        self.point5            = [ float(element.get('pnt5x')),  float(element.get('pnt5y')),  float(element.get('pnt5z')) ]
        self.point6            = [ float(element.get('pnt6x')),  float(element.get('pnt6y')),  float(element.get('pnt6z')) ]
        self.point7            = [ float(element.get('pnt7x')),  float(element.get('pnt7y')),  float(element.get('pnt7z')) ]
        self.point8            = [ float(element.get('pnt8x')),  float(element.get('pnt8y')),  float(element.get('pnt8z')) ]
        self.point9            = [ float(element.get('pnt9x')),  float(element.get('pnt9y')),  float(element.get('pnt9z')) ]
        self.point10           = [ float(element.get('pnt10x')), float(element.get('pnt10y')), float(element.get('pnt10z')) ]


class DimensionArcLength(BaseDimensionGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.point             = [ float(element.get(f'pnt1{i}')) for i in ['x', 'y', 'z'] ]
        self.point_pull1       = [ float(element.get(f'pnt2{i}')) for i in ['x', 'y', 'z'] ]
        self.point_pull2       = [ float(element.get(f'pnt3{i}')) for i in ['x', 'y', 'z'] ]
        self.point_center      = [ float(element.get(f'pnt4{i}')) for i in ['x', 'y', 'z'] ]
        self.point_start       = [ float(element.get(f'pnt5{i}')) for i in ['x', 'y', 'z'] ]
        self.point_end         = [ float(element.get(f'pnt6{i}')) for i in ['x', 'y', 'z'] ]
        self.point7            = [ float(element.get(f'pnt7{i}')) for i in ['x', 'y', 'z'] ]
        self.point8            = [ float(element.get(f'pnt8{i}')) for i in ['x', 'y', 'z'] ]
        self.point9            = [ float(element.get(f'pnt9{i}')) for i in ['x', 'y', 'z'] ]
        self.point10           = [ float(element.get(f'pnt10{i}')) for i in ['x', 'y', 'z'] ]


class DimensionApl(BaseDimensionGeometry):
    def __init__(self, element: _Element):
        super().__init__(element)
        self.vector       = [ float(element.get(i)) for i in ['dvecx', 'dvecy', 'dvecz'] ]
        self.point        = [ float(element.get('pnt1x')),  float(element.get('pnt1y')),  float(element.get('pnt1z')) ]
        self.point1_start = [ float(element.get('pnt2x')),  float(element.get('pnt2y')),  float(element.get('pnt2z')) ]
        self.point1_end   = [ float(element.get('pnt3x')),  float(element.get('pnt3y')),  float(element.get('pnt3z')) ]
        self.point2_start = [ float(element.get('pnt4x')),  float(element.get('pnt4y')),  float(element.get('pnt4z')) ]
        self.point2_end   = [ float(element.get('pnt5x')),  float(element.get('pnt5y')),  float(element.get('pnt5z')) ]
        self.point6       = [ float(element.get('pnt6x')),  float(element.get('pnt6y')),  float(element.get('pnt6z')) ]
        self.point7       = [ float(element.get('pnt7x')),  float(element.get('pnt7y')),  float(element.get('pnt7z')) ]
        self.point8       = [ float(element.get('pnt8x')),  float(element.get('pnt8y')),  float(element.get('pnt8z')) ]
        self.point9       = [ float(element.get('pnt9x')),  float(element.get('pnt9y')),  float(element.get('pnt9z')) ]
        self.point10      = [ float(element.get('pnt10x')), float(element.get('pnt10y')), float(element.get('pnt10z')) ]


class DimensionLine:
    def __init__(self, element: _Element):
        self.line_color         = CadTypes.Color.get_value( int(element.get('line_color')) )
        self.line_width         = CadTypes.Line.Width.get_value( int(element.get('line_width')) )
        self.text_color         = CadTypes.Color.get_value( int(element.get('text_color')) )
        self.text_width         = CadTypes.Line.Width.get_value( int(element.get('text_width')) )
        self.rouway             = CadTypes.Geometry.DimensionLine.ROUND.get_value( int(element.get('rouway')) )
        self.round              = int(element.get('round'))
        self.suppress           = element.get('suppress') != '0'
        self.multiple_mode      = int(element.get('multiple_mode'))
        self.multiple           = float(element.get('multiple'))
        self.angle_type         = CadTypes.Geometry.DimensionLine.AngleType.get_value( int(element.get('angtype')) )
        self.display_angle      = CadTypes.Geometry.DimensionLine.DisplayAngle.get_value( int(element.get('dispang')) )
        self.tilt_angle         = int(element.get('tiltang'))
        self.arrow1_type        = CadTypes.Geometry.DimensionLine.Arrow.get_value( int(element.get('arrow1_type')) )
        self.arrow2_type        = CadTypes.Geometry.DimensionLine.Arrow.get_value( int(element.get('arrow2_type')) )
        self.aidline1           = CadTypes.Geometry.DimensionLine.AidLine.get_value( int(element.get('aidline1')) )
        self.aidline2           = CadTypes.Geometry.DimensionLine.AidLine.get_value( int(element.get('aidline2')) )
        self.term1_mark         = CadTypes.Geometry.DimensionLine.TermMark.get_value( int(element.get('term1_mark')) )
        self.term2_mark         = CadTypes.Geometry.DimensionLine.TermMark.get_value( int(element.get('term2_mark')) )
        self.dot                = element.get('dot') != '0'
        self.dimval_height      = float(element.get('dimval_height'))
        self.dimval_width_ratio = float(element.get('dimval_width_ratio'))
        self.space_ratio        = float(element.get('space_ratio'))
        self.dimtol_ratio       = float(element.get('dimtol_ratio'))
        self.aidline_tilt       = float(element.get('aidline_tilt'))
        self.arrow_width        = float(element.get('arrow_width'))
        self.arrow_ang          = float(element.get('arrow_ang'))
        self.dot_diam           = float(element.get('dot_diam'))
        self.dimval_scale       = float(element.get('dimval_scale'))
        self.dimval_space       = float(element.get('dimval_space'))
        self.underline1_len     = float(element.get('underline1_len'))
        self.underline2_len     = float(element.get('underline2_len'))
        self.multiple           = float(element.get('multiple'))
        self.dres13             = float(element.get('dres13'))
        self.dres14             = float(element.get('dres14'))
        self.dres15             = float(element.get('dres15'))
        self.dres16             = float(element.get('dres16'))
        self.dres17             = float(element.get('dres17'))
        self.dres18             = float(element.get('dres18'))
        self.dres19             = float(element.get('dres19'))


class DimensionValue:
    def __init__(self, element: _Element):
        self.disp: bool         = element.get('disp') != '0'
        self.mark1: bool        = element.get('mark1') != '0'
        self.mark2              = CadTypes.Geometry.DimensionValue.Mark2.get_value( int(element.get('mark2')) )
        self.mark3              = CadTypes.Geometry.DimensionValue.Mark3.get_value( int(element.get('mark3')) )
        self.fwordexist: bool   = element.get('fwordexist') != '0'
        self.bwordexist: bool   = element.get('bwordexist') != '0'
        self.dwordexist: bool   = element.get('dwordexist') != '0'
        self.tolexist           = CadTypes.Geometry.DimensionValue.Tolerance.get_value( int(element.get('tolexist')) )
        self.frame: bool        = element.get('frame') != '0'
        self.underline: bool    = element.get('underline') != '0'
        self.correctline: bool  = element.get('correctline') != '0'
        self.val_refer: bool    = element.get('val_refer') != '0'
        self.tol_refer: bool    = element.get('tol_refer') != '0'
        self.dimval_type: bool  = element.get('dimval_type') != '0'
        self.dist1              = float(element.get('dist1'))
        self.dist2              = float(element.get('dist2'))
        self.frontword: str     = element.get('frontword')
        self.backword: str      = element.get('backword')
        self.downword: str      = element.get('downword')
        self.upper_tolword: str = element.get('upper_tolword')
        self.down_tolword: str  = element.get('down_tolword')
        self.valword: str       = element.get('valword')
        self.hmword: str        = element.get('hmword')
        self.opt_word: str      = element.get('opt_word')
        self.str_num: str       = element.get('str_num')
        self.cres09             = element.get('cres09')


class TextAttribute:
    def __init__(self, element: _Element):
        self.font: bool     = element.get('font') != '0'
        self.font_name: str = element.get('font_name')
        self.height         = float(element.get('height'))
        self.width_ratio    = float(element.get('width_ratio'))
        self.tilt           = int(element.get('tilt'))
        self.space_ratio    = float(element.get('space_ratio'))
        self.row_space      = float(element.get('row_space'))
        self.color          = int(element.get('color'))
        self.width          = int(element.get('width'))


class LineAttribute:
    def __init__(self, element: _Element):
        splitted = element.text.split()
        self.width = CadTypes.Line.Width.get_value( int(splitted[0]) )
        self.style = CadTypes.Line.Style.get_value( int(splitted[1]) )
        self.color = CadTypes.Color.get_value( int(splitted[2]) )


class GeometryFactory:

    class_ = {
        'sx_inf_geom_line3d'                : Line3D,
        'sx_inf_geom_line2d'                : Line2D,
        'sx_inf_geom_pnt3d'                 : Point3D,
        'sx_inf_geom_pnt2d'                 : Point2D,
        'sx_inf_geom_arc3d'                 : Arc3D,
        'sx_inf_geom_arc2d'                 : Arc2D,
        'sx_inf_geom_circle3d'              : Circle3D,
        'sx_inf_geom_circle2d'              : Circle2D,
        'sx_inf_geom_ellipse2d'             : Ellipse2D,
        'sx_inf_geom_elparc2d'              : EllipseArc2D,
        'sx_inf_geom_spline2d'              : Spline2D,
        'sx_inf_geom_other_curve'           : OtherCurve,
        'sx_inf_geom_cap'                   : Cap,
        'sx_inf_geom_plane'                 : Plane,
        'sx_inf_geom_cone'                  : Cone,
        'sx_inf_geom_cylinder'              : Cylinder,
        'sx_inf_geom_sphere'                : Sphere,
        'sx_inf_geom_torus'                 : Torus,
        'sx_inf_geom_other_surf'            : OtherSurf,
        'sx_inf_geom_draft_text'            : Text,
        'sx_inf_geom_draft_leadline'        : LeadLine,
        'sx_inf_geom_draft_note'            : Note,
        'sx_inf_geom_draft_balloon'         : Balloon,
        'sx_inf_geom_draft_smark'           : SMark,
        'sx_inf_geom_draft_delta'           : Delta,
        'sx_inf_geom_draft_weld'            : Welding,
        'sx_inf_geom_draft_simweld'         : SimpleWelding,
        'sx_inf_geom_draft_tolframe'        : ToleranceFrame,
        'sx_inf_geom_draft_geotol'          : GeometricTolerance,
        'sx_inf_geom_draft_detamu'          : Datum,
        'sx_inf_geom_draft_cutline'         : CutLine,
        'sx_inf_geom_draft_arrowview'       : ArrowView,
        'sx_inf_geom_draft_arrow'           : Arrow,
        'sx_inf_geom_draft_symbol'          : Symbol,
        'sx_inf_geom_draft_symbolmetal'     : SymbolMetal,
        'sx_inf_geom_draft_indicator'       : Indicator,
        'sx_inf_geom_draft_finishmark'      : FinishMark,
        'sx_inf_geom_draft_other'           : Other,
        'sx_inf_geom_draft_hatch'           : Hatch,
        'sx_inf_geom_draft_mark'            : Mark,
        'sx_inf_geom_draft_lgtdim'          : DimensionLength,
        'sx_inf_geom_draft_angdim'          : DimensionAngle,
        'sx_inf_geom_draft_diadim'          : DimensionDiameter,
        'sx_inf_geom_draft_chamdim'         : DimensionCham,
        'sx_inf_geom_draft_arcleng'         : DimensionArcLength,
        'sx_inf_geom_draft_apldim'          : DimensionApl,
        'sxml_inf_geom_draft_dimvalue_attr' : DimensionValue,
        'sxml_inf_geom_draft_dimline_attr'  : DimensionLine
    }

    @classmethod
    def create(cls, sx_inf_geom: _Element):
        geometry_class = cls.class_.get(sx_inf_geom.tag)
        if geometry_class is None:
            return None
        element: BaseGeometry = geometry_class(sx_inf_geom)
        return element
