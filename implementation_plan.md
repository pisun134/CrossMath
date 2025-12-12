# Cross Math Game Implementation Plan

## Goal Description
Implement a "Cross Math" game using PyQt6. The game features a crossword-style grid of math equations where some numbers are missing. Players must drag and drop numbers from a sorted list into the correct empty cells to solve the puzzle.

## User Review Required
> [!IMPORTANT]
> **Difficulty Levels**: I will define the difficulty levels as follows. Please confirm if this matches your expectation:
> - **Easy**: Small grid (e.g., 5x5), simple operations (+, -), single-operation equations.
> - **Medium**: Medium grid (e.g., 7x7), includes (*), mixed 1-2 operation equations.
> - **Hard**: Larger grid (e.g., 9x9), includes (/), mostly 2-operation equations.
> - **Expert**: Large grid (e.g., 11x11), all operations, complex intersections.

## Proposed Changes

### Core Logic
#### [NEW] [game_logic.py](file:///f:/WORKSPACE/Репетиторство/Ученики/Артём Овчаренко/CrossMath/game_logic.py)
- `Equation` class: Represents a single math equation (e.g., "3 + 5 = 8").
- `CrossMathGrid` class: Manages the 2D grid state, intersections, and validation.
- `PuzzleGenerator` class:
    - Generates a valid crossword layout of equations.
    - Handles difficulty scaling (grid size, operators, complexity).
    - Removes numbers to create "holes" for the player to fill.

### UI Components (PyQt6)
#### [NEW] [main_window.py](file:///f:/WORKSPACE/Репетиторство/Ученики/Артём Овчаренко/CrossMath/main_window.py)
- `MainWindow`: Main application window containing the grid and the number list.
- Difficulty selection menu/buttons.

#### [NEW] [widgets.py](file:///f:/WORKSPACE/Репетиторство/Ученики/Артём Овчаренко/CrossMath/widgets.py)
- `DraggableLabel`: A QLabel subclass that supports drag operations.
- `DropCell`: A widget representing a grid cell that accepts drops.
- `NumberBank`: A widget displaying the sorted list of available numbers.

### Entry Point
#### [NEW] [main.py](file:///f:/WORKSPACE/Репетиторство/Ученики/Артём Овчаренко/CrossMath/main.py)
- Application entry point.

## Verification Plan

### Automated Tests
- Unit tests for `Equation` generation to ensure mathematical correctness.
- Unit tests for `CrossMathGrid` to ensure equations intersect correctly.

### Manual Verification
- Run the application.
- Test Drag and Drop functionality:
    - Drag a number to an empty cell.
    - Drag a number back to the list (if allowed) or swap numbers.
- Verify "Win" condition when all cells are filled correctly.
- Check difficulty levels change the grid size and complexity.
