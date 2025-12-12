from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QPushButton, QComboBox, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from game_logic import PuzzleGenerator
from widgets import DropCell, NumberBank

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Математический кроссворд")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left side: Game Board
        self.board_container = QWidget()
        self.board_layout = QVBoxLayout(self.board_container)
        
        # Center the grid horizontally
        self.grid_centering_layout = QHBoxLayout()
        self.grid_centering_layout.addStretch()
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.grid_centering_layout.addLayout(self.grid_layout)
        self.grid_centering_layout.addStretch()
        
        self.board_layout.addLayout(self.grid_centering_layout)
        self.board_layout.addStretch()
        
        # Right side: Controls and Number Bank
        self.controls_container = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_container)
        self.controls_container.setFixedWidth(250)

        # Difficulty Selector
        self.diff_label = QLabel("Сложность:")
        self.diff_combo = QComboBox()
        self.diff_map = {
            "Легко": "easy",
            "Средне": "medium",
            "Сложно": "hard",
            "Эксперт": "expert"
        }
        self.diff_combo.addItems(self.diff_map.keys())
        self.controls_layout.addWidget(self.diff_label)
        self.controls_layout.addWidget(self.diff_combo)

        # New Game Button
        self.new_game_btn = QPushButton("Новая игра")
        self.new_game_btn.clicked.connect(self.start_new_game)
        self.controls_layout.addWidget(self.new_game_btn)

        self.controls_layout.addSpacing(20)
        self.controls_layout.addWidget(QLabel("Доступные числа:"))
        
        # Number Bank
        self.number_bank = NumberBank()
        self.controls_layout.addWidget(self.number_bank)
        self.controls_layout.addStretch()

        self.main_layout.addWidget(self.board_container, stretch=1)
        self.main_layout.addWidget(self.controls_container)

        self.current_grid_state = None
        self.solution_grid = None
        self.cells = {} # Map (r, c) -> DropCell

        # Start initial game
        self.start_new_game()

    def start_new_game(self):
        diff_text = self.diff_combo.currentText()
        difficulty = self.diff_map.get(diff_text, "easy")
        
        # Generate puzzle
        # This might take a moment, could be threaded in a real app
        generated = PuzzleGenerator.generate_puzzle(difficulty)
        if not generated:
            QMessageBox.warning(self, "Error", "Failed to generate puzzle. Please try again.")
            return

        self.solution_grid = generated
        playable_grid, removed_numbers = PuzzleGenerator.create_playable_state(generated, difficulty)
        self.current_grid_state = playable_grid

        # Setup Grid UI
        self.clear_grid()
        
        size = len(playable_grid)
        for r in range(size):
            for c in range(size):
                cell_data = playable_grid[r][c]
                if cell_data:
                    val, type_ = cell_data
                    
                    cell_widget = DropCell(r, c, self)
                    cell_widget.dropped.connect(self.on_cell_dropped)
                    cell_widget.cleared.connect(self.on_cell_cleared)
                    self.cells[(r, c)] = cell_widget
                    
                    if type_ == 'empty_number':
                        # This is a hole
                        cell_widget.setStyleSheet(cell_widget.default_style)
                    else:
                        # This is a static part (operator, equals, or given number)
                        cell_widget.setText(str(val))
                        cell_widget.current_value = val # For validation
                        cell_widget.setAcceptDrops(False) # Cannot drop here
                        # Style differently for static content
                        cell_widget.setStyleSheet("""
                            QLabel {
                                background-color: #ddd;
                                border: 1px solid #999;
                                border-radius: 3px;
                                font-size: 14px;
                                font-weight: bold;
                                color: #000;
                            }
                        """)
                    
                    self.grid_layout.addWidget(cell_widget, r, c)
                else:
                    # Empty space, maybe add a spacer or just nothing
                    pass

        # Setup Number Bank
        self.number_bank.set_numbers(removed_numbers)

    def clear_grid(self):
        # Remove all widgets from grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.cells = {}

    def on_cell_dropped(self, r, c, value):
        # Callback from DropCell
        self.number_bank.remove_number(value)
        self.check_solution()

    def on_cell_cleared(self, value):
        self.number_bank.add_number(value)
        self.check_solution()

    def check_solution(self):
        if not self.solution_grid:
            return

        for r in range(self.solution_grid.size):
            for c in range(self.solution_grid.size):
                solution_cell = self.solution_grid.grid[r][c]
                if solution_cell:
                    sol_val = solution_cell[0]
                    
                    if (r, c) in self.cells:
                        cell_widget = self.cells[(r, c)]
                        user_val = cell_widget.current_value
                        
                        if cell_widget.acceptDrops() and user_val is not None:
                            if int(user_val) == int(sol_val):
                                cell_widget.setStyleSheet("""
                                    QLabel {
                                        background-color: #90EE90;
                                        border: 2px solid #228B22;
                                        border-radius: 5px;
                                        font-size: 18px;
                                        color: #000;
                                        font-weight: bold;
                                    }
                                """)
