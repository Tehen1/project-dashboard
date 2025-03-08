# Project Dashboard

This dashboard provides an overview of all projects and their details.

## Data Requirements

The dashboard requires CSV data files to function properly:

- **Required**: `Projects - full.csv` - The main data file containing project information
- **Optional**: Other CSV files can be used as fallbacks but are not necessary

## CSV File Management

- Only the main `Projects - full.csv` file should be committed to Git
- Other CSV files are excluded via `.gitignore` to keep the repository clean

## Running the Dashboard

1. Create a virtual environment:
   ```bash
   python3 -m venv project_dashboard_env
   ```

2. Activate the virtual environment:
   ```bash
   source project_dashboard_env/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install streamlit pandas plotly fpdf watchdog
   ```

4. Run the dashboard:
   ```bash
   streamlit run project_dashboard.py
   ```

## Features

- Overview statistics
- Data visualizations
- Project filtering 
- Timeline view
- Project details
- Notifications system
- GitHub integration
- PDF export functionality

