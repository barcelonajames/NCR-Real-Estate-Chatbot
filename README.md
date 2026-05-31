# NCR Real Estate Intelligence Chatbot
**Uplift Code Camp — Capstone Project**

An AI-powered chatbot that helps users find, compare, and evaluate real estate in Metro Manila (NCR). Ask it anything — rental prices, commute costs, solar viability, or your True Monthly Cost.

---

## Team Setup (do this once, together)

### 1. Clone the project
```bash
git clone https://github.com/YOUR-ORG/ncr_realestate_chatbot.git
cd ncr_realestate_chatbot
```

### 2. Open in VS Code
- Open VS Code
- File → Open Folder → select `ncr_realestate_chatbot`

### 3. Create your virtual environment (optional but recommended)
In the VS Code terminal:
```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

### 4. Install all packages
```bash
pip install -r requirements.txt
```

### 5. Set up your API keys
- Copy `.env.example` and rename it to `.env`
- Open `.env` and fill in:
  - `ANTHROPIC_API_KEY` — one key shared by the team (from console.anthropic.com)
  - `SEARCHAPI_KEY_1` through `SEARCHAPI_KEY_4` — one per team member (from searchapi.io)

### 6. Run the app
```bash
streamlit run app.py
```
The app opens at **http://localhost:8501**

---

## Project Structure

```
ncr_realestate_chatbot/
├── app.py                  ← Main file. Run this to start the chatbot.
├── requirements.txt        ← All Python packages needed
├── .env.example            ← API key template (copy this to .env)
├── .gitignore              ← Tells Git to ignore sensitive files
│
├── config/
│   └── prompts.py          ← Instructions we give to Claude Haiku
│
├── steps/                  ← The 5-step pipeline
│   ├── step1_input.py      ← Sidebar filters + sanitization
│   ├── step2_llm_intent.py ← Haiku understands the question
│   ├── step3_searchapi.py  ← Fetches live property data
│   ├── step4_llm_match.py  ← Haiku formats the answer
│   └── step5_display.py    ← Shows the answer to the user
│
├── components/             ← Display components (maps, charts, etc.)
│   ├── map_view.py         ← Interactive Folium map
│   ├── tmc_display.py      ← True Monthly Cost breakdown
│   ├── comparison.py       ← Side-by-side comparison
│   ├── link_cards.py       ← Property listing cards
│   └── charts.py           ← Price trend charts
│
└── utils/
    └── session.py          ← Manages conversation memory
```

---

## How the Pipeline Works

```
User types a question
        ↓
Step 1 — Streamlit checks the message is safe (no API key needed)
        ↓
Step 2 — Claude Haiku understands what the user wants (ANTHROPIC_API_KEY)
        ↓
Step 3 — SearchAPI fetches live Google results (SEARCHAPI_KEY_1-4)
        ↓
Step 4 — Claude Haiku reads results + formats the best answer (ANTHROPIC_API_KEY)
        ↓
Step 5 — Streamlit displays the answer (map / cards / TMC / chart / text)
```

---

## Team Member Responsibilities

| Member | Owns |
|--------|------|
| Member 1 | `steps/step1_input.py` + all `components/` files |
| Member 2 | `steps/step2_llm_intent.py` + `steps/step4_llm_match.py` + `config/prompts.py` |
| Member 3 | `steps/step3_searchapi.py` + all 4 SearchAPI keys in `.env` |
| Member 4 | `app.py` + `utils/session.py` + merges all branches |

---

## GitHub Collaboration

```bash
# Create your own branch before making changes
git checkout -b member-1-frontend

# Stage and commit your changes
git add .
git commit -m "Add sidebar filter sections"

# Push your branch
git push origin member-1-frontend

# Create a Pull Request on GitHub for Member 4 to review and merge
```
