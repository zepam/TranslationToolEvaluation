"""
Script to convert portland_data_profile.json to a LaTeX formatted table.
Creates a table with alert types as rows and languages as columns.
"""

import json
from pathlib import Path


def json_to_latex_table(json_input, output_dir=None):
    """
    Convert JSON profile data to LaTeX table format.
    
    Args:
        json_input: Path to a JSON file, folder of JSON files, or list of JSON files
        output_dir: Directory to save LaTeX tables (optional, prints to console if None)
    """
    # Handle folder vs file input
    json_files_list = []
    if isinstance(json_input, str):
        input_path = Path(json_input)
        if input_path.is_dir():
            json_files_list = sorted(input_path.glob("*_profile.json"))
        elif input_path.is_file():
            json_files_list = [input_path]
    elif isinstance(json_input, list):
        json_files_list = [Path(f) for f in json_input]
    
    if not json_files_list:
        raise ValueError("No JSON files found")
    
    # Process each JSON file
    for json_file in json_files_list:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        alert_types = sorted(data['alert_types'])
        languages = sorted(data['languages'])
        # replace all _ with a space and capitalize each word
        languages = [lang.replace('_', ' ').title() for lang in languages]
        translations = data['translations_per_alert_type_per_language']
        
        # Start LaTeX table
        latex_lines = []
        latex_lines.append('\\begin{table}[H]')
        latex_lines.append('\\centering')
        latex_lines.append('\\small')
        
        # Column specification
        num_cols = len(languages) + 1  # +1 for alert type column
        col_spec = '|l|' + 'c|' * len(languages)
        latex_lines.append(f'\\begin{{tabular}}{{{col_spec}}}')
        latex_lines.append('\\hline')
        
        # Header row
        header = ['Alert Type'] + languages
        header_row = ' & '.join(header) + ' \\\\'
        latex_lines.append(header_row)
        latex_lines.append('\\hline')
        
        # Data rows
        for alert_type in alert_types:
            row_data = [alert_type.replace('_', ' ')]  # replace underscores
            row_data = [cell.title() for cell in row_data]  # capitalize each word
            for language in languages:
                count = translations.get(alert_type, {}).get(language, '')
                row_data.append(str(count) if count else '-')
            row = ' & '.join(row_data) + ' \\\\'
            latex_lines.append(row)
        
        latex_lines.append('\\hline')
        latex_lines.append('\\end{tabular}')
        latex_lines.append('\\caption{Translations per Alert Type per Language}')
        
        # Create unique label based on filename
        label = json_file.stem.replace('_profile', '')
        latex_lines.append(f'\\label{{tab:{label}_translations}}')
        latex_lines.append('\\end{table}')
        
        latex_table = '\n'.join(latex_lines)
        
        # Output
        if output_dir:
            output_path = Path(output_dir) / f"{json_file.stem}_table.tex"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_table)
            print(f"LaTeX table saved to {output_path}")
        else:
            print(f"\n--- {json_file.name} ---")
            print(latex_table)


def main():
    input_folder = "data/processed/portland"
    output_dir = "data/processed/portland/tables"
    json_to_latex_table(input_folder, output_dir)


if __name__ == "__main__":
    main()
