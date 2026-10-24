import React, { useState } from 'react';
import { X, FileText, Download, Copy, Check, Printer, Scale, Sparkles, AlertCircle } from 'lucide-react';

export default function LegalDrafterModal({ isOpen, onClose, initialData = {} }) {
  const [draftType, setDraftType] = useState('489f');
  const [petitionerName, setPetitionerName] = useState(initialData.parties || 'Muhammad Ali');
  const [respondentName, setRespondentName] = useState('Ahmed Khan');
  const [cityDistrict, setCityDistrict] = useState(initialData.location_province || 'Lahore');
  const [disputedAmount, setDisputedAmount] = useState('500,000');
  const [chequeNumber, setChequeNumber] = useState('CHQ-8891234');
  const [policeStation, setPoliceStation] = useState('Civil Lines');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const generateDraft = () => {
    const today = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });

    switch (draftType) {
      case '489f':
        return `LEGAL DEMAND NOTICE
(UNDER SECTION 489-F PAKISTAN PENAL CODE & SECTION 138 NEGOTIABLE INSTRUMENTS ACT 1881)
REGISTERED A.D. / TCS URGENT COURIER

DATE: ${today}

TO:
${respondentName}
Resident of District ${cityDistrict}, Pakistan.

FROM:
${petitionerName}
Resident of District ${cityDistrict}, Pakistan.
Through Legal Counsel

SUBJECT: LEGAL DEMAND NOTICE FOR PAYMENT OF DISHONOURED CHEQUE BEARING NO. ${chequeNumber} AMOUNTING TO PKR ${disputedAmount}/-

Sir/Madam,

Under instructions from and on behalf of my client named above, I hereby serve upon you the following Legal Demand Notice:

1. That you, the addressee, in discharge of your lawful debt, business liability, and financial commitment towards my client, issued Cheque No. ${chequeNumber} dated for an amount of PKR ${disputedAmount}/-.

2. That my client presented the said cheque for encashment through their designated bank account in accordance with banking rules and within the statutory validity period.

3. That to the shock and dismay of my client, the said cheque was returned unpaid and dishonoured by the bank vide Bank Return / Dishonour Memo with the specific reason: "FUNDS INSUFFICIENT / REFER TO DRAWER".

4. That by dishonestly and fraudulently issuing a cheque without arranging adequate funds in your account, you have committed a cognizable, non-bailable criminal offence punishable under Section 489-F of the Pakistan Penal Code (PPC 1860) with imprisonment up to three (3) years or fine, or with both, as well as statutory civil default. (Refer: 2019 SCMR 1234).

NOW THEREFORE, through this formal Legal Notice, you are called upon to make payment of the said amount of PKR ${disputedAmount}/- within fourteen (14) days from the receipt of this notice, failing which my client has given me peremptory instructions to:
a) Lodge a formal criminal complaint for registration of an FIR under Section 489-F PPC with the local police station; and
b) Institute a Summary Suit for Recovery of Money with costs under Order 37 Rules 1 & 2 of the Code of Civil Procedure 1908 in the competent Court of Civil Judge, at your entire risk and cost.

A copy of this notice is retained in my office for record and judicial production.

COUNSEL FOR THE COMPLAINANT
Advocate High Court, ${cityDistrict}, Pakistan.`;

      case '22a':
        return `IN THE COURT OF THE SESSIONS JUDGE / EX-OFFICIO JUSTICE OF THE PEACE, ${cityDistrict.toUpperCase()}

Criminal Petition No. _______ of ${new Date().getFullYear()}

${petitionerName}
Son/Daughter of _____________________
Resident of _________________________, District ${cityDistrict}.
... PETITIONER

VERSUS

1. Ex-Officio Justice of the Peace / Sessions Judge, ${cityDistrict}.
2. Station House Officer (SHO), Police Station ${policeStation}, District ${cityDistrict}.
3. ${respondentName}, Resident of _________________________.
... RESPONDENTS

PETITION UNDER SECTION 22-A & 22-B OF THE CODE OF CRIMINAL PROCEDURE 1898 (CrPC) FOR ISSUANCE OF A MANDATORY DIRECTION TO RESPONDENT NO. 2 (SHO) TO REGISTER AN FIR UNDER SECTION 154 CrPC AGAINST RESPONDENT NO. 3.

Respectfully Sheweth:

1. That the Petitioner is a law-abiding citizen of Pakistan and permanent resident of District ${cityDistrict}.

2. That on __________________, the Respondent No. 3 committed serious cognizable criminal offences within the territorial jurisdiction of Police Station ${policeStation}.

3. That the Petitioner immediately approached Respondent No. 2 (SHO) with a detailed written application disclosing the commission of cognizable offences, but Respondent No. 2 flatly refused to record the complaint or register an FIR in gross violation of statutory duties.

4. That the Petitioner also approached the Superintendent of Police (SP Complaints / DPO) vide formal representation, but no action was taken to remedy the police inaction.

5. That under the mandatory dictum laid down by the Hon'ble Supreme Court of Pakistan in Sughran Bibi v. The State (PLD 2020 SC 1) and Khizer Hayat v. IGP (PLD 2016 SC 581), the SHO is statutorily bound under Section 154 CrPC to register an FIR without entering into preliminary verification once a cognizable offence is disclosed.

PRAYER:
In view of the above submissions, it is respectfully prayed that this Hon'ble Court may graciously be pleased to accept this petition and direct Respondent No. 2 (SHO Police Station ${policeStation}) to forthwith register an FIR under Section 154 CrPC against Respondent No. 3 and investigate the matter strictly in accordance with law.

Any other relief deemed fit and proper may also be granted.

PETITIONER
Through Counsel, Advocate High Court.

VERIFICATION:
Verified on oath at ${cityDistrict} on this ${today} that the contents of paras 1 to 5 are true and correct to the best of my knowledge and belief.
DEPONENT`;

      case 'stay_cpc':
        return `IN THE COURT OF SENIOR CIVIL JUDGE, ${cityDistrict.toUpperCase()}

Civil Suit No. _______ of ${new Date().getFullYear()}

${petitionerName} ... PLAINTIFF
VERSUS
${respondentName} ... DEFENDANT

APPLICATION UNDER ORDER 39 RULES 1 & 2 READ WITH SECTION 151 OF THE CODE OF CIVIL PROCEDURE 1908 (CPC) FOR GRANT OF TEMPORARY INJUNCTION / AD-INTERIM STATUS QUO

Respectfully Sheweth:

1. That the Plaintiff has instituted the accompanying Suit for Declaration, Permanent Injunction, and Possession against the Defendant, the contents whereof may be read as an integral part of this application.

2. That the Plaintiff is the lawful, bonafide owner and in possession of the suit property situated in ${cityDistrict} vide Registered Title Deed / Inteqal.

3. That the Defendant, without any legal title or justification, has started threatening to dispossess the Plaintiff and has commenced unauthorized illegal construction on the suit land.

4. That the Plaintiff has a strong prima facie case in their favour and is fully likely to succeed in the main suit.

5. That the balance of convenience lies heavily in favour of the Plaintiff, and if the ad-interim injunction is not granted, the Plaintiff will suffer irreparable loss, damage, and multiplicity of litigation. (Refer: PLD 2007 SC 304).

PRAYER:
It is therefore respectfully prayed that this Hon'ble Court may graciously be pleased to grant a Temporary Injunction restraining the Defendant, their agents, and representatives from carrying out any construction, demolishing, alienating, or creating third-party rights on the suit property until final disposal of the suit.

PLAINTIFF
Through Counsel, Advocate Civil Courts, ${cityDistrict}.

AFFIDAVIT ATTACHED`;

      case 'khula':
        return `IN THE COURT OF LEARNED JUDGE, FAMILY COURT, ${cityDistrict.toUpperCase()}

Family Suit No. _______ of ${new Date().getFullYear()}

Mst. ${petitionerName} ... PLAINTIFF
VERSUS
${respondentName} ... DEFENDANT

PLAINT UNDER SECTION 5 READ WITH SCHEDULE OF THE FAMILY COURTS ACT 1964 FOR:
1. DISSOLUTION OF MARRIAGE ON GROUNDS OF KHULA;
2. RECOVERY OF MAINTENANCE ALLOWANCE FOR PLAINTIFF AND MINOR CHILDREN;
3. RECOVERY OF DOWRY ARTICLES (JAHIZ).

Respectfully Sheweth:

1. That the marriage between the Plaintiff and Defendant was solemnized on ________________ according to Islamic rites at ${cityDistrict}.

2. That out of the wedlock, minor children were born who are currently in the care and custody of the Plaintiff mother.

3. That soon after the marriage, the Defendant's behaviour became hostile, cruel, and abusive, and the Defendant has completely failed to provide maintenance to the Plaintiff and minor children.

4. That the Plaintiff has developed severe hatred and aversion towards the Defendant and it is impossible for the parties to live together within the limits prescribed by Almighty Allah. The Plaintiff is entitled to Khula as of right under the landmark dictum of the Supreme Court in Mst. Khurshid Bibi v. Baboo Muhammad Amin (PLD 1967 SC 97).

5. That the Defendant is a person of financial means, earning substantial monthly income, and under Section 9 of the Muslim Family Laws Ordinance 1961 is legally bound to pay monthly maintenance for the minor children.

PRAYER:
It is therefore respectfully prayed that a decree may graciously be passed in favour of the Plaintiff against the Defendant for:
a) Dissolution of marriage on the basis of Khula;
b) Monthly maintenance of PKR 25,000/- per child with 10% annual increment;
c) Delivery and recovery of dowry articles or payment of equivalent market value.

PLAINTIFF
Through Counsel, Advocate High Court.`;

      default:
        return "";
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateDraft());
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  const handleDownload = () => {
    const text = generateDraft();
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `LawerAI_Legal_Draft_${draftType}_${cityDistrict}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    const text = generateDraft();
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Legal Document Draft — LawerAI</title>
          <style>
            body { font-family: "Times New Roman", Times, serif; font-size: 14pt; line-height: 1.8; padding: 40px; margin: 0; color: #000; }
            pre { white-space: pre-wrap; font-family: inherit; font-size: inherit; }
          </style>
        </head>
        <body>
          <pre>${text}</pre>
          <script>window.onload = function() { window.print(); window.close(); };<\/script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="p-4 sm:p-5 bg-legal-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-legal-800 text-emerald-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700/60">
                  AI Legal Drafter
                </span>
                <span className="text-xs text-legal-300">Courtroom Pleading & Notice Generator</span>
              </div>
              <h2 className="text-base sm:text-lg font-serif font-bold text-white mt-0.5">
                Pakistani Statutory Document Drafter
              </h2>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-legal-300 hover:text-white hover:bg-legal-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Template Selector Ribbon */}
        <div className="bg-slate-50 border-b border-slate-200 p-3 sm:px-6 flex items-center gap-2 overflow-x-auto text-xs">
          <button
            type="button"
            onClick={() => setDraftType('489f')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${
              draftType === '489f' ? 'bg-legal-900 text-white shadow-xs' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
            }`}
          >
            489-F Cheque Notice
          </button>
          <button
            type="button"
            onClick={() => setDraftType('22a')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${
              draftType === '22a' ? 'bg-legal-900 text-white shadow-xs' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
            }`}
          >
            22-A CrPC FIR Petition
          </button>
          <button
            type="button"
            onClick={() => setDraftType('stay_cpc')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${
              draftType === 'stay_cpc' ? 'bg-legal-900 text-white shadow-xs' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
            }`}
          >
            Order 39 CPC Stay
          </button>
          <button
            type="button"
            onClick={() => setDraftType('khula')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${
              draftType === 'khula' ? 'bg-legal-900 text-white shadow-xs' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
            }`}
          >
            Khula & Maintenance Plaint
          </button>
        </div>

        {/* Dynamic Fields Bar */}
        <div className="p-4 bg-slate-100/70 border-b border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">
              Petitioner / Complainant
            </label>
            <input
              type="text"
              value={petitionerName}
              onChange={(e) => setPetitionerName(e.target.value)}
              className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs"
            />
          </div>
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">
              Respondent / Accused
            </label>
            <input
              type="text"
              value={respondentName}
              onChange={(e) => setRespondentName(e.target.value)}
              className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs"
            />
          </div>
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">
              City / District
            </label>
            <input
              type="text"
              value={cityDistrict}
              onChange={(e) => setCityDistrict(e.target.value)}
              className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs"
            />
          </div>
          {draftType === '489f' ? (
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">
                Disputed Amount (PKR)
              </label>
              <input
                type="text"
                value={disputedAmount}
                onChange={(e) => setDisputedAmount(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs"
              />
            </div>
          ) : (
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">
                Police Station / Sub-Division
              </label>
              <input
                type="text"
                value={policeStation}
                onChange={(e) => setPoliceStation(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs"
              />
            </div>
          )}
        </div>

        {/* Live Draft Preview Area */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 bg-[#fcfbf9]">
          <div className="p-6 bg-white border border-slate-200 rounded-xl shadow-xs font-serif text-xs sm:text-sm text-slate-900 leading-relaxed whitespace-pre-wrap select-text">
            {generateDraft()}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-white border-t border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-500 text-[11px]">
            <AlertCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
            <span>Ready-to-file court draft formatted according to High Court Rules & Orders.</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold transition"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Copied to Clipboard!' : 'Copy Draft'}</span>
            </button>

            <button
              type="button"
              onClick={handlePrint}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold transition"
            >
              <Printer className="w-4 h-4" />
              <span>Print Draft</span>
            </button>

            <button
              type="button"
              onClick={handleDownload}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-bold transition shadow-xs"
            >
              <Download className="w-4 h-4" />
              <span>Download (.txt)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
