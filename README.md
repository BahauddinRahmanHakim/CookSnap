# 🍳 CookSnap — Sistem Rekomendasi Resep Berbasis Bahan Makanan

## Deskripsi Singkat

**CookSnap** adalah aplikasi web berbasis Streamlit yang merekomendasikan resep masakan Indonesia berdasarkan bahan makanan yang dimiliki pengguna. Sistem ini menggabungkan **dual information retrieval** (BM25 + TF-IDF), **asisten AI agentic** (Groq LLaMA 3.3), dan **estimasi nutrisi otomatis** untuk memberikan pengalaman memasak yang cerdas dan efisien.

> **Misi**: Membantu masyarakat Indonesia memasak lebih cerdas, mengurangi food waste, dan memaksimalkan bahan yang sudah tersedia di dapur.

---

## Fitur Utama

### 1. 🔍 Pencarian Resep Cerdas (Dual Retrieval)

Pengguna cukup memasukkan bahan yang dimiliki, dan sistem akan mencarikan resep yang paling cocok menggunakan **dua algoritma retrieval secara paralel**:

| Algoritma | Pendekatan | Keunggulan |
|-----------|-----------|------------|
| **BM25-Okapi** | Probabilistic term frequency | Relevansi tinggi untuk keyword matching |
| **TF-IDF + Cosine Similarity** | Vector space model | Kecocokan semantik antar bahan |

Hasil pencarian diurutkan berdasarkan:
- **Kecocokan bahan** (70%) — persentase bahan yang sudah dimiliki pengguna
- **Popularitas resep** (30%) — jumlah "loves" dari Cookpad

#### Filter Pencarian
- Tingkat kesulitan (Mudah / Sedang / Sulit)
- Kategori masakan
- Maksimal waktu memasak
- Jumlah hasil yang ditampilkan

### 2. 🤖 Asisten Chef AI (Agentic Architecture + Function Calling)

**Chef Ari** adalah asisten virtual yang menggunakan arsitektur **agentic** dengan **function calling** — LLM (Groq LLaMA 3.3) yang **memutuskan sendiri** kapan perlu memanggil tools lokal berdasarkan pertanyaan pengguna.

#### Tools yang Tersedia (3 tools):

| Tool | Fungsi | Contoh Trigger |
|------|--------|----------------|
| 🔄 `cari_substitusi_bahan` | Mencari alternatif pengganti bahan dari database lokal | "Apa pengganti santan?" |
| 📊 `cari_info_nutrisi` | Mengambil info nutrisi (kalori, protein, dll.) dari database | "Berapa kalori dalam ayam?" |
| 🔍 `cari_resep` | Mencari resep yang menggunakan bahan tertentu dari 10.000+ resep | "Resep apa dari tempe?" |

#### Alur Kerja Agentic (Function Calling):
```
User Query
    │
    ▼
┌──────────────────────────────────────────┐
│  Step 1: Kirim ke LLM + Tool Definitions │
│  (Groq LLaMA 3.3 + AGENT_TOOLS schema)  │
└──────────────────┬───────────────────────┘
                   │
          LLM MEMUTUSKAN SENDIRI
          ┌────────┴────────┐
          │                 │
     Tool Diperlukan    Jawab Langsung
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌──────────────┐
│ Step 2: Execute │  │ Direct Reply │
│ tool_calls dari │  │ tanpa tool   │
│ respons LLM     │  └──────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Step 3: Tool results dikirim balik  │
│ ke LLM sebagai context tambahan     │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Step 4: LLM menghasilkan jawaban    │
│ final yang menggabungkan:           │
│   • Data dari tool results          │
│   • Pengetahuan umum LLM           │
└─────────────────────────────────────┘
```

> **Penting**: LLM yang memutuskan tool mana yang dipanggil (via function calling), bukan hard-coded if/else. Ini adalah implementasi **true agentic architecture**.

#### Knowledge Base Substitusi Bahan
Sistem memiliki database substitusi bahan masakan Indonesia, misalnya:
- **Santan** → susu evaporasi + kelapa parut kering
- **Kecap manis** → kecap asin + gula aren
- **Kemiri** → kacang mete sangrai
- Dan 10+ bahan lainnya

### 3. 📊 Estimasi Nutrisi

Setiap resep dilengkapi estimasi nutrisi otomatis:
- **Kalori** (kcal) — total dan per porsi
- **Protein** (gram)
- **Lemak** (gram)
- **Karbohidrat** (gram)
- **Serat** (gram)

Estimasi dihitung berdasarkan 100g per bahan yang teridentifikasi dalam database nutrisi.

### 4. 📖 Detail Resep Lengkap

Halaman detail resep menampilkan:
- **Gambar resep** dari Cookpad (via OG image scraping)
- **Bahan-bahan** dengan penanda hijau (✅) untuk bahan yang sudah dimiliki
- **Langkah memasak** berurutan
- **Link ke Cookpad** untuk resep asli
- **Saran substitusi** untuk bahan yang kurang

### 5. 🌗 Dark / Light Mode

Toggle tema di sidebar untuk beralih antara:
- **Dark Mode** — tema gelap default, nyaman untuk mata
- **Light Mode** — tema terang untuk penggunaan di siang hari

### 6. 🏠 Beranda Interaktif

Halaman beranda menampilkan:
- **Hero section** dengan animasi dan statistik dataset
- **Quick search** — langsung cari resep dari beranda
- **Fitur unggulan** — penjelasan 3 fitur utama
- **Cara kerja** — panduan langkah penggunaan
- **Resep terpopuler** — 6 resep dengan likes tertinggi
- **Jelajahi kategori** — akses cepat ke kategori masakan

---

## Teknologi yang Digunakan

### Backend & Framework

| Teknologi | Fungsi | Versi |
|-----------|--------|-------|
| **Python** | Bahasa pemrograman utama | 3.8+ |
| **Streamlit** | Web framework untuk UI interaktif | ≥ 1.35.0 |
| **Pandas** | Manipulasi dan analisis data | ≥ 2.0.0 |
| **NumPy** | Komputasi numerik | ≥ 1.24.0 |
| **scikit-learn** | TF-IDF Vectorizer & Cosine Similarity | ≥ 1.3.0 |

### AI & NLP

| Teknologi | Fungsi |
|-----------|--------|
| **BM25-Okapi** | Information retrieval (implementasi custom) |
| **TF-IDF** | Vector space retrieval (via scikit-learn) |
| **Groq API** | Inference LLM cloud (gratis) |
| **LLaMA 3.3 70B** | Large Language Model untuk chat AI |

### Data & Storage

| Komponen | Format | Deskripsi |
|----------|--------|-----------|
| `recipes.csv` | CSV | Data resep (judul, kategori, waktu, kesulitan, dll.) |
| `ingredients.csv` | CSV | Data bahan per resep |
| `nutrition.csv` | CSV | Database nutrisi per bahan |
| `steps.csv` | CSV | Langkah-langkah memasak per resep |

### Frontend & Styling

| Teknologi | Fungsi |
|-----------|--------|
| **HTML/CSS** (inline Streamlit) | Layout dan styling custom |
| **Google Fonts** | Playfair Display (heading) + DM Sans (body) |
| **CSS Variables** | Dual theme system (dark/light) |
| **CSS Animations** | Hero glow, fade-in, shimmer effects |

---

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI                         │
│  ┌──────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐  │
│  │Beranda│ │Cari Resep│ │Detail Resep│ │Asisten Chef │  │
│  └──┬───┘ └────┬─────┘ └─────┬─────┘ └──────┬───────┘  │
│     │          │              │               │          │
├─────┴──────────┴──────────────┴───────────────┴─────────┤
│                   BUSINESS LOGIC                        │
│  ┌────────────┐ ┌────────────┐ ┌──────────────────────┐ │
│  │   BM25     │ │   TF-IDF   │ │    ChefAgent         │ │
│  │  (Custom)  │ │ (sklearn)  │ │  ┌────────────────┐  │ │
│  └─────┬──────┘ └─────┬──────┘ │  │ Substitusi KB  │  │ │
│        │              │        │  │ Nutrisi Tool   │  │ │
│        └──────┬───────┘        │  │ Search Tool    │  │ │
│               │                │  └────────┬───────┘  │ │
│         Search Engine          │           │          │ │
│                                │     Groq LLaMA 3.3  │ │
│                                └──────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                     DATA LAYER                          │
│  ┌──────────┐ ┌─────────────┐ ┌─────────┐ ┌─────────┐  │
│  │recipes   │ │ingredients  │ │nutrition│ │steps    │  │
│  │.csv      │ │.csv         │ │.csv     │ │.csv     │  │
│  └──────────┘ └─────────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Cara Kerja Detail

### 1. Proses Pencarian Resep

```
Input: "ayam, bawang putih, tomat"
         │
         ▼
┌─────────────────────┐
│  Tokenisasi Bahan   │  → normalize → split → filter stopwords
│  ["ayam", "bawang",│
│   "putih", "tomat"] │
└────────┬────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ BM25  │ │TF-IDF │
│ Score │ │ Score │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         ▼
┌─────────────────────┐
│  Top 150 Candidates │  ← BM25 primary ranking
│  + Filter           │  ← difficulty, category, time
│  + Match Score      │  ← % bahan cocok
│  + Popularity       │  ← loves dari Cookpad
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  Final Score =      │
│  match_ratio × 0.7  │
│  + popularity × 0.3 │
└────────┬────────────┘
         ▼
   Top-K Results
```

### 2. Proses Asisten Chef (Agentic + Function Calling)

```
User: "Apa pengganti santan?"
         │
         ▼
┌──────────────────────────────────────┐
│  ChefAgent.run_agent(chat_history)   │
│                                      │
│  Step 1: _groq_request(             │
│    messages = chat_history,          │
│    tools = AGENT_TOOLS               │  ← 3 tool definitions
│  )                                   │
└──────────────┬───────────────────────┘
               │
     LLM response berisi tool_calls?
       ┌───────┴───────┐
       │ Ya            │ Tidak
       ▼               ▼
┌──────────────┐ ┌─────────────┐
│ execute_tool │ │ Return      │
│ ("cari_      │ │ content     │
│  substitusi  │ │ langsung    │
│  _bahan",    │ └─────────────┘
│ {nama_bahan: │
│  "santan"})  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ Tool Result:                 │
│ "santan bisa diganti dengan: │
│  susu evaporasi + kelapa..." │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Step 4: _groq_request(       │
│   messages + tool_results    │  ← LLM buat jawaban final
│ )                            │
└──────────────────────────────┘
```

### 3. BM25-Okapi — Rumus Scoring

```
Score(D, Q) = Σ IDF(qi) × [ tf(qi, D) × (k1 + 1) ]
                           ─────────────────────────
                           tf(qi, D) + k1 × (1 - b + b × |D| / avgdl)

Dimana:
  • k1 = 1.5  (term frequency saturation)
  • b  = 0.65 (length normalization)
  • IDF(qi) = log((N - n + 0.5) / (n + 0.5) + 1)
```

---

## Struktur Folder

```
cooksnap3/
├── cooksnap_ver2.py          # Aplikasi utama (1882 baris)
├── requirements.txt          # Dependensi Python
├── .gitignore               # Git ignore rules
├── 1_data_cleaning.ipynb    # Notebook data cleaning
└── data/
    ├── data_clean/
    │   ├── recipes.csv       # ~10,000+ resep
    │   ├── ingredients.csv   # Bahan per resep
    │   ├── nutrition.csv     # Database nutrisi
    │   └── steps.csv         # Langkah memasak
    └── raw/                  # Data mentah (sebelum cleaning)
```

---

## Cara Menjalankan

### 1. Install Dependensi

```bash
pip install -r requirements.txt
```

### 2. Setup API Key (untuk Asisten Chef)

Buat file `.env` di root folder:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxx
```

> Dapatkan API key gratis di [console.groq.com](https://console.groq.com)

### 3. Jalankan Aplikasi

```bash
streamlit run cooksnap_ver2.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`.

---

## Halaman Aplikasi

| Halaman | Deskripsi |
|---------|-----------|
| 🏠 **Beranda** | Landing page dengan hero, quick search, fitur unggulan, resep terpopuler, dan kategori |
| 🔍 **Cari Resep** | Pencarian resep dengan input bahan, filter, dan perbandingan BM25 vs TF-IDF |
| 📖 **Detail Resep** | Gambar, bahan (dengan penanda), langkah, nutrisi, substitusi |
| 🤖 **Asisten Chef** | Chat AI dengan Chef Ari — substitusi, tips, nutrisi, tanya jawab masak |

---

## Sumber Data

- **Resep**: Scraping dari [Cookpad Indonesia](https://cookpad.com/id)
- **Nutrisi**: Database nutrisi bahan makanan Indonesia
- **Gambar**: Diambil real-time dari Cookpad via OG meta tag

---

## Dependensi

```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
python-dotenv>=1.0.0
requests>=2.28.0
```

---

## Catatan Teknis

- **BM25 diimplementasikan from scratch** (bukan library `rank-bm25`) untuk kontrol penuh parameter k1 dan b
- **TF-IDF menggunakan scikit-learn** `TfidfVectorizer` + `cosine_similarity`
- **Groq API dipanggil via `requests`** langsung (bukan SDK `groq`), untuk meminimalkan dependensi
- **Caching** menggunakan `@st.cache_data` dan `@st.cache_resource` untuk performa optimal
- **Gambar Cookpad** di-cache selama 24 jam (`ttl=86400`) untuk mengurangi request
- **Theme system** menggunakan CSS Variables yang di-switch berdasarkan `st.session_state`
