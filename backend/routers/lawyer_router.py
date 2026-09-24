"""
Lawyer and Legal Aid Directory Router
Provides directory lookup of Pakistani legal aid clinics, bar councils, and advocates.
"""

import os
import json
import logging
from typing import Optional, List
from fastapi import APIRouter, Query
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/lawyers", tags=["Lawyer Directory"])


def load_lawyer_data() -> List[dict]:
    path = os.path.join(settings.DATA_DIR, "lawyer_directory.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading lawyer directory: {e}")
    return []


@router.get("")
async def get_lawyers(
    city: Optional[str] = Query(None, description="Filter by city (e.g. Lahore, Karachi, Islamabad)"),
    province: Optional[str] = Query(None, description="Filter by province (e.g. Punjab, Sindh, ICT)"),
    specialty: Optional[str] = Query(None, description="Filter by legal specialty"),
    free_aid_only: Optional[bool] = Query(None, description="Filter for free legal aid only"),
    search: Optional[str] = Query(None, description="Search term")
):
    all_lawyers = load_lawyer_data()
    filtered = all_lawyers

    if city:
        city_lower = city.lower()
        filtered = [l for l in filtered if city_lower in l.get("city", "").lower()]

    if province:
        prov_lower = province.lower()
        filtered = [l for l in filtered if prov_lower in l.get("province", "").lower()]

    if specialty:
        spec_lower = specialty.lower()
        filtered = [
            l for l in filtered
            if any(spec_lower in s.lower() for s in l.get("specialties", []))
            or spec_lower in l.get("category", "").lower()
        ]

    if free_aid_only is True:
        filtered = [l for l in filtered if l.get("is_free_legal_aid") is True]

    if search:
        s_lower = search.lower()
        filtered = [
            l for l in filtered
            if s_lower in l.get("name", "").lower()
            or s_lower in l.get("description", "").lower()
            or any(s_lower in s.lower() for s in l.get("specialties", []))
        ]

    return {
        "count": len(filtered),
        "results": filtered
    }
