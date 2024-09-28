
import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import HoleCommand


class Hole:
    def __init__(self) -> None:
        self.name = ''
        self.detail_name = ''
        self.pattern_name = ''
        self.hole_yobi = ''
        self.hole_type = ''
        self.modeltype = 0
        self.origin = []
        self.matrix = []
        self.id = 0
        self.hole_number = 0
        self.tap_type = 0
        self.num_th = 0
        self.dir_th = 0
        self.d_type = ''
        self.penetrate = False
        self.u_name = ''
        self.faces = []
        self.parameters = []

    def from_inf(self, hole_data: 'HoleCommand.Data'):
        self.name                      = hole_data.name
        self.detail_name               = hole_data.detail_name
        self.pattern_name              = hole_data.pattern_name
        self.hole_type                 = hole_data.hole_type
        self.modeltype                 = hole_data.modeltype
        self.id                        = hole_data.id
        self.hole_number               = hole_data.hole_number
        self.tap_type                  = hole_data.tap_type
        self.num_th                    = hole_data.num_th
        self.dir_th                    = hole_data.dir_th
        self.d_type                    = hole_data.d_type
        self.penetrate                 = hole_data.penetrate
        self.u_name                    = hole_data.u_name
        self.origin: list[float]       = hole_data.origin
        self.matrix: list[list[float]] = hole_data.matrix
