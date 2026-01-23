-- SmartSortierer Pro - Database Schema
-- PostgreSQL 16+
-- Version: 0.1.0

-- =============================================================================
-- ENUMS
-- =============================================================================

CREATE TYPE doc_status AS ENUM (
    'INGESTED',      -- File copied to 01_ingested, hash computed
    'ANALYZING',     -- Pipeline running (extract, chunk, embed)
    'ANALYZED',      -- Ready for review/classification
    'NEEDS_REVIEW',  -- Requires manual review
    'APPROVED',      -- User approved metadata/classification
    'COMMITTED',     -- Moved to final destination in 03_sorted
    'ERROR',         -- Processing failed
    'DUPLICATE'      -- Duplicate detected via SHA256
);

CREATE TYPE job_status AS ENUM (
    'PENDING',
    'RUNNING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);

CREATE TYPE audit_actor_type AS ENUM (
    'USER',
    'SYSTEM',
    'WORKER',
    'API'
);

CREATE TYPE audit_event_type AS ENUM (
    'DOC_INGESTED',
    'DOC_ANALYZED',
    'DOC_APPROVED',
    'DOC_REJECTED',
    'DOC_COMMITTED',
    'DOC_DUPLICATE',
    'FILE_UPLOADED',
    'FILE_MOVED',
    'FILE_RENAMED',
    'FILE_DELETED',
    'HA_ACTION_PROPOSED',
    'HA_ACTION_EXECUTED',
    'HA_ACTION_REJECTED',
    'CHAT_MESSAGE',
    'SYSTEM_ERROR'
);

-- =============================================================================
-- DOCUMENTS
-- =============================================================================

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    
    -- File identification
    file_sha256 VARCHAR(64) NOT NULL,
    original_filename VARCHAR(512) NOT NULL,
    mime_type VARCHAR(128),
    file_size_bytes BIGINT,
    
    -- Storage paths (relative to SS_STORAGE_ROOT)
    inbox_relpath VARCHAR(1024),           -- Original path in 00_inbox
    ingested_relpath VARCHAR(1024),        -- Immutable copy in 01_ingested
    staged_relpath VARCHAR(1024),          -- Temp path in 02_staging
    final_relpath VARCHAR(1024),           -- Final path in 03_sorted
    
    -- Status & workflow
    status doc_status NOT NULL DEFAULT 'INGESTED',
    duplicate_of_doc BIGINT REFERENCES documents(id),
    
    -- Extracted metadata
    extracted_text TEXT,
    page_count INTEGER,
    ocr_needed BOOLEAN DEFAULT FALSE,
    
    -- Classification (from LLM or rules)
    category VARCHAR(256),
    suggested_filename VARCHAR(512),
    suggested_target_path VARCHAR(1024),
    classification_confidence FLOAT,
    llm_trace JSONB,                       -- Minimal LLM response for audit
    
    -- User override
    user_approved_category VARCHAR(256),
    user_approved_filename VARCHAR(512),
    user_approved_target_path VARCHAR(1024),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    analyzed_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    committed_at TIMESTAMPTZ,
    
    -- Indexes
    CONSTRAINT documents_sha256_unique UNIQUE (file_sha256)
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_sha256 ON documents(file_sha256);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- =============================================================================
-- DOCUMENT REVISIONS (History)
-- =============================================================================

CREATE TABLE document_revisions (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- What changed
    action VARCHAR(64) NOT NULL,           -- e.g., 'COMMIT', 'MOVE', 'RENAME'
    old_path VARCHAR(1024),
    new_path VARCHAR(1024),
    metadata_snapshot JSONB,
    
    -- Who & when
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(256)
);

CREATE INDEX idx_document_revisions_doc_id ON document_revisions(document_id);
CREATE INDEX idx_document_revisions_created_at ON document_revisions(created_at DESC);

-- =============================================================================
-- DOCUMENT CHUNKS (for RAG)
-- =============================================================================

CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    chunk_index INTEGER NOT NULL,          -- Order in document
    chunk_text TEXT NOT NULL,
    chunk_tokens INTEGER,
    
    -- Vector embedding stored in Qdrant, this just tracks metadata
    qdrant_point_id UUID,                  -- Reference to Qdrant point
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT document_chunks_unique UNIQUE (document_id, chunk_index)
);

CREATE INDEX idx_document_chunks_doc_id ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_qdrant_id ON document_chunks(qdrant_point_id);

-- =============================================================================
-- TAGS
-- =============================================================================

CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    color VARCHAR(32),                     -- For UI
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE document_tags (
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (document_id, tag_id)
);

CREATE INDEX idx_document_tags_doc_id ON document_tags(document_id);
CREATE INDEX idx_document_tags_tag_id ON document_tags(tag_id);

-- =============================================================================
-- RULES (Classification Rules)
-- =============================================================================

CREATE TABLE rules (
    id BIGSERIAL PRIMARY KEY,
    
    name VARCHAR(256) NOT NULL,
    description TEXT,
    priority INTEGER NOT NULL DEFAULT 100, -- Lower = higher priority
    
    -- Conditions (JSON)
    conditions JSONB NOT NULL,             -- e.g., {"filename_regex": "invoice.*", "mime_type": "application/pdf"}
    
    -- Actions (JSON)
    actions JSONB NOT NULL,                -- e.g., {"category": "Invoices", "target_path": "03_sorted/Finance/Invoices"}
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rules_priority ON rules(priority ASC) WHERE is_active = TRUE;

-- =============================================================================
-- JOBS (Background Tasks Queue)
-- =============================================================================

CREATE TABLE jobs (
    id BIGSERIAL PRIMARY KEY,
    
    job_type VARCHAR(128) NOT NULL,        -- e.g., 'extract_text', 'embed_document', 'classify'
    
    status job_status NOT NULL DEFAULT 'PENDING',
    priority INTEGER NOT NULL DEFAULT 100,
    
    -- Payload
    payload JSONB NOT NULL,                -- Job-specific data
    
    -- Results
    result JSONB,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    
    -- Related entities
    document_id BIGINT REFERENCES documents(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Lock mechanism (for worker dequeue)
    locked_by VARCHAR(256),                -- Worker ID
    locked_at TIMESTAMPTZ
);

CREATE INDEX idx_jobs_status_priority ON jobs(status, priority ASC, created_at ASC);
CREATE INDEX idx_jobs_document_id ON jobs(document_id);
CREATE INDEX idx_jobs_type_status ON jobs(job_type, status);

-- =============================================================================
-- AUDIT LOG
-- =============================================================================

CREATE TABLE audit_events (
    id BIGSERIAL PRIMARY KEY,
    
    event_type audit_event_type NOT NULL,
    
    -- Actor
    actor_type audit_actor_type NOT NULL,
    actor_id VARCHAR(256),                 -- User ID, Worker ID, etc.
    
    -- Context
    resource_type VARCHAR(128),            -- 'document', 'file', 'ha_action'
    resource_id BIGINT,
    
    -- Details
    event_data JSONB,                      -- Event-specific payload
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_events_type ON audit_events(event_type);
CREATE INDEX idx_audit_events_actor ON audit_events(actor_type, actor_id);
CREATE INDEX idx_audit_events_resource ON audit_events(resource_type, resource_id);
CREATE INDEX idx_audit_events_created_at ON audit_events(created_at DESC);

-- =============================================================================
-- CHAT SESSIONS & MESSAGES (RAG Chat)
-- =============================================================================

CREATE TABLE chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    
    session_type VARCHAR(64) NOT NULL,     -- 'docs' or 'agent'
    title VARCHAR(512),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    
    role VARCHAR(32) NOT NULL,             -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    
    -- RAG metadata
    citations JSONB,                       -- Array of {doc_id, chunk_id, snippet, score}
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id, created_at ASC);

-- =============================================================================
-- HOME ASSISTANT ACTIONS (for confirmation mode)
-- =============================================================================

CREATE TABLE ha_actions (
    id BIGSERIAL PRIMARY KEY,
    
    -- Action details
    domain VARCHAR(64) NOT NULL,           -- 'light', 'switch', 'scene'
    service VARCHAR(128) NOT NULL,         -- 'turn_on', 'turn_off'
    entity_id VARCHAR(256),
    service_data JSONB,
    
    -- Status
    status VARCHAR(64) NOT NULL DEFAULT 'PROPOSED', -- 'PROPOSED', 'CONFIRMED', 'EXECUTED', 'REJECTED', 'FAILED'
    
    -- User prompt
    user_message TEXT,                     -- Original chat message
    llm_reasoning TEXT,                    -- Why the LLM suggested this
    
    -- Results
    execution_result JSONB,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    
    -- Related
    chat_session_id BIGINT REFERENCES chat_sessions(id) ON DELETE SET NULL
);

CREATE INDEX idx_ha_actions_status ON ha_actions(status);
CREATE INDEX idx_ha_actions_created_at ON ha_actions(created_at DESC);

-- =============================================================================
-- TRIGGERS (Auto-update timestamps)
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rules_updated_at BEFORE UPDATE ON rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
