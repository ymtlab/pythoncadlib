from lxml import etree
import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client, RPartCommand
from pycadsx.entity import Entity, EntityFactory
from pycadsx.cadtypes import CadTypes


class RPart:
    def __init__(self, client: 'Client', model_id: int = 0, wfno: int = 0, vsno: int = 0):
        self.client         = client
        self.model_id       = model_id
        self.wfno           = wfno
        self.vsno           = vsno
        self.type           = CadTypes.Entity.Type.NONE
        self.id             = 0
        self.prmno          = 0
        self.kind           = CadTypes.Entity.Kind.Invalid
        self.part_id        = 0
        self.is3d           = False
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
        self.ref_model_name = ''
        self.part3d_name    = None
        self.has_pos        = False
        self.is_mirror      = False
        self.ref_vs_name    = ''
        self.angle          = 0.0
        self.origin         = [ 0.0, 0.0, 0.0 ]

    def from_ent(self, data: 'RPartCommand.Data'):
        self.type       = data.type
        self.id         = data.id
        self.prmno      = data.prmno
        self.kind       = data.kind
        self.part_id    = data.part_id
        self.is3d: bool = data.is3d

    def from_inf_r_part(self, info: 'RPartCommand.Info'):
        self.name: str           = info.name
        self.comment: str        = info.comment
        self.origin              = info.origin
        self.angle               = info.angle
        self.ref_model_name: str = info.ref_model_name
        self.ref_vs_name: str    = info.ref_vs_name
        self.is_mirror: bool     = info.is_mirror
        self.has_pos: bool       = info.has_pos
        self.part3d_name         = info.part3d_name

    def get_entities(self):
        return self.client.r_part.get_entities(self)
