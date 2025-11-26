recipe_sharing_flask_api/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   │
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── categories.py
│   │       ├── ingredients.py
│   │       ├── ratings.py
│   │       └── recipes.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── ingredient.py
│   │   ├── rating.py
│   │   ├── recipe.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── category_schema.py
│   │   ├── ingredient_schema.py
│   │   ├── rating_schema.py
│   │   ├── recipe_schema.py
│   │   └── user_schema.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── decorators.py
│       ├── responses.py
│       └── validators.py
│
├── instance/
├── migrations/
│   └── versions/
├── uploads/
├── .venv/
├── .env
├── .env.example
├── .gitignore
└── run.py
