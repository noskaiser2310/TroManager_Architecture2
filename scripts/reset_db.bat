set PGPASSWORD=postgres
psql -U postgres -d tromanager -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -U postgres -d tromanager -f database\schema.sql
