"""
pages/chat.py — CookSnap
Halaman Asisten Chef: agentic chat dengan Groq LLaMA 3.3
dan 3 built-in tools (substitusi, nutrisi, cari resep).
"""

import html
import re
import streamlit as st


def clean_chat_content(content: str) -> str:
    text = html.unescape(content or '')
    text = re.sub(r'(?i)<br\s*/?>', '\n', text)
    text = re.sub(r'(?i)<p[^>]*>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = text.strip()
    # Escape any remaining HTML-sensitive characters before rendering inside a safe container.
    text = html.escape(text, quote=False)
    return text.replace('\n', '<br>')


def render(chef_agent):
    st.markdown('<div class="section-title">🤖 Asisten Chef Virtual</div>', unsafe_allow_html=True)
    st.markdown("""<div class="section-sub">
        Tanya apa saja seputar memasak — tips, substitusi bahan, teknik, atau modifikasi resep.<br>
        Ditenagai <strong style='color:var(--accent-warm);'>Groq LLaMA 3.3</strong> dengan
        <strong style='color:var(--accent-warm);'>Agentic Architecture</strong>
        (3 tools: Substitusi Bahan, Info Nutrisi, Cari Resep).
    </div>""", unsafe_allow_html=True)

    # ── Suggestion Chips (saat chat kosong) ──
    if not st.session_state.chat_history:
        st.markdown('<div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:10px;">💬 Mulai percakapan atau coba pertanyaan ini:</div>', unsafe_allow_html=True)
        suggestions = [
            "Apa pengganti santan untuk masakan berkuah?",
            "Berapa kalori dalam ayam?",
            "Resep apa yang bisa dibuat dari tempe?",
            "Tips agar ayam goreng crispy dan tidak berminyak?",
        ]
        cols_sug = st.columns(2)
        for i, sug in enumerate(suggestions):
            with cols_sug[i % 2]:
                if st.button(sug, key=f"sug_{i}"):
                    st.session_state.chat_history.append({"role": "user", "content": sug})

    # Pastikan semua jawaban assistant yang tersimpan sudah dibersihkan
    for msg in st.session_state.chat_history:
        if msg.get("role") == "assistant":
            msg["content"] = clean_chat_content(msg.get("content", ""))

    # ── Render Chat History ──
    chat_container = st.container()
    with chat_container:
        for idx, msg in enumerate(st.session_state.chat_history):
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
            elif msg["role"] == "assistant":
                # Tampilkan tool badges jika ada
                tool_badges = ""
                chat_tools = st.session_state.get("chat_tools", [])
                if chat_tools and idx < len(chat_tools) and chat_tools[idx]:
                    badges_html = ""
                    for t in chat_tools[idx]:
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

                safe_content = clean_chat_content(msg['content'])
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-start; margin-bottom:12px;'>
                    <div style='max-width:80%;'>
                        <div class='chat-name' style='color:var(--accent-warm);'>👨‍🍳 CHEF ARI</div>
                        {tool_badges}
                        <div class='chat-bubble-ai' style='white-space:pre-wrap; word-break:break-word;'>{safe_content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Auto-respond — Agentic Loop ──
    if (st.session_state.chat_history and
            st.session_state.chat_history[-1]["role"] == "user"):

        with st.spinner("🤖 Chef Ari sedang berpikir & memilih tools..."):
            reply, tools_used = chef_agent.run_agent(st.session_state.chat_history)

        reply = clean_chat_content(reply)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": reply,
        })
        if "chat_tools" not in st.session_state:
            st.session_state.chat_tools = []
        st.session_state.chat_tools.append(tools_used if tools_used else [])
        st.rerun()

    # ── Input Form ──
    st.markdown("---")
    with st.form("chat_form", clear_on_submit=True):
        col_inp, col_send = st.columns([5, 1])
        with col_inp:
            user_msg = st.text_input(
                "Pesan",
                placeholder="Tanya Chef Ari tentang memasak...",
                label_visibility="collapsed",
                key="chat_input",
            )
        with col_send:
            send_btn = st.form_submit_button("Kirim 📤", use_container_width=True)

    if send_btn and user_msg.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_msg.strip()})
        st.rerun()

    # ── Clear Chat ──
    if st.session_state.chat_history:
        if st.button("🗑 Hapus Riwayat Chat"):
            st.session_state.chat_history = []
            st.session_state.chat_tools   = []
            st.rerun()
