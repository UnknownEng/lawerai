"""
Multi-Provider LLM Integration Service with RAG Grounding and Local Legal Engine
Configurable via environment variables (Gemini, Claude, GPT, or offline Local Engine).
Enforces strictly plain-text outputs with no emojis, no markdown bold, and no headers.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from .config import settings
from .safety import apply_guardrails, LEGAL_DISCLAIMER

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are "Qanoon Sahayak" (قانون معاون) — a friendly, knowledgeable legal guide specialized in Pakistani law.
Your role is to explain things the way you would explain them to a friend who has never dealt with courts or legal matters before.

IMPORTANT RULES & GUIDELINES:
1. PLAIN, EVERYDAY LANGUAGE (NO UNNECESSARY JARGON):
   - Explain everything simply and clearly so someone with no legal or English education can understand what happened and what to do next.
   - Strictly avoid confusing legalese such as: "jurisdiction", "decree", "ad-interim restraining order", "prima facie case", "balance of convenience", "istighasa", "rendition of accounts", "estoppel", or "res judicata".
   - When a common legal term must be used (like "FIR" or "khula"), briefly explain it in plain everyday words the first time it is used (for example: "an FIR (an official police report)", "khula (when a wife requests a divorce through the family court)").
   - Keep court and forum names simple (for example: "the local magistrate's court", "the family court", "the local rent office", "the civil court").
2. DIRECTLY ANSWER PROCEDURAL QUESTIONS:
   - If the user asks a specific question (e.g., whether withdrawing an earlier khula petition for reconciliation counts against them), answer that question directly in the very first sentence before explaining other legal steps.
3. STRICT STATUTORY GROUNDING:
   - You MUST base all legal citations strictly on the provided statutory sections from the legal knowledge base. Always cite the exact Act name and Section number (e.g., "Section 10 of the Family Courts Act 1964").
4. LOW CONFIDENCE HANDLING:
   - If the retrieved sections do not directly match the facts, do NOT commit to an unrelated statute or guess random sections. Clearly state that more specific facts are needed, explain what is missing, and ask a clarifying question.
5. OUTPUT FORMATTING (STRICT PLAIN TEXT):
   - NO EMOJIS anywhere.
   - NO MARKDOWN BOLD (**text**) anywhere.
   - NO MARKDOWN HEADERS (### or ####) anywhere.
   - NO DECORATIVE SYMBOLS (👉, ⚖️, ⚠️, 🚨).
   - Use simple numbered lists (1., 2., 3.) only for genuine sequential action steps.
   - Write in natural, easy-to-read paragraphs.
6. ONE CLARIFYING QUESTION AT A TIME:
   - Ask ONLY ONE focused follow-up question per turn to gather missing facts.
7. NO REPEATED DISCLAIMER:
   - The user has already received the full legal disclaimer in the welcome message of their session.
   - Do NOT repeat or append the legal disclaimer or legal drafting advisory paragraph to your response.
"""


def _is_valid_api_key(key: Optional[str]) -> bool:
    if not key:
        return False
    k = key.strip().lower()
    if k.startswith("your-") or "api-key" in k or k in ["none", "placeholder", "xxx"]:
        return False
    return len(k) > 15


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        if self.provider == "auto":
            if _is_valid_api_key(settings.GEMINI_API_KEY):
                self.active_provider = "gemini"
            elif _is_valid_api_key(settings.ANTHROPIC_API_KEY):
                self.active_provider = "claude"
            elif _is_valid_api_key(settings.OPENAI_API_KEY):
                self.active_provider = "openai"
            else:
                self.active_provider = "local"
        else:
            self.active_provider = self.provider

        logger.info(f"Initialized LLMService with provider: {self.active_provider}")

    async def generate_legal_response(
        self,
        user_query: str,
        chat_history: List[Dict[str, str]],
        retrieved_sections: List[Dict[str, Any]],
        case_state: Dict[str, Any],
        language: str = "en",
        analyzed_issues: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate grounded legal intake response using configured LLM or Local Legal Engine.
        Enforces strict plain text output without emojis, headers, or markdown bold.
        Supports multi-issue segmented analysis and role-aware directional grounding.
        """
        # Corpus-wide factual citation validation:
        # Guarantee that any cited statute's prerequisite subject matter actually appears in the user query.
        from ingestion.vector_store import LegalVectorStore
        retrieved_sections = [
            sec for sec in retrieved_sections
            if LegalVectorStore.verify_factual_relevance(sec, user_query)
        ]

        # Format statutory context
        context_blocks = []
        for sec in retrieved_sections:
            block = (
                f"{sec.get('act_title')} - Section {sec.get('section_number')}: {sec.get('section_title')}\n"
                f"Category: {sec.get('category')} | Jurisdiction: {sec.get('jurisdiction')}\n"
                f"Forum / Court: {sec.get('forum_court')}\n"
                f"Classification: Cognizable: {sec.get('cognizable')} | Bailable: {sec.get('bailable')}\n"
                f"Punishment: {sec.get('punishment')}\n"
                f"Plain Summary: {sec.get('summary_plain')}\n"
                f"Statutory Text: {sec.get('statutory_text')}\n"
                f"Required Evidence: {', '.join(sec.get('evidence_required', []))}\n"
                f"Recommended Practical Steps: {'; '.join(sec.get('practical_steps', []))}\n"
            )
            context_blocks.append(block)

        statutory_context = "\n".join(context_blocks) if context_blocks else "No direct statutory match found in knowledge base."

        # Prompt payload
        case_summary_json = json.dumps({
            "issue_type": case_state.get("issue_type", "Pending"),
            "parties": case_state.get("parties", "Undisclosed"),
            "location_province": case_state.get("location_province", "Unspecified"),
            "dates": case_state.get("dates", "Undisclosed"),
            "documents_mentioned": case_state.get("documents_mentioned", [])
        }, ensure_ascii=False)

        if analyzed_issues and len(analyzed_issues) > 1:
            multi_issue_prompt_blocks = []
            for iss in analyzed_issues:
                sec_summaries = []
                for s in iss.get("retrieved_sections", []):
                    sec_summaries.append(f"- {s.get('act_title')} - {s.get('section_number')}: {s.get('section_title')}: {s.get('summary_plain')}")
                secs_text = "\n".join(sec_summaries) if sec_summaries else "No high-confidence statute match."
                block = (
                    f"Issue {iss.get('issue_index')}: {iss.get('issue_title')}\n"
                    f"Aggrieved Party: {iss.get('aggrieved_party')} | Wrongdoer: {iss.get('wrongdoer')}\n"
                    f"Action Taken: {iss.get('action_taken')}\n"
                    f"Relief Sought: {iss.get('relief_sought')}\n"
                    f"Retrieved Statutory Sections for this issue:\n{secs_text}\n"
                )
                multi_issue_prompt_blocks.append(block)

            user_prompt = (
                f"CURRENT STRUCTURED CASE SUMMARY:\n{case_summary_json}\n\n"
                f"ANALYZED ISSUES & ROLE-AWARE GROUNDING STATUTES:\n\n" +
                "\n".join(multi_issue_prompt_blocks) + "\n\n"
                f"USER QUERY / INTAKE DETAILS:\n{user_query}\n\n"
                f"Preferred Language: {language}\n\n"
                f"IMPORTANT FORMATTING INSTRUCTIONS FOR MULTI-ISSUE RESPONSE:\n"
                f"1. Clearly separate and address each issue under plain labels: 'Issue 1: [Title]', 'Issue 2: [Title]', etc.\n"
                f"2. For each issue, explain the aggrieved party's legal remedy, the relevant statutes from retrieved grounding, and why each applies (e.g. restoration under Specific Relief Act Section 9 if locked out, declaration under SRA Section 42, stay order under CPC Order 39, or eviction under rent law if default).\n"
                f"3. Provide practical numbered steps (1., 2., 3.) and key evidence needed for each issue.\n"
                f"4. End with ONE focused clarifying question. Do NOT include or repeat the legal disclaimer or drafting advisory.\n"
                f"5. Write in natural plain sentences. NO emojis. NO markdown bold (**text**). NO markdown headers (###)."
            )
        else:
            user_prompt = (
                f"CURRENT STRUCTURED CASE SUMMARY:\n{case_summary_json}\n\n"
                f"RETRIEVED PAKISTANI STATUTORY SECTIONS (RAG GROUNDING):\n{statutory_context}\n\n"
                f"USER QUERY / INTAKE DETAILS:\n{user_query}\n\n"
                f"NEXT CLARIFYING QUESTION TO CONSIDER ASKING: {case_state.get('next_clarifying_question', '')}\n\n"
                f"Preferred Language: {language}\n\n"
                f"IMPORTANT FORMATTING INSTRUCTION: Write your entire response in plain, natural sentences. "
                f"Do not use emojis. Do not use markdown bold (**text**). Do not use markdown headers (###). "
                f"Explain applicable laws, practical steps (numbered 1, 2, 3), and evidence needed, "
                f"and end with exactly ONE clarifying question. Do NOT include or repeat the legal disclaimer."
            )

        response_text = ""

        # 1. Try Gemini
        if self.active_provider == "gemini" and _is_valid_api_key(settings.GEMINI_API_KEY):
            try:
                response_text = await self._call_gemini(user_prompt, chat_history)
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Falling back to Local Legal Engine.")

        # 2. Try Claude
        elif self.active_provider == "claude" and _is_valid_api_key(settings.ANTHROPIC_API_KEY):
            try:
                response_text = await self._call_claude(user_prompt, chat_history)
            except Exception as e:
                logger.warning(f"Claude API call failed: {e}. Falling back to Local Legal Engine.")

        # 3. Try OpenAI
        elif self.active_provider == "openai" and _is_valid_api_key(settings.OPENAI_API_KEY):
            try:
                response_text = await self._call_openai(user_prompt, chat_history)
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Falling back to Local Legal Engine.")

        # 4. Built-in Local Legal Engine fallback (Zero-dependency, immediate, guaranteed)
        if not response_text:
            response_text = self._generate_local_legal_response(
                user_query, retrieved_sections, case_state, language, analyzed_issues
            )

        # Apply guardrails and enforce plain text formatting
        safe_response = apply_guardrails(response_text)

        return {
            "content": safe_response,
            "provider_used": self.active_provider if response_text else "local_engine",
            "citations": [
                {
                    "id": sec["id"],
                    "act_code": sec.get("act_code"),
                    "act_title": sec.get("act_title"),
                    "section_number": sec.get("section_number"),
                    "section_title": sec.get("section_title"),
                    "forum_court": sec.get("forum_court")
                }
                for sec in retrieved_sections
            ]
        }

    async def _call_gemini(self, user_prompt: str, chat_history: List[Dict[str, str]]) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        contents = []
        for msg in chat_history[-6:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        contents.append({"role": "user", "parts": [{"text": user_prompt}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception(f"Gemini API error {resp.status_code}: {resp.text}")

    async def _call_claude(self, user_prompt: str, chat_history: List[Dict[str, str]]) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        messages = []
        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": settings.CLAUDE_MODEL,
            "system": SYSTEM_PROMPT,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["content"][0]["text"]
            else:
                raise Exception(f"Claude API error {resp.status_code}: {resp.text}")

    async def _call_openai(self, user_prompt: str, chat_history: List[Dict[str, str]]) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 2048
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"OpenAI API error {resp.status_code}: {resp.text}")

    def _generate_local_legal_response(
        self,
        user_query: str,
        retrieved_sections: List[Dict[str, Any]],
        case_state: Dict[str, Any],
        language: str,
        analyzed_issues: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        High-precision Local Legal Engine for zero-dependency operation.
        Explains Pakistani law simply and clearly, like explaining to a friend with zero legal background.
        No emojis, no markdown bold, no headers, simple numbered lists only for steps, and no repeated disclaimers.
        Supports multi-issue segmented analysis and single-issue consultation turns.
        """
        is_urdu = language == "ur" or any("\u0600" <= c <= "\u06FF" for c in user_query)
        q_lower = user_query.lower()

        def _simplify_forum(forum: str) -> str:
            if not forum:
                return "the local court"
            f = forum.lower()
            if "magistrate" in f:
                return "the local magistrate's court"
            if "rent" in f:
                return "the local rent office / rent controller"
            if "family" in f:
                return "the family court"
            if "consumer" in f:
                return "the district consumer court"
            if "labour" in f:
                return "the local labour court"
            if "high court" in f:
                return "the High Court"
            if "civil" in f:
                return "the local civil court"
            if "session" in f:
                return "the sessions court"
            return forum

        # Direct procedural answer check (e.g. Khula withdrawal / reconciliation)
        procedural_prefix = ""
        if "khula" in q_lower and any(w in q_lower for w in ["withdr", "withdrew", "withdrawn"]) and any(w in q_lower for w in ["reconcil", "again", "new case", "count against", "stop me", "second"]):
            procedural_prefix = (
                "To answer your question directly: withdrawing a previous khula petition because you reconciled does NOT "
                "count against you, and it does not stop you from filing a new case. Under Pakistani family law, trying to "
                "reconcile is encouraged. If things did not work out and discord has returned, you have every right to file "
                "a fresh khula case before the family court.\n\n"
            )

        # Multi-issue response assembly
        if analyzed_issues and len(analyzed_issues) > 1:
            res_parts = []
            if procedural_prefix:
                res_parts.append(procedural_prefix.strip() + "\n")

            for issue in analyzed_issues:
                idx = issue.get("issue_index", 1)
                title = issue.get("issue_title", f"Issue {idx}")
                issue_secs = issue.get("retrieved_sections", [])
                confidence = issue.get("confidence_passed", len(issue_secs) > 0)

                res_parts.append(f"Issue {idx}: {title}\n")

                if not confidence or not issue_secs:
                    rs = issue.get("relief_sought", "")
                    if rs and rs != "Legal clarification" and issue.get("issue_title") != "General Inquiry":
                        res_parts.append(f"{rs}\n")
                    else:
                        res_parts.append(
                            "Based on the details provided so far, there is not yet enough specific factual information to identify "
                            "the exact Pakistani law or court for this matter.\n"
                        )
                    continue

                top_sec = issue_secs[0]
                act_title = top_sec.get("act_title", "Pakistani Law")
                sec_num = str(top_sec.get("section_number", "")).strip()
                sec_display = sec_num if (sec_num.lower().startswith("section") or sec_num.lower().startswith("order") or sec_num.lower().startswith("art")) else f"Section {sec_num}"
                sec_title = top_sec.get("section_title", "")
                forum = top_sec.get("forum_court", "the relevant court")
                simple_forum = _simplify_forum(forum)
                punishment = top_sec.get("punishment", "")
                summary_plain = top_sec.get("summary_plain", "")

                if len(issue_secs) > 1:
                    second_sec = issue_secs[1]
                    sec2_num = str(second_sec.get("section_number", "")).strip()
                    sec2_display = sec2_num if (sec2_num.lower().startswith("section") or sec2_num.lower().startswith("order") or sec2_num.lower().startswith("art")) else f"Section {sec2_num}"
                    sec2_act = second_sec.get("act_title", "Pakistani Law")
                    sec2_summary = second_sec.get("summary_plain", "")
                    res_parts.append(
                        f"Based on the facts you shared, the relevant Pakistani laws are {sec_display} of the {act_title} "
                        f"and {sec2_display} of the {sec2_act}.\n\n"
                        f"In plain terms, this law means: {summary_plain} In addition, {sec2_display} provides: {sec2_summary}\n\n"
                        f"The proper place to take this matter is {simple_forum}."
                    )
                else:
                    res_parts.append(
                        f"Based on the facts you shared, the relevant Pakistani law is {sec_display} of the {act_title}, which covers {sec_title}.\n\n"
                        f"In plain terms, this law means: {summary_plain}\n\n"
                        f"The proper place to take this matter is {simple_forum}."
                    )

                rs = issue.get("relief_sought", "")
                if rs and rs != "Legal clarification" and issue.get("issue_title") != "General Inquiry" and len(rs) > 40:
                    res_parts.append(f"{rs.strip()}\n")

                if punishment:
                    res_parts.append(f"The legal remedy or penalty provided under the law is: {punishment}\n")

                steps = top_sec.get("practical_steps", [])
                if steps:
                    res_parts.append("Here are the practical next steps you should consider:")
                    for s_idx, step in enumerate(steps, 1):
                        res_parts.append(f"{s_idx}. {step}")
                    res_parts.append("")

                evidence = top_sec.get("evidence_required", [])
                if evidence:
                    res_parts.append(f"To support your position, the key documents and evidence you will need include: {', '.join(evidence)}.\n")

            clarifying = case_state.get("next_clarifying_question", "Which city or province did this take place in, and are there any written documents or notices involved?")
            res_parts.append(f"To help clarify your situation further: {clarifying}\n")

            return "\n".join(res_parts)

        # Single-issue response assembly
        top_sec = retrieved_sections[0] if retrieved_sections else None

        if not top_sec:
            outside_coverage_msg = ""
            if analyzed_issues and analyzed_issues[0].get("relief_sought"):
                first_iss = analyzed_issues[0]
                rs = first_iss.get("relief_sought", "")
                title = first_iss.get("issue_title", "")
                if rs and rs != "Legal clarification" and title != "General Inquiry":
                    outside_coverage_msg = rs

            if outside_coverage_msg:
                clarifying = case_state.get("next_clarifying_question", "")
                if clarifying and not ("Statutory Currency" in title or "coercive control" in rs.lower() or "Support and Protection" in rs):
                    return f"{outside_coverage_msg}\n\nTo help clarify your situation further: {clarifying}"
                return outside_coverage_msg
            if is_urdu:
                return (
                    "آپ کے بیان کردہ معاملے کے بارے میں درست قانونی رہنمائی فراہم کرنے کے لیے مزید تفصیلات درکار ہیں۔ "
                    "برائے مہربانی بتائیں کہ واقعہ کس شہر یا صوبے میں پیش آیا اور کیا اس میں کوئی معاہدہ، پولیس شکایت، یا دستاویز موجود ہے؟\n\n"
                    f"{case_state.get('next_clarifying_question', 'کیا آپ اس واقعے کے بارے میں کچھ مزید تفصیل بتا سکتے ہیں؟')}"
                )
            return (
                "Based on the details provided so far, there is not yet enough specific information to identify the exact Pakistani law or court that applies to your situation.\n\n"
                "To help you determine the right legal remedy and applicable law, could you please provide a few more details about what happened?\n\n"
                f"{case_state.get('next_clarifying_question', 'Which city or province did this happen in, and are there any written documents or police complaints involved?')}"
            )

        # Build grounded response in plain, natural prose
        act_title = top_sec.get("act_title", "Pakistani Law")
        sec_num = top_sec.get("section_number", "")
        sec_title = top_sec.get("section_title", "")
        forum = top_sec.get("forum_court", "the relevant court")
        simple_forum = _simplify_forum(forum)
        punishment = top_sec.get("punishment", "")
        summary_plain = top_sec.get("summary_plain", "")
        summary_urdu = top_sec.get("summary_urdu", "")

        # Directional role check for cheque matters: Drawer vs Payee
        is_cheque_drawer = bool(
            re.search(
                r"\b(?:i\s*gave|i\s*issued|my\s*cheque|gave\s*(?:someone\s*)?a\s*cheque|issued\s*a\s*cheque|fearing\s*arrest|get\s*me\s*arrested|threaten\w*\s*(?:to\s*)?(?:cash|arrest)|deal\s*fell\s*through|deal\s*cancelled|drawer)\b",
                q_lower
            )
        ) or (analyzed_issues and any("Failed Consideration Defense" in iss.get("issue_title", "") for iss in analyzed_issues))

        has_489f = any("489" in str(s.get("section_number", "")) for s in retrieved_sections)

        if is_cheque_drawer and has_489f:
            simple_forum = "the sessions court (for Pre-Arrest Bail under Section 498 CrPC) and the local civil court (for cancellation of the cheque)"
            punishment = "Under Section 489-F PPC, criminal liability requires dishonest intention at the time of issuance; if the cheque was issued for an underlying transaction that failed (failure of consideration), dishonest intention is negated, constituting a valid defense against conviction."
            steps = [
                "Issue written 'Stop Payment' instructions to your bank immediately, recording that the underlying commercial transaction fell through.",
                "Dispatch a formal legal notice through an advocate demanding the return and cancellation of the cheque due to failure of consideration.",
                "If police summon you or threaten an FIR under Section 489-F PPC, immediately apply for Pre-Arrest Bail under Section 498 CrPC before the Sessions Court.",
                "File a civil suit for declaration and cancellation of instrument under Sections 39 & 42 of the Specific Relief Act 1877 before the Civil Court, with an application under Order XXXIX Rules 1 & 2 CPC to restrain encashment or prosecution."
            ]
            evidence = [
                "Written agreement or correspondence proving the business deal fell through",
                "Bank receipt or acknowledgement of Stop Payment instructions",
                "Copy of legal notice served demanding return and cancellation of the cheque",
                "Evidence establishing failure of consideration and absence of dishonest intention at inception"
            ]
        else:
            steps = top_sec.get("practical_steps", [])
            evidence = top_sec.get("evidence_required", [])

        if is_urdu:
            res_parts = []
            if procedural_prefix:
                res_parts.append(procedural_prefix.strip() + "\n")
            res_parts.extend([
                f"آپ کے بیان کردہ حالات کے مطابق، اس معاملے پر {act_title} کی دفعہ {sec_num} ({sec_title}) لاگو ہوتی ہے۔\n",
                f"اس قانون کا آسان مفہوم یہ ہے: {summary_urdu}\n",
                f"اس معاملے کو {simple_forum} میں لے جایا جاتا ہے۔"
            ])
            if punishment:
                res_parts.append(f"قانون کے تحت تدارک یا سزا: {punishment}\n")

            if steps:
                res_parts.append("عملی اقدامات:")
                for i, step in enumerate(steps, 1):
                    res_parts.append(f"{i}. {step}")
                res_parts.append("")

            if evidence:
                res_parts.append(f"ضروری ثبوت اور دستاویزات: {', '.join(evidence)}۔\n")

            clarifying = case_state.get("next_clarifying_question", "کیا اس معاملے میں پہلے سے کوئی ایف آئی آر یا قانونی نوٹس دیا گیا ہے؟")
            res_parts.append(f"اگلا سوال: {clarifying}\n")

            return "\n".join(res_parts)

        else:
            sec_clean = str(sec_num).strip()
            sec_display = sec_clean if (sec_clean.lower().startswith("section") or sec_clean.lower().startswith("order") or sec_clean.lower().startswith("art")) else f"Section {sec_clean}"
            res_parts = []
            if procedural_prefix:
                res_parts.append(procedural_prefix.strip() + "\n")
            elif analyzed_issues and analyzed_issues[0].get("relief_sought"):
                rs = analyzed_issues[0].get("relief_sought", "")
                title = analyzed_issues[0].get("issue_title", "")
                if rs and rs != "Legal clarification" and title != "General Inquiry" and len(rs) > 80:
                    is_contradictory = (
                        ("signed" in q_lower or "written" in q_lower) and "verbal agreement" in rs.lower()
                    ) or (
                        not bool(re.search(r"\b(?:foreign|overseas|uk|upwork|fiverr)\b", q_lower)) and "extraterritorial" in rs.lower()
                    )
                    if not is_contradictory:
                        res_parts.append(rs.strip() + "\n\n")

            if len(retrieved_sections) > 1:
                sec2 = retrieved_sections[1]
                sec2_clean = str(sec2.get("section_number", "")).strip()
                sec2_display = sec2_clean if (sec2_clean.lower().startswith("section") or sec2_clean.lower().startswith("order") or sec2_clean.lower().startswith("art")) else f"Section {sec2_clean}"
                sec2_act = sec2.get("act_title", "Pakistani Law")
                sec2_summary = sec2.get("summary_plain", "")
                res_parts.extend([
                    f"Based on the facts you shared, the relevant Pakistani laws are {sec_display} of the {act_title} and {sec2_display} of the {sec2_act}.\n",
                    f"In plain terms, this law means: {summary_plain} In addition, {sec2_display} provides: {sec2_summary}\n",
                    f"The proper place to take this matter is {simple_forum}."
                ])
            else:
                res_parts.extend([
                    f"Based on the facts you shared, the relevant Pakistani law is {sec_display} of the {act_title}, which covers {sec_title}.\n",
                    f"In plain terms, this law means: {summary_plain}\n",
                    f"The proper place to take this matter is {simple_forum}."
                ])
            if punishment:
                res_parts.append(f"The legal remedy or penalty provided under the law is: {punishment}\n")

            if steps:
                res_parts.append("Here are the practical next steps you should consider:")
                for i, step in enumerate(steps, 1):
                    res_parts.append(f"{i}. {step}")
                res_parts.append("")

            if evidence:
                res_parts.append(f"To support your position, the key documents and evidence you will need include: {', '.join(evidence)}.\n")

            clarifying = case_state.get("next_clarifying_question", "Has any formal FIR, police complaint, or legal notice already been filed?")
            res_parts.append(f"To help clarify your situation further: {clarifying}\n")

            return "\n".join(res_parts)
