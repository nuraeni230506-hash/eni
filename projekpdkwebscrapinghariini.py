import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# CONFIG PAGE
st.set_page_config(
    page_title="Analisis Tren Perikanan Indonesia 2021-2025",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LOAD DATA WITH CACHE
@st.cache_data
def load_data():
    data_produksi = pd.read_csv("data_bps_perikanan.csv")
    data_harga = pd.read_csv("data_harga_ecommerce.csv")
    return data_produksi, data_harga

data_produksi, data_harga = load_data()

# HEADER
st.title("📊 Analisis Tren Produksi Tangkapan Perikanan & Harga Jual Ikan")
st.subheader("Data BPS & E-Commerce Indonesia Tahun 2021-2025")

st.write("""
Analisis komprehensif tentang tren produksi hasil tangkapan perikanan dari Badan Pusat Statistik (BPS) 
dan pergerakan harga jual ikan di platform e-commerce terkemuka di Indonesia (Tokopedia, Shopee, Lazada) 
dalam periode 2021-2025.
""")

# garis pemisah
st.divider()

# SIDEBAR - LINK E-COMMERCE & SUMBER DATA
with st.sidebar:
    st.header("🔗 Sumber Data & Platform E-Commerce")
    
    st.subheader("📍 Sumber Data BPS")
    st.markdown("""
    - **Badan Pusat Statistik (BPS)**: 
      https://www.bps.go.id/
    - **Data Perikanan Indonesia**:
      https://www.bps.go.id/id/subject/166/perikanan.html
    """)
    
    st.subheader("🛒 Platform E-Commerce Penjualan Ikan")
    st.markdown("""
    - **[Tokopedia](https://www.tokopedia.com/search?q=ikan)**
    - **[Shopee](https://shopee.co.id/search?keyword=ikan)**
    - **[Lazada](https://www.lazada.co.id/search/?q=ikan)**
    """)
    
    st.divider()
    
    st.subheader("📈 Tahun Analisis")
    tahun_selected = st.multiselect(
        "Pilih Tahun",
        sorted(data_produksi['Tahun'].unique()),
        default=sorted(data_produksi['Tahun'].unique())
    )
    
    st.subheader("🐟 Jenis Ikan")
    ikan_selected = st.multiselect(
        "Pilih Jenis Ikan",
        data_produksi['Jenis_Ikan'].unique(),
        default=data_produksi['Jenis_Ikan'].unique()
    )

# Filter data berdasarkan pilihan
data_produksi_filtered = data_produksi[
    (data_produksi['Tahun'].isin(tahun_selected)) & 
    (data_produksi['Jenis_Ikan'].isin(ikan_selected))
]

data_harga_filtered = data_harga[
    (data_harga['Tahun'].isin(tahun_selected)) & 
    (data_harga['Jenis_Ikan'].isin(ikan_selected))
]

st.divider()

# METRIC CARD - STATISTIK UTAMA
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_produksi = data_produksi_filtered['Produksi_Ton'].sum()
    st.metric(
        "Total Produksi",
        f"{total_produksi:,.0f} Ton",
        f"{((total_produksi / data_produksi['Produksi_Ton'].sum()) * 100):.1f}%"
    )

with col2:
    avg_harga = data_harga_filtered[['Harga_Perkg_Tokopedia', 'Harga_Perkg_Shopee', 'Harga_Perkg_Lazada']].mean().mean()
    st.metric(
        "Rata-rata Harga",
        f"Rp {avg_harga:,.0f}/kg",
        "E-Commerce"
    )

with col3:
    jumlah_data = len(data_produksi_filtered)
    st.metric(
        "Jumlah Data Produksi",
        f"{jumlah_data} records",
        "2021-2025"
    )

with col4:
    jenis_ikan = len(ikan_selected)
    st.metric(
        "Jenis Ikan Analisis",
        f"{jenis_ikan} jenis",
        "Utama"
    )

st.divider()

# SECTION 1: ANALISIS PRODUKSI PERIKANAN
st.header("📈 1. Tren Produksi Tangkapan Perikanan (BPS)")

col1, col2 = st.columns(2)

# Pre-compute untuk efisiensi
produksi_tahun = data_produksi_filtered.groupby(['Tahun', 'Jenis_Ikan'])['Produksi_Ton'].sum().reset_index()
produksi_total_tahun = data_produksi_filtered.groupby('Tahun')['Produksi_Ton'].sum().reset_index()

with col1:
    # Grafik Produksi per Tahun dan Jenis Ikan
    fig_produksi = px.bar(
        produksi_tahun,
        x='Tahun',
        y='Produksi_Ton',
        color='Jenis_Ikan',
        title='Produksi Ikan per Tahun (2021-2025)',
        labels={'Produksi_Ton': 'Produksi (Ton)', 'Tahun': 'Tahun'},
        barmode='group',
        height=400
    )
    fig_produksi.update_layout(hovermode='x unified')
    st.plotly_chart(fig_produksi, use_container_width=True)

with col2:
    # Grafik Tren Produksi Total
    fig_tren = px.area(
        produksi_total_tahun,
        x='Tahun',
        y='Produksi_Ton',
        title='Tren Produksi Total Ikan',
        labels={'Produksi_Ton': 'Produksi (Ton)', 'Tahun': 'Tahun'},
        height=400
    )
    st.plotly_chart(fig_tren, use_container_width=True)

st.divider()

# SECTION 2: ANALISIS HARGA JUAL IKAN DI E-COMMERCE
st.header("💰 2. Tren Harga Jual Ikan di E-Commerce (Tokopedia, Shopee, Lazada)")

col1, col2 = st.columns(2)

# Pre-compute harga per platform
harga_platform_stats = []
for platform in ['Tokopedia', 'Shopee', 'Lazada']:
    col_name = f'Harga_Perkg_{platform}'
    temp = data_harga_filtered.groupby('Tahun')[col_name].mean().reset_index()
    temp.columns = ['Tahun', 'Harga_Rata2']
    temp['Platform'] = platform
    harga_platform_stats.append(temp)

harga_platform_df = pd.concat(harga_platform_stats, ignore_index=True)

# Pre-compute harga per jenis ikan
harga_jenis_mean = data_harga_filtered[[
    'Tahun', 'Jenis_Ikan', 'Harga_Perkg_Tokopedia', 
    'Harga_Perkg_Shopee', 'Harga_Perkg_Lazada'
]].copy()

harga_jenis_mean['Harga_Rata2'] = harga_jenis_mean[[
    'Harga_Perkg_Tokopedia', 'Harga_Perkg_Shopee', 'Harga_Perkg_Lazada'
]].mean(axis=1)

harga_jenis_df = harga_jenis_mean.groupby(['Tahun', 'Jenis_Ikan'])['Harga_Rata2'].mean().reset_index()

with col1:
    fig_harga = px.bar(
        harga_platform_df,
        x='Tahun',
        y='Harga_Rata2',
        color='Platform',
        title='Rata-rata Harga Ikan per Platform E-Commerce',
        labels={'Harga_Rata2': 'Harga (Rp/kg)', 'Tahun': 'Tahun'},
        barmode='group',
        height=400
    )
    st.plotly_chart(fig_harga, use_container_width=True)

with col2:
    fig_harga_jenis = px.line(
        harga_jenis_df,
        x='Tahun',
        y='Harga_Rata2',
        color='Jenis_Ikan',
        title='Tren Harga per Jenis Ikan (Rata-rata E-Commerce)',
        labels={'Harga_Rata2': 'Harga (Rp/kg)', 'Tahun': 'Tahun'},
        markers=True,
        height=400
    )
    st.plotly_chart(fig_harga_jenis, use_container_width=True)

st.divider()

# SECTION 3: PERBANDINGAN HARGA PER PLATFORM
st.header("🔄 3. Perbandingan Harga Antar Platform E-Commerce")

col1, col2 = st.columns(2)

# Prepare data untuk box plot dengan melt (jauh lebih cepat dari iterrows)
harga_melt = data_harga_filtered.melt(
    id_vars=['Tahun', 'Jenis_Ikan'],
    value_vars=['Harga_Perkg_Tokopedia', 'Harga_Perkg_Shopee', 'Harga_Perkg_Lazada'],
    var_name='Platform',
    value_name='Harga'
)
harga_melt['Platform'] = harga_melt['Platform'].str.replace('Harga_Perkg_', '')

with col1:
    fig_box = px.box(
        harga_melt,
        x='Platform',
        y='Harga',
        color='Platform',
        title='Distribusi Harga per Platform',
        labels={'Harga': 'Harga (Rp/kg)', 'Platform': 'Platform E-Commerce'},
        height=400
    )
    st.plotly_chart(fig_box, use_container_width=True)

with col2:
    # Heatmap WPP vs Produksi
    wpp_produksi = data_produksi_filtered.groupby(['Tahun', 'WPP'])['Produksi_Ton'].sum().reset_index()
    pivot_wpp = wpp_produksi.pivot(index='WPP', columns='Tahun', values='Produksi_Ton')
    
    fig_heatmap = px.imshow(
        pivot_wpp,
        labels={'x': 'Tahun', 'y': 'Wilayah Pengelolaan Perikanan (WPP)', 'color': 'Produksi (Ton)'},
        title='Heatmap Produksi per WPP',
        color_continuous_scale='YlGn',
        height=400
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.divider()

# SECTION 4: TABEL DATA DETAIL
st.header("📋 4. Data Detail - Produksi Tangkapan Perikanan")

tab1, tab2, tab3 = st.tabs(["Produksi BPS", "Harga E-Commerce", "Analisis Ringkas"])

with tab1:
    st.subheader("Data Produksi Ikan dari BPS (2021-2025)")
    st.dataframe(
        data_produksi_filtered.sort_values(['Tahun', 'Jenis_Ikan']),
        use_container_width=True,
        height=400
    )
    
    # Unduh Data Produksi
    csv_produksi = data_produksi_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data Produksi (CSV)",
        data=csv_produksi,
        file_name="data_produksi_perikanan_2021-2025.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("Data Harga Ikan dari E-Commerce (2021-2025)")
    st.dataframe(
        data_harga_filtered.sort_values(['Tahun', 'Bulan', 'Jenis_Ikan']),
        use_container_width=True,
        height=400
    )
    
    # Unduh Data Harga
    csv_harga = data_harga_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data Harga (CSV)",
        data=csv_harga,
        file_name="data_harga_ecommerce_2021-2025.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("Ringkasan Analisis")
    
    # Statistik Deskriptif Produksi
    st.write("**Statistik Produksi:**")
    st.dataframe(
        data_produksi_filtered.groupby('Jenis_Ikan')['Produksi_Ton'].describe().round(0),
        use_container_width=True
    )
    
    # Statistik Deskriptif Harga
    st.write("**Statistik Harga (Rata-rata per Platform):**")
    harga_stats_desc = data_harga_filtered[[
        'Harga_Perkg_Tokopedia', 
        'Harga_Perkg_Shopee', 
        'Harga_Perkg_Lazada'
    ]].describe().round(0)
    harga_stats_desc.columns = ['Tokopedia (Rp/kg)', 'Shopee (Rp/kg)', 'Lazada (Rp/kg)']
    st.dataframe(harga_stats_desc, use_container_width=True)

st.divider()

# SECTION 5: INSIGHT DAN KESIMPULAN
st.header("💡 5. Key Insights & Kesimpulan")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **📊 Tren Produksi:**
    
    - Peningkatan konsisten produksi 2021-2025
    - Tuna adalah komoditas dengan produksi tertinggi
    - Rata-rata pertumbuhan positif setiap tahunnya
    """)

with col2:
    st.success("""
    **💹 Tren Harga:**
    
    - Kenaikan harga signifikan seiring pertumbuhan demand
    - Variasi harga antar platform 3-5%
    - Tokopedia umumnya lebih kompetitif
    """)

with col3:
    st.warning("""
    **🎯 Rekomendasi:**
    
    - Optimalisasi distribusi ke e-commerce
    - Monitor harga di ketiga platform
    - Fokus pada jenis ikan bernilai tinggi
    """)

st.divider()

# FOOTER
st.divider()

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.caption("""
    **📌 Sumber Data:**
    - Data Produksi: Badan Pusat Statistik (BPS)
    - Data Harga: Tokopedia, Shopee, Lazada
    """)

with footer_col2:
    st.caption("""
    **🔗 Referensi Resmi:**
    - [BPS.go.id](https://www.bps.go.id/)
    - [Tokopedia](https://www.tokopedia.com/)
    - [Shopee](https://shopee.co.id/)
    """)

with footer_col3:
    st.caption("""
    **📊 Dashboard Info:**
    - Versi: 2.0
    - Update: Juni 2025
    - Data: 2021-2025
    """)

st.divider()

st.markdown("""
---
**Dashboard Analisis Tren Produksi Tangkapan Perikanan dan Harga Jual Ikan di Indonesia (2021-2025)**  
*Menggunakan data dari Badan Pusat Statistik (BPS) dan Platform E-Commerce Terkemuka*  
Dibuat dengan Python, Pandas, dan Streamlit | © 2025
""")