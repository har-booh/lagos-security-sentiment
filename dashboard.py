
"""
Lagos Security Sentiment Analysis - Streamlit Dashboard
Real-time monitoring dashboard for security sentiment across Lagos
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Lagos Security Sentiment Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE = "http://localhost:5000"

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .positive-sentiment {
        color: #10B981;
        font-weight: bold;
    }
    .neutral-sentiment {
        color: #F59E0B;
        font-weight: bold;
    }
    .negative-sentiment {
        color: #EF4444;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
@st.cache_data(ttl=30)
def fetch_current_sentiment():
    """Fetch current sentiment data"""
    try:
        response = requests.get(f"{API_BASE}/api/sentiment/current", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching sentiment: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_alerts():
    """Fetch active alerts"""
    try:
        response = requests.get(f"{API_BASE}/api/alerts/active", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching alerts: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_areas():
    """Fetch area analysis"""
    try:
        response = requests.get(f"{API_BASE}/api/areas", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching areas: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_trends():
    """Fetch weekly trends"""
    try:
        response = requests.get(f"{API_BASE}/api/trends/weekly", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching trends: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_sources():
    """Fetch source breakdown"""
    try:
        response = requests.get(f"{API_BASE}/api/sources", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching sources: {e}")
        return []

def get_sentiment_label(score):
    """Get sentiment label and color"""
    if score > 0.4:
        return "Positive 😊", "positive-sentiment", "#10B981"
    elif score > 0.1:
        return "Neutral 😐", "neutral-sentiment", "#F59E0B"
    else:
        return "Concerning 😟", "negative-sentiment", "#EF4444"

def create_gauge_chart(value, title):
    """Create a gauge chart for sentiment"""
    # Normalize value from -1,1 to 0,100 for display
    normalized_value = ((value + 1) / 2) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=normalized_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 50, 'increasing': {'color': "#10B981"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#3B82F6"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#FEE2E2'},
                {'range': [30, 55], 'color': '#FEF3C7'},
                {'range': [55, 100], 'color': '#D1FAE5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#333", 'family': "Arial"}
    )
    
    return fig

# Header
st.title("🛡️ Lagos Security Sentiment Monitor")
st.markdown("**Real-time security sentiment analysis across Lagos, Nigeria**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh interval (seconds)", 10, 120, 30)
    
    st.markdown("---")
    st.header("📊 About")
    st.info("""
    This dashboard monitors security-related sentiment across Lagos using:
    - Social media analysis
    - News monitoring
    - Government announcements
    - Community reports
    
    The system applies bias correction to provide accurate sentiment analysis.
    """)
    
    st.markdown("---")
    st.header("🔗 API Status")
    
    # Check API health
    try:
        health = requests.get(f"{API_BASE}/api/health", timeout=2)
        if health.status_code == 200:
            st.success("✅ API Online")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")
    
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Main Dashboard
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "🚨 Alerts", 
    "📍 Areas", 
    "📈 Trends", 
    "🔍 Sources"
])

# Tab 1: Overview
with tab1:
    # Fetch current data
    sentiment_data = fetch_current_sentiment()
    
    if sentiment_data:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sentiment_score = sentiment_data.get('overall_sentiment', 0)
            label, css_class, color = get_sentiment_label(sentiment_score)
            st.metric(
                "Overall Sentiment",
                label,
                f"{sentiment_score:.2f}",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Data Sources",
                f"{sentiment_data.get('total_sources', 0):,}",
                "posts analyzed"
            )
        
        with col3:
            st.metric(
                "Active Alerts",
                sentiment_data.get('active_alerts', 0),
                "monitoring"
            )
        
        with col4:
            confidence = sentiment_data.get('confidence', 0)
            st.metric(
                "Confidence",
                f"{confidence * 100:.0f}%",
                "reliability"
            )
        
        st.markdown("---")
        
        # Gauge charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                create_gauge_chart(
                    sentiment_data.get('overall_sentiment', 0),
                    "Bias-Adjusted Sentiment"
                ),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                create_gauge_chart(
                    sentiment_data.get('raw_sentiment', 0),
                    "Raw Sentiment (Before Correction)"
                ),
                use_container_width=True
            )
        
        # Last update
        last_update = sentiment_data.get('last_update')
        if last_update:
            st.caption(f"📅 Last updated: {last_update}")
        else:
            st.caption("📅 Waiting for data...")
        
        # Bias correction info
        with st.expander("ℹ️ About Bias Correction"):
            st.markdown("""
            **Why Bias Correction?**
            
            Social media and news sources naturally skew negative for security topics.
            Our system adjusts for this by:
            
            - **Twitter**: 30% negative bias reduction
            - **News Media**: 40% negative bias reduction
            - **Government**: 20% negative weight increase
            - **Facebook**: 20% negative bias reduction
            
            This provides a more accurate picture of actual security conditions.
            """)
    else:
        st.warning("⚠️ Unable to fetch sentiment data. Make sure the API is running.")
        st.code("python -m app.main", language="bash")

# Tab 2: Alerts
with tab2:
    st.header("🚨 Active Security Alerts")
    
    alerts = fetch_alerts()
    
    if alerts:
        for alert in alerts:
            severity = alert.get('severity', 'medium')
            
            # Determine alert color
            if severity == 'high':
                alert_type = "error"
                icon = "🔴"
            else:
                alert_type = "warning"
                icon = "🟡"
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### {icon} {alert.get('area', 'Unknown Area')}")
                    st.write(alert.get('message', 'No message'))
                    st.caption(
                        f"Confidence: {alert.get('confidence', 0) * 100:.0f}% • "
                        f"Time: {alert.get('time', 'N/A')} • "
                        f"Type: {alert.get('type', 'general')}"
                    )
                
                with col2:
                    st.markdown(f"**{severity.upper()}**")
                
                st.markdown("---")
    else:
        st.success("✅ No active alerts - All clear!")
        st.balloons()

# Tab 3: Areas
with tab3:
    st.header("📍 Lagos Area Analysis")
    
    areas = fetch_areas()
    
    if areas:
        # Create DataFrame
        df = pd.DataFrame(areas)
        
        # Sort by sentiment
        df = df.sort_values('sentiment', ascending=True)
        
        # Add sentiment label
        df['status'] = df['sentiment'].apply(lambda x: get_sentiment_label(x)[0])
        
        # Create bar chart
        fig = px.bar(
            df,
            x='sentiment',
            y='area',
            orientation='h',
            color='sentiment',
            color_continuous_scale=['red', 'yellow', 'green'],
            labels={'sentiment': 'Sentiment Score', 'area': 'Area'},
            title='Sentiment by Area'
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_range=[-1, 1]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Detailed Area Data")
        
        # Format the dataframe
        display_df = df[['area', 'sentiment', 'sources', 'confidence', 'status']].copy()
        display_df.columns = ['Area', 'Sentiment Score', 'Data Sources', 'Confidence', 'Status']
        display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x * 100:.0f}%")
        display_df['Sentiment Score'] = display_df['Sentiment Score'].apply(lambda x: f"{x:.3f}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No area data available yet. Data will appear after the first analysis cycle.")

# Tab 4: Trends
with tab4:
    st.header("📈 Weekly Sentiment Trends")
    
    trends = fetch_trends()
    
    if trends:
        df = pd.DataFrame(trends)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['sentiment'],
            mode='lines+markers',
            name='Adjusted Sentiment',
            line=dict(color='#3B82F6', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['raw_sentiment'],
            mode='lines+markers',
            name='Raw Sentiment',
            line=dict(color='#EF4444', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='Sentiment Over Time (7 Days)',
            xaxis_title='Date',
            yaxis_title='Sentiment Score',
            yaxis_range=[-1, 1],
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Incidents chart
        fig2 = px.bar(
            df,
            x='date',
            y='incidents',
            title='Daily Security Incidents',
            labels={'incidents': 'Number of Incidents', 'date': 'Date'}
        )
        
        fig2.update_layout(height=300)
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_sentiment = df['sentiment'].mean()
            st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
        
        with col2:
            total_incidents = df['incidents'].sum()
            st.metric("Total Incidents", f"{total_incidents}")
        
        with col3:
            trend_direction = "📈" if df['sentiment'].iloc[-1] > df['sentiment'].iloc[0] else "📉"
            st.metric("Trend", trend_direction)
    else:
        st.info("Trend data will be available after collecting data for several days.")

# Tab 5: Sources
with tab5:
    st.header("🔍 Data Source Breakdown")
    
    sources = fetch_sources()
    
    if sources:
        df = pd.DataFrame(sources)
        
        # Pie chart
        fig = px.pie(
            df,
            values='count',
            names='name',
            title='Data Distribution by Source',
            hole=0.4
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Source details
        st.subheader("Source Details")
        
        for _, source in df.iterrows():
            with st.expander(f"{source['name']} - {source['percentage']}%"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Posts", f"{source['count']:,}")
                
                with col2:
                    st.metric("Sentiment", f"{source['sentiment']:.2f}")
                
                with col3:
                    st.metric("Raw Sentiment", f"{source['raw_sentiment']:.2f}")
    else:
        st.info("Source data will be available after data collection begins.")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Lagos Security Sentiment Analysis System v1.0.0</p>
        <p>Making Lagos Safer Through Intelligent Monitoring 🇳🇬</p>
    </div>
    """,
    unsafe_allow_html=True
)
