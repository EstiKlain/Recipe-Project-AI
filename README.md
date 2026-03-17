Recipe Management System (Backend)
מערכת מתקדמת לניהול, חיפוש ודירוג מתכונים המבוססת על Flask, המשלבת בינה מלאכותית (AI) וארכיטקטורת קוד נקייה מבוססת Services.

🚀 תכונות מרכזיות
AI Image Validation: שימוש במודל ResNet50 כדי לוודא שמשתמשים מעלים תמונות של אוכל בלבד.

Service-Layer Architecture: הפרדה מוחלטת בין שכבת הניתובים (Routes) ללוגיקה העסקית (Services).

מערכת הרשאות מבוססת תפקידים: שימוש ב-Decorators לניהול גישה עבור Reader, Uploader, ו-Admin.

חיפוש ומיון חכם: אלגוריתם לחישוב אחוזי התאמה לפי מצרכים ואפשרות מיון לפי זמן הכנה, דירוג או קושי.

עיבוד תמונות אוטונומי: יצירת ווריאציות (thumbnails) באופן אוטומטי בעת העלאת מתכון.

🛠 טכנולוגיות
Framework: Flask.

Database: SQLAlchemy (SQLite).

Security: Flask-JWT-Extended.

AI Engine: TensorFlow & Keras.

Image Processing: Pillow (PIL).

📂 מבנה הפרויקט (לפי המבנה שלך)
Plaintext

├── app/
│   ├── routes/          # ניהול נתיבי ה-API (Blueprints)
│   │   ├── auth_routes.py   # הרשמה והתחברות
│   │   ├── recipe_routes.py # ניהול מתכונים
│   │   └── admin_routes.py  # ניהול מנהל ומערכת
│   ├── services/        # לוגיקה עסקית (Service Layer)
│   │   ├── auth_service.py
│   │   ├── recipe_service.py
│   │   └── admin_service.py
│   ├── utils/           # כלי עזר (AI, דקורטורים, עיבוד תמונה)
│   ├── models.py        # הגדרת טבלאות ה-DB
│   └── __init__.py      # אתחול האפליקציה
├── static/              # אחסון תמונות מעובדות
├── run.py               # נקודת ההרצה של הפרויקט
└── requirements.txt     # רשימת ספריות להתקנה
⚙️ הוראות הרצה
התקנת הספריות: pip install -r requirements.txt

הרצת השרת: python run.py

השרת יהיה זמין בכתובת: http://127.0.0.1:5000

🔐 אבטחה
המערכת משתמשת בטוקנים מסוג JWT לצורך אימות. יש להוסיף את הטוקן ב-Header של הבקשות המאובטחות: Authorization: Bearer <your_token>