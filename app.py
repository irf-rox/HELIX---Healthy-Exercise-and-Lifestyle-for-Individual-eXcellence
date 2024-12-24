import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from groq import Groq

# Load dataset
dataset = pd.read_csv("Dataset/final_dataset.csv")

# Initialize Flask app
app = Flask(__name__)

# Function to calculate BMI
def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 1)

# Function to retrieve exercise plan
def retrieve_plan(bmi, gender, age, dataset):
    dataset['BMI'] = dataset['BMI'].round(1)
    user_data = dataset[ 
        (dataset['Gender'].str.lower() == gender.lower()) &
        (dataset['Age'] == age) &
        (dataset['BMI'] == bmi)
    ]
    if not user_data.empty:
        return user_data['Exercise Recommendation Plan'].iloc[0]
    return 1  # Default beginner plan if no match

# Function to generate recommendations using Groq API
def generate_recommendations(age, gender, height, weight, fitness_goal, plan_level):
    # Define the prompt
    prompt = f"""
    Create a daily workout routine and diet plan for a {age}-year-old {gender} 
    with a height of {height} meters, weight of {weight} kg, and fitness goal: {fitness_goal}. 
    Use an exercise intensity level {plan_level} from a scale of 1 to 7 where 1 being the lightest and 7 being the most intense.
    """

    try:
        # Initialize Groq client
        client = Groq(api_key="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")  # Replace with your actual API key

        # Generate text using the Groq model
        completion = client.chat.completions.create(
            model="llama3-groq-8b-8192-tool-use-preview",
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": ""}
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stream=True,
            stop=None,
        )

        # Process and return the generated response
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        return response.strip()

    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

# Route for the input form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        age = int(request.form["age"])
        gender = request.form["gender"]
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        fitness_goal = request.form["fitness_goal"]

        # Calculate BMI
        bmi = calculate_bmi(weight, height)

        # Retrieve exercise recommendation plan
        plan_level = retrieve_plan(bmi, gender, age, dataset)

        # Generate recommendations using Groq API
        recommendations = generate_recommendations(age, gender, height, weight, fitness_goal, plan_level)

        # Redirect to result page with data
        return redirect(url_for("result", bmi=bmi, plan_level=plan_level, recommendations=recommendations))

    return render_template("index.html")

# Route for the result page
@app.route("/result")
def result():
    bmi = request.args.get("bmi")
    plan_level = request.args.get("plan_level")
    recommendations = request.args.get("recommendations")
    return render_template("result.html", bmi=bmi, plan_level=plan_level, recommendations=recommendations)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
