# Prompting Styles Evaluation

## Accuracy Results

| Style | Accuracy |
|---------|---------|
| Zero-shot | 100% |
| Few-shot | 96.67% |
| Role-based | 96.67% |

---

## Examples Where Zero-Shot Worked Well

### TCK-105
Ticket: Tracking status stuck in transit for five days.

Prediction: Shipping

Reason: The issue clearly relates to package delivery.

### TCK-118
Ticket: Account locked due to suspicious activity.

Prediction: Account

Reason: The ticket is directly related to account access and management.

### TCK-122
Ticket: Laptop charger becomes extremely hot.

Prediction: Product Quality

Reason: The issue concerns product safety and quality.

---

## Examples Where Few-Shot Worked Well

### TCK-109
Prediction: Login

Reason: The examples helped identify password reset and login-related issues.

### TCK-123
Prediction: Order Change

Reason: The examples clearly demonstrated order modification requests.

### TCK-120
Prediction: Product Quality

Reason: The damaged product closely matched the provided examples.

---

## Examples Where Role-Based Worked Well

### TCK-117
Prediction: Account

Reason: The request involves account deletion and user data management.

### TCK-119
Prediction: Product Quality

Reason: The role-based prompt correctly identified a defective product issue.

### TCK-127
Prediction: Other

Reason: The ticket is a sales inquiry rather than a support issue.

---

## Failure Cases

### Few-Shot Failure

#### TCK-106

Ticket:
I paid extra for overnight shipping, but my order arrived three days late. I need a refund for the shipping fees.

Ground Truth:
Shipping

Prediction:
Refund

Reason:
The model focused on the word "refund" instead of the main issue being delayed shipping.

---

### Role-Based Failure

#### TCK-106

Ticket:
I paid extra for overnight shipping, but my order arrived three days late. I need a refund for the shipping fees.

Ground Truth:
Shipping

Prediction:
Refund

Reason:
The model prioritized the refund request rather than the shipping problem.

---

### Zero-Shot Failures

No failures observed in this experiment.

---

## Conclusion

Zero-shot prompting achieved the highest accuracy (100%) on this dataset.

Few-shot and role-based prompting both achieved 96.67% accuracy and made the same mistake on TCK-106 by classifying it as Refund instead of Shipping.

This experiment suggests that for straightforward customer support ticket classification tasks, zero-shot prompting can perform extremely well when category definitions are clear.

Recommended usage:

- Zero-shot → Fast classification tasks with clearly defined categories.
- Few-shot → Useful when categories are ambiguous and examples can guide the model.
- Role-based → Useful when domain expertise or specialized reasoning is required.