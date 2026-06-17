"""
pages/search.py — CookSnap
Halaman Cari Resep: filter, dual retrieval BM25+TF-IDF,
model comparison expander, dan daftar hasil.
"""

import html
import streamlit as st

from models import search_recipes, compare_models, url_to_cookpad


def render(recipes_df, ingredients_df, bm25_model, tfidf_model, recipe_ids_list, grouped_ings):
    st.markdown('<div class="section-title">🔍 Cari Resep dari Bahan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Masukkan bahan yang kamu punya — CookSnap merekomendasikan resep terbaik dengan BM25 + TF-IDF dual retrieval.</div>', unsafe_allow_html=True)

    with st.container():
        col_filter1, col_filter2, col_filter3, col_filter4 = st.columns([2, 1, 1, 1])

        with col_filter1:
            # Use session_state for the text area to avoid losing the typed
            # input during Streamlit reruns when buttons are pressed.
            if "ingredient_input" not in st.session_state:
                st.session_state.ingredient_input = (
                    "\n".join(st.session_state.last_ingredients)
                    if st.session_state.get("last_ingredients")
                    else ""
                )
            ingredient_input = st.text_area(
                "Bahan yang dimiliki",
                key="ingredient_input",
                placeholder="Masukkan satu bahan per baris:\nayam\nbawang putih\ntomat\ntelur",
                height=120,
            )
        with col_filter2:
            difficulty_options = ["Semua"] + sorted(recipes_df["difficulty"].dropna().unique().tolist())
            difficulty = st.selectbox("Tingkat Kesulitan", difficulty_options)

        with col_filter3:
            category_options = ["Semua"] + sorted(recipes_df["category"].dropna().unique().tolist())
            default_cat_idx = 0
            if st.session_state.get("search_category", "Semua") in category_options:
                default_cat_idx = category_options.index(st.session_state["search_category"])
            category = st.selectbox("Kategori", category_options, index=default_cat_idx)
            old_category = st.session_state.get("search_category", "Semua")
            if category != old_category:
                st.session_state.search_results = []
                st.session_state.search_page = 1
            st.session_state.search_category = category

        with col_filter4:
            max_time = st.slider("Maks. Waktu (menit)", 0, 180, 0, step=15)
            top_k    = st.slider("Tampilkan", 5, 20, 10)
            main_boost = st.slider("Bobot Bahan Utama (boost)", 0.0, 0.5, 0.15, step=0.05)

    col_btn1, _ = st.columns([1, 5])
    with col_btn1:
        do_search = st.button("🔍 Cari Sekarang", use_container_width=True)

    if do_search:
        # Read the current text area from session_state to avoid stale values
        raw = st.session_state.get("ingredient_input", "")
        user_ings = [i.strip() for i in raw.replace(",", "\n").split("\n") if i.strip()]
        st.session_state.last_ingredients = user_ings
        st.session_state.search_category = category
        st.session_state.search_page = 1
        if not user_ings:
            st.warning("⚠️ Masukkan minimal 1 bahan!")
        else:
            with st.spinner(f"Mencari resep dari {len(user_ings)} bahan..."):
                results = search_recipes(
                    user_ings, recipes_df, ingredients_df,
                    bm25_model, tfidf_model, recipe_ids_list, grouped_ings,
                    top_k=top_k,
                    difficulty_filter=difficulty,
                    category_filter=category,
                    max_time=max_time if max_time > 0 else None,
                    main_boost=main_boost,
                )
            st.session_state.search_results = results

    results   = st.session_state.search_results
    user_ings = st.session_state.last_ingredients

    if not user_ings and st.session_state.search_category != "Semua":
        results = search_recipes(
            [], recipes_df, ingredients_df,
            bm25_model, tfidf_model, recipe_ids_list, grouped_ings,
            top_k=None,
            difficulty_filter=difficulty,
            category_filter=st.session_state.search_category,
            max_time=max_time if max_time > 0 else None,
            main_boost=main_boost,
        )
        st.session_state.search_results = results

    page_size = 10
    display_count = min(len(results), st.session_state.get("search_page", 1) * page_size)

    if results:
        search_context = (
            f" untuk bahan: <strong style='color:var(--accent-warm);'>{html.escape(', '.join(user_ings[:5]), quote=True)}</strong>"
            if user_ings else
            f" dalam kategori: <strong style='color:var(--accent-warm);'>{html.escape(st.session_state.search_category, quote=True)}</strong>"
        )

        # ── Model Comparison Expander ──
        with st.expander("🔬 Perbandingan Model (BM25 vs TF-IDF)"):
            comparison = compare_models(user_ings[:3], bm25_model, tfidf_model, recipe_ids_list, top_k=5)
            col_bm25, col_tfidf = st.columns(2)
            with col_bm25:
                st.markdown("**🏆 BM25 Top 5**")
                for rid, score in comparison["bm25_top"]:
                    row = recipes_df[recipes_df["recipe_id"] == rid]
                    title = row.iloc[0]["title"] if not row.empty else rid
                    st.markdown(f"- {title}: `{score:.4f}`")
            with col_tfidf:
                st.markdown("**📊 TF-IDF Top 5**")
                for rid, score in comparison["tfidf_top"]:
                    row = recipes_df[recipes_df["recipe_id"] == rid]
                    title = row.iloc[0]["title"] if not row.empty else rid
                    st.markdown(f"- {title}: `{score:.4f}`")

        st.markdown(f"""
        <div style='margin: 16px 0 8px; font-size: 0.82rem; color: var(--text-muted);'>
            ✅ Ditemukan <strong style='color:var(--accent-warm);'>{len(results)}</strong> resep
            untuk bahan: <strong style='color:var(--accent-warm);'>{', '.join(user_ings[:5])}</strong>
            {'...' if len(user_ings) > 5 else ''}
        </div>
        <div style='margin-bottom:12px; font-size:0.82rem; color:var(--text-muted);'>
            Menampilkan <strong>{display_count}</strong> dari <strong>{len(results)}</strong> resep.
        </div>
        """, unsafe_allow_html=True)

        for rank, r in enumerate(results[:display_count], 1):
            pct        = int(r["match_ratio"] * 100)
            have_text  = " ".join([f"<span class='ing-pill-have'>{html.escape(str(i), quote=False)}</span>" for i in r["have"][:6]])
            miss_text  = " ".join([f"<span class='ing-pill-miss'>{html.escape(str(i), quote=False)}</span>" for i in r["miss"][:4]])
            if not have_text and not miss_text:
                miss_text = "<span class='ing-pill-miss'>Tidak ada data bahan</span>"
            cookpad_url = url_to_cookpad(r.get("url", ""))
            link_html  = (
                f'<a href="{html.escape(cookpad_url, quote=True)}" target="_blank" '
                f'style="font-size:0.7rem; color:var(--text-muted); text-decoration:none;">🔗 Cookpad</a>'
                if cookpad_url else ""
            )

            meta_html = (
                f"<span class='meta-chip'>📂 {html.escape(str(r['category']), quote=False)}</span>"
                f"<span class='meta-chip'>⏱ {html.escape(str(r['cook_time']), quote=False)} mnt</span>"
                + (f"<span class='meta-chip' style='background:#fff1c6;'>⭐ Bahan Utama</span>" if r.get('main_match') else "")
                + f"<span class='meta-chip'>⚡ {html.escape(str(r['difficulty']), quote=False)}</span>"
                + f"<span class='meta-chip'>❤ {html.escape(str(r['loves']), quote=False)}</span>"
                + f"<span class='meta-chip'>👥 {html.escape(str(r['servings']), quote=False)} porsi</span>"
            )

            card_html = (
                f"<div class='recipe-card'>"
                f"<div class='recipe-rank'>#{rank}</div>"
                f"<div class='recipe-title'>{html.escape(str(r['title']), quote=False)}</div>"
                f"<div class='recipe-meta'>{meta_html}</div>"
                "<div class='match-bar-wrap'>"
                "<div class='match-label'>"
                "<span>Kecocokan Bahan</span>"
                f"<span>{len(r['have'])}/{r['total_ings']} bahan ({pct}%)</span>"
                "</div>"
                "<div class='match-bar-bg'>"
                f"<div class='match-bar-fill' style='width:{pct}%;'></div>"
                "</div>"
                "</div>"
                "<div class='ingredient-pills'>"
                f"{have_text} {miss_text}"
                "</div>"
                f"<div style='margin-top:8px;'>{link_html}</div>"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

            col_a, _ = st.columns([1, 6])
            with col_a:
                if st.button("📖 Detail", key=f"detail_{rank}_{r['recipe_id']}"):
                    st.session_state.selected_recipe = r["recipe_id"]
                    st.session_state.page = "Detail Resep"
                    st.rerun()

        if display_count < len(results):
            if st.button("📄 Muat lebih banyak", key="load_more_results"):
                st.session_state.search_page += 1
                st.rerun()

