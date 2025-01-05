from joblib import load

def predict_lecture_category(data):
    model = load('./model/svm_model.joblib')
    vectorizer = load('./model/vectorizer.joblib')
    scaler = load('./model/scaler.joblib')

    new_titles_transformed = vectorizer.transform(data)
    new_titles_scaled = scaler.transform(new_titles_transformed)
    predictions = model.predict(new_titles_scaled)

    print(predictions)
    return predictions


titles = [
    "Assigment: Implement Spring Security",
    "Why use Frameworks?",
    "Learn calculus in 10 minutes",
    "What are RDBMs?",
    "Code your first controller",
    "Quiz: Module 5",
    "Discussion: What is the benefit of using libraries?"
]

predict_lecture_category(titles)
