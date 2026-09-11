import pandas as pd
import numpy as np

def normalize_company_name(name):
    """Normalize company names for better matching"""
    if pd.isna(name):
        return ""
    return str(name).strip().lower()

def match_and_transfer_data():
    # Read both Excel files
    to_write_df = pd.read_excel('to_match.xlsx', sheet_name='Sheet 1')
    sample_complete_df = pd.read_excel('IndiaAI_Complete.xlsx', sheet_name='Sheet1')
    
    # Create normalized company name columns for matching
    print(to_write_df.columns)
    to_write_df['normalized_company'] = to_write_df['Company'].apply(normalize_company_name)
    sample_complete_df['normalized_company'] = sample_complete_df['company'].apply(normalize_company_name)
    
    # Get list of columns to transfer (all columns from to_write except 'Company')
    columns_to_transfer = [col for col in to_write_df.columns if col != 'Company' and col != 'normalized_company']
    
    # Track unmatched companies
    unmatched_companies = []
    
    # Create a copy to avoid modifying the original during iteration
    result_df = sample_complete_df.copy()
    
    # Iterate through companies in to_write
    for _, row in to_write_df.iterrows():
        company = row['Company']
        normalized_name = row['normalized_company']
        
        # Find matching rows in sample_complete
        matches = sample_complete_df[sample_complete_df['normalized_company'] == normalized_name]
        
        if len(matches) > 0:
            # For each matching row, update the columns
            for idx in matches.index:
                for col in columns_to_transfer:
                    # Only update if the value is not empty in to_write
                    if pd.notna(row[col]) and row[col] not in ['', ' ']:
                        result_df.at[idx, col] = row[col]
        else:
            unmatched_companies.append(company)
    
    # Print unmatched companies
    if unmatched_companies:
        print("Companies not found in sample_complete:")
        for company in unmatched_companies:
            print(f"- {company}")
    else:
        print("All companies matched successfully!")
    
    # Drop the temporary normalized column
    result_df = result_df.drop(columns=['normalized_company'])
    
    # Save to new Excel file
    result_df.to_excel('IndiaAI_complete_Updates.xlsx', index=False)
    print("Saved updated data to IndiaAI_complete_Updated.xlsx")

if __name__ == '__main__':
    match_and_transfer_data()