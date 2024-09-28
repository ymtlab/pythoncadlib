import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client, WindowCommand
from pycadsx.cadtypes import CadTypes


class Window:
    def __init__(self, client: 'Client', pdno: int) -> None:
        self.client = client
        self.pdno = pdno
        self.get_inf()

    def from_inf(self, window: 'WindowCommand.Info'):
        self.is_base  = window.is_base
        self.model_id = window.model_id
        self.vsno     = window.vsno
        self.vstype   = window.vstype
        self.wfno     = window.wfno
        self.wftype   = window.wftype
        self.status   = window.status
        self.rect     = window.rect
        self.mdi_rect = window.mdi_rect

    def get_inf(self):
        self.client.window.get_inf(self)

    def zoom_full(self):
        self.client.window.zoom_full()

    def zoom_rasio(self, ratio: float):
        self.client.window.zoom_rasio(ratio)

    def set_dimension(self, is3d: bool):
        self.client.window.set_dimension(self, is3d)

    def close(self):
        self.client.window.close(self)

    def rotate(self, zvec: list, xvec: list):
        self.client.window.rotate(self, zvec, xvec)
    
    def pan(self, center: list):
        self.client.window.pan(self, center)

    def get_mdi_rect(self):
        self.client.window.get_mdi_rect()
    
    def set_active(self):
        self.client.window.set_active(self)
    
    def switch_dimension(self):
        self.client.window.switch_dimension()
    
    def set_vs(self, model_id: int, vsno: int):
        self.client.window.set_vs(self, model_id, vsno)

    def set_wf(self, model_id: int, wfno: int):
        self.client.window.set_wf(self, model_id, wfno)
    
    def set_system_view(self, view: 'CadTypes.Window.View'):
        self.client.window.set_system_view(view)

    def set_status(self, status: 'CadTypes.Window.Status'):
        self.client.window.set_status(self, status)

    def get_virtual_position(self, point: list[float]):
        self.client.window.get_virtual_position(self, point)
