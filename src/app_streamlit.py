import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# Configuración de la página
st.set_page_config(
    page_title="Gran Juego Dashboard",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
    }
    .stApp {
        background-image: linear-gradient(to right top, #ffffff, #f8f9fa, #f1f3f5, #e9ecef, #dee2e6);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. Carga de Datos
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Ruta mapeada en Docker
    DATA_PATH = "/home/jovyan/work/data/processed/qog_great_game.parquet"
    try:
        # Usamos Pandas para agilidad en el dashboard (dataset pequeño)
        df = pd.read_parquet(DATA_PATH)
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df = load_data()

# -----------------------------------------------------------------------------
# 2. Sidebar y Filtros
# -----------------------------------------------------------------------------
st.sidebar.title("🌏 Configuración")
st.sidebar.markdown("---")

if not df.empty:
    # Asegurar años enteros y ordenados
    years = sorted(df['year'].dropna().unique().astype(int))
    
    # Lógica inteligente: Por defecto, seleccionar el último año que tenga datos reales
    # para las variables clave (evita mostrar el 2023 si está vacío).
    valid_data_years = df.dropna(subset=['wdi_expmil', 'gle_cgdpc'])['year'].unique().astype(int)
    if len(valid_data_years) > 0:
        default_year = int(max(valid_data_years))
    else:
        default_year = int(years[-1])

    selected_year = st.sidebar.slider("Filtrar por Año", int(years[0]), int(years[-1]), default_year)
    
    countries = df['cname'].unique()
    selected_countries = st.sidebar.multiselect("Seleccionar Países", countries, default=countries)
    
    # Datos filtrados
    df_filtered = df[(df['year'] == selected_year) & (df['cname'].isin(selected_countries))]
else:
    st.sidebar.warning("No hay datos cargados.")
    df_filtered = pd.DataFrame()

# -----------------------------------------------------------------------------
# 3. Layout Principal
# -----------------------------------------------------------------------------
st.title("🌏 Dashboard: El 'Gran Juego' Post-Soviético")
st.markdown("### Análisis de Factores de Poder y Desarrollo Económico")
st.markdown("---")

# Métricas Clave (KPIs)
col1, col2, col3, col4 = st.columns(4)
if not df_filtered.empty:
    avg_gdp = df_filtered['gle_cgdpc'].mean()
    avg_mil = df_filtered['wdi_expmil'].mean()
    avg_dem = df_filtered['p_polity2'].mean()
    avg_corr = df_filtered['vdem_corr'].mean()
    
    col1.metric("Promedio PIB (PPP)", f"${avg_gdp:,.0f}")
    col2.metric("Gasto Militar (% PIB)", f"{avg_mil:.2f}%")
    col3.metric("Índice Democracia", f"{avg_dem:.1f}")
    col4.metric("Control Corrupción", f"{avg_corr:.2f}")

# Tabs de contenido
tab1, tab2, tab3, tab4 = st.tabs(["📊 Análisis Exploratorio", "🤖 Modelo ML Interactivo", "🗺️ Visión Regional", "📂 Documentación"])

# -----------------------------------------------------------------------------
# Tab 1: Análisis Exploratorio
# -----------------------------------------------------------------------------
with tab1:
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.subheader("Evolución del PIB per Cápita")
        # Line chart de toda la serie histórica (no solo el año filtrado) para los países seleccionados
        df_hist = df[df['cname'].isin(selected_countries)]
        fig_line = px.line(df_hist, x='year', y='gle_cgdpc', color='cname', 
                           markers=True, title="Trayectoria Económica (1991-2023)",
                           labels={'gle_cgdpc': 'PIB per Cápita', 'year': 'Año', 'cname': 'País'})
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_viz2:
        st.subheader("Relación: Gasto Militar vs PIB")
        # Limpiar datos para evitar error de NaNs en 'size'
        df_scatter = df_filtered.dropna(subset=['wdi_pop', 'wdi_expmil', 'gle_cgdpc']).copy()
        
        if not df_scatter.empty:
            fig_scatter = px.scatter(df_scatter, x='wdi_expmil', y='gle_cgdpc', 
                                    size='wdi_pop', color='cname', hover_name='cname',
                                    title=f"Scatter Plot (Año {selected_year})",
                                    labels={'wdi_expmil': 'Gasto Militar (%)', 'gle_cgdpc': 'PIB', 'wdi_pop': 'Población'})
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("No hay datos completos de Población/Gasto Militar para este año.")

    st.subheader("Matriz de Correlación (Histórico - Países Seleccionados)")
    if not df.empty:
        # Calcular correlación sobre TODO el histórico de los países seleccionados
        # (No filtramos por año porque necesitamos N grande para correlaicón)
        df_corr_source = df[df['cname'].isin(selected_countries)]
        
        features = ['gle_cgdpc', 'wdi_lifexp', 'p_polity2', 'vdem_corr', 'wdi_expmil']
        corr_matrix = df_corr_source[features].dropna().corr()
        
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r",
                             title=f"Correlación ({', '.join(selected_countries)})")
        st.plotly_chart(fig_corr, use_container_width=True)

# -----------------------------------------------------------------------------
# Tab 2: Modelo ML Interactivo
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("""
    ### 🔮 Simulador Random Forest
    Entrena un modelo en tiempo real y **mueve los deslizadores** para predecir cómo cambiaría el PIB bajo diferentes condiciones políticas.
    """)
    
    col_ml_left, col_ml_right = st.columns([1, 2])
    
    # Entrenar modelo (Scikit-Learn)
    features_ml = ['wdi_lifexp', 'p_polity2', 'vdem_corr', 'wdi_expmil']
    target_ml = 'gle_cgdpc'
    
    df_ml = df.dropna(subset=features_ml + [target_ml])
    X = df_ml[features_ml]
    y = df_ml[target_ml]
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    r2 = r2_score(y, model.predict(X))
    
    with col_ml_left:
        st.success(f"Modelo Entrenado (R²: {r2:.2f})")
        st.markdown("#### Parámetros de Simulación:")
        
        sim_life = st.slider("Esperanza de Vida", float(X['wdi_lifexp'].min()), float(X['wdi_lifexp'].max()), float(X['wdi_lifexp'].mean()))
        sim_dem = st.slider("Democracia (Polity)", -10.0, 10.0, float(X['p_polity2'].mean()))
        sim_corr = st.slider("Control Corrupción", 0.0, 1.0, float(X['vdem_corr'].mean()))
        sim_mil = st.slider("Gasto Militar (%)", 0.0, float(X['wdi_expmil'].max()), float(X['wdi_expmil'].mean()))
        
        input_data = pd.DataFrame([[sim_life, sim_dem, sim_corr, sim_mil]], columns=features_ml)
        prediction = model.predict(input_data)[0]
        
        st.metric("PIB Predicho", f"${prediction:,.2f}")

    with col_ml_right:
        st.subheader("Importancia de Variables (Feature Importance)")
        importances = pd.DataFrame({
            'Feature': features_ml,
            'Importance': model.feature_importances_
        }).sort_values(by='Importance', ascending=True)
        
        fig_imp = px.bar(importances, x='Importance', y='Feature', orientation='h', 
                         color='Importance', color_continuous_scale='Viridis')
        st.plotly_chart(fig_imp, use_container_width=True)

# -----------------------------------------------------------------------------
# Tab 3: Visión regional
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Comparativa por Subregiones")
    fig_box = px.box(df, x="subregion", y="gle_cgdpc", color="subregion", 
                     title="Distribución del PIB por Región Geopolítica",
                     points="all")
    st.plotly_chart(fig_box, use_container_width=True)

# -----------------------------------------------------------------------------
# Tab 4: Documentación del Proyecto
# -----------------------------------------------------------------------------
def read_markdown_file(filename):
    path = f"/home/jovyan/work/{filename}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al leer el archivo {filename}: {e}"

with tab4:
    st.header("📂 Documentación del Proyecto")
    st.markdown("Selecciona el documento que deseas visualizar:")
    
    docs = {
        "ℹ️ README (General)": "README.md",
        "🏗️ Infraestructura": "02_INFRAESTRUCTURA.md",
        "📊 Resultados y Análisis": "03_RESULTADOS.md",
        "🧠 Reflexión IA": "04_REFLEXION_IA.md"
    }
    
    selected_doc_name = st.radio("Archivos Disponibles:", list(docs.keys()), horizontal=True)
    
    st.markdown("---")
    
    # Mostrar contenido del archivo seleccionado
    file_content = read_markdown_file(docs[selected_doc_name])
    st.markdown(file_content, unsafe_allow_html=True)
