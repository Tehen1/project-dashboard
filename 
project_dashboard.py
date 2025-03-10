css = """
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
    # Add info about GitHub integration
    st.sidebar.info("**GitHub Integration Features:**\n"
                  "- Link projects to their GitHub repositories\n"
                  "- Track project progress with GitHub issues\n"
                  "- Get notifications for repository updates")
    st.markdown(
        "> **Data Source**: This dashboard requires at least one CSV file with project data.\n"
        "> The preferred data source is \"Projects - full.csv\" which should be kept in the repository.\n"
        "> Other CSV files are optional and may be excluded from version control."
    )
        metric_html = "<div class='metric-card'>"
        metric_html += "<div class='metric-title'>Active Projects</div>"
        metric_html += f"<div class='metric-value-active'>{active_projects}</div>"
        metric_html += "</div>"
        st.markdown(metric_html, unsafe_allow_html=True)
    with col2:
        metric_html = "<div class='metric-card'>"
        metric_html += "<div class='metric-title'>Total Projects</div>"
        metric_html += f"<div class='metric-value-total'>{total_projects}</div>"
        metric_html += "</div>"
        st.markdown(metric_html, unsafe_allow_html=True)
    with col3:
        metric_html = "<div class='metric-card'>"
        metric_html += "<div class='metric-title'>High Priority</div>"
        metric_html += f"<div class='metric-value-priority'>{high_priority}</div>"
        metric_html += "</div>"
        st.markdown(metric_html, unsafe_allow_html=True)
    with col4:
        metric_html = "<div class='metric-card'>"
        metric_html += "<div class='metric-title'>Categories</div>"
        metric_html += f"<div class='metric-value-category'>{unique_categories}</div>"
        metric_html += "</div>"
        st.markdown(metric_html, unsafe_allow_html=True)
                    # Add GitHub styled repository link
                    github_html = "<div style='margin-top: 15px; margin-bottom: 15px;'>"
                    github_html += f"{github_button(repo_url, 'View on GitHub')}"
                    github_html += "</div>"
                    st.markdown(github_html, unsafe_allow_html=True)
                        github_stats_html = "<div style='background-color: #f6f8fa; padding: 10px; border-radius: 6px; margin-top: 10px;'>"
                        github_stats_html += "<div style='display: flex; gap: 15px;'>"
                        github_stats_html += "<div><strong>Stars:</strong> N/A</div>"
                        github_stats_html += "<div><strong>Forks:</strong> N/A</div>"
                        github_stats_html += "<div><strong>Open Issues:</strong> N/A</div>"
                        github_stats_html += "</div></div>"
                        st.markdown(github_stats_html, unsafe_allow_html=True)
