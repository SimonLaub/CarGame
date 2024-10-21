"""
Car game project. October 2024.
- Programming a car game using an LLM
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 14:03:05 2024

@author: sila
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix

# Load the data from the Excel file
df = pd.read_excel('game_data.xlsx')

print ( df.describe( include = 'all' ))
print ( df.values)

# show the data
print ( df.describe( include = 'all' ))
print ( df.values)

# Prepare features and target variable
X = df[['Car_Offset', 'Traffic_Position']].to_numpy()  # Convert selected features to NumPy array
#X = df[['Car_Offset']].to_numpy()  # Convert selected features to NumPy array
y = df['User_action'].to_numpy()

'''from imblearn.over_sampling import SMOTE
smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X, y)'''

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale data set
scaler = StandardScaler()
scaler.fit(X_train)
xtrain = scaler.transform(X_train)
xtest= scaler.transform(X_test)

from sklearn.neural_network import MLPClassifier
mlp = MLPClassifier( hidden_layer_sizes =( 5, 5 ), max_iter = 100000 , random_state = 42 )

mlp.fit(xtrain, y_train)

#predictions
predictions = mlp.predict(xtest)

matrix = confusion_matrix(y_test,predictions)
print (matrix)
print (classification_report(y_test,predictions))
