"""
models.py — CookSnap
Algoritma retrieval (BM25, TF-IDF), pencarian resep,
estimasi nutrisi, dan fungsi-fungsi helper.
"""

from __future__ import annotations

import math
import os
import re
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    return re.sub(r'[^\w\s]', '', text.lower()).strip()


def canonicalize(name: str) -> str:
    """Return a cleaned ingredient string with brand/seasoning tokens removed.

    Examples: 'Royco ayam' -> 'ayam', 'Kaldu ayam bubuk' -> 'ayam'
    """
    if not name:
        return ""
    name = normalize(name)
    # tokens that usually indicate seasoning, brand, or packaging
    remove_tokens = {
        'royco', 'masako', 'sasa', 'kaldu', 'bumbu', 'penyedap', 'sachet',
        'serbuk', 'bubuk', 'instan', 'rasa', 'micin', 'msg', 'penyedap',
        'bumbu', 'bumbu', 'bumbuinstan'
    }
    parts = [p for p in name.split() if p not in remove_tokens]
    return ' '.join(parts)


def tokenize_ingredient(name: str) -> List[str]:
    # Tokenize after canonicalizing ingredient to remove brand/seasoning words
    name = canonicalize(name)
    tokens = name.split()
    stopwords = {'dan', 'atau', 'untuk', 'yang', 'dengan', 'ke', 'di', 'dari', 'sesuai', 'selera'}
    return [t for t in tokens if t not in stopwords and len(t) > 1]


def ingredient_match_score(
    user_ingredients: List[str],
    recipe_ingredients: List[str],
) -> Tuple[float, List[str], List[str]]:
    have, miss = [], []

    # Canonicalize user ingredients and build a set of tokens for matching
    user_tokens = set()
    for u in user_ingredients:
        for t in tokenize_ingredient(u):
            user_tokens.add(t)

    for ri in recipe_ingredients:
        ri_tokens = tokenize_ingredient(ri)

        # Exact token overlap
        matched = any(t in user_tokens for t in ri_tokens)

        # Fallback: substring match between normalized forms (handles 'royco ayam' vs 'ayam')
        if not matched:
            ri_norm = normalize(ri)
            for ut in user_tokens:
                if ut in ri_norm or ri_norm in ut:
                    matched = True
                    break

        if matched:
            have.append(ri)
        else:
            miss.append(ri)
    total = len(recipe_ingredients)
    ratio = len(have) / total if total > 0 else 0
    return ratio, have, miss


def is_strong_main_ingredient(ingredient: str, main_tokens: List[str]) -> bool:
    if not ingredient or not main_tokens:
        return False
    canonical = canonicalize(ingredient)
    tokens = canonical.split()
    if not tokens:
        return False

    main = main_tokens[0]
    weak_prefixes = {
        'sosis', 'telur', 'telor', 'perasa', 'kaldu', 'saus', 'sambal', 'kornet',
        'nugget', 'bakso', 'pangsit', 'daging', 'tepung', 'miskin', 'bumbu',
        'royco', 'masako', 'sasa', 'sosis ayam', 'telor ayam', 'perasa ayam'
    }

    if tokens == [main]:
        return True
    if tokens[0] == main:
        return True
    if tokens[-1] == main and tokens[0] not in weak_prefixes:
        return True
    return False


def url_to_cookpad(url_col: str) -> str:
    if not url_col or pd.isna(url_col):
        return ""
    m = re.match(r'/id/resep/(\d+)', str(url_col))
    if m:
        return f"https://cookpad.com/id/resep/{m.group(1)}"
    return ""


def get_category_emoji(category: str) -> str:
    mapping = {
        "Daging": "🥩", "Sayur": "🥦", "Seafood": "🦐", "Ayam": "🍗",
        "Nasi":   "🍚", "Mie":   "🍜", "Kue":    "🍰", "Minuman": "🥤",
        "Snack":  "🍿", "Sup":   "🍲", "Goreng":  "🍳", "Telur":   "🥚",
        "Tahu":   "🟡", "Tempe": "🟫", "Ikan":    "🐟",
    }
    for k, v in mapping.items():
        if k.lower() in category.lower():
            return v
    return "🍽"


# ─────────────────────────────────────────────────────────────
# BM25 IMPLEMENTATION
# ─────────────────────────────────────────────────────────────

class BM25Okapi:
    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.65):
        self.k1 = k1
        self.b  = b
        self.corpus_size = len(corpus)
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.doc_len: List[int] = []
        self.avgdl: float = 0.0
        self._build(corpus)

    def _build(self, corpus: List[List[str]]):
        nd: Dict[str, int] = defaultdict(int)
        total_len = 0
        for doc in corpus:
            freq: Dict[str, int] = Counter(doc)
            self.doc_freqs.append(freq)
            self.doc_len.append(len(doc))
            total_len += len(doc)
            for term in freq:
                nd[term] += 1
        self.avgdl = total_len / self.corpus_size if self.corpus_size else 1
        for term, n in nd.items():
            self.idf[term] = math.log(
                (self.corpus_size - n + 0.5) / (n + 0.5) + 1
            )

    def get_scores(self, query: List[str]) -> np.ndarray:
        scores = np.zeros(self.corpus_size)
        for term in query:
            if term not in self.idf:
                continue
            idf_val = self.idf[term]
            for i, freq in enumerate(self.doc_freqs):
                tf = freq.get(term, 0)
                if tf == 0:
                    continue
                dl = self.doc_len[i]
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                scores[i] += idf_val * (tf * (self.k1 + 1)) / denom
        return scores

    def get_top_n(self, query: List[str], n: int = 10) -> List[int]:
        scores = self.get_scores(query)
        return np.argsort(scores)[::-1][:n].tolist()


# ─────────────────────────────────────────────────────────────
# TF-IDF IMPLEMENTATION
# ─────────────────────────────────────────────────────────────

class TFIDFRetriever:
    """TF-IDF retriever untuk perbandingan dengan BM25."""

    def __init__(self, corpus: List[List[str]]):
        self.corpus = corpus
        self.vectorizer = TfidfVectorizer(tokenizer=lambda x: x, lowercase=False)
        self.doc_vectors = None
        self._build()

    def _build(self):
        corpus_text = [" ".join(doc) for doc in self.corpus]
        self.doc_vectors = self.vectorizer.fit_transform(corpus_text)

    def get_scores(self, query: List[str]) -> np.ndarray:
        query_text = " ".join(query)
        query_vec = self.vectorizer.transform([query_text])
        scores = cosine_similarity(query_vec, self.doc_vectors).flatten()
        return scores

    def get_top_n(self, query: List[str], n: int = 10) -> List[int]:
        scores = self.get_scores(query)
        return np.argsort(scores)[::-1][:n].tolist()


# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_data():
    base_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data"),
        "data/data_clean",
        "data\\data_clean",
        "Data",
        ".",
    ]
    for base in base_paths:
        try:
            recipes     = pd.read_csv(os.path.join(base, "recipes.csv"))
            ingredients = pd.read_csv(os.path.join(base, "ingredients.csv"))
            nutrition   = pd.read_csv(os.path.join(base, "nutrition.csv"))
            steps       = pd.read_csv(os.path.join(base, "steps.csv"))
            return recipes, ingredients, nutrition, steps
        except FileNotFoundError:
            continue
    raise FileNotFoundError("Data CSV tidak ditemukan. Letakkan di folder Data/ atau data/data_clean/")


@st.cache_resource(show_spinner=False)
def build_index(ingredients_df: pd.DataFrame):
    grouped = (
        ingredients_df.groupby("recipe_id")["ingredient_name"]
        .apply(list)
        .to_dict()
    )
    recipe_ids = list(grouped.keys())
    corpus = []
    for rid in recipe_ids:
        tokens = []
        for ing in grouped[rid]:
            tokens.extend(tokenize_ingredient(str(ing)))
        corpus.append(tokens)
    bm25  = BM25Okapi(corpus)
    tfidf = TFIDFRetriever(corpus)
    return bm25, tfidf, recipe_ids, grouped


# ─────────────────────────────────────────────────────────────
# RECIPE SEARCH
# ─────────────────────────────────────────────────────────────

def search_recipes(
    user_ingredients: List[str],
    recipes_df: pd.DataFrame,
    ingredients_df: pd.DataFrame,
    bm25: BM25Okapi,
    tfidf: TFIDFRetriever,
    recipe_ids: List[str],
    grouped_ingredients: Dict,
    top_k: int = 10,
    difficulty_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    max_time: Optional[int] = None,
    main_boost: float = 0.15,
) -> List[Dict]:
    results = []

    if not user_ingredients:
        for _, row in recipes_df.iterrows():
            if difficulty_filter and difficulty_filter != "Semua":
                if row.get("difficulty", "") != difficulty_filter:
                    continue
            if category_filter and category_filter != "Semua":
                if row.get("category", "") != category_filter:
                    continue
            if max_time is not None and max_time > 0:
                cook_time = row.get("cook_time_min", 999)
                if pd.notna(cook_time) and int(cook_time) > max_time:
                    continue

            rid = row["recipe_id"]
            recipe_ings = [str(i) for i in grouped_ingredients.get(rid, [])]
            loves = int(row.get("loves", 0)) if pd.notna(row.get("loves", 0)) else 0
            score = min(loves / 50, 0.3)

            results.append({
                "recipe_id":    rid,
                "title":        row["title"],
                "category":     row.get("category", "-"),
                "difficulty":   row.get("difficulty", "-"),
                "cook_time":    int(row.get("cook_time_min", 0)) if pd.notna(row.get("cook_time_min", 0)) else 0,
                "servings":     int(row.get("servings", 2)) if pd.notna(row.get("servings", 2)) else 2,
                "loves":        loves,
                "score":        score,
                "match_ratio":  0.0,
                "have":         [],
                "miss":         recipe_ings,
                "main_match":   False,
                "total_ings":   len(recipe_ings),
                "url":          row.get("url", ""),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results if top_k is None else results[:top_k]

    query_tokens = []
    for ing in user_ingredients:
        query_tokens.extend(tokenize_ingredient(ing))

    # Treat the first user ingredient as the "main" ingredient and boost recipes
    # that contain it. This improves ranking for searches where a primary
    # ingredient was intended by the user.
    main_ing = user_ingredients[0].strip().lower() if user_ingredients else None
    main_tokens = tokenize_ingredient(main_ing) if main_ing else []

    top_indices   = bm25.get_top_n(query_tokens, n=min(150, len(recipe_ids)))
    candidate_ids = [recipe_ids[i] for i in top_indices]

    for rid in candidate_ids:
        row = recipes_df[recipes_df["recipe_id"] == rid]
        if row.empty:
            continue
        row = row.iloc[0]

        if difficulty_filter and difficulty_filter != "Semua":
            if row.get("difficulty", "") != difficulty_filter:
                continue
        if category_filter and category_filter != "Semua":
            if row.get("category", "") != category_filter:
                continue
        if max_time is not None and max_time > 0:
            cook_time = row.get("cook_time_min", 999)
            if pd.notna(cook_time) and int(cook_time) > max_time:
                continue

        recipe_ings = [str(i) for i in grouped_ingredients.get(rid, [])]
        match_ratio, have, miss = ingredient_match_score(user_ingredients, recipe_ings)
        loves = int(row.get("loves", 0)) if pd.notna(row.get("loves", 0)) else 0

        # Check if the recipe contains the main ingredient (token-level match).
        main_match = False
        if main_tokens:
            for ri in recipe_ings:
                ri_norm = normalize(str(ri))
                for mt in main_tokens:
                    if mt in ri_norm or ri_norm in mt:
                        main_match = True
                        break
                if main_match:
                    break

        # Detect when the main ingredient is truly a main item, not a compound secondary.
        strong_main_match = any(is_strong_main_ingredient(ri, main_tokens) for ri in recipe_ings)
        if strong_main_match:
            applied_boost = float(main_boost) * 2.0
        elif main_match:
            applied_boost = float(main_boost)
        else:
            applied_boost = 0.0

        score = match_ratio * 0.5 + min(loves / 50, 0.2) + applied_boost

        results.append({
            "recipe_id":    rid,
            "title":        row["title"],
            "category":     row.get("category", "-"),
            "difficulty":   row.get("difficulty", "-"),
            "cook_time":    int(row.get("cook_time_min", 0)) if pd.notna(row.get("cook_time_min", 0)) else 0,
            "servings":     int(row.get("servings", 2)) if pd.notna(row.get("servings", 2)) else 2,
            "loves":        loves,
            "score":        score,
            "match_ratio":  match_ratio,
            "have":         have,
            "miss":         miss,
            "main_match":   main_match,
            "total_ings":   len(recipe_ings),
            "url":          row.get("url", ""),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ─────────────────────────────────────────────────────────────
# MODEL COMPARISON (BM25 vs TF-IDF)
# ─────────────────────────────────────────────────────────────

def compare_models(
    user_ingredients: List[str],
    bm25_model: BM25Okapi,
    tfidf_model: TFIDFRetriever,
    recipe_ids: List[str],
    top_k: int = 5,
) -> Dict:
    query_tokens = []
    for ing in user_ingredients:
        query_tokens.extend(tokenize_ingredient(ing))

    bm25_indices  = bm25_model.get_top_n(query_tokens, n=top_k)
    tfidf_indices = tfidf_model.get_top_n(query_tokens, n=top_k)
    bm25_scores   = bm25_model.get_scores(query_tokens)
    tfidf_scores  = tfidf_model.get_scores(query_tokens)

    return {
        "bm25_top":  [(recipe_ids[i], float(bm25_scores[i]))  for i in bm25_indices],
        "tfidf_top": [(recipe_ids[i], float(tfidf_scores[i])) for i in tfidf_indices],
    }


# ─────────────────────────────────────────────────────────────
# NUTRITION ESTIMATOR
# ─────────────────────────────────────────────────────────────

def estimate_nutrition(
    recipe_id: str,
    grouped_ings: Dict,
    nutrition_df: pd.DataFrame,
) -> Dict:
    ings   = grouped_ings.get(recipe_id, [])
    totals = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "fiber": 0.0}
    nut_map = {row["ingredient_name"]: row for _, row in nutrition_df.iterrows()}
    for ing in ings:
        ing_norm = normalize(str(ing))
        matched  = None
        for key in nut_map:
            if normalize(key) in ing_norm or ing_norm in normalize(key):
                matched = nut_map[key]
                break
        if matched is not None:
            g = 100
            totals["calories"] += float(matched["calories_per_100g"]) * g / 100
            totals["protein"]  += float(matched["protein_g"])  * g / 100
            totals["fat"]      += float(matched["fat_g"])       * g / 100
            totals["carbs"]    += float(matched["carbs_g"])     * g / 100
            totals["fiber"]    += float(matched["fiber_g"])     * g / 100
    return totals
