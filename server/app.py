# This file is part of the Flask application for the project.

# server/app.py

# Importing necessary libraries
from flask import g
from create_app import create_app
from database.session import ScopedSession
from datetime import datetime, timezone
import os

# Import the register_routes function
from routes.all_routes import register_routes
from services.websocket_service import init_socketio, socketio

# Create the application instance
app = create_app()

# Register routes
register_routes(app)

# Initialize SocketIO
init_socketio(app)

# Global session handling
def log_with_timing(prev_time, message):
    current_time = datetime.now(timezone.utc)
    elapsed = (current_time - prev_time).total_seconds() if prev_time else 0
    print(f"[{current_time.isoformat()}] {message} (Elapsed: {elapsed:.4f}s)")
    return current_time

@app.before_request
def create_session():
    """ Runs before every request to create a new session. """
    t = log_with_timing(None, "[GLOBAL BEFORE_REQUEST] Creating session...")
    g.session = ScopedSession()
    t = log_with_timing(t, "[GLOBAL BEFORE_REQUEST] Session created and attached to g.")

@app.teardown_request
def remove_session(exception=None):
    """
    Runs after every request.
    - Rolls back if there's an exception,
    - Otherwise commits,
    - Then removes the session from the registry.
    """
    t = log_with_timing(None, "[GLOBAL TEARDOWN_REQUEST] Starting teardown...")
    session = getattr(g, 'session', None)
    if session:
        if exception:
            t = log_with_timing(t, "[GLOBAL TEARDOWN_REQUEST] Exception detected. Rolling back session.")
            session.rollback()
        else:
            t = log_with_timing(t, "[GLOBAL TEARDOWN_REQUEST] Committing session.")
            session.commit()
        t = log_with_timing(t, "[GLOBAL TEARDOWN_REQUEST] Removing session from registry.")
        ScopedSession.remove()

if __name__ == '__main__':
    socketio.run(app, debug=True)