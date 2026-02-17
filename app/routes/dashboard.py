from fastapi import APIRouter
from app.schemas import FilterPayload
from app.utils.query_builder import build_query
from app.database import get_collection

router = APIRouter()
sales = get_collection("sales")


@router.post("/analytics/dashboard")
def analytics_dashboard(filters: FilterPayload):

    query = build_query(filters)

    pipeline = [

        {"$match": query},

        {
            "$facet": {

                # ---------------- KPI ----------------
                "kpis": [
                    {
                        "$group": {
                            "_id": None,
                            "total_revenue": {"$sum": "$Revenue"},
                            "total_orders": {"$sum": 1},
                            "units_sold": {"$sum": "$Units_Sold"},
                            "total_profit": {"$sum": "$Profit"}
                        }
                    }
                ],

                # ---------------- Revenue Trend ----------------
                "revenue_trend": [
                    {
                        "$group": {
                            "_id": "$Order_Date",
                            "revenue": {"$sum": "$Revenue"}
                        }
                    },
                    {"$sort": {"_id": 1}}
                ],

                # ---------------- Category Share ----------------
                "category_share": [
                    {
                        "$group": {
                            "_id": "$Category",
                            "revenue": {"$sum": "$Revenue"}
                        }
                    }
                ],

                # ---------------- Top SKUs ----------------
                "top_skus": [
                    {
                        "$group": {
                            "_id": "$SKU",
                            "units_sold": {"$sum": "$Units_Sold"},
                            "revenue": {"$sum": "$Revenue"}
                        }
                    },
                    {"$sort": {"units_sold": -1}},
                    {"$limit": 10}
                ],

                # ---------------- State Heatmap ----------------
                "state_heatmap": [
                    {
                        "$group": {
                            "_id": "$State",
                            "revenue": {"$sum": "$Revenue"}
                        }
                    }
                ],

                # ---------------- Customer Analytics ----------------
                "customer_analytics": [
                    {
                        "$group": {
                            "_id": "$Customer_ID",
                            "orders": {"$sum": 1},
                            "revenue": {"$sum": "$Revenue"}
                        }
                    }
                ],

                # ---------------- Profit Analytics ----------------
                "profit_analytics": [
                    {
                        "$group": {
                            "_id": "$Category",
                            "profit": {"$sum": "$Profit"},
                            "revenue": {"$sum": "$Revenue"}
                        }
                    }
                ],

                # ---------------- Fulfillment Analytics ----------------
                "fulfillment_analytics": [
                    {
                        "$group": {
                            "_id": "$Fulfillment_Type",
                            "orders": {"$sum": 1},
                            "profit": {"$sum": "$Profit"}
                        }
                    }
                ]

            }
        }
    ]

    result = list(sales.aggregate(pipeline))[0]

    # Post-processing KPI
    kpis = result["kpis"][0] if result["kpis"] else {}

    return {
        "kpis": kpis,
        "revenue_trend": result["revenue_trend"],
        "category_share": result["category_share"],
        "top_skus": result["top_skus"],
        "state_heatmap": result["state_heatmap"],
        "customer_analytics": result["customer_analytics"],
        "profit_analytics": result["profit_analytics"],
        "fulfillment_analytics": result["fulfillment_analytics"]
    }
