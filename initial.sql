CREATE TABLE IF NOT EXISTS files
(
    id         serial PRIMARY KEY,
    name       varchar   not null unique,
    pitch      integer   not null default 100,
    created_at timestamp not null default now()
);

CREATE TABLE IF NOT EXISTS chunks
(
    id         serial PRIMARY KEY,
    name       varchar   not null unique,
    file       integer REFERENCES files ON DELETE CASCADE,
    created_at timestamp not null default now()
);

CREATE TABLE IF NOT EXISTS jobs
(
    id         serial PRIMARY KEY,
    file       integer REFERENCES files ON DELETE CASCADE,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    status     integer   not null default 0
);
