"""
Safety & Guardrail Engine for Qanoon Sahayak
Enforces strict legal compliance, emergency intervention, and non-prediction policies.
Provides plain-text output sanitization with no emojis, no markdown bold, and no headers.
"""

import re
import logging
from typing import Tuple, List, Dict, Any

logger = logging.getLogger(__name__)

LEGAL_DISCLAIMER = (
    "Legal Disclaimer: Qanoon Sahayak provides educational and informational guidance based on Pakistani law. "
    "This does not constitute formal legal advice or an attorney-client relationship. Case outcomes depend on "
    "evidence, limitation periods, and judicial discretion. Always consult a licensed Advocate of the High Court "
    "or Bar Council for formal legal representation and court filings."
)

DRAFT_WARNING_BANNER = (
    "\n\nLegal Drafting Advisory: This draft template is provided strictly for educational reference and initial preparation. "
    "Under the Legal Practitioners and Bar Councils Act 1973, all court pleadings, plaints, petitions, and formal legal notices "
    "must be formally finalized, vetted, and signed by an enrolled Advocate licensed with the Bar Council before submission to any court or authority.\n"
)

# Emergency patterns for Pakistan (Self-Harm and Immediate Domestic Violence)
SELF_HARM_PATTERNS = [
    r"\b(suicide|suicidal|kill\s*myself|end\s*my\s*life|ending\s*my\s*life|end\s*it\s*all|want\s*to\s*die|wishing\s*to\s*die|wish\s*i\s*(?:was|were)\s*dead|better\s*off\s*dead|self\s*harm|harming\s*myself|hurt\s*myself)\b",
    r"\b(don'?t\s+see\s+(?:the\s+)?point\s+in\s+living|no\s+point\s+in\s+living|not\s+worth\s+living|can'?t\s+(?:go\s+on\s+)?live|don'?t\s+want\s+to\s+live|give\s*up\s+on\s+life|tired\s+of\s+living|thinking\s+of\s+ending\s+it)\b",
    r"\b(خودکشی|مرنا\s*چاہتا|مرنا\s*چاہتی|زندگی\s*ختم|جینے\s*کا\s*(?:کوئی\s*)?فائدہ\s*نہیں|جان\s*دے\s*دوں|زندگی\s*سے\s*تنگ)\b",
    r"\b(khudkushi|khud\s*kushi|mar\s*jaon|marne\s*laga|marne\s*ka\s*dil|jeene\s*ka\s*(?:koi\s*)?faida\s*nahi|zindagi\s*khatam|zindagi\s*se\s*tang)\b"
]

DOMESTIC_VIOLENCE_PATTERNS = [
    r"\b(hits\s*me|hit\s*me|hitting\s*me|beats\s*me|beat\s*me|beating\s*me|punches\s*me|punched\s*me|slaps\s*me|slapped\s*me|choking\s*me|choked\s*me|strangling\s*me|strangled\s*me|kicking\s*me|kicked\s*me)\b",
    r"\b(don'?t\s+feel\s+safe\s+at\s+home|not\s+safe\s+at\s+home|unsafe\s+at\s+home|fear\s+for\s+my\s+life|afraid\s+for\s+my\s+safety|threatens\s+to\s+(?:harm|kill|hurt)\s+me|threatened\s+to\s+(?:harm|kill|hurt)\s+me|terrified\s+for\s+my\s+life)\b",
    r"\b(physically\s*abusive|physical\s*abuse|domestic\s*violence|domestic\s*abuse|abuses\s*me|abused\s*me|violence\s*at\s*home|violent\s*at\s*home)\b",
    r"\b(locked\s*in\s*(?:the\s*)?room|locked\s*me\s*in|knife\s*at\s*my\s*throat|gun\s*pointed|going\s*to\s*kill\s*me\s*now|throw\s*acid|acid\s*attack|shoot\s*me|shoot\s*dead)\b",
    r"\b(جان\s*سے\s*مارنے|کمرے\s*میں\s*بند|تشدد|مار\s*پیٹ|مارتا\s*ہے|مارتی\s*ہے|گھریلو\s*تشدد|محفوظ\s*نہیں|جان\s*کا\s*خطرہ)\b",
    r"\b(mar\s*rha\s*hai|maar\s*rha\s*hai|kamray\s*me\s*band|jaan\s*ka\s*khatra|abhe\s*maar\s*dega|marta\s*hai|maarta\s*hai|hath\s*uthata|mehfooz\s*nahi|ghar\s*me\s*mehfooz\s*nahi|tashaddud|gharelu\s*tashaddud)\b"
]

# Coercive Control & Non-Physical Domestic Abuse Patterns
COERCIVE_CONTROL_PATTERNS = [
    r"\b(?:takes?|took|taking|confiscated?|confiscating|seized?)\s*(?:her|his|my)?\s*phone\b",
    r"\b(?:takes?|took|taking)\s*(?:away\s*)?(?:the\s*)?phone\b",
    r"\b(?:won'?t\s+let|doesn'?t\s+allow|not\s+allowed\s+to|can'?t|cannot)\s*(?:her|him|me)?\s*(?:call|contact|talk\s+to|reach|phone)\s*(?:anyone|anybody|family|friends|outside)?\b",
    r"\b(?:phone\s*chheen|phone\s*cheen|phone\s*le\s*liya|raabta\s*nahi|phone\s*band)\b",
    r"\b(?:locks?|locked|locking)\s*(?:her|him|me)\s*(?:out\s+of\s+the\s+house|out\s+of\s+home|out\s+of\s+her\s+house|inside|in\s+the\s+room|in\s+a\s+room|in\s+the\s+house)\b",
    r"\b(?:not\s+allowed\s+to\s+leave|doesn'?t\s+let\s+(?:her|him|me)\s+leave|won'?t\s+let\s+(?:her|him|me)\s+leave)\b",
    r"\b(?:coercive\s*control|restricting\s*(?:her|his|my)\s*(?:movement|phone|communication)|isolat(?:ing|ed)\s*(?:her|him|me))\b",
    r"\b(?:kamray\s*me\s*band|bahar\s*nikal\s*diya|ghar\s*se\s*nikal\s*diya)\b"
]

THIRD_PARTY_PATTERNS = [
    r"\b(?:my\s+friend|my\s+friend'?s|friend'?s\s+husband|friend'?s\s+wife|my\s+sister|my\s+sister'?s|sister'?s\s+husband|my\s+cousin|my\s+neighbor|someone\s+i\s+know|a\s+woman\s+i\s+know|a\s+girl\s+i\s+know|meri\s+dost|meri\s+behen|meri\s+saheli)\b"
]

JUDICIAL_PREDICTION_PATTERNS = [
    (r"(the\s+court\s+will\s+(?:definitely|certainly|100%|surely)\s+(?:rule|decide|order|grant))",
     "Pakistani courts evaluate each case on its merits and evidence; the court may consider"),
    (r"(you\s+will\s+(?:definitely|guaranteed|certainly|100%)\s+win)",
     "the likelihood of relief depends on discharging the statutory burden of proof and supporting evidence"),
    (r"(the\s+judge\s+will\s+(?:definitely|certainly)\s+accept)",
     "the presiding judge has discretionary authority to evaluate")
]


def detect_emergency(user_text: str) -> Tuple[bool, str, List[Dict[str, str]]]:
    """
    Detect immediate life danger, self-harm, suicidal ideation, or domestic violence.
    Returns (is_emergency, trigger_reason, recommended_helplines).
    """
    text_lower = user_text.lower()

    # 1. Check self-harm / suicidal ideation
    for pat in SELF_HARM_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return True, "self_harm_risk", [
                {"name": "Rozan Mental Health & Crisis Helpline", "phone": "0800-22444", "hours": "9am-5pm"},
                {"name": "National Human Rights Helpline", "phone": "1099", "hours": "24/7 Toll Free"},
                {"name": "Edhi Emergency Services", "phone": "115", "hours": "24/7"}
            ]

    # 2. Check domestic violence / immediate violence
    for pat in DOMESTIC_VIOLENCE_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return True, "domestic_violence_immediate_danger", [
                {"name": "Police Emergency", "phone": "15", "hours": "24/7 Urgent Response"},
                {"name": "Punjab Women Protection Helpline", "phone": "1043", "hours": "24/7"},
                {"name": "Sindh Women & Child Helpline", "phone": "1098", "hours": "24/7"},
                {"name": "Rescue 1122 Medical Paramedics", "phone": "1122", "hours": "24/7"},
                {"name": "Madadgar National Helpline", "phone": "1098", "hours": "24/7"}
            ]

    return False, "", []


def detect_coercive_control(user_text: str) -> Tuple[bool, bool, str, List[Dict[str, str]]]:
    """
    Detect coercive control / non-physical domestic abuse patterns (isolation, phone confiscation, movement restriction).
    Returns (is_coercive_control, is_third_party, trigger_reason, helplines).
    """
    text_lower = user_text.lower()
    is_cc = any(re.search(pat, text_lower, re.IGNORECASE) for pat in COERCIVE_CONTROL_PATTERNS)
    if not is_cc:
        return False, False, "", []

    is_third_party = any(re.search(pat, text_lower, re.IGNORECASE) for pat in THIRD_PARTY_PATTERNS)

    helplines = [
        {"name": "Punjab Women Protection Helpline", "phone": "1043", "hours": "24/7 Toll-Free Support"},
        {"name": "Sindh Women & Child Helpline", "phone": "1098", "hours": "24/7"},
        {"name": "Madadgar National Helpline", "phone": "1098", "hours": "24/7 Crisis & Legal Aid"},
        {"name": "Police Emergency", "phone": "15", "hours": "24/7 Urgent Intervention"}
    ]

    reason = "coercive_control_third_party" if is_third_party else "coercive_control_first_person"
    return True, is_third_party, reason, helplines


def build_coercive_control_third_party_response(helplines: List[Dict[str, str]]) -> str:
    """
    Constructs an appropriately calibrated response for third-party reports of coercive control / domestic abuse.
    Acknowledges concern for the friend, surfaces support resources, explains legal remedies,
    and never commits to unrelated commercial or fraud citations.
    """
    helpline_lines = "\n".join([f"{i}. {h['name']}: {h['phone']} ({h.get('hours', '24/7')})" for i, h in enumerate(helplines, 1)])
    return (
        "Support and Protection Advisory for Your Friend:\n\n"
        "What you are describing is a serious and concerning pattern of coercive control and domestic abuse. "
        "Depriving someone of their phone, preventing them from communicating with family or support networks, "
        "and locking them out of their home are recognized forms of psychological abuse and unlawful restraint.\n\n"
        "If you want to assist your friend, please gently connect her with these dedicated protection and legal aid services:\n\n"
        f"{helpline_lines}\n\n"
        "Relevant Legal Protections Under Pakistani Law:\n"
        "1. Protection of Women against Violence Act 2016 (Punjab) / Domestic Violence (Prevention and Protection) Acts (Sindh, KP, Balochistan, and ICT): "
        "A woman subjected to emotional abuse, isolation, or deprivation of communication can obtain urgent Protection Orders, Residence Orders (restraining the abuser from locking her out or forcing her from the home), and Monetary Relief from the Family/Magistrate Court through the District Women Protection Officer.\n"
        "2. Pakistan Penal Code (Sections 340, 341, and 342): Wrongful confinement and wrongful restraint are cognizable offenses when an individual is unlawfully prevented from moving or locked up against their will.\n"
        "3. Shelter and Counseling: District Women Protection Centers and Dar-ul-Aman facilities provide temporary safe accommodation, medical assistance, and state-sponsored legal aid.\n\n"
        "Practical Advice:\n"
        "Help your friend keep a secure, secret record of incidents, and if she is locked out or in danger of physical harm, police assistance can be summoned immediately at 15.\n\n"
        "Which city or province is your friend located in, and does she currently have a safe alternative place to stay?"
    )


def sanitize_court_predictions(response_text: str) -> str:
    """
    Replaces any absolute predictions of court rulings with proper legal discretion language.
    """
    text = response_text
    for pattern, replacement in JUDICIAL_PREDICTION_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def simplify_legal_jargon(text: str) -> str:
    """
    Simplifies complex legal jargon into everyday conversational words:
    - 'ad-interim restraining order' / 'ad-interim temporary injunction' -> 'temporary stay order'
    - 'prima facie case' -> 'a clear initial case based on facts'
    - 'balance of convenience' -> 'who faces greater hardship'
    - 'rendition of accounts' -> 'settlement of business accounts and profits'
    - 'istighasa' -> 'direct private complaint to the magistrate (istighasa)'
    - 'falls under the jurisdiction of' -> 'is handled by'
    - 'jurisdiction of' -> 'authority of'
    - 'court jurisdiction' -> 'court'
    - 'discretionary jurisdiction' -> 'discretionary authority'
    - 'eviction decree' -> 'eviction order'
    - 'decree for khula' -> 'court ruling for khula'
    - 'obtain a decree' -> 'obtain a court decision'
    """
    if not text:
        return ""
    replacements = [
        (r"\bad-interim\s+restraining\s+order\b", "temporary stay order"),
        (r"\bad-interim\s+temporary\s+injunction\b", "temporary stay order"),
        (r"\bad-interim\s+injunction\b", "temporary stay order"),
        (r"\bad-interim\b", "temporary"),
        (r"\bprima\s+facie\s+case\b", "clear initial case based on facts"),
        (r"\bprima\s+facie\b", "clear initial evidence"),
        (r"\bbalance\s+of\s+convenience\b", "who faces greater hardship"),
        (r"\brendition\s+of\s+accounts\b", "settlement of business accounts and profits"),
        (r"\bistighasa\b", "direct private complaint to the magistrate (istighasa)"),
        (r"\bfalls\s+under\s+the\s+jurisdiction\s+of\b", "is handled by"),
        (r"\bunder\s+the\s+jurisdiction\s+of\b", "handled by"),
        (r"\bcourt\s+jurisdiction\b", "court"),
        (r"\bdiscretionary\s+jurisdiction\b", "discretionary authority"),
        (r"\bjurisdiction\s+of\b", "authority of"),
        (r"\beviction\s+decree\b", "eviction order"),
        (r"\bdecree\s+for\s+khula\b", "court ruling for khula"),
        (r"\bobtain\s+a\s+decree\b", "obtain a court decision"),
    ]
    for pattern, rep in replacements:
        text = re.sub(pattern, rep, text, flags=re.IGNORECASE)
    return text


def enforce_drafting_guardrail(response_text: str) -> str:
    """
    If the response contains a formal court pleading draft template, append lawyer review banner.
    Does NOT trigger on regular conversational messages mentioning 'legal notice' or 'versus'.
    """
    text_lower = response_text.lower()
    if "respectfully sheweth" in text_lower and ("plaint under" in text_lower or "in the court of" in text_lower):
        if "Legal Drafting Advisory" not in response_text and "MANDATORY LEGAL DRAFTING ADVISORY" not in response_text:
            response_text += DRAFT_WARNING_BANNER
    return response_text


def strip_formatting_and_emojis(text: str) -> str:
    """
    Strict plain text formatter:
    - Removes all emojis
    - Removes markdown bold (**text**)
    - Removes markdown headers (###, ####)
    - Removes decorative symbols (👉, ⚖️, ⚠️, 🚨, etc.)
    - Removes blockquote '>' indicators
    - Preserves simple numbered lists and natural paragraphs
    """
    if not text:
        return ""

    # Remove markdown headers like ### or #### at the start of lines
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)

    # Remove bold: **text** -> text
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)

    # Remove bold/italic combos: ***text*** -> text
    text = re.sub(r"\*\*\*([^*]+)\*\*\*", r"\1", text)

    # Remove italic markers: *text* -> text (when used for styling, not bullet)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", text)

    # Remove unicode emoji ranges
    text = re.sub(r"[\U00010000-\U0010ffff]", "", text)

    # Remove specific decorative and emoji symbols
    emoji_symbols = [
        "⚖️", "⚖", "⚠️", "⚠", "🚨", "👉", "📞", "📎", "✅", "❌", "💡", "📌",
        "🔹", "🔸", "▪️", "▫️", "•", "→", "►", "★", "☆"
    ]
    for sym in emoji_symbols:
        text = text.replace(sym, "")

    # Remove markdown blockquote characters
    text = re.sub(r"^\s*>\s*", "", text, flags=re.MULTILINE)

    # Remove markdown horizontal rules (--- or ***)
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Normalize multiple blank lines to at most 2
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def apply_guardrails(response_text: str) -> str:
    """Apply all output safety filters and enforce plain text styling."""
    text = sanitize_court_predictions(response_text)
    text = simplify_legal_jargon(text)
    text = enforce_drafting_guardrail(text)
    text = strip_formatting_and_emojis(text)
    return text
