# ♟️ Flask Chess LAN Multiplayer

A real-time, web-based chess application built with **Python**, **Flask**, and **Socket.IO**. This project supports playing against a **Minimax AI** or challenging a friend over your **Local Area Network (LAN)**.

---

## ✨ Features

* **Real-time Multiplayer:** Create a room, get a 6-character code, and play instantly.
* **AI Opponent:** Practice your moves against an AI powered by the Minimax algorithm with Alpha-Beta pruning.
* **Full Chess Rules:** 
  * Castling (King & Queen side).
  * En Passant captures.
  * Pawn Promotion (Queen, Rook, Bishop, Knight).
  * Automatic detection of Checkmate, Stalemate, and Draw by insufficient material.
* **Clean Interface:** A responsive, wood-themed board with legal move highlighting.

---

## 🚀 Installation & Setup

### 1. Necessary
Ensure you have **Python 3.8** or higher installed.

### 2. Clone & Setup
Open your terminal and run:
```bash
# Clone the repository
git clone https://github.com/davidghesu/chess_web.git
cd chess_web

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# Activate it (macOS/Linux)
source venv/bin/activate

# Install dependencies
cd chess
pip install -r requirements.txt
```
### 3. Running the Application
```bash
python server.py
```
* **Open your browser and go to:** [http://localhost:5000](http://localhost:5000)

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Flask-SocketIO.
* **Frontend:** JavaScript, HTML, CSS
* **AI:** Minimax Algorithm with Alpha-Beta Pruning.