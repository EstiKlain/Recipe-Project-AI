
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt # ספריית ההצפנה
from flask_jwt_extended import JWTManager # <--- הוספת תמיכה בטוקנים
import os
from dotenv import load_dotenv
from config import Config  # ייבוא המחלקה מהקובץ החדש
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# אתחול ה-Limiter
# default_limits מגדיר הגנה כללית על כל הראוטים באתר
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://", # שומר את הנתונים בזיכרון השרת
)
# טעינת המשתנים מהקובץ .env לתוך המערכת
load_dotenv()
# הגדרת אובייקט ה-SQLAlchemy (מחוץ לפונקציה כדי שיהיה נגיש לכל הקבצים)
db = SQLAlchemy()
bcrypt = Bcrypt() # יצירת אובייקט ההצפנה
jwt = JWTManager() # <--- יצירת אובייקט הטוקנים

def create_app():
    # יצירת מופע האפליקציה של Flask
    # חישוב הנתיב האבסולוטי לתיקיית ה-static שנמצאת מחוץ ל-app
    # os.path.abspath(os.path.dirname(__file__)) נותן את הנתיב לתיקיית app
    # '..' יוצא תיקייה אחת למעלה ל-RecipeProject
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    app = Flask(__name__, static_folder=static_path)
    # טעינת כל ההגדרות מהקובץ config.py בשורה אחת!
    app.config.from_object(Config)
    # # הגדרות (Configurations)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db' # מיקום מסד הנתונים
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # כיבוי התראות מיותרות לחיסכון במשאבים
    # app.config['SECRET_KEY'] = 'dev_key_123' # מפתח לאבטחת סשנים

    # חיבור מסד הנתונים לאפליקציה שנוצרה
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)  # <--- חיבור הטוקנים לאפליקציה

    # יצירת הקשר (Context) - מאפשר לבצע פעולות שדורשות שהאפליקציה תהיה "חיה"
    with app.app_context():
        # ייבוא המודלים כדי ש-SQLAlchemy יידע אילו טבלאות ליצור
        from . import models
        db.create_all() # יצירת הקובץ recipes.db והטבלאות במידה ולא קיימים

        # רישום ה-Blueprint (הנתיבים שכתבנו ב-routes.py)
        # אנחנו מייבאים אותו כאן בפנים כדי למנוע מצב של לופ (ייבוא מעגלי)
        # ייבוא ה-Blueprints החדשים מהתיקייה שיצרנו
        from .routes.auth_routes import auth_bp
        from .routes.admin_routes import admin_bp
        from .routes.recipe_routes import recipe_bp
        # רישום ה-Blueprints באפליקציה
        app.register_blueprint(auth_bp,url_prefix='/auth')
        app.register_blueprint(admin_bp,url_prefix='/admin')
        app.register_blueprint(recipe_bp,url_prefix='/recipes')

        @app.errorhandler(429)
        def ratelimit_handler(e):
            return jsonify({
                "error": "Too many requests",
                "message": "חרגת מכמות הבקשות המותרת. נסה שוב מאוחר יותר."
            }), 429
    return app
