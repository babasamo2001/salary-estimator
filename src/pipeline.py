# Import libraries
import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder


def clean_train_and_save_model():
    # Load data
    BASE_DIR = Path(__file__).resolve().parent.parent
    PATH = BASE_DIR / "data" / "salary_data.csv"
    df = pd.read_csv(PATH)

    # Convert data format to efficient parquet format
    df.to_parquet(BASE_DIR / "data" / "salary_data.parquet")
    df = pd.read_parquet(BASE_DIR / "data" / "salary_data.parquet")

    print("Original shape:", df.shape)

    # Drop duplicates
    print("Total exact duplicate rows:", df.duplicated().sum())
    df = df.drop_duplicates()
    df = df.dropna(subset=['Salary', 'Age', 'Years of Experience'])
    df = df[(df['Salary'] > 0) & (df['Years of Experience'] >= 0) & (df['Age'] > 15)]

    print("Cleaned shape:", df.shape)

    # Separate data features for transformations
    numeric_features = ['Age', 'Years of Experience']
    categorical_features = ['Gender', 'Education Level', 'Job Title']

    X = df[numeric_features + categorical_features]
    y = df['Salary']

    # Split data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Set up training variables
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('feature_selector', SelectKBest(score_func=f_regression, k='all')),
        ('model', RandomForestRegressor(random_state=42))
    ])

    param_grid = {
        'model__n_estimators': [50, 100, 200],
        'model__max_depth': [None, 10, 20]
    }

    # Train and save the best model
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=5,
        scoring='r2',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    os.makedirs("models", exist_ok=True)
    model_path = os.path.join("models", "salary_pipeline.joblib")
    joblib.dump(grid_search.best_estimator_, model_path)
    print(f"Pipeline model successfully trained and saved to {model_path}!")


if __name__ == "__main__":
    clean_train_and_save_model()
