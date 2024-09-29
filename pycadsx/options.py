from pathlib import Path
from pycadsx.cadtypes import CadTypes


class SurfaceMarkOption:
    remove_type         = CadTypes.Entity.SMark.RemoveType.NOREMOVE
    lay_symbol          = CadTypes.Entity.SMark.LaySymbol.NONE
    machining_process   = ''
    machining_allowance = ''
    parameter1          = ''
    parameter2          = ''
    parameter3          = ''
    circle_mark         = False
    lead_line           = False
    arrow_type          = CadTypes.Geometry.DimensionLine.Arrow.BOTH
    lead_standard       = True
    setangle            = False
    angle               = 60.0
    additionalline      = False
    lead_left           = False


class Project3d2dOption:
    frame_file: Path             = None
    view_top                     = False
    view_left                    = False
    view_front                   = False
    view_right                   = False
    view_back                    = False
    view_bottom                  = False
    scale                        = 0.0
    mode_view                    = 1
    pos_view_top: list[float]    = [0.0, 0.0, 0.0]
    pos_view_left: list[float]   = [0.0, 0.0, 0.0]
    pos_view_front: list[float]  = [0.0, 0.0, 0.0]
    pos_view_right: list[float]  = [0.0, 0.0, 0.0]
    pos_view_back: list[float]   = [0.0, 0.0, 0.0]
    pos_view_bottom: list[float] = [0.0, 0.0, 0.0]
    space                        = False
    space_right                  = 5.0
    space_top                    = 5.0
    space_left                   = 5.0
    space_bottom                 = 5.0
    remove_overlap               = False
    remove_int                   = False
    tangent_mode                 = 0
    tangent_angle                = 0.0
    part_mode                    = 1
    hole                         = 0
    hole_center_line             = False
    center_offset                = 0
    offset_ratio                 = 10.0
    offset_length                = 2.0
    hole_inf                     = False
    outline                      = 1
    outline_style                = 0
    outline_width                = 0
    inter_hidden_line            = 0
    inter_hidden_line_style      = 2
    inter_hidden_line_width      = 0
    self_hidden_line             = 0
    self_hidden_line_style       = 2
    self_hidden_line_width       = 0
    copy3d                       = True
