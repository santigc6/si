--
--  Fichero que actualiza la base de datos
--

--
--	Table to represent languages as an integer
--
CREATE TABLE public.languages (
    id_lang integer NOT NULL,
    name_lang character varying(32),
    CONSTRAINT languages_pkey PRIMARY KEY (id_lang)
);


ALTER TABLE public.languages OWNER TO alumnodb;

--
--	Table to represent countries as an integer
--
CREATE TABLE public.countries (
    id_country integer NOT NULL,
    name_country character varying(32),
    CONSTRAINT countries_pkey PRIMARY KEY (id_country)
);


ALTER TABLE public.countries OWNER TO alumnodb;

--
--	Table to represent Categories
--
CREATE TABLE public.categories (
    id_cat integer NOT NULL,
    name_cat character varying(32),
    CONSTRAINT categories_pkey PRIMARY KEY (id_cat)
);


ALTER TABLE public.categories OWNER TO alumnodb;


--
--	Matches each film with its categories
--
ALTER TABLE public.imdb_moviegenres 
	ALTER COLUMN genre TYPE integer,
	ALTER COLUMN genre SET NOT NULL,
	ADD CONSTRAINT imdb_moviegenres_genre_fkey FOREIGN KEY (genre)
		REFERENCES public.categories(id_cat);

DROP TABLE public.imdb_movielanguages;

--
-- Each film has it's language
--
ALTER TABLE public.imdb_movies
	ADD COLUMN language integer NOT NULL,
	ADD COLUMN extrainformation text,
	ADD CONSTRAINT imdb_movies_fkey FOREIGN KEY (language)
		REFERENCES public.languages(id_lang);
