

## Example usage with cli
```console
birds new `migration_name` --dir myproject/migrations
```
Write your sql up migration in /myproject/migrations/{current_timestamp}_migration_name.up.sql
```code
create table "user"(
  id serial primary key,
  first_name text not null,
  last_name text,
  created_at timestamptz not null
);
```
Write your sql down migration in /myproject/migrations/{current_timestamp}_migration_name.down.sql
```code
drop table "user";
```
Upgrade database
```console
birds up --db_url postgres://login:password@localhost:5432/db
```
Downgrade database
```console
birds down --db_url postgres://login:password@localhost:5432/db
```

## Example usage in code
```
migrator = Migrator(
    dir="myproject/migrations",
    db_pool=self.db_pool,
)
await migrator.apply_migrations()
```

work in progress..
