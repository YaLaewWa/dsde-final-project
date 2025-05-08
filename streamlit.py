# streamlit_pydeck_demo.py

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import json

# with open("subdistricts.geojson", encoding="utf-8") as f:
#     geojson_data = json.load(f)

# Function to load data
@st.cache_data
def load_data():
    df = pd.read_csv("data\mock3kRows.csv", index_col=0)
    df['longitude'] = [float(i.split(',')[0]) for i in df['coords']]
    df['latitude'] = [float(i.split(',')[1]) for i in df['coords']]
    df = df.drop(columns=['coords'])
    return df

df = load_data()

problem_types = ['น้ำท่วม', 'ร้องเรียน', 'ความสะอาด', 'ท่อระบายน้ำ', 'ถนน', 'คลอง',
       'ทางเท้า', 'เสียงรบกวน', 'สะพาน', 'สายไฟ', 'กีดขวาง', 'แสงสว่าง',
       'สัตว์จรจัด', 'ต้นไม้', 'ความปลอดภัย', 'จราจร', 'การเดินทาง',
       'เสนอแนะ', 'คนจรจัด', 'ห้องน้ำ', 'ป้ายจราจร', 'สอบถาม', 'ป้าย',
       'PM2.5']

# viz

# Sidebar controls
# map_layer_type = st.sidebar.radio('Map Type', ["ScatterplotLayer", "HeatmapLayer"])

map_style = st.sidebar.radio(
    "Map Style",
    ["dark", "light", "streets", "satellite"]
)
map_style = "mapbox://styles/mapbox/" + map_style + "-v9"

view_state = pdk.ViewState(
                longitude=df['longitude'].mean(),
                latitude=df['latitude'].mean(),
                zoom=9
            )

severity_color_mapping = {
    "Very Low": [161, 161, 161, 150],   # Gray
    "Low": [255, 255, 255, 150],        # White (previous Very Low)
    "Medium": [255, 235, 59, 150],      # Yellow (previous Low)
    "High": [255, 152, 0, 150],         # Orange (previous Medium)
    "Very High": [244, 67, 54, 200]     # Red (previous High)
}

severity_color_mapping_hex = {
    "Very Low": "#a1a1a1",    # Gray with 150 alpha (96 in hex)
    "Low": "#ffffff",         # White with 150 alpha
    "Medium": "#ffeb3b",      # Yellow with 150 alpha
    "High": "#ff9800",        # Orange with 150 alpha
    "Very High": "#f44336"    # Red with 200 alpha (C8 in hex)
}

severity_radius_mapping = {
    "Very Low": 200,      # Base radius (200)
    "Low": 300,          # 200 * 1.5
    "Medium": 450,       # 300 * 1.5
    "High": 675,         # 450 * 1.5
    "Very High": 1012    # 675 * 1.5 (rounded to nearest integer)
}

# Main app
def plot():
    st.title('Bangkok problems visualization (old)')
    st.write('### Map')
    prob_dict = {}
    if 'prob_dict' not in st.session_state:
        prob_dict = {i:True for i in problem_types}
        st.session_state.prob_dict = prob_dict
    else:
        prob_dict = st.session_state.prob_dict

    with st.popover("Select the problems"):
        prob_dict = st.session_state.prob_dict
        if st.button('Select all'):
            for i in problem_types:
                st.session_state[i] = True
            prob_dict = {i:True for i in problem_types}
            st.session_state.prob_dict = prob_dict
        if st.button('Unselect all'):
            for i in problem_types:
                st.session_state[i] = False
            prob_dict = {i:False for i in problem_types}
            st.session_state.prob_dict = prob_dict
        col1, col2, col3 = st.columns(3)
        with col1:
            for i in problem_types[:8]:
                prob_dict[i] = st.checkbox(i, key=i, value=prob_dict[i])
            st.session_state.prob_dict = prob_dict

        with col2:
            for i in problem_types[8:16]:
                prob_dict[i] = st.checkbox(i, key=i, value=prob_dict[i])
            st.session_state.prob_dict = prob_dict

        with col3:
            for i in problem_types[16:]:
                prob_dict[i] = st.checkbox(i, key=i, value=prob_dict[i])
            st.session_state.prob_dict = prob_dict

    chosen_type = set()
    for i in problem_types:
        if prob_dict[i]:
            chosen_type.add(i)
    type_str = ', '.join(list(chosen_type))
    st.write("**Selected type**: ", type_str)

    df['type'] = [i[1:-1].split(',') if type(i) == str else [] for i in df['type']]

    viz = df[[True if set(i) & chosen_type else False for i in df['type']]]
    viz['color'] = [severity_color_mapping[i] for i in viz['severity']]
    viz['radius'] = [severity_radius_mapping[i] for i in viz['severity']]
    viz['color_hex'] = [severity_color_mapping_hex[i] for i in viz['severity']]

    @st.cache_data
    def create_scatter(dataframe):
        layer = pdk.Layer(
            "ScatterplotLayer",
            dataframe,
            get_position=["longitude", "latitude"],
            get_radius='radius',
            get_color='color',
            pickable=True
        )

        tooltip = {
            "html": """
                <div style="border: 2px solid {color_hex}; border-radius: 10px; padding: 10px; background-color: #3d3d3d; width: 300px">
                    <div style="
                        display: -webkit-box;
                        -webkit-line-clamp: 3;
                        -webkit-box-orient: vertical;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    ">
                        <b>Description:</b> {comment}
                    </div>
                    <div>
                        <b>Type: </b>{type}
                    </div>
                    <div>
                        <b>Time to solve (days): </b>{time_to_solve}
                    </div>
                    <div>
                        <b>Severity: </b><span style="color: {color_hex}">{severity}</span>
                    </div>
                    <img src="{photo}" height="200" width="200" />
                </div>
            """,
            "style": {"color": "white", 'background-color': 'transparent'}
        }

        return pdk.Deck(layers=[layer], initial_view_state=view_state, map_style=map_style, tooltip=tooltip)

    @st.cache_data
    def create_heatmap(dataframe):
        layer = pdk.Layer(
            "HeatmapLayer",
            dataframe,
            get_position=["longitude", "latitude"],
            opacity=0.5,
            pickable=True
        )
        return pdk.Deck(layers=[layer], initial_view_state=view_state, map_style=map_style)

    # Display Map
    
    tab1, tab2 = st.tabs(["Scatter", "Heatmap"])
    scatter = create_scatter(viz)
    heatmap = create_heatmap(viz)
    if len(viz) != 0:
        tab1.pydeck_chart(scatter)
        tab2.pydeck_chart(heatmap)

def histogram():
    st.write('# Time to solve')
    fig = px.histogram(df, x="time_to_solve", labels={'time_to_solve': 'Time to solve (days)'})
    st.plotly_chart(fig)

    st.write('# Severity')
    fig = px.histogram(df, x="severity")
    st.plotly_chart(fig)

    def calculate_mean_ttl():
        ttl = df.groupby('severity').mean("time_to_solve")
        ttl = ttl.reset_index()
        sev = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
        ttl_list = []
        sev = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
        ttl_list = []
        for i in sev:
            if len(ttl[ttl['severity'] == i]) > 0:
                ttl_list.append(ttl[ttl['severity'] == i]['time_to_solve'].iloc[0])
            else:
                sev.remove(i)
                
        mean_ttl = pd.DataFrame({'Severity':sev, 'Mean time to solve (days)': ttl_list})
        return mean_ttl

    st.write('# Mean time to solve for each severity')
    mean_ttl = calculate_mean_ttl()
    fig = px.bar(mean_ttl, x='Severity', y='Mean time to solve (days)')
    st.plotly_chart(fig)

# def geojson():
#     polygon = pdk.Layer(
#         "GeoJsonLayer",
#         geojson_data,
#         opacity=0.8,
#         stroked=False,
#         filled=True,
#         extruded=True,
#         wireframe=True,
#         get_elevation="properties.valuePerSqm / 20",
#         get_fill_color="[255, 255, properties.growth * 255]",
#         get_line_color=[255, 255, 255],
#     )
#     map = pdk.Deck(layers=[polygon], initial_view_state=view_state, map_style=map_style)
#     st.pydeck_chart(map)


def main():
    page = st.sidebar.radio(
        "Choose page",
        ['Plot', 'Histogram', 'Geojson']
    )
    if page == 'Plot':
        plot()
    elif page == 'Histogram':
        histogram()
    # elif page == 'Geojson':
    #     geojson()


if __name__ == "__main__":
    main()