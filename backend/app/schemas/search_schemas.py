from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SearchResultItem(BaseModel):
    record_id: str
    record_type: str  # service, alert, incident, scenario, plan, validation, benchmark
    title: str
    subtitle: str
    source_module: str
    status: Optional[str] = None
    severity: Optional[str] = None
    created_at: Optional[datetime] = None
    url_path: str

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem] = Field(default_factory=list)

class SearchSuggestionsResponse(BaseModel):
    suggestions: List[str] = Field(default_factory=list)
