import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import time
from streamlit.components.v1 import html
import base64
from fpdf import FPDF
import io
import threading
import webbrowser
import json
import requests
from pathlib import Path
# Define GitHub logo as SVG
github_logo = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"#24292e\">" + \
    "<path d=\"M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z\"/>" + \
    "</svg>"

# Function to generate GitHub-styled buttons
def github_button(url, text):
    button_style = "<style>" + \
    ".github-button {" + \
    "    display: inline-flex;" + \
    "    align-items: center;" + \
    "    background-color: #24292e;" + \
    "    color: white;" + \
    "    padding: 8px 12px;" + \
    "    border-radius: 6px;" + \
    "    font-weight: 600;" + \
    "    font-size: 14px;" + \
    "    text-decoration: none;" + \
    "    margin: 5px 0;" + \
    "    transition: background-color 0.3s;" + \
    "}" + \
    ".github-button:hover {" + \
    "    background-color: #0366d6;" + \
    "}" + \
    "</style>"
    
    return f"{button_style}" + \
    f"<a href=\"{url}\" target=\"_blank\" class=\"github-button\">" + \
    f"{github_logo} <span style=\"margin-left: 8px;\">{text}</span>" + \
    "</a>"

# Functions to load and save GitHub repository links
def get_github_repos_file():
    return Path("github_repos.json")

def load_github_repos():
    repos_file = get_github_repos_file()
    if repos_file.exists():
        try:
            with open(repos_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading GitHub repository links: {e}")
            return {}
    return {}

def save_github_repos(repos_dict):
    repos_file = get_github_repos_file()
    try:
        with open(repos_file, 'w') as f:
            json.dump(repos_dict, f)
        return True
    except Exception as e:
        st.error(f"Error saving GitHub repository links: {e}")
        return False

# Function to validate GitHub repository URL
def is_valid_github_url(url):
    if not url:
        return False
    # Check if URL has valid GitHub format
    if not url.startswith("https://github.com/"):
        return False
    # Check if repository exists (optional)
    try:
        response = requests.head(url, timeout=2)
        return response.status_code < 400
    except:
        return True  # If can't connect, still accept the URL

# Page configuration
st.set_page_config(
    page_title="Project Management Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown(
    "<style>" +
    "    .main {" +
    "        background-color: #f5f5f5;" +
    "    }" +
    "    .project-card {" +
    "        background-color: white;" +
    "        border-radius: 5px;" +
    "        padding: 20px;" +
    "        margin-bottom: 20px;" +
    "        box-shadow: 0 4px 6px rgba(0,0,0,0.1);" +
    "    }" +
    "    .category-header {" +
    "        background-color: #6f42c1;" +
    "        color: white;" +
    "        padding: 10px 15px;" +
    "        border-radius: 5px;" +
    "        margin: 15px 0 10px 0;" +
    "        font-weight: bold;" +
    "        cursor: pointer;" +
    "    }" +
    "    .category-content {" +
    "        border-left: 3px solid #6f42c1;" +
    "        padding-left: 15px;" +
    "        margin-left: 5px;" +
    "    }" +
    "    .status-active {" +
    "        color: white;" +
    "        background-color: #28a745;" +
    "        padding: 3px 10px;" +
    "        border-radius: 10px;" +
    "        font-size: 14px;" +
    "    }" +
    "    .status-on-hold {" +
    "        color: white;" +
    "        background-color: #ffc107;" +
    "        padding: 3px 10px;" +
    "        border-radius: 10px;" +
    "        font-size: 14px;" +
    "    }" +
    "    .status-completed {" +
    "        color: white;" +
    "        background-color: #007bff;" +
    "        padding: 3px 10px;" +
    "        border-radius: 10px;" +
    "        font-size: 14px;" +
    "    }" +
    "    .status-abandoned {" +
    "        color: white;" +
    "        background-color: #dc3545;" +
    "        padding: 3px 10px;" +
    "        border-radius: 10px;" +
    "        font-size: 14px;" +
    "    }" +
    "    .priority-high {" +
    "        color: white;" +
    "        background-color: #dc3545;" +
    "        padding: 3px 10px;" +
    "        border-radius: 10px;" +
    "        font-size: 14px;" +
    "    }" +
    "    .priority-medium {" +
    "        color: white;" +
    "        background-color: #ffc107;" +
    "        padding: 3px 10px;" +
    "        border-radius: 10px;" +
    "        font-size: 14px;" +
    "    }" +
    "    .priority-low {" +
    "        color: white;" +
    "        background-color: #28a745;" +
    "        padding: 3px 10px;" +
    "        border-radius: 10px;" +
    "        font-size: 14px;" +
    "    }" +
    "    .section-header {" +
    "        background-color: #4e73df;" +
    "        color: white;" +
    "        padding: 10px;" +
    "        border-radius: 5px;" +
    "        margin-bottom: 20px;" +
    "    }" +
    "    .metric-card {" +
    "        background-color: white;" +
    "        border-left: 5px solid #4e73df;" +
    "        padding: 15px;" +
    "        border-radius: 5px;" +
    "        box-shadow: 0 2px 4px rgba(0,0,0,0.1);" +
    "    }" +
    "    .metric-title {" +
    "        color: #555;" +
    "        font-size: 1.1em;" +
    "        margin-bottom: 10px;" +
    "    }" +
    "    .metric-value-active {" +
    "        color: #28a745;" +
    "        font-size: 2.2em;" +
    "        font-weight: bold;" +
    "    }" +
    "    .metric-value-total {" +
    "        color: #007bff;" +
    "        font-size: 2.2em;" +
    "        font-weight: bold;" +
    "    }" +
    "    .metric-value-priority {" +
    "        color: #dc3545;" +
    "        font-size: 2.2em;" +
    "        font-weight: bold;" +
    "    }" +
    "    .metric-value-category {" +
    "        color: #6f42c1;" +
    "        font-size: 2.2em;" +
    "        font-weight: bold;" +
    "    }" +
    "</style>", 
    unsafe_allow_html=True
)
# Function for main application
def main():
    # Load saved GitHub repository links
    github_repos = load_github_repos()
    
    # Show requirements message
    show_requirements_message()
    
    # Display about section in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info("This dashboard provides an overview of all projects and their details. Use the filters to narrow down projects by category, status, priority, or technology stack.")
    st.sidebar.markdown("**Last updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # GitHub Integration sidebar section
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"<div style='display: flex; align-items: center;'><h3 style='margin-right: 10px;'>GitHub Integration</h3>{github_logo}</div>", unsafe_allow_html=True)
    
    # GitHub connection status
    if 'github_token' in st.session_state:
        st.sidebar.success("✓ Connected to GitHub")
        if st.sidebar.button("Disconnect from GitHub"):
            del st.session_state['github_token']
            st.experimental_rerun()
    else:
        st.sidebar.warning("Not connected to GitHub")
        st.sidebar.markdown(github_button("https://github.com/login", "Connect with GitHub"), unsafe_allow_html=True)
    
    # Global GitHub settings
    with st.sidebar.expander("GitHub Settings"):
        default_org = st.text_input("Default Organization/User", 
                                    value=st.session_state.get('default_github_org', ''),
                                    placeholder="e.g., your-username")
        if st.button("Save Settings"):
            st.session_state['default_github_org'] = default_org
            st.success("Settings saved!")
    
    # Add info about GitHub integration
    st.sidebar.info(
        "**GitHub Integration Features:**\n" + 
        "- Link projects to their GitHub repositories\n" + 
        "- Track project progress with GitHub issues\n" + 
        "- Get notifications for repository updates"
    )

    
    # Auto-refresh option
    st.sidebar.markdown("---")
    st.sidebar.subheader("Dashboard Settings")
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 
                                         min_value=10, 
                                         max_value=300, 
                                         value=60, 
                                         step=10,
                                         disabled=not auto_refresh)
    
    if auto_refresh:
        st.sidebar.info(f"Dashboard will refresh every {refresh_interval} seconds.")
        time.sleep(refresh_interval)
        st.experimental_rerun()

    # Export to PDF functionality
    st.sidebar.markdown("---")
    if st.sidebar.button("Export Dashboard to PDF"):
        try:
            # Create a PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(190, 10, "Project Management Dashboard", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(190, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
            pdf.ln(10)
            
            # Add dashboard metrics
            pdf.set_font("Arial", "B", 14)
            pdf.cell(190, 10, "Dashboard Metrics", ln=True)
            pdf.set_font("Arial", "", 12)
            
            # Create a table of project data
            pdf.set_font("Arial", "B", 12)
            pdf.cell(60, 10, "Project Name", border=1)
            pdf.cell(40, 10, "Status", border=1)
            pdf.cell(40, 10, "Category", border=1)
            pdf.cell(40, 10, "Priority", border=1, ln=True)
            
            pdf.set_font("Arial", "", 10)
            for _, row in df.iterrows():
                pdf.cell(60, 10, str(row.get('Project Name', 'Unknown'))[:28], border=1)
                pdf.cell(40, 10, str(row.get('Status', 'Unknown')), border=1)
                pdf.cell(40, 10, str(row.get('Category', 'Unknown')), border=1)
                pdf.cell(40, 10, str(row.get('Priority', 'Unknown')), border=1, ln=True)
                
            # Output the PDF to bytes buffer
            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_bytes = pdf_output.getvalue()
            
            # Create download button
            b64_pdf = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="project_dashboard.pdf">Download PDF</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
            st.sidebar.success("PDF Export Ready! Click the link above to download.")
        except Exception as e:
            st.sidebar.error(f"Error generating PDF: {e}")
    
    # Title and description
    st.title("Project Management Dashboard")
    st.markdown("Dashboard for monitoring and tracking all projects. Use the sidebar to filter projects and access dashboard features.")
    st.markdown(
        "> **Data Source**: This dashboard requires at least one CSV file with project data.\n" + 
        "> The preferred data source is \"Projects - full.csv\" which should be kept in the repository.\n" + 
        "> Other CSV files are optional and may be excluded from version control."
    )
    
    # Load data from CSV files
    @st.cache_data(ttl=300)  # Cache data for 5 minutes
    def load_data():
        try:
            csv_files = []
            for root, _, files in os.walk('.'):
                for file in files:
                    if file.endswith('.csv'):
                        csv_files.append(os.path.join(root, file))
            
            # If no CSV files found, return empty DataFrame
            if not csv_files:
                st.warning("No CSV files found in the directory.")
                return pd.DataFrame()
            
            # Focus on Projects - full.csv if it exists
            main_file = None
            for file in csv_files:
                if "Projects - full.csv" in file:
                    main_file = file
                    break
            
            if main_file:
                df = pd.read_csv(main_file)
                return df
            else:
                # If main file not found, use the first CSV file
                df = pd.read_csv(csv_files[0])
                return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    df = load_data()
    
    # If DataFrame is empty, show message and stop
    if df.empty:
        st.warning("No data available. Please check your CSV files.")
        st.stop()
    
    # Overview metrics section
    st.markdown("<div class='section-header'><h2>Overview</h2></div>", unsafe_allow_html=True)
    
    # Count metrics
    total_projects = len(df)
    active_projects = len(df[df['Status'] == 'Active']) if 'Status' in df.columns else 0
    high_priority = len(df[df['Priority'] == 'High']) if 'Priority' in df.columns else 0
    unique_categories = df['Category'].nunique() if 'Category' in df.columns else 0
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            "<div class='metric-card'>" +
            "<div class='metric-title'>Active Projects</div>" +
            f"<div class='metric-value-active'>{active_projects}</div>" +
            "</div>", 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            "<div class='metric-card'>" +
            "<div class='metric-title'>Total Projects</div>" +
            f"<div class='metric-value-total'>{total_projects}</div>" +
            "</div>", 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            "<div class='metric-card'>" +
            "<div class='metric-title'>High Priority</div>" +
            f"<div class='metric-value-priority'>{high_priority}</div>" +
            "</div>", 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            "<div class='metric-card'>" +
            "<div class='metric-title'>Categories</div>" +
            f"<div class='metric-value-category'>{unique_categories}</div>" +
            "</div>", 
            unsafe_allow_html=True
        )
    
    # Create charts for data visualization
    st.markdown("<div class='section-header'><h2>Data Visualizations</h2></div>", unsafe_allow_html=True)
    
    # Distribution by status and category in two columns
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig = px.pie(status_counts, values='Count', names='Status', 
                        title='Project Distribution by Status',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Status column not found in the data.")
    
    with chart_col2:
        if 'Category' in df.columns:
            category_counts = df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']
            
            fig = px.bar(category_counts, x='Category', y='Count',
                        title='Project Distribution by Category',
                        color='Count', color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Category column not found in the data.")
    
    # Technology usage chart
    # Function to detect technologies from project names and descriptions
    def detect_technologies(project_name, description=None, category=None):
        # Dictionary mapping keywords to technologies
        tech_keywords = {
            # Frontend frameworks and libraries
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'svelte': 'Svelte',
            'jquery': 'jQuery',
            'backbone': 'Backbone.js',
            'ember': 'Ember.js',
            
            # Backend frameworks
            'node': 'Node.js',
            'express': 'Express.js',
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'rails': 'Ruby on Rails',
            'symfony': 'Symfony',
            'laravel': 'Laravel',
            'spring': 'Spring',
            'nestjs': 'NestJS',
            'asp.net': 'ASP.NET',
            
            # Languages
            'php': 'PHP',
            'python': 'Python',
            'java': 'Java',
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'go': 'Go',
            'golang': 'Go',
            'rust': 'Rust',
            'c#': 'C#',
            '.net': '.NET',
            'ruby': 'Ruby',
            'scala': 'Scala',
            'elixir': 'Elixir',
            'clojure': 'Clojure',
            'haskell': 'Haskell',
            
            # Frontend technologies
            'html': 'HTML',
            'css': 'CSS',
            'sass': 'Sass',
            'less': 'Less',
            'bootstrap': 'Bootstrap',
            'tailwind': 'Tailwind CSS',
            'material': 'Material UI',
            'bulma': 'Bulma',
            
            # Databases
            'mongo': 'MongoDB',
            'postgres': 'PostgreSQL',
            'mysql': 'MySQL',
            'sql': 'SQL',
            'redis': 'Redis',
            'sqlite': 'SQLite',
            'firestore': 'Firestore',
            'dynamodb': 'DynamoDB',
            'cassandra': 'Cassandra',
            'couchdb': 'CouchDB',
            
            # Infrastructure
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'aws': 'AWS',
            'azure': 'Azure',
            'gcp': 'GCP',
            'heroku': 'Heroku',
            'netlify': 'Netlify',
            'vercel': 'Vercel',
            'jenkins': 'Jenkins',
            'gitlab': 'GitLab CI',
            'github actions': 'GitHub Actions',
            
            # Mobile
            'android': 'Android',
            'ios': 'iOS',
            'swift': 'Swift',
            'kotlin': 'Kotlin',
            'flutter': 'Flutter',
            'react native': 'React Native',
            'expo': 'Expo',
            'ionic': 'Ionic',
            'xamarin': 'Xamarin',
            
            # AI/ML
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'keras': 'Keras',
            'scikit': 'Scikit-learn',
            'ml': 'Machine Learning',
            'ai': 'AI',
            'cv': 'Computer Vision',
            'nlp': 'NLP',
            
            # Blockchain
            'blockchain': 'Blockchain',
            'web3': 'Web3',
            'eth': 'Ethereum',
            'solidity': 'Solidity',
            'nft': 'NFT',
            'bitcoin': 'Bitcoin',
            
            # CMS
            'wordpress': 'WordPress',
            'drupal': 'Drupal',
            'joomla': 'Joomla',
            'contentful': 'Contentful',
            'strapi': 'Strapi',
            
            # Testing
            'jest': 'Jest',
            'cypress': 'Cypress',
            'selenium': 'Selenium',
            'playwright': 'Playwright',
            'pytest': 'Pytest',
            'junit': 'JUnit',
            'solidity': 'Solidity',
            'nft': 'NFT',
            'fastapi': 'FastAPI',
            'api': 'API',
            'graphql': 'GraphQL',
            'rest': 'REST API',
            'sass': 'SASS',
            'gatsby': 'Gatsby',
            'next': 'Next.js',
            'nuxt': 'Nuxt.js',
            'svelte': 'Svelte',
            'firebase': 'Firebase',
            'supabase': 'Supabase',
            'stripe': 'Stripe',
            'pwa': 'PWA',
            'seo': 'SEO',
            'ui': 'UI/UX',
            'ux': 'UI/UX',
            'design': 'Design',
            'figma': 'Figma',
            'websocket': 'WebSockets',
            'socketio': 'Socket.IO',
            'shadcn': 'shadcn/ui',
        }
        
        detected_techs = set()
        
        # Helper function to detect tech from text
        def detect_from_text(text):
            if not text or pd.isna(text):
                return
            
            text_lower = text.lower()
            for keyword, tech in tech_keywords.items():
                if keyword in text_lower:
                    detected_techs.add(tech)
        
        # Check project name
        detect_from_text(project_name)
        
        # Check description
        detect_from_text(description)
        
        # Use category to infer technologies
        category_tech_map = {
            'Web Development': ['HTML', 'CSS', 'JavaScript'],
            'Mobile Development': ['Mobile'],
            'Database': ['Database'],
            'Machine Learning': ['Python', 'Machine Learning'],
            'AI/ML': ['Python', 'AI', 'Machine Learning'],
            'Data Science': ['Python', 'Data Analysis'],
            'DevOps': ['Docker', 'CI/CD'],
            'Blockchain': ['Blockchain', 'Smart Contracts'],
        }
        
        if category and category in category_tech_map:
            detected_techs.update(category_tech_map[category])
        
        # Return comma-separated string of technologies
        return ', '.join(detected_techs) if detected_techs else None

    # Technology usage chart
    if 'Tech Stack' in df.columns:
        # Extract technologies from Tech Stack column
        tech_list = []
        for tech_stack in df['Tech Stack'].dropna():
            techs = [t.strip() for t in tech_stack.split(',')]
            # Replace 'Inconnu' with original value instead of filtering it out
            # This ensures we don't replace it with "Multiple Technologies" elsewhere
            processed_techs = [tech if tech != 'Inconnu' else 'Unknown' for tech in techs]
            tech_list.extend(processed_techs)
        
        tech_counts = pd.Series(tech_list).value_counts().reset_index()
        tech_counts.columns = ['Technology', 'Count']  # Add this line to rename columns
        tech_counts = tech_counts.head(15)  # Top 15 technologies
        
        fig = px.bar(tech_counts, x='Count', y='Technology', 
                    title='Most Used Technologies',
                    orientation='h',
                    color='Count', color_continuous_scale='Turbo')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add Auto-detect Technologies button for projects with unknown tech stacks
        st.markdown("### Auto-detect Technologies")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            Some projects might have unknown technology stacks or incorrect information.
            Click the button to automatically detect technologies based on project names and categories.
            """)
            
        with col2:
            if st.button("Auto-detect Technologies", key="auto_detect_tech"):
                # Make a copy of the DataFrame to work with
                updated_df = df.copy()
                # Count how many tech stacks were updated
                update_count = 0
                
                # Find projects with unknown or empty tech stacks
                for idx, row in updated_df.iterrows():
                    # Check if Tech Stack is Unknown, empty, or contains 'Inconnu'
                    if ('Tech Stack' not in row or 
                        pd.isna(row['Tech Stack']) or 
                        row['Tech Stack'] == 'Unknown' or 
                        row['Tech Stack'] == 'Inconnu' or
                        row['Tech Stack'] == 'Multiple Technologies' or
                        row['Tech Stack'] == ''):
                        
                        # Try to detect technologies
                        project_name = row.get('Project Name', '')
                        description = row.get('Résumé_Détaillé', '')
                        category = row.get('Category', '')
                        
                        detected_tech = detect_technologies(project_name, description, category)
                        
                        if detected_tech:
                            updated_df.at[idx, 'Tech Stack'] = detected_tech
                            update_count += 1
                
                # If any updates were made, offer to save the changes
                if update_count > 0:
                    st.success(f"✅ Successfully detected technologies for {update_count} projects!")
                    
                    if st.button("Save Changes to CSV", key="save_detected_tech"):
                        try:
                            # Backup the original file
                            backup_file = f"Projects - full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            df.to_csv(backup_file, index=False)
                            
                            # Save the updated DataFrame
                            updated_df.to_csv('Projects - full.csv', index=False)
                            
                            st.success(f"✅ Changes saved! Original file backed up as {backup_file}")
                            st.info("Refresh the page to see the updated technology information.")
                        except Exception as e:
                            st.error(f"❌ Error saving changes: {e}")
                else:
                    st.info("No new technologies detected. All projects already have appropriate tech stacks.")
                    
        st.markdown("---")
        fig.update_layout(height=500)
    
    # Timeline chart with Gantt style
    st.markdown("<div class='section-header'><h2>Project Timeline</h2></div>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* Custom styling for the timeline visualization */
    .js-plotly-plot .plotly .modebar {
        right: 10px !important;
    }
    .js-plotly-plot .plotly .xaxis .gridline, 
    .js-plotly-plot .plotly .yaxis .gridline {
        stroke-width: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create timeline filters
    st.markdown("### Timeline Filters")
    timeline_filter_col1, timeline_filter_col2, timeline_filter_col3 = st.columns(3)
    
    with timeline_filter_col1:
        status_timeline_filter = st.multiselect(
            'Filter by Status', 
            options=df['Status'].unique().tolist() if 'Status' in df.columns else [],
            default=df['Status'].unique().tolist() if 'Status' in df.columns else []
        )
    
    with timeline_filter_col2:
        if 'Category' in df.columns:
            category_timeline_filter = st.multiselect(
                'Filter by Category', 
                options=df['Category'].dropna().unique().tolist(),
                default=df['Category'].dropna().unique().tolist()
            )
        else:
            category_timeline_filter = []
    
    with timeline_filter_col3:
        if 'Priority' in df.columns:
            priority_timeline_filter = st.multiselect(
                'Filter by Priority', 
                options=df['Priority'].dropna().unique().tolist(),
                default=df['Priority'].dropna().unique().tolist()
            )
        else:
            priority_timeline_filter = []
    
    # Create timeline data
    if 'Last Updated' in df.columns:
        try:
            # Create a copy of dataframe for timeline
            timeline_df = df.copy()
            
            # Apply filters
            if status_timeline_filter:
                timeline_df = timeline_df[timeline_df['Status'].isin(status_timeline_filter)]
            
            if category_timeline_filter and 'Category' in df.columns:
                timeline_df = timeline_df[timeline_df['Category'].isin(category_timeline_filter)]
            
            if priority_timeline_filter and 'Priority' in df.columns:
                timeline_df = timeline_df[timeline_df['Priority'].isin(priority_timeline_filter)]
            
            # Prepare timeline data
            if 'Creation Date' in timeline_df.columns:
                timeline_df['Start'] = pd.to_datetime(timeline_df['Creation Date'], errors='coerce')
            else:
                # If no creation date, use a date 30 days before Last Updated
                timeline_df['Start'] = pd.to_datetime(timeline_df['Last Updated'], errors='coerce') - pd.Timedelta(days=30)
            
            timeline_df['End'] = pd.to_datetime(timeline_df['Last Updated'], errors='coerce')
            
            # Add target completion date as a milestone
            if 'Target Completion' in timeline_df.columns:
                timeline_df['Target'] = pd.to_datetime(timeline_df['Target Completion'], errors='coerce')
            
            # Remove rows with invalid dates
            timeline_df = timeline_df.dropna(subset=['Start', 'End'])
            
            # Sort by start date
            timeline_df = timeline_df.sort_values('Start')
            
            # Limit to the most recent 100 projects to keep the chart readable
            if len(timeline_df) > 100:
                st.info(f"Showing the 100 most recent projects out of {len(timeline_df)} matching your filters.")
                timeline_df = timeline_df.iloc[-100:]
            
            if not timeline_df.empty:
                # Create the timeline visualization using Plotly
                fig = go.Figure()
                
                # Define colors for different statuses - using more vibrant colors
                color_map = {
                    'Active': '#00E676',      # Vibrant green
                    'On Hold': '#FFAB00',     # Vibrant amber
                    'Completed': '#2979FF',   # Vibrant blue
                    'Abandoned': '#FF1744',   # Vibrant red
                    'In Progress': '#651FFF', # Vibrant purple
                    'Planned': '#00B0FF',     # Vibrant light blue
                    'Testing': '#FF9100',     # Vibrant orange
                    'Reviewing': '#F50057'    # Vibrant pink
                }
                
                # Add timeline markers for each project (using go.Scatter instead of go.Bar)
                for idx, row in timeline_df.iterrows():
                    status = row.get('Status', 'Unknown')
                    # Default is now a vibrant teal instead of grey if status not in map
                    color = color_map.get(status, '#00BCD4')
                    
                    # Calculate duration for the hover text
                    start_date = row['Start']
                    end_date = row['End']
                    duration_days = (end_date - start_date).days
                    
                    # Create hover text with relevant project info
                    hover_text = (
                        f"<b>{row['Project Name']}</b><br>"
                        f"Status: {status}<br>"
                        f"Duration: {duration_days} days<br>"
                        f"Start: {start_date.strftime('%Y-%m-%d')}<br>"
                        f"Last Update: {end_date.strftime('%Y-%m-%d')}<br>"
                    )
                    
                    if 'Category' in row and pd.notna(row['Category']):
                        hover_text += f"Category: {row['Category']}<br>"
                        hover_text += f"Category: {row['Category']}<br>"
                    
                    if 'Priority' in row and pd.notna(row['Priority']):
                        hover_text += f"Priority: {row['Priority']}<br>"
                    
                    if 'Tech Stack' in row and pd.notna(row['Tech Stack']):
                        hover_text += f"Tech Stack: {row['Tech Stack']}<br>"
                    # Add a line connecting start to end date
                    fig.add_trace(go.Scatter(
                        x=[start_date, end_date],
                        y=[row['Project Name'], row['Project Name']],
                        mode='lines',
                        line=dict(
                            color=color,
                            width=3
                        ),
                        name=status,
                        legendgroup=status,
                        showlegend=(idx == next((i for i, r in timeline_df.iterrows() if r.get('Status') == status), None)),
                        hoverinfo='skip'
                    ))
                    
                    # Add start point marker (circle)
                    fig.add_trace(go.Scatter(
                        x=[start_date],
                        y=[row['Project Name']],
                        mode='markers',
                        marker=dict(
                            symbol='circle',
                            size=8,
                            color=color,
                            line=dict(width=1, color='white')
                        ),
                        name=f"{status} (Start)",
                        hoverinfo='text',
                        hovertext=hover_text,
                        showlegend=False,
                        legendgroup=status
                    ))
                    
                    # Add end point marker (circle)
                    fig.add_trace(go.Scatter(
                        x=[end_date],
                        y=[row['Project Name']],
                        mode='markers',
                        marker=dict(
                            symbol='circle',
                            size=10,
                            color=color,
                            line=dict(width=1, color='white')
                        ),
                        name=f"{status} (End)",
                        hoverinfo='text',
                        hovertext=hover_text,
                        showlegend=False,
                        legendgroup=status
                    ))
                    if 'Target' in row and pd.notna(row['Target']):
                        fig.add_trace(go.Scatter(
                            x=[row['Target']],
                            y=[row['Project Name']],
                            mode='markers',
                            marker=dict(
                                symbol='diamond',
                                size=10,
                                color='rgba(255,255,255,0.9)',  # White fill
                                line=dict(width=2, color='#E91E63'),  # Pink border
                            ),
                            name='Target Date',
                            hoverinfo='text',
                            hovertext=f"<b>Target Completion:</b> {row['Target'].strftime('%Y-%m-%d')}",
                            showlegend=(idx == timeline_df.index[0]),  # Only show in legend once
                            legendgroup='Target'
                        ))
                
                # Update layout for better appearance
                fig.update_layout(
                    title='Project Timeline (Gantt Chart)',
                    height=max(400, len(timeline_df) * 20),  # More compact height
                    margin=dict(l=10, r=10, t=40, b=30),
                    plot_bgcolor='white',  # Clean white background
                    paper_bgcolor='white',
                    yaxis=dict(
                        autorange="reversed",  # Reverses the y-axis so newest projects are at top
                        title='',
                        tickfont=dict(size=10),  # Smaller font for project names
                    ),
                    xaxis=dict(
                        title='Timeline',
                        gridcolor='rgba(240, 240, 240, 0.9)',  # Lighter grid lines
                        zeroline=False,  # Remove zero line for cleaner look
                    ),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Arial",
                        bordercolor='rgba(0,0,0,0.1)',  # Subtle border
                    ),
                    bargap=0.4,  # Increase gap between bars for better separation
                    uniformtext=dict(minsize=8, mode='hide'),  # Consistent text size
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bgcolor='rgba(255,255,255,0.8)',
                    ),
                )
                # No need to manually add legend items as they're now created naturally through the scatter points
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No project data available for timeline visualization.")
        except Exception as e:
            st.error(f"Error creating timeline visualization: {e}")
    else:
        st.warning("'Last Updated' column is required for timeline visualization.")
    
    # Cycling routes visualization section
    display_cycling_routes(df)
    
    # Filters for projects
    st.markdown("<div class='section-header'><h2>Project Filters</h2></div>", unsafe_allow_html=True)
    
    # Create filter columns
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    # Filter by status
    with filter_col1:
        status_options = ['All'] + sorted(df['Status'].unique().tolist()) if 'Status' in df.columns else ['All']
        status_filter = st.selectbox('Filter by Status', status_options)
    
    # Filter by category
    with filter_col2:
        # Filter out NaN values from Category column before sorting
        if 'Category' in df.columns:
            # Get unique categories and filter out NaN values
            categories = [cat for cat in df['Category'].unique().tolist() if pd.notna(cat)]
            category_options = ['All'] + sorted(categories)
        else:
            category_options = ['All']
        category_filter = st.selectbox('Filter by Category', category_options)
    
    # Filter by priority
    with filter_col3:
        priority_options = ['All'] + sorted(df['Priority'].unique().tolist()) if 'Priority' in df.columns else ['All']
        priority_filter = st.selectbox('Filter by Priority', priority_options)
    
    # Filter by technology
    with filter_col4:
        # Extract all unique technologies
        all_techs = set()
        if 'Tech Stack' in df.columns:
            for tech_stack in df['Tech Stack'].dropna():
                techs = [t.strip() for t in tech_stack.split(',')]
                all_techs.update(techs)
        
        tech_options = ['All'] + sorted(list(all_techs))
        tech_filter = st.selectbox('Filter by Technology', tech_options)
    
    # Search functionality
    search_query = st.text_input('Search Projects', '')
    
    # Apply filters
    filtered_df = df.copy()
    
    if status_filter != 'All' and 'Status' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    
    if category_filter != 'All' and 'Category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Category'] == category_filter]
    
    if priority_filter != 'All' and 'Priority' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Priority'] == priority_filter]
    
    if tech_filter != 'All' and 'Tech Stack' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Tech Stack'].fillna('').str.contains(tech_filter)]
    
    if search_query:
        # Search across all string columns
        filtered_df = filtered_df[filtered_df.astype(str).agg(' '.join, axis=1).str.contains(search_query, case=False)]
    
    # Display number of filtered projects
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} projects**")
    
    # Project cards section
    st.markdown("<div class='section-header'><h2>Project Details</h2></div>", unsafe_allow_html=True)
    
    # No need to call a separate function for notifications since we're handling them later
    
    # If no projects match filters
    if filtered_df.empty:
        st.warning("No projects match the selected filters.")
    else:
        # Group projects by category
        if 'Category' in filtered_df.columns:
            # Sort the DataFrame by Category to group properly
            filtered_df = filtered_df.sort_values(by='Category')
            
            # Get all unique categories
            categories = filtered_df['Category'].unique()
            
            # Create collapsible sections for each category
            for category in categories:
                category_df = filtered_df[filtered_df['Category'] == category]
                
                # Create a collapsible section for each category
                with st.expander(f"**{category}** ({len(category_df)} projects)", expanded=False):
                    # Display all projects in this category
                    for _, row in category_df.iterrows():
                        st.markdown("<div class='project-card'>", unsafe_allow_html=True)
                        
                        # Project header with status badge
                        project_name = row.get('Project Name', 'Unknown Project')
                        project_status = row.get('Status', 'Unknown')
                        status_class = f"status-{project_status.lower().replace(' ', '-')}"
                        
                        st.markdown(f"<h3>{project_name} <span class='{status_class}'>{project_status}</span></h3>", unsafe_allow_html=True)
        else:
            # If no Category column, fall back to displaying all filtered projects
            for _, row in filtered_df.iterrows():
                st.markdown("<div class='project-card'>", unsafe_allow_html=True)
                
                # Project header with status badge
                project_name = row.get('Project Name', 'Unknown Project')
                project_status = row.get('Status', 'Unknown')
                status_class = f"status-{project_status.lower().replace(' ', '-')}"
                
                st.markdown(f"<h3>{project_name} <span class='{status_class}'>{project_status}</span></h3>", unsafe_allow_html=True)
            
            # Project details in columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Display category and tech stack
                if 'Category' in row and not pd.isna(row['Category']):
                    st.markdown(f"**Category:** {row['Category']}")
                
                if 'Tech Stack' in row and not pd.isna(row['Tech Stack']):
                    st.markdown("**Tech Stack:**")
                    tech_list = [tech.strip() for tech in row['Tech Stack'].split(',')]
                    st.markdown(", ".join(tech_list))
                
                if 'Location' in row and not pd.isna(row['Location']):
                    st.markdown(f"**Location:** {row['Location']}")
                
                # Display existing GitHub repository link if available
                if project_name in github_repos:
                    repo_url = github_repos[project_name]
                    # Add GitHub styled repository link
                    st.markdown(
                        f"<div style=\"margin-top: 15px; margin-bottom: 15px;\">" +
                        f"{github_button(repo_url, 'View on GitHub')}" +
                        "</div>", 
                        unsafe_allow_html=True
                    )
                    
                    # Add basic GitHub stats if connected
                    if 'github_token' in st.session_state:
                        st.markdown(
                            "<div style=\"background-color: #f6f8fa; padding: 10px; border-radius: 6px; margin-top: 10px;\">" +
                            "<div style=\"display: flex; gap: 15px;\">" +
                            "<div><strong>Stars:</strong> N/A</div>" +
                            "<div><strong>Forks:</strong> N/A</div>" +
                            "<div><strong>Open Issues:</strong> N/A</div>" +
                            "</div>" +
                            "</div>", 
                            unsafe_allow_html=True
                        )
                
                # GitHub repository form in an expander to save space
                with st.expander("Link GitHub Repository"):
                    with st.form(key=f"github_form_{_}"):
                        repo_url = st.text_input("GitHub Repository URL", 
                                               value=github_repos.get(project_name, ""),
                                               placeholder="https://github.com/username/repo")
                        
                        # Option to generate repo name from project name
                        if st.session_state.get('default_github_org', ''):
                            org = st.session_state['default_github_org']
                            repo_slug = project_name.lower().replace(' ', '-')
                            suggested_url = f"https://github.com/{org}/{repo_slug}"
                            
                            if st.button("Use suggested URL", key=f"suggest_{_}"):
                                repo_url = suggested_url
                        
                        # Validate GitHub URL
                        if repo_url and not repo_url.startswith("https://github.com/"):
                            st.warning("Please enter a valid GitHub URL starting with https://github.com/")
                        
                        submit = st.form_submit_button("Save GitHub Link")
                        
                        if submit and repo_url:
                            if is_valid_github_url(repo_url):
                                github_repos[project_name] = repo_url
                                if save_github_repos(github_repos):
                                    st.success(f"GitHub repository linked to {project_name}!")
                                else:
                                    st.error("Failed to save GitHub repository link. Please try again.")
                            else:
                                st.error("Invalid GitHub URL. Please check the format and ensure the repository exists.")
                            # Remove experimental_rerun to avoid reloading the entire page
                            # st.experimental_rerun()
            
            with col2:
                if 'Priority' in row and not pd.isna(row['Priority']):
                    priority_class = f"priority-{row['Priority'].lower().replace(' ', '-')}"
                    st.markdown(f"<div style='margin-bottom: 15px;'><strong>Priority:</strong> <span class='{priority_class}'>{row['Priority']}</span></div>", unsafe_allow_html=True)
                
                # Progress indicator if available
                if 'Progress' in row and not pd.isna(row['Progress']):
                    try:
                        progress_value = float(row['Progress'].replace('%', '')) / 100
                        st.progress(progress_value)
                        st.markdown(f"**Progress:** {row['Progress']}")
                    except:
                        pass
                
                # Next Actions
                if 'Next Actions' in row and not pd.isna(row['Next Actions']):
                    st.markdown("##### Next Actions")
                    actions = row['Next Actions'].split('\n')
                    for action in actions:
                        if action.strip():
                            st.markdown(f"- {action.strip()}")
                
                # Dependencies
                if 'Dependencies' in row and not pd.isna(row['Dependencies']):
                    st.markdown("##### Dependencies")
                    dependencies = row['Dependencies'].split('\n')
                    dependencies = row['Dependencies'].split('\n')
                    for dependency in dependencies:
                        if dependency.strip():
                            st.markdown(f"- {dependency.strip()}")
                if 'Documentation Status' in row and not pd.isna(row['Documentation Status']):
                    st.markdown(f"**Documentation Status:** {row['Documentation Status']}")

# For displaying cycling routes
def display_cycling_routes(df):
    st.markdown("<div class='section-header'><h2>Cycling Activity Routes</h2></div>", unsafe_allow_html=True)
    
    # Check if we have cycling data
    if 'lat' not in df.columns or 'lon' not in df.columns:
        st.info("No cycling route data available. Please upload GPS data with latitude and longitude coordinates.")
        
        # File uploader for GPS data
        uploaded_file = st.file_uploader("Upload cycling GPS data (CSV with lat, lon columns)", type="csv")
        if uploaded_file is not None:
            cycling_data = pd.read_csv(uploaded_file)
            if 'lat' in cycling_data.columns and 'lon' in cycling_data.columns:
                # Display the map
                st.map(cycling_data)
                
                # Display additional statistics if available
                if 'distance' in cycling_data.columns:
                    st.metric("Total Distance", f"{cycling_data['distance'].sum():.2f} km")
                if 'duration' in cycling_data.columns:
                    st.metric("Total Duration", f"{cycling_data['duration'].sum():.2f} min")
            else:
                st.error("Uploaded file must contain 'lat' and 'lon' columns.")
    else:
        # If lat/lon data is already in the dataframe
        st.map(df[['lat', 'lon']])

# Add notification system for deadlines
def display_notifications(df):
    if not df.empty and 'Last Updated' in df.columns:
        st.markdown("---")
        st.markdown("<div class='section-header'><h2>Notifications</h2></div>", unsafe_allow_html=True)
    
        # Calculate days since last update for each project
        current_date = pd.Timestamp(datetime.now().date())
        
        # Create a DataFrame for notifications
        notification_data = []
        
        for _, row in df.iterrows():
            if 'Last Updated' in row and not pd.isna(row['Last Updated']):
                # Ensure last_updated is a pandas Timestamp for consistent type comparison
                last_updated = pd.Timestamp(row['Last Updated']) if isinstance(row['Last Updated'], datetime) else pd.Timestamp(row['Last Updated'])
                days_since_update = (current_date - last_updated).days
                
                # Add notifications for projects not updated recently
                if days_since_update > 30:
                    notification_data.append({
                        'Project': row.get('Project Name', 'Unknown Project'),
                        'Notification': f"Not updated for {days_since_update} days",
                        'Type': 'Warning',
                        'Days': days_since_update
                    })
                
                # Add notifications for high priority projects
                if 'Priority' in row and row['Priority'] == 'High':
                    notification_data.append({
                        'Project': row.get('Project Name', 'Unknown Project'),
                        'Notification': "High priority project",
                        'Type': 'Info',
                        'Days': days_since_update
                    })
        
        if notification_data:
            notification_df = pd.DataFrame(notification_data)
            
            # Display notifications
            for _, notif in notification_df.iterrows():
                if notif['Type'] == 'Warning':
                    st.warning(f"**{notif['Project']}**: {notif['Notification']}")
                else:
                    st.info(f"**{notif['Project']}**: {notif['Notification']}")
        else:
            st.success("No notifications at this time.")

# Define display_footer function
def display_footer():
    # Add footer with version information
    st.markdown("---")
    footer_html = "<div style='text-align: center; color: gray;'>"
    footer_html += f"<p>Projects Dashboard v1.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    footer_html += "<p>For questions or support, contact the development team</p>"
    footer_html += "<p>"
    footer_html += f"<a href='https://github.com' target='_blank' style='color: #24292e; text-decoration: none; display: inline-flex; align-items: center; justify-content: center;'>{github_logo} <span style='margin-left: 5px;'>View on GitHub</span></a>"
    footer_html += "</p>"
    footer_html += "</div>"
    st.markdown(footer_html, unsafe_allow_html=True)

def show_requirements_message():
    # Requirements installation message (first run)
    if 'show_req_message' not in st.session_state:
        st.session_state.show_req_message = True
    
    if st.session_state.show_req_message:
        st.sidebar.markdown("---")
        st.sidebar.warning("**First time running?**")
        st.sidebar.warning("Make sure to install required packages:")
        st.sidebar.code("pip install streamlit pandas plotly fpdf")
        if st.sidebar.button("I've installed the requirements"):
            st.session_state.show_req_message = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()

