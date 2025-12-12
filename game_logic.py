import random
import operator

class Equation:
    def __init__(self, parts, result):
        self.parts = parts  # List of numbers and operators, e.g., [3, '+', 5]
        self.result = result

    def __str__(self):
        return f"{' '.join(map(str, self.parts))} = {self.result}"

    @staticmethod
    def generate(difficulty):
        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }
        
        if difficulty == 'easy':
            allowed_ops = ['+', '-']
            num_ops = 1
            max_val = 15
        elif difficulty == 'medium':
            allowed_ops = ['+', '-', '*']
            num_ops = random.choice([1, 2])
            max_val = 20
        elif difficulty == 'hard':
            allowed_ops = ['+', '-', '*', '/']
            num_ops = 2
            max_val = 30
        else:
            allowed_ops = ['+', '-', '*', '/']
            num_ops = random.choice([2, 3])
            max_val = 40

        # Simple generation logic (placeholder for more complex intersection logic)
        # In a real crossword, we need to fit into existing numbers. 
        # For now, just generating standalone valid equations.
        
        parts = []
        current_val = random.randint(1, max_val)
        parts.append(current_val)
        
        for _ in range(num_ops):
            op_sym = random.choice(allowed_ops)
            op_func = ops[op_sym]
            
            # Try to find a valid next number
            valid = False
            for _ in range(20):
                next_val = random.randint(1, max_val)
                # Avoid division by zero and non-integer results
                if op_sym == '/' and (next_val == 0 or current_val % next_val != 0):
                    continue
                # Avoid negative or zero results
                if op_sym == '-' and current_val - next_val <= 0:
                    continue
                    
                temp_result = int(op_func(current_val, next_val))
                # Ensure result is not zero
                if temp_result == 0:
                    continue
                    
                parts.append(op_sym)
                parts.append(next_val)
                current_val = temp_result
                valid = True
                break
            
            if not valid:
                # Fallback or retry (simplified)
                return Equation.generate(difficulty)

        return Equation(parts, current_val)

class CrossMathGrid:
    def __init__(self, size):
        self.size = size
        # Grid stores tuples: (value, type) where type is 'number', 'operator', 'equals'
        # value can be int or str
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.equations = []

    def is_valid_pos(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def can_place(self, equation, r, c, direction):
        # direction: (dr, dc) e.g., (0, 1) for horizontal, (1, 0) for vertical
        dr, dc = direction
        parts = equation.parts + ['=', equation.result]
        length = len(parts)
        
        # Check bounds
        if not self.is_valid_pos(r, c):
            return False
            
        end_r = r + (length - 1) * dr
        end_c = c + (length - 1) * dc
        if not self.is_valid_pos(end_r, end_c):
            return False

        # Check before start and after end (to ensure we don't extend an existing equation)
        before_r, before_c = r - dr, c - dc
        if self.is_valid_pos(before_r, before_c) and self.grid[before_r][before_c] is not None:
            return False
            
        after_r, after_c = end_r + dr, end_c + dc
        if self.is_valid_pos(after_r, after_c) and self.grid[after_r][after_c] is not None:
            return False

        # Check intersections and adjacency
        for i, part in enumerate(parts):
            curr_r, curr_c = r + i * dr, c + i * dc
            cell = self.grid[curr_r][curr_c]
            
            if cell is not None:
                # If cell is occupied, it must match exactly
                if cell[0] != part:
                    return False
            else:
                # If cell is empty, check perpendicular neighbors
                # Perpendicular vectors: (dc, dr) and (-dc, -dr)
                # If direction is (0, 1) [horiz], perp is (1, 0) and (-1, 0) [vert]
                # If direction is (1, 0) [vert], perp is (0, 1) and (0, -1) [horiz]
                
                p1_r, p1_c = curr_r + dc, curr_c + dr
                p2_r, p2_c = curr_r - dc, curr_c - dr
                
                if self.is_valid_pos(p1_r, p1_c) and self.grid[p1_r][p1_c] is not None:
                    return False
                if self.is_valid_pos(p2_r, p2_c) and self.grid[p2_r][p2_c] is not None:
                    return False
        
        return True

    def place_equation(self, equation, r, c, direction):
        dr, dc = direction
        parts = equation.parts + ['=', equation.result]
        
        for i, part in enumerate(parts):
            curr_r, curr_c = r + i * dr, c + i * dc
            # Determine type
            if isinstance(part, int):
                p_type = 'number'
            elif part == '=':
                p_type = 'equals'
            else:
                p_type = 'operator'
            
            self.grid[curr_r][curr_c] = (part, p_type)
        
        self.equations.append((equation, r, c, direction))

    def print_grid(self):
        for row in self.grid:
            line = ""
            for cell in row:
                if cell:
                    line += str(cell[0]).center(3)
                else:
                    line += " . "
            print(line)

class PuzzleGenerator:
    @staticmethod
    def generate_puzzle(difficulty):
        if difficulty == 'easy':
            size = 7
            num_equations = 4
        elif difficulty == 'medium':
            size = 9
            num_equations = 7
        elif difficulty == 'hard':
            size = 11
            num_equations = 12
        else:
            size = 13
            num_equations = 18

        grid = CrossMathGrid(size)
        
        # 1. Place initial equation in the center (horizontal)
        attempts = 0
        while attempts < 100:
            eq = Equation.generate(difficulty)
            # Calculate length
            length = len(eq.parts) + 2 # +2 for '=' and result
            
            # Center it
            r = size // 2
            c = (size - length) // 2
            
            if c >= 0:
                grid.place_equation(eq, r, c, (0, 1))
                break
            attempts += 1
            
        if not grid.equations:
            return None # Failed to start

        # 2. Try to add more equations intersecting existing ones
        # We look for numbers in the grid and try to build perpendicular equations from them
        
        count = 1
        failures = 0
        while count < num_equations and failures < 50:
            # Pick a random existing cell that is a number
            candidates = []
            for r in range(size):
                for c in range(size):
                    cell = grid.grid[r][c]
                    if cell and cell[1] == 'number':
                        candidates.append((r, c))
            
            if not candidates:
                break
                
            r, c = random.choice(candidates)
            val = grid.grid[r][c][0]
            
            # Determine direction (perpendicular to existing equation at this cell? 
            # Actually, a cell might be part of H and V. If so, skip.)
            # Simple check: look at neighbors.
            has_h_neighbor = (grid.is_valid_pos(r, c-1) and grid.grid[r][c-1]) or \
                             (grid.is_valid_pos(r, c+1) and grid.grid[r][c+1])
            has_v_neighbor = (grid.is_valid_pos(r-1, c) and grid.grid[r-1][c]) or \
                             (grid.is_valid_pos(r+1, c) and grid.grid[r+1][c])
                             
            if has_h_neighbor and has_v_neighbor:
                failures += 1
                continue # Already crossed
            
            direction = (1, 0) if has_h_neighbor else (0, 1)
            
            # Generate an equation that contains 'val' at some position
            # This is tricky. Instead, let's just generate random equations and see if they fit
            # such that the intersection aligns.
            # OR: Generate an equation, find where 'val' is in it, and align.
            
            new_eq = Equation.generate(difficulty)
            parts = new_eq.parts + ['=', new_eq.result]
            
            # Find indices where 'val' appears in new_eq
            match_indices = [i for i, x in enumerate(parts) if x == val]
            
            if not match_indices:
                failures += 1
                continue
            
            placed = False
            random.shuffle(match_indices)
            for idx in match_indices:
                # Calculate start pos if we align parts[idx] at (r, c)
                dr, dc = direction
                start_r = r - idx * dr
                start_c = c - idx * dc
                
                if grid.can_place(new_eq, start_r, start_c, direction):
                    grid.place_equation(new_eq, start_r, start_c, direction)
                    placed = True
                    count += 1
                    break
            
            if not placed:
                failures += 1

        return grid

    @staticmethod
    def create_playable_state(grid, difficulty):
        # Remove numbers to create the puzzle
        # Return: 
        # - modified grid (with None for holes)
        # - list of removed numbers (the bank)
        
        # Percentage of numbers to remove
        if difficulty == 'easy':
            prob = 0.4
        elif difficulty == 'medium':
            prob = 0.5
        elif difficulty == 'hard':
            prob = 0.6
        else:
            prob = 0.7
            
        removed_numbers = []
        playable_grid = [[None for _ in range(grid.size)] for _ in range(grid.size)]
        
        for r in range(grid.size):
            for c in range(grid.size):
                cell = grid.grid[r][c]
                if cell:
                    val, type_ = cell
                    if type_ == 'number' and random.random() < prob:
                        # Remove it
                        removed_numbers.append(val)
                        playable_grid[r][c] = (None, 'empty_number') # Placeholder for drop
                    else:
                        playable_grid[r][c] = cell
        
        removed_numbers.sort()
        return playable_grid, removed_numbers
