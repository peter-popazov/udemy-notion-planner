import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
from joblib import dump

def train():
    data = pd.read_csv('train.csv', encoding='utf-16')
    titles = data['title']
    categories = data['category']

    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(titles)
    y = categories

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler(with_mean=False)  # SVM requires sparse matrix for input
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    param_grid = {
        'C': [1, 10, 100],
        'gamma': [0.01, 0.1, 1],
        'kernel': ['linear', 'rbf', 'sigmoid']
    }

    grid_search = GridSearchCV(SVC(), param_grid, refit=True, verbose=2, cv=5, n_jobs=-1)
    grid_search.fit(X_train_scaled, y_train)

    svm_model = grid_search.best_estimator_

    y_pred = svm_model.predict(X_test_scaled)
    print("Classification Report:\n", classification_report(y_test, y_pred))
    print("Accuracy Score:", accuracy_score(y_test, y_pred))

    dump(svm_model, '../model/svm_model.joblib')
    dump(vectorizer, '../model/vectorizer.joblib')
    dump(scaler, '../model/scaler.joblib')

train()