from pathlib import Path
import sys

def count_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)

def main():
    folder = Path(__file__).parent
    csv_files = sorted(folder.glob("*.csv"))
    if not csv_files:
        print("No CSV files found.")
        return

    total = 0
    for p in csv_files:
        n = count_lines(p)
        print(f"{p.name}: {n}")
        total += n
    print(f"TOTAL: {total}")

if __name__ == "__main__":
    main()