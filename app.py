from flask import Flask, render_template, request, jsonify, session
import json
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.human = 'O'
        self.ai = 'X'
        self.game_over = False
        self.winner = None
        
    def print_board(self):
        return {
            'board': self.board,
            'game_over': self.game_over,
            'winner': self.winner
        }
    
    def is_winner(self, player):
        win_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        return any(all(self.board[i] == player for i in combo) for combo in win_combos)
    
    def is_board_full(self):
        return ' ' not in self.board
    
    def get_empty_spaces(self):
        return [i for i in range(9) if self.board[i] == ' ']
    
    def minimax(self, depth, is_maximizing, alpha=float('-inf'), beta=float('inf')):
        if self.is_winner(self.ai):
            return 10 - depth
        if self.is_winner(self.human):
            return depth - 10
        if self.is_board_full():
            return 0
        
        if is_maximizing:
            best_score = float('-inf')
            for move in self.get_empty_spaces():
                self.board[move] = self.ai
                score = self.minimax(depth + 1, False, alpha, beta)
                self.board[move] = ' '
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score
        else:
            best_score = float('inf')
            for move in self.get_empty_spaces():
                self.board[move] = self.human
                score = self.minimax(depth + 1, True, alpha, beta)
                self.board[move] = ' '
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            return best_score
    
    def ai_move(self):
        best_score = float('-inf')
        best_move = None
        for move in self.get_empty_spaces():
            self.board[move] = self.ai
            score = self.minimax(0, False)
            self.board[move] = ' '
            if score > best_score:
                best_score = score
                best_move = move
        if best_move is not None:
            self.board[best_move] = self.ai
            if self.is_winner(self.ai):
                self.game_over = True
                self.winner = 'AI'
            elif self.is_board_full():
                self.game_over = True
                self.winner = 'Draw'
        return best_move
    
    def make_move(self, position):
        if self.board[position] == ' ':
            self.board[position] = self.human
            if self.is_winner(self.human):
                self.game_over = True
                self.winner = 'Human'
                return True
            elif self.is_board_full():
                self.game_over = True
                self.winner = 'Draw'
                return True
            return False
        return False

games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new-game', methods=['POST'])
def new_game():
    game_id = secrets.token_hex(8)
    games[game_id] = TicTacToe()
    return jsonify({'game_id': game_id, 'board': games[game_id].board})

@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data.get('game_id')
    position = data.get('position')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    if game.game_over:
        return jsonify({'error': 'Game is over'}), 400
    
    if game.make_move(position):
        return jsonify({
            'board': game.board,
            'game_over': game.game_over,
            'winner': game.winner
        })
    
    if not game.game_over:
        game.ai_move()
    
    return jsonify({
        'board': game.board,
        'game_over': game.game_over,
        'winner': game.winner
    })

@app.route('/api/game/<game_id>', methods=['GET'])
def get_game(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    game = games[game_id]
    return jsonify({
        'board': game.board,
        'game_over': game.game_over,
        'winner': game.winner
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
