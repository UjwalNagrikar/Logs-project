from flask import Flask, jsonify, request
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

app = Flask(__name__)

API_URL = "http://api:5000/search"  # Assuming the API service is running on this URL
API_BASE_URL = "http://localhost:5000/api"

# Configure Streamlit
st.set_page_config(
    page_title="LogX Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown(""" 
<style> 
    .main-header { 
        font-size: 3rem; 
        color: #1f77b4; 
        text-align: center; 
        margin-bottom: 2rem; 
    } 
    .metric-card { 
        background-color: #f0f2f6; 
        padding: 1rem; 
        border-radius: 10px; 
        margin: 0.5rem; 
    } 
    .error-log { 
        background-color: #ffebee; 
        border-left: 4px solid #f44336; 
        padding: 10px; 
        margin: 5px 0; 
    } 
    .warning-log { 
        background-color: #fff3e0; 
        border-left: 4px solid #ff9800; 
        padding: 10px; 
        margin: 5px 0; 
    } 
    .info-log { 
        background-color: #e8f5e8; 
        border-left: 4px solid #4caf50; 
        padding: 10px; 
        margin: 5px 0; 
    } 
</style> 
""", unsafe_allow_html=True)

def fetch_data(endpoint: str, params: dict = None) -> dict:
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return {}

def format_log_entry(log: dict) -> str:
    """Format log entry for display"""
    timestamp = log.get('_source', {}).get('timestamp', '')
    level = log.get('_source', {}).get('level', 'INFO')
    message = log.get('_source', {}).get('message', '')
    source = log.get('_source', {}).get('source', '')
    
    return f"**{timestamp}** [{level}] {source}: {message}"

def get_log_style_class(level: str) -> str:
    """Get CSS class for log level"""
    if level == 'ERROR':
        return 'error-log'
    elif level == 'WARNING':
        return 'warning-log'
    else:
        return 'info-log'

# Main Dashboard
def main():
    st.markdown('<h1 class="main-header">📊 LogX Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Time range selector
        time_range = st.selectbox(
            "Time Range",
            ["Last 1 Hour", "Last 24 Hours", "Last 7 Days", "Custom"]
        )
        
        if time_range == "Custom":
            start_date = st.date_input("Start Date")
            start_time = st.time_input("Start Time")
            end_date = st.date_input("End Date")
            end_time = st.time_input("End Time")
            
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
        else:
            end_datetime = datetime.now()
            if time_range == "Last 1 Hour":
                start_datetime = end_datetime - timedelta(hours=1)
            elif time_range == "Last 24 Hours":
                start_datetime = end_datetime - timedelta(hours=24)
            elif time_range == "Last 7 Days":
                start_datetime = end_datetime - timedelta(days=7)
        
        # Other filters
        log_level = st.selectbox(
            "Log Level",
            ["All", "ERROR", "WARNING", "INFO", "DEBUG"]
        )
        
        source_filter = st.text_input("Source Filter")
        search_query = st.text_input("Search Query")
        
        # Apply filters button
        apply_filters = st.button("🔄 Apply Filters")
    
    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch statistics
    stats = fetch_data("stats")
    
    with col1:
        total_logs = stats.get('total_logs', 0)
        st.metric("📊 Total Logs", f"{total_logs:,}")
    
    with col2:
        error_logs = stats.get('error_logs', 0)
        st.metric("🚨 Error Logs", f"{error_logs:,}")
    
    with col3:
        warning_logs = stats.get('warning_logs', 0)
        st.metric("⚠️ Warning Logs", f"{warning_logs:,}")
    
    with col4:
        sources = len(stats.get('sources', []))
        st.metric("🔗 Active Sources", sources)
    
    # Charts section
    st.header("📈 Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Log Timeline")
        
        if 'timeline' in stats and stats['timeline']:
            timeline_df = pd.DataFrame(stats['timeline'])
            timeline_df['time'] = pd.to_datetime(timeline_df['time'])
            
            fig = px.line(
                timeline_df, 
                x='time', 
                y='count',
                title='Logs Over Time',
                labels={'count': 'Number of Logs', 'time': 'Time'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timeline data available")
    
    with chart_col2:
        st.subheader("Sources Distribution")
        
        if 'sources' in stats and stats['sources']:
            sources_df = pd.DataFrame(stats['sources'])
            
            fig = px.pie(
                sources_df,
                values='count',
                names='name',
                title='Log Sources Distribution'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No source data available")
    
    # Log Level Distribution
    st.subheader("Log Level Distribution")
    
    level_data = {
        'ERROR': error_logs,
        'WARNING': warning_logs,
        'INFO': total_logs - error_logs - warning_logs
    }
    
    level_df = pd.DataFrame(list(level_data.items()), columns=['Level', 'Count'])
    
    fig = px.bar(
        level_df,
        x='Level',
        y='Count',
        title='Log Levels Distribution',
        color='Level',
        color_discrete_map={
            'ERROR': '#f44336',
            'WARNING': '#ff9800',
            'INFO': '#4caf50'
        }
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Logs Section
    st.header("📋 Recent Logs")
    
    # Build search parameters
    search_params = {
        'start_time': start_datetime.isoformat(),
        'end_time': end_datetime.isoformat(),
        'limit': 50
    }
    
    if search_query:
        search_params['q'] = search_query
    
    if log_level != "All":
        search_params['level'] = log_level
    
    if source_filter:
        search_params['source'] = source_filter
    
    # Fetch logs
    logs_data = fetch_data("search", search_params)
    
    if 'hits' in logs_data and logs_data['hits']['hits']:
        logs = logs_data['hits']['hits']
        
        # Display logs with styling
        for log in logs:
            log_level = log.get('_source', {}).get('level', 'INFO')
            log_class = get_log_style_class(log_level)
            formatted_log = format_log_entry(log)
            
            st.markdown(f'<div class="{log_class}">{formatted_log}</div>', unsafe_allow_html=True)
    else:
        st.info("No logs found for the selected filters")
    
    # Auto-refresh option
    if st.checkbox("🔄 Auto-refresh (30 seconds)"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()

@app.route('/logs', methods=['GET'])
def get_logs():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    response = requests.get(API_URL, params={'query': query})
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch logs from API"}), response.status_code

    logs = response.json()
    return jsonify(logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Run on port 5001 for the dashboard service