# class3_app.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# 1) Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2) Initialize Supabase and Groq clients
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
groq = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")  # or llama3-70b if preferred

# 3) Fetch and clean Supabase data
@st.cache_data(show_spinner=False)
def load_data():
    res = supabase.table("product_reviews").select("*").execute()
    df = pd.DataFrame(res.data)
    # Clean numeric types
    df["actual_price"]        = df["actual_price"].astype(float)
    df["discounted_price"]    = df["discounted_price"].astype(float)
    df["discount_percentage"] = df["discount_percentage"].astype(float)
    df["rating"]              = df["rating"].astype(float)
    df["rating_count"]        = df["rating_count"].astype(int)
    return df

# 4) Generate LLM insights
def ask_ai(overview: dict, top_cats: list):
    messages = [
        SystemMessage(content="You are a data analyst expert in e-commerce sales."),
        HumanMessage(content=(
            f"Here are key product stats from an e-commerce dataset:\n\n"
            f"- Avg Price: ₹{overview['avg_price']:.2f}\n"
            f"- Avg Rating: {overview['avg_rating']:.2f}\n"
            f"- Top Categories: {', '.join(top_cats)}\n\n"
            f"Please write 3 insights or observations in bullet points."
        )),
    ]
    response = groq(messages=messages)
    return response.content

# 5) Build Streamlit UI
st.set_page_config(page_title="🧠 AI-Powered Product Insights", layout="wide")
st.title("📊 AI Product Review Explorer")

with st.spinner("Loading data from Supabase..."):
    df = load_data()

st.subheader("Sample Data")
st.dataframe(df.head(10), use_container_width=True)

# Price histogram
st.subheader("Price Distribution")
fig1, ax1 = plt.subplots()
df["actual_price"].plot(kind="hist", bins=30, ax=ax1, color="skyblue")
ax1.set_title("Actual Price Histogram")
ax1.set_xlabel("Price (₹)")
st.pyplot(fig1)

# Rating histogram
st.subheader("Rating Distribution")
fig2, ax2 = plt.subplots()
df["rating"].plot(kind="hist", bins=20, ax=ax2, color="lightgreen")
ax2.set_title("Rating Histogram")
ax2.set_xlabel("Rating (0–5)")
st.pyplot(fig2)

# Stats summary
avg_price = df["actual_price"].mean()
avg_rating = df["rating"].mean()

# Top 3 categories by review count
exploded = df.assign(category=df["category"].str.split("|")).explode("category")
top_categories = exploded["category"].value_counts().head(3).index.tolist()

st.subheader("Quick Stats")
st.metric("Average Price", f"₹{avg_price:.2f}")
st.metric("Average Rating", f"{avg_rating:.2f}")
st.write("Top Categories:", ", ".join(top_categories))

# Ask Groq for insights
if st.button("🧠 Generate AI Insights"):
    with st.spinner("Thinking..."):
        insights = ask_ai({"avg_price": avg_price, "avg_rating": avg_rating}, top_categories)
    st.markdown("### 🤖 AI Observations")
    st.markdown(insights)