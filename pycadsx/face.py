import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client, FaceCommand
from pycadsx.cadtypes import CadTypes


class Face:
    def __init__(self, client: 'Client') -> None:
        self.client = client
        self.id = 0
        self.prmno = 0
        self.faceno = 0
        self.csgsol = 0
        self.type = 0
        self.face_type = 0
    
    def from_face(self, face_data: 'FaceCommand.Data'):
        self.id        = face_data.id
        self.prmno     = face_data.prmno
        self.faceno    = face_data.faceno
        self.csgsol    = face_data.csgsol
        self.type      = face_data.type
        self.face_type = face_data.face_type

    def get_geometry(self):
        return self.client.face.get_geometry(self)
    
    def get_geometries(self, faces: list['Face']):
        return self.client.face.get_geometries(faces)

    def get_edges(self):
        return self.client.face.get_edges(self)

    def get_faces_edges(self, faces: list['Face']):
        return self.client.face.get_faces_edges(self, faces)

    def get_center_point(self):
        return self.client.face.get_center_point(self)

    def get_on_point(self, point: list[float]=None, real: bool=None):
        return self.client.face.get_on_point(self, point, real)

    def get_mass(self):
        return self.client.face.get_mass(self)

    def get_masses(self, faces: list['Face']):
        return self.client.face.get_masses(faces)

    def eval(self, point: list[float]):
        return self.client.face.eval(self, point)

    def get_color(self):
        return self.client.face.get_color(self)

    def get_colors(self, faces: list['Face']):
        return self.client.face.get_colors(faces)

    def set_color(self, color: CadTypes.Color):
        return self.client.face.set_color(self, color)

    def set_colors(self, faces: list['Face'], color: CadTypes.Color):
        return self.client.face.set_colors(faces, color)
