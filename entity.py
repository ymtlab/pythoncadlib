from lxml import etree
import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client, EntityCommand
from pycadsx.cadtypes import CadTypes
from pycadsx.geometry import DimensionValue, DimensionLine
#from pycadsx.part import Part
#from pycadsx.r_part import RPart


class Entity:
    def __init__(self, client: 'Client'):
        self.client         = client
        self.geometry       = None
        self.edges          = []
        self.type           = CadTypes.Entity.Type.NONE
        self.id             = 0
        self.prmno          = 0
        self.kind           = CadTypes.Entity.Kind.Invalid
        self.part_id        = 0
        self.is3d           = False
        self.userid         = 0
        self.vswfno         = 0
        self.layer          = 0
        self.visi           = False
        self.is_25d         = False
        self.member_kind    = 0
        self.prim_num       = 0
        self.ent_len        = 0
        self.model_id       = 0
        self.grp_kind       = 0
        self.cg_attr        = 0
        self.profile_attr   = 0
        self.arrow_id       = 0
        self.body_type      = CadTypes.Entity.BodyType.Other
        self.vwtype         = 0
        self.fc_state       = CadTypes.Entity.FcState.NONE
        self.is_transparent = False
        self.is_draft       = False

    def from_ent(self, entity_data: 'EntityCommand.Data'):
        self.type    = entity_data.type
        self.id      = entity_data.id
        self.prmno   = entity_data.prmno
        self.kind    = entity_data.kind
        self.part_id = entity_data.part_id
        self.is3d    = entity_data.is3d
        
    def from_inf(self, entity_info: 'EntityCommand.Info'):
        self.userid         = entity_info.userid
        self.is3d           = entity_info.is3d
        self.vswfno         = entity_info.vswfno
        self.layer          = entity_info.layer
        self.type           = entity_info.type
        self.visi           = entity_info.visi
        self.is_25d         = entity_info.is_25d
        self.member_kind    = entity_info.member_kind
        self.prim_num       = entity_info.prim_num
        self.ent_len        = entity_info.ent_len
        self.model_id       = entity_info.model_id
        self.grp_kind       = entity_info.grp_kind
        self.cg_attr        = entity_info.cg_attr
        self.profile_attr   = entity_info.profile_attr
        self.part_id        = entity_info.part_id
        self.arrow_id       = entity_info.arrow_id
        self.body_type      = entity_info.body_type
        self.id             = entity_info.id
        self.vwtype         = entity_info.vwtype
        self.fc_state       = entity_info.fc_state
        self.is_transparent = entity_info.is_transparent
        self.is_draft       = entity_info.is_draft
        self.kind           = entity_info.kind

    def set_dimension_text_size(self, height: float, width_ratio: float, space_ratio: float, dimtol_ratio1: float, dimtol_ratio2: float, tol_space: float, tilt: int):
        entity_data = self.client.entity.set_dimension_text_size(self.id, height, width_ratio, space_ratio, dimtol_ratio1, dimtol_ratio2, tol_space, tilt)
        self.id    = entity_data.id
        self.prmno = entity_data.prmno
        self.type  = entity_data.type
        return entity_data

    def set_color(self, color: 'CadTypes.Color'):
        self.client.entity.set_color(self.id, color.value)

    def set_layer(self, layer: int):
        self.client.entity.set_layer(self.id, layer)

    def get_geometry(self):
        return self.client.entity.get_geometry(self.id, self.prmno)
        
    def edit_text(self, texts: list[str]):
        entity_data = self.client.entity.edit_text(self.type, self.id, self.prmno, self.visi, texts)
        self.id    = entity_data.id
        self.prmno = entity_data.prmno
        self.type  = entity_data.type

    def set_visible(self, visible: bool):
        self.client.entity.set_visible(self.id, visible)

    def edit_dimension_text(self, dimension_text: DimensionValue, dimension_line: DimensionLine):
        entity_data = self.client.entity.edit_dimension_text(self.id, self.type, self.visi, dimension_text, dimension_line)
        self.id    = entity_data.id
        self.prmno = entity_data.prmno
        self.type  = entity_data.type

    def get_on_point(self, point: list[float], real: bool):
        return self.client.entity.get_on_point(self.id, self.prmno, point, real)


class EntityGroup(Entity):
    def __init__(self, data: etree._Element) -> None:
        super().__init__(data)


class EntityRefer(Entity):
    def __init__(self, data: etree._Element) -> None:
        super().__init__(data)


class EntityFactory:

    class_ = {
        0 : Entity,
        #1 : RPart,
        2 : EntityGroup,
        3 : EntityRefer
        #6 : Part
    }
    
    @classmethod
    def create(cls, client: 'Client', entity_data: 'EntityCommand.Data') -> Entity:
        entity_class: Entity = cls.class_.get(entity_data.kind, Entity)
        entity: Entity = entity_class(client)
        entity.from_ent(entity_data)
        return entity
