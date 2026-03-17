<div dir="rtl">

# 🍳 Recipe Management System (Backend)

מערכת חכמה לניהול, חיפוש ודירוג מתכונים המבוססת על **Flask**. הפרויקט משלב יכולות בינה מלאכותית (AI) וארכיטקטורת קוד נקייה (Service Layer) המיועדת להרחבה ולאבטחה מקסימלית.

---

## 🚀 Key Features | תכונות מרכזיות

* **AI Image Validation:** אימות תמונות באמצעות מודל **ResNet50**. המערכת מוודאת שמשתמשים מעלים תמונות של אוכל בלבד ומסננת תוכן לא רלוונטי באופן אוטומטי.
* **Service-Layer Architecture:** הפרדה מוחלטת בין שכבת הניתובים (**Routes**) ללוגיקה העסקית (**Services**), מה שמבטיח קוד קריא וקל לתחזוקה.
* **Role-Based Access Control (RBAC):** ניהול הרשאות מבוסס תפקידים (**Admin, Uploader, Reader**) באמצעות דקורטורים מותאמים אישית.
* **Smart Search & Matching:** אלגוריתם חיפוש חכם המחשב אחוזי התאמה (**Match Score**) לפי המצרכים הקיימים אצל המשתמש.
* **Automated Image Processing:** יצירת Thumbnails וניקוי מטא-דאטה בעזרת ספריית **Pillow** למניעת פרצות אבטחה.

---

## 🛠 Tech Stack | טכנולוגיות

| תחום | טכנולוגיה |
| :--- | :--- |
| **Framework** | Flask |
| **Database** | SQLAlchemy (SQLite) |
| **Authentication** | Flask-JWT-Extended |
| **AI Engine** | TensorFlow & Keras (ResNet50) |
| **Image Processing** | Pillow (PIL) |
| **Security** | Flask-Limiter, Bcrypt |

---

## 📂 Project Structure | מבנה הפרויקט

</div>

```plaintext
├── app/
│   ├── routes/          # ניהול נתיבי ה-API (Blueprints)
│   ├── services/        # לוגיקה עסקית (Service Layer)
│   ├── utils/           # כלי עזר (AI, Decorators, Image Processing)
│   ├── models.py        # הגדרת טבלאות ה-Database
│   └── __init__.py      # אתחול האפליקציה והגדרות אבטחה
├── static/              # אחסון תמונות מעובדות
├── run.py               # נקודת ההרצה של הפרויקט
└── requirements.txt     # רשימת ספריות להתקנה
```
<div dir="rtl">

---

## ⚙️ Setup & Installation | הוראות הרצה

1.  **התקנת הספריות:** `pip install -r requirements.txt`

2.  **הרצת השרת:** `python run.py`

3.  **כתובת השרת:** השרת יהיה זמין בכתובת: `http://127.0.0.1:5000`

---

## 🔐 Security | אבטחת מידע

המערכת משתמשת בטוקנים מסוג **JWT**. יש להוסיף את הטוקן ב-Header של הבקשות המאובטחות בצורה הבאה:  
`Authorization: Bearer <your_token>`

---

*הפרויקט פותח כחלק מלימודי פיתוח תוכנה.*

</div>