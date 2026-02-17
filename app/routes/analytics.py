from fastapi import APIRouter
from app.schemas import FilterPayload
from app.utils.query_builder import build_query
from app.services.kpi_service import compute_kpis
from app.services.sales_service import revenue_trend

router = APIRouter()

@router.post("/analytics")
def analytics_dashboard(filters: FilterPayload):

    query = build_query(filters)

    kpis = compute_kpis(query)
    revenue_chart = revenue_trend(query)

    response = {
        "kpis": {
            "total_revenue": kpis.get("total_revenue", 0),
            "total_orders": kpis.get("total_orders", 0),
            "units_sold": kpis.get("units_sold", 0),
            "total_profit": kpis.get("total_profit", 0)
        },
        "charts": {
            "revenue_trend": revenue_chart
        }
    }

    return response
