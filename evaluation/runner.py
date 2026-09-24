"""
Evaluation Runner for Qanoon Sahayak Legal Chatbot.
Executes test scenarios against the chat API endpoints in-process or over HTTP.
"""

import time
import logging
from typing import Dict, Any, List
from httpx import AsyncClient, ASGITransport
from backend.main import app
from .scenario_generator import TestScenario

logger = logging.getLogger(__name__)


class EvaluationRunner:
    """
    Executes test scenarios against the live FastAPI application.
    """

    def __init__(self, base_url: str = "http://test"):
        self.base_url = base_url

    async def run_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """
        Executes a single scenario by creating a session and sending the test message.
        """
        transport = ASGITransport(app=app)
        start_time = time.time()

        async with AsyncClient(transport=transport, base_url=self.base_url, timeout=30.0) as client:
            # 1. Create Session
            sess_resp = await client.post(
                "/api/chat/sessions",
                json={
                    "title": f"Eval: {scenario.id}",
                    "language": scenario.language
                }
            )
            if sess_resp.status_code != 200:
                return {
                    "scenario_id": scenario.id,
                    "error": f"Failed to create session: {sess_resp.status_code} {sess_resp.text}",
                    "latency": time.time() - start_time
                }

            session_id = sess_resp.json()["session_id"]

            # 2. Get initial session details (to check welcome message)
            detail_resp = await client.get(f"/api/chat/sessions/{session_id}")
            welcome_msg = ""
            if detail_resp.status_code == 200:
                messages = detail_resp.json().get("messages", [])
                if messages:
                    welcome_msg = messages[0].get("content", "")

            # 3. Send test query
            msg_resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={
                    "content": scenario.input_text,
                    "language": scenario.language
                }
            )
            latency = time.time() - start_time

            if msg_resp.status_code != 200:
                return {
                    "scenario_id": scenario.id,
                    "error": f"Failed to send message: {msg_resp.status_code} {msg_resp.text}",
                    "latency": latency
                }

            data = msg_resp.json()
            asst_msg = data.get("assistant_message", {})
            case_summary = data.get("case_summary", {})
            detected_domain = case_summary.get("issue_type", "")

            return {
                "scenario_id": scenario.id,
                "session_id": session_id,
                "welcome_message": welcome_msg,
                "response_text": asst_msg.get("content", ""),
                "citations": [c.get("id") for c in asst_msg.get("citations", [])],
                "citation_objects": asst_msg.get("citations", []),
                "detected_domain": detected_domain,
                "case_summary": case_summary,
                "is_emergency": data.get("is_emergency", False),
                "helplines": data.get("emergency_helplines", []),
                "latency": round(latency, 3),
                "error": None
            }

    async def run_all(self, scenarios: List[TestScenario]) -> List[Dict[str, Any]]:
        """
        Executes a batch of test scenarios sequentially.
        """
        results = []
        for idx, scenario in enumerate(scenarios, 1):
            logger.info(f"Running scenario {idx}/{len(scenarios)}: {scenario.id} ({scenario.domain} / {scenario.difficulty})")
            res = await self.run_scenario(scenario)
            results.append(res)
        return results
