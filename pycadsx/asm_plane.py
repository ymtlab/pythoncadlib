from pycadsx.client import Client, AsmPlaneCommand
from pycadsx.window import Window
from pycadsx.vs import VS


class AsmPlane:
    def __init__(self, client: Client, model_id: int = 0, wfno: int = 1, no: int = 1) -> None:
        self.client = client
        self.model_id = model_id
        self.wfno = wfno
        self.no = no

    def from_inf(self, asm_plane_info: AsmPlaneCommand.Info):
        self.origin  = asm_plane_info.origin
        self.matrix  = asm_plane_info.matrix
        self.vsno    = asm_plane_info.vsno
        self.vs_type = asm_plane_info.vs_type
        self.refid   = asm_plane_info.refid
        self.wfno    = asm_plane_info.wfno
        self.wf_type = asm_plane_info.wf_type

    def get_inf(self):
        self.from_inf( self.client.asm_plane.get_inf(self.model_id, self.wfno, self.no) )

    def set_active(self, window: Window):
        self.client.asm_plane.set_active(window.pdno, self.no)

    def delete(self, window: Window, vs: VS):
        self.client.asm_plane.delete(window.pdno, vs.name)

    def create(self, vs: VS):
        self.client.asm_plane.create(vs.vsno, vs.refid)

    def offset(self, window: Window, point: list[float]):
        self.client.asm_plane.offset(window.pdno, point, self.no)
