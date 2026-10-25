#%%
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from xgboost import XGBRegressor

print("Imports loaded successfully!")
#%%
# Load dataset
data_path = os.path.join("..", "data", "salary_data.csv")
df = pd.read_csv(data_path)

print(df.describe())
print("Original shape:", df.shape)

# 1. Drop exact duplicates
df = df.drop_duplicates()

# 2. Drop rows with missing target values (Salary)
df = df.dropna(subset=['Salary'])

# 3. Remove logical outliers/impossible values (Age reference removed since feature is dropped)
df = df[(df['Salary'] > 0) & (df['Years of Experience'] >= 0)]

print("Cleaned shape:", df.shape)
df.head()
#%%
# Separate features (Excluding Age and Gender to prevent collinearity and OOD issues)
numeric_features = ['Years of Experience']
categorical_features = ['Education Level', 'Job Title']

X = df[numeric_features + categorical_features]
y = df['Salary']

# Split data for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training samples: {X_train.shape[0]}")
print(f"Testing samples: {X_test.shape[0]}")
#%%
# Numeric pipeline: Impute missing values with median
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

# Categorical pipeline: Impute missing with constant string, then one-hot encode
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

# Transform the features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Set up training pipeline with XGBoost Regressor
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('feature_selector', SelectKBest(score_func=f_regression, k='all')),
    ('model', XGBRegressor(random_state=42, objective='reg:squarederror'))
])
#%%
# Tuned hyperparameter grid for XGBoost
param_grid = {
    'model__n_estimators': [100, 200],
    'model__max_depth': [3, 5, 7],
    'model__learning_rate': [0.01, 0.1, 0.2]
}

# Train model using GridSearchCV
grid_search = GridSearchCV(
    estimator=pipeline,
    param_grid=param_grid,
    cv=5,
    scoring='r2',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print(f"Best R² Score on Cross-Validation: {grid_search.best_score_:.4f}")
print(f"Best Parameters: {grid_search.best_params_}")
#%%
best_model = grid_search.best_estimator_

# Evaluate performance on test set
y_pred = best_model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"Test Set R² Score: {r2:.4f}")
print(f"Test Set RMSE: ${rmse:,.2f}")

# Save trained model pipeline
os.makedirs(os.path.join("..", "models"), exist_ok=True)
model_path = os.path.join("..", "models", "salary_pipeline.joblib")
joblib.dump(best_model, model_path)

print(f"Pipeline successfully saved to {model_path}!")