from lxml import etree
import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client
from pycadsx.entity import Entity, EntityFactory
from pycadsx.face import Face
from pycadsx.edge import Edge
from pycadsx.cadtypes import CadTypes
from pycadsx.part import Part


class Selection:
    def __init__(self, client: 'Client', element: etree._Element, model_id: int, wfno: int) -> None:
        points = element.xpath('./sx_pos')

        self.status = CadTypes.Select.Status( int( element.get('status') ) )
        self.point_status = CadTypes.Select.PointStatus( int( element.get('pos_status') ) )

        self.entities: list[Entity] = []
        for sx_ent in element.xpath('./sx_ent'):
            if int(sx_ent.get('type', 0)) == CadTypes.Entity.Type.PART:
                entity = client.create_part(sx_ent, model_id, wfno)
            else:
                entity = EntityFactory.create(client, client.entity.entity_data(sx_ent))
            self.entities.append(entity)

        self.edges: list[Edge] = []
        for sx_edge in element.xpath('./sx_edge'):
            edge =  Edge(client)
            edge.from_edge(client.edge.edge_info(sx_edge))
            self.edges.append(edge)
        
        self.faces: list[Face] = []
        for sx_face in element.xpath('./sx_face'):
            face = Face(client)
            face.from_face(client.face.face_data(sx_face))
            self.faces.append(face)

        self.points: list[list[float]] = [ [float(p.get('x')), float(p.get('y')), float(p.get('z'))] for p in element.xpath('./sx_pos') ]
        
        for sx_inf_select_hitinf in element.xpath('./sx_inf_select_hitinf'):
            points = sx_inf_select_hitinf.xpath('./sx_pos')
            self.hit_points: list[float] = [ float(points[0].get('x')), float(points[0].get('y')), float(points[0].get('z')) ] if len(points) > 0 else []

            self.hit_entities: list[Entity] = []
            for sx_ent in sx_inf_select_hitinf.xpath('./sx_ent'):
                if int(sx_ent.get('type', 0)) == CadTypes.Entity.Type.PART:
                    entity = Part(client)
                    entity.from_ent(client.entity.entity_data(sx_ent))
                    entity.get_inf()
                    entity.get_parent()
                else:
                    entity = EntityFactory.create(client, sx_ent)
                self.hit_entities.append(entity)

            self.hit_edges: list[Edge] = []
            for sx_edge in sx_inf_select_hitinf.xpath('./sx_edge'):
                edge =  Edge(client)
                edge.from_edge(client.edge.edge_info(sx_edge))
                self.hit_edges.append(edge)
            
            self.hit_faces: list[Face] = []
            for sx_face in sx_inf_select_hitinf.xpath('./sx_face'):
                face = Face(client)
                face.from_face(client.face.face_data(sx_face))
                self.faces.append(face)
