# FarmCredit: Credit Scoring and Embedded AI for Nigerian Agripreneurs

**FarmCredit** is a data-driven credit scoring and AI support system designed to empower young Nigerian farmers by improving access to affordable finance and providing personalized educational assistance. The project combines a heuristic credit scoring model, a continuously trained ML pipeline, and an advanced embedded AI system to address key barriers in agricultural finance.

---

## Table of Contents

* [Problem Statement](#problem-statement)
* [Heuristic Credit Scoring Model](#heuristic-credit-scoring-model)
* [ML Model Training and Inference Pipeline](#ml-model-training-and-inference-pipeline)
* [Embedded AI System](#embedded-ai-system)
* [Architecture Diagrams](#architecture-diagrams)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)

---

## Problem Statement

Agriculture employs over 35% of Nigeria's workforce but suffers from underinvestment due to limited access to affordable finance—especially for youth in rural areas. This challenge stems from perceived risks, lack of credit history, and data scarcity. FarmCredit seeks to bridge this gap with a data-driven credit scoring model and AI tools that enable lenders to confidently extend credit while educating and supporting farmers.

---

## Heuristic Credit Scoring Model

Inspired by traditional FICO scoring, our heuristic model calculates credit scores by aggregating five key components:

1. **Personal and Demographic Factors** (age, education, experience, family support)
2. **Financial History** (wallet balances, BVN verification, income sources, transaction patterns)
3. **Loan History** (repayment timeliness, debt load, loan applications)
4. **Agricultural Factors** (farm size, crop diversity, production history, profit margins)
5. **Geographical and Environmental Risks** (location risk zones, market proximity)

Each component is scored using domain heuristics, summed into a raw score (0–850), and scaled to a final score (300–850), which maps to a credit rating category (Excellent to Very Poor). This transparent approach enables immediate creditworthiness estimation in data-sparse environments.

---

## ML Model Training and Inference Pipeline

To improve predictive accuracy over time, FarmCredit continuously trains an ML model on real loan data:

* Loan data is migrated monthly from the operational database (AWS RDS) to AWS S3 for training.
* AWS SageMaker handles model training jobs and hosts the model endpoint.
* AWS Lambda functions orchestrate monthly training (triggered by EventBridge) and daily inference requests.
* Model predictions at loan request time are evaluated against actual repayment outcomes at maturity.
* Evaluation metrics feed a monitoring dashboard to track model performance and detect drift.

This cyclical pipeline allows FarmCredit to evolve from heuristic rules to a fully data-driven credit scoring system.

---

## Embedded AI System

FarmCredit integrates a Retrieval-Augmented Generation (RAG) AI assistant to enhance farmer support:

* Powered by AWS Bedrock’s large language models and AWS Managed Pinecone (vector database).
* Answers farmer queries about loans, balances, and credit status with personalized, real-time responses.
* Educates farmers on best agricultural and financial practices to promote knowledge growth.
* Provides a conversational interface embedded in the Farm Credit App for continuous engagement.

This embedded AI system improves financial inclusion by combining actionable insights with interactive education.

---


## Usage

* **Heuristic Model:** Expose the credit scoring function via AWS Lambda behind API Gateway for inference by the Farm Credit App.
* **ML Pipeline:** Configure EventBridge to trigger monthly training Lambda and daily inference Lambda for SageMaker interaction.
* **Embedded AI:** Connect the Farm Credit App API Gateway and Lambda to AWS Bedrock and Pinecone for intelligent query handling.

For detailed API documentation, please check the [docs.md](docs.md) file.

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for bug fixes, enhancements, or additional features.

---

## License

This project is licensed under the MIT License.
