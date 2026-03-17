from . import db  # ייבוא אובייקט ה-db מתוך __init__.py של התיקייה הנוכחית
import json


# מחלקת בסיס (BaseModel) שמורישה ID ומתודת שמירה
class BaseModel(db.Model):
    __abstract__ = True  # מציין שזו מחלקה כללית ולא טבלה בפני עצמה
    id = db.Column(db.Integer, primary_key=True)  # הורשה של תכונת ה-id

    def save(self):
        """מתודה שאחראית להמיר את אובייקט הפייתון לשורה בטבלה ב-DB"""
        db.session.add(self)
        db.session.commit()
# מודל משתמש - נתוני משתמש ורמת הרשאה
class User(BaseModel):
    __tablename__ = 'users'
    name = db.Column(db.String(255), nullable=False)  # שם של המשתמש
    email = db.Column(db.String(120), unique=True, nullable=False)  # לא יכולות להיות 2 כתובות מייל זהות
    password = db.Column(db.String(255), nullable=False)  # הסיסמה של המשתמש
    role = db.Column(db.String(20), default='Reader')  # Admin, Uploader, Reader
    is_approved_uploader = db.Column(db.Boolean, default=False)  # האם המנהל אישר את המשתמש
    requested_upgrade = db.Column(db.Boolean, default=False)  # האם ביקש להיות מעלה מתכונים?

    # קשר למתכונים שהמשתמש העלה
    recipes = db.relationship('Recipe', backref='author', lazy=True)
# כתוב הערות יפות אבל לא מעודכן
# מודל מתכון - נתוני המתכון הראשיים
# class Recipe(BaseModel):
#     __tablename__ = 'recipes'
#     title = db.Column(db.String(100), nullable=False)
#     instructions = db.Column(db.Text, nullable=False)  # תיאור ההוראות להכנת המתכון
#     image_path = db.Column(db.String(255))  # הנתיב לשמירת התמונה המקורית בשרת
#     variation_paths = db.Column(db.Text)  # נשמר כמחרוזת/JSON המכיל את הנתיבים של 3 התמונות
#     recipe_type = db.Column(db.String(20))  # כשרות: חלבי, בשרי, פרווה
#
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # מקשר למשתמש שהעלה את המתכון
#
#     # קשר לרכיבים (One-to-Many)
#     ingredients = db.relationship('IngredientEntry', backref='recipe', lazy=True, cascade="all, delete-orphan")
#
#     def set_variations(self, paths_list):
#         self.variation_paths = json.dumps(paths_list)
#
#     def get_variations(self):
#         return json.loads(self.variation_paths) if self.variation_paths else []


# מודל רכיב בודד - רשימת הרכיבים והכמויות
# מודל מתכון
class Recipe(BaseModel):
    __tablename__ = 'recipes'
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False) # הוספתי תיאור כללי
    instructions = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))
    # שדה שישמור את רשימת הוריאציות כטקסט (JSON)
    variation_paths = db.Column(db.Text, nullable=True) # כאן נשמר ה-JSON כטקסט
    recipe_type = db.Column(db.String(20)) # חלבי, בשרי, פרווה
    prep_time = db.Column(db.Integer, default=30)  # זמן הכנה בדקות
    rating = db.Column(db.Float, default=0.0)  # דירוג ממוצע
    difficulty = db.Column(db.String(20), default='Medium')  # Easy, Medium, Hard
    author_name= db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # קשר לרכיבים
    ingredients = db.relationship('IngredientEntry', backref='recipe', lazy=True, cascade="all, delete-orphan")
    ratings = db.relationship('Rating', backref='recipe', lazy=True, cascade="all, delete-orphan")
    def set_variations(self, paths_list):
        """הופך רשימה לטקסט JSON עבור ה-DB"""
        self.variation_paths = json.dumps(paths_list)

    def get_variations(self):
        """הופך את הטקסט מה-DB חזרה לרשימת פייתון"""
        return json.loads(self.variation_paths) if self.variation_paths else []
class IngredientEntry(BaseModel):
    __tablename__ = 'ingredients'
    product = db.Column(db.String(100), nullable=False)  # שם הרכיב
    amount = db.Column(db.Float, nullable=False)  # הכמות הנדרשת
    unit = db.Column(db.String(50))  # יחידת המידה
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)  # קשר One-to-Many בין Recipe לרכיבים
class Rating(BaseModel):
    __tablename__ = 'ratings'

    score = db.Column(db.Integer, nullable=False)  # הציון (1-5)
    comment = db.Column(db.Text, nullable=True)  # אופציונלי (התגובה הטקסטואלית)
    # קישור למשתמש שנתן את הדירוג
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # קישור למתכון שקיבל את הדירוג
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    user = db.relationship('User', backref='ratings_given')
    # הגבלה: כל משתמש יכול לדרג כל מתכון רק פעם אחת
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_rating'),
    )

    def __init__(self, user_id, recipe_id, score,comment=None):
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.score = score
        self.comment = comment