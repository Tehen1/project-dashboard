#!/usr/bin/env python3
"""
analyze_uncategorized.py - Analyzes uncategorized projects in 'Projects - full.csv'
"""

import pandas as pd

def main():
    # Read the CSV file
    df = pd.read_csv('Projects - full.csv')
    
    # Find uncategorized projects (NaN in Category column)
    uncategorized = df[pd.isna(df['Category'])]
    
    # Print the number of uncategorized projects
    print('Number of uncategorized projects:', len(uncategorized))
    
    # Print tech stacks for uncategorized projects
    print('\nTech stacks for uncategorized projects:')
    for idx, row in uncategorized.iterrows():
        tech_stack = row.get('Tech Stack', 'N/A')
        if pd.isna(tech_stack):
            tech_stack = 'N/A'
        print(f"- {row['Project Name']}: {tech_stack}")
    
    # Optional: Summarize most common tech stacks in uncategorized projects
    if 'Tech Stack' in df.columns and len(uncategorized) > 0:
        print("\nMost common tech stacks in uncategorized projects:")
        tech_counts = uncategorized['Tech Stack'].value_counts().head(5)
        for tech, count in tech_counts.items():
            if pd.notna(tech):
                print(f"- {tech}: {count}")

if __name__ == "__main__":
    main()

