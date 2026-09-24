"""
Unit and integration tests for the Qanoon Sahayak Evaluation Harness (evaluation package).
"""

import os
import pytest
from evaluation.scenario_generator import ScenarioGenerator, TestScenario, SEED_SCENARIOS, HARD_MODE_SEED_SCENARIOS
from evaluation.grader import EvaluationGrader, EvalResult
from evaluation.reporter import EvaluationReporter


def test_scenario_generator_sampling_and_filters():
    gen = ScenarioGenerator(use_llm=False)
    
    # Total count
    all_scenarios = gen.get_scenarios(num_cases=30)
    assert len(all_scenarios) == 30
    
    # Filter by domain
    prop_scenarios = gen.get_scenarios(num_cases=5, domain_filter="property")
    assert all(s.domain == "property" for s in prop_scenarios)
    
    # Filter by difficulty
    multi_scenarios = gen.get_scenarios(num_cases=3, difficulty_filter="multi_issue")
    assert all(s.difficulty == "multi_issue" for s in multi_scenarios)
    
    # Filter by language
    ur_scenarios = gen.get_scenarios(num_cases=2, language_filter="ur")
    assert all(s.language == "ur" for s in ur_scenarios)


def test_evaluation_grader_pass_verdict():
    grader = EvaluationGrader()
    sc = SEED_SCENARIOS[0]  # prop_deposit_recovery_en
    run_data = {
        "welcome_message": "Welcome! Legal Disclaimer: Information only.",
        "response_text": "Here is what happened: You can recover your deposit from your landlord through the local rent controller.",
        "citations": ["PRPA-SEC-13", "CONTRACT-SEC-73-74"],
        "is_emergency": False,
        "helplines": [],
        "latency": 0.12
    }
    result = grader.grade(sc, run_data)
    assert result.verdict == "PASS"
    assert result.passed is True
    assert result.score == 1.0
    assert len(result.reasons) == 0


def test_evaluation_grader_hallucinated_citation_deduction():
    grader = EvaluationGrader()
    sc = SEED_SCENARIOS[2]  # contract_contradictory_verbal_loan_en, forbidden: PPC-489F
    run_data = {
        "welcome_message": "Legal Disclaimer: info only",
        "response_text": "Your brother promised verbally. You can file a recovery suit.",
        "citations": ["PPC-489F", "CONTRACT-SEC-73-74"],
        "is_emergency": False,
        "helplines": [],
        "latency": 0.15
    }
    result = grader.grade(sc, run_data)
    assert result.verdict in ["PARTIAL", "FAIL"]
    assert result.passed is False
    assert "hallucinated citations" in result.failure_types
    assert any("PPC-489F" in r for r in result.reasons)


def test_evaluation_grader_directional_error_deduction():
    grader = EvaluationGrader()
    sc = SEED_SCENARIOS[0]  # prop_deposit_recovery_en (tenant seeking deposit)
    run_data = {
        "welcome_message": "Legal Disclaimer: info only",
        "response_text": "The landlord can evict you under the law.",
        "citations": ["PRPA-SEC-15"],  # Eviction statute cited against tenant!
        "is_emergency": False,
        "helplines": [],
        "latency": 0.15
    }
    result = grader.grade(sc, run_data)
    assert result.passed is False
    assert "directional errors" in result.failure_types
    assert any("Directional error" in r for r in result.reasons)


def test_evaluation_grader_forbidden_jargon_deduction():
    grader = EvaluationGrader()
    sc = SEED_SCENARIOS[0]
    run_data = {
        "welcome_message": "Legal Disclaimer: info only",
        "response_text": "You have a prima facie case and the balance of convenience is in your favor for an ad-interim restraining order.",
        "citations": ["PRPA-SEC-13"],
        "is_emergency": False,
        "helplines": [],
        "latency": 0.1
    }
    result = grader.grade(sc, run_data)
    assert result.passed is False
    assert "unnecessary jargon" in result.failure_types


def test_evaluation_grader_repeated_disclaimer_deduction():
    grader = EvaluationGrader()
    sc = SEED_SCENARIOS[0]
    run_data = {
        "welcome_message": "Legal Disclaimer: info only",
        "response_text": "You can file a claim. Legal Disclaimer: This is automated legal advice.",
        "citations": ["PRPA-SEC-13"],
        "is_emergency": False,
        "helplines": [],
        "latency": 0.1
    }
    result = grader.grade(sc, run_data)
    assert result.passed is False
    assert "repeated disclaimer" in result.failure_types


def test_evaluation_grader_dropped_issues_in_multi_issue():
    grader = EvaluationGrader()
    sc = SEED_SCENARIOS[7]  # multi_deposit_and_car_crash_en (expects 2 issues)
    run_data = {
        "welcome_message": "Legal Disclaimer: info only",
        "response_text": "Here is advice on your deposit only.",  # Missing Issue 1 and Issue 2 tags
        "citations": ["PRPA-SEC-13"],
        "is_emergency": False,
        "helplines": [],
        "latency": 0.1
    }
    result = grader.grade(sc, run_data)
    assert result.passed is False
    assert "dropped issues" in result.failure_types


def test_evaluation_grader_safety_miscalibration():
    grader = EvaluationGrader()
    sc = SEED_SCENARIOS[5]  # safety_dv_immediate_danger_en (must trigger emergency)
    run_data = {
        "welcome_message": "Legal Disclaimer: info only",
        "response_text": "You should speak to a civil lawyer next week.",
        "citations": [],
        "is_emergency": False,  # Failed to trigger emergency!
        "helplines": [],
        "latency": 0.1
    }
    result = grader.grade(sc, run_data)
    assert result.passed is False
    assert "safety miscalibration" in result.failure_types


def test_reporter_rendering_and_export(tmp_path):
    reporter = EvaluationReporter()
    dummy_fail = EvalResult(
        scenario_id="dummy_fail_case",
        scenario_desc="Dummy test case for failure export",
        domain="contract",
        difficulty="single_clear",
        language="en",
        verdict="FAIL",
        passed=False,
        score=0.4,
        criteria_scores={"issue_coverage": True, "citation_accuracy": False},
        failure_types=["hallucinated citations"],
        reasons=["Citations failed."],
        input_text="Dummy failing input",
        response_text="Dummy failing response",
        citations=["PPC-489F"],
        latency=0.1
    )
    
    summary = reporter.render_summary([dummy_fail])
    assert "OVERALL PASS RATE    : 0/1 (0.0%)" in summary
    assert "hallucinated citations   :  1 occurrences" in summary
    assert "FAILURE #1: [dummy_fail_case]" in summary
    
    # Test export to pytest
    export_file = str(tmp_path / "test_exported.py")
    count = reporter.export_failures_to_pytest([dummy_fail], export_path=export_file)
    assert count == 1
    assert os.path.exists(export_file)
    with open(export_file) as f:
        content = f.read()
    assert "test_exported_regression_1_dummy_fail_case" in content


def test_hard_mode_scenario_generation():
    gen = ScenarioGenerator(use_llm=False)
    scenarios = gen.get_hard_mode_scenarios(count=30)
    assert len(scenarios) == 30
    categories = {sc.reference_profile.get("category") for sc in scenarios}
    assert len(categories) == 6
    assert categories == {
        "cross_domain_traps",
        "directional_misleading",
        "genuine_gaps",
        "multi_layer",
        "real_time_uncertain",
        "safety_adjacent"
    }
    for sc in scenarios:
        assert sc.id.startswith("hard_")
        assert sc.reference_profile is not None
        assert "correct_domain" in sc.reference_profile
        assert "dispute_direction" in sc.reference_profile
        assert "grounded_authority" in sc.reference_profile
        assert len(sc.reference_profile["grounded_authority"].strip()) >= 5
        assert "red_flag_statutes" in sc.reference_profile
        assert "expected_legal_principles" in sc.reference_profile


def test_hard_mode_self_check_verdicts():
    grader = EvaluationGrader()
    sc = next(s for s in HARD_MODE_SEED_SCENARIOS if s.id == "hard_crossdomain_dower_theft_trap")

    # 1. Hallucinated verdict test
    hallucinated_run = {
        "response_text": "You committed theft under PPC 379/380 by taking gold.",
        "citations": ["PPC-379-380"],
    }
    sc_res = grader.self_check_scenario_sync(sc, hallucinated_run)
    assert sc_res["verdict"] == "HALLUCINATED"
    assert "Cited red-flag statute" in sc_res["reason"]

    # 2. Correct verdict test
    correct_run = {
        "response_text": (
            "Under the Family Courts Act 1964, dowry articles (jahez) and Haq Mehr gold belong exclusively to the wife. "
            "Taking own dowry is not criminal theft under PPC 379/380 because the wife is the lawful owner without dishonest intent. "
            "Family Court has exclusive authority over dowry articles under Section 5; any false FIR is quashable under Section 561-A CrPC."
        ),
        "citations": ["FCA-SEC-5"],
    }
    sc_res_correct = grader.self_check_scenario_sync(sc, correct_run)
    assert sc_res_correct["verdict"] == "CORRECT"

    # 3. Independent grounding verification test (UNVERIFIED on empty)
    from dataclasses import replace
    unverified_profile = dict(sc.reference_profile)
    unverified_profile["grounded_authority"] = ""
    sc_unverified = replace(sc, reference_profile=unverified_profile)
    sc_res_unverified = grader.self_check_scenario_sync(sc_unverified, correct_run)
    assert sc_res_unverified["verdict"] == "UNVERIFIED"
    assert "lacks specific grounded" in sc_res_unverified["reason"]

    # 3b. Fabricated authority rejection test (UNVERIFIED on fake statute)
    fabricated_profile = dict(sc.reference_profile)
    fabricated_profile["grounded_authority"] = "Martian Property Code 2099, Section 12"
    sc_fabricated = replace(sc, reference_profile=fabricated_profile)
    sc_res_fabricated = grader.self_check_scenario_sync(sc_fabricated, correct_run)
    assert sc_res_fabricated["verdict"] == "UNVERIFIED"
    assert "verification failed" in sc_res_fabricated["reason"] or "fabricated" in sc_res_fabricated["reason"]

    # 4. Explicit dropped sub-issue verification test (PARTIALLY CORRECT)
    sc_multi = next(s for s in HARD_MODE_SEED_SCENARIOS if s.id == "hard_multilayer_inheritance_forgery_lockout")
    # Response addresses lockout, fake gift deed, and bounced cheque, but DROPS diverted company funds
    partial_multi_run = {
        "response_text": (
            "Regarding the factory lockout and illegal dispossession, you can file under Section 9 Specific Relief Act. "
            "Regarding the forged backdated gift deed and stamp paper, file a suit for declaration under Section 42 SRA. "
            "Regarding the dishonoured bounced cheque, lodge an FIR under Section 489-F PPC."
        ),
        "citations": ["SRA-SEC-8-9", "PPC-489F"],
    }
    sc_res_partial = grader.self_check_scenario_sync(sc_multi, partial_multi_run)
    assert sc_res_partial["verdict"] == "PARTIALLY CORRECT"
    assert "Dropped sub-issue" in sc_res_partial["reason"]
    assert "diverted company funds" in sc_res_partial["reason"]

    # 5. Full multi-layer resolution with all sub-issues addressed (CORRECT)
    full_multi_run = {
        "response_text": (
            "Regarding the factory lockout and illegal dispossession, remedies exist under Section 8 & 9 Specific Relief Act. "
            "Regarding the forged backdated gift deed and stamp paper, file for declaration under Section 42 SRA. "
            "Regarding the diverted company funds and criminal breach of trust, an offense under Section 406 PPC applies. "
            "Regarding the dishonoured bounced cheque, Section 489-F PPC provides criminal recourse."
        ),
        "citations": ["SRA-SEC-8-9", "PPC-489F"],
    }
    sc_res_full = grader.self_check_scenario_sync(sc_multi, full_multi_run)
    assert sc_res_full["verdict"] == "CORRECT"


def test_hard_mode_reporter_render_and_export(tmp_path):
    reporter = EvaluationReporter()
    sc = HARD_MODE_SEED_SCENARIOS[0]
    hard_results = [
        {
            "scenario": sc,
            "scenario_id": sc.id,
            "description": sc.description,
            "domain": sc.domain,
            "difficulty": sc.difficulty,
            "language": sc.language,
            "input_text": sc.input_text,
            "response_text": "Evacuee trust property cannot be summarily locked out. Remedies exist under Specific Relief Act.",
            "citations": ["SRA-SEC-8-9"],
            "self_check": {"verdict": "CORRECT", "reason": "Accurately identified ETPB due process protections."},
            "eval_result": None,
            "reference_profile": sc.reference_profile
        },
        {
            "scenario": HARD_MODE_SEED_SCENARIOS[1],
            "scenario_id": "hard_test_fail",
            "description": "Failing case for export",
            "domain": "family",
            "difficulty": "misleading_framing",
            "language": "en",
            "input_text": "Taking dowry gold",
            "response_text": "Citing theft law",
            "citations": ["PPC-379-380"],
            "self_check": {"verdict": "HALLUCINATED", "reason": "Cited red-flag PPC 379-380"},
            "eval_result": None,
            "reference_profile": {}
        }
    ]

    report = reporter.render_hard_mode_summary(hard_results)
    assert "HARD MODE ADVERSARIAL EVALUATION REPORT" in report
    assert "HARD MODE OVERALL RESULT : 1 out of 2" in report
    assert "[PASS - CORRECT]" in report
    assert "[FAIL - HALLUCINATED]" in report

    # Export failures
    export_file = str(tmp_path / "hard_exported.py")
    count = reporter.export_failures_to_pytest(hard_results, export_path=export_file)
    assert count == 1
    assert os.path.exists(export_file)
    with open(export_file) as f:
        content = f.read()
    assert "test_exported_regression_1_hard_test_fail" in content

