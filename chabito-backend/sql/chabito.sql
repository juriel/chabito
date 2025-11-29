-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Chat contact table
CREATE TABLE chat_contact (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation table
CREATE TABLE chat_conversation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_contact UUID NOT NULL,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'closed', 'pending')),
    context_data TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Message table
CREATE TABLE chat_message (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_conversation UUID NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('human', 'ai', 'system', 'function', 'tool')),
    content TEXT NOT NULL,
    mime_type VARCHAR(100),
    filename VARCHAR(255),
    additional_kwargs TEXT,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Basic indexes
CREATE INDEX idx_conversation_contact ON chat_conversation(chat_contact);
CREATE INDEX idx_message_conversation ON chat_message(chat_conversation);