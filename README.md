# 🍳 CookSnap — Sistem Rekomendasi Resep Berbasis Bahan Makanan

## Demo
https://cooksnap.streamlit.app/

## Deskripsi Singkat

**CookSnap** adalah aplikasi web berbasis Streamlit yang merekomendasikan resep masakan Indonesia berdasarkan bahan yang kamu miliki. Aplikasi ini menggabungkan:
- **Retrieval ganda**: BM25-Okapi + TF-IDF untuk menemukan resep paling relevan dari ribuan data
- **Agentic Chef AI**: Chef Ari menggunakan Groq LLaMA 3.3 dengan function calling untuk mencari substitusi bahan, info nutrisi, dan rekomendasi resep
- **Estimasi nutrisi otomatis**: kalkulasi kalori, protein, lemak, karbohidrat, dan serat per resep

> **Misi**: Membantu pengguna memasak lebih cerdas, memaksimalkan bahan yang tersedia, dan mengurangi food waste.

---

## Fitur Utama

### 1. 🔍 Pencarian Bahan ke Resep

Masukkan bahan yang ada di dapur, lalu CookSnap akan mencari resep yang cocok menggunakan algoritma dual retrieval:

| Algoritma | Pendekatan | Kegunaan |
|-----------|-----------|----------|
| **BM25-Okapi** | Probabilistic term frequency | Menangkap relevansi kata kunci bahan |
| **TF-IDF** | Vector space model | Menilai kecocokan konteks bahan |

Hasil pencarian mempertimbangkan:
- **Kecocokan bahan** (`match_ratio`)
- **Popularitas resep** (`loves`)
- **Boost bahan utama** untuk bahan pertama yang dimasukkan pengguna

#### Filter Pencarian
- Tingkat kesulitan
- Kategori masakan
- Maksimal waktu memasak
- Jumlah hasil yang ditampilkan

### 2. 🧠 Asisten Chef Virtual "Chef Ari"

Chef Ari adalah asisten AI yang menggunakan **Groq LLaMA 3.3** dan schema function calling. Ia otomatis memutuskan apakah perlu memanggil tools lokal saat menjawab:

| Tool | Fungsi |
|------|--------|
| 🔄 `cari_substitusi_bahan` | Substitusi bahan masakan Indonesia |
| 📊 `cari_info_nutrisi` | Info nutrisi bahan makanan dari database lokal |
| 🔎 `cari_resep` | Rekomendasi resep dari bahan tertentu |

Chef Ari dapat menjawab pertanyaan seperti:
- "Apa pengganti santan?"
- "Berapa kalori dalam ayam?"
- "Resep apa yang bisa dibuat dari tempe?"

### 3. 📊 Estimasi Nutrisi Resep

Setiap resep pada halaman detail menampilkan estimasi nutrisi:
- Kalori total dan per porsi
- Protein
- Lemak
- Karbohidrat
- Serat

Estimasi dihitung berdasarkan data nutrisi lokal dan bahan resep.

### 4. 📖 Detail Resep Lengkap

Halaman detail resep menyajikan:
- Gambar resep dari Cookpad via OG metadata
- Informasi resep: kategori, waktu, kesulitan, porsi, likes
- Daftar bahan dengan indikator bahan yang sudah dimiliki
- Langkah memasak terurut
- Tab nutrisi dan substitusi bahan
- Embedded chat Chef Ari untuk tips resep khusus

### 5. 🌗 Tema Gelap / Terang

CookSnap mendukung mode gelap dan terang yang dapat diubah dari sidebar.

### 6. 🏠 Beranda Interaktif

Halaman beranda memuat:
- Hero section dengan ringkasan fitur
- Quick search bahan
- Statistik resep, bahan, dan kategori
- Resep terpopuler
- Jelajahi kategori resep

---

## Teknologi yang Digunakan

### Backend & Framework

| Teknologi | Fungsi | Versi |
|-----------|--------|-------|
| **Python** | Bahasa utama | 3.8+ |
| **Streamlit** | UI interaktif | ≥ 1.35.0 |
| **Pandas** | Manipulasi data | ≥ 2.0.0 |
| **NumPy** | Komputasi numerik | ≥ 1.24.0 |
| **scikit-learn** | TF-IDF + cosine similarity | ≥ 1.3.0 |

### AI & NLP

| Teknologi | Fungsi |
|-----------|--------|
| **BM25-Okapi** | Retrieval custom di `models.py` |
| **TF-IDF** | Perbandingan similarity vektor |
| **Groq API** | Inference LLM cloud |
| **LLaMA 3.3** | AI chat assistant |

### Data & Storage

| Komponen | Format | Deskripsi |
|----------|--------|-----------|
| `recipes.csv` | CSV | Metadata resep |
| `ingredients.csv` | CSV | Bahan resep per resep |
| `nutrition.csv` | CSV | Data nutrisi bahan |
| `steps.csv` | CSV | Langkah memasak |

### Frontend & Styling

| Teknologi | Fungsi |
|-----------|--------|
| **Inline CSS** | Styling custom Streamlit |
| **Google Fonts** | Tipografi khas |
| **CSS Variables** | Theme management |

---

## Arsitektur Aplikasi

```
                      ┌──────────────────────────┐
                      │      Streamlit UI        │
                      │   (app.py + pages/*)     │
                      └──────────┬───────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │                     │                     │
┌──────────▼────────┐  ┌─────────▼──────────┐  ┌──────────▼──────────┐
│   pages/home.py   │  │  pages/search.py   │  │  pages/detail.py    │
│  Beranda + quick  │  │  Pencarian bahan,  │  │  Detail resep,      │
│      search       │  │  filter, model     │  │  nutrisi, substitusi│
└──────────┬────────┘  │  comparison        │  │  & embedded chat    │
           │           └─────────┬──────────┘  └──────────┬──────────┘
           │                     │                        │
           │                     │                        │
           │           ┌─────────▼───────────┐            │
           │           │     models.py       │            │
           │           │ BM25 + TF-IDF       │            │
           │           │ search, ranking,    │            │
           │           │ nutrition estimate  │            │
           │           └─────────┬───────────┘            │
           │                     │                        │
           │                     │                        │
           │           ┌─────────▼───────────┐            │
           │           │    ai_agent.py      │◄───────────┘
           │           │ Chef Ari + agentic  │
           │           │ tools / Groq API    │
           │           └─────────┬───────────┘
           │                     │
           │                     │
           │      ┌──────────────▼────────────────┐
           │      │          Data Layer           │
           │      │ recipes.csv, ingredients.csv, │
           └──────│ nutrition.csv, steps.csv      │
                  └───────────────────────────────┘
```
Deskripsi struktur folder:
- `app.py` adalah entry point utama yang mengatur halaman Streamlit dan routing.
- Folder `pages/` berisi modul halaman UI: `home.py`, `search.py`, `detail.py`, dan `chat.py`.
- `models.py` menyimpan logika retrieval, scoring, dan estimasi nutrisi.
- `ai_agent.py` mengelola Chef Ari, Groq API, dan function calling tools.
- `styles.py` dan `utils.py` menyediakan styling dan utilitas helper.
- Folder `Data/` menyimpan dataset CSV yang digunakan aplikasi.
---

## Halaman Aplikasi

| Halaman | Deskripsi |
|---------|-----------|
| 🏠 **Beranda** | Hero, quick search, resep populer, dan kategori |
| 🔍 **Cari Resep** | Input bahan, filter, dual retrieval, dan hasil rekomendasi |
| 📖 **Detail Resep** | Info resep, bahan cocok, langkah memasak, nutrisi, substitusi, Chef Ari |

---

## Cara Menjalankan

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup API Key

Buat file `.env` di root folder:

```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxxx
```

> Dapatkan kunci API di `https://console.groq.com`.

### 3. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka `http://localhost:8501` di browser.

---

## Sumber Data

- **Resep**: Cookpad Indonesia, https://www.kaggle.com/datasets/canggih/indonesian-food-recipes
- **Nutrisi**: Database nutrisi bahan masakan lokal
- **Gambar**: Diambil dari halaman Cookpad via OG metadata

---

## Catatan Teknis

- `models.py` mengimplementasikan **BM25-Okapi** custom dan **TF-IDF** untuk pencarian bahan.
- `ai_agent.py` mengendalikan Chef Ari dengan **Groq API** dan **function calling**.
- `pages/search.py` menggunakan filter kategori, kesulitan, waktu masak, dan main ingredient boost.
- `pages/detail.py` menampilkan bahan yang cocok, langkah, nutrisi, substitusi, dan embedded chat.
- `load_data` mencari data di folder `Data/` atau `data/data_clean/`.
