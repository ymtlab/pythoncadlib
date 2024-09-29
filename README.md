# 使い方

## ツリーをCSV出力するサンプル

```python
import csv
import pycadsx

def main():
    cad = pycadsx.PyCadSx()
    cad.get_inf_sys()
    cad.active_model.get_tree()

    output_list = [ ['Level', 'Name', 'Comment'] ]

    stack: list[tuple[int, pycadsx.Part]] = [(0, cad.active_model.top_part)]
    while stack:
        level, part = stack.pop()
        output_data = [level, part.name, part.comment]
        output_list.append(output_data)
        for child in part.children:
            stack.append((level + 1, child))
    
    with open('tree.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(output_list)

if __name__ == '__main__':
    main()
```

## パーツを追加するサンプル

```python
import pycadsx

def main():
    cad = pycadsx.PyCadSx()
    cad.get_inf_sys()
    cad.active_model.get_tree()

    for i in range(3):
        child = cad.active_model.top_part.create_child(f'name{i:03d}', f'comment{i:03d}')
        
        for j in range(3):
            child.create_child(f'name{i:03d}-{j:03d}', f'comment{i:03d}-{j:03d}')

if __name__ == '__main__':
    main()
```

## PySide6のQTreeViewにツリーを表示するサンプル

```python
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
```
