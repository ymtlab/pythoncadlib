from pathlib import Path
from pycadsx.cadtypes import CadTypes
import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client
from pycadsx.vs import VS
from pycadsx.wf import WF
from pycadsx.part import Part
from pycadsx.entity import Entity
from pycadsx.print_info import PrintInfo
from pycadsx.material import Material
from pycadsx.plotter import Plotter
from pycadsx.options import SurfaceMarkOption
from pycadsx.window import Window
from pycadsx.options import Project3d2dOption


class Model:
    def __init__(self, client: 'Client', model_id: int) -> None:
        self.top_part                = None
        self.vs_list: list[VS]       = []
        self.wf_list: list[WF]       = []
        self.vs_global: VS           = None
        self.wf_global: WF           = None
        self.parts: dict[int, Part]  = {}
        self.active_part: Part       = None
        self.client                  = client
        self.id                      = model_id
        self.draft_attribute         = None
        self.window: Window          = None
        self.path: str               = ''
        self.name: str               = ''
        self.comment: str            = ''
        self.passwd: str             = ''
        self.is_read_only: bool      = False
        self.is_modify: bool         = False
        self.access                  = None
        self.nvs                     = None
        self.nwf                     = None
        self.modified_ids: list[int] = []

        self.default_papers = [
            [ 'A4',  297, 210, 1.0],
            [ 'A3',  420, 297, 1.0],
            [ 'A4',  297, 210, 0.5],
            [ 'A3',  420, 297, 0.5],
            [ 'A2',  594, 420, 1.0],
            [ 'A2',  594, 420, 0.5],
            [ 'A1',  841, 594, 1.0],
            [ 'A1',  841, 594, 0.5],
            [ 'A0', 1189, 841, 1.0],
            [ 'A0', 1189, 841, 0.5],
            [ 'A1',  841, 594, 0.2],
            [ 'A0', 1189, 841, 0.2],
            [ 'A1',  841, 594, 0.1],
            [ 'A0', 1189, 841, 0.1],
            [ 'A1',  841, 594, 0.05],
            [ 'A0', 1189, 841, 0.05],
            [ 'A1',  841, 594, 0.01],
            [ 'A0', 1189, 841, 0.01],
            [ 'A0', 1189, 841, 0.005],
            [ 'A0', 1189, 841, 0.001],
            [ 'A0', 1189, 841, 0.0005],
            [ 'A0', 1189, 841, 0.0001]
        ]

        self.get_inf(self)
        self.get_wf_list()
        self.get_vs_list()
        self.get_top_part()
        self.get_window()

    def create(self):
        self.client.model.create()

    def create_asm_plane(self, vs: VS):
        self.client.model.create_asm_plane(vs)
        
    def delete_entities(self, entities: list[Entity]):
        self.client.model.delete_entities(entities)

    def delete_print_infos(self, print_infos: list[PrintInfo]):
        self.client.model.delete_print_infos(print_infos)

    def delete_vs(self, vs: VS):
        if vs in self.vs_list:
            del self.vs_list[self.vs_list.index(vs)]
        self.client.model.delete_vs( vs, self.get_window() )
        
    def delete_all_vs(self, is_delete_global_entities=False):
        self.get_window().set_dimension(False)
        front_view = None
        for vs in self.vs_list[::-1]:
            if vs != self.vs_global:
                if vs.view_type == CadTypes.VS.View.FRONT:
                    front_view = vs
                else:
                    self.delete_vs(vs)
        self.delete_vs(front_view)
        if is_delete_global_entities:
            self.vs_global.set_active()
            entities = list( self.vs_global.get_entities(0, 0, True, True, True, True).values() )
            self.delete_entities(entities)

    def find_parts(self, partname: str):
        parts = [ part for part in self.parts.values() if part.name == partname ]
        return parts

    def get_global_vs(self):
        return self.client.model.get_global_vs(self)
    
    def get_inf(self, model: 'Model'):
        return self.client.model.get_inf(model)
    
    def get_vs_list(self):
        self.vs_list, self.vs_global = self.client.model.get_vs_list(self)

    def get_wf_list(self):
        self.wf_list, self.wf_global = self.client.model.get_wf_list(self)
        
    def get_active_part(self):
        if self.active_part is not None:
            self.active_part.is_active = False
        system_info = self.client.system.get_inf_sys()
        if system_info.active_part is None:
            self.active_part = self.top_part
        else:
            if system_info.active_part.id in self.parts:
                self.active_part = self.parts[system_info.active_part.id]
            else:
                self.active_part = system_info.active_part
        return self.active_part

    def get_tree(self, wf: WF = None):
        if wf is None:
            wf = self.wf_global
        self.parts = {}
        self.get_top_part()
        self.get_modified_parts_list()
        self.client.model.get_tree(self, wf)

    def get_children(self, parent: 'Part'):
        parts = parent.get_children()
        self.parts = self.parts | parts
        return parts.values()

    def get_top_part(self, wf: WF = None):
        if wf is None:
            wf = self.wf_global
        self.top_part = Part(self.client, self.id, wf.wfno)
        self.set_top_part_info(wf)
        return self.top_part
    
    def set_top_part_info(self, wf: WF = None):
        if wf is None:
            wf = self.wf_global
        #self.top_part.from_inf_part(PartCommand.Info({
        self.top_part.from_inf_part(self.client.part.Info({
            'name' : wf.top_name, 'comment' : wf.top_comment,
            'orgx'  : '0.0', 'orgy'  : '0.0', 'orgz'  : '0.0',
            'zvecx' : '0.0', 'zvecy' : '0.0', 'zvecz' : '1.0',
            'xvecx' : '1.0', 'xvecy' : '0.0', 'xvecz' : '0.0',
            'is_mirror' : '0', 'is_external' : '1', 'is_read_only' : '1' if self.is_read_only else '0', 'is_dummy' : '0', 'edit' : '0',
            'ref_model_name' : self.name, 'path' : self.path, 'date' : '0', 'time' : '0', 'is_active' : '0', 'has_grp' : '0', 'id' : '0'
        }))
        self.top_part.get_extra_info()
        self.parts[self.top_part.id] = self.top_part
    
    def get_extra_info(self):
        return self.top_part.get_extra_info()

    def get_extra_infos(self, parts: list['Part']):
        self.client.model.get_extra_infos(parts)
    
    def set_extra_infos(self, parts: list['Part'], extra_infos: list[dict[str, str]]):
        self.client.model.set_extra_infos(parts, extra_infos)
    
    def get_modified_parts_list(self):
        return self.client.model.get_modified_parts_list(self)

    def get_external_parts(self, wf: WF = None):
        self.get_tree(wf)

        parts: dict[str, list[Part]] = {}
        for part in self.parts.values():
            if part.is_external:
                if part.name in parts:
                    parts[part.name].append(part)
                else:
                    parts[part.name] = [part]
                    
        external_parts = dict( sorted( parts.items() ) )

        return external_parts

    def set_entities_visible(self, entities: list['Entity'], visible: bool):
        if len(entities) > 0:
            self.client.model.set_entities_visible(entities, visible)

    def show_only_parts(self, parts: list['Part']):
        self.client.model.show_only_parts(parts)

    def show_only_entities(self, entities: list['Entity']):
        all_entities = self.get_entities(0, 0, True, True, True, True)
        self.set_entities_visible( list(all_entities.values()), False ) # 全要素非表示
        self.set_entities_visible( entities, True ) # 指定したパーツを表示

    def get_window(self):
        self.window = self.client.model.get_window(self)
        return self.window

    def zoom_full(self):
        self.client.model.zoom_full()

    def get_entities(self, offset: int, num: int, visible: bool, part: bool, layer: bool, _type: bool, wf: WF = None) -> dict[int, 'Entity']:
        if wf is None:
            wf = self.wf_global
        return self.client.model.get_entities(self, wf, offset, num, visible, part, layer, _type)
    
    def get_top_entities(self, offset: int, num: int, visible: bool, layer: bool, _type: bool, wf: WF = None) -> dict[int, 'Entity']:
        if wf is None:
            wf = self.wf_global
        return self.client.model.get_top_entities(self, wf, offset, num, visible, layer, _type)
    
    def get_all_entities(self):
        entities: dict[int, Entity] = {}
        for i in range(100):
            _entities = self.get_entities(i*100000, 100000, True, True, True, True)
            if not _entities:
                break
            entities |= _entities

        entity_types = CadTypes.Entity().entity_types()
        for entity in entities.values():
            if entity.type in entity_types:
                if entity.part_id in self.parts:
                    part = self.parts[entity.part_id]
                    part.entities[entity.id] = entity
        
        return entities

    def get_entities_2d(self, offset: int, num: int, visible: bool, part: bool, layer: bool, _type: bool, vs: VS = None) -> dict[int, 'Entity']:
        if vs is None:
            vs = self.vs_global
        return self.client.model.get_entities_2d(self, offset, num, visible, part, layer, _type, vs)

    def close(self):
        self.get_window().close()

    def get_materials(self, entities: list['Entity']):
        return self.client.model.get_materials(entities)
    
    def set_inf_material(self, material: Material, entities: list[Entity]):
        self.client.model.set_inf_material(material, entities)

    def get_model_info(self):
        return self.client.model.get_model_info(self)
    
    def set_model_info(self, titles: list[str], infos: list[str]):
        self.client.model.set_model_info(titles, infos)

    def get_asmplane(self, wfno: int, plane_no: int):
        self.client.model.get_asmplane(self, wfno, plane_no)

    def get_parts(self, wfno: int = None):
        if wfno is None:
            wfno = self.wf_global.wfno
        all_parts, top_children = self.client.model.get_parts_by_name(self, wfno, None)
        top_part = self.get_top_part(self.wf_global)
        top_part.children = list( top_children.values() )
        return all_parts

    def get_parts_by_name(self, partname: str, wfno: int = None):
        if wfno is None:
            wfno = self.wf_global.wfno
        all_parts, top_children = self.client.model.get_parts_by_name(self, wfno, partname)
        return all_parts

    def set_search_layer(self, layers: list[int], mode: bool):
        self.client.model.set_search_layer(layers, mode)

    def set_display_layer(self, layers: list[int], mode: bool):
        self.client.model.set_display_layer(layers, mode)

    def get_extent(self, wf: WF = None):
        if wf is None:
            wf = self.wf_global
        return self.client.model.get_extent(self, wf)

    def set_layer(self, entities: list['Entity'], layer: int):
        self.client.model.set_layer(entities, layer)

    def set_layer_name(self, layer: int, name: str):
        self.client.model.set_layer_name(layer, name)

    def get_draft_attribute(self):
        return self.client.model.get_draft_attribute()
    
    def create_surface_mark(self, target_object, lead_point: list[float], place_point: list[float], surface_mark_option: SurfaceMarkOption):
        self.client.model.create_surface_mark(self, target_object, lead_point, place_point, surface_mark_option)

    def create_text(self, point: list[float], text: list[str], angle=0.0, direction=True, bold=False, italic=False, font_name='ストローク', ttype=4, position=CadTypes.Entity.Text.Base.LeftBottom):
        return self.client.model.create_text(point, text, angle, direction, bold, italic, font_name, ttype, position)
    
    def create_line_2d(self, p0: list[float], p1: list[float]):
        self.client.model.create_line_2d(p0, p1)

    def get_local_font(self, font_name: str):
        return self.client.model.get_local_font(font_name)

    def get_geometries(self, entities: list['Entity']):
        return self.client.model.get_geometries(entities)

    def set_entities_color(self, entities: list[Entity], color: CadTypes.Color):
        self.client.model.set_entities_color(entities, color)

    def update_2d_drawing(self):
        self.client.model.update_2d_drawing(self)

    def get_print_infos(self):
        return self.client.model.get_print_infos(self)
    
    def get_layer_names(self):
        return self.client.model.get_layer_names()

    def set_active(self):
        self.get_window().set_active()

    def copy_entities(self, entities: list['Entity'], p0: list[float], p1: list[float], angle_x: float, angle_y: float, angle_z: float, attribute: bool, layer: bool, group: bool, part: bool):
        return self.client.model.copy_entities(self, entities, p0, p1, angle_x, angle_y, angle_z, attribute, layer, group, part)
        
    def copy_entities_to_other_wf(self, entities: list['Entity'], model: 'Model', p0: list[float], p1: list[float], angle_x: float, angle_y: float, angle_z: float, attribute: bool, layer: bool, group: bool):
        self.client.model.copy_entities_to_other_wf(entities, self, model, p0, p1, angle_x, angle_y, angle_z, attribute, layer, group)

    def get_search_layer(self) -> list[bool]:
        return self.client.model.get_search_layer()

    def get_display_layer(self) -> list[bool]:
        return self.client.model.get_display_layer()
    
    def get_mass(self, entities: list['Entity'], density=1.0, unit_type=CadTypes.Mass.Unit.MM_KG, is_si=True, mode_accuracy=CadTypes.Mass.Accuracy.Low, is_create_point=False, vector=[0.0, 0.0, 1.0]):
        return self.client.model.get_mass(entities, density, unit_type, is_si, mode_accuracy, is_create_point, vector)

    def print_drawing(self, print_info: PrintInfo, plotter: Plotter):
        self.client.model.print_drawing(print_info, plotter)

    def print_drawing_all_area(self, print_info: PrintInfo, plotter: Plotter):
        self.client.model.print_drawing_all_area(print_info, plotter)

    def save(self):
        self.client.model.save()

    def save_as(self, path: Path, comment: str, version: int=None, level: int=None):
        self.client.model.save_as(path, comment, version, level)

    def save_part(self, parts: list[Part], is_modified: bool, is_child: bool):
        self.client.model.save_part(self, parts, is_modified, is_child)

    def change_view_expression(self, vs_list: list[VS], layers: list[int], hidden_line: bool, sin: bool, high_accuracy: bool, pipe_center_line: bool, hole_center_line: float):
        self.client.model.change_view_expression(vs_list, layers, hidden_line, sin, high_accuracy, pipe_center_line, hole_center_line)

    def select(self, mode: CadTypes.Select.Mode, text: str, select_go: bool, select_entity: bool, select_edge: bool, select_face: bool, select_point: bool):
        return self.client.model.select(self, mode, text, select_go, select_entity, select_edge, select_face, select_point)

    def select_entities(self, mode: CadTypes.Select.Mode, multi_init: CadTypes.Select.MultiInit):
        return self.client.model.select_entities(self, mode, multi_init)

    def select2(self, mode: CadTypes.Select.Mode, text: str, select_edge: bool, select_entity: bool, select_face: bool, select_point: bool, select_go: bool):
        self.client.model.select2(mode, text, select_edge, select_entity, select_face, select_point, select_go)

    def export(self, filepath: Path):
        self.client.model.export(filepath)

    def free_parts(self, parts: list['Part']):
        self.free_parts(self, parts)

    def copy_mirror(self, entities: list[Entity | Part], p0: list[float], p1: list[float], p2: list[float], attribute: bool, layer: bool, group: bool, part: bool):
        return self.client.model.copy_mirror(self, entities, p0, p1, p2, attribute, layer, group, part)

    def copy_mirror2(self, entities: list[Entity | Part], p0: list[float], v0: list[float], attribute: bool, layer: bool, group: bool, part: bool):
        return self.client.model.copy_mirror2(self, entities, p0, v0, attribute, layer, group, part)
    
    def parasolid_import(self, path: Path, name: str, comment: str):
        self.client.model.parasolid_import(path, name, comment)

    def move_entities(self, entities: list[Entity], vector: list[float]):
        self.client.model.move_entities(entities, vector)

    def move_entities_2d(self, entities: list[Entity], vector: list[float]):
        self.client.model.move_entities_2d(entities, vector)

    def set_parts_names(self, parts: list[Part], names: list[str], comments: list[str], filenames: list[str], change_all: bool = False):
        self.client.model.set_parts_names(parts, names, comments, filenames, change_all)
        
    def reload_parts(self, parts: list[Part]):
        self.client.model.reload_parts(parts)

    def set_scale(self, scale: float):
        self.client.model.set_scale(scale)
        
    def set_print_area(self, margin=20.0):
        return self.client.model.set_print_area(self, margin)

    def set_print_area_all(self):
        return self.client.model.set_print_area_all(self)

    def project_3d2d_isome(self, point3d: list[float], point2d: list[float], option: Project3d2dOption):
        self.client.model.project_3d2d_isome2(self, point3d, point2d, option)

    def project_drawing(self, point: list[float]):
        self.client.model.project_drawing(self, point)

    def project_drawing_isometric(self, point: list[float]):
        self.client.model.project_drawing_isometric(self, point)

    def set_drawing_frame(self, frame_file_path: Path):
        self.client.model.set_drawing_frame(self, frame_file_path)

    def dimension_tree_entities(self):
        dimansions_tree_entities: list[Entity] = []
        for child in self.top_part.children:
            if child.name == '[寸法]' and not child.is_external:
                stack = [child]
                while stack:
                    current_child = stack.pop()
                    dimansions_tree_entities.extend( list(current_child.get_entities().values()) )
                    stack.extend(current_child.children)
                return dimansions_tree_entities
        return dimansions_tree_entities

    def get_line_attributes(self, entities: list[Entity]):
        return self.client.model.get_line_attributes(entities)

    def set_coordinate(self, origin: list[float], x_vector: list[float], z_vector: list[float]):
        self.client.model.set_coordinate(self, origin, x_vector, z_vector)

    def get_extent_list(self, entities: list[Entity]):
        return self.client.model.get_extent_list(entities)

    def set_entities_to_global_vs(self, entities: list[Entity]):
        self.client.model.set_entities_to_global_vs(self, entities)

    def set_entities_to_vs(self, vs: VS, entities: list[Entity]):
        self.client.model.set_entities_to_vs(self, vs, entities)

    def copy_entities_2d(self, entities: list[Entity], p0: list[float], p1: list[float], attribute: bool, layer: bool, group: bool):
        return self.client.model.copy_entities_2d(self, entities, p0, p1, attribute, layer, group)

    def set_inf_print_size(self, point: list[float], drawing_size: str, paper_size: str, vertical: bool, scale: float, size_x: float = 0, size_y: float = 0):
        self.client.model.set_inf_print_size(point, drawing_size, paper_size, vertical, scale, size_x, size_y)
        return self.get_print_infos()[-1]
    
    def create_vs_local(self, name: str, point: list[float], angle: float, scale: float):
        self.client.model.create_vs_local(name, point, angle, scale)
        self.get_vs_list()
        for vs in self.vs_list:
            if vs.name == name:
                return vs

    def take_in_parts(self, parts: list[Part], all_level: bool):
        self.client.model.take_in_parts(parts, all_level)

    def echo(self, entities_or_parts: list[Entity]):
        self.client.model.echo(entities_or_parts)

    def create_drawing(self, scale: float, views: list[CadTypes.VS.View], template_path: Path=None, margin: int=20.0):
        self.get_window()   
        self.window.set_dimension(True)
        self.set_scale(scale)
        
        box = self.get_extent()

        self.delete_all_vs(True)
        self.delete_print_infos( self.get_print_infos() )
        
        if template_path is not None:
            self.set_drawing_frame(template_path)
        
        w, h, d = box[1][0] - box[0][0], box[1][1] - box[0][1], box[1][2] - box[0][2]

        right_x  =   w/2 + margin * 3 + d/2
        back_x   =   w/2 + margin * 3 + d   + margin + w/2
        left_x   = - w/2 - margin * 3 - d/2
        top_y    =   h/2 + margin * 3 + d/2
        bottom_y = - h/2 - margin * 3 - d/2
        
        origins = {
            CadTypes.VS.View.FRONT  : [    0.0,      0.0],
            CadTypes.VS.View.RIGHT  : [right_x,      0.0],
            CadTypes.VS.View.BACK   : [ back_x,      0.0],
            CadTypes.VS.View.LEFT   : [ left_x,      0.0],
            CadTypes.VS.View.TOP    : [    0.0,    top_y],
            CadTypes.VS.View.BOTTOM : [    0.0, bottom_y],
            CadTypes.VS.View.ISOME  : [right_x,    top_y]
        }

        for view_type, origin in origins.items():
            if view_type in views:
                if view_type == CadTypes.VS.View.ISOME:
                    self.project_drawing_isometric(origin)
                else:
                    self.project_drawing(origin)

        self.vs_global.set_active()
        self.set_scale(scale)
        self.fit_views(margin)
        
    def fit_views(self, margin: int = 20.0):
        self.get_vs_list()
        vs_list = { vs.view_type : vs for vs in self.vs_list if vs.type == CadTypes.VS.Type.VIEW }
        front = vs_list[CadTypes.VS.View.FRONT]
        if front is None:
            return
        
        front_extent = front.map_to_global( front.get_extent() )

        if CadTypes.VS.View.TOP in vs_list:
            vs = vs_list[CadTypes.VS.View.TOP]
            extent = vs.map_to_global( vs.get_extent() )
            d = extent[0][1] - front_extent[1][1] - margin
            if d > 0.0001:
                vs.move([ vs.origin[0], vs.origin[1] - d ])
                vs.get_inf()
        
        if CadTypes.VS.View.BOTTOM in vs_list:
            vs = vs_list[CadTypes.VS.View.BOTTOM]
            extent = vs.map_to_global( vs.get_extent() )
            d = front_extent[0][1] - extent[1][1] - margin
            if d > 0.0001:
                vs.move([ vs.origin[0], vs.origin[1] + d ])
                vs.get_inf()
        
        if CadTypes.VS.View.LEFT in vs_list:
            vs = vs_list[CadTypes.VS.View.LEFT]
            extent = vs.map_to_global( vs.get_extent() )
            d = front_extent[0][0] - extent[1][0] - margin
            if d > 0.0001:
                vs.move([ vs.origin[0] + d, vs.origin[1] ])
                vs.get_inf()
        
        right_extent = None
        if CadTypes.VS.View.RIGHT in vs_list:
            vs = vs_list[CadTypes.VS.View.RIGHT]
            right_extent = vs.map_to_global( vs.get_extent() )
            d = right_extent[0][0] - front_extent[1][0] - margin
            if d > 0.0001:
                vs.move([ vs.origin[0] - d, vs.origin[1] ])
                vs.get_inf()
                right_extent = vs.map_to_global( vs.get_extent() )
        
        if CadTypes.VS.View.BACK in vs_list:
            vs = vs_list[CadTypes.VS.View.BACK]
            extent = vs.map_to_global( vs.get_extent() )
            extent0 = right_extent if right_extent is not None else front_extent
            d = extent[0][0] - extent0[1][0] - margin
            if d > 0.0001:
                vs.move([ vs.origin[0] - d, vs.origin[1] ])
                vs.get_inf()

        print_infos = self.get_print_infos()

        drawing_extent = self.get_drawing_extent( list( vs_list.values() ) )

        if len(print_infos) > 0:
            print_center = [
                (print_infos[0].right_top[0] + print_infos[0].left_bottom[0]) / 2,
                (print_infos[0].right_top[1] + print_infos[0].left_bottom[1]) / 2
            ]

            drawing_center = [
                    ( drawing_extent[1][0] + drawing_extent[0][0] ) / 2,
                    ( drawing_extent[1][1] + drawing_extent[0][1] ) / 2
                ]
            
            diff = [ print_center[0] - drawing_center[0], print_center[1] - drawing_center[1] ]
        else:
            diff = [ 0 - drawing_extent[0][0] + margin, 0 - drawing_extent[0][1] + margin ]

        for vs in vs_list.values():
            if (-0.0001 < diff[0] < 0.0001) and (-0.0001 < diff[1] < 0.0001):
                continue
            vs.move([ vs.origin[0] + diff[0], vs.origin[1] + diff[1] ])
            vs.get_inf()
        
        isome = [ vs for vs in self.vs_list if vs.view_type == CadTypes.VS.View.LOCAL ]
        isome = isome[0] if len(isome) > 0 else None
        if isome is not None:
            front.get_inf()
            isome.get_inf()
            front_extent = front.map_to_global( front.get_extent() )
            isome_extent = isome.map_to_global( isome.get_extent() )
            diff = [ front_extent[1][0] - isome_extent[0][0] + margin, front_extent[1][1] - isome_extent[0][1] + margin ]
            if not( (-0.0001 < diff[0] < 0.0001) and (-0.0001 < diff[1] < 0.0001) ):
                isome.move([ isome.origin[0] + diff[0], isome.origin[1] + diff[1] ])

    def get_drawing_extent(self, vs_list: list[VS]):
        x0, y0, x1, y1 = 999999999999999, 999999999999999, -999999999999999, -999999999999999
        for vs in vs_list:
            if vs.type == CadTypes.VS.Type.LOCAL_VIEW:
                continue
            e = vs.map_to_global( vs.get_extent() )
            if e[0][0] < x0: x0 = e[0][0]
            if e[1][0] < x0: x0 = e[1][0]
            if e[0][0] > x1: x1 = e[0][0]
            if e[1][0] > x1: x1 = e[1][0]
            if e[0][1] < y0: y0 = e[0][1]
            if e[1][1] < y0: y0 = e[1][1]
            if e[0][1] > y1: y1 = e[0][1]
            if e[1][1] > y1: y1 = e[1][1]
        return [ [x0, y0], [x1, y1] ]

    def get_entities_in_box(self,  box: list[list[float]], part: bool, org: list[float] = [0, 0, 0], zvec: list[float] = [0, 0, 1], xvec: list[float] = [1, 0, 0]):
        return self.client.model.get_entities_in_box(self, box, part, org, zvec, xvec)
