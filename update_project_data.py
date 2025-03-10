#!/usr/bin/env python3
import pandas as pd
import re
import os
import shutil
import datetime
import plotly.express as px
import sys

# Function to create a backup of a file
def backup_file(file_path):
    """Create a backup of the specified file with timestamp in filename."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}_backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

# Function to update tech stack based on project name and category
def update_tech_stack(df):
    """Update 'Tech Stack' field for projects where it's currently 'Inconnu'."""
    # Create a backup of the CSV file
    csv_file = 'Projects - full.csv'
    backup_file(csv_file)
    
    # Map to store project name/category patterns to tech stacks
    tech_stack_mapping = {
        # Web Development patterns
        r'(react|web|frontend|front-end|html|css|javascript|js|landing page|website)': 'JavaScript/React',
        r'(vue|nuxt|svelte|angular)': 'JavaScript/Vue/Angular',
        r'(node|express|nestjs)': 'Node.js',
        r'(php|laravel|symfony|wordpress|wp)': 'PHP',
        r'(ruby|rails)': 'Ruby on Rails',
        r'(django|flask|fastapi|python web)': 'Python/Django/Flask',
        
        # Mobile Development patterns
        r'(mobile|android|ios|flutter|react native|expo|app)': 'Mobile Development',
        
        # Backend/Database patterns
        r'(api|backend|back-end|server|database|db|sql|mysql|postgres|mongodb)': 'Backend',
        
        # AI/ML patterns
        r'(ai|ml|machine learning|neural|nlp|chatbot|bot)': 'Python/TensorFlow/PyTorch',
        
        # DevOps/Infrastructure patterns
        r'(devops|docker|kubernetes|k8s|aws|azure|cloud|ci/cd|jenkins)': 'DevOps',
        
        # Blockchain patterns
        r'(blockchain|crypto|web3|ethereum|solidity|nft)': 'Blockchain/Web3',
        
        # General patterns (fallback)
        r'(python)': 'Python',
        r'(java|spring)': 'Java',
        r'(c\#|\.net|asp\.net)': 'C#/.NET',
        r'(c\+\+)': 'C++',
        r'(go|golang)': 'Go',
    }
    
    # Function to determine tech stack based on project name and category
    def determine_tech_stack(row):
        if row['Tech Stack'] != 'Inconnu':
            return row['Tech Stack']
        
        project_name = str(row['Project Name']).lower()
        category = str(row['Category']).lower() if pd.notna(row['Category']) else ""
        
        for pattern, tech in tech_stack_mapping.items():
            if re.search(pattern, project_name) or re.search(pattern, category):
                return tech
        
        # Default to "Unknown" if no match found
        return "Multiple Technologies"
    
    # Apply the function to update tech stacks
    updated_count = 0
    for idx, row in df.iterrows():
        if row['Tech Stack'] == 'Inconnu':
            new_tech = determine_tech_stack(row)
            if new_tech != 'Inconnu':
                df.at[idx, 'Tech Stack'] = new_tech
                updated_count += 1
    
    # Save the updated DataFrame to CSV
    df.to_csv(csv_file, index=False)
    print(f"Updated {updated_count} projects with 'Inconnu' tech stack")
    return df

# Function to update the timeline visualization in project_dashboard.py
def update_timeline_visualization():
    """Modify project_dashboard.py to enhance the timeline visualization."""
    dashboard_file = 'project_dashboard.py'
    backup_file(dashboard_file)
    
    with open(dashboard_file, 'r') as f:
        content = f.read()
    
    # Define the pattern for the timeline visualization code
    timeline_pattern = r'(# Project Timeline.*?px\.timeline\(.*?\).*?)(st\.plotly_chart\(.*?\))'
    
    # Define the improved timeline code
    improved_timeline = '''# Project Timeline
    st.header("Project Timeline")
    
    # Ensure the data is sorted chronologically
    timeline_df = df.sort_values('Last Updated')
    
    # Create a more appealing timeline with enhanced styling
    timeline_fig = px.timeline(
        timeline_df,
        x_start="Last Updated", 
        x_end="Completion Date", 
        y="Project Name",
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Bold,  # More appealing color scheme
        hover_data=["Tech Stack", "Status", "Priority"]  # Add more info on hover
    )
    
    # Improve layout
    timeline_fig.update_layout(
        height=600,  # Increased height for better visibility
        margin=dict(l=50, r=50, t=50, b=50),  # Improved margins
        title='Project Timeline (Chronological Order)',
        xaxis_title='Timeline',
        yaxis_title='Projects',
        legend_title='Category',
        hovermode="closest"
    )
    
    # Add annotations or styling
    timeline_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    timeline_fig.update_yaxes(autorange="reversed")  # Reverse y-axis for more intuitive timeline
    
    st.plotly_chart(timeline_fig, use_container_width=True)'''
    
    # Replace the timeline code in the file
    updated_content = re.sub(timeline_pattern, improved_timeline, content, flags=re.DOTALL)
    
    # Write the updated content back to the file
    with open(dashboard_file, 'w') as f:
        f.write(updated_content)
    
    print(f"Updated timeline visualization in {dashboard_file}")

def main():
    try:
        # Read the CSV file
        df = pd.read_csv('Projects - full.csv')
        
        # 1. Update tech stack information
        df = update_tech_stack(df)
        
        # 2. Update timeline visualization
        update_timeline_visualization()
        
        print("All updates completed successfully!")
        print("\nTo see the changes, run:")
        print("source ./project_dashboard_env/bin/activate && streamlit run project_dashboard.py")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

