# Bitcoin Trust Network Analysis and Fraud Detection

## Overview
This project focuses on analyzing the "Web of Trust" within the Bitcoin OTC platform to identify fraudulent behavior and malicious actors. Bitcoin transactions are inherently anonymous, making face-to-face (P2P) trading susceptible to scams. To mitigate this, platforms like Bitcoin OTC rely on a user-rating system. However, this system is vulnerable to Sybil attacks, where scammers create fake communities and positive ratings to build false reputation before defrauding victims.

The primary objective of this project is to apply graph theory algorithms and machine learning techniques to the Bitcoin OTC trust network to detect scammers, identify malicious communities, and accurately predict whether future interactions will be reliable or fraudulent.

## Methodology and Algorithms
The project involves constructing a Directed Weighted Graph from the raw transaction and rating data. We then apply the following analytical models:

### 1. Centrality and Reputation Analysis
We divided the graph into a "Trust Network" (edges > 0) and a "Distrust Network" (edges < 0). 
- **PageRank:** Applied to the Trust Network to identify the core reliable users and establish a baseline for platform reputation.
- **Weighted In-Degree:** Applied to the Distrust Network to pinpoint the most prominent scammers who received the highest volume of negative reviews.

### 2. Community Detection (Louvain Algorithm)
We utilized the Louvain algorithm on the Trust Network to detect dense communities. Following this, we implemented a mechanism to scan each community and evaluate the volume of negative ratings (distrust) it received from outside the community. A high ratio of external distrust relative to the community's size strongly indicates a malicious group attempting to generate a fake internal reputation bubble.

### 3. Link Prediction (Machine Learning)
To predict the reliability of future connections, we split the data chronologically (around the year 2014) to prevent data leakage. We built a training graph using only the early years and extracted structural features for user pairs, including:
- Common Neighbors
- Degree rankings
- PageRank scores

We then trained a Random Forest classification model to predict whether future transactions would be categorized as reliable or fraudulent.

## Key Findings
- **Exploratory Data Analysis (EDA):** The vast majority of transactions are positive, resulting in a large Trust Network. However, negative transactions are highly concentrated around specific nodes that accumulate significant distrust, indicating targeted fraudulent activity rather than random dissatisfaction.
- **Malicious Community Detection:** The community detection algorithm successfully identified small groups that exchanged positive ratings internally but received severe negative ratings from central, reliable users outside the group. This confirms the presence of identity-forging mechanisms on the platform.
- **Prediction Accuracy:** The Link Prediction model achieved strong accuracy in forecasting future connections. Structural metrics like "Common Neighbors" and user Centrality proved sufficient to provide early warnings about the likelihood of fraud in future transactions, even between completely anonymous users who had not previously interacted.

## Conclusions
This analysis demonstrates the power of graph algorithms in financial cybersecurity. It highlights that legitimate and malicious activities can be effectively separated within an anonymous, blockchain-like network solely by examining the topology of user interactions. Combining community detection for Sybil attack identification with machine learning for individual transaction reliability prediction provides a robust framework that can be implemented in real-time trading platforms to protect users.

## Team Contributions
The project work was divided as follows:
- **Data Processing and EDA:** Responsible for cleaning raw data, applying centrality metrics (PageRank and In-Degree), visualizing network distributions, and writing the introduction and motivation sections.
- **Link Prediction Model:** Responsible for developing the chronological Train/Test split, extracting features from the graph for the machine learning model, and writing the results section.
- **Community Detection:** Responsible for implementing the Louvain algorithm, developing the logic to identify malicious communities based on external negative ratings, integrating the code into the Jupyter Notebook, and writing the conclusions.

## Repository Structure
- `Bitcoin_Network_Analysis.ipynb`: The main Jupyter Notebook containing all data processing, graph algorithms, and machine learning models.
- `soc-sign-bitcoinotc.csv.gz`: The compressed dataset used for the analysis.
- Project reports and presentation materials.

## Requirements
To run the analysis, you will need the following Python libraries:
- networkx
- pandas
- matplotlib
- scikit-learn
