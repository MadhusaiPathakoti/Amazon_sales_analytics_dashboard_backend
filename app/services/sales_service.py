from app.database import get_collection

sales_collection = get_collection("sales")

def revenue_trend(query):

    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$Order_Date",
                "revenue": {"$sum": "$Revenue"}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    data = list(sales_collection.aggregate(pipeline))

    return [
        {"date": d["_id"], "revenue": d["revenue"]}
        for d in data
    ]
