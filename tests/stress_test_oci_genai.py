"""
OCI GenAI Rate Limit Stress Test
================================
Simulates concurrent workshop users hitting xai.grok-3-fast via OCI GenAI.

Auth modes:
  1. Traditional: ~/.oci/config (OciUserPrincipalAuth) -- use for local testing
  2. API key:     OCI_GENAI_API_KEY env var            -- use for Codespaces

Usage:
  # Traditional auth, 10 concurrent users, 5 calls each
  python tests/stress_test_oci_genai.py --users 10 --calls-per-user 5

  # API key auth, 50 concurrent users
  OCI_GENAI_API_KEY=xxx python tests/stress_test_oci_genai.py --auth apikey --users 50

  # Full workshop simulation (120 calls per user, staggered start)
  python tests/stress_test_oci_genai.py --users 100 --calls-per-user 120 --stagger 2.0
"""

import argparse
import json
import os
import sys
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

# ── Config ────────────────────────────────────────────────────────────────
REGION_IAM = "us-ashburn-1"
REGION_APIKEY = os.environ.get("OCI_GENAI_REGION", "us-phoenix-1")
COMPARTMENT_ID = "ocid1.tenancy.oc1..aaaaaaaaypz3jeouf67rycnobkfaj7zepotuvpoqtqipfai3qs4qw7ok6yna"
MODEL = "xai.grok-3-fast"

# Typical workshop prompts (varied lengths to simulate real usage)
PROMPTS = [
    "What is reinforcement learning? Answer in 2 sentences.",
    "Explain how vector similarity search works with cosine distance. Keep it under 100 words.",
    "Compare HNSW and IVF indexing strategies for approximate nearest neighbor search. Be concise.",
    "What are the 6 types of memory in cognitive architectures? List them briefly.",
    "How does retrieval-augmented generation improve factual accuracy in LLM responses?",
    "Explain the difference between episodic and semantic memory in AI agents.",
    "What is context window management and why does it matter for long conversations?",
    "Describe how tool-calling works in modern LLM APIs. 3 sentences max.",
    "What are the advantages of storing embeddings in Oracle Database vs a standalone vector DB?",
    "How does memory offloading help agents handle long research sessions?",
]


@dataclass
class CallResult:
    user_id: int
    call_num: int
    success: bool
    latency_s: float
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    error: str = ""
    status_code: int = 0


@dataclass
class TestResults:
    results: list = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)
    start_time: float = 0.0

    def add(self, r: CallResult):
        with self.lock:
            self.results.append(r)

    def summary(self) -> dict:
        total_duration = time.time() - self.start_time
        successes = [r for r in self.results if r.success]
        failures = [r for r in self.results if not r.success]
        latencies = [r.latency_s for r in successes]
        total_tokens = sum(r.total_tokens for r in successes)
        input_tokens = sum(r.input_tokens for r in successes)
        output_tokens = sum(r.output_tokens for r in successes)

        # Tokens per minute (extrapolated from actual duration)
        tpm = (total_tokens / total_duration) * 60 if total_duration > 0 else 0

        # Error breakdown
        error_counts = {}
        for r in failures:
            key = f"{r.status_code}: {r.error[:80]}" if r.error else f"{r.status_code}"
            error_counts[key] = error_counts.get(key, 0) + 1

        return {
            "total_calls": len(self.results),
            "successes": len(successes),
            "failures": len(failures),
            "failure_rate": f"{len(failures)/len(self.results)*100:.1f}%" if self.results else "N/A",
            "total_duration_s": round(total_duration, 1),
            "latency_p50_s": round(statistics.median(latencies), 2) if latencies else 0,
            "latency_p95_s": round(sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0, 2),
            "latency_p99_s": round(sorted(latencies)[int(len(latencies)*0.99)] if latencies else 0, 2),
            "latency_max_s": round(max(latencies), 2) if latencies else 0,
            "total_tokens": total_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "tokens_per_minute": round(tpm),
            "requests_per_minute": round(len(successes) / total_duration * 60) if total_duration > 0 else 0,
            "error_breakdown": error_counts,
        }


def create_client(auth_mode: str):
    """Create OpenAI-compatible client with the chosen auth mode."""
    if auth_mode == "apikey":
        from openai import OpenAI
        api_key = os.environ.get("OCI_GENAI_API_KEY")
        if not api_key:
            print("ERROR: OCI_GENAI_API_KEY env var not set. Required for apikey auth mode.")
            sys.exit(1)
        endpoint = f"https://inference.generativeai.{REGION_APIKEY}.oci.oraclecloud.com/openai/v1"
        return OpenAI(base_url=endpoint, api_key=api_key)
    else:
        from oci_openai import OciOpenAI, OciUserPrincipalAuth
        auth = OciUserPrincipalAuth(profile_name="DEFAULT")
        return OciOpenAI(auth=auth, region=REGION_IAM, compartment_id=COMPARTMENT_ID)


def single_call(client, user_id: int, call_num: int, model: str) -> CallResult:
    """Make one chat completion call, return metrics."""
    prompt = PROMPTS[call_num % len(PROMPTS)]
    messages = [
        {"role": "system", "content": "You are a helpful research assistant. Be concise. /no_think"},
        {"role": "user", "content": prompt},
    ]

    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=256,
            temperature=0.7,
        )
        latency = time.time() - t0
        usage = response.usage
        return CallResult(
            user_id=user_id,
            call_num=call_num,
            success=True,
            latency_s=latency,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )
    except Exception as e:
        latency = time.time() - t0
        status = getattr(e, 'status_code', 0) or getattr(e, 'code', 0) or 0
        return CallResult(
            user_id=user_id,
            call_num=call_num,
            success=False,
            latency_s=latency,
            error=str(e)[:200],
            status_code=int(status) if status else 0,
        )


def simulate_user(client, user_id: int, calls_per_user: int, model: str,
                   results: TestResults, call_delay: float):
    """Simulate one workshop user making sequential LLM calls."""
    for c in range(calls_per_user):
        r = single_call(client, user_id, c, model)
        results.add(r)

        # Live progress
        status = "OK" if r.success else f"FAIL({r.status_code})"
        tok = f"{r.total_tokens}tok" if r.success else r.error[:40]
        elapsed = time.time() - results.start_time
        print(f"  [{elapsed:6.1f}s] user={user_id:03d} call={c+1:03d} {status} {r.latency_s:.2f}s {tok}")

        # Small delay between calls (simulates user reading output)
        if call_delay > 0 and c < calls_per_user - 1:
            time.sleep(call_delay)


def run_stress_test(args):
    print(f"\n{'='*70}")
    print(f"  OCI GenAI Stress Test")
    print(f"  Model:    {args.model}")
    print(f"  Region:   {REGION_APIKEY if args.auth == 'apikey' else REGION_IAM}")
    print(f"  Auth:     {args.auth}")
    print(f"  Users:    {args.users}")
    print(f"  Calls/user: {args.calls_per_user}")
    print(f"  Total calls: {args.users * args.calls_per_user}")
    print(f"  Stagger:  {args.stagger}s between user starts")
    print(f"  Call delay: {args.call_delay}s between calls per user")
    print(f"{'='*70}\n")

    # Validate auth before spawning threads
    print("Validating auth with a single test call...")
    client = create_client(args.auth)
    test = single_call(client, user_id=999, call_num=0, model=args.model)
    if not test.success:
        print(f"FATAL: Auth validation failed: {test.error}")
        sys.exit(1)
    print(f"Auth OK. Test call: {test.latency_s:.2f}s, {test.total_tokens} tokens\n")

    results = TestResults()
    results.start_time = time.time()

    # Each thread gets its own client to avoid connection pooling bottlenecks
    def user_worker(user_id):
        user_client = create_client(args.auth)
        if args.stagger > 0:
            time.sleep(user_id * args.stagger)
        simulate_user(user_client, user_id, args.calls_per_user, args.model, results, args.call_delay)

    with ThreadPoolExecutor(max_workers=args.users) as executor:
        futures = [executor.submit(user_worker, uid) for uid in range(args.users)]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"Thread error: {e}")

    # Results
    summary = results.summary()
    print(f"\n{'='*70}")
    print("  RESULTS")
    print(f"{'='*70}")
    for k, v in summary.items():
        if k == "error_breakdown":
            if v:
                print(f"\n  Error breakdown:")
                for err, count in v.items():
                    print(f"    {count}x  {err}")
        else:
            print(f"  {k:.<30s} {v}")

    # Rate limit verdict
    tpm = summary["tokens_per_minute"]
    failures = summary["failures"]
    total = summary["total_calls"]
    print(f"\n{'='*70}")
    print("  VERDICT")
    print(f"{'='*70}")

    if failures == 0 and tpm < 80000:
        print("  PASS: No throttling, well within 100K TPM limit.")
        print(f"  Headroom: ~{100000 - tpm:,} TPM remaining.")
    elif failures == 0 and tpm < 100000:
        print("  WARN: No failures but approaching 100K TPM limit.")
        print("  Recommend adding exponential backoff to the agent loop.")
    elif failures > 0 and failures / total < 0.05:
        print("  WARN: Some throttling detected (<5% failure rate).")
        print("  Viable with retry logic + exponential backoff.")
    elif failures > 0:
        print(f"  FAIL: {summary['failure_rate']} failure rate. Too many concurrent users")
        print("  for this TPM allocation. Options:")
        print("    1. Request TPM limit increase from Oracle")
        print("    2. Stagger workshop sections so not everyone hits Part 6 simultaneously")
        print("    3. Add aggressive backoff + retry in the agent loop")

    # Save raw results
    outfile = "tests/stress_test_results.json"
    with open(outfile, "w") as f:
        raw = [
            {
                "user_id": r.user_id, "call_num": r.call_num, "success": r.success,
                "latency_s": round(r.latency_s, 3), "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens, "total_tokens": r.total_tokens,
                "error": r.error, "status_code": r.status_code,
            }
            for r in results.results
        ]
        json.dump({"summary": summary, "calls": raw}, f, indent=2, default=str)
    print(f"\n  Raw results saved to {outfile}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCI GenAI rate limit stress test")
    parser.add_argument("--auth", choices=["oci", "apikey"], default="oci",
                        help="Auth mode: 'oci' for ~/.oci/config, 'apikey' for OCI_GENAI_API_KEY env var")
    parser.add_argument("--model", default=MODEL, help=f"Model ID (default: {MODEL})")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent simulated users")
    parser.add_argument("--calls-per-user", type=int, default=5, help="LLM calls per user")
    parser.add_argument("--stagger", type=float, default=0.0,
                        help="Seconds between each user starting (0 = all at once)")
    parser.add_argument("--call-delay", type=float, default=0.5,
                        help="Seconds between sequential calls per user (simulates reading time)")
    args = parser.parse_args()
    run_stress_test(args)
