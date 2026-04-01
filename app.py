from flask import Flask, render_template, request
import csv
import os

app = Flask(__name__)

# File path (important for Railway)
file_path = os.path.join(os.getcwd(), 'data.csv')

# Create CSV if not exists
if not os.path.exists(file_path):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','score'])


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/quiz')
def quiz():
    return render_template('quiz.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/report')
def report():
    return render_template('report.html')


@app.route('/submit', methods=['POST'])
def submit():
    score = 0
    answers = []

    tech_keywords = ["code", "computer", "software", "math", "data", "programming"]
    business_keywords = ["people", "talk", "manage", "business", "leader", "communication"]

    for key in request.form:
        answer = request.form[key].lower()
        answers.append(answer)

        for word in tech_keywords:
            if word in answer:
                score += 1

        for word in business_keywords:
            if word in answer:
                score -= 1

    # Save data
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(answers + [score])

    if score > 0:
        result = "Technology Career (Software, Data, IT)"
    else:
        result = "Business / Social Career (Management, Marketing)"

    return render_template('result.html', result=result)


# 🚀 IMPORTANT FOR RAILWAY
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)