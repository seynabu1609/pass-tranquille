# pass-tranquille
Application d'itinéraires pour les JOJ Dakar 2026


##  Description
Pass Tranquille permet de calculer le meilleur itinéraire entre deux points 
à Dakar en combinant le réseau routier, le TER et le BRT.

##  Architecture
 Sous-système  Description 
 OS1 – Métier 
 OS2 – Données : Collecte et traitement des données géospatiales 
 OS3 – Modèle : Algorithme de calcul d'itinéraires 
 OS4 – Plateforme : Interface utilisateur Streamlit 

## Équipe
- Mame Seynabou NDIAYE – Cheffe de projet
- Mouhamed CISSE – 
- Mouhamadou Falilou DIAGNE –
- Yves Chadrac KATE – 
- Alexis Mando NGODJI –
- Moktar Yacin 

##  Technologies
Python · PostgreSQL/PostGIS · OSMNX · NetworkX · Streamlit · GTFS

## Structure du projet

pass-tranquille/
├── data/              → Données brutes et nettoyées
├── notebooks/         → Analyses exploratoires
├── src/
│   ├── data_pipeline/ → OS2
│   ├── model/         → OS3
│   ├── backend/       → OS1
│   └── frontend/      → OS4
├── tests/
└── docs/              → Documentation et rapports
\```
