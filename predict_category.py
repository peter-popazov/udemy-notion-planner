from joblib import load

def predict_lecture_category(data: str) -> str:
    model = load("model/svm_model.joblib")
    vectorizer = load("model/vectorizer.joblib")
    scaler = load("model/scaler.joblib")

    new_titles_transformed = vectorizer.transform([data])
    new_titles_scaled = scaler.transform(new_titles_transformed)
    predictions = model.predict(new_titles_scaled)

    return str(predictions[0])