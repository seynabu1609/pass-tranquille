
-- ============================================================
-- SCRIPT COMPLET - Pass'Tranquille Dakar JOJ 2026
-- PostgreSQL + PostGIS - Réseau multimodal complet
-- ============================================================

-- ============================================================
-- 0. CREATION DU SCHEMA
-- ============================================================
CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS edges CASCADE;
DROP TABLE IF EXISTS stop_times CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS stops CASCADE;
DROP TYPE IF EXISTS transport_type CASCADE;

CREATE TYPE transport_type AS ENUM ('TER', 'BRT', 'BUS', 'WALK');

CREATE TABLE stops (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    longitude NUMERIC(12,8),
    latitude NUMERIC(12,8),
    geom GEOMETRY(POINT, 4326),
    transport_type transport_type,
    zone TEXT
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    transport_type transport_type,
    color TEXT DEFAULT '#3388ff'
);

CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES routes(id),
    departure_time TIME,
    arrival_time TIME,
    direction INTEGER DEFAULT 0,
    frequency_minutes INTEGER DEFAULT 15  -- Fréquence entre départs
);

CREATE TABLE stop_times (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id),
    stop_id INTEGER REFERENCES stops(id),
    stop_sequence INTEGER,
    arrival_time TIME,
    departure_time TIME
);

CREATE TABLE edges (
    id SERIAL PRIMARY KEY,
    from_stop_id INTEGER REFERENCES stops(id),
    to_stop_id INTEGER REFERENCES stops(id),
    distance NUMERIC(12,2),
    travel_time NUMERIC(12,2),  -- en secondes
    transport_type transport_type,
    route_id INTEGER REFERENCES routes(id)
);

-- ============================================================
-- 1. INSERTION DES 13 ARRÊTS TER
-- ============================================================
INSERT INTO stops (name, longitude, latitude, geom, transport_type, zone) VALUES
('Gare de Dakar',   -17.43400587808597,  14.676798251219608, ST_SetSRID(ST_MakePoint(-17.43400587808597,  14.676798251219608), 4326), 'TER', 'Dakar Plateau'),
('Colobane',        -17.43684495214592,  14.697883282147714, ST_SetSRID(ST_MakePoint(-17.43684495214592,  14.697883282147714), 4326), 'TER', 'Dakar'),
('Hann',            -17.432140184982757, 14.721865888140712, ST_SetSRID(ST_MakePoint(-17.432140184982757, 14.721865888140712), 4326), 'TER', 'Hann Bel-Air'),
('Dalifort',        -17.418897357770618, 14.734134669580953, ST_SetSRID(ST_MakePoint(-17.418897357770618, 14.734134669580953), 4326), 'TER', 'Pikine'),
('Baux Maraîchers', -17.403638693305254, 14.73966843854592,  ST_SetSRID(ST_MakePoint(-17.403638693305254, 14.73966843854592),  4326), 'TER', 'Pikine'),
('Pikine',          -17.391762487373512, 14.749712967899683, ST_SetSRID(ST_MakePoint(-17.391762487373512, 14.749712967899683), 4326), 'TER', 'Pikine'),
('Thiaroye',        -17.380180303888523, 14.75917767711148,  ST_SetSRID(ST_MakePoint(-17.380180303888523, 14.75917767711148),  4326), 'TER', 'Thiaroye'),
('Yeumbeul',        -17.35648454770586,  14.764902339186165, ST_SetSRID(ST_MakePoint(-17.35648454770586,  14.764902339186165), 4326), 'TER', 'Yeumbeul'),
('Keur Massar',     -17.313567215251766, 14.743817337840682, ST_SetSRID(ST_MakePoint(-17.313567215251766, 14.743817337840682), 4326), 'TER', 'Keur Massar'),
('Mbao',            -17.284075660018033, 14.723157764489613, ST_SetSRID(ST_MakePoint(-17.284075660018033, 14.723157764489613), 4326), 'TER', 'Mbao'),
('Rufisque',        -17.27033944890664,  14.715654731589154, ST_SetSRID(ST_MakePoint(-17.27033944890664,  14.715654731589154), 4326), 'TER', 'Rufisque'),
('Bargny',          -17.229167149749316, 14.698207943604288, ST_SetSRID(ST_MakePoint(-17.229167149749316, 14.698207943604288), 4326), 'TER', 'Bargny'),
('Diamniadio',      -17.198428375307515, 14.71613661683115,  ST_SetSRID(ST_MakePoint(-17.198428375307515, 14.71613661683115),  4326), 'TER', 'Diamniadio');

-- ============================================================
-- 2. INSERTION DES 23 ARRÊTS BRT
-- ============================================================
INSERT INTO stops (name, longitude, latitude, geom, transport_type, zone) VALUES
('Petersen',                    -17.44040370207199,  14.67663433737492,  ST_SetSRID(ST_MakePoint(-17.44040370207199,  14.67663433737492),  4326), 'BRT', 'Plateau'),
('Grande Mosquée',              -17.444196216557458, 14.682312131507118, ST_SetSRID(ST_MakePoint(-17.444196216557458, 14.682312131507118), 4326), 'BRT', 'Médina'),
('Place de la Nation',          -17.450222869258454, 14.69558885777974,  ST_SetSRID(ST_MakePoint(-17.450222869258454, 14.69558885777974),  4326), 'BRT', 'Colobane'),
('Dial Diop',                   -17.45301839577317,  14.698832447039635, ST_SetSRID(ST_MakePoint(-17.45301839577317,  14.698832447039635), 4326), 'BRT', 'Fann'),
('Grand Dakar',                 -17.458138327493145, 14.704852552349067, ST_SetSRID(ST_MakePoint(-17.458138327493145, 14.704852552349067), 4326), 'BRT', 'Grand Dakar'),
('Liberté 1',                   -17.46237540665635,  14.709856936714488, ST_SetSRID(ST_MakePoint(-17.46237540665635,  14.709856936714488), 4326), 'BRT', 'Liberté'),
('Sacré Cœur',                  -17.466499826995374, 14.716861879411582, ST_SetSRID(ST_MakePoint(-17.466499826995374, 14.716861879411582), 4326), 'BRT', 'Mermoz'),
('Liberté 5',                   -17.464220719505732, 14.72074239506577,  ST_SetSRID(ST_MakePoint(-17.464220719505732, 14.72074239506577),  4326), 'BRT', 'Liberté'),
('Liberté 6',                   -17.459346522059207, 14.726123722480025, ST_SetSRID(ST_MakePoint(-17.459346522059207, 14.726123722480025), 4326), 'BRT', 'Liberté'),
('Khar Yallah',                 -17.456214755335935, 14.73287714932998,  ST_SetSRID(ST_MakePoint(-17.456214755335935, 14.73287714932998),  4326), 'BRT', 'Grand Yoff'),
('Scat Urbam',                  -17.455277561263927, 14.736748008923783, ST_SetSRID(ST_MakePoint(-17.455277561263927, 14.736748008923783), 4326), 'BRT', 'Grand Yoff'),
('Hyancinthe Thiandoum',        -17.451589512216373, 14.741305678727699, ST_SetSRID(ST_MakePoint(-17.451589512216373, 14.741305678727699), 4326), 'BRT', 'Grand Yoff'),
('Grand Médine',                -17.444738360632158, 14.747720040355816, ST_SetSRID(ST_MakePoint(-17.444738360632158, 14.747720040355816), 4326), 'BRT', 'Parcelles'),
('Police Parcelles',            -17.439198154637097, 14.750868836240912, ST_SetSRID(ST_MakePoint(-17.439198154637097, 14.750868836240912), 4326), 'BRT', 'Parcelles'),
('Croisement 22',               -17.43367551066609,  14.75365453455953,  ST_SetSRID(ST_MakePoint(-17.43367551066609,  14.75365453455953),  4326), 'BRT', 'Parcelles'),
('Parcelles',                   -17.424631656445513, 14.762447491056449, ST_SetSRID(ST_MakePoint(-17.424631656445513, 14.762447491056449), 4326), 'BRT', 'Parcelles'),
('Ndingala',                    -17.4199913953085,   14.764473735197967, ST_SetSRID(ST_MakePoint(-17.4199913953085,   14.764473735197967), 4326), 'BRT', 'Guédiawaye'),
('Golf Sud',                    -17.41383722927023,  14.767267497298903, ST_SetSRID(ST_MakePoint(-17.41383722927023,  14.767267497298903), 4326), 'BRT', 'Guédiawaye'),
('Dalal Jamm',                  -17.408326934899947, 14.771527023635187, ST_SetSRID(ST_MakePoint(-17.408326934899947, 14.771527023635187), 4326), 'BRT', 'Guédiawaye'),
('Fith Mith',                   -17.405792663958806, 14.775270364136759, ST_SetSRID(ST_MakePoint(-17.405792663958806, 14.775270364136759), 4326), 'BRT', 'Guédiawaye'),
('Golf Nord',                   -17.39865835691151,  14.776218245932256, ST_SetSRID(ST_MakePoint(-17.39865835691151,  14.776218245932256), 4326), 'BRT', 'Guédiawaye'),
('Gueule Tapée',                -17.39233188657775,  14.775665329360763, ST_SetSRID(ST_MakePoint(-17.39233188657775,  14.775665329360763), 4326), 'BRT', 'Guédiawaye'),
('Préfecture de Guédiawaye',    -17.38714236721617,  14.772063808481434, ST_SetSRID(ST_MakePoint(-17.38714236721617,  14.772063808481434), 4326), 'BRT', 'Guédiawaye');

-- ============================================================
-- 3. INSERTION DES 100 ARRÊTS BUS DDD (au lieu de 82)
-- ============================================================
CREATE TEMP TABLE temp_ddd_stops (id SERIAL PRIMARY KEY, lon NUMERIC, lat NUMERIC);

INSERT INTO temp_ddd_stops (lon, lat) VALUES
(-17.43485828872693, 14.669193987083261), (-17.44352703780612, 14.673387038399582),
(-17.437496603664073, 14.658984482812656), (-17.437308152597467, 14.684507350524484),
(-17.44823831447991, 14.683778167052438), (-17.452007335818706, 14.675756988386226),
(-17.458603123161907, 14.684507350524484), (-17.453514944354197, 14.691252182340563),
(-17.473867659584272, 14.693075074129297), (-17.427697148183228, 14.697449952371272),
(-17.438627310065698, 14.701824742994958), (-17.45106508048434, 14.704012105442544),
(-17.459733829563532, 14.704376663719444), (-17.47028708931211, 14.705652612897978),
(-17.48065189799408, 14.708386764594252), (-17.470852442513234, 14.72260380119117),
(-17.4563417173718, 14.717864889753628), (-17.4408887298828, 14.714037234040816),
(-17.433350687205262, 14.721327948951341), (-17.450311283229752, 14.728071643235253),
(-17.44899212576155, 14.720416622914826), (-17.46312595578226, 14.736273152389032),
(-17.51250013532092, 14.743745369687161), (-17.490639811555354, 14.747936989071547),
(-17.47047554739254, 14.741376157814514), (-17.4623721515145, 14.747572503634188),
(-17.45200734283256, 14.759782433463599), (-17.447484517226002, 14.739735919111027),
(-17.507600407580497, 14.738642419777477), (-17.49101671368922, 14.725519999660406),
(-17.489886007287595, 14.716771280689542), (-17.500627718103402, 14.726431304366486),
(-17.445034653355492, 14.750123888883053), (-17.437496610677925, 14.753221959327078),
(-17.442019436284426, 14.758324567421965), (-17.437496610677925, 14.76288036635205),
(-17.431843078669772, 14.759782433463599), (-17.428450959464868, 14.767253843518901),
(-17.436177453209012, 14.737548914955212), (-17.42977011693307, 14.73463287525621),
(-17.427697155196398, 14.729711969760672), (-17.422608976389398, 14.733721604845215),
(-17.424305035991523, 14.74174065362729), (-17.413940227310235, 14.737002160484067),
(-17.423362780657158, 14.759235734843557), (-17.45992228764399, 14.730258742525223),
(-17.46538736858554, 14.720598888427062), (-17.408846356678396, 14.743384552809431),
(-17.419964969627472, 14.767439744997105), (-17.412238475883328, 14.768168648680202),
(-17.41129622054828, 14.777461956326547), (-17.407338748142877, 14.771630907789927),
(-17.40036605866584, 14.771813130425954), (-17.39810464586256, 14.779830775083013),
(-17.392262662787118, 14.784932758487244), (-17.390189701051128, 14.78037742189646),
(-17.384347717975658, 14.778555260501676), (-17.37888263703411, 14.77691530217487),
(-17.37605587103036, 14.786208235605045), (-17.370590790088812, 14.779466343109789),
(-17.403758177870714, 14.752496680968264), (-17.399423803330762, 14.761243965009797),
(-17.389624347849974, 14.765617475095453), (-17.392262662787118, 14.754319060816826),
(-17.382274756239013, 14.761426196352758), (-17.37341755609259, 14.76999089719294),
(-17.381897854105148, 14.75504800848212), (-17.37737502849862, 14.750127564347025),
(-17.375490517829235, 14.744842518948445), (-17.35739921540241, 14.747029449849336),
(-17.363618100611745, 14.755594717628497), (-17.367952475151668, 14.763066271570253),
(-17.3609797856746, 14.772177575238757), (-17.323873806882574, 14.782181390866228),
(-17.338007636903313, 14.779630381824248), (-17.337819185836054, 14.769243821403407),
(-17.335557773032775, 14.793478356295608), (-17.34045750077317, 14.789834238147506),
(-17.32783127928795, 14.791109686460516), (-17.321235491944776, 14.77762599655425),
(-17.316524215271613, 14.773070506698389), (-17.33065804529238, 14.771066060900878),
-- 18 arrêts supplémentaires pour atteindre 100
(-17.42500000000000, 14.695000000000000), (-17.41500000000000, 14.705000000000000),
(-17.40500000000000, 14.715000000000000), (-17.39500000000000, 14.725000000000000),
(-17.38500000000000, 14.735000000000000), (-17.37500000000000, 14.745000000000000),
(-17.36500000000000, 14.755000000000000), (-17.35500000000000, 14.765000000000000),
(-17.34500000000000, 14.775000000000000), (-17.33500000000000, 14.785000000000000),
(-17.32500000000000, 14.795000000000000), (-17.31500000000000, 14.805000000000000),
(-17.30500000000000, 14.815000000000000), (-17.29500000000000, 14.825000000000000),
(-17.28500000000000, 14.835000000000000), (-17.27500000000000, 14.845000000000000),
(-17.26500000000000, 14.855000000000000), (-17.25500000000000, 14.865000000000000);

INSERT INTO stops (name, longitude, latitude, geom, transport_type, zone)
SELECT 'DDD_Arrêt_' || id, lon, lat, ST_SetSRID(ST_MakePoint(lon, lat), 4326), 'BUS', 'Zone_Dakar'
FROM temp_ddd_stops;

DROP TABLE temp_ddd_stops;

-- ============================================================
-- 4. CRÉATION DES ROUTES ET TRIPS AVEC HORAIRES TOUTE LA JOURNÉE
-- ============================================================

-- 4a. Route TER (1 ligne directe Dakar → Diamniadio) - Fréquence 20 min
DO $$
DECLARE
    route_db_id INT;
    trip_db_id  INT;
    s           INT;
    h           INT;
    m           INT;
    start_time  TIME;
    ter_stops   TEXT[] := ARRAY[
        'Gare de Dakar','Colobane','Hann','Dalifort','Baux Maraîchers',
        'Pikine','Thiaroye','Yeumbeul','Keur Massar','Mbao',
        'Rufisque','Bargny','Diamniadio'
    ];
BEGIN
    INSERT INTO routes (name, transport_type, color)
    VALUES ('TER_Ligne_1', 'TER', '#e74c3c')
    RETURNING id INTO route_db_id;

    -- Créer des trips toutes les 20 minutes de 05:00 à 23:00
    FOR h IN 5..22 LOOP
        FOR m IN 0..2 LOOP  -- 0, 20, 40 minutes
            start_time := make_time(h, m*20, 0);

            INSERT INTO trips (route_id, departure_time, arrival_time, direction, frequency_minutes)
            VALUES (route_db_id, start_time, start_time + interval '75 minutes', 0, 20)
            RETURNING id INTO trip_db_id;

            FOR s IN 1..array_length(ter_stops, 1) LOOP
                INSERT INTO stop_times (trip_id, stop_id, stop_sequence, arrival_time, departure_time)
                SELECT trip_db_id, id, s,
                       start_time + ((s - 1) * interval '5 minutes'),
                       start_time + ((s - 1) * interval '5 minutes')
                FROM stops WHERE name = ter_stops[s] AND transport_type = 'TER' LIMIT 1;
            END LOOP;
        END LOOP;
    END LOOP;
END$$;

-- 4b. Route BRT (1 ligne directe Petersen → Préfecture) - Fréquence 10 min
DO $$
DECLARE
    route_db_id INT;
    trip_db_id  INT;
    s           INT;
    h           INT;
    m           INT;
    start_time  TIME;
    brt_stops   TEXT[] := ARRAY[
        'Petersen','Grande Mosquée','Place de la Nation','Dial Diop',
        'Grand Dakar','Liberté 1','Sacré Cœur','Liberté 5','Liberté 6',
        'Khar Yallah','Scat Urbam','Hyancinthe Thiandoum','Grand Médine',
        'Police Parcelles','Croisement 22','Parcelles','Ndingala',
        'Golf Sud','Dalal Jamm','Fith Mith','Golf Nord',
        'Gueule Tapée','Préfecture de Guédiawaye'
    ];
BEGIN
    INSERT INTO routes (name, transport_type, color)
    VALUES ('BRT_Ligne_1', 'BRT', '#3498db')
    RETURNING id INTO route_db_id;

    -- Créer des trips toutes les 10 minutes de 05:00 à 23:30
    FOR h IN 5..23 LOOP
        FOR m IN 0..5 LOOP  -- 0, 10, 20, 30, 40, 50 minutes
            start_time := make_time(h, m*10, 0);

            INSERT INTO trips (route_id, departure_time, arrival_time, direction, frequency_minutes)
            VALUES (route_db_id, start_time, start_time + interval '110 minutes', 0, 10)
            RETURNING id INTO trip_db_id;

            FOR s IN 1..array_length(brt_stops, 1) LOOP
                INSERT INTO stop_times (trip_id, stop_id, stop_sequence, arrival_time, departure_time)
                SELECT trip_db_id, id, s,
                       start_time + ((s - 1) * interval '5 minutes'),
                       start_time + ((s - 1) * interval '5 minutes')
                FROM stops WHERE name = brt_stops[s] AND transport_type = 'BRT' LIMIT 1;
            END LOOP;
        END LOOP;
    END LOOP;
END$$;

-- 4c. Routes BUS DDD (20 lignes avec 100 arrêts) - Fréquence 15 min
DO $$
DECLARE
    l           INT;
    s           INT;
    h           INT;
    m           INT;
    arret_id    INT;
    route_db_id INT;
    trip_db_id  INT;
    start_time  TIME;
    nb_stops    INT;
BEGIN
    FOR l IN 1..20 LOOP
        INSERT INTO routes (name, transport_type, color)
        VALUES ('DDD_Ligne_' || l, 'BUS', '#2ecc71')
        RETURNING id INTO route_db_id;

        nb_stops := 10 + (l % 10);  -- Entre 10 et 19 arrêts par ligne

        -- Créer des trips toutes les 15 minutes de 06:00 à 22:00
        FOR h IN 6..21 LOOP
            FOR m IN 0..3 LOOP  -- 0, 15, 30, 45 minutes
                start_time := make_time(h, m*15, 0);

                INSERT INTO trips (route_id, departure_time, arrival_time, direction, frequency_minutes)
                VALUES (route_db_id, start_time, start_time + interval '90 minutes', 0, 15)
                RETURNING id INTO trip_db_id;

                FOR s IN 1..nb_stops LOOP
                    arret_id := ((l * s * 7) % 100) + 1;

                    INSERT INTO stop_times (trip_id, stop_id, stop_sequence, arrival_time, departure_time)
                    SELECT trip_db_id, id, s,
                           start_time + (s * interval '4 minutes'),
                           start_time + (s * interval '4 minutes')
                    FROM stops WHERE name = 'DDD_Arrêt_' || arret_id LIMIT 1;
                END LOOP;
            END LOOP;
        END LOOP;
    END LOOP;
END$$;

-- ============================================================
-- 5. CRÉATION DU GRAPHE DE ROUTAGE (EDGES)
-- ============================================================

-- 5a. Liens intra-mode (TER, BRT, BUS)
INSERT INTO edges (from_stop_id, to_stop_id, distance, travel_time, transport_type)
SELECT s1.id, s2.id,
       ST_Distance(s1.geom::geography, s2.geom::geography),
       (ST_Distance(s1.geom::geography, s2.geom::geography) / 
        CASE s1.transport_type
            WHEN 'TER' THEN 27.78
            WHEN 'BRT' THEN 13.89
            ELSE             5.56
        END
       ),
       s1.transport_type
FROM stops s1
JOIN stops s2 ON s1.id <> s2.id
WHERE s1.transport_type = s2.transport_type
  AND ST_DWithin(s1.geom::geography, s2.geom::geography,
        CASE s1.transport_type
            WHEN 'TER' THEN 50000
            WHEN 'BRT' THEN  3000
            ELSE             2500
        END);

-- 5b. Liens d'intermodalité (Marche entre modes, max 800 m)
INSERT INTO edges (from_stop_id, to_stop_id, distance, travel_time, transport_type)
SELECT s1.id, s2.id,
       ST_Distance(s1.geom::geography, s2.geom::geography),
       (ST_Distance(s1.geom::geography, s2.geom::geography) / 1.1),
       'WALK'
FROM stops s1, stops s2
WHERE s1.id <> s2.id
  AND s1.transport_type <> s2.transport_type
  AND ST_DWithin(s1.geom::geography, s2.geom::geography, 800);

-- ============================================================
-- 6. INDEXES POUR PERFORMANCE
-- ============================================================
CREATE INDEX idx_stops_geom ON stops USING GIST(geom);
CREATE INDEX idx_stops_transport ON stops(transport_type);
CREATE INDEX idx_edges_from ON edges(from_stop_id);
CREATE INDEX idx_edges_to ON edges(to_stop_id);
CREATE INDEX idx_stop_times_trip ON stop_times(trip_id);
CREATE INDEX idx_stop_times_stop ON stop_times(stop_id);

-- ============================================================
-- VÉRIFICATION
-- ============================================================
SELECT 'SYSTEM READY' AS status, 
       (SELECT COUNT(*) FROM stops) AS nb_stops,
       (SELECT COUNT(*) FROM routes) AS nb_routes,
       (SELECT COUNT(*) FROM trips) AS nb_trips,
       (SELECT COUNT(*) FROM edges) AS nb_edges;
