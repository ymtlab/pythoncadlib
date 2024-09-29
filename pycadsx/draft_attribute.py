from lxml import etree


class DraftAttribute:
    def __init__(self, element: etree._Element) -> None:
        for sx_draft_atr_general in element.xpath('./sx_draft_atr_general'):
            self.general = General(sx_draft_atr_general)
            
        for sx_draft_atr_word in element.xpath('./sx_draft_atr_word'):
            sx_draft_atr_texts = sx_draft_atr_word.xpath('./sx_draft_atr_text')
            self.word_dimension = Word(sx_draft_atr_texts[0])
            self.word_1 = Word(sx_draft_atr_texts[1])
            self.word_2 = Word(sx_draft_atr_texts[2])
            self.word_3 = Word(sx_draft_atr_texts[3])

        for sx_draft_atr_notation in element.xpath('./sx_draft_atr_notation'):
            self.notation = Notation(sx_draft_atr_notation)

        for sx_draft_atr_smark in element.xpath('./sx_draft_atr_smark'):
            self.smark = Word(sx_draft_atr_smark.xpath('./sx_draft_atr_text')[0])

        for sx_draft_atr_balloon in element.xpath('./sx_draft_atr_balloon'):
            self.balloon = Balloon(sx_draft_atr_balloon)
            
        for sx_draft_atr_weld in element.xpath('./sx_draft_atr_weld'):
            self.welding = Welding(sx_draft_atr_weld)
            
        for sx_draft_atr_geotol in element.xpath('./sx_draft_atr_geotol'):
            self.geometric_tolerance = GeometricTolerance(sx_draft_atr_geotol)
            
        for sx_draft_atr_dimform in element.xpath('./sx_draft_atr_dimform'):
            self.dimension_form = DimensionForm(sx_draft_atr_dimform)
            
        for sx_draft_appdim in element.xpath('./sx_draft_appdim'):
            self.append_dimension = AppendDimension(sx_draft_appdim)


class AppendDimension:
    def __init__(self, element: etree._Element) -> None:
        sx_draft_atr_text = element.xpath('./sx_draft_atr_text')
        self.finish_mark_len = float(element.get('finish_mark_len'))
        self.delta_len = float(element.get('delta_len'))
        self.word_arron = Word(sx_draft_atr_text[0])
        self.word_cutline = Word(sx_draft_atr_text[1])


class DimensionForm:
    def __init__(self, element: etree._Element) -> None:
        self.dimval_space = float(element.get('dimval_space'))
        self.note_underline_len = float(element.get('note_underline_len'))
        self.underline1_len = float(element.get('underline1_len'))
        self.underline2_len = float(element.get('underline2_len'))
        self.step_space = float(element.get('step_space'))
        self.prog_diameter = float(element.get('prog_diameter'))
        self.prog_space = float(element.get('prog_space'))
        self.prog_bend_width = float(element.get('prog_bend_width'))
        self.note_space = float(element.get('note_space'))


class GeometricTolerance:
    def __init__(self, element: etree._Element) -> None:
        self.frame_ratio = float(element.get('frame_ratio'))
        self.datum_ratio = float(element.get('datum_ratio'))
        self.datum_fill = element.get('datum_fill') != '0'
        self.word = Word(element.xpath('./sx_draft_atr_text')[0])


class Welding:
    def __init__(self, element: etree._Element) -> None:
        self.route_ratio = float(element.get('route_ratio'))
        self.ang_ratio = float(element.get('ang_ratio'))
        self.form_cir_ratio = float(element.get('form_cir_ratio'))
        self.form_site_ratio = float(element.get('form_site_ratio'))
        self.form_base_ratio = float(element.get('form_base_ratio'))
        self.form_baseline_head_ratio = float(element.get('form_baseline_head_ratio'))
        self.form_baseline_tail_ratio = float(element.get('form_baseline_tail_ratio'))
        self.form_tail_ratio = float(element.get('form_tail_ratio'))
        self.word = Word(element.xpath('./sx_draft_atr_text')[0])


class Balloon:
    def __init__(self, element: etree._Element) -> None:
        self.diameter = float( element.get('diameter', 0.0) )
        self.auto_size = element.get('auto_size') != '0'
        self.word = Word(element.xpath('./sx_draft_atr_text')[0])


class General:
    def __init__(self, element: etree._Element) -> None:
        self.color          = int(element.get('color'))
        self.width          = int(element.get('width'))
        self.aidline_extlen = float(element.get('aidline_extlen'))
        self.aidline_space  = float(element.get('aidline_space'))
        self.aidline_tilt   = float(element.get('aidline_tilt'))
        self.arrow_type     = int(element.get('arrow_type'))
        self.disp_baseline  = element.get('disp_baseline') != '0'
        self.arrow_width    = float(element.get('arrow_width'))
        self.arrow_ang      = float(element.get('arrow_ang'))
        self.dot_diam       = float(element.get('dot_diam'))


class Word:
    def __init__(self, element: etree._Element) -> None:
        self.font = element.get('font') != '0'
        self.font_name = element.get('font_name')
        self.height = float(element.get('height'))
        self.width_ratio = float(element.get('width_ratio'))
        self.tilt = int(element.get('tilt'))
        self.space_ratio = float(element.get('space_ratio'))
        self.row_space = float(element.get('row_space'))
        self.color = int(element.get('color'))
        self.width = int(element.get('width'))


class Notation:
    def __init__(self, element: etree._Element) -> None:
        self.rouway = int(element.get('rouway'))
        self.round = int(element.get('round'))
        self.suppress = element.get('suppress') != '0'
        self.multiple_mode = int(element.get('multiple_mode'))
        self.multiple = float(element.get('multiple'))
        self.dimtol1_ratio = float(element.get('dimtol1_ratio'))
        self.dimtol2_ratio = float(element.get('dimtol2_ratio'))
        self.dimtol2_space = float(element.get('dimtol2_space'))
        self.dimtol_pos = int(element.get('dimtol_pos'))
        self.angtype = int(element.get('angtype'))
        self.dispang = int(element.get('dispang'))
        self.dispang_angdim = int(element.get('dispang_angdim'))
        self.dimval_scale = float(element.get('dimval_scale'))
