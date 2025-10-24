MAX - A fraud detection system for embedded finance.

## Architecture

```
                                ┌─────────────────┐
                                │     frontend    │
                                └────────┬────────┘
                                         |
                                         ↓
                                ┌─────────────────┐
                                │     backend     │
                                └────────┬────────┘
                                         |           
                                         ↓
         ┌────────────────────┬────────────────────┬────────────────────┐
         ↓                    ↓                    ↓                    ↓
┌─────────────────┐  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   rule engine   │  │   descriptive   │ │   predictive    │ │ risk aggreagtion│ 
│                 │  │analytics engine │ │analytics engine │ │    engine       │
└─────────────────┘  └─────────────────┘ └─────────────────┘ └─────────────────┘


```
## Data flow

```
+--------------------+
                     
        ┌───────────────────────────────────────┐
        │            Ingestion                  │
        └─────────────────┬─────────────────────┘
                          │
                          │
                          ↓
        ┌───────────────────────────────────────┐
        │           BACKEND                     │
        │  - Orchestration (Workflows)          │
        │  - User Management (Auth)             │
        │  - Input/Ingestion                    │
        │  - Input Sanitization                 │
        └─────────────────┬─────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ↓               ↓               ↓
┌───────────────┐   ┌───────────┐ ┌──────────────┐
│ RULE ENGINE   │   │ ML MODEL  │ │   ANOMALY    │
│               │   │           │ │  DETECTION   │
│ Deterministic │   │ XGBoost/NN│ │              │
│ - Blacklist   |   | - Features| | Unsupervised |
| - Velocity    |   | - Scoring | | - Isolation  |
|               │   │           │ │ - Autoencoder|
└───────┬───────┘   └─────┬─────┘ └──────┬───────┘
        │                 │              │
        └─────────────────┼──────────────┘
                          ↓
        ┌───────────────────────────────────────┐
        │   RISK AGGREGATION ENGINE             │
        │                                       │
        │   Score = 0.3×Rule + 0.5×ML + 0.2×AD  │
        │                                       │
        │   Thresholds:                         │
        │   < 0.3  → Auto-Approve               │
        │   0.3-0.7 → Human Review              │
        │   > 0.7  → Auto-Block                 │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ↓               ↓               ↓
    ┌────────┐  ┌──────────────┐  ┌────────┐
    │APPROVE │  │ HUMAN REVIEW │  │ BLOCK  │
    └────────┘  └──────┬───────┘  └────────┘
                       │
                       │
                       ↓
        ┌──────────────────────────────────────┐
        │   FEEDBACK LOOP                      │
        │   Labels → Model Retraining          │
        └──────────────────────────────────────┘
                   
```


## Use cases

https://docs.google.com/spreadsheets/d/1YFAoreEE3M_yJxrjLkx92qoIPFh0YinAQshdZ5iMICQ/edit?usp=sharing


## components


## v2

- Model driven risk aggrigation engine

Use a second machine learning model (a "meta-learner" or "stacking model") that takes the three engine scores (ScoreR​,ScoreML​,ScoreDA​) as its input features and outputs the final risk score. This allows for a non-linear combination of the scores.

