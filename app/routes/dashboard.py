from fastapi import APIRouter
from app.schemas import FilterPayload
from app.utils.query_builder import build_query
from app.database import get_collection

router = APIRouter()
sales = get_collection("sales")


@router.post("/analytics/dashboard")
def analytics_dashboard(filters: FilterPayload):

    query = build_query(filters)

    # ---------------- KPI ----------------
    kpi_pipeline = [
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
    kpis = list(sales.aggregate(kpi_pipeline))
    kpis = kpis[0] if kpis else {}

    # ---------------- Revenue Trend ----------------
    revenue_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$Order_Date",
                "revenue": {"$sum": "$Revenue"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    revenue_trend = list(sales.aggregate(revenue_pipeline))

    # ---------------- Category Share ----------------
    category_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$Category",
                "revenue": {"$sum": "$Revenue"}
            }
        }
    ]
    category_share = list(sales.aggregate(category_pipeline))

    # ---------------- Top SKUs ----------------
    sku_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$SKU",
                "units_sold": {"$sum": "$Units_Sold"},
                "revenue": {"$sum": "$Revenue"}
            }
        },
        {"$sort": {"units_sold": -1}},
        {"$limit": 10}
    ]
    top_skus = list(sales.aggregate(sku_pipeline))

    # ---------------- State Heatmap ----------------
    state_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$State",
                "revenue": {"$sum": "$Revenue"}
            }
        }
    ]
    state_heatmap = list(sales.aggregate(state_pipeline))

    # ---------------- Customer Analytics ----------------
    customer_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$Customer_ID",
                "orders": {"$sum": 1},
                "revenue": {"$sum": "$Revenue"}
            }
        }
    ]
    customer_data = list(sales.aggregate(customer_pipeline))

    repeat_customers = len([c for c in customer_data if c["orders"] > 1])
    total_customers = len(customer_data)

    customer_analytics = {
        "total_customers": total_customers,
        "repeat_customers": repeat_customers
    }

    # ---------------- Profit Analytics ----------------
    profit_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$Category",
                "profit": {"$sum": "$Profit"},
                "revenue": {"$sum": "$Revenue"}
            }
        }
    ]
    profit_analytics = list(sales.aggregate(profit_pipeline))

    # ---------------- Fulfillment Analytics ----------------
    fulfillment_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$Fulfillment_Type",
                "orders": {"$sum": 1},
                "profit": {"$sum": "$Profit"}
            }
        }
    ]
    fulfillment_analytics = list(sales.aggregate(fulfillment_pipeline))

    # ---------------- FINAL RESPONSE ----------------

    return {
        "kpis": kpis,
        "revenue_trend": revenue_trend,
        "category_share": category_share,
        "top_skus": top_skus,
        "state_heatmap": state_heatmap,
        "customer_analytics": customer_analytics,
        "profit_analytics": profit_analytics,
        "fulfillment_analytics": fulfillment_analytics
    }
