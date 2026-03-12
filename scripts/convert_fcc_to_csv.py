import pandas as pd
import os

# Read the Excel file
excel_file = '/home/jen/TranslationsDataset/data/raw/fcc/fcc_alerts.xlsx'
xls = pd.ExcelFile(excel_file)

# Create a new Excel writer for output
output_file = '/home/jen/TranslationsDataset/data/raw/fcc/fcc_alerts_converted.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    
    # Process each sheet
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        
        # Dictionary to store language: text
        data_dict = {}
        
        # Parse each row (Column A = language, Column B = text)
        for idx, row in df.iterrows():
            lang = str(row[0]).strip() if pd.notna(row[0]) else None
            text = str(row[1]).strip() if pd.notna(row[1]) else None
            
            # Only add if both language and text exist
            if lang and text and lang != 'nan':
                data_dict[lang] = text
        
        # Create new dataframe (one row of data)
        new_df = pd.DataFrame([data_dict])
        
        # Sort columns alphabetically
        new_df = new_df[sorted(new_df.columns)]

        # change to proper directory for saving CSV files
        os.chdir(os.path.dirname(excel_file))
        
        # Write to Excel sheet
        new_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Write to CSV file with headers
        csv_filename = f'{sheet_name}.csv'
        new_df.to_csv(csv_filename, index=False, header=True)
        print(f"Saved: {csv_filename}")

print("Conversion complete!")