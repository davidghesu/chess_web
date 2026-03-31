// MODE is defined in game.html before this file is loaded

// ── State ──────────────────────────────────────────────────────────────────────
let board       = null;
let selected    = null;
let legalMoves  = [];
let sessionId   = Math.random().toString(36).slice(2);
let playerColor = null;
let roomCode    = null;
let gameActive  = false;
let pendingMove = null;

// ── Start ──────────────────────────────────────────────────────────────────────
if (MODE === 'ai') {
    playerColor = 'white';
    startNewGame();
}

function startNewGame() {
    fetch('/ai/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    })
        .then(r => r.json())
        .then(data => { board = data; gameActive = true; render(); });
}

// ── Board rendering ────────────────────────────────────────────────────────────
function render() {
    const container = document.getElementById('board');
    container.innerHTML = '';

    // reverse board for black
    const rows = playerColor === 'black' ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
    const cols = playerColor === 'black' ? [7,6,5,4,3,2,1,0] : [0,1,2,3,4,5,6,7];

    for (const row of rows) {
        for (const col of cols) {
            const sq = document.createElement('div');
            sq.className = 'square ' + ((row + col) % 2 === 0 ? 'dark' : 'light');

            if (selected && selected[0] === row && selected[1] === col)
                sq.classList.add('selected');
            if (legalMoves.some(m => m[0] === row && m[1] === col))
                sq.classList.add('legal');

            const piece = board.grid[row][col];  // local în render()
            if (piece) {
                const img = document.createElement('img');
                img.src = `/static/images/${piece.color}_${piece.type}.png`;
                img.alt = `${piece.color} ${piece.type}`;
                sq.appendChild(img);
            }

            sq.addEventListener('click', () => onClick(row, col));
            container.appendChild(sq);
        }
    }

    updateStatus();
}

function applyMoveLocally(start, end) {
    const piece = board.grid[start[0]][start[1]];
    board.grid[end[0]][end[1]] = piece;
    board.grid[start[0]][start[1]] = null;
    board.turn = 'black';
    selected   = null;
    legalMoves = [];
    render();
}

// ── Status ─────────────────────────────────────────────────────────────────────
function updateStatus() {
    const el = document.getElementById('status');
    el.className = '';
    if (!gameActive) return;

    if (board.checkmate) {
        el.textContent = `Checkmate! ${board.turn === 'white' ? 'Black' : 'White'} wins.`;
        el.className = 'alert';
        gameActive = false;
    } else if (board.stalemate) {
        el.textContent = 'Stalemate.';
        el.className = 'alert';
        gameActive = false;
    } else if (board.draw) {
        el.textContent = 'Draw.';
        el.className = 'alert';
        gameActive = false;
    } else if (board.in_check) {
        el.textContent = `${board.turn === 'white' ? 'White' : 'Black'} is in check!`;
        el.className = 'alert';
    } else if (MODE === 'online') {
        const isMyTurn = board.turn === playerColor;
        el.textContent = isMyTurn ? 'Your turn' : "Opponent's turn...";
        if (isMyTurn) el.className = 'my-turn';
    } else {
        el.textContent = `Turn: ${board.turn === 'white' ? 'White' : 'Black'}`;
        if (board.turn === playerColor) el.className = 'my-turn';
    }
}

// ── Promotion ──────────────────────────────────────────────────────────────────
function isPawnPromotion(start, end) {
    const piece = board.grid[start[0]][start[1]];  // local în isPawnPromotion()
    if (!piece || piece.type !== 'pawn') return false;
    return (piece.color === 'white' && end[0] === 7) ||
        (piece.color === 'black' && end[0] === 0);
}

function showPromoDialog(start, end) {
    pendingMove = { start, end };

    const color = board.grid[start[0]][start[1]].color;
    const pieceTypes = ['queen', 'rook', 'bishop', 'knight'];
    const choices = document.getElementById('promo-choices');
    choices.innerHTML = '';

    for (const type of pieceTypes) {
        const btn = document.createElement('button');
        btn.className = 'promo-btn';
        btn.title = type;

        const img = document.createElement('img');
        img.src = `/static/images/${color}_${type}.png`;
        img.alt = type;
        btn.appendChild(img);

        btn.addEventListener('click', () => {
            document.getElementById('promo-overlay').classList.add('hidden');
            executeMove(pendingMove.start, pendingMove.end, type);
            pendingMove = null;
        });

        choices.appendChild(btn);
    }

    document.getElementById('promo-overlay').classList.remove('hidden');
}

// ── Click on square ────────────────────────────────────────────────────────────
function onClick(row, col) {
    if (!gameActive || !board) return;
    if (board.turn !== playerColor) return;

    const piece = board.grid[row][col];  // local în onClick()

    if (selected === null) {
        if (piece && piece.color === board.turn) {
            selected = [row, col];
            fetchMoves(row, col);
        }
    } else {
        if (legalMoves.some(m => m[0] === row && m[1] === col)) {
            const start = selected;
            const end   = [row, col];
            selected    = null;
            legalMoves  = [];

            if (isPawnPromotion(start, end)) {
                showPromoDialog(start, end);
            } else {
                executeMove(start, end, 'queen');
            }
        } else if (piece && piece.color === board.turn) {
            selected = [row, col];
            fetchMoves(row, col);
        } else {
            selected   = null;
            legalMoves = [];
            render();
        }
    }
}

// ── Legal moves ────────────────────────────────────────────────────────────────
function fetchMoves(row, col) {
    if (MODE === 'ai') {
        fetch('/ai/moves', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, row, col })
        })
            .then(r => r.json())
            .then(moves => { legalMoves = moves; render(); });
    } else {
        socket.emit('moves', { code: roomCode, row, col });
    }
}

// ── Execute move ───────────────────────────────────────────────────────────────
function executeMove(start, end, promotion) {
    if (MODE === 'ai') {
        applyMoveLocally(start, end);
        setThinking(true);

        fetch('/ai/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, start, end, promotion })
        })
            .then(r => r.json())
            .then(data => {
                setThinking(false);
                board = data.board;
                render();
            });
    } else {
        socket.emit('move', { code: roomCode, start, end, promotion });
    }
}

function setThinking(on) {
    document.getElementById('thinking').textContent = on ? 'AI is thinking...' : '';
}

// ── Online: WebSocket ──────────────────────────────────────────────────────────
// createRoom and joinRoom are called from HTML (onclick)
// socket is created in game.html only if MODE === 'online'

function createRoom() {
    fetch('/online/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    })
        .then(r => r.json())
        .then(data => {
            if (data.error) { document.getElementById('error-msg').textContent = data.error; return; }
            roomCode = data.code;
            document.getElementById('lobby-buttons').style.display = 'none';
            document.getElementById('room-code-display').textContent = roomCode;
            document.getElementById('room-code-display').style.display = 'block';
            document.getElementById('waiting-msg').style.display = 'block';
            socket.emit('join', { code: roomCode });
        })
        .catch(() => {
            document.getElementById('error-msg').textContent = 'Error creating room.';
        });
}

function joinRoom() {
    const code = document.getElementById('code-input').value.toUpperCase().trim();
    if (!code) { document.getElementById('error-msg').textContent = 'Introduce a code.'; return; }

    fetch('/online/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    })
        .then(r => r.json())
        .then(data => {
            if (data.error) { document.getElementById('error-msg').textContent = data.error; return; }
            roomCode = code;
            socket.emit('join', { code: roomCode });
        });
}