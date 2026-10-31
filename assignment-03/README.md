# Assignment 03 (ML-04): Search Intelligence Data Contract

Notebook: [`work/notebooks/w03_data_contract.ipynb`](../work/notebooks/w03_data_contract.ipynb). Shared loader and frame builder: [`work/scripts/warehouse.py`](../work/scripts/warehouse.py).

## What was asked

Describe my lane's slice of the warehouse in five plain answers (row, tables, window, target, one exclusion). Prove three facts with three queries on a mid-panel month: grain, row count and date span, and availability filtered with `IS TRUE`. Build at most five features with an "available when?" line each. Add one label-derived column on purpose, watch the score jump, remove it. Name one limitation of the slice.

## What I built

The contract moves Lane 2 onto the warehouse release. One row is one page at a decision date (1 April 2026), with features from March 2026 only and the label from April only: declined by more than 20% per day and at least 20 points worse than the page's own client. The three queries run on `month=2026-03`. The five features are log impressions, days visible, impression-weighted position, late-month momentum and content age. The leak test uses a client-grouped holdout. The same frame builder is reused unchanged in weeks 4 to 6.

## How to run

```bash
pip install -r assignment-03/requirements.txt jupyter
```

Accept the gate on [`FlyRank/internship-warehouse`](https://huggingface.co/datasets/FlyRank/internship-warehouse), then set a Read token as `HF_TOKEN` (environment variable, or a Colab secret with that name). Never paste it into a cell.

```bash
jupyter nbconvert --to notebook --execute work/notebooks/w03_data_contract.ipynb --output-dir /tmp
```

Each monthly file (about 90 to 150 MB) downloads once and is cached by `huggingface_hub`. If you already have a local copy of the release with the same folder layout, point `FLYRANK_WAREHOUSE_DIR` at it to skip the download.

## Findings

The grain holds: zero duplicate (date, client, page) keys, and no page sits in two clients. March has 9,841,378 daily rows across 31 days, 55 clients and 331,437 pages.

Only 36.7% of rows survive `gsc_data_available IS TRUE`, and none of those has zero impressions. Search Console rows exist only on days a page was shown, so tracking coverage has to be checked per client, and a missing April row at a tracked client means zero impressions. The first draft of the frame got this wrong.

The slice holds 84,347 pages from 36 clients, with a 27.0% base rate. Adding the label-derived `change_pct` lifts held-out ROC AUC from 0.66 to 0.89; with it removed, 0.66 is the honest starting point.

Named limitation: staleness can't be measured at the decision date. 79.6% of pages carry a "last updated" date after 1 April, because the field is a July snapshot. Pages updated after 1 April declined less often (24.7% vs 36.1%), so a staleness feature would carry future information.
