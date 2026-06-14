import os
import sys
import time
from pathlib import Path

# Add backend dir to path to ensure imports work
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.append(str(BACKEND_DIR))

from rag.retriever import retrieve
from rag.context_assembler import ContextAssembler
from llm.answer_generator import generate_answer

TEST_QUERIES = [
    # 1. Overview queries
    ("Explain the overall architecture and layout of this project.", "OVERVIEW"),
    ("What is the tech stack and frameworks used in this codebase?", "OVERVIEW"),
    
    # 2. Debugging queries
    ("Why is token validation failing or throwing errors?", "DEBUG"),
    ("Why is retinaface face detection failing?", "DEBUG"),
    
    # 3. Code search queries
    ("Find where retinaface face validation logic is declared.", "CODE_SEARCH"),
    ("Find how database tables and configurations are set up.", "CODE_SEARCH"),
    ("Search for camera manager streaming logic.", "CODE_SEARCH"),
    
    # 4. File recovery queries
    ("get full code of src/main.py", "FILE_RECOVERY"),
    ("entire code of indexer.py", "FILE_RECOVERY")
]

def run_verify():
    print("\n" + "="*70)
    print("RAG UPGRADE EVALUATION & LATENCY VERIFICATION")
    print("="*70 + "\n")
    
    results = []
    
    for idx, (query, expected_intent) in enumerate(TEST_QUERIES, 1):
        print(f"[{idx}/{len(TEST_QUERIES)}] Query: '{query}'")
        
        # Measure retrieval
        ret_start = time.perf_counter()
        ret_data = retrieve(query)
        ret_end = time.perf_counter()
        ret_time = (ret_end - ret_start) * 1000
        
        intent = ret_data.get("query_type", "UNKNOWN")
        results_count = len(ret_data.get("results", []))
        
        # Assemble context
        context_str = ContextAssembler.assemble_context(ret_data)
        
        # Measure generation
        gen_start = time.perf_counter()
        answer = "SKIPPED (File Recovery)"
        if intent != "FILE_RECOVERY":
            try:
                answer = generate_answer(query, context_str)
            except Exception as e:
                answer = f"ERROR: {e}"
        gen_end = time.perf_counter()
        gen_time = (gen_end - gen_start) * 1000 if intent != "FILE_RECOVERY" else 0.0
        
        print(f"      Mapped Intent: {intent} (Expected: {expected_intent})")
        print(f"      Retrieval Time: {ret_time:.2f} ms | Chunks Count: {results_count}")
        if intent != "FILE_RECOVERY":
            print(f"      Generation Time: {gen_time:.2f} ms")
            print(f"      Answer (preview): {answer.strip().replace(chr(10), ' ')[:140]}...")
        print("-" * 50)
        
        results.append({
            "query": query,
            "expected": expected_intent,
            "actual": intent,
            "ret_time": ret_time,
            "gen_time": gen_time,
            "chunks": results_count,
            "success": intent == expected_intent
        })
        
    print("\n" + "="*70)
    print("BENCHMARK METRICS SUMMARY")
    print("="*70)
    print(f"| {'Query':<45} | {'Expected':<12} | {'Actual':<12} | {'Ret (ms)':<9} | {'Gen (ms)':<9} |")
    print(f"| {'-'*45} | {'-'*12} | {'-'*12} | {'-'*9} | {'-'*9} |")
    
    total_ret = 0.0
    total_gen = 0.0
    correct_intents = 0
    count_gen = 0
    
    for r in results:
        print(f"| {r['query'][:43]:<45} | {r['expected']:<12} | {r['actual']:<12} | {r['ret_time']:>9.1f} | {r['gen_time']:>9.1f} |")
        total_ret += r["ret_time"]
        if r["actual"] != "FILE_RECOVERY" and not r["gen_time"] == 0.0:
            total_gen += r["gen_time"]
            count_gen += 1
        if r["success"]:
            correct_intents += 1
            
    avg_ret = total_ret / len(TEST_QUERIES)
    avg_gen = total_gen / count_gen if count_gen > 0 else 0.0
    intent_accuracy = (correct_intents / len(TEST_QUERIES)) * 100
    
    print(f"| {'-'*45} | {'-'*12} | {'-'*12} | {'-'*9} | {'-'*9} |")
    print(f"Average Retrieval Latency  : {avg_ret:.2f} ms")
    if count_gen > 0:
        print(f"Average Generation Latency : {avg_gen:.2f} ms")
    print(f"Intent Classification Accuracy: {intent_accuracy:.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_verify()
