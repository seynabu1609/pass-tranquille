--
-- PostgreSQL database dump
--

\restrict SLtzOynaVqDX9u5IOr8sEgZavOqinxK500o7RhkhCZaf0ft63Y5AzFoaW66s1pf

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-06-14 14:22:08

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 8 (class 2615 OID 31517)
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- TOC entry 6111 (class 0 OID 0)
-- Dependencies: 8
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- TOC entry 2 (class 3079 OID 30435)
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- TOC entry 6112 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- TOC entry 3 (class 3079 OID 31518)
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- TOC entry 6113 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 236 (class 1259 OID 31717)
-- Name: aretes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.aretes (
    id integer NOT NULL,
    noeud_debut integer,
    noeud_fin integer,
    distance_m double precision,
    mode character varying(50),
    temps_pointe double precision,
    temps_normal double precision,
    temps_soir double precision,
    geom public.geometry(LineString,4326)
);


ALTER TABLE public.aretes OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 31716)
-- Name: aretes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.aretes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.aretes_id_seq OWNER TO postgres;

--
-- TOC entry 6114 (class 0 OID 0)
-- Dependencies: 235
-- Name: aretes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.aretes_id_seq OWNED BY public.aretes.id;


--
-- TOC entry 234 (class 1259 OID 31707)
-- Name: noeuds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.noeuds (
    id integer NOT NULL,
    nom character varying(255),
    type character varying(50),
    geom public.geometry(Point,4326)
);


ALTER TABLE public.noeuds OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 31706)
-- Name: noeuds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.noeuds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.noeuds_id_seq OWNER TO postgres;

--
-- TOC entry 6115 (class 0 OID 0)
-- Dependencies: 233
-- Name: noeuds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.noeuds_id_seq OWNED BY public.noeuds.id;


--
-- TOC entry 238 (class 1259 OID 31737)
-- Name: sites_joj; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sites_joj (
    id integer NOT NULL,
    nom character varying(255),
    type_site character varying(100),
    adresse text,
    geom public.geometry(Point,4326)
);


ALTER TABLE public.sites_joj OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 31736)
-- Name: sites_joj_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sites_joj_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sites_joj_id_seq OWNER TO postgres;

--
-- TOC entry 6116 (class 0 OID 0)
-- Dependencies: 237
-- Name: sites_joj_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sites_joj_id_seq OWNED BY public.sites_joj.id;


--
-- TOC entry 5924 (class 2604 OID 31720)
-- Name: aretes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aretes ALTER COLUMN id SET DEFAULT nextval('public.aretes_id_seq'::regclass);


--
-- TOC entry 5923 (class 2604 OID 31710)
-- Name: noeuds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noeuds ALTER COLUMN id SET DEFAULT nextval('public.noeuds_id_seq'::regclass);


--
-- TOC entry 5925 (class 2604 OID 31740)
-- Name: sites_joj id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites_joj ALTER COLUMN id SET DEFAULT nextval('public.sites_joj_id_seq'::regclass);


--
-- TOC entry 6103 (class 0 OID 31717)
-- Dependencies: 236
-- Data for Name: aretes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.aretes (id, noeud_debut, noeud_fin, distance_m, mode, temps_pointe, temps_normal, temps_soir, geom) FROM stdin;
\.


--
-- TOC entry 6101 (class 0 OID 31707)
-- Dependencies: 234
-- Data for Name: noeuds; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.noeuds (id, nom, type, geom) FROM stdin;
\.


--
-- TOC entry 6105 (class 0 OID 31737)
-- Dependencies: 238
-- Data for Name: sites_joj; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sites_joj (id, nom, type_site, adresse, geom) FROM stdin;
\.


--
-- TOC entry 5915 (class 0 OID 30754)
-- Dependencies: 223
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- TOC entry 5917 (class 0 OID 31520)
-- Dependencies: 228
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.topology (id, name, srid, "precision", hasz, useslargeids) FROM stdin;
\.


--
-- TOC entry 5918 (class 0 OID 31539)
-- Dependencies: 229
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.layer (topology_id, layer_id, schema_name, table_name, feature_column, feature_type, level, child_id) FROM stdin;
\.


--
-- TOC entry 6117 (class 0 OID 0)
-- Dependencies: 235
-- Name: aretes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.aretes_id_seq', 1, false);


--
-- TOC entry 6118 (class 0 OID 0)
-- Dependencies: 233
-- Name: noeuds_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.noeuds_id_seq', 1, false);


--
-- TOC entry 6119 (class 0 OID 0)
-- Dependencies: 237
-- Name: sites_joj_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sites_joj_id_seq', 1, false);


--
-- TOC entry 6120 (class 0 OID 0)
-- Dependencies: 227
-- Name: topology_id_seq; Type: SEQUENCE SET; Schema: topology; Owner: postgres
--

SELECT pg_catalog.setval('topology.topology_id_seq', 1, false);


--
-- TOC entry 5941 (class 2606 OID 31725)
-- Name: aretes aretes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aretes
    ADD CONSTRAINT aretes_pkey PRIMARY KEY (id);


--
-- TOC entry 5939 (class 2606 OID 31715)
-- Name: noeuds noeuds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noeuds
    ADD CONSTRAINT noeuds_pkey PRIMARY KEY (id);


--
-- TOC entry 5945 (class 2606 OID 31745)
-- Name: sites_joj sites_joj_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites_joj
    ADD CONSTRAINT sites_joj_pkey PRIMARY KEY (id);


--
-- TOC entry 5942 (class 1259 OID 31747)
-- Name: idx_aretes_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_aretes_geom ON public.aretes USING gist (geom);


--
-- TOC entry 5937 (class 1259 OID 31746)
-- Name: idx_noeuds_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_noeuds_geom ON public.noeuds USING gist (geom);


--
-- TOC entry 5943 (class 1259 OID 31748)
-- Name: idx_sites_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sites_geom ON public.sites_joj USING gist (geom);


--
-- TOC entry 5946 (class 2606 OID 31726)
-- Name: aretes aretes_noeud_debut_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aretes
    ADD CONSTRAINT aretes_noeud_debut_fkey FOREIGN KEY (noeud_debut) REFERENCES public.noeuds(id);


--
-- TOC entry 5947 (class 2606 OID 31731)
-- Name: aretes aretes_noeud_fin_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aretes
    ADD CONSTRAINT aretes_noeud_fin_fkey FOREIGN KEY (noeud_fin) REFERENCES public.noeuds(id);


-- Completed on 2026-06-14 14:22:08

--
-- PostgreSQL database dump complete
--

\unrestrict SLtzOynaVqDX9u5IOr8sEgZavOqinxK500o7RhkhCZaf0ft63Y5AzFoaW66s1pf

