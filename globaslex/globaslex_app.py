#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GloBasLex Mini-Database - Streamlit App
Author: Minyogog Jean Baptiste
Date: 2026-05-14
Description: Interactive visualization of the GloBasLex SQLite database
"""

import streamlit as st
import sqlite3
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
from collections import Counter

# ==================== CONFIGURATION ====================

# Chemin absolu vers la base de donnees
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "globaslex.db")

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="GloBasLex Mini-Database",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F4E78;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666666;
        text-align: center;
        font-style: italic;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE CONNECTION ====================

@st.cache_resource
def get_connection():
    """Retourne une connexion SQLite persistante"""
    if not os.path.exists(DB_PATH):
        st.error("Base de donnees introuvable: {}".format(DB_PATH))
        st.stop()
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ==================== DATA FUNCTIONS ====================

def get_concepts():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM concepts ORDER BY swadesh_list_order", conn)
    return df

def get_translations(concept_id=None, language_id=None):
    conn = get_connection()
    query = """
    SELECT t.*, c.concept_label, c.concept_name, l.language_name, l.language_code
    FROM translations t
    JOIN concepts c ON t.concept_id = c.id
    JOIN languages l ON t.language_id = l.id
    """
    conditions = []
    if concept_id:
        conditions.append("t.concept_id = {}".format(concept_id))
    if language_id:
        conditions.append("t.language_id = {}".format(language_id))
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY c.swadesh_list_order, l.language_code"
    return pd.read_sql(query, conn)

def get_colexifications():
    conn = get_connection()
    query = """
    SELECT c.*, l.language_name, l.language_code
    FROM colexifications c
    JOIN languages l ON c.language_id = l.id
    ORDER BY l.language_name
    """
    return pd.read_sql(query, conn)

def get_languages():
    conn = get_connection()
    return pd.read_sql("SELECT * FROM languages ORDER BY language_name", conn)

def get_all_translations_flat():
    """Retourne toutes les traductions pour export CSV"""
    conn = get_connection()
    query = """
    SELECT 
        c.concept_label,
        c.swadesh_list_order,
        l.language_code,
        l.language_name,
        l.family,
        l.region,
        t.word,
        t.ipa,
        t.pos,
        t.morphology,
        t.colexification,
        t.source,
        t.annotator
    FROM translations t
    JOIN concepts c ON t.concept_id = c.id
    JOIN languages l ON t.language_id = l.id
    ORDER BY c.swadesh_list_order, l.language_code
    """
    return pd.read_sql(query, conn)

# ==================== HEADER ====================

st.markdown('<p class="main-header">GloBasLex Mini-Database</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">100 Swadesh Concepts x 6 Languages | IPA + Morphological Annotation<br>Built by Minyogog Jean Baptiste</p>', unsafe_allow_html=True)

# ==================== SIDEBAR ====================

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page:", [
    "Dashboard",
    "Search by Concept",
    "Search by Language",
    "Colexifications",
    "Network Analysis",
    "Download Data"
])

st.sidebar.markdown("---")
st.sidebar.info("""
**GloBasLex Mini-Database**
Built by Minyogog Jean Baptiste
University of Yaounde I
Language Technology Specialist
""")

# ==================== PAGE: DASHBOARD ====================

if page == "Dashboard":
    st.header("Project Overview")

    col1, col2, col3, col4 = st.columns(4)

    concepts_df = get_concepts()
    translations_df = get_translations()
    colex_df = get_colexifications()
    languages_df = get_languages()

    with col1:
        st.metric("Concepts", len(concepts_df))
    with col2:
        st.metric("Translations", len(translations_df))
    with col3:
        st.metric("Languages", len(languages_df))
    with col4:
        st.metric("Colexifications", len(colex_df))

    st.subheader("Language Coverage")
    lang_counts = translations_df.groupby('language_name').size().reset_index(name='count')
    st.bar_chart(lang_counts.set_index('language_name'))

    st.subheader("POS Distribution")
    pos_counts = translations_df['pos'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    pos_counts.plot(kind='bar', ax=ax, color='#2E75B6')
    ax.set_xlabel("Part of Speech")
    ax.set_ylabel("Count")
    ax.set_title("Distribution des categories grammaticales")
    st.pyplot(fig)

    st.subheader("Morphology Distribution")
    morph_counts = translations_df['morphology'].value_counts()
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    morph_counts.plot(kind='bar', ax=ax2, color='#70AD47')
    ax2.set_xlabel("Morphology Type")
    ax2.set_ylabel("Count")
    ax2.set_title("Distribution des types morphologiques")
    st.pyplot(fig2)

# ==================== PAGE: SEARCH BY CONCEPT ====================

elif page == "Search by Concept":
    st.header("Search by Concept")

    concepts_df = get_concepts()
    concept_options = dict(zip(concepts_df['concept_name'], concepts_df['id']))
    selected_concept = st.selectbox("Select a concept:", list(concept_options.keys()))

    if selected_concept:
        concept_id = concept_options[selected_concept]
        results = get_translations(concept_id=concept_id)

        st.subheader("Translations for: {}".format(selected_concept))

        # Affichage en grille de 3 colonnes
        cols = st.columns(3)
        for idx, row in results.iterrows():
            with cols[idx % 3]:
                colex_badge = ""
                if row['colexification']:
                    colex_badge = '<span style="background-color:#ff6b6b;color:white;padding:2px 8px;border-radius:10px;font-size:0.8em;">COLEX</span>'

                st.markdown("""
                <div style="background-color:#f0f2f6;padding:15px;border-radius:10px;margin:5px;">
                    <h4>{} {}</h4>
                    <p><b>Word:</b> {}</p>
                    <p><b>IPA:</b> <code>{}</code></p>
                    <p><b>POS:</b> {} | <b>Morph:</b> {}</p>
                    <p><b>Source:</b> {}</p>
                </div>
                """.format(
                    row['language_name'], 
                    colex_badge,
                    row['word'], 
                    row['ipa'] if row['ipa'] else 'N/A',
                    row['pos'] if row['pos'] else 'N/A',
                    row['morphology'] if row['morphology'] else 'N/A',
                    row['source'] if row['source'] else 'N/A'
                ), unsafe_allow_html=True)

        # Details de colexification si present
        colex_data = results[results['colexification'].notna()]
        if len(colex_data) > 0:
            st.subheader("Colexifications detected:")
            for _, row in colex_data.iterrows():
                st.write("- **{}**: {} -> {}".format(row['language_name'], row['word'], row['colexification']))

# ==================== PAGE: SEARCH BY LANGUAGE ====================

elif page == "Search by Language":
    st.header("Search by Language")

    languages_df = get_languages()
    lang_options = dict(zip(languages_df['language_name'], languages_df['id']))
    selected_lang = st.selectbox("Select a language:", list(lang_options.keys()))

    if selected_lang:
        lang_id = lang_options[selected_lang]
        results = get_translations(language_id=lang_id)

        st.subheader("Lexicon: {}".format(selected_lang))

        # Info langue
        lang_info = languages_df[languages_df['id'] == lang_id].iloc[0]
        st.write("**Family:** {} | **Region:** {} | **ISO:** {}".format(
            lang_info['family'], lang_info['region'], lang_info['iso_code']
        ))

        # Tableau complet
        display_df = results[['concept_name', 'word', 'ipa', 'pos', 'morphology', 'colexification']].copy()
        display_df.columns = ['Concept', 'Word', 'IPA', 'POS', 'Morphology', 'Colexification']
        st.dataframe(display_df, use_container_width=True)

        # Statistiques
        st.subheader("Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total entries", len(results))
        with col2:
            st.metric("With IPA", len(results[results['ipa'].notna()]))
        with col3:
            st.metric("Colexifications", len(results[results['colexification'].notna()]))

        # IPA sample
        st.subheader("IPA Sample (first 10)")
        sample = results[results['ipa'].notna()].head(10)
        for _, row in sample.iterrows():
            st.write("**{}**: {} -> {}".format(row['concept_name'], row['word'], row['ipa']))

# ==================== PAGE: COLEXIFICATIONS ====================

elif page == "Colexifications":
    st.header("Cross-Linguistic Colexifications")

    colex_df = get_colexifications()

    if len(colex_df) > 0:
        # Filtre par langue
        languages = ['All'] + sorted(colex_df['language_name'].unique().tolist())
        selected_lang = st.selectbox("Filter by language:", languages)

        if selected_lang != 'All':
            filtered_df = colex_df[colex_df['language_name'] == selected_lang]
        else:
            filtered_df = colex_df

        st.subheader("Colexification Patterns ({} found)".format(len(filtered_df)))

        for _, row in filtered_df.iterrows():
            with st.expander("{}: {} ({} <-> {})".format(
                row['language_name'], row['word'], row['concept1'], row['concept2']
            )):
                st.markdown("""
                - **Language:** {}
                - **Word:** {} ({})"
                - **Concepts:** {} <-> {}
                - **Type:** {}
                - **Scientific Value:** {}
                - **Source:** {}
                """.format(
                    row['language_name'],
                    row['word'],
                    row['ipa'] if row['ipa'] else 'N/A',
                    row['concept1'],
                    row['concept2'],
                    row['colex_type'] if row['colex_type'] else 'N/A',
                    row['scientific_value'] if row['scientific_value'] else 'N/A',
                    row['source'] if row['source'] else 'N/A'
                ))

        # Network visualization
        st.subheader("Colexification Network")
        G = nx.Graph()
        for _, row in filtered_df.iterrows():
            G.add_edge(row['concept1'], row['concept2'],
                      language=row['language_name'], word=row['word'])

        if len(G.edges()) > 0:
            fig, ax = plt.subplots(figsize=(12, 10))
            pos = nx.spring_layout(G, k=3, seed=42)

            # Dessiner les noeuds
            nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue',
                                node_size=3000, alpha=0.9)

            # Dessiner les labels
            nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight='bold')

            # Dessiner les aretes
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', 
                                   width=2, alpha=0.5)

            ax.set_title("Colexification Network")
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("No colexifications to display in network.")
    else:
        st.info("No colexifications recorded yet.")

# ==================== PAGE: NETWORK ANALYSIS ====================

elif page == "Network Analysis":
    st.header("Lexical Network Analysis")

    translations_df = get_translations()

    # Language comparison matrix
    st.subheader("Cross-Linguistic Comparison (Concept x Language)")
    pivot = translations_df.pivot_table(
        index='concept_name',
        columns='language_name',
        values='word',
        aggfunc='first'
    )
    st.dataframe(pivot.head(20), use_container_width=True)

    # Coverage analysis
    st.subheader("Concept Coverage Analysis")
    coverage = translations_df.groupby(['concept_name', 'language_name']).size().unstack(fill_value=0)
    st.dataframe(coverage.head(20), use_container_width=True)

    # Shared forms analysis
    st.subheader("Shared Lexical Forms Across Languages")
    shared = translations_df.groupby('word').agg({
        'language_name': lambda x: ', '.join(sorted(set(x))),
        'concept_name': lambda x: ', '.join(sorted(set(x)))
    }).reset_index()
    shared = shared[shared['language_name'].str.contains(',')]
    if len(shared) > 0:
        st.write("Words shared between multiple languages:")
        st.dataframe(shared, use_container_width=True)
    else:
        st.info("No shared lexical forms found across languages.")

    # POS comparison
    st.subheader("POS Distribution by Language")
    pos_by_lang = translations_df.groupby(['language_name', 'pos']).size().unstack(fill_value=0)
    st.dataframe(pos_by_lang, use_container_width=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    pos_by_lang.plot(kind='bar', ax=ax, stacked=True)
    ax.set_xlabel("Language")
    ax.set_ylabel("Count")
    ax.set_title("POS Distribution by Language")
    ax.legend(title="POS", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

# ==================== PAGE: DOWNLOAD DATA ====================

elif page == "Download Data":
    st.header("Download Database")

    # Export as CSV
    st.subheader("Export as CSV")

    export_df = get_all_translations_flat()
    csv = export_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Download Full Dataset (CSV)",
        data=csv,
        file_name="globaslex_data.csv",
        mime="text/csv"
    )

    st.write("Preview:")
    st.dataframe(export_df.head(10), use_container_width=True)

    # Database file
    st.subheader("Download SQLite Database")

    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            db_bytes = f.read()
        st.download_button(
            label="Download SQLite Database",
            data=db_bytes,
            file_name="globaslex.db",
            mime="application/octet-stream"
        )
        st.write("File size: {:.1f} KB".format(len(db_bytes) / 1024))
    else:
        st.error("Database file not found.")

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#666;">
    <p>GloBasLex Mini-Database | 100 Swadesh Concepts x 6 Languages</p>
    <p>Minyogog Jean Baptiste | University of Yaounde I</p>
</div>
""", unsafe_allow_html=True)