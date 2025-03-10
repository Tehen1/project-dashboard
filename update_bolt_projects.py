#!/usr/bin/env python3
import pandas as pd
import shutil
import os
from datetime import datetime

def main():
    # File paths
    csv_file = 'Projects - full.csv'
    backup_file = f'Projects - full_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    # 1. Create a backup of the original CSV file
    print(f"Creating backup of {csv_file} as {backup_file}...")
    shutil.copy2(csv_file, backup_file)
    
    # 2. Read the CSV file
    print(f"Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # URL to project name mapping
    url_to_name = {
        'https://bolt.new/p/39020098': 'RhymeChain Landing Page Implementation',
        'https://bolt.new/p/38971021': 'Dating App Initial Setup',
        'https://bolt.new/p/35892284': 'Poe Clone with FastAPI Server Bot',
        'https://bolt.new/p/35708401': 'Optimized WP-CLI Interface with Modular Structure',
        'https://bolt.new/p/33551412': 'Configuration initiale du projet SaaS Chatbot',
        'https://bolt.new/p/36978758': 'Poe Clone with FastAPI Server Bot (forked)',
        'https://bolt.new/p/38551126': 'SEO and Technical Optimization Implementation',
        'https://bolt.new/p/37344196': 'Landing Page Implementation',
        'https://bolt.new/p/41504999': 'Enhanced RhymeChain UI with Modern Features',
        'https://bolt.new/p/41382612': 'Set up Expo with shadcn/ui',
        'https://bolt.new/p/41372262': 'Communication Skills Learning Platform',
        'https://bolt.new/p/41084222': 'Set up RhymeChain base application',
        'https://bolt.new/p/41072646': 'Fixie NFT Run Clone Implementation',
        'https://bolt.new/p/40879477': 'Initial Full-Stack Setup',
        'https://bolt.new/p/39883435': 'Database Schema Setup',
        'https://bolt.new/p/39874638': 'React Pong Game',
        'https://bolt.new/p/37097429': 'Build and Deployment Configuration',
        'https://bolt.new/p/36584033': 'Create Aut0-P0st Landing Page',
        'https://bolt.new/p/36547221': 'Set up PBN CMS project structure',
        'https://bolt.new/p/35460947': 'Setting up SoulSync Dating Platform',
        'https://bolt.new/p/33639274': 'WordPress Automation Scripts Setup'
    }
    
    # Category mapping based on keywords in project names
    category_keywords = {
        'Web Development': ['Landing Page', 'SEO', 'UI', 'React', 'FastAPI', 'Full-Stack', 'CMS'],
        'Mobile Development': ['Expo', 'App', 'Dating', 'SoulSync'],
        'AI/ML': ['Bot', 'Chatbot', 'Poe', 'Clone'],
        'DevOps': ['Configuration', 'Setup', 'Deployment', 'Build', 'Scripts'],
        'Blockchain': ['NFT', 'RhymeChain'],
        'Database': ['Schema', 'Database']
    }
    
    # Function to determine category based on project name
    def determine_category(project_name):
        for category, keywords in category_keywords.items():
            if any(keyword.lower() in project_name.lower() for keyword in keywords):
                return category
        return "Other"  # Default category if no keywords match
    
    # 3. Replace project names and update categories
    updated_count = 0
    for idx, row in df.iterrows():
        project_name = row['Project Name']
        
        # Check if the project name is a bolt.new URL
        if isinstance(project_name, str) and any(url in project_name for url in url_to_name.keys()):
            for url, name in url_to_name.items():
                if url in project_name:
                    # Update project name
                    df.at[idx, 'Project Name'] = name
                    
                    # Update category if it's "Other" or empty
                    if pd.isna(row['Category']) or row['Category'] == 'Other':
                        new_category = determine_category(name)
                        df.at[idx, 'Category'] = new_category
                    
                    updated_count += 1
                    break
    
    # 4. Save the updated CSV file
    print(f"Saving updated CSV file...")
    df.to_csv(csv_file, index=False)
    
    print(f"Update complete. {updated_count} project names replaced.")
    print(f"Original file backed up as {backup_file}")

if __name__ == "__main__":
    main()

