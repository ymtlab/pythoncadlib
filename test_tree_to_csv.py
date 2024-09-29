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
