#!/usr/bin/env python3
"""
consolidate_projects.py

This script reads all CSV files in the current directory, extracts project information,
transforms the data to match the structure of "Projects - full.csv", and consolidates
all unique projects into the main file while avoiding duplicates.
"""

import os
import csv
import re
import pandas as pd
from datetime import datetime
import unicodedata
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def normalize_text(text):
    """Normalize text by removing special characters and lowercasing."""
    if not isinstance(text, str):
        return ""
    # Remove accents
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    # Convert to lowercase
    text = text.lower()
    # Remove special characters except spaces, alphanumeric and basic punctuation
    text = re.sub(r'[^\w\s\-\.]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_project_name(text):
    """Extract the project name from a text field."""
    if not isinstance(text, str):
        return ""
    # Remove line numbers that might be in the data
    text = re.sub(r'^\d+\|', '', text)
    # Extract the project name (assuming it's the first part before any delimiter)
    name = text.split(' - ')[0] if ' - ' in text else text
    return name.strip()

def get_category_from_name(name):
    """Infer category from project name keywords."""
    name_lower = name.lower()
    
    categories = {
        'AI/ML': ['ai', 'ml', 'intelligence', 'chatbot', 'gpt', 'llm'],
        'Web Application': ['web', 'app', 'dashboard', 'landing', 'page', 'portal'],
        'Infrastructure': ['infrastructure', 'boilerplate', 'template', 'framework', 'component'],
        'SEO': ['seo', 'keyword', 'analytics', 'backlink'],
        'SaaS': ['saas', 'subscription', 'service'],
        'DevOps': ['devops', 'deploy', 'automation', 'ci/cd'],
        'Web3/Blockchain': ['web3', 'blockchain', 'nft', 'token', 'crypto'],
        'Tools': ['tool', 'generator', 'creator'],
        'Analytics': ['analytics', 'report', 'metrics', 'insight']
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    
    return "Other"

def get_main_file_columns():
    """Get the column structure from the main projects file."""
    try:
        with open('Projects - full.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            # Remove line number column if it exists
            if header and header[0].isdigit() or header[0].startswith('Colonne'):
                header = header[1:]
            return header
    except FileNotFoundError:
        # Return default columns if file doesn't exist
        return ["Project Name", "Category", "Status", "Priority", "Location", 
                "Next Actions", "Dependencies", "Tech Stack", "Documentation Status", 
                "Last Updated", "Résumé_Détaillé"]

def parse_lovable_csv(file_path, columns):
    """Parse lovable.csv and transform data to match the main file structure."""
    projects = []
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8', dtype=str)
        for _, row in df.iterrows():
            # Skip header or incomplete rows
            if not isinstance(row.iloc[2], str) or row.iloc[2] == 'flex-shrink':
                continue
                
            project_name = row.iloc[2].replace('-', ' ').title()
            last_updated = row.iloc[4] if len(row) > 4 and isinstance(row.iloc[4], str) else "Unknown"
            
            # Extract date from strings like "about 18 hours ago"
            current_date = datetime.now().strftime('%Y-%m')
            
            project = {
                "Project Name": project_name,
                "Category": get_category_from_name(project_name),
                "Status": "Active",
                "Priority": "Medium",
                "Location": "",
                "Next Actions": "",
                "Dependencies": "",
                "Tech Stack": "",
                "Documentation Status": "In Progress",
                "Last Updated": current_date,
                "Résumé_Détaillé": f"Project imported from Lovable. Last activity: {last_updated}"
            }
            
            # Map to main file structure
            project_dict = {col: project.get(col, "") for col in columns}
            projects.append(project_dict)
            
    except Exception as e:
        logging.error(f"Error parsing {file_path}: {e}")
    
    return projects

def parse_websim_csv(file_path, columns):
    """Parse websim.csv and transform data to match the main file structure."""
    projects = []
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8', dtype=str)
        for _, row in df.iterrows():
            # Skip header rows or empty rows
            if not isinstance(row.iloc[3], str) or row.iloc[3] == 'text-md':
                continue
                
            project_name = row.iloc[3]
            last_updated = row.iloc[5] if len(row) > 5 and isinstance(row.iloc[5], str) else "Unknown"
            
            # Extract date from strings like "17 hours ago"
            current_date = datetime.now().strftime('%Y-%m')
            
            project = {
                "Project Name": project_name,
                "Category": get_category_from_name(project_name),
                "Status": "Active",
                "Priority": "Medium",
                "Location": "",
                "Next Actions": "",
                "Dependencies": "",
                "Tech Stack": "",
                "Documentation Status": "In Progress",
                "Last Updated": current_date,
                "Résumé_Détaillé": f"Project imported from WebSim. Last activity: {last_updated}"
            }
            
            # Process additional projects in the same row
            if len(row) > 8 and isinstance(row.iloc[8], str) and row.iloc[8] and row.iloc[8] != 'text-md 2':
                additional_project_name = row.iloc[8]
                additional_last_updated = row.iloc[10] if len(row) > 10 else "Unknown"
                
                additional_project = {
                    "Project Name": additional_project_name,
                    "Category": get_category_from_name(additional_project_name),
                    "Status": "Active",
                    "Priority": "Medium",
                    "Location": "",
                    "Next Actions": "",
                    "Dependencies": "",
                    "Tech Stack": "",
                    "Documentation Status": "In Progress",
                    "Last Updated": current_date,
                    "Résumé_Détaillé": f"Project imported from WebSim. Last activity: {additional_last_updated}"
                }
                
                additional_project_dict = {col: additional_project.get(col, "") for col in columns}
                projects.append(additional_project_dict)
            
            # Map to main file structure
            project_dict = {col: project.get(col, "") for col in columns}
            projects.append(project_dict)
            
    except Exception as e:
        logging.error(f"Error parsing {file_path}: {e}")
    
    return projects

def parse_generic_csv(file_path, columns):
    """Parse any other CSV file and attempt to extract project information."""
    projects = []
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8', dtype=str)
        # Try to identify column with project names
        potential_name_columns = [
            col for col in df.columns 
            if any(keyword in col.lower() for keyword in ['name', 'title', 'project', 'nom'])
        ]
        
        name_column = potential_name_columns[0] if potential_name_columns else df.columns[min(1, len(df.columns)-1)]
        
        for _, row in df.iterrows():
            if not isinstance(row[name_column], str) or row[name_column] == name_column:
                continue
                
            project_name = extract_project_name(row[name_column])
            
            # Skip if no meaningful project name was extracted
            if not project_name or project_name.strip() == '':
                continue
                
            project = {
                "Project Name": project_name,
                "Category": get_category_from_name(project_name),
                "Status": "Active",
                "Priority": "Medium",
                "Location": "",
                "Next Actions": "",
                "Dependencies": "",
                "Tech Stack": "",
                "Documentation Status": "In Progress",
                "Last Updated": datetime.now().strftime('%Y-%m'),
                "Résumé_Détaillé": f"Project imported from {os.path.basename(file_path)}"
            }
            
            # Map to main file structure
            project_dict = {col: project.get(col, "") for col in columns}
            projects.append(project_dict)
            
    except Exception as e:
        logging.error(f"Error parsing {file_path}: {e}")
    
    return projects

def is_duplicate(project, existing_projects):
    """Check if the project is a duplicate based on normalized project name."""
    project_name = normalize_text(project["Project Name"])
    
    for existing in existing_projects:
        existing_name = normalize_text(existing["Project Name"])
        
        # Check for high similarity
        if project_name == existing_name or \
           (len(project_name) > 5 and len(existing_name) > 5 and \
            (project_name in existing_name or existing_name in project_name)):
            return True
    
    return False

def main():
    # Get the column structure from the main file
    columns = get_main_file_columns()
    logging.info(f"Using columns: {columns}")
    
    # Read existing projects from main file
    existing_projects = []
    try:
        main_df = pd.read_csv('Projects - full.csv', encoding='utf-8', dtype=str)
        
        # Check if first column is an index/line number column
        first_col = main_df.columns[0]
        if 'Colonne' in first_col or first_col.isdigit() or first_col.startswith('Unnamed'):
            # Shift columns
            shifted_columns = main_df.columns[1:].tolist()
            main_df = main_df.iloc[:, 1:]
            main_df.columns = shifted_columns
        
        for _, row in main_df.iterrows():
            project_dict = {}
            for col in columns:
                if col in main_df.columns:
                    project_dict[col] = row.get(col, "")
                else:
                    project_dict[col] = ""
            existing_projects.append(project_dict)
        
        logging.info(f"Loaded {len(existing_projects)} existing projects")
    except FileNotFoundError:
        logging.warning("Main projects file not found. Will create a new one.")
    except Exception as e:
        logging.error(f"Error reading main projects file: {e}")
    
    # Find and process all CSV files
    all_projects = existing_projects.copy()
    new_projects = []
    
    for file in os.listdir('.'):
        if file.endswith('.csv') and file != 'Projects - full.csv':
            logging.info(f"Processing {file}...")
            
            if 'lovable' in file.lower():
                projects = parse_lovable_csv(file, columns)
            elif 'websim' in file.lower():
                projects = parse_websim_csv(file, columns)
            else:
                projects = parse_generic_csv(file, columns)
            
            # Add non-duplicate projects
            for project in projects:
                if not is_duplicate(project, all_projects):
                    new_projects.append(project)
                    all_projects.append(project)
            
            logging.info(f"Found {len(projects)} projects in {file}, {len(new_projects)} are new")
    
    # Add new projects to main file
    if new_projects:
        # Create a DataFrame with all projects
        merged_df = pd.DataFrame(all_projects)
        
        # Save to file
        merged_df.to_csv('Projects - full.csv', index=True, encoding='utf-8')
        logging.info(f"Saved {len(all_projects)} projects to 'Projects - full.csv' ({len(new_projects)} new)")
    else:
        logging.info("No new projects found")

if __name__ == "__main__":
    main()

