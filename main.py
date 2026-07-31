import sys
import sqlite3
from core.database import initialize_database

def main():
    print("=" * 45)
    print("           CyberLab Manager")
    print("=" * 45)
    
    print("Initializing system...")
    
    try:
        initialize_database()
        print("[✓] Database initialized successfully.")
        
        # Here is where you would eventually start your main application loop,
        # launch your GUI (like Tkinter/PyQt), or start your web server.
        # start_app() 
        
    except sqlite3.Error as e:
        print(f"[X] CRITICAL ERROR: Failed to initialize database.")
        print(f"Details: {e}")
        sys.exit(1) # Exit the program with an error code
    except Exception as e:
        print(f"[X] UNEXPECTED ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
