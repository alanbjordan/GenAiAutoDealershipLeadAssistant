from flask_socketio import SocketIO, emit
from services.analytics_helpers import get_analytics_summary

# Initialize SocketIO
socketio = SocketIO()

def init_socketio(app):
    """Initialize SocketIO with the Flask app."""
    socketio.init_app(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

def emit_analytics_update():
    """Emit analytics summary update to all connected clients."""
    try:
        summary = get_analytics_summary()
        socketio.emit('analytics_summary', summary, broadcast=True)
    except Exception as e:
        print(f"Error emitting analytics update: {e}") 