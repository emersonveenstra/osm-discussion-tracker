# osm-discussion-tracker

Webapp to track changeset discussions you're interested in

## Initial setup

### Backend
create a PostgreSQL user and database, then create the tables:
```
CREATE TABLE odt_changeset (
  csid bigint not null,
  uid bigint not null,
  ts timestamp without time zone not null,
  username text not null,
  comment text not null
);
CREATE TABLE odt_comment (
  csid bigint not null,
  uid bigint not null,
  ts timestamp without time zone not null,
  username text not null,
  comment text not null
);
CREATE TABLE odt_state (
  last_state bigint default 0,
  update_in_progress boolean default false
);
insert into odt_state (last_state) values (0);
```


Add the following as env variables:
```
export DB_HOST='127.0.0.1'
export DB_PORT=5432
export DB_USER='odt'
export DB_PASS='odt'
export DB_NAME='odt'
```

