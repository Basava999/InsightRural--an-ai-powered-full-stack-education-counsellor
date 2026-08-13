-- KCET Counselling Platform — Production PostgreSQL Schema
-- Single source of truth for structured data. ChromaDB is semantic search only.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ── ENUMS ────────────────────────────────────────────────────────────────────
CREATE TYPE exam_type AS ENUM ('KCET', 'JEE_MAIN', 'JEE_ADVANCED', 'NEET_UG');
CREATE TYPE college_type_enum AS ENUM (
    'Government', 'Government_Aided', 'Private_Autonomous',
    'Type1_Unaided', 'Type2_Unaided', 'Deemed_Private'
);
CREATE TYPE gender_type AS ENUM ('Male', 'Female', 'Other', 'Any');
CREATE TYPE user_role AS ENUM ('student', 'counsellor', 'admin');

-- ── DISTRICTS ────────────────────────────────────────────────────────────────
CREATE TABLE districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    is_hk_371j BOOLEAN DEFAULT FALSE,
    is_rural_eligible BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ── STUDENTS ─────────────────────────────────────────────────────────────────
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    kcet_rank INT,
    category VARCHAR(20) DEFAULT 'GM',
    gender gender_type DEFAULT 'Any',
    preferred_branch VARCHAR(50),
    preferred_city VARCHAR(100),
    preferred_district VARCHAR(100),
    hostel_required BOOLEAN DEFAULT FALSE,
    budget_annual INT,
    is_rural BOOLEAN DEFAULT FALSE,
    kannada_medium BOOLEAN DEFAULT FALSE,
    snq BOOLEAN DEFAULT FALSE,
    hk_371j BOOLEAN DEFAULT FALSE,
    minority BOOLEAN DEFAULT FALSE,
    college_type_pref college_type_enum,
    role user_role DEFAULT 'student',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_rank ON students(kcet_rank);

-- ── QUOTAS ───────────────────────────────────────────────────────────────────
CREATE TABLE quotas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    percent NUMERIC(5,2) NOT NULL,
    description TEXT,
    is_special BOOLEAN DEFAULT FALSE
);

-- ── COLLEGES ─────────────────────────────────────────────────────────────────
CREATE TABLE colleges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type college_type_enum NOT NULL,
    city VARCHAR(100),
    district VARCHAR(100),
    district_id UUID REFERENCES districts(id),
    state VARCHAR(100) DEFAULT 'Karnataka',
    affiliation VARCHAR(100),
    established_year INT,
    naac_grade VARCHAR(10),
    nba_accredited BOOLEAN DEFAULT FALSE,
    hostel_available BOOLEAN DEFAULT FALSE,
    website VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    total_seats INT,
    placement_avg_lpa NUMERIC(8,2),
    placement_highest_lpa NUMERIC(8,2),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_colleges_code ON colleges(code);
CREATE INDEX idx_colleges_city ON colleges(city);
CREATE INDEX idx_colleges_district ON colleges(district);
CREATE INDEX idx_colleges_type ON colleges(type);
CREATE INDEX idx_colleges_name_trgm ON colleges USING gin(name gin_trgm_ops);

-- ── BRANCHES ─────────────────────────────────────────────────────────────────
CREATE TABLE branches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    degree_type VARCHAR(50) DEFAULT 'B.E.',
    duration_years INT DEFAULT 4
);

CREATE TABLE college_branches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    seats INT DEFAULT 0,
    UNIQUE(college_id, branch_id)
);

-- ── CUTOFFS (multi-year) ─────────────────────────────────────────────────────
CREATE TABLE cutoffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    year INT NOT NULL,
    round_number INT DEFAULT 1,
    category VARCHAR(20) NOT NULL,
    quota_code VARCHAR(20) DEFAULT 'GM',
    closing_rank INT NOT NULL,
    opening_rank INT,
    source_url VARCHAR(500),
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(college_id, branch_id, year, round_number, category, quota_code)
);

CREATE INDEX idx_cutoffs_college ON cutoffs(college_id);
CREATE INDEX idx_cutoffs_branch ON cutoffs(branch_id);
CREATE INDEX idx_cutoffs_year ON cutoffs(year);
CREATE INDEX idx_cutoffs_category ON cutoffs(category);
CREATE INDEX idx_cutoffs_rank ON cutoffs(closing_rank);

-- ── FEES ─────────────────────────────────────────────────────────────────────
CREATE TABLE fees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id),
    year INT NOT NULL,
    fee_category VARCHAR(50),
    gm_fee NUMERIC(12,2),
    obc_fee NUMERIC(12,2),
    sc_st_fee NUMERIC(12,2) DEFAULT 0,
    hostel_fee NUMERIC(12,2),
    mess_fee NUMERIC(12,2),
    other_fees NUMERIC(12,2),
    UNIQUE(college_id, branch_id, year)
);

-- ── HOSTELS ──────────────────────────────────────────────────────────────────
CREATE TABLE hostels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
    name VARCHAR(255),
    type VARCHAR(50),
    boys_available BOOLEAN DEFAULT FALSE,
    girls_available BOOLEAN DEFAULT FALSE,
    capacity_boys INT,
    capacity_girls INT,
    annual_fee NUMERIC(12,2),
    mess_fee NUMERIC(12,2),
    amenities JSONB DEFAULT '[]',
    rules JSONB DEFAULT '[]',
    eligibility JSONB DEFAULT '{}',
    contact VARCHAR(255),
    source_url VARCHAR(500),
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hostels_college ON hostels(college_id);

-- ── PLACEMENTS ───────────────────────────────────────────────────────────────
CREATE TABLE placements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id),
    year INT NOT NULL,
    highest_package_lpa NUMERIC(10,2),
    average_package_lpa NUMERIC(10,2),
    median_package_lpa NUMERIC(10,2),
    placement_percentage NUMERIC(5,2),
    top_recruiters JSONB DEFAULT '[]',
    source_url VARCHAR(500)
);

-- ── SCHOLARSHIPS ─────────────────────────────────────────────────────────────
CREATE TABLE scholarships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(255),
    amount NUMERIC(12,2),
    amount_type VARCHAR(50),
    eligibility JSONB NOT NULL DEFAULT '{}',
    deadline DATE,
    application_url VARCHAR(500),
    documents_required JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    source_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ── RECOMMENDATION AUDIT ─────────────────────────────────────────────────────
CREATE TABLE recommendation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    request_payload JSONB NOT NULL,
    response_payload JSONB NOT NULL,
    engine_version VARCHAR(20) DEFAULT '1.0.0',
    confidence_score NUMERIC(5,2),
    data_completeness NUMERIC(5,2),
    processing_ms INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ── API AUDIT ────────────────────────────────────────────────────────────────
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES students(id),
    action VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255),
    ip_address INET,
    request_hash VARCHAR(64),
    status_code INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ── ML MODEL REGISTRY ────────────────────────────────────────────────────────
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    metrics JSONB DEFAULT '{}',
    artifact_path VARCHAR(500),
    is_active BOOLEAN DEFAULT FALSE,
    trained_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ── SEED QUOTAS (KEA official percentages) ─────────────────────────────────
INSERT INTO quotas (code, name, percent, is_special) VALUES
    ('GM', 'General Merit', 32.00, FALSE),
    ('SC', 'Scheduled Caste', 15.00, FALSE),
    ('ST', 'Scheduled Tribe', 3.00, FALSE),
    ('CAT1', 'Category-1', 4.00, FALSE),
    ('2A', 'Category-2A', 15.00, FALSE),
    ('2B', 'Category-2B', 4.00, FALSE),
    ('3A', 'Category-3A', 4.00, FALSE),
    ('3B', 'Category-3B', 5.00, FALSE),
    ('RURAL', 'Rural Quota', 15.00, TRUE),
    ('KM', 'Kannada Medium', 5.00, TRUE),
    ('371J', 'Hyderabad-Karnataka 371(J)', 8.00, TRUE),
    ('SNQ', 'Supernumerary Quota', 0.00, TRUE)
ON CONFLICT (code) DO NOTHING;
