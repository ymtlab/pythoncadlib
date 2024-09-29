from enum import IntEnum
import typing
if typing.TYPE_CHECKING:
    from pycadsx.client import Client, WfCommand


class WfType(IntEnum):
	WORK_WF: int = 0
	GLOBAL_WF: int = 1


class WF:
    def __init__(self, client: 'Client') -> None:
        self.client = client
        self.Type = WfType
        self.model_id: int = 0
        self.wfno: int = 0
        self.type: int = 0
        self.name = ''
        self.top_name = ''
        self.top_comment = ''

    def from_data(self, data: 'WfCommand.Data'):
        self.model_id = data.model_id
        self.wfno     = data.wfno
        self.type     = data.type

    def from_inf(self, info: 'WfCommand.Info'):
        self.name        = info.name
        self.type        = info.type
        self.top_name    = info.top_name
        self.top_comment = info.top_comment
