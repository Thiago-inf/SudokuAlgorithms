import random
import csv
from enum import Enum
from restrictionPropagationAlg import restrictionPropagation
import time
from statistics import mean

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

# Display Sudoku
def display(grid):
    width = 1+max(len(grid[s]) for s in squares)
    line = '+'.join(['-'*(width*2)]*2)
    for r in rows:
        print(''.join(grid[r+c].center(width)
                      for c in cols))
    
# Convert a Dictionary grid into a String representation of a grid
def toString(dictionaryGrid):
    strGrid = ''
    for values in dictionaryGrid.values():
        strGrid += values
    return strGrid

# Convert a Dictionary grid into a Matrix representation of a grid
def toMatrix(grid):
    matrixGrid = [[0 for col in range(N)] for line in range(N)]
    i = 0
    j = 0
    for value in grid.values():
        matrixGrid[i][j] = int(value)
        j += 1
        if j == N:
            j = 0
            i += 1
    return matrixGrid
    
# Check if given Sudoku is solved or not  
def isSolved(grid):
    return all(len(value) == 1 and value != '0' and value in digits for value in grid.values())

# Cross line-column information
def cross(A, B):
    return [a+b for a in A for b in B]

# Convert a given Sudoku String to a Dictionary Sudoku
def toDictionary(grid):
    chars = [c for c in grid if c in digits or c in '0']
    return dict(zip(squares, chars))

# Main algorithm to generate a new Sudoku
# Parameters:
# grid --> already solved grid(dictionary format)
# qtRemove --> integer with how many values should be removed from grid.
def generateSudokuByExistingGrid(grid, qtRemove):
    squaresOccupied = list(grid.keys())
    validSquares = squaresOccupied.copy()
    newGrid = grid.copy()
    counter = 0
    while qtRemove > 0:
        randomSquare = random.choice(validSquares)
        randomSquareValue = [randomSquare, grid.get(randomSquare)]
        if randomSquareValue[1] != '0':
            newGrid = assign(newGrid, randomSquareValue[0], '0')
            solvedGrid, diff = solve(newGrid, True)
            if countSolutions(0, 0, toMatrix(solvedGrid), 0) == 1:
                counter = 0
                squaresOccupied.remove(randomSquareValue[0])
                qtRemove -= 1
                validSquares = squaresOccupied.copy()
            else:
                counter += 1
                validSquares.remove(randomSquareValue[0])
                newGrid = assign(newGrid, randomSquareValue[0], randomSquareValue[1])
        if len(validSquares) == 0:
            break
    return newGrid, len(squaresOccupied)

# Candidates grid creation
def createCandidatesGrid(grid):
    dictPossibleValues = dict((s, digits) for s in squares)
    for square,digit in grid.items():
        if digit in digits:
            dictPossibleValues[square] = digit
    for square, possibleValues in dictPossibleValues.items():
        if len(possibleValues) > 1:
            squareUnit = units.get(square)
            squareColumn = squareUnit[0]
            squareLine = squareUnit[1]
            squareBox = squareUnit[2] if N > 3 else []
            for index, x in enumerate(squareLine):
                columnValue = grid.get(squareColumn[index])
                if columnValue in digits:
                    possibleValues = possibleValues.replace(columnValue, '')
                lineValue = grid.get(squareLine[index])
                if lineValue in digits:
                    possibleValues = possibleValues.replace(lineValue, '')
                if len(squareBox) > 0:
                    boxValue = grid.get(squareBox[index])
                    if boxValue in digits:
                        possibleValues = possibleValues.replace(boxValue, '')
            dictPossibleValues[square] = possibleValues
    return dictPossibleValues

def convertCandidatesGridToNormalGrid(candidatesGrid):
    normalGrid = candidatesGrid.copy()
    for square, candidateValues in candidatesGrid.items():
        if len(candidateValues) > 1:
            normalGrid[square] = '0'
    return normalGrid

def assign(grid, square, value):
    grid[square] = value
    return grid

# Main algorithm of Single Candidate technique
def singleCandidate(grid, square):
    squareUnit = units.get(square)
    squareColumn = squareUnit[0]
    squareLine = squareUnit[1]
    noBox = False
    try:
        squareBox = squareUnit[2]
    except IndexError:
        squareBox = []
        noBox = True
    possibleDigits = digits
    for index, x in enumerate(squareLine):
        possibleDigits = possibleDigits.replace(grid.get(squareLine[index]), '')
        possibleDigits = possibleDigits.replace(grid.get(squareColumn[index]), '')
        if not noBox:
            possibleDigits = possibleDigits.replace(grid.get(squareBox[index]), '')
    #if there is only one possibility, assign it to grid
    if len(possibleDigits) == 1:
        grid = assign(grid, square, possibleDigits)
    return grid

# Main algorithm of Single Position technique
def singlePosition(grid, unit):
    remainingDigits = digits
    remainingSquares = unit.copy()
    for square in unit:
        digitInSquare = grid.get(square)
        if digitInSquare in digits:
            remainingDigits = remainingDigits.replace(digitInSquare, '')
            remainingSquares.remove(square)
    
    for remainingDigit in remainingDigits:
        validSquares = []
        for remainingSquare in remainingSquares:
            squareUnit = units.get(remainingSquare)
            squareColumn = squareUnit[0]
            squareLine = squareUnit[1]
            squareBox = squareUnit[2]
            for index, x in enumerate(squareLine):
                if grid.get(squareColumn[index]) == remainingDigit or grid.get(squareLine[index]) == remainingDigit or grid.get(squareBox[index]) == remainingDigit:
                    break
            else:
                validSquares.append(remainingSquare)
        
        if len(validSquares) == 1:
            grid = assign(grid, validSquares[0], remainingDigit)
    
    return grid

# Main algorithm of Candidate Lines technique
def candidateLines(candidatesGrid, box):
    squareCandidates = []
    validDigits = digits
    for square in box:
        value = candidatesGrid.get(square)
        if len(value) > 1:
            squareCandidates.append(square)
        else:
            validDigits = validDigits.replace(value, '')
    for validDigit in validDigits:
        squaresWithDigit = []
        for squareCandidate in squareCandidates:
            value = candidatesGrid.get(squareCandidate)
            if validDigit in value:
                squaresWithDigit.append(squareCandidate)
        
        if len(squaresWithDigit) == 2:
            square1Column = units.get(squaresWithDigit[0])[0]
            square1Line = units.get(squaresWithDigit[0])[1]
            square2Column = units.get(squaresWithDigit[1])[0]
            square2Line = units.get(squaresWithDigit[1])[1]
            
            candidate = []
            if squaresWithDigit[0] in square2Column:
                candidate = square2Column
            elif squaresWithDigit[0] in square2Line:
                candidate = square2Line
            elif squaresWithDigit[1] in square1Column:
                candidate = square1Column
            elif squaresWithDigit[1] in square1Line:
                candidate = square1Line

            for square in candidate:
                values = candidatesGrid.get(square)
                if len(values) > 1 and validDigit in values and square not in squaresWithDigit:
                    candidatesGrid[square] = values.replace(validDigit, '')
    return candidatesGrid

# Main algorithm of Naked Pairs technique(also known as Disjoint Subsets)
def nakedPairs(candidatesGrid, line):
    twoCandidatesValues = [candidatesGrid.get(square) for square in line if len(candidatesGrid.get(square)) == 2]
    nakedPair = [twoCandidatesValue for twoCandidatesValue in twoCandidatesValues if twoCandidatesValues.count(twoCandidatesValue) == 2]
    if len(nakedPair) > 0:
        nakedPair = nakedPair[0]
        for square in line:
            value = candidatesGrid.get(square)
            if value != nakedPair:
                value = value.replace(nakedPair[0], '')
                value = value.replace(nakedPair[1], '')
                candidatesGrid[square] = value
    return candidatesGrid

# Main algorithm of Naked Triples technique(also known as Disjoint Subsets)
# both algorithms could be just one...
def nakedTriples(candidatesGrid, line):
    twoCandidatesValues = [candidatesGrid.get(square) for square in line if len(candidatesGrid.get(square)) == 3]
    nakedPair = [twoCandidatesValue for twoCandidatesValue in twoCandidatesValues if twoCandidatesValues.count(twoCandidatesValue) == 3]
    if len(nakedPair) > 0:
        nakedPair = nakedPair[0]
        for square in line:
            value = candidatesGrid.get(square)
            if value != nakedPair:
                value = value.replace(nakedPair[0], '')
                value = value.replace(nakedPair[1], '')
                value = value.replace(nakedPair[2], '')
                candidatesGrid[square] = value
    return candidatesGrid

# Check if a position in a matrix representation grid is valid
def isValidPosition(line, column, symbol, matrixGrid):
    for index in range(N):
        if matrixGrid[line][index] == symbol:
            return False
        
    for index in range(N):
        if matrixGrid[index][column] == symbol:
            return False
    
    firstRegion = regions[0]
    letters = []
    numbers = []
    for cell in firstRegion:
        if cell[0] not in letters:
            letters.append(cell[0])
        if cell[1] not in numbers:
            numbers.append(cell[1])
        
    lines = len(letters)
    columns = len(numbers)

    start_row = (line//lines) * lines
    start_col = (column//columns) * columns
    for indexLine in range(lines):
        for indexColumn in range(columns):
            if matrixGrid[start_row+indexLine][start_col+indexColumn] == symbol:
                return False
    return True

# Count how many solutions the given Sudoku(matrix representation) has
def countSolutions(line, column, matrixGrid, solutions):
    if line == N:
        line = 0
        column += 1
        if column == N:
            return solutions + 1
    if matrixGrid[line][column] != 0:
        return countSolutions(line + 1, column, matrixGrid, solutions)
    
    for symbol in range(1, N+1):
        if solutions < 2 and isValidPosition(line, column, symbol, matrixGrid):
            matrixGrid[line][column] = symbol
            solutions = countSolutions(line + 1, column, matrixGrid, solutions)
    matrixGrid[line][column] = 0
    return solutions

# Main algorithm to solve Sudokus
def solve(grid, isValidator):
    currentGrid = grid.copy()
    tryAgain = True
    useDedutiveTechs = False
    
    #tries single position and single candidate techniques
    while tryAgain:
        tryAgain = False
        for square, value in currentGrid.items():
            if value == '0':
                gridBeforeTech = currentGrid.copy()
                currentGrid = singleCandidate(currentGrid, square)
                if gridBeforeTech != currentGrid and not tryAgain:
                    tryAgain = True
        for unit in unitlist:
            gridBeforeTech = currentGrid.copy()
            currentGrid = singlePosition(currentGrid, unit)
            if gridBeforeTech != currentGrid and not tryAgain:
                tryAgain = True
        if isSolved(currentGrid):
            break

        #if the techniques were not enough, use dedutive techniques to reduce candidates
        if not tryAgain and not useDedutiveTechs:
            useDedutiveTechs = True
        if useDedutiveTechs:
            beforeGrid = currentGrid.copy()
            candidatesCurrentGrid = createCandidatesGrid(currentGrid)
            for region in regions:
                candidatesCurrentGrid = candidateLines(candidatesCurrentGrid, region)
            for line in lines:
                candidatesCurrentGrid = nakedPairs(candidatesCurrentGrid, line)
                candidatesCurrentGrid = nakedTriples(candidatesCurrentGrid, line)
            for column in columns:
                candidatesCurrentGrid = nakedPairs(candidatesCurrentGrid, column)
                candidatesCurrentGrid = nakedTriples(candidatesCurrentGrid, column)
            currentGrid = convertCandidatesGridToNormalGrid(candidatesCurrentGrid)
            if beforeGrid != currentGrid and not tryAgain:
                tryAgain = True

    if isSolved(currentGrid) and not useDedutiveTechs:
        return currentGrid, Difficulty.EASY.name
    elif isSolved(currentGrid) and useDedutiveTechs:
        return currentGrid, Difficulty.MEDIUM.name
    else:
        if not isValidator:
            currentGrid = restrictionPropagation(toString(currentGrid))
        return currentGrid, Difficulty.HARD.name
        
######### PRE PROCESSING SUDOKU STRUCTURE #########
def createDigits(n):
    return numbers[0:n]

def createRows(n):
    return alphabet[:n]

def createUnitList(n):
    #as far as I know, Sudokus of grade 3 or less doesnt have any regions('boxes')
    if n <= 3:
        boxesLetters = ()
        boxesDigits = ()
    else:
        # this will generate boxes(regions) of the Sudoku given its size
        boxWidth = 0
        boxHeight = 0
        lowestDifference = n
        valuesUntilN = list(number for number in range(1,n))
        for firstNumber in valuesUntilN:
            for secondNumber in valuesUntilN:
                if firstNumber * secondNumber == n and abs(firstNumber - secondNumber) < lowestDifference:
                    boxWidth = firstNumber
                    boxHeight = secondNumber
                    lowestDifference = abs(firstNumber - secondNumber)
        boxesLetters = tuple([alphabet[i:i+boxWidth] for i in range(0, boxHeight * boxWidth, boxWidth)])
        boxesDigits = tuple([digits[i:i+boxHeight] for i in range(0, boxHeight * boxWidth, boxHeight)])
        global lines
        global columns
        global regions
        lines = [cross(rows, c) for c in cols]
        columns = [cross(r, cols) for r in rows]
        regions = [cross(rs, cs) for rs in boxesLetters for cs in boxesDigits]
    return (lines + columns + regions)
    
# use this N variable to change between sudoku sizes
# N = 6 for 6x6 sudokus, N = 9 for 9x9 sudokus, etc
N = 6
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '123456789ABCDEF'
digits = createDigits(N)
rows     = createRows(N)
cols     = digits
lines = []
columns = []
regions  = []
squares  = cross(rows, cols)

unitlist = createUnitList(N)

units = dict((s, [u for u in unitlist if s in u]) 
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)
           
# some Sudokus example
'''
grid1 = "400000805030000000000700000020000060000080400000010000000603070500200000104000000"
grid2 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
grid3 = '005300000800000020070010500400005300010070006003200080060500009004000030000009700'
grid4 = '835416927296857431410293658569134782123678549748529163652781394981345276374962815'

grid5 = '030006089070900004000130025300420856050769030461053002720014000500008060980200040'
grid6 = '006030708030000001200000600100350006079040150500017004002000007600000080407060200'
grid7 = '000423005760000040500900821429000000000602000000000132845009007010000056900251000'
grid8 = '001957063000806070769130805007261350312495786056378000108609507090710608674583000'

grid2x2 = '2110'
grid3x3 = '100020000'
grid4x4 = '3204143203210143'
grid4x4solved = '3214143243212143'
grid6x6 = '614035523614241560365421152346430152'
grid6x6solved = '614235523614241563365421152346436152'
'''
