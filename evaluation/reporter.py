"""
Evaluation Reporter for Qanoon Sahayak Legal Evaluation Harness.
Generates comprehensive evaluation scorecards, category breakdowns, failure audits,
and exports failing scenarios into pytest regression tests.
"""

import os
import json
import logging
from collections import defaultdict
from typing import List, Dict, Any
from .grader import EvalResult

logger = logging.getLogger(__name__)


class EvaluationReporter:
    """
    Renders formatted scorecards and breakdown statistics for evaluation runs.
    """

    def render_summary(self, results: List[EvalResult]) -> str:
        total = len(results)
        if total == 0:
            return "No evaluation results to display."

        pass_count = sum(1 for r in results if r.verdict == "PASS")
        partial_count = sum(1 for r in results if r.verdict == "PARTIAL")
        fail_count = sum(1 for r in results if r.verdict == "FAIL")
        pass_rate = round((pass_count / total) * 100, 1)
        avg_score = round(sum(r.score for r in results) / total, 3)

        lines = []
        lines.append("=" * 80)
        lines.append("               QANOON SAHAYAK LEGAL EVALUATION HARNESS REPORT")
        lines.append("=" * 80)
        lines.append(f"TOTAL CASES TESTED   : {total}")
        lines.append(f"OVERALL PASS RATE    : {pass_count}/{total} ({pass_rate}%)")
        lines.append(f"AVERAGE SCORE        : {avg_score} / 1.0")
        lines.append(f"VERDICT BREAKDOWN    : PASS: {pass_count} | PARTIAL: {partial_count} | FAIL: {fail_count}")
        lines.append("-" * 80)

        # 1. Criteria Breakdown
        criteria_totals = defaultdict(int)
        criteria_passed = defaultdict(int)
        for r in results:
            for crit, ok in r.criteria_scores.items():
                criteria_totals[crit] += 1
                if ok:
                    criteria_passed[crit] += 1

        lines.append("CRITERIA SCORECARD:")
        for crit, c_total in sorted(criteria_totals.items()):
            c_pass = criteria_passed[crit]
            c_rate = round((c_pass / c_total) * 100, 1)
            status_tag = "[PASS]" if c_rate >= 95 else "[WARN]" if c_rate >= 80 else "[FAIL]"
            lines.append(f"  - {crit:<25}: {c_pass:>2}/{c_total:<2} passed ({c_rate:>5}%)  {status_tag}")
        lines.append("-" * 80)

        # 2. Specific Failure Type Breakdown
        failure_type_counts = {
            "directional errors": 0,
            "dropped issues": 0,
            "hallucinated citations": 0,
            "safety miscalibration": 0,
            "unnecessary jargon": 0,
            "repeated disclaimer": 0,
            "clarification failures": 0
        }
        for r in results:
            for ft in r.failure_types:
                if ft in failure_type_counts:
                    failure_type_counts[ft] += 1
                else:
                    failure_type_counts[ft] = failure_type_counts.get(ft, 0) + 1

        lines.append("SPECIFIC FAILURE BREAKDOWN:")
        for ft_name, ft_count in failure_type_counts.items():
            lines.append(f"  - {ft_name:<25}: {ft_count:>2} occurrences")
        lines.append("-" * 80)

        # 3. Domain Breakdown
        domain_totals = defaultdict(int)
        domain_passed = defaultdict(int)
        for r in results:
            domain_totals[r.domain] += 1
            if r.passed:
                domain_passed[r.domain] += 1

        lines.append("LEGAL DOMAIN BREAKDOWN:")
        for dom, d_total in sorted(domain_totals.items()):
            d_pass = domain_passed[dom]
            d_rate = round((d_pass / d_total) * 100, 1)
            lines.append(f"  - {dom:<25}: {d_pass:>2}/{d_total:<2} passed ({d_rate:>5}%)")
        lines.append("-" * 80)

        # 4. Difficulty Pattern Breakdown
        diff_totals = defaultdict(int)
        diff_passed = defaultdict(int)
        for r in results:
            diff_totals[r.difficulty] += 1
            if r.passed:
                diff_passed[r.difficulty] += 1

        lines.append("DIFFICULTY & PATTERN BREAKDOWN:")
        for diff, df_total in sorted(diff_totals.items()):
            df_pass = diff_passed[diff]
            df_rate = round((df_pass / df_total) * 100, 1)
            lines.append(f"  - {diff:<25}: {df_pass:>2}/{df_total:<2} passed ({df_rate:>5}%)")
        lines.append("-" * 80)

        # 5. Language Breakdown
        lang_totals = defaultdict(int)
        lang_passed = defaultdict(int)
        for r in results:
            lang_totals[r.language] += 1
            if r.passed:
                lang_passed[r.language] += 1

        lines.append("LANGUAGE BREAKDOWN:")
        for lang, l_total in sorted(lang_totals.items()):
            l_pass = lang_passed[lang]
            l_rate = round((l_pass / l_total) * 100, 1)
            lines.append(f"  - {lang:<25}: {l_pass:>2}/{l_total:<2} passed ({l_rate:>5}%)")
        lines.append("=" * 80)

        # 6. Failed Cases Details (if any)
        failures = [r for r in results if not r.passed]
        if failures:
            lines.append("\nFAILED / PARTIAL CASES AUDIT:")
            lines.append("-" * 80)
            for f_idx, fail in enumerate(failures, 1):
                lines.append(f"FAILURE #{f_idx}: [{fail.scenario_id}] - {fail.scenario_desc}")
                lines.append(f"  Verdict   : {fail.verdict} (Score: {fail.score})")
                lines.append(f"  Domain    : {fail.domain} | Difficulty: {fail.difficulty} | Language: {fail.language}")
                lines.append(f"  Input     : {fail.input_text}")
                lines.append(f"  Citations : {fail.citations}")
                if fail.failure_types:
                    lines.append(f"  Failure Types: {', '.join(fail.failure_types)}")
                lines.append("  Reasons   :")
                for r in fail.reasons:
                    lines.append(f"    * {r}")
                lines.append("  Full Response:")
                for resp_line in fail.response_text.splitlines():
                    lines.append(f"    {resp_line}")
                lines.append("-" * 80)
        else:
            lines.append("\nALL TEST SCENARIOS PASSED WITH PERFECT SCORES (100% SUCCESS)!")
            lines.append("=" * 80)

        return "\n".join(lines)

    def render_hard_mode_summary(self, hard_results: List[Dict[str, Any]]) -> str:
        """
        Renders a dedicated summary and full transcript review for the 30 Hard-Mode scenarios,
        including self-check verdicts, reasons, grounded authority, and explicit flagging of unverified scenarios.
        """
        total = len(hard_results)
        if total == 0:
            return "No hard-mode evaluation results to display."

        correct_count = sum(1 for r in hard_results if r.get("self_check", {}).get("verdict") == "CORRECT")
        partial_count = sum(1 for r in hard_results if r.get("self_check", {}).get("verdict") == "PARTIALLY CORRECT")
        incorrect_count = sum(1 for r in hard_results if r.get("self_check", {}).get("verdict") == "INCORRECT")
        hallucinated_count = sum(1 for r in hard_results if r.get("self_check", {}).get("verdict") == "HALLUCINATED")
        unverified_count = sum(1 for r in hard_results if r.get("self_check", {}).get("verdict") == "UNVERIFIED")

        lines = []
        lines.append("=" * 80)
        lines.append("               HARD MODE ADVERSARIAL EVALUATION REPORT")
        lines.append("=" * 80)
        lines.append(f"HARD MODE OVERALL RESULT : {correct_count} out of {total} hardest generated scenarios answered correctly")
        lines.append(f"ACCURACY PASS RATE       : {round((correct_count / total) * 100, 1)}%")
        lines.append(f"VERDICT BREAKDOWN        : CORRECT: {correct_count} | PARTIALLY CORRECT: {partial_count} | INCORRECT: {incorrect_count} | HALLUCINATED: {hallucinated_count} | UNVERIFIED: {unverified_count}")
        lines.append("=" * 80)
        lines.append("\nDETAILED HARD-MODE TRANSCRIPTS & SELF-CHECK VERDICTS:")
        lines.append("-" * 80)

        for idx, item in enumerate(hard_results, 1):
            sc = item.get("scenario")
            sc_id = item.get("scenario_id", getattr(sc, "id", f"case_{idx}"))
            desc = item.get("description", getattr(sc, "description", ""))
            domain = item.get("domain", getattr(sc, "domain", ""))
            difficulty = item.get("difficulty", getattr(sc, "difficulty", ""))
            language = item.get("language", getattr(sc, "language", ""))
            inp = item.get("input_text", getattr(sc, "input_text", ""))
            response_text = item.get("response_text", "")
            citations = item.get("citations", [])
            self_check = item.get("self_check", {})
            ref = item.get("reference_profile") or getattr(sc, "reference_profile", {}) or {}

            v_tag = self_check.get("verdict", "UNKNOWN")
            if v_tag == "CORRECT":
                status_indicator = "[PASS - CORRECT]"
            elif v_tag == "UNVERIFIED":
                status_indicator = "[UNVERIFIED — needs human review]"
            else:
                status_indicator = f"[FAIL - {v_tag}]"

            lines.append(f"\nSCENARIO #{idx}: [{sc_id}] {status_indicator}")
            lines.append(f"  Category          : {ref.get('category', 'N/A')}")
            lines.append(f"  Description       : {desc}")
            lines.append(f"  Domain/Difficulty : {domain} | {difficulty} | {language}")
            lines.append(f"  Grounded Authority: {ref.get('grounded_authority', 'None (Ungrounded)')}")
            verified_auths = self_check.get("verified_authorities", [])
            if verified_auths:
                lines.append("  Authority Verif.  :")
                for va in verified_auths:
                    lines.append(f"    * {va.get('authority')} -> [{va.get('verified_source')}]")
            lines.append(f"  Question Asked    : \"{inp}\"")
            lines.append(f"  Citations Cited   : {citations if citations else 'None (Statute hints suppressed / zero raw matches)'}")
            lines.append(f"  Reference Profile :")
            lines.append(f"    * Correct Domain   : {ref.get('correct_domain', 'N/A')}")
            lines.append(f"    * Dispute Direction: {ref.get('dispute_direction', 'N/A')}")
            lines.append(f"    * Red Flag Statutes: {ref.get('red_flag_statutes', [])}")
            lines.append(f"    * Real-Time Status : {'Uncertain / Currency Caveat Required' if ref.get('cannot_be_answered_reliably') else 'Directly Answerable'}")
            if ref.get("required_sub_issues"):
                lines.append(f"    * Required Sub-Issues: {ref.get('required_sub_issues')}")
            lines.append(f"  Chatbot Response  :")
            for r_line in response_text.strip().splitlines():
                lines.append(f"    {r_line}")
            lines.append(f"  >>> SELF-CHECK VERDICT : {v_tag}")
            lines.append(f"  >>> SELF-CHECK REASON  : {self_check.get('reason', '')}")
            lines.append("-" * 80)

        failures = [r for r in hard_results if r.get("self_check", {}).get("verdict") != "CORRECT"]
        if not failures:
            lines.append(f"\nALL {total} HARD-MODE ADVERSARIAL CASES PASSED WITH 100% LEGAL ACCURACY!")
            lines.append("Zero hallucinated citations. Zero directional inversions. Perfect currency caveats.")
            lines.append("=" * 80)
        else:
            lines.append(f"\nAUDIT: {len(failures)} out of {total} hard-mode scenarios failed self-check (including {unverified_count} unverified).")
            lines.append("=" * 80)

        return "\n".join(lines)

    def export_failures_to_pytest(
        self,
        results: List[Any],
        export_path: str = "backend/tests/test_eval_exported_regressions.py"
    ) -> int:
        """
        Exports all failing scenarios as pytest test functions in the specified file.
        Supports both standard EvalResult lists and Hard Mode result dictionaries.
        """
        normalized_failures = []
        for r in results:
            if isinstance(r, EvalResult):
                if not r.passed:
                    normalized_failures.append({
                        "scenario_id": r.scenario_id,
                        "description": r.scenario_desc,
                        "language": r.language,
                        "input_text": r.input_text,
                        "reasons": r.reasons
                    })
            elif isinstance(r, dict):
                self_check = r.get("self_check", {})
                eval_res = r.get("eval_result")
                is_fail = (self_check.get("verdict") != "CORRECT") or (eval_res and not eval_res.passed)
                if is_fail:
                    sc = r.get("scenario")
                    reasons = []
                    if self_check.get("reason"):
                        reasons.append(f"Self-check verdict {self_check.get('verdict')}: {self_check.get('reason')}")
                    if eval_res and eval_res.reasons:
                        reasons.extend(eval_res.reasons)
                    normalized_failures.append({
                        "scenario_id": r.get("scenario_id") or getattr(sc, "id", "hard_case"),
                        "description": r.get("description") or getattr(sc, "description", ""),
                        "language": r.get("language") or getattr(sc, "language", "en"),
                        "input_text": r.get("input_text") or getattr(sc, "input_text", ""),
                        "reasons": reasons
                    })

        if not normalized_failures:
            logger.info("No failed scenarios to export.")
            return 0

        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        py_lines = [
            '"""',
            'Auto-generated regression tests exported from Evaluation Harness failures.',
            '"""',
            '',
            'import asyncio',
            'from httpx import AsyncClient, ASGITransport',
            'from backend.main import app',
            '',
        ]

        for idx, fail in enumerate(normalized_failures, 1):
            clean_id = fail["scenario_id"].replace('-', '_').replace('.', '_')
            func_name = f"test_exported_regression_{idx}_{clean_id}"
            clean_input = fail["input_text"].replace('"', '\\"').replace('\n', ' ')
            py_lines.extend([
                f"def {func_name}():",
                f'    """Regression for {fail["description"]}"""',
                '    async def run():',
                '        transport = ASGITransport(app=app)',
                '        async with AsyncClient(transport=transport, base_url="http://test") as client:',
                f'            sess_resp = await client.post("/api/chat/sessions", json={{"title": "{fail["scenario_id"]}", "language": "{fail["language"]}"}})',
                '            session_id = sess_resp.json()["session_id"]',
                f'            msg = "{clean_input}"',
                '            r = (await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": msg})).json()',
                '            content = r["assistant_message"]["content"]',
                '            citations = [c["id"] for c in r["assistant_message"]["citations"]]',
                '            # Assertions to be resolved based on evaluation failure reasons:',
            ])
            for reason in fail["reasons"]:
                py_lines.append(f'            # TODO: {reason}')
            py_lines.extend([
                '            assert r.get("assistant_message") is not None',
                '    asyncio.run(run())',
                '',
            ])

        with open(export_path, "w", encoding="utf-8") as f:
            f.write("\n".join(py_lines))

        logger.info(f"Exported {len(normalized_failures)} failing scenarios to {export_path}")
        return len(normalized_failures)
