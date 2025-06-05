# class1_ingest.py
import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from postgrest.exceptions import APIError

load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

def ingest_csv(csv_path: str):
    df = pd.read_csv(csv_path)

    # Clean & cast price columns
    for col in ("discounted_price", "actual_price"):
        df[col] = (
            df[col]
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )

    # Clean & cast discount percentage
    df["discount_percentage"] = (
        df["discount_percentage"]
        .str.replace("%", "", regex=False)
        .astype(float)
    )

    # Clean rating: keep only digits and dot, then to float
    df["rating"] = (
        df["rating"]
        .astype(str)
        .str.replace(r"[^0-9\.]", "", regex=True)
    )
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)

    # Clean rating_count: remove commas, coerce to numeric, fill NaN, then int
    df["rating_count"] = (
        pd.to_numeric(
            df["rating_count"].str.replace(",", "", regex=False),
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    records = df.to_dict(orient="records")
    for i in range(0, len(records), 50):
        chunk = records[i : i + 50]
        try:
            supabase.table("product_reviews") \
                     .upsert(chunk, on_conflict="product_id") \
                     .execute()
            print(f"✅ Upserted rows {i}–{i+len(chunk)-1}")
        except APIError as e:
            print(f"❌ Failed batch {i}–{i+len(chunk)-1}: {e}")

if __name__ == "__main__":
    ingest_csv("data/amazon.csv")