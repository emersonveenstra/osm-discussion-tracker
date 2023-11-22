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
  comment text not null,
  UNIQUE(csid)
);
CREATE TABLE odt_comment (
  comment_id text not null,
  csid bigint not null,
  uid bigint not null,
  ts timestamp without time zone not null,
  username text not null,
  comment text not null,
  UNIQUE(comment_id)
);
CREATE TABLE odt_user (
  uid bigint not null,
  username text not null,
  isActive bool not null,
  UNIQUE(uid)
);
CREATE TABLE odt_resolved (
  uid bigint not null,
  csid bigint not null,
  resolved_at timestamp without time zone not null,
  expires_at timestamp without time zone
);
CREATE TABLE odt_state (
  min_state bigint default 0,
  max_state bigint default 0,
  update_in_progress boolean default false
);
insert into odt_state (min_state, max_state) values (0,0);
```


Add the following as env variables:
```
export DB_HOST='127.0.0.1'
export DB_PORT=5432
export DB_USER='odt'
export DB_PASS='odt'
export DB_NAME='odt'
``` 

systemd service and timer for changeset importer:
```
[Unit]
Description=changeset importer
Wants=network.target
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/home/emerson/repos/osm-discussion-tracker
ExecStart=/home/emerson/repos/osm-discussion-tracker/.venv/bin/python3 backend/changeset-importer.py -c 20 -b 20

[Install]
WantedBy=multi-user.target
```
```
[Unit]
Description=changeset importer timer

[Timer]
OnCalendar=minutely
Persistent=true

[Install]
WantedBy=timers.target
```