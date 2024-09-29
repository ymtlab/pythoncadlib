import os
import subprocess
from pathlib import Path
from pycadsx.model import Model
from pycadsx.material import Material
from pycadsx.part import Part
from pycadsx.plotter import Plotter


class PyCadSx:
    def __init__(self, is_debug=False) -> None:
        from pycadsx.client import Client
        self._is_debug = is_debug
        self.client = Client(self._is_debug)

        self.active_model: Model = None
        self.version             = -1
        self.level               = -1
        self.path: str           = ''
        self.pen_color           = -1
        self.pen_style           = -1
        self.pen_width           = -1
        self.scale               = -1.0
        self.grid                = -1.0
        self.active_layer        = -1
        self.active_model_id     = -1
        self.pdno                = -1
        self.navi: bool          = False
        self.cross: bool         = False
        self.dim: bool           = False
        self.sys3d: bool         = False
        self.plane_lock: bool    = False
        self.is_viewer: bool     = False
        self.mod_flg             = -1

        self.model: dict[int, Model] = {}
        self.active_part: Part = None
        self.plotters: list[Plotter] = []
        self.default_plotter: Plotter = None

        self.icaddir = Path( os.getenv('ICADDIR') )
        self.ini = IniFileParser(self.icaddir / 'ETC/ICAD.ini')
        self.model_info_titles  = ['設計情報', '加工情報', '組付情報'] + [ self.ini.get('@PARTSINFO').get(f'TAB_NAME{i}') for i in range(1, 5) ]
        self.materials: list[Material] = []
        self.db_lock = DBLock(self.icaddir / 'bin/DBLOCK.exe')

    def model_set_active(self, model: 'Model'):
        self.active_model = model
        self.active_model.set_active()

    def create_model(self):
        self.active_model.create()
        self.get_inf_sys()
        return self.active_model

    def get_inf_sys(self):
        system_data                  = self.client.system.get_inf_sys()
        self.version                 = system_data.version
        self.level                   = system_data.level
        self.path: str               = system_data.path
        self.pen_color               = system_data.pen_color
        self.pen_style               = system_data.pen_style
        self.pen_width               = system_data.pen_width
        self.scale                   = system_data.scale
        self.grid                    = system_data.grid
        self.active_layer            = system_data.active_layer
        self.active_model_id         = system_data.active_model_id
        self.pdno                    = system_data.pdno
        self.navi: bool              = system_data.navi
        self.cross: bool             = system_data.cross
        self.dim: bool               = system_data.dim
        self.sys3d: bool             = system_data.sys3d
        self.plane_lock: bool        = system_data.plane_lock
        self.is_viewer: bool         = system_data.is_viewer
        self.mod_flg                 = system_data.mod_flg
        self.active_part             = system_data.active_part
        self.model: dict[int, Model] = system_data.model
        self.active_model            = system_data.active_model
        
        for model_id, model in system_data.model.items():
            if not model_id in self.model:
                self.model[model_id] = model
        
        for model_id, model in self.model.items():
            if not model_id in system_data.model:
                del self.model[model_id]
        
        if system_data.active_model.id in self.model:
            self.active_model = self.model[system_data.active_model.id]

        self.get_plotters()

    def open_model(self, path: Path, read_only: bool = False, password: str = None):
        self.client.system.open_model(self, path, read_only, password)
        self.get_inf_sys()

    def get_materials(self):
        self.materials: list[Material] = self.client.system.get_materials()
        return self.materials

    def get_local_font(self, font_name: str):
        return self.client.system.get_local_font(font_name)
    
    def get_plotters(self):
        self.plotters, self.default_plotter = self.client.system.get_plotters()
        return self.plotters, self.default_plotter
    
    def get_language(self):
        language = IniFileParser(f'{self.icaddir}\\LANG\\Language')
        return int( language.get('LANGUAGE').get('ILANGID', '1') )


class IniFileParser:
    def __init__(self, filepath: Path) -> None:
        self._data = {}
        with open(filepath, encoding='cp932') as f:
            lines = f.readlines()
        for line in lines:
            if line[-1] == '\n':
                line = line[:-1]
            if line == '' or line.startswith(';') or line.startswith('；'):
                continue
            elif line.startswith('[') and line.endswith(']'):
                section = line[1:-1]
                self._data[section] = {}
                continue
            else:
                splitted = line.split('=') + ['', '']
                self._data[section][splitted[0]] = splitted[1]

    def __getitem__(self, key) -> dict:
        return self._data.get(key, {})
    
    def get(self, key) -> dict:
        return self.__getitem__(key)


class DBLock:
    def __init__(self, path: Path) -> None:
        self.exe_path = path

    def remove_read_only(self, path: Path):
        process = subprocess.Popen(
                [self.exe_path, '/OFF', str( path.absolute() )],
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        process.wait()
        stdout, stderr = process.communicate()
