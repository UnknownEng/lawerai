"""
Feedback Router for Closed Lawyer Beta
Collects structured feedback on chatbot responses:
- "citation wrong"
- "reasoning wrong"
- "looks fine"
- optional lawyer notes / comments
Saves encrypted feedback to database for audit and review.
"""

import logging
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from ..database import get_db, Feedback, User
from ..auth import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/feedback", tags=["Feedback & Beta Audit"])


class SubmitFeedbackRequest(BaseModel):
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    feedback_type: str = Field(..., description="citation_wrong, reasoning_wrong, looks_fine, thumbs_up, thumbs_down")
    category: Optional[str] = "general"
    comment: Optional[str] = None
    query_excerpt: Optional[str] = None
    citations_flagged: Optional[List[Any]] = Field(default_factory=list)


@router.post("")
async def submit_feedback(
    req: SubmitFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """Save feedback from lawyer/tester on assistant answer."""
    feedback = Feedback(
        user_id=user.id if user else None,
        session_id=req.session_id,
        message_id=req.message_id,
        feedback_type=req.feedback_type,
        category=req.category or "general",
        comment=req.comment or "",
        query_excerpt=req.query_excerpt or "",
        citations_flagged=req.citations_flagged or []
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    logger.info(f"Feedback received: type={feedback.feedback_type}, category={feedback.category}, id={feedback.id}")
    return {
        "status": "success",
        "feedback_id": feedback.id,
        "message": "Thank you! Your feedback has been recorded for legal review."
    }


@router.get("/summary")
async def get_feedback_summary(
    db: AsyncSession = Depends(get_db)
):
    """Returns aggregated feedback stats for legal review."""
    stmt = (
        select(Feedback.feedback_type, func.count(Feedback.id))
        .group_by(Feedback.feedback_type)
    )
    res = await db.execute(stmt)
    type_counts = {row[0]: row[1] for row in res.all()}

    # Recent entries
    recent_stmt = (
        select(Feedback)
        .order_by(desc(Feedback.created_at))
        .limit(20)
    )
    recent_res = await db.execute(recent_stmt)
    recent_feedbacks = [
        {
            "id": f.id,
            "session_id": f.session_id,
            "feedback_type": f.feedback_type,
            "category": f.category,
            "comment": f.comment,
            "query_excerpt": f.query_excerpt,
            "citations_flagged": f.citations_flagged,
            "created_at": f.created_at
        }
        for f in recent_res.scalars().all()
    ]

    return {
        "total_feedbacks": sum(type_counts.values()),
        "breakdown": type_counts,
        "by_type": type_counts,
        "recent_entries": recent_feedbacks
    }
