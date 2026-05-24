# gui.py
# This is the Graphical User Interface (GUI) for the game using PyQt6.
# It is designed with a modern dark theme and a live diagnostics panel for the Minimax AI.

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QComboBox, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# Import game logic and Minimax algorithm from game_logic
from game_logic import TicTacToeGame, find_best_move
import game_logic

class TicTacToeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = TicTacToeGame()
        self.ai_player = 'O'
        self.human_player = 'X'
        self.current_turn = 'X' # The player who starts first
        self.is_game_over = False
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Tic-Tac-Toe AI (Minimax Algorithm)")
        self.setMinimumSize(850, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0e14; /* Dark space background */
            }
            QLabel {
                color: #c9d1d9;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QComboBox {
                background-color: #1f293d;
                border: 2px solid #2d3d5a;
                border-radius: 8px;
                color: #ffffff;
                padding: 6px 12px;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
            }
            QComboBox:hover {
                border: 2px solid #00f0ff;
            }
            QComboBox QAbstractItemView {
                background-color: #1f293d;
                color: #ffffff;
                selection-background-color: #00f0ff;
                selection-color: #0b0e14;
            }
            QPushButton#reset_btn {
                background-color: #ff5e62;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#reset_btn:hover {
                background-color: #ff7b7f;
            }
            QPushButton#reset_btn:pressed {
                background-color: #d14b4f;
            }
        """)

        # Main widget and general layout (horizontal layout splitting the window into two columns)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # =====================================================================
        # Left Column: Game Board Panel
        # =====================================================================
        left_panel = QVBoxLayout()
        
        # Elegant top title
        title_label = QLabel("TIC-TAC-TOE AI")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #00f0ff; margin-bottom: 5px;") # Cyan neon color
        left_panel.addWidget(title_label)
        
        # Current turn indicator
        self.status_label = QLabel("No risk, no fun! 🤭")
        self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #8b949e; margin-bottom: 15px;")
        left_panel.addWidget(self.status_label)

        # 3x3 game board grid
        self.board_grid = QGridLayout()
        self.board_grid.setSpacing(10)
        self.buttons = []
        
        for i in range(9):
            btn = QPushButton("")
            btn.setObjectName(f"cell_{i}")
            btn.setFixedSize(120, 120)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
            
            # Style grid buttons with QSS (glow and elegant rounded borders)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #151b26;
                    border: 2px solid #2d3d5a;
                    border-radius: 15px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #1f2a3d;
                    border: 2px solid #00f0ff; /* Blue glow on hover */
                }
                QPushButton:pressed {
                    background-color: #0b0e14;
                }
            """)
            
            # Connect button click event
            btn.clicked.connect(lambda checked, idx=i: self.cell_clicked(idx))
            self.buttons.append(btn)
            
            row, col = divmod(i, 3)
            self.board_grid.addWidget(btn, row, col)
            
        left_panel.addLayout(self.board_grid)
        left_panel.addStretch()
        
        # =====================================================================
        # Right Column: Control & Diagnostics Panel
        # =====================================================================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        # --- Game Settings Group ---
        settings_group = QGroupBox("Game Settings")
        settings_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        settings_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2d3d5a;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                color: #00f0ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(10)
        
        # Difficulty Level
        diff_layout = QHBoxLayout()
        diff_label = QLabel("Difficulty Level:")
        diff_label.setFont(QFont("Segoe UI", 11))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Hard (Unbeatable)", "Medium (Depth Limit=2)", "Easy (Random)"])
        diff_layout.addWidget(diff_label)
        diff_layout.addWidget(self.diff_combo)
        settings_layout.addLayout(diff_layout)
        
        # Start Selection
        start_layout = QHBoxLayout()
        start_label = QLabel("Who starts first?")
        start_label.setFont(QFont("Segoe UI", 11))
        self.start_combo = QComboBox()
        self.start_combo.addItems(["Player (X)", "AI (O)"])
        self.start_combo.currentIndexChanged.connect(self.starting_player_changed)
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_combo)
        settings_layout.addLayout(start_layout)
        
        right_panel.addWidget(settings_group)
        
        # --- Minimax Diagnostics Panel ---
        diagnostics_group = QGroupBox("Minimax Diagnostics")
        diagnostics_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        diagnostics_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2d3d5a;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                color: #ff5e62; /* Neon orange/red color */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        diag_layout = QVBoxLayout(diagnostics_group)
        diag_layout.setSpacing(12)
        
        # States Explored
        states_title = QLabel("🔍 States Explored:")
        states_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.states_val = QLabel("0 states")
        self.states_val.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self.states_val.setStyleSheet("color: #00f0ff; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #2d3d5a;")
        diag_layout.addWidget(states_title)
        diag_layout.addWidget(self.states_val)
        
        # Evaluation Score
        score_title = QLabel("📊 Evaluation Score:")
        score_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.score_val = QLabel("AI has not played yet")
        self.score_val.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.score_val.setStyleSheet("color: #ff5e62; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #2d3d5a;")
        diag_layout.addWidget(score_title)
        diag_layout.addWidget(self.score_val)
        
        # AI Decision
        expl_title = QLabel("💡 AI Decision Explainer:")
        expl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.expl_val = QLabel("Waiting for your first move to start analysis...")
        self.expl_val.setWordWrap(True)
        self.expl_val.setFont(QFont("Segoe UI", 10))
        self.expl_val.setStyleSheet("color: #8b949e; background-color: #151b26; padding: 10px; border-radius: 6px; border: 1px solid #2d3d5a;")
        self.expl_val.setMinimumHeight(80)
        diag_layout.addWidget(expl_title)
        diag_layout.addWidget(self.expl_val)
        
        right_panel.addWidget(diagnostics_group)
        
        # Reset Button
        self.reset_button = QPushButton("Reset Game 🔄")
        self.reset_button.setObjectName("reset_btn")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_button.clicked.connect(self.reset_game)
        right_panel.addWidget(self.reset_button)
        
        # Add columns to main layout
        main_layout.addLayout(left_panel, stretch=3)
        main_layout.addLayout(right_panel, stretch=2)

    def starting_player_changed(self):
        """Handle changes to the starting player"""
        self.reset_game()

    def cell_clicked(self, idx):
        """Handle cell click by the human player"""
        if self.is_game_over or self.current_turn != self.human_player or self.game.board[idx] != " ":
            return
            
        # 1. Execute human move
        self.game.make_move(idx, self.human_player)
        self.update_board_ui()
        
        winner = self.game.check_winner()
        if winner:
            self.handle_game_over(winner)
            return
            
        # 2. Switch turn to AI
        self.current_turn = self.ai_player
        self.status_label.setText("AI is thinking... 🧠")
        self.status_label.setStyleSheet("color: #ff5e62;")
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        QTimer.singleShot(400, self.ai_turn)

    def ai_turn(self):
        """Execute AI turn using Minimax"""
        QApplication.restoreOverrideCursor()
        
        if self.is_game_over:
            return
            
        # Get selected difficulty
        difficulty_text = self.diff_combo.currentText()
        if "Hard" in difficulty_text:
            difficulty = "Hard"
        elif "Medium" in difficulty_text:
            difficulty = "Medium"
        else:
            difficulty = "Easy"
            
        # Search for the best move
        best_move, score = find_best_move(self.game, self.ai_player, self.human_player, difficulty)
        
        if best_move is not None:
            # Make the move
            self.game.make_move(best_move, self.ai_player)
            self.update_board_ui()
            
            # Update diagnostic panel
            self.update_diagnostics_ui(best_move, score, difficulty)
            
            # Check winner/tie after AI move
            winner = self.game.check_winner()
            if winner:
                self.handle_game_over(winner)
                return
                
            # Return turn to human player
            self.current_turn = self.human_player
            self.status_label.setText("Your turn, Boss! Play X")
            self.status_label.setStyleSheet("color: #8b949e;")

    def update_board_ui(self):
        """Update board buttons UI based on current board state"""
        for i in range(9):
            val = self.game.board[i]
            self.buttons[i].setText(val)
            
            # Unique styling based on player
            if val == 'X':
                self.buttons[i].setStyleSheet("""
                    QPushButton {
                        background-color: #151b26;
                        border: 2px solid #00f0ff; /* Neon cyan border */
                        border-radius: 15px;
                        color: #00f0ff; /* Neon cyan color */
                    }
                """)
            elif val == 'O':
                self.buttons[i].setStyleSheet("""
                    QPushButton {
                        background-color: #151b26;
                        border: 2px solid #ff5e62; /* Neon red/pink border */
                        border-radius: 15px;
                        color: #ff5e62; /* Neon red/pink color */
                    }
                """)
            else:
                # Empty cell
                self.buttons[i].setStyleSheet("""
                    QPushButton {
                        background-color: #151b26;
                        border: 2px solid #2d3d5a;
                        border-radius: 15px;
                        color: #ffffff;
                    }
                    QPushButton:hover {
                        background-color: #1f2a3d;
                        border: 2px solid #00f0ff;
                    }
                """)

    def update_diagnostics_ui(self, move, score, difficulty):
        """Update the diagnostic UI panel to show the algorithm details"""
        # 1. Update states explored
        self.states_val.setText(f"{game_logic.states_explored:,} states")
        
        # 2. Update math evaluation score
        if difficulty == "Easy":
            self.score_val.setText("Disabled (Random Move)")
            self.score_val.setStyleSheet("color: #8b949e; background-color: #151b26; padding: 6px; border-radius: 6px;")
            self.expl_val.setText("In Easy mode, the algorithm does not look ahead. It simply chooses a random empty cell to make the game easier.")
            return
            
        score_text = ""
        score_style = ""
        explanation_text = ""
        
        if score == 1:
            score_text = "+1 (Guaranteed AI Win - MAX)"
            score_style = "color: #4ade80; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #4ade80;"
        elif score == -1:
            score_text = "-1 (Guaranteed Player Win - MIN)"
            score_style = "color: #f87171; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #f87171;"
        else:
            score_text = "0 (Guaranteed Draw under optimal play)"
            score_style = "color: #fbbf24; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #fbbf24;"
            
        self.score_val.setText(score_text)
        self.score_val.setStyleSheet(score_style)
        
        # 3. Formulate the explanation for the AI move
        move_name = f"Cell #{move + 1}"
        
        if difficulty == "Medium":
            explanation_text = f"Since difficulty is 'Medium' (Heuristic Mode), I searched only 2 levels deep (Depth Limit = 2) to avoid combinatorial explosion. I chose {move_name} as the best heuristic move for now."
        else:
            # Hard Difficulty: Full Search
            if score == 0:
                explanation_text = f"I explored all possible scenarios ({game_logic.states_explored:,} combinations) and found that playing in {move_name} is the optimal choice to guarantee at least a draw and prevent you from forming a winning plan."
            elif score == 1:
                explanation_text = f"Great! The algorithm detected a flaw in your strategy and analyzed {game_logic.states_explored:,} possibilities to secure a guaranteed win. Played in {move_name} to complete the winning path."
            else:
                explanation_text = f"The algorithm is in trouble! Assuming you play optimally, the AI expects a loss (-1). Played in {move_name} to prolong the game as much as possible."
                
        self.expl_val.setText(explanation_text)

    def handle_game_over(self, winner):
        """Handle game over condition and winner declaration"""
        self.is_game_over = True
        
        # Disable all buttons
        for btn in self.buttons:
            btn.setCursor(Qt.CursorShape.ArrowCursor)
            
        if winner == "Tie":
            self.status_label.setText("It's a draw! 🙉")
            self.status_label.setStyleSheet("color: #fbbf24; font-weight: bold; font-size: 18px;")
            self.expl_val.setText("The game ended in a guaranteed draw. This is what always happens when both sides play with perfect intelligence in Tic-Tac-Toe!")
        else:
            if winner == self.human_player:
                self.status_label.setText("Well done! 😂")
                self.status_label.setStyleSheet("color: #4ade80; font-weight: bold; font-size: 18px;")
                self.expl_val.setText("Awesome! You won! (Note: You can never beat the Hard level. Try Easy or Medium levels to see the difference!)")
            else:
                self.status_label.setText("Alright, thanks, that's enough 🙄")
                self.status_label.setStyleSheet("color: #f87171; font-weight: bold; font-size: 18px;")
                self.expl_val.setText("The computer is the winner! The Minimax algorithm prevailed by exploring the game tree and finding the path to a guaranteed win without making any mistakes.")

    def reset_game(self):
        """Reset the game and start a new match"""
        self.game.reset()
        self.is_game_over = False
        
        # Clear board buttons and restore pointers/cursors
        for btn in self.buttons:
            btn.setText("")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.update_board_ui()
        
        # Restore diagnostic and analysis board values
        self.states_val.setText("0 states")
        self.score_val.setText("Waiting for game to start")
        self.score_val.setStyleSheet("color: #8b949e; background-color: #151b26; padding: 6px; border-radius: 6px; border: 1px solid #2d3d5a;")
        self.expl_val.setText("Waiting for your first move to start analysis...")
        
        # Determine who starts
        starting_option = self.start_combo.currentText()
        if "Player" in starting_option:
            self.current_turn = self.human_player
            self.status_label.setText("Your turn! Play with X")
            self.status_label.setStyleSheet("color: #8b949e;")
        else:
            self.current_turn = self.ai_player
            self.status_label.setText("AI is thinking... 🧠")
            self.status_label.setStyleSheet("color: #ff5e62;")
            # Start AI turn with a small delay
            QTimer.singleShot(400, self.ai_turn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set layout direction to LeftToRight for English layout orientation
    app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    
    gui = TicTacToeGUI()
    gui.show()
    sys.exit(app.exec())
