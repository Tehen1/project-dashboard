import re

# Read the original file
with open('project_dashboard.py', 'r') as file:
    content = file.read()

# 1. Add merge_duplicate_projects function after load_data
load_data_pattern = r'def load_data\(\):.*?return df'
load_data_code = re.search(load_data_pattern, content, re.DOTALL).group(0)

merge_duplicate_code = '''
@st.cache_data
def merge_duplicate_projects(df):
    # Identifie les doublons basés sur le nom du projet
    duplicates = df['Project Name'].duplicated(keep=False)
    unique_df = df[~duplicates].copy()
    
    # Traite les projets en doublon
    duplicate_names = df.loc[duplicates, 'Project Name'].unique()
    
    for name in duplicate_names:
        # Sélectionne toutes les occurrences de ce projet
        project_rows = df[df['Project Name'] == name]
        
        # Crée une nouvelle ligne en fusionnant les informations
        merged_row = project_rows.iloc[0].copy()
        
        # Pour chaque colonne, prend la valeur non vide la plus détaillée
        for col in df.columns:
            if col != 'Project Name' and col != 'Unnamed: 0':
                # Valeurs uniques non-vides pour cette colonne
                values = [val for val in project_rows[col].unique() if pd.notna(val) and val != '']
                
                if len(values) > 0:
                    # S'il y a plusieurs valeurs, prendre la plus longue (probablement la plus détaillée)
                    merged_row[col] = max(values, key=lambda x: len(str(x)) if isinstance(x, str) else 0)
        
        # Ajouter cette ligne fusionnée aux résultats
        unique_df = pd.concat([unique_df, pd.DataFrame([merged_row])], ignore_index=True)
    
    return unique_df'''

# Insert function after load_data
modified_content = content.replace(load_data_code, load_data_code + merge_duplicate_code)

# 2. Call merge_duplicate_projects after df = load_data()
load_data_call_pattern = r'df = load_data\(\)'
modified_content = modified_content.replace('df = load_data()', 'df = load_data()\n    # Merge duplicate projects\n    df = merge_duplicate_projects(df)')

# 3. Improve CSS for responsiveness
css_pattern = r'st\.markdown\(\s*"<style>".*?"</style>",\s*unsafe_allow_html=True\s*\)'
css_code = re.search(css_pattern, modified_content, re.DOTALL).group(0)

additional_css = '''
"    @media (max-width: 768px) {" +
"        .metric-card {" +
"            margin-bottom: 15px;" +
"        }" +
"        .project-card {" +
"            padding: 15px;" +
"        }" +
"    }" +
"    .chart-container {" +
"        background-color: white;" + 
"        border-radius: 5px;" +
"        padding: 15px;" +
"        box-shadow: 0 2px 5px rgba(0,0,0,0.05);" +
"        margin-bottom: 20px;" +
"    }" +'''

# Add responsive CSS
modified_css = css_code.replace('"</style>"', additional_css + '\n    "</style>"')
modified_content = modified_content.replace(css_code, modified_css)

# 4. Update timeline visualization for better readability
timeline_layout_pattern = r'fig\.update_layout\(\s*title=\'Project Timeline \(Gantt Chart\)\'.*?\)'
timeline_layout_code = re.search(timeline_layout_pattern, modified_content, re.DOTALL).group(0)

new_timeline_layout = '''fig.update_layout(
            title='Project Timeline (Gantt Chart)',
            height=max(500, min(len(timeline_df) * 20, 1000)),  # Hauteur limitée entre 500 et 1000px
            margin=dict(l=20, r=20, t=60, b=30),  # Marges plus grandes
            plot_bgcolor='rgba(250, 250, 250, 0.9)',  # Fond légèrement grisé pour meilleur contraste
            yaxis=dict(
                autorange="reversed",  # Reverses the y-axis so newest projects are at top
                title='',
                tickangle=-30,  # Angle des noms de projets pour éviter le chevauchement
                tickfont=dict(size=11),  # Smaller font for project names
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
        )'''

modified_content = modified_content.replace(timeline_layout_code, new_timeline_layout)

# 5. Wrap charts in container for better styling - fixed syntax error
replacement_chart_code = """st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
      st.plotly_chart(fig, use_container_width=True)
      st.markdown("</div>", unsafe_allow_html=True)"""

modified_content = modified_content.replace(
    'st.plotly_chart(fig, use_container_width=True)',
    replacement_chart_code
)

# 6. Reformat project card display
project_card_pattern = r'st\.markdown\(f"<h3>{project_name} <span class=\'{status_class}\'>{project_status}</span></h3>", unsafe_allow_html=True\)'
new_project_card = '''st.markdown(
            f"""
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <h3 style='margin: 0;'>{project_name}</h3>
                <span class='{status_class}'>{project_status}</span>
            </div>
            
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px;'>
                <div>
                    <p><strong>Category:</strong> {row.get('Category', 'N/A')}</p>
                    <p><strong>Tech Stack:</strong> {row.get('Tech Stack', 'N/A')}</p>
                    <p><strong>Last Updated:</strong> {row.get('Last Updated', 'N/A')}</p>
                </div>
                <div>
                    <p><strong>Priority:</strong> <span class='{priority_class if "Priority" in row and not pd.isna(row["Priority"]) else ""}'>{row.get('Priority', 'N/A')}</span></p>
                    <p><strong>Documentation:</strong> {row.get('Documentation Status', 'N/A')}</p>
                </div>
            </div>
            
            {f"<p><strong>Description:</strong> {row.get('Résumé_Détaillé', '')}</p>" if 'Résumé_Détaillé' in row and not pd.isna(row['Résumé_Détaillé']) else ""}
            """, 
            unsafe_allow_html=True
        )'''

modified_content = modified_content.replace(project_card_pattern, new_project_card)

# Write the modified file
with open('project_dashboard.py', 'w') as file:
    file.write(modified_content)

print("Dashboard update script completed!")
