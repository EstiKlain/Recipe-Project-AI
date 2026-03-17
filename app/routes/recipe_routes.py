from flask import Blueprint, request, jsonify, current_app
from app.models import User, Recipe, IngredientEntry
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import uploader_required
from app.services.recipe_service import RecipeService

# יצירת Blueprint למתכונים
recipe_bp = Blueprint('recipes', __name__)

@recipe_bp.route('/mine', methods=['GET'])
@uploader_required
def get_my_recipes():
    """רק משתמש שהוא Uploader מאושר יכול לראות את 'המתכונים שלי'"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # בגלל הדקורטור, רק משתמשים מאושרים יגיעו לכאן.
    # אם Reader ינסה להיכנס, הוא יקבל 403 Forbidden אוטומטית.

    # שימוש בפונקציה הקיימת ב-Service כדי לעצב כל מתכון ברשימה
    my_recipes = [RecipeService.format_recipe(recipe, include_comments=True) for recipe in user.recipes]

    return jsonify(my_recipes), 200

@recipe_bp.route('/add', methods=['POST'])
@uploader_required  # רק משתמש עם הרשאת מעלה יכול
def add_recipe():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # קריאה ל-Service לביצוע כל העבודה
    new_recipe, error = RecipeService.create_recipe(
        data=request.form,
        file=request.files.get('image'),
        user_id=user_id,
        author_name=user.name if user else "Unknown"
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "המתכון עלה בהצלחה עם כל הוריאציות!",
        "recipe_id": new_recipe.id
    }), 201

    # except Exception as e:
    #     db.session.rollback()
    #     return jsonify({"error": f"משהו השתבש: {str(e)}"}), 500

@recipe_bp.route('/<int:recipe_id>', methods=['DELETE'])
@uploader_required
def delete_recipe(recipe_id):

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        return jsonify({"error": "המתכון לא נמצא"}), 404

    # קריאה ל-Service (הלוגיקה, הקבצים וה-Exception Handling נמצאים שם)
    success, message, status_code = RecipeService.delete_recipe(recipe, user)

    if not success:
        return jsonify({"error": message}), status_code

    return jsonify({"message": message}), status_code

@recipe_bp.route('/<int:recipe_id>', methods=['GET'])
@jwt_required()
def get_recipe_details(recipe_id):
    """שליפת פרטי מתכון מלאים כולל תגובות"""
    # קריאה ל-Service לקבלת הנתונים המעובדים
    recipe_data = RecipeService.get_recipe_details(recipe_id)

    if not recipe_data:
        return jsonify({"error": "המתכון לא נמצא"}), 404

    return jsonify(recipe_data), 200

@recipe_bp.route('/search', methods=['POST'])
@jwt_required()
def search_recipes():
    # במקום data = request.get_json()
    data = request.get_json(silent=True) or {}

    # קריאה ל-Service שמחזיר לנו רשימת דיקשנריז עם אובייקט 'recipe'
    results = RecipeService.get_filtered_recipes(
        ingredients_list=data.get('ingredients', []),
        sort_by=request.args.get('sort','match'),
        order=request.args.get('order', 'asc') ,    # ברירת מחדל: עולה (מהקל/מהיר לנמוך)
        recipe_type =  data.get('recipe_type')  # חדש: מקבל "בשרי", "חלבי" או "פרווה"
    )
    # 3. קריאה ללוגיקת העיצוב שפיצלנו לתוך ה-Service
    output = RecipeService.search_recipes_logic(results)
    return jsonify(output), 200

@recipe_bp.route('/<int:recipe_id>/rate', methods=['POST'])
@jwt_required()
def rate_recipe(recipe_id):
    # שליפת ה-ID של המשתמש מתוך ה-Token (כדי לדעת מי מדרג)
    user_id = get_jwt_identity()

    # שליפת הנתונים מה-Body
    data = request.get_json(silent=True) or {}
    score = data.get('score')
    comment = data.get('comment')  # יחזיר None אם המשתמש לא שלח תגובה
    # קריאה ל-Service לביצוע הלוגיקה
    recipe, error = RecipeService.add_rating(recipe_id, user_id, score,comment)

    if error:
        # אם ה-Service החזיר שגיאה (למשל דירוג כפול או ציון לא תקין)
        return jsonify({"error": error}), 400

    # אם הכל עבר בשלום, מחזירים את הממוצע החדש
    return jsonify({
        "message": "הדירוג נשמר בהצלחה!",
        "new_average": recipe.rating
    }), 200