# KartEase Support Agent

A customer support chatbot for a made-up online shop called **KartEase**.

You type a question in the terminal, and the agent answers it by using one or both of these tools:

- **Policy search** – looks up answers in 4 policy documents (returns, shipping, payments, warranty).
- **Order status** – looks up an order in a small `orders.csv` file.

If you ask something that is not about KartEase orders or policies, the agent politely says it cannot help.

---

## What this project uses

| Part | What I used |
| --- | --- |
| **Framework** | LangChain |
| **AI model** | Google Gemini free tier (model name is set in `.env` as `GEMINI_MODEL`) |
| **Vector database** | Chroma (saved in the `chroma_db/` folder) |
| **Embeddings** | Gemini embeddings (model name is set in `.env` as `GEMINI_EMBED_MODEL`) |
| **Tests** | pytest |
| **Language** | Python 3.10 or newer |

---

## Why I chose LangChain

I chose LangChain because it is a standard and widely used framework for building AI applications and agents. It provides ready-made components for loading documents, splitting text into chunks, working with Chroma DB, and defining agent tools. Turning plain Python functions into agent tools was clean, structured and easy to maintain.

---

## How it works (simple version)

1. **Ingest (`ingest.py`)** – The 4 policy files are cut into small pieces called *chunks* (11 chunks in total). Each chunk is turned into numbers (an *embedding*) using Gemini and saved in Chroma. This is done only once. If Chroma already has data, the script skips it so the free quota is not wasted.
2. **Policy search (`policy_search.py`)** – For a policy question, the 3 most similar chunks are retrieved from Chroma. Gemini is told to answer only from those chunks and to name the source file. If the answer is not in the chunks, it replies: *"Sorry, I can only help with KartEase orders and policies."*
3. **Order tool (`tools.py`)** – A plain Python function, `get_order_status`, that reads `orders.csv` and returns the product, status, dates and payment method for an order ID.
4. **Agent (`agent.py`)** – Gemini reads the question and the tool descriptions, then decides which tool to use: policy, order, both, or none.
5. **Chat loop (`app.py`)** – A simple terminal chat. After each answer it shows which tool(s) were used.

---

## Project files

```
kartease_starter/
├── data/                       4 policy documents (.md)
├── tests/
│   └── test_order_tool.py      pytest tests for the order tool
├── orders.csv                  sample orders
├── ingest.py                   builds the Chroma knowledge base
├── policy_search.py            policy question answering
├── tools.py                    get_order_status function
├── agent.py                    the agent that picks the tools
├── app.py                      terminal chat
├── run_tests.py                runs the 14 test questions
├── check_gemini.py             checks that the API key works
├── test_retrieval.py           checks that search finds the right chunks
├── results.txt                 saved answers from the 14 test questions
├── requirements-langchain.txt  packages to install
├── .env.example                example settings file
└── README.md
```

---

## Setup

You need **Python 3.10 or newer** and a free Gemini API key.

**1. Get the code**
```bash
git clone https://github.com/abireshu/kartease-support-agent.git
cd kartease-support-agent
```

**2. Create a virtual environment and turn it on**

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\activate
```
Mac or Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

**3. Install the packages**
```bash
pip install -r requirements-langchain.txt
```

**4. Add your API key**

- Get a free key from [Google AI Studio](https://aistudio.google.com/).
- Copy the example file:
  - Windows: `copy .env.example .env`
  - Mac or Linux: `cp .env.example .env`
- Open `.env` and paste your key after `GOOGLE_API_KEY=`.
- If the model in `.env` is no longer free, choose a free Flash model from AI Studio and change `GEMINI_MODEL`.

> Never share your `.env` file or upload it to GitHub. It is already listed in `.gitignore`.

**5. Check that Gemini works (optional)**
```bash
python check_gemini.py
```

---

## How to run

**Step 1 – Build the knowledge base (only once):**
```bash
python ingest.py
```
You should see that 11 chunks were created. If you run it again, it says Chroma already has data and skips it.

**Step 2 – Start the chat:**
```bash
python app.py
```
Type a question and press Enter. Type `exit` to quit.

Example:
```
You: Where is my order KE1002?
Agent: Your order KE1002 (Prestige pressure cooker) is Shipped and expected by 7 October 2026.
[Tools used: get_order_status]
```

**Run the unit tests:**
```bash
python -m pytest
```
These tests only check the order tool. They do not use Gemini, so they are fast and free.

**Run the 14 test questions:**
```bash
python run_tests.py
```
Answers are saved in `results.txt`. If the free daily quota runs out, run it again later. Questions that are already finished are skipped.

---

## Test results

I ran the 14 test questions through the agent. A question is a **Pass** only if the answer has the expected content **and** the right tools were used.

| # | Question | Expected | Tools used | Result |
| --- | --- | --- | --- | --- |
| 1 | How many days do I have to return a phone? | 10 days from delivery | search_policies | Pass |
| 2 | Can I return earbuds if I just don't like them? | No, hygiene reasons (unless damaged or defective) | search_policies | Pass |
| 3 | What is the delivery charge on a ₹350 order? | ₹40 (free from ₹499) | search_policies | Pass |
| 4 | If I order at 4 PM, when will it be dispatched? | Next working day (cut-off 2 PM) | TODO | TODO |
| 5 | Can I use a coupon together with a bank offer? | No | search_policies | Pass |
| 6 | How long is Extended Protection and when can I buy it? | 1 extra year; within 30 days of delivery | TODO | TODO |
| 7 | Can I pay cash on delivery for a ₹12,000 order? | No, COD only up to ₹10,000 | TODO | TODO |
| 8 | Where is my order KE1002? | Shipped; expected 2026-10-07 | TODO | TODO |
| 9 | What is the status of order ke1005? | Processing; expected 2026-10-08 | TODO | TODO |
| 10 | What is the status of order KE9999? | No order found | TODO | TODO |
| 11 | My return for KE1006 was picked up. When will I get my refund? | Quality check, then 5 to 7 working days to the debit card | TODO | TODO |
| 12 | I paid cash for KE1009. If I return it, how do I get my money back? | Cash on Delivery; refund to bank account or UPI in 5 to 7 working days | TODO | TODO |
| 13 | Who is the CEO of Google? | Sorry message | TODO | TODO |
| 14 | Write me a poem about Diwali. | Sorry message | TODO | TODO |

**Unit tests:** 3 pytest tests for the order tool, all passing (known order, lowercase order ID, unknown order).

### One fix I tried

- **Question that failed:** TODO
- **What went wrong:** TODO
- **What I changed (one thing only):** TODO
- **Result after the change:** TODO

---

## Known limitations

1. **Free-tier limits.** The free Gemini plan allows only about 20 requests per day for one model, and one question can use about 3 requests. Heavy testing can hit the limit or give temporary "high demand" errors.
2. **No memory.** Every question is answered on its own. If you ask "Where is my order KE1002?" and then "When will it arrive?", the agent does not know what "it" means.

---

## Demo

TODO: add your demo video link, or write "Live demo".

The demo shows 4 kinds of question:
1. Order question: "Where is my order KE1002?"
2. Policy question: "How many days do I have to return a phone?"
3. Both tools: "My return for KE1006 was picked up. When will I get my refund?"
4. Unrelated: "Write me a poem about Diwali."

---

## Author

TODO: your name and course or batch.
