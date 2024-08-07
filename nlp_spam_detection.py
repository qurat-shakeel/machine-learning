# -*- coding: utf-8 -*-
"""NLP_spam_detection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13Q44fXKvjgCUa26XPJgC7EU0BcutqCE5
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Download NLTK data
nltk.download('stopwords')
nltk.download('wordnet')

df = pd.read_csv('SMS_detection.csv', encoding='latin-1')
df

df.head()

df.drop(['Unnamed: 2','Unnamed: 3','Unnamed: 4'],axis=1,inplace=True)
df

df= df.rename(columns={'v1':'label','v2':'message'})
df

df.shape

def preprocess_text(text):
    # Lowercase the text
    text = text.lower()

    # Remove special characters and digits
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\d', ' ', text)

    # Remove single characters
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Tokenize text
    tokens = text.split()

    # Remove stopwords and perform lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in set(stopwords.words('english'))]

    # Join tokens back into a single string
    text = ' '.join(tokens)

    return text

df['message'] = df['message'].apply(preprocess_text)

# Display the first few rows of the dataframe after preprocessing
df.head()

# Splitting the dataset
X = df['message']
y = df['label'].map({'ham': 0, 'spam': 1})

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Extraction using TF-IDF
tfidf_vectorizer = TfidfVectorizer(max_features=3000)
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

# Model Training
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Predictions
y_pred = model.predict(X_test_tfidf)

# Evaluation
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print("Classification Report:")
print(classification_report(y_test, y_pred))

!pip install sentence-transformers

from sentence_transformers import SentenceTransformer
from imblearn.over_sampling import SMOTE
# Load SBERT model
model = SentenceTransformer('all-distilroberta-v1')

# Generate SBERT embeddings for the training and test sets
X_train_embeddings = model.encode(X_train.tolist(), convert_to_numpy=True)
X_test_embeddings = model.encode(X_test.tolist(), convert_to_numpy=True)

# Handle class imbalance using SMOTE
smote = SMOTE(random_state=42, sampling_strategy=0.5)
X_train_smote, y_train_smote = smote.fit_resample(X_train_embeddings, y_train)

# Model Training
classifier = LogisticRegression(max_iter=1000)
classifier.fit(X_train_smote, y_train_smote)

y_pred = classifier.predict(X_test_embeddings)

# Evaluation
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print("Classification Report:")
print(classification_report(y_test, y_pred))



