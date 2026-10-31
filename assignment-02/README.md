# Assignment 02 (ML-03): Frame Your Lane as an ML Task

The notebook lives where the internship expects it:
[`work/notebooks/w02_ml_task_framing.ipynb`](../work/notebooks/w02_ml_task_framing.ipynb).
This folder is the index entry for it.

## What was asked

Turn the week 1 lane into a concrete ML task: name the task type, define the target (and whether it comes from an observed outcome or a rule), pick one success metric with a number that means "good", show the unit of analysis as a real dataframe, and argue why ML beats a fixed rule for this problem.

## What I built

A filled and executed week 2 skeleton for Lane 2 (Refresh / Content Opportunity Scoring). The task is ranking, done pointwise: a classifier estimates the chance a page declines in the next window, and the queue is sorted on that. The notebook proposes a future-window target for the warehouse (90-day feature window, next-30-day decline of more than 20%, a 100-impression volume floor, and a 20-point margin against the client's own median change). It also tests how much the volume floor and client adjustment strip from the starter proxy. The metrics are precision@50 on held-out clients plus demand captured@50, both written as reusable functions, with the "good" thresholds fixed before any training. Every one of the 44 starter columns gets a role (id, label source, window overlap, excluded, candidate feature).

## How to run

From a fresh clone, at the repo root:

```bash
pip install -r assignment-02/requirements.txt jupyter
jupyter nbconvert --to notebook --execute work/notebooks/w02_ml_task_framing.ipynb --output-dir /tmp
```

Or open it in Colab and Run all. The random ordering uses seed 42, so outputs reproduce exactly.

## Findings

Most of the starter "decline" label isn't page-level. Adding a 100-impression floor removes about 5,200 positives, and requiring a page to drop 20 points more than its own client's median brings the positive rate among eligible pages from 61.6% down to 25.0%.

Precision and demand disagree. On the starter proxy, sorting by page size captures 47% of the best possible lost demand in its top 50 but has the lowest precision (0.42), while sorting by staleness has base-rate precision (0.52) and captures none. Both metrics stay.

No single signal separates the classes well; the best (page age) reaches an AUC of 0.59. Signals also interact: for pages older than a year the decline rate falls from 0.50 to 0.20 as position worsens, while for pages aged 91 to 180 days it rises from 0.62 to 0.76 between page 1 and pages 3 to 5. That conditional, spread-out pattern is the case for a model over an if-statement, with the caveat that part of the starter signal shares days with the label windows.
