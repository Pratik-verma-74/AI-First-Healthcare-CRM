-- ============================================================================
-- AI-First CRM HCP Module - Complete Supabase PostgreSQL Database Schema
-- Designed for Healthcare CRM (Medical Representatives & HCP Interactions)
-- ============================================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they already exist (in reverse order of foreign key dependencies)
DROP TABLE IF EXISTS chat_history CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS follow_up CASCADE;
DROP TABLE IF EXISTS interaction CASCADE;
DROP TABLE IF EXISTS hcp CASCADE;

-- ============================================================================
-- 1. HCP (Healthcare Professionals) Table
-- ============================================================================
CREATE TABLE hcp (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(150) NOT NULL,
    hospital VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    phone VARCHAR(50),
    city VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hcp_name ON hcp(name);
CREATE INDEX idx_hcp_hospital ON hcp(hospital);
CREATE INDEX idx_hcp_specialty ON hcp(specialty);

-- ============================================================================
-- 2. Interaction (Core Interaction Logs) Table
-- ============================================================================
CREATE TABLE interaction (
    id SERIAL PRIMARY KEY,
    hcp_id INTEGER NOT NULL REFERENCES hcp(id) ON DELETE CASCADE,
    interaction_type VARCHAR(100) DEFAULT 'Meeting',
    interaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    interaction_time VARCHAR(20) DEFAULT '12:00',
    attendees TEXT,
    topics_discussed TEXT,
    materials_shared TEXT,
    samples_distributed TEXT,
    observed_sentiment VARCHAR(50) DEFAULT 'Neutral' CHECK (observed_sentiment IN ('Positive', 'Neutral', 'Negative')),
    outcomes TEXT,
    ai_summary TEXT,
    status VARCHAR(50) DEFAULT 'Draft' CHECK (status IN ('Draft', 'Confirmed', 'Saved')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interaction_hcp_id ON interaction(hcp_id);
CREATE INDEX idx_interaction_date ON interaction(interaction_date);
CREATE INDEX idx_interaction_status ON interaction(status);

-- ============================================================================
-- 3. FollowUp (Scheduled Follow-up Tasks & Reminders) Table
-- ============================================================================
CREATE TABLE follow_up (
    id SERIAL PRIMARY KEY,
    interaction_id INTEGER NOT NULL REFERENCES interaction(id) ON DELETE CASCADE,
    hcp_id INTEGER NOT NULL REFERENCES hcp(id) ON DELETE CASCADE,
    action_description TEXT NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Completed', 'Cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_follow_up_interaction_id ON follow_up(interaction_id);
CREATE INDEX idx_follow_up_hcp_id ON follow_up(hcp_id);
CREATE INDEX idx_follow_up_due_date ON follow_up(due_date);

-- ============================================================================
-- 4. AuditLog (Full Traceability of AI and Manual Actions) Table
-- ============================================================================
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    changes TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);

-- ============================================================================
-- 5. ChatHistory (Conversation Transcripts) Table
-- ============================================================================
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    sender VARCHAR(50) NOT NULL CHECK (sender IN ('user', 'ai', 'system')),
    message TEXT NOT NULL,
    tool_called VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);

-- ============================================================================
-- Sample Seed Data (Indian Healthcare Ecosystem for Realist Testing)
-- ============================================================================

-- Seed HCPs
INSERT INTO hcp (name, specialty, hospital, contact_email, phone, city) VALUES
('Dr. Rakesh Sharma', 'Cardiology', 'Apollo Hospital, New Delhi', 'rakesh.sharma@apollo.com', '+91-9811098110', 'New Delhi'),
('Dr. Anjali Gupta', 'Oncology', 'AIIMS, New Delhi', 'anjali.gupta@aiims.edu', '+91-9876543210', 'New Delhi'),
('Dr. Vikram Mehta', 'Endocrinology', 'Fortis Healthcare, Mumbai', 'v.mehta@fortis.com', '+91-9822334455', 'Mumbai'),
('Dr. Sunita Rao', 'Pediatrics', 'Manipal Hospital, Bangalore', 's.rao@manipal.com', '+91-9844556677', 'Bangalore'),
('Dr. Rajesh Khanna', 'Neurology', 'Medanta The Medicity, Gurgaon', 'r.khanna@medanta.org', '+91-9911223344', 'Gurgaon');

-- Seed Past Interactions
INSERT INTO interaction (hcp_id, interaction_type, interaction_date, interaction_time, attendees, topics_discussed, materials_shared, samples_distributed, observed_sentiment, outcomes, ai_summary, status) VALUES
(1, 'Meeting', '2025-04-10', '11:30', 'Dr. Rakesh Sharma, Amit Kumar (MR)', 'Discussed clinical efficacy of CardioPlus in hypertensive patients with Type 2 diabetes. Highlighted 24-hour blood pressure control.', 'CardioPlus Clinical Trial Monograph, Dosage Flowchart Brochure', '{"product": "CardioPlus 50mg", "quantity": 15}', 'Positive', 'Doctor appreciated the once-daily dosing and agreed to prescribe CardioPlus to 5 new patients this week.', 'Medical Representative met Dr. Rakesh Sharma at Apollo Hospital to discuss CardioPlus clinical trials. Shared monograph brochure and 15 trial samples. Doctor showed strong interest and agreed to initiate prescriptions.', 'Saved'),
(2, 'Advisory Board', '2025-04-12', '14:00', 'Dr. Anjali Gupta, Dr. Neha Verma, Medical Affairs Team', 'OncoBoost Phase III survival data presentation and discussion on immune-related adverse event management.', 'OncoBoost Phase III Clinical Deck, Management Guidelines Booklet', '{"product": "OncoBoost Starter Kit", "quantity": 5}', 'Positive', 'Dr. Gupta consented to participate as a keynote speaker at the upcoming National Oncology Summit.', 'Conducted Advisory Board session with Dr. Anjali Gupta at AIIMS regarding OncoBoost Phase III survival data. Shared complete clinical deck and 5 starter kits. Dr. Gupta accepted invitation to speak at National Summit.', 'Saved'),
(3, 'Meeting', '2025-04-15', '16:00', 'Dr. Vikram Mehta, Priya Singh (MR)', 'Reviewed GlucoFix ER efficacy compared to standard metformin therapy.', 'GlucoFix ER Patient Care Guide', '{"product": "GlucoFix ER 1000mg", "quantity": 10}', 'Neutral', 'Doctor requested additional post-marketing surveillance data on gastrointestinal tolerability before switching ongoing patients.', 'Discussed GlucoFix ER with Dr. Vikram Mehta at Fortis Healthcare. Shared patient guides and 10 samples. Doctor expressed neutral sentiment, requesting further GI tolerability data before expanding usage.', 'Saved');

-- Seed FollowUps
INSERT INTO follow_up (interaction_id, hcp_id, action_description, due_date, status) VALUES
(1, 1, 'Deliver updated CardioPlus patient support brochures and check initial prescription feedback.', '2025-04-24', 'Pending'),
(2, 2, 'Send official speaker invitation packet and travel itinerary for National Oncology Summit.', '2025-04-25', 'Pending'),
(3, 3, 'Provide medical affairs GI tolerability study report for GlucoFix ER.', '2025-04-22', 'Pending');

-- Seed Audit Logs
INSERT INTO audit_log (entity_type, entity_id, action, changes) VALUES
('Interaction', 1, 'AI_SAVE', '{"status": "Saved", "ai_summary": "Generated automatically via Log Interaction tool"}'),
('Interaction', 2, 'AI_SAVE', '{"status": "Saved", "ai_summary": "Generated automatically via Log Interaction tool"}'),
('Interaction', 3, 'AI_SAVE', '{"status": "Saved", "ai_summary": "Generated automatically via Log Interaction tool"}');

-- Seed Chat History
INSERT INTO chat_history (session_id, sender, message, tool_called) VALUES
('demo-session-101', 'user', 'I met Dr Rakesh Sharma at Apollo Hospital today morning. Discussed CardioPlus clinical trials and shared the clinical monograph brochure. Gave 15 samples of CardioPlus 50mg. Doctor was very interested. Schedule follow up in two weeks.', NULL),
('demo-session-101', 'ai', 'I have extracted the interaction details for Dr. Rakesh Sharma at Apollo Hospital. I filled out the structured form with CardioPlus clinical discussions, brochure shared, 15 samples distributed, and positive sentiment. Would you like me to save this interaction and schedule the follow-up for April 24, 2025?', 'log_interaction');
