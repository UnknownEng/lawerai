"""
Legal Corpus Loader and Chunking Engine
Loads statutory law documents, validates metadata, and builds searchable units.
"""

import os
import glob
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def load_corpus_documents(corpus_dir: str) -> List[Dict[str, Any]]:
    """
    Read all JSON files from the corpus directory and return validated statutory records.
    """
    documents: List[Dict[str, Any]] = []
    pattern = os.path.join(corpus_dir, "*.json")
    files = glob.glob(pattern)

    logger.info(f"Found {len(files)} corpus files in {corpus_dir}")

    for filepath in sorted(files):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        doc = sanitize_document(item, os.path.basename(filepath))
                        if doc:
                            documents.append(doc)
                elif isinstance(data, dict):
                    doc = sanitize_document(data, os.path.basename(filepath))
                    if doc:
                        documents.append(doc)
        except Exception as e:
            logger.error(f"Error loading file {filepath}: {e}")

    logger.info(f"Successfully loaded {len(documents)} statutory sections.")
    return documents


def sanitize_document(item: Dict[str, Any], source_file: str) -> Dict[str, Any]:
    """Validate and enrich statutory record with unified searchable text."""
    act_code = item.get("act_code", "GEN").upper()
    sec_num = str(item.get("section_number", ""))
    doc_id = item.get("id", f"{act_code}-{sec_num}").strip()

    title = item.get("section_title", "")
    act_title = item.get("act_title", "")
    chapter = item.get("chapter", "")
    plain_summary = item.get("summary_plain", "")
    urdu_summary = item.get("summary_urdu", "")
    statutory_text = item.get("statutory_text", "")
    category = item.get("category", "")
    jurisdiction = item.get("jurisdiction", "Federal")
    evidence = item.get("evidence_required", [])
    steps = item.get("practical_steps", [])
    forum = item.get("forum_court", "")

    # Build rich searchable composite text
    search_parts = [
        f"Act: {act_title} ({act_code})",
        f"Section: {sec_num} - {title}",
        f"Chapter: {chapter}",
        f"Category: {category}",
        f"Jurisdiction: {jurisdiction}",
        f"Plain Summary: {plain_summary}",
        f"Urdu Summary: {urdu_summary}",
        f"Court / Forum: {forum}",
        f"Statutory Text: {statutory_text}",
        f"Evidence Required: {' '.join(evidence) if isinstance(evidence, list) else str(evidence)}",
        f"Practical Steps: {' '.join(steps) if isinstance(steps, list) else str(steps)}"
    ]
    searchable_text = "\n".join(search_parts)

    return {
        "id": doc_id,
        "source_file": source_file,
        "act_code": act_code,
        "act_title": act_title,
        "section_number": sec_num,
        "section_title": title,
        "chapter": chapter,
        "jurisdiction": jurisdiction,
        "category": category,
        "cognizable": item.get("cognizable", "N/A"),
        "bailable": item.get("bailable", "N/A"),
        "compoundable": item.get("compoundable", "N/A"),
        "punishment": item.get("punishment", ""),
        "summary_plain": plain_summary,
        "summary_urdu": urdu_summary,
        "statutory_text": statutory_text,
        "evidence_required": evidence,
        "practical_steps": steps,
        "forum_court": forum,
        "searchable_text": searchable_text
    }
