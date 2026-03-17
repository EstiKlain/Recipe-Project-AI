from flask import Blueprint, jsonify
from app import db
from app.models import User
from app.services.admin_service import AdminService
from app.utils.decorators import admin_required,uploader_required # המאבטח שלנו!
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/approve/<int:target_user_id>', methods=['POST'])
@admin_required  # <--- המאבטח מוודא שרק אדמין נכנס לכאן!
def approve_user(target_user_id):
    """נתיב שמאפשר למנהל לאשר משתמש רגיל להפוך למעלה מתכונים"""
    success, message, status = AdminService.approve_user(target_user_id)
    return jsonify({"message": message}), status


@admin_bp.route('/pending_users', methods=['GET'])
@admin_required
def get_pending_users():
    # שליפה רק של מי שביקש שדרוג ועדיין לא אושר
    pending_users = User.query.filter_by(requested_upgrade=True, is_approved_uploader=False).all()

    users_list = []
    for user in pending_users:
        users_list.append({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "requested": user.requested_upgrade
        })

    return jsonify(users_list), 200

@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@admin_required  # רק מנהל יכול למחוק!
def delete_user(user_id):
    success, message, status = AdminService.delete_user(user_id)
    return jsonify({"message": message}), status

