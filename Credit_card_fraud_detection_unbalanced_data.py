# -*- coding: utf-8 -*-
"""Copy of Project 10. Credit Card Fraud Detection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eXMjE6ZSewYcGGtXmY-TkiMWTSQtIp0U

Importing the Dependencies
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from random import randrange, uniform
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, recall_score

# loading the dataset to a Pandas DataFrame
credit_card_data = pd.read_csv('/content/creditcard.csv')

# first 5 rows of the dataset
credit_card_data.head()

credit_card_data.tail()

# dataset informations
credit_card_data.info()

# checking the number of missing values in each column
credit_card_data.isnull().sum()

# distribution of legit transactions & fraudulent transactions
credit_card_data['Class'].value_counts()

"""This Dataset is highly unblanced

0 --> Normal Transaction

1 --> fraudulent transaction
"""

# separating the data for analysis
legit = credit_card_data[credit_card_data.Class == 0]
fraud = credit_card_data[credit_card_data.Class == 1]

print(legit.shape)
print(fraud.shape)

# statistical measures of the data
legit.Amount.describe()

fraud.Amount.describe()

# compare the values for both transactions
credit_card_data.groupby('Class').mean()

"""Under-Sampling

Build a sample dataset containing similar distribution of normal transactions and Fraudulent Transactions

Number of Fraudulent Transactions --> 492
"""

legit_sample = legit.sample(n=492)

"""Concatenating two DataFrames"""

new_dataset = pd.concat([legit_sample, fraud], axis=0)

new_dataset.head()

new_dataset.tail()

new_dataset['Class'].value_counts()

new_dataset.groupby('Class').mean()

"""Splitting the data into Features & Targets"""

X = new_dataset.drop(columns='Class', axis=1)
Y = new_dataset['Class']

print(X)

print(Y)

"""Split the data into Training data & Testing Data"""

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, stratify=Y, random_state=2)

print(X.shape, X_train.shape, X_test.shape)

"""Model Training

Logistic Regression
"""

model = LogisticRegression()

# training the Logistic Regression Model with Training Data
model.fit(X_train, Y_train)

"""Model Evaluation

Accuracy Score
"""

# accuracy on training data
X_train_prediction = model.predict(X_train)
training_data_accuracy = accuracy_score(X_train_prediction, Y_train)

print('Accuracy on Training data : ', training_data_accuracy)

# accuracy on test data
X_test_prediction = model.predict(X_test)
test_data_accuracy = accuracy_score(X_test_prediction, Y_test)

print('Accuracy score on Test Data : ', test_data_accuracy)

"""Synthetic Minority Oversampling"""

def SMOTE(sample: np.array, N: int, k: int) -> np.array:

    T, num_attrs = sample.shape

    # If N is less than 100%, randomize the minority class samples as only a random percent of them will be SMOTEd
    if N < 100:
        T = round(N / 100 * T)
        N = 100
    # The amount of SMOTE is assumed to be in integral multiples of 100
    N = int(N / 100)
    synthetic = np.zeros([T * N, num_attrs])
    new_index = 0
    nbrs = NearestNeighbors(n_neighbors=k+1).fit(sample.values)

    def populate(N, i, nnarray):

        nonlocal new_index
        nonlocal synthetic
        nonlocal sample
        while N != 0:
            nn = randrange(1, k+1)
            for attr in range(num_attrs):
                dif = sample.iloc[nnarray[nn]][attr] - sample.iloc[i][attr]
                gap = uniform(0, 1)
                synthetic[new_index][attr] = sample.iloc[i][attr] + gap * dif
            new_index += 1
            N = N - 1

    for i in range(T):
        nnarray = nbrs.kneighbors(sample.iloc[i].values.reshape(1, -1), return_distance=False)[0]
        populate(N, i, nnarray)

    return synthetic

synthetic = SMOTE(fraud, N=200, k=5)

synthetic.shape

synthetic_df = pd.DataFrame(synthetic, columns=fraud.columns)
combined_minority_df = pd.concat([fraud, synthetic_df])
combined_minority_df["Class"] = 1

new_df = pd.concat([combined_minority_df, credit_card_data[credit_card_data['Class'] == 0]])

X = new_df.drop(['Class'], axis=1)
y = new_df['Class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf = RandomForestClassifier()
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)

test_data_accuracy = accuracy_score(y_pred, y_test)
recall_score = recall_score(y_pred, y_test)

test_data_accuracy

recall_score

