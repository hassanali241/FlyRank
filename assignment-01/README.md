# Assignment 01 (ML-02): Research Question and Provisional Lane

The notebook for this assignment lives where the internship expects it:
[`work/notebooks/w01_research_question.ipynb`](../work/notebooks/w01_research_question.ipynb).
This folder is the index entry for it.

## What was asked

Pick a provisional lane from the lane guide (or go freestyle), then write the framing in a notebook: the search question, the unit of analysis, the output, the action someone takes from it, the cost of a wrong recommendation, and why data or ML helps at all. Back the lane choice with two or three real numbers from the starter dataset, and say carefully what the work can and can't claim.

## What I built

A filled and executed version of the week 1 skeleton. The provisional lane is Lane 2, Refresh / Content Opportunity Scoring, with the Growth / Recovery freestyle direction kept open for when I move to the warehouse. The unit is one page at a fixed decision point, and the output is a ranked review queue (top 50 to start) with a suggested action, reason codes and a confidence label for each page. Evaluation is planned as precision@K at the capacity cutoff plus a demand-weighted view, since missed declines on high-demand pages cost far more than the rest.

## How to run

From a fresh clone, at the repo root:

```bash
pip install -r assignment-01/requirements.txt jupyter
jupyter nbconvert --to notebook --execute work/notebooks/w01_research_question.ipynb --output-dir /tmp
```

Or open it in Colab and Run all. The notebook finds `data/raw/content_refresh_anonymized.csv` by walking up from wherever it's run, so no paths need editing.

## Findings

A "declining and visible" rule flags 13,152 pages (43.8% of the slice), about 263 times what a team can review in one cycle. Filtering alone doesn't help; the pages need an order.

Pages tagged as declining lost 47.9% of their prior-month impressions (29.4M down to 15.3M), and the top 10% of pages hold 70.2% of all impressions. There's real demand at stake, and it's concentrated.

The share of a client's pages tagged "down" ranges from 0% to 93.7%. On the worst client nearly every page dropped in the same month, which points to site-level effects rather than page-level decay. Client-holdout validation and client-relative features are needed.

The starter label can be rebuilt from the current 30-day windows on 100% of rows. It describes a drop that already happened, so the next step (week 2) is a target measured after the decision point.
