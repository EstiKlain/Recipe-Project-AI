import os
from dotenv import load_dotenv

# טעינת המשתנים מקובץ ה-.env
load_dotenv()


class Config:
    # שליפת המשתנים מה-env, ואם הם לא קיימים - שימוש בברירת מחדל
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_default')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_secret_default')
    # הגדרות תיקיית העלאות
    # UPLOAD_FOLDER = os.path.join('static', 'uploads', 'recipes')
    # 3. טיפול חכם בנתיב התיקייה
    # קודם כל מושכים את המחרוזת מה-env
    _raw_path = os.getenv('UPLOAD_FOLDER_PATH', 'static/uploads/recipes')

    # הופכים את הנתיב למוחלט (Absolute Path) כדי שלא ילך לאיבוד
    # os.getcwd() נותן לנו את הנתיב של תיקיית הפרויקט הראשית
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), *_raw_path.split('/')))