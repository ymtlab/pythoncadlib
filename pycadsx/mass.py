from lxml import etree


class Moment:
    def __init__(self, element: etree._Element) -> None:
        self.origin = [ float( element.get(f'org{i}') ) for i in ['x', 'y', 'z'] ]

        self.matrix = [ [ float(element.get(f'{i}vec{j}')) for j in ['x', 'y', 'z'] ] for i in ['x', 'z'] ]
        self.matrix.insert(1, [
            self.matrix[1][1] * self.matrix[0][2] - self.matrix[1][2] * self.matrix[0][1],
            self.matrix[1][2] * self.matrix[0][0] - self.matrix[1][0] * self.matrix[0][2],
            self.matrix[1][0] * self.matrix[0][1] - self.matrix[1][1] * self.matrix[0][0]
        ])
        self.i_xx  = float(element.get('i_xx', 0.0))
        self.i_yy  = float(element.get('i_yy', 0.0))
        self.i_zz  = float(element.get('i_zz', 0.0))
        self.pi_xy = float(element.get('pi_xy', 0.0))
        self.pi_yz = float(element.get('pi_yz', 0.0))
        self.pi_zx = float(element.get('pi_zx', 0.0))
        self.r_gx  = float(element.get('r_gx', 0.0))
        self.r_gy  = float(element.get('r_gy', 0.0))
        self.r_gz  = float(element.get('r_gz)', 0.0))


class Mass:
    def __init__(self, element: etree._Element) -> None:
        self.is_SI              = element.get('is_SI', False)
        self.unit_type          = int( element.get('unit_type', 3) )
        self.volume             = float( element.get('volume', 0.0) )
        self.area               = float( element.get('area', 0.0) )
        self.length             = float( element.get('length', 0.0) )
        self.density            = float( element.get('density', 0.0) )
        self.mass               = float( element.get('mass', 0.0) )
        self.weight             = float( element.get('weight', 0.0) )
        self.center_point       = [ float( element.get(i, 0.0) ) for i in ['cx', 'cy', 'cz'] ]
        self.inf_global_moment  = None #element.get('', None)
        self.inf_gravity_moment = None #element.get('', None)
        self.inf_main_moment    = None #element.get('', None)
        self.specific_pos       = None #element.get('', None)
        self.specific_axis      = None #element.get('', None)
        self.specific_moment    = 0.0 #element.get('', 0.0)
        self.specific_radius    = 0.0 #element.get('', 0.0)
        self.id                 = int( element.get('id', 0) )
        self.csgsol             = int( element.get('csgsol', 0) )
        self.prmno              = int( element.get('prmno', 0) )
        self.faceno             = int( element.get('faceno', 0) )
        self.edgeno             = int( element.get('edgeno', 0) )

        self.moments = []
        for sx_inf_moment in element.xpath('./sx_inf_moment'):
            self.moments.append( Moment(sx_inf_moment) )
