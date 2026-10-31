# Assignment 05 (ML-08): Capstone Modeling Lane

Notebook: [`work/notebooks/w05_model.ipynb`](../work/notebooks/w05_model.ipynb). Metrics receipt: [`work/outputs/w05_model_metrics.json`](../work/outputs/w05_model_metrics.json).

## What was asked

Build the right model for the lane and compare it with the week 4 baseline on the same data, split and metric. Use a valid validation design and explain the method choice. Report useful metrics, interpret the features or errors, and don't reward complexity for its own sake.

## What I built

Three classifiers (logistic regression, random forest, gradient boosting), each producing a ranking score from the predicted probability of decline. Eight features: the five from the week 3 contract plus CTR, CTR gap against the position tier (with tier medians fitted on training clients only) and the client's median momentum. Validation is 5-fold cross-validation grouped by client, with out-of-fold scores pooled so every method is ranked over the same 84,347 pages as the frozen week 4 rule. Two extra rows weight a score by March demand. The notebook also covers permutation importance, logistic coefficients, false positives, costly misses, and the overlap between the model's top 500 and the rule's. Seed is 42 throughout.

## How to run

Same setup as [assignment-03](../assignment-03/README.md), then:

```bash
jupyter nbconvert --to notebook --execute work/notebooks/w05_model.ipynb --output-dir /tmp
```

## Findings

| Method | ROC AUC | Avg precision | P@50 | P@500 | Demand captured@50 |
|---|---:|---:|---:|---:|---:|
| Week 4 rule | 0.595 | 0.389 | 0.96 | 0.874 | 0.069 |
| Logistic regression | 0.692 | 0.480 | 0.88 | 0.806 | 0.059 |
| Random forest | 0.706 | 0.497 | 0.94 | 0.820 | 0.007 |
| Gradient boosting | 0.693 | 0.477 | 0.88 | 0.798 | 0.044 |
| Rule x demand | 0.592 | 0.348 | 0.70 | 0.568 | 0.290 |
| Forest x demand | 0.521 | 0.287 | 0.48 | 0.378 | 0.508 |

The models rank the whole list better; the rule wins or ties in the top 50 to 500. Gradient boosting isn't better than the forest on any column. Weighted by demand, the forest finds much bigger declines at lower precision.

Momentum carries the forest: shuffling it costs about 0.20 average precision. Shuffling the client-level feature *improved* held-out results, a sign that it encodes client identity. The big misses are large, steady pages that collapsed in April with no warning in March.
