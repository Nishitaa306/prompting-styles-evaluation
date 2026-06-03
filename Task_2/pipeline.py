import os
import json
from groq import Groq
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# =====================================================
# CONFIGURATION
# =====================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "llama-3.3-70b-versatile"

# =====================================================
# LOAD PROMPTS
# =====================================================

with open("prompts/extract.txt", "r") as f:
    extract_prompt_template = f.read()

with open("prompts/generate.txt", "r") as f:
    generate_prompt_template = f.read()

with open("prompts/select.txt", "r") as f:
    select_prompt_template = f.read()

with open("brand_rules.md", "r") as f:
    brand_rules = f.read()

# =====================================================
# PRODUCT BRIEFS
# =====================================================

product_briefs = [
    "NovaFit Smart Bottle tracks hydration, syncs with a mobile app, and sends reminders for busy professionals.",

    "LunaGlow Desk Lamp automatically adjusts brightness, reduces eye strain, and is designed for students.",

    "TrailMate Backpack includes waterproof storage, solar charging, and ergonomic support for hikers.",

    "FreshBox Smart Fridge Organizer monitors food freshness and helps families reduce food waste.",

    "EchoBuds Wireless Earbuds provide active noise cancellation, long battery life, and are designed for commuters."
]

# =====================================================
# LLM CALL FUNCTION
# =====================================================

def call_llm(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# =====================================================
# SAFE JSON PARSER
# =====================================================

def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        return {
            "error": "Invalid JSON returned",
            "raw_output": text
        }

# =====================================================
# CREATE RUNS DIRECTORY
# =====================================================

os.makedirs("runs", exist_ok=True)

# =====================================================
# PIPELINE EXECUTION
# =====================================================

for idx, brief in enumerate(product_briefs, start=1):

    print(f"\nRunning Pipeline for Brief {idx}")

    run_folder = f"runs/run_{idx}"
    os.makedirs(run_folder, exist_ok=True)

    # -------------------------------------------------
    # Save Input Brief
    # -------------------------------------------------

    with open(f"{run_folder}/input_brief.txt", "w") as f:
        f.write(brief)

    # =================================================
    # STEP 1 - EXTRACT
    # =================================================

    extract_prompt = extract_prompt_template.format(
        product_brief=brief
    )

    step1_output = call_llm(extract_prompt)

    with open(f"{run_folder}/step1_attributes.json", "w") as f:
        f.write(step1_output)

    # =================================================
    # STEP 2 - GENERATE
    # =================================================

    generate_prompt = generate_prompt_template.format(
        attributes_json=step1_output
    )

    step2_output = call_llm(generate_prompt)

    with open(f"{run_folder}/step2_variants.json", "w") as f:
        f.write(step2_output)

    # =================================================
    # STEP 3 - SELECT
    # =================================================

    select_prompt = select_prompt_template.format(
        brand_rules=brand_rules,
        variants=step2_output
    )

    step3_output = call_llm(select_prompt)

    with open(f"{run_folder}/step3_winner.json", "w") as f:
        f.write(step3_output)

    print(f"Completed Run {idx}")

print("\nAll 5 pipeline runs completed successfully!")