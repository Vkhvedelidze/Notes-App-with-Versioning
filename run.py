"""
Simple runner script for the Notes App with Versioning
This script provides an easy way to start the application
"""

import uvicorn
import os
import sys

def main():
    print("Starting Notes App with Versioning...")
    print("Features: CRUD operations, versioning, and modern UI")
    print("Access the app at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("=" * 50)
    
    #Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("Error: main.py not found. Please run from the project root directory.")
        sys.exit(1)
    # Start the application
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down Notes App...")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
