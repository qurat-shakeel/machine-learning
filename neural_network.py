# -*- coding: utf-8 -*-
"""neural_network.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lbg2Ko6UikuLX2tseN6WJ99upjVFSoEg
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV
from scikeras.wrappers import KerasClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
import random

!pip install scikeras

# Set random seeds for reproducibility
seed = 42
np.random.seed(seed)
tf.random.set_seed(seed)
random.seed(seed)

df = pd.read_csv("titanicc.csv")

# Feature engineering
df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
df['Title'] = df['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
df['Title'] = df['Title'].replace(['Lady', 'Countess', 'Capt', 'Col',
                                    'Don', 'Dr', 'Major', 'Rev', 'Sir',
                                    'Jonkheer', 'Dona'], 'Rare')
df['Title'] = df['Title'].replace('Mlle', 'Miss')
df['Title'] = df['Title'].replace('Ms', 'Miss')
df['Title'] = df['Title'].replace('Mme', 'Mrs')

columns_to_drop = ['PassengerId', 'Ticket', 'Fare', 'Name', 'Cabin']
X = df.drop(columns=columns_to_drop)
y = df['Survived']

# Handle missing values
numerical_features = ['Age', 'SibSp', 'Parch', 'FamilySize']
categorical_features = ['Pclass', 'Sex', 'Embarked', 'Title']

numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)
    ])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=seed)

X_train = preprocessor.fit_transform(X_train)
X_test = preprocessor.transform(X_test)

X_train = np.array(X_train)
X_test = np.array(X_test)
y_train = np.array(y_train)
y_test = np.array(y_test)



def create_model(learning_rate=0.001, dropout_rate=0.3, l2_reg=0.001):
    model = Sequential([
        Dense(128, input_dim=X_train.shape[1], activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l2_reg)),
        Dropout(dropout_rate),
        Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l2_reg)),
        Dropout(dropout_rate),
        Dense(32, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l2_reg)),
        Dropout(dropout_rate),
        Dense(1, activation='sigmoid')
    ])
    optimizer = Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

model = KerasClassifier(model=create_model, verbose=0)

# Define hyperparameters grid
param_grid = {
    'batch_size': [16, 32, 64],
    'epochs': [50, 100, 200],
    'model__learning_rate': [0.001, 0.01, 0.1],
    'model__dropout_rate': [0.3, 0.4, 0.5],
    'model__l2_reg': [0.001, 0.01]
}

early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

random_search = RandomizedSearchCV(estimator=model, param_distributions=param_grid, n_iter=10, cv=3, verbose=1, random_state=seed)
random_search_result = random_search.fit(X_train, y_train, validation_data=(X_test, y_test), callbacks=[early_stopping])

history = model.fit(X_train, y_train, epochs=100, validation_data=(X_test, y_test), callbacks=[early_stopping])

best_model = random_search_result.best_estimator_
loss, accuracy = best_model.model_.evaluate(X_test, y_test)
print(f'Best Model Test Accuracy: {accuracy * 100:.2f}%')