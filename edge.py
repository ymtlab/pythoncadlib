import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client, EdgeCommand


class Edge:
    def __init__(self, client: 'Client'):
        self.client = client
        self.geometry = None

    def from_edge(self, data: 'EdgeCommand.Info'):
        self.type      = data.type
        self.edge_type = data.edge_type
        self.id        = data.id
        self.csgsol    = data.csgsol
        self.prmno     = data.prmno
        self.edgeno    = data.edgeno

    def get_geometry(self):
        self.client.edge.get_geometry(self.id, self.prmno, self.edgeno, self.csgsol)
        
    def get_geometries(self, edges: list['Edge']):
        ids, prmnos, edgenos, csgsols = [], [], [], []
        for edge in edges:
            ids.append(edge.id)
            prmnos.append(edge.prmno)
            edgenos.append(edge.edgeno)
            csgsols.append(edge.csgsol)
        self.client.edge.get_geometries(ids, prmnos, edgenos, csgsols)

    def get_end_points(self):
        return self.client.edge.get_end_points(self.id, self.prmno, self.edgeno, self.csgsol)
    
    def get_middle_point(self):
        return self.client.edge.get_middle_point(self.id, self.prmno, self.edgeno, self.csgsol)

    def get_on_point(self, point: list[float], read: bool):
        return self.client.edge.get_on_point(self.id, self.prmno, self.edgeno, self.csgsol, self, point, read)
        
    def get_mass(self):
        self.client.edge.get_mass(self.id, self.prmno, self.edgeno, self.csgsol)
        
    def get_mass_list(self, edges: list['Edge']):
        ids, prmnos, edgenos, csgsols = [], [], [], []
        for edge in edges:
            ids.append(edge.id)
            prmnos.append(edge.prmno)
            edgenos.append(edge.edgeno)
            csgsols.append(edge.csgsol)
        self.client.edge.get_mass_list(ids, prmnos, edgenos, csgsols)

    def eval(self, point: list[float]):
        self.client.edge.eval(self.id, self.prmno, self.edgeno, self.csgsol, point)

    def get_face_list(self):
        self.client.edge.get_face_list(self.id, self.prmno, self.edgeno, self.csgsol)
        
    def get_face_list_from_edges(self, edges: list['Edge']):
        ids, prmnos, edgenos, csgsols = [], [], [], []
        for edge in edges:
            ids.append(edge.id)
            prmnos.append(edge.prmno)
            edgenos.append(edge.edgeno)
            csgsols.append(edge.csgsol)
        self.client.edge.get_face_list_from_edges(ids, prmnos, edgenos, csgsols)
