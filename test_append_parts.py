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
