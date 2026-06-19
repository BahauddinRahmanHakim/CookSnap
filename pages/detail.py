"""
pages/detail.py — CookSnap
Halaman Detail Resep: gambar, metadata, bahan & langkah,
estimasi nutrisi, dan saran substitusi bahan.
"""

import html
import re
import streamlit as st

from models import (
    get_category_emoji,
    url_to_cookpad,
    ingredient_match_score,
    estimate_nutrition,
)
from ai_agent import get_substitution_hint
from utils import fetch_cookpad_image, show_recipe_image


def clean_chat_content(content: str) -> str:
    """Strip semua tag HTML dari output LLM, kembalikan plain text."""
    text = html.unescape(content or '')
    text = re.sub(r'(?i)<br\s*/?>', '\n', text)
    text = re.sub(r'(?i)<p[^>]*>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return text.strip()



def build_chef_context(recipe_row, grouped_ings):
    recipe_ings = [str(i) for i in grouped_ings.get(recipe_row["recipe_id"], [])]
    return """Resep yang sedang dilihat:
- Judul: {title}
- Kategori: {category}
- Tingkat kesulitan: {difficulty}
- Waktu masak: {cook_time} menit
- Porsi: {servings} orang
- Bahan utama: {ingredients}""".format(
        title=recipe_row['title'],
        category=recipe_row.get('category', '-'),
        difficulty=recipe_row.get('difficulty', '-'),
        cook_time=recipe_row.get('cook_time_min', '-'),
        servings=int(recipe_row.get('servings', 2)),
        ingredients=', '.join(recipe_ings[:8]) + ('... ' if len(recipe_ings) > 8 else ''),
    )


def render_chef_chat(recipe_row, grouped_ings, chef_agent, rid):
    if st.session_state.chef_chat_recipe_id != rid:
        st.session_state.chef_chat_history = []
        st.session_state.chef_chat_tools = []
        st.session_state.chef_chat_recipe_id = rid
        st.session_state.show_chef_chat = False

    recipe_context = build_chef_context(recipe_row, grouped_ings)

    # Pastikan semua jawaban assistant yang tersimpan sudah dibersihkan
    for msg in st.session_state.chef_chat_history:
        if msg.get("role") == "assistant":
            msg["content"] = clean_chat_content(msg.get("content", ""))

    if st.session_state.show_chef_chat:
        st.markdown("""
        <style>
        .chef-fab-hint {
            margin-top: 12px; font-size: 0.88rem; color: var(--text-muted);
        }
        .chef-chat-header {
            display: flex; align-items: center; gap: 12px; margin-bottom: 12px;
        }
        .chef-chat-badge {
            display: inline-flex; align-items: center; justify-content: center;
            width: 36px; height: 36px; border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange));
            color: #000; font-size: 1.2rem;
        }
        .chef-chat-box {
            padding: 20px; border: 1px solid var(--border); border-radius: var(--radius);
            background: var(--bg-secondary);
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="chef-chat-header">'
                    '<div class="chef-chat-badge">👨‍🍳</div>'
                    '<div>'
                    '<div class="section-title" style="margin:0;">Asisten Chef</div>'
                    '<div class="chef-fab-hint">Chef Ari siap membantu resep ini dengan konteks bahan dan langkah.</div>'
                    '</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="chef-chat-box">'
                    '<div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:14px;">'
                    '<strong>Konsep resep:</strong><br>'
                    f'{recipe_context.replace("\n", "<br>")}'
                    '</div>'
                    '</div>', unsafe_allow_html=True)

        if not st.session_state.chef_chat_history:
            st.markdown('<div style="font-size:0.9rem; color:var(--text-muted); margin-bottom:12px;">'
                        'Mulai dengan menanyakan tips, substitusi, atau modifikasi resep ini.</div>', unsafe_allow_html=True)

        for idx, msg in enumerate(st.session_state.chef_chat_history):
            if msg["role"] == "user":
                user_content = html.escape(msg['content'] or '', quote=False).replace('\n', '<br>')
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-end; margin-bottom:12px;'>
                    <div>
                        <div class='chat-name' style='text-align:right; color:var(--text-muted);'>KAMU</div>
                        <div class='chat-bubble-user'>{user_content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                tool_badges = ""
                chef_tools = st.session_state.get("chef_chat_tools", [])
                if chef_tools and idx < len(chef_tools) and chef_tools[idx]:
                    badges_html = ""
                    for t in chef_tools[idx]:
                        t_name = t["name"].replace("_", " ").title()
                        t_arg  = html.escape(str(t.get("args", {}).get("nama_bahan", "")), quote=False)
                        badges_html += (
                            f"<span style='display:inline-flex;align-items:center;gap:4px;"
                            f"font-size:0.65rem;padding:3px 10px;border-radius:20px;"
                            f"background:rgba(106,175,106,0.12);border:1px solid rgba(106,175,106,0.35);"
                            f"color:var(--accent-green);margin:0 4px 4px 0;'>"
                            f"🔧 {t_name}"
                            f"{f' → <em>{t_arg}</em>' if t_arg else ''}"
                            f"</span>"
                        )
                    tool_badges = (
                        f"<div style='margin-bottom:6px;'>"
                        f"<span style='font-size:0.6rem;color:var(--text-dim);'>TOOLS DIPANGGIL:</span><br>"
                        f"{badges_html}</div>"
                    )

                # ── Bubble Chat ──
                safe_content = clean_chat_content(msg['content']).replace('\n', '<br>')
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-start; margin-bottom:12px;'>
                    <div style='max-width:80%;'>
                        <div class='chat-name' style='color:var(--accent-warm);'> 👨‍🍳 CHEF ARI {tool_badges}</div>                         
                        <div class='chat-bubble-ai'>{safe_content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if (st.session_state.chef_chat_history and
                st.session_state.chef_chat_history[-1]["role"] == "user"):
            with st.spinner("🤖 Chef Ari sedang berpikir..."):
                reply, tools_used = chef_agent.run_agent(
                    st.session_state.chef_chat_history,
                    recipe_context=recipe_context,
                )
            reply = clean_chat_content(reply)
            st.session_state.chef_chat_history.append({
                "role": "assistant",
                "content": reply,
            })
            if "chef_chat_tools" not in st.session_state:
                st.session_state.chef_chat_tools = []
            st.session_state.chef_chat_tools.append(tools_used if tools_used else [])
            st.rerun()

        st.markdown("---")
        with st.form("chef_chat_form", clear_on_submit=True):
            col_inp, col_send = st.columns([5, 1])
            with col_inp:
                user_msg = st.text_input(
                    "Pesan",
                    placeholder="Tanya Chef Ari tentang resep ini...",
                    label_visibility="collapsed",
                    key="chef_chat_input",
                )
            with col_send:
                send_btn = st.form_submit_button("Kirim 📤", use_container_width=True)

        if send_btn and user_msg.strip():
            st.session_state.chef_chat_history.append({"role": "user", "content": user_msg.strip()})
            st.rerun()

        if st.session_state.chef_chat_history:
            if st.button("🗑 Hapus Riwayat Chef Ari", key="chef_chat_clear"):
                st.session_state.chef_chat_history = []
                st.session_state.chef_chat_tools = []
                st.rerun()


def render(recipes_df, steps_df, grouped_ings, nutrition_df, chef_agent):
    rid = st.session_state.selected_recipe

    if not rid:
        st.info("Pilih resep dari halaman Cari Resep terlebih dahulu.")
        if st.button("← Kembali ke Pencarian"):
            st.session_state.page = "Cari Resep"
            st.rerun()
        return

    recipe_row = recipes_df[recipes_df["recipe_id"] == rid]
    if recipe_row.empty:
        st.error("Resep tidak ditemukan.")
        return

    recipe_row = recipe_row.iloc[0]

    if st.button("← Kembali ke Hasil Pencarian"):
        st.session_state.page = "Cari Resep"
        st.rerun()

    # ── Gambar Resep ──
    url_col = recipe_row.get("url", "")
    show_recipe_image(url_col, str(recipe_row["title"]), height=280)

    cookpad_url = url_to_cookpad(url_col)
    if cookpad_url:
        st.markdown(
            f'<div style="margin-bottom:8px;">'
            f'<a href="{cookpad_url}" target="_blank" '
            f'style="font-size:0.75rem; color:var(--text-muted); text-decoration:none;">'
            f'🔗 Lihat resep asli di Cookpad</a></div>',
            unsafe_allow_html=True,
        )

    # ── Header ──
    st.markdown(f"""
    <div style='margin: 8px 0 8px;'>
        <div style='font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em;'>
            {recipe_row.get('category', '')}
        </div>
        <div style='font-family: Playfair Display, serif; font-size: 2rem; font-weight: 800;
             color: var(--text-primary); line-height: 1.2; margin: 6px 0;'>
            {recipe_row['title']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='recipe-meta' style='margin-bottom:20px;'>
        <span class='meta-chip'>⏱ {int(recipe_row.get('cook_time_min', 0))} menit</span>
        <span class='meta-chip'>⚡ {recipe_row.get('difficulty', '-')}</span>
        <span class='meta-chip'>👥 {int(recipe_row.get('servings', 2))} porsi</span>
        <span class='meta-chip'>❤ {int(recipe_row.get('loves', 0))} suka</span>
        <span class='meta-chip'>🥬 {int(recipe_row.get('ingredient_count', 0))} bahan</span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🥬 Bahan & Langkah", "📊 Nutrisi", "🔄 Substitusi Bahan"])

    # ── TAB 1: Bahan & Langkah ──
    with tab1:
        col_ing, col_steps = st.columns([1, 2])

        with col_ing:
            st.markdown('<div class="section-title" style="font-size:1rem;">Bahan-Bahan</div>', unsafe_allow_html=True)
            recipe_ings   = grouped_ings.get(rid, [])
            user_ings_set = set(st.session_state.last_ingredients)
            for ing in recipe_ings:
                ing_str = str(ing)
                matched = any(
                    ut.lower() in ing_str.lower() or ing_str.lower() in ut.lower()
                    for ut in user_ings_set
                )
                color = "var(--accent-green)" if matched else "var(--text-primary)"
                icon  = "✅" if matched else "○"
                st.markdown(f"""
                <div style='display:flex; align-items:center; gap:8px; padding:6px 0;
                     border-bottom: 1px solid var(--border); font-size:0.84rem; color:{color};'>
                    <span>{icon}</span><span>{ing_str}</span>
                </div>
                """, unsafe_allow_html=True)

        with col_steps:
            st.markdown('<div class="section-title" style="font-size:1rem;">Langkah Memasak</div>', unsafe_allow_html=True)
            recipe_steps = steps_df[steps_df["recipe_id"] == rid].sort_values("step_number")
            if recipe_steps.empty:
                st.info("Langkah memasak tidak tersedia untuk resep ini.")
            else:
                for _, step_row in recipe_steps.iterrows():
                    st.markdown(f"""
                    <div class='step-card'>
                        <div class='step-num'>{int(step_row['step_number'])}</div>
                        <div class='step-text'>{step_row['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── TAB 2: Nutrisi ──
    with tab2:
        st.markdown('<div class="section-title" style="font-size:1rem;">Estimasi Nutrisi</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:16px;">*Estimasi berdasarkan 100g per bahan yang teridentifikasi dalam database nutrisi.</div>', unsafe_allow_html=True)

        nut      = estimate_nutrition(rid, grouped_ings, nutrition_df)
        servings = max(int(recipe_row.get("servings", 2)), 1)

        col_nut1, col_nut2 = st.columns(2)
        with col_nut1:
            st.markdown(f"""
            <div class='metric-card' style='margin-bottom:12px;'>
                <div class='metric-value'>{nut['calories']:.0f}</div>
                <div class='metric-label'>Total Kalori (kcal)</div>
            </div>
            <div class='metric-card'>
                <div class='metric-value'>{nut['calories']/servings:.0f}</div>
                <div class='metric-label'>Per Porsi (kcal)</div>
            </div>
            """, unsafe_allow_html=True)
        with col_nut2:
            for name, val, color, ref in [
                ("Protein", nut["protein"], "var(--accent-green)", 50),
                ("Lemak",   nut["fat"],     "var(--accent-orange)", 70),
                ("Karbo",   nut["carbs"],   "var(--accent-warm)", 300),
                ("Serat",   nut["fiber"],   "var(--accent-blue)", 25),
            ]:
                pct_bar = min(int(val / ref * 100), 100)
                st.markdown(f"""
                <div class='nut-row'>
                    <div class='nut-label'>{name}</div>
                    <div class='nut-bar-bg'>
                        <div class='nut-bar-fill' style='width:{pct_bar}%; background:{color};'></div>
                    </div>
                    <div class='nut-val'>{val:.1f}g</div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 3: Substitusi ──
    with tab3:
        recipe_ings_list = [str(i) for i in grouped_ings.get(rid, [])]
        _, _, miss = ingredient_match_score(st.session_state.last_ingredients, recipe_ings_list)

        if not miss:
            st.success("🎉 Kamu punya semua bahan yang dibutuhkan!")
        else:
            st.markdown(f"""
            <div class='substitution-warning'>
                ⚠️ Kamu kurang <strong>{len(miss)}</strong> bahan: {', '.join(miss[:8])}
            </div>
            """, unsafe_allow_html=True)

            hints = get_substitution_hint(miss)
            if hints:
                st.markdown('<div class="section-title" style="font-size:1rem; margin-bottom:8px;">💡 Saran Substitusi</div>', unsafe_allow_html=True)
                st.markdown(hints)
            else:
                st.info("Tidak ada data substitusi untuk bahan yang kurang. Tanyakan ke Asisten Chef!")

            if st.button("🤖 Tanya Asisten Chef tentang Substitusi"):
                miss_text_prompt = ", ".join(miss[:6])
                st.session_state.chef_chat_history.append({
                    "role": "user",
                    "content": f"Saya ingin membuat '{recipe_row['title']}' tapi kekurangan bahan: {miss_text_prompt}. Apa saja alternatif penggantinya?"
                })
                st.session_state.show_chef_chat = True
                st.rerun()

    # ── Embedded AI Chef Chat di bawah detail resep ──
    render_chef_chat(recipe_row, grouped_ings, chef_agent, rid)

    button_label = "✕" if st.session_state.show_chef_chat else "👨‍🍳"
    button_help = "Tutup Asisten Chef" if st.session_state.show_chef_chat else "Klik untuk Membuka Asisten Chef di bawah Detail Resep"

    st.markdown("""
    <style>
    .st-key-chef_fab .stButton button {
        position: fixed !important;
        bottom: 1.8rem !important;
        right: 1.8rem !important;
        min-width: 60px !important;
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        font-size: 1.6rem !important;
        line-height: 1 !important;
        padding: 0 !important;
        background: linear-gradient(135deg, var(--accent-warm), var(--accent-orange)) !important;
        color: #000 !important;
        border: none !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.25) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 9999 !important;
    }
    .st-key-chef_fab .stButton button:hover {
        transform: translateY(-2px) !important;
        opacity: 0.95 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button(button_label, key="chef_fab", help=button_help):
        st.session_state.show_chef_chat = not st.session_state.show_chef_chat
        st.rerun()

  
