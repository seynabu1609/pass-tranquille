-- ============================================================
-- A. CRÉATION DES ROUTES ET TRIPS AVEC HORAIRES TOUTE LA JOURNÉE
-- ============================================================

-- a. Route TER (1 ligne directe Dakar → Diamniadio) - Fréquence 20 min
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

-- b. Route BRT (1 ligne directe Petersen → Préfecture) - Fréquence 10 min
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

-- c. Routes BUS DDD (20 lignes avec 100 arrêts) - Fréquence 15 min
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