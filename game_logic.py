# game_logic.py

class TicTacToeGame:
    def __init__(self):
        # 0 | 1 | 2
        # ----------
        # 3 | 4 | 5
        # ----------
        # 6 | 7 | 8
        self.board = [" "] * 9
        
    def reset(self):
        self.board = [" "] * 9

    def make_move(self, index, player):
        if self.board[index] == " ":
            self.board[index] = player
            return True
        return False

    def undo_move(self, index):#for backtrack
        self.board[index] = " "

    def get_empty_cells(self):
        return [i for i, cell in enumerate(self.board) if cell == " "]

    def check_winner(self):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  
            [0, 4, 8], [2, 4, 6]
        ]
        
        for combo in win_conditions:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != " ":
                return self.board[combo[0]] # return x or o 
                #the list is not empty  
        if " " not in self.board:
            return "Tie"
            
        # game still on
        return None


states_explored = 0

def minimax(game, depth, is_maximizing, ai_player, human_player):
    """
    1. Explore (Recursion)
    2. Score 
    3. Backtrack
       -  MAX (الذكاء الاصطناعي)
       -  MIN (الإنسان) 
    """
    global states_explored
    states_explored += 1 

    # ------------------ step 2: Score--> Terminal States) ------------------
    winner = game.check_winner()
    if winner == ai_player:
        return 1  
    if winner == human_player:
        return -1 
    if winner == "Tie":
        return 0  

    # ------------------ step 1 & 3: Explore & Backtrack ------------------
    if is_maximizing:#Ai turn
        best_score = float('-inf')
        for move in game.get_empty_cells():
            game.make_move(move, ai_player)
            score = minimax(game, depth + 1, False, ai_player, human_player)
            game.undo_move(move)
            best_score = max(score, best_score)
        return best_score
    else:#Human turn
        best_score = float('inf')
        for move in game.get_empty_cells():
            game.make_move(move, human_player)
            score = minimax(game, depth + 1, True, ai_player, human_player)
            game.undo_move(move)
            best_score = min(score, best_score)
        return best_score


def find_best_move(game, ai_player, human_player, difficulty="Hard"):
    """
    step 4: Decide 
    1. Easy 
    2. Medium 
    3. Hard 
    """
    global states_explored
    states_explored = 0 

    empty_cells = game.get_empty_cells()
    if not empty_cells:
        return None

    if difficulty == "Easy":
        import random
        states_explored = 1
        return random.choice(empty_cells), 0

    best_move = None
    best_score = float('-inf')
    
    for move in empty_cells:
        game.make_move(move, ai_player)
        
        # (depth_limit = 2)
        if difficulty == "Medium":
            score = minimax_with_depth_limit(game, 0, 2, False, ai_player, human_player)
        else:
            score = minimax(game, 0, False, ai_player, human_player)
            
        game.undo_move(move)

        if score > best_score:
            best_score = score
            best_move = move

    if best_move is None:
        best_move = empty_cells[0]

    return best_move, best_score


def minimax_with_depth_limit(game, depth, max_depth, is_maximizing, ai_player, human_player):

    global states_explored
    states_explored += 1

    winner = game.check_winner()
    if winner == ai_player:
        return 1
    if winner == human_player:
        return -1
    if winner == "Tie":
        return 0

    if depth >= max_depth:
        return 0

    if is_maximizing:
        best_score = float('-inf')
        for move in game.get_empty_cells():
            game.make_move(move, ai_player)
            score = minimax_with_depth_limit(game, depth + 1, max_depth, False, ai_player, human_player)
            game.undo_move(move)
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for move in game.get_empty_cells():
            game.make_move(move, human_player)
            score = minimax_with_depth_limit(game, depth + 1, max_depth, True, ai_player, human_player)
            game.undo_move(move)
            best_score = min(score, best_score)
        return best_score
