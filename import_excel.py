def normalize_name(name):
    return str(name).strip().lower()

import pandas as pd
import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)

cur = conn.cursor()

# Read Excel file
excel_file = "data/uni_data.xlsx"

df = pd.read_excel(excel_file, sheet_name="University")

for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO universities
        (uni_name, city, address, website, office_phone, student_number, topik_requirement)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        row['uni_name'],
        row['city'],
        row['address'],
        row['website'],
        row['office_phone'],
        row['student_number'],
        row['topik_requirement']
    ))

conn.commit()

print("University data imported successfully!")


language_df = pd.read_excel(
    excel_file,
    sheet_name="LanguageInstitute"
)

language_df.columns = language_df.columns.str.strip().str.lower()

for _, row in language_df.iterrows():

    cur.execute(
        "SELECT id FROM universities WHERE uni_name = %s",
        (row['uni_name'],)
    )

    university = cur.fetchone()

    if university:

        university_id = university[0]

        cur.execute("""
            INSERT INTO language_institutes
            (university_id, tuition_fee, lang_url, lang_email)
            VALUES (%s, %s, %s, %s)
        """, (
            university_id,
            row['tuition_fee'],
            row['lang_url'],
            row['lang_email']
        ))

# =========================
# University Name Mapping
# =========================

cur.execute("""
    SELECT id, uni_name
    FROM universities
""")

university_rows = cur.fetchall()

university_map = {}

for row in university_rows:

    university_id = row[0]
    university_name = normalize_name(row[1])

    university_map[university_name] = university_id

print("\nUniversity Mapping Created")
print(university_map)

# =========================
# Tuition Fees Import
# =========================

tuition_df = pd.read_excel(
    excel_file,
    sheet_name="Tuitionfees"
)

tuition_df.columns = (
    tuition_df.columns
    .str.strip()
    .str.lower()
)

print("\n===== Tuition Import Start =====")

for _, row in tuition_df.iterrows():

    excel_uni_name = normalize_name(row['uni_name'])

    if excel_uni_name in university_map:

        university_id = university_map[excel_uni_name]

        cur.execute("""
            INSERT INTO tuition_fees
            (university_id, department_name, tuition_fee)
            VALUES (%s, %s, %s)
        """, (
            university_id,
            row['department_name'],
            row['tuition_fee']
        ))

        print(f"Inserted Tuition: {row['uni_name']}")

    else:

        print(f"NOT FOUND: {row['uni_name']}")

print("===== Tuition Import Complete =====\n")


# =========================
# Scholarships Import
# =========================

scholarship_df = pd.read_excel(
    excel_file,
    sheet_name="Scholarships"
)

scholarship_df.columns = (
    scholarship_df.columns
    .str.strip()
    .str.lower()
)

print("\n===== Scholarship Import Start =====")

for _, row in scholarship_df.iterrows():

    excel_uni_name = normalize_name(row['uni_name'])

    if excel_uni_name in university_map:

        university_id = university_map[excel_uni_name]

        cur.execute("""
            INSERT INTO scholarships
            (university_id, score, percentage)
            VALUES (%s, %s, %s)
        """, (
            university_id,
            row['score'],
            row['percentage']
        ))

        print(f"Inserted Scholarship: {row['uni_name']}")

    else:

        print(f"NOT FOUND: {row['uni_name']}")

print("===== Scholarship Import Complete =====\n")

# =========================
# Majors Import
# =========================

majors_df = pd.read_excel(
    excel_file,
    sheet_name="Majors"
)

majors_df.columns = (
    majors_df.columns
    .str.strip()
    .str.lower()
)

print("\n===== Majors Import Start =====")

for _, row in majors_df.iterrows():

    excel_uni_name = normalize_name(row['uni_name'])

    if excel_uni_name in university_map:

        university_id = university_map[excel_uni_name]

        cur.execute("""
            INSERT INTO majors
            (university_id, department_name, major_name)
            VALUES (%s, %s, %s)
        """, (
            university_id,
            row['department_name'],
            row['major_name']
        ))

        print(f"Inserted Major: {row['uni_name']}")

    else:

        print(f"NOT FOUND: {row['uni_name']}")

print("===== Majors Import Complete =====\n")

conn.commit()

cur.close()
conn.close()

print("All Data Imported Successfully!")