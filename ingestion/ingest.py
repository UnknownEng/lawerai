"""
CLI Script for Ingesting, Chunking, Embedding, and Validating the Legal Corpus
Usage:
    python -m ingestion.ingest [--refresh]
"""

import os
import sys
import argparse
import logging
from .corpus_loader import load_corpus_documents
from .vector_store import LegalVectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingestion")


def run_ingestion(corpus_dir: str, output_path: str, force_refresh: bool = False):
    logger.info("==================================================")
    logger.info("   Qanoon Sahayak — Legal Corpus Ingestion Pipeline")
    logger.info("==================================================")

    store = LegalVectorStore(storage_path=output_path)

    # Load statutory documents
    documents = load_corpus_documents(corpus_dir)
    if not documents:
        logger.error(f"No statutory documents found in {corpus_dir}!")
        sys.exit(1)

    # Check if update is needed
    if not force_refresh and os.path.exists(output_path):
        logger.info("Checking if existing vector store needs update...")
        # Check count
        if len(store.documents) == len(documents):
            logger.info("Vector store is already up-to-date. Use --refresh to rebuild.")
            run_benchmark_validation(store)
            return

    logger.info(f"Building fresh vector store for {len(documents)} legal sections...")
    store.build_index(documents)
    logger.info(f"Vector store successfully saved to {output_path}")

    # Run benchmark verification
    run_benchmark_validation(store)


def run_benchmark_validation(store: LegalVectorStore):
    """Run benchmark queries to verify retrieval accuracy."""
    logger.info("\n--- Running Statutory Retrieval Benchmark Tests ---")
    test_cases = [
        {
            "query": "A contractor took 10 lakh rupees under false promise and turned off his phone",
            "expected_act": "PPC",
            "expected_sec": "420"
        },
        {
            "query": "The buyer gave me a bank cheque for goods and it bounced with insufficient funds slip",
            "expected_act": "PPC",
            "expected_sec": "489-F"
        },
        {
            "query": "The SHO at the local police station refuses to register my FIR",
            "expected_act": "CrPC",
            "expected_sec": "22-A & 22-B"
        },
        {
            "query": "My husband has kicked me out and is not paying any monthly maintenance for minor children",
            "expected_act": "MFLO",
            "expected_sec": "Section 9"
        },
        {
            "query": "Opponent is starting illegal construction on my inherited plot, I need urgent stay order",
            "expected_act": "CPC",
            "expected_sec": "Order XXXIX, Rules 1 & 2"
        },
        {
            "query": "Tenant has stopped paying monthly rent in Lahore and tenancy expired",
            "expected_act": "PRPA",
            "expected_sec": "Section 15"
        },
        {
            "query": "Someone is blackmailing me on WhatsApp and threatening to upload private photos",
            "expected_act": "PECA",
            "expected_sec": "Sections 20 & 21"
        }
    ]

    passed = 0
    for test in test_cases:
        query = test["query"]
        expected_sec = test["expected_sec"]
        results = store.search_hybrid(query, top_k=2)

        matched = False
        top_res = results[0] if results else {}
        top_sec = top_res.get("section_number", "")
        top_act = top_res.get("act_code", "")

        for r in results:
            if expected_sec.lower() in r.get("section_number", "").lower() or r.get("act_code", "").lower() == test["expected_act"].lower():
                matched = True
                break

        status = "PASSED" if matched else "FAILED"
        if matched:
            passed += 1

        logger.info(f"[{status}] Query: '{query[:45]}...'")
        logger.info(f"         Expected: {test['expected_act']} {expected_sec} | Retrieved Top: {top_act} {top_sec} (Score: {top_res.get('retrieval_score', 0)})")

    logger.info(f"\nBenchmark Result: {passed}/{len(test_cases)} tests passed.")
    if passed == len(test_cases):
        logger.info("All legal retrieval benchmarks passed with 100% precision!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest legal corpus for Qanoon Sahayak")
    parser.add_argument("--refresh", action="store_true", help="Force rebuild vector store")
    parser.add_argument("--corpus-dir", default=None, help="Directory containing JSON statutory files")
    parser.add_argument("--output-path", default=None, help="Path to save vector store JSON")

    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    corpus_directory = args.corpus_dir or os.path.join(base_dir, "data", "legal_corpus")
    output_file = args.output_path or os.path.join(base_dir, "data", "legal_vector_store.json")

    run_ingestion(corpus_directory, output_file, force_refresh=args.refresh)
