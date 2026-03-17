import sys
import os

# הוספת תיקיית הפרויקט לנתיב של פייתון באופן ידני
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)