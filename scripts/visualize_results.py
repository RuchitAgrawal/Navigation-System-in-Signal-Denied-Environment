#!/usr/bin/env python
# scripts/visualize_results.py -- Regenerate all plots from saved results
import argparse, sys
from pathlib import Path
sys.path.insert(0, '.')
import pandas as pd
from src.visualization.report import save_markdown_summary
def main():
    parser = argparse.ArgumentParser(description='Regenerate plots from CSV results')
    parser.add_argument('-r', '--results', default='results', help='Results root')
    args = parser.parse_args()
    csv_path = Path(args.results) / 'csv' / 'benchmark_summary.csv'
    if not csv_path.exists():
        print(f'No summary CSV at {csv_path}. Run benchmark first.')
        sys.exit(1)
    df = pd.read_csv(csv_path)
    rows = df.to_dict('records')
    save_markdown_summary(rows, Path(args.results) / 'benchmark_results.md')
    print(f'Saved Markdown summary: {args.results}/benchmark_results.md')
    print(f'Loaded {len(rows)} result rows.')

if __name__ == '__main__': main()

