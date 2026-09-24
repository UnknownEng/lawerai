"""
Chat and Case Intake Router
Handles real-time legal consultation turns, RAG retrieval, OCR uploads, live Case Summary, and dossier export.
"""

import os
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db, ChatSession, Message, CaseSummary, UploadedDocument, EmergencyLog, User
from ..auth import get_current_user_optional
from ..config import settings
from ..rate_limiter import limiter
from ..storage_service import storage_service
from ..safety import detect_emergency, LEGAL_DISCLAIMER
from ..ocr_service import extract_text_from_file
from ..intake_tracker import update_case_state
from ..llm_service import LLMService
from ..reasoning_engine import LegalReasoningEngine
from ..export_service import generate_html_dossier
from ingestion.vector_store import LegalVectorStore

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat & Intake"])

# Singletons
vector_store = LegalVectorStore(storage_path=settings.VECTOR_STORE_PATH)
llm_service = LLMService()
reasoning_engine = LegalReasoningEngine()


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Legal Consultation"
    language: Optional[str] = "en"  # "en", "ur", "roman_ur"


class SendMessageRequest(BaseModel):
    content: str
    language: Optional[str] = "en"


@router.post("/sessions")
async def create_session(
    request: Request,
    req: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    # Check beta access gate if enabled
    if settings.REQUIRE_BETA_CODE and not user:
        beta_code = request.headers.get("x-beta-code", "").strip()
        expected = settings.BETA_ACCESS_CODE.strip()
        if beta_code.lower() != expected.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="A valid beta invitation code is required to start a consultation during closed beta."
            )

    session = ChatSession(
        user_id=user.id if user else None,
        title=req.title or "New Legal Consultation",

        language=req.language or "en",
        case_category="Initial Legal Intake"
    )
    db.add(session)
    await db.flush()

    # Create initial CaseSummary record
    summary = CaseSummary(
        session_id=session.id,
        issue_type="General Legal Inquiry",
        parties="Undisclosed",
        dates="Undisclosed",
        location_province="Federal / Unspecified",
        documents_mentioned=[],
        stage="intake_clarifying",
        applicable_laws=[],
        next_steps=[],
        evidence_checklist=[]
    )
    db.add(summary)

    # Initial Welcome message from assistant
    welcome_text = (
        "السلام علیکم / Greetings! I am Qanoon Sahayak (قانون معاون), your AI assistant for Pakistani law.\n\n"
        "Please describe the legal situation you are facing in your own words (English, اردو, or Roman Urdu). "
        "Like a lawyer during an initial consultation, I will review applicable Pakistani statutes (PPC, CrPC, CPC, Family Laws, etc.), "
        "outline evidence you will need, explain practical next steps, and ask clarifying questions one step at a time.\n\n"
        f"{LEGAL_DISCLAIMER}"
    )
    welcome_msg = Message(
        session_id=session.id,
        role="assistant",
        content=welcome_text,
        structured_data={"type": "welcome"}
    )
    db.add(welcome_msg)

    await db.commit()
    await db.refresh(session)

    return {
        "session_id": session.id,
        "title": session.title,
        "language": session.language,
        "created_at": session.created_at
    }


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """List sessions for the logged-in user or recent sessions."""
    stmt = select(ChatSession)
    if user:
        stmt = stmt.where(ChatSession.user_id == user.id)
    stmt = stmt.order_by(ChatSession.updated_at.desc()).limit(20)
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    return [
        {
            "id": s.id,
            "title": s.title,
            "language": s.language,
            "case_category": s.case_category,
            "updated_at": s.updated_at
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_session_detail(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.messages), selectinload(ChatSession.case_summary), selectinload(ChatSession.documents))
        .where(ChatSession.id == session_id)
    )
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Consultation session not found.")

    summary = session.case_summary
    return {
        "id": session.id,
        "title": session.title,
        "language": session.language,
        "case_category": session.case_category,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "citations": m.citations or [],
                "is_emergency": m.is_emergency,
                "created_at": m.created_at
            }
            for m in session.messages
        ],
        "case_summary": {
            "issue_type": summary.issue_type if summary else "Pending",
            "parties": summary.parties if summary else "Undisclosed",
            "dates": summary.dates if summary else "Undisclosed",
            "location_province": summary.location_province if summary else "Federal / Unspecified",
            "documents_mentioned": summary.documents_mentioned if summary else [],
            "stage": summary.stage if summary else "intake_clarifying",
            "applicable_laws": summary.applicable_laws if summary else [],
            "next_steps": summary.next_steps if summary else [],
            "evidence_checklist": summary.evidence_checklist if summary else []
        } if summary else {},
        "documents": [
            {"id": d.id, "file_name": d.file_name, "file_type": d.file_type, "created_at": d.created_at}
            for d in session.documents
        ]
    }


@router.post("/sessions/{session_id}/messages")
@limiter.limit("20/minute")
async def send_message(
    request: Request,
    session_id: str,
    req: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.messages), selectinload(ChatSession.case_summary), selectinload(ChatSession.documents))
        .where(ChatSession.id == session_id)
    )
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Consultation session not found.")

    user_text = req.content.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    # 1. Check for active emergency (Self-harm / Immediate Domestic Violence)
    is_emergency, emergency_reason, emergency_helplines = detect_emergency(user_text)

    # Save User message
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=user_text,
        is_emergency=is_emergency
    )
    db.add(user_msg)

    # If Emergency detected: immediately log & construct crisis response
    if is_emergency:
        log_entry = EmergencyLog(
            session_id=session.id,
            trigger_reason=emergency_reason,
            user_message=user_text
        )
        db.add(log_entry)

        helpline_lines = "\n".join([f"{i}. {h['name']}: {h['phone']} ({h.get('hours', '24/7')})" for i, h in enumerate(emergency_helplines, 1)])
        emergency_reply = (
            "Immediate Safety and Crisis Notice:\n\n"
            "Your safety and life are the most important priority right now. If you or someone with you is in immediate physical danger, "
            "please contact emergency services or trusted helplines without delay:\n\n"
            f"{helpline_lines}\n\n"
            "If police intervention is required immediately, please call 15. For female survivors of domestic abuse, call 1043 in Punjab or 1098 in Sindh and nationally.\n\n"
            "Once you are in a safe and secure location, we can examine legal remedies such as urgent Protection Orders, "
            "filing a complaint under Section 154 of the Code of Criminal Procedure, or other legal protection."
        )

        asst_msg = Message(
            session_id=session.id,
            role="assistant",
            content=emergency_reply,
            is_emergency=True,
            citations=[]
        )
        db.add(asst_msg)
        await db.commit()

        return {
            "user_message": {"id": user_msg.id, "role": "user", "content": user_msg.content},
            "assistant_message": {"id": asst_msg.id, "role": "assistant", "content": asst_msg.content, "is_emergency": True, "citations": []},
            "is_emergency": True,
            "emergency_helplines": emergency_helplines
        }

    # Step 2 & 3 & 4: Multi-Issue Reasoning, Fact Extraction, and Role-Aware Retrieval
    reasoning = reasoning_engine.analyze(user_text)

    analyzed_issues_data = []
    all_retrieved_sections = []
    seen_section_ids = set()

    for issue in reasoning.issues:
        issue_sections = []
        if issue.statute_hints:
            raw_sections = vector_store.search_hybrid(issue.search_query, top_k=5, min_score=0.35)
            # Maintain strict priority order of statute_hints
            for hint_id in issue.statute_hints:
                match = next((s for s in raw_sections if s.get("id") == hint_id), None)
                if not match:
                    match = vector_store.get_section_by_id(hint_id, query=user_text)
                if match and match.get("id") not in [s.get("id") for s in issue_sections]:
                    issue_sections.append(match)
        elif issue.jurisdiction_hint in ["Provincial (Khyber Pakhtunkhwa)", "Provincial (Balochistan)"]:
            issue_sections = []
        elif not issue.statute_hints and issue.issue_title != "General Inquiry":
            issue_sections = []
        elif not issue.statute_hints and issue.issue_title == "General Inquiry":
            issue_sections = vector_store.search_hybrid(issue.search_query, top_k=2, min_score=0.45)
        else:
            issue_sections = vector_store.search_hybrid(issue.search_query, top_k=2, min_score=0.45)

        # Enforce factual relevance gate on issue_sections
        issue_sections = [
            s for s in issue_sections
            if vector_store.verify_factual_relevance(s, user_text)
        ]

        confidence_passed = len(issue_sections) > 0

        analyzed_issues_data.append({
            "issue_index": issue.issue_index,
            "issue_title": issue.issue_title,
            "raw_text": issue.raw_text,
            "subject_matter": issue.subject_matter,
            "parties": issue.parties,
            "aggrieved_party": issue.aggrieved_party,
            "wrongdoer": issue.wrongdoer,
            "action_taken": issue.action_taken,
            "relief_sought": issue.relief_sought,
            "search_query": issue.search_query,
            "retrieved_sections": issue_sections,
            "confidence_passed": confidence_passed
        })

        for sec in issue_sections:
            if sec.get("id") not in seen_section_ids:
                seen_section_ids.add(sec.get("id"))
                all_retrieved_sections.append(sec)

    # If no reasoning issues were formed (fallback)
    if not reasoning.issues:
        all_retrieved_sections = vector_store.search_hybrid(user_text, top_k=3, min_score=0.45)

    # Final corpus-wide factual relevance gate: discard any citation lacking factual justification in user text
    all_retrieved_sections = [
        s for s in all_retrieved_sections
        if vector_store.verify_factual_relevance(s, user_text)
    ]

    # Build chat history for LLM
    history = []
    for m in session.messages[-8:]:
        history.append({"role": m.role, "content": m.content})

    # Step 5: Update structured Case Summary state
    current_summary_dict = {}
    if session.case_summary:
        current_summary_dict = {
            "issue_type": session.case_summary.issue_type,
            "parties": session.case_summary.parties,
            "dates": session.case_summary.dates,
            "location_province": session.case_summary.location_province,
            "documents_mentioned": session.case_summary.documents_mentioned,
            "stage": session.case_summary.stage,
            "applicable_laws": session.case_summary.applicable_laws,
            "next_steps": session.case_summary.next_steps,
            "evidence_checklist": session.case_summary.evidence_checklist
        }

    updated_state = update_case_state(
        current_state=current_summary_dict,
        user_message=user_text,
        retrieved_sections=all_retrieved_sections
    )

    has_specific_issues = len(reasoning.issues) > 1 or (len(reasoning.issues) == 1 and reasoning.issues[0].issue_title != "General Inquiry")
    if len(reasoning.issues) > 1:
        updated_state["issue_type"] = " & ".join([iss.issue_title for iss in reasoning.issues])
        updated_state["parties"] = "; ".join([iss.parties for iss in reasoning.issues])
    elif len(reasoning.issues) == 1 and reasoning.issues[0].issue_title != "General Inquiry":
        updated_state["issue_type"] = reasoning.issues[0].issue_title
        updated_state["parties"] = reasoning.issues[0].parties

    if has_specific_issues:
        current_laws = []
        for sec in all_retrieved_sections:
            current_laws.append({
                "id": sec["id"],
                "act_code": sec.get("act_code"),
                "act_title": sec.get("act_title"),
                "section_number": sec.get("section_number"),
                "section_title": sec.get("section_title"),
                "category": sec.get("category"),
                "forum_court": sec.get("forum_court"),
                "summary_plain": sec.get("summary_plain"),
                "punishment": sec.get("punishment")
            })
        updated_state["applicable_laws"] = current_laws

    # Step 6: Generate LLM response strictly grounded in retrieved sections
    llm_result = await llm_service.generate_legal_response(
        user_query=user_text,
        chat_history=history,
        retrieved_sections=all_retrieved_sections,
        case_state=updated_state,
        language=req.language or session.language,
        analyzed_issues=analyzed_issues_data
    )

    # Save Assistant message
    asst_msg = Message(
        session_id=session.id,
        role="assistant",
        content=llm_result["content"],
        citations=llm_result["citations"],
        is_emergency=False
    )
    db.add(asst_msg)

    # Update CaseSummary in DB
    if not session.case_summary:
        summary_obj = CaseSummary(session_id=session.id)
        db.add(summary_obj)
    else:
        summary_obj = session.case_summary

    summary_obj.issue_type = updated_state.get("issue_type", summary_obj.issue_type)
    summary_obj.parties = updated_state.get("parties", summary_obj.parties)
    summary_obj.dates = updated_state.get("dates", summary_obj.dates)
    summary_obj.location_province = updated_state.get("location_province", summary_obj.location_province)
    summary_obj.documents_mentioned = updated_state.get("documents_mentioned", summary_obj.documents_mentioned)
    summary_obj.stage = updated_state.get("stage", summary_obj.stage)
    summary_obj.applicable_laws = updated_state.get("applicable_laws", summary_obj.applicable_laws)
    summary_obj.next_steps = updated_state.get("next_steps", summary_obj.next_steps)
    summary_obj.evidence_checklist = updated_state.get("evidence_checklist", summary_obj.evidence_checklist)

    # Also update session title if initial title
    if session.title == "New Legal Consultation" and updated_state.get("issue_type"):
        session.title = updated_state.get("issue_type")[:50]
        session.case_category = updated_state.get("issue_type")[:100]

    await db.commit()

    return {
        "user_message": {"id": user_msg.id, "role": "user", "content": user_msg.content},
        "assistant_message": {
            "id": asst_msg.id,
            "role": "assistant",
            "content": asst_msg.content,
            "citations": asst_msg.citations,
            "is_emergency": False,
            "provider_used": llm_result.get("provider_used")
        },
        "case_summary": updated_state,
        "is_emergency": False
    }


@router.post("/sessions/{session_id}/upload")
@limiter.limit("10/minute")
async def upload_document(
    request: Request,
    session_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.documents), selectinload(ChatSession.case_summary))
        .where(ChatSession.id == session_id)
    )
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Consultation session not found.")

    content = await file.read()
    orig_name = file.filename or "uploaded_doc"
    content_type = file.content_type or "application/octet-stream"

    # Save via storage service (supports local and S3/R2)
    storage_key, ref_path = storage_service.save_file(content, orig_name, content_type)

    # For OCR extraction: extract text from local path or temporary file
    temp_path = None
    if os.path.exists(ref_path):
        ocr_path = ref_path
    else:
        import tempfile
        ext = os.path.splitext(orig_name)[1].lower()
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content)
            temp_path = tmp.name
        ocr_path = temp_path

    try:
        extracted = extract_text_from_file(ocr_path, content_type)
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

    doc_record = UploadedDocument(
        session_id=session.id,
        file_name=orig_name,
        file_type=content_type,
        file_path=storage_key,
        extracted_text=extracted
    )
    db.add(doc_record)

    # Add as system/user document note in messages
    summary_snippet = extracted[:300] + ("..." if len(extracted) > 300 else "")
    doc_msg = Message(
        session_id=session.id,
        role="user",
        content=f"📎 [Uploaded Document: {orig_name}]\n```\n{summary_snippet}\n```\nPlease analyze this document in relation to my case."
    )
    db.add(doc_msg)

    # Update mentioned documents in CaseSummary
    if session.case_summary:
        current_docs = list(session.case_summary.documents_mentioned or [])
        if orig_name not in current_docs:
            current_docs.append(f"{orig_name} (Uploaded & Verified)")
            session.case_summary.documents_mentioned = current_docs

    await db.commit()

    return {
        "id": doc_record.id,
        "file_name": doc_record.file_name,
        "extracted_text_preview": summary_snippet
    }


@router.get("/sessions/{session_id}/documents/{doc_id}/download")
async def download_document(
    session_id: str,
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    stmt = select(UploadedDocument).where(
        UploadedDocument.id == doc_id,
        UploadedDocument.session_id == session_id
    )
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    url = storage_service.generate_download_url(doc.file_path, doc.file_name)
    if url:
        return RedirectResponse(url=url)

    # Local storage fallback
    local_path = doc.file_path if os.path.isabs(doc.file_path) else os.path.join(settings.UPLOAD_DIR, doc.file_path)
    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Document file not found on storage.")

    return FileResponse(path=local_path, filename=doc.file_name, media_type=doc.file_type)


@router.get("/sessions/{session_id}/export/html")
async def export_dossier_html(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.messages), selectinload(ChatSession.case_summary))
        .where(ChatSession.id == session_id)
    )
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Consultation session not found.")

    case_state = {
        "issue_type": session.case_summary.issue_type if session.case_summary else session.title,
        "parties": session.case_summary.parties if session.case_summary else "Undisclosed",
        "dates": session.case_summary.dates if session.case_summary else "Undisclosed",
        "location_province": session.case_summary.location_province if session.case_summary else "Federal",
        "applicable_laws": session.case_summary.applicable_laws if session.case_summary else [],
        "evidence_checklist": session.case_summary.evidence_checklist if session.case_summary else [],
        "next_steps": session.case_summary.next_steps if session.case_summary else []
    }
    messages_data = [{"role": m.role, "content": m.content} for m in session.messages]

    html_content = generate_html_dossier(session.title, case_state, messages_data)
    return HTMLResponse(content=html_content)


@router.get("/sessions/{session_id}/export/json")
async def export_dossier_json(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.messages), selectinload(ChatSession.case_summary))
        .where(ChatSession.id == session_id)
    )
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Consultation session not found.")

    return {
        "dossier_id": session.id,
        "title": session.title,
        "case_category": session.case_category,
        "summary": {
            "issue_type": session.case_summary.issue_type if session.case_summary else "Pending",
            "parties": session.case_summary.parties if session.case_summary else "Undisclosed",
            "dates": session.case_summary.dates if session.case_summary else "Undisclosed",
            "location_province": session.case_summary.location_province if session.case_summary else "Federal",
            "documents_mentioned": session.case_summary.documents_mentioned if session.case_summary else [],
            "applicable_laws": session.case_summary.applicable_laws if session.case_summary else [],
            "next_steps": session.case_summary.next_steps if session.case_summary else [],
            "evidence_checklist": session.case_summary.evidence_checklist if session.case_summary else []
        },
        "transcript": [{"role": m.role, "content": m.content, "created_at": str(m.created_at)} for m in session.messages],
        "disclaimer": LEGAL_DISCLAIMER
    }
