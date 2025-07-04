-- drop table if table
DO
$$
BEGIN
   IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'reconciler_user') THEN
      DROP ROLE reconciler_user;
   END IF;
END
$$;

CREATE ROLE reconciler_user;

ALTER ROLE reconciler_user CREATEDB;

CREATE DATABASE reconciler OWNER reconciler_user;
