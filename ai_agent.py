"""
ai_agent.py — CookSnap
Agentic Chef Assistant: Groq API, function calling, ChefAgent, SUBSTITUTION_KB.

Arsitektur Agentic:
  1. User query dikirim ke LLM beserta definisi tools
  2. LLM MEMUTUSKAN SENDIRI apakah perlu memanggil tool
  3. Jika ya → tool dieksekusi → hasilnya dikembalikan ke LLM
  4. LLM menghasilkan jawaban final berdasarkan tool results
  5. Jika tidak → LLM langsung menjawab

Tools yang tersedia:
  🔄 cari_substitusi_bahan  — cari alternatif pengganti bahan
  📊 cari_info_nutrisi      — info nutrisi bahan makanan
  🔍 cari_resep             — cari resep berdasarkan bahan
"""

from __future__ import annotations

import html
import json
import os
import re
from typing import List, Dict, Tuple, Optional

import pandas as pd
import requests

from models import normalize


# ─────────────────────────────────────────────────────────────
# LOAD ENV
# ─────────────────────────────────────────────────────────────

def load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()


# ─────────────────────────────────────────────────────────────
# GROQ API
# ─────────────────────────────────────────────────────────────

def _groq_request(
    messages: List[Dict],
    system: str = "",
    max_tokens: int = 1000,
    tools: Optional[List] = None,
    tool_choice: Optional[str] = None,
) -> Dict:
    """Raw Groq API request — returns full response dict."""
    api_key = os.environ.get("GROQ_API_KEY", "")
    api_url = os.environ.get("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    model   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        return {"error": "GROQ_API_KEY tidak ditemukan. Tambahkan di file .env"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    payload: Dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": full_messages,
        "temperature": 0.7,
    }
    if tools is not None:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice if tool_choice is not None else "auto"
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        return resp.json()
    except Exception as e:
        return {"error": f"Koneksi gagal: {str(e)}"}


def call_groq(messages: List[Dict], system: str = "", max_tokens: int = 1000) -> str:
    """Simple text-only Groq call (no tools)."""
    data = _groq_request(messages, system, max_tokens)
    if "error" in data and isinstance(data["error"], str):
        return f"⚠️ {data['error']}"
    if "choices" in data and data["choices"]:
        content = data["choices"][0]["message"].get("content", "")
        return content
    err_msg = data.get("error", {})
    if isinstance(err_msg, dict):
        return f"⚠️ Error dari API: {err_msg.get('message', str(data))}"
    return f"⚠️ Error dari API: {str(data)}"


# ─────────────────────────────────────────────────────────────
# SUBSTITUTION KNOWLEDGE BASE
# ─────────────────────────────────────────────────────────────

SUBSTITUTION_KB = {
    "santan":        ["susu evaporasi + kelapa parut kering", "santan kemasan instan"],
    "gula pasir":    ["madu", "gula aren", "sirup maple"],
    "cuka":          ["air jeruk nipis", "air jeruk lemon"],
    "kemiri":        ["kacang mete sangrai", "almond sangrai"],
    "terasi":        ["saus ikan", "pasta udang"],
    "daun salam":    ["daun bay laurel kering", "daun pandan (sedikit)"],
    "serai":         ["kulit lemon + jahe", "serai bubuk"],
    "kecap manis":   ["kecap asin + gula aren", "hoisin sauce"],
    "lengkuas":      ["jahe", "galangal powder"],
    "daun jeruk":    ["daun makrut kering", "kulit jeruk parut"],
    "tepung terigu": ["tepung beras", "tepung tapioka (untuk pengental)"],
    "mentega":       ["minyak goreng", "margarin"],
    "bawang bombai": ["bawang merah (lebih banyak)", "bawang daun"],
}


def get_substitution_hint(missing_ingredients: List[str]) -> str:
    hints = []
    for ing in missing_ingredients[:5]:
        ing_low = ing.lower()
        for key, subs in SUBSTITUTION_KB.items():
            if key in ing_low or ing_low in key:
                hints.append(f"**{ing}** → bisa diganti dengan: {', '.join(subs)}")
                break
    return "\n".join(hints) if hints else ""


# ─────────────────────────────────────────────────────────────
# TOOL DEFINITIONS (OpenAI-compatible function calling schema)
# ─────────────────────────────────────────────────────────────

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "cari_substitusi_bahan",
            "description": (
                "Mencari alternatif pengganti bahan masakan Indonesia. "
                "Gunakan tool ini ketika user bertanya tentang pengganti, "
                "substitusi, atau alternatif suatu bahan masakan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nama_bahan": {
                        "type": "string",
                        "description": "Nama bahan yang ingin dicari penggantinya, "
                                       "contoh: santan, kemiri, terasi, kecap manis",
                    }
                },
                "required": ["nama_bahan"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cari_info_nutrisi",
            "description": (
                "Mencari informasi nutrisi (kalori, protein, lemak, karbohidrat, serat) "
                "dari suatu bahan makanan berdasarkan database nutrisi lokal. "
                "Gunakan tool ini ketika user bertanya tentang kalori, gizi, nutrisi, "
                "protein, lemak, atau karbohidrat suatu bahan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nama_bahan": {
                        "type": "string",
                        "description": "Nama bahan makanan, contoh: ayam, beras, tempe, tahu",
                    }
                },
                "required": ["nama_bahan"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cari_resep",
            "description": (
                "Mencari daftar resep masakan yang menggunakan bahan tertentu "
                "dari database resep lokal (10.000+ resep Cookpad Indonesia). "
                "Gunakan tool ini ketika user bertanya resep apa yang bisa dibuat "
                "dari bahan tertentu, atau ingin rekomendasi resep."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nama_bahan": {
                        "type": "string",
                        "description": "Nama bahan utama untuk mencari resep, "
                                       "contoh: ayam, tempe, udang",
                    }
                },
                "required": ["nama_bahan"],
            },
        },
    },
]

CHEF_SYSTEM = """Kamu adalah Chef Ari, asisten koki virtual CookSnap yang ahli masakan Indonesia.
Kamu ramah, informatif, dan selalu memberikan jawaban praktis berbahasa Indonesia.

Spesialisasimu:
- Resep tradisional & modern Indonesia
- Substitusi bahan masakan
- Tips & teknik memasak
- Informasi nutrisi bahan makanan
- Mengurangi food waste

INSTRUKSI PENTING:
- Gunakan tools yang tersedia untuk menjawab pertanyaan yang relevan.
- Jika user bertanya tentang pengganti bahan → gunakan tool cari_substitusi_bahan.
- Jika user bertanya tentang nutrisi/kalori → gunakan tool cari_info_nutrisi.
- Jika user bertanya resep dari bahan tertentu → gunakan tool cari_resep.
- Untuk pertanyaan umum tentang memasak, jawab langsung tanpa tool.
- Berikan jawaban yang jelas, terstruktur, dan tidak terlalu panjang.
- Gunakan emoji sesekali agar lebih ramah.
- PENTING: Jangan pernah menyertakan tag HTML dalam jawabanmu.
- Jawab hanya dengan teks biasa dan tanda markdown yang diizinkan (bold, italic, bullet points).
- Jangan menulis tag pembuka atau penutup HTML apapun."""


# ─────────────────────────────────────────────────────────────
# CHEF AGENT
# ─────────────────────────────────────────────────────────────

class ChefAgent:
    """
    Agentic Chef Assistant — LLM memutuskan tool mana yang dipanggil.

    Alur kerja:
        User Query
            → LLM + Tool Definitions
            → LLM memilih tool (atau jawab langsung)
            → Tool dieksekusi
            → Hasil dikembalikan ke LLM
            → LLM menghasilkan jawaban final
    """

    def __init__(self, recipes_df, ingredients_df, grouped_ings, nutrition_df):
        self.recipes_df     = recipes_df
        self.ingredients_df = ingredients_df
        self.grouped_ings   = grouped_ings
        self.nutrition_df   = nutrition_df

    # ── TOOL 1: Substitusi Bahan ──
    def tool_cari_substitusi_bahan(self, nama_bahan: str) -> str:
        nama = nama_bahan.lower().strip()
        results = []
        for key, subs in SUBSTITUTION_KB.items():
            if key in nama or nama in key:
                results.append(f"- **{key}** bisa diganti dengan: {', '.join(subs)}")
        if results:
            return "Hasil pencarian substitusi bahan:\n" + "\n".join(results)
        return (
            f"Bahan '{nama_bahan}' tidak ditemukan di database substitusi lokal. "
            "Kamu bisa memberikan saran berdasarkan pengetahuan umum."
        )

    # ── TOOL 2: Info Nutrisi ──
    def tool_cari_info_nutrisi(self, nama_bahan: str) -> str:
        nama = nama_bahan.lower().strip()
        nut_map = {row["ingredient_name"]: row for _, row in self.nutrition_df.iterrows()}
        for key in nut_map:
            if nama in key.lower() or key.lower() in nama:
                row = nut_map[key]
                return (
                    f"Nutrisi **{key}** (per 100g):\n"
                    f"- Kalori: {float(row.get('calories_per_100g', 0)):.0f} kcal\n"
                    f"- Protein: {float(row.get('protein_g', 0)):.1f} g\n"
                    f"- Lemak: {float(row.get('fat_g', 0)):.1f} g\n"
                    f"- Karbohidrat: {float(row.get('carbs_g', 0)):.1f} g\n"
                    f"- Serat: {float(row.get('fiber_g', 0)):.1f} g"
                )
        return (
            f"Bahan '{nama_bahan}' tidak ditemukan di database nutrisi lokal. "
            "Kamu bisa memberikan estimasi berdasarkan pengetahuan umum."
        )

    # ── TOOL 3: Cari Resep ──
    def tool_cari_resep(self, nama_bahan: str) -> str:
        nama = nama_bahan.lower().strip()
        matches = []
        seen_ids = set()
        for rid, ings in self.grouped_ings.items():
            for ing in ings:
                if nama in str(ing).lower():
                    if rid in seen_ids:
                        break
                    seen_ids.add(rid)
                    row = self.recipes_df[self.recipes_df["recipe_id"] == rid]
                    if not row.empty:
                        r = row.iloc[0]
                        title = r["title"]
                        cat   = r.get("category", "-")
                        diff  = r.get("difficulty", "-")
                        loves = int(r.get("loves", 0))
                        matches.append(f"- **{title}** ({cat}, {diff}, ❤{loves})")
                        break
            if len(matches) >= 8:
                break
        if matches:
            return (
                f"Resep yang menggunakan '{nama_bahan}' "
                f"({len(matches)} ditemukan):\n" + "\n".join(matches)
            )
        return f"Tidak ditemukan resep dengan bahan '{nama_bahan}' di database."

    # ── Tool Dispatcher ──
    def execute_tool(self, tool_name: str, arguments: Dict) -> str:
        tool_map = {
            "cari_substitusi_bahan": self.tool_cari_substitusi_bahan,
            "cari_info_nutrisi":     self.tool_cari_info_nutrisi,
            "cari_resep":            self.tool_cari_resep,
        }
        fn = tool_map.get(tool_name)
        if fn is None:
            return f"Tool '{tool_name}' tidak dikenali."
        nama_bahan = arguments.get("nama_bahan", "")
        return fn(nama_bahan)

    # ── Agentic Loop ──
    def run_agent(self, chat_history: List[Dict], recipe_context: Optional[str] = None) -> Tuple[str, List[Dict]]:
        """
        Menjalankan agentic loop:
          1. Kirim query + tools ke LLM
          2. Jika LLM memilih tool → eksekusi → kirim hasil balik ke LLM
          3. LLM generate jawaban final

        Returns:
            (reply_text, tools_used)
            tools_used = [{"name": "...", "args": {...}, "result": "..."}]
        """
        tools_used = []
        system_prompt = CHEF_SYSTEM
        if recipe_context:
            system_prompt = (
                f"{CHEF_SYSTEM}\n\n"
                f"KONTEKS RESEP:\n{recipe_context}"
            )

        # Step 1: Kirim ke LLM dengan tool definitions
        data = _groq_request(
            messages=chat_history,
            system=system_prompt,
            max_tokens=1000,
            tools=AGENT_TOOLS,
        )

        if "error" in data and isinstance(data["error"], str):
            return f"⚠️ {data['error']}", []
        if "choices" not in data or not data["choices"]:
            err_msg = data.get("error", {})
            if isinstance(err_msg, dict):
                return f"⚠️ {err_msg.get('message', str(data))}", []
            return f"⚠️ {str(data)}", []

        choice  = data["choices"][0]
        message = choice["message"]

        # Step 2: Cek apakah LLM ingin memanggil tool
        tool_calls = message.get("tool_calls")

        if not tool_calls:
            # LLM langsung menjawab tanpa tool — kembalikan mentah, display layer yang bersihkan
            return message.get("content", ""), []

        # Step 3: Eksekusi setiap tool yang dipanggil LLM
        follow_up_messages = list(chat_history)
        follow_up_messages.append({
            "role": "assistant",
            "content": message.get("content") or "",
            "tool_calls": tool_calls,
        })

        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"]["arguments"])
            except (json.JSONDecodeError, KeyError):
                fn_args = {}

            tool_result = self.execute_tool(fn_name, fn_args)
            tools_used.append({
                "name":   fn_name,
                "args":   fn_args,
                "result": tool_result,
            })
            follow_up_messages.append({
                "role":         "tool",
                "tool_call_id": tc["id"],
                "content":      tool_result,
            })

        # Step 4: Kirim tool results ke LLM untuk jawaban final
        final_data = _groq_request(
            messages=follow_up_messages,
            system=CHEF_SYSTEM,
            max_tokens=1000,
        )

        if "choices" in final_data and final_data["choices"]:
            final_reply = final_data["choices"][0]["message"].get("content", "")
        else:
            final_reply = "\n\n".join(t["result"] for t in tools_used)

        return final_reply, tools_used
