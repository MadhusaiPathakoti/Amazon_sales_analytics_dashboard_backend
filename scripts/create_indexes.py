from app.database import get_collection

def create_indexes():
    sales = get_collection("sales")

    sales.create_index("Order_Date")
    sales.create_index("State")
    sales.create_index("Category")
    sales.create_index("SKU")
    sales.create_index("Fulfillment_Type")

    print("Indexes created")


if __name__ == "__main__":
    create_indexes()
