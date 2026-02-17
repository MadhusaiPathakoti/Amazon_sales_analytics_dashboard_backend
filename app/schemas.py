from pydantic import BaseModel
from typing import List, Optional

class FilterPayload(BaseModel):
    date_range: Optional[List[str]]
    state: Optional[List[str]]
    category: Optional[List[str]]
    sku: Optional[List[str]]
    fulfillment: Optional[List[str]]
