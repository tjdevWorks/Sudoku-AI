assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]

rows='ABCDEFGHI'
cols='123456789'

boxes = cross(rows, cols) # It is a list of all boxes keys

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

diaglist = [[row_units[i][i] for i in range(9)],[row_units[i][8-i] for i in range(9)]] # A list of diagonal box keys for solving diagonal sudoku

unitlist = row_units + column_units + square_units + diaglist
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes) # A dictionary of box id as key and value as a set of keys of it's row, column, and grid

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    for box in boxes:
        if(len(values[box]) == 2):#Checks if length of box value is two to find it's naked twin
            v = values[box]
            z=units[box]#Gives a list of lists of box's row, column and grid unit
            for l in z:
                poped_box = l.pop(l.index(box))
                for b in l:
                    if values[b] == v:
                        neighbours = l
                        poped_b = neighbours.pop(neighbours.index(b))
                        for n in neighbours:
                            #Replace the naked twin value of it's peer with empty string
                            values = assign_value(values ,n, values[n].replace(v[0],''))
                            values = assign_value(values ,n, values[n].replace(v[1],''))
                        neighbours.append(poped_b)
                poped_box = l.append(poped_box)
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """

    sudgrid = dict(zip(boxes, grid))
    for key, value in sudgrid.items():
        if sudgrid[key] == '.':
            sudgrid[key] = '123456789'
    return sudgrid

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    '''
    This function eliminates the solved value boxes values from it's peers' box
    '''
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values= assign_value(values,peer,values[peer].replace(digit,''))
    return values

def only_choice(values):
    '''
    This function is for finding the digit which can exists in only one box in every unit and assign that box the digit
    '''
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    '''
    This function is used to leverage the two constraints only_choice and eliminate iteratively to solve the puzzle entirely
    '''
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    '''
    Using depth first search, create a tree and solve the sudoku recursively
    '''
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all([len(values[s])==1 for s in boxes]):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = search(grid_values(grid))
    if values is False:
        return False
    else:
        return values

if __name__ == '__main__':

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    values = solve(diag_sudoku_grid)
    if values is False:
        print("Sudoku cannot be solved")
    else:
        display(values)

        try:
            from visualize import visualize_assignments
            visualize_assignments(assignments)

        except SystemExit:
            pass
        except:
            print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
