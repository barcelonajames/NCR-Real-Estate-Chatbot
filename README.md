# NCR Real Estate Intelligence

### An AI-powered chatbot that helps Metro Manila residents
### find the right home — and understand what it will
### actually cost to live there.

---

## The Problem

Property listings in NCR show the rent. They don't show
the transport costs, utility bills, commute time, or flood
risk. For many workers, the "affordable" apartment 2 hours
from the office ends up costing more per month than a unit
closer to the CBD — once you count what listings never
mention.

---

## The Solution

A domain-specific AI chatbot built on Streamlit that
searches live property listings and answers real estate
questions in plain language — returning not just listings,
but a **True Monthly Cost** breakdown that surfaces the
full cost of inhabiting a property: rent + utilities +
transport + commute time value.

Ask it anything:

- *"What's a good area for a family of 4 near QC under ₱40k?"*
- *"Show me condos near BGC on a map"*
- *"What will it really cost me to live in Antipolo?"*
- *"Is it better to buy or rent in Pasig right now?"*

---

## My Contribution

This was a team project (4 members) built as part of
Uplift Code Camp's AI Startup Builder Challenge.

My role covered:

- **Concept and domain framing** — identified the
invisible cost gap as the core problem worth solving
- **True Monthly Cost framework** — originated and
defined the TMC metric as the product's signature
analytical insight
- **Prompt engineering and AI integration** — designed
the Claude Haiku prompt architecture across Steps 2
and 4 of the pipeline, and led the AI-assisted
development workflow that connected the pipeline
components
- **Pitch and storytelling** — led the narrative
structure of the presentation; the project was
commended by reviewers for narrative clarity and
real-world applicability

---

## Signature Feature — True Monthly Cost

The number that changes how people think about housing.

| Cost Component        | Example     |
| --------------------- | ----------- |
| Rent + condo dues     | ₱25,000     |
| Utilities             | ₱5,200      |
| Transport             | ₱8,500      |
| Time cost (commute)   | ₱5,400      |
| **True Monthly Cost** | **₱44,100** |

*The ₱19,100 gap is what listings never mention.*

---

## Tech Stack

| Tool         | Role                                          |
| ------------ | --------------------------------------------- |
| Streamlit    | Interface — sidebar filters, chat, maps       |
| Claude Haiku | AI brain — intent parsing + answer formatting |
| SearchAPI    | Live Google search — real property listings   |
| Python       | Pipeline glue — connects all components       |

---

## Pipeline Architecture
```
User types a question
↓
Step 1 — Streamlit: input validation + sidebar filters
↓
Step 2 — Claude Haiku: understands intent + builds search query
↓
Step 3 — SearchAPI: fetches live listings from Lamudi, Dot Property, etc.
↓
Step 4 — Claude Haiku: matches results + formats answer
↓
Step 5 — Streamlit: displays map / TMC / cards / chart
```

---

## Project Structure
```
NCR-Real-Estate-Chatbot/
├── app.py                  ← Main entry point
├── requirements.txt
├── .env.example            ← API key template
├── config/
│   └── prompts.py          ← Claude Haiku instructions
├── steps/                  ← 5-step pipeline
│   ├── step1_input.py
│   ├── step2_llm_intent.py
│   ├── step3_searchapi.py
│   ├── step4_llm_match.py
│   └── step5_display.py
├── components/             ← Display components
│   ├── map_view.py
│   ├── tmc_display.py
│   ├── comparison.py
│   ├── link_cards.py
│   └── charts.py
├── slides/
│   └── NCR Real Estate Intelligence – AI Startup Builder Challenge.pptx
└── utils/
    └── session.py
```

---

## Pitch Deck

Full project presentation including problem framing,
solution walkthrough, system architecture, and
future roadmap:

[View Presentation Deck](slides/NCR%20Real%20Estate%20Intelligence%20-%20AI%20Startup%20Builder%20Challenge.pptx)

[View on Google Drive (PDF)](https://drive.google.com/file/d/1fUlknXqe1qOOkzBZnaRSVwd-rZs3awA7/view?usp=sharing)

---

## Setup

### 1. Clone the repository
git clone https://github.com/barcelonajames/NCR-Real-Estate-Chatbot.git
cd NCR-Real-Estate-Chatbot

### 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up API keys

Copy `.env.example` to `.env` and fill in:

- `ANTHROPIC_API_KEY` — from console.anthropic.com
- `SEARCHAPI_KEY_1` through `SEARCHAPI_KEY_4` — from searchapi.io

### 5. Run the app
streamlit run app.py

Opens at **http://localhost:8501**

---

*Built as part of Uplift Code Camp —
AI Startup Builder Challenge, 2026*
