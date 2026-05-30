DROP TABLE IF EXISTS users, posts, answer, questions, scholarships, tuition_fees, majors, language_institutes, universities CASCADE;

CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    uni_name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    address TEXT,
    website TEXT,
    office_phone VARCHAR(50),
    student_number INTEGER,
    topik_requirement INTEGER
);

CREATE TABLE language_institutes (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    tuition_fee INTEGER,
    lang_url TEXT,
    lang_email VARCHAR(255)
);

CREATE TABLE tuition_fees (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    department_name VARCHAR(255),
    tuition_fee VARCHAR(255)
);

CREATE TABLE majors (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    department_name VARCHAR(255),
    major_name VARCHAR(255),
    language_track VARCHAR(50)
);

CREATE TABLE scholarships (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    score INTEGER,
    percentage INTEGER
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    education_level VARCHAR(100),
    topik_score INTEGER,
    interest_field VARCHAR(255),
    budget INTEGER,
    preferred_region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions (

    id SERIAL PRIMARY KEY,

    title VARCHAR(255),

    content TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE answer (

    id SERIAL PRIMARY KEY,

    question_id INTEGER REFERENCES questions(id),

    content TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
