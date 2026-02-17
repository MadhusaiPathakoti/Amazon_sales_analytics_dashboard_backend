from app.database import get_collection

sales_collection = get_collection("sales")

def compute_kpis(query):

    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": None,
                "total_revenue": {"$sum": "$Revenue"},
                "total_orders": {"$sum": 1},
                "units_sold": {"$sum": "$Units_Sold"},
                "total_profit": {"$sum": "$Profit"}
            }
        }
    ]

    result = list(sales_collection.aggregate(pipeline))

    return result[0] if result else {}
