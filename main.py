# main.py
from authentication import show_login_window
from gui import MainGUI
import database  # Import the module, not DatabaseManager

def launch_main_gui(officer):
    """Launch the main GUI after successful login"""
    app = MainGUI(officer)  # No db_manager needed
    app.run()

if __name__ == "__main__":
    database.init_db()  # Initialize database
    show_login_window(launch_main_gui)  # Start with login window