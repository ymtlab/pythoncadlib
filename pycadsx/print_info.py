from lxml import etree


class PrintInfo:
    def __init__(self, element: etree._Element) -> None:
        self.no: int        = int(element.get('no'))
        self.size: str      = element.get('size')
        self.vertical: bool = element.get('vertical') != '0'

        self.width       = float(element.get('d0'))
        self.height      = float(element.get('d1'))
        self.scale       = float(element.get('d2'))
        self.left_bottom = [ float(element.get('d3')), float(element.get('d4')) ]
        self.right_top   = [ float(element.get('d5')), float(element.get('d6')) ]

        self.d7  = float(element.get('d7'))
        self.d8  = float(element.get('d8'))
        self.d9  = float(element.get('d9'))
        self.d10 = float(element.get('d10'))
        self.d11 = float(element.get('d11'))
        self.d12 = float(element.get('d12'))
        self.d13 = float(element.get('d13'))
        self.d14 = float(element.get('d14'))
        self.d15 = float(element.get('d15'))
        self.d16 = float(element.get('d16'))
        self.d17 = float(element.get('d17'))
        self.d18 = float(element.get('d18'))
        self.d19 = float(element.get('d19'))
