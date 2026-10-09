import re
import sys
import time

# Force UTF-8 output on Windows PowerShell (needed for the ₹ symbol)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from agent import agent, ask_with_tools

RESULTS_FILE = "results.txt"

QUESTIONS = [
    "How many days do I have to return a phone?",
    "Can I return earbuds if I just don't like them?",
    "What is the delivery charge on a ₹350 order?",
    "If I order at 4 PM, when will it be dispatched?",
    "Can I use a coupon together with a bank offer?",
    "How long is Extended Protection and when can I buy it?",
    "Can I pay cash on delivery for a ₹12,000 order?",
    "Where is my order KE1002?",
    "What is the status of order ke1005?",
    "What is the status of order KE9999?",
    "My return for KE1006 was picked up. When will I get my refund?",
    "I paid cash for KE1009. If I return it, how do I get my money back?",
    "Who is the CEO of Google?",
    "Write me a poem about Diwali.",
]

MAX_RETRIES = 3        # attempts per question for temporary 503 errors
RETRY_WAIT = 30        # seconds to wait between 503 retries
PAUSE_BETWEEN = 3      # seconds between questions


def load_done():
    """Return the set of question numbers that already have a real answer."""
    try:
        with open(RESULTS_FILE, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return set()
    # Only blocks that contain a 'Tools:' line count as finished.
    return {int(n) for n in re.findall(r"^#(\d+): [^\n]*\nTools:", text, re.M)}


def run_one(question):
    """Ask one question. Returns (answer, tools, error_text)."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            answer, tools = ask_with_tools(agent, question)
            return answer, tools, None
        except Exception as e:
            err = str(e)
            if "503" in err and attempt < MAX_RETRIES:
                print(f"   503 from Gemini, retrying in {RETRY_WAIT}s "
                      f"(attempt {attempt}/{MAX_RETRIES})...")
                time.sleep(RETRY_WAIT)
                continue
            return None, None, err
    return None, None, "unknown error"


def run_all():
    done = load_done()
    if done:
        print(f"Already recorded: {sorted(done)}. Skipping those.\n")

    with open(RESULTS_FILE, "a", encoding="utf-8") as out:
        for i, q in enumerate(QUESTIONS, 1):
            if i in done:
                continue

            print(f"Running #{i}: {q}")
            answer, tools, err = run_one(q)

            if err:
                print(f"   FAILED: {err[:150]}\n")
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    print("Daily quota used up. Run this script again later; "
                          "finished questions will be skipped.")
                    return
                continue  # other error: skip, try the next question

            block = (
                f"#{i}: {q}\n"
                f"Tools: {tools if tools else 'none'}\n"
                f"Answer: {answer}\n"
                f"{'-' * 60}\n"
            )
            print(block)
            out.write(block)
            out.flush()
            time.sleep(PAUSE_BETWEEN)

    remaining = [n for n in range(1, len(QUESTIONS) + 1) if n not in load_done()]
    if remaining:
        print(f"Still missing: {remaining}. Run again to retry them.")
    else:
        print("All 14 questions recorded in results.txt.")


if __name__ == "__main__":
    run_all()