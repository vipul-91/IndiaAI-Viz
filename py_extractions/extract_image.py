import pandas as pd
import json

def extract_image_url(featured_image):
    """Extract image URL from featured_image object"""
    if not featured_image:
        return None
    
    # First try to get full_url
    if 'full_url' in featured_image:
        return featured_image['full_url']
    
    # If not available, try to get first item from allFiles
    if 'allFiles' in featured_image and featured_image['allFiles']:
        return featured_image['allFiles'][0]
    
    return None

def main():
    # Read JSON file
    with open('people.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Read Excel file
    excel_path = 'indiaai_people_cleaned.xlsx'
    df = pd.read_excel(excel_path, sheet_name='Sheet1')
    
    # Extract image URLs from JSON
    image_urls = []
    for item in data['data']:
        featured_image = item.get('featured_image', {})
        image_urls.append(extract_image_url(featured_image))
    
    # Add image_url column to DataFrame
    df['image_url'] = image_urls
    
    # Save to new Excel file
    output_path = 'indiaai_people_cleaned_with_image.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Sheet1')
    print(f"Successfully saved to {output_path}")

if __name__ == '__main__':
    main()