import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT column_name, data_type, udt_name, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'visits_visit'
    ORDER BY ordinal_position
""")
print("=" * 80)
print("SCHEMA: visits_visit")
print("=" * 80)
print(f"{'Column':<20} {'Type':<20} {'UDT':<20} {'Nullable':<10} {'Default'}")
print("-" * 80)
for row in cursor.fetchall():
    col, dtype, udt, nullable, default = row
    print(f"{col:<20} {dtype:<20} {udt:<20} {nullable:<10} {default or ''}")

# Check foreign keys
cursor.execute("""
    SELECT
        tc.constraint_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE tc.table_name = 'visits_visit'
      AND tc.constraint_type = 'FOREIGN KEY'
""")
print("\n" + "=" * 80)
print("FOREIGN KEYS")
print("=" * 80)
for row in cursor.fetchall():
    print(f"  {row[1]} -> {row[2]}.{row[3]} (constraint: {row[0]})")

# Check indexes
cursor.execute("""
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE tablename = 'visits_visit'
""")
print("\n" + "=" * 80)
print("INDEXES")
print("=" * 80)
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")
