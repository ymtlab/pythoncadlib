from lxml import etree


class Material:
    def __init__(self, element: etree._Element) -> None:
        self.name: str  = element.get('name')
        self.matid: str = element.get('matid')
        self.spe_grav   = float( element.get('spe_grav') )
        self.dif        = [ int( element.get(f'd{i}') ) for i in range(4) ]
        self.spe        = [ int( element.get(f's{i}') ) for i in range(4) ]
        self.shi        = int( element.get('shi') )
        self.alpha      = int( element.get('alpha') )
        self.id         = int( element.get('id') )
