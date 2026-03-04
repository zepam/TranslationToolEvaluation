"""
Convert a CSV file to a formatted LaTeX table.

This function reads a CSV file, applies text transformations (replacing underscores
with spaces and capitalizing appropriately), and generates a formatted LaTeX table
with bolded headers, custom column alignment, and caption/label.

Args:
    csv_file (str): Path to the input CSV file.
    output_file (str, optional): Path to write the LaTeX table output. If None,
        the table is printed to stdout. Defaults to None.
Returns:
    None: Outputs the LaTeX table either to a file or prints it.
Notes:
    - Column headers and data cells have underscores replaced with spaces
    - Headers are formatted with title case (with lowercase exceptions for 'and', 'in')
    - First column is left-aligned, all other columns are right-aligned
    - Column headers are bolded in the output
    - Table is wrapped with LaTeX table environment and centered
    - Includes caption: "Count of translation per each event type"
    - Includes label: "tab:domain_counts_portland"
"""


# convert the data profile domain counts CSV to a LaTeX table
import pandas as pd
import re

def domain_counts(csv_file, output_file=None):
    df = pd.read_csv(csv_file)
    # Replace underscores with spaces and capitalize every word
    df = df.apply(lambda col: col.str.replace('_', ' ').str.title().str.replace('And', 'and').str.replace('In', 'in') if col.dtype == 'object' else col)
    
    df.columns = df.columns.str.replace('_', ' ').str.title()
    latex_table = df.to_latex(index=False, escape=False)
    
    # Bold the column headers
    lines = latex_table.split('\n')
    for i, line in enumerate(lines):
        if ' & ' in line and '\\' in line:
            # This is the header row
            headers = [h.strip() for h in line.split('&')]
            bold_headers = []
            for j, h in enumerate(headers):
                # h = h.rstrip().rstrip('\\').strip()
                h = h.strip()
                # Remove \\ from last header if present
                if j == len(headers) - 1 and h.endswith('\\'):
                    bold_headers.append(f'\\textbf{{{h}}} \\\\')
                else:
                    bold_headers.append(f'\\textbf{{{h}}}')
            lines[i] = ' & '.join(bold_headers)
            break
    latex_table = '\n'.join(lines)
    
    
    # Left align first column, right align all others. 
    col_format = 'l' + 'r' * (len(df.columns) - 1)

    latex_table = re.sub(r'\\begin{tabular}\{[^}]+\}', f'\\\\begin{{tabular}}{{{col_format}}}', latex_table)

    latex_table = '\\begin{table}\n\\centering\n' + latex_table + '\n\\end{table}'
    
    # Add gray background to header row
    latex_table = latex_table.replace('\\caption{Domain Counts}', '')
    latex_table = latex_table.replace('\\end{tabular}', '\\end{tabular}\n\\caption{Count of translation per each event type}\n\\label{tab:domain_counts_portland}')
    
   
    if output_file:
        with open(output_file, 'w') as f:
            f.write(latex_table)
        print(f"Wrote LaTeX table to {output_file}")
    else:
        print(latex_table)

def make_beautiful_files():
    input_csv = "data/processed/portland/stats/domain_counts.csv"
    output_tex = "data/processed/portland/tables/domain_counts_table.tex"
    domain_counts(input_csv, output_tex)

def main():
    make_beautiful_files()
    

if __name__ == "__main__":
    main()