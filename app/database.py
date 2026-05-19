from __future__ import annotations
import psycopg2, psycopg2.extras
from typing import Any, Optional

class Database:
    def __init__(self): self.conn = None

    def connect(self, host, port, dbname, user, password):
        self.conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        self.conn.autocommit = False

    def disconnect(self):
        if self.conn and not self.conn.closed: self.conn.close()

    def is_connected(self):
        return self.conn is not None and not self.conn.closed

    def _call_query(self, sql, params=()):
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params); self.conn.commit()
            return [dict(r) for r in cur.fetchall()]

    def _call_scalar(self, sql, params=()):
        with self.conn.cursor() as cur:
            cur.execute(sql, params); self.conn.commit()
            row = cur.fetchone(); return row[0] if row else None

    def _call_void(self, sql, params=()):
        with self.conn.cursor() as cur:
            cur.execute(sql, params); self.conn.commit()

    def get_all_countries(self):
        return self._call_query("SELECT * FROM sp_countries_get_all()")

    def get_country_by_id(self, rid):
        rows = self._call_query("SELECT * FROM sp_countries_get_by_id(%s)", (rid,))
        return rows[0] if rows else None

    def get_countries_for_dropdown(self):
        return self._call_query("SELECT * FROM sp_countries_get_for_dropdown()")

    def create_country(self, name, continent, population, area, independence_date, notes):
        return self._call_scalar("SELECT sp_countries_create(%s,%s,%s,%s,%s,%s) AS new_id",
                                 (name, continent, population, area, independence_date, notes))

    def update_country(self, rid, name, continent, population, area, independence_date, notes):
        self._call_void("SELECT sp_countries_update(%s,%s,%s,%s,%s,%s,%s)",
                        (rid, name, continent, population, area, independence_date, notes))

    def delete_country(self, rid):
        self._call_void("SELECT sp_countries_delete(%s)", (rid,))

    def get_all_cities(self):
        return self._call_query("SELECT * FROM sp_cities_get_all()")

    def get_city_by_id(self, rid):
        rows = self._call_query("SELECT * FROM sp_cities_get_by_id(%s)", (rid,))
        return rows[0] if rows else None

    def create_city(self, name, country_id, description, population, area, founded_date):
        return self._call_scalar("SELECT sp_cities_create(%s,%s,%s,%s,%s,%s) AS new_id",
                                 (name, country_id, description, population, area, founded_date))

    def update_city(self, rid, name, country_id, description, population, area, founded_date):
        self._call_void("SELECT sp_cities_update(%s,%s,%s,%s,%s,%s,%s)",
                        (rid, name, country_id, description, population, area, founded_date))

    def delete_city(self, rid):
        self._call_void("SELECT sp_cities_delete(%s)", (rid,))
