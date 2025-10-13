--
-- PostgreSQL database cluster dump
--

\restrict oRiqchj0NxqdED83L1mUDAnYMh0xKOA63Ve5JkPGRq37RvY0u8UFV1N9oUCHtiX

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:4ra1HinWGoqNVHJ3w/tpjg==$3KhAytVJs1CCRwkdIHFwlHwgV9/Crv9b8STdADGAJ9w=:4qIxUWVlFXdpAF7beTjPEbmam+q7PKlsL3twJ1/f1Oo=';

--
-- User Configurations
--






\unrestrict oRiqchj0NxqdED83L1mUDAnYMh0xKOA63Ve5JkPGRq37RvY0u8UFV1N9oUCHtiX

--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

\restrict w85fSMspDprlT8dHJpgXPCKC5GKZDSm39x3DQ1Rt4MhzLjvBEDvnzMx0JCBnt4I

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-0+deb13u1)

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
-- PostgreSQL database dump complete
--

\unrestrict w85fSMspDprlT8dHJpgXPCKC5GKZDSm39x3DQ1Rt4MhzLjvBEDvnzMx0JCBnt4I

--
-- Database "db" dump
--

--
-- PostgreSQL database dump
--

\restrict 6OAdsAZ9d0T8d9algWbhP0ziSij3HoZ0XDJmwmLz3zZYNO6Sva3Qead7UXkbATm

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-0+deb13u1)

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
-- Name: db; Type: DATABASE; Schema: -; Owner: -
--

CREATE DATABASE db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


\unrestrict 6OAdsAZ9d0T8d9algWbhP0ziSij3HoZ0XDJmwmLz3zZYNO6Sva3Qead7UXkbATm
\connect db
\restrict 6OAdsAZ9d0T8d9algWbhP0ziSij3HoZ0XDJmwmLz3zZYNO6Sva3Qead7UXkbATm

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
-- PostgreSQL database dump complete
--

\unrestrict 6OAdsAZ9d0T8d9algWbhP0ziSij3HoZ0XDJmwmLz3zZYNO6Sva3Qead7UXkbATm

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

\restrict ZG16Vr4KOTHsWtUiLPP3X60DH1sg9pFaj9EriX8gOjgcx23QApNuSyDJcY4UE1N

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-0+deb13u1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: game_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.game_results (
    id integer NOT NULL,
    username character varying,
    label character varying,
    sequence_label character varying,
    is_correct boolean
);


--
-- Name: game_results_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.game_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: game_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.game_results_id_seq OWNED BY public.game_results.id;


--
-- Name: games; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.games (
    id integer NOT NULL,
    text character varying,
    type character varying,
    sequence_label character varying,
    label character varying,
    options character varying,
    answers character varying,
    images character varying,
    full_answer character varying,
    final_message character varying
);


--
-- Name: games_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.games_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.games_id_seq OWNED BY public.games.id;


--
-- Name: giveaways; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.giveaways (
    id integer NOT NULL,
    label character varying,
    username character varying,
    user_id bigint
);


--
-- Name: giveaways_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.giveaways_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: giveaways_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.giveaways_id_seq OWNED BY public.giveaways.id;


--
-- Name: promos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.promos (
    id integer NOT NULL,
    label character varying,
    description character varying,
    image character varying,
    status character varying
);


--
-- Name: promos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.promos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: promos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.promos_id_seq OWNED BY public.promos.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    user_id bigint,
    name character varying,
    phone character varying,
    points integer,
    is_admin boolean,
    username character varying,
    mail character varying,
    last_call character varying,
    last_call_giveaway character varying,
    last_call_long character varying
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: game_results id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.game_results ALTER COLUMN id SET DEFAULT nextval('public.game_results_id_seq'::regclass);


--
-- Name: games id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.games ALTER COLUMN id SET DEFAULT nextval('public.games_id_seq'::regclass);


--
-- Name: giveaways id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.giveaways ALTER COLUMN id SET DEFAULT nextval('public.giveaways_id_seq'::regclass);


--
-- Name: promos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promos ALTER COLUMN id SET DEFAULT nextval('public.promos_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: game_results; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.game_results (id, username, label, sequence_label, is_correct) FROM stdin;
\.


--
-- Data for Name: games; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.games (id, text, type, sequence_label, label, options, answers, images, full_answer, final_message) FROM stdin;
\.


--
-- Data for Name: giveaways; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.giveaways (id, label, username, user_id) FROM stdin;
1	2025-10-12T18	maks9804	449769108
2	2025-10-12T18	vprincipespravedlivo	603690207
3	2025-10-12T18	saromet	148756453
4	2025-10-12T18	maks9804	449769108
5	2025-10-12T18	saromet	148756453
\.


--
-- Data for Name: promos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.promos (id, label, description, image, status) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, user_id, name, phone, points, is_admin, username, mail, last_call, last_call_giveaway, last_call_long) FROM stdin;
2	603690207	Миша	79097671016	0	f	vprincipespravedlivo	-	\N	3439|2025-10-12T15:27:24+00:00|603690207|private	\N
3	148756453	Peter griffin	79197337483	0	t	saromet	-	\N	3440|2025-10-12T15:27:24+00:00|148756453|private	\N
1	449769108	Максим	79682664394	0	t	maks9804	-	\N	3438|2025-10-12T15:27:24+00:00|449769108|private	\N
\.


--
-- Name: game_results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.game_results_id_seq', 1, false);


--
-- Name: games_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.games_id_seq', 1, false);


--
-- Name: giveaways_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.giveaways_id_seq', 5, true);


--
-- Name: promos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.promos_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: game_results game_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.game_results
    ADD CONSTRAINT game_results_pkey PRIMARY KEY (id);


--
-- Name: games games_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (id);


--
-- Name: giveaways giveaways_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.giveaways
    ADD CONSTRAINT giveaways_pkey PRIMARY KEY (id);


--
-- Name: promos promos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promos
    ADD CONSTRAINT promos_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_game_results_label; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_game_results_label ON public.game_results USING btree (label);


--
-- Name: ix_game_results_sequence_label; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_game_results_sequence_label ON public.game_results USING btree (sequence_label);


--
-- Name: ix_games_label; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_games_label ON public.games USING btree (label);


--
-- Name: ix_giveaways_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_giveaways_user_id ON public.giveaways USING btree (user_id);


--
-- Name: ix_promos_label; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_promos_label ON public.promos USING btree (label);


--
-- Name: ix_users_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_user_id ON public.users USING btree (user_id);


--
-- PostgreSQL database dump complete
--

\unrestrict ZG16Vr4KOTHsWtUiLPP3X60DH1sg9pFaj9EriX8gOjgcx23QApNuSyDJcY4UE1N

--
-- PostgreSQL database cluster dump complete
--

