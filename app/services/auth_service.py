from app.models import User
from app import db, bcrypt
from flask_jwt_extended import create_access_token
import re


class AuthService:
    @staticmethod
    def is_valid_email(email):
        """בדיקת פורמט אימייל"""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)

    @staticmethod
    def register_user(data):
        """לוגיקת רישום משתמש חדש"""
        # 1. בדיקת שדות חסרים
        required_fields = ['email', 'password', 'name']
        if not data or not all(field in data for field in required_fields):
            return None, "Missing email, password or name", 400

        email = data.get('email').strip()
        password = data.get('password')
        name = data.get('name').strip()

        # 2. וולידציות (מילה במילה מהקוד שלך)
        if len(name) < 2:
            return None, "Name must be at least 2 characters long", 400
        if not AuthService.is_valid_email(email):
            return None, "Invalid email format", 400
        if len(password) < 6:
            return None, "Password must be at least 6 characters long", 400

        # 3. בדיקה אם קיים
        if User.query.filter_by(email=email).first():
            return None, "User already exists", 400

        # 4. הצפנה ויצירה
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_pw, name=name, role='Reader')
        new_user.save()

        return new_user, f"Hello {new_user.name}! Registration successful.", 201

    @staticmethod
    def login_user(data):
        """לוגיקת התחברות ויצירת טוקן"""
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # יצירת טוקן (Identity חייב להיות מחרוזת)
            access_token = create_access_token(identity=str(user.id))
            return {
                "token": access_token,
                "role": user.role,
                "user_id": user.id,
                "message": "Login successful!"
            }, None, 200

        return None, "Invalid email or password", 401

#לפני הפיצול עם הערות טובות
# @auth_bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#
#     # --- בדיקות נתונים (Validation) ---
#
#     # 1. בדיקה שכל השדות הנדרשים קיימים (כולל name)
#     required_fields = ['email', 'password', 'name']
#     if not data or not all(field in data for field in required_fields):
#         return jsonify({"message": "Missing email, password or name"}), 400
#
#     email = data.get('email').strip()
#     password = data.get('password')
#     name = data.get('name').strip()
#
#     # 2. בדיקת תקינות השם (שלא יהיה ריק ושלא יהיה קצר מדי)
#     if len(name) < 2:
#         return jsonify({"message": "Name must be at least 2 characters long"}), 400
#
#     # 3. בדיקת פורמט מייל
#     if not is_valid_email(email):
#         return jsonify({"message": "Invalid email format"}), 400
#
#     # 4. בדיקת אורך סיסמה
#     if len(password) < 6:
#         return jsonify({"message": "Password must be at least 6 characters long"}), 400
#
#     # --- סוף בדיקות הנתונים ---
#
#     # בדיקה אם המייל כבר תפוס
#     if User.query.filter_by(email=email).first():
#         return jsonify({"message": "User already exists"}), 400
#
#     # הצפנת סיסמה
#     hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
#
#     # יצירת המשתמש החדש עם השם
#     new_user = User(
#         email=email,
#         password=hashed_pw,
#         name=name,  # <--- שמירת השם החדש
#         role='Reader'
#     )
#     new_user.save()
#
#     return jsonify({"message": f"Hello {new_user.name}! Registration successful."}), 201
#
# @auth_bp.route('/login', methods=['POST'])
# def login():
#     """נתיב לכניסת משתמש קיים - מעדכן לשימוש בטוקנים"""
#
#     # 1. קבלת נתונים מהלקוח (Postman)
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#
#     # 2. חיפוש המשתמש במסד הנתונים לפי המייל
#     # הפונקציה .first() תחזיר את המשתמש או None אם הוא לא קיים
#     user = User.query.filter_by(email=email).first()
#
#     # 3. בדיקת תקינות:
#     # האם המשתמש נמצא?
#     # ואם כן - האם הסיסמה שהוקלדה (password) מתאימה לזו ששמורה ב-DB (user.password)?
#     if user and bcrypt.check_password_hash(user.password, password):
#         # יצירת טוקן ("צמיד") שבתוכו מוצפן ה-ID של המשתמש
#         # זה מאפשר לשרת לזהות את המשתמש בבקשות הבאות
#         access_token = create_access_token(identity=str(user.id))
#
#         # אם הכל תקין, נחזיר הודעת הצלחה, את הטוקן ואת התפקיד
#         return jsonify({
#             "message": "Login successful!",
#             "token": access_token,  # הלקוח ישמור את זה לבקשות הבאות
#             "role": user.role,
#             "user_id": user.id
#         }), 200
#     else:
#         # אם המייל לא קיים או שהסיסמה שגויה
#         return jsonify({"message": "Invalid email or password"}), 401
