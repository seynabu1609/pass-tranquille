# 📊 Pass'Tranquille — Tâches Data : Nettoyage & Graphe
**Auteur :** Cissé  
**Formation :** Licence 3 Big Data — DIT Dakar  
**Projet :** Pass'Tranquille · Réseau multimodal Dakar · JOJ 2026  
**Superviseur :** Dr. Seydou Nourou Sylla  
**Date :** Juin 2026

---

## 📋 Contexte

Pass'Tranquille est une application de recommandation d'itinéraires multimodaux pour Dakar, conçue dans le cadre des Jeux Olympiques de la Jeunesse 2026. Ce document décrit les deux tâches réalisées par Cissé dans le cadre de la phase **Données** et de la phase **Modélisation** du projet.

| Tâche | Phase | Durée |
|-------|-------|-------|
| Nettoyage et documentation du dataset | Données | 2 jours |
| Construction du graphe multimodal | Modélisation | — |

**Source de données :** `01_schema_and_data.sql` — schéma PostgreSQL/PostGIS produit par Falilou (137 nœuds : 13 TER + 23 BRT + 82 BUS DDD + 19 POI JOJ 2026)

---

## 📁 Livrables

```
pass_tranquille_data/
│
├── notebook1_nettoyage_dataset.ipynb   ← Tâche 1 : Nettoyage & Documentation
├── notebook2_construction_graphe.ipynb ← Tâche 2 : Construction du graphe
│
├── stops_clean.csv      (généré par notebook 1)
├── graph_nodes.csv      (généré par notebook 2)
├── graph_edges.csv      (généré par notebook 2)
│
├── repartition_modes.png    (figure notebook 1)
├── carte_noeuds.png         (figure notebook 1)
├── graphe_multimodal.png    (figure notebook 2)
│
└── 01_schema_and_data.sql   ← fichier source (Falilou) à placer ici
```

> ⚠️ Le fichier `01_schema_and_data.sql` doit être placé dans le **même dossier** que les notebooks pour que le parsing fonctionne.

---

## 🧹 Tâche 1 — Nettoyage & Documentation du Dataset

**Fichier :** `notebook1_nettoyage_dataset.ipynb`

### Objectif
Extraire, auditer, corriger et documenter les données brutes du schéma SQL de Falilou avant leur utilisation dans le graphe.

### Méthodologie

Le dataset est parsé directement depuis le SQL source via expressions régulières Python, sans nécessiter une instance PostgreSQL active. Cette approche permet un audit indépendant de la base de données.

**5 dimensions de qualité évaluées :**

| Dimension | Score | Résultat |
|-----------|-------|----------|
| Complétude | ✅ 100% | Aucune valeur manquante |
| Unicité | ✅ 100% | Aucun doublon (nom ni coordonnées) |
| Validité géographique | ✅ 100% | Tous les points dans la zone Dakar |
| Cohérence des zones | ⚠️ 94% | 82 arrêts BUS avec zone générique (`Zone_Dakar`) |
| Cohérence des types | ✅ 100% | 4 modes corrects (TER / BRT / BUS / POI) |

**Score global : 98/100**

Le score de 94% sur la cohérence des zones est inhérent à la source : les arrêts DDD n'ont pas de zone géographique précise dans le SQL de Falilou (donnée non disponible).

### Corrections appliquées

- **Apostrophe SQL** : `Place de l''Indépendance` (notation SQL) → `Place de l'Indépendance` (UTF-8 correct)
- **Types de données** : coordonnées arrondies à 9 décimales (standard GPS WGS84)
- **Colonne `transport_type`** : convertie en catégorie ordonnée `['TER', 'BRT', 'BUS', 'POI']`
- **Colonne `mode_label`** : libellé complet ajouté (ex. `TER` → `Train Express Régional`)
- **Colonne `geom_wkt`** : géométrie au format WKT OGC (`POINT (lon lat)`, SRID 4326)

### Export produit

**`stops_clean.csv`** — 137 lignes × 7 colonnes :

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | int | Identifiant unique (1–137) |
| `name` | str | Nom de l'arrêt ou du POI |
| `longitude` | float | Coordonnée X (WGS84) |
| `latitude` | float | Coordonnée Y (WGS84) |
| `transport_type` | category | TER / BRT / BUS / POI |
| `zone` | str | Zone géographique |
| `mode_label` | str | Libellé complet du mode |
| `geom_wkt` | str | Géométrie WKT (SRID 4326) |

---

## 🕸️ Tâche 2 — Construction du Graphe Multimodal

**Fichier :** `notebook2_construction_graphe.ipynb`

### Objectif
Construire le graphe de transport multimodal de Dakar sous forme de graphe orienté NetworkX, en respectant exactement les règles de connectivité définies dans le SQL de Falilou, puis valider le graphe par des calculs d'itinéraires.

### Architecture du graphe

**Type :** `networkx.DiGraph` (orienté — cohérent avec `pgRouting directed=TRUE`)

**Nœuds :** 137 (arrêts + POI), chacun portant les attributs `name`, `transport_type`, `latitude`, `longitude`, `zone`

**Arêtes :** 4 types, construits selon les règles du SQL section 9 :

| Type | Règle | Vitesse |
|------|-------|---------|
| TER | Arrêts TER distants ≤ 50 km | 100 km/h |
| BRT | Arrêts BRT distants ≤ 3 km | 50 km/h |
| BUS | Arrêts DDD distants ≤ 2,5 km | 20 km/h |
| WALK | Modes différents ou vers/depuis POI ≤ 800 m | 4 km/h |

Les distances sont calculées via la **formule de Haversine** — identique au calcul `ST_Distance(...::geography)` de PostGIS utilisé dans le SQL source.

### Algorithmes implémentés

**Dijkstra** (`networkx.dijkstra_path`) — algorithme principal, identique à `pgr_dijkstra` de pgRouting, avec `travel_time` en secondes comme poids.

**A\*** (`networkx.astar_path`) — algorithme alternatif avec heuristique géographique Haversine, plus rapide sur les grands graphes (recommandé par le README de Falilou pour la suite).

### Tests de validation

Itinéraires testés (identiques aux exemples du README de Falilou) :

```
Gare de Dakar        → Diamniadio
Hôtel Pullman        → Dakar Arena
Musée des Civilisations Noires → Stade Abdoulaye Wade
Piscine Olympique    → Stade Abdoulaye Wade  (A*)
```

### Exports produits

**`graph_nodes.csv`** — 137 lignes, avec degré de chaque nœud dans le graphe

**`graph_edges.csv`** — toutes les arêtes avec colonnes :

| Colonne | Description |
|---------|-------------|
| `from_stop_id` | ID nœud source |
| `to_stop_id` | ID nœud cible |
| `from_name` / `to_name` | Noms lisibles |
| `distance_m` | Distance en mètres |
| `travel_time_s` | Temps de trajet en secondes |
| `transport_type` | TER / BRT / BUS / WALK |

Ces fichiers sont directement intégrables dans PostgreSQL via `COPY` et compatibles avec `pgr_createTopology()`.

---

## ⚙️ Installation & Exécution

### Prérequis Python

```bash
pip install pandas numpy matplotlib seaborn networkx
```

### Lancement

```bash
# S'assurer que 01_schema_and_data.sql est dans le dossier courant
jupyter notebook notebook1_nettoyage_dataset.ipynb
jupyter notebook notebook2_construction_graphe.ipynb
```

Les deux notebooks sont **indépendants** : chacun reparse le SQL source de manière autonome. Il n'est pas nécessaire d'exécuter le notebook 1 avant le notebook 2.

---

## 🔗 Intégration avec le reste du projet

| Tâche équipe | Lien avec ce travail |
|---|---|
| Falilou — Extraction OSM & schéma SQL | Source des données (`01_schema_and_data.sql`) |
| Alexis — Base PostgreSQL/PostGIS | `graph_edges.csv` → `COPY` dans la table `edges` |
| Moktar — Choix du modèle | Graphe NetworkX réutilisable + export compatible pgRouting |
| Yves — Backend | `graph_nodes.csv` et `graph_edges.csv` pour les endpoints `/route` |

### Intégration PostgreSQL

```sql
-- Importer les arêtes générées dans la base d'Alexis
COPY edges (from_stop_id, to_stop_id, distance, travel_time, transport_type)
FROM '/chemin/vers/graph_edges.csv' CSV HEADER ENCODING 'UTF8';

-- Reconstruire la topologie pgRouting
ALTER TABLE edges ADD COLUMN id SERIAL PRIMARY KEY;
ALTER TABLE edges ADD COLUMN source INT, ADD COLUMN target INT;
SELECT pgr_createTopology('edges', 0.00001);
```

---

## 📌 Points d'attention pour la suite

- Les arrêts **DDD BUS** n'ont pas de zone géographique précise — à enrichir si les données deviennent disponibles
- L'**Île de Gorée** (POI_19) n'est pas connectée au reste du graphe (accès uniquement par ferry, non modélisé)
- Les horaires GTFS (Falilou) sont simulés — à remplacer par les données officielles TER/BRT/DDD pour un calcul temporel réel
- Pour les JOJ 2026, envisager `pgr_dijkstraVia()` pour les itinéraires multi-étapes (hôtel → site A → site B)

---

*README rédigé par Cissé — Projet Pass'Tranquille · DIT Dakar · Juin 2026*
