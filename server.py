from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return "Go to /screen to share screen or /watch to view"

@app.route("/screen")
def screen():
    return render_template("screen.html")

@app.route("/watch")
def watch():
    return render_template("watch.html")

# WebRTC Signaling
@socketio.on("offer")
def handle_offer(offer):
    print("📡 Received Offer")
    emit("offer", offer, broadcast=True)

@socketio.on("answer")
def handle_answer(answer):
    print("📡 Received Answer")
    emit("answer", answer, broadcast=True)

@socketio.on("candidate")
def handle_candidate(candidate):
    print("📡 Received ICE Candidate")
    emit("candidate", candidate, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
