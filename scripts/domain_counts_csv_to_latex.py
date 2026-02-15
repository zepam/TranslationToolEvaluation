# conver the data profile domain counts CSV to a LaTeX table
import pandas as pd

def csv_to_latex_table(csv_file, output_file=None):
    df = pd.read_csv(csv_file)
    # Replace underscores with spaces and capitalize every word
    df = df.apply(lambda col: col.str.replace('_', ' ').str.title() if col.dtype == 'object' else col)
    latex_table = df.to_latex(index=False, caption="Domain Counts", label="tab:domain_counts", escape=False)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(latex_table)
        print(f"Wrote LaTeX table to {output_file}")
    else:
        print(latex_table)

def main():
    input_csv = "data/processed/portland/domain_counts.csv"
    output_tex = "data/processed/portland/domain_counts_table.tex"
    csv_to_latex_table(input_csv, output_tex)

if __name__ == "__main__":
    main()