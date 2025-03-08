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
github_logo = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#24292e">
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
</svg>"""

# Function to generate GitHub-styled buttons
def github_button(url, text):
    button_style = """
    <style>
    .github-button {
        display: inline-flex;
        align-items: center;
        background-color: #24292e;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 14px;
        text-decoration: none;
        margin: 5px 0;
        transition: background-color 0.3s;
    }
    .github-button:hover {
        background-color: #0366d6;
    }
    </style>
    """
    
    return f"""
    {button_style}
    <a href="{url}" target="_blank" class="github-button">
        {github_logo} <span style="margin-left: 8px;">{text}</span>
    </a>
    """

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
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .project-card {
        background-color: white;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-active {
        color: white;
        background-color: #28a745;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 14px;
    }
    .status-on-hold {
        color: white;
        background-color: #ffc107;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 14px;
    }
    .status-completed {
        color: white;
        background-color: #007bff;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 14px;
    }
    .status-abandoned {
        color: white;
        background-color: #dc3545;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 14px;
    }
    .priority-high {
        color: white;
        background-color: #dc3545;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 14px;
    }
    .priority-medium {
        color: white;
        background-color: #ffc107;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 14px;
    }
    .priority-low {
        color: white;
        background-color: #28a745;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 14px;
    }
    .section-header {
        background-color: #4e73df;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        border-left: 5px solid #4e73df;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-title {
        color: #555;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .metric-value-active {
        color: #28a745;
        font-size: 2.2em;
        font-weight: bold;
    }
    .metric-value-total {
        color: #007bff;
        font-size: 2.2em;
        font-weight: bold;
    }
    .metric-value-priority {
        color: #dc3545;
        font-size: 2.2em;
        font-weight: bold;
    }
    .metric-value-category {
        color: #6f42c1;
        font-size: 2.2em;
        font-weight: bold;
    }
</style>
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
    st.sidebar.info("""
    **GitHub Integration Features:**
    - Link projects to their GitHub repositories
    - Track project progress with GitHub issues
    - Get notifications for repository updates
    """)

    
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
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-title'>Active Projects</div>
            <div class='metric-value-active'>{}</div>
        </div>
        """.format(active_projects), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-title'>Total Projects</div>
            <div class='metric-value-total'>{}</div>
        </div>
        """.format(total_projects), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-title'>High Priority</div>
            <div class='metric-value-priority'>{}</div>
        </div>
        """.format(high_priority), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-title'>Categories</div>
            <div class='metric-value-category'>{}</div>
        </div>
        """.format(unique_categories), unsafe_allow_html=True)
    
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
    if 'Tech Stack' in df.columns:
        # Extract technologies from Tech Stack column
        tech_list = []
        for tech_stack in df['Tech Stack'].dropna():
            techs = [t.strip() for t in tech_stack.split(',')]
            tech_list.extend(techs)
        
        tech_counts = pd.Series(tech_list).value_counts().reset_index()
        tech_counts.columns = ['Technology', 'Count']
        tech_counts = tech_counts.head(15)  # Top 15 technologies
        
        fig = px.bar(tech_counts, x='Count', y='Technology', 
                    title='Most Used Technologies',
                    orientation='h',
                    color='Count', color_continuous_scale='Turbo')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline chart
    st.subheader("Project Timeline")
    
    # Create timeline data
    if 'Last Updated' in df.columns:
        try:
            timeline_df = df[['Project Name', 'Status', 'Last Updated']].copy()
            timeline_df['Start_Date'] = pd.to_datetime(timeline_df['Last Updated'])
            timeline_df['End_Date'] = pd.Timestamp(datetime.now())  # Current date as end date
            
            if not timeline_df.empty:
                fig = px.timeline(timeline_df, 
                                x_start="Start_Date", 
                                x_end="End_Date",
                                y="Project Name", 
                                color="Status",
                                title="Project Timeline - Last Updated to Current Date")
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No timeline data available.")
        except Exception as e:
            st.error(f"Error generating timeline: {e}")
    
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
        category_options = ['All'] + sorted(df['Category'].unique().tolist()) if 'Category' in df.columns else ['All']
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
    
    # Display notifications
    display_notifications(df)
    
    # If no projects match filters
    if filtered_df.empty:
        st.warning("No projects match the selected filters.")
    else:
        # Display all filtered projects
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
                    st.markdown(f"""
                    <div style="margin-top: 15px; margin-bottom: 15px;">
                        {github_button(repo_url, "View on GitHub")}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add basic GitHub stats if connected
                    if 'github_token' in st.session_state:
                        st.markdown("""
                        <div style="background-color: #f6f8fa; padding: 10px; border-radius: 6px; margin-top: 10px;">
                            <div style="display: flex; gap: 15px;">
                                <div><strong>⭐ Stars:</strong> N/A</div>
                                <div><strong>🍴 Forks:</strong> N/A</div>
                                <div><strong>🔍 Open Issues:</strong> N/A</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
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
                    for dependency in dependencies:
                        if dependency.strip():
                        if dependency.strip():
                            st.markdown(f"- {dependency.strip()}")
                
                # Documentation Status
                if 'Documentation Status' in row and not pd.isna(row['Documentation Status']):
                    st.markdown(f"**Documentat# Add notification system for deadlines
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

if __name__ == "__main__":
    main()

def display_footer():
    # Add footer with version information
    st.markdown("---")
    st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Projects Dashboard v1.0 | Last updated: {}</p>
    <p>For questions or support, contact the development team</p>
    <p>
        <a href="https://github.com" target="_blank" style="color: #24292e; text-decoration: none; display: inline-flex; align-items: center; justify-content: center;">
            {github_logo} <span style="margin-left: 5px;">View on GitHub</span>
        </a>
    </p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

def show_requirements_message():
    # Requirements installation message (first run)
    if 'show_req_message' not in st.session_state:
        st.session_state.show_req_message = True
    
    if st.session_state.show_req_message:
        st.sidebar.markdown("---")
        st.sidebar.warning("""
        **First time running?**
        
        Make sure to install required packages:
        ```
        pip install streamlit pandas plotly fpdf
        ```
        """)
        if st.sidebar.button("I've installed the requirements"):
            st.session_state.show_req_message = False
            st.experimental_rerun()

# Add requirements message to the main function
def main():
    # Load saved GitHub repository links
    github_repos = load_github_repos()
    
    # Show requirements message
    show_requirements_message()
    

# End of the dashboard application

