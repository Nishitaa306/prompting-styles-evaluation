# Chain-of-Thought Evaluation

## Accuracy

| Method | Accuracy |
|---------|----------|
| Direct | 100.00% |
| CoT | 100.00% |
| Self Consistency | 100.00% |

## Total Cost

| Method | Cost |
|---------|---------|
| Direct | $0.001953 |
| CoT | $0.003047 |
| Self Consistency | $0.015392 |

## Cost Per Correct Answer

| Method | Cost/Correct |
|---------|---------|
| Direct | $0.000130 |
| CoT | $0.000203 |
| Self Consistency | $0.001026 |

## Decision Rule

- Use Direct Prompting for simple tasks and lowest cost.
- Use Chain-of-Thought when reasoning is required.
- Use Self-Consistency when maximum accuracy is needed.
