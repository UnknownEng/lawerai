"""
CLI Entry Point for Qanoon Sahayak Automated Testing & Evaluation Harness.

Usage:
    python3 -m evaluation.run_eval --num-cases 30
    python3 -m evaluation.run_eval --num-cases 30 --export-failures
    python3 -m evaluation.run_eval --domain property --difficulty single_clear
"""

import sys
import json
import asyncio
import argparse
import logging
from .scenario_generator import ScenarioGenerator
from .runner import EvaluationRunner
from .grader import EvaluationGrader
from .reporter import EvaluationReporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("run_eval")


async def main_async(args: argparse.Namespace):
    generator = ScenarioGenerator(use_llm=args.use_llm_gen)
    runner = EvaluationRunner(base_url=args.base_url)
    grader = EvaluationGrader()
    reporter = EvaluationReporter()

    if args.hard_mode:
        count = args.num_cases if args.num_cases else 30
        print(f"\n[+] Initializing HARD-MODE evaluation: generating and loading {count} toughest adversarial Pakistani legal test scenarios...")
        if args.use_llm_gen:
            scenarios = await generator.generate_hard_mode_scenarios(count=count)
        else:
            scenarios = generator.get_hard_mode_scenarios(count=count)
        print(f"[+] Loaded {len(scenarios)} hard-mode adversarial scenarios.\n")

        print("[+] Executing hard-mode scenarios against live chatbot...")
        run_data_list = await runner.run_all(scenarios)

        print("\n[+] Grading responses and running self-check against reference answer profiles...")
        hard_results = []
        for sc, run_data in zip(scenarios, run_data_list):
            eval_res = grader.grade(sc, run_data)
            self_check = await grader.self_check_scenario(sc, run_data)
            hard_results.append({
                "scenario": sc,
                "scenario_id": sc.id,
                "description": sc.description,
                "domain": sc.domain,
                "difficulty": sc.difficulty,
                "language": sc.language,
                "input_text": sc.input_text,
                "response_text": run_data.get("response_text", ""),
                "citations": run_data.get("citations", []),
                "eval_result": eval_res,
                "self_check": self_check,
                "reference_profile": getattr(sc, "reference_profile", {})
            })

        # Render hard-mode summary report
        report = reporter.render_hard_mode_summary(hard_results)
        print("\n" + report)

        # Export failures if requested
        if args.export_failures:
            count = reporter.export_failures_to_pytest(hard_results)
            if count > 0:
                print(f"\n[+] Exported {count} failing scenarios to backend/tests/test_eval_exported_regressions.py")

        # Output JSON if requested
        if args.output_json:
            data_to_dump = [
                {
                    "scenario_id": r["scenario_id"],
                    "description": r["description"],
                    "domain": r["domain"],
                    "difficulty": r["difficulty"],
                    "language": r["language"],
                    "input_text": r["input_text"],
                    "response_text": r["response_text"],
                    "citations": r["citations"],
                    "self_check": r["self_check"],
                    "grade_passed": r["eval_result"].passed,
                    "grade_score": r["eval_result"].score,
                    "reference_profile": r["reference_profile"]
                }
                for r in hard_results
            ]
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump(data_to_dump, f, indent=2, ensure_ascii=False)
            print(f"\n[+] Detailed results saved to {args.output_json}")

        all_correct = all(r["self_check"].get("verdict") == "CORRECT" and r["eval_result"].passed for r in hard_results)
        sys.exit(0 if all_correct else 1)

    print(f"\n[+] Sampling {args.num_cases} Pakistani legal test scenarios...")
    scenarios = generator.get_scenarios(
        num_cases=args.num_cases,
        domain_filter=args.domain,
        difficulty_filter=args.difficulty,
        language_filter=args.language
    )
    print(f"[+] Loaded {len(scenarios)} evaluation scenarios.\n")

    print(f"[+] Executing scenarios against chatbot API endpoints...")
    run_data_list = await runner.run_all(scenarios)

    print(f"\n[+] Grading responses against expected profiles...")
    results = []
    for sc, run_data in zip(scenarios, run_data_list):
        res = grader.grade(sc, run_data)
        results.append(res)

    # Render summary report
    report = reporter.render_summary(results)
    print("\n" + report)

    # Export failures if requested
    if args.export_failures:
        count = reporter.export_failures_to_pytest(results)
        if count > 0:
            print(f"\n[+] Exported {count} failing scenarios to backend/tests/test_eval_exported_regressions.py")

    # Output JSON if requested
    if args.output_json:
        data_to_dump = [
            {
                "scenario_id": r.scenario_id,
                "description": r.scenario_desc,
                "domain": r.domain,
                "difficulty": r.difficulty,
                "language": r.language,
                "verdict": r.verdict,
                "passed": r.passed,
                "score": r.score,
                "criteria": r.criteria_scores,
                "failure_types": r.failure_types,
                "reasons": r.reasons,
                "input_text": r.input_text,
                "detected_domain": r.detected_domain,
                "citations": r.citations,
                "latency": r.latency
            }
            for r in results
        ]
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(data_to_dump, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Detailed results saved to {args.output_json}")

    passed_all = all(r.passed for r in results)
    sys.exit(0 if passed_all else 1)


def main():
    parser = argparse.ArgumentParser(description="Run Qanoon Sahayak Automated Evaluation Harness")
    parser.add_argument("--hard-mode", action="store_true", help="Generate and evaluate 10 toughest adversarial scenarios with reference self-checking")
    parser.add_argument("--num-cases", type=int, default=30, help="Number of test scenarios to evaluate in standard mode (default: 30)")
    parser.add_argument("--domain", type=str, default=None, help="Filter scenarios by legal domain (property, family, criminal, contract, labour, consumer, cyber)")
    parser.add_argument("--difficulty", type=str, default=None, help="Filter scenarios by difficulty pattern (single_clear, multi_issue, contradictory, vague_low_info, etc.)")
    parser.add_argument("--language", type=str, default=None, help="Filter scenarios by language (en, ur, roman_ur)")
    parser.add_argument("--base-url", type=str, default="http://test", help="API base URL (default: http://test for in-process)")
    parser.add_argument("--use-llm-gen", action="store_true", help="Generate scenarios dynamically via LLM instead of seed bank")
    parser.add_argument("--export-failures", action="store_true", help="Export failing scenarios as pytest tests")
    parser.add_argument("--output-json", type=str, default=None, help="Path to save detailed JSON evaluation results")

    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
