# start.py
#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from modules.main import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error: {str(e)}")
        print("Please ensure:")
        print("1. 'modules' folder exists")
        print("2. Required files exist in modules/")
        sys.exit(1)
    except Exception as e:
        print(f"Startup error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()