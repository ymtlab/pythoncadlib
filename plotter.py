
from lxml import etree


class Plotter:
    def __init__(self, element: etree._Element) -> None:
        self.no = element.get('no')
        self.name = element.get('name')
