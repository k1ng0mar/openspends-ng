// OpenSpends NG — Supabase Schema SQL
// Run this in Supabase Dashboard → SQL Editor → New Query → Run
// https://app.supabase.com/project/jbzimuwxtzdevdtzkhcb

-- Enable PostGIS (Supabase has it enabled — verify with)
-- SELECT PostGIS_Version();

-- States
CREATE TABLE states (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    capital VARCHAR(100),
    region VARCHAR(50)
);

-- LGAs
CREATE TABLE lgas (
    id SERIAL PRIMARY KEY,
    state_id INTEGER NOT NULL REFERENCES states(id),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    UNIQUE(state_id, name)
);

-- MDAs
CREATE TABLE mdas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20) UNIQUE,
    level VARCHAR(10) NOT NULL,
    state_id INTEGER REFERENCES states(id),
    lga_id INTEGER REFERENCES lgas(id),
    parent_id INTEGER REFERENCES mdas(id),
    ncoa_sector VARCHAR(10)
);
CREATE INDEX idx_mda_level ON mdas(level);
CREATE INDEX idx_mda_state ON mdas(state_id);

-- Fiscal Years
CREATE TABLE fiscal_years (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL UNIQUE,
    is_current BOOLEAN DEFAULT FALSE
);

-- NCOA
CREATE TABLE ncoa (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    description VARCHAR(300),
    category VARCHAR(100),
    chapter VARCHAR(100),
    group_name VARCHAR(100)
);

-- Budgets
CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    mda_id INTEGER NOT NULL REFERENCES mdas(id),
    year_id INTEGER NOT NULL REFERENCES fiscal_years(id),
    season VARCHAR(10) NOT NULL,
    approved DOUBLE PRECISION,
    revised DOUBLE PRECISION,
    estimated DOUBLE PRECISION,
    spent DOUBLE PRECISION,
    variance_pct DOUBLE PRECISION,
    source_url VARCHAR(500),
    updated_at TIMESTAMPTZ,
    UNIQUE(mda_id, year_id, season)
);
CREATE INDEX idx_budget_mda_year ON budgets(mda_id, year_id);

-- Spending
CREATE TABLE spending (
    id SERIAL PRIMARY KEY,
    mda_id INTEGER NOT NULL REFERENCES mdas(id),
    beneficiary VARCHAR(300),
    purpose TEXT,
    amount DOUBLE PRECISION NOT NULL,
    date DATE NOT NULL,
    reference VARCHAR(100),
    location_id VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_spending_date_mda ON spending(date, mda_id);
CREATE INDEX idx_spending_amount ON spending(amount);

-- Projects (with PostGIS)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    mda_id INTEGER REFERENCES mdas(id),
    state_id INTEGER NOT NULL REFERENCES states(id),
    lga_id INTEGER REFERENCES lgas(id),
    budget_id INTEGER REFERENCES budgets(id),
    contractor VARCHAR(300),
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'not_started',
    budget_allocated DOUBLE PRECISION,
    spent DOUBLE PRECISION DEFAULT 0,
    geolocation GEOGRAPHY(POINT, 4326),
    photos TEXT,
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_project_state_status ON projects(state_id, status);
CREATE INDEX idx_project_mda ON projects(mda_id);

-- Geolocation Cache
CREATE TABLE geolocation_cache (
    id VARCHAR(50) PRIMARY KEY,
    address VARCHAR(300),
    state VARCHAR(100),
    lga VARCHAR(100),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Contracts (OCDS)
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    ocid VARCHAR(100) UNIQUE,
    title VARCHAR(500),
    mda_id INTEGER REFERENCES mdas(id),
    amount DOUBLE PRECISION,
    status VARCHAR(50),
    award_date DATE,
    supplier VARCHAR(300),
    source_data TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_contract_ocid ON contracts(ocid);

-- Enable Row Level Security (RLS)
ALTER TABLE states ENABLE ROW LEVEL SECURITY;
ALTER TABLE lgas ENABLE ROW LEVEL SECURITY;
ALTER TABLE mdas ENABLE ROW LEVEL SECURITY;
ALTER TABLE fiscal_years ENABLE ROW LEVEL SECURITY;
ALTER TABLE ncoa ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE spending ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE geolocation_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;

-- Public read policies (all tables)
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE format('CREATE POLICY "public_read" ON %I FOR SELECT TO anon, authenticated USING (true)', t);
    END LOOP;
END;
$$;

-- ── Seed Data ──

INSERT INTO states (name, code, capital, region) VALUES
    ('Abia','AB','Umuahia','south-east'),
    ('Adamawa','AD','Yola','north-east'),
    ('Akwa Ibom','AK','Uyo','south-south'),
    ('Anambra','AN','Awka','south-east'),
    ('Bauchi','BA','Bauchi','north-east'),
    ('Bayelsa','BY','Yenagoa','south-south'),
    ('Benue','BE','Makurdi','north-central'),
    ('Borno','BO','Maiduguri','north-east'),
    ('Cross River','CR','Calabar','south-south'),
    ('Delta','DE','Asaba','south-south'),
    ('Ebonyi','EB','Abakaliki','south-east'),
    ('Edo','ED','Benin City','south-south'),
    ('Ekiti','EK','Ado-Ekiti','south-west'),
    ('Enugu','EN','Enugu','south-east'),
    ('Gombe','GO','Gombe','north-east'),
    ('Imo','IM','Owerri','south-east'),
    ('Jigawa','JI','Dutse','north-west'),
    ('Kaduna','KD','Kaduna','north-west'),
    ('Kano','KN','Kano','north-west'),
    ('Katsina','KT','Katsina','north-west'),
    ('Kebbi','KE','Birnin Kebbi','north-west'),
    ('Kogi','KO','Lokoja','north-central'),
    ('Kwara','KW','Ilorin','north-central'),
    ('Lagos','LA','Ikeja','south-west'),
    ('Nasarawa','NA','Lafia','north-central'),
    ('Niger','NI','Minna','north-central'),
    ('Ogun','OG','Abeokuta','south-west'),
    ('Ondo','ON','Akure','south-west'),
    ('Osun','OS','Oshogbo','south-west'),
    ('Oyo','OY','Ibadan','south-west'),
    ('Plateau','PL','Jos','north-central'),
    ('Rivers','RI','Port Harcourt','south-south'),
    ('Sokoto','SO','Sokoto','north-west'),
    ('Taraba','TA','Jalingo','north-east'),
    ('Zamfara','ZA','Gusau','north-west'),
    ('FCT Abuja','FC','Abuja','north-central');

INSERT INTO mdas (name, code, level, ncoa_sector) VALUES
    ('Federal Ministry of Finance','FED-FINANCE','fed','01'),
    ('Federal Ministry of Health','FED-HEALTH','fed','07'),
    ('Federal Ministry of Education','FED-EDUCATION','fed','09'),
    ('Federal Ministry of Defence','FED-DEFENCE','fed','02'),
    ('Federal Ministry of Works & Housing','FED-WORKS','fed','06'),
    ('Federal Ministry of Agriculture','FED-AGRIC','fed','04'),
    ('Federal Ministry of Transportation','FED-TRANSPORT','fed','04'),
    ('Federal Ministry of Power','FED-POWER','fed','04'),
    ('Federal Ministry of Water Resources','FED-WATER','fed','06'),
    ('Budget Office of the Federation','BOF','fed','01'),
    ('Office of the Accountant General','OAGF','fed','01'),
    ('Federal Inland Revenue Service','FIRS','fed','01');

INSERT INTO fiscal_years (year, is_current) VALUES
    (2020,false),(2021,false),(2022,false),(2023,false),(2024,true),(2025,true),(2026,true);

INSERT INTO ncoa (code, category, description) VALUES
    ('2','EXPENDITURE','Expenditure'),
    ('21','PERSONNEL COST','Personnel Cost'),
    ('2101','Salaries and Wages','Salaries and Wages'),
    ('22','OTHER RECURRENT COSTS','Overhead Cost'),
    ('23','CAPITAL EXPENDITURE','Capital Expenditure'),
    ('2301','Fixed Assets','Fixed Assets');

INSERT INTO budgets (mda_id, year_id, season, approved, spent, source_url) VALUES
    ((SELECT id FROM mdas WHERE code='FED-FINANCE'), (SELECT id FROM fiscal_years WHERE year=2024), 'budget', 4500000000000, 3200000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-FINANCE'), (SELECT id FROM fiscal_years WHERE year=2025), 'budget', 5200000000000, 4100000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-HEALTH'), (SELECT id FROM fiscal_years WHERE year=2024), 'budget', 1800000000000, 1500000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-HEALTH'), (SELECT id FROM fiscal_years WHERE year=2025), 'budget', 2100000000000, 1750000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-EDUCATION'), (SELECT id FROM fiscal_years WHERE year=2024), 'budget', 1200000000000, 980000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-EDUCATION'), (SELECT id FROM fiscal_years WHERE year=2025), 'budget', 1450000000000, 1100000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-DEFENCE'), (SELECT id FROM fiscal_years WHERE year=2024), 'budget', 950000000000, 870000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-WORKS'), (SELECT id FROM fiscal_years WHERE year=2024), 'budget', 780000000000, 620000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-WORKS'), (SELECT id FROM fiscal_years WHERE year=2025), 'budget', 1100000000000, 850000000000, 'https://budgetoffice.gov.ng'),
    ((SELECT id FROM mdas WHERE code='FED-AGRIC'), (SELECT id FROM fiscal_years WHERE year=2024), 'budget', 420000000000, 350000000000, 'https://budgetoffice.gov.ng');

-- Projects with GPS
INSERT INTO projects (title, mda_id, state_id, contractor, start_date, end_date, status, budget_allocated, spent, geolocation, source) VALUES
    ('Abuja-Kano Expressway Phase 1', (SELECT id FROM mdas WHERE code='FED-TRANSPORT'), (SELECT id FROM states WHERE code='FC'), 'Buildwell Ltd', '2024-01-15', '2026-12-31', 'in_progress', 450000000000, 180000000000, ST_SetSRID(ST_MakePoint(7.3986, 9.0765), 4326)::geography, 'tracka'),
    ('Lagos-Ibadan Expressway Rehabilitation', (SELECT id FROM mdas WHERE code='FED-WORKS'), (SELECT id FROM states WHERE code='LA'), 'Reynolds Construction', '2023-06-01', '2025-06-01', 'completed', 210000000000, 205000000000, ST_SetSRID(ST_MakePoint(3.3792, 6.5244), 4326)::geography, 'tracka'),
    ('Abuja Metro Rail Extension', (SELECT id FROM mdas WHERE code='FED-TRANSPORT'), (SELECT id FROM states WHERE code='FC'), 'CCCC Nigeria', '2024-03-01', '2027-03-01', 'in_progress', 320000000000, 85000000000, ST_SetSRID(ST_MakePoint(7.4951, 9.0579), 4326)::geography, 'tracka'),
    ('National Health Insurance Scheme Upgrade', (SELECT id FROM mdas WHERE code='FED-HEALTH'), (SELECT id FROM states WHERE code='FC'), 'HealthTech NG', '2024-07-01', '2025-12-31', 'in_progress', 85000000000, 42000000000, ST_SetSRID(ST_MakePoint(7.3986, 9.0765), 4326)::geography, 'tracka'),
    ('Universal Basic Education Digital Labs', (SELECT id FROM mdas WHERE code='FED-EDUCATION'), (SELECT id FROM states WHERE code='FC'), 'EduTech Africa', '2024-09-01', '2026-06-30', 'in_progress', 120000000000, 35000000000, ST_SetSRID(ST_MakePoint(7.3986, 9.0765), 4326)::geography, 'tracka'),
    ('Kano Water Supply Rehabilitation', (SELECT id FROM mdas WHERE code='FED-WATER'), (SELECT id FROM states WHERE code='KN'), 'Water Works Ltd', '2023-01-01', '2025-12-31', 'in_progress', 65000000000, 48000000000, ST_SetSRID(ST_MakePoint(8.5925, 12.0022), 4326)::geography, 'tracka'),
    ('Mambilla Hydroelectric Dam', (SELECT id FROM mdas WHERE code='FED-POWER'), (SELECT id FROM states WHERE code='TA'), 'Sinohydro', '2020-01-01', '2028-12-31', 'in_progress', 3600000000000, 1200000000000, ST_SetSRID(ST_MakePoint(11.2833, 6.7833), 4326)::geography, 'tracka');
