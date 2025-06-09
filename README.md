# AI Product Review Explorer (Learning Project)

Welcome to the **AI Product Review Explorer**! This is my very first data engineering and AI project, created as a learning experience to explore modern data tools, cloud databases, and AI-powered insights.

## What does this app do?

- **Connects to Supabase**: Fetches product review data from a Supabase cloud database.
- **Cleans and Visualizes Data**: Uses Python (pandas, matplotlib, Streamlit) to clean, summarize, and visualize product prices, ratings, and categories.
- **AI-Powered Insights**: Integrates with Groq's LLM (via LangChain) to generate smart, human-readable insights about the data.
- **Interactive Web App**: Built with Streamlit, so you can explore the data, see charts, and get AI-generated observations with a click.

## Why did I build this?

This is my first end-to-end project in data engineering and AI. My goal was to learn:
- How to ingest and clean real-world data
- How to use Supabase as a cloud database
- How to build interactive dashboards with Streamlit
- How to use large language models (LLMs) for data analysis
- How to connect all these tools together in Python

## How to run the app

1. **Clone this repo and install requirements:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Set up your `.env` file** with your Supabase and Groq API keys (see the provided `.env` example).
3. **Run the Streamlit app:**
   ```sh
   streamlit run class3_app.py
   ```

## Project Structure
- `class1_ingest.py`: Ingests and cleans CSV data, uploads to Supabase
- `class2_vz.py`: Data cleaning, summary stats, and matplotlib visualizations
- `class3_app.py`: The main Streamlit app with AI-powered insights
- `requirements.txt`: All Python dependencies
- `data/`: Example data files
- `data_visualizations/`: Saved charts

---

Thank you for checking out my project! As this is my first attempt, feedback and suggestions are welcome.