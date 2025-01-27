--
--  Fichero que actualiza la base de datos
--
-------------------------------------------------------------------------------
--
--  Table to represent alerts
--
CREATE TABLE public.alertas (
    prod_id integer NOT NULL,
    notice character varying(64),
    stamp timestamp
);

ALTER TABLE public.alertas OWNER TO alumnodb;

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

-- We insert the languages
INSERT INTO public.languages (name_lang)
SELECT DISTINCT public.imdb_movielanguages.language
FROM public.imdb_movielanguages;

-- We update every language
UPDATE public.imdb_movielanguages
SET language=public.languages.id_lang
FROM public.languages
WHERE public.imdb_movielanguages.language=public.languages.name_lang;

-- Now we update the data type
ALTER TABLE public.imdb_movielanguages 
  ALTER COLUMN language TYPE integer USING (language::integer),
  ALTER COLUMN language SET NOT NULL;

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

-- We insert the countries
INSERT INTO public.countries (name_country)
SELECT DISTINCT public.imdb_moviecountries.country
FROM public.imdb_moviecountries;

INSERT INTO public.countries (name_country)
SELECT DISTINCT (TRIM(LEADING FROM public.customers.country))
FROM public.customers;

-- We update all the countries in the database
UPDATE public.imdb_moviecountries
SET country=public.countries.id_country
FROM public.countries
WHERE public.imdb_moviecountries.country=public.countries.name_country;

ALTER TABLE imdb_moviecountries
  ALTER COLUMN country TYPE integer USING (country::integer),
  ALTER COLUMN country SET NOT NULL;

UPDATE public.customers
SET country=public.countries.id_country
FROM public.countries
WHERE (TRIM(LEADING FROM public.customers.country))=public.countries.name_country;

ALTER TABLE public.customers
  ALTER COLUMN country TYPE integer USING (country::integer),
  ALTER COLUMN country SET NOT NULL;

-------------------------------------------------------------------------------

--
--	Table to represent Genres
--
CREATE TABLE public.genres (
    id_genre integer NOT NULL,
    name_genre character varying(32),
    CONSTRAINT genres_pkey PRIMARY KEY (id_genre)
);


ALTER TABLE public.genres OWNER TO alumnodb;

-------------------------------------------------------------------------------

CREATE SEQUENCE public.genres_id_genre_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.genres_id_genre_seq OWNER TO alumnodb;

ALTER SEQUENCE public.genres_id_genre_seq OWNED BY public.genres.id_genre;

ALTER TABLE ONLY public.genres ALTER COLUMN id_genre SET DEFAULT nextval('public.genres_id_genre_seq'::regclass);

-- We insert the genres
INSERT INTO public.genres (name_genre)
SELECT DISTINCT public.imdb_moviegenres.genre
FROM public.imdb_moviegenres;

-- We update every language
UPDATE public.imdb_moviegenres
SET genre=public.genres.id_genre
FROM public.genres
WHERE public.imdb_moviegenres.genre=public.genres.name_genre;

-- Now we update the data type
ALTER TABLE public.imdb_moviegenres
  ALTER COLUMN genre TYPE integer USING (genre::integer),
  ALTER COLUMN genre SET NOT NULL;

-------------------------------------------------------------------------------

--
--	Matches each film with its genres
--
ALTER TABLE public.imdb_moviegenres 
	DROP CONSTRAINT imdb_moviegenres_movieid_fkey,
	ADD CONSTRAINT imdb_moviegenres_movieid_fkey FOREIGN KEY (movieid)
      REFERENCES public.imdb_movies (movieid)
      ON UPDATE CASCADE,
	ADD CONSTRAINT imdb_moviegenres_genre_fkey FOREIGN KEY (genre)
		REFERENCES public.genres(id_genre)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

--
-- Each film has it's language, etc.
--
ALTER TABLE public.imdb_movielanguages
	DROP CONSTRAINT imdb_movielanguages_movieid_fkey,
	ADD CONSTRAINT imdb_movielanguages_movieid_fkey FOREIGN KEY (movieid)
      REFERENCES public.imdb_movies (movieid)
      ON UPDATE CASCADE,
	ADD CONSTRAINT imdb_movielanguages_language_fkey FOREIGN KEY (language)
		REFERENCES public.languages(id_lang)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

ALTER TABLE public.imdb_moviecountries
	DROP CONSTRAINT imdb_moviecountries_movieid_fkey,
	ADD CONSTRAINT imdb_moviecountries_movieid_fkey FOREIGN KEY (movieid)
      	REFERENCES public.imdb_movies (movieid) 
    	ON UPDATE CASCADE,
	ADD CONSTRAINT imdb_moviecountries_country_fkey FOREIGN KEY (country)
		REFERENCES public.countries(id_country)
		ON UPDATE CASCADE;

-------------------------------------------------------------------------------

ALTER TABLE public.orders
	ALTER COLUMN customerid SET NOT NULL,
	ADD CONSTRAINT orders_customerid_fkey FOREIGN KEY (customerid)
		REFERENCES public.customers (customerid)
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
    ON UPDATE CASCADE,
  ADD CONSTRAINT imdb_actormovies_actorid_fkey FOREIGN KEY (actorid)
    REFERENCES public.imdb_actors (actorid)
    ON UPDATE CASCADE;
    
-------------------------------------------------------------------------------
    
ALTER TABLE public.imdb_movies ALTER COLUMN year TYPE integer USING (SPLIT_PART(year, '-', 1)::integer);

-------------------------------------------------------------------------------

ALTER TABLE public.alertas
  ADD CONSTRAINT alertas_prod_id_fkey FOREIGN KEY (prod_id)
    REFERENCES public.products (prod_id)
    ON UPDATE CASCADE;
    
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION setOrderAmount ()
    RETURNS void
AS $$
BEGIN
    WITH total AS (
        SELECT orders.orderid AS id, SUM(products.price) AS suma
        FROM orders INNER JOIN orderdetail ON orders.orderid = orderdetail.orderid
            INNER JOIN products ON products.prod_id = orderdetail.prod_id
        GROUP BY orders.orderid)
    UPDATE
        orders
    SET
        netamount = total.suma,
        totalamount = total.suma + tax
    FROM
        total
    WHERE
        orders.orderid = total.id AND
        orders.netamount IS NULL;
END;
$$ LANGUAGE plpgsql;

SELECT setOrderAmount();

-------------------------------------------------------------------------------
