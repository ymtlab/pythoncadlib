import os
from pathlib import Path
import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client, PartCommand
from pycadsx.edge import Edge
from pycadsx.material import Material
from pycadsx.cadtypes import CadTypes
from pycadsx.entity import Entity


class Part:
    def __init__(self, client: 'Client', model_id: int = 0, wfno: int = 1):
        self.client                              = client
        self.parent: Part                        = None
        self.children: list[Part]                = []
        self.entities: dict[int, Entity]         = {}
        self.geometries                          = []
        self.extra_info                          = {}
        self.model_id                            = model_id
        self.wfno                                = wfno
        self.name: str                           = ''
        self.comment: str                        = ''
        self.is_mirror: bool                     = False
        self.is_external: bool                   = False
        self.is_read_only: bool                  = False
        self.is_unloaded: bool                   = False
        self.is_modified: bool                   = False
        self.ref_model_name: str                 = ''
        self.path: str                           = ''
        self.date                                = 0
        self.time                                = 0
        self.is_active: bool                     = False
        self.has_grp: bool                       = False
        self.id                                  = 0
        self.origin: list[float]                 = []
        self.matrix: list[list[float]]           = []
        self.material: list[Material]    = []

    def __repr__(self):
        return f"{self.name} {super().__repr__()}"
    
    def from_ent(self, data: 'PartCommand.Data'):
        self.type       = data.type
        self.id         = data.id
        self.prmno      = data.prmno
        self.kind       = data.kind
        self.part_id    = data.part_id
        self.is3d: bool = data.is3d

    def from_inf_part(self, data: 'PartCommand.Info'):
        self.name: str           = data.name
        self.comment: str        = data.comment
        self.is_mirror: bool     = data.is_mirror
        self.is_external: bool   = data.is_external
        self.is_read_only: bool  = data.is_read_only
        self.is_unloaded: bool   = data.is_unloaded
        self.is_modified: bool   = data.is_modified
        self.ref_model_name: str = data.ref_model_name
        self.path: str           = data.path
        self.date                = data.date
        self.time                = data.time
        self.is_active: bool     = data.is_active
        self.has_grp: bool       = data.has_grp
        self.id                  = data.id
        self.origin              = data.origin
        self.matrix              = data.matrix

    def value(self, key: str):
        if key == 'Sys_Parts_Name':
            return self.name
        if key == 'Sys_Parts_Comment':
            return self.comment
        if key == 'Sys_Parts_Filename':
            return self.ref_model_name if self.is_external else ''
        if key == 'Sys_Parts_Lowest':
            return len(self.children) == 0
        if key == 'Sys_Parts_IsExternal':
            return self.is_external
        if key == 'Sys_Parts_IsReadOnly':
            return self.is_read_only
        if key == 'Sys_Parts_IsMirror':
            return self.is_mirror
        if key == 'Sys_Parts_IsModified':
            return self.is_modified
        if key == 'Sys_Parts_MaterialNo':
            return ','.join(self.material)
        if key == '__is_read_only__':
            if self.is_external:
                file_path = Path(self.path) / f'{self.ref_model_name}.icd'
                return file_path.is_file() and not os.access(file_path, os.W_OK)
        if key in self.extra_info:
            return self.extra_info.get(key, '')
        return ''

    def append_entities(self, entities: list['Part']):
        self.client.part.append_entities(self, entities)
    
    def append_parts(self, parts: list['Part']):
        self.client.part.append_parts(self, parts)
        
    def create_child(self, name: str, comment: str):
        return self.client.part.create_child(self, name, comment)

    def create_children(self, name: str, comment: str, quantity: int):
        return self.client.part.create_children(self, name, comment, quantity)

    def delete(self):
        self.client.part.delete(self)

    def find_parts(self, partname: str, is_recursion=False):
        def recursion(parent: Part):
            for child in parent.children:
                if child.name == partname:
                    parts.append(child)
                if is_recursion:
                    recursion(child)
        parts: list[Part] = []
        recursion(self)
        return parts
    
    def free(self):
        self.client.part.free(self)

    def get_inf(self):
        self.client.part.get_inf(self)

    def get_extra_info(self):
        return self.client.part.get_extra_info(self)

    def get_entities(self):
        return self.client.part.get_entities(self)

    def get_edges(self, entities: list[Entity]):
        return self.client.part.get_edges(entities)
    
    def get_edges_geometries(self, edges: list[Edge]):
        return self.client.part.get_edges_geometries(edges)

    def get_geometries(self, entities: list[Entity]):
        return self.client.part.get_geometries(entities)

    def get_model_info(self):
        self.client.part.get_model_info(self)

    def get_children(self):
        return self.client.part.get_children(self)
    
    def get_parent(self):
        return self.client.part.get_parent(self)

    def get_tree(self):
        return self.client.part.get_tree(self)

    def set_name(self, partname: str, comment: str, filename: str, change_all: bool = False):
        self.client.part.set_name(self, partname, comment, filename, change_all)

    def set_access(self, is_read_only: bool):
        self.client.part.set_access(self, is_read_only)

    def set_active(self):
        self.client.part.set_active(self)

    def set_extra_info(self, extra_info: dict[str, str]):
        self.client.part.set_extra_info(self, extra_info)

    def set_model_info(self, titles: list[str], infos: list[str]):
        self.client.part.set_model_info(self, titles, infos)

    def get_mass(self, density=1.0, unit_type=CadTypes.Mass.Unit.MM_KG, is_si=True, mode_accuracy=CadTypes.Mass.Accuracy.Low, is_create_point=False):
        return self.client.part.get_mass(self, density, unit_type, is_si, mode_accuracy, is_create_point)

    def get_entities_mass(self, entities: list[Entity], density=1.0, unit_type=CadTypes.Mass.Unit.MM_KG, is_si=True, mode_accuracy=CadTypes.Mass.Accuracy.Low, is_create_point=False):
        return self.client.part.get_entities_mass(entities, density, unit_type, is_si, mode_accuracy, is_create_point)
        
    def put(self, filepath: Path, point: list[float], matrix: list[list[float]], is_external: bool = True, is_all_level: bool = False, is_read_only: bool = True, password: str = ''):
        return self.client.part.put(self, filepath, point, matrix, is_external, is_all_level, is_read_only, password)

    def get_materials(self):
        return self.client.part.get_materials(self)

    def set_material(self, material: Material):
        self.client.part.set_material(self, material)

    def get_hole_infos(self, entities: list[Entity]):
        return self.client.part.get_hole_infos(entities)

    def take_in(self, all_level: bool, same_name: bool=False):
        self.client.part.take_in(self, all_level, same_name)

    def take_out(self, is_all: bool, path: Path):
        self.client.part.take_out(self, is_all, path)

    def create_3d_point(self, point: list[float]):
        self.client.part.create_3d_point(self, point)

    def get_extent(self):
        return self.client.part.get_extent(self)

    def get_tree_element(self):
        return self.client.part.get_tree_element(self)

    def echo(self):
        return self.client.part.echo(self)
