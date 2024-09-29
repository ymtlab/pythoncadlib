import base64
import traceback
import sys
import socket
import re
import tempfile
import os
import csv
import io
import math
from pathlib import Path
from lxml import etree
from pycadsx.cadtypes import CadTypes
from pycadsx.edge import Edge
from pycadsx.face import Face
from pycadsx.model import Model
from pycadsx.entity import Entity, EntityFactory
from pycadsx.geometry import (
    GeometryFactory, Text, Note, Datum, ArrowView, CutLine,
    DimensionValue, DimensionLine, BaseDimensionGeometry, BaseGeometry, LineAttribute
)
from pycadsx.material import Material
from pycadsx.part import Part
from pycadsx.plotter import Plotter
from pycadsx.window import Window
from pycadsx.vs import VS
from pycadsx.mass import Mass
from pycadsx.print_info import PrintInfo
from pycadsx.wf import WF
from pycadsx.draft_attribute import DraftAttribute
from pycadsx.options import SurfaceMarkOption, Project3d2dOption
from pycadsx.selection import Selection
from pycadsx.hole import Hole
from pycadsx.r_part import RPart
from pycadsx.pycadsx import PyCadSx


class BaseCommand:
    def __init__(self, client: 'Client') -> None:
        self.client = client

    def send(self, command: str, xml_file_name=None, is_recieve=True, is_macro=False, ret_ent=True) -> etree._Element:
        return self.client.send(command, xml_file_name, is_recieve, is_macro, ret_ent)
    
    def join_entities(self, entities: list[Entity]):
        if len(entities) == 0:
            return ''
        return '\n'.join([ ' '.join([ str(e.id) for e in entities[i:i+5] ]) for i in range(0, len(entities), 5) ])


class AsmPlaneCommand(BaseCommand):

    class Info:
        def __init__(self, element: etree._Element) -> None:
            sx_vs = element.xpath('./sx_vs')[0]
            sx_wf = element.xpath('./sx_wf')[0]
            sx_pos = element.xpath('./sx_pos')[0]
            matrix = []
            for sx_vec in element.xpath('./sx_vec'):
                matrix.append([ float(sx_vec.get(i)) for i in ['x', 'y', 'z'] ])

            matrix.append([
                matrix[0][1] * matrix[1][2] - matrix[0][2] * matrix[1][1],
                matrix[0][2] * matrix[1][0] - matrix[0][0] * matrix[1][2],
                matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
            ])
            
            self.origin  = [ float(sx_pos.get(i)) for i in ['x', 'y', 'z'] ]
            self.matrix  = matrix
            self.vsno    = int( sx_vs.get('vsno') )
            self.vs_type = int( sx_vs.get('type') )
            self.refid   = int( sx_vs.get('refid') )
            self.wfno    = int( sx_wf.get('wfno') )
            self.wf_type = int( sx_wf.get('type') )
    
    def asm_plane_info(self, element: etree._Element):
        return AsmPlaneCommand.Info(element)

    def get_inf(self, model_id: int, wfno: int, plno: int):
        element = self.send(f';JVGAPI .MODEL {model_id} .WFNO {wfno} .PLNO {plno} : ;GXDMY;@JVEND', 'asmplane.get_inf.xml')
        return AsmPlaneCommand.Info(element)

    def set_active(self, pdno: int, plno):
        self.send(f';PLNAVW {pdno} {plno}', 'asmplane.get.xml')

    def delete(self, pdno: int, vs_name: str):
        self.send(f';PLNDEL ={pdno} /{vs_name}/ .MSG /YES/ ;@JVEND', 'asmplane.get.xml')

    def create(self, vsno: int, refid: int):
        self.send(f';PLNVWP @PLNVWP @AUTOVW ={vsno} ;@ENT @PICKID ID {refid} IDEND\n..MSGBOX /YES/\n@GO\n;@JVEND', 'asmplane.create.xml')

    def offset(self, pdno: int, point: list[float], plno: int):
        self.send(f'@PLNOFS ={pdno} ={plno}\n@POS @HIT S {pdno} X {point[0]:.8} Y {point[1]:.8} Z {point[2]:.8},\n;@JVEND', 'asmplane.offset.xml')


class EdgeCommand(BaseCommand):

    class Info:
        def __init__(self, element: etree._Element) -> None:
            self.type      = int( element.get('type') )
            self.edge_type = int( element.get('edge_type') )
            self.id        = int( element.get('id') )
            self.csgsol    = int( element.get('csgsol') )
            self.prmno     = int( element.get('prmno') )
            self.edgeno    = int( element.get('edgeno') )

    def edge_info(self, element: etree._Element):
        return EdgeCommand.Info(element)

    def get_geometry(self, id: int, prmno: int, edgeno: int, csgsol: int):
        element = self.send(f';JVGEOM .ENTID {id} .PRMNO {prmno} .EDGENO {edgeno} .CSGSOL {csgsol} : ;@JVEND', 'edge.get_geometry.xml')

    def get_geometries(self, ids: list[int], prmnos: list[int], edgenos: list[int], csgsols: list[int]):
        element = self.send(';JVGEO2\n' + '\n'.join([f'.ENTID {id} .PRMNO {prmno} .EDGENO {edgeno} .CSGSOL {csgsol} :' for id, prmno, edgeno, csgsol in zip(ids, prmnos, edgenos, csgsols)]) + '\n;@GO;@JVEND', 'edge.get_geometries.xml')

    def get_end_points(self, id: int, prmno: int, edgeno: int, csgsol: int):
        element = self.send(f';JVUENT .KIND 5 .ENTID {id} .PRMNO {prmno} .DSPID {csgsol} .EDGENO {edgeno} : ;@JVEND', 'edge.get_end_points.xml')
        points = []
        for sx_pos in element.xpath('./sx_pos'):
            points.append([float( sx_pos.get('x') ), float( sx_pos.get('y') ), float( sx_pos.get('z') )])
        return points
    
    def get_middle_point(self, id: int, prmno: int, edgeno: int, csgsol: int):
        element = self.send(f';JVUENT .KIND 8 .ENTID {id} .PRMNO {prmno} .DSPID {csgsol} .EDGENO {edgeno} : ;@JVEND', 'edge.get_middle_point.xml')
        for sx_pos in element.xpath('./sx_pos'):
            return [float( sx_pos.get('x') ), float( sx_pos.get('y') ), float( sx_pos.get('z') )]

    def get_on_point(self, id: int, prmno: int, edgeno: int, csgsol: int, point: list[float], read: bool):
        command  = ';JVVEC .KIND 0\n' if read else ';JVVEC .KIND 1\n'
        command += f'.ENTID {id} .PRMNO {prmno} .EDGENO {edgeno} .CSGSOL {csgsol}\n'
        command += f'.PX {point[0]:.8} .PY {point[1]:.8} .PZ {point[2]:.8} :\n;@JVEND'
        element = self.send(command, 'edge.get_on_point.xml')
        for sx_pos in element.xpath('./sx_pos'):
            return [float( sx_pos.get('x') ), float( sx_pos.get('y') ), float( sx_pos.get('z') )]
        
    def get_mass(self, id: int, prmno: int, edgeno: int, csgsol: int):
        element = self.send(f';JVUENT .KIND 7 .ENTID {id} .PRMNO {prmno} .DSPID {csgsol} .EDGENO {edgeno} : ;@JVEND', 'edge.get_mass.xml')

    def get_mass_list(self, ids: list[int], prmnos: list[int], edgenos: list[int], csgsols: list[int]):
        element = self.send(';JVUEN2\n' + '\n'.join([f'.KIND 7 .ENTID {id} .PRMNO {prmno} .DSPID {csgsol} .EDGENO {edgeno} :' for id, prmno, edgeno, csgsol in zip(ids, prmnos, edgenos, csgsols)]) + '\n;@GO;@JVEND', 'edge.get_mass_list.xml')

    def eval(self, id: int, prmno: int, edgeno: int, csgsol: int, point: list[float]):
        element = self.send(f';JVVEC .KIND 1 .ENTID {id} .PRMNO {prmno} .EDGENO {edgeno} .CSGSOL {csgsol} .PX {point[0]:.8} .PY {point[1]:.8} .PZ {point[2]:.8} :\n;@JVEND', 'edge.eval.xml')

    def get_face_list(self, id: int, prmno: int, edgeno: int, csgsol: int):
        element = self.send(f';GXDMY;JVUENT .KIND 3 .ENTID {id} .PRMNO {prmno} .DSPID {csgsol} .EDGENO {edgeno} : ;@JVEND', 'edge.get_face_list.xml')

    def get_face_list_from_edges(self, ids: list[int], prmnos: list[int], edgenos: list[int], csgsols: list[int]):
        element = self.send(';JVUEN2\n' + '\n'.join([f'.KIND 3 .ENTID {id} .PRMNO {prmno} .DSPID {csgsol} .EDGENO {edgeno} :' for id, prmno, edgeno, csgsol in zip(ids, prmnos, edgenos, csgsols)]) + '\n;@GO;@JVEND', 'edge.get_face_list_from_edges.xml')


class EntityCommand(BaseCommand):

    class Data:
        def __init__(self, element: etree._Element) -> None:
            self.type    = CadTypes.Entity().get_type( int( element.get('type') ) )
            self.id      = int( element.get('id') )
            self.prmno   = int( element.get('prmno') )
            self.kind    = CadTypes.Entity.Kind( int( element.get('kind') ) )
            self.part_id = int( element.get('part_id') )
            self.is3d    = element.get('dim') != '0'

    class Info:
        def __init__(self, element: etree._Element) -> None:
            self.userid         = int(element.get('userid'))
            self.is3d           = element.get('dim') != '0'
            self.vswfno         = int(element.get('vswfno'))
            self.layer          = int(element.get('layer'))
            self.type           = CadTypes.Entity().get_type( int(element.get('type')) )
            self.visi           = element.get('visi') != '0'
            self.is_25d         = element.get('is_25d') != '0'
            self.member_kind    = int(element.get('member_kind'))
            self.prim_num       = int(element.get('prim_num'))
            self.ent_len        = int(element.get('ent_len'))
            self.model_id       = int(element.get('model_id'))
            self.grp_kind       = int(element.get('grp_kind'))
            self.cg_attr        = int(element.get('cg_attr'))
            self.profile_attr   = int(element.get('profile_attr'))
            self.part_id        = int(element.get('parts_id'))
            self.arrow_id       = int(element.get('arrow_id'))
            self.body_type      = CadTypes.Entity.BodyType( int(element.get('body_type')) )
            self.id             = int(element.get('id'))
            self.vwtype         = int(element.get('vwtype'))
            self.fc_state       = CadTypes.Entity.FcState( int(element.get('fc_state')) )
            self.is_transparent = element.get('is_transparent') != '0'
            self.is_draft       = element.get('is_draft') != '0'

            num3 = int(element.get('kind'))
            if num3 in [0, 4, 5]:
                num3 = 0
            elif num3 == 2:
                num3 = 1 if self.grp_kind != 0 else 2
            elif num3 == 3:
                num3 = 3
            elif num3 == 6:
                num3 = 6
            
            self.kind = CadTypes.Entity.Kind(num3)
        
    def entity_data(self, element: etree._Element):
        return EntityCommand.Data(element)
    
    def entity_info(self, element: etree._Element):
        return EntityCommand.Info(element)

    def set_dimension_text_size(self, entity_id: int, height: float, width_ratio: float, space_ratio: float, dimtol_ratio1: float, dimtol_ratio2: float, tol_space: float, tilt: int):
        command  = f';CHGATR;MOJI;CTST;TALL\n.DHT {height} .DWD {width_ratio} .DDS {space_ratio} .DKS {dimtol_ratio1} .DSC {dimtol_ratio2} .TST {tol_space} .ANG1 {tilt}\n@PICKID ID {entity_id} IDEND @GO\n;@JVEND'
        element = self.send(command, 'entity.set_dimension_text_size.xml')
        for sx_ent in element.xpath('./sx_ent'):
            return EntityCommand.Data(sx_ent)

    def set_color(self, entity_id: int, color: int):
        self.send(f';COLCHG {color}\n@WINID VISI 6 ID {entity_id} IDEND\n@GO\n;@JVEND', 'entity.set_color.xml')

    def set_layer(self, entity_id: int, layer: int):
        self.send(f';CHGATR;CLAY;ELM\n.NLAY {layer}\n@WINID ID {entity_id} IDEND\n@GO\n;@JVEND', 'entity.set_color.xml')

    def get_geometry(self, entity_id: int, prmno: int):
        element = self.send(f';JVGEOM .ENTID {entity_id} .PRMNO {prmno} : ;@JVEND', 'entity.get_geometry.xml')
        for child in element:
            return GeometryFactory.create(child)
        
    def edit_text(self, entity_type: int, entity_id: int, prmno: int, visi: bool, texts: list[str]):
        command = ''

        if entity_type == CadTypes.Entity.Type.TEXT:
            if len(texts) == 0 or any([ len(text) > 80 for text in texts ]):
                return
            
            text_geometry: Text = self.get_geometry(entity_id, prmno)
            attribute = text_geometry.attribute
            
            command += f';NOTE;EDT;ETEXT\n@PICKID ID {entity_id} IDEND\n..CODFLG /1/\n'
            command += f'..NUMLIN /{len(texts)}LIN/\n..FNTNUM /{len(texts)}/\n'
            command += f'..FNTTYP /{1 if attribute.font else 0}/\n'
            command += f'..FNTNAM /{attribute.font_name if attribute.font else "OFF"}/\n'
            command += f'..FNTITL /{1 if attribute.tilt  == -15 and attribute.font else 0}/\n'
            command += f'..FNTBLD /{1 if attribute.width ==   1 and attribute.font else 0}/\n'
            command += f'..FNTHIT /{attribute.height}/\n'
            command += '\n'.join([f'..STRI{i+1:02} /{self.client.string_to_base64string(text if text != "" else " ")}/' for i, text in enumerate(texts)]) + '\n'

        elif entity_type == CadTypes.Entity.Type.LBL:
            if len(texts) == 0:
                return
            
            note_geometry: Note = self.get_geometry(entity_id, prmno)
            attribute = note_geometry.attribute

            command += f';LABEL;LBL;ETXT\n@PICKID ID {entity_id} IDEND\n..CODFLG /1/\n'
            command += f'..NUMLIN /{len(texts)}LIN/\n..FNTNUM /{len(texts)}/\n'
            command += f'..FNTTYP /{1 if attribute.font else 0}/\n'
            command += f'..FNTNAM /{attribute.font_name if attribute.font else "OFF"}/\n'
            command += f'..FNTITL /{1 if attribute.tilt  == -15 and attribute.font else 0}/\n'
            command += f'..FNTBLD /{1 if attribute.width ==   1 and attribute.font else 0}/\n'
            command += f'..FNTHIT /{attribute.height}/\n'
            command += '\n'.join([f'..STRI{i+1:02} /{self.client.string_to_base64string(text if text != "" else " ")}/' for i, text in enumerate(texts)]) + '\n'
            command += f'..TATEFL /{1 if note_geometry.verline else 0}/\n'
            command += f'..SITAFL /{1 if note_geometry.underline else 0}/\n'

        elif entity_type == CadTypes.Entity.Type.BALL:
            texts[1] = texts[1].replace('/', '//') if len(texts) > 1 and texts[1] is not None and texts[1] != '' else ' '
            command += f';BALOON;BAL;ETXT\n@PICKID ID {entity_id} IDEND\n'
            command += f'.UTXT /{texts[0].replace("/", "//")}/ .DTXT /{texts[1]}/ :\n'

        elif entity_type in [ CadTypes.Entity.Type.APL, CadTypes.Entity.Type.ARL, CadTypes.Entity.Type.DLIN, CadTypes.Entity.Type.DANG, CadTypes.Entity.Type.DARC, CadTypes.Entity.Type.DCHA ]:
            if len(texts[0]) > 32:
                return
            command += f';CHGDM2;CDIM;CED\n@PICKID ID {entity_id} IDEND\n'
            command += '..CODFLG /1/\n'
            command += '..NUMLIN /1LIN/\n'
            command += '..FNTNUM /0/\n'
            command += '..FNTTYP /0/\n'
            command += '..FNTNAM //\n'
            command += '..FNTITL /0/\n'
            command += '..FNTBLD /0/\n'
            command += '..FNTHIT /0/\n'
            command += f'..STRI01 /{self.client.string_to_base64string(texts[0])}/\n'

        elif entity_type == CadTypes.Entity.Type.DELTA:
            if len(texts[0]) > 3:
                return
            command += f';SMBAPL;DLT;EDT\n@PICKID ID {entity_id} IDEND\n.DTXT /{texts[0].replace("/", "//")}/\n'

        elif entity_type == CadTypes.Entity.Type.GTOL:
            geometry = self.get_geometry(entity_id, prmno)
            if type(geometry) is not Datum:
                return
            if len(texts[0]) > 2:
                return
            command += f';GEOTOL;GEW;KIGO\n@PICKID ID {entity_id} IDEND\n.SGN /{texts[0].replace("/", "//")}/\n'

        elif entity_type == CadTypes.Entity.Type.SYM:
            if len(texts[0]) > 8:
                return
            geometry = self.get_geometry(entity_id, prmno)
            if type(geometry) is not ArrowView:
                if type(geometry) is not CutLine:
                    return
                command += f';SMBAPL;LCT;EDS;ETXT\n@PICKID ID {entity_id} IDEND\n.SETU /{texts[0].replace('/', '//')}/\n'
            else:
                command += f';SMBAPL;LAR;EDY;ETXT\n@PICKID ID {entity_id} IDEND\n'

        else:
            return

        command += ';@JVEND'
        element = self.send(command, 'entity.edit_text.xml')

        entity_data = None
        for sx_ent in element.xpath('./sx_ent'):
            entity_data = EntityCommand.Data(sx_ent)
            break

        if not visi and entity_data is not None:
            self.set_visible(entity_data.id, False)
        
        return entity_data

    def set_visible(self, entity_id: int, visible: bool):
        self.send(f'{";JVVISI" if visible else ";INVIS;OPT"}\n@WINID ID {entity_id} IDEND\n@GO\n;@JVEND', 'entity.set_visible.xml')

    def edit_dimension_text(self, entity_id: int, entity_type: int, visi: bool, dimension_text: DimensionValue, dimension_line: DimensionLine):
        if not entity_type in [
                    CadTypes.Entity.Type.APL,
                    CadTypes.Entity.Type.ARL,
                    CadTypes.Entity.Type.DLIN,
                    CadTypes.Entity.Type.DANG,
                    CadTypes.Entity.Type.DARC,
                    CadTypes.Entity.Type.DCHA
                ]:
            return
        
        num3 = dimension_text.mark2 * 10 + dimension_text.mark3 if not dimension_text.mark1 else 100 + dimension_text.mark2 * 10 + dimension_text.mark3

        if not (num3 % 10 == 9):
            if num3 == 7:
                num2 = 42
            elif num3 == 8:
                num2 = 43
            else:
                if (
                        (num3 <   0 or num3 >   6) and
                        (num3 <  10 or num3 >  16) and
                        (num3 <  20 or num3 >  26) and
                        (num3 < 100 or num3 > 106) and
                        (num3 < 110 or num3 > 116) and
                        (num3 < 120 or num3 > 126)
                    ):
                    return
                if num3 >= 100:
                    num2 = 21
                num3 %= 100
                if (num3 / 10 == 1):
                    num2 += 7
                if (num3 / 20 == 1):
                    num2 += 14
                num3 %= 10
                num2 += num3
        
        dimension_text.upper_tolword = dimension_text.upper_tolword.Trim()
        if (dimension_text.upper_tolword != "" and dimension_text.upper_tolword is not None):
            dimension_text.down_tolword = dimension_text.down_tolword.Trim()
            if (dimension_text.down_tolword != "" and dimension_text.down_tolword is not None):
                tolerance = f'{dimension_text.upper_tolword.replace("±", "*")}//{dimension_text.down_tolword.replace("±", "*")}'
            else:
                tolerance = dimension_text.upper_tolword.replace("±", "*")
        else:
            tolerance = ''
        
        command  = f';CHGDM2;CDIM;OCED\n@PICKID ID {entity_id} IDEND\n'
        command += f'..DIMTYP /{1}/\n'
        command += f'..DIMKIN /{1}/\n'
        command += f'..DIMTX1 /{dimension_text.frontword.replace("/", "//")}/\n'
        command += f'..DIMTX2 /{dimension_text.backword.replace("/", "//")}/\n'
        command += f'..DIMTX3 /{dimension_text.downword.replace("/", "//")}/\n'
        command += f'..DIMNUM /{dimension_text.str_num}/\n'
        command += f'..DIMKFG /{1 if (num3 % 10 == 9) else 0}/\n'
        command += f'..DIMSIN /{num2}/\n'
        command += f'..DIMNIN /{dimension_text.opt_word}/\n'
        command += f'..DIMREF /{1 if dimension_text.val_refer else 0}/\n'
        command += f'..DIMTFG /{1 if dimension_text.dimval_type else 2}/\n'
        command += f'..DIMNOT /{dimension_text.valword.replace("/", "//")}/\n'
        command += f'..DIMDIS /{dimension_text.dist1}/\n'
        command += f'..DIMDI2 /{dimension_text.dist2}/\n'
        command += f'..DIMHEM /{dimension_text.hmword.replace("/", "//")}/\n'
        command += f'..DIMRE2 /{1 if dimension_text.tol_refer else 0}/\n'
        command += f'..DIMTOL /{tolerance}/\n'
        command += f'..DIMROL /{dimension_line.round}/\n'
        command += f'..DIMWAY /{3}/\n'
        command += f'..DIMMHB /{dimension_line.multiple}/\n'
        command += f'..DIMMMD /{dimension_line.multiple_mode}/\n'
        command += f'..DIMZER /{1 if dimension_line.suppress else 0}/\n'
        command += f'..DIMSCL /{dimension_line.dimval_scale}/\n'
        command += f'..DIMDEG /{dimension_line.angtype + 4 if entity_type == 26 else 4}/\n'
        command += f'..DIMDOT /{1 if dimension_line.dot else 0}/\n'
        command += f'..DIMRCT /{1 if dimension_text.frame else 0}/\n'
        command += f'..DIMUNL /{1 if dimension_text.underline else 0}/\n'
        command += f'..DIMMFL /{1 if dimension_text.correctline else 0}/\n'
        command += f';@JVEND'
        
        element = self.send(command, 'entity.edit_dimension_text.xml')
        entity_data = None
        for sx_ent in element.xpath('./sx_ent'):
            entity_data = EntityCommand.Data(sx_ent)
            break

        if not visi:
            self.set_visible(entity_id, False)
        
        return entity_data

    def get_on_point(self, entity_id: int, prmno: int, point: list[float], real: bool):
        element = self.send(f';JVVEC .KIND {0 if real else 1} .ENTID {entity_id} .PRMNO {prmno} .PX {point[0]:.8f} .PY {point[1]:.8f} .PZ {point[2]:.8f} : ;@JVEND', 'entity.get_on_point.xml')
        for sx_pos in element.xpath('entity.get_on_point.xml'):
            return [ float( sx_pos.get('x') ), float( sx_pos.get('y') ), float( sx_pos.get('z') ) ]


class FaceCommand(BaseCommand):

    class Data:
        def __init__(self, element: etree._Element) -> None:
            self.id        = element.get('id')
            self.prmno     = element.get('prmno')
            self.faceno    = element.get('faceno')
            self.csgsol    = element.get('csgsol')
            self.type      = element.get('type')
            self.face_type = element.get('face_type')
    
    def face_data(self, element: etree._Element):
        return FaceCommand.Data(element)
    
    def get_geometry(self, face: Face):
        element = self.send(f';JVGEOM .ENTID {face.id} .PRMNO {face.prmno} .FACENO {face.faceno} .CSGSOL {face.csgsol} : ;@JVEND', 'face.get_geometry.xml')
        return GeometryFactory.create(element)

    def get_geometries(self, faces: list[Face]):
        element = self.send(';JVGEO2\n' + '\n'.join([ f'.ENTID {f.id} .PRMNO {f.prmno} .FACENO {f.faceno} .CSGSOL {f.csgsol} :' for f in faces]) + '\n;@GO;@JVEND', 'face.get_geometries.xml')
        return [ GeometryFactory.create(e) for e in element ]

    def get_edges(self, face: Face):
        element = self.send(f';GXDMY;JVUENT .KIND 4 .ENTID {face.id} .PRMNO {face.prmno} .DSPID {face.csgsol} .FACENO {face.faceno} : ;@JVEND', 'face.get_edges.xml')
        edges = []
        for sx_edge in element.xpath('./sx_edge'):
            edge = Edge(self.client)
            edge.from_edge( EdgeCommand.Info(sx_edge) )
            edges.append(edge)
        return edges

    def get_faces_edges(self, faces: list[Face]):
        element = self.send(';JVUEN2\n' + '\n'.join([f'.KIND 4 .ENTID {f.id} .PRMNO {f.prmno} .DSPID {f.csgsol} .FACENO {f.faceno} :' for f in faces]) + '\n;@GO;@JVEND', 'face.get_faces_edges.xml')
        edges = []
        for sx_edge in element.xpath('./sx_edge'):
            edge = Edge(self.client)
            edge.from_edge( EdgeCommand.Info(sx_edge) )
            edges.append(edge)
        return edges

    def get_center_point(self, face: Face):
        element = self.send(f';JVUENT .KIND 8 .ENTID {face.id} .PRMNO {face.prmno} .DSPID {face.csgsol} .FACENO {face.faceno} ;@JVEND', 'face.get_center_point.xml')
        for sx_pos in element.xpath('./sx_pos'):
            return [ float(sx_pos.get('x')), float(sx_pos.get('y')), float(sx_pos.get('z')) ]

    def get_on_point(self, face: Face, point: list[float]=None, real: bool=None):
        if point is None and real is None:
            command  = f';JVUENT .KIND 16 .ENTID {face.id} .PRMNO {face.prmno} .DSPID {face.csgsol} .FACENO {face.faceno} ;@JVEND'
        else:
            command  = f';JVVEC .KIND {0 if real else 1}\n.ENTID {face.id} .PRMNO {face.prmno} .FACENO {face.faceno} .CSGSOL {face.csgsol} .PX {point[0]:0.8f} .PY {point[1]:0.8f} .PZ {point[2]:0.8f} : ;@JVEND'
        element = self.send(command, 'face.get_on_point.xml')
        for sx_pos in element.xpath('./sx_pos'):
            return [ float(sx_pos.get('x')), float(sx_pos.get('y')), float(sx_pos.get('z')) ]

    def get_mass(self, face: Face):
        command = f';JVUENT .KIND 7 .ENTID {face.id} .PRMNO {face.prmno} .DSPID {face.csgsol} .FACENO {face.faceno} : ;@JVEND'
        element = self.send(command, 'face.get_on_point.xml')
        for sx_inf_mass in element.xpath('sx_inf_mass'):
            return Mass(sx_inf_mass)

    def get_masses(self, faces: list[Face]):
        element = self.send(';JVUEN2\n' + '\n'.join([f'.KIND 7 .ENTID {f.id} .PRMNO {f.prmno} .DSPID {f.csgsol} .FACENO {f.faceno} :' for f in faces]) + '\n;@GO;@JVEND', 'face.get_masses.xml')
        return [ Mass(sx_inf_mass) for sx_inf_mass in element.xpath('sx_inf_mass') ]

    def eval(self, face: Face, point: list[float]):
        command  = f';JVVEC .KIND 1 .ENTID {face.id}, .PRMNO {face.prmno} .FACENO {face.faceno} .CSGSOL {face.csgsol}\n'
        command += f'.PX {point[0]:.8f} .PY {point[1]:.8f} .PZ {point[2]:.8f} : ;@JVEND'
        element = self.send(command, 'face.eval.xml')

    def get_color(self, face: Face):
        element = self.send(f';JVUENT .KIND 13 .ENTID {face.id} .PRMNO {face.prmno} .DSPID {face.csgsol} .FACENO {face.faceno} : ;@JVEND', 'face.get_color.xml')
        for sx_int in element.xpath('./sx_int'):
            return CadTypes.Color(int(sx_int))

    def get_colors(self, faces: list[Face]):
        element = self.send('\n'.join([f';JVUENT .KIND 13 .ENTID {f.id} .PRMNO {f.prmno} .DSPID {f.csgsol} .FACENO {f.faceno} :' for f in faces]) + '\n;@JVEND', 'face.get_colors.xml')
        return [ CadTypes.Color(int(sx_int)) for sx_int in element.xpath('./sx_int') ]

    def set_color(self, face: Face, color: CadTypes.Color):
        command  = ';CHGATR;FACATR;NONCOL\n' if color == CadTypes.Color.NONE else f';FCLCHG {color}\n'
        command += f'@ENT @PICKID ID {face.id} MID {face.csgsol} PNO {face.prmno} FNO {face.faceno} IDEND\n'
        command += f'@GO\n.SHORI / 0/\n;GXDMY;@JVEND'
        self.send(command, 'face.set_color.xml')

    def set_colors(self, faces: list[Face], color: CadTypes.Color):
        command  = ';CHGATR;FACATR;NONCOL' if color == CadTypes.Color.NONE else f';FCLCHG {color}'
        command += '\n'.join([f'@ENT @PICKID ID {f.id} MID {f.csgsol} PNO {f.prmno} FNO {f.faceno} IDEND' for f in faces])
        command += f'\n@GO\n.SHORI / 0/\n;GXDMY;@JVEND'
        self.send(command, 'face.set_colors.xml')


class HoleCommand(BaseCommand):
    
    class Data:
        def __init__(self, element: etree._Element) -> None:
            self.name         = element.get('name')
            self.detail_name  = element.get('detail_name')
            self.pattern_name = element.get('hole_yobi')
            self.hole_type    = element.get('hole_type')
            self.modeltype    = int(element.get('modeltype'))
            self.id           = int(element.get('id'))
            self.hole_number  = int(element.get('hole_number'))
            self.tap_type     = int(element.get('tap_type'))
            self.num_th       = int(element.get('num_th'))
            self.dir_th       = int(element.get('dir_th'))
            self.d_type       = element.get('d_type')
            self.penetrate    = element.get('penetrate') == '1'
            self.u_name       = element.get('u_name')

            self.origin: list[float] = [ float(element.get('orgx', 0.0)), float(element.get('orgy', 0.0)), float(element.get('orgz', 0.0)) ]

            self.matrix: list[list[float]] = [
                [ float(element.get('xvecx', 0.0)), float(element.get('xvecy', 0.0)), float(element.get('xvecz', 0.0)) ],
                [],
                [ float(element.get('zvecx', 0.0)), float(element.get('zvecy', 0.0)), float(element.get('zvecz', 0.0)) ]
            ]

            self.matrix[1] = [
                self.matrix[2][1] * self.matrix[0][2] - self.matrix[2][2] * self.matrix[0][1],
                self.matrix[2][2] * self.matrix[0][0] - self.matrix[2][0] * self.matrix[0][2],
                self.matrix[2][0] * self.matrix[0][1] - self.matrix[2][1] * self.matrix[0][0]
            ]


class RPartCommand(BaseCommand):

    class Data:
        def __init__(self, element: etree._Element) -> None:
            self.type       = int( element.get('type') )    if element is not None else None
            self.id         = int( element.get('id') )      if element is not None else None
            self.prmno      = int( element.get('prmno') )   if element is not None else None
            self.kind       = int( element.get('kind') )    if element is not None else None
            self.part_id    = int( element.get('part_id') ) if element is not None else None
            self.is3d: bool = element.get('dim') != '0'     if element is not None else None
    
    class Info:
        def __init__(self, element: etree._Element) -> None:
            self.name: str           = element.get('name', '')
            self.comment: str        = element.get('comment', '')
            self.origin              = [ float( element.get(f'org{i}') ) for i in ['x', 'y', 'z'] ]
            self.angle               = float( element.get('angle') )
            self.ref_model_name: str = element.get('ref_model_name', '')
            self.ref_vs_name: str    = element.get('ref_vs_name', '')
            self.is_mirror: bool     = element.get('is_mirror') != '0'
            self.has_pos: bool       = element.get('has_pos') != '0'
            self.part3d_name         = element.get('part3d_name', '')
        
    def r_part_data(self, element: etree._Element):
        return RPartCommand.Data(element)
    
    def r_part_info(self, element: etree._Element):
        return RPartCommand.Info(element)

    def get_entities(self, r_part: RPart):
        data = self.send(f';GXDMY;JVUENT .KIND 2 .ENTID {r_part.id} : ;@JVEND', 'rpart.get_entities.xml')

        entities = {}
        for sx_ent in data.findall('sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity
            
        return entities


class WfCommand(BaseCommand):

    class Data:
        def __init__(self, element: etree._Element) -> None:
            self.model_id = int( element.get('model_id', '0') )
            self.wfno = int( element.get('wfno', '0') )
            self.type = int( element.get('type', '0') )

    class Info:
        def __init__(self, element: etree._Element) -> None:
            self.name        = element.get('name', '')
            self.type        = int( element.get('type', '0') )
            self.top_name    = element.get('top_name', '')
            self.top_comment = element.get('top_comment', '')
    
    def wf_data(self, element: etree._Element):
        return WfCommand.Data(element)
    
    def wf_info(self, element: etree._Element):
        return WfCommand.Info(element)


class VsCommand(BaseCommand):

    class Data:
        def __init__(self, element: etree._Element) -> None:
            self.model_id = int(element.get('model_id'))
            self.vsno = int(element.get('vsno'))
            self.type = CadTypes.VS.Type( int(element.get('type')) )
            self.refid = int(element.get('refid'))

    class Info:
        def __init__(self, element: etree._Element) -> None:
            sx_inf_vs = element.find('sx_inf_vs')
            sx_pos = sx_inf_vs.find('sx_pos')

            matrix = []
            for sx_vec in sx_inf_vs.findall('sx_vec'):
                matrix.append([ float(sx_vec.get('x')), float(sx_vec.get('y')), float(sx_vec.get('z')) ])
            
            matrix.append([
                matrix[0][1] * matrix[1][2] - matrix[0][2] * matrix[1][1],
                matrix[0][2] * matrix[1][0] - matrix[0][0] * matrix[1][2],
                matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
            ])

            view_type = {'!XY': 2, '!-XZ': 1, '!YZ': 3, '!-YZ': 4, '!X-Y': 5, '!XZ': 6, '!!GLOBAL': 0}

            self.name = sx_inf_vs.get('name')
            self.origin = [float(sx_inf_vs.get('x')), float(sx_inf_vs.get('y')), 0.0]
            self.angle = float(sx_inf_vs.get('angle'))
            self.scale = float(sx_inf_vs.get('scale'))
            self.has_local = sx_inf_vs.get('has_local') != '0'
            self.comment = sx_inf_vs.get('comment')
            self.type = CadTypes.VS.Type( int(sx_inf_vs.get('type')) )
            self.view_type = CadTypes.VS.View( view_type.get(self.name, -1) )
            self.local_origin = [ float(sx_pos.get(i)) for i in ['x', 'y', 'z'] ]
            self.local_matrix = [ matrix[1], matrix[2], matrix[0] ]
    
    def vs_data(self, element: etree._Element):
        return VsCommand.Data(element)
    
    def vs_info(self, element: etree._Element):
        return VsCommand.Info(element)

    def get_inf(self, vs: VS):
        element = self.send(f';JVGWVI .MODEL {vs.model_id} .VS {vs.vsno} .WF 0 : ;@JVEND', 'vs.inf.xml')
        return VsCommand.Info(element)

    def get_window(self, vs: VS):
        data = self.send(f';JVGPD .MODEL {vs.model_id} .VS {vs.vsno} .WF 0 : ;@JVEND', 'vs.get_window.xml')
        for sx_pd in data.xpath('./sx_pd'):
            window = Window(self.client, int(sx_pd.get('pdno')))
            return window

    def set_active(self, vs: VS):
        window = self.get_window(vs)
        if window is None:
            return
        self.send(f';XSOPW2 {window.pdno} 2 /{vs.name}/ .MSG /YES/ ;@JVEND', 'vs.set_active', False)
        return window

    def get_entities(self, vs: VS, offset: int, num: int, visible: bool, part: bool, layer: bool, _type: bool):
        self.set_active(vs)
        command  = f';JVUVW .KIND 1 .SXDIM 2 .MODEL {vs.model_id} .VWNO {vs.vsno} .NUM0 {offset} .NUM1 {num} '
        command += f'.VISI {1 if visible else 0} .RPART {1 if part else 0} .LAYER {1 if layer else 0} .STYPE {1 if _type else 0} : ;@JVEND'
        element = self.send(command, 'vs.get_entities.xml')
        
        entities: dict[int, Entity] = {}
        for sx_ent in element.xpath('./sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity
        
        element = self.send(';JVEIN2\n' + '\n'.join([ f'.ID {e.id} :' for e in entities.values() ]) + '\n@GO;@JVEND', 'vs.get_intent.xml')
        for sx_entinf in element.xpath('./sx_entinf'):
            _id = int( sx_entinf.get('id') )
            if _id in entities:
                entities[_id].from_inf(EntityCommand.Info(sx_entinf))

        return entities
    
    def get_r_parts(self, vs: VS, partname: str=None) -> dict[int, RPart]:
        kind = 5 if partname is not None else 6
        if partname is None:
            partname = ' '
        data = self.send(f';JVUVW .KIND {kind} .SXDIM 2 .MODEL {vs.model_id} .VWNO {vs.vsno} .PNAME /{partname}/ : ;@JVEND', 'vs.get_r_parts.xml')

        r_parts: dict[int, RPart] = {}
        for sx_ent in data.xpath('./sx_ent'):
            r_part = RPart(self.client, vs.model_id, 0, vs.vsno)
            r_part.from_ent(RPartCommand.Data(sx_ent))
            r_parts[r_part.id] = r_part
        
        data = self.send(';JVGPI2\n' + '\n'.join([ f'.KIND 0 .ID {r_part.id} :' for r_part in r_parts.values() ]) + '\n;@GO;@JVEND', 'vs.get_inf_r_parts.xml')
        for inf_r_part in data.xpath('./sx_inf_rpart'):
            part_id = int( inf_r_part.get('id') )
            r_part = r_parts[part_id]
            r_part.from_inf_r_part(RPartCommand.Info(inf_r_part))

        return r_parts

    def get_entities_in_rect(self, vs: VS, p0: list[float], p1: list[float], part: bool, cross: bool):

        element = self.send(';JVGSIF;GXDMY;@JVEND', 'pycadsx.get_inf_sys.xml')
        sx_inf_sys = element.xpath('./sx_inf_sys')
        _cross = sx_inf_sys[0].get('cross', '0') != '0' if len(sx_inf_sys) > 0 else False

        window = self.set_active(vs)

        command  = f'@SWIN W{"ON" if cross else "IS"}\n' if cross != _cross else ''
        command += f';JVENTS .KIND {1 if part else 0} : @WIN\n'
        command += f'S {window.pdno} X {p0[0]:.8f} Y {p0[1]:.8f} Z 0 ,\n'
        command += f'S {window.pdno} X {p1[0]:.8f} Y {p1[1]:.8f} Z 0 ,\n'
        command +=  '@GO;GXDMY\n'
        command += f'@SWIN W{"ON" if _cross else "IS"}' if cross != _cross else ''

        element = self.send(command, 'vs.get_entities_in_rect.xml')
        
        entities: dict[int, Entity] = {}
        for sx_ent in element.xpath('./sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity
        
        element = self.send(';JVEIN2\n' + '.\n'.join([ f'.ID {e.id} :' for e in entities.values() ]) + '\n@GO;@JVEND', 'vs.get_intent.xml')
        for sx_entinf in element.xpath('./sx_entinf'):
            _id = int( sx_entinf.get('id') )
            if _id in entities:
                entities[_id].from_inf( EntityCommand.Info(sx_entinf) )

        return entities

    def get_extent(self, vs: VS):
        element = self.send(f';JVUVW .KIND 0 .SXDIM 2 .MODEL {vs.model_id} .VWNO {vs.vsno} : ;@JVEND', 'vs.get_extent.xml')
        for sx_box in element.xpath('./sx_box'):
            points = [ [ float(sx_box.get(f'{j}{i}')) for j in ['x', 'y', 'z'] ] for i in ['1', '2'] ]
            _id = int( sx_box.get('id') )
            return points
        
    def get_view_position(self, vs: VS):
        point = [0.113 * vs.vsno, 0.137 * vs.vsno]
        return vs.convert_point(point)

    def move(self, vs: VS, point: list[float]):
        if vs.refid != 0:
            command = f';VWTRNS @ENT @PICKID ID {vs.refid} IDEND '
        else:
            #point = self.get_view_position(vs)
            pdno = vs.get_window().pdno
            command = f';VWTRNS @HIT S {pdno} X {vs.origin[0] + 0.1:.8f} Y {vs.origin[1] + 0.1:.8f} Z 0.0 , '
        command += f'.TRANSX {point[0] - vs.origin[0]:.8f} .TRANSY {point[1] - vs.origin[1]:.8f} : ;@JVEND'
        self.send(command, 'vs.get_extent.xml')

    def set_scale(self, vs: VS, scale: float, move_view: bool = False):
        if vs.type == CadTypes.VS.Type.WORK_VS:
            self.send(f';KICNTL;DSCALE .SCL {scale:.8f} : ;@JVEND', 'vs.set_scale.xml')
        else:
            if vs.refid != 0:
                command = f';VWSCAL @ENT @PICKID ID {vs.refid} IDEND '
            else:
                point = self.get_view_position(vs)
                command = f';VWSCAL;@POS @ON S {vs.get_window().pdno} X {point[0]:.8f} Y {point[1]:.8f} Z 0.0 , '
                #;VWSCAL;@HIT S {sxWindow.pdno} X {inf.org.x + 0.1:.8f} Y {inf.org.y + 0.1:.8f} Z 0.0 ,
            if vs.type == CadTypes.VS.Type.VIEW:
                command += ';SCALE1 ' if move_view else ';SCALE2 '
            command += f'.SCL {scale:.8f} : ;@JVEND'
            self.send(command, 'vs.set_scale.xml')


class ModelCommand(BaseCommand):

    default_papers = [
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

    class Data:
        def __init__(self, element: etree._Element) -> None:
            self.path: str          = element.get('path')
            self.name: str          = element.get('name')
            self.comment: str       = element.get('comment')
            self.passwd: str        = element.get('passwd')
            self.is_read_only: bool = element.get('is_read_only') != '0'
            self.is_modify: bool    = element.get('is_modify') != '0'
            self.access             = int( element.get('access') )
            self.nvs                = int( element.get('nvs') )
            self.nwf                = int( element.get('nwf') )

    def model_data(self, element: etree._Element):
        return ModelCommand.Data(element)
    
    def create(self):
        self.send(';NEW;CLR;@JVEND', 'model.create.xml')
    
    def get_inf(self, model: Model):
        element = self.send(f';JVGMIF .NAME {model.id} : ;GXDMY;@JVEND', 'model.get_inf.xml')
        for sx_inf_model in element.xpath('./sx_inf_model'):
            model_data = ModelCommand.Data(sx_inf_model)
            model.path: str          = model_data.path
            model.name: str          = model_data.name
            model.comment: str       = model_data.comment
            model.passwd: str        = model_data.passwd
            model.is_read_only: bool = model_data.is_read_only
            model.is_modify: bool    = model_data.is_modify
            model.access             = model_data.access
            model.nvs                = model_data.nvs
            model.nwf                = model_data.nwf
            return model_data

    def get_vs_list(self, model: Model):
        data = self.send(f';JVGVWL .MODEL {model.id} .VWMODE 2 : ;@JVEND', 'model.get_vs_list.xml')
        vs_list, vs_global = [], None
        for sx_vs in data.findall('sx_vs'):
            vs = VS(self.client)
            vs.from_data( VsCommand.Data(sx_vs) )
            vs.get_inf()
            vs_list.append(vs)
            if vs.type == CadTypes.VS.Type.GLOBAL_VIEW:
                vs_global = vs
        return vs_list, vs_global

    def get_wf_list(self, model: Model):
        wf_list, wf_global = [], None
        element = self.send(f';JVGVWL .MODEL {model.id} .VWMODE 3 : ;@JVEND', 'model.get_wf_list.xml')
        for sx_wf in element.xpath('./sx_wf'):
            wf = WF(self.client)
            wf.from_data( WfCommand.Data(sx_wf) )
            sx_inf_wf = self.send(f';JVGWVI .MODEL {model.id} .VS 0 .WF {wf.wfno} : ;@JVEND', 'model.get_inf_wf.xml')
            wf.from_inf( WfCommand.Info(sx_inf_wf.xpath('./sx_inf_wf')[0]) )
            wf_list.append(wf)
            if wf.Type.GLOBAL_WF == wf.type:
                wf_global = wf
        return wf_list, wf_global
        
    def create_asm_plane(self, vs: VS):
        self.send(f';PLNVWP @PLNVWP @AUTOVW ={vs.vsno} ;@ENT @PICKID ID {vs.refid} IDEND ..MSGBOX /YES/ @GO ;@JVEND', 'model.create_asm_plane.xml')

    def delete_entities(self, entities: list[Entity]):
        if len(entities) == 0:
            return
        command  = ';ERASE;OPT;@IOFF FEATURE ;@IOFF HSCH ;@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n;@GO\n.MSG /ALL /\n.SHORI / 0/\n;GXDMY;@JVEND'
        self.send(command, 'model.delete_entities.xml')

    def delete_print_infos(self, print_infos: list[PrintInfo]):
        if len(print_infos) == 0:
            return
        command  =  ';PLOT3;INF;DEL;LST\n'
        command += f'.SELCNT /{len(print_infos):2d}/\n'
        command += '\n'.join([f'.AREA /{info.no:2d}/' for info in print_infos ])
        command += '\n: ;GXDMY;@JVEND'
        self.send(command, 'model.delete_print_infos.xml')

    def delete_vs(self, vs: VS, window: Window):
        if vs.type == CadTypes.VS.Type.WORK_VS:
            self.send(';KPURGE;DEL .MSG /YES / : .MSG /CAN / : ;@JVEND', 'model.delete_vs.xml')
            return
        
        if vs.refid != 0:
            command = f';VWERSE;DEL @ENT @PICKID ID {vs.refid} IDEND\n'
        else:
            point = [0.113 * vs.vsno, 0.137 * vs.vsno]
            point2 = vs.convert_point(point, True)
            command = f';VWERSE;DEL;@POS @ON S {window.pdno:d} X {point2[0]:.8f} Y {point2[1]:.8f} Z 0.0 ,\n'
        command += '@GO .MSG /YES/ ;@JVEND'
        self.send(command, 'model.delete_vs.xml')

    def get_tree(self, model: Model, wf: WF = None):

        try:
            element = self.send(f';JVUVW .KIND 10 .SXDIM 3 .MODEL {model.id} .VWNO {wf.wfno} : ;@JVEND', 'model.get_modified_parts_list.xml')
            model.modified_ids = [ int( sx_ent.get('id') ) for sx_ent in element.xpath('./sx_ent') ]
        except:
            model.modified_ids = []

        try:
            element = self.send(f';JVGPID .KIND 5 .MODEL {model.id} .WFNO {wf.wfno} : ;@JVEND', 'model.get_tree.xml')
            
            stack = [ (model.top_part, element) for element in element.xpath('./sx_inf_parttree') ]
            while stack:
                parent_part, element = stack.pop()
                
                for sx_inf_parttree in element.xpath('./sx_inf_parttree'):

                    child_part = Part(self.client, model.id, wf.wfno)

                    for sx_ent in sx_inf_parttree.xpath('./sx_ent'):
                        child_part.from_ent( PartCommand.Data(sx_ent) )
                        break

                    for sx_inf_part in sx_inf_parttree.xpath('./sx_inf_part'):
                        child_part.from_inf_part( PartCommand.Info(sx_inf_part) )
                        break

                    sx_str_list = sx_inf_parttree.xpath('./sx_str')
                    if len(sx_str_list) > 0:
                        child_part.extra_info = self.client.extra_info_to_dict([i.text for i in sx_str_list])
                    
                    child_part.parent = parent_part
                    child_part.is_modified = child_part.id in model.modified_ids
                    model.parts[child_part.id] = child_part
                    parent_part.children.append(child_part)

                    stack.append( (child_part, sx_inf_parttree) )
        except:
            model.top_part.get_children()
            stack1 = model.top_part.children.copy()
            while stack1:
                parent_part = stack1.pop()
                parent_part.is_modified = parent_part.id in model.modified_ids
                model.parts[parent_part.id] = parent_part

                try:
                    element = self.send(f';JVGPID .KIND 5 .ID {parent_part.id} : ;@JVEND', 'part.get_tree_element.xml')
                    stack2 = [ ( parent_part, element.xpath('./sx_inf_parttree')[0] ) ]
                    while stack2:
                        parent_part, element = stack2.pop()

                        for sx_inf_parttree in element.xpath('./sx_inf_parttree'):
                        
                            child_part = Part(self.client, model.id, wf.wfno)

                            for sx_ent in sx_inf_parttree.xpath('./sx_ent'):
                                child_part.from_ent( PartCommand.Data(sx_ent) )
                                break

                            for sx_inf_part in sx_inf_parttree.xpath('./sx_inf_part'):
                                child_part.from_inf_part( PartCommand.Info(sx_inf_part) )
                                break

                            sx_str_list = sx_inf_parttree.xpath('./sx_str')
                            if len(sx_str_list) > 0:
                                child_part.extra_info = self.client.extra_info_to_dict([i.text for i in sx_str_list])

                            child_part.parent = parent_part
                            child_part.is_modified = child_part.id in model.modified_ids
                            model.parts[child_part.id] = child_part
                            parent_part.children.append(child_part)

                            stack2.append( (child_part, sx_inf_parttree) )
                    
                except:
                    parent_part.get_children()

                    for child_part in parent_part.children:
                        child_part.is_modified = child_part.id in model.modified_ids
                        stack1.append(child_part)

    def get_extra_infos(self, parts: list['Part']):
        exinfs = self.send(';JVPIX3;PGET\n' + '\n'.join([f'@WINID ID {p.id} IDEND' for p in parts if p.id != 0]) + '\n;@GO;@JVEND', 'model.get_extra_infos.xml')
        if len(exinfs) > 0:
            extra_info: dict[int] = {}
            texts = []
            for data in exinfs:
                if data.tag == 'sx_str':
                    texts.append(data.text)
                if data.tag == 'sx_ent':
                    part_id = int( data.get('part_id') )
                    extra_info[part_id] = texts
                    texts = []
            for part in parts:
                part.extra_info = self.client.extra_info_to_dict( extra_info.get(part.id, []) )

    def set_extra_infos(self, parts: list['Part'], extra_infos: list[dict[str, str]]):
        for i in range(len(parts)):
            if parts[i].id == 0:
                top_part = parts.pop(i)
                top_part_extra_info = extra_infos.pop(i)
                top_part.set_extra_info(top_part_extra_info)
                break

        if len(parts) == 0:
            return
        
        for i in list( range( len(parts) ) )[::-1]:
            if not extra_infos[i]:
                parts.pop(i)
                extra_infos.pop(i)

        if len(parts) == 0:
            return
        
        extra_info_commands = []
        for extra_info in extra_infos:
            base64_string = self.client.extra_info_to_base64string(extra_info)
            array = []
            for i, text in enumerate( re.split('[\n,\0]', base64_string) ):
                text3 = 'NEWLINE' if i != 0 else ' '
                for j in range( 0, len(text), 32 ):
                    array.append(f'/{ text3 }/\n/ { text[j : j + 32].replace("/", "//") } /')
            extra_info_commands.append('\n'.join(array))
        
        for i in range( 0, len(parts), 100 ):
            command  = ';JVPIX3;PSET\n'
            command += '\n'.join([ f'@WINID ID {p.id} IDEND {e} ;@GO\n' for p, e in zip(parts[i:i+100], extra_info_commands[i:i+100]) ])
            command += '\n;@GO;@JVEND'
            self.send(command, 'model.set_extra_infos.xml')

    def get_modified_parts_list(self, model: Model):
        element = self.send(f';JVUVW .KIND 10 .SXDIM 3 .MODEL {model.id} .VWNO {model.wf_global.wfno} : ;@JVEND', 'model.get_modified_parts_list.xml')
        modified_ids = [ int( sx_ent.get('id') ) for sx_ent in element.xpath('./sx_ent') ]
        for part in model.parts.values():
            part.is_modified = part.id in modified_ids
        model.modified_ids = modified_ids
        return modified_ids

    def set_entities_visible(self, entities: list['Entity'], visible: bool):
        command = ';JVVISI ;@WINID ID \n' if visible else ';INVIS;OPT ;@WINID ID \n'
        command += self.join_entities(entities)
        command += '\nIDEND @GO ;@JVEND'
        self.send(command, 'model.set_entities_visible.xml')

    def get_window(self, model: Model, wfno: int=0):
        data = self.send(f';JVGPD .MODEL {model.id} .VS 0 .WF {wfno} : ;@JVEND', 'model.get_window.xml')
        for sx_pd in data.xpath('./sx_pd'):
            return Window( self.client, int(sx_pd.get('pdno')) )

    def zoom_full(self):
        self.send('@ZOOMFUL ;@JVEND', 'model.zoom_full.xml')

    def get_entities(self, model: Model, wf: WF, offset: int, num: int, visible: bool, part: bool, layer: bool, _type: bool) -> dict[int, 'Entity']:
        element = self.send(f';JVUVW .KIND 1 .SXDIM 3 .MODEL {model.id} .VWNO {wf.wfno} .NUM0 {offset} .NUM1 {num} .VISI {1 if visible else 0} .RPART {1 if part else 0} .LAYER {1 if layer else 0} .STYPE {1 if _type else 0} : ;@JVEND', 'model.get_entities.xml')

        entities: dict[int, Entity] = {}
        for sx_ent in element.xpath('./sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity

        #command = ';JVEIN2 ;@WINID ID\n'
        #command += self.join_entities( list( entities.values() ) )
        #command += '\nIDEND @GO ;@JVEND'

        #element = self.send(command, 'model.get_intent.xml')
        element = self.send(';JVEIN2\n' + '\n'.join([ f'.ID {e.id} :' for e in entities.values() ]) + '\n@GO;@JVEND', 'model.get_intent.xml')
        for sx_entinf in element.xpath('./sx_entinf'):
            _id = int( sx_entinf.get('id') )
            if _id in entities:
                entities[_id].from_inf( EntityCommand.Info(sx_entinf) )

        return entities
    
    def get_entities_in_box(self, model: Model, box: list[list[float]], part: bool, org: list[float]=[0.0, 0.0, 0.0], zvec: list[float]=[0.0, 0.0, 1.0], xvec: list[float]=[1.0, 0.0, 0.0]):
        command  = f";JVSBOX .KIND 1 .MID {model.id} .WFNO {model.wf_global.wfno} .EMODE {1 if part else 0}\n"
        command += f".MINX {box[0][0]:.8f}\n"
        command += f".MINY {box[0][1]:.8f}\n"
        command += f".MINZ {box[0][2]:.8f}\n"
        command += f".MAXX {box[1][0]:.8f}\n"
        command += f".MAXY {box[1][1]:.8f}\n"
        command += f".MAXZ {box[1][2]:.8f}\n"
        command += f".ORGX {org[0]:.8f}\n"
        command += f".ORGY {org[1]:.8f}\n"
        command += f".ORGZ {org[2]:.8f}\n"
        command += f".ZVECX {zvec[0]:.15f}\n"
        command += f".ZVECY {zvec[1]:.15f}\n"
        command += f".ZVECZ {zvec[2]:.15f}\n"
        command += f".XVECX {xvec[0]:.15f}\n"
        command += f".XVECY {xvec[1]:.15f}\n"
        command += f".XVECZ {xvec[2]:.15f}\n"
        command += ":\n"
        command += ";@JVEND"
        element = self.send(command, 'model.get_entities_in_box.xml')

        entities: dict[int, Entity] = {}
        for sx_ent in element.xpath('./sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity
        
        return entities
        
    def get_top_entities(self, model: Model, wf: WF, offset: int, num: int, visible: bool, layer: bool, _type: bool) -> dict[int, 'Entity']:
        element = self.send(f';JVUVW .KIND 2 .SXDIM 3 .MODEL {model.id} .VWNO {wf.wfno} .NUM0 {offset} .NUM1 {num} .VISI {1 if visible else 0} .LAYER {1 if layer else 0} .STYPE {1 if _type else 0} : ;@JVEND', 'model.get_entities.xml')

        entities: dict[int, Entity] = {}
        for sx_ent in element.xpath('./sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity

        element = self.send(';JVEIN2\n' + '\n'.join([ f'.ID {e.id} :' for e in entities.values() ]) + '\n@GO;@JVEND', 'model.get_intent.xml')
        for sx_entinf in element.xpath('./sx_entinf'):
            _id = int( sx_entinf.get('id') )
            if _id in entities:
                entities[_id].from_inf( EntityCommand.Info(sx_entinf) )

        return entities

    def get_entities_2d(self, model: Model, offset: int, num: int, visible: bool, part: bool, layer: bool, _type: bool, vs: VS = None) -> dict[int, 'Entity']:
        command  = f';JVUVW .KIND 1 .SXDIM 2 .MODEL {model.id} .VWNO {vs.vsno} .NUM0 {offset} .NUM1 {num} '
        command += f'.VISI {1 if visible else 0} .RPART {1 if part else 0} .LAYER {1 if layer else 0} .STYPE {1 if _type else 0} : ;@JVEND'
        data = self.send(command, 'model.get_entities.xml')
        entities: dict[int, Entity] = {}
        for sx_ent in data.findall('sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity
        return entities

    def get_materials(self, entities: list['Entity']):
        data = self.send(';JVUEN2\n' + '\n'.join([f'.KIND 0 .ENTID {entity.id} :' for entity in entities]) + '\n;@GO;@JVEND', 'model.get_materials.xml')
        materials: list[Material] = []
        for sx_inf_mat in data.xpath('./sx_inf_mat'):
            materials.append( Material(sx_inf_mat) )
        return materials

    def set_inf_material(self, material: Material, entities: list[Entity]):
        command  = f';VOL3D;SET0;SET1 @WINID ID {entities.pop(0).id}\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n@GO\n.SHORI / 0/\n'

        if len(material.name) <= 64:
            command += f'.ZAI1 /{material.name.replace('/', '//')}/\n.ZAI2 / /\n'
        else:
            array2 = self.client.split_string(material.name)
            command += f'.ZAI1 /{array2[0].replace('/', '//')}/\n.ZAI2 /{array2[1].replace('/', '//')}/\n'
        
        command += f'.KIG /{material.matid.replace('/', '//')}/\n'
        command += f'.HIJYU /{material.spe_grav:.4f}/\n'
        command += f'.DIF /{material.dif[0]:03},{material.dif[1]:03},{material.dif[2]:03},{material.dif[3]:03}/\n'
        command += f'.SPE /{material.spe[0]:03},{material.spe[1]:03},{material.spe[2]:03},{material.spe[3]:03}/\n'
        command += f'.SHI /{material.shi:03}/\n'
        command += f'.ALP /{material.alpha:03}/\n'
        command += ';GXDMY;@JVEND'

        self.send(command, 'model.set_inf_material.xml')

    def get_model_info(self, model: Model):
        entities = self.client.model.get_entities(model, model.wf_global, 0, 0, True, False, True, True)
        entity_types = list(set([ entity.type for entity in entities.values() ]))
        if not CadTypes.Entity.Type.EXTRA_INFO in entity_types:
            return [ [] for _ in range(7) ]

        info_datas: list[list[str]] = []
        for _ in range(2):
            try:
                temp_file_path = None
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    temp_file_path = f.name
                
                command  = ';PTINFO\n@GO\n..PISWAT /1/\n;PTINFO\n;PIFND\n;@GO\n'
                command += '..PISWAT /0/\n'
                command += '..UNIFLG /0/\n'
                command += f'..FILEN1 /{temp_file_path}/\n'
                command += '..FILEN2 //\n'
                command += '..PCOUNT /1/\n'
                command += '..PINDEX /0/\n'
                command += ';@JVEND'

                self.send(command, 'model.get_model_info.xml')

                with open(temp_file_path, mode='r', encoding='cp932') as f:
                    lines = f.readlines()
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

                for line in lines:
                    line = line.rstrip()
                    _match = re.fullmatch(r'\[' + model.name + r' - .*\]', line)
                    if _match and len(info_datas) < 7:
                        if len(info_datas) > 0:
                            if info_datas[-1][-1] == '':
                                info_datas[-1].pop()
                        info_datas.append([])
                    else:
                        info_datas[-1].append(line)
        
                if len(info_datas) > 0:
                    if info_datas[-1][-1] == '':
                        info_datas[-1].pop()
                
                if len(info_datas) > 6:
                    break
            except:
                if temp_file_path is not None:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)

        if len(info_datas) == 0:
            return [ [] for _ in range(7) ]
        
        return info_datas

    def set_model_info(self, titles: list[str], infos: list[str]):
        command  = ';PTINFO\n;PISET\n@GO\n..PISWAT /1/\n;PTINFO\n;PISET\n;@GO\n'
        command += '..PISWAT /0/\n'
        command += '..CODFLG /1/\n'
        command += '..TABCNT /7/\n'
        
        for info_title, info_data in zip(titles, infos):
            base64_info_title = self.client.string_to_base64string(info_title)
            base64_string = self.client.string_to_base64string(info_data)
            splitted = [ base64_string[i:i+160] for i in range(0, len(base64_string), 160) ]
            command += f'..INFTIT /{base64_info_title}/\n'
            command += f'..LINCNT /{len(splitted)}/\n'
            for d in splitted:
                command += f'..INFDAT /{d}/\n'
        
        command += ';@JVEND'

        self.send(command, 'model.set_model_info.xml')

    def get_asmplane(self, model: Model, wfno: int, plane_no: int):
        data = self.send(f';JVGAPI .MODEL {model.id} .WFNO {wfno} .PLNO {plane_no} : ;GXDMY;@JVEND', 'model.get_asmplane.xml')

    def get_parts_by_name(self, model: Model, wfno: int, partname: str):
        _partname = ' ' if partname is None else partname.replace('/', '//')
        kind = 6 if partname is None else 5
        element = self.send(f';JVUVW .KIND {kind} .SXDIM 3 .MODEL {model.id} .VWNO {wfno} .PNAME /{_partname}/ : ;GXDMY;@JVEND', 'model.get_parts_by_name.xml')
        
        parts: dict[int, Part] = {}
        for sx_ent in element.xpath('./sx_ent'):
            if int(sx_ent.get('type')) == CadTypes.Entity.Type.PART:
                part = Part(self.client, model.id, model.wf_global.wfno)
                part.from_ent( PartCommand.Data(sx_ent) )
                parts[part.id] = part

        parts3 = list(parts.values())
        for i in range(0, len(parts3), 20000):
            id_command = '\n'.join([f'.KIND 0 .ID {p.id} :' for p in parts3[i:i+10000] if p.id != 0])
            element = self.send(f';JVGPI2\n{id_command}\n;@GO ;@JVEND', 'model.get_infparts.xml')
            infos = {}
            for sx_inf_part in element.xpath('./sx_inf_part'):
                info = PartCommand.Info(sx_inf_part)
                infos[info.id] = info
        
        for i in range(0, len(parts3), 20000):
            id_command = '\n'.join([f'@WINID ID {p.id} IDEND' for p in parts3[i:i+10000] if p.id != 0])
            element = self.send(f';JVPIX3;PGET\n{id_command}\n;@GO;@JVEND', 'model.get_ex_infs.xml')
            extra_info: dict[int, dict] = {}
            texts = []
            for data in element:
                if data.tag == 'sx_str':
                    texts.append(data.text)
                if data.tag == 'sx_ent':
                    _extra_info = self.client.extra_info_to_dict(texts)
                    part_id = int( data.get('part_id') )
                    extra_info[part_id] = _extra_info
                    texts = []
        
        for part_id in parts:
            if part_id in infos:
                parts[part_id].from_inf_part( infos[part_id] )
            if part_id in extra_info:
                parts[part_id].extra_info = extra_info[part_id]
        
        parts2 = parts.copy()
        part_ids = list(parts2.keys())
        for part_id in part_ids:
            if part_id in parts2:
                sx_ents = self.send(f';JVGPI2 .KIND 2 . ID {part_id} : ;@JVEND', 'model.get_inf_entities.xml').xpath('./sx_ent')
                parts2[part_id].children= [ parts2.pop(int(sx_ent.get('id'))) for sx_ent in sx_ents ]
        
        return parts, parts2
        
    def set_search_layer(self, layers: list[int], mode: bool):
        num = 255 if layers is None else sum(1 for layer in layers if 0 < layer < 256)
        command = f'@ECHCLS {"ADD" if mode else ""}\n@ACTCLS {"ADD" if mode else "DEL"}{"\n@GO" if num > 0 else ""}\n;@JVEND'
        self.send(command, 'model.set_search_layer.xml')

    def set_display_layer(self, layers: list[int], mode: bool):
        num = 255 if layers is None else sum(1 for layer in layers if 0 < layer < 256)
        if num > 0:
            a = ' ALL' if layers is None else ''.join(f' {layer}' for layer in layers if 0 < layer < 256) + ' @GO'
            if not mode:
                b = ' ALL' if layers is None else ''.join(f' {layer}' for layer in layers if 0 < layer < 256) + ' @GO'
        command = f'@ECHCLS {"ADD" if mode else "DEL"}{a}\n@ACTCLS {"DEL" if not mode else ""}{b}\n;@JVEND'
        self.send(command, 'model.set_display_layer.xml')

    def get_extent(self, model: Model, wf: WF = None):
        if wf is None:
            wf = model.wf_global
        element = self.send(f';JVUVW .KIND 0 .SXDIM 3 .MODEL {model.id} .VWNO {wf.wfno} : ;@JVEND', 'model.get_extent.xml')
        for sx_box in element.xpath('./sx_box'):
            points = [ [ float(sx_box.get(f'{j}{i}')) for j in ['x', 'y', 'z'] ] for i in ['1', '2'] ]
            _id = int( sx_box.get('id') )
            return points

    def set_layer(self, entities: list['Entity'], layer: int):
        command  = f';CHGATR;CLAY;ELM .NLAY {layer} ;@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n@GO\n;@JVEND'
        self.send(command, 'model.set_layer.xml')

    def set_layer_name(self, layer: int, name: str):
        self.send(f';@LYRNAM ..LYRCNT /1/ ..LYR001 /{layer:03d} {name.replace("/", "//")}/ ;@JVEND', 'model.set_layer_name.xml')

    def get_draft_attribute(self):
        element = self.send(f';JVUMDL / / .KIND 3 .MODEL {-1} : ;@JVEND', 'model.get_draft_attribute.xml')
        for sx_draft_atr in element.xpath('./sx_draft_atr'):
            self.draft_attribute = DraftAttribute(sx_draft_atr)
            return self.draft_attribute
        return None

    def create_surface_mark(self, model: Model, target_object, lead_point: list[float], place_point: list[float], surface_mark_option: SurfaceMarkOption):
        point1 = []
        sxPos2 = []
        array2 = [0, 3, 1, 2]

        if (place_point != None):
            if not surface_mark_option.lead_left:
                point1[0] = place_point[0] + 1.0
                point1[1] = place_point[1]
                point1[2] = place_point[2] - 1.0
            else:
                point1[0] = place_point[0] - 1.0
                point1[1] = place_point[1]
                point1[2] = place_point[2] + 1.0
        
        ledlin, aidlin = None, None
        if type(target_object) is list:
            ledlin, aidlin = 1, 0
        elif type(target_object) is Edge or type(target_object) is Entity:
            if surface_mark_option.lead_line:
                if surface_mark_option.lead_standard:
                    ledlin = 2
                    aidlin = 1 if surface_mark_option.additionalline else 0
                else:
                    ledlin, aidlin = 0, 0
            else:
                ledlin, aidlin = 1, 0
        if ledlin is None:
            return
        
        cutting    = '' if surface_mark_option.machining_allowance is None or surface_mark_option.machining_allowance == '' else surface_mark_option.machining_allowance.replace('/', '//')
        proway     = '' if surface_mark_option.machining_process is None or surface_mark_option.machining_process == '' else surface_mark_option.machining_process.replace('/', '//')
        parameter1 = '' if surface_mark_option.parameter1 is None or surface_mark_option.parameter1 == '' else surface_mark_option.parameter1.replace('/', '//')
        parameter2 = '' if surface_mark_option.parameter2 is None or surface_mark_option.parameter2 == '' else surface_mark_option.parameter2.replace('/', '//')
        parameter3 = '' if surface_mark_option.parameter3 is None or surface_mark_option.parameter3 == '' else surface_mark_option.parameter3.replace('/', '//')
        
        command  =  ';NSMARK;DETA\n'
        command += f'..REMTYP /{surface_mark_option.remove_type.value + 1}/\n'
        command += f'..STREAK /{surface_mark_option.lay_symbol.value}/\n'
        command += f'..CIRCUM /{1 if surface_mark_option.circle_mark else 0}/\n'
        command += f'..ARWTYP /{array2[surface_mark_option.arrow_type.value]}/\n'
        command += f'..LEDLIN /{ledlin}/\n'
        command += f'..AIDLIN /{aidlin}/\n'
        command += f'..CUTING /{cutting}/\n'
        command += f'..PROWAY /{proway}/\n'
        command += f'..PARAM1 /{parameter1}/\n'
        command += f'..PARAM2 /{parameter2}/\n'
        command += f'..PARAM3 /{parameter3}/\n'
        command +=  '..VALUE1 //\n'
        command +=  '..VALUE2 //\n'
        command += f'..VALUE3 /{parameter1}/\n'
        command +=  '..VALUE4 //\n'

        if (surface_mark_option.setangle):
            command += ';@ION OPTS\n'
            command += f'.ANG {surface_mark_option.angle:.8f}\n'
        else:
            command += ';@IOFF OPTS\n'
        
        if type(target_object) is list:
            command += f'@POS @HIT X {target_object[0]:.8f} Y {target_object[1]:.8f} Z {target_object[2]:.8f},\n'
        
        if type(target_object) is Edge:
            if target_object.edge_type in [ CadTypes.Entity.Type.LPRJ, CadTypes.Entity.Type.ROT, CadTypes.Entity.Type.CONE ]:
                try:
                    p = target_object.get_on_point(lead_point, True)
                except:
                    p = lead_point
                command += f';@ENT @PICKID ID {target_object.id} PNO {target_object.prmno} ENO {target_object.edgeno} MID {target_object.csgsol} P {p[0]:.8f} {p[1]:.8f} {p[2]:.8f} IDEND\n'

                if (surface_mark_option.lead_line and surface_mark_option.lead_standard and surface_mark_option.additionalline):
                    command += f'@POS @HIT X {lead_point[0]:.8f} Y {lead_point[1]:.8f} Z {lead_point[2]:.8f},\n'
                command += f'@POS @HIT X {place_point[0]:.8f} Y {place_point[1]:.8f} Z {place_point[2]:.8f},\n'
                
                if (surface_mark_option.lead_line):
                    command += f'@POS @HIT X {point1[0]:.8f} Y {point1[1]:.8f} Z {point1[2]:.8f},\n'
            else:
                return
            
        if type(target_object) is Entity:
            if target_object.type in [
                CadTypes.Entity.Type.LINE,
                CadTypes.Entity.Type.CIR,
                CadTypes.Entity.Type.ARC,
                CadTypes.Entity.Type.ELP,
                CadTypes.Entity.Type.ELPA,
                CadTypes.Entity.Type.SPL
            ]:
                try:
                    p = target_object.get_on_point(lead_point, True)
                except:
                    p = lead_point
                command += f';@ENT @PICKID ID {target_object.id} P {p[0]:.8f} {p[1]:.8f} {p[2]:.8f} IDEND\n'
            else:
                if ((target_object.type != 27 and target_object.type != 29) or not surface_mark_option.lead_line or surface_mark_option.lead_standard):
                    return
                try:
                    sxPos2 = target_object.get_on_point(place_point, True)
                except:
                    geometry = target_object.get_geometry()
                    if target_object.type != CadTypes.Entity.Type.DARC:
                        sxPos2 = geometry.lead_point
                    else:
                        if geometry.type != CadTypes.Geometry.Type.DLIN:
                            sxPos2 = geometry.lead_point
                        else:
                            sxPos2 = geometry.lead_point
                
                window = self.get_window(model)
                if window is None:
                    return
                
                command += f'@ENT S {window.pdno} X {sxPos2[0]:.6f} Y {sxPos2[1]:.6f} Z {sxPos2[2]:.6f} ,\n'

            if (surface_mark_option.lead_line and surface_mark_option.lead_standard and surface_mark_option.additionalline):
                command += f'@POS @HIT X {lead_point[0]:.8f} Y {lead_point[1]:.8f} Z {lead_point[2]:.8f},\n'
            
            command += f'@POS @HIT X {place_point[0]:.8f} Y {place_point[1]:.8f} Z {place_point[2]:.8f},\n'
            if (surface_mark_option.lead_line):
                command += f'@POS @HIT X {point1[0]:.8f} Y {point1[1]:.8f} Z {point1[2]:.8f},\n'
        
        command += ';@JVEND'
        element = self.send(command, 'model.create_surface_mark.xml')
        for sx_ent in element.xpath('./sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            return entity
        return None

    def create_text(self, point: list[float], texts: list[str], angle=0.0, direction=True, bold=False, italic=False, font_name='ストローク', ttype=4, position=CadTypes.Entity.Text.Base.LeftBottom):
        array3 = ['', 'LT', 'CT', 'RT', 'LC', 'CC', 'RC', 'LB', 'CB', 'RB']
        array4 = ['', 'TBL1', 'TBL2', 'TBL3', 'TBLD']

        if ttype < 1 or ttype > 4:
            return
        if position.value < 1 or position.value > 9:
            return
        if font_name not in ['ストローク', 'Stroke']:
            font_name = self.get_local_font(font_name)
            if font_name is None:
                return
        if len(texts) > 20 or len(texts) == 0:
            return
        for text in texts:
            if text and len(text) > 80:
                return

        command = ';NOTE;PCHR\n'
        command += f';{'HOR' if direction else 'VER'}\n' if font_name in ['ストローク', 'Stroke'] else ';HOR\n'
        command += f';{array3[position.value]};{array4[ttype]}\n'
        command += f'.ANG {angle:.8f}\n'
        command += f'@POS @HIT X {point[0]:.8f} Y {point[1]:.8f} Z {point[2]:.8f},\n'
        command += '..CODFLG /1/\n'
        command += f'..NUMLIN /{len(texts)}LIN/\n'
        command += f'..FNTNUM /{len(texts)}/\n'

        if font_name in ['ストローク', 'Stroke']:
            command += '..FNTTYP /0/\n'
            command += '..FNTNAM /OFF/\n'
            command += f'..FNTITL /0/\n'
            command += f'..FNTBLD /0/\n'
        else:
            command += '..FNTTYP /1/\n'
            command += f'..FNTNAM /{font_name}/\n'
            command += f'..FNTITL /1/' if italic else f'..FNTITL /0/\n'
            command += f'..FNTBLD /1/' if bold else f'..FNTBLD /0/\n'

        command += '..FNTHIT /4/\n'

        for i, text in enumerate(texts):
            text = self.client.string_to_base64string(text)
            text = ' ' if len(text) == 0 else text
            command += f'..STRI{i + 1:02d} /{text}/\n'
        
        command += ';@JVEND'
        element = self.send(command, 'model.create_text.xml')
    
        entities: dict[int, Entity] = {}
        for sx_ent in element.findall('sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity

        element = self.send(';JVEIN2\n' + '\n'.join([ f'.ID {e.id} :' for e in entities.values() ]) + '\n@GO;@JVEND', 'model.get_intent.xml')
        for sx_entinf in element.xpath('./sx_entinf'):
            _id = int( sx_entinf.get('id') )
            if _id in entities:
                entities[_id].from_inf(EntityCommand.Info(sx_entinf))

        return list( entities.values() )[0]
    
    def get_local_font(self, font_name: str):
        font_name = self.client.string_to_base64string(font_name)
        element = self.send(f';JVFONT /{font_name}/ ;@JVEND', 'model.get_local_font.xml')
        text = ''
        for sx_str in element.xpath('./sx_str'):
            text += sx_str.text if sx_str.text is not None else ''
        return text

    def create_line_2d(self, p0: list[float], p1: list[float]):
        command  = ';BSLINE;PTP;LLIN;@IOFF TRN;@IOFF CAJ\n'
        command += f'@POS @HIT X {p0[0]:.8f} Y {p0[1]:.8f} Z 0.0,\n'
        command += f'@POS @HIT X {p1[0]:.8f} Y {p1[1]:.8f} Z 0.0,\n'
        command += ';@JVEND'
        self.send(command, 'model.create_line_2d.xml')

    def get_geometries(self, entities: list['Entity']):
        geometry_include_entities = [ entity for entity in entities if entity.type in CadTypes.Entity().geometry_include_types() ]
        geometries: list[BaseDimensionGeometry] = []
        element = self.send(';JVGEO2\n' + '\n'.join([ f'.ENTID {e.id} .PRMNO {e.prmno} :' for e in geometry_include_entities ]) + '\n@GO;@JVEND', 'model.get_geometries.xml')
        text_info, line_info = None, None
        for child in element:
            geometry = GeometryFactory.create(child)
            if geometry is None:
                continue
            if type(geometry) is DimensionValue:
                text_info = geometry
                continue
            if type(geometry) is DimensionLine:
                line_info = geometry
                continue
            if issubclass(type(geometry), BaseDimensionGeometry):
                geometry.text_info = text_info
                geometry.line_info = line_info
            geometry_include_entities[len(geometries)].geometry = geometry
            geometries.append(geometry)
            text_info, line_info = None, None
            
        return geometries

    def set_entities_color(self, entities: list[Entity], color: CadTypes.Color):
        command = f';COLCHG {color.value} ;@WINID VISI 6 ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n@GO\n;@JVEND'
        self.send(command, 'model.set_entities_color.xml')

    def update_2d_drawing(self, model: Model):
        self.get_window(model).set_dimension(False)
        command  = ';CRTVW;MENUCVRE;CVREEXEC\n'
        command += '..UPDFLG /1/\n'
        command += '..COMFLG /0/\n' # 0は未更新から更新、1は更新済みから更新
        command += '..LINCTR /0/\n'
        command += ';@JVEND'
        self.send(command, 'model.update_2d_drawing.xml')

    def get_print_infos(self, model: Model):
        element = self.send(f';JVGDIL .MODEL {model.id} : ;@JVEND', 'model.get_print_infos.xml')
        print_infos: list[PrintInfo] = []
        for sx_inf_print in element.xpath('./sx_inf_print'):
            print_infos.append( PrintInfo(sx_inf_print) )
        return print_infos
    
    def get_layer_names(self):
        tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        path = Path(tmp.name)
        tmp.close()

        command  = '@LYREXP\n'
        command += '.RICTL /1/\n'
        command += f'.FNAME /{path.name}/\n'
        command += f'.DIR1 /{path.parent}/\n'
        command += '.DIR2 //\n'
        command += '.DIR3 //\n'
        command += '.DIR4 //\n'
        command += '.LYRCNT /0/\n'
        command += '@SCHKPT\n'
        command += ';@JVEND'
        
        self.send(command, 'model.get_layer_names.xml')

        with open(path, mode='r', encoding='cp932') as f:
            current_layer_names = { int(r[0]) : r[1] for r in csv.reader(f) }
        
        path.unlink()
        
        return current_layer_names

    def copy_entities(
                self, model: Model, entities: list[Entity], p0: list[float], p1: list[float],
                angle_x: float, angle_y: float, angle_z: float, attribute: bool, layer: bool, group: bool, part: bool
            ):
        
        system_info = self.client.system.get_inf_sys()
        entity0 = entities[0]
        if type(entity0) is Part:
            if entity0.id == system_info.active_part.id:
                entity0.parent.set_active()
        
        command  = f';COPY5;MOV;@IOFF FEATURE;@IOFF CON;@IOFF DEL\n'
        command += f';@I{"ON" if attribute else "OFF"} ATR;@I{"ON" if layer else "OFF"} '
        command += f'LAY;@I{"ON" if group else "OFF"} GRM;@I{"ON" if part else "OFF"} CLA;@IOFF HSCH;@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n@GO\n'
        command += f'@POS;@HIT X {p0[0]:.8f} Y {p0[1]:.8f} Z {p0[2]:.8f},\n'
        command += f';@CHGTP0 ={angle_x:.14f} ={angle_y:.14f} ={angle_z:.14f}\n'
        command += f';@POS;@HIT X {p1[0]:.8f} Y {p1[1]:.8f} Z {p1[2]:.8f},\n'
        if group:
            command += '.SELECT-NUM /0/\n'
        command += ';@JVEND'

        element = self.send(command, 'model.copy_entities.xml')
        entities = []
        for sx_ent in element.xpath('./sx_ent'):
            if int(sx_ent.get('type')) == CadTypes.Entity.Type.PART:
                entity = Part(self.client, model.id, model.wf_global.wfno)
                entity.from_ent( PartCommand.Data(sx_ent) )
                entity.get_inf()
                entity.get_parent()
            else:
                entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities.append(entity)
        return entities

    def copy_entities_2d(self, model: Model, entities: list[Entity], p0: list[float], p1: list[float], attribute: bool, layer: bool, group: bool):
        if len(entities) == 0:
            return
        model.get_window()
        command  = f';COPY3;MOV;@IOFF CON;@IOFF DEL \n'
        command += f';@I{"ON" if attribute else "OFF"} ATR'
        command += f';@I{"ON" if layer else "OFF"} LAY'
        command += f';@I{"ON" if group else "OFF"} GRM\n'
        command += f';@WINID ID '
        command += self.join_entities(entities)
        command += f'\n IDEND\n@GO\n'
        command += f'@HIT S {model.window.pdno} X {p0[0]:.8f} Y {p0[1]:.8f} Z 0.00000000 ,\n'
        command += f'@HIT S {model.window.pdno} X {p1[0]:.8f} Y {p1[1]:.8f} Z 0.00000000 ,\n'
        command += ' : ;@JVEND'

        element = self.send(command, 'model.copy_entities_2d.xml')
        entities2: dict[int, Entity] = {}
        for sx_ent in element.xpath('./sx_ent'):
            entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities2[entity.id] = entity
            
        element = self.send(';JVEIN2\n' + '\n'.join([ f'.ID {e.id} :' for e in entities2.values() ]) + '\n@GO;@JVEND', 'part.get_intent.xml')
        for sx_entinf in element.xpath('./sx_entinf'):
            _id = int( sx_entinf.get('id') )
            if _id in entities2:
                entities2[_id].from_inf( EntityCommand.Info(sx_entinf) )

        return list( entities2.values() )

    def copy_entities_to_other_wf(
                self, entities: list['Entity'], model1: Model, model2: Model, p0: list[float], p1: list[float],
                angle_x: float, angle_y: float, angle_z: float, attribute: bool, layer: bool, group: bool
            ):
        window1 = self.get_window(model1)
        window2 = self.get_window(model2)
        #window2 = self.get_window(model, wf.wfno)
        
        command  = f';@WRKSCRN {window1.pdno} ;COPY5;WIN;@IOFF FEATURE;@IOFF DEL\n'
        command += f';@I{"ON" if attribute else "OFF"} ATR ;@I{"ON" if layer else "OFF"} LAY ;@I{"ON" if group else "OFF"} GRM ;@IOFF HSCH ;@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n@GO\n'
        command += f'@POS;@HIT S {window1.pdno} X {p0[0]:.8f} Y {p0[1]:.8f} Z {p0[2]:.8f},\n'
        command += f';@CHGTP0 ={angle_x:.14f} ={angle_y:.14f} ={angle_z:.14f}\n'
        command += f';@WRKSCRN {window2.pdno}\n'
        command += f';@POS;@HIT S {window2.pdno} X {p1[0]:.8f} Y {p1[1]:.8f} Z {p1[2]:.8f},\n'
        if group:
            command += '.SELECT-NUM /0/\n'
        command += ';@JVEND'

        self.send(command, 'model.copy_entities_to_other_wf.xml')

    def get_global_vs(self, model: Model):
        element = self.send(f';JVGNVW .SXDIM 2 .MODEL {model.id} .NAME /        /: ;@JVEND', 'model.get_global_vs.xml')
        for sx_vs in element.xpath('./sx_vs'):
            model.vs_global = VS(self.client)
            model.vs_global.from_data( VsCommand.Data(sx_vs) )
            return model.vs_global

    def get_search_layer(self) -> list[bool]:
        element = self.send(';JVGMSK .KIND 1 : ;@JVEND', 'model.get_search_layer.xml')
        return [ i == '1' for i in element.xpath('./sx_bool')[0].text.strip().split('\n') ]

    def get_display_layer(self) -> list[bool]:
        element = self.send(';JVGMSK .KIND 0 : ;@JVEND', 'model.get_display_layer.xml')
        return [ i == '1' for i in element.xpath('./sx_bool')[0].text.strip().split('\n') ]
    
    def get_mass(
                self, entities: list['Entity'], density=1.0, unit_type=CadTypes.Mass.Unit.MM_KG,
                is_si=True, mode_accuracy=CadTypes.Mass.Accuracy.Low, is_create_point=False, vector=[0.0, 0.0, 1.0]
            ):
        
        body_types = CadTypes.Entity().body_types()
        entities = [ entity for entity in entities if entity.type in body_types ]
        if len(entities) == 0:
            return None
        
        command  = f';VOL3D;VOL0;@ION AREA;@ION CENT;@ION MOME\n.SCL {density}\n@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n;@GO\n;@GO\n'
        command += '..NUMTYP /1/\n'
        command += f'..UNTTYP /{unit_type.value}/\n'
        command += '..PTPLAC /-5/\n'
        command += f'..KGFUNT /{2 if is_si else 1}/\n'
        command += f'..ACCRCY /{mode_accuracy.value}/\n'
        command += f'..COFGRV /{1 if is_create_point else 0}/\n'
        command += '..STRNUM /0/\n'
        command += ';@JVEND'

        data = self.send(command, 'model.get_mass.xml')
        for sx_inf_mass in data.xpath('./sx_inf_mass'):
            return Mass(sx_inf_mass)

        return None

    def print_drawing(self, print_info: PrintInfo, plotter: Plotter):
        command  = ';PLOT3;OUT;AREA;LST\n'
        command += f'.SELCNT /{1:2d}/\n'
        command += f'.AREA /{print_info.no:2d}/\n'
        command += f'.ANGLE  /{0:3d}/\n'
        command += f'.OUTCNT /{1:3d}/\n'
        command += f'.OPT1 /{0:1d}/\n'
        command += f'.OPT2 /{0:1d}/\n'
        command += f'.PLOTNO /{plotter.no}/\n'
        command += f'.HFFLG /0/\n'
        command += f'.HFTCNT /1/\n'
        command += f'.POSIT /1/\n'
        command += f'.HFTXT0 / /\n'
        command += f'.HFTXT1 / /\n'
        command += f'.HFPNTX /5.000000/\n'
        command += f'.HFPNTY /5.000000/\n'
        command += f'.FONTNM / /\n'
        command += f'.SIZE /5.000000/\n'
        command += f':\n;@JVEND'
        self.send(command, 'model.print_drawing.xml')

    def print_drawing_all_area(self, print_info: PrintInfo, plotter: Plotter):
        psize = print_info.size
        if psize != 'XY':
            if print_info.vertical:
                psize = psize + ' Lg' if self.client.get_language() != 1 else ' 縦'
            else:
                psize = psize + ' Si' if self.client.get_language() != 1 else ' 横'
        scale = 'AUTO           ' if print_info.scale < 0 else f'{print_info.scale:.8f}'

        command  = ';PLOT3;OUT;DSP;@GO\n'
        command += f'.SLIDX /{1:4d}/\n'
        command += f'.ANGLE  /{0:3d}/\n'
        command += '.FMINF / /\n'
        command += f'.PSIZE /{psize}/\n'
        command += f'.PSIZX /{print_info.width:.6f} /\n'
        command += f'.PSIZY /{print_info.height:.6f} /\n'
        command += f'.SCALE  /{scale}/\n'
        command += f'.OUTCNT /{1}/\n'
        command += f'.OPT2 /{0:1d}/\n'
        command += f'.PLOTNO /{plotter.no}/\n'
        command += '.HFFLG /0/\n'
        command += '.HFTCNT /1/\n'
        command += '.POSIT /1/\n'
        command += '.HFTXT0 / /\n'
        command += '.HFTXT1 / /\n'
        command += '.HFPNTX /5.000000/\n'
        command += '.HFPNTY /5.000000/\n'
        command += '.FONTNM / /\n'
        command += '.SIZE /5.000000/\n'
        command += ':\n;@JVEND'

        self.send(command, 'model.print_drawing_all_area.xml')

    def save(self):
        system_info = self.client.system.get_inf_sys()
        command = ';GXDMY;SAVEMD;UPD .MSG /YES/\n;@JVEND' if system_info.mod_flg == 2 else ';GXDMY;SAVEO .MSG /YES/\n;@JVEND'
        self.send(command, 'model.save.xml')

    def save_as(self, path: Path, comment: str, version: int=None, level: int=None):
        system_info = self.client.system.get_inf_sys()
        version = system_info.version if version is None else version
        level = system_info.level if level is None else level
        comment = comment.replace('/', '//') if comment is not None and comment != '' else ' '

        command  =  ';GXDMY;SAVEMD;ADD\n' if system_info.mod_flg == '2' else ';GXDMY;SAVEAS;SAVE\n'
        command += f'.FILEx /{path.stem}/\n'
        command +=  '.PRTCT /0/\n'
        command +=  '.PASSWD /        /\n'
        command += f'.DIRx /{path.parent}/\n'
        command += f'.COMMENTx /{comment}/\n'
        command += f'.SAVLVL /{version:02d}{level:02d}/\n'
        command +=  ';@JVEND'

        self.send(command, 'model.save_as.xml')

    def save_part(self, model: Model, parts: list[Part], is_modified: bool, is_child: bool):
        window = self.get_window(model)
        window.set_dimension(True)

        command = ';APLSAV;SAOVW ;@WINID ID'
        command += '\n'.join([ ' '.join([ f'{part.id}' for part in parts[i:i+5] ]) for i in range(0, len(parts), 5) ])
        command += '\nIDEND\n@GO\n'

        if is_modified:
            command += '..PTSCNT /MOD/\n'
        elif is_child:
            command += '..PTSCNT /ALL/\n'
        elif parts is None:
            command += '..PTSCNT /1/\n'
            command += f'..PTSNAM /{model.top_part.name}/\n'
        else:
            command += f'..PTSCNT /{len(parts)}/\n'
            for part in parts:
                command += f'..PTSNAM /{part.name}/\n'
        
        command += f';GXDMY;@JVEND'

        self.send(command, 'model.save_part.xml')

    def change_view_expression(self, vs_list: list[VS], layers: list[int], hidden_line: bool, sin: bool, high_accuracy: bool, pipe_center_line: bool, hole_center_line: float):
        system_info = self.client.system.get_inf_sys()
        window = system_info.active_model.get_window()

        vs_list2, extents = [], []
        for vs in vs_list:
            if vs.type in [ CadTypes.VS.Type.VIEW, CadTypes.VS.Type.LOCAL_VIEW ]:
                extent = vs.get_extent()
                global_extent = vs.map_to_global(extent)
                vs_list2.append(vs)
                extents.append(global_extent)
        
        for vs, extent in zip(vs_list2, extents):
            vs: VS
            point = self.client.calculate.find_unique_point([ e for e in extents if e != extent ], extent)
            if point is None:
                continue

            command  = ';CRTVW;MENUCVEX;MENUCVOP\n'
            command += '@HIT\n'
            command += f'S {window.pdno} X {point[0]:.8f} Y {point[1]:.8f} Z {0.0:.8f} ,\n'
            command += '..DLGSTA /1/\n' # 0:キャンセル, 1:OK
            command += '..RNDSUP /0.000000/\n' # 丸み半径
            command += '..CMFSUP /0.000000/\n' # 面取り長
            command += f'..HIDDEN /{1 if hidden_line else 0}/\n' # 隠線
            command += f'..ACCURT /{1 if high_accuracy else 0}/\n' # 高精度
            command += f'..SMOOTH /{1 if sin else 0}/\n' # 正接線
            command += f'..CENLNE /{0 if math.isclose(hole_center_line, 0, abs_tol=0.09) else 1}/\n' # 穴の中心線の有無 CENVALが0なら0
            command += '..CENSTL /1/\n' # 穴の中心線関係? 常に1?
            command += f'..CENVAL /{hole_center_line:.6f}/\n' # 穴の中心線
            if layers is not None:
                command += f'..UPLYNM /{len(layers)}/\n' # レイヤの数
                command += '\n'.join([ f'..UPLYER /{layer}/' for layer in layers ]) + '\n' # レイヤ
            command += '..TRMCLR /0/\n' # トリム
            command += f'..DSCALE /{system_info.scale:.6f}/\n' # 尺度 0.500000
            command += f'..PCNLNE /{1 if pipe_center_line else 0}/\n' # 配管中心線
            command += '..LINCTR /0/\n'  # 寸法のずれ確認表示
            command += ';@JVEND'

            self.send(command, 'model.change_view_expression.xml')

    def project_3d2d_isome(self, model: Model, point3d: list[float], point2d: list[float], option: Project3d2dOption):
        window = self.get_window(model)
        window.set_active()
        window.set_dimension(True)
        window.zoom_full()
        window.zoom_rasio(0.8)

        p2 = [ window.rect[0][0], window.rect[0][1] ]
        p3 = [ window.rect[1][0], window.rect[1][1] ]
        p4 = window.get_virtual_position(p2)
        p5 = window.get_virtual_position(p3)
        p6 = window.get_virtual_position([ p2[0] + (p3[0] - p2[0]) / 10, p2[1] + (p3[1] - p2[1]) / 10 ])
        p7 = window.get_virtual_position([ p3[0] - (p3[0] - p2[0]) / 10, p3[1] - (p3[1] - p2[1]) / 10 ])

        command  =  ';BEAD;HIDLIN\n'
        command +=  '@GO\n'
        command +=  '@GO\n'
        command +=  '.MSG /0000/\n'
        command +=  ':\n'
        command +=  '@GO\n'
        command += f'@HIT S {window.pdno} X {p4[0]:.8f} Y {p4[1]:.8f} Z {p4[2]:.8f} ,\n'
        command += f'@HIT S {window.pdno} X {p5[0]:.8f} Y {p5[1]:.8f} Z {p5[2]:.8f} ,\n'
        command += '.MSG /NO/\n'
        command += f'.SHORI /1/\n'
        command += f'.INSEN /  {1 if (option.inter_hidden_line != 0 or option.self_hidden_line != 0) else 0}/\n'
        command += f'.REDU /  {1 if option.remove_overlap else 0}/\n'
        command += f'.INTRF /  {1 if option.remove_int else 0}/\n'
        command += f'.TANG /  {option.tangent_mode}/\n'
        command += f'.ANG / {option.tangent_angle}/\n'
        command += f'.PRT /  {option.part_mode}/\n'
        command += f'.PRJWAY /  {option.hole}/\n'
        command += f'.CENTER /  {1 if option.hole_center_line else 0}/\n'
        command += f'.OSTYPE /  {option.center_offset}/\n'
        command += f'.OSTRTO /  {option.offset_ratio}/\n'
        command += f'.OSTWDH /  {option.offset_length}/\n'
        command += f'.HOLINF /  {1 if option.hole_inf else 0}/\n'
        command += f'.EXTERNAL / {option.outline}00{option.outline_style:2d}{option.outline_width:2d}/\n'
        command += f'.MUTUAL / {option.inter_hidden_line}00{option.inter_hidden_line_style:2d}{option.inter_hidden_line_width:2d}/\n'
        command += f'.SELF / {option.self_hidden_line}00{option.self_hidden_line_style:2d}{option.self_hidden_line_width:2d}/\n'
        command += f'.COPYMODE /  {1 if option.copy3d else 0}/\n'
        command += f'.SIMPLE /  1/\n'
        command += f'@HIT X {point2d[0]:.8f} Y {point2d[1]:.8f} Z {0.0:.8f} ,\n'
        command += f';GXDMY;@JVEND'
        self.send(command, 'model.project_3d2d_isome.xml', is_macro=False)
        
    def project_3d2d_isome2(self, model: Model, point3d: list[float], point2d: list[float], option: Project3d2dOption):
        window = model.get_window()
        window.zoom_full()
        window.zoom_rasio(0.8)
        p0 = window.get_virtual_position(window.rect[0])
        p1 = window.get_virtual_position(window.rect[1])
        globalVS = model.get_global_vs()
        window2 = None
        if globalVS is not None:
            window2 = globalVS.get_window()
            entities = list( globalVS.get_entities(0, 10, True, True, True, True).values() )
        
        command  = ";HIDLIN;SMDL;DVLP1\n@WIN\n"
        command += f"S {window.pdno} X {p0[0]:.8f} Y {p0[1]:.8f} Z {p0[2]:.8f} ,\n"
        command += f"S {window.pdno} X {p1[0]:.8f} Y {p1[1]:.8f} Z {p1[2]:.8f} ,\n"
        command += "@GO\n"
        command += f"@HIT S {window.pdno} X {point3d[0]:.8f} Y {point3d[1]:.8f} Z {point3d[2]:.8f} ,\n"
        command += ".MSG /0000/\n:\n"

        if window2 is None:
            p2 = window.get_virtual_position([
                window.rect[0][0] + (window.rect[1][0] - window.rect[0][0]) // 10,
                window.rect[0][1] + (window.rect[1][1] - window.rect[0][1]) // 10
            ])
            p3 = window.get_virtual_position([
                window.rect[1][0] - (window.rect[1][0] - window.rect[0][0]) // 10,
                window.rect[1][1] - (window.rect[1][1] - window.rect[0][1]) // 10
            ])
            command += f"@HIT S {window.pdno} X {p2[0]:.8f} Y {p2[1]:.8f} Z {p2[2]:.8f} ,\n"
            command += f"@HIT S {window.pdno} X {p3[0]:.8f} Y {p3[1]:.8f} Z {p3[2]:.8f} ,\n"
            system_info = self.client.system.get_inf_sys()
            pdno = system_info.pdno
        else:
            command += "@GO\n"

        if window2 is None and len(entities) == 0:
            if option.frame_file is not None:
                command += ".MSG /YES/\n"
                command += f".FILEx /{option.frame_file.stem}/\n"
                command += ".PASSWD /        /\n"
                command += f".DIRx /{option.frame_file.parent}/\n"
                command += ".SHORI /-1/\n"
                command += ";GXDMY\n"
                command += ";@JVEND\n"
                self.send(command, is_macro=True, ret_ent=False)
                if window is not None:
                    window.close()
                    window = None
                option.frame_file = None
                self.project_3d2d_isome2(model, point3d, point2d, option)
                return
            command += ".MSG /NO/\n"

        command += f".SHORI /1/", f".INSEN /  {1 if (option.inter_hidden_line != 0 or option.self_hidden_line != 0) else 0}/\n"
        command += f".REDU /  {1 if option.remove_overlap else 0}/\n"
        command += f".INTRF /  {1 if option.remove_int else 0}/\n"
        command += f".TANG /  {option.tangent_mode}/\n"
        command += f".ANG / {option.tangent_angle}/\n"
        command += f".PRT /  {option.part_mode}/\n"
        command += f".PRJWAY /  {option.hole}/\n"
        command += f".CENTER /  {1 if option.hole_center_line else 0}/\n"
        command += f".OSTYPE /  {option.center_offset}/\n"
        command += f".OSTRTO /  {option.offset_ratio}/\n"
        command += f".OSTWDH /  {option.offset_length}/\n"
        command += f".HOLINF /  {1 if option.hole_inf else 0}/\n"
        command += f".EXTERNAL / {option.outline}00{option.outline_style:02d}{option.outline_width:02d}/\n"
        command += f".MUTUAL / {option.inter_hidden_line}00{option.inter_hidden_line_style:02d}{option.inter_hidden_line_width:02d}/\n"
        command += f".SELF / {option.self_hidden_line}00{option.self_hidden_line_style:02d}{option.self_hidden_line_width:02d}/\n"
        command += f".COPYMODE /  {1 if option.copy3d else 0}/\n"
        command += ".SIMPLE /  0/\n"
        command += f"@HIT X {point2d[0]:.8f} Y {point2d[1]:.8f} Z {0.0:.8f} ,\n"
        command += ";GXDMY;@JVEND"
        self.send(command, is_macro=True, ret_ent=False, is_recieve=False)

        if window is not None:
            window.close()

        window2.set_active()

    def project_drawing(self, model: Model, point: list[float], margin=10.0):
        window = self.get_window(model)
        window.set_dimension(False)
        self.send(f';CRTVW;MENUCVST;PUT\n@HIT S        {window.pdno} X {point[0]:>18.8f} Y {point[1]:>18.8f} Z {0.0:>18.8f} ,\n;GXDMY;@JVEND', 'model.project_drawing.xml')

    def project_drawing_isometric(self, model: Model, point: list[float], margin=10.0):
        window = self.get_window(model)
        window.set_dimension(False)
        self.send(f';CRTVW;MENUCVIS\n@HIT S        {window.pdno} X {point[0]:>18.8f} Y {point[1]:>18.8f} Z {0.0:>18.8f} ,\n;GXDMY;@JVEND', 'model.project_drawing_isometric.xml')

    def set_drawing_frame(self, model: Model, frame_file_path: Path):
        folder_name = str(frame_file_path.parent)
        folders  = [ f'{folder_name[i:i+64]:<64}' for i in range(0, len(folder_name), 64) ]
        if len(folders) < 4:
            folders = folders + ['                                                                ' for _ in range(4-len(folders))]
        
        window = self.get_window(model)
        window.set_dimension(False)

        command  = ';CRTVW;MENUCVTL;CVTLEXEC\n'
        command += f'.FILE /{frame_file_path.stem}/\n'
        command += f'.PASSWD /        /\n'
        command += '\n'.join([ f'.DIR{i+1} /{folder}/' for i, folder in enumerate(folders) ])
        command += '\n;@JVEND'

        self.send(command, 'model.create_drawing_view.xml')

    def select(self, model: Model, mode: CadTypes.Select.Mode, text: str, select_go: bool, select_entity: bool, select_edge: bool, select_face: bool, select_point: bool):
        try:
            num = 0
            if select_go:
                num += 1
            if select_entity and not select_edge and not select_face:
                if mode == CadTypes.Select.Mode.Entity:
                    num += 2
                elif mode == CadTypes.Select.Mode.Part:
                    num += 4
                elif mode == CadTypes.Select.Mode.Multi:
                    num += 8
                else:
                    raise 'パラメタの内容に誤りがあります。'
            if select_edge:
                num += 16
            if select_face:
                num += 32
            if select_point:
                num += 64
            if num == 0:
                raise 'パラメタの内容に誤りがあります。'
            
            text = text if text else ' '
            if text != ' ':
                if len(text) > 72:
                    raise '文字型パラメタの文字数が規定範囲外です。'
                text = text.replace('/', '//')

            element = self.send(f';JVSEL .KIND {num} .MSG /{text}/ :', 'model.select.xml', is_macro=True)
            for sx_inf_select in element.xpath('./sx_inf_select'):
                return Selection(self.client, sx_inf_select, model.id, model.wf_global.wfno)
        except:
            print(traceback.format_exc())

        self.send(';GXDMY;@JVEND')

    def select_entities(self, model: Model, mode: CadTypes.Select.Mode, multi_init: CadTypes.Select.MultiInit):
        try:
            kind = mode if mode != CadTypes.Select.Mode.Multi else {0: 3, 2: 4}.get(multi_init.value, 2)
            element = self.send(f';JVENTS .KIND {kind} :', 'model.select_entities.xml', is_macro=True)
            
            entities = []
            for sx_ent in element.xpath('sx_ent'):
                if CadTypes.Entity().get_type( int( sx_ent.get('type') ) ) == CadTypes.Entity.Type.PART:
                    part = Part(self.client, model.id, model.wf_global.wfno)
                    part.from_ent( PartCommand.Data(sx_ent) )
                    part.get_inf()
                    part.get_parent()
                    entities.append(part)
                else:
                    entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
                    entities.append(entity)
        except:
            print(traceback.format_exc())

        self.send(';GXDMY;@JVEND')
        
        return entities

    def select2(self, mode: CadTypes.Select.Mode, text: str, select_edge: bool, select_entity: bool, select_face: bool, select_point: bool, select_go: bool):
        num = 0
        if select_go:
            num += 1
        if select_entity and not select_edge and not select_face:
            num = {
                CadTypes.Select.Mode.Entity: num + 2,
                CadTypes.Select.Mode.Part:   num + 4,
                CadTypes.Select.Mode.Multi:  num + 8
            }.get(mode, 3)
        if select_edge:
            num += 16
        if select_face:
            num += 32
        if select_point:
            num += 64
        if num == 0:
            raise Exception('パラメタの内容に誤りがあります。')
        text = text if text and len(text.encode('utf-8')) <= 72 else ' '
        text = text.replace('/', '//')
        element = self.send(f';JVSEL .KIND {num} .MSG /{text}/ : ;GXDMY;@JVEND')
        for sx_inf_select in element.xpath('./sx_inf_select'):
            return Selection(sx_inf_select)
        return None

    def export(self, filepath: Path):
        if filepath.suffix == '.html':
            command  = ';DEIOUT\n'
            command += f'..FPATH1 /{str(filepath.parent)}/\n'
            command += '..FPATH2 / /\n'
            command += '..FPATH3 / /\n'
            command += '..FPATH4 / /\n'
            command += f'..FNAME1 /{filepath.stem}/\n'
            command += '..FNAME2 / /\n'
            command += '..FNAME3 / /\n'
            command += '..FNAME4 / /\n'
            command += '..CKPROT /0/\n'
            command += '..PASWD1 / /\n'
            command += '..CKITEM /1011/\n'
            command += ';GXDMY;@JVEND'
            self.send(command)
            return
        
        elif filepath.suffix == '.ps': # FILE_TYPE_PS = 12
            return

        command  = ';GXDMY;CNVDRW;EXPORT\n'
        command += f'.FILEx /{filepath.stem}/\n'
        command += f'.DIRx /{filepath.parent}/\n'

        if filepath.suffix == '.stl':
            command += f'.FILTYP /stl {0} {0:3d}/\n'

        elif filepath.suffix == '.stlm':
            command += f'.FILTYP /stlm {0} {0:3d}/\n'

        else:
            command += f'.FILTYP /{filepath.suffix.replace(".", "")}/\n'
        
        command += f'.IGSMOD /{0}/\n;GXDMY;@JVEND'

        self.send(command)

    def free_parts(self, model: Model, parts: list['Part']):
        command = f';TD4MOD;PTFRE @WINID ID {parts.pop(0).id}\n'
        command += '\n'.join([ ' '.join([ f'{part.id}' for part in parts[i:i+5] ]) for i in range(0, len(parts), 5)])
        command += '\nIDEND\n@GO\n'
        command += '.MSG /ALL /\n' if len(parts) > 1 else '.SHORI / 0/\n'
        command += ';@JVEND'
        model.top_part.set_active()
        self.send(command, 'model.free_parts.xml')

    def copy_mirror(self, model: Model, entities: list[Entity | Part], p0: list[float], p1: list[float], p2: list[float], attribute: bool, layer: bool, group: bool, part: bool):
        command  = ';COPY5;MIR;@IOFF FEATURE;@IOFF DEL\n'
        command += f';@I{"ON" if attribute else "OFF"} ATR ;@I{"ON" if layer else "OFF"} LAY ;@I{"ON" if group else "OFF"} GRM ;@I{"ON" if part else "OFF"} CLA ;@IOFF HSCH\n'
        command += f';@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n@GO\n'
        command += f'@POS @HIT X {p0[0]:.8f} Y {p0[1]:.8f} Z {p0[2]:.8f},\n'
        command += f'@POS @HIT X {p1[0]:.8f} Y {p1[1]:.8f} Z {p1[2]:.8f},\n'
        command += f'@POS @HIT X {p2[0]:.8f} Y {p2[1]:.8f} Z {p2[2]:.8f},\n'
        if group:
            command += '.SELECT-NUM /0/\n'
        command += ';@JVEND'
        
        element = self.send(command, 'model.copy_mirror.xml')

        mirrored_parts: list[Part] = []
        for sx_ent in element.xpath('./sx_ent'):
            #if sx_ent.get('type') == '204':
            if int( sx_ent.get('type') ) == CadTypes.Entity.Type.PART:
                mirrored_part = Part(self.client, model.id, model.wf_global.wfno)
                mirrored_part.from_ent( PartCommand.Data(sx_ent) )
                mirrored_part.get_inf()
                mirrored_part.parent = entities[len(mirrored_parts)].parent
                mirrored_parts.append(mirrored_part)

        element = self.send(';JVGPI2\n' + '\n'.join([f'.KIND 0 .ID {part.id} :' for part in mirrored_parts]) + '\n;@GO ;@JVEND', 'model.get_infparts.xml')
        for child, infpart in zip(mirrored_parts, element.xpath('./sx_inf_part')):
            child.from_inf_part( PartCommand.Info(infpart) )
        
        element = self.send(';JVPIX3;PGET\n' + '\n'.join([f'@WINID ID {part.id} IDEND' for part in mirrored_parts if part.id != 0]) + '\n;@GO;@JVEND', 'model.get_ex_infs.xml')
        extra_info: dict[int] = {}
        texts = []
        for data in element:
            if data.tag == 'sx_str':
                texts.append(data.text)
            if data.tag == 'sx_ent':
                _extra_info = self.client.extra_info_to_dict(texts)
                part_id = int( data.get('part_id') )
                extra_info[part_id] = _extra_info
                texts = []
        for mirrored_part in mirrored_parts:
            mirrored_part.extra_info = extra_info.get(mirrored_part.id, {})
        
        mirrored_parts2: dict[int, Part] = { mirrored_part.id : mirrored_part for mirrored_part in mirrored_parts }

        return mirrored_parts2

    def copy_mirror2(self, model: Model, entities: list[Entity | Part], p0: list[float], v0: list[float], attribute: bool, layer: bool, group: bool, part: bool) -> dict[int, Part]:
        v0 = self.client.calculate.normalize(v0)
        if abs(v0[0]) > 1e-08 or abs(v0[1]) > 1e-08:
            v1 = [ -v0[1], v0[0], 0.0]
        else:
            v1 = [ -v0[2], 0.0, v0[0]]

        v1 = self.client.calculate.normalize(v1)
        v2 = self.client.calculate.cross(v0, v1)

        p1 = [
                p0[0] + v1[0], 
                p0[1] + v1[1], 
                p0[2] + v1[2]
            ]

        p2 = [
                p0[0] + v2[0], 
                p0[1] + v2[1], 
                p0[2] + v2[2]
            ]
        
        return self.copy_mirror(model, entities, p0, p1, p2, attribute, layer, group, part)

    def parasolid_import(self, path: Path, name: str, comment: str):
        filenames  = [ f'{path.name[i:i+64]:<64}' for i in range(0, len( str(path.name) ), 64) ]
        if len(filenames) < 4:
            filenames = filenames + ['                                                                ' for _ in range(4-len(filenames))]

        folders  = [ f'{str(path.parent)[i:i+64]:<64}' for i in range(0, len( str(path.parent) ), 64) ]
        if len(folders) < 4:
            folders = folders + ['                                                                ' for _ in range(4-len(folders))]
        
        command  = ';PSTRAN;JELM;IMP\n'
        command += '.FILENUM /  1/\n'
        command += '\n'.join([ f'.FNM{i+1} /{filename}/' for i, filename in enumerate(filenames) ]) + '\n'
        command += '\n'.join([ f'.DIR{i+1} /{folder}/' for i, folder in enumerate(folders) ]) + '\n'
        command += ': @GO\n'
        command += '.SHORI /1/\n'
        command += f'.PARTSNAME /{name}/\n'
        command += f'.COMMENT1 /{comment}/\n'
        command += '.COMMENT2 / /\n'
        command += '.CHECKMODE /  0/\n'
        command += ';@JVEND'
        self.send(command, 'model.parasolid_import.xml')

    def move_entities(self, entities: list[Entity], vector: list[float]):
        command  = f';TRANS5;MOV;@IOFF FEATURE;@IOFF HSCH;@WINID ID\n'
        command += self.join_entities(entities)
        command += f'\nIDEND\n@GO\n.DX {vector[0]:.8f} .DY {vector[1]:.8f} .DZ {vector[2]:.8f} : ;@JVEND'
        self.send(command, 'model.move_entities.xml')

    def move_entities_2d(self, entities: list[Entity], vector: list[float]):
        command  = f';TRANS3;MOV;@IOFF CON;@WINID ID\n'
        command += self.join_entities(entities)
        command += f'\nIDEND\n@GO\n.DX {vector[0]:.8f} .DY {vector[1]:.8f} : ;@JVEND'
        self.send(command, 'model.move_entities.xml')

    def set_parts_names(self, parts: list[Part], names: list[str], comments: list[str], filenames: list[str], change_all: bool = False):
        command = ''
        for i in range( len(parts) ):
            part, name, comment, filename = parts[i], names[i], comments[i], filenames[i]

            if comment is None:
                comment = part.comment

            if name is None:
                name = part.name

            if filename is None:
                filename = part.ref_model_name

            if part.id == 0:
                part.set_name(name, comment, filename)
                self.save_as(Path(part.path)/f'{name}.icd', part.comment)
                continue
            
            if part.is_external:
                if not filename:
                    filename = part.ref_model_name
                else:
                    if filename == '':
                        filename = name
                    if len(filename) > 40:
                        raise '文字型パラメタの文字数が規定範囲外です。'
                    if not self.client.check_filename(filename):
                        raise 'パラメタの内容に誤りがあります。'

            if len(name) > 40:
                raise '文字型パラメタの文字数が規定範囲外です。'
            if name.replace(' ', '').replace('\u3000', '') == '':
                raise 'パラメタの内容に誤りがあります。'
            if len(comment) > 48:
                raise '文字型パラメタの文字数が規定範囲外です。'
            
            if part.is_external:
                old_filename = part.ref_model_name.replace('/', '//')
                new_filename = filename.replace('/', '//')
            else:
                old_filename = ' '
                new_filename = ' '

            comment = comment if comment else ''
            comment = comment.replace('/', '//')

            command += ';TD4MOD;PTINF;PTNAM;PARTS;@IOFF ;ALLLEV\n'
            command += f'@PICKID ID {part.id} IDEND\n'
            command += '@GO\n'
            command += '.SHORI /0/\n'
            command += f'.CHECKMODE /{1 if change_all else 0}/\n'
            command += '.COUNT /1/\n'
            command += f'.OLDPNAME /{part.name.replace('/', '//')}/\n'
            command += f'.OLDMNAME /{old_filename}/\n'
            command += f'.NEWPNAME /{name.replace('/', '//')}/\n'

            if len(comment) <= 40:
                command += f'.NEWCMNTx /{comment}/\n'
            else:
                flag = False
                splitted = self.client.split_string(comment)
                if splitted[0].endswith('/'):
                    num3 = len(splitted[0]) - len(splitted[0].replace('/', ''))
                    if num3 % 2 == 1:
                        flag = True
                if flag:
                    command += f'.NEWCMNT1 /{splitted[0][:-1]}/\n'
                    command += f'.NEWCMNT2 /{splitted[1]}/\n'
                else:
                    command += f'.NEWCMNTx /{comment}/\n'

            command += f'.NEWMNAME /{new_filename}/\n'

            if change_all:
                command += '.SHORI /0/\n'

        command += ';GXDMY;@JVEND'
        self.send(command, 'model.set_parts_names.xml')

        for part in parts:
            part.get_inf()

    def reload_parts(self, parts: list[Part]):
        parts_command = ''
        count = 0
        for part in parts:
            parents = [part.parent]
            while parents[-1] is not None:
                parents.append(parents[-1].parent)
            parents = parents[:-1][::-1]
            parent_names = '\\'.join([ parent.name for parent in parents ])
            parts_command += f'.SELCL /\\{parent_names}/\n'
            parts_command += f'.SELNM /{part.name}/\n'
            count += 1
            break
        
        if count == 0:
            return
        
        self.send(f';TD4MOD ;PTSAI @ENT @PTWIN\n.SELCNT /{count}/\n.SELPZ /0/\n{parts_command}@GO\n.MSG /ALL /\n;GXDMY;@JVEND', 'model.reload_parts.xml')

    def set_scale(self, scale: float):
        self.send(f';@VSCALE {scale:.6f} ;@JVEND', 'model.set_scale.xml', is_macro=True, ret_ent=False, is_recieve=False)

    def set_print_area(self, model: Model, margin=20.0):
        paper_size = None
        window = self.get_window(model)
        window.set_dimension(False)
        self.set_scale(1.0)
        window.zoom_full()

        e = model.vs_global.get_extent()
        for paper_data in self.default_papers:
            size, paper_w, paper_h, scale = paper_data[0], paper_data[1], paper_data[2], paper_data[3]
            model_w, model_h = (e[1][0] - e[0][0] + margin * 2) * scale, (e[1][1] - e[0][1] + margin * 2) * scale
            if model_w < paper_w and model_h < paper_h:
                paper_size = size
                break
        
        if paper_size is None:
            return None, None, None
        
        dimension_types = CadTypes.Entity().dimension_types()

        self.set_scale(scale)

        for vs in model.vs_list:
            vs.set_active()
            for vs in model.vs_list:
                dimensions = [ entity for entity in vs.get_entities(0, 0, True, True, True, True).values() if entity.type in dimension_types ]
                if len(dimensions) > 0:
                    self.set_present_scale(dimensions)

        window.zoom_full()
        e = model.vs_global.get_extent()
        window.zoom_full()
        
        left_bottom = [e[0][0] - margin, e[0][1] - margin]
        print_info = self.set_inf_print_size(left_bottom, paper_size, paper_size, False, -1.0, paper_w, paper_h)

        return paper_size, scale, print_info
    
    def set_print_area_all(self, model: Model):
        window = self.get_window(model)
        window.set_dimension(False)
        extents = {}
        for vs in model.vs_list:
            extents[vs.type] = ( vs, vs.map_to_global( vs.get_extent() ) )

    def set_present_scale(self, entities: list[Entity]):
        command  = ';CDMLOC;ASIZ ;@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND @GO ;@JVEND'
        self.send(command, 'model.set_present_scale.xml')

    def set_inf_print_size(self, point: list[float], drawing_size: str, paper_size: str, vertical: bool, scale: float, size_x: float=0.0, size_y: float=0.0):
        drawing_width, drawing_height = {'A0':(1189.0,841.0),'A1':(841.0,594.0),'A2':(594.0,420.0),'A3':(420.0,297.0),'A4':(297.0,210.0)}.get(drawing_size, (0, 0))
        paper_width, paper_height = {
            'A0': (1189.0, 841.0), 'A1': (841.0, 594.0), 'A2': ( 594.0, 420.0), 'A3': (420.0, 297.0), 'A4': (297.0, 210.0),
            'A5': ( 210.0, 148.0), 'A6': (148.0, 105.0), 'B1': (1030.0, 728.0), 'B2': (728.0, 515.0), 'B3': (515.0, 364.0),
            'B4': ( 364.0, 257.0), 'B5': (257.0, 182.0), 'B6': ( 182.0, 128.0), 'B7': (128.0, 91.0),
            'A0ロール': (1189.0, 841.0), 'A0Rol': (1189.0, 841.0), 'A1ロール': (839.8, 594.0),'XY': (size_x, size_y)
        }.get(paper_size)
        
        if paper_size in ['A0ロール', 'A0Rol', 'A1ロール', 'A1Rol', 'XY', '']:
            paper_size = 'XY   '
            scale = paper_height / drawing_height if paper_size != "XY" else paper_height / drawing_height if not vertical else paper_width / drawing_width
        
        if paper_size in ["XY", "A0ロール", "A0Rol", "A1ロール", "A1Rol"]:
            if vertical:
                paper_width, paper_height = paper_height, paper_width
                paper_size = ' Lg' if self.client.get_language() != 1 else ' 縦'
            else:
                paper_size = ' Si' if self.client.get_language() != 1 else ' 横'

        if not scale <= 0.0:
            if paper_size in ["A0ロール", "A0Rol", "A1ロール", "A1Rol"]:
                slidx = 1
            else:
                slidx = 2
        else:
            if math.isclose(scale, 1.0, abs_tol=0.0001):
                slidx = 0
            else:
                slidx = 2

        command  = ';PLOT3;INF;SET;FIX\n'
        command += f';SZ{drawing_size}\n'
        command += f'{";VER" if vertical else ";HOR"}\n'
        command += f'@POS @HIT X {point[0]:.8f} Y {point[1]:.8f} Z 0.0,\n'
        command += f'.SLIDX /{slidx:04d}/\n'
        command += f'.ANGLE /000/\n'
        command += f'.FMINF / /\n'
        command += f'.PSIZE /{paper_size}/\n'
        command += f'.PSIZX /{paper_width:.6f}/\n'
        command += f'.PSIZY /{paper_height:.6f}/\n'
        command += f'.SCALE /{scale:.6f}/\n'
        command += f':\n'
        command += f';GXDMY;@JVEND'
        element = self.send(command, 'model.set_inf_print_size.xml')

    def get_line_attributes(self, entities: list[Entity]):
        element = self.send(';GXDMY;JVUEN2\n' + '\n'.join([ f'.KIND 1 .ENTID {e.id} .PRMNO {0} :' for e in entities ]) + '\n@GO;@JVEND', 'model.get_line_attributes.xml')
        line_attributes: list[LineAttribute] = []
        for sx_int in element.xpath('./sx_int'):
            line_attributes.append( LineAttribute(sx_int) )
        return line_attributes

    def set_coordinate(self, model: Model, origin: list[float], x_vector: list[float], z_vector: list[float]):
        command  = f';JVSMT2\n.ORGX {origin[0]:.8f}\n.ORGY {origin[1]:.8f}\n.ORGZ {origin[2]:.8f}\n'
        command += f'.KIND {3}\n.MID {model.id}\n.WFNO {model.wf_global.wfno}\n'
        command += f'.ZVECX {z_vector[0]:.16f}\n.ZVECY {z_vector[1]:.16f}\n.ZVECZ {z_vector[2]:.16f}\n'
        command += f'.XVECX {x_vector[0]:.16f}\n.XVECY {x_vector[1]:.16f}\n.XVECZ {x_vector[2]:.16f}\n'
        command += ':\n;GXDMY;@JVEND'
        self.send(command, 'model.set_coordinate.xml')

    def get_extent_list(self, entities: list[Entity]):
        element = self.send(';JVBOX2\n' + '\n'.join([f'.ID {e.id} :' for e in entities]) + '\n;@GO;@JVEND', 'get_extent_list.xml')
        boxes: list[list[float]] = []
        for sx_box in element.xpath('./sx_box'):
            points = [ [ float(sx_box.get(f'{j}{i}')) for j in ['x', 'y', 'z'] ] for i in ['1', '2'] ]
            _id = int( sx_box.get('id') )
            boxes.append(points)
        return boxes

    def set_entities_to_global_vs(self, model: Model, entities: list[Entity]):
        entities2 = {}
        for entity in entities:
            entities2[entity.vswfno] = entities2.get(entity.vswfno, []) + [entity]
        for entities3 in entities2.values():
            command  =  ';TDCHGV;@WINID ID\n'
            command +=  '\n'.join([ ' '.join([ str(e.id) for e in entities3[i:i+5] ]) for i in range(0, len(entities3), 5) ])
            command +=  '\nIDEND\n;@GO\n'
            command += f'S {model.window.pdno} X 0.0 Y 0.0 Z 0.0,\n'
            command +=  ';@GO;GXDMY;@JVEND'
            self.send(command, 'model.set_entities_to_global_vs.xml')

    def set_entities_to_vs(self, model: Model, vs: VS, entities: list[Entity]):
        entities2 = {}
        for entity in entities:
            entities2[entity.vswfno] = entities2.get(entity.vswfno, []) + [entity]

        model.vs_global.set_active()
        
        point = [0.113 * vs.vsno, 0.137 * vs.vsno]
        point2 = vs.convert_point(point, True)

        for entities3 in entities2.values():
            command  =  ';TDCHGV;@WINID ID\n'
            command +=  '\n'.join([ ' '.join([ str(e.id) for e in entities3[i:i+5] ]) for i in range(0, len(entities3), 5) ])
            command +=  '\nIDEND\n;@GO\n'
            command += f'S {model.window.pdno} X {point2[0]:.8f} Y {point2[1]:.8f} Z 0.0 ,\n'
            command +=  ';@GO;GXDMY;@JVEND'
            self.send(command, 'model.set_entities_to_global_vs.xml')

    def create_vs_local(self, name: str, point: list[float], angle: float, scale: float):
        command  = f';VWLOCL;LCLSET .LCLNAM /{name.replace("/", "//")}/ .LCLANG {angle} .LCLSCL /{scale}/ : '
        command += f';@POS @HIT X {point[0]:.8f} Y {point[1]:.8f} Z 0.0, ;@JVEND'
        element = self.send(command, 'model.create_vs_local.xml')

    def take_in_parts(self, parts: list[Part], all_level: bool):
        command  = f';TD4MOD;OUTCHG\n@I{"ON" if all_level else "OFF"};ALLLEV ;@WINID ID\n'
        command += '\n'.join([ ' '.join([ f'{part.id}' for part in parts[i:i+5] ]) for i in range(0, len(parts), 5) ])
        command += f'\nIDEND\n;@GO\n'
        command += '.MSG /ALL /\n'
        command += ';GXDMY;@JVEND'
        self.send(command, 'model.take_in.xml')
        #self.get_inf(part)

    def show_only_parts(self, parts: list[Part]):
        command  = ';INVIS;@WINID ID\n'
        command += '\n'.join([ ' '.join([ f'{part.id}' for part in parts[i:i+5] ]) for i in range(0, len(parts), 5) ])
        command += f'\nIDEND\n;@GO\n'
        command += ';GXDMY;@JVEND'
        self.send(command, 'model.show_only_parts.xml')

    def echo(self, entities: list[Entity]):
        return self.send(f';JVUEN3 .KIND 1 : @WINID ID {self.join_entities(entities)} IDEND @GO;@JVEND', 'part.echo.xml')


class PartCommand(BaseCommand):

    class Data:
        def __init__(self, element: etree._Element) -> None:
            self.type       = int( element.get('type') )    if element is not None else None
            self.id         = int( element.get('id') )      if element is not None else None
            self.prmno      = int( element.get('prmno') )   if element is not None else None
            self.kind       = int( element.get('kind') )    if element is not None else None
            self.part_id    = int( element.get('part_id') ) if element is not None else None
            self.is3d: bool = element.get('dim') != '0'     if element is not None else None
    
    class Info:
        def __init__(self, element: etree._Element) -> None:
            self.name: str           = element.get('name')                if element is not None else None
            self.comment: str        = element.get('comment')             if element is not None else None
            self.is_mirror: bool     = element.get('is_mirror') != '0'    if element is not None else None
            self.is_external: bool   = element.get('is_external') != '0'  if element is not None else None
            self.is_read_only: bool  = element.get('is_read_only') != '0' if element is not None else None
            self.is_unloaded: bool   = element.get('is_dummy') != '0'     if element is not None else None
            #self.is_modified: bool   = element.get('edit') == '1'         if element is not None else None
            self.is_modified: bool   = False
            self.ref_model_name: str = element.get('ref_model_name')      if element is not None else None
            self.path: str           = element.get('path')                if element is not None else None
            self.date                = int( element.get('date') )         if element is not None else None
            self.time                = int( element.get('time') )         if element is not None else None
            self.is_active: bool     = element.get('is_active') != '0'    if element is not None else None
            self.has_grp: bool       = element.get('has_grp') != '0'      if element is not None else None
            self.id                  = int( element.get('id') )           if element is not None else None
            
            self.origin = [
                float(element.get('orgx', 0.0)),
                float(element.get('orgy', 0.0)),
                float(element.get('orgz', 0.0))
            ]

            self.matrix = [
                [ float(element.get('xvecx', 0.0)), float(element.get('xvecy', 0.0)), float(element.get('xvecz', 0.0)) ],
                [],
                [ float(element.get('zvecx', 0.0)), float(element.get('zvecy', 0.0)), float(element.get('zvecz', 0.0)) ]
            ]

            self.matrix[1] = [
                self.matrix[2][1] * self.matrix[0][2] - self.matrix[2][2] * self.matrix[0][1],
                self.matrix[2][2] * self.matrix[0][0] - self.matrix[2][0] * self.matrix[0][2],
                self.matrix[2][0] * self.matrix[0][1] - self.matrix[2][1] * self.matrix[0][0]
            ]

    def part_data(self, element: etree._Element):
        return PartCommand.Data(element)
    
    def part_info(self, element: etree._Element):
        return PartCommand.Info(element)

    def append_entities(self, part: Part, entities: list[Part]):
        part_entities = self.get_entities(part)
        not_include_entities = [ e for e in entities if not e.id in part_entities ]

        if len(not_include_entities) == 0:
            return

        if part.id == 0:
            command  = ';TD4MOD\n;@WINID ID\n'
            command += self.join_entities(not_include_entities)
            command += '\nIDEND @GO\n@GO\n.MSG /ALL /\n;GXDMY;@JVEND'
        else:
            command  =  ';TD4MOD;PTMOV;PTADD\n;@WINID ID\n'
            command += self.join_entities(not_include_entities)
            command +=  '\nIDEND @GO\n'
            command += f'@PICKID ID {part.id} IDEND\n'
            command +=  '.SHORI / 0/\n'
            command +=  '.SHORI / 0/\n'
            command +=  '.SHORI / 0/\n'
            command +=  '.SHORI / 0/\n'
            command +=  '.MSG /ALL /\n'
            command +=  ';GXDMY;@JVEND'
        
        self.send(command, 'part.append_entities.xml')

    def append_parts(self, parent0: Part, parts: list[Part]):
        command = ';TD4MOD;PTMOV;PTPMV\n'
        parent1: dict[Part, list[int]] = {}
        for part1 in parts:
            index = part1.parent.children.index(part1)
            if part1.parent in parent1:
                parent1[part1.parent].append(index)
            else:
                parent1[part1.parent] = [index]
            command += f'@PICKID ID {part1.id} IDEND\n'
        command +=  ';@GO\n'
        if parent0.id == 0:
            command += f'@GO\n'
        else:
            command += f'@PICKID ID {parent0.id} IDEND\n'
        command +=  '.SHORI / 0/'
        command +=  '.SHORI / 0/'
        command +=  ';GXDMY;@JVEND'
        self.send(command, 'part.append_parts.xml', is_recieve=False)
        for part2, indexes in parent1.items():
            for index in sorted(indexes)[::-1]:
                part3 = part2.children.pop(index)
                part3.parent = parent0
                parent0.children.append(part3)
    
    def create_child(self, parent: Part, name: str, comment: str):
        self.set_active(parent)
        data = self.send(';TD5NEW @GO : ;@JVEND\n' if parent.id == 0 else f';TD5NEW @PICKID ID {parent.id} IDEND : ;GXDMY;@JVEND', 'part.create_child.xml')
        sx_ent = data.find('sx_ent')
        part = Part(self.client)
        part.parent = parent
        part.from_ent( PartCommand.Data(sx_ent) )
        part.get_inf()
        parent.children.append(part)
        part.set_name(name, comment, '')
        return part
    
    def create_children(self, parent: Part, name: str, comment: str, quantity: int):
        self.set_active(parent)
        if parent.id == 0:
            command = ';TD5NEW\n' + '\n'.join(['@GO : ' for _ in range(quantity)]) + '\n;@JVEND'
        else:
            command = ';TD5NEW\n' + '\n'.join([f'@PICKID ID {parent.id} IDEND :' for _ in range(quantity)]) + '\n;@JVEND'
        data = self.send(command, 'part.create_children.xml')
        parts = []
        for sx_ent in data.xpath('./sx_ent'):
            part = Part(self.client)
            part.parent = parent
            part.from_ent( PartCommand.Data(sx_ent) )
            part.get_inf()
            parent.children.append(part)
            part.set_name(name, comment, '')
            parts.append(part)
        return parts

    def delete(self, part: Part):
        self.send(f';ERASE;OPT;@IOFF FEATURE ;@IOFF HSCH @WINID ID {part.id} IDEND\n;@GO\n.MSG /ALL /\n.SHORI / 0/\n;GXDMY;@JVEND', 'part.delete.xml')

    def free(self, part: Part):
        self.send(f';TD4MOD;PTFRE @PICKID ID {part.id} IDEND ;@GO\n.SHORI / 0/\n;GXDMY;@JVEND', 'part.free.xml')

    def get_inf(self, part: Part):
        if part.id == 0:
            return
        element = self.send(f';JVGPID .KIND 0 .ID {part.id} .MODEL 1 : ;@JVEND', 'part.get_inf.xml')
        for sx_inf_part in element.xpath('sx_inf_part'):
            part.from_inf_part( PartCommand.Info(sx_inf_part) )
            return

    def get_extra_info(self, part: Part):
        element = self.send(f';JVPIX;PGET @WINID ID {part.model_id if part.id == 0 else part.id} IDEND ;@JVEND', 'part.get_ex_inf.xml')
        part.extra_info = self.client.extra_info_to_dict([ i.text for i in element.xpath('./sx_str') ])
        return part.extra_info

    def get_entities(self, part: Part):
        if part.id == 0:
            data = self.send(f';JVUVW .KIND 2 .SXDIM 3 .MODEL {part.model_id} .VWNO {part.wfno} .NUM0 0 .NUM1 0 .VISI 1 .LAYER 1 .STYPE 1 : ;@JVEND', 'part.get_top_entities.xml')
        else:
            data = self.send(f';GXDMY;JVUENT .KIND 2 .ENTID {part.id} : ;@JVEND', 'part.get_entities.xml')

        entities: dict[int, Entity] = {}
        for sx_ent in data.findall('sx_ent'):
            entity: Entity = EntityFactory.create(self.client, EntityCommand.Data(sx_ent))
            entities[entity.id] = entity
        
        element = self.send(';JVEIN2\n' + '\n'.join([ f'.ID {e.id} :' for e in entities.values() ]) + '\n@GO;@JVEND', 'part.get_intent.xml')
        for sx_entinf in element.xpath('./sx_entinf'):
            _id = int( sx_entinf.get('id') )
            if _id in entities:
                entities[_id].from_inf( EntityCommand.Info(sx_entinf) )

        part.entities = {}
        for _id in entities:
            part.entities[_id] = entities[_id]
        
        return part.entities
    
    def get_edges(self, entities: list[Entity]):
        edges = []
        _entities = { entity.id : entity for entity in entities }
        element = self.send('\n'.join([f';JVEDGS .ENTID {entity.id} : ' for entity in entities ]) + '\n;@JVEND', 'part.get_edges.xml')
        for sx_edge in element.findall('sx_edge'):
            edge = Edge(self.client)
            edge.from_edge( EdgeCommand.Info(sx_edge) )
            _entities[edge.id].edges.append(edge)
            edges.append(edge)
        return edges
    
    def get_edges_geometries(self, edges: list[Edge]):
        geometries: list[BaseGeometry] = []
        element = self.send(';JVGEO2\n' + '\n'.join([f'.ENTID {e.id} .PRMNO {e.prmno} .EDGENO {e.edgeno} .CSGSOL {e.csgsol} :' for e in edges]) + '\n;@GO;@JVEND', 'part.get_edges_geometries.xml')
        for child in element:
            geometry = GeometryFactory.create(child)
            geometries.append(geometry)
        return geometries

    def get_geometries(self, entities: list[Entity]):
        geometries = []
        element = self.send(';JVGEO2\n' + '\n'.join([ f'.ENTID {e.id} .PRMNO {e.prmno} :' for e in entities ]) + '\n@GO;@JVEND', 'part.get_geometries.xml')
        for child in element:
            geometry = GeometryFactory.create(child)
            if geometry is not None:
                geometries.append(geometry)
        return geometries

    def get_model_info(self, part: Part):
        parent, indexes, tree = part, [], []
        for _ in range(100):
            if parent.parent is None:
                break
            tree.append(parent.name)
            child_names = [ child.name for child in parent.parent.children ]
            if child_names.count(parent.name) > 1:
                indexes.append( child_names.index(parent.name) )
            else:
                indexes.append(None)
            parent = parent.parent
        indexes = indexes[::-1]
        tree = tree[::-1]

        data = []
        for i, (index, partname) in enumerate( zip(indexes, tree) ):
            if index is not None:
                data.append(f'.SELSN /{index}/')
            if i == 0:
                data.append(f'.SELNM /{partname}/')
            else:
                data.append(f'.SELCL /{partname}/')
        
        command  = f';PTINFO @ENT @PTPIC @PICKID ID {part.id} IDEND @GO\n'
        #command  = [';PTINFO @ENT @PTPIC']
        #command += ['.SELPZ /0/']
        #command += ['.SELCL /\/']
        #command += data
        #command += ['..PISWAT /1/']
        #command += [';PTINFO ;PIFND ;@GO']
        command += '..PISWAT /0/\n'
        command += '..UNIFLG /0/\n'
        command += '..FILEN1 /C:\\Temp\\temp.txt/\n'
        command += '..FILEN2 //\n'
        command += '..PCOUNT /1/\n'
        command += '..PINDEX /0/\n'
        command += ';GXDMY;@JVEND'
        
        self.send(command, 'part.get_model_info.xml')

    def get_children(self, part: Part):
        part.children = []
        if part.id == 0:
            element = self.send(f';JVGPID .KIND 3 .ID 0 .MODEL {part.model_id} .WFNO {part.wfno} : ;@JVEND', 'part.get_children.xml')
        else:
            element = self.send(f';JVGPID .KIND 2 .ID {part.id} : ;@JVEND', 'part.get_children.xml')
        for sx_ent in element.findall('sx_ent'):
            part2 = Part(self.client, part.model_id, part.wfno)
            part2.from_ent( PartCommand.Data(sx_ent) )
            part2.parent = part
            part.children.append(part2)
        
        infparts = self.send(';JVGPI2\n' + '\n'.join([f'.KIND 0 .ID {child.id} :' for child in part.children]) + '\n;@GO ;@JVEND', 'part.get_infparts.xml')
        for child, infpart in zip(part.children, infparts.xpath('./sx_inf_part')):
            child.from_inf_part( PartCommand.Info(infpart) )
        
        command = ';JVPIX3;PGET\n'
        command += '\n'.join([f'@WINID ID {child.id} IDEND' for child in part.children])
        command += '\n;@GO;@JVEND'

        element = self.send(command, 'part.get_extra_infos.xml')
        if len(element) > 0:
            extra_info: dict[int] = {}
            texts = []
            for data in element:
                if data.tag == 'sx_str':
                    texts.append(data.text)
                if data.tag == 'sx_ent':
                    _extra_info = self.client.extra_info_to_dict(texts)
                    part_id = int( data.get('part_id') )
                    extra_info[part_id] = _extra_info
                    texts = []
            for child in part.children:
                child.extra_info = extra_info.get(child.id, {})
        
        parts = { child.id : child for child in part.children }

        return parts
    
    def get_parent(self, part: Part):
        element = self.send(f';JVGPID .KIND 1 .ID {part.id} : ;@JVEND', 'part.get_parent.xml')
        for sx_ent in element.xpath('./sx_ent'):
            parent = Part(self.client, part.model_id, part.wfno)
            parent.from_ent( PartCommand.Data(sx_ent) )
            parent.get_inf()
            return parent
        parent = Part(self.client, part.model_id, part.wfno)
        element = self.send(f';JVGMIF .NAME {part.model_id} : ;GXDMY;@JVEND', 'part.get_inf_model.xml')
        for sx_inf_model in element.xpath('./sx_inf_model'):
            parent.path: str          = sx_inf_model.get('path', '')
            parent.name: str          = sx_inf_model.get('name', '')
            parent.comment: str       = sx_inf_model.get('comment', '')
            parent.is_read_only: bool = sx_inf_model.get('is_read_only') != '0'
            parent.is_modified: bool  = sx_inf_model.get('is_modify') == '1'
        return parent

    def get_tree(self, part: Part):
        parts: dict[int, Part] = {}

        if part.id == 0:
            element = self.send(f';JVGPID .KIND 5 .MODEL {part.model_id} .WFNO {part.wfno} : ;@JVEND', 'part.get_tree.xml')
        else:
            element = self.send(f';JVGPID .KIND 5 .ID {part.id} : ;@JVEND', 'part.get_tree.xml')
        
        part.children = []

        stack = [ (part, i) for i in element.xpath('./sx_inf_parttree') ]
        while stack:
            parent, sx_inf_parttree = stack.pop()
            
            part = Part(self.client, part.model_id, part.wfno)
            part.parent = parent

            for sx_ent in sx_inf_parttree.xpath('./sx_ent'):
                part.from_ent( PartCommand.Data(sx_ent) )
                break

            for sx_inf_part in sx_inf_parttree.xpath('./sx_inf_part'):
                part.from_inf_part( PartCommand.Info(sx_inf_part) )
                break

            sx_str_list = sx_inf_parttree.xpath('./sx_str')
            if len(sx_str_list) > 0:
                part.extra_info = self.client.extra_info_to_dict([i.text for i in sx_str_list])

            parts[part.id] = part
            parent.children.append(part)

            stack.extend([ (part, i) for i in sx_inf_parttree.xpath('./sx_inf_parttree') ])

        return parts

    def set_name(self, part: Part, partname: str, comment: str, filename: str, change_all: bool = False):
        new_partname = partname.replace('/', '//')

        if part.is_external:
            if filename is None:
                filename = part.ref_model_name
            else:
                if filename == '':
                    name = part.name if name == '' or name is None else name
                    name = name.replace(' ', '').replace('\u3000', '')
                    filename = name
                if len(filename) > 40:
                    return
                if not self.client.check_filename(filename):
                    return
            new_filename = filename.replace('/', '//')
        else:
            new_filename = ' '
        
        if comment is None:
            comment = part.comment
        if len( comment.encode('utf-16le') ) > 48:
            return
        
        old_partname = part.name.replace('/', '//')
        old_partname = ' ' if old_partname == '' else old_partname
        
        old_filename = part.ref_model_name if part.is_external else ' '
        old_filename = old_filename.replace('/', '//')

        new_comment = '' if comment is None else comment.replace('/', '//')
        comment_command = f'.NEWCMNTx /{new_comment}/\n'
        if len( new_comment.encode('utf-16le') ) > 40:
            new_comments = [new_comment[:40], new_comment[40:]]
            if new_comments[0].endswith('/'):
                count = len(new_comments[0]) - len(new_comments[0].replace('/', ''))
                if count % 2 == 1:
                    comment_command  = f'.NEWCMNT1 /{new_comments[0][:-1]}/\n'
                    comment_command += f'.NEWCMNT2 /{new_comments[1]}/\n'

        command  = ';TD4MOD;PTINF;PTNAM;PARTS;@IOFF ;ALLLEV\n'
        if part.id != 0:
            command += f'@PICKID ID {part.id} IDEND\n'
        command += '@GO\n'
        command += '.SHORI /0/\n'
        command += f'.CHECKMODE /{1 if change_all and part.id != 0 else 0}/\n'
        command += '.COUNT /1/\n'
        command += f'.OLDPNAME /{old_partname}/\n'
        command += f'.OLDMNAME /{old_filename}/\n'
        command += f'.NEWPNAME /{new_partname}/\n'
        command += comment_command
        command += f'.NEWMNAME /{new_filename}/\n'
        if change_all and part.id != 0:
            command += '.SHORI /0/\n'
        command += ';GXDMY;@JVEND'

        self.send(command, 'part.set_name.xml')
        
        part.name = partname
        part.comment = comment if comment is not None else ''
        part.ref_model_name = filename if filename is not None else ''

    def set_access(self, part: Part, is_read_only: bool):
        self.get_inf(part)
        if not part.is_external:
            return
        if not part.is_read_only:
            return
        if part.id != 0:
            command  = ';TD4MOD;PTACC\n'
            command += ';TARLS;TAFLLW\n' if is_read_only else ';TAGET\n'
            command += f'@PICKID ID {part.id} IDEND @GO\n'
            command += f'.SHORI / {"0" if is_read_only else "2"}/\n;GXDMY;@JVEND'
            self.send(command, 'part.set_access.xml')

    def set_active(self, part: Part):
        self.get_inf(part)
        if part.is_active:
            return
        if part.id == 0:

            active_part_id = None
            element = self.send(';JVGSIF;GXDMY;@JVEND', 'part.get_inf_sys.xml')
            sx_inf_sys = element.xpath('./sx_inf_sys')
            if sx_inf_sys:
                sx_inf_sys: etree._Element = sx_inf_sys[0]
                sx_ent = sx_inf_sys.xpath('./sx_ent')
                if len(sx_ent) > 0:
                    active_part_id = int( sx_ent[0].get('id') )
            if active_part_id is None:
                return
            
            command  = f';TD4MOD;PTINP @GO ;@JVEND'
        else:
            command  = f';TD4MOD;PTINP @PICKID ID {part.id} IDEND ;GXDMY;@JVEND'
        self.send(command, 'part.set_active.xml')

    def set_extra_info(self, part: Part, extra_info: dict[str, str]):
        texts = re.split('[\n,\0]', self.client.extra_info_to_base64string(extra_info))
        array = ''
        for i, text in enumerate(texts):
            text3 = 'NEWLINE' if i != 0 else ' '
            for j in range( int( len(text) / 32 ) + 1 ):
                text2 = text[j * 32 : (j + 1) * 32].replace('/', '//')
                array += f'/{text3}/\n/ {text2} /\n'

        if part.id == 0:
            command = f';JVPIX;PSET .MODEL {part.model_id} .WF {part.wfno} : \n' + array + ';@GO ;@JVEND'
        else:
            command = f';JVPIX;PSET @WINID ID {part.id} IDEND\n' + array + ';@GO ;@JVEND'
        
        self.send(command, 'part.set_exinf.xml')
        part.extra_info = extra_info

    def set_model_info(self, part: Part, titles: list[str], infos: list[str]):
        datas = ''
        for info_title, info_data in zip(titles, infos):
            base64_info_title = base64.urlsafe_b64encode( info_title.encode('utf-16le') ).decode('utf-8')
            base64_string = base64.urlsafe_b64encode( info_data.encode('utf-16le') ).decode('utf-8')
            splitted = [ base64_string[i:i+160] for i in range(0, len(base64_string), 160) ]
            datas += f'..INFTIT /{base64_info_title}/\n'
            datas += f'..LINCNT /{len(splitted)}/\n'
            datas += '\n'.join([ f'..INFDAT /{d}/' for d in splitted ]) + '\n'

        command  = f';PTINFO;PISET @PICKID ID {part.id} IDEND\n'
        command += '..PISWAT /1/\n'
        command += ';PTINFO;PISET;@GO\n'
        command += '..PISWAT /0/\n'
        command += '..CODFLG /1/\n'
        command += '..TABCNT /7/\n'
        command += datas
        command += ';GXDMY;@JVEND'

        self.send(command, 'part.set_model_info.xml')

    def get_mass(self, part: Part, density=1.0, unit_type=CadTypes.Mass.Unit.MM_KG, is_si=True, mode_accuracy=CadTypes.Mass.Accuracy.Low, is_create_point=False):
        body_types = CadTypes.Entity().body_types()
        entities = [ entity for entity in self.get_entities(part).values() if entity.type in body_types ]
        if len(entities) == 0:
            return None
        
        command  = ';VOL3D;VOL0;@ION AREA;@ION CENT;@ION MOME\n'
        command += f'.SCL {density}\n'
        command += f'@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n;@GO\n;@GO\n'
        command += '..NUMTYP /1/\n'
        command += f'..UNTTYP /{unit_type}/\n'
        command += '..PTPLAC /-5/\n'
        command += f'..KGFUNT /{2 if is_si else 1}/\n'
        command += f'..ACCRCY /{mode_accuracy}/\n'
        command += f'..COFGRV /{1 if is_create_point else 0}/\n'
        command += '..STRNUM /0/\n'
        command += ';@JVEND'

        data = self.send(command, 'part.get_mass.xml')
        for sx_inf_mass in data.xpath('./sx_inf_mass'):
            return Mass(sx_inf_mass)

        return None

    def get_entities_mass(self, entities: list[Entity], density=1.0, unit_type=CadTypes.Mass.Unit.MM_KG, is_si=True, mode_accuracy=CadTypes.Mass.Accuracy.Low, is_create_point=False):
        body_types = CadTypes.Entity().body_types()
        entities = [ entity for entity in entities if entity.type in body_types ]
        if len(entities) == 0:
            return None
        
        command  = ';VOL3D;VOL0;@ION AREA;@ION CENT;@ION MOME\n'
        command += f'.SCL {density}\n'
        command += f'@WINID ID\n'
        command += self.join_entities(entities)
        command += '\nIDEND\n;@GO\n;@GO\n'
        command += '..NUMTYP /1/\n'
        command += f'..UNTTYP /{unit_type}/\n'
        command += '..PTPLAC /-5/\n'
        command += f'..KGFUNT /{2 if is_si else 1}/\n'
        command += f'..ACCRCY /{mode_accuracy}/\n'
        command += f'..COFGRV /{1 if is_create_point else 0}/\n'
        command += '..STRNUM /0/\n'
        command += ';@JVEND'

        data = self.send(command, 'part.get_mass.xml')
        for sx_inf_mass in data.xpath('./sx_inf_mass'):
            return Mass(sx_inf_mass)

        return None

    def put(self, part: Part, filepath: Path, point: list[float], matrix: list[list[float]], is_external: bool = True, is_all_level: bool = False, is_read_only: bool = True, password: str = ''):
        
        num2 = 1E-11
        euler_angle = [0.0, 0.0, 0.0]
        if (abs(abs(matrix[2][0]) - 1.0) <= num2):
            euler_angle[0] = 0.0
            euler_angle[1] = 0.5 * math.pi if (matrix[2][0] >= 0.0) else -0.5 * math.pi
            euler_angle[2] = math.atan2(matrix[0][1], matrix[1][1])
        else:
            euler_angle[0] = math.atan2(0.0 - matrix[2][1], matrix[2][2])
            if (abs(euler_angle[0] - 0.5 * math.pi) < num2):
                euler_angle[1] = math.atan2(matrix[2][0], 0.0 - matrix[2][1])
            elif (abs(euler_angle[0] + 0.5 * math.pi) < num2):
                euler_angle[1] = math.atan2(matrix[2][0], matrix[2][1])
            else:
                x = matrix[2][2] / math.cos(euler_angle[0])
                euler_angle[1] = math.atan2(matrix[2][0], x)
            euler_angle[2] = math.atan2(0.0 - matrix[1][0], matrix[0][0])
            if (math.cos(euler_angle[1]) < 0.0):
                euler_angle[0] = math.atan2(matrix[2][1], 0.0 - matrix[2][2])
                if (abs(euler_angle[0] - 0.5 * math.pi) < num2):
                    euler_angle[1] = math.atan2(matrix[2][0], 0.0 - matrix[2][1])
                elif (abs(euler_angle[0] + 0.5 * math.pi) < num2):
                    euler_angle[1] = math.atan2(matrix[2][0], matrix[2][1])
                else:
                    x2 = matrix[2][2] / math.cos(euler_angle[0])
                    euler_angle[1] = math.atan2(matrix[2][0], x2)
                euler_angle[2] = math.atan2(matrix[1][0], 0.0 - matrix[0][0])

        command  = ';TD4ARG;ARGSTD\n'
        if is_external:
            command += ';@IOFF;INPRT\n'
        else:
            command += ';@ION;INPRT\n'
            command += '@IOFF;ALLLEV\n' if is_all_level else '@ION;ALLLEV\n'
        command += ';LOD\n'
        command += f'.FILEx /{filepath.stem}/\n'
        command += '.PASSWD /        /\n' if password == '' else f'.PASSWD /{password:>8}/\n'
        command += f'.DIRx /{filepath.parent}/\n'
        command += '.OPMODE /1/\n' if is_read_only else '.OPMODE /0/\n'
        command += f':\n.OFS /{0}/\n:\n'
        command += f'@HIT X {point[0]:.8f} Y {point[1]:.8f} Z {point[2]:.8f} ,@GO\n'
        command += f'.ANGX /{euler_angle[0]:.14f}/ .ANGY /{euler_angle[1]:.14f}/ .ANGZ /{euler_angle[2]:.14f}/\n'
        command += ';@JVEND'

        element = self.send(command, 'part.put.xml')
        parts = []
        for sx_ent in element.xpath('./element'):
            part2 = Part(self.client, part.model_id, part.wfno)
            part2.from_ent( PartCommand.Data(sx_ent) )
            parts.append(part2)
        
        return parts

    def get_materials(self, part: Part):
        part.material = []
        body_types = CadTypes.Entity().body_types()
        bodies = [ entity for entity in self.get_entities(part).values() if entity.type in body_types ]
        if len(bodies) == 0:
            return
        elemenet = self.send(';JVUEN2\n' + '\n'.join([f'.KIND 0 .ENTID {body.id} :' for body in bodies]) + '\n;@GO;@JVEND', 'part.get_materials.xml')
        for sx_inf_mat in elemenet.xpath('./sx_inf_mat'):
            part.material.append( Material(sx_inf_mat) )
        return part.material

    def set_material(self, part: Part, material: Material):
        if material is None:
            command  = f';VOL3D;SET0;DEL1\n@WINID ID {part.id} VISI 6 IDEND\n@GO'
        else:
            command  = f';VOL3D;SET0;SET1\n@WINID ID {part.id} IDEND\n@GO\n'
            command += '.SHORI / 0/\n'
            if len( material.name.encode('utf-16le') ) <= 64:
                command += f'.ZAI1 /{material.name.replace("/", "//")}/\n'
                command +=  '.ZAI2 / /\n'
            else:
                splitted_name = self.client.split_string(material.name)
                command += f'.ZAI1 /{splitted_name[0].replace("/", "//")}/\n'
                command += f'.ZAI2 /{splitted_name[1].replace("/", "//")}/\n'
            command += f'.KIG /{material.matid.replace("/", "//")}/\n'
            command += f'.HIJYU /{material.spe_grav:.4f}/\n'
            command += f'.DIF /{material.dif[0]:3d},{material.dif[1]:3d},{material.dif[2]:3d},{material.dif[3]:3d}/\n'
            command += f'.SPE /{material.spe[0]:3d},{material.spe[1]:3d},{material.spe[2]:3d},{material.spe[3]:3d}/\n'
            command += f'.SHI /{material.shi:3d}/\n'
            command += f'.ALP /{material.alpha:3d}/\n'
            command += ';GXDMY;@JVEND'
        self.send(command, 'part.set_material.xml')

    def get_hole_infos(self, entities: list[Entity]):
        elemenet = self.send(';JVUEN2\n' + '\n'.join([f'.KIND 14 .ENTID {entity.id} :\n' for entity in entities ]) + '\n;@GO;@JVEND', 'part.set_material.xml')
        holes = { entity.id : [] for entity in entities }
        for sx_inf_hole in elemenet.xpath('./sx_inf_hole'):
            hole = Hole()
            hole.from_inf( HoleCommand.Data(sx_inf_hole) )
            holes[hole.id].append(hole)
        holes: list[Hole] = list( holes.values() )
        return holes

    def take_in(self, part: Part, all_level: bool, same_name: bool=False):
        message_command = '.MSG /NO  /\n'
        if same_name:
            elemenet = self.send(f';JVUENT .KIND 10 .ENTID {part.id} : ;@JVEND', 'part.take_in.xml')
            if len( elemenet.xpath('sx_ent') ) > 0:
                message_command = '.MSG /ALL /\n'

        command  = f';TD4MOD;OUTCHG\n@I{"ON" if all_level else "OFF"};ALLLEV\n@PICKID ID {part.id} IDEND\n;@GO\n'
        command += message_command
        command += ';GXDMY;@JVEND'
        
        self.send(command, 'part.take_in.xml')

        self.get_inf(part)

    def take_out(self, part: Part, is_all: bool, path: Path):
        if is_all:
            elemenet = self.send(f';JVUENT .KIND 10 .ENTID {part.id} : ;@JVEND', 'part.take_out.xml')
            if len( elemenet.xpath('sx_ent') ) > 0:
                message_command = '.MSG /ALL /\n'
            else:
                message_command = '.MSG /NO  /\n'
        
        command  = f';TD4MOD;INCHG\n@PICKID ID {part.id} IDEND\n;@GO\n'
        if part.has_grp:
            command += '.SHORI / 0/\n'
        if is_all:
            command += message_command
        command += '.SHORI /1/\n'
        command += f'.MODELNAME /{part.name.replace("/", "//")}/\n'
        command += f'.DIRx /{path}/\n;GXDMY;@JVEND'

        self.send(command, 'part.take_out.xml')

        self.get_inf(part)

    def create_3d_point(self, part: Part, point: list[float]):
        self.set_active(part)
        element = self.send(f';POINT3;SPEC .NCNT 1\n;@POS;@HIT X {point[0]:.8f} Y {point[1]:.8f} Z {point[2]:.8f} ,\n;GXDMY;@JVEND', 'part.create_3d_point.xml')

    def get_extent(self, part: Part):
        element = self.send(f';JVBOX .ID {part.id} : ;@JVEND', 'part.create_3d_point.xml')
        for sx_box in element.xpath('./sx_box'):
            points = [ [ float(sx_box.get(f'{j}{i}')) for j in ['x', 'y', 'z'] ] for i in ['1', '2'] ]
            _id = int( sx_box.get('id') )
            return points

    def get_tree_element(self, part: Part):
        return self.send(f';JVGPID .KIND 5 .ID {part.id} : ;@JVEND', 'part.get_tree_element.xml')

    def echo(self, part: Part):
        return self.send(f';JVUEN3 .KIND 1 : @WINID ID {part.id} IDEND @GO;@JVEND', 'part.echo.xml')


class SystemCommand(BaseCommand):
    
    class Data:
        def __init__(self, client: 'Client', element: etree._Element) -> None:
            self.version                 = int( element.get('version', '-1') )
            self.level                   = int( element.get('level', '-1') )
            self.path: str               = element.get('path', '')
            self.pen_color               = int( element.get('color', '-1') )
            self.pen_style               = int( element.get('style', '-1') )
            self.pen_width               = int( element.get('width', '-1') )
            self.scale                   = float( element.get('scale', '-1') )
            self.grid                    = float( element.get('grid', '-1') )
            self.active_layer            = int( element.get('layer', '-1') )
            self.active_model_id         = int( element.get('model', '-1') )
            self.pdno                    = int( element.get('pdno', '-1') )
            self.navi: bool              = element.get('navi', '0') != '0'
            self.cross: bool             = element.get('cross', '0') != '0'
            self.dim: bool               = element.get('dim', '0') != '0'
            self.sys3d: bool             = element.get('sys3d', '0') != '0'
            self.plane_lock: bool        = element.get('plane_lock', '0') != '0'
            self.is_viewer: bool         = element.get('is_viewer', '0') != '0'
            self.mod_flg                 = int( element.get('mod_flg', '-1') )
            self.active_part: Part       = None 
            self.active_model: Model     = None
            self.model: dict[int, Model] = {}

            for sx_ent in element.xpath('./sx_ent'):
                self.active_part = Part(client, self.active_model_id)
                self.active_part.from_ent( PartCommand.Data(sx_ent) )
                self.active_part.get_inf()
                self.active_part.get_parent()
                break

            for sx_model in element.xpath('./sx_model'):
                model_id = int( sx_model.get('model_id', '0') )
                self.model[model_id] = Model(client, model_id)
                if model_id == self.active_model_id:
                    self.active_model = self.model[model_id]

    def system_data(self, element: etree._Element):
        return SystemCommand.Data(self.client, element)

    def get_inf_sys(self):
        element = self.send(';JVGSIF;GXDMY;@JVEND', 'system.get_inf_sys.xml')
        for sx_inf_sys in element.xpath('./sx_inf_sys'):
            return SystemCommand.Data(self.client, sx_inf_sys)

    def open_model(self, cad: PyCadSx, path: Path, read_only: bool = False, password: str = None):
        model_paths = [ Path(model.path)/f'{model.name}.icd' for model in cad.model.values() ]
        if path in model_paths:
            return
        password = "        " if password is None or password == "" else password
        command  = f";GXDMY;OPEN;LOD .FILE /{path.stem}/\n"
        command += f'.PASSWD /{password}/\n'
        command += f'.DIRx /{path.parent}/\n'
        command += f'.OPMODE /{1 if read_only else 0}/\n'
        command += ';GXDMY;@JVEND'
        self.send(command, 'pycadsx.open_model.xml')

    def get_materials(self):
        materials: list[Material] = []
        data = self.send(';JVGMAT;@JVEND', 'get_inf_materials.xml')
        for sx_inf_mat in data.xpath('./sx_inf_mat'):
            materials.append(Material(sx_inf_mat))
        return materials

    def get_local_font(self, font_name: str):
        font_name = self.client.string_to_base64string(font_name)
        element = self.send(f';JVFONT /{font_name}/ ;@JVEND', 'pycadsx.get_local_font.xml')
        text = ''
        for sx_str in element.xpath('./sx_str'):
            text += sx_str.text if sx_str.text is not None else ''
        return text
    
    def get_plotters(self):
        plotters: list[Plotter] = []
        default_plotter: Plotter = None
        element = self.send(';JVPLOT;@JVEND', 'pycadsx.get_plotters.xml')
        default_plotter_number = 'PLOT01'
        
        for sx_inf_def_plot in element.xpath('./sx_inf_def_plot'):
            default_plotter_number = sx_inf_def_plot.get('no')

        for sx_inf_plot_list in element.xpath('./sx_inf_plot_list'):
            plotters.append( Plotter(sx_inf_plot_list) )
            if plotters[-1].no == default_plotter_number:
                default_plotter = plotters[-1]
            
        return plotters, default_plotter


class WindowCommand(BaseCommand):
    
    class Info:
        def __init__(self, element: etree._Element) -> None:
            for sx_inf_pd in element.xpath('./sx_inf_pd'):
                self.is_base  = sx_inf_pd.get('is_base') == '1'
                self.model_id = int( sx_inf_pd.get('model_id') )
                self.vsno     = int( sx_inf_pd.get('vsno') )
                self.vstype   = int( sx_inf_pd.get('vstype') )
                self.wfno     = int( sx_inf_pd.get('wfno') )
                self.wftype   = int( sx_inf_pd.get('wftype') )
                self.status   = CadTypes.Window.Status.get_value( int( sx_inf_pd.get('status') ) )

                self.rect = [
                    [int( sx_inf_pd.get('xmin') ), int( sx_inf_pd.get('ymin') )],
                    [int( sx_inf_pd.get('xmax') ), int( sx_inf_pd.get('ymax') )]
                ]

                self.mdi_rect = [
                    [int( sx_inf_pd.get('mdi_xmin') ), int( sx_inf_pd.get('mdi_ymin') )],
                    [int( sx_inf_pd.get('mdi_xmax') ), int( sx_inf_pd.get('mdi_ymax') )]
                ]
                return

    def get_inf(self, window: Window):
        element = self.send(f';JVGPIF .PDNO {window.pdno} : ;@JVEND', 'window.get_inf.xml')
        window.from_inf( WindowCommand.Info(element) )

    def zoom_full(self):
        self.send('@ZOOMFUL ;@JVEND', 'window.zoom_full.xml')

    def zoom_rasio(self, ratio: float):
        self.send(f'@ZOOM {ratio} : ;@JVEND', 'window.zoom_rasio.xml')

    def set_dimension(self, window: Window, is3d: bool):
        self.get_inf(window)
        if is3d and window.vsno != 0:
            self.send(';DIMSW1 @GO ;@JVEND', 'window.set_dimension.xml')

        if not is3d and window.wfno != 0:
            self.send(';DIMSW1 @GO ;@JVEND', 'window.set_dimension.xml')

    def close(self, window: Window):
        if window.is_base:
            self.send(f';WKSCR1 {window.pdno} ;CLOSE ;CLS .MSG /NO/ ;GXDMY;@JVEND', 'window.close.xml')
        else:
            self.send(f';@XSCLOS {window.pdno} ;@JVEND', 'window.close.xml')

    def rotate(self, window: Window, zvec: list, xvec: list):
        self.send(f'@RMSET /{window.pdno}/ /{xvec[0]:.15f}/ /{xvec[1]:.15f}/ /{xvec[2]:.15f}/ /{zvec[0]:.15f}/ /{zvec[1]:.15f}/ /{zvec[2]:.15f}/ ;@JVEND')

    def pan(self, window: Window, center: list):
        self.send(f'@PANHIT S {window.pdno} X {center[0]:.8f} Y {center[1]:.8f}  Z {center[2]:.8f}, ;@JVEND')

    def get_mdi_rect(self):
        self.send(';JVGMDI : ;@JVEND')
    
    def set_active(self, window: Window):
        self.send(f';WKSCR1 {window.pdno} : ;@JVEND')
    
    def switch_dimension(self):
        self.send(f';DIMSW1 @GO : ;@JVEND')
    
    def set_vs(self, window: Window, model_id: int, vsno: int):
        self.send(f';JVUVW .KIND 8 .SXDIM 2 .MODEL {model_id} .VWNO {vsno} .NUM0 {window.pdno} : ;@JVEND')

    def set_wf(self, window: Window, model_id: int, wfno: int):
        self.send(f';JVUVW .KIND 8 .SXDIM 3 .MODEL {model_id} .VWNO {wfno} .NUM0 {window.pdno} : ;@JVEND')
    
    def set_system_view(self, view: 'CadTypes.Window.View'):
        if view == CadTypes.Window.View.TOP:
            command = f';@SVIWT =0 @go;@JVEND'
        elif view == CadTypes.Window.View.FRONT:
            command = f';@SVIWF =0 @go;@JVEND'
        elif view == CadTypes.Window.View.RIGHT:
            command = f';@SVIWRI =0 @go;@JVEND'
        elif view == CadTypes.Window.View.LEFT:
            command = f';@SVIWL =0 @go;@JVEND'
        elif view == CadTypes.Window.View.BACK:
            command = f';@SVIWRE =0 @go;@JVEND'
        elif view == CadTypes.Window.View.BOTTOM:
            command = f';@SVIWB =0 @go;@JVEND'
        else:
            return
        self.send(command, 'window.set_system_view.xml')

    def set_status(self, window: Window, status: 'CadTypes.Window.Status'):
        self.get_inf(window)
        if status == CadTypes.Window.Status.NORMAL:
            if window.status == CadTypes.Window.Status.ICON:
                command = f'@XSICON {window.pdno} ;@JVEND'
            else:
                command = f'@XSMAX {window.pdno} ;@JVEND'
        elif status == CadTypes.Window.Status.ICON:
            command = f'@XSICON {window.pdno} ;@JVEND'
        elif status == CadTypes.Window.Status.MAX:
            command = f'@XSMAX {window.pdno} ;@JVEND'
        else:
            return

        self.send(command, 'window.set_status.xml')

    def get_virtual_position(self, window: Window, point: list[float]):
        element = self.send(f';JVGPSV .PDNO {window.pdno} .SCX {point[0]} .SCY {point[1]} : ;@JVEND', 'window.get_virtual_position.xml')
        for sx_pos in element.xpath('./sx_pos'):
            return [ float(sx_pos.get('x')), float(sx_pos.get('y')), float(sx_pos.get('z')) ]

class Calculate:
    def normalize(self, v: list[float]):
        length = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5
        if length == 0:
            return [1.0, 0.0, 0.0]
        return [v[0] / length, v[1] / length, v[2] / length]
    
    def cross(self, v0: list[float], v1: list[float]):
        return [
            v0[1] * v1[2] - v0[2] * v1[1],
            v0[2] * v1[0] - v0[0] * v1[2],
            v0[0] * v1[1] - v0[1] * v1[0]
        ]

    def is_point_in_rect(self, point: list[float], rect: list[list[float]]):
        return rect[0][0] <= point[0] <= rect[1][0] and rect[0][1] <= point[1] <= rect[1][1]

    def find_unique_point(self, rects: list[list[list[float]]], target_rect: list[list[float]], step=2.0):
        x_min, y_min = target_rect[0]
        x_max, y_max = target_rect[1]
        
        x_min, y_min = x_min + 1, y_min + 1
        x_max, y_max = x_max - 1, y_max - 1
        
        x = x_min
        while x <= x_max:
            y = y_min
            while y <= y_max:
                point = [x, y]
                if self.is_point_in_rect(point, target_rect):
                    in_other_rects = False
                    for rect in rects:
                        if rect != target_rect and self.is_point_in_rect(point, rect):
                            in_other_rects = True
                            break
                    if not in_other_rects:
                        return point
                y += step
            x += step
        
        return None


class Client:
    def __init__(self, is_debug=False, host='localhost', port=3999, encoding='utf-16le'):
        self.log_path                = Path(sys.argv[0]).parent / 'xml'
        self.send_string_template    = 'license=ON\nmode=__mode__\nret_ent=__ret_ent__\n__commands__\nSxMsg_End'
        self._is_debug               = is_debug
        self.host                    = host
        self.port                    = port
        self.encoding                = encoding
        self.system                  = SystemCommand(self)
        self.asm_plane               = AsmPlaneCommand(self)
        self.edge                    = EdgeCommand(self)
        self.entity                  = EntityCommand(self)
        self.face                    = FaceCommand(self)
        self.model                   = ModelCommand(self)
        self.part                    = PartCommand(self)
        self.r_part                  = RPartCommand(self)
        self.vs                      = VsCommand(self)
        self.window                  = WindowCommand(self)
        self.calculate               = Calculate()
        
    def send(self, command: str, xml_file_name=None, is_recieve=True, is_macro=False, ret_ent=True) -> etree._Element:
        mode = 'COMMAND' if is_macro else 'MACRO,NODISP'
        ret_ent = 'ON' if ret_ent else 'OFF'

        send_string     = self.send_string_template
        send_string     = send_string.replace('__mode__', mode)
        send_string     = send_string.replace('__ret_ent__', ret_ent)
        send_string     = send_string.replace('__commands__', command)
        ir_code         = []
        chunks          = None
        error_massage   = None
        recieved_string = None
        
        _client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            _client.connect( (self.host, self.port) )
            _client.sendall( send_string.encode(self.encoding) )

            if is_recieve:
                chunks = []
                while True:
                    chunk = _client.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
        except:
            error_massage = traceback.format_exc()
                
        _client.close()

        element = None

        if chunks is not None:
            if len(chunks) > 0:
                recieved_string = b''.join(chunks).decode(self.encoding)
                recieved_string = recieved_string.replace('<?xml version="1.0" encoding="Unicode"?>\n', '')
                recieved_string = recieved_string.replace('&', '&amp;')
                recieved_string = recieved_string.replace('amp;amp;', 'amp;')
                recieved_string = recieved_string.replace('amp;lt;', 'lt;')
                recieved_string = recieved_string.replace('amp;gt;', 'gt;')
                recieved_string = recieved_string.replace('amp;quot;', 'quot;')
                if recieved_string[-1] == '\x00':
                    recieved_string = recieved_string[:-1]
            
                if xml_file_name is not None and self._is_debug:
                    self.log_path.mkdir(parents=True, exist_ok=True)
                    with open(self.log_path / xml_file_name, mode='w') as f:
                        f.write(recieved_string)

                element: etree._Element = etree.fromstring(recieved_string)

                error = element.xpath('./sx_err')
                if error:
                    error: etree._Element = error[0]
                    ir_code = [ error.get('ir0'), error.get('ir1'), error.get('ir2') ]
                    error_massage = '-'.join(ir_code) + f' : {error.text}'

        if error_massage is not None:
            raise Exception(f'{error_massage} ({"-".join(ir_code)})\ncommand : \n{command}')
        
        return element

    def string_to_base64string(self, _string: str):
        _bytes = _string.replace('\n', '\r\n').replace('\r\r\n', '\r\n').encode('utf-16le')
        base64_data = base64.urlsafe_b64encode(_bytes)
        base64string = base64_data.decode('utf-8')
        replaced = base64string.replace('+', '-').replace('/', '_')
        return replaced

    def extra_info_to_base64string(self, extra_info: dict[str, str]):
        extra_info_text = ','.join([
            '{},"{}"'.format(key, value)
            for key, value in extra_info.items()
            if (value != '') and (value is not None) and key.startswith('User_')
        ])

        _bytes = extra_info_text.replace('\n', '\r\n').replace('\r\r\n', '\r\n').encode('utf-16le')
        base64_data = base64.urlsafe_b64encode(_bytes)
        base64string = base64_data.decode('utf-8')
        replaced = base64string.replace('+', '-').replace('/', '_')

        return replaced

    def split_string(self, text: str) -> list[str]:
        s, count, split_comments = 0, 0, []
        for e, c in enumerate(text):
            count += len( c.encode('utf-16le') )
            if count == 40:
                split_comments.append(text[s : e + 1])
                count, s = 0, e + 1
            elif count == 41:
                split_comments.append(text[s : e])
                count, s = 0, e
            elif e == len(text) - 1:
                split_comments.append(text[s : ])
        return split_comments

    def get_language(self):
        with open(f'{os.getenv("ICADDIR")}\\LANG\\Language', mode='r', encoding='cp932') as f:
            language_lines = f.readlines()
        for line in language_lines:
            if line.startswith('ILANGID='):
                return int( line.replace('ILANGID=', '') )
        return 1

    def base64string_to_string(self, base64_string):
        b64decoded = base64.urlsafe_b64decode(base64_string)
        decoded = b64decoded.decode('utf-16le')
        return decoded

    def extra_info_to_dict(self, texts: list[str]):
        base64_string = ''.join(texts)
        if base64_string == '':
            return {}
        b64decoded = base64.urlsafe_b64decode(base64_string)
        decoded = b64decoded.decode('utf-16le')

        f = io.StringIO()
        f.write(decoded)
        f.seek(0)
        csv_reader = csv.reader(f)
        datas = csv_reader.__next__()
        f.close()
        data = {
            datas[i*2].strip() : datas[i*2+1].strip()
            for i in range( int( len(datas) / 2 ) )
        }

        return data

    def check_filename(self, filename: str):
        for c in [
            ' ', '/', '\\', '<', '>', ',', '!', '"', '$', '\'', '~',
            '|', '`', ';', ':', '*', '?', '\t', '\r', '\n', '\u3000'
        ]:
            if c in filename:
                return False
        return True

    def create_part(self, element: etree._Element, model_id: int = 0, wfno: int = 1):
        part = Part(self, model_id, wfno)
        part.from_ent( PartCommand.Data(element) )
        part.get_inf()
        part.parent = part.get_parent()
        return part
