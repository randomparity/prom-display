#!/usr/bin/env python3
"""Simple load generator for OpenAI-compatible inference servers (llama.cpp, vLLM)."""

import argparse
import json
import time
import urllib.request
import urllib.error

PROMPTS = [
    "Explain how a hash table works in two sentences.",
    "Write a haiku about distributed systems.",
    "What is the difference between TCP and UDP?",
    "Describe the concept of backpressure in streaming systems.",
    "Give a one-paragraph summary of how TLS handshakes work.",
    "What are the tradeoffs between B-trees and LSM-trees?",
    "Explain eventual consistency to a five-year-old.",
    "Why is the sky blue? Answer in one sentence.",
]


def send_request(url, prompt, max_tokens):
    body = json.dumps({
        "model": "default",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        f"{url}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(description="Inference server load generator")
    parser.add_argument("--url", default="http://127.0.0.1:8080",
                        help="Base URL of the inference server (default: http://127.0.0.1:8080)")
    parser.add_argument("--max-tokens", type=int, default=50,
                        help="Max tokens per completion (default: 50)")
    parser.add_argument("--count", type=int, default=0,
                        help="Number of requests (0 = infinite, default: 0)")
    parser.add_argument("--delay", type=float, default=0,
                        help="Seconds to wait between requests (default: 0)")
    args = parser.parse_args()

    print(f"Target: {args.url}  max_tokens={args.max_tokens}  "
          f"count={'infinite' if args.count == 0 else args.count}  delay={args.delay}s")

    i = 0
    try:
        while args.count == 0 or i < args.count:
            prompt = PROMPTS[i % len(PROMPTS)]
            try:
                t0 = time.monotonic()
                result = send_request(args.url, prompt, args.max_tokens)
                elapsed = time.monotonic() - t0

                usage = result.get("usage", {})
                prompt_tok = usage.get("prompt_tokens", 0)
                comp_tok = usage.get("completion_tokens", 0)
                speed = comp_tok / elapsed if elapsed > 0 else 0

                i += 1
                print(f"#{i:>4d}  prompt={prompt_tok:>4d} tok  "
                      f"completion={comp_tok:>3d} tok  "
                      f"{speed:>5.1f} tok/s  {elapsed:>5.1f}s")

            except (urllib.error.URLError, ConnectionError, OSError) as e:
                print(f"  connection error: {e} — retrying in 2s")
                time.sleep(2)
                continue

            if args.delay > 0:
                time.sleep(args.delay)

    except KeyboardInterrupt:
        print(f"\nStopped after {i} requests.")


if __name__ == "__main__":
    main()
