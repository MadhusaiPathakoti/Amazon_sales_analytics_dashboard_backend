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

                # ---------------- KPI CORE ----------------
                "kpis": [
                    {
                        "$group": {
                            "_id": None,
                            "total_revenue": {"$sum": "$Revenue"},
                            "total_orders": {"$sum": 1},
                            "units_sold": {"$sum": "$Units_Sold"},
                            "total_profit": {"$sum": "$Profit"},
                            "total_discount": {"$sum": "$Discount"}
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
                    {"$sort": {"revenue": -1}},
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

                # ---------------- Customer Orders ----------------
                "customer_orders": [
                    {
                        "$group": {
                            "_id": "$Customer_ID",
                            "orders": {"$sum": 1},
                            "revenue": {"$sum": "$Revenue"}
                        }
                    }
                ],

                # ---------------- Profit by Category ----------------
                "profit_by_category": [
                    {
                        "$group": {
                            "_id": "$Category",
                            "profit": {"$sum": "$Profit"},
                            "revenue": {"$sum": "$Revenue"}
                        }
                    }
                ],

                # ---------------- Fulfillment ----------------
                "fulfillment": [
                    {
                        "$group": {
                            "_id": "$Fulfillment_Type",
                            "orders": {"$sum": 1},
                            "profit": {"$sum": "$Profit"}
                        }
                    }
                ],

                # ---------------- Monthly Revenue ----------------
                "monthly_revenue": [
                    {
                        "$group": {
                            "_id": {"$substr": ["$Order_Date", 0, 7]},
                            "revenue": {"$sum": "$Revenue"}
                        }
                    },
                    {"$sort": {"_id": 1}}
                ]
            }
        }
    ]

    result = list(sales.aggregate(pipeline))[0]

    # ---------------- DERIVED BUSINESS METRICS ----------------

    kpis = result["kpis"][0] if result["kpis"] else {}

    total_revenue = kpis.get("total_revenue", 0)
    total_profit = kpis.get("total_profit", 0)
    total_discount = kpis.get("total_discount", 0)
    total_orders = kpis.get("total_orders", 0)

    # Profit margin %
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

    # Discount impact %
    discount_impact = (total_discount / total_revenue * 100) if total_revenue else 0

    # Customer analytics
    customers = result["customer_orders"]
    total_customers = len(customers)
    repeat_customers = len([c for c in customers if c["orders"] > 1])
    repeat_customer_pct = (repeat_customers / total_customers * 100) if total_customers else 0

    # CLV approximation
    avg_revenue_per_customer = (total_revenue / total_customers) if total_customers else 0

    # SKU concentration
    top_sku_revenue = sum([sku["revenue"] for sku in result["top_skus"]])
    sku_concentration = (top_sku_revenue / total_revenue * 100) if total_revenue else 0

    # ---------------- FINAL RESPONSE ----------------

    return {
        "kpis": kpis,

        "business_metrics": {
            "profit_margin_pct": profit_margin,
            "discount_impact_pct": discount_impact,
            "repeat_customer_pct": repeat_customer_pct,
            "avg_customer_value": avg_revenue_per_customer,
            "sku_concentration_pct": sku_concentration
        },

        "revenue_trend": result["revenue_trend"],
        "category_share": result["category_share"],
        "top_skus": result["top_skus"],
        "state_heatmap": result["state_heatmap"],
        "profit_by_category": result["profit_by_category"],
        "fulfillment_analytics": result["fulfillment"],
        "monthly_revenue": result["monthly_revenue"]
    }
