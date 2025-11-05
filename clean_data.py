"""
Clean and deduplicate scraped data
"""
import json
import pandas as pd
from pathlib import Path

def clean_exhibitors():
    """Remove duplicates and clean exhibitor data"""

    # Read the JSON data
    with open('output/equipauto_exhibitors.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Original records: {len(data)}")

    # Create a dict to store unique exhibitors by name
    unique_exhibitors = {}

    for item in data:
        name = item.get('full_text', '').strip()
        if not name:
            continue

        # If this is the first time we see this name, or if this record has more info
        if name not in unique_exhibitors:
            unique_exhibitors[name] = {
                'name': name,
                'stand': item.get('stand', ''),
                'links': item.get('links', []),
                'classes': item.get('classes', ''),
            }
        else:
            # Merge data if this record has additional info
            existing = unique_exhibitors[name]
            if not existing['stand'] and item.get('stand'):
                existing['stand'] = item['stand']
            if not existing['links'] and item.get('links'):
                existing['links'] = item['links']

    # Convert to list
    cleaned_data = list(unique_exhibitors.values())

    # Add IDs
    for idx, item in enumerate(cleaned_data, 1):
        item['id'] = idx

    # Sort by name
    cleaned_data.sort(key=lambda x: x['name'])

    print(f"Unique exhibitors: {len(cleaned_data)}")
    print(f"Removed {len(data) - len(cleaned_data)} duplicates")

    # Save cleaned JSON
    with open('output/equipauto_exhibitors_clean.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    print("Saved: output/equipauto_exhibitors_clean.json")

    # Save as CSV
    df = pd.DataFrame(cleaned_data)
    df.to_csv('output/equipauto_exhibitors_clean.csv', index=False, encoding='utf-8')
    print("Saved: output/equipauto_exhibitors_clean.csv")

    # Save as Excel
    df.to_excel('output/equipauto_exhibitors_clean.xlsx', index=False, engine='openpyxl')
    print("Saved: output/equipauto_exhibitors_clean.xlsx")

    # Print sample
    print("\nSample of cleaned data:")
    print(json.dumps(cleaned_data[:5], ensure_ascii=False, indent=2))

    # Statistics
    print(f"\nStatistics:")
    print(f"  Total unique exhibitors: {len(cleaned_data)}")
    print(f"  Exhibitors with stand info: {sum(1 for x in cleaned_data if x.get('stand'))}")
    print(f"  Exhibitors with links: {sum(1 for x in cleaned_data if x.get('links'))}")

if __name__ == '__main__':
    clean_exhibitors()
