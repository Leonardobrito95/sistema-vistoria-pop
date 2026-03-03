-- Tabela para armazenar as vistorias dos POPs
CREATE TABLE IF NOT EXISTS vistoria_pop (
    submission_id SERIAL PRIMARY KEY,
    pop_name VARCHAR(255) NOT NULL,
    inspector_name VARCHAR(255) NOT NULL,
    submission_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    form_data JSONB,
    photos JSONB
);

-- Tabela para armazenar os usuários do sistema
CREATE TABLE IF NOT EXISTS vistoria_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(120) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);