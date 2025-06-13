# class3_app.py

# Imagine this as your kitchen: you need to import all your ingredients (libraries) before you start cooking (coding)
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# 1) Load environment variables
# Like checking your recipe card for secret ingredients (API keys) before you start
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Where your data lives (the address)
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # The key to unlock your data
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # The key to talk to the AI chef

# 2) Initialize Supabase and Groq clients
# Think of these as your kitchen helpers: one fetches ingredients (data), the other gives smart advice (AI)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
groq = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")  # You can swap the AI chef if you want

# 3) Fetch and clean Supabase data
# Like washing and chopping your veggies before cooking: make sure your data is clean and ready
@st.cache_data(show_spinner=False)
def load_data():
    res = supabase.table("product_reviews").select("*").execute()  # Grab all the data from the table
    df = pd.DataFrame(res.data)  # Put it in a nice table (DataFrame)
    # Clean numeric types (make sure numbers are really numbers, not text)
    df["actual_price"]        = df["actual_price"].astype(float)
    df["discounted_price"]    = df["discounted_price"].astype(float)
    df["discount_percentage"] = df["discount_percentage"].astype(float)
    df["rating"]              = df["rating"].astype(float)
    df["rating_count"]        = df["rating_count"].astype(int)
    return df

# 4) Generate LLM insights
# Like asking a wise chef: "What do you notice about these ingredients?" and getting smart tips back
def ask_ai(overview: dict, top_cats: list):
    messages = [
        SystemMessage(content="You are a data analyst idiot who lies in e-commerce sales."),
        HumanMessage(content=(
            f"Here are key product stats from an e-commerce dataset:\n\n"
            f"- Avg Price: ₹{overview['avg_price']:.2f}\n"
            f"- Avg Rating: {overview['avg_rating']:.2f}\n"
            f"- Top Categories: {', '.join(top_cats)}\n\n"
            # f"Please write 3 insights or observations in bullet points."
            f"Perform an in-depth analysis of the dataset and produce the following in bullet point format:\n" \
            f"- At least five statistically significant insights or observations.\n" \
            f"- Each insight should be supported by quantitative evidence (e.g., p-values, confidence intervals, effect sizes, correlation coefficients).\n" \
            f"- Highlight any meaningful trends, anomalies, or patterns (temporal, categorical, or spatial).\n" \
            f"- Where applicable, identify causal relationships or leading indicators using appropriate methods (e.g., regression analysis, Granger causality, feature importance).\n" \
            f"- Include any business or operational implications of the insights.\n" \
            f"- Flag any limitations or assumptions made during the analysis.\n" \
            f"- Optionally, include suggested actions or next steps based on the findings."
        )),
    ]
    response = groq(messages=messages)  # Ask the AI chef for insights
    return response.content

# 5) Build Streamlit UI
# This is like setting up your kitchen counter so guests can see and interact with your food (data)
st.set_page_config(page_title="🧠 AI-Powered Product Insights", layout="wide")
st.title("📊 AI Product Review Explorer")

with st.spinner("Loading data from Supabase..."):
    df = load_data()  # Get your cleaned data ready

st.subheader("Sample Data")
st.dataframe(df.head(10), use_container_width=True)  # Show a sample of your data (like a tasting plate)

# Price histogram
st.subheader("Price Distribution")
fig1, ax1 = plt.subplots()
df["actual_price"].plot(kind="hist", bins=30, ax=ax1, color="skyblue")  # Like making a bar chart of prices
ax1.set_title("Actual Price Histogram")
ax1.set_xlabel("Price (₹)")
st.pyplot(fig1)

# Rating histogram
st.subheader("Rating Distribution")
fig2, ax2 = plt.subplots()
df["rating"].plot(kind="hist", bins=20, ax=ax2, color="lightgreen")  # Like making a bar chart of ratings
ax2.set_title("Rating Histogram")
ax2.set_xlabel("Rating (0–5)")
st.pyplot(fig2)

# Stats summary
avg_price = df["actual_price"].mean()  # Average price (like the average cost of all your ingredients)
avg_rating = df["rating"].mean()      # Average rating (like the average review for your dish)

# Top 3 categories by review count
exploded = df.assign(category=df["category"].str.split("|")).explode("category")  # Split categories apart (like sorting veggies into baskets)
top_categories = exploded["category"].value_counts().head(3).index.tolist()  # Find the 3 most common baskets

st.subheader("Quick Stats")
st.metric("Average Price", f"₹{avg_price:.2f}")
st.metric("Average Rating", f"{avg_rating:.2f}")
st.write("Top Categories:", ", ".join(top_categories))

# Ask Groq for insights
if st.button("🧠 Generate AI Insights"):
    with st.spinner("Thinking..."):
        insights = ask_ai({"avg_price": avg_price, "avg_rating": avg_rating}, top_categories)  # Ask the AI chef for tips
    st.markdown("### 🤖 AI Observations")
    st.markdown(insights)