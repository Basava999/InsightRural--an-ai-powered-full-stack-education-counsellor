-- PostgreSQL Universal Schema for InsightRural Admission Intelligence Platform

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- For performance monitoring

-- ENUMS for Data Integrity
CREATE TYPE exam_type AS ENUM ('KCET', 'JEE_MAIN', 'JEE_ADVANCED', 'NEET_UG');
CREATE TYPE college_category AS ENUM ('IIT', 'NIT', 'IIIT', 'GFTI', 'GOVT_MEDICAL', 'PVT_MEDICAL', 'DEEMED', 'GOVT_ENGG', 'PVT_ENGG');
CREATE TYPE seat_quota AS ENUM ('AIQ', 'STATE', 'HOME_STATE', 'OTHER_STATE', 'NRI', 'MANAGEMENT');

-- EXAMS TABLE
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name exam_type NOT NULL,
    counseling_body VARCHAR(100) NOT NULL, -- e.g., KEA, JoSAA, MCC
    website_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- COLLEGES TABLE
CREATE TABLE colleges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE, -- Official code (e.g., E001 for KCET, JoSAA Institute Code)
    name VARCHAR(255) NOT NULL,
    type college_category NOT NULL,
    state VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    established_year INT,
    accreditation JSONB, -- NAAC, NBA details
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_colleges_type ON colleges(type);
CREATE INDEX idx_colleges_state ON colleges(state);

-- COURSES/BRANCHES TABLE
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE, -- e.g., CSE, MBBS, ECE
    name VARCHAR(255) NOT NULL,
    degree_type VARCHAR(50) NOT NULL, -- B.Tech, B.E., MBBS, BDS
    duration_years INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- COUNSELING ROUNDS TABLE
CREATE TABLE counseling_rounds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID REFERENCES exams(id) ON DELETE CASCADE,
    year INT NOT NULL,
    round_number INT NOT NULL,
    is_mock BOOLEAN DEFAULT FALSE,
    published_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(exam_id, year, round_number)
);

-- CUTOFFS TABLE
CREATE TABLE cutoffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID REFERENCES colleges(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    round_id UUID REFERENCES counseling_rounds(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL, -- GM, SC, ST, OBC, General-EWS
    quota seat_quota NOT NULL,
    gender VARCHAR(20) DEFAULT 'Gender-Neutral', -- Gender-Neutral, Female-only
    opening_rank INT,
    closing_rank INT NOT NULL,
    score NUMERIC(10, 2), -- For exams where score matters alongside rank (e.g., NEET)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cutoffs_college ON cutoffs(college_id);
CREATE INDEX idx_cutoffs_course ON cutoffs(course_id);
CREATE INDEX idx_cutoffs_category ON cutoffs(category);
CREATE INDEX idx_cutoffs_rank ON cutoffs(closing_rank);

-- SEAT MATRIX TABLE
CREATE TABLE seat_matrix (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID REFERENCES colleges(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    year INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    quota seat_quota NOT NULL,
    total_seats INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(college_id, course_id, year, category, quota)
);

-- FEES TABLE
CREATE TABLE fees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID REFERENCES colleges(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    year INT NOT NULL,
    tuition_fee_per_year NUMERIC(15, 2) NOT NULL,
    hostel_fee_per_year NUMERIC(15, 2),
    mess_fee_per_year NUMERIC(15, 2),
    other_fees NUMERIC(15, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(college_id, course_id, year)
);

-- PLACEMENTS TABLE
CREATE TABLE placements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID REFERENCES colleges(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id), -- Nullable if college-wide placement
    year INT NOT NULL,
    highest_package_lpa NUMERIC(10, 2),
    average_package_lpa NUMERIC(10, 2),
    median_package_lpa NUMERIC(10, 2),
    placement_percentage NUMERIC(5, 2),
    top_recruiters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- PIPELINE AUDIT LOG (To track automated scraping runs)
CREATE TABLE pipeline_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_name VARCHAR(100) NOT NULL,
    target_exam exam_type NOT NULL,
    year INT NOT NULL,
    status VARCHAR(50) NOT NULL, -- STARTED, SUCCESS, FAILED
    records_processed INT DEFAULT 0,
    error_details TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);
