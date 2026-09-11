import pandas as pd
import json
import re
from unidecode import unidecode

def normalize_string(s):
    """Normalize strings for case-insensitive and symbol-insensitive comparison"""
    if not isinstance(s, str):
        return ""
    # Convert to lowercase, remove special characters, and transliterate unicode
    s = unidecode(s).lower()
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def get_first_word(s):
    """Extract the first word from a string after normalization"""
    if not isinstance(s, str):
        return ""
    # Split on common separators and take first part
    s = re.split(r'[\s.\-()]+', s)[0]
    return normalize_string(s)

def extract_image_url(featured_image):
    """Extract image URL from featured_image object"""
    if not featured_image or not isinstance(featured_image, dict):
        return None
    
    # First try to get full_url
    if 'full_url' in featured_image:
        return featured_image['full_url']
    
    # If not available, try to get first item from allFiles
    if 'allFiles' in featured_image and isinstance(featured_image['allFiles'], list) and featured_image['allFiles']:
        return featured_image['allFiles'][0]
    
    return None

def extract_categories(items):
    """Extract category names from list of dictionaries or strings"""
    if not items or not isinstance(items, list):
        return ""
    
    names = []
    for item in items:
        if isinstance(item, dict) and 'name' in item:
            names.append(item['name'])
        elif isinstance(item, str):
            names.append(item)
    return ", ".join(names)

def get_country_name(country_data):
    """Extract country name from different possible structures"""
    if isinstance(country_data, dict):
        return country_data.get('name', '')
    elif isinstance(country_data, str):
        return country_data
    return ""

def fix_url(url):
    """Ensure URLs have proper https:// prefix"""
    if pd.isna(url) or not url or url.strip() == "":
        return url
    url = url.strip()
    if not url.startswith('http'):
        # Check if it starts with www
        if url.startswith('www.'):
            return 'https://' + url
        else:
            return 'https://www.' + url
    return url

def main():
    # Read JSON file
    with open('all_companies.json', 'r', encoding='utf-8') as f:
        data = json.load(f)['data']
    
    # Read Excel file
    excel_path = 'indiaai_people_cleaned_with_image.xlsx'
    df = pd.read_excel(excel_path, sheet_name='Sheet1')
    
    # Create new columns in DataFrame
    new_columns = [
        "company_head_category",
        "company_country",
        "company_image_url",
        "company_categories",
        "company_tags",
        "company_feature",
        "short_excerpt",
        "location",
        "state",
        "highlights",
        "website",
        "company_linkedIn",
        "company_twitter"
    ]
    
    for col in new_columns:
        df[col] = ""
    
    # Add matching status column
    df['matching'] = 0  # 0 = unmatched, 1 = matched in first round, 2 = matched in second round
    
    # Prepare unmatched entries list
    unmatched = []
    
    # Create normalized company name mapping for Excel (first round)
    excel_companies = {}
    for idx, row in df.iterrows():
        company = row['company']
        if pd.notna(company):
            normalized = normalize_string(company)
            if normalized:
                if normalized not in excel_companies:
                    excel_companies[normalized] = []
                excel_companies[normalized].append(idx)
    
    # Process JSON data - FIRST ROUND
    for company_data in data:
        title = company_data.get('title', '')
        if not title:
            continue
            
        # Normalize company name for matching
        normalized_title = normalize_string(title)
        
        # Find matching rows in Excel
        row_indices = excel_companies.get(normalized_title, [])
        
        # Extract values from JSON
        values = {
            "company_head_category": company_data.get('head_category', ''),
            "company_country": get_country_name(company_data.get('country', '')),
            "company_image_url": extract_image_url(company_data.get('featured_image', {})),
            "company_categories": extract_categories(company_data.get('categories', [])),
            "company_tags": extract_categories(company_data.get('tags', [])),
            "company_feature": extract_categories(company_data.get('featured_tags', [])),
            "short_excerpt": company_data.get('excerpt', ''),
            "location": company_data.get('location', ''),
            "state": company_data.get('state', ''),
            "highlights": company_data.get('highlights', company_data.get('content', '')),
            "website": company_data.get('website', ''),
            "company_linkedIn": company_data.get('linkedIn', ''),
            "company_twitter": company_data.get('twitter', '')
        }
        
        # Add to DataFrame if matched
        if row_indices:
            for row_idx in row_indices:
                for col, value in values.items():
                    df.at[row_idx, col] = value
                df.at[row_idx, 'matching'] = 1  # Mark as matched in first round
        else:
            # Add to unmatched list for possible second round
            unmatched.append({"title": title, **values})
    
    # SECOND ROUND: Match by first word for unmatched entries
    # Create mapping of first words for unmatched Excel rows
    unmatched_excel_first_words = {}
    for idx, row in df.iterrows():
        if row['matching'] == 0:  # Only consider unmatched rows
            company = row['company']
            if pd.notna(company):
                first_word = get_first_word(company)
                if first_word:
                    if first_word not in unmatched_excel_first_words:
                        unmatched_excel_first_words[first_word] = []
                    unmatched_excel_first_words[first_word].append(idx)
    
    # Process unmatched JSON entries
    second_round_unmatched = []
    for entry in unmatched:
        title = entry['title']
        first_word = get_first_word(title)
        
        # Find matching Excel rows by first word
        matching_indices = unmatched_excel_first_words.get(first_word, [])
        
        if matching_indices:
            for row_idx in matching_indices:
                # Update the row with extracted values
                for col in new_columns:
                    df.at[row_idx, col] = entry[col]
                df.at[row_idx, 'matching'] = 2  # Mark as matched in second round
        else:
            # Keep unmatched if no match found
            second_round_unmatched.append(entry)
    
    # Merge feature and category columns
    feature_cols = ['feature-1', 'feature-2', 'category-1', 'category-2', 'category-3']
    
    # Create a new column by combining non-empty values
    df['people-feature-category'] = df[feature_cols].apply(
        lambda row: ', '.join([str(val) for val in row if pd.notna(val) and str(val).strip() != '']), 
        axis=1
    )
    
    # Drop the original feature and category columns
    df.drop(columns=feature_cols, inplace=True)
    
    # Fix URLs in all link columns
    url_columns = ['linkedIn', 'twitter', 'company_linkedIn', 'company_twitter', 'website']
    for col in url_columns:
        if col in df.columns:
            df[col] = df[col].apply(fix_url)
    
    # Reorder columns as specified
    column_order = [
        'No.', 'people', 'designation', 'company', 'category', 
        'company_head_category', 'country', 'company_country', 
        'state', 'location', 'people-feature-category', 
        'company_categories', 'company_tags', 'company_feature',
        'linkedIn', 'twitter', 'website', 'company_linkedIn', 
        'company_twitter', 'matching', 'short_excerpt', 
        'highlights', 'excerpt', 'image_url', 'company_image_url'
    ]
    
    # Add any missing columns (to prevent errors)
    for col in column_order:
        if col not in df.columns:
            df[col] = ""
    
    # Reorder columns
    df = df[column_order]
    
    # Save updated Excel
    output_path = 'TRY_IndiaAI.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Sheet1')
    
    # Save unmatched entries
    if second_round_unmatched:
        unmatched_df = pd.DataFrame(second_round_unmatched)
        unmatched_df.to_excel('unmatched_companies.xlsx', index=False)
        print(f"Saved {len(second_round_unmatched)} unmatched companies to unmatched_companies.xlsx")
    
    print(f"Successfully updated Excel file saved to {output_path}")
    print("Matching Summary:")
    print(f"- First round matches: {len(df[df['matching'] == 1])}")
    print(f"- Second round matches: {len(df[df['matching'] == 2])}")
    print(f"- Total unmatched: {len(second_round_unmatched)}")

if __name__ == '__main__':
    main()