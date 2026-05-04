CREATE TABLE IF NOT EXISTS countries (
    id                SERIAL          PRIMARY KEY,
    name              VARCHAR(200)    NOT NULL,
    continent         VARCHAR(100)    NOT NULL,
    population        INTEGER,
    area              DECIMAL(14, 2),
    independence_date DATE,
    notes             TEXT,
    is_deleted        BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cities (
    id           SERIAL        PRIMARY KEY,
    name         VARCHAR(200)  NOT NULL,
    country_id   INTEGER       NOT NULL REFERENCES countries(id),
    description  TEXT,
    population   INTEGER,
    area         DECIMAL(12, 2),
    founded_date DATE,
    is_deleted   BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS countries_history (
    history_id        SERIAL      PRIMARY KEY,
    operation         VARCHAR(10) NOT NULL,
    changed_at        TIMESTAMP   NOT NULL DEFAULT NOW(),
    record_id         INTEGER     NOT NULL,
    name              VARCHAR(200),
    continent         VARCHAR(100),
    population        INTEGER,
    area              DECIMAL(14, 2),
    independence_date DATE,
    notes             TEXT,
    is_deleted        BOOLEAN
);

CREATE TABLE IF NOT EXISTS cities_history (
    history_id   SERIAL      PRIMARY KEY,
    operation    VARCHAR(10) NOT NULL,
    changed_at   TIMESTAMP   NOT NULL DEFAULT NOW(),
    record_id    INTEGER     NOT NULL,
    name         VARCHAR(200),
    country_id   INTEGER,
    description  TEXT,
    population   INTEGER,
    area         DECIMAL(12, 2),
    founded_date DATE,
    is_deleted   BOOLEAN
);

CREATE OR REPLACE FUNCTION trg_countries_history()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    r  countries%ROWTYPE;
    op VARCHAR(10);
BEGIN
    IF TG_OP = 'DELETE' THEN
        r := OLD; op := 'DELETE';
    ELSE
        r := NEW;
        op := CASE TG_OP WHEN 'INSERT' THEN 'INSERT' ELSE 'UPDATE' END;
    END IF;
    INSERT INTO countries_history(operation, record_id, name, continent, population, area, independence_date, notes, is_deleted)
    VALUES (op, r.id, r.name, r.continent, r.population, r.area, r.independence_date, r.notes, r.is_deleted);
    IF TG_OP = 'DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
END;
$$;

DROP TRIGGER IF EXISTS countries_audit ON countries;
CREATE TRIGGER countries_audit
AFTER INSERT OR UPDATE OR DELETE ON countries
FOR EACH ROW EXECUTE FUNCTION trg_countries_history();

CREATE OR REPLACE FUNCTION trg_cities_history()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    r  cities%ROWTYPE;
    op VARCHAR(10);
BEGIN
    IF TG_OP = 'DELETE' THEN
        r := OLD; op := 'DELETE';
    ELSE
        r := NEW;
        op := CASE TG_OP WHEN 'INSERT' THEN 'INSERT' ELSE 'UPDATE' END;
    END IF;
    INSERT INTO cities_history(operation, record_id, name, country_id, description, population, area, founded_date, is_deleted)
    VALUES (op, r.id, r.name, r.country_id, r.description, r.population, r.area, r.founded_date, r.is_deleted);
    IF TG_OP = 'DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
END;
$$;

DROP TRIGGER IF EXISTS cities_audit ON cities;
CREATE TRIGGER cities_audit
AFTER INSERT OR UPDATE OR DELETE ON cities
FOR EACH ROW EXECUTE FUNCTION trg_cities_history();

CREATE OR REPLACE FUNCTION sp_countries_get_all()
RETURNS TABLE(id INTEGER, name VARCHAR(200), continent VARCHAR(100), population INTEGER, area DECIMAL(14,2), independence_date DATE, notes TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.continent, c.population, c.area, c.independence_date, c.notes
    FROM countries c
    WHERE c.is_deleted = FALSE
    ORDER BY c.name;
END;
$$;

CREATE OR REPLACE FUNCTION sp_countries_get_by_id(p_id INTEGER)
RETURNS TABLE(id INTEGER, name VARCHAR(200), continent VARCHAR(100), population INTEGER, area DECIMAL(14,2), independence_date DATE, notes TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.continent, c.population, c.area, c.independence_date, c.notes
    FROM countries c
    WHERE c.id = p_id AND c.is_deleted = FALSE;
END;
$$;

CREATE OR REPLACE FUNCTION sp_countries_get_for_dropdown()
RETURNS TABLE(id INTEGER, name VARCHAR(200))
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name
    FROM countries c
    WHERE c.is_deleted = FALSE
    ORDER BY c.name;
END;
$$;

CREATE OR REPLACE FUNCTION sp_countries_create(p_name VARCHAR(200), p_continent VARCHAR(100), p_population INTEGER, p_area DECIMAL(14,2), p_independence_date DATE, p_notes TEXT)
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE v_id INTEGER;
BEGIN
    INSERT INTO countries(name, continent, population, area, independence_date, notes)
    VALUES (p_name, p_continent, p_population, p_area, p_independence_date, p_notes)
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$;

CREATE OR REPLACE FUNCTION sp_countries_update(p_id INTEGER, p_name VARCHAR(200), p_continent VARCHAR(100), p_population INTEGER, p_area DECIMAL(14,2), p_independence_date DATE, p_notes TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE countries
    SET name = p_name, continent = p_continent, population = p_population,
        area = p_area, independence_date = p_independence_date, notes = p_notes, updated_at = NOW()
    WHERE id = p_id AND is_deleted = FALSE;
END;
$$;

CREATE OR REPLACE FUNCTION sp_countries_delete(p_id INTEGER)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE countries SET is_deleted = TRUE, updated_at = NOW() WHERE id = p_id;
END;
$$;

CREATE OR REPLACE FUNCTION sp_cities_get_all()
RETURNS TABLE(id INTEGER, name VARCHAR(200), country_id INTEGER, country_name VARCHAR(200), description TEXT, population INTEGER, area DECIMAL(12,2), founded_date DATE)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.country_id, cn.name::VARCHAR(200), c.description, c.population, c.area, c.founded_date
    FROM cities c
    JOIN countries cn ON c.country_id = cn.id
    WHERE c.is_deleted = FALSE
    ORDER BY c.name;
END;
$$;

CREATE OR REPLACE FUNCTION sp_cities_get_by_id(p_id INTEGER)
RETURNS TABLE(id INTEGER, name VARCHAR(200), country_id INTEGER, country_name VARCHAR(200), description TEXT, population INTEGER, area DECIMAL(12,2), founded_date DATE)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.country_id, cn.name::VARCHAR(200), c.description, c.population, c.area, c.founded_date
    FROM cities c
    JOIN countries cn ON c.country_id = cn.id
    WHERE c.id = p_id AND c.is_deleted = FALSE;
END;
$$;

CREATE OR REPLACE FUNCTION sp_cities_create(p_name VARCHAR(200), p_country_id INTEGER, p_description TEXT, p_population INTEGER, p_area DECIMAL(12,2), p_founded_date DATE)
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE v_id INTEGER;
BEGIN
    INSERT INTO cities(name, country_id, description, population, area, founded_date)
    VALUES (p_name, p_country_id, p_description, p_population, p_area, p_founded_date)
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$;

CREATE OR REPLACE FUNCTION sp_cities_update(p_id INTEGER, p_name VARCHAR(200), p_country_id INTEGER, p_description TEXT, p_population INTEGER, p_area DECIMAL(12,2), p_founded_date DATE)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE cities
    SET name = p_name, country_id = p_country_id, description = p_description,
        population = p_population, area = p_area, founded_date = p_founded_date, updated_at = NOW()
    WHERE id = p_id AND is_deleted = FALSE;
END;
$$;

CREATE OR REPLACE FUNCTION sp_cities_delete(p_id INTEGER)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE cities SET is_deleted = TRUE, updated_at = NOW() WHERE id = p_id;
END;
$$;