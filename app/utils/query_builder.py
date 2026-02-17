def build_query(filters):
    query = {}

    if filters.date_range:
        query["Order_Date"] = {
            "$gte": filters.date_range[0],
            "$lte": filters.date_range[1]
        }

    if filters.state:
        query["State"] = {"$in": filters.state}

    if filters.category:
        query["Category"] = {"$in": filters.category}

    if filters.sku:
        query["SKU"] = {"$in": filters.sku}

    if filters.fulfillment:
        query["Fulfillment_Type"] = {"$in": filters.fulfillment}

    return query
