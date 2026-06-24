
"""
Pass'Tranquille - Application Web Streamlit
Dakar JOJ 2026 - Itineraire multimodal avec carte interactive

Lancement: streamlit run webapp.py
"""

import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
from datetime import datetime, time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend import PassTranquilleAPI, MODE_COLORS, MODE_NAMES, POI_CATEGORIES

# ============================================================
# CONFIGURATION PAGE
# ============================================================

st.set_page_config(
    page_title="Pass'Tranquille - Dakar JOJ 2026",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLES CSS
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    .main-header h1 { font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .main-header p { font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem; }

    .route-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .route-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
    .route-card.fastest { border-left-color: #27ae60; }
    .route-card.alternative { border-left-color: #f39c12; }

    .segment-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
        color: white;
    }
    .segment-badge .icon { margin-right: 0.4rem; font-size: 1rem; }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    .stat-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .stat-box .value { font-size: 1.5rem; font-weight: 700; color: #2c3e50; }
    .stat-box .label { font-size: 0.8rem; color: #7f8c8d; margin-top: 0.3rem; }

    .step-timeline {
        position: relative;
        padding-left: 2rem;
        margin: 1rem 0;
    }
    .step-timeline::before {
        content: '';
        position: absolute;
        left: 0.5rem;
        top: 0;
        bottom: 0;
        width: 3px;
        background: #e0e0e0;
    }
    .step-item {
        position: relative;
        padding: 0.8rem 0;
        padding-left: 1.5rem;
    }
    .step-item::before {
        content: '';
        position: absolute;
        left: -1.75rem;
        top: 1.2rem;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 0 0 3px;
    }
    .step-item.ter::before { background: #e74c3c; box-shadow: 0 0 0 3px #e74c3c; }
    .step-item.brt::before { background: #3498db; box-shadow: 0 0 0 3px #3498db; }
    .step-item.bus::before { background: #2ecc71; box-shadow: 0 0 0 3px #2ecc71; }
    .step-item.walk::before { background: #95a5a6; box-shadow: 0 0 0 3px #95a5a6; }

    .congestion-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .congestion-low { background: #d4edda; color: #155724; }
    .congestion-moderate { background: #fff3cd; color: #856404; }
    .congestion-high { background: #f8d7da; color: #721c24; }

    .joj-banner {
        background: linear-gradient(90deg, #ff6b6b, #feca57);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }

    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    .poi-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-left: 4px solid;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if 'api' not in st.session_state:
    st.session_state.api = PassTranquilleAPI()
    st.session_state.api.initialize()

if 'selected_route' not in st.session_state:
    st.session_state.selected_route = None

if 'routes_data' not in st.session_state:
    st.session_state.routes_data = None

if 'from_lat' not in st.session_state:
    st.session_state.from_lat = 14.6768
    st.session_state.from_lon = -17.4340
    st.session_state.to_lat = 14.7721
    st.session_state.to_lon = -17.3871

if 'click_mode' not in st.session_state:
    st.session_state.click_mode = None

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def get_mode_icon(mode):
    icons = {'TER': '🚆', 'BRT': '🚌', 'BUS': '🚍', 'WALK': '🚶'}
    return icons.get(mode, '📍')

def get_poi_icon(category):
    icons = {
        'site_jo': '⭐', 'hotel': '🏨', 'musee': '🏛️',
        'monument': '🏛️', 'transport': '⛵'
    }
    return icons.get(category, '📍')

def create_map(center_lat=14.72, center_lon=-17.47, zoom=12, routes_data=None, selected_route_idx=None):
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='CartoDB positron',
        attr='PassTranquille'
    )

    # Tuiles
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='Satellite', overlay=False, control=True
    ).add_to(m)
    folium.TileLayer(tiles='OpenStreetMap', name='OpenStreetMap', overlay=False, control=True).add_to(m)

    # === POINTS D'INTERET ===
    poi_data = st.session_state.api.get_poi_data()
    poi_groups = {}

    for cat_key, cat_info in POI_CATEGORIES.items():
        poi_groups[cat_key] = folium.FeatureGroup(name=f"{get_poi_icon(cat_key)} {cat_info['label']}", show=True)

    for feature in poi_data['features']:
        cat = feature['properties']['category']
        name = feature['properties']['Nom']
        lon, lat = feature['geometry']['coordinates']
        cat_info = POI_CATEGORIES.get(cat, POI_CATEGORIES['monument'])

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"<b>{get_poi_icon(cat)} {name}</b><br><span style='color:{cat_info['color']};font-weight:600;'>{cat_info['label']}</span>",
                max_width=250
            ),
            tooltip=f"{get_poi_icon(cat)} {name}",
            icon=folium.Icon(color=cat_info['marker_color'], icon=cat_info['icon'], prefix='fa')
        ).add_to(poi_groups[cat])

    for group in poi_groups.values():
        group.add_to(m)

    # === ARRETS DE TRANSPORT ===
    stops = st.session_state.api.get_all_stops()

    ter_stops = [s for s in stops if s['transport_type'] == 'TER']
    brt_stops = [s for s in stops if s['transport_type'] == 'BRT']
    bus_stops = [s for s in stops if s['transport_type'] == 'BUS']

    ter_group = folium.FeatureGroup(name='🚆 TER (13 arrets)', show=False)
    brt_group = folium.FeatureGroup(name='🚌 BRT (23 arrets)', show=False)
    bus_group = folium.FeatureGroup(name='🚍 BUS DDD (100 arrets)', show=False)

    for stop in ter_stops:
        folium.Marker(
            location=[float(stop['latitude']), float(stop['longitude'])],
            popup=folium.Popup(f"<b>🚆 {stop['name']}</b><br>Zone: {stop['zone']}", max_width=200),
            tooltip=stop['name'],
            icon=folium.Icon(color='red', icon='train', prefix='fa')
        ).add_to(ter_group)

    for stop in brt_stops:
        folium.Marker(
            location=[float(stop['latitude']), float(stop['longitude'])],
            popup=folium.Popup(f"<b>🚌 {stop['name']}</b><br>Zone: {stop['zone']}", max_width=200),
            tooltip=stop['name'],
            icon=folium.Icon(color='blue', icon='bus', prefix='fa')
        ).add_to(brt_group)

    for stop in bus_stops[:40]:
        folium.Marker(
            location=[float(stop['latitude']), float(stop['longitude'])],
            popup=folium.Popup(f"<b>🚍 {stop['name']}</b><br>Zone: {stop['zone']}", max_width=200),
            tooltip=stop['name'],
            icon=folium.Icon(color='green', icon='bus', prefix='fa')
        ).add_to(bus_group)

    ter_group.add_to(m)
    brt_group.add_to(m)
    bus_group.add_to(m)

    # === ITINERAIRE SELECTIONNE ===
    if routes_data and selected_route_idx is not None:
        route = routes_data[selected_route_idx]

        for step in route['steps']:
            color = step['color']
            weight = 5 if step['mode'] != 'WALK' else 3
            dash_array = None if step['mode'] != 'WALK' else '10, 10'

            folium.PolyLine(
                locations=[
                    [step['from']['lat'], step['from']['lon']],
                    [step['to']['lat'], step['to']['lon']]
                ],
                color=color, weight=weight, opacity=0.85, dash_array=dash_array,
                popup=f"{get_mode_icon(step['mode'])} {step['mode_name']}: {step['distance_formatted']}"
            ).add_to(m)

            folium.CircleMarker(
                location=[step['from']['lat'], step['from']['lon']],
                radius=6, color=color, fill=True, fillColor=color, fillOpacity=0.9
            ).add_to(m)

        if route['steps']:
            first_step = route['steps'][0]
            folium.Marker(
                location=[first_step['from']['lat'], first_step['from']['lon']],
                popup="📍 Depart",
                icon=folium.Icon(color='green', icon='play', prefix='fa')
            ).add_to(m)

            last_step = route['steps'][-1]
            folium.Marker(
                location=[last_step['to']['lat'], last_step['to']['lon']],
                popup="🏁 Destination",
                icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa')
            ).add_to(m)

    # === CONTROLE COUCHES ===
    folium.LayerControl(collapsed=False).add_to(m)

    plugins.LocateControl().add_to(m)
    plugins.MousePosition().add_to(m)

    return m

def render_step_timeline(route):
    st.markdown("### 📋 Detail du trajet")
    for i, step in enumerate(route['steps']):
        mode_class = step['mode'].lower()
        icon = get_mode_icon(step['mode'])
        wait_info = f'<span>⏳ Attente: {int(step["wait_time"]/60)}min</span>' if step.get('wait_time', 0) > 0 else ''

        st.markdown(f"""
        <div class="step-timeline">
            <div class="step-item {mode_class}">
                <div style="font-weight: 600; color: #2c3e50;">{icon} {step['mode_name']}</div>
                <div style="color: #7f8c8d; font-size: 0.9rem;">De <b>{step['from']['name']}</b> a <b>{step['to']['name']}</b></div>
                <div style="display: flex; gap: 1rem; margin-top: 0.3rem; font-size: 0.85rem;">
                    <span>📏 {step['distance_formatted']}</span>
                    <span>⏱️ {step['duration_formatted']}</span>
                    {wait_info}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #667eea; margin: 0;">🚌 Pass'Tranquille</h2>
        <p style="color: #7f8c8d; font-size: 0.9rem;">Dakar JOJ 2026</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # === MODE DE SAISIE ===
    input_mode = st.radio(
        "📍 Mode de saisie",
        ["Selectionner un arret", "Coordonnees manuelles", "Cliquer sur la carte"],
        index=0
    )

    st.markdown("---")

    # === DEPART ===
    st.subheader("🚀 Depart")

    if input_mode == "Cliquer sur la carte":
        st.info("👇 Activez le mode, puis cliquez sur la carte")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("📍 Choisir DEPART", use_container_width=True, 
                        type="primary" if st.session_state.click_mode == 'depart' else "secondary"):
                st.session_state.click_mode = 'depart'
                st.rerun()
        with col_d2:
            if st.button("🏁 Choisir DEST.", use_container_width=True,
                        type="primary" if st.session_state.click_mode == 'destination' else "secondary"):
                st.session_state.click_mode = 'destination'
                st.rerun()

        if st.session_state.click_mode == 'depart':
            st.warning("🖱️ Cliquez sur la carte pour le DEPART")
        elif st.session_state.click_mode == 'destination':
            st.warning("🖱️ Cliquez sur la carte pour la DESTINATION")

        from_lat = st.session_state.from_lat
        from_lon = st.session_state.from_lon
        st.code(f"DEPART: {from_lat:.6f}, {from_lon:.6f}", language=None)

    elif input_mode == "Coordonnees manuelles":
        col1, col2 = st.columns(2)
        with col1:
            from_lat = st.number_input("Lat", value=st.session_state.from_lat, format="%.6f", key="from_lat_manual")
        with col2:
            from_lon = st.number_input("Lon", value=st.session_state.from_lon, format="%.6f", key="from_lon_manual")
        st.session_state.from_lat = from_lat
        st.session_state.from_lon = from_lon
    else:
        stops = st.session_state.api.get_all_stops()
        stop_names = [s['name'] for s in stops]
        selected_from = st.selectbox("Arret de depart", stop_names, key="from_stop")
        from_stop = next(s for s in stops if s['name'] == selected_from)
        from_lat = float(from_stop['latitude'])
        from_lon = float(from_stop['longitude'])
        st.session_state.from_lat = from_lat
        st.session_state.from_lon = from_lon

    st.markdown("---")

    # === DESTINATION ===
    st.subheader("🏁 Destination")

    if input_mode == "Cliquer sur la carte":
        to_lat = st.session_state.to_lat
        to_lon = st.session_state.to_lon
        st.code(f"DEST: {to_lat:.6f}, {to_lon:.6f}", language=None)

    elif input_mode == "Coordonnees manuelles":
        col1, col2 = st.columns(2)
        with col1:
            to_lat = st.number_input("Lat", value=st.session_state.to_lat, format="%.6f", key="to_lat_manual")
        with col2:
            to_lon = st.number_input("Lon", value=st.session_state.to_lon, format="%.6f", key="to_lon_manual")
        st.session_state.to_lat = to_lat
        st.session_state.to_lon = to_lon
    else:
        selected_to = st.selectbox("Arret d'arrivee", stop_names, key="to_stop")
        to_stop = next(s for s in stops if s['name'] == selected_to)
        to_lat = float(to_stop['latitude'])
        to_lon = float(to_stop['longitude'])
        st.session_state.to_lat = to_lat
        st.session_state.to_lon = to_lon

    st.markdown("---")

    # === OPTIONS ===
    st.subheader("⚙️ Options")
    departure_date = st.date_input("📅 Date", value=datetime(2026, 6, 15))
    departure_time_val = st.time_input("🕐 Heure", value=time(8, 30))
    is_joj = st.checkbox("🏅 Evenement JOJ (congestion +)", value=False)

    st.markdown("---")

    # === BOUTON CALCULER ===
    if st.button("🔍 Calculer l'itineraire", type="primary", use_container_width=True):
        with st.spinner("🧮 Calcul des itineraires en cours..."):
            departure_dt = datetime.combine(departure_date, departure_time_val)

            result = st.session_state.api.get_routes(
                from_lon=from_lon,
                from_lat=from_lat,
                to_lon=to_lon,
                to_lat=to_lat,
                departure_time=departure_dt,
                is_joj_event=is_joj
            )

            st.session_state.routes_data = result
            st.session_state.selected_route = None
            st.session_state.click_mode = None
            st.rerun()

    # === POINTS D'INTERET RAPIDES ===
    st.markdown("---")
    st.subheader("📍 Points d'interet JOJ")

    poi_data = st.session_state.api.get_poi_data()

    # Grouper par categorie
    poi_by_cat = {}
    for f in poi_data['features']:
        cat = f['properties']['category']
        if cat not in poi_by_cat:
            poi_by_cat[cat] = []
        poi_by_cat[cat].append(f)

    for cat_key, cat_info in POI_CATEGORIES.items():
        if cat_key in poi_by_cat:
            with st.expander(f"{get_poi_icon(cat_key)} {cat_info['label']} ({len(poi_by_cat[cat_key])})"):
                for f in poi_by_cat[cat_key]:
                    name = f['properties']['Nom']
                    lon, lat = f['geometry']['coordinates']

                    col_p1, col_p2 = st.columns([3, 1])
                    with col_p1:
                        st.markdown(f"<div class='poi-card' style='border-left-color: {cat_info['color']};'>{get_poi_icon(cat_key)} <b>{name}</b></div>", unsafe_allow_html=True)
                    with col_p2:
                        if st.button("🚀", key=f"poi_{name.replace(' ', '_')}", help=f"Aller a {name}"):
                            st.session_state.to_lat = lat
                            st.session_state.to_lon = lon
                            departure_dt = datetime.combine(departure_date, departure_time_val)
                            result = st.session_state.api.get_routes(
                                from_lon=st.session_state.from_lon,
                                from_lat=st.session_state.from_lat,
                                to_lon=lon,
                                to_lat=lat,
                                departure_time=departure_dt,
                                is_joj_event=is_joj
                            )
                            st.session_state.routes_data = result
                            st.session_state.selected_route = None
                            st.rerun()

    # === STATS RESEAU ===
    st.markdown("---")
    st.subheader("📊 Reseau")
    stops = st.session_state.api.get_all_stops()
    ter_count = len([s for s in stops if s['transport_type'] == 'TER'])
    brt_count = len([s for s in stops if s['transport_type'] == 'BRT'])
    bus_count = len([s for s in stops if s['transport_type'] == 'BUS'])

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🚆 TER", ter_count)
        st.metric("🚌 BRT", brt_count)
    with col2:
        st.metric("🚍 BUS", bus_count)
        st.metric("📍 Total", len(stops))

# ============================================================
# CONTENU PRINCIPAL
# ============================================================

st.markdown("""
<div class="main-header">
    <h1>🚌 Pass'Tranquille</h1>
    <p>Itineraires multimodaux intelligents pour les JOJ Dakar 2026</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="joj-banner">
    🏅 Jeux Olympiques de la Jeunesse 2026 | Dakar, Senegal | 22 octobre - 9 novembre 2026
</div>
""", unsafe_allow_html=True)

# Mode resultats
if st.session_state.routes_data and st.session_state.routes_data['status'] == 'success':
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("🗺️ Itineraires proposes")
        routes = st.session_state.routes_data['routes']

        for idx, route in enumerate(routes):
            segments_html = ""
            for seg in route['segments']:
                icon = get_mode_icon(seg['mode'])
                segments_html += f'<span class="segment-badge" style="background-color: {seg["color"]};"><span class="icon">{icon}</span>{seg["mode_name"]} {seg["distance_formatted"]}</span>'

            congestion = route.get('congestion_level', 'Faible')
            congestion_class = {'Faible': 'congestion-low', 'Moderee': 'congestion-moderate', 'Elevee': 'congestion-high'}.get(congestion, 'congestion-low')
            card_class = "fastest" if idx == 0 else "alternative"

            st.markdown(f"""
            <div class="route-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #2c3e50;">{'🥇' if idx == 0 else '🥈'} Itineraire {idx + 1}</h3>
                    <span class="congestion-badge {congestion_class}">🚦 {congestion}</span>
                </div>
                <div class="stats-grid">
                    <div class="stat-box"><div class="value">{route['predicted_duration_formatted']}</div><div class="label">Duree estimee</div></div>
                    <div class="stat-box"><div class="value">{route['total_distance_meters']/1000:.1f} km</div><div class="label">Distance totale</div></div>
                    <div class="stat-box"><div class="value">{route['total_transfers']}</div><div class="label">Correspondances</div></div>
                </div>
                <div style="margin-top: 1rem;">{segments_html}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Voir sur la carte - Itineraire {idx + 1}", key=f"route_btn_{idx}", use_container_width=True):
                st.session_state.selected_route = idx
                st.rerun()

        if st.session_state.selected_route is not None:
            st.markdown("---")
            render_step_timeline(routes[st.session_state.selected_route])

    with col_right:
        st.subheader("🗺️ Carte interactive")
        m = create_map(
            center_lat=(st.session_state.from_lat + st.session_state.to_lat) / 2,
            center_lon=(st.session_state.from_lon + st.session_state.to_lon) / 2,
            zoom=12,
            routes_data=routes,
            selected_route_idx=st.session_state.selected_route
        )
        map_data = st_folium(m, width=700, height=600, key="map_with_routes")

        # Gestion du clic
        if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
            clicked = map_data['last_clicked']
            lat, lng = clicked['lat'], clicked['lng']

            if st.session_state.click_mode == 'depart':
                st.session_state.from_lat = lat
                st.session_state.from_lon = lng
                st.session_state.click_mode = None
                st.success(f"✅ Depart defini: {lat:.6f}, {lng:.6f}")
                st.rerun()
            elif st.session_state.click_mode == 'destination':
                st.session_state.to_lat = lat
                st.session_state.to_lon = lng
                st.session_state.click_mode = None
                st.success(f"✅ Destination definie: {lat:.6f}, {lng:.6f}")
                st.rerun()

else:
    # Mode carte seule
    st.subheader("🗺️ Carte du reseau de Dakar")
    st.info("💡 Selectionnez un Point d'Interet JOJ dans le panneau gauche, ou configurez manuellement votre trajet.")

    m = create_map(zoom=12)
    map_data = st_folium(m, width=1200, height=700, key="map_initial")

    if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
        clicked = map_data['last_clicked']
        lat, lng = clicked['lat'], clicked['lng']

        if st.session_state.click_mode == 'depart':
            st.session_state.from_lat = lat
            st.session_state.from_lon = lng
            st.session_state.click_mode = None
            st.success(f"✅ Depart defini: {lat:.6f}, {lng:.6f}")
            st.rerun()
        elif st.session_state.click_mode == 'destination':
            st.session_state.to_lat = lat
            st.session_state.to_lon = lng
            st.session_state.click_mode = None
            st.success(f"✅ Destination definie: {lat:.6f}, {lng:.6f}")
            st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>🚌 Pass'Tranquille | Dakar JOJ 2026 | Python + PostgreSQL/PostGIS + Machine Learning</p>
    <p style="font-size: 0.8rem;">Dijkstra + Yen k-shortest paths | Gradient Boosting temps reel | 19 Points d'Interet JOJ</p>
</div>
""", unsafe_allow_html=True)