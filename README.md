

🍳 Recipe Management System (Backend)
מערכת מתקדמת לניהול, חיפוש ודירוג מתכונים המבוססת על Flask. הפרויקט משלב יכולות בינה מלאכותית (AI) וארכיטקטורת קוד נקייה המיועדת להרחבה ולאבטחה מקסימלית.

🚀 Key Features | תכונות מרכזיות
AI Image Validation: אימות תמונות באמצעות מודל ResNet50. המערכת מוודאת שמשתמשים מעלים תמונות של אוכל בלבד ומסננת תוכן לא רלוונטי באופן אוטומטי.

Service-Layer Architecture: הפרדה מוחלטת בין שכבת הניתובים (Routes) ללוגיקה העסקית (Services), מה שמבטיח קוד קריא, ניתן לבדיקה (Testable) וקל לתחזוקה.

Role-Based Access Control (RBAC): ניהול הרשאות מבוסס תפקידים (Admin, Uploader, Reader) באמצעות דקורטורים מותאמים אישית.

Smart Search & Matching: אלגוריתם חיפוש חכם המחשב אחוזי התאמה (Match Score) לפי המצרכים שקיימים אצל המשתמש בבית.

Automated Image Processing: יצירת וריאציות של תמונות (Thumbnails) וניקוי מטא-דאטה בעזרת ספריית Pillow למניעת פרצות אבטחה.

🛠 Tech Stack | טכנולוגיות
תחום	טכנולוגיה
Framework	Flask
Database	SQLAlchemy (SQLite)
Authentication	Flask-JWT-Extended
AI / ML	TensorFlow & Keras (ResNet50)
Image Processing	Pillow (PIL)
Security	Flask-Limiter, Bcrypt
📂 Project Structure | מבנה הפרויקט
Plaintext
├── app/
│   ├── routes/          # ניהול נתיבי ה-API (Blueprints)
│   │   ├── auth_routes.py   # הרשמה והתחברות
│   │   ├── recipe_routes.py # ניהול מתכונים
│   │   └── admin_routes.py  # ניהול מערכת
│   ├── services/        # לוגיקה עסקית (Service Layer)
│   │   ├── auth_service.py
│   │   ├── recipe_service.py
│   │   └── admin_service.py
│   ├── utils/           # כלי עזר (AI, Decorators, Image Processing)
│   ├── models.py        # הגדרת טבלאות ה-Database
│   └── __init__.py      # אתחול האפליקציה והגדרות אבטחה
├── static/              # אחסון תמונות מעובדות
├── run.py               # נקודת ההרצה של הפרויקט
└── requirements.txt     # רשימת ספריות להתקנה
⚙️ Setup & Installation | הוראות הרצה
התקנת הספריות:

Bash
pip install -r requirements.txt
הרצת השרת:

Bash
python run.py
כתובת השרת:
השרת יהיה זמין בכתובת: http://127.0.0.1:5000

🔐 Security | אבטחת מידע
המערכת הוקשחה בשלוש שכבות הגנה:

אימות: שימוש בטוקנים מסוג JWT. יש להוסיף את הטוקן ב-Header של הבקשות: Authorization: Bearer <token>.

מניעת הזרקות: שימוש ב-ORM למניעת SQL Injection וניקוי שמות קבצים באמצעות secure_filename.

הגבלת קצב: שימוש ב-Rate Limiter למניעת התקפות Brute Force על נתיבי הגישה.