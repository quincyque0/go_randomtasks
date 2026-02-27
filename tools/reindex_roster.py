import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / 'students' / 'roster.csv'

def main():
    with ROSTER.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Group students by group
    groups = {}
    for row in rows:
        grp = row['group']
        if grp not in groups:
            groups[grp] = []
        groups[grp].append(row)

    # Re-assign IDs
    new_rows = []
    # We want to keep the order of groups somewhat consistent or sorted
    for grp in sorted(groups.keys()):
        students = groups[grp]
        # Sort students by name to have deterministic IDs
        students.sort(key=lambda x: x['name'])
        
        for i, student in enumerate(students, 1):
            new_id = f"s{str(i).zfill(2)}"
            new_rows.append({
                'id': new_id,
                'name': student['name'],
                'group': grp
            })

    # Write back
    with ROSTER.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'group'])
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Re-indexed {len(new_rows)} students across {len(groups)} groups.")

if __name__ == "__main__":
    main()
