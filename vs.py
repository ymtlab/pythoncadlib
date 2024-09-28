import math
from pycadsx.cadtypes import CadTypes
import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client, VsCommand
from pycadsx.r_part import RPart


class VS:
    def __init__(self, client: 'Client') -> None:
        self.client = client
        self.model_id = 0
        self.vsno = 0
        self.type = CadTypes.VS.Type(0)
        self.refid = 0

    def from_data(self, data: 'VsCommand.Data'):
        self.model_id = data.model_id
        self.vsno     = data.vsno
        self.type     = data.type
        self.refid    = data.refid

    def get_inf(self):
        info = self.client.vs.get_inf(self)
        self.name         = info.name
        self.origin       = info.origin
        self.angle        = info.angle
        self.scale        = info.scale
        self.has_local    = info.has_local
        self.comment      = info.comment
        self.type         = info.type
        self.view_type    = info.view_type
        self.local_origin = info.local_origin
        self.local_matrix = info.local_matrix

    def get_r_parts(self, partname: str=None) -> dict[int, RPart]:
        return self.client.vs.get_r_parts(self, partname)

    def get_window(self):
        return self.client.vs.get_window(self)

    def set_active(self):
        return self.client.vs.set_active(self)

    def get_entities(self, offset: int, num: int, visible: bool, part: bool, layer: bool, _type: bool):
        return self.client.vs.get_entities(self, offset, num, visible, part, layer, _type)
    
    def get_entities_in_rect(self, p0: list[float], p1: list[float], part: bool, cross: bool):
        return self.client.vs.get_entities_in_rect(self, p0, p1, part, cross)
    
    def get_extent(self):
        return self.client.vs.get_extent(self)

    def map_to_global(self, points1: list[ list[float] ]):
        
        if self.type not in [CadTypes.VS.Type.VIEW, CadTypes.VS.Type.LOCAL_VIEW]:
            return [points1[0][:], points1[1][:]]
        
        points2 = [[0.0, 0.0], [0.0, 0.0]]

        if self.angle == 0.0:
            points2[0][0] = points1[0][0] * self.scale + self.origin[0]
            points2[0][1] = points1[0][1] * self.scale + self.origin[1]
            points2[1][0] = points1[1][0] * self.scale + self.origin[0]
            points2[1][1] = points1[1][1] * self.scale + self.origin[1]
        else:
            rad = math.radians(self.angle)
            cos = math.cos(rad)
            sin = math.sin(rad)

            points = [
                [points1[0][0], points1[0][1]],
                [points1[1][0], points1[0][1]],
                [points1[0][0], points1[1][1]],
                [points1[1][0], points1[1][1]]
            ]

            transformed_points = [
                [
                    (p[0] * cos - p[1] * sin) * self.scale + self.origin[0],
                    (p[0] * sin + p[1] * cos) * self.scale + self.origin[1]
                ] for p in points
            ]

            points2[0][0] = min(p[0] for p in transformed_points)
            points2[0][1] = min(p[1] for p in transformed_points)
            points2[1][0] = max(p[0] for p in transformed_points)
            points2[1][1] = max(p[1] for p in transformed_points)

        return points2

    def convert_point(self, point: list[float], to_global: bool=True):
        if not self.type in [CadTypes.VS.Type.VIEW, CadTypes.VS.Type.LOCAL_VIEW]:
            return point
        
        self.get_inf()
        angle = self.angle / 180.0 * math.pi

        if to_global:
            if math.isclose(angle, 0.0, abs_tol=0.001):
                point[0] = point[0] * self.scale + self.origin[0]
                point[1] = point[1] * self.scale + self.origin[1]
                return point
            cos, sin = math.cos(angle), math.sin(angle)
            point[0] = (point[0] * cos - point[1] * sin) * self.scale + self.origin[0]
            point[1] = (point[0] * sin + point[1] * cos) * self.scale + self.origin[1]
            return point
        
        if math.isclose(angle, 0.0, abs_tol=0.001):
            point[0] = (point[0] - self.origin[0]) * self.scale
            point[1] = (point[1] - self.origin[1]) * self.scale
            return point
            
        cos, sin = math.cos(angle), math.sin(angle)
        point[0] = ((point[0] - self.origin[0]) * cos - (point[1] - self.origin[1]) * sin) * self.scale
        point[1] = ((point[0] - self.origin[0]) * sin + (point[1] - self.origin[1]) * cos) * self.scale
        return point

    def move(self, point: list[float]):
        self.client.vs.move(self, point)

    def set_scale(self, scale: float, move: bool = False):
        self.client.vs.set_scale(self, scale, move)