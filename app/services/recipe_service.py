import json
import uuid

from app.models import Recipe, Rating, db, IngredientEntry
from app.utils.image_service import validate_is_food, process_recipe_images
import os
import shutil
from flask import current_app

class RecipeService:
    # הגדרת סיומות מותרות
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    @staticmethod
    def allowed_file(filename):
        """בודק אם סיומת הקובץ מותרת"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in RecipeService.ALLOWED_EXTENSIONS


    @staticmethod
    def create_recipe(data, file, user_id, author_name):
        """
        מרכזת את כל לוגיקת יצירת המתכון: וולידציה, עיבוד תמונות ושמירה ב-DB
        """
        # 1. קבלת נתונים גולמיים
        title = data.get('title')
        instructions = data.get('instructions')
        ingredients_raw = data.get('ingredients')  # קודם לוקחים את הנתון הגולמי

        # --- הוספת הגבלת גודל קובץ (שיפור אבטחה וביצועים) ---
        MAX_FILE_SIZE = 5 * 1024 * 1024  # הגבלה ל-5MB (מומלץ יותר מ-20MB כדי לשמור על מהירות השרת)

        if file:
            # בדיקת גודל הקובץ
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # החזרת הסמן לתחילת הקובץ לקריאה בהמשך

            # בדיקת סיומת
            if not RecipeService.allowed_file(file.filename):
                return None, "סוג קובץ לא נתמך. מותר להעלות רק תמונות.", 400

            if file_size > MAX_FILE_SIZE:
                return None, f"הקובץ גדול מדי ({file_size / (1024 * 1024):.1f}MB). הגודל המקסימלי המותר הוא 5MB."
        # --------------------------------------------------

        # 2. המרה לרשימה (פעם אחת בלבד!)
        ingredients_list = []
        try:
            if ingredients_raw:
                if isinstance(ingredients_raw, str):
                    ingredients_list = json.loads(ingredients_raw)
                else:
                    ingredients_list = ingredients_raw
        except Exception as e:
            print(f"JSON Error: {e}")
            return None, "פורמט המרכיבים לא תקין"

        # 3. בדיקה שכל הנתונים קיימים (כולל שהרשימה לא ריקה)
        if not all([title, instructions, ingredients_list, file]):
            return None, "חובה להזין שם, הוראות, מרכיבים ותמונה!"

        # --- מחקנו כאן את הניסיון השני להמרה שגרם לשגיאה ---

        # 4. אימות AI לתמונה (האם זה אוכל?)
        is_food, detected_label = validate_is_food(file)
        if not is_food:
            return None, f"התמונה זוהתה כ-{detected_label}. נא להעלות תמונת אוכל בלבד!"

        # 5. עיבוד תמונות (Pillow)
        recipe_uuid = str(uuid.uuid4())[:12]
        main_path, variations_dict = process_recipe_images(file, author_name, recipe_uuid)
        # טיפול בטוח במספרים - מחוץ ליצירת האובייקט!
        try:
            raw_prep_time = data.get('prep_time', 30)
            # בדיקה אם זה מספר חיובי
            if str(raw_prep_time).isdigit():
                prep_time = int(raw_prep_time)
            else:
                prep_time = 30
        except (ValueError, TypeError):
            prep_time = 30
        # 6. יצירת אובייקט המתכון
        new_recipe = Recipe(
            title=title,
            description=data.get('description', ''),
            instructions=instructions,
            recipe_type=data.get('recipe_type', 'פרווה'),
            image_path=main_path,
            user_id=user_id,
            prep_time=prep_time,
            difficulty=data.get('difficulty', 'Medium'),
            rating=0.0,
            author_name=author_name
        )
        new_recipe.set_variations(variations_dict)
        db.session.add(new_recipe)

        # 7. הוספת המרכיבים
        for ing in ingredients_list:
            if not ing.get('product') or not ing.get('amount'):
                db.session.rollback()
                return None, "חסר מוצר או כמות באחד המרכיבים"

            new_ing = IngredientEntry(
                product=ing.get('product'),
                amount=ing.get('amount'),
                unit=ing.get('unit', ''),
                recipe=new_recipe
            )
            db.session.add(new_ing)

        try:
            db.session.commit()
            return new_recipe, None
        except Exception as e:
            db.session.rollback()
            return None, f"שגיאת מסד נתונים: {str(e)}"

    @staticmethod
    def delete_recipe(recipe, user):
        """
                מוחק מתכון ואת כל התמונות שלו מהשרת.
                בודק הרשאות (רק לבעל המתכון או לאדמין מותר למחוק).
                """
        # 1. הבדיקה המקורית שלך
        if str(recipe.user_id) != str(user.id) and user.role != 'Admin':
            return False, "אין לך הרשאה למחוק מתכון זה", 403

        try:
            # 2. מחיקת הקבצים - בדיוק לפי השורה שכתבת במקור
            if recipe.image_path:
                recipe_folder = os.path.dirname(recipe.image_path)
                if os.path.exists(recipe_folder):
                    shutil.rmtree(recipe_folder)

            # 3. המחיקה מה-DB
            db.session.delete(recipe)
            db.session.commit()
            return True, "המתכון נמחק בהצלחה", 200

        except Exception as e:
            # 4. הבלוק ששאלת עליו - מטפל בשגיאות ומחזיר סטטוס 500
            db.session.rollback()
            print(f"❌ Delete error: {str(e)}")
            return False, f"משהו השתבש במחיקה: {str(e)}", 500

    @staticmethod
    def calculate_match_score(user_ingredients_set, recipe_ingredients):
        """חישוב אחוז התאמה לפי השדה במודל שלך"""
        if not recipe_ingredients:
            return 0
        matches = sum(1 for ri in recipe_ingredients if ri.product.lower() in user_ingredients_set)
        return (matches / len(recipe_ingredients)) * 100

    @staticmethod
    def get_filtered_recipes(ingredients_list=None, sort_by=None,order='asc', recipe_type=None):
        # 1. שליפת המתכונים
        query = Recipe.query

        # 2. סינון לפי סוג מתכון (אם המשתמש בחר סוג)
        if recipe_type:
            query = query.filter(Recipe.recipe_type == recipe_type)
        all_recipes = query.all()
        results = []
        # 3. חישוב ציוני התאמה
        # המרה ל-SET פעם אחת לפני הלולאה - לביצועים מקסימליים
        user_set = {i.strip().lower() for i in ingredients_list} if ingredients_list else None

        for r in all_recipes:
            score = 100
            if user_set is not None:
                score = RecipeService.calculate_match_score(user_set, r.ingredients)

            # החזרת מתכונים: אם יש התאמה או שלא נשלחו מצרכים בכלל
            if score > 0 or user_set is None:
                results.append({"recipe": r, "match_score": score})

        # 4. מיון (לפי הקוד שכבר בנינו)
        is_reverse = True if order == 'desc' else False
        # מילון עזר להמרת טקסט למספר לצורך מיון לוגי
        difficulty_map = {
            'Easy': 1,
            'Medium': 2,
            'Hard': 3
        }

        # --- לוגיקת המיון המורחבת ---
        if sort_by == 'time':
            results.sort(key=lambda x: x['recipe'].prep_time or 0, reverse=is_reverse)
        elif sort_by == 'rating':
            rating_reverse = False if order == 'asc' else True
            results.sort(key=lambda x: x['recipe'].rating, reverse=rating_reverse)
        elif sort_by == 'difficulty':
            # שימוש ב-map כדי ש-Easy (1) יהיה קטן מ-Hard (3)
            results.sort(key=lambda x: difficulty_map.get(x['recipe'].difficulty, 2), reverse=is_reverse)
        else:
            results.sort(key=lambda x: x['match_score'], reverse=True)

        return results

    @staticmethod
    def add_rating(recipe_id, user_id, score,comment=None):
        # 1. בדיקת תקינות הציון
        if not score or not (1 <= score <= 5):
            return None, "הציון חייב להיות בין 1 ל-5"
        # 2. בדיקה: האם המתכון קיים בכלל?
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return None, "המתכון לא נמצא, לא ניתן לדרג"
        # בדיקה האם המשתמש מנסה לדרג את עצמו
        if recipe.user_id == user_id:
            return None, "לא ניתן לדרג מתכון של עצמך"
        # 3. יצירה וניסיון שמירה

        # בדיקה האם המשתמש כבר דירג בעבר
        existing_rating = Rating.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

        if existing_rating:
            # עדכון דירוג קיים
            existing_rating.score = score
            existing_rating.comment = comment
            existing_rating.save()
        else:
             # יצירת דירוג חדש
                new_rating = Rating(user_id=user_id, recipe_id=recipe_id, score=score, comment=comment)
                new_rating.save()

        # 4. חישוב ממוצע (כאן כבר יש לנו את אובייקט ה-recipe מהבדיקה קודם)
        all_ratings = Rating.query.filter_by(recipe_id=recipe_id).all()
        average = sum(r.score for r in all_ratings) / len(all_ratings)

        recipe.rating = round(average, 1)
        recipe.save()

        return recipe, None

    @staticmethod
    def get_recipe_details(recipe_id):  # הנה הפונקציה שהייתה חסרה!
        """שולף מתכון בודד ומעצב אותו כולל תגובות"""
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return None
        # כאן אנחנו קוראים לפורמטר ומבקשים לכלול תגובות
        return RecipeService.format_recipe(recipe, include_comments=True)

    @staticmethod
    def clean_path(full_path):
        if not full_path: return ""
        # מחפש את המילה static ומחזיר ממנה והלאה
        parts = full_path.split('static')
        return "/static" + parts[-1].replace('\\', '/')

    @staticmethod
    def format_recipe(recipe, match_score=None, include_comments=False):
        """הופך אובייקט מתכון לדיקשנרי מעוצב עבור ה-Frontend"""
        # ניקוי נתיבי כל הווריאציות (תמונות קטנות/בינוניות)
        variations = recipe.get_variations()
        cleaned_variations = {k: RecipeService.clean_path(v) for k, v in variations.items()}

        data = {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "instructions": recipe.instructions,
            "recipe_type": recipe.recipe_type,
            "prep_time": recipe.prep_time,
            "rating": recipe.rating,
            "difficulty": recipe.difficulty,
            "author_name": recipe.author_name,
            "main_image": RecipeService.clean_path(recipe.image_path),
            "all_images": cleaned_variations,
            "ingredients": [
                {"product": i.product, "amount": i.amount, "unit": i.unit}
                for i in recipe.ingredients
            ]
        }

        # הוספת ציון התאמה (רק אם קיים - בחיפושים)
        if match_score is not None:
            data['match_score'] = f"{match_score:.1f}%"

        # הוספת תגובות (רק אם ביקשנו - בדף מתכון בודד)
        if include_comments:
            data['comments'] = [
                {
                    "username": r.user.name,
                    "score": r.score,
                    "comment": r.comment or ""
                } for r in recipe.ratings
            ]

        return data

    @staticmethod
    def search_recipes_logic(results):
        """
        לוקחת את תוצאות החיפוש הגולמיות ובונה מהן את ה-output המעוצב.
        """
        # output = []
        # for res in results:
        #     # שימוש בפורמטר הקיים ב-Service כפי שמופיע אצלך בקוד
        #     formatted = RecipeService.format_recipe(
        #         recipe=res['recipe'],
        #         match_score=res['match_score'],
        #         include_comments=False
        #     )
        #     output.append(formatted)
        #
        # return output

        return [
            RecipeService.format_recipe(res['recipe'], match_score=res['match_score'])
            for res in results
        ]