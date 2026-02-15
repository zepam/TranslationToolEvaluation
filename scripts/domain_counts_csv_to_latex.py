# convert the data profile domain counts CSV to a LaTeX table
import pandas as pd
import re

def csv_to_latex_table(csv_file, output_file=None):
    df = pd.read_csv(csv_file)
    # Replace underscores with spaces and capitalize every word
    df = df.apply(lambda col: col.str.replace('_', ' ').str.title() if col.dtype == 'object' else col)
    
    # Capitalize column headers and add gray background
    df.columns = df.columns.str.replace('_', ' ').str.title()
    latex_table = df.to_latex(index=False, escape=False)
    
    # Left align first column, right align others
    col_format = '|l|r|'

    latex_table = re.sub(r'\\begin{tabular}\{[^}]+\}', f'\\\\begin{{tabular}}{{{col_format}}}', latex_table)

    latex_table = '\\begin{table}\n\\label{tab:domain_counts}\n' + latex_table + '\n\\end{table}'
    
    # Add gray background to header row
    latex_table = latex_table.replace('\\caption{Domain Counts}', '')
    latex_table = latex_table.replace('\\end{tabular}', '\\end{tabular}\n\\caption{Domain Counts}\n\\label{tab:domain_counts}')
    latex_table = latex_table.replace('\\toprule', '\\toprule\n\\rowcolor{lightgray}')
    
   
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