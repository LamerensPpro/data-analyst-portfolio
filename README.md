# Portfolio - Pascal Lamerens

Data Analyst | Power BI, SQL, Python | Certifié Wild Code School

---

## Projets

### [Projet 1 : Analyse des Salaires en France (1996-2022)](./Projet_1_Salaires_France/)

Dashboard Power BI analysant l'évolution des salaires en France sur 26 ans (données INSEE).

**Insights clés :**
- Les classes moyennes perdent le plus face au SMIC (-22%)
- Les inégalités H/F persistent à -21%
- Le SMIC rattrape tous les salaires

**Compétences :** Power Query, DAX, Modélisation en étoile, Data Storytelling

[Voir le projet →](./Projet_1_Salaires_France/)

---

### [Projet 2 : Data Cleaning - Retail Sales](./Projet_02_Data_Cleaning_Retail/)

Nettoyage et amélioration de la qualité d'un dataset de ventes retail volontairement "sale" (valeurs manquantes, doublons, incohérences).

**Compétences :** Python (Pandas), Data Quality, Documentation, Traçabilité des transformations

**Source :** [Kaggle - Retail Store Sales (Dirty)](https://www.kaggle.com/datasets/ahmedmohamed2003/retail-store-sales-dirty-for-data-cleaning)

[Voir le projet →](./Projet_02_Data_Cleaning_Retail/) 

---

### [Projet 3 : API Météo & Pollution - France](./Projet_03_API_Meteo_Pollution/)

Application Streamlit d'analyse météo et qualité de l'air pour 40 préfectures françaises via API Open-Meteo.

**Fonctionnalités :**
- Extraction temps réel (météo + qualité de l'air)
- Sélection région et ville
- Statistiques comparatives régionales
- Classements et visualisations

**Compétences :** Python (Requests, Pandas), Streamlit, API REST, Jointures de données, Matplotlib

**APIs utilisées :**
- [Open-Meteo Weather API](https://open-meteo.com/en/docs)
- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)

[Voir le projet →](./Projet_03_API_Meteo_Pollution/)

---

### [Projet 4 : SQL Avancé - E-Commerce Analytics](./Projet_04_SQL_Avance/)

Analyses SQL avancées sur une base e-commerce brésilienne (100k+ commandes) : analyses temporelles, segmentation clients, ranking vendeurs.

**Techniques SQL démontrées :**
- CTE (Common Table Expressions) multiples et imbriquées
- Window Functions (RANK, NTILE, LAG)
- Agrégations complexes avec PARTITION BY
- Analyses RFM (Recency, Monetary)
- Calculs de croissance temporelle

**Compétences :** SQLite, Requêtes complexes, VS Code (extension SQLite), Analyse métier

**Source :** [Kaggle - Olist E-Commerce Database](https://www.kaggle.com/datasets/terencicp/e-commerce-dataset-by-olist-as-an-sqlite-database)

[Voir le projet →](./Projet_04_SQL_Avance/)

---

### [Projet 5 : Pipeline Analytics Engineer - Données Boursières CAC 40](./Projet_05_Yahoo_Finance/)

Pipeline ELT complet avec orchestration Airflow, transformations dbt et analyse de 5 actions du CAC 40.

**Architecture complète :**
- Ingestion Python (full refresh + incrémental quotidien)
- Transformations dbt (Bronze → Silver → Gold)
- Orchestration Airflow (DAG automatisé)
- 12 tests qualité données automatisés

**Stack technique :** Python, PostgreSQL, dbt-core, Apache Airflow, Docker

**Compétences :** ELT, Analytics Engineering, Orchestration, Data Quality, Architecture en couches, Docker

[Voir le projet →](./Projet_05_Yahoo_Finance/)

---

### [Projet 6 : Crypto Dashboard - GCP · BigQuery · Looker Studio](./Projet_06_Crypto_GCP_BIGQUERY_LOOKER/)

Pipeline de données crypto end-to-end sur GCP avec dashboard analytique en temps réel.

**Architecture complète :**
- Ingestion Python via yfinance (BTC, ETH, SOL)
- Stockage BigQuery
- Automatisation Cloud Functions + Cloud Scheduler
- Métriques SQL (RSI, MACD, Moyennes Mobiles, Volatilité)
- Visualisation Looker Studio

**Métriques SQL :**
- [RSI (Relative Strength Index)](https://fr.wikipedia.org/wiki/Relative_strength_index)
- [MACD (Moving Average Convergence Divergence)](https://fr.wikipedia.org/wiki/MACD)
- [Moyennes Mobiles](https://fr.wikipedia.org/wiki/Moyenne_mobile)
- [Volatilité](https://fr.wikipedia.org/wiki/Volatilit%C3%A9_(finance))

**Stack technique :** Python, BigQuery, Cloud Functions, Cloud Scheduler, Looker Studio, GCP

**Compétences :** Pipeline cloud, Analytics Engineering, SQL avancé, Automatisation, Data Visualisation

**Dashboard live :** [Voir le dashboard →](https://datastudio.google.com/reporting/a109e328-2fd6-4231-9dce-7d509c84713f)

[Voir le projet →](./Projet_06_Crypto_GCP_BIGQUERY_LOOKER/)

---

### [Projet 7 : RH & Paie Analytics - Détection d'anomalies data quality](./Projet_07_RH_Paie_Analytics/)

Pipeline complet de génération, transformation et contrôle qualité de données RH/Paie, avec détection d'anomalies basée sur des règles métier réelles (pas de seuils arbitraires).

**Architecture complète :**
- Génération de données synthétiques réalistes (Python, Faker) : salariés, contrats, événements RH, paies
- Enrichissement historique SMIC via API OpenFisca (jointure `merge_asof` / fill-forward, pandas)
- Réévaluation annuelle du taux horaire (augmentation + alignement légal SMIC)
- Chargement BigQuery (Python, `google-cloud-bigquery`)
- Transformations dbt en couches (staging → intermediate → marts)
- **Détection d'anomalies via tests dbt singuliers** (`store_failures`), avec archivage horodaté dans une table d'historique dédiée — pas de logique de détection dupliquée entre modèles et tests
- Table de référence des anomalies (seed dbt) : code stable, libellé métier, domaine, niveau de criticité — sur le principe d'un référentiel validé par les métiers, pas de valeurs codées en dur
- Documentation dbt générée (lineage graph, descriptions de modèles et colonnes)
- 3 dashboards Looker Studio : RH (effectifs, absentéisme, turnover), Paie (masse salariale, cotisations), Qualité (suivi des anomalies dans le temps)

**Anomalies détectées (règles métier, pas de seuils arbitraires) :**
- Incohérence genre / NIR déclaré, NIR dupliqué
- Rétrogradation de catégorie socio-professionnelle
- Date d'événement antérieure à l'embauche
- CDD sans date de fin (obligation légale)
- Salaire sous le SMIC en vigueur à la date du bulletin
- Montant de paie incohérent avec la règle de calcul réelle (congé payé, arrêt maladie selon durée, maternité/paternité)

**Stack technique :** Python, Pandas, Faker, BigQuery, dbt-core, dbt tests (singuliers + `store_failures`), Looker Studio, Git (sparse-checkout)

**Compétences :** Data quality par la logique métier (pas la déduction statistique), architecture de tests dbt, réconciliation légale (SMIC, droit du travail), séparation Bronze/Silver/Gold, gouvernance de la donnée (table de référence des anomalies), observabilité (historisation des résultats de tests)

**Dashboards live :**
- [Dashboard RH →](https://datastudio.google.com/reporting/cf013c51-6502-44c7-9687-0c24e5246afa)
- [Dashboard Paie →](https://datastudio.google.com/reporting/332b2515-bfad-4794-a6c0-510e341cf69c)
- [Dashboard Qualité →](https://datastudio.google.com/reporting/f148711d-041f-4421-9558-6197f8faf88d)

[Voir le projet →](./Projet_07_RH_Paie_Analytics/)
