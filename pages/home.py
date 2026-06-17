"""
pages/home.py — CookSnap
Halaman Beranda: hero, quick search, feature cards, how it works,
top recipes, category explore, dan footer.
"""

import pandas as pd
import streamlit as st

from models import search_recipes, get_category_emoji, url_to_cookpad
from utils import fetch_cookpad_image


def render(recipes_df, ingredients_df, bm25_model, tfidf_model, recipe_ids_list, grouped_ings):
    cats = recipes_df["category"].value_counts()

    # ── HERO ──
    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-logo">🍳 CookSnap</div>
        <div class="hero-tagline">
            Masukkan bahan yang ada di dapur — kami carikan resep terbaik untuk kamu, seketika.
        </div>
        <div class="hero-sub">BM25 · TF-IDF · Agentic AI · Groq LLaMA 3</div>
        <div class="hero-stats">
            <div>
                <div class="hero-stat-num">{len(recipes_df):,}</div>
                <div class="hero-stat-label">Resep</div>
            </div>
            <div>
                <div class="hero-stat-num">{ingredients_df['ingredient_name'].nunique():,}</div>
                <div class="hero-stat-label">Bahan Unik</div>
            </div>
            <div>
                <div class="hero-stat-num">{len(cats)}</div>
                <div class="hero-stat-label">Kategori</div>
            </div>
        </div>
        <div>
            <span class="hero-badge">⚡ BM25-Okapi</span>
            <span class="hero-badge">📊 TF-IDF</span>
            <span class="hero-badge">🤖 Chef AI</span>
            <span class="hero-badge">🍽 Nutrisi</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── QUICK SEARCH ──
    st.markdown("""
    <div class="quick-search-wrap">
        <div class="quick-search-label">🥬 Punya bahan apa hari ini?</div>
        <div class="quick-search-hint">Ketik bahan yang ada di dapur, pisahkan dengan koma — CookSnap carikan resepnya!</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col1:
        quick_input = st.text_input(
            "Bahan",
            placeholder="Contoh: ayam, bawang putih, tomat, telur...",
            label_visibility="collapsed",
        )
    with col2:
        quick_search = st.button("🔍 Cari Resep", use_container_width=True)

    if quick_search and quick_input:
        user_ings = [i.strip() for i in quick_input.replace(",", "\n").split("\n") if i.strip()]
        st.session_state.last_ingredients = user_ings
        with st.spinner("Mencari resep terbaik..."):
            results = search_recipes(
                user_ings, recipes_df, ingredients_df,
                bm25_model, tfidf_model, recipe_ids_list, grouped_ings, top_k=8,
            )
        st.session_state.search_results = results
        st.session_state.page = "Cari Resep"
        st.rerun()

    # ── FEATURE CARDS ──
    st.markdown('<div class="divider-section"><span class="divider-label">Fitur Unggulan</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="feature-icon">🔍</span>
            <div class="feature-title">Pencarian Cerdas BM25 + TF-IDF</div>
            <div class="feature-desc">Dua algoritma retrieval berjalan paralel. BM25-Okapi untuk relevansi kata, TF-IDF untuk kecocokan vektor bahan — hasil terbaik dari keduanya.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">Asisten Chef AI Agentic</div>
            <div class="feature-desc">Chef Ari siap membantu — substitusi bahan, tips memasak, info nutrisi, hingga modifikasi resep. Didukung Groq LLaMA 3.3 + agentic tools.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Estimasi Nutrisi Lengkap</div>
            <div class="feature-desc">Lihat estimasi kalori, protein, lemak, karbohidrat, dan serat per resep. Cocok untuk kamu yang peduli asupan gizi harian.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── HOW IT WORKS ──
    st.markdown('<div class="divider-section"><span class="divider-label">Cara Kerja</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:24px; box-shadow:var(--card-shadow);'>
        <div class='how-step'>
            <div class='how-num'>1</div>
            <div class='how-content'>
                <div class='how-title'>Masukkan bahan yang kamu punya</div>
                <div class='how-desc'>Ketik nama bahan satu per satu — ayam, bawang, tomat, atau apa pun yang ada di dapur.</div>
            </div>
        </div>
        <div class='how-step'>
            <div class='how-num'>2</div>
            <div class='how-content'>
                <div class='how-title'>BM25 + TF-IDF memindai ribuan resep</div>
                <div class='how-desc'>Algoritma dual-retrieval memeriksa kecocokan bahan secara paralel dan memberikan skor relevansi gabungan.</div>
            </div>
        </div>
        <div class='how-step'>
            <div class='how-num'>3</div>
            <div class='how-content'>
                <div class='how-title'>Resep terbaik direkomendasikan</div>
                <div class='how-desc'>Hasil diurutkan berdasarkan % kecocokan bahan + popularitas. Kamu bisa lihat bahan mana yang cocok dan yang kurang.</div>
            </div>
        </div>
        <div class='how-step'>
            <div class='how-num'>4</div>
            <div class='how-content'>
                <div class='how-title'>Tanya Asisten Chef jika perlu</div>
                <div class='how-desc'>Butuh substitusi bahan? Mau tanya tips memasak? Chef Ari siap menjawab kapan saja.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TOP RECIPES ──
    st.markdown('<div class="divider-section"><span class="divider-label">Resep Terpopuler</span></div>', unsafe_allow_html=True)
    top_recipes = recipes_df.nlargest(6, "loves")
    top_cols = st.columns(3)
    for idx, (_, row) in enumerate(top_recipes.iterrows()):
        with top_cols[idx % 3]:
            emoji = get_category_emoji(str(row.get("category", "")))
            loves_val     = int(row["loves"])
            cook_time_val = int(row["cook_time_min"]) if pd.notna(row.get("cook_time_min")) else 0
            diff_val      = row.get("difficulty", "-")
            cookpad_url   = url_to_cookpad(row.get("url", ""))
            img_url       = fetch_cookpad_image(cookpad_url) if cookpad_url else None

            if img_url:
                img_html = (
                    f"<div style='width:100%;height:140px;border-radius:10px;overflow:hidden;"
                    f"margin:8px 0 10px;background:var(--bg-secondary);'>"
                    f"<img src='{img_url}' style='width:100%;height:100%;object-fit:cover;' "
                    f"onerror=\"this.parentElement.innerHTML="
                    f"'<div style=\\'display:flex;align-items:center;justify-content:center;"
                    f"height:100%;font-size:3rem;\\'>{emoji}</div>'\" />"
                    f"</div>"
                )
            else:
                img_html = (
                    f"<div style='width:100%;height:140px;border-radius:10px;overflow:hidden;"
                    f"margin:8px 0 10px;background:var(--bg-secondary);display:flex;"
                    f"align-items:center;justify-content:center;font-size:3rem;'>{emoji}</div>"
                )

            st.markdown(f"""
            <div class='top-recipe-home'>
                <div class='tr-rank'>#{idx+1}</div>
                {img_html}
                <div class='tr-title'>{row['title']}</div>
                <div style='display:flex; gap:10px; align-items:center; flex-wrap:wrap;'>
                    <span class='tr-loves'>❤ {loves_val:,} suka</span>
                    <span class='meta-chip'>⏱ {cook_time_val} mnt</span>
                    <span class='meta-chip'>⚡ {diff_val}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Lihat Resep", key=f"home_recipe_{idx}"):
                st.session_state.selected_recipe = row["recipe_id"]
                st.session_state.page = "Detail Resep"
                st.rerun()

    # ── CATEGORY EXPLORE ──
    st.markdown('<div class="divider-section"><span class="divider-label">Jelajahi Kategori</span></div>', unsafe_allow_html=True)
    num_cats = min(len(cats), 5)
    col_cats = st.columns(num_cats)
    for i, (cat, count) in enumerate(cats.head(num_cats).items()):
        with col_cats[i]:
            emo = get_category_emoji(cat)
            st.markdown(f"""
            <div class='cat-card'>
                <span class='cat-emoji'>{emo}</span>
                <div class='cat-name'>{cat}</div>
                <div class='cat-count'>{count} resep</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Lihat", key=f"cat_{i}", use_container_width=True):
                st.session_state.search_category = cat
                st.session_state.last_ingredients = []
                st.session_state.search_results = []
                st.session_state.search_page = 1
                st.session_state.page = "Cari Resep"
                st.rerun()

    # ── FOOTER ──
    st.markdown("""
    <div style="text-align:center; padding:56px 0 32px; border-top:1px solid var(--border); margin-top:56px;">
        <div style="font-family:'Playfair Display',serif; font-size:1.5rem; font-weight:800;
             background:linear-gradient(135deg,#e8a838,#d4622a);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:10px;">
            🍳 CookSnap
        </div>
        <div style="font-size:0.8rem; color:var(--text-dim); line-height:1.9;">
            Sistem Rekomendasi Resep Berbasis Bahan Makanan<br>
            Data resep dari Cookpad Indonesia · AI oleh Groq LLaMA 3.3 · BM25-Okapi + TF-IDF<br>
            <span style="color:var(--border);">—</span><br>
            Dibuat untuk membantu masyarakat Indonesia memasak lebih cerdas dan mengurangi food waste
        </div>
    </div>
    """, unsafe_allow_html=True)
