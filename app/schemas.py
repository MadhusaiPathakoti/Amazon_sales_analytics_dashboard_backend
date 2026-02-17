from pydantic import BaseModel
from typing import List, Optional

class FilterPayload(BaseModel):
    date_range: Optional[List[str]] = None
    state: Optional[List[str]] = None
    category: Optional[List[str]] = None
    sku: Optional[List[str]] = None
    fulfillment: Optional[List[str]] = None
