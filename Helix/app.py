from flask import Flask, render_template, request
from langchain_community.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from groq import Groq

app = Flask(__name__, static_folder='static')

CHROMA_PATH = "chroma"
GROQ_API_KEY = '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'

groq_client = Groq(api_key=GROQ_API_KEY)

def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)

def generate_fitness_plan(age, gender, height, weight, activity_level, fitness_goal):
    bmi = calculate_bmi(weight, height)

    query_text = f"""
    Create a detailed and personalized daily workout routine and diet plan for a {age}-year-old {gender} with:
    - Height: {height} meters
    - Weight: {weight} kg
    - Daily activity level: {activity_level}
    - BMI: {bmi}
    - Fitness goal: {fitness_goal}s
    Response Requirements:
    - Workout plan with specific exercises, durations, and intensities.
    - Diet plan with meals, calories, and macros.
    - Leave a line after each heading.
    """

    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedder)

    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if not results or results[0][1] < 0.5:
        return "Unable to find relevant context in the database."

    context_points = [f"Example {i+1}: {doc.page_content}" for i, (doc, _) in enumerate(results)]
    context_text = "\n\n---\n\n".join(context_points)

    full_prompt = f"""
    Context:
    {context_text}

    Based on the above context, create a detailed and personalized fitness plan for the user.

    User Attributes:
    {query_text}

    Response Requirements:
    - Workout plan with specific exercises, durations, and intensities.
    - Diet plan with meals, calories, and macros.

    Response:
    Provide a detailed response in plain text, not as a tool call or structured JSON.
    """

    completion = groq_client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.5,
        max_tokens=1024,
        top_p=0.65,
        stream=False
    )

    response_text = completion.choices[0].message.content
    #sources = [f"{doc.metadata.get('source', 'unknown')} (Example {i+1})" for i, (doc, _) in enumerate(results)]
    formatted_response = f"\nYour BMI is {bmi}.\n{response_text}"
    return formatted_response

@app.route('/')
def index():
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

        #print("\n\n\n\n\n\n\n",f"Age: {age}, Gender: {gender}, Height: {height}, Weight: {weight}, Activity Level: {activity_level}, Fitness Goal: {fitness_goal}")

        result_text = generate_fitness_plan(age, gender, height, weight, activity_level, fitness_goal)
        return render_template('result.html', result=result_text)

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
