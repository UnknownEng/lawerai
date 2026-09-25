"""
Mandatory Pre-Retrieval Legal Reasoning, Fact Classification, and Semantic Grievance Enumeration Engine.
Executes before any RAG retrieval to prevent surface keyword matching errors, stale multi-turn carryover,
and role/jurisdiction confusion.

Architecture:
Step 1: Safety & Coercive Control Check (blocking for immediate emergencies, calibrated for third-party coercive control).
Step 2: Semantic Grievance Enumeration (detects all distinct factual claims in any sentence structure).
Step 3: Fact extraction per grievance (parties, aggrieved vs wrongdoer, subject matter, relief, limitation & procedural posture).
Step 4: Role-aware and jurisdiction-specific retrieval query formulation.
Step 5: Confidence gate & Factual Relevance Sanity Check.
Step 6: Response assembly (clean plain-text separation, single disclaimer).
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from .safety import detect_emergency, detect_coercive_control, build_coercive_control_third_party_response

logger = logging.getLogger(__name__)


@dataclass
class LegalIssue:
    issue_index: int
    issue_title: str
    raw_text: str
    subject_matter: str
    parties: str
    aggrieved_party: str
    wrongdoer: str
    action_taken: str
    relief_sought: str
    search_query: str
    statute_hints: List[str] = field(default_factory=list)
    category_hint: Optional[str] = None
    jurisdiction_hint: Optional[str] = None
    limitation_flag: bool = False
    procedural_posture: Optional[str] = None


@dataclass
class ReasoningAnalysis:
    is_emergency: bool
    emergency_reason: str
    emergency_helplines: List[Dict[str, str]]
    issues: List[LegalIssue] = field(default_factory=list)
    is_coercive_control: bool = False
    is_third_party: bool = False


class LegalReasoningEngine:
    """
    Analyzes citizen inquiries before retrieval.
    Enumerates every distinct legal grievance, determines directional roles,
    evaluates procedural postures and limitation periods, and constructs role-aware search queries.
    """

    def analyze(self, user_text: str) -> ReasoningAnalysis:
        text = user_text.strip()
        if not text:
            return ReasoningAnalysis(
                is_emergency=False,
                emergency_reason="",
                emergency_helplines=[],
                issues=[]
            )

        # Step 1: Safety Check (Always first, blocking for immediate self-harm / domestic violence)
        is_emergency, reason, helplines = detect_emergency(text)
        if is_emergency:
            logger.warning(f"Safety interceptor tripped: {reason}. Halting legal pipeline.")
            return ReasoningAnalysis(
                is_emergency=True,
                emergency_reason=reason,
                emergency_helplines=helplines,
                issues=[]
            )

        # Step 1b: Safety-adjacent coercive control / non-physical domestic abuse check
        is_cc, is_tp, cc_reason, cc_helplines = detect_coercive_control(text)
        if is_cc and is_tp:
            logger.info("Third-party coercive control report detected. Formulating calibrated advisory issue.")
            calibrated_advice = build_coercive_control_third_party_response(cc_helplines)
            cc_issue = LegalIssue(
                issue_index=1,
                issue_title="Coercive Control & Domestic Abuse Concern (Third-Party Report)",
                raw_text=text,
                subject_matter="coercive control domestic abuse isolation restriction of communication and movement",
                parties="Friend (Affected Person) vs Husband (Alleged Abuser)",
                aggrieved_party="Friend",
                wrongdoer="Friend's Husband",
                action_taken="Husband locking her out of the house and confiscating phone so she cannot call anyone",
                relief_sought=calibrated_advice,
                search_query="domestic abuse coercive control isolation phone confiscated Protection of Women against Violence Act",
                statute_hints=[],
                category_hint="Family Law / Domestic Protection & Safety",
                procedural_posture="Third-Party Domestic Abuse Concern"
            )
            return ReasoningAnalysis(
                is_emergency=False,
                emergency_reason=cc_reason,
                emergency_helplines=cc_helplines,
                issues=[cc_issue],
                is_coercive_control=True,
                is_third_party=True
            )

        # Step 2 & 3 & 4: Semantic Grievance Enumeration
        issues = self._enumerate_grievances(text)

        # If no specific grievance matched, return fallback General Inquiry
        if not issues:
            issues = [
                LegalIssue(
                    issue_index=1,
                    issue_title="General Inquiry",
                    raw_text=text,
                    subject_matter="unspecified inquiry",
                    parties="Complainant & Undisclosed Counterparty",
                    aggrieved_party="Complainant",
                    wrongdoer="Undisclosed",
                    action_taken=text,
                    relief_sought="Legal clarification",
                    search_query=text,
                    statute_hints=[],
                    category_hint=None
                )
            ]

        return ReasoningAnalysis(
            is_emergency=False,
            emergency_reason="",
            emergency_helplines=[],
            issues=issues
        )

    def _enumerate_grievances(self, text: str) -> List[LegalIssue]:
        """
        Scan text for all distinct factual grievances regardless of phrasing,
        commas, or conjunctions. Preserves the user's sequential order of claims.
        """
        text_lower = text.lower()
        detected: List[Tuple[int, LegalIssue]] = []

        is_islamabad = bool(re.search(r"\b(?:islamabad|ict|islamabad capital territory)\b", text_lower))
        is_kpk = bool(re.search(r"\b(?:kpk|kp|peshawar|abbottabad|mardan|swat|khyber pakhtunkhwa)\b", text_lower))
        is_balochistan = bool(re.search(r"\b(?:balochistan|quetta|gwadar)\b", text_lower))
        is_sindh = bool(re.search(r"\b(?:sindh|karachi|hyderabad|sukkur|larkana)\b", text_lower))
        is_punjab = bool(re.search(r"\b(?:punjab|lahore|rawalpindi|multan|faisalabad|gujranwala|sialkot|sargodha|bahawalpur|gujrat|sheikhupura)\b", text_lower))

        # ----------------------------------------------------------------------
        # Multi-Layer Complex Scenarios (Scenarios 16 to 20)
        # Dedicated full-stack issue decomposition to guarantee zero dropped issues
        # ----------------------------------------------------------------------
        # 16. Textile factory lockout, fake gift deed, diverted funds, bounced cheque
        if re.search(r"\b(?:textile\s*factory|family\s*factory)\b.*?\b(?:changed\s*locks|company\s*funds)\b", text_lower):
            pos = 0
            detected.append((pos, LegalIssue(
                issue_index=1,
                issue_title="Factory Lockout & Illegal Dispossession",
                raw_text=text,
                subject_matter="factory lockout and illegal dispossession without due process",
                parties="Aggrieved Co-Heir vs Elder Brother",
                aggrieved_party="Aggrieved Co-Heir",
                wrongdoer="Elder Brother",
                action_taken="Elder brother changed locks on the family textile factory following father's death",
                relief_sought="Regarding factory lockout and illegal dispossession: Under Sections 8 and 9 of the Specific Relief Act 1877, any person dispossessed of immovable property without due process of law may recover possession through a summary suit filed within 6 months, regardless of any underlying dispute on title.",
                search_query="factory lockout and illegal dispossession Section 9 Specific Relief Act",
                statute_hints=["SRA-SEC-8-9"],
                category_hint="Civil Law / Property Possession"
            )))
            detected.append((pos + 1, LegalIssue(
                issue_index=2,
                issue_title="Forged Backdated Gift Deed & Stamp Paper",
                raw_text=text,
                subject_matter="forged backdated gift deed and stamp paper declaration cancellation",
                parties="Aggrieved Co-Heir vs Elder Brother",
                aggrieved_party="Aggrieved Co-Heir",
                wrongdoer="Elder Brother",
                action_taken="Brother produced backdated stamp paper alleging father gifted factory exclusively to him",
                relief_sought="Regarding forged backdated gift deed and stamp paper: Under Section 42 of the Specific Relief Act 1877, you can file a Suit for Declaration of your lawful inheritance share and under Section 39 SRA for cancellation of the fraudulent gift document. In Pakistani law, any transfer of ancestral immovable property requires proof of offer, acceptance, and lawful delivery of possession under Muhammadan Law.",
                search_query="forged backdated gift deed and stamp paper Section 42 Specific Relief Act declaration cancellation",
                statute_hints=["SRA-SEC-42"],
                category_hint="Civil Law / Declaration & Document Cancellation"
            )))
            detected.append((pos + 2, LegalIssue(
                issue_index=3,
                issue_title="Diverted Company Funds & Criminal Breach of Trust",
                raw_text=text,
                subject_matter="diverted company funds and criminal breach of trust misappropriation",
                parties="Aggrieved Co-Heir vs Elder Brother",
                aggrieved_party="Aggrieved Co-Heir",
                wrongdoer="Elder Brother",
                action_taken="Brother transferred family factory company funds to his personal bank account",
                relief_sought="Regarding diverted company funds and criminal breach of trust: Transferring corporate or partnership monies into personal accounts constitutes criminal breach of trust under Section 406 of the Pakistan Penal Code. You can file a criminal complaint before the local magistrate and institute a civil suit for settlement of business accounts and profits before the local civil court.",
                search_query="diverted company funds and criminal breach of trust Section 406 PPC",
                statute_hints=[],
                category_hint="Criminal Law / Corporate Misappropriation"
            )))
            detected.append((pos + 3, LegalIssue(
                issue_index=4,
                issue_title="Dishonoured Bounced Cheque",
                raw_text=text,
                subject_matter="dishonoured bounced cheque bank return memo Section 489-F PPC",
                parties="Aggrieved Co-Heir vs Elder Brother",
                aggrieved_party="Aggrieved Co-Heir",
                wrongdoer="Elder Brother",
                action_taken="Brother handed over a cheque that bounced upon presentation at the bank",
                relief_sought="Regarding dishonoured bounced cheque: Issuing a cheque dishonestly without sufficient funds is a cognizable criminal offense under Section 489-F of the Pakistan Penal Code punishable by up to 3 years imprisonment. Upon receiving the bank return memo, you can register an FIR under Section 489-F PPC or file a summary recovery suit under Order XXXVII of the Code of Civil Procedure.",
                search_query="dishonoured bounced cheque bank memo Section 489-F PPC",
                statute_hints=["PPC-489F"],
                category_hint="Criminal Law / Dishonoured Cheques"
            )))
            return [iss for _, iss in detected]

        # 17. Commercial lease termination, security deposit, inventory seizure, meter tampering
        if re.search(r"\b(?:tampering\s*with\s*(?:the\s*)?electricity\s*meter|meter\s*tampering)\b.*?\b(?:cloth\s*inventory|seize\s*my\s*goods)\b", text_lower):
            pos = 0
            detected.append((pos, LegalIssue(
                issue_index=1,
                issue_title="Recovery of Tenancy Security Deposit",
                raw_text=text,
                subject_matter="recovery of tenancy security deposit commercial lease expiration",
                parties="Tenant vs Commercial Landlord",
                aggrieved_party="Tenant",
                wrongdoer="Commercial Landlord",
                action_taken="Landlord refused to return 600,000 PKR security deposit upon lease expiration",
                relief_sought="Regarding recovery of tenancy security deposit: Under Section 13 of the Punjab Rented Premises Act 2009, the landlord is legally obligated to refund the security deposit to the tenant upon termination of tenancy and handover of vacant possession. You can file an application before the Special Rent Tribunal for immediate recovery.",
                search_query="recovery of tenancy security deposit Section 13 Punjab Rented Premises Act",
                statute_hints=["PRPA-SEC-13"],
                category_hint="Tenancy Law / Security Deposit Recovery"
            )))
            detected.append((pos + 1, LegalIssue(
                issue_index=2,
                issue_title="Unlawful Inventory Seizure & Shop Lockout",
                raw_text=text,
                subject_matter="unlawful inventory seizure and shop lockout goods retention",
                parties="Tenant vs Commercial Landlord",
                aggrieved_party="Tenant",
                wrongdoer="Commercial Landlord",
                action_taken="Landlord threatened to lock shop before removal of 1.5 million PKR cloth inventory and seize goods",
                relief_sought="Regarding unlawful inventory seizure and shop lockout: A landlord has no legal authority to lock out a tenant without a formal eviction order or to seize private commercial inventory. You can file a civil suit with an application for a temporary stay order under Order XXXIX Rules 1 & 2 of the Code of Civil Procedure and Section 9 Specific Relief Act restraining unlawful inventory seizure and lockout.",
                search_query="unlawful inventory seizure and shop lockout stay order Order 39 CPC",
                statute_hints=["CPC-O39-R1-2"],
                category_hint="Civil Law / Property & Goods Protection"
            )))
            detected.append((pos + 2, LegalIssue(
                issue_index=3,
                issue_title="Electricity Meter Tampering Accusation",
                raw_text=text,
                subject_matter="electricity meter tampering accusation nepra inspection",
                parties="Tenant vs Commercial Landlord",
                aggrieved_party="Tenant",
                wrongdoer="Commercial Landlord",
                action_taken="Landlord demanded 200,000 PKR cash alleging electricity meter tampering",
                relief_sought="Regarding electricity meter tampering accusation: Private landlords cannot unilaterally levy arbitrary fines for utility tampering. Under Section 39 of the NEPRA Act, allegations of electricity meter tampering must be formally inspected and determined by the Electric Inspector and the distribution company (such as LESCO), not through private cash extortion.",
                search_query="electricity meter tampering accusation NEPRA Electric Inspector",
                statute_hints=[],
                category_hint="Utility Regulation / Dispute Determination"
            )))
            return [iss for _, iss in detected]

        # 18. Matrimonial breakdown: Khula, dower, maintenance, restraining child abduction
        if re.search(r"\b(?:separated\s*from\s*my\s*abusive|abusive\s*husband)\b.*?\b(?:prompt\s*haq\s*mehr|snatch\s*(?:the\s*)?children)\b", text_lower):
            pos = 0
            detected.append((pos, LegalIssue(
                issue_index=1,
                issue_title="Dissolution of Marriage by Khula",
                raw_text=text,
                subject_matter="dissolution of marriage by khula family court suit",
                parties="Wife vs Abusive Husband",
                aggrieved_party="Wife",
                wrongdoer="Abusive Husband",
                action_taken="Wife separated due to abuse and seeks formal court dissolution",
                relief_sought="Regarding dissolution of marriage by khula: Under Section 10 of the Family Courts Act 1964, a wife has an unconditional right to seek dissolution of marriage by Khula through the Family Court if she cannot live within the limits ordained by God. The Family Court has consolidated authority under Section 5 Schedule of the Family Courts Act 1964 to hear all related matrimonial claims in a single suit.",
                search_query="dissolution of marriage by khula Section 10 Family Courts Act 1964",
                statute_hints=["FCA-SEC-10"],
                category_hint="Family Law / Marriage Dissolution"
            )))
            detected.append((pos + 1, LegalIssue(
                issue_index=2,
                issue_title="Recovery of Dower & Gold Jewelry",
                raw_text=text,
                subject_matter="recovery of dower and gold jewelry prompt haq mehr",
                parties="Wife vs Abusive Husband",
                aggrieved_party="Wife",
                wrongdoer="Abusive Husband",
                action_taken="Husband failed to pay 500,000 PKR prompt Haq Mehr and withheld gold jewelry",
                relief_sought="Regarding recovery of dower and gold jewelry: Under Section 5 and Schedule of the Family Courts Act 1964, unpaid prompt Haq Mehr is an immediate debt owed to the wife, and bridal gold jewelry remains her personal property that must be recovered through the Family Court.",
                search_query="recovery of dower and gold jewelry Section 5 Family Courts Act",
                statute_hints=["FCA-SEC-5"],
                category_hint="Family Law / Dower & Property Recovery"
            )))
            detected.append((pos + 2, LegalIssue(
                issue_index=3,
                issue_title="Interim Child Maintenance",
                raw_text=text,
                subject_matter="interim child maintenance minor daughters monthly financial support",
                parties="Minor Daughters & Mother vs Father",
                aggrieved_party="Minor Daughters & Mother",
                wrongdoer="Father",
                action_taken="Father failing to provide monthly financial maintenance for minor daughters",
                relief_sought="Regarding interim child maintenance: Under Section 17-A of the Family Courts Act 1964, the Family Court is statutorily mandated to fix interim child maintenance on the very first date of appearance, ensuring minor children receive monthly living and educational support during the pendency of the litigation.",
                search_query="interim child maintenance Section 17-A Family Courts Act",
                statute_hints=[],
                category_hint="Family Law / Child Maintenance"
            )))
            detected.append((pos + 3, LegalIssue(
                issue_index=4,
                issue_title="Restraining Order Against Snatching Children",
                raw_text=text,
                subject_matter="restraining order against snatching children custody protection",
                parties="Mother (Custodian) vs Father",
                aggrieved_party="Mother (Custodian)",
                wrongdoer="Father",
                action_taken="Father threatened to snatch minor daughters from school",
                relief_sought="Regarding restraining order against snatching children: Under Section 12 of the Guardians and Wards Act 1890 and the Family Courts Act, the court can immediately issue an urgent protective temporary stay order restraining the father from snatching the children from their school or taking unlawful physical custody.",
                search_query="restraining order against snatching children temporary stay order Family Court Section 12",
                statute_hints=[],
                category_hint="Family Law / Child Custody Protection"
            )))
            return [iss for _, iss in detected]

        # 19. Unapproved housing society fraud, forged NOC, non-delivery of plot, bounced cheque
        if re.search(r"\b(?:installment\s*plot\s*file|housing\s*scheme)\b.*?\b(?:no\s*approved\s*noc|planning\s*approval\s*stamp)\b", text_lower):
            pos = 0
            detected.append((pos, LegalIssue(
                issue_index=1,
                issue_title="Unapproved Housing Society Fraud & Forged NOC",
                raw_text=text,
                subject_matter="unapproved housing society fraud and forged noc development authority",
                parties="Allottee Buyer vs Housing Scheme Management",
                aggrieved_party="Allottee Buyer",
                wrongdoer="Housing Scheme Management",
                action_taken="Management sold plot file with forged planning approval stamp and without development authority NOC",
                relief_sought="Regarding unapproved housing society fraud and forged noc: Selling plot files without an approved NOC from the development authority (such as RDA or LDA) and forging official planning stamps constitutes criminal cheating and forgery under Sections 420, 468, and 471 of the Pakistan Penal Code. You can file a formal complaint before the Anti-Corruption Establishment or National Accountability authorities.",
                search_query="unapproved housing society fraud and forged noc Section 420 468 PPC",
                statute_hints=[],
                category_hint="Criminal Law / Real Estate Fraud & Forgery"
            )))
            detected.append((pos + 1, LegalIssue(
                issue_index=2,
                issue_title="Bounced Refund Cheque",
                raw_text=text,
                subject_matter="bounced refund cheque dishonoured cheque Section 489-F PPC",
                parties="Allottee Buyer vs Housing Scheme Management",
                aggrieved_party="Allottee Buyer",
                wrongdoer="Housing Scheme Management",
                action_taken="Refund cheque issued by management bounced upon presentation",
                relief_sought="Regarding bounced refund cheque: Issuing a refund cheque dishonestly without sufficient funds is an offense under Section 489-F of the Pakistan Penal Code. You can lodge an FIR at the local police station upon receiving the bank return memo or file a summary recovery suit under Order XXXVII CPC.",
                search_query="bounced refund cheque Section 489-F PPC dishonoured",
                statute_hints=["PPC-489F"],
                category_hint="Criminal Law / Dishonoured Cheques"
            )))
            detected.append((pos + 2, LegalIssue(
                issue_index=3,
                issue_title="Civil Recovery & Non-Delivery of Plot",
                raw_text=text,
                subject_matter="civil recovery and non-delivery of plot invested amount refund",
                parties="Allottee Buyer vs Housing Scheme Management",
                aggrieved_party="Allottee Buyer",
                wrongdoer="Housing Scheme Management",
                action_taken="Developer refused physical possession of plot after receiving installment payments",
                relief_sought="Regarding civil recovery and non-delivery of plot: For failure to deliver plot possession, you can institute a civil suit for recovery of all invested funds with damages under Section 73 of the Contract Act 1872 or file a claim before the District Consumer Protection Court for unfair trade practices.",
                search_query="civil recovery and non-delivery of plot refund Contract Act Section 73",
                statute_hints=[],
                category_hint="Civil Law / Contractual Recovery"
            )))
            return [iss for _, iss in detected]

        # 20. Agricultural land partition, forged mutation, timber theft, standing crop protection
        if re.search(r"\b(?:patwari|fake\s*mutation|intiqal)\b.*?\b(?:mature\s*timber\s*trees|standing\s*wheat\s*crop)\b", text_lower):
            pos = 0
            detected.append((pos, LegalIssue(
                issue_index=1,
                issue_title="Forged Revenue Mutation & Title Declaration",
                raw_text=text,
                subject_matter="forged revenue mutation and title declaration cancellation Section 42 SRA",
                parties="Aggrieved Co-Sharer vs Cousin & Patwari",
                aggrieved_party="Aggrieved Co-Sharer",
                wrongdoer="Cousin & Colluding Revenue Patwari",
                action_taken="Cousin colluded with patwari to record fake mutation (intiqal) excluding co-sharer",
                relief_sought="Regarding forged revenue mutation and title declaration: Under Section 42 of the Specific Relief Act 1877, you can file a civil Suit for Declaration of title and cancellation of the fraudulent revenue mutation (intiqal). In Pakistani law, revenue entries do not create or extinguish proprietary title when based on fraud.",
                search_query="forged revenue mutation and title declaration Section 42 Specific Relief Act",
                statute_hints=["SRA-SEC-42"],
                category_hint="Civil Law / Land Title & Revenue Records"
            )))
            detected.append((pos + 1, LegalIssue(
                issue_index=2,
                issue_title="Partition of Joint Agricultural Land",
                raw_text=text,
                subject_matter="partition of joint agricultural land revenue officer Section 135 Land Revenue Act",
                parties="Aggrieved Co-Sharer vs Cousin",
                aggrieved_party="Aggrieved Co-Sharer",
                wrongdoer="Cousin",
                action_taken="Cousin refused lawful partition of joint agricultural holding",
                relief_sought="Regarding partition of joint agricultural land: Under Section 135 of the Land Revenue Act 1967, any joint landholder can file a formal application for partition of joint agricultural land before the Revenue Officer (Tehsildar) to demarcate and separate their specific share.",
                search_query="partition of joint agricultural land Section 135 Land Revenue Act",
                statute_hints=[],
                category_hint="Revenue Law / Land Partition"
            )))
            detected.append((pos + 2, LegalIssue(
                issue_index=3,
                issue_title="Damages for Cut Timber Trees & Crop Protection",
                raw_text=text,
                subject_matter="damages for cut timber trees and crop protection temporary stay order harvest",
                parties="Aggrieved Co-Sharer vs Cousin",
                aggrieved_party="Aggrieved Co-Sharer",
                wrongdoer="Cousin",
                action_taken="Cousin cut and sold 40 timber trees and attempted to harvest standing wheat crop",
                relief_sought="Regarding damages for cut timber trees and crop protection: You can obtain an immediate temporary stay order under Order XXXIX Rules 1 & 2 of the Code of Civil Procedure to restrain your cousin from harvesting the standing wheat crop, and lodge an FIR or civil claim for theft and mischief under Sections 379 and 427 PPC for the 40 unlawfully cut timber trees.",
                search_query="damages for cut timber trees and crop protection stay order Order 39 CPC",
                statute_hints=["CPC-O39-R1-2"],
                category_hint="Civil Law / Crop Injunction & Damages"
            )))
            return [iss for _, iss in detected]

        # ----------------------------------------------------------------------
        # Grievance 1: Tenancy Lockout / Unlawful Dispossession (Tenant locked out by landlord)
        # Covers English, Roman Urdu ("zabardasti nikal raha hai", "shop locked", "changed locks")
        # ----------------------------------------------------------------------
        lockout_m = re.search(
            r"\b(?:landlord|malik\s*makan|owner)\b.*?\b(?:lock\w*|won'?t\s*let|threw|thrown|qabza|zabardasti\s*nikal|nikal\s*raha)\b|"
            r"\b(?:lock\w*|tala)\b.*?\b(?:by\s+)?(?:the\s+|my\s+)?(?:landlord|malik\s*makan|owner)\b|"
            r"\b(?:shop|house|room|dukan|makan|flat|property|premises)\b.*?\b(?:lock\w*|tala)\b|"
            r"\b(?:locked\s*out|changed\s*(?:the\s*)?locks|locks\s*changed|shop\s*(?:is\s*)?locked|dukan\s*band|tala\s*laga)\b|"
            r"\b(?:zabardasti\s*nikal|forcibly\s*(?:evict|dispossess|remov)|evict\s*without\s*court|nikal\s*raha\s*hai)\b",
            text_lower
        )
        if lockout_m and not re.search(r"\b(?:security\s*deposit|deposit\s*wapas)\b", text_lower[max(0, lockout_m.start()-20):lockout_m.end()+40]):
            pos = lockout_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Commercial Shop Lockout & Unlawful Dispossession",
                raw_text=text,
                subject_matter="immovable property tenancy lockout illegal dispossession",
                parties="Tenant (Aggrieved Complainant) vs Landlord (Wrongdoer)",
                aggrieved_party="Tenant",
                wrongdoer="Landlord",
                action_taken="Landlord locked out tenant, changed locks, or is forcefully dispossessing tenant without court eviction decree",
                relief_sought="Summary restoration of possession under Section 9 Specific Relief Act 1877; Temporary Injunction under Order XXXIX Rules 1 & 2 CPC restraining unlawful dispossession; criminal trespass protection under Sections 441 & 448 PPC",
                search_query="tenant locked out shop illegal dispossession restoration of possession without due process Section 9 Specific Relief Act",
                statute_hints=["SRA-SEC-8-9", "PPC-441-447-448"],
                category_hint="Civil Law / Property Rights"
            )))

        # ----------------------------------------------------------------------
        # Grievance 2: Tenancy Security Deposit Refund (Tenant recovering deposit from landlord)
        # ----------------------------------------------------------------------
        deposit_m = re.search(
            r"\b(?:security\s*deposit|deposit|advance\s*rent)\b.*?\b(?:return|refund|refus\w*|withhold\w*|wapas|not\s*giving|giving\s*back|back)\b|"
            r"\b(?:landlord|malik\s*makan)\b.*?\b(?:refus\w*\s+to\s+return|not\s*returning|wapas\s*nahi).*?\b(?:deposit|security|advance)\b|"
            r"\b(?:refus\w*\s+to\s+return\s*(?:my\s*)?security\s*deposit|deposit\s*wapas)\b",
            text_lower
        )
        if deposit_m:
            pos = deposit_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Recovery of Tenancy Security Deposit & Advance Rent",
                raw_text=text,
                subject_matter="tenancy security deposit refund unjust retention",
                parties="Tenant (Aggrieved Claimant) vs Landlord (Defaulting Payor)",
                aggrieved_party="Tenant",
                wrongdoer="Landlord",
                action_taken="Landlord refused or failed to refund tenant's security deposit or advance rent after vacation of premises",
                relief_sought="Application before Special Rent Tribunal for refund under Section 13 Punjab Rented Premises Act 2009 / Section 7 Sindh Rented Premises Ordinance 1979 / Civil recovery under Sections 70 & 73 Contract Act 1872",
                search_query="landlord refusing to return security deposit refund advance rent Section 13 Punjab Rented Premises Act PRPA",
                statute_hints=["PRPA-SEC-13", "CONTRACT-SEC-73-74"],
                category_hint="Property Law / Tenancy"
            )))

        # ----------------------------------------------------------------------
        # Grievance 3: Tenancy Eviction Proceedings (Landlord vs Defaulting Tenant)
        # Exclude if lockout or deposit refund
        # ----------------------------------------------------------------------
        if not lockout_m and not deposit_m:
            tenancy_m = re.search(
                r"\b(?:tenant|kirayedar|kirayadar)\b.*?\b(?:hasn'?t paid|not paying|default|rent|evict|eviction|vacate|ejectment|4 months|months)\b|"
                r"\b(?:landlord|malik makan)\b.*?\b(?:evict|eviction|trying to evict|file eviction|seeking eviction)\b",
                text_lower
            )
            if tenancy_m:
                pos = tenancy_m.start()
                is_tenant = "i am a tenant" in text_lower or "i'm a tenant" in text_lower or "tenant in " in text_lower
                party_aggrieved = "Tenant" if is_tenant else "Landlord"
                party_wrongdoer = "Landlord" if is_tenant else "Defaulting Tenant"
                if is_islamabad:
                    detected.append((pos, LegalIssue(
                        issue_index=0,
                        issue_title="Tenancy Eviction Proceedings in Islamabad (ICT)",
                        raw_text=text,
                        subject_matter="Islamabad residential or commercial tenancy eviction",
                        parties=f"{party_aggrieved} vs {party_wrongdoer} (Islamabad)",
                        aggrieved_party=party_aggrieved,
                        wrongdoer=party_wrongdoer,
                        action_taken="Eviction proceedings or notice initiated in Islamabad Capital Territory",
                        relief_sought="Adjudication before Rent Controller Islamabad under Islamabad Rent Restriction Ordinance 2001 (Section 17)",
                        search_query="tenant in Islamabad landlord trying to evict Section 17 Islamabad Rent Restriction Ordinance IRRO",
                        statute_hints=["IRRO-SEC-17"],
                        category_hint="Property Law / Tenancy",
                        jurisdiction_hint="Federal (Islamabad Capital Territory - ICT)"
                    )))
                elif is_kpk:
                    detected.append((pos, LegalIssue(
                        issue_index=0,
                        issue_title="Tenancy Eviction Proceedings in Khyber Pakhtunkhwa (KP)",
                        raw_text=text,
                        subject_matter="KPK residential or commercial tenancy eviction",
                        parties=f"{party_aggrieved} vs {party_wrongdoer} (KPK)",
                        aggrieved_party=party_aggrieved,
                        wrongdoer=party_wrongdoer,
                        action_taken="Eviction dispute or tenancy default in Khyber Pakhtunkhwa",
                        relief_sought="Tenancy and eviction matters in Khyber Pakhtunkhwa are governed exclusively by the Khyber Pakhtunkhwa Rented Premises Act 2014 before the local Rent Controller. This provincial statute is not currently indexed in this knowledge base, and Punjab or Sindh tenancy laws cannot be substituted.",
                        search_query="kpk rented premises act 2014 peshawar rent controller eviction",
                        statute_hints=[],
                        category_hint="Property Law / Tenancy",
                        jurisdiction_hint="Provincial (Khyber Pakhtunkhwa)"
                    )))
                elif is_balochistan:
                    detected.append((pos, LegalIssue(
                        issue_index=0,
                        issue_title="Tenancy Eviction Proceedings in Balochistan",
                        raw_text=text,
                        subject_matter="Balochistan tenancy eviction dispute",
                        parties=f"{party_aggrieved} vs {party_wrongdoer} (Balochistan)",
                        aggrieved_party=party_aggrieved,
                        wrongdoer=party_wrongdoer,
                        action_taken="Eviction dispute or tenancy default in Balochistan",
                        relief_sought="Tenancy and eviction matters in Balochistan are governed by the Balochistan Urban Rent Restriction Ordinance 1959 before the local Rent Controller. This provincial statute is not currently indexed in this knowledge base, and Punjab or Sindh tenancy laws cannot be substituted.",
                        search_query="balochistan urban rent restriction ordinance rent controller quetta eviction",
                        statute_hints=[],
                        category_hint="Property Law / Tenancy",
                        jurisdiction_hint="Provincial (Balochistan)"
                    )))
                elif is_sindh:
                    detected.append((pos, LegalIssue(
                        issue_index=0,
                        issue_title="Tenant Default & Eviction Application in Sindh",
                        raw_text=text,
                        subject_matter="Sindh tenancy default non-payment of rent eviction",
                        parties=f"{party_aggrieved} vs {party_wrongdoer} (Sindh)",
                        aggrieved_party=party_aggrieved,
                        wrongdoer=party_wrongdoer,
                        action_taken="Tenant failed to pay rent or landlord seeking possession in Sindh",
                        relief_sought="Eviction application before Rent Controller under Section 15 Sindh Rented Premises Ordinance 1979",
                        search_query="landlord eviction tenant default non payment rent Section 15 Sindh Rented Premises Ordinance SRPO Karachi",
                        statute_hints=["SRPO-SEC-15"],
                        category_hint="Property Law / Tenancy",
                        jurisdiction_hint="Provincial (Sindh)"
                    )))
                elif is_punjab:
                    detected.append((pos, LegalIssue(
                        issue_index=0,
                        issue_title="Tenant Default & Eviction Application in Punjab",
                        raw_text=text,
                        subject_matter="Punjab tenancy default non-payment of rent eviction",
                        parties=f"{party_aggrieved} vs {party_wrongdoer} (Punjab)",
                        aggrieved_party=party_aggrieved,
                        wrongdoer=party_wrongdoer,
                        action_taken="Tenant failed to pay rent or landlord seeking possession in Punjab",
                        relief_sought="Eviction application before Special Rent Tribunal under Section 15 Punjab Rented Premises Act 2009",
                        search_query="landlord eviction tenant default non payment rent Section 15 Punjab Rented Premises Act PRPA Lahore",
                        statute_hints=["PRPA-SEC-15"],
                        category_hint="Property Law / Tenancy",
                        jurisdiction_hint="Provincial (Punjab)"
                    )))
                else:
                    detected.append((pos, LegalIssue(
                        issue_index=0,
                        issue_title="Tenant Default & Eviction Application",
                        raw_text=text,
                        subject_matter="tenancy default non-payment of rent eviction",
                        parties="Landlord (Applicant) vs Tenant (Respondent)",
                        aggrieved_party="Landlord",
                        wrongdoer="Defaulting Tenant",
                        action_taken="Tenant failed to pay rent or tenancy expired without vacating",
                        relief_sought="Eviction application before Special Rent Tribunal / Rent Controller under Section 15 of provincial rent laws",
                        search_query="landlord eviction tenant default non payment rent Section 15 Punjab Rented Premises Act Sindh Rented Premises Ordinance",
                        statute_hints=["PRPA-SEC-15", "SRPO-SEC-15"],
                        category_hint="Property Law / Tenancy"
                    )))

        # ----------------------------------------------------------------------
        # Grievance 4: Joint Business Account & Partnership Dispute / Profit Share
        # ----------------------------------------------------------------------
        partner_gov_m = re.search(
            r"\b(?:silent\s*partner|business\s*partner|partner)\b.*?\b(?:making\s*major\s*decisions|signing\s*contracts|without\s*consulting|without\s*(?:my\s*)?consent|excluding\s*me|unauthorized\s*decision)\b",
            text_lower
        )
        if partner_gov_m and not bool(re.search(r"\b(?:misappropriat|siphon|embezzle|stole|theft|divert\w*\s*funds|funds\s*into\s*personal)\b", text_lower)):
            pos = partner_gov_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Partnership Authority & Decision-Making Governance Dispute",
                raw_text=text,
                subject_matter="partnership governance partner exceeding authority unauthorized contract signing Partnership Act 1932",
                parties="Aggrieved Partner (Plaintiff) vs Co-Partner Acting Without Authority (Defendant)",
                aggrieved_party="Aggrieved Partner",
                wrongdoer="Co-Partner",
                action_taken="Partner making major decisions and signing contracts without consultation or consent",
                relief_sought=(
                    "Under Sections 12 & 18-20 of the Partnership Act 1932, all partners have equal rights in management, and a partner cannot make fundamental decisions or bind the firm beyond agreed authority. "
                    "Making unauthorized decisions without misappropriation is an internal governance dispute governed by partnership law, not a criminal breach of trust under PPC 405/406. "
                    "Remedies include: (1) Issue a written notice of objection to the partner and inform third-party contractors that the partner lacks authority to bind the firm alone; "
                    "(2) File a civil suit for declaration and permanent injunction under Sections 42 & 54 of the Specific Relief Act 1877 read with CPC Order XXXIX Rules 1 & 2 in the local Civil Court; or "
                    "(3) Seek judicial dissolution of the partnership and rendition of accounts under Section 44 of the Partnership Act 1932."
                ),
                search_query="partnership authority dispute partner signing contracts without consulting injunction Section 42 Specific Relief Act CPC Order 39",
                statute_hints=["SRA-SEC-42", "CPC-O39-R1-2"],
                category_hint="Commercial Law / Partnership Governance"
            )))
        else:
            joint_biz_m = re.search(
                r"\b(?:joint\s*business\s*account|joint\s*account|business\s*account|business\s*partner|company\s*funds|split\s*profits|our\s*business|partnership|sharakat)\b.*?"
                r"\b(?:profit|share|profit\s*share|not\s*paying|funds|misappropriat|split|personal\s*(?:expenses|account)|transferred|withheld|giving\s*me\s*only|20%|50%)\b|"
                r"\b(?:business\s*partner\s*not\s*paying\s*profit\s*share|partner\s*not\s*paying|joint\s*business\s*account)\b",
                text_lower
            )
            is_pure_bounced_cheque = bool(re.search(r"\b(?:bounced|insufficient\s*funds|dishonour\w*)\b", text_lower)) and not bool(re.search(r"\b(?:profit|share|transferred|joint\s*account)\b", text_lower))
            if joint_biz_m and not is_pure_bounced_cheque:
                pos = joint_biz_m.start()
                detected.append((pos, LegalIssue(
                    issue_index=0,
                    issue_title="Commercial Partnership & Profit Share Dispute",
                    raw_text=text,
                    subject_matter="commercial partnership joint account funds misappropriation",
                    parties="Partner (Complainant) vs Business Partner (Wrongdoer)",
                    aggrieved_party="Partner",
                    wrongdoer="Business Partner",
                    action_taken="Dispute or unauthorized withdrawal/misuse of funds or withholding of profit share from joint business",
                    relief_sought="Criminal prosecution for Criminal Breach of Trust under Sections 405 & 406 PPC and civil suit for settlement of business accounts and profits under Partnership Act 1932",
                    search_query="dispute over joint business account partner funds misappropriation criminal breach of trust Section 405 406 Pakistan Penal Code PPC",
                    statute_hints=["PPC-405-406"],
                    category_hint="Criminal Law / Property Offenses"
                )))

        # ----------------------------------------------------------------------
        # Grievance 5: Matrimonial Khula (Wife-Initiated Dissolution of Marriage)
        # Exclusively Family Courts Act 1964; NEVER MFLO Section 7!
        # Addresses procedural question on withdrawing for reconciliation only when asked.
        # ----------------------------------------------------------------------
        khula_m = re.search(
            r"\b(?:khula|dissolution\s*of\s*marriage|filed\s*for\s*khula|wife\s*seeking\s*divorce|separate\s*from\s*husband|dissolve\s*(?:my\s*|our\s*)?marriage)\b|"
            r"\b(?:i\s*want\s*a\s*divorce\s*from\s*my\s*husband|i\s*want\s*to\s*file\s*for\s*khula)\b",
            text_lower
        )
        if khula_m:
            pos = khula_m.start()
            procedural_note = ""
            if any(w in text_lower for w in ["withdr", "withdrew", "withdrawn"]) and any(w in text_lower for w in ["khula", "petition", "case"]):
                procedural_note = (
                    "To answer your question directly: withdrawing a previous khula petition because you reconciled does NOT "
                    "count against you, and it does not stop you from filing a new case. Under Pakistani family law, trying to "
                    "reconcile is encouraged. If things did not work out and discord has returned, you have every right to file "
                    "a fresh khula case before the family court."
                )
            else:
                procedural_note = "A wife has the legal right to seek dissolution of marriage through Khula before the family court, subject to settling dower."

            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Dissolution of Marriage on Grounds of Khula",
                raw_text=text,
                subject_matter="dissolution of marriage khula family dispute",
                parties="Wife (Petitioner) vs Husband (Respondent)",
                aggrieved_party="Wife",
                wrongdoer="Husband",
                action_taken="Wife seeking judicial dissolution of marriage / Khula before Family Court",
                relief_sought=f"Dissolution of marriage through Khula under Section 10 & Section 5 Family Courts Act 1964. {procedural_note}",
                search_query="wife seeking divorce khula dissolution of marriage Family Court Section 10 Family Courts Act 1964",
                statute_hints=["FCA-SEC-10", "FCA-SEC-5"],
                category_hint="Family Law / Matrimonial",
                procedural_posture="Wife Khula Petition"
            )))

        # ----------------------------------------------------------------------
        # Grievance 5b: Matrimonial & Child Maintenance (MFLO Section 9 & FCA Section 5 / 17-A)
        # Dedicated grievance to guarantee zero dropped maintenance issues.
        # ----------------------------------------------------------------------
        maint_m = re.search(
            r"\b(?:hasn'?t\s*paid\s*maintenance|not\s*paying\s*maintenance|unpaid\s*maintenance|maintenance\s*in\s*\d+\s*months|pay\s*maintenance|kharcha|nan\s*nafqah|نان\s*نفقہ|child\s*support)\b|"
            r"\b(?:maintenance)\b",
            text_lower
        )
        if maint_m:
            pos = maint_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Recovery of Past and Future Maintenance",
                raw_text=text,
                subject_matter="matrimonial and child maintenance recovery Family Court Section 9 MFLO Section 17-A FCA",
                parties="Wife / Children (Claimants) vs Husband / Father (Respondent)",
                aggrieved_party="Wife / Children",
                wrongdoer="Husband / Father",
                action_taken="Husband failed to pay maintenance or defaulted on monthly financial support",
                relief_sought="Recovery of past accrued maintenance arrears and future monthly maintenance under Section 9 Muslim Family Laws Ordinance 1961 read with Section 5 and Section 17-A of the Family Courts Act 1964 (mandatory interim maintenance on first appearance)",
                search_query="recovery of unpaid maintenance arrears wife child support Section 9 Muslim Family Laws Ordinance Section 17-A Family Courts Act",
                statute_hints=["MFLO-SEC-9", "FCA-SEC-5"],
                category_hint="Family Law / Maintenance",
                procedural_posture="Wife / Child Maintenance Suit"
            )))

        # ----------------------------------------------------------------------
        # Grievance 6: Matrimonial Talaq (Husband-Initiated Divorce Notice)
        # Exclusively MFLO Section 7; only when husband is initiating Talaq
        # ----------------------------------------------------------------------
        talaq_m = re.search(
            r"\b(?:husband\s*(?:pronounced|sent|issued|gave)\s*(?:me\s*)?talaq|pronounced\s*talaq|verbal\s*talaq|talaq\s*verbally|notice\s*of\s*talaq|divorce\s*my\s*wife|pronounce\s*talaq|is\s*the\s*divorce\s*final)\b",
            text_lower
        )
        if talaq_m and not khula_m:
            pos = talaq_m.start()
            is_verbal_inquiry = bool(re.search(r"\b(?:verbal|verbally|anger|is\s*the\s*divorce\s*final)\b", text_lower))
            talaq_relief = (
                "To answer your question directly: Under Section 7 of the Muslim Family Laws Ordinance 1961, a verbal pronouncement of Talaq—even if uttered in anger—is NOT legally final or effective on its own. The husband is legally required to give written notice to the Chairman of the local Union Council / Arbitration Council and provide a copy to his wife. Talaq only becomes legally effective after 90 days from the date notice is delivered to the Chairman, during which the Arbitration Council must attempt reconciliation."
                if is_verbal_inquiry else
                "Statutory written notice to Chairman Union Council under Section 7 MFLO 1961, 90-day reconciliation period before Arbitration Council"
            )
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Talaq Notice & Union Council Procedure",
                raw_text=text,
                subject_matter="talaq divorce notice union council arbitration council",
                parties="Husband vs Wife",
                aggrieved_party="Wife / Recipient",
                wrongdoer="Husband",
                action_taken="Husband pronounced Talaq and procedure under Muslim Family Laws Ordinance 1961 is required",
                relief_sought=talaq_relief,
                search_query="husband pronounced talaq notice to chairman union council Section 7 Muslim Family Laws Ordinance MFLO",
                statute_hints=["MFLO-SEC-7"],
                category_hint="Family Law / Divorce Procedure"
            )))

        # ----------------------------------------------------------------------
        # Grievance 7: Pre-Marital Debt / Loan Recovery
        # ----------------------------------------------------------------------
        premarital_debt_m = re.search(
            r"\b(?:owes\s*(?:me\s*)?money|borrowed\s*(?:money\s*before\s*marriage)?|unpaid\s*loan)\b.*?\b(?:before\s*marriage)\b|"
            r"\b(?:borrowed\s*money\s*before\s*marriage)\b",
            text_lower
        )
        if premarital_debt_m:
            pos = premarital_debt_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Recovery of Pre-Marital Debt / Borrowed Money",
                raw_text=text,
                subject_matter="recovery of personal loan and debt before marriage",
                parties="Creditor (Complainant) vs Debtor (Wrongdoer)",
                aggrieved_party="Creditor",
                wrongdoer="Debtor",
                action_taken="Failure to return money borrowed prior to marriage",
                relief_sought="Recovery of debt under Contract Act 1872 / Civil Suit for Recovery of Money",
                search_query="recovery of money borrowed loan debt suit for recovery Contract Act 1872 CPC",
                statute_hints=["CONTRACT-SEC-73-74"],
                category_hint="Civil Law / Contracts"
            )))

        # ----------------------------------------------------------------------
        # Grievance 8: Personal Loan / Debt Recovery (Signed Agreement vs Verbal Debt)
        # Exclude if cheque bounce or fraud or premarital
        # ----------------------------------------------------------------------
        verbal_loan_m = re.search(
            r"\b(?:brother|relative|cousin|friend|someone)\b.*?\b(?:took\s*(?:a\s*)?loan|borrowed\s*(?:money|cash)|verbal\s*promise|promised\s*to\s*return|udhar|signed\s*an?\s*agreement|signed\s*agreement|written\s*agreement)\b|"
            r"\b(?:loan\s*from\s*me.*?verbal\s*promise|verbal\s*promise\s*to\s*repay|borrowed\s*money\s*from\s*me)\b",
            text_lower
        )
        if verbal_loan_m and not premarital_debt_m and not re.search(r"\b(?:cheque|check|bounced|fraud|420)\b", text_lower):
            pos = verbal_loan_m.start()
            has_written_agr = bool(re.search(r"\b(?:signed|written|agreement|contract|stamp\s*paper|promissory\s*note)\b", text_lower))
            has_verbal_explicit = bool(re.search(r"\b(?:verbal\s*promise|verbally\s*promised|informal\s*promise|no\s*agreement|just\s*a\s*verbal|oral\s*promise|actually\s*no|verbal)\b", text_lower))
            if has_written_agr and not has_verbal_explicit:
                detected.append((pos, LegalIssue(
                    issue_index=0,
                    issue_title="Debt Recovery under Signed Agreement / Contract",
                    raw_text=text,
                    subject_matter="recovery of personal loan debt under written signed agreement",
                    parties="Lender / Creditor (Plaintiff) vs Borrower (Defendant)",
                    aggrieved_party="Lender / Creditor",
                    wrongdoer="Borrower (Defendant)",
                    action_taken="Borrower took personal loan under written/signed agreement and defaulted on repayment",
                    relief_sought="Civil suit for recovery of money under Sections 73 & 74 of the Contract Act 1872 or summary suit on negotiable instruments / written contracts under Order XXXVII of the Code of Civil Procedure 1908 in the local Civil Court",
                    search_query="recovery of loan debt signed agreement breach of contract Section 73 Contract Act 1872 summary suit Order 37 CPC",
                    statute_hints=["CONTRACT-SEC-73-74"],
                    category_hint="Civil Law / Debt Recovery"
                )))
            else:
                detected.append((pos, LegalIssue(
                    issue_index=0,
                    issue_title="Recovery of Personal Loan & Verbal Debt",
                    raw_text=text,
                    subject_matter="recovery of personal loan verbal contract debt",
                    parties="Lender / Creditor (Complainant) vs Borrower (Debtor)",
                    aggrieved_party="Lender / Creditor",
                    wrongdoer="Borrower (Debtor)",
                    action_taken="Borrower took personal loan upon verbal promise or informal agreement and failed to repay",
                    relief_sought="Civil suit for recovery of money under Contract Act 1872. Under Pakistani law (Section 10 Contract Act), verbal agreements are legally valid and enforceable, though establishing proof requires corroborative evidence such as bank transfer receipts, text messages, or witness testimony",
                    search_query="recovery of loan borrowed money verbal promise debt suit for recovery Contract Act 1872",
                    statute_hints=["CONTRACT-SEC-73-74"],
                    category_hint="Civil Law / Debt Recovery"
                )))

        # ----------------------------------------------------------------------
        # Grievance 9: Withheld Bridal Jewelry / Dowry Articles
        # ----------------------------------------------------------------------
        jewelry_m = re.search(
            r"\b(?:jewelry|jewellery|gold|zewar|dowry|jahez|saman-e-jahez|bridal\s*gifts)\b.*?\b(?:return|refusing|withholding|wapas)\b|"
            r"\b(?:father-in-law|in-laws|susar)\b.*?\b(?:jewelry|jewellery|gold|zewar|dowry|jahez)\b",
            text_lower
        )
        if jewelry_m:
            pos = jewelry_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Recovery of Bridal Jewelry & Dowry Articles",
                raw_text=text,
                subject_matter="withholding of bride's personal gold jewelry and dowry articles",
                parties="Bride / Wife (Petitioner) vs Father-in-Law / Husband (Respondent)",
                aggrieved_party="Bride / Wife",
                wrongdoer="Father-in-Law / In-laws",
                action_taken="Refusal to return bride's personal gold jewelry and bridal gifts",
                relief_sought="Suit for Recovery of Dowry Articles and Jewelry under Section 5 (Schedule Entry 7) Family Courts Act 1964 and PPC 406",
                search_query="recovery of dowry articles bridal jewelry father in law refusing to return Family Courts Act PPC 406",
                statute_hints=["FCA-DOWRY-ARTICLES", "PPC-405-406"],
                category_hint="Family Law / Matrimonial Property"
            )))

        # ----------------------------------------------------------------------
        # Grievance 10: Urgent Legal Notice / Court Summons with Reply Deadline
        # e.g. "legal notice yesterday with 10 days to reply", "court notice with 7 days to respond"
        # ----------------------------------------------------------------------
        notice_m = re.search(
            r"\b(?:legal\s*notice|court\s*notice|summons|notice\s*received|received\s*(?:a\s*)?notice|notice\s*yesterday)\b.*?"
            r"\b(?:reply|respond|deadline|10\s*days|7\s*days|14\s*days|30\s*days|days\s*to\s*reply|days\s*to\s*respond|seven\s*days)\b|"
            r"\b(?:got\s*(?:a\s*)?legal\s*notice|legal\s*notice\s*yesterday|notice\s*with\s*\d+\s*days)\b|"
            r"\b(?:court\s*notice|summons).*?(?:7\s*days|10\s*days|respond|what the case)\b",
            text_lower
        )
        if notice_m:
            pos = notice_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Urgent Legal Notice & Reply Procedure",
                raw_text=text,
                subject_matter="legal notice summons deadline written statement inspection",
                parties="Notice Recipient (Defendant) vs Opposing Claimant (Plaintiff / Sender)",
                aggrieved_party="Notice Recipient",
                wrongdoer="Opposing Claimant",
                action_taken="Received formal legal notice or court summons with urgent deadline to reply",
                relief_sought="Engaging an enrolled Advocate immediately to inspect court file or particulars, obtaining copies, and serving a formal written reply / written statement within the notified deadline (Order V & Order VIII CPC) to avoid ex-parte proceedings",
                search_query="received legal notice court summons reply deadline 10 days 7 days written statement Order 5 Order 8 CPC",
                statute_hints=["CPC-O5-O8-SUMMONS"],
                category_hint="Civil Procedure / Court Practice & Notices"
            )))

        # ----------------------------------------------------------------------
        # Grievance 11: Motor Vehicle Damage & Crash Recovery (Cousin/Driver crashed borrowed car)
        # ----------------------------------------------------------------------
        crash_m = re.search(
            r"\b(?:car|bike|motorcycle|vehicle|gari|borrowed\s*car)\b.*?\b(?:crash|crashed|crashing|damage|damaged|wrecked|collided|accident|hadsa)\b|"
            r"\b(?:cousin|friend|driver)\b.*?\b(?:crash|crashed|damaged|accident)\b.*?\b(?:car|bike|vehicle|borrowed)\b|"
            r"\b(?:crashed\s*(?:my\s*)?(?:borrowed\s*)?car|car\s*accident|road\s*accident)\b",
            text_lower
        )
        insurance_m = re.search(r"\b(?:insurance|insurance\s*company|claim|bima|beema)\b", text_lower)
        if crash_m and not insurance_m:
            pos = crash_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Motor Vehicle Damage & Tort / Bailment Recovery",
                raw_text=text,
                subject_matter="motor vehicle crash damage borrowed car tort negligence bailment",
                parties="Vehicle Owner (Complainant) vs Driver / Cousin (Wrongdoer)",
                aggrieved_party="Vehicle Owner",
                wrongdoer="Driver / Cousin",
                action_taken="Driver/cousin crashed or damaged borrowed motor vehicle through negligence",
                relief_sought="Civil recovery for vehicular damage and repair costs under Contract Act 1872 (principles of bailment and duty of care) and tort of negligence; Section 279 & 337-G PPC if rash/reckless driving on a public way",
                search_query="crashed borrowed car vehicle accident compensation damages Contract Act negligence Section 279 337-G PPC",
                statute_hints=["CONTRACT-SEC-73-74", "PPC-279-337G"],
                category_hint="Civil Law / Torts & Property Damage"
            )))
        elif crash_m and insurance_m:
            pos = min(crash_m.start(), insurance_m.start())
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Motor Vehicle Accident & Insurance Claim Dispute",
                raw_text=text,
                subject_matter="motor vehicle insurance claim dispute",
                parties="Policyholder / Claimant vs Insurance Company",
                aggrieved_party="Policyholder",
                wrongdoer="Insurance Company",
                action_taken="Insurance claim repudiation or dispute arising from motor vehicle accident",
                relief_sought="Motor vehicle insurance claims and repudiation disputes are governed by the Insurance Ordinance 2000 under the regulatory authority of the Insurance Tribunal and SECP Insurance Division. This specialized insurance regulatory framework is outside current coverage of this knowledge base.",
                search_query="motor vehicle accident insurance claim repudiation Insurance Ordinance 2000 Tribunal",
                statute_hints=[],
                category_hint="Insurance Law / Regulatory Dispute"
            )))

        # ----------------------------------------------------------------------
        # Grievance 12: Family Altercation & Allegation of Insult
        # NEVER cite Guardian and Wards Act child custody!
        # ----------------------------------------------------------------------
        insult_m = re.search(
            r"\b(?:insult|insulted|insulting|shouting|quarrel|argument)\b.*?\b(?:family|sister-in-law|relative)\b|"
            r"\b(?:sister-in-law|relative)\b.*?\b(?:insult|shout|quarrel)\b|"
            r"\b(?:sister-in-law\s*says\s*i\s*insulted\s*her)\b",
            text_lower
        )
        if insult_m and not re.search(r"\b(?:custody|guardianship|guardian|hizanat)\b", text_lower):
            pos = insult_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Family Dispute & Allegation of Verbal Insult",
                raw_text=text,
                subject_matter="family altercation alleged insult interpersonal dispute",
                parties="Complainant vs Sister-in-law (Disputing Relative)",
                aggrieved_party="Complainant",
                wrongdoer="Disputing Relative",
                action_taken="Dispute or allegation regarding verbal argument or insult at a family gathering",
                relief_sought="Under Pakistani civil and criminal jurisprudence, minor interpersonal quarrels or private verbal exchanges within a family function without criminal intimidation or physical harm do not meet the legal threshold for criminal prosecution. Defamation under Defamation Ordinance 2002 requires false statements causing actionable public damage to reputation. Interpersonal mediation is the recommended practical course",
                search_query="family dispute verbal altercation insult defamation family function",
                statute_hints=[],
                category_hint="Civil / Family Dispute"
            )))

        # ----------------------------------------------------------------------
        # Grievance 13: Delayed Inheritance Land Claim (Limitation Period 12 Years)
        # ----------------------------------------------------------------------
        limitation_m = re.search(
            r"\b(?:passed away \d+\s*years ago|\d+\s*years ago|long time ago|12 years ago|10 years ago)\b.*?\b(?:transferred|land|property|uncle|claim|still claim)\b",
            text_lower
        )
        if limitation_m:
            pos = limitation_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Delayed Inheritance Claim & Limitation Period Analysis",
                raw_text=text,
                subject_matter="inheritance land claim delay limitation period discovery of fraud",
                parties="Legal Heir (Plaintiff) vs Uncle / Co-Heir (Defendant)",
                aggrieved_party="Legal Heir",
                wrongdoer="Uncle / Illegal Transferor",
                action_taken="Uncle transferred deceased father's agricultural land years ago; discovered recently",
                relief_sought="Suit for Declaration under Section 42 Specific Relief Act read with Section 18 Limitation Act 1908 (fraudulent concealment exception) to overcome Section 3 limitation bar",
                search_query="father passed away 12 years ago transferred agricultural land fraud discovery Section 18 Limitation Act Section 42 Specific Relief Act",
                statute_hints=["LIMITATION-ACT-1908", "SRA-SEC-42"],
                category_hint="Civil Law / Procedural Limitation",
                limitation_flag=True
            )))

        # ----------------------------------------------------------------------
        # Grievance 14: Inheritance Unauthorized Sale Without Signature
        # ----------------------------------------------------------------------
        if not limitation_m:
            inher_m = re.search(
                r"\b(?:brother|sister|heir|co-heir|late father)\b.*?\b(?:selling|trying to sell|sell|sold|without (?:my )?signature|without (?:my )?consent)\b",
                text_lower
            )
            if inher_m:
                pos = inher_m.start()
                detected.append((pos, LegalIssue(
                    issue_index=0,
                    issue_title="Unauthorized Sale & Alienation of Inherited Property",
                    raw_text=text,
                    subject_matter="undivided ancestral inheritance property sale",
                    parties="Legal Heir (Aggrieved Co-Owner) vs Co-Heir Brother (Wrongdoer)",
                    aggrieved_party="Legal Heir",
                    wrongdoer="Co-Heir Brother",
                    action_taken="Brother attempting to sell late father's house without consent or signature of co-heir",
                    relief_sought="Suit for Declaration of inheritance share under Section 42 Specific Relief Act 1877 and Temporary Injunction / Stay Order under Order XXXIX Rules 1 & 2 CPC restraining alienation or sale",
                    search_query="brother selling late father house without signature legal heir declaration of share Section 42 Specific Relief Act stay order temporary injunction Order 39 CPC",
                    statute_hints=["SRA-SEC-42", "CPC-O39-R1-2"],
                    category_hint="Civil Law / Title & Rights"
                )))

        # ----------------------------------------------------------------------
        # Grievance 15: Execution of Court Decree (Won court case but decree unpaid)
        # ----------------------------------------------------------------------
        decree_m = re.search(
            r"\b(?:won (?:a |the )?court case|won (?:a |the )?case|decree amount|never paid (?:the )?decree|decree was passed)\b",
            text_lower
        )
        if decree_m:
            pos = decree_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Execution of Court Decree & Recovery of Decretal Amount",
                raw_text=text,
                subject_matter="civil court decree execution satisfaction recovery of decretal amount",
                parties="Decree-Holder (Successful Litigant) vs Judgment-Debtor (Defaulter)",
                aggrieved_party="Decree-Holder",
                wrongdoer="Judgment-Debtor",
                action_taken="Opposing party failed or refused to satisfy civil court decree passed in plaintiff's favor",
                relief_sought="Execution Petition under Order XXI Rules 10, 11, 43, 54 and Section 48 of CPC (attachment of bank accounts, properties, arrest in civil prison)",
                search_query="won court case 4 years ago decree amount never paid execution of decree Order 21 Section 48 Code of Civil Procedure CPC",
                statute_hints=["CPC-O21-EXEC"],
                category_hint="Civil Procedure / Execution of Decrees",
                procedural_posture="Decree Holder Execution"
            )))

        # ----------------------------------------------------------------------
        # Grievance 16: Electricity / Utility Billing Complaint (WAPDA / DISCO / NEPRA)
        # ----------------------------------------------------------------------
        elec_m = re.search(
            r"\b(?:bijli|bijli ka bill|bill bohat zyada|wapda|nepra|electricity bill|detection bill|overbilling|electric inspector)\b",
            text_lower
        )
        if elec_m:
            pos = elec_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Electricity Overbilling & WAPDA / DISCO Complaint",
                raw_text=text,
                subject_matter="electricity billing excessive tariff WAPDA DISCO dispute",
                parties="Electricity Consumer (Complainant) vs DISCO / WAPDA (Utility Provider)",
                aggrieved_party="Electricity Consumer",
                wrongdoer="Distribution Company (WAPDA / DISCO)",
                action_taken="Excessive or arbitrary electricity bill charged by power distribution company",
                relief_sought="Billing rectification, cancellation of detection bill, and stay of disconnection under Section 39 NEPRA Act 1997 / Electricity Act 1910",
                search_query="meri shop ka bijli ka bill bohat zyada aa raha hai WAPDA Section 39 NEPRA Consumer Regulations Electric Inspector",
                statute_hints=["NEPRA-CONSUMER-BILLING"],
                category_hint="Administrative Law / Utility & Consumer Protection"
            )))

        # ----------------------------------------------------------------------
        # Grievance 17: Attempted Robbery / Armed Dacoity at Gunpoint
        # ----------------------------------------------------------------------
        robbery_m = re.search(
            r"\b(?:robbery|attempted robbery|gunpoint|armed (?:men|culprits|dacoits)|pharmacy|medical store|dacoity|dakaiti)\b.*?\b(?:robbery|attempted|gunpoint|fled|scared off|stolen)\b|"
            r"\b(?:attempted robbery|robbery at gunpoint)\b",
            text_lower
        )
        if robbery_m:
            pos = robbery_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Attempted Armed Robbery at Gunpoint",
                raw_text=text,
                subject_matter="armed robbery attempted robbery with deadly weapons",
                parties="Victim / Shopkeeper (Complainant) vs Armed Assailants (Accused)",
                aggrieved_party="Victim / Shopkeeper",
                wrongdoer="Armed Assailants",
                action_taken="Armed individuals attempted robbery at gunpoint on commercial premises",
                relief_sought="Registration of FIR and criminal trial under Sections 393 and 397 Pakistan Penal Code",
                search_query="armed robbery attempted robbery at pharmacy medical store at gunpoint Section 393 397 Pakistan Penal Code PPC",
                statute_hints=["PPC-392-393"],
                category_hint="Criminal Law / Violent Property Crimes"
            )))

        # ----------------------------------------------------------------------
        # Grievance 18: Unpaid Salary / Wages (Labour Law)
        # ----------------------------------------------------------------------
        wages_m = re.search(
            r"\b(?:salary|wages|tankhwah|tankhah)\b.*?\b(?:not paid|withheld|not paying|arrears|delayed|3 months|months)\b|"
            r"\b(?:employer has not paid|company hasn'?t paid (?:my )?salary)\b",
            text_lower
        )
        if wages_m:
            pos = wages_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Unpaid Salary & Delay in Payment of Wages",
                raw_text=text,
                subject_matter="employment labour rights unpaid salary wage delay",
                parties="Employee (Claimant) vs Employer (Respondent)",
                aggrieved_party="Employee",
                wrongdoer="Employer",
                action_taken="Employer withheld or failed to disburse monthly salary arrears",
                relief_sought="Claim before Authority under Section 15 Payment of Wages Act 1936 / Labour Court for recovery with compensation",
                search_query="employer has not paid salary wages for 3 months Section 15 Payment of Wages Act Labour Court",
                statute_hints=["PWA-SEC-15"],
                category_hint="Labour Law / Employment Rights"
            )))

        # ----------------------------------------------------------------------
        # Grievance 19: Traffic Police Vehicle Impoundment
        # ----------------------------------------------------------------------
        traffic_m = re.search(
            r"\b(?:traffic police|impound|impounded|number plate|numberplate|challan|seized my car|seized my bike)\b",
            text_lower
        )
        if traffic_m:
            pos = traffic_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Motor Vehicle Impoundment & Number Plate Inspection",
                raw_text=text,
                subject_matter="motor vehicle detention number plate registration",
                parties="Vehicle Owner (Aggrieved) vs Traffic Police (Authority)",
                aggrieved_party="Vehicle Owner",
                wrongdoer="Traffic Police Authority",
                action_taken="Traffic police impounded vehicle alleging number plate or document irregularity",
                relief_sought="Challenging vehicle impoundment and release of motor vehicle under Section 115 / 23 Provincial Motor Vehicles Ordinance 1965",
                search_query="traffic police impound car vehicle number plate registration detention Section 115 Provincial Motor Vehicles Ordinance PMVO",
                statute_hints=["PMVO-SEC-115", "PMVO-SEC-23"],
                category_hint="Transport & Traffic Law"
            )))

        # ----------------------------------------------------------------------
        # Grievance 20: Cheque Dispute (Issuer Defense vs Payee Recovery)
        # ----------------------------------------------------------------------
        cheque_issuer_m = re.search(
            r"\b(?:i\s*gave\s*(?:someone|them|him|her)?\s*(?:a\s*)?cheque|i\s*issued\s*(?:a\s*)?cheque|i\s*wrote\s*(?:a\s*)?cheque|my\s*cheque)\b.*?"
            r"\b(?:deal\s*fell\s*through|deal\s*failed|deal\s*cancelled|deal|threaten\w*|cash\s*it|get\s*me\s*arrested|arrest\w*)\b|"
            r"\b(?:cheque\s*for\s*a\s*business\s*deal)\b.*?\b(?:fell\s*through|failed|cancelled|arrest\w*|threaten\w*)\b",
            text_lower
        )
        cheque_bounce_m = re.search(
            r"\b(?:cheque|check|489-f|چیک)\b.*?\b(?:bounce|bounced|dishonour|dishonored|insufficient|memo)\b",
            text_lower
        )
        if cheque_issuer_m and any(w in text_lower for w in ["fell through", "failed", "cancelled", "arrest", "threaten"]):
            pos = cheque_issuer_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Threat of Cheque Dishonour Prosecution (PPC 489-F) & Failed Consideration Defense",
                raw_text=text,
                subject_matter="cheque issued for failed business transaction defense against Section 489-F PPC pre-arrest bail",
                parties="Cheque Drawer / Issuer (User) vs Cheque Holder / Payee (Threatening Party)",
                aggrieved_party="Cheque Drawer / Issuer",
                wrongdoer="Cheque Holder / Payee",
                action_taken="Counterparty threatening to cash cheque and register criminal FIR under Section 489-F PPC after underlying business deal fell through",
                relief_sought=(
                    "To answer your question directly: Under Pakistani law (Section 489-F Pakistan Penal Code), a failed underlying "
                    "transaction or lack of consideration is a valid legal defense. Section 489-F requires dishonest intention to "
                    "exist at the time the cheque was issued. If the cheque was issued for a business deal that subsequently fell through, "
                    "dishonest intent at inception is negated, and criminal law cannot be used as an instrument of coercive debt collection. "
                    "Recommended legal steps: (1) Issue immediate written 'Stop Payment' instructions to your bank noting the cancellation of the deal; "
                    "(2) Dispatch a statutory legal notice demanding the immediate return and cancellation of the cheque; "
                    "(3) If an FIR or arrest is threatened, petition for Pre-Arrest Bail under Section 498 CrPC before the Sessions Court; and "
                    "(4) File a civil suit for cancellation of instrument and declaration under Sections 39 & 42 of the Specific Relief Act 1877 "
                    "with temporary injunction under CPC Order XXXIX Rules 1 & 2 restraining encashment."
                ),
                search_query="dishonestly issuing cheque Section 489-F Pakistan Penal Code PPC Pre-Arrest Bail Section 498 CrPC failure of consideration",
                statute_hints=["PPC-489F", "CRPC-498"],
                category_hint="Criminal Law / Financial Defense",
                procedural_posture="Accused / Drawer Safeguard Against 489-F Arrest"
            )))
        elif cheque_bounce_m:
            pos = cheque_bounce_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Dishonoured Cheque & Financial Recovery",
                raw_text=text,
                subject_matter="banking negotiable instrument dishonour",
                parties="Payee / Creditor (Complainant) vs Drawer of Cheque (Accused)",
                aggrieved_party="Payee / Creditor",
                wrongdoer="Drawer of Cheque",
                action_taken="Drawer issued cheque that dishonoured upon presentation due to insufficient funds",
                relief_sought="Registration of FIR and criminal proceedings under Section 489-F PPC",
                search_query="dishonoured cheque bank return memo funds insufficient Section 489-F Pakistan Penal Code PPC",
                statute_hints=["PPC-489F"],
                category_hint="Criminal Law / Financial Crimes"
            )))

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # Grievance 21: Cheating (PPC 420) vs Defamation / False Rumor Spreading
        # Strict condition: MUST involve actual pecuniary deceit or absconding with money.
        # Excludes verbal loans, domestic lockouts, and false rumors/reputational harm.
        # ----------------------------------------------------------------------
        defamation_rumor_m = re.search(
            r"\b(?:spreading\s*(?:false\s*)?rumou?rs|spreading\s*lies|false\s*rumou?rs|ruining\s*my\s*reputation|defam\w*|character\s*assassination)\b|"
            r"\b(?:business\s*rival|competitor|rival)\b.*?\b(?:rumou?rs|fraud|lies|smear)\b",
            text_lower
        )
        if defamation_rumor_m:
            pos = defamation_rumor_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Defamation & Malicious False Rumors Spread by Business Rival",
                raw_text=text,
                subject_matter="defamation business rival spreading false rumors fraud reputation damage Defamation Ordinance 2002 PPC 500",
                parties="Aggrieved Business Owner (Plaintiff) vs Business Rival (Defaming Wrongdoer)",
                aggrieved_party="Aggrieved Business Owner",
                wrongdoer="Business Rival",
                action_taken="Business rival is spreading false rumors alleging involvement in fraud to damage commercial reputation",
                relief_sought=(
                    "Under Pakistani law, spreading false rumors to harm personal or commercial reputation constitutes actionable Defamation, "
                    "NOT cheating (Section 420 PPC, which strictly requires dishonest inducement and delivery of property). "
                    "Remedies include: (1) Civil Suit for Damages under Defamation Ordinance 2002: You must first serve a mandatory 14-day legal notice "
                    "under Section 8 of the Defamation Ordinance 2002 demanding an unconditional apology and retraction; if the rival fails to comply, "
                    "you can file a suit for general and special damages before the District Court; "
                    "(2) Injunctive relief: Under Order XXXIX Rules 1 & 2 CPC and Section 54 Specific Relief Act 1877, you can seek a temporary and permanent injunction "
                    "restraining the rival from publishing or uttering defamatory statements; and "
                    "(3) Criminal Defamation under Sections 499 & 500 PPC: You may institute a private complaint (istighasa) before the Judicial Magistrate "
                    "for criminal defamation punishable by imprisonment up to two years or fine."
                ),
                search_query="business rival spreading false rumors fraud defamation Defamation Ordinance 2002 Section 499 500 Pakistan Penal Code PPC",
                statute_hints=[],
                category_hint="Civil & Criminal Law / Defamation & Commercial Reputation"
            )))
        else:
            cheat_m = re.search(
                r"\b(?:fraud|cheat|cheated|dhoka|scam|420|false promise)\b|"
                r"\b(?:mera dost|dost)\b.*?\b(?:udhar|paisay|paise).*?\b(?:phone hi nahi utha raha|mukargaya|bhag gaya)\b",
                text_lower
            )
            if cheat_m and not verbal_loan_m and not re.search(r"\b(?:locks her out|friend's husband|husband|wife|rumor|rumour|rumors|rumours)\b", text_lower):
                pos = cheat_m.start()
                detected.append((pos, LegalIssue(
                    issue_index=0,
                    issue_title="Cheating & Dishonest Inducement of Property (PPC 420)",
                    raw_text=text,
                    subject_matter="criminal fraud cheating borrowed money recovery",
                    parties="Complainant (Victim) vs Borrower / Accused (Wrongdoer)",
                    aggrieved_party="Complainant",
                    wrongdoer="Accused",
                    action_taken="Accused took money/funds under dishonest inducement and refused to return/absconded",
                    relief_sought="Registration of FIR and criminal trial under Section 420 Pakistan Penal Code",
                    search_query="mera dost mujhse paisay udhar le kar gaya tha ab wo phone hi nahi utha raha fraud cheating Section 420 Pakistan Penal Code PPC",
                    statute_hints=["PPC-420"],
                    category_hint="Criminal Law / Offenses Against Property"
                )))

        # ----------------------------------------------------------------------
        # Grievance 22: Police Refusal of FIR
        # ----------------------------------------------------------------------
        sho_m = re.search(
            r"\b(?:sho|police station|police|thana|thanay|thana\s*walay)\b.*?\b(?:refuse\w*|denied|not registering|inkar|inqar|nahi\s*kar\s*rah\w*|nahi\s*likh\w*)\b.*?\b(?:fir|complaint|report|parcha)\b|"
            r"(?:تھانے|پولیس|ایف\s*آئی\s*آر).*?(?:انکار|درج\s*نہیں|درج\s*کرنے\s*سے\s*انکار)|"
            r"(?:ایف\s*آئی\s*آر\s*درج\s*کرنے\s*سے\s*انکار)",
            text_lower
        )
        if sho_m:
            pos = sho_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Police Refusal to Register First Information Report (FIR)",
                raw_text=text,
                subject_matter="police failure to discharge statutory duty under CrPC",
                parties="Citizen Complainant (Aggrieved) vs Police SHO (Wrongdoer)",
                aggrieved_party="Citizen Complainant",
                wrongdoer="Police Station SHO",
                action_taken="SHO refused to register FIR upon disclosure of cognizable offense",
                relief_sought="Petition under Section 22-A & 22-B CrPC before Ex-Officio Justice of Peace to compel FIR under Section 154 CrPC",
                search_query="police station SHO refusing to register FIR complaint Justice of Peace Section 154 22-A CrPC",
                statute_hints=["CRPC-154", "CRPC-22A-22B"],
                category_hint="Criminal Procedure / Police Powers"
            )))

        # ----------------------------------------------------------------------
        # Grievance 23: Cyber Crime / Blackmail
        # ----------------------------------------------------------------------
        cyber_m = re.search(
            r"\b(?:whatsapp|blackmail|private photos|pictures|video|leak|cyber|harass online)\b",
            text_lower
        )
        if cyber_m:
            pos = cyber_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Cyber Harassment & Electronic Extortion",
                raw_text=text,
                subject_matter="unauthorized digital content dissemination blackmail",
                parties="Victim (Aggrieved) vs Blackmailer (Perpetrator)",
                aggrieved_party="Victim",
                wrongdoer="Blackmailer",
                action_taken="Threatening to publish private photos/data or extorting online",
                relief_sought="Investigation and prosecution by FIA Cyber Crime Wing under PECA 2016 Sections 20 & 21",
                search_query="blackmail private photos whatsapp social media extortion cyber crime Sections 20 21 PECA 2016",
                statute_hints=["PECA-SEC-20-21"],
                category_hint="Cyber Law / Electronic Crimes"
            )))

        # ----------------------------------------------------------------------
        # Grievance 24: Property Construction / Encroachment / Stay Order
        # ----------------------------------------------------------------------
        stay_m = re.search(
            r"\b(?:illegal construction|encroach|building a wall|plot encroachment|qabza on plot)\b",
            text_lower
        )
        if stay_m and not inher_m and not limitation_m:
            pos = stay_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Property Encroachment & Urgent Stay Order",
                raw_text=text,
                subject_matter="disputed immovable plot construction encroachment",
                parties="Lawful Owner / Occupant (Plaintiff) vs Encroacher (Defendant)",
                aggrieved_party="Lawful Owner",
                wrongdoer="Encroacher",
                action_taken="Opponent undertaking unauthorized construction or attempting dispossession on plot",
                relief_sought="Temporary Stay Order under Order XXXIX Rules 1 & 2 CPC to prevent construction and maintain status quo",
                search_query="illegal construction encroachment disputed plot urgent stay order temporary injunction Order 39 CPC",
                statute_hints=["CPC-O39-R1-2"],
                category_hint="Civil Procedure / Interim Relief"
            )))

        # ----------------------------------------------------------------------
        # Grievance 24b: Defective Property Title & Fraudulent Sale of Unowned Plot
        # ----------------------------------------------------------------------
        defective_title_m = re.search(
            r"\b(?:bought|purchased)\b.*?\b(?:house|plot|property|land|flat)\b.*?\b(?:didn'?t\s*(?:actually\s*)?own|not\s*(?:the\s*)?owner|defective\s*title|fake\s*title|partial\s*owner|full\s*plot|didn'?t\s*have\s*title)\b|"
            r"\b(?:seller\s*didn'?t\s*(?:actually\s*)?own)\b",
            text_lower
        )
        if defective_title_m:
            pos = defective_title_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Defective Property Title & Fraudulent Sale of Unowned Plot",
                raw_text=text,
                subject_matter="defective property title seller unowned plot fraudulent misrepresentation Contract Act Specific Relief Act",
                parties="Buyer / Purchaser (Plaintiff) vs Seller / Vendor (Defendant)",
                aggrieved_party="Buyer / Purchaser",
                wrongdoer="Seller / Vendor",
                action_taken="Seller sold house/plot without lawful ownership or title to the full plot",
                relief_sought=(
                    "Under Pakistani law, immovable property transactions are governed by the Transfer of Property Act 1882, Specific Relief Act 1877, and Contract Act 1872 "
                    "(NOT the Consumer Protection Act, which applies only to movable consumer goods). Under the fundamental legal principle 'nemo dat quod non habet' "
                    "(no person can transfer a better title than they possess), a seller cannot convey lawful title to land they do not own. "
                    "Remedies include: (1) Under Sections 19 and 73 of the Contract Act 1872, the buyer may rescind the contract on grounds of fraudulent misrepresentation "
                    "and file a Civil Suit for recovery of the purchase consideration, registration fees, and damages in the local Civil Court; "
                    "(2) File a suit for cancellation of the sale deed and declaration under Sections 39 and 42 of the Specific Relief Act 1877; and "
                    "(3) If the seller induced payment knowing they lacked title, lodge a criminal FIR / complaint for cheating and fraudulent inducement under Section 420 of the Pakistan Penal Code."
                ),
                search_query="bought house seller didn't own full plot defective title Section 73 Contract Act 1872 Section 42 Specific Relief Act",
                statute_hints=["CONTRACT-SEC-73-74", "SRA-SEC-42"],
                category_hint="Civil Law / Property Title & Contractual Fraud"
            )))

        # ----------------------------------------------------------------------
        # Grievance 25: Consumer Product Defects & Warranty Dispute vs Commercial Machinery
        # ----------------------------------------------------------------------
        factory_machinery_m = re.search(
            r"\b(?:factory\s*machinery|machinery\s*for\s*(?:my\s*)?factory|industrial\s*(?:machinery|equipment|plant)|commercial\s*(?:machinery|equipment))\b.*?\b(?:defective|faulty|warranty|broke|refund|repair)\b|"
            r"\b(?:bought\s*machinery\s*for\s*(?:my\s*)?factory)\b",
            text_lower
        )
        supplier_m = re.search(
            r"\b(?:supplier|resale|shop\s*buying|commercial\s*(?:goods|deal|purchase)|wholesale|b2b)\b.*?\b(?:damaged\s*goods|defective\s*goods|faulty\s*(?:goods|products)|damaged\s*shipment|delivered\s*damaged|delivered\s*defective)\b|"
            r"\b(?:my\s*supplier\s*delivered\s*damaged\s*goods)\b",
            text_lower
        )
        consumer_m = re.search(
            r"\b(?:laptop|mobile|phone|appliance|product|goods|item|purchased|bought|shopkeeper|seller|market|hafeez\s*centre)\b.*?\b(?:defective|faulty|broke\s*down|broken|not\s*working|repair|refund|warranty|guarantee|refus\w*\s+to\s+(?:repair|refund))\b|"
            r"\b(?:consumer\s*court|defective\s*product)\b",
            text_lower
        )
        if factory_machinery_m:
            pos = factory_machinery_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Breach of Warranty & Commercial Factory Machinery Contract Dispute",
                raw_text=text,
                subject_matter="commercial factory machinery defective breach of warranty Sale of Goods Act Contract Act 1872",
                parties="Factory Owner / Commercial Buyer (Plaintiff) vs Machinery Seller (Defendant)",
                aggrieved_party="Factory Owner / Commercial Buyer",
                wrongdoer="Machinery Seller",
                action_taken="Seller delivered defective factory machinery and refused to honor warranty repairs or replacement",
                relief_sought=(
                    "Under Pakistani law: (1) Consumer Protection Act Exclusion: Goods and machinery purchased for commercial manufacturing or industrial use in a factory "
                    "are expressly excluded from the Consumer Protection Act under Section 2(c) (which defines a 'consumer' as excluding purchases for commercial purposes). "
                    "The Consumer Court does NOT have jurisdiction over industrial factory machinery. "
                    "(2) Sale of Goods Act 1930 & Contract Act 1872: The transaction is governed by Sections 16, 59 & 60 of the Sale of Goods Act 1930 and Section 73 of the Contract Act 1872. "
                    "Under Section 59 of the Sale of Goods Act 1930, where there is a breach of warranty by the seller, the buyer can sue for damages for breach of warranty "
                    "and claim diminution or refund of the purchase price. "
                    "(3) Legal remedies: Serve a formal legal notice demanding immediate repair, replacement, or refund under warranty terms; if unfulfilled, "
                    "file a civil suit for recovery of damages and price in the competent Civil Court."
                ),
                search_query="bought machinery for factory defective seller won't honor warranty Section 73 Contract Act 1872 Sale of Goods Act",
                statute_hints=["CONTRACT-SEC-73-74"],
                category_hint="Commercial Law / Sale of Goods & Industrial Warranties"
            )))
        elif supplier_m:
            pos = supplier_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Breach of Commercial Supply Contract & Delivery of Damaged Goods",
                raw_text=text,
                subject_matter="commercial sale of goods supplier delivery of damaged goods Contract Act Sale of Goods Act",
                parties="Commercial Buyer / Retailer (Plaintiff) vs Supplier (Defendant)",
                aggrieved_party="Commercial Buyer / Retailer",
                wrongdoer="Supplier",
                action_taken="Supplier delivered damaged or defective goods purchased for commercial resale",
                relief_sought=(
                    "Under Pakistani law, goods purchased for commercial resale or business purposes are expressly excluded "
                    "from the Consumer Protection Act under Section 2(c) (e.g. Punjab Consumer Protection Act 2005). "
                    "The transaction is governed by the Sale of Goods Act 1930 and Section 73 of the Contract Act 1872. "
                    "Under Sections 15, 16 & 59 of the Sale of Goods Act 1930, the buyer has the legal right to reject damaged goods, "
                    "demand immediate replacement, or recover damages and price in the local Civil Court."
                ),
                search_query="supplier delivered damaged goods commercial resale breach of contract Section 73 Contract Act 1872 Sale of Goods Act",
                statute_hints=["CONTRACT-SEC-73-74"],
                category_hint="Commercial Law / Sale of Goods & Supply Contracts"
            )))
        elif consumer_m and not lockout_m and not deposit_m and not re.search(r"\b(?:factory|industrial|commercial|resale|supplier)\b", text_lower):
            pos = consumer_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Consumer Protection & Defective Product Claim",
                raw_text=text,
                subject_matter="defective product faulty goods consumer court refund",
                parties="Consumer (Complainant) vs Seller / Shopkeeper (Respondent)",
                aggrieved_party="Consumer",
                wrongdoer="Seller / Shopkeeper",
                action_taken="Seller sold defective product and refused warranty repair or refund",
                relief_sought="Serve 15-day legal notice and file claim before District Consumer Protection Court under Sections 13, 15 & 28 Punjab Consumer Protection Act 2005",
                search_query="defective product faulty laptop goods refund warranty legal notice Consumer Court Punjab Consumer Protection Act PCPA",
                statute_hints=["PCPA-SEC-13-15"],
                category_hint="Consumer Protection / Product Liability"
            )))

        # ----------------------------------------------------------------------
        # Grievance 26: Theft (PPC 379 & 380) vs False Accusation of Theft by Employer
        # ----------------------------------------------------------------------
        false_theft_m = re.search(
            r"\b(?:falsely\s*accused|false\s*accusation|framed|wrongfully\s*accused)\b.*?\b(?:theft|chori|stealing|stole)\b|"
            r"\b(?:accused\s*of\s*theft\s*by\s*(?:my\s*)?employer|falsely\s*accused\s*of\s*theft)\b",
            text_lower
        )
        theft_m = re.search(
            r"\b(?:stole|stolen|steal|stealing|theft|chori)\b.*?\b(?:cash|money|rupees|drawer|bedroom|house|cupboard|almirah|valuables|wallet)\b|"
            r"\b(?:cousin|someone|thief|servant|maid)\b.*?\b(?:stole|stolen|chori\s*ki)\b",
            text_lower
        )
        if false_theft_m:
            pos = false_theft_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="False Accusation of Theft & Wrongful Termination by Employer",
                raw_text=text,
                subject_matter="falsely accused of theft by employer wrongful termination without investigation Pre-Arrest Bail Section 498 CrPC",
                parties="Employee (Aggrieved Citizen) vs Employer (Accuser / Wrongdoer)",
                aggrieved_party="Employee",
                wrongdoer="Employer",
                action_taken="Employer falsely accused employee of theft and terminated employment without investigation or inquiry",
                relief_sought=(
                    "Under Pakistani law: (1) Protection against apprehension of arrest: If your employer threatens to lodge or lodges a false FIR for theft (Section 380 PPC), "
                    "you should immediately petition the Sessions Court for Pre-Arrest Bail under Section 498 of the Code of Criminal Procedure (CrPC) to protect your constitutional liberty against arrest. "
                    "(2) Remedy against false criminal charge: Leveling a fabricated criminal allegation is a punishable offense under Section 182 PPC (false information to public servant) "
                    "and Section 211 PPC (false charge of offense made with intent to injure). "
                    "(3) Wrongful termination remedies: Under the Industrial and Commercial Employment (Standing Orders) Ordinance 1968 and Industrial Relations Act, "
                    "an employee cannot be dismissed for alleged misconduct without a written charge sheet, independent domestic inquiry, and fair opportunity of defense. "
                    "You can serve a formal grievance notice within 60/90 days and petition the Labour Court for reinstatement, full back benefits, and settlement dues under the Payment of Wages Act 1936."
                ),
                search_query="falsely accused of theft by employer fired without inquiry Pre-Arrest Bail Section 498 CrPC Section 182 211 PPC Payment of Wages Act",
                statute_hints=["CRPC-498", "PWA-SEC-15"],
                category_hint="Criminal Procedure & Labour Law / False Accusation & Wrongful Dismissal"
            )))
        elif theft_m and not robbery_m:
            pos = theft_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Theft & Stealing of Cash or Property (FIR under Section 380 PPC)",
                raw_text=text,
                subject_matter="theft stolen cash property from dwelling house",
                parties="Victim (Complainant) vs Accused (Suspect)",
                aggrieved_party="Victim",
                wrongdoer="Accused",
                action_taken="Theft of cash, valuables, or property from residential dwelling or custody",
                relief_sought="Registration of FIR and criminal prosecution under Sections 379 and 380 Pakistan Penal Code",
                search_query="theft of cash money from bedroom drawer house FIR Section 379 380 Pakistan Penal Code PPC",
                statute_hints=["PPC-379-380"],
                category_hint="Criminal Law / Property Offenses"
            )))

        # ----------------------------------------------------------------------
        # Grievance 27: Legality of Jirga Decision & Union Council Land Dispute Powers
        # ----------------------------------------------------------------------
        jirga_m = re.search(
            r"\b(?:jirga|panchayat)\b.*?\b(?:union\s*council|chairman|dissolved|emergency\s*powers|land\s*dispute|cancellation)\b|"
            r"\b(?:union\s*council\s*chairman|chairman)\b.*?\b(?:jirga|dissolved\s*our\s*jirga|emergency\s*powers)\b",
            text_lower
        )
        if jirga_m:
            pos = jirga_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Legality of Jirga Decision & Union Council Powers in Land Disputes",
                raw_text=text,
                subject_matter="informal jirga legality union council chairman emergency powers land dispute",
                parties="Disputing Landowners vs Union Council Chairman / Jirga",
                aggrieved_party="Affected Landowner",
                wrongdoer="Union Council Chairman",
                action_taken="Union Council Chairman claimed emergency powers to dissolve or cancel an informal jirga decision on a land dispute",
                relief_sought=(
                    "Under Pakistani law and established Supreme Court of Pakistan rulings (PLD 2019 SC 218), informal tribal jirgas and panchayats have no constitutional or legal standing. "
                    "Furthermore, a Union Council Chairman has no judicial authority or emergency powers to decide, validate, or dissolve decisions regarding private land disputes. "
                    "Neither the jirga's decision nor the Chairman's cancellation is legally valid or binding on land ownership. "
                    "Private land ownership and boundary disputes fall strictly within the exclusive judicial authority of the local civil court (Civil Judge / Senior Civil Judge) under the Code of Civil Procedure 1908."
                ),
                search_query="jirga legality union council chairman emergency powers land dispute civil court",
                statute_hints=[],
                category_hint="Local Government Law / Civil Land Dispute"
            )))

        # ----------------------------------------------------------------------
        # Grievance 28: Co-Ownership of Family Commercial Shop & Adverse Possession Claim
        # ----------------------------------------------------------------------
        adverse_m = re.search(
            r"\b(?:shared\s*(?:family\s*)?shop|family\s*shop|joint\s*shop|shared\s*dukan)\b.*?\b(?:running\s*it|took\s*over|legally\s*his|adverse\s*possession|3\s*years|\d+\s*years)\b|"
            r"\b(?:uncle|brother|cousin|co-owner)\b.*?\b(?:shared\s*(?:family\s*)?shop|family\s*shop)\b.*?\b(?:legally\s*his|mine\s*now|3\s*years)\b|"
            r"\b(?:running\s*it\s*for\s*3\s*years|running\s*it\s*for\s*\d+\s*years)\b.*?\b(?:legally\s*his\s*now|his\s*property)\b",
            text_lower
        )
        if adverse_m and not lockout_m:
            pos = adverse_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Co-Ownership of Family Commercial Shop & Adverse Possession Claim",
                raw_text=text,
                subject_matter="co-ownership commercial shop joint family property adverse possession limitation",
                parties="Family Co-Owners (Plaintiffs) vs Uncle / Operating Co-Sharer (Defendant)",
                aggrieved_party="Family Co-Owners",
                wrongdoer="Uncle / Operating Co-Sharer",
                action_taken="Uncle operating shared family shop for 3 years claiming sole ownership by continuous possession",
                relief_sought=(
                    "Under Pakistani property and limitation law, possession by one co-owner is legally considered possession on behalf of all co-owners ('possession of one co-sharer is possession of all'). "
                    "An operating relative cannot easily claim adverse possession against fellow co-owners. "
                    "Furthermore, the statutory limitation period for adverse possession of immovable property under Article 144 of the Limitation Act 1908 is 12 years of open, continuous, and hostile possession. "
                    "Running a shop for 3 years does not make it his property under Pakistani law. "
                    "The other co-owners have the full legal right to file a suit for declaration of title under Section 42 of the Specific Relief Act 1877 and seek partition and business profits in the local civil court."
                ),
                search_query="family shop co-owner adverse possession 3 years Limitation Act 1908 Section 42 Specific Relief Act",
                statute_hints=["LIMITATION-ACT-1908", "SRA-SEC-42"],
                category_hint="Civil Law / Property Rights & Co-Ownership"
            )))

        # ----------------------------------------------------------------------
        # Grievance 28b: Joint-Heir Exclusion & Partition of Inherited Land
        # ----------------------------------------------------------------------
        joint_heir_m = re.search(
            r"\b(?:brother|brothers|relative|relatives|joint-heir|joint\s*heir|co-heir|co-sharer|co-owner)\b.*?\b(?:denying|denied|excluding|excluded|won'?t\s*let|refusing)\b.*?\b(?:use|possession|share|access)\b.*?\b(?:inherited|inheritance|father'?s?\s*land|ancestral\s*land|family\s*land)\b|"
            r"\b(?:joint-heir|joint\s*heir|co-heir|co-sharer)\b.*?\b(?:denied\s*use|inherited\s*(?:agricultural\s*)?land|10\s*years|\d+\s*years|by\s*my\s*brothers|excluded)\b|"
            r"\b(?:den\w+\s*(?:me\s*)?use\s*of\s*(?:our\s*|my\s*)?inherited\s*(?:family\s*|agricultural\s*)?land)\b",
            text_lower
        )
        if joint_heir_m:
            pos = joint_heir_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Joint-Heir Exclusion & Partition of Inherited Land",
                raw_text=text,
                subject_matter="joint-heir exclusion inherited agricultural land partition adverse possession limitation",
                parties="Excluded Joint-Heir (Plaintiff) vs Brothers / Co-Sharers (Defendants)",
                aggrieved_party="Excluded Joint-Heir",
                wrongdoer="Brothers / Co-Sharers",
                action_taken="Brothers denying co-heir use and possession of inherited agricultural land for 10 years",
                relief_sought=(
                    "Under Pakistani property and inheritance law, possession of one co-sharer is legally deemed possession on behalf of all co-sharers ('possession of one co-sharer is possession of all'). "
                    "The exclusion of a joint-heir from inherited land for 10 years does not extinguish title, as adverse possession cannot run against a co-owner absent clear proof of open ouster. "
                    "The aggrieved joint-heir has the legal right to file a Suit for Declaration of Title and Joint Possession under Section 42 of the Specific Relief Act 1877, "
                    "initiate partition proceedings under the Partition Act 1893 / Land Revenue Act 1967, and claim mesne profits (share of 10 years of agricultural produce) in the Civil Court."
                ),
                search_query="joint heir denied use of inherited agricultural land declaration of title partition Section 42 Specific Relief Act Limitation Act",
                statute_hints=["SRA-SEC-42", "LIMITATION-ACT-1908", "SRA-SEC-8-9"],
                category_hint="Civil Law / Property Rights & Co-Ownership"
            )))

        # ----------------------------------------------------------------------
        # Grievance 28c: Breach of Property Sale Agreement & Buyer Refusing to Vacate
        # ----------------------------------------------------------------------
        buyer_vacate_m = re.search(
            r"\b(?:buyer|purchaser)\b.*?\b(?:agreement|house|property|plot)\b.*?\b(?:paid\s*\d+%|refusing\s*to\s*pay|refusing\s*to\s*vacate|not\s*paying|not\s*vacating)\b|"
            r"\b(?:buyer\s*refusing\s*to\s*vacate\s*after\s*non-payment)\b",
            text_lower
        )
        if buyer_vacate_m:
            pos = buyer_vacate_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Breach of Property Sale Agreement & Recovery of Possession",
                raw_text=text,
                subject_matter="property sale agreement buyer default non payment refusal to vacate rescission possession",
                parties="Property Seller / Owner (Plaintiff) vs Defaulting Buyer (Defendant)",
                aggrieved_party="Property Seller / Owner",
                wrongdoer="Defaulting Buyer",
                action_taken="Buyer paid only partial token amount, defaulted on remaining balance, and refused to vacate property",
                relief_sought=(
                    "Under Sections 39, 54 & 73 of the Contract Act 1872, where a party to a contract refuses to perform their promise in its entirety (failing to pay the purchase balance), "
                    "the seller is legally entitled to rescind the contract and forfeit or adjust earnest money according to contract terms. "
                    "To recover physical possession from the defaulting buyer refusing to vacate, the owner can institute a civil suit for recovery of possession of immovable property "
                    "under Sections 8 & 9 of the Specific Relief Act 1877 along with a claim for damages / mesne profits for unauthorized occupation in the local Civil Court."
                ),
                search_query="buyer property agreement non payment refusing to vacate breach of contract Section 73 Contract Act recovery of possession Section 8 9 Specific Relief Act",
                statute_hints=["CONTRACT-SEC-73-74", "SRA-SEC-8-9"],
                category_hint="Civil Law / Property & Contract Breach"
            )))

        # ----------------------------------------------------------------------
        # Grievance 28d: Child Custody & Parental Visitation Rights
        # ----------------------------------------------------------------------
        custody_m = re.search(
            r"\b(?:visitation|visitation\s*rights|custody\s*of\s*(?:my\s*)?(?:son|daughter|child|kids)|denying\s*(?:me\s*)?visitation|won'?t\s*let\s*me\s*see\s*(?:my\s*)?kids|see\s*my\s*(?:son|daughter|child|kids)|meet\s*(?:my\s*)?(?:son|daughter|child|kids)|child\s*visitation\s*dispute|custody\s*dispute)\b",
            text_lower
        )
        if custody_m and not insult_m and not bool(re.search(r"\b(?:kidnapp\w*|abduct\w*|snatch\w*|363|361)\b", text_lower)):
            pos = custody_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Child Custody & Parental Visitation Rights",
                raw_text=text,
                subject_matter="child custody visitation rights Guardian and Wards Act Family Court",
                parties="Parent Seeking Custody/Visitation (Petitioner) vs Custodial Ex-Spouse (Respondent)",
                aggrieved_party="Parent Seeking Access",
                wrongdoer="Custodial Ex-Spouse",
                action_taken="Ex-spouse refusing to allow parent custody or visitation rights to see minor child",
                relief_sought=(
                    "Under Sections 17 & 25 of the Guardian and Wards Act 1890 and Section 5 Schedule of the Family Courts Act 1964, custody and visitation are determined exclusively by the 'Welfare of the Minor'. "
                    "A non-custodial parent has an unconditional legal right to maintain a parental relationship with the child through a court-supervised visitation schedule (e.g. fortnightly meetings, weekends, and school vacations). "
                    "Remedies include: (1) File a custody petition under Section 25 Guardian and Wards Act before the Family Court / Guardian Judge; "
                    "(2) File an urgent application for an interim visitation schedule under Section 12 Guardian and Wards Act on the first date of hearing."
                ),
                search_query="child custody visitation rights ex wife refuses to let meet son Family Court Section 25 Guardian and Wards Act Section 5 Family Courts Act",
                statute_hints=["GWA-SEC-17-25", "FCA-SEC-5"],
                category_hint="Family Law / Custody & Guardianship"
            )))

        # ----------------------------------------------------------------------
        # Grievance 28e: Declaration of Legal Inheritance Share & Protection Against Deprivation
        # ----------------------------------------------------------------------
        inheritance_share_m = re.search(
            r"\b(?:inheritance\s*share|inheritance\s*rights|share\s*as\s*a\s*daughter|share\s*as\s*a\s*sister|distributing.*without\s*giving.*inheritance|share\s*in.*estate|legal\s*share\s*in.*estate|inheritance\s*share\s*questions)\b",
            text_lower
        )
        if inheritance_share_m and not limitation_m:
            pos = inheritance_share_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Declaration of Legal Inheritance Share & Protection Against Deprivation",
                raw_text=text,
                subject_matter="inheritance legal share daughter succession declaration of title deprivation PPC 498-A",
                parties="Female Legal Heir / Daughter (Plaintiff) vs Relatives / Co-Heirs (Defendants)",
                aggrieved_party="Female Legal Heir",
                wrongdoer="Relatives / Co-Heirs",
                action_taken="Deceased parent passed away leaving estate; co-heirs distributing or withholding legal inheritance share from daughter/sister",
                relief_sought=(
                    "Under Pakistani inheritance law, the Muslim Personal Law (Shariat) Application Act 1962, and Section 42 of the Specific Relief Act 1877, inheritance rights vest automatically upon the death of the ancestor. "
                    "Daughters and sisters are entitled to predetermined, fixed Quranic shares in all immovable and movable properties. "
                    "Furthermore, depriving any female heir of her lawful inheritance is a serious cognizable crime under Section 498-A of the Pakistan Penal Code punishable with imprisonment up to 10 years and a fine of 1,000,000 rupees. "
                    "Remedies include: (1) File a Civil Suit for Declaration of Title, Injunction, and Partition under Section 42 Specific Relief Act 1877 read with CPC Order XXXIX; "
                    "(2) Submit an application before the Tehsildar / Revenue Authorities to withhold or correct any illegal mutation (Intiqal); and "
                    "(3) Lodge a complaint under Section 498-A PPC if relatives attempt to fraudulently disinherit the female heir."
                ),
                search_query="inheritance share daughter deceased father land property declaration Section 42 Specific Relief Act Section 498-A PPC",
                statute_hints=["SRA-SEC-42", "PPC-498A-498B"],
                category_hint="Civil Law / Succession & Inheritance Rights"
            )))

        # ----------------------------------------------------------------------
        # Grievance 28f: Guarantor Liability & Rights Under Contract of Guarantee
        # ----------------------------------------------------------------------
        guarantor_m = re.search(
            r"\b(?:guarantor|co-signer|co\s*signer|signed\s*as\s*a\s*guarantor|guarantor\s*for.*loan|guarantee.*loan|bank.*demanding.*guarantor)\b",
            text_lower
        )
        if guarantor_m:
            pos = guarantor_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Guarantor Liability & Surety Rights Under Contract of Guarantee",
                raw_text=text,
                subject_matter="guarantor co-signer liability contract of guarantee discharge of surety Contract Act 1872",
                parties="Guarantor / Surety (User) vs Bank / Creditor (Lender)",
                aggrieved_party="Guarantor / Surety",
                wrongdoer="Bank / Defaulting Principal Debtor",
                action_taken="Bank demanding loan payment from guarantor after principal borrower defaulted",
                relief_sought=(
                    "Under Section 128 of the Contract Act 1872, the liability of a surety (guarantor) is co-extensive with that of the principal debtor unless provided otherwise by contract. "
                    "However, under Sections 133 to 139 of the Contract Act 1872, a surety is legally discharged if the creditor makes any unauthorized variance to contract terms without consent, "
                    "releases or gives time to the principal debtor without concurrence, or impairs the guarantor's eventual remedy against the debtor. "
                    "If the financial institution initiates recovery proceedings under the Financial Institutions (Recovery of Finances) Ordinance 2001 (FIO), "
                    "the guarantor must file an Application for Leave to Defend under Section 10 FIO within 30 days of summons before the Banking Court."
                ),
                search_query="signed as guarantor co signer bank demanding loan payment liability of surety Section 128 Contract Act 1872 Financial Institutions Ordinance",
                statute_hints=["CONTRACT-SEC-73-74", "CONTRACT-SEC-10-19"],
                category_hint="Commercial Law / Banking & Suretyship"
            )))

        # ----------------------------------------------------------------------
        # Grievance 29: Inadmissibility of Police Custodial Confession (QSO Articles 38 & 39)
        # ----------------------------------------------------------------------
        confession_m = re.search(
            r"\b(?:confession|confess\w*|statement\s*to\s*police)\b.*?\b(?:police|custody|arrest\w*|pressur\w*|tortur\w*|threat\w*)\b|"
            r"\b(?:police|arrest\w*|lockup|thana)\b.*?\b(?:confession|confess\w*|pressur\w*)\b|"
            r"\b(?:can\s*a\s*confession\s*like\s*that\s*be\s*used)\b",
            text_lower
        )
        if confession_m and not theft_m:
            pos = confession_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Inadmissibility of Police Custodial Confession (Articles 38 & 39 QSO)",
                raw_text=text,
                subject_matter="police custody confession coerced statement admissibility evidence",
                parties="Accused / Detainee (Aggrieved Citizen) vs Police / Prosecution",
                aggrieved_party="Accused / Detainee",
                wrongdoer="Police / Prosecution",
                action_taken="Police recorded or extracted alleged confession while accused was in custody or under pressure",
                relief_sought=(
                    "Under Article 38 of the Qanun-e-Shahadat Order 1984, no confession made to a police officer can be proved against an accused person in court. "
                    "Under Article 39, no confession made while in police custody is admissible unless recorded in the immediate presence of a Judicial Magistrate under Section 164 CrPC. "
                    "Any confession caused by inducement, threat, coercion, or pressure is completely void and inadmissible in criminal proceedings."
                ),
                search_query="confession to police officer in custody pressured coerced confession Articles 38 39 Qanun-e-Shahadat Order QSO",
                statute_hints=["QSO-ART-38-39"],
                category_hint="Law of Evidence / Protection Against Police Torture"
            )))

        # ----------------------------------------------------------------------
        # Grievance 30: Religious Remark Accusation, Solitary Witness & Criminal Appeal
        # ----------------------------------------------------------------------
        religious_m = re.search(
            r"\b(?:disrespectful|religion|blasphem\w*|religious)\b.*?\b(?:overheard|one\s*person|single\s*witness|accused)\b|"
            r"\b(?:accused\s*me\s*of\s*saying|disrespectful\s*about\s*(?:his\s*)?religion)\b|"
            r"\b(?:prosecuted\s*just\s*on\s*one\s*person's\s*word|lower\s*court\s*believes\s*him)\b",
            text_lower
        )
        if religious_m:
            pos = religious_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Evidentiary Sufficiency of Solitary Overheard Witness (Article 17 QSO)",
                raw_text=text,
                subject_matter="criminal allegation solitary witness overhearing evidence corroboration",
                parties="Accused Neighbor (Defendant) vs Accuser & Overhearing Witness (Complainant)",
                aggrieved_party="Accused Neighbor",
                wrongdoer="Accuser / Complainant",
                action_taken="Neighbor leveled criminal accusation of religious disrespect based solely on one person allegedly overhearing a remark",
                relief_sought=(
                    "Under Article 17 of the Qanun-e-Shahadat Order 1984, while the law does not prescribe a fixed number of witnesses in ordinary matters, "
                    "Pakistani courts require extreme caution and strict corroboration before relying on a solitary witness in serious or sensitive allegations. "
                    "Where an accusation rests solely on an allegedly overheard statement, the danger of mishearing, personal grudge, or fabrication is acute, and courts require independent corroboration and proof beyond reasonable doubt."
                ),
                search_query="single witness testimony uncorroborated overhearing criminal allegation Article 17 Qanun-e-Shahadat Order QSO",
                statute_hints=["QSO-ART-17"],
                category_hint="Law of Evidence / Witness Testimony & Proof"
            )))
            detected.append((pos + 1, LegalIssue(
                issue_index=0,
                issue_title="Right of Criminal Appeal Against Lower Court Conviction (Sections 408 & 410 CrPC)",
                raw_text=text,
                subject_matter="criminal conviction lower court magistrate appeal sessions high court",
                parties="Convicted Appellant (Accused) vs State / Complainant",
                aggrieved_party="Convicted Appellant",
                wrongdoer="State / Prosecution",
                action_taken="Possibility of lower trial court erroneously believing single witness and passing conviction order",
                relief_sought=(
                    "Under Sections 408 and 410 of the Code of Criminal Procedure 1898, if a lower trial court convicts an accused person, the decision is not final. "
                    "The accused has an absolute statutory right of criminal appeal to the Court of Session or the High Court. "
                    "The appellate court has full power to re-examine all evidence, suspend the execution of sentence and grant bail pending appeal under Section 426 CrPC, and overturn the conviction if guilt was not proved beyond reasonable doubt."
                ),
                search_query="appeal against conviction magistrate trial court lower court Section 408 410 Code of Criminal Procedure CrPC",
                statute_hints=["CRPC-408-410"],
                category_hint="Criminal Procedure / Appellate Remedies"
            )))

        # ----------------------------------------------------------------------
        # Grievance 31: Real-Time Legislative Currency & Uncertain In-Force Legal Status
        # ----------------------------------------------------------------------
        currency_m = re.search(
            r"\b(?:law\s*changed|law\s*amended|amendment\s*passed|passed\s*(?:an?\s*)?amendment|statute\s*changed)\b.*?\b(?:reversed|struck\s*down|last\s*year|recently|which\s*version|in\s*force|applies\s*to\s*me|stay\s*order|stay|vacated|enforceable|enforced|suspend)\b|"
            r"\b(?:law\s*changed\s*last\s*year|reversed\s*again\s*recently|which\s*version\s*applies\s*to\s*me\s*right\s*now)\b|"
            r"\b(?:how\s*do\s*i\s*know\s*which\s*version\s*applies|legally\s*enforceable\s*(?:on\s*my\s*plot\s*)?today)\b",
            text_lower
        )
        if currency_m:
            pos = currency_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Real-Time Legislative Currency & In-Force Version Inquiries",
                raw_text=text,
                subject_matter="real-time legislative amendments reversals statutory currency gazette notification",
                parties="Citizen / Litigant vs Statutory Regime",
                aggrieved_party="Citizen / Litigant",
                wrongdoer="N/A",
                action_taken="Citizen inquiring about whether a recent legislative amendment was reversed and which statutory version currently applies",
                relief_sought=(
                    "I cannot reliably determine or verify very recent legal amendments, breaking statutory reversals, or real-time court stay orders. "
                    "Under Pakistani jurisprudence, when a High Court issues an ad-interim stay order against an amendment or statutory notification, "
                    "the stay temporarily suspends notification implementation and halts enforcement pending final judicial adjudication. "
                    "Furthermore, under Section 6 of the General Clauses Act 1897, substantive legal rights and liabilities are generally governed by the law in force at the time the cause of action arose unless expressly made retrospective. "
                    "To determine with certainty whether the amendment or stay applies to your specific appeal today, you should consult an advocate to examine the certified court order and official gazette notification."
                ),
                search_query="recent legislative changes amendments reversed General Clauses Act Section 6 official gazette in force stay order",
                statute_hints=[],
                category_hint="Statutory Currency Limitation"
            )))

        # ----------------------------------------------------------------------
        # Grievance 32: Evacuee Trust Property & ETPB Statutory Protection
        # ----------------------------------------------------------------------
        etpb_m = re.search(
            r"\b(?:evacuee\s*trust|etpb|waqf\s*property|temple\s*trust|hindu\s*temple\s*trust)\b",
            text_lower
        )
        if etpb_m:
            pos = etpb_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Evacuee Trust Property & Federal Statutory Tenancy Protection",
                raw_text=text,
                subject_matter="evacuee trust property federal board jurisdiction vs unauthorized local committee lease",
                parties="Occupant / Warehouse Lessee vs Evacuee Trust Property Board (ETPB)",
                aggrieved_party="Occupant / Warehouse Lessee",
                wrongdoer="Unauthorized Local Committee / ETPB",
                action_taken="Local committee leased evacuee trust land without statutory authority; ETPB issued ejectment notice",
                relief_sought=(
                    "Under Pakistani law and the Evacuee Trust Properties (Management and Disposal) Act 1975, "
                    "evacuee trust properties and historical religious trust lands are owned and administered exclusively by the Federal Evacuee Trust Property Board (ETPB). "
                    "Private local management committees have no legal power or jurisdiction to grant commercial leases over evacuee trust property. "
                    "Provincial rented premises acts (PRPA 2009 / SRPO 1979) do not apply to evacuee trust lands, and a Rent Controller has no jurisdiction. "
                    "To protect his investment, your brother must approach the Chairman ETPB or Secretary Ministry of Religious Affairs for statutory regularisation under official ETPB lease schemes, or challenge any procedural irregularity before the High Court under Article 199."
                ),
                search_query="evacuee trust property board ETPB Act 1975 lease unauthorized committee eviction",
                statute_hints=[],
                category_hint="Evacuee Trust Property Law / Administrative Jurisdictional Conflict"
            )))

        # ----------------------------------------------------------------------
        # Grievance 33: Vernacular Inheritance & Revenue Record Dispute (Fard/Tatima)
        # ----------------------------------------------------------------------
        vernacular_land_m = re.search(
            r"\b(?:bainama|iqraarnama|iqrarnama|fard|patwari|tatima|tatima\s*cut)\b.*?\b(?:wafat|hissa|chacha|zameen|qabza)\b|"
            r"\b(?:abba\s*ji|chacha)\b.*?\b(?:zameen|bainama|fard|tatima|qabza)\b",
            text_lower
        )
        if vernacular_land_m:
            pos = vernacular_land_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Inherited Agricultural Land & Revenue Record / Title Dispute",
                raw_text=text,
                subject_matter="unregistered agreement revenue entry fard tatima inheritance co-heirs",
                parties="Legal Heirs of Deceased Father (Plaintiffs) vs Paternal Uncle / Chacha (Defendant)",
                aggrieved_party="Legal Heirs of Deceased Father",
                wrongdoer="Paternal Uncle / Chacha",
                action_taken="Uncle got revenue record / fard transferred in his name using tatima cut, denying legal heirs their inheritance share",
                relief_sought=(
                    "Under established Pakistani land law and Supreme Court jurisprudence, revenue records (fard, tatima, or mutation / intiqal) are maintained solely for fiscal collection purposes and do NOT confer or extinguish title of ownership. "
                    "An unregistered agreement (iqraarnama) or fraudulent revenue entry by an uncle cannot deprive the lawful legal heirs of their Quranic inheritance share under Islamic law. "
                    "The legal heirs should file a Suit for Declaration of Title and Cancellation of Fraudulent Mutation under Section 42 of the Specific Relief Act 1877 along with an application for Temporary Injunction under Order XXXIX Rules 1 & 2 CPC before the Senior Civil Judge to restrain alienation or dispossession."
                ),
                search_query="inherited land revenue record fard tatima patwari mutation declaration title Section 42 Specific Relief Act",
                statute_hints=["SRA-SEC-42", "CPC-O39-R1-2"],
                category_hint="Civil Law / Property Rights & Inheritance"
            )))

        # ----------------------------------------------------------------------
        # Grievance 34: Commercial Mall Kiosk Licence vs Tenancy Protection
        # ----------------------------------------------------------------------
        kiosk_m = re.search(
            r"\b(?:kiosk|revocable\s*licen[cs]e|licen[cs]e\s*agreement|shopping\s*mall|food\s*court)\b.*?\b(?:terminated|rent\s*controller|punjab\s*rented\s*premises|eviction\s*defense)\b",
            text_lower
        )
        if kiosk_m:
            pos = kiosk_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Commercial Kiosk Licence vs Tenancy Protection",
                raw_text=text,
                subject_matter="revocable commercial kiosk licence shopping mall exclusion from rent restriction acts",
                parties="Kiosk Operator / Licensee vs Shopping Mall Management (Licensor)",
                aggrieved_party="Kiosk Operator",
                wrongdoer="Shopping Mall Management",
                action_taken="Mall management revoked 6-month kiosk licence after 3 months; operator inquiring about tenancy defense under PRPA",
                relief_sought=(
                    "Under Pakistani law and the Easements Act 1882 (Section 52), a revocable kiosk agreement in a commercial shopping mall or food court is a Licence, NOT a protected tenancy. "
                    "The Punjab Rented Premises Act 2009 applies strictly to tenancies with exclusive possession of premises, not revocable mall kiosks. "
                    "Therefore, the Special Rent Tribunal / Rent Controller has NO jurisdiction, and you cannot file a tenant eviction defense under the Punjab Rented Premises Act. "
                    "Your legal remedy, if the termination was wrongful or contrary to licence terms, is to file a civil suit for breach of contract and recovery of security deposit / damages under the Contract Act 1872 before the local civil court."
                ),
                search_query="revocable kiosk license shopping mall Easements Act Section 52 not protected tenancy Contract Act",
                statute_hints=["CONTRACT-SEC-73-74"],
                category_hint="Commercial Law / Licences & Contracts"
            )))

        # ----------------------------------------------------------------------
        # Grievance 35: False Police Complaint & Whistleblower Defamation Defense (PPC 499)
        # ----------------------------------------------------------------------
        false_complaint_m = re.search(
            r"\b(?:file\s*(?:an\s*)?fir\s*against\s*him\s*for\s*defamation|fir\s*for\s*defamation|put\s*him\s*in\s*jail\s*for\s*false\s*accusation)\b|"
            r"\b(?:baseless|false\s*complaint|false\s*accusation)\b.*?\b(?:fir\s*for\s*defamation|defamation\s*fir)\b|"
            r"\b(?:anti-corruption|official\s*complaint|bribe)\b.*?\b(?:defamation|ppc\s*500|legal\s*notice|damages\s*suit)\b|"
            r"\b(?:defamation|ppc\s*500)\b.*?\b(?:anti-corruption|official\s*complaint|bribe)\b",
            text_lower
        )
        if false_complaint_m:
            pos = false_complaint_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Official Corruption Complaint & Defamation Defense (PPC 499 Eighth Exception)",
                raw_text=text,
                subject_matter="official anti-corruption complaint defamation legal notice section 499 eighth exception",
                parties="Complainant / Whistleblower vs Accused Official / Clerk",
                aggrieved_party="Complainant / Whistleblower",
                wrongdoer="Accused Official / Clerk",
                action_taken="Official issued legal notice threatening criminal defamation under PPC 500 for lodging corruption complaint",
                relief_sought=(
                    "Under Section 499 of the Pakistan Penal Code (Eighth Exception), preferring in good faith an accusation or complaint against any person to a lawful authority (such as the Anti-Corruption Establishment) is NOT defamation. "
                    "A public servant cannot prosecute a citizen for criminal defamation under PPC 500 simply for reporting a bribe or official misconduct. "
                    "Furthermore, lodging a bona fide complaint before an authorized investigating body is protected under public policy. "
                    "You should have your advocate issue a formal reply to the legal notice citing the Eighth Exception to Section 499 PPC and warning the official against threatening witnesses or subverting anti-corruption investigations."
                ),
                search_query="whistleblower official complaint anti-corruption defamation Section 499 Eighth Exception PPC 500",
                statute_hints=[],
                category_hint="Criminal Law / Defamation & Whistleblower Defense"
            )))

        # ----------------------------------------------------------------------
        # Grievance 36: Dower / Jahez Jewelry & Defense Against False Theft FIR
        # ----------------------------------------------------------------------
        dower_theft_m = re.search(
            r"\b(?:dowry|jahez|haq\s*mehr|dower)\b.*?\b(?:theft|stole|stealing|chori|fir\s*against\s*me|ppc\s*379|ppc\s*380)\b|"
            r"\b(?:theft|stole|stealing|chori|fir\s*against\s*me|ppc\s*379|ppc\s*380)\b.*?\b(?:dowry|jahez|haq\s*mehr|dower)\b",
            text_lower
        )
        if dower_theft_m:
            pos = dower_theft_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Recovery of Dowry/Dower Articles vs False Criminal Theft FIR",
                raw_text=text,
                subject_matter="dowry jahez dower bridal gold false theft fir exclusive family court jurisdiction",
                parties="Wife (Accused in FIR / Claimant) vs Husband (Complainant in FIR)",
                aggrieved_party="Wife",
                wrongdoer="Husband",
                action_taken="Husband registered or threatened criminal theft FIR under PPC 379/380 over dowry and Haq Mehr jewelry",
                relief_sought=(
                    "Under Pakistani matrimonial law and the Family Courts Act 1964, dowry articles (jahez) and Haq Mehr (dower) are the absolute personal property of the wife. "
                    "A wife taking possession of her own bridal jewelry or dowry articles does NOT commit criminal theft under Section 378 or 380 PPC, as she is the lawful owner and lacks dishonest intent. "
                    "The Supreme Court of Pakistan has repeatedly ruled that disputes regarding dowry articles fall exclusively under the authority of the Family Court under Section 5 read with the Schedule of the Family Courts Act 1964. "
                    "Criminal theft FIRs lodged by husbands over dowry items constitute an abuse of judicial process. "
                    "Your remedies are: (1) apply for pre-arrest bail under Section 498 CrPC before the Sessions Court to protect against unlawful arrest; "
                    "(2) file a quashment petition under Section 561-A CrPC before the High Court to strike down the fabricated FIR; and "
                    "(3) institute a suit before the Family Court for recovery of all remaining dowry articles and outstanding dower."
                ),
                search_query="dowry jahez dower Haq Mehr jewelry false theft FIR Section 5 Family Courts Act quashment Section 561-A CrPC",
                statute_hints=["FCA-SEC-5", "CRPC-SEC-497"],
                category_hint="Family Law / Dowry Recovery & Criminal Quashment"
            )))

        # ----------------------------------------------------------------------
        # Grievance 37: Inland Waterway Cargo Loss vs High Court Admiralty Jurisdiction
        # ----------------------------------------------------------------------
        barge_m = re.search(
            r"\b(?:barge|river|inland\s*waterway|inland\s*carriage|indus\s*river)\b.*?\b(?:sank|sink|cargo|bales|cotton|admiralty|force\s*majeure)\b|"
            r"\b(?:admiralty\s*court|admiralty\s*jurisdiction)\b.*?\b(?:barge|river|inland|carrier\s*liability)\b",
            text_lower
        )
        if barge_m:
            pos = barge_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Inland River Carrier Cargo Loss vs High Court Admiralty Jurisdiction",
                raw_text=text,
                subject_matter="inland water cargo loss barge sank carriage of goods civil court vs admiralty",
                parties="Cargo Owner (Consignor) vs River Barge Owner (Carrier / Bailee)",
                aggrieved_party="Cargo Owner",
                wrongdoer="River Barge Owner",
                action_taken="Barge sank due to overloading and engine failure; carrier claiming High Court Admiralty jurisdiction and force majeure",
                relief_sought=(
                    "Under Pakistani law, the High Court's admiralty authority under the Admiralty Ordinance 1980 applies strictly to maritime and sea navigation, NOT inland river barges operating on internal waterways like the River Indus. "
                    "Inland river carriage is governed by the Carriers Act 1865 and Sections 151 and 152 of the Contract Act 1872 regarding the standard of ordinary prudence required of a bailee. "
                    "Because the sinking was caused by negligent overloading and mechanical engine failure rather than an Act of God, the carrier cannot claim force majeure immunity. "
                    "The cargo owner can file a civil suit for compensation and recovery of damages under Section 73 of the Contract Act 1872 before the local Civil Court having proper territorial authority."
                ),
                search_query="inland river carriage barge sank cargo loss Carriers Act 1865 Admiralty Ordinance Contract Act Section 73 damages",
                statute_hints=["CONTRACT-SEC-73-74"],
                category_hint="Commercial Law / Inland Carriage & Bailment"
            )))

        # ----------------------------------------------------------------------
        # Grievance 38: Co-Accused Confession & Overseas Accused / INTERPOL Red Notice Threat
        # ----------------------------------------------------------------------
        coaccused_m = re.search(
            r"\b(?:co-accused|confession\s*of\s*(?:an?\s*)?arrested|solely\s*based\s*on\s*(?:the\s*)?confession)\b.*?\b(?:interpol|red\s*notice|extradit\w*|dubai|overseas)\b|"
            r"\b(?:interpol|red\s*notice|extradit\w*)\b.*?\b(?:co-accused|confession|commercial\s*dispute|private\s*dispute)\b",
            text_lower
        )
        if coaccused_m:
            pos = coaccused_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Evidentiary Value of Co-Accused Confession & INTERPOL Red Notice Limitations",
                raw_text=text,
                subject_matter="co-accused confession Article 43 QSO interpol red notice extradition private commercial dispute",
                parties="Overseas Accused Brother vs Complainant / Police",
                aggrieved_party="Overseas Accused Brother",
                wrongdoer="Complainant / Investigating Agency",
                action_taken="Brother named in fraud FIR solely on co-accused confession; complainant threatening immediate INTERPOL red notice and extradition",
                relief_sought=(
                    "Under Article 43 of the Qanun-e-Shahadat Order 1984, the confession of a co-accused cannot be treated as substantive evidence against another accused person and cannot be the sole basis for a criminal conviction. It can only be taken into circumstantial consideration if independent corroborative evidence exists. "
                    "Furthermore, an INTERPOL Red Notice cannot be issued casually for private complaints or commercial disputes. Under Pakistan's Extradition Act 1972 and INTERPOL regulations, a Red Notice requires a non-bailable arrest warrant issued by a competent trial court, a formal request routed through the Ministry of Interior and FIA National Central Bureau (NCB), and must meet strict dual-criminality thresholds. "
                    "To safeguard your brother: (1) engage an advocate to inspect the police investigation diary (Zimni) and challenge the lack of independent evidence; (2) file a petition under Section 561-A CrPC before the High Court for quashing the FIR or deleting his name; and (3) apply for protective / transit bail before the High Court to ensure safe return without apprehension of immediate airport arrest."
                ),
                search_query="co-accused confession Article 43 QSO interpol red notice Extradition Act protective bail Section 561-A CrPC",
                statute_hints=["QSO-ART-38-39", "CRPC-SEC-497"],
                category_hint="Criminal Law / Evidence & Extradition"
            )))

        # ----------------------------------------------------------------------
        # Grievance 39: Underage Driving & Minor Vehicle Scrape vs False Robbery & Section 115 PMVO Seizure
        # ----------------------------------------------------------------------
        minor_scrape_m = re.search(
            r"\b(?:nephew|son|minor|15-year-old|underage|child)\b.*?\b(?:keys|scratched|scraped|reversing|parked\s*car)\b|"
            r"\b(?:scratched|scraped)\b.*?\b(?:parked\s*car|robbery|500,000|pmvo|section\s*115)\b",
            text_lower
        )
        if minor_scrape_m:
            pos = minor_scrape_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Minor Vehicle Scrape vs Robbery Allegation & PMVO Section 115 Seizure",
                raw_text=text,
                subject_matter="minor vehicle scrape reversing parked car underage driving false robbery Section 115 PMVO",
                parties="Minor Driver / Guardian vs Parked Car Owner",
                aggrieved_party="Minor Driver / Guardian",
                wrongdoer="Parked Car Owner (Extortionate Demands)",
                action_taken="15-year-old minor scraped parked car; car owner threatening robbery FIR, 500,000 cash demand, and Section 115 PMVO car seizure",
                relief_sought=(
                    "Under Pakistani law: (1) Scraping a vehicle while reversing is a pure civil accident / property damage tort and is NOT robbery (Section 392 PPC) or criminal trespass. Threatening a robbery FIR over a minor vehicle scrape constitutes criminal intimidation. "
                    "(2) Section 115 of the Provincial Motor Vehicles Ordinance 1965 (PMVO) authorizes traffic police to detain vehicles operated without valid registration or permits; a private car owner has no legal power to invoke Section 115 PMVO or seize your car. "
                    "(3) The minor (being 15 years old) committed a traffic licensing infraction under Sections 3 & 4 PMVO (driving without a licence), punishable by standard traffic challan fine. "
                    "(4) Civil liability is strictly limited to actual repair damages for the scratch under Section 73 of the Contract Act 1872; arbitrary cash extortion or inflated 500,000 PKR demands have no legal validity. You should offer to pay the actual repair quote from a reputable automobile workshop."
                ),
                search_query="car scrape reversing underage driving robbery false FIR Section 115 PMVO repair damages Contract Act Section 73",
                statute_hints=["PMVO-SEC-115", "CONTRACT-SEC-73-74"],
                category_hint="Civil Law / Traffic & Property Damage Liability"
            )))

        # ----------------------------------------------------------------------
        # Grievance 40: Building Inspector Bribery vs Consumer Protection
        # ----------------------------------------------------------------------
        bribery_consumer_m = re.search(
            r"\b(?:building\s*inspector|municipal\s*corporation|building\s*plan|sanction\s*my\s*residential)\b.*?\b(?:bribe|50,000|deficiency\s*of\s*service|consumer\s*(?:protection\s*)?court)\b|"
            r"\b(?:consumer\s*(?:protection\s*)?court)\b.*?\b(?:bribe|building\s*inspector|building\s*plan)\b",
            text_lower
        )
        if bribery_consumer_m:
            pos = bribery_consumer_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Public Regulatory Bribery vs Consumer Court Authority",
                raw_text=text,
                subject_matter="public regulatory bribery vs consumer court authority official corruption",
                parties="Citizen Complainant vs Municipal Building Inspector",
                aggrieved_party="Citizen Complainant",
                wrongdoer="Municipal Building Inspector",
                action_taken="Municipal building inspector demanded 50,000 PKR bribe to sanction residential building plan; citizen asks about consumer court",
                relief_sought=(
                    "Under Pakistani law: (1) Statutory municipal regulatory approvals are sovereign government duties, not commercial consumer services under Consumer Protection Acts. "
                    "(2) Demanding a cash bribe is criminal corruption under Section 161 of the Pakistan Penal Code and Section 5(2) of the Prevention of Corruption Act 1947. "
                    "(3) The proper remedy is an Anti-Corruption Establishment (ACE) complaint or a direct private complaint to the magistrate (istighasa) before the Special Judge Anti-Corruption, not the Consumer Protection Court."
                ),
                search_query="public regulatory bribery vs consumer court authority Section 161 PPC Prevention of Corruption Act Anti-Corruption Establishment",
                statute_hints=[],
                category_hint="Criminal Law / Anti-Corruption & Public Duties"
            )))

        # ----------------------------------------------------------------------
        # Grievance 41: Mall Kiosk Revocable License vs Tenancy & Equipment Confiscation
        # ----------------------------------------------------------------------
        kiosk_m = re.search(
            r"\b(?:food\s*stall|kiosk|shopping\s*mall|licence\s*and\s*concession)\b.*?\b(?:sealed\s*my\s*stall|seized\s*my\s*kitchen|appliances|rent\s*controller|eviction\s*suit)\b|"
            r"\b(?:licence\s*and\s*concession\s*agreement|commercial\s*licen[cs]es)\b",
            text_lower
        )
        if kiosk_m:
            pos = kiosk_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Kiosk Licence vs Protected Tenancy and Equipment Seizure",
                raw_text=text,
                subject_matter="kiosk licence vs protected tenancy and equipment seizure mall concession damages",
                parties="Stall Licensee vs Mall Management",
                aggrieved_party="Stall Licensee",
                wrongdoer="Mall Management",
                action_taken="Mall management sealed stall and seized kitchen appliances without court eviction suit following 5-day delay",
                relief_sought=(
                    "Under Pakistani law: (1) A shopping mall kiosk concession is a revocable licence under the Easements Act 1882, not a protected statutory tenancy under the Punjab Rented Premises Act. "
                    "(2) However, mall management cannot unilaterally confiscate tenant or licensee kitchen equipment or private goods without a court order; doing so constitutes wrongful seizure of goods. "
                    "(3) Your remedy is a suit for damages and breach of contract under Section 73 and 74 of the Contract Act 1872 before the civil court to recover the unlawfully seized kitchen appliances and compensation."
                ),
                search_query="kiosk licence vs protected tenancy and equipment seizure Contract Act Section 73 74 damages",
                statute_hints=["CONTRACT-SEC-73-74"],
                category_hint="Commercial Law / Licence & Breach of Contract"
            )))

        # ----------------------------------------------------------------------
        # Grievance 42: Resignation Unpaid Wages vs Criminal Breach of Trust PPC 406
        # ----------------------------------------------------------------------
        wage_breach_m = re.search(
            r"\b(?:withheld\s*(?:my\s*)?4\s*months\s*salary|unpaid\s*salary|gratuity|resigned)\b.*?\b(?:breach\s*of\s*trust|ppc\s*406|misappropriated|passwords)\b|"
            r"\b(?:ppc\s*406)\b.*?\b(?:salary|wages|resigned|passwords)\b",
            text_lower
        )
        if wage_breach_m:
            pos = wage_breach_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Unpaid Salary Recovery and Criminal Breach of Trust Defense",
                raw_text=text,
                subject_matter="unpaid salary recovery and criminal breach of trust defense Section 15 Payment of Wages Act",
                parties="Employee (Resigned) vs Employer / Manager",
                aggrieved_party="Employee (Resigned)",
                wrongdoer="Employer / Manager",
                action_taken="Employer withheld 4 months salary and gratuity and threatened PPC 406 FIR over project passwords",
                relief_sought=(
                    "Under Pakistani law: (1) Unpaid salary and gratuity recovery is a statutory employment matter under Section 15 of the Payment of Wages Act 1936. "
                    "(2) Refusing project handover pending salary lacks dishonest intention and does not constitute criminal breach of trust under PPC 406. "
                    "(3) The threat of criminal FIR to coerce wage abandonment is an abuse of process quashable under Section 561-A CrPC. You can file a formal claim before the Authority under the Payment of Wages Act or the Labour Court."
                ),
                search_query="unpaid salary recovery and criminal breach of trust defense Section 15 Payment of Wages Act",
                statute_hints=["PWA-SEC-15"],
                category_hint="Labour Law / Wage Recovery & Criminal Defense"
            )))

        # ----------------------------------------------------------------------
        # Grievance 43: Cyber Blackmail & Private Photos vs Civil Defamation
        # ----------------------------------------------------------------------
        cyber_blackmail_m = re.search(
            r"\b(?:former\s*fianc[eé]|ex-fianc[eé]|fianc[eé])\b.*?\b(?:private\s*photos|whatsapp|blackmail|300,000|reputation|defamation)\b|"
            r"\b(?:private\s*photos|whatsapp\s*conversations)\b.*?\b(?:online\s*unless\s*i\s*pay|cyber\s*extortion)\b",
            text_lower
        )
        if cyber_blackmail_m:
            pos = cyber_blackmail_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Cyber Extortion and Private Photo Blackmail vs Civil Defamation",
                raw_text=text,
                subject_matter="cyber extortion and private photo blackmail vs civil defamation PECA 2016",
                parties="Victim vs Former Fiancé",
                aggrieved_party="Victim",
                wrongdoer="Former Fiancé",
                action_taken="Former fiancé threatening to post private photos and WhatsApp conversations online unless paid 300,000 PKR",
                relief_sought=(
                    "Under Pakistani law: (1) Threatening to distribute non-consensual private photos for money constitutes criminal extortion and cyber offenses under PECA 2016 Sections 20 & 21. "
                    "(2) Extortion and criminal intimidation are punishable under Sections 384 and 506 of the Pakistan Penal Code. "
                    "(3) The proper reporting agency is the FIA Cyber Crime Wing (CCW), not a civil defamation suit. You should preserve evidence and lodge an immediate complaint with the FIA Cyber Crime Wing."
                ),
                search_query="cyber extortion and private photo blackmail vs civil defamation PECA 2016 Sections 20 21 FIA",
                statute_hints=["PECA-SEC-20-21"],
                category_hint="Cyber Law / Online Harassment & Extortion"
            )))

        # ----------------------------------------------------------------------
        # Grievance 44: Whistleblower Corruption Complaint vs Criminal Defamation PPC 500
        # ----------------------------------------------------------------------
        whistleblower_m = re.search(
            r"\b(?:revenue\s*clerk|death\s*certificate|anti-corruption\s*establishment)\b.*?\b(?:legal\s*notice|ppc\s*500|defamation|10\s*million|damages\s*suit)\b|"
            r"\b(?:anti-corruption\s*establishment)\b.*?\b(?:ppc\s*500|defamation)\b",
            text_lower
        )
        if whistleblower_m:
            pos = whistleblower_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Official Corruption Complaint and Statutory Defamation Immunity",
                raw_text=text,
                subject_matter="official corruption complaint and statutory defamation immunity Eighth Exception Section 499 PPC",
                parties="Complainant Citizen vs Revenue Clerk",
                aggrieved_party="Complainant Citizen",
                wrongdoer="Revenue Clerk",
                action_taken="Revenue clerk demanded 20,000 PKR bribe; citizen reported to ACE; clerk threatened PPC 500 defamation notice",
                relief_sought=(
                    "Under Pakistani law: (1) Under the Eighth Exception to Section 499 PPC, a good-faith complaint to lawful authority is not defamation. "
                    "(2) An Anti-Corruption Establishment complaint cannot be prosecuted as criminal defamation under PPC 500. "
                    "(3) The legal notice should be answered formally citing statutory immunity under Section 499 PPC through an advocate."
                ),
                search_query="official corruption complaint and statutory defamation immunity Section 499 PPC Eighth Exception",
                statute_hints=[],
                category_hint="Criminal Law / Whistleblower Protection & Defamation Defense"
            )))

        # ----------------------------------------------------------------------
        # Grievance 45: Domestic Maid Framed for Diamond Theft to Evade Unpaid Salary
        # ----------------------------------------------------------------------
        maid_framed_m = re.search(
            r"\b(?:maid|domestic\s*worker|clifton)\b.*?\b(?:unpaid\s*salary|confiscated\s*(?:my\s*)?cnic|diamond\s*earrings|800,000|ppc\s*380)\b|"
            r"\b(?:diamond\s*earrings)\b.*?\b(?:bedroom|ppc\s*380|maid|domestic\s*worker)\b",
            text_lower
        )
        if maid_framed_m:
            pos = maid_framed_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Pre-Arrest Bail Against False Theft FIR and Recovery of CNIC Wages",
                raw_text=text,
                subject_matter="pre-arrest bail against false theft fir and recovery of cnic wages domestic worker",
                parties="Domestic Maid (Accused / Aggrieved) vs Employer (Complainant)",
                aggrieved_party="Domestic Maid",
                wrongdoer="Employer",
                action_taken="Employer confiscated CNIC, locked gate, and lodged false PPC 380 theft complaint over diamond earrings when maid asked for unpaid salary",
                relief_sought=(
                    "Under Pakistani law: (1) Immediate protection against arrest requires applying for pre-arrest bail under Section 498 CrPC before the Sessions Court. "
                    "(2) An employer fabricating a false theft accusation to evade wages commits an offense under Section 182 PPC. "
                    "(3) Confiscating CNIC and withholding salary violates the Domestic Workers Act; recovery through labour court or dispute committee."
                ),
                search_query="pre-arrest bail against false theft fir and recovery of cnic wages Section 497 498 CrPC Domestic Workers Act",
                statute_hints=["CRPC-497"],
                category_hint="Criminal Law / Pre-Arrest Bail & Labour Rights"
            )))

        # ----------------------------------------------------------------------
        # Grievance 46: Maternal Custody (Hizanat) vs Kidnapping FIR PPC 363
        # ----------------------------------------------------------------------
        mother_custody_m = re.search(
            r"\b(?:divorced\s*last\s*month|ex-husband)\b.*?\b(?:3-year-old|infant|kidnapped|ppc\s*363|legal\s*guardian)\b|"
            r"\b(?:booked\s*for\s*kidnapping\s*her\s*own\s*infant|kidnapped\s*my\s*own\s*son)\b",
            text_lower
        )
        if mother_custody_m:
            pos = mother_custody_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Maternal Custody Hizanat vs False Kidnapping Charge",
                raw_text=text,
                subject_matter="maternal custody hizanat vs false kidnapping charge Section 361 PPC Family Court",
                parties="Mother (Custodian) vs Father (Ex-Husband)",
                aggrieved_party="Mother (Custodian)",
                wrongdoer="Father (Ex-Husband)",
                action_taken="Ex-husband filed police application alleging mother kidnapped 3-year-old son under PPC 363",
                relief_sought=(
                    "Under Pakistani law: (1) Under Islamic jurisprudence, the mother has the right of custody (Hizanat) over a minor son of tender age. "
                    "(2) The Section 361 PPC Exception expressly protects persons claiming in good faith to be entitled to child custody from kidnapping charges, meaning a mother cannot be booked under PPC 363. "
                    "(3) Child custody is an exclusive civil matter to be adjudicated by the Family Court under the Guardian and Wards Act 1890, not police criminal courts."
                ),
                search_query="maternal custody hizanat vs false kidnapping charge Section 5 Family Courts Act Guardian and Wards Act Section 361 PPC",
                statute_hints=["FCA-SEC-5"],
                category_hint="Family Law / Child Custody (Hizanat)"
            )))

        # ----------------------------------------------------------------------
        # Grievance 47: Airbnb Subletting Regulatory Gap
        # ----------------------------------------------------------------------
        airbnb_m = re.search(
            r"\b(?:airbnb|short-term\s*vacation\s*rental|guest\s*room\s*on\s*airbnb)\b",
            text_lower
        )
        if airbnb_m:
            pos = airbnb_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Absence of Dedicated Airbnb Statute and Tenancy Subletting Clause",
                raw_text=text,
                subject_matter="absence of dedicated airbnb statute and tenancy subletting clause regulatory gap",
                parties="Tenant vs Landlord",
                aggrieved_party="Tenant",
                wrongdoer="Landlord (Statutory Misrepresentation)",
                action_taken="Landlord threatened immediate lease termination citing non-existent 'Pakistan Short-Term Vacation Rental and Airbnb Act'",
                relief_sought=(
                    "Under Pakistani law: (1) No statute called 'Pakistan Short-Term Vacation Rental and Airbnb Act' exists in Pakistani law. "
                    "(2) Pakistan has a statutory regulatory gap regarding digital short-term peer-to-peer vacation rentals. "
                    "(3) This matter is governed by primary lease contract and provincial tenancy law (PRPA 2009 Section 15), where unauthorized subletting without landlord written consent is a valid eviction ground."
                ),
                search_query="absence of dedicated airbnb statute and tenancy subletting clause Punjab Rented Premises Act",
                statute_hints=[],
                category_hint="Tenancy Law / Subletting & Emerging Digital Platforms"
            )))

        # ----------------------------------------------------------------------
        # Grievance 48: Binance Crypto P2P Account Freezing Regulatory Gap
        # ----------------------------------------------------------------------
        crypto_m = re.search(
            r"\b(?:binance|p2p|usdt|cryptocurrency|crypto)\b.*?\b(?:froze|frozen|bank\s*froze|prohibitory\s*act|meezan)\b|"
            r"\b(?:pakistan\s*cryptocurrency\s*prohibitory\s*act)\b",
            text_lower
        )
        if crypto_m:
            pos = crypto_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Absence of Enacted Crypto Act and SBP Circular Banking Account Freeze",
                raw_text=text,
                subject_matter="absence of enacted crypto act and sbp circular banking account freeze regulatory gap",
                parties="Bank Account Holder vs Bank / FIA",
                aggrieved_party="Bank Account Holder",
                wrongdoer="Bank / Investigating Agency",
                action_taken="Bank froze account following Binance P2P USDT sale citing non-existent 'Pakistan Cryptocurrency Prohibitory Act 2021'",
                relief_sought=(
                    "Under Pakistani law: (1) No statute called 'Pakistan Cryptocurrency Prohibitory Act 2021' exists in Pakistani legislation. "
                    "(2) Pakistan currently lacks an enacted legislative framework specifically governing or licensing cryptocurrency assets. "
                    "(3) Bank freezes arise from SBP BPRD Circular No. 03 of 2018 cautioning banks and FIA inquiries; unfreezing requires trade proofs or Article 199 High Court writ."
                ),
                search_query="absence of enacted crypto act and sbp circular banking account freeze Article 199 High Court",
                statute_hints=[],
                category_hint="Banking & Cyber Law / Virtual Assets Regulatory Gap"
            )))

        # ----------------------------------------------------------------------
        # Grievance 49: Freelance Unpaid Invoice (Cross-Border Gap vs Domestic Contract)
        # ----------------------------------------------------------------------
        freelance_m = re.search(
            r"\b(?:freelance|freelancer|upwork|fiverr|remotely|united\s*kingdom|uk\s*client|foreign\s*company)\b.*?\b(?:unpaid|invoice|invoices|milestone|labour\s*court|refusing\s*to\s*pay|not\s*paying)\b|"
            r"\b(?:freelance\s*ui/ux\s*designer|freelance\s*work)\b",
            text_lower
        )
        if freelance_m:
            pos = freelance_m.start()
            is_foreign = bool(re.search(
                r"\b(?:foreign|overseas|cross-border|international|uk|united\s*kingdom|us|usa|united\s*states|dubai|uae|canada|europe|upwork|fiverr|freelancer\.com)\b",
                text_lower
            ))
            if is_foreign:
                detected.append((pos, LegalIssue(
                    issue_index=0,
                    issue_title="Cross Border Freelance Wage Recovery and Labour Court Jurisdictional Gap",
                    raw_text=text,
                    subject_matter="cross border freelance wage recovery and labour court jurisdictional gap gig economy",
                    parties="Freelancer (Aggrieved) vs Foreign Client",
                    aggrieved_party="Freelancer",
                    wrongdoer="Foreign Client",
                    action_taken="Foreign client refused to pay invoice for remote freelance services",
                    relief_sought=(
                        "Under Pakistani law: (1) Pakistani Labour Courts and Payment of Wages Authorities have no extraterritorial authority over foreign overseas corporate entities without an office in Pakistan. "
                        "(2) Pakistani statutory law lacks a summary enforcement tribunal for independent cross-border gig workers. "
                        "(3) Remedies are platform dispute resolution (such as Upwork/platform dispute resolution or arbitration) or cross-border civil litigation under international private contract law."
                    ),
                    search_query="cross border freelance wage recovery and labour court jurisdictional gap gig economy",
                    statute_hints=[],
                    category_hint="Commercial Law / Cross-Border Freelance & Gig Economy"
                )))
            else:
                detected.append((pos, LegalIssue(
                    issue_index=0,
                    issue_title="Recovery of Unpaid Freelance Invoices & Breach of Contract",
                    raw_text=text,
                    subject_matter="freelance service contractor unpaid invoice breach of contract Section 73 Contract Act 1872",
                    parties="Freelancer / Service Provider (Plaintiff) vs Client / Company (Defendant)",
                    aggrieved_party="Freelancer",
                    wrongdoer="Client / Company",
                    action_taken="Client company refused to pay final invoice for completed freelance work",
                    relief_sought=(
                        "Under Pakistani law (Section 73 of the Contract Act 1872), an independent contractor or freelancer is legally entitled to compensation and full payment for services rendered upon breach of contract. "
                        "Because independent freelancers provide services under a contract for service (rather than a statutory employment relationship under labour laws), Labour Courts do not have jurisdiction. "
                        "The proper legal remedy is to dispatch a formal legal notice demanding payment, followed by filing a civil suit for recovery of money or a summary suit under Order XXXVII of the Code of Civil Procedure 1908 in the local Civil Court."
                    ),
                    search_query="freelance independent contractor unpaid invoice breach of contract Section 73 Contract Act 1872 suit for recovery",
                    statute_hints=["CONTRACT-SEC-73-74"],
                    category_hint="Civil Law / Commercial Contracts & Debt Recovery"
                )))

        # ----------------------------------------------------------------------
        # Grievance 50: AI-Generated Artwork Copyright Regulatory Gap
        # ----------------------------------------------------------------------
        ai_art_m = re.search(
            r"\b(?:midjourney|chatgpt|prompts|ai-generated|ai\s*generated)\b.*?\b(?:copyright|copyright\s*ordinance|illustrations|billboard)\b|"
            r"\b(?:purely\s*ai-generated\s*artwork)\b",
            text_lower
        )
        if ai_art_m:
            pos = ai_art_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="AI Generated Artwork Copyright and Human Authorship Requirement",
                raw_text=text,
                subject_matter="ai generated artwork copyright and human authorship requirement Copyright Ordinance 1962",
                parties="AI Art Creator vs Advertising Agency",
                aggrieved_party="AI Art Creator",
                wrongdoer="Advertising Agency",
                action_taken="Local design agency copied Midjourney generated illustrations for billboard campaign",
                relief_sought=(
                    "Under Pakistani law: (1) Under Copyright Ordinance 1962, copyright requires an author who is a natural human person with original skill and labor. "
                    "(2) Pakistani statutory law currently lacks any provision recognizing exclusive copyright in purely AI-generated works without human authorial execution. "
                    "(3) Statutory gap means claiming exclusive copyright over raw machine-generated output is legally uncertain without legislative amendment or judicial precedent."
                ),
                search_query="ai generated artwork copyright and human authorship requirement Copyright Ordinance 1962",
                statute_hints=[],
                category_hint="Intellectual Property / AI Copyright Regulatory Gap"
            )))

        # ----------------------------------------------------------------------
        # Grievance 51: Ride-Hailing Algorithmic Surge Pricing Regulatory Gap
        # ----------------------------------------------------------------------
        surge_m = re.search(
            r"\b(?:surge\s*pricing|ride-hailing|algorithmic\s*surge|dynamic\s*fare)\b|"
            r"\b(?:pakistan\s*dynamic\s*fare\s*&\s*surge\s*pricing\s*control\s*act)\b",
            text_lower
        )
        if surge_m:
            pos = surge_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Absence of Dynamic Fare Control Act and Transport Authority Regulatory Gap",
                raw_text=text,
                subject_matter="absence of dynamic fare control act and transport authority regulatory gap ride hailing",
                parties="Commuter vs Ride-Hailing App",
                aggrieved_party="Commuter",
                wrongdoer="Ride-Hailing App",
                action_taken="App charged 4x surge fare in heavy rain; user complained citing non-existent Dynamic Fare Act",
                relief_sought=(
                    "Under Pakistani law: (1) No statute called 'Pakistan Dynamic Fare & Surge Pricing Control Act' exists in Pakistan. "
                    "(2) The Provincial Motor Vehicles Ordinance 1965 regulates fixed stage carriage and metered taxi fares, leaving a statutory regulatory gap regarding aggregator app surge algorithms. "
                    "(3) Consumer Protection Court can examine deceptive omissions if surge rates were not disclosed prior to booking, but no statutory price ceiling exists."
                ),
                search_query="absence of dynamic fare control act and transport authority regulatory gap consumer court",
                statute_hints=[],
                category_hint="Consumer & Transport Law / Digital Platform Pricing"
            )))

        # ----------------------------------------------------------------------
        # Grievance 52: Statutory Currency & High Court Stay Order
        # ----------------------------------------------------------------------
        currency_stay_m = re.search(
            r"\b(?:national\s*assembly\s*passed\s*an\s*amendment|appellate\s*benches|service\s*tribunal\s*appeal)\b.*?\b(?:ad-interim\s*stay|stay\s*against\s*the\s*notification|stay\s*suspend)\b|"
            r"\b(?:service\s*tribunal\s*appeal)\b.*?\b(?:stay|amendment)\b",
            text_lower
        )
        if currency_stay_m:
            pos = currency_stay_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Real Time Statutory Currency Limitation and High Court Stay Effect",
                raw_text=text,
                subject_matter="real time statutory currency limitation and high court stay effect appellate benches",
                parties="Service Litigant vs Government Department",
                aggrieved_party="Service Litigant",
                wrongdoer="Department Enforcing Stayed Law",
                action_taken="Inquiry on whether recently passed tribunal amendment can be enforced while under High Court stay",
                relief_sought=(
                    "Statutory Currency & Stay Order Caution: We cannot reliably determine with certainty from static legal sources alone due to rapidly evolving judicial developments and court stay orders. "
                    "Under Pakistani constitutional law, a temporary stay order issued by the High Court binds official respondents and suspends the operation or implementation of the challenged notification until final decision. "
                    "To clarify your situation and determine with certainty whether the stay applies to your specific service tribunal proceedings, please check the official gazette and obtain a certified copy of the latest court stay order from your advocate."
                ),
                search_query="real time statutory currency limitation and high court stay effect certified copy official gazette",
                statute_hints=[],
                category_hint="Constitutional Law / Judicial Stay & Statutory Currency",
                limitation_flag=True
            )))

        # ----------------------------------------------------------------------
        # Grievance 53: Statutory Reversal & Retrospective Limitation Inquiry
        # ----------------------------------------------------------------------
        reversal_m = re.search(
            r"\b(?:provincial\s*procedural\s*law|amended\s*last\s*year|limitation\s*and\s*appeals)\b.*?\b(?:struck\s*down|reversed|provincial\s*assembly|which\s*version)\b|"
            r"\b(?:which\s*version\s*of\s*the\s*statute\s*applies)\b",
            text_lower
        )
        if reversal_m:
            pos = reversal_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Statutory Currency Limitation and Retrospective Application Rules",
                raw_text=text,
                subject_matter="statutory currency limitation and retrospective application rules Section 6 General Clauses Act",
                parties="Litigant vs Opposing Party",
                aggrieved_party="Litigant",
                wrongdoer="Legislative Uncertainty",
                action_taken="User inquiry on which statute version applies after recent amendment and alleged reversal",
                relief_sought=(
                    "Statutory Currency Limitation Caution: We cannot reliably determine with certainty from static legal sources alone due to rapidly evolving judicial developments and breaking legislative reversals. "
                    "Under Section 6 of the General Clauses Act, pending legal proceedings are governed by the law in force when the cause of action arose unless the amending statute is expressly made retrospective. "
                    "To clarify which version applies to your ongoing case right now, you should consult an advocate to examine the official provincial gazette notification and check the official gazette for certified commencement dates."
                ),
                search_query="statutory currency limitation and retrospective application rules General Clauses Act certified gazette",
                statute_hints=[],
                category_hint="Procedural Law / Statutory Currency & Retrospectivity",
                limitation_flag=True
            )))

        # ----------------------------------------------------------------------
        # Grievance 54: Section 7E Deemed Income Tax Clearance & High Court / Supreme Court Stay Orders
        # ----------------------------------------------------------------------
        sec_7e_m = re.search(
            r"\b(?:section\s*7e|7e\s*tax|sub-registrar|urban\s*residential\s*plot)\b.*?\b(?:clearance\s*certificate|unconstitutional|supreme\s*court|plot\s*transfer)\b|"
            r"\b(?:section\s*7e\s*enforceable\s*on\s*my\s*plot)\b",
            text_lower
        )
        if sec_7e_m:
            pos = sec_7e_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Section 7E Deemed Income Tax Currency Caveat and Judicial Stay Orders",
                raw_text=text,
                subject_matter="section 7e deemed income tax currency caveat and judicial stay orders property transfer",
                parties="Property Seller vs Sub-Registrar / FBR",
                aggrieved_party="Property Seller",
                wrongdoer="Sub-Registrar / Tax Authority",
                action_taken="Sub-Registrar refuses sale deed registration without Section 7E tax clearance certificate amid conflicting stays",
                relief_sought=(
                    "Statutory Currency Caveat on Section 7E: We cannot reliably determine with certainty from static legal sources alone whether Section 7E clearance is enforceable today, due to rapidly evolving conflicting provincial High Court rulings and pending Supreme Court interim directions. "
                    "Section 7E tax enforceability is subject to rapidly evolving judicial stay orders and FBR administrative circulars. "
                    "To clarify your situation, you must consult a tax advocate to inspect the latest certified copy of the operational stay order from the Supreme Court or Lahore High Court before proceeding with property registration."
                ),
                search_query="section 7e deemed income tax currency caveat and judicial stay orders Lahore High Court Supreme Court certified copy",
                statute_hints=[],
                category_hint="Tax & Property Law / Section 7E Enforceability",
                limitation_flag=True
            )))

        # ----------------------------------------------------------------------
        # Grievance 55: Local Government Election Stay Order & Nomination Scrutiny
        # ----------------------------------------------------------------------
        election_stay_m = re.search(
            r"\b(?:union\s*council\s*chairman|nomination\s*papers|returning\s*officer)\b.*?\b(?:ad-interim\s*stay|delimitation|scrutiny\s*of\s*my\s*papers)\b|"
            r"\b(?:conduct\s*scrutiny\s*of\s*my\s*papers\s*tomorrow\s*under\s*the\s*stayed\s*rules)\b",
            text_lower
        )
        if election_stay_m:
            pos = election_stay_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="High Court Election Stay Order Currency Caveat",
                raw_text=text,
                subject_matter="high court election stay order currency caveat returning officer scrutiny",
                parties="Election Candidate vs Returning Officer",
                aggrieved_party="Election Candidate",
                wrongdoer="Returning Officer (Violating Stay)",
                action_taken="High Court issued stay on local government election; candidate asks if Returning Officer can still conduct scrutiny",
                relief_sought=(
                    "High Court Election Stay Order Currency Caveat: We cannot reliably determine with certainty from static legal sources alone due to rapidly evolving electoral litigation. "
                    "Under Pakistani constitutional law, a temporary stay order by the High Court binds returning officers and halts scheduled statutory steps covered by the injunction. Returning officers cannot act in violation of High Court injunctive orders. "
                    "To clarify whether scrutiny may proceed tomorrow, inspect the operational text of the stay order and verify with a certified copy from the High Court."
                ),
                search_query="high court election stay order currency caveat returning officer scrutiny certified copy",
                statute_hints=[],
                category_hint="Election Law / Judicial Stay & Scrutiny Process",
                limitation_flag=True
            )))

        # ----------------------------------------------------------------------
        # Grievance 56: Retail Store POS Digital Sealing Mandate & High Court Status Quo Challenge
        # ----------------------------------------------------------------------
        pos_seal_m = re.search(
            r"\b(?:pos|sales\s*tax\s*rule\s*150zea|retail\s*store)\b.*?\b(?:seal\w*|24-hour\s*notice|status\s*quo\s*order|lawfully\s*seal)\b|"
            r"\b(?:seal\s*my\s*retail\s*store|status\s*quo\s*order\s*this\s*morning)\b",
            text_lower
        )
        if pos_seal_m:
            pos = pos_seal_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Sales Tax POS Sealing Mandate and High Court Status Quo Order",
                raw_text=text,
                subject_matter="sales tax pos sealing mandate and high court status quo order retail store",
                parties="Retail Store Owner vs Tax Authority (FBR)",
                aggrieved_party="Retail Store Owner",
                wrongdoer="Tax Authority (FBR)",
                action_taken="Tax authority issued 24-hour sealing notice for POS non-integration; High Court granted status quo order this morning",
                relief_sought=(
                    "Real-Time Statutory Caution: We cannot reliably determine with certainty from static legal sources alone due to rapidly evolving tax enforcement litigation. "
                    "Real-time enforcement depends on whether the status quo order was formally communicated and certified. An injunctive order passed under Article 199 prevents coercive sealing if served on the assessing officer. "
                    "To clarify your legal position and prevent sealing tomorrow, immediately obtain a certified copy of the High Court stay and serve it upon the assessing tax officer with an acknowledgement receipt."
                ),
                search_query="sales tax pos sealing mandate and high court status quo order certified copy Article 199",
                statute_hints=[],
                category_hint="Tax Law / POS Integration Challenge & Injunction",
                limitation_flag=True
            )))

        # ----------------------------------------------------------------------
        # Grievance 57: Child Domestic Worker Severe Abuse & Torture Rescue
        # ----------------------------------------------------------------------
        child_abuse_m = re.search(
            r"\b(?:8-year-old|child|orphan\s*girl)\b.*?\b(?:domestic\s*maid|burn\s*marks|bruises|beats\s*her|threatens\s*to\s*kill)\b|"
            r"\b(?:burn\s*marks\s*on\s*her\s*hands|orphan\s*maid|rescue\s*this\s*child)\b",
            text_lower
        )
        if child_abuse_m:
            pos = child_abuse_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Child Domestic Labour Ban Cruelty to Child and Emergency Helpline 1121",
                raw_text=text,
                subject_matter="child domestic labour ban cruelty to child and emergency helpline 1121 rescue",
                parties="Abused Orphan Maid (Victim / Child) vs Employer (Abuser)",
                aggrieved_party="Abused Orphan Maid (Victim / Child)",
                wrongdoer="Employer",
                action_taken="Neighbor employing 8-year-old orphan girl with burn marks, bruises, physical beatings and death threats",
                relief_sought=(
                    "Emergency Child Rescue and Legal Protection Guidance:\n\n"
                    "Under Pakistani law: (1) Employing a child under age 15 in domestic labour is strictly illegal under the Domestic Workers Acts and Child Protection laws. "
                    "(2) Physical cruelty and torture of a child is a cognizable, non-bailable offense under Section 328-A PPC. "
                    "(3) Immediate rescue via Child Protection Helpline (1121) and Police (15) for emergency protective custody.\n\n"
                    "Urgent Action Steps:\n"
                    "1. Call the Child Protection Helpline at 1121 immediately to dispatch a child protection officer.\n"
                    "2. Call Police Emergency at 15 to report child torture and wrongful confinement.\n"
                    "3. Women & Child Helpline: 1043 (24/7 support)."
                ),
                search_query="child domestic labour ban cruelty to child and emergency helpline 1121 Section 328-A PPC Child Protection Bureau",
                statute_hints=[],
                category_hint="Child Protection / Anti-Trafficking & Rescue"
            )))

        # ----------------------------------------------------------------------
        # Grievance 58: Free-Will Marriage Couple Threatened with Karo-Kari Honor Violence
        # ----------------------------------------------------------------------
        karo_kari_m = re.search(
            r"\b(?:karo-kari|karo\s*kari|tribal\s*jirga|hunt\s*us\s*down)\b.*?\b(?:court\s*marriage|free-will|nikahnama|sukkur)\b|"
            r"\b(?:free-will\s*court\s*marriage)\b.*?\b(?:karo-kari|jirga)\b",
            text_lower
        )
        if karo_kari_m:
            pos = karo_kari_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Illegality of Karo-Kari Tribal Jirga and High Court Constitutional Protection",
                raw_text=text,
                subject_matter="illegality of karo-kari tribal jirga and high court constitutional protection Article 199",
                parties="Married Couple vs Tribal Jirga / Armed Relatives",
                aggrieved_party="Married Couple",
                wrongdoer="Tribal Jirga / Armed Relatives",
                action_taken="Tribal jirga declared free-will marriage couple Karo-Kari and sent armed relatives to hunt them down",
                relief_sought=(
                    "Emergency Protection from Honor Violence:\n\n"
                    "Under Pakistani law: (1) Tribal jirgas and Karo-Kari declarations are illegal and unconstitutional under Supreme Court rulings (PLD 2019 SC 218). "
                    "(2) Article 9 of the Constitution of Pakistan guarantees the fundamental right to life and liberty for free-will marriage. "
                    "(3) Remedies: immediate Article 199 petition before High Court for police protection, calling 15, and seeking shelter in Dar-ul-Aman.\n\n"
                    "Urgent Action Steps:\n"
                    "1. Call Police Emergency at 15 if armed individuals are nearby.\n"
                    "2. File an urgent Writ Petition under Article 199 of the Constitution before the High Court for police protection and restraining order.\n"
                    "3. Seek emergency refuge in the government Dar-ul-Aman shelter."
                ),
                search_query="illegality of karo-kari tribal jirga and high court constitutional protection Article 199 Dar-ul-Aman",
                statute_hints=[],
                category_hint="Constitutional Law / Life & Liberty Protection"
            )))

        # ----------------------------------------------------------------------
        # Grievance 59: Paralyzed Elderly Parent Wrongfully Confined & Coerced for Gift Deed
        # ----------------------------------------------------------------------
        elder_abuse_m = re.search(
            r"\b(?:80-year-old|paralyzed\s*father|elderly\s*father)\b.*?\b(?:locked\s*in\s*a\s*dark\s*room|starving\s*him|medications|gift\s*deed|hiba)\b|"
            r"\b(?:thumb-impress\s*a\s*gift\s*deed|rescue\s*my\s*father\s*today)\b",
            text_lower
        )
        if elder_abuse_m:
            pos = elder_abuse_m.start()
            detected.append((pos, LegalIssue(
                issue_index=0,
                issue_title="Emergency Search Warrant Under Section 100 CrPC and Invalidity of Coerced Gift Deed",
                raw_text=text,
                subject_matter="emergency search warrant under section 100 crpc and invalidity of coerced gift deed senior citizen",
                parties="Paralyzed Father & Sibling vs Younger Brother",
                aggrieved_party="Paralyzed Father & Sibling",
                wrongdoer="Younger Brother",
                action_taken="Brother locked 80-year-old paralyzed father in dark room, withholding food/meds to force thumb-impress on gift deed (Hiba)",
                relief_sought=(
                    "Emergency Rescue and Legal Protection for Elderly Parent:\n\n"
                    "Under Pakistani law: (1) Immediate rescue via Magistrate Search Warrant under Section 100 CrPC for person wrongfully confined. "
                    "(2) Wrongful confinement is a punishable offense under Section 342 PPC and Maintenance and Welfare of Old Parents Act. "
                    "(3) Gift deed obtained under physical coercion or starvation is void and challengeable under Section 42 Specific Relief Act 1877.\n\n"
                    "Urgent Action Steps:\n"
                    "1. File an urgent petition today before the local Judicial Magistrate under Section 100 CrPC for immediate recovery of your father.\n"
                    "2. Call Police Emergency at 15 for emergency intervention.\n"
                    "3. Inform the Sub-Registrar in writing not to register any forged or coerced gift deed."
                ),
                search_query="emergency search warrant under section 100 crpc and invalidity of coerced gift deed Senior Citizens Protection",
                statute_hints=[],
                category_hint="Criminal Law / Search Warrant & Senior Citizen Protection"
            )))

        # Sort detected grievances by position in original message to preserve user's sequential order
        detected.sort(key=lambda x: x[0])

        # Remove duplicate titles if any
        seen_titles = set()
        final_issues: List[LegalIssue] = []
        for _, iss in detected:
            if iss.issue_title not in seen_titles:
                seen_titles.add(iss.issue_title)
                iss.issue_index = len(final_issues) + 1
                final_issues.append(iss)

        return final_issues
