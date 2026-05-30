def normalize_name(name):
    return str(name).strip().lower()

import pandas as pd
import psycopg2

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="kstudy",
    user="postgres",
    password="kangtaehyun52!"
)

cur = conn.cursor()

# Read Excel file
excel_file = "data/uni_data.xlsx"

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