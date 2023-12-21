# osm-discussion-tracker

Webapp to track changeset discussions you're interested in

## Initial setup

### Backend
create a PostgreSQL user and database, then create the tables:
```
CREATE TABLE odt_changeset (
  csid bigint not null,
  uid bigint not null,
  ts timestamp with time zone not null,
  username text not null,
  last_activity_ts timestamp with time zone not null,
  last_activity_uid bigint not null,
  tags jsonb,
  UNIQUE(csid)
);
CREATE TABLE odt_changeset_comment (
  id text not null,
  csid bigint not null,
  uid bigint not null,
  ts timestamp with time zone not null,
  username text not null,
  text text not null,
  UNIQUE(id)
);
CREATE TABLE odt_changeset_note (
  username text not null,
  csid bigint not null,
  ts timestamp with time zone,
  text text not null,
  isFlag bool default false
);
CREATE TABLE odt_user (
  uid bigint not null,
  username text not null,
  prev_usernames text[],
  isAdmin bool,
  tags jsonb,
  UNIQUE(uid)
);
CREATE TABLE odt_user_auth (
  uid bigint not null,
  auth_token text not null,
  UNIQUE(auth_token)
);
CREATE TABLE odt_user_note (
  uid bigint not null,
  user_from text not null,
  ts timestamp with time zone,
  text text,
  isFlag bool default false
);
CREATE TABLE odt_watched_changesets (
  uid bigint not null,
  csid bigint not null,
  resolved_at timestamp with time zone,
  snooze_until timestamp with time zone
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
ExecStart=/home/emerson/repos/osm-discussion-tracker/.venv/bin/python3 backend/changeset_importer.py -c 20 -b 20

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