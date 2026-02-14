from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Database create karna
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            result TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Automation Logic (kal yahi change karenge)
def process_data(user_input):
    text = user_input.lower()
    words = text.split()
    word_count = len(words)

    # Common keyword groups (easy to modify tomorrow)
    categories = {
        "Education": ["study", "exam", "school", "college", "subject"],
        "Health": ["pain", "fever", "cold", "cough", "headache"],
        "Finance": ["money", "expense", "budget", "salary", "loan"],
        "Environment": ["waste", "plastic", "pollution", "climate", "water"]
    }

    detected_category = "General"

    for category, keywords in categories.items():
        for word in words:
            if word in keywords:
                detected_category = category
                break

    # Simple scoring logic
    score = word_count * 2

    return f"""
    Word Count: {word_count} <br>
    Detected Category: {detected_category} <br>
    Generated Score: {score}
    """


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    # user_input = request.form["user_input"]
    # result = process_data(user_input)

    # conn = sqlite3.connect("data.db")
    # c = conn.cursor()
    # c.execute("INSERT INTO submissions (user_input, result) VALUES (?, ?)", (user_input, result))
    # conn.commit()
    # conn.close()
    user_input = request.form["user_input"]
    result = process_data(user_input)

    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    # Save new submission
    c.execute("INSERT INTO submissions (user_input, result) VALUES (?, ?)", 
              (user_input, result))
    conn.commit()

    # Fetch all data (Dashboard Logic)
    c.execute("SELECT user_input, result FROM submissions")
    data = c.fetchall()
    conn.close()

    total_entries = len(data)

    scores = []
    categories = []

    for entry in data:
        result_text = entry[1]

        try:
            score_part = result_text.split("Generated Score:")[1]
            score = int(score_part.strip().split()[0])
            scores.append(score)
        except:
            pass

        if "Detected Category:" in result_text:
            cat_part = result_text.split("Detected Category:")[1]
            category = cat_part.split("<br>")[0].strip()
            categories.append(category)

    avg_score = sum(scores) / len(scores) if scores else 0
    most_common_category = max(set(categories), key=categories.count) if categories else "None"

    return render_template("dashboard.html",
                           total_entries=total_entries,
                           avg_score=avg_score,
                           most_common_category=most_common_category,
                           data=data)

    return render_template("result.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
