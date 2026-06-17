"""
utils.py — CookSnap
Fungsi utilitas: fetch gambar dari Cookpad, render gambar resep.
"""

from __future__ import annotations

import re

import requests
import streamlit as st

from models import get_category_emoji, url_to_cookpad


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_cookpad_image(cookpad_url: str):
    if not cookpad_url:
        return None
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        res = requests.get(cookpad_url, headers=headers, timeout=5)
        if res.status_code == 200:
            m = re.search(r'<meta property="og:image" content="([^"]+)"', res.text)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


def show_recipe_image(url_col: str, title: str, height: int = 220):
    cookpad_url = url_to_cookpad(url_col)
    emoji   = get_category_emoji(title)
    img_url = fetch_cookpad_image(cookpad_url) if cookpad_url else None

    if img_url:
        st.markdown(f'''
        <div style="width:100%; height:{height}px; border-radius:12px; overflow:hidden;
             background:var(--bg-secondary); border:1px solid var(--border); margin-bottom:14px;">
            <img src="{img_url}" style="width:100%; height:100%; object-fit:cover;"
                 onerror="this.parentElement.innerHTML='<div style=\\'display:flex;align-items:center;justify-content:center;height:100%;font-size:4rem;\\'>{emoji}</div>'" />
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="recipe-image-placeholder" style="height:{height}px; margin-bottom:14px;">
            <span>{emoji}</span>
        </div>
        ''', unsafe_allow_html=True)
