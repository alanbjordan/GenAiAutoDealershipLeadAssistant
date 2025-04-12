# This file is part of the Flask application for the project.

# server/app.py

# Importing necessary libraries
from flask import g
from create_app import create_app
from database.session import ScopedSession
from datetime import datetime
import os



# Import Blueprints
from routes.all_routes import all_routes_bp

# Create the application instance
app = create_app()

# Global session handling
def log_with_timing(prev_time, message):
    current_time = datetime.utcnow()
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
            t = log_with_timing(t, "[GLOBAL TEARDOWN_REQUEST] No exception. Committing session.")
            session.commit()
        ScopedSession.remove()
        t = log_with_timing(t, "[GLOBAL TEARDOWN_REQUEST] Session removed.")
    else:
        t = log_with_timing(t, "[GLOBAL TEARDOWN_REQUEST] No session found.")

# Registering Blueprints
app.register_blueprint(all_routes_bp, url_prefix="/api")


# Main function to run the application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)