

def display_board(state):
    for i in range(10):
        for j in range(10):
            print(state.data['piece_locations'].get((i,j),'.'), end='')
        print('\n')
    
