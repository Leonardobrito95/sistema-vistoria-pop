-- Tabela para rastrear pendências encontradas nas vistorias dos POPs
CREATE TABLE IF NOT EXISTS vistoria_pendencias (
    id SERIAL PRIMARY KEY,
    pop_name VARCHAR(255) NOT NULL,
    categoria VARCHAR(100) NOT NULL,  -- Ex: 'limpeza', 'ar_condicionado', 'gerador', etc.
    descricao TEXT NOT NULL,
    data_identificacao TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    data_resolucao TIMESTAMP WITHOUT TIME ZONE,
    status VARCHAR(20) DEFAULT 'pendente',  -- 'pendente', 'resolvido'
    submission_id INTEGER REFERENCES vistoria_pop(submission_id) ON DELETE CASCADE,
    observacoes TEXT,
    resolved_by VARCHAR(255)  -- Nome do usuário que resolveu
);

-- Adiciona coluna resolved_by se não existir (para bancos já criados)
ALTER TABLE vistoria_pendencias ADD COLUMN IF NOT EXISTS resolved_by VARCHAR(255);

-- Índices para melhorar performance de consultas
CREATE INDEX IF NOT EXISTS idx_pendencias_pop ON vistoria_pendencias(pop_name);
CREATE INDEX IF NOT EXISTS idx_pendencias_status ON vistoria_pendencias(status);
CREATE INDEX IF NOT EXISTS idx_pendencias_data ON vistoria_pendencias(data_identificacao);
