import os
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def fetch_data():
    """Fetch all rows from product_reviews."""
    resp = supabase.table("product_reviews").select("*").execute()
    return pd.DataFrame(resp.data)

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure numeric columns are correct dtype."""
    df["actual_price"]        = df["actual_price"].astype(float)
    df["discounted_price"]    = df["discounted_price"].astype(float)
    df["discount_percentage"] = df["discount_percentage"].astype(float)
    df["rating"]              = df["rating"].astype(float)
    df["rating_count"]        = df["rating_count"].astype(int)
    return df

def compute_price_summary(df: pd.DataFrame) -> dict:
    """Return descriptive stats for actual prices."""
    return df["actual_price"].describe().to_dict()

def compute_rating_summary(df: pd.DataFrame) -> dict:
    """Return descriptive stats for ratings."""
    return df["rating"].describe().to_dict()

def top_categories(df: pd.DataFrame, n=5) -> pd.Series:
    """
    Count reviews per category.
    Note: categories are pipe-delimited; split and explode.
    """
    # Split pipe-delimited categories into rows
    exploded = df.assign(
        category=df["category"].str.split("|")
    ).explode("category")
    return exploded["category"].value_counts().head(n)

def plot_histogram(series: pd.Series, title: str, xlabel: str):
    """Helper: plot a simple histogram and save it."""
    # Create data_visualizations directory if it doesn't exist
    viz_dir = "data_visualizations"
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    
    plt.figure()
    series.plot(kind="hist", bins=30)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.tight_layout()
    
    # Save the plot (replace spaces with underscores for filename)
    filename = f"{viz_dir}/{title.lower().replace(' ', '_')}.png"
    plt.savefig(filename)
    plt.close()  # Close the figure to free memory
    print(f"Saved histogram to {filename}")

if __name__ == "__main__":
    # Fetch & clean
    df = fetch_data()
    df = clean_df(df)

    # Compute summaries
    price_stats  = compute_price_summary(df)
    rating_stats = compute_rating_summary(df)
    print("=== Actual Price Summary ===")
    for k,v in price_stats.items():
        print(f"{k}: {v}")
    print("\n=== Rating Summary ===")
    for k,v in rating_stats.items():
        print(f"{k}: {v}")

    # Top categories
    top_cats = top_categories(df)
    print("\n=== Top 5 Categories by Review Count ===")
    print(top_cats.to_string())

    # Plot distributions
    plot_histogram(df["actual_price"], "Actual Price Distribution", "Price (₹)")
    plot_histogram(df["rating"],       "Rating Distribution",       "Rating (0–5)")