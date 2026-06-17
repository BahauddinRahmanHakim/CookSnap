"""
app.py — CookSnap
Entry point utama: konfigurasi halaman, sidebar, routing antar page.

Jalankan dengan:
    streamlit run app.py
"""

import streamlit as st

from styles import inject_css
from models import load_data, build_index
from ai_agent import ChefAgent
import pages.home   as page_home
import pages.search as page_search
import pages.detail as page_detail
import pages.chat   as page_chat


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CookSnap",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide   default page navigation
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# THEME STATE
# ─────────────────────────────────────────────────────────────
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

is_light = st.session_state.theme_mode == "light"
inject_css(is_light)


# ─────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────
defaults = {
    "page":                 "Beranda",
    "selected_recipe":      None,
    "chat_history":         [],
    "chat_tools":           [],
    "chef_chat_history":    [],
    "chef_chat_tools":      [],
    "chef_chat_recipe_id":  None,
    "show_chef_chat":       False,
    "search_results":       [],
    "last_ingredients":     [],
    "search_category":      "Semua",
    "search_page":          1,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
# LOAD DATA & BUILD INDEX
# ─────────────────────────────────────────────────────────────
with st.spinner("Memuat data resep..."):
    recipes_df, ingredients_df, nutrition_df, steps_df = load_data()

with st.spinner("Membangun indeks BM25 + TF-IDF..."):
    bm25_model, tfidf_model, recipe_ids_list, grouped_ings = build_index(ingredients_df)

chef_agent = ChefAgent(recipes_df, ingredients_df, grouped_ings, nutrition_df)


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-logo">🍳 CookSnap</div>
        <div class="sidebar-brand-sub">Masak Cerdas, Kurangi Limbah</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Theme Toggle ──
    theme_icon  = "☀️" if is_light else "🌙"
    theme_label = "Light Mode" if is_light else "Dark Mode"
    st.markdown(f"""
    <div class="theme-toggle-wrap">
        <span class="theme-icon">{theme_icon}</span>
        <span class="theme-label">{theme_label}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 Ganti Tema", use_container_width=True, key="theme_toggle"):
        st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"
        st.rerun()

    st.markdown("---")

    # ── Navigation ──
    pages     = ["🏠  Beranda", "🔍  Cari Resep", "📖  Detail Resep"]
    page_keys = ["Beranda",    "Cari Resep",     "Detail Resep"]
    for label, key in zip(pages, page_keys):
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("---")

    st.markdown(f"""
    <div class="sidebar-stats">
        📊 <strong>{len(recipes_df):,}</strong> resep<br>
        🥬 <strong>{ingredients_df['ingredient_name'].nunique():,}</strong> bahan unik<br>
        🔎 Retrieval: <strong>BM25 + TF-IDF</strong><br>
        🤖 AI Chat: <strong>Groq LLaMA 3.3</strong>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "Beranda":
    page_home.render(
        recipes_df, ingredients_df,
        bm25_model, tfidf_model, recipe_ids_list, grouped_ings,
    )

elif page == "Cari Resep":
    page_search.render(
        recipes_df, ingredients_df,
        bm25_model, tfidf_model, recipe_ids_list, grouped_ings,
    )

elif page == "Detail Resep":
    page_detail.render(recipes_df, steps_df, grouped_ings, nutrition_df, chef_agent)
