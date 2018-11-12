--
--  Fichero que actualiza la base de datos
--
-------------------------------------------------------------------------------
--
--	Table to represent languages as an integer
--
CREATE TABLE public.languages (
    id_lang integer NOT NULL,
    name_lang character varying(32),
    CONSTRAINT languages_pkey PRIMARY KEY (id_lang)
);


ALTER TABLE public.languages OWNER TO alumnodb;

-------------------------------------------------------------------------------

CREATE SEQUENCE public.languages_id_lang_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.languages_id_lang_seq OWNER TO alumnodb;

ALTER SEQUENCE public.languages_id_lang_seq OWNED BY public.languages.id_lang;

ALTER TABLE ONLY public.languages ALTER COLUMN id_lang SET DEFAULT nextval('public.languages_id_lang_seq'::regclass);

-------------------------------------------------------------------------------

--
--	Table to represent countries as an integer
--
CREATE TABLE public.countries (
    id_country integer NOT NULL,
    name_country character varying(32),
    CONSTRAINT countries_pkey PRIMARY KEY (id_country)
);


ALTER TABLE public.countries OWNER TO alumnodb;

-------------------------------------------------------------------------------

CREATE SEQUENCE public.countries_id_country_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.countries_id_country_seq OWNER TO alumnodb;

ALTER SEQUENCE public.countries_id_country_seq OWNED BY public.countries.id_country;

ALTER TABLE ONLY public.countries ALTER COLUMN id_country SET DEFAULT nextval('public.countries_id_country_seq'::regclass);
-------------------------------------------------------------------------------

--
--	Table to represent Categories
--
CREATE TABLE public.categories (
    id_cat integer NOT NULL,
    name_cat character varying(32),
    CONSTRAINT categories_pkey PRIMARY KEY (id_cat)
);


ALTER TABLE public.categories OWNER TO alumnodb;

-------------------------------------------------------------------------------

CREATE SEQUENCE public.categories_id_cat_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.categories_id_cat_seq OWNER TO alumnodb;

ALTER SEQUENCE public.categories_id_cat_seq OWNED BY public.categories.id_cat;

ALTER TABLE ONLY public.categories ALTER COLUMN id_cat SET DEFAULT nextval('public.categories_id_cat_seq'::regclass);

-------------------------------------------------------------------------------

--
--	Matches each film with its categories
--
ALTER TABLE public.imdb_moviegenres 
	ALTER COLUMN genre TYPE integer,
	ALTER COLUMN genre SET NOT NULL,
	DROP CONSTRAINT imdb_moviegenres_movieid_fkey,
	ADD CONSTRAINT imdb_moviegenres_movieid_fkey FOREIGN KEY (movieid)
      REFERENCES public.imdb_movies (movieid)
      ON UPDATE CASCADE,
	ADD CONSTRAINT imdb_moviegenres_genre_fkey FOREIGN KEY (genre)
		REFERENCES public.categories(id_cat)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

--
-- Each film has it's language, etc.
--
ALTER TABLE public.imdb_movielanguages
	ALTER COLUMN language integer NOT NULL,
	DROP CONSTRAINT imdb_movielanguages_movieid_fkey,
	ADD CONSTRAINT imdb_movielanguages_movieid_fkey FOREIGN KEY (movieid)
      REFERENCES public.imdb_movies (movieid)
      ON UPDATE CASCADE,
	ADD CONSTRAINT imdb_movielanguages_language_fkey FOREIGN KEY (language)
		REFERENCES public.languages(id_lang)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

ALTER TABLE public.imdb_actors ALTER COLUMN gender TYPE character varying(1);

-------------------------------------------------------------------------------

ALTER TABLE public.imdb_moviecountries
	ALTER COLUMN country TYPE integer,
	ALTER COLUMN country SET NOT NULL,
	DROP CONSTRAINT imdb_moviecountries_movieid_fkey,
	ADD CONSTRAINT imdb_moviecountries_movieid_fkey FOREIGN KEY (movieid)
      	REFERENCES public.imdb_movies (movieid) 
    	ON UPDATE CASCADE,
	ADD CONSTRAINT imdb_moviecountries_country_fkey FOREIGN KEY (country)
		REFERENCES public.countries(id_country)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

CREATE TABLE public.status (
	id_status integer NOT NULL,
	name_status character varying(12),
	CONSTRAINT status_pkey PRIMARY KEY (id_status)
);

ALTER TABLE public.status OWNER TO alumnodb;

-------------------------------------------------------------------------------

CREATE SEQUENCE public.status_id_status_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.status_id_status_seq OWNER TO alumnodb;

ALTER SEQUENCE public.status_id_status_seq OWNED BY public.status.id_status;

ALTER TABLE ONLY public.status ALTER COLUMN id_status SET DEFAULT nextval('public.status_id_status_seq'::regclass);

-------------------------------------------------------------------------------

ALTER TABLE public.orders
	ALTER COLUMN status TYPE integer NOT NULL,
	ALTER COLUMN status SET DEFAULT 0,
	ALTER COLUMN customerid SET NOT NULL,
	ADD CONSTRAINT orders_status_fkey FOREIGN KEY (status)
		REFERENCES public.statuses (id_status)
		ON UPDATE CASCADE,	
	ADD CONSTRAINT orders_customerid_fkey FOREIGN KEY (customerid)
		REFERENCES public.customer (customerid)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

ALTER TABLE public.orderdetail
	ALTER COLUMN orderid SET NOT NULL,
	ALTER COLUMN prod_id SET NOT NULL,
	ADD CONSTRAINT orderdetail_orderid_fkey FOREIGN KEY (orderid)
		REFERENCES public.orders (orderid)
		ON UPDATE CASCADE,
	ADD CONSTRAINT orderdetail_prod_id_fkey FOREIGN KEY (prod_id)
		REFERENCES public.products (prod_id)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

ALTER TABLE public.products
	DROP CONSTRAINT products_movieid_fkey,
	ADD CONSTRAINT products_movieid_fkey FOREIGN KEY (movieid)
      REFERENCES public.imdb_movies (movieid)
      ON UPDATE CASCADE;

-------------------------------------------------------------------------------

ALTER TABLE public.inventory
	DROP CONSTRAINT inventory_pkey,
	ADD CONSTRAINT inventory_fkey FOREIGN KEY (prod_id)
		REFERENCES public.products (prod_id)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

ALTER TABLE public.imdb_movies ALTER COLUMN year TYPE integer;

-------------------------------------------------------------------------------

ALTER TABLE public.imdb_directormovies
	DROP CONSTRAINT imdb_directormovies_directorid_fkey,
	DROP CONSTRAINT imdb_directormovies_movieid_fkey,
	ADD CONSTRAINT imdb_directormovies_directorid_fkey FOREIGN KEY (directorid)
   	REFERENCES public.imdb_directors (directorid)
    ON UPDATE CASCADE,
  ADD CONSTRAINT imdb_directormovies_movieid_fkey FOREIGN KEY (movieid)
    REFERENCES public.imdb_movies (movieid)
    ON UPDATE CASCADE;

-------------------------------------------------------------------------------

ALTER TABLE public.imdb_actormovies
  ADD CONSTRAINT imdb_actormovies_movieid_fkey FOREIGN KEY (movieid)
    REFERENCES public.imdb_movies (movieid)
    ON UPDATE CASCADE;
  ADD CONSTRAINT imdb_actormovies_actorid_fkey FOREIGN KEY (actorid)
    REFERENCES public.imdb_actors (actorid)
    ON UPDATE CASCADE;