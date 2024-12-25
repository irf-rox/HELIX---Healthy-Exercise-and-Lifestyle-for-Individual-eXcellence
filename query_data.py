from langchain_community.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.prompts import ChatPromptTemplate
from groq import Groq

CHROMA_PATH = "chroma"
GROQ_API_KEY = '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'

PROMPT_TEMPLATE = """
Use the provided context to design a tailored, detailed fitness plan including workouts and diet.

Context:
{context}

Query:
{question}

Response Requirements:
- Workout plan: Include specific exercises, durations, and intensities.
- Diet plan: Provide detailed meals, calories, and macros tailored to goals and BMI.

Ensure the advice is practical, easy to follow, and aligned with the user's attributes.
"""

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)

def main():
    try:
        # Collect user inputs
        age = int(input("Enter your age: "))
        gender = input("Enter your gender (male/female): ").strip().lower()
        height = float(input("Enter your height in meters: "))
        weight = float(input("Enter your weight in kg: "))
        fitness_goal = input("Enter your fitness goal (e.g., weight loss, muscle gain): ").strip()

        # Calculate BMI
        bmi = calculate_bmi(weight, height)

        # Prepare the query
        query_text = f"""
        Create a personalized daily workout routine and diet plan for a {age}-year-old {gender} with:
        - Height: {height} meters
        - Weight: {weight} kg
        - BMI: {bmi}
        - Fitness goal: {fitness_goal}
        """

        # Prepare the DB with the custom embedding function (using SentenceTransformerEmbeddings)
        embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedder)

        # Search the DB
        results = db.similarity_search_with_relevance_scores(query_text, k=3)
        if not results or results[0][1] < 0.5:
            print("Unable to find relevant context in the database.")
            return

        # Consolidate Context
        context_points = []
        for i, (doc, _score) in enumerate(results):
            context_points.append(f"Example {i+1}: {doc.page_content}")
        context_text = "\n\n---\n\n".join(context_points)

        # Debug: Print context and query
        #print("Debug Context:", context_text)
        #print("Debug Query:", query_text)

        # Simplified prompt for better guidance
        full_prompt = f"""
        Context:
        {context_text}

        Based on the above context, create a personalized fitness plan for the user ni text form.

        User Attributes:
        {query_text}

        Response:
        - Workout plan with specific exercises, durations, and intensities.
        - Diet plan with meals, calories, and macros.


        Response Requirements:
        Provide the response in plain text, not as a tool call or structured JSON.
        """

        # Call the Groq API
        completion = groq_client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stream=False
        )

        # Collect the response
        response_text = completion.choices[0].message.content
        sources = [f"{doc.metadata.get('source', 'unknown')} (Example {i+1})" for i, (doc, _) in enumerate(results)]
        formatted_response = f"\n{response_text}\n\nSources:\n{', '.join(sources)}"
        print("\n\nResponse:", formatted_response)

    except Exception as e:
        print("Error occurred:", str(e))

if __name__ == "__main__":
    main()
