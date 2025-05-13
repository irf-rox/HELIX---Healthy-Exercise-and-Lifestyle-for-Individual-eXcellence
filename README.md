# HELIX - Healthy Exercise and Lifestyle for Individual eXcellence 🌱💪

## Overview 🚀

HELIX is a personalized web application designed to help users maintain a healthy lifestyle by generating **fitness plans**, **diet recommendations**, and **lifestyle tips**. The application uses **Retrieving Augmented Generation (RAG)** models and **Llama3** from **Groq** to create customized suggestions based on user data. Built with **Flask**, HELIX also integrates **Google Drive API** to store **vector embeddings** for efficient data retrieval.

## Key Features 🌟

* **Personalized Fitness Plans**: Tailored workout routines based on your goals and health data 🏋️‍♂️
* **Diet Recommendations**: Meal plans designed to complement your fitness objectives 🍏🥗
* **Lifestyle Tips**: Expert advice for improving mental and physical well-being 🧘‍♀️
* **RAG Model Integration**: Generate recommendations using advanced models like Llama3 🤖
* **Cloud Storage for Embeddings**: Google Drive is used to store **vector embeddings**, allowing fast retrieval and cloud synchronization 📂
* **Web Interface**: A user-friendly web interface built using Flask 💻

## How It Works 🔧

1. **User Input**: Users input their personal data such as age, weight, and health goals.
2. **Data Processing**: The RAG model processes the input and retrieves relevant information to generate personalized plans.
3. **Vector Embedding Storage**: Vector embeddings, which represent fitness data and recommendations, are stored in **Google Drive** to optimize retrieval and recommendation generation.
4. **Personalized Recommendations**: Users receive custom fitness plans, diet suggestions, and lifestyle tips based on their data.
5. **Cloud Sync**: Embeddings are synchronized with Google Drive for efficient data retrieval.

## Installation Guide ⚙️

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/irf-rox/HELIX---Healthy-Exercise-and-Lifestyle-for-Individual-eXcellence.git
   cd HELIX---Healthy-Exercise-and-Lifestyle-for-Individual-eXcellence/Helix
   ```

2. **Install Required Dependencies**:
   Use pip to install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. **Google Drive API Setup**:

   * Visit the [Google Developers Console](https://console.developers.google.com/).
   * Create a new project and enable the **Google Drive API**.
   * Download the **credentials file** (`credentials.json`).
   * Follow the [Google Drive API Python Quickstart](https://developers.google.com/drive/api/v3/quickstart-python) to set up the credentials.

   Place the `credentials.json` file in the project directory.

4. **Run the Flask Application**:
   Start the Flask app:

   ```bash
   python app.py
   ```

5. **Access the Application**:
   Open your browser and go to `http://127.0.0.1:5000` to start using HELIX.

## Usage 💡

Once the app is up and running, use the following features:

1. **Input Your Data**: Enter your health data, including age, weight, and fitness goals.
2. **Choose Preferences**: Select the type of fitness plans, diet plans, and lifestyle tips you are interested in.
3. **Receive Recommendations**: Based on the data and preferences, the app will provide:

   * **Fitness Plan**: A workout schedule designed for your specific goals.
   * **Diet Plan**: Meal recommendations to complement your fitness routine.
   * **Lifestyle Tips**: Suggestions to help improve mental and physical health.
4. **Cloud Storage**: The app uses Google Drive to store vector embeddings of the data, ensuring efficient and quick retrieval for future sessions.

## System Architecture 🏗️

The application consists of several key components:

* **Flask**: Manages the web interface, routing, and user inputs.
* **RAG Model**: The core component that processes user input and generates recommendations.
* **Sentence Transformers**: Used for transforming textual data into vector embeddings.
* **Google Drive API**: Stores vector embeddings, ensuring efficient data management and retrieval.

## Cloud Storage for Vector Embeddings ☁️

Google Drive is used exclusively for storing **vector embeddings** — the mathematical representations of user preferences, fitness plans, and recommendations. The embeddings are stored in specific directories on Google Drive, allowing for fast retrieval and seamless synchronization across sessions.

### Setting Up Google Drive Sync

1. **Authentication**: The app requires user authentication to access Google Drive.
2. **Embedding Storage**: After generating the embeddings, they are saved in a directory structure within Google Drive, such as:

   * `/HELIX/Vector_Embeddings/`

## Challenges Faced and Solutions 💭

1. **Dataset Preparation**: The dataset had to be cleaned and transformed to fit the RAG model requirements. It involved removing redundant data and converting it into a Markdown format.
2. **API Key Setup**: Initially, obtaining a free API key for Llama3 was challenging, but after some research, I managed to secure one.
3. **Google Drive Integration**: Setting up and organizing Google Drive for embedding storage was complex but necessary for efficient data retrieval.

## Future Improvements 🔧

* **UI Enhancements**: Improve the user interface to make it more visually appealing and interactive.
* **Advanced Features**: Add functionality to track progress over time and provide ongoing recommendations.
* **Integration with Wearables**: Implement integration with fitness trackers to automatically update workout data.

## Contributing 🤝

Contributions are always welcome! If you'd like to contribute, fork the repository, make your changes, and submit a pull request.
