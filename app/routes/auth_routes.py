from flask import Blueprint, request, jsonify
from app import limiter # וודאי שייבאת את האובייקט שיצרת ב-init
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import re

from app.services.auth_service import AuthService

# יצירת Blueprint חדש במיוחד לאימות ורישום
auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """פונקציית עזר לבדיקה אם המייל בפורמט תקין"""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

@auth_bp.route('/')
def home():
    """נתיב בדיקה פשוט כדי לוודא שהשרת מגיב"""
    return "The Recipe Server is Running!"

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("3 per hour") # מניעת יצירת משתמשי ספאם בכמויות
def register():
    data = request.get_json()
    user, message, status = AuthService.register_user(data)
    return jsonify({"message": message}), status

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute") # הגבלה מחמירה להתחברות
def login():
    """נתיב לכניסת משתמש קיים - מעדכן לשימוש בטוקנים"""

    # 1. קבלת נתונים מהלקוח (Postman)
    data = request.get_json()
    result, error, status = AuthService.login_user(data)
    if error:
        return jsonify({"message": error}), status
    return jsonify(result), status
@auth_bp.route('/me', methods=['GET'])
@jwt_required()  # רק משתמש עם טוקן יכול לגשת
def get_current_user():
    """מחזיר את פרטי המשתמש המחובר לפי הטוקן שלו"""
    # חילוץ ה-ID מהטוקן
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # החזרת המידע (בלי הסיסמה כמובן!)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_approved": user.is_approved_uploader,
        "requested_upgrade": user.requested_upgrade
    }), 200

@auth_bp.route('/request_upgrade', methods=['POST'])
@jwt_required()  # צריך רק להיות מחובר, לא משנה התפקיד
def request_upgrade():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.is_approved_uploader:
        return jsonify({"message": "You are already an uploader!"}), 400

    if user.requested_upgrade:
        return jsonify({"message": "Request already sent. Please wait for admin approval."}), 400

    # עדכון הבקשה
    user.requested_upgrade = True
    user.save()

    return jsonify({"message": "Request sent to admin successfully!"}), 200
