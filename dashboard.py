import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ──
st.set_page_config(
    page_title="Global AI Index Dashboard (2015-2026)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load Data ──
@st.cache_data
def load_data():
    df = pd.read_csv("ai_index_cleaned.csv")
    return df

df = load_data()

# ── Colorblind-safe palette ──
CB_COLORS = ['#0077BB', '#33BBEE', '#009988', '#EE6677', '#CC3311',
             '#EE7733', '#BBBBBB', '#AA3377', '#66CCEE', '#228833',
             '#DDCC77', '#882255', '#44AA99', '#999933', '#AA4499',
             '#332288', '#117733', '#88CCEE', '#CC6677', '#DDDDDD']

REGION_COLORS = {
    'North America': '#0077BB',
    'Europe': '#33BBEE',
    'Asia': '#009988',
    'South America': '#EE6677',
    'Africa': '#EE7733'
}

# ── Sidebar Filters ──
st.sidebar.title("Filters")

# Year filter
years = sorted(df['year'].unique())
year_range = st.sidebar.slider(
    "Year Range",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

# Region filter
regions = sorted(df['region'].unique())
selected_regions = st.sidebar.multiselect(
    "Regions", regions, default=regions
)

# Country filter
available_countries = sorted(df[df['region'].isin(selected_regions)]['country'].unique())
selected_countries = st.sidebar.multiselect(
    "Countries", available_countries, default=available_countries
)

# Apply filters
mask = (
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1]) &
    (df['region'].isin(selected_regions)) &
    (df['country'].isin(selected_countries))
)
filtered = df[mask].copy()

# ── Navigation ──
page = st.sidebar.radio("Dashboard Page", ["Overview", "Country Deep Dive", "Comparison"])

# =====================================================================
# PAGE 1: OVERVIEW
# =====================================================================
if page == "Overview":
    st.title("Global AI Index — Overview (2015-2026)")
    st.markdown("Tracking AI readiness and rankings across 20 countries over a decade.")

    # KPI Cards
    latest_year = filtered['year'].max()
    df_latest = filtered[filtered['year'] == latest_year]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg AI Score", f"{df_latest['ai_index_score'].mean():.1f}")
    with col2:
        st.metric("Total Investment", f"${df_latest['ai_investment_billion_usd'].sum():.1f}B")
    with col3:
        st.metric("Countries", f"{df_latest['country'].nunique()}")
    with col4:
        st.metric("Avg Readiness", f"{df_latest['ai_readiness_score'].mean():.1f}")

    st.markdown("---")

    # Choropleth Map
    st.subheader(f"AI Index Score by Country ({latest_year})")
    fig_map = px.choropleth(
        df_latest,
        locations='iso_code',
        color='ai_index_score',
        hover_name='country',
        hover_data={'ai_global_rank': True, 'ai_readiness_score': ':.1f', 'iso_code': False},
        color_continuous_scale='Viridis',
        range_color=[df_latest['ai_index_score'].min() - 5, df_latest['ai_index_score'].max() + 2],
        labels={'ai_index_score': 'AI Index Score'}
    )
    fig_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor='lightgray',
                 projection_type='natural earth', bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=10, b=0),
        height=450
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Two columns: Bar Chart + Line Chart
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"Top 10 Countries ({latest_year})")
        top10 = df_latest.nlargest(10, 'ai_index_score').sort_values('ai_index_score')
        fig_bar = px.bar(
            top10, x='ai_index_score', y='country', orientation='h',
            color='region', color_discrete_map=REGION_COLORS,
            hover_data={'ai_global_rank': True},
            labels={'ai_index_score': 'AI Index Score', 'country': ''}
        )
        fig_bar.update_layout(
            height=400, margin=dict(l=0, r=20, t=10, b=0),
            showlegend=True, legend=dict(orientation='h', y=-0.15),
            plot_bgcolor='white',
            xaxis=dict(gridcolor='#f0f0f0'),
            yaxis=dict(gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("AI Score Trends Over Time")
        fig_line = px.line(
            filtered.sort_values(['country', 'year']),
            x='year', y='ai_index_score', color='country',
            hover_data={'region': True, 'ai_global_rank': True},
            labels={'ai_index_score': 'AI Index Score', 'year': 'Year'},
            color_discrete_sequence=CB_COLORS
        )
        fig_line.update_layout(
            height=400, margin=dict(l=0, r=20, t=10, b=0),
            plot_bgcolor='white',
            xaxis=dict(gridcolor='#f0f0f0', dtick=1),
            yaxis=dict(gridcolor='#f0f0f0'),
            hovermode='x unified',
            legend=dict(font=dict(size=9))
        )
        fig_line.update_traces(line_width=2)
        st.plotly_chart(fig_line, use_container_width=True)

    # Regional Averages
    st.subheader("Regional Average AI Index Score Over Time")
    regional = filtered.groupby(['year', 'region'])['ai_index_score'].mean().reset_index()
    fig_area = px.area(
        regional.sort_values('year'), x='year', y='ai_index_score',
        color='region', color_discrete_map=REGION_COLORS,
        labels={'ai_index_score': 'Avg AI Index Score', 'year': 'Year', 'region': 'Region'}
    )
    fig_area.update_layout(
        height=350, margin=dict(l=0, r=20, t=10, b=0),
        plot_bgcolor='white',
        xaxis=dict(gridcolor='#f0f0f0', dtick=1),
        yaxis=dict(gridcolor='#f0f0f0')
    )
    st.plotly_chart(fig_area, use_container_width=True)


# =====================================================================
# PAGE 2: COUNTRY DEEP DIVE
# =====================================================================
elif page == "Country Deep Dive":
    st.title("Country Deep Dive")

    # Country selector
    country = st.selectbox("Select a Country", sorted(filtered['country'].unique()), index=0)
    df_country = filtered[filtered['country'] == country].sort_values('year')
    latest = df_country[df_country['year'] == df_country['year'].max()].iloc[0]

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("AI Index Score", f"{latest['ai_index_score']:.1f}")
    with col2:
        st.metric("Global Rank", f"#{int(latest['ai_global_rank'])}")
    with col3:
        st.metric("AI Investment", f"${latest['ai_investment_billion_usd']:.1f}B")
    with col4:
        st.metric("AI Startups", f"{int(latest['ai_startups_count']):,}")

    st.markdown("---")

    # Radar Chart - Key Dimensions
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"Dimension Profile ({int(latest['year'])})")
        dimensions = {
            'Consumer Adoption': 'ai_adoption_consumer',
            'Enterprise Adoption': 'ai_adoption_enterprise',
            'Cloud Infrastructure': 'cloud_infrastructure',
            'AI Policy': 'ai_policy_score',
            'Data Availability': 'data_availability',
            'Internet Penetration': 'internet_penetration',
            'GPU Availability': 'gpu_availability_index'
        }

        # Normalize against all countries for that year
        df_year = df[df['year'] == latest['year']]
        values = []
        for label, col_name in dimensions.items():
            col_min = df_year[col_name].min()
            col_max = df_year[col_name].max()
            val = (latest[col_name] - col_min) / (col_max - col_min) * 100 if col_max > col_min else 50
            values.append(val)

        categories = list(dimensions.keys())
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(0,119,187,0.15)',
            line=dict(color='#0077BB', width=2),
            name=country
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 105])),
            height=400, margin=dict(l=40, r=40, t=20, b=40),
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_right:
        st.subheader("Score Trend Over Time")
        fig_trend = px.area(
            df_country, x='year', y='ai_index_score',
            labels={'ai_index_score': 'AI Index Score', 'year': 'Year'},
            color_discrete_sequence=['#0077BB']
        )
        fig_trend.update_layout(
            height=400, margin=dict(l=0, r=20, t=10, b=0),
            plot_bgcolor='white',
            xaxis=dict(gridcolor='#f0f0f0', dtick=1),
            yaxis=dict(gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # Gauge Charts Row
    st.subheader("Key Metrics")
    gauge_metrics = [
        ("Consumer Adoption", latest['ai_adoption_consumer']),
        ("Enterprise Adoption", latest['ai_adoption_enterprise']),
        ("AI Readiness", latest['ai_readiness_score']),
        ("AI Policy Score", latest['ai_policy_score']),
        ("Regulation Score", latest['ai_regulation_score'])
    ]
    gauge_cols = st.columns(5)
    for i, (name, value) in enumerate(gauge_metrics):
        with gauge_cols[i]:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': name, 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': '#0077BB'},
                    'steps': [
                        {'range': [0, 40], 'color': '#fee0d2'},
                        {'range': [40, 70], 'color': '#fcbba1'},
                        {'range': [70, 100], 'color': '#deebf7'}
                    ]
                },
                number={'font': {'size': 22}}
            ))
            fig_g.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=10))
            st.plotly_chart(fig_g, use_container_width=True)

    # Detail Table
    st.subheader("Yearly Data")
    display_cols = ['year', 'ai_index_score', 'ai_global_rank', 'ai_investment_billion_usd',
                    'ai_research_papers', 'ai_startups_count', 'ai_readiness_score',
                    'gdp_per_capita']
    st.dataframe(
        df_country[display_cols].sort_values('year', ascending=False).reset_index(drop=True),
        use_container_width=True, hide_index=True
    )


# =====================================================================
# PAGE 3: COMPARISON
# =====================================================================
elif page == "Comparison":
    st.title("Country Comparison")

    # Multi-select for comparison
    default_compare = [c for c in ['USA', 'China', 'Germany', 'UK', 'Japan'] if c in filtered['country'].unique()]
    compare_countries = st.multiselect(
        "Select countries to compare",
        sorted(filtered['country'].unique()),
        default=default_compare[:5]
    )

    if len(compare_countries) < 2:
        st.warning("Please select at least 2 countries to compare.")
    else:
        df_compare = filtered[filtered['country'].isin(compare_countries)]
        latest_year = df_compare['year'].max()
        df_comp_latest = df_compare[df_compare['year'] == latest_year]

        # Side-by-side Bar Chart
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader(f"AI Index Score ({latest_year})")
            fig_comp_bar = px.bar(
                df_comp_latest.sort_values('ai_index_score'),
                x='ai_index_score', y='country', orientation='h',
                color='country', color_discrete_sequence=CB_COLORS,
                labels={'ai_index_score': 'AI Index Score', 'country': ''}
            )
            fig_comp_bar.update_layout(
                height=350, margin=dict(l=0, r=20, t=10, b=0),
                showlegend=False, plot_bgcolor='white',
                xaxis=dict(gridcolor='#f0f0f0'),
                yaxis=dict(gridcolor='#f0f0f0')
            )
            st.plotly_chart(fig_comp_bar, use_container_width=True)

        with col_right:
            st.subheader("Score Trends Over Time")
            fig_comp_line = px.line(
                df_compare.sort_values(['country', 'year']),
                x='year', y='ai_index_score', color='country',
                labels={'ai_index_score': 'AI Index Score', 'year': 'Year'},
                color_discrete_sequence=CB_COLORS
            )
            fig_comp_line.update_layout(
                height=350, margin=dict(l=0, r=20, t=10, b=0),
                plot_bgcolor='white',
                xaxis=dict(gridcolor='#f0f0f0', dtick=1),
                yaxis=dict(gridcolor='#f0f0f0')
            )
            fig_comp_line.update_traces(line_width=2.5)
            st.plotly_chart(fig_comp_line, use_container_width=True)

        # Scatter Plot: GDP vs AI Score
        st.subheader(f"GDP per Capita vs AI Index Score ({latest_year})")
        fig_scatter = px.scatter(
            df_comp_latest,
            x='gdp_per_capita', y='ai_index_score',
            size='ai_investment_billion_usd', color='country',
            hover_name='country',
            hover_data={'ai_global_rank': True, 'region': True, 'gdp_per_capita': ':,.0f'},
            size_max=50,
            labels={
                'gdp_per_capita': 'GDP per Capita (USD)',
                'ai_index_score': 'AI Index Score',
                'ai_investment_billion_usd': 'AI Investment ($B)'
            },
            color_discrete_sequence=CB_COLORS
        )
        fig_scatter.update_layout(
            height=450, margin=dict(l=0, r=20, t=10, b=0),
            plot_bgcolor='white',
            xaxis=dict(gridcolor='#f0f0f0'),
            yaxis=dict(gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Radar Comparison
        st.subheader(f"Dimension Comparison ({latest_year})")
        dimensions = {
            'Consumer Adoption': 'ai_adoption_consumer',
            'Enterprise Adoption': 'ai_adoption_enterprise',
            'Cloud Infrastructure': 'cloud_infrastructure',
            'AI Policy': 'ai_policy_score',
            'Data Availability': 'data_availability',
            'Research Papers': 'ai_research_papers',
            'GPU Availability': 'gpu_availability_index'
        }
        df_year_all = df[df['year'] == latest_year]
        fig_radar_comp = go.Figure()
        categories = list(dimensions.keys())

        for i, c in enumerate(compare_countries):
            row = df_comp_latest[df_comp_latest['country'] == c].iloc[0]
            values = []
            for label, col_name in dimensions.items():
                col_min = df_year_all[col_name].min()
                col_max = df_year_all[col_name].max()
                val = (row[col_name] - col_min) / (col_max - col_min) * 100 if col_max > col_min else 50
                values.append(val)
            fig_radar_comp.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=c,
                line=dict(color=CB_COLORS[i % len(CB_COLORS)], width=2),
                opacity=0.7
            ))

        fig_radar_comp.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 105])),
            height=500, margin=dict(l=60, r=60, t=20, b=40)
        )
        st.plotly_chart(fig_radar_comp, use_container_width=True)

        # Comparison Matrix
        st.subheader("Detailed Comparison")
        compare_cols = ['country', 'ai_index_score', 'ai_global_rank', 'ai_readiness_score',
                        'ai_investment_billion_usd', 'ai_startups_count', 'ai_research_papers',
                        'gdp_per_capita', 'ai_adoption_consumer', 'ai_adoption_enterprise']
        st.dataframe(
            df_comp_latest[compare_cols].sort_values('ai_index_score', ascending=False).reset_index(drop=True),
            use_container_width=True, hide_index=True
        )

# ── Footer ──
st.sidebar.markdown("---")
st.sidebar.caption("Data: Global AI Index (2015-2026) | Kaggle")
st.sidebar.caption("Built with Streamlit & Plotly")
