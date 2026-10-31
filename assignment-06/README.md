# Assignment 06 (ML-09): Validation and Research Claim Audit

Notebook: [`work/notebooks/w06_validation_audit.ipynb`](../work/notebooks/w06_validation_audit.ipynb).

## What was asked

Pick two findings from FlyRank's research paper and, constructively, ask where each label comes from and whether the validation carries the claim. Then audit my own week 5 model: re-run it under a grouped or time-aware split with a before/after comparison, audit the features for leakage, show real failure examples, and rewrite my own claims in safe language.

## What I built

The paper questions cover Finding #4 (the refresh "multiplier") and the ML appendix growth model (71% holdout accuracy). For the second, I worked out from the paper's own counts that always predicting growth would score 62.1%. The week 5 forest is re-run three ways, with the frozen rule scored on the same rows each time:
- a random 80/20 split, as the paper did;
- grouped by client;
- time-forward: trained on March and April decisions, tested on May.

The leakage audit runs as code assertions, plus two train-with/train-without tests: the client-level feature, which is now dropped, and staleness from the July snapshot. The sealed June month is opened once with the final seven-feature model. The notebook ends with failure examples from June and three of my own sentences rewritten.

## How to run

Same setup as [assignment-03](../assignment-03/README.md). It needs the February to June 2026 monthly files (about 640 MB, downloaded once):

```bash
jupyter nbconvert --to notebook --execute work/notebooks/w06_validation_audit.ipynb --output-dir /tmp
```

## Findings

| Design | Forest AUC | Forest AP | Rule AUC | Rule AP |
|---|---:|---:|---:|---:|
| Before: random 80/20 (April) | 0.767 | 0.571 | 0.593 | 0.393 |
| After: grouped by client (April) | 0.706 | 0.497 | 0.595 | 0.389 |
| After: time-forward to May | 0.732 | 0.580 | 0.634 | 0.471 |
| May, unseen clients only | 0.748 | 0.596 | 0.662 | 0.498 |
| Sealed June, final model | 0.703 | 0.496 | 0.602 | 0.399 |

The random split overstated the forest by about 0.06 AUC and 0.07 average precision. Under time-forward validation the signal holds, including on clients the model never saw.

In June the rule's perfect precision (1.00 at 500) is one client's churn: 495 of its top 500 pages came from a single client. Without that client, the forest and the rule tie at 0.82 for the top 50.

The client-level feature was dropped: it helped only where clients repeat between training and test. Snapshot staleness gave no score jump, but stays excluded on design grounds, since 80.9% of its values come after the decision date.
