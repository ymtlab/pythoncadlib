from PySide6 import QtWidgets, QtGui
import pycadsx

class TreeWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.cad = pycadsx.PyCadSx()

        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Comment'])

        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.model)
        self.view.setColumnWidth(0, 200)

        self.load_tree_button = QtWidgets.QPushButton('Load Tree')

        self.resize(400, 400)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.load_tree_button)
        self.layout().addWidget(self.view)

        self.load_tree_button.clicked.connect(self.load_tree)

    def load_tree(self):
        self.model.removeRows(0, self.model.rowCount())
        self.cad.get_inf_sys()
        self.cad.active_model.get_tree()
        
        stack: list[ tuple[QtGui.QStandardItem, pycadsx.Part] ] = [ (self.model.invisibleRootItem(), self.cad.active_model.top_part) ]

        while stack:
            parent, part = stack.pop()

            items = [
                QtGui.QStandardItem(part.name),
                QtGui.QStandardItem(part.comment)
            ]

            parent.appendRow(items)

            for child in part.children:
                stack.append( (items[0], child) )
        
        self.view.expandAll()

def main():
    app = QtWidgets.QApplication([])
    widget = TreeWidget()
    widget.show()
    app.exec()

if __name__ == '__main__':
    main()
