import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from coursekit.variant import load_variant, student_id, student_group

def main():
    if len(sys.argv) < 2:
        print("Использование: python tools/show_my_variant.py <НОМЕР_НЕДЕЛИ>")
        sys.exit(1)

    week = sys.argv[1].zfill(2)
    try:
        v = load_variant(week)
        print(f"\n=== Вариант для {student_group()} / {student_id()} (Неделя {week}) ===")
        print(json.dumps(v, indent=2, ensure_ascii=False))
        print("=================================================================\n")
    except FileNotFoundError:
        print(f"Вариант для недели {week} не найден для {student_group()}/{student_id()}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
