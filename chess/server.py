from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import random, string, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logic.board import Board
from logic.ai import get_best_move

app = Flask(__name__)
app.secret_key = 'chess'
socketio = SocketIO(app)

ai_games     = {}
online_games = {}

# ── Pages ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai')
def page_ai():
    return render_template('game.html', mode='ai')

@app.route('/online')
def page_online():
    return render_template('game.html', mode='online')

# ── AI ────────────────────────────────────────────────────────────────────────
# creates a new AI game
@app.route('/ai/new', methods=['POST'])
def ai_new():
    data = request.get_json(silent=True) or {}
    sid = data.get('session_id', 'default')
    board = Board()
    board.initialize_board()
    ai_games[sid] = board
    return jsonify(board_to_dict(board))

# shows all the possible moves
@app.route('/ai/moves', methods=['POST'])
def ai_moves():
    data = request.get_json(silent=True) or {}
    sid = data.get('session_id', 'default')
    row, col = data.get('row', 0), data.get('col', 0)
    board = ai_games.get(sid)
    if not board:
        return jsonify([])

    all_legal = board.get_all_legal_moves(board.turn)
    moves = [list(end) for start, end in all_legal if start == (row, col)]
    return jsonify(moves)

# executes the move and wait for AI
@app.route('/ai/move', methods=['POST'])
def ai_move():
    data = request.get_json(silent=True) or {}
    sid = data.get('session_id', 'default')
    start = tuple(data.get('start', [0, 0]))
    end = tuple(data.get('end', [0, 0]))
    promotion = data.get('promotion', 'queen')
    board = ai_games.get(sid)

    if not board:
        return jsonify({"error": "Game not found"}), 404
    board.move_piece(start, end, promotion_choice=promotion)

    if not board.is_checkmate(board.turn) and not board.is_stalemate(board.turn) and not board.is_insufficient_material():
        move = get_best_move(board, depth=2)
        if move:
            board.move_piece(*move)

    return jsonify({"board": board_to_dict(board)})

# ── Online ────────────────────────────────────────────────────────────────────

@app.route('/online/create', methods=['POST'])
def online_create():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=6))
        if code not in online_games:
            break
    board = Board()
    board.initialize_board()
    online_games[code] = {"board": board, "players": {}}
    print(f"[online] created room: {code}")
    return jsonify({"code": code})


@app.route('/online/join', methods=['POST'])
def online_join():
    data = request.get_json(silent=True) or {}
    code = data.get('code', '').upper().strip()
    if not code:
        return jsonify({"error": "Introduce a code"}), 400
    if code not in online_games:
        return jsonify({"error": f"The code '{code}' does not exist"}), 404
    if len(online_games[code]["players"]) >= 2:
        return jsonify({"error": "The room is full"}), 400
    return jsonify({"ok": True})


@socketio.on('join')
def on_join(data):
    code = data.get('code', '').upper().strip()
    game = online_games.get(code)
    if not game:
        emit('error_msg', {'msg': f"The room '{code}' does not exist"})
        return
    sid = request.sid
    join_room(code)
    color = 'white' if len(game['players']) == 0 else 'black'
    game['players'][sid] = color
    print(f"[online] {sid[:8]} joined {code} as {color}")
    emit('joined', {'color': color, 'board': board_to_dict(game['board'])})
    if len(game['players']) == 2:
        emit('start', {}, to=code)

# shows possible moves
@socketio.on('moves')
def on_moves(data):
    code = data.get('code', '').upper()
    row, col = data.get('row', 0), data.get('col', 0)
    game = online_games.get(code)
    if not game:
        emit('moves_result', [])
        return
    board = game['board']
    if board.turn != game['players'].get(request.sid):
        emit('moves_result', [])
        return
    all_legal = board.get_all_legal_moves(board.turn)
    moves = [list(end) for start, end in all_legal if start == (row, col)]
    emit('moves_result', moves)

# executes the move
@socketio.on('move')
def on_move(data):
    code = data.get('code', '').upper()
    start = tuple(data.get('start', [0, 0]))
    end = tuple(data.get('end', [0, 0]))
    promotion = data.get('promotion', 'queen')
    game = online_games.get(code)
    if not game:
        return
    board = game['board']
    if board.turn != game['players'].get(request.sid):
        return
    board.move_piece(start, end, promotion_choice=promotion)
    emit('update', board_to_dict(board), to=code)


@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    for code, game in list(online_games.items()):
        if sid in game['players']:
            del game['players'][sid]
            emit('opponent_left', {'msg': 'The opponent left. Game is over.'}, to=code)
            del online_games[code]
            print(f"[online] {sid[:8]} left {code}")
            break

# ── Utility──────────────────────────────────────────────────────────────────
def board_to_dict(board):
    grid = []
    for row in range(8):
        row_data = []
        for col in range(8):
            piece = board.grid[row][col]
            row_data.append({"type": piece.type, "color": piece.color} if piece else None)
        grid.append(row_data)
    return {
        "grid":                  grid,
        "turn":                  board.turn,
        "in_check":              board.in_check(board.turn),
        "checkmate":             board.is_checkmate(board.turn),
        "stalemate":             board.is_stalemate(board.turn),
        "draw":                  board.is_draw(),
    }

if __name__ == '__main__':
    print("Server at: http://localhost:5000")
    socketio.run(app, debug=True, port=5000)