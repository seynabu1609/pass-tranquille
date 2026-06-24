-- ============================================================
-- Pass'Tranquille — Dakar JOJ 2026
-- Construction du Graphe de Routage (Edges)
-- Auteur : Cissé
-- Date   : Juin 2026
-- ============================================================
-- Ce script construit les arêtes du graphe multimodal à partir
-- des arrêts déjà insérés dans la table stops.
-- À exécuter APRÈS le script principal (01_database_schema.sql)
-- ============================================================

-- ============================================================
-- ÉTAPE 1 — Liens intra-mode (TER, BRT, BUS)
-- ============================================================
-- Pour chaque paire d'arrêts du même mode de transport,
-- on calcule la distance réelle avec ST_Distance (en mètres)
-- puis on divise par la vitesse du mode pour obtenir le temps
-- de trajet en secondes (poids de l'arc dans le graphe).
--
-- Vitesses utilisées :
--   TER  → 27,78 m/s  (100 km/h)
--   BRT  → 13,89 m/s  (50 km/h)
--   BUS  →  5,56 m/s  (20 km/h)
--
-- Seuils de connexion :
--   TER  → arrêts distants ≤ 50 000 m
--   BRT  → arrêts distants ≤  3 000 m
--   BUS  → arrêts distants ≤  2 500 m
-- ============================================================

INSERT INTO edges (from_stop_id, to_stop_id, distance, travel_time, transport_type)
SELECT
    s1.id,
    s2.id,
    ST_Distance(s1.geom::geography, s2.geom::geography)          AS distance,
    ST_Distance(s1.geom::geography, s2.geom::geography) /
        CASE s1.transport_type
            WHEN 'TER' THEN 27.78   -- 100 km/h en m/s
            WHEN 'BRT' THEN 13.89   -- 50  km/h en m/s
            ELSE             5.56   -- 20  km/h en m/s (BUS)
        END                                                       AS travel_time,
    s1.transport_type
FROM stops s1
JOIN stops s2 ON s1.id <> s2.id
WHERE s1.transport_type = s2.transport_type
  AND ST_DWithin(
        s1.geom::geography,
        s2.geom::geography,
        CASE s1.transport_type
            WHEN 'TER' THEN 50000   -- 50 km
            WHEN 'BRT' THEN  3000   -- 3 km
            ELSE             2500   -- 2,5 km (BUS)
        END
      );

-- ============================================================
-- ÉTAPE 2 — Liens d'intermodalité (marche entre modes ≤ 800 m)
-- ============================================================
-- Si deux arrêts de modes différents sont à moins de 800 mètres
-- l'un de l'autre, on crée automatiquement un arc de type WALK.
-- Vitesse piétonne : 1,1 m/s (≈ 4 km/h).
--
-- C'est cette étape qui rend le réseau véritablement multimodal :
-- l'algorithme Dijkstra peut changer de transport en cours de
-- route en empruntant ces arcs de marche.
-- ============================================================

INSERT INTO edges (from_stop_id, to_stop_id, distance, travel_time, transport_type)
SELECT
    s1.id,
    s2.id,
    ST_Distance(s1.geom::geography, s2.geom::geography)          AS distance,
    ST_Distance(s1.geom::geography, s2.geom::geography) / 1.1    AS travel_time,
    'WALK'
FROM stops s1, stops s2
WHERE s1.id <> s2.id
  AND s1.transport_type <> s2.transport_type
  AND ST_DWithin(s1.geom::geography, s2.geom::geography, 800);

-- ============================================================
-- VÉRIFICATION
-- ============================================================

SELECT
    transport_type  AS mode,
    COUNT(*)        AS nb_aretes,
    ROUND(AVG(distance)::numeric, 0)     AS distance_moy_m,
    ROUND(AVG(travel_time)::numeric, 0)  AS temps_moy_s
FROM edges
GROUP BY transport_type
ORDER BY transport_type;

SELECT
    'GRAPHE PRÊT'           AS status,
    COUNT(*)                AS total_aretes,
    SUM(CASE WHEN transport_type = 'TER'  THEN 1 ELSE 0 END) AS aretes_ter,
    SUM(CASE WHEN transport_type = 'BRT'  THEN 1 ELSE 0 END) AS aretes_brt,
    SUM(CASE WHEN transport_type = 'BUS'  THEN 1 ELSE 0 END) AS aretes_bus,
    SUM(CASE WHEN transport_type = 'WALK' THEN 1 ELSE 0 END) AS aretes_walk
FROM edges;
