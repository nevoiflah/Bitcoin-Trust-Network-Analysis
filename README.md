# Bitcoin Trust Network Analysis and Fraud Detection

Final project — Graph Algorithms (אלגוריתמים בגרפים), Ruppin Academic College, 2026.

Full write-up: [דוח מסכם - פרויקט ביטקוין.pdf](דוח%20מסכם%20-%20פרויקט%20ביטקוין.pdf) (Hebrew)

## Overview

Bitcoin trading is pseudonymous: a user is identified only by a wallet address, with no name, address, or verifiable history. In peer-to-peer (P2P) trading, where buyer and seller transact directly, this creates a hard trust problem. Platforms like Bitcoin OTC address it with a **Web of Trust** — after each trade, users rate each other from −10 to +10.

That mechanism is itself attackable. In a **Sybil attack**, a scammer spins up a cluster of fake accounts that rate each other highly to manufacture reputation quickly, then defrauds users who relied on the score.

This project applies graph algorithms and machine learning to the Bitcoin OTC rating network to identify prominent scammers, uncover Sybil-style communities, and predict whether a future interaction will be honest or fraudulent — using **network topology alone**, with no identity information.

## Dataset

[Stanford SNAP — `soc-sign-bitcoinotc`](https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html), covering 2010–2016.

| | |
|---|---|
| Ratings (edges) | 35,592 |
| Users (nodes) | 5,881 |
| Positive edges (Trust Network) | 32,029 (~90%) |
| Negative edges (Distrust Network) | 3,563 (~10%) |

The notebook loads the dataset directly from SNAP at runtime — **nothing needs to be downloaded**.

## Methodology

A directed, weighted graph is built with NetworkX, then split into a Trust Network (rating > 0) and a Distrust Network (rating < 0) so each can be measured with an appropriate metric.

**1. Centrality and reputation**
- **PageRank** on the Trust Network — scores reliability by the *quality* of who vouches for you, not just the count. A scammer boosted only from inside their own clique scores poorly, because their raters score poorly themselves.
- **Weighted In-Degree** on the Distrust Network — sums the *magnitude* of negative ratings absorbed, surfacing repeat offenders.

**2. Community detection (Louvain)**
Louvain (modularity maximization, resolution 1.0, `seed=42`) partitions the Trust Network. Each of the 20 largest communities is then scanned for **external distrust**: the total negative rating it absorbed from users *outside* it, normalized by community size. A high ratio marks a group the wider network distrusts while its members endorse each other — the signature of a Sybil cluster.

**3. Link prediction (Random Forest)**
Split **chronologically** at January 2014 to avoid data leakage: the training graph and all its centrality metrics are computed from pre-2014 data only. Five structural features per user pair — PageRank of source and target, common neighbours, target in-degree, source out-degree — feed a 100-tree Random Forest with `class_weight='balanced'`.

## Key Findings

**Ratings are not bipolar.** Contrary to the intuitive expectation, ratings concentrate at *low positive* values: **+1 and +2 alone are 72%** of all ratings, and only 10.2% have magnitude ≥ 8. Notably **−10 (6.8%) is over three times more common than +10 (2.1%)** — users extend trust cautiously in small increments but reach for the maximum penalty when they detect fraud. This asymmetry is what justifies splitting the graph in the first place.

**Trust is extremely concentrated.** In-degree in the Trust Network follows a power law: median 2 positive ratings per user, 80.4% of users with ≤ 5, while the top 1% hold 23.3% of all positive ratings (top user: 535). Most users have too little history to establish reputation — which is precisely the gap scammers exploit.

**A Sybil cluster is clearly identifiable.** Louvain found 42 communities (largest: 875, 858, 773, 533, 523 members). Community **#15** stands out sharply:

| Community | Size | External distrust | Ratio per member |
|---|---|---|---|
| **#15** | 32 | 4,365 | **136.41** |
| #12 | 64 | 1,772 | 27.69 |
| #10 | 76 | 1,710 | 22.50 |

32 users absorbing 4,365 units of negative rating from outside the group — a 5× margin over the next-worst community.

**One user sits on both leaderboards.** User 1810 ranks 5th by PageRank (0.0076) *and* 2nd by negative in-degree (−385) — consistent with a reputation built honestly and then cashed in, a commercial rivalry, or a compromised account.

**Topology alone predicts trust well, and fraud better than it first appears.** On a chronological test set of 2,529 pairs (338 fraud, 2,191 trust):

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Trust | 0.87 | 0.99 | 0.93 |
| Fraud @ default 0.5 threshold | 0.64 | 0.07 | 0.13 |
| **Fraud @ tuned 0.11 threshold** | 0.28 | **0.44** | **0.34** |

Overall accuracy 0.87. Fraud recall of 0.07 at the default threshold looks like a model that learned nothing about fraud — but that reading is wrong. `predict()` thresholds at 0.5, and with ~87% of edges positive almost nothing clears it; `class_weight='balanced'` reweights each tree's split criterion but never moves that cut-off. Judged as a *ranking*, the model achieves **AP = 0.30 against a 0.134 random baseline (2.2×)** with ROC-AUC 0.70. Lowering the threshold to 0.11 lifts fraud recall to 0.44 and F1 to 0.34 with no retraining. The right way to deploy this is as a ranked risk score with a tunable operating point, chosen by the relative cost of a missed scam versus a false accusation.

## Conclusions

Legitimate and malicious activity can be separated in a pseudonymous network by examining interaction topology alone. Community detection exposes coordinated Sybil groups; supervised link prediction scores individual future interactions. Remaining headroom is in the **features** rather than the threshold — an AP of 0.30 still leaves most fraud low in the ranking. Natural extensions are explicit Structural Balance features (balanced/unbalanced triad counts), resampling such as SMOTE, and a GNN over the signed graph.

## Repository Structure

| File | Contents |
|---|---|
| `Bitcoin_Network_Analysis.ipynb` | Full analysis — loading, EDA, centrality, Louvain, link prediction, threshold analysis |
| `דוח מסכם - פרויקט ביטקוין.pdf` | Final report (Hebrew, 8 pages) |
| `דו_ח_מסכם_פרויקט_ביטקוין.md` | Report source |
| `bitcoin_scam_detection.pptx` | Milestone presentation |
| `eda_ratings.png`, `eda_indegree.png`, `pr_curve.png` | Figures used in the report |

## Running It

```bash
pip install networkx pandas matplotlib seaborn scikit-learn
jupyter notebook Bitcoin_Network_Analysis.ipynb
```

Then run all cells. The notebook installs its own dependencies in the first cell and fetches the dataset from SNAP, so it runs end-to-end on a clean machine with no manual setup.

Results are reproducible (`seed=42` for Louvain, `random_state=42` for the Random Forest). Note that Random Forest output can shift marginally across scikit-learn versions; the committed outputs were produced with scikit-learn 1.6.1.

## Team

The work was carried out jointly and in equal measure by all three members — every stage was discussed, designed, and implemented together. Leading responsibilities:

- **נבו יפלח** — data loading and processing, EDA and network distribution visualisations, centrality metrics (PageRank, weighted In-Degree); introduction, motivation, and dataset sections of the report.
- **ליאל ירדני** — link prediction model: chronological split, structural feature extraction, Random Forest training, threshold analysis; results section of the report.
- **אילן קוזוקרו** — Louvain community detection, malicious-community logic based on external distrust ratio, notebook integration and commentary; related work and conclusions sections of the report.

## References

1. S. Kumar, F. Spezzano, V.S. Subrahmanian, C. Faloutsos. *Edge Weight Prediction in Weighted Signed Networks.* ICDM, 2016.
2. J. Leskovec, D. Huttenlocher, J. Kleinberg. *Signed Networks in Social Media.* ACM CHI, 2010.
3. J. Leskovec, A. Krevl. *SNAP Datasets: Stanford Large Network Dataset Collection.* https://snap.stanford.edu/data, 2014.
