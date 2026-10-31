# Assignment 04 (ML-07): Baseline Action Score and Top-10 Review

Notebook: [`work/notebooks/w04_baseline_score.ipynb`](../work/notebooks/w04_baseline_score.ipynb). Metrics receipt: [`work/outputs/w04_baseline_metrics.json`](../work/outputs/w04_baseline_metrics.json).

## What was asked

Check two signals the rule leans on with bucket tables and n, at least one of them behind a real FlyRank flag, and give each a verdict. Encode one rule with a score, one reason code and an action label. Write the ranked queue to `work/outputs/baseline_action_score.csv` from the notebook. Review the top ten, saying for each why it's there and what would make it wrong. Confirm or switch the lane.

## What I built

The rule runs on the week 3 frame (1 April 2026 decision, March features, April label). The signals checked were volume (quick-win), CTR against its position tier (CTR-fix logic), and late-March momentum, which replaced volume once volume failed. The rule flags pages that slid through late March *and* sit below their tier's median CTR, and ranks them by how hard they slid. It has one reason code, `sliding_and_under_clicked`, and one action, `refresh_and_rewrite_snippet`. The notebook writes the full 84,347-row queue to the CSV, which git ignores by design and every run regenerates. The top ten each have a review line. Lane 2 is confirmed as the locked lane.

## How to run

Same setup as [assignment-03](../assignment-03/README.md) (requirements plus `HF_TOKEN`), then:

```bash
jupyter nbconvert --to notebook --execute work/notebooks/w04_baseline_score.ipynb --output-dir /tmp
```

## Findings

| Signal | Verdict | Evidence |
|---|---|---|
| Volume (quick-win) | OPPOSITE | decline rate falls from 31.3% (100-300 impressions) to 19.2% (10K+) |
| CTR vs position tier (CTR-fix) | CONFIRMED | 39.5% for pages far below their tier's CTR vs 16.4% far above |
| Late-March momentum | CONFIRMED | 51.9% for pages sliding hard vs about 17% for rising pages |

The rule flags 17.1% of pages. Precision is 1.00 at 20, 0.96 at 50, 0.874 at 500 and 0.832 at 1,000, against a 27.0% base rate (a random top 50 got 0.24). Demand captured at 50 is only 6.9%.

The top of the queue is mostly pages that had already dropped out of search: 23 of the top 50 had zero April impressions. They're real declines, but they need an indexing check, not a snippet rewrite. One client holds 13 of the 50 slots, and 485 pages show an impossible average position below 1.
