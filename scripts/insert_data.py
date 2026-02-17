import pandas as pd
from app.database import get_collection

def insert_initial_data():

    sales_collection = get_collection("sales")

    df = pd.read_excel("amazon_sales_dataset_100k_india.xlsx")

    records = df.to_dict(orient="records")

    if records:
        sales_collection.insert_many(records)

    print("Data inserted successfully")


if __name__ == "__main__":
    insert_initial_data()
