import random
import operator

class Equation:
    def __init__(self, parts, result):
        self.parts = parts  # Список чисел и операторов, например, [3, '+', 5]
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

        # Простая логика генерации (заглушка для более сложной логики пересечений)
        # В реальном кроссворде нам нужно вписываться в существующие числа.
        # Пока просто генерируем отдельные допустимые уравнения.
        
        parts = []
        current_val = random.randint(1, max_val)
        parts.append(current_val)
        
        for _ in range(num_ops):
            op_sym = random.choice(allowed_ops)
            op_func = ops[op_sym]
            
            # Попытка найти допустимое следующее число
            valid = False
            for _ in range(20):
                next_val = random.randint(1, max_val)
                # Избегаем деления на ноль и нецелых результатов
                if op_sym == '/' and (next_val == 0 or current_val % next_val != 0):
                    continue
                # Избегаем отрицательных или нулевых результатов
                if op_sym == '-' and current_val - next_val <= 0:
                    continue
                    
                temp_result = int(op_func(current_val, next_val))
                # Убеждаемся, что результат не равен нулю
                if temp_result == 0:
                    continue
                    
                parts.append(op_sym)
                parts.append(next_val)
                current_val = temp_result
                valid = True
                break
            
            if not valid:
                # Откат или повторная попытка (упрощено)
                return Equation.generate(difficulty)

        return Equation(parts, current_val)

class CrossMathGrid:
    def __init__(self, size):
        self.size = size
        # Сетка хранит кортежи: (значение, тип), где тип - 'number', 'operator', 'equals'
        # значение может быть int или str
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.equations = []

    def is_valid_pos(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def can_place(self, equation, r, c, direction):
        # направление: (dr, dc), например, (0, 1) для горизонтального, (1, 0) для вертикального
        dr, dc = direction
        parts = equation.parts + ['=', equation.result]
        length = len(parts)
        
        # Проверка границ
        if not self.is_valid_pos(r, c):
            return False
            
        end_r = r + (length - 1) * dr
        end_c = c + (length - 1) * dc
        if not self.is_valid_pos(end_r, end_c):
            return False

        # Проверка перед началом и после конца (чтобы убедиться, что мы не расширяем существующее уравнение)
        before_r, before_c = r - dr, c - dc
        if self.is_valid_pos(before_r, before_c) and self.grid[before_r][before_c] is not None:
            return False
            
        after_r, after_c = end_r + dr, end_c + dc
        if self.is_valid_pos(after_r, after_c) and self.grid[after_r][after_c] is not None:
            return False

        # Проверка пересечений и смежности
        for i, part in enumerate(parts):
            curr_r, curr_c = r + i * dr, c + i * dc
            cell = self.grid[curr_r][curr_c]
            
            if cell is not None:
                # Если ячейка занята, она должна точно совпадать
                if cell[0] != part:
                    return False
            else:
                # Если ячейка пуста, проверяем перпендикулярных соседей
                # Перпендикулярные векторы: (dc, dr) и (-dc, -dr)
                # Если направление (0, 1) [горизонтально], перп. (1, 0) и (-1, 0) [вертикально]
                # Если направление (1, 0) [вертикально], перп. (0, 1) и (0, -1) [горизонтально]
                
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
            # Определение типа
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
        
        # 1. Разместить начальное уравнение в центре (горизонтально)
        attempts = 0
        while attempts < 100:
            eq = Equation.generate(difficulty)
            # Рассчитать длину
            length = len(eq.parts) + 2 # +2 для '=' и результата
            
            # Центрировать
            r = size // 2
            c = (size - length) // 2
            
            if c >= 0:
                grid.place_equation(eq, r, c, (0, 1))
                break
            attempts += 1
            
        if not grid.equations:
            return None # Не удалось начать

        # 2. Попытаться добавить больше уравнений, пересекающих существующие
        # Мы ищем числа в сетке и пытаемся строить перпендикулярные уравнения от них
        
        count = 1
        failures = 0
        while count < num_equations and failures < 50:
            # Выбрать случайную существующую ячейку с числом
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
            
            # Определить направление (перпендикулярно существующему уравнению в этой ячейке? 
            # На самом деле, ячейка может быть частью H и V. Если так, пропустить.)
            # Простая проверка: посмотреть на соседей.
            has_h_neighbor = (grid.is_valid_pos(r, c-1) and grid.grid[r][c-1]) or \
                             (grid.is_valid_pos(r, c+1) and grid.grid[r][c+1])
            has_v_neighbor = (grid.is_valid_pos(r-1, c) and grid.grid[r-1][c]) or \
                             (grid.is_valid_pos(r+1, c) and grid.grid[r+1][c])
                             
            if has_h_neighbor and has_v_neighbor:
                failures += 1
                continue # Уже пересекается
            
            direction = (1, 0) if has_h_neighbor else (0, 1)
            
            # Сгенерировать уравнение, содержащее 'val' в какой-то позиции
            # Это трудно. Вместо этого давайте просто генерируем случайные уравнения и видим, подходят ли они
            # так, чтобы пересечение выравнивалось.
            # ИЛИ: Сгенерировать уравнение, найти где 'val' в нём, и выравнять.
            
            new_eq = Equation.generate(difficulty)
            parts = new_eq.parts + ['=', new_eq.result]
            
            # Найти индексы, где 'val' появляется в new_eq
            match_indices = [i for i, x in enumerate(parts) if x == val]
            
            if not match_indices:
                failures += 1
                continue
            
            placed = False
            random.shuffle(match_indices)
            for idx in match_indices:
                # Рассчитать начальную позицию, если выравнять parts[idx] в (r, c)
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
        # Удалить числа для создания головоломки
        # Возвращает: 
        # - модифицированная сетка (с None для ячеек)
        # - список удалённых чисел (банк)
        
        # Процент чисел для удаления
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
        
        # Первый проход: удаление на основе вероятности
        for r in range(grid.size):
            for c in range(grid.size):
                cell = grid.grid[r][c]
                if cell:
                    val, type_ = cell
                    if type_ == 'number' and random.random() < prob:
                        # Удалить
                        removed_numbers.append(val)
                        playable_grid[r][c] = (None, 'empty_number') # Заполнитель для перетаскивания
                    else:
                        playable_grid[r][c] = cell

        # Гарантировать, что удалено по крайней мере 2 числа
        while len(removed_numbers) < 2:
            # Найти все оставшиеся числа
            candidates = []
            for r in range(grid.size):
                for c in range(grid.size):
                    cell = playable_grid[r][c]
                    if cell and cell[1] == 'number':
                        candidates.append((r, c))
            
            if not candidates:
                break # Больше нет чисел для удаления
                
            # Выбрать одно для удаления
            r, c = random.choice(candidates)
            val = playable_grid[r][c][0]
            removed_numbers.append(val)
            playable_grid[r][c] = (None, 'empty_number')
        
        removed_numbers.sort()
        return playable_grid, removed_numbers
