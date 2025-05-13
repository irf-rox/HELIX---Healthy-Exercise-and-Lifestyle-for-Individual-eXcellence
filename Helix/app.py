import os
from flask import Flask, render_template, request
from langchain_community.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from groq import Groq
from drive_downloader import download_chroma_from_drive

app = Flask(__name__, static_folder='static')

CHROMA_PATH = "temp_chroma/chroma"
GROQ_API_KEY = '<your_api_key>'
PARENT_FOLDER_ID = "188eYmPiSfbEaRA8rpZBlTWNYIGjppLXX"

groq_client = Groq(api_key=GROQ_API_KEY)

def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)

def generate_fitness_plan(age, gender, height, weight, activity_level, fitness_goal):
    bmi = calculate_bmi(weight, height)

    query_text = f"""
    Create a detailed and personalized daily workout routine, a detailed diet plan and additional health tips for a {age}-year-old {gender} with:
    - Height: {height} meters
    - Weight: {weight} kg
    - Daily activity level: {activity_level}
    - BMI: {bmi}
    - Fitness goal: {fitness_goal}
    Response Requirements:
    - Workout plan with specific exercises, durations, and intensities.
    - Diet plan with meals, calories, and macros.
    - Leave a line after each heading.
    """

    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedder)

    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    # if not results or results[0][1] < 0.5:
    #     return "Unable to find relevant context in the database."
    if not results or any(len(result) < 2 for result in results) or results[0][1] < 0.5:
        return "Unable to find relevant context in the database."


    context_points = [f"Example {i+1}: {doc.page_content}" for i, (doc, score) in enumerate(results) if score >= 0.5]
    if not context_points:
        return "Unable to find relevant context in the database."
    context_text = "\n\n---\n\n".join(context_points)


    full_prompt = f"""
    Context:
    {context_text}

    Based on the above context, create a detailed and personalized fitness plan for the user.

    User Attributes:
    {query_text}

    **Instructions:**
    - Only respond with a fitness plan, a diet plan and some additional health tips including:
        1. Workout plan with specific exercises, durations, and intensities with each workout listed point-wise and in a detailed manner.
        2. Diet plan with meals, calories, and macros with each food listed point-wise and include the nutrition information.
    - Always include the three headings workout plan, diet plan and additional tips.
    - Do NOT include any other information like book recommendations, unrelated advice, or general fitness trends.
    - Format the response in plain text.

    Begin the response with the physical workouts plan and then continue with the diet plan and any additional tips.

    Response:
    Provide a detailed response in plain text, not as a tool call or structured JSON.
    """

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.5,
        max_tokens=1024,
        top_p=0.65,
        stream=False
    )

    response_text = completion.choices[0].message.content
    formatted_response = f"\nYour BMI is {bmi}\n{response_text}"
    return formatted_response

@app.route('/')
def index():
    download_chroma_from_drive(PARENT_FOLDER_ID)
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    try:
        age = int(request.form['age'])
        gender = request.form['gender']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        activity_level = request.form['activity_level']
        fitness_goal = request.form['fitness_goal']

    #     result_text = generate_fitness_plan(age, gender, height, weight, activity_level, fitness_goal)
    #     if "Unable to find relevant context" in result_text:
    #         return render_template('result.html', result=None, error_message="Sorry, we couldn't prepare a fitness plan for you. Please try again with correct details.")
    #     return render_template('result.html', result=result_text)
    # except Exception as e:
    #     return f"An error occurred: {str(e)}"

        result_text = generate_fitness_plan(age, gender, height, weight, activity_level, fitness_goal)
        print(result_text)
        bmi = None
        workout_plan = None
        diet_plan = None
        additional_tips = None

        if "Your BMI is " in result_text:
            bmi = result_text.split("Your BMI is ")[1].split("\n")[0].strip()
        if "**Workout Plan**" in result_text and "**Diet Plan**" in result_text:
            workout_plan = result_text.split("**Workout Plan**")[1].split("**Diet Plan**")[0].strip()
        if "**Diet Plan**" in result_text and "**Additional Tips**" in result_text:
            diet_plan = result_text.split("**Diet Plan**")[1].split("**Additional Tips**")[0].strip()
        if "**Additional Tips**" in result_text:
            additional_tips = result_text.split("**Additional Tips**")[1].strip()

        return render_template(
            'result.html',
            bmi=bmi,
            workout_plan=workout_plan,
            diet_plan=diet_plan,
            additional_tips=additional_tips,
            error_message=None
        )
    except Exception as e:
        return f"An error occurred: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
