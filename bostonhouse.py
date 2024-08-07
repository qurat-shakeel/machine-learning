# -*- coding: utf-8 -*-
"""BostonHouse.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Pa_NLjGEB63tA0isA-b9cU5V3DouHyRp
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

data = pd.read_csv('Boston Dataset.csv')
data

! pip install ydata_profiling
 import matplotlib.pyplot as plt
 from ydata_profiling import ProfileReport
 profile = ProfileReport(data)
 profile.to_file('housingprice.html')

from google.colab import files
files.download('housingprice.html')

data.drop(columns='Unnamed: 0',axis=0,inplace=True)
data

data.info()

correlations_medv = data.corr()['medv']

# Identify columns to drop based on correlation threshold
columns_to_drop = correlations_medv[abs(correlations_medv) < 0.2].index
# Drop the identified columns from the DataFrame
data = data.drop(columns=columns_to_drop)

# Display the modified DataFrame
print(data)

# Separate features and target
X = data.drop(columns=['medv'])
y = data['medv']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

! pip install lazypredict

from lazypredict.Supervised import LazyRegressor

# Initialize LazyRegressor
lazy = LazyRegressor(verbose=0, ignore_warnings=True, custom_metric=None)

# Fit and evaluate models
models, predictions = lazy.fit(X_train, X_test, y_train, y_test)

# Display the results
print(models)

# Find the model with the highest R-squared value
best_model_name = models.sort_values(by='R-Squared', ascending=False).iloc[0].name
print(f"Best Model: {best_model_name}")

import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor

if best_model_name == 'GradientBoostingRegressor':
    best_model = GradientBoostingRegressor()
elif best_model_name == 'LinearRegression':
    best_model = LinearRegression()
else:
    raise ValueError("Unexpected best model name")

# Fit the best model
best_model.fit(X_train, y_train)

# Save the model
joblib.dump(best_model, 'best_model.pkl')

# Load the saved model
loaded_model = joblib.load('best_model.pkl')

# Make predictions
y_pred = loaded_model.predict(X_test)

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# Calculate evaluation metrics

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
adjusted_r2 = 1 - (1-r2) * (len(y_test)-1) / (len(y_test) - X_test.shape[1] - 1)

print(f"MAE of the best model: {mae}")
print(f"RMSE of the best model: {rmse}")
print(f"R-squared of the best model: {r2}")
print(f"Adjusted R-squared of the best model: {adjusted_r2}")