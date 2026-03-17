# import uuid
# import io
# import os
# import numpy as np
# from PIL import Image, ImageEnhance, ImageDraw, ImageFont
# from werkzeug.utils import secure_filename
# from flask import current_app
# import tensorflow as tf
#
# # טעינת המודל בצורה מפורשת - ResNet50
# # אנחנו טוענים אותו מחוץ לפונקציה כדי שיקרה רק פעם אחת
# try:
#     print("⏳ Loading AI Model (ResNet50)...")
#     model = tf.keras.applications.ResNet50(weights='imagenet')
#     preprocess_input = tf.keras.applications.resnet50.preprocess_input
#     decode_predictions = tf.keras.applications.resnet50.decode_predictions
#     print("✅ Model Loaded Successfully!")
# except Exception as e:
#     print(f"❌ Error loading model: {e}")
#     model = None
# def validate_is_food(file):
#     """בדיקה האם התמונה היא של אוכל עם הודעות זיהוי מפורטות"""
#
#     if model is None:
#         return True, "model_not_found_bypass"
#
#     try:
#
#         # 1. קריאת הקובץ והחזרת הסמן (חובה!)
#         file.seek(0)
#         img_bytes = file.read()
#         file.seek(0)
#
#         if not img_bytes:
#             return False, "קובץ ריק"
#
#         # 2. עיבוד התמונה לפורמט שה-AI מכיר
#         img = Image.open(io.BytesIO(img_bytes))
#         img = img.convert('RGB')  # פותר בעיות של שקיפות או פורמטים מיוחדים
#         img = img.resize((224, 224))
#
#         x = tf.keras.preprocessing.image.img_to_array(img)
#         x = np.expand_dims(x, axis=0)
#         x = preprocess_input(x)
#
#         # 3. זיהוי באמצעות המודל
#         preds = model.predict(x)
#
#         try:
#             decoded = decode_predictions(preds, top=3)[0]
#
#             # רשימת מילים שקשורות לאוכל
#             food_keywords = ['food', 'dish', 'meal', 'pizza', 'bakery', 'confectionery',
#                             'soup', 'meat', 'ice_cream', 'guacamole', 'burger', 'sandwich',
#                             'vegetable', 'fruit', 'trifle', 'chocolate_sauce', 'cake']
#
#              # השגת הזיהוי הכי חזק של ה-AI
#              top_prediction_label = decoded[0][1].replace('_', ' ')
#
#              # בדיקה האם אחד משלושת הזיהויים הראשונים הוא אוכל
#                 for (_, label, prob) in decoded:
#                  if any(key in label.lower() for key in food_keywords) and prob > 0.1:
#                       return True, label
#
#              # אם הגענו לכאן, זה לא זוהה כאוכל - נחזיר את מה שכן זוהה
#                 return False, top_prediction_label
#
#         except Exception as e:
# print(f"⚠️ AI Decode Warning: {inner_e}. Bypassing check.")
#             # אם מילון השמות פגום, פשוט נאשר את התמונה כדי לא לתקוע את המערכת
#             return True, "bypass_due_to_dictionary_error"
#     except Exception as e:
#         # הדפסת השגיאה האמיתית לטרמינל שלך כדי שנוכל לראות מה קרה
#         print(f"❌ AI Critical Error: {str(e)}")
#         return True, f"שגיאה טכנית: {str(e)}"
#
#
#
# def process_recipe_images(file, author_name):
#     """מייצר שם ייחודי ושומר 5 וריאציות + סימן מים. מחזיר (נתיב_ראשי, מילון_וריאציות)"""
#     file.seek(0)  # וודוא שהקובץ נקרא מהתחלה
#     # 1. יצירת שמות וקבצים
#     safe_filename = secure_filename(file.filename)
#     name_part, extension = os.path.splitext(safe_filename)
#     if not extension: extension = '.jpg'
#
#     unique_filename = f"{name_part}_{str(uuid.uuid4())[:8]}{extension}"
#     # upload_folder = os.path.join('static', 'uploads', 'recipes')
#     upload_folder=current_app.config['UPLOAD_FOLDER']
#
#     if not os.path.exists(upload_folder):
#         os.makedirs(upload_folder)
#
#     main_path = os.path.join(upload_folder, unique_filename)
#     file.save(main_path)
#
#     # 2. פתיחת התמונה לעיבוד
#     img = Image.open(main_path)
#     if img.mode in ("RGBA", "P"):
#         img = img.convert("RGB")
#
#     width, height = img.size
#     variations = {}
#
#     # א. Thumbnail
#     thumb = img.copy()
#     thumb.thumbnail((150, 150))
#     t_path = os.path.join(upload_folder, f"thumb_{unique_filename}")
#     thumb.save(t_path)
#     variations['thumb'] = t_path
#
#     # ב. Medium
#     medium = img.copy()
#     medium.thumbnail((500, 500))
#     m_path = os.path.join(upload_folder, f"medium_{unique_filename}")
#     medium.save(m_path)
#     variations['medium'] = m_path
#
#     # ג. Gray
#     g_path = os.path.join(upload_folder, f"gray_{unique_filename}")
#     img.copy().convert("L").save(g_path)
#     variations['gray'] = g_path
#
#     # ד. Vibrant
#     v_path = os.path.join(upload_folder, f"vibrant_{unique_filename}")
#     ImageEnhance.Color(img.copy()).enhance(1.6).save(v_path)
#     variations['vibrant'] = v_path
#
#     # ה. סימן מים (Watermark)
#     watermark_img = img.copy().convert("RGBA")
#     overlay = Image.new('RGBA', watermark_img.size, (0, 0, 0, 0))
#     draw = ImageDraw.Draw(overlay)
#
#     try:
#         font_size = int(height * 0.04)
#         font = ImageFont.truetype("arial.ttf", font_size)
#     except:
#         font = ImageFont.load_default()
#
#     text = f" Chef {author_name} "
#     bbox = draw.textbbox((0, 0), text, font=font)
#     tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
#     tx, ty = width - tw - 20, height - th - 20
#
#     draw.rectangle([tx - 10, ty - 10, tx + tw + 10, ty + th + 10], fill=(0, 0, 0, 160))
#     draw.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)
#
#     w_final = Image.alpha_composite(watermark_img, overlay).convert("RGB")
#     w_path = os.path.join(upload_folder, f"signed_{unique_filename}")
#     w_final.save(w_path)
#     variations['watermarked'] = w_path
#
#     return main_path, variations

import uuid
import io
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
from flask import current_app
import tensorflow as tf
import json


# טעינת המודל בצורה מפורשת - ResNet50
try:
    print("⏳ Loading AI Model (ResNet50)...")
    model = tf.keras.applications.MobileNetV2(weights='imagenet')
    preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input
    decode_predictions = tf.keras.applications.mobilenet_v2.decode_predictions
    print("✅ Model Loaded Successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None


def validate_is_food(file):
    if model is None:
        return False, "מערכת הזיהוי אינה זמינה"

    try:
        # 1. טעינת התמונה ועיבודה
        file.seek(0)
        img = Image.open(io.BytesIO(file.read())).convert('RGB').resize((224, 224))
        file.seek(0)

        x = tf.keras.preprocessing.image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

        # 2. זיהוי (מניב רשימת הסתברויות)
        preds = model.predict(x, verbose=0)

        # 3. טעינה ידנית של המילון מהתיקייה המקומית שלך
        # נתיב לקובץ שכבר נמצא אצלך:
        path_to_json = os.path.expanduser('~/.keras/models/imagenet_class_index.json')

        with open(path_to_json, 'r') as f:
            class_index = json.load(f)

        # 4. חילוץ התוצאות הכי גבוהות (כמו שעושה decode_predictions)
        top_indices = np.argsort(preds[0])[::-1][:5]  # לוקח את 3 התוצאות הראשונות

        # מילות מפתח לחסימת צילומי מסך ואישור אוכל
        food_keywords = [
            'food', 'dish', 'meal', 'pizza', 'bakery', 'cake', 'meat', 'soup',
            'stew', 'cuisine', 'plate', 'dessert', 'chocolate', 'confectionery',
            'brownie', 'pretzel', 'bun', 'dough', 'ice cream', 'trifle'
        ]
        # רשימת מילים שהמודל נוטה להתבלבל בהן כשיש אוכל (כמו סוכריות או מרקמים)
        # אם אחת מאלה היא התוצאה הראשונה, אנחנו נאשר אותה כ"חשודה כאוכל"
        false_negatives = ['pinwheel', 'honeycomb', 'artichoke', 'trifle', 'potpie']

        # מונחים טכניים שלעיתים המודל מתבלבל בינם לבין אוכל בתמונות תקריב
        ambiguous_keywords = ['pinwheel', 'artichoke', 'honeycomb']
        detected_labels = []
        is_food = False
        highest_confidence_label = ""

        for i in top_indices:
            # שליפת השם מהמילון המקומי: class_index[index] מחזיר [ID, Name]
            label = class_index[str(i)][1].lower().replace('_', ' ')
            confidence = preds[0][i]
            detected_labels.append(label)

            if not highest_confidence_label:
                highest_confidence_label = label

            # בדיקה האם המילה מזוהה כאוכל ורמת הביטחון מספקת
            if any(key in label for key in food_keywords) and confidence > 0.10:
                is_food = True
                print(f"✅ Food confirmed: {label} ({confidence:.2f})")
                return True, label
                # בונוס: טיפול במקרים כמו "שבבשת" (Pinwheel) שנובעים מסוכריות צבעוניות
            if any(key in label for key in ambiguous_keywords) and confidence > 0.30:
                 # אם המודל מאוד בטוח שזה 'pinwheel' בתמונה שהמשתמש טוען שהיא מתכון,
                # בשילוב עם מילות מפתח אחרות ב-Top 5, נטה לאשר.
                is_food = True
                return True, f"{label} (interpreted as food)"

        top_label = detected_labels[0]
        if any(fn in top_label for fn in false_negatives):
            print(f"⚠️ Warning: Detected {top_label}, allowing as food exception.")
            return True, f"{top_label} (recognized as food)"

        if is_food:
            print(f"✅ Food detected: {detected_labels[0]}")
            return True, detected_labels[0]
        else:
            print(f"❌ Not food: Detected {detected_labels[0]}")
            return False, f"Not food (detected: {detected_labels[0]})"

    except Exception as e:
        print(f"❌ Error in local validation: {e}")
        return False, "שגיאה בתהליך הזיהוי"
def process_recipe_images(file, author_name, recipe_folder_name):
    """מייצר שם ייחודי ושומר וריאציות של התמונה"""
    file.seek(0)

    # 1. הכנת נתיב התיקייה
    base_upload_folder = current_app.config['UPLOAD_FOLDER']
    # יצירת נתיב ספציפי: static/uploads/recipes/recipe_uuid
    recipe_specific_folder = os.path.join(base_upload_folder, recipe_folder_name)

    if not os.path.exists(recipe_specific_folder):
        os.makedirs(recipe_specific_folder)

    # 2.הכנת שמות הקבצים
    safe_filename = secure_filename(file.filename)
    name_part, extension = os.path.splitext(safe_filename)
    if not extension:
        extension = '.jpg'

    # unique_filename = f"{name_part}_{str(uuid.uuid4())[:8]}{extension}"
    unique_filename = f"{name_part}_{extension}"

    # נתיב ראשי בתוך התיקייה החדשה
    main_path = os.path.join(recipe_specific_folder, unique_filename)
    file.save(main_path)

    # upload_folder = current_app.config['UPLOAD_FOLDER']
    # if not os.path.exists(upload_folder):
    #     os.makedirs(upload_folder)

    # main_path = os.path.join(upload_folder, unique_filename)
    # file.save(main_path)

    # 3. פתיחת התמונה לעיבוד Pillow
    img = Image.open(main_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    width, height = img.size
    variations = {}

    # א. Thumbnail
    thumb = img.copy()
    thumb.thumbnail((150, 150))
    t_path = os.path.join(recipe_specific_folder, f"thumb_{unique_filename}")
    thumb.save(t_path)
    variations['thumb'] = t_path

    # ב. Medium
    medium = img.copy()
    medium.thumbnail((500, 500))
    m_path = os.path.join(recipe_specific_folder, f"medium_{unique_filename}")
    medium.save(m_path)
    variations['medium'] = m_path

    # ג. Gray
    g_path = os.path.join(recipe_specific_folder, f"gray_{unique_filename}")
    img.copy().convert("L").save(g_path)
    variations['gray'] = g_path

    # ד. Vibrant
    v_path = os.path.join(recipe_specific_folder, f"vibrant_{unique_filename}")
    ImageEnhance.Color(img.copy()).enhance(1.6).save(v_path)
    variations['vibrant'] = v_path

    # ה. סימן מים (Watermark)
    watermark_img = img.copy().convert("RGBA")
    overlay = Image.new('RGBA', watermark_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font_size = int(height * 0.04)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = f" Chef {author_name} "
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = width - tw - 20, height - th - 20

    draw.rectangle([tx - 10, ty - 10, tx + tw + 10, ty + th + 10], fill=(0, 0, 0, 160))
    draw.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)

    w_final = Image.alpha_composite(watermark_img, overlay).convert("RGB")
    w_path = os.path.join(recipe_specific_folder, f"signed_{unique_filename}")
    w_final.save(w_path)
    variations['watermarked'] = w_path

    return main_path, variations
