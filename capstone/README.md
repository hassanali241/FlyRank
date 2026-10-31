# Capstone: Which pages should a content team review first?

**Paper:** https://hassanali241.github.io/FlyRank/ (source: [`docs/index.html`](../docs/index.html), data: [`docs/paper/results.json`](../docs/paper/results.json))
**Notebook:** [`work/notebooks/capstone.ipynb`](../work/notebooks/capstone.ipynb) · **Report:** [`work/capstone_report.md`](../work/capstone_report.md) · **Paper URL file:** [`submission/paper_url.txt`](../submission/paper_url.txt)

## What was asked

Pick a lane (or freestyle), build a repeatable model on real FlyRank search data, validate it honestly, and turn it into ranked content recommendations. Ship the result as a deployed research paper with nine sections (abstract through data credit), and record its URL in `submission/paper_url.txt`.

## What I built

Lane 2, Refresh / Content Opportunity Scoring, on the warehouse release. The notebook builds 346,229 page decisions across four months, each with features from one month and an outcome from the next. It compares the frozen week 4 rule with a seven-feature random forest under four designs: random split (the "before"), client-grouped, time-forward, and a sealed June month. It then retrains on all labeled months and scores a July review queue with an action and reason codes per page. The same notebook writes the data file the paper reads, so the paper's charts and numbers always match the last run.

The paper is a single static page in `docs/`, served by GitHub Pages from the `main` branch. Its charts are drawn in the browser from the notebook's data, with hover tooltips and light and dark themes, and it was checked at phone width.

## How to run

```bash
pip install -r assignment-06/requirements.txt jupyter
jupyter nbconvert --to notebook --execute --inplace work/notebooks/capstone.ipynb
```

This needs the Hugging Face gate accepted and `HF_TOKEN` set (see [assignment-03](../assignment-03/README.md)). To preview the paper locally: `python -m http.server --directory docs`, then open http://localhost:8000.

## Findings

| Design | Forest ROC AUC | Rule ROC AUC |
|---|---:|---:|
| Random 80/20 (before) | 0.748 | 0.593 |
| Grouped by client | 0.707 | 0.595 |
| Time-forward to May | 0.729 | 0.634 |
| Sealed June | 0.703 | 0.602 |

The forest ranks the whole list better in every honest design. For the top 50 to 500 pages a team can review, the two are level: 0.82 precision at 50 each on June, once one client that filled 495 of the rule's top 500 is excluded. Weighting by demand trades precision for size: the forest's top 50 then covers 60% of the June lost demand that the best possible top 50 could cover, but only 48% of those pages declined.

The July queue covers 96,727 pages from 43 clients. Its top 50 is capped at 10 per client: 25 refresh-and-rewrite, 14 refresh, 7 indexing checks, 2 snippet rewrites and 2 monitor.
