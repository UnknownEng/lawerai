"""
Emergency Helpline and Crisis Resource Router
"""

import os
import json
import logging
from typing import List
from fastapi import APIRouter
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/emergency", tags=["Emergency Resources"])


def load_emergency_data() -> List[dict]:
    path = os.path.join(settings.DATA_DIR, "emergency_resources.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading emergency resources: {e}")
    return []


@router.get("/resources")
async def get_emergency_resources():
    resources = load_emergency_data()
    return {
        "status": "active",
        "emergency_disclaimer": "If in immediate life danger, call Police 15 or Rescue 1122 right away.",
        "resources": resources
    }
