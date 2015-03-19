CREATE TABLE `city` (
        `country`       TEXT collate nocase,
        `postal_code`   TEXT collate nocase,
        `city`          TEXT collate nocase,
        `state1`        TEXT collate nocase,
        `state2`        TEXT collate nocase,
        `province1`     TEXT,
        `province2`     TEXT,
        `community1`    TEXT,
        `community2`    TEXT,
        `latitude`      REAL,
        `longitude`     REAL,
        `coord_accuracy`        INTEGER
);
CREATE INDEX idx_country on city (country collate nocase);
CREATE INDEX idx_postal_code on city (postal_code collate nocase);
CREATE INDEX idx_city on city (city collate nocase);
CREATE INDEX idx_state1 on city (state1 collate nocase);
CREATE INDEX idx_state2 on city (state2 collate nocase);

CREATE TABLE `country` (
        `abbreviation`  TEXT collate nocase,
        `name`  TEXT collate nocase
);
CREATE INDEX idx_abbreviation on country (abbreviation collate nocase);
CREATE INDEX idx_name on country (name collate nocase);

CREATE TABLE `street_suffix` (
        `suffix_name`  TEXT collate nocase
);
CREATE INDEX idx_suffix_name on street_suffix (suffix_name collate nocase);

CREATE TABLE `landmark` (
        `resource`      TEXT collate nocase,
        `address`       TEXT,
        `city`          TEXT,
        `county`        TEXT,
        `state`         TEXT,
        `country`       TEXT
);
CREATE INDEX idx_resource on landmark (resource collate nocase);
