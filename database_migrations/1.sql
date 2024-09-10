CREATE TABLE settings (
    name VARCHAR(255) NOT NULL PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO settings (name, value) VALUES ('version', '1');
INSERT INTO settings (name, value) VALUES ('admin_password', 'admin');