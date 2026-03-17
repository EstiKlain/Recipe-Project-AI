from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
# ---------------------------------------------------------
# דקורטור 1: בדיקת הרשאת מנהל (Admin)
# ---------------------------------------------------------
def admin_required(f):
    @wraps(f)
    @jwt_required()  # קודם כל בודק שיש בכלל טוקן תקין
    def decorated_function(*args, **kwargs):
        # חילוץ ה-ID של המשתמש מתוך הטוקן
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # אם המשתמש לא אדמין - עצור והחזר שגיאה
        if not user or user.role != 'Admin':
            return jsonify({"message": "Admins only! Access denied."}), 403

        return f(*args, **kwargs)  # הכל תקין? כנס לפונקציה

    return decorated_function


# ---------------------------------------------------------
# דקורטור 2: בדיקת הרשאת מעלה מתכונים מאושר (Uploader)
# ---------------------------------------------------------
def uploader_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # בודק אם הוא מנהל (כי למנהל מותר הכל) או אולפאודר מאושר
        is_approved = user and (user.role == 'Admin' or (user.role == 'Uploader' and user.is_approved_uploader))

        if not is_approved:
            return jsonify({"message": "Only approved uploaders can perform this action."}), 403

        return f(*args, **kwargs)

    return decorated_function