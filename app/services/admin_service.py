from app.models import User
from app import db


class AdminService:
    @staticmethod
    def approve_user(target_user_id):
        """לוגיקת אישור משתמש כמעלה מתכונים"""
        user_to_approve = User.query.get(target_user_id)

        if not user_to_approve:
            return False, "User not found", 404

        if user_to_approve.is_approved_uploader:
            return False, f"User {user_to_approve.email} is already an approved uploader!", 400

        # עדכון הנתונים
        user_to_approve.role = 'Uploader'
        user_to_approve.is_approved_uploader = True

        # שמירה ל-DB באמצעות המתודה הקיימת במודל שלך
        user_to_approve.save()

        return True, f"User {user_to_approve.email} is now an approved uploader!", 200

    @staticmethod
    def delete_user(user_id):
        """לוגיקת מחיקת משתמש"""
        user = User.query.get(user_id)

        if not user:
            return False, "User not found", 404

        if user.role == 'Admin':
            return False, "Cannot delete an admin user!", 400

        db.session.delete(user)
        db.session.commit()
        return True, f"User {user.email} deleted successfully", 200