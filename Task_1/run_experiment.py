import json
import os
import csv
from collections import Counter

from groq import Groq
from dotenv import load_dotenv

# ==========================
# CONFIG
# ==========================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "llama-3.3-70b-versatile"

# Approximate Groq pricing
INPUT_COST_PER_MILLION = 0.59
OUTPUT_COST_PER_MILLION = 0.79

# ==========================
# LOAD PROMPTS
# ==========================

with open("prompts/direct.txt", "r") as f:
    DIRECT_PROMPT = f.read()

with open("prompts/cot.txt", "r") as f:
    COT_PROMPT = f.read()

with open("prompts/sc.txt", "r") as f:
    SC_PROMPT = f.read()

# ==========================
# LOAD SCENARIOS
# ==========================

scenarios = []

with open("scenarios.jsonl", "r") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        scenarios.append(json.loads(line))
# ==========================
# HELPERS
# ==========================

def estimate_cost(prompt_tokens, completion_tokens):
    input_cost = (
        prompt_tokens / 1_000_000
    ) * INPUT_COST_PER_MILLION

    output_cost = (
        completion_tokens / 1_000_000
    ) * OUTPUT_COST_PER_MILLION

    return input_cost + output_cost


def ask_model(prompt_text, temperature=0.0):

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=temperature,
        messages=[
            {
                "role": "user",
                "content": prompt_text
            }
        ]
    )

    answer = response.choices[0].message.content.strip()

    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens

    cost = estimate_cost(
        prompt_tokens,
        completion_tokens
    )

    return answer, cost


def normalize_answer(text):

    text = text.lower().strip()

    if "yes" in text:
        return "Yes"

    if "no" in text:
        return "No"

    return "Unknown"


def majority_vote(answers):
    counts = Counter(answers)
    return counts.most_common(1)[0][0]

# ==========================
# RUN EXPERIMENT
# ==========================

results = []

direct_correct_total = 0
cot_correct_total = 0
sc_correct_total = 0

direct_total_cost = 0
cot_total_cost = 0
sc_total_cost = 0

for scenario in scenarios:

    scenario_id = scenario["scenario_id"]
    ground_truth = scenario["ground_truth"]

    scenario_text = json.dumps(
        scenario,
        indent=2
    )

    # ----------------------
    # DIRECT
    # ----------------------

    direct_prompt = DIRECT_PROMPT.replace(
        "{scenario}",
        scenario_text
    )

    direct_answer_raw, direct_cost = ask_model(
        direct_prompt,
        temperature=0
    )

    direct_answer = normalize_answer(
        direct_answer_raw
    )

    direct_correct = int(
        direct_answer == ground_truth
    )

    # ----------------------
    # CoT
    # ----------------------

    cot_prompt = COT_PROMPT.replace(
        "{scenario}",
        scenario_text
    )

    cot_answer_raw, cot_cost = ask_model(
        cot_prompt,
        temperature=0
    )

    cot_answer = normalize_answer(
        cot_answer_raw
    )

    cot_correct = int(
        cot_answer == ground_truth
    )

    # ----------------------
    # SELF CONSISTENCY
    # ----------------------

    sc_answers = []
    sc_cost = 0

    for _ in range(5):

        answer_raw, run_cost = ask_model(
            cot_prompt,
            temperature=0.7
        )

        sc_answers.append(
            normalize_answer(answer_raw)
        )

        sc_cost += run_cost

    sc_answer = majority_vote(
        sc_answers
    )

    sc_correct = int(
        sc_answer == ground_truth
    )

    # ----------------------
    # ACCUMULATE
    # ----------------------

    direct_correct_total += direct_correct
    cot_correct_total += cot_correct
    sc_correct_total += sc_correct

    direct_total_cost += direct_cost
    cot_total_cost += cot_cost
    sc_total_cost += sc_cost

    results.append([
        scenario_id,
        direct_answer,
        direct_correct,
        cot_answer,
        cot_correct,
        sc_answer,
        sc_correct,
        round(direct_cost, 8),
        round(cot_cost, 8),
        round(sc_cost, 8)
    ])

    print(
        f"Scenario {scenario_id} completed"
    )

# ==========================
# SAVE CSV
# ==========================

with open("results.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "scenario_id",
        "direct_answer",
        "direct_correct",
        "cot_answer",
        "cot_correct",
        "sc_answer",
        "sc_correct",
        "direct_cost_usd",
        "cot_cost_usd",
        "sc_cost_usd"
    ])

    writer.writerows(results)

# ==========================
# METRICS
# ==========================

total = len(scenarios)

direct_accuracy = (
    direct_correct_total / total
)

cot_accuracy = (
    cot_correct_total / total
)

sc_accuracy = (
    sc_correct_total / total
)

direct_cpp = (
    direct_total_cost / direct_correct_total
    if direct_correct_total
    else 0
)

cot_cpp = (
    cot_total_cost / cot_correct_total
    if cot_correct_total
    else 0
)

sc_cpp = (
    sc_total_cost / sc_correct_total
    if sc_correct_total
    else 0
)

# ==========================
# REPORT
# ==========================

with open(
    "cot_decision_rule.md",
    "w"
) as f:

    f.write("# Chain-of-Thought Evaluation\n\n")

    f.write("## Accuracy\n\n")
    f.write("| Method | Accuracy |\n")
    f.write("|---------|----------|\n")
    f.write(
        f"| Direct | {direct_accuracy:.2%} |\n"
    )
    f.write(
        f"| CoT | {cot_accuracy:.2%} |\n"
    )
    f.write(
        f"| Self Consistency | {sc_accuracy:.2%} |\n\n"
    )

    f.write("## Total Cost\n\n")
    f.write("| Method | Cost |\n")
    f.write("|---------|---------|\n")
    f.write(
        f"| Direct | ${direct_total_cost:.6f} |\n"
    )
    f.write(
        f"| CoT | ${cot_total_cost:.6f} |\n"
    )
    f.write(
        f"| Self Consistency | ${sc_total_cost:.6f} |\n\n"
    )

    f.write("## Cost Per Correct Answer\n\n")
    f.write("| Method | Cost/Correct |\n")
    f.write("|---------|---------|\n")
    f.write(
        f"| Direct | ${direct_cpp:.6f} |\n"
    )
    f.write(
        f"| CoT | ${cot_cpp:.6f} |\n"
    )
    f.write(
        f"| Self Consistency | ${sc_cpp:.6f} |\n\n"
    )

    f.write("## Decision Rule\n\n")
    f.write(
        "- Use Direct Prompting for simple tasks and lowest cost.\n"
    )
    f.write(
        "- Use Chain-of-Thought when reasoning is required.\n"
    )
    f.write(
        "- Use Self-Consistency when maximum accuracy is needed.\n"
    )

print("\nExperiment completed successfully.")
print("Generated:")
print("- results.csv")
print("- cot_decision_rule.md")