import sqlite3
import zipfile
import io
import re
from collections import Counter
import math
import random
import streamlit as st

# --- Backend: Subtitle Extraction and Search ---
def extract_subtitles_from_db(db_path):
    subtitle_data = {}
    try:
        st.info(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check available tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        st.write(f"Available tables: {tables}")
        if not tables:
            st.error("No tables found in database!")
            return subtitle_data
        
        table_name = 'zipfiles'
        if ('zipfiles',) not in tables:
            st.warning(f"'zipfiles' table not found. Using first available table: {tables[0][0]}")
            table_name = tables[0][0]
        
        cursor.execute(f"SELECT num, name, content FROM {table_name}")
        rows = cursor.fetchall()
        st.write(f"Found {len(rows)} rows in '{table_name}' table.")
        
        # Progress bar for extraction
        progress_bar = st.progress(0)
        total_rows = len(rows)
        
        for i, (num, name, content_blob) in enumerate(rows):
            progress = (i + 1) / total_rows
            progress_bar.progress(progress)
            
            if name.endswith('.srt'):
                try:
                    srt_content = content_blob.decode('utf-8', errors='ignore')
                    subtitle_data[f"subtitle_{num}_{name}"] = srt_content
                except AttributeError:
                    srt_content = content_blob.decode('utf-8', errors='ignore')
                    subtitle_data[f"subtitle_{num}_{name}"] = srt_content
            elif name.endswith('.nfo'):
                continue
            else:
                try:
                    with zipfile.ZipFile(io.BytesIO(content_blob)) as zf:
                        srt_files = [f for f in zf.namelist() if f.endswith('.srt')]
                        for file_name in srt_files:
                            srt_content = zf.read(file_name).decode('utf-8', errors='ignore')
                            subtitle_data[f"subtitle_{num}_{file_name}"] = srt_content
                except (zipfile.BadZipFile, UnicodeDecodeError, TypeError) as e:
                    st.warning(f"Failed to process row {num} as ZIP: {e}")
                    continue
        
        conn.close()
        
        st.write(f"Total subtitles extracted before sampling: {len(subtitle_data)}")
        
        # Sample 30% of the data
        if subtitle_data:
            sampled_keys = random.sample(list(subtitle_data.keys()), max(1, int(len(subtitle_data) * 0.3)))
            subtitle_data = {key: subtitle_data[key] for key in sampled_keys}
            st.write(f"After sampling: {len(subtitle_data)} subtitles (30% of original)")
        
        return subtitle_data
    
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return {}
    except Exception as e:
        st.error(f"Unexpected error during extraction: {e}")
        return {}

def preprocess_srt(text):
    lines = text.split('\n')
    clean_lines = [line.strip() for line in lines if not re.match(r'^\d+$|^[\d:,]+ --> [\d:,]+$', line) and line.strip()]
    return " ".join(clean_lines).lower().split()

def vectorize_text(words):
    return Counter(words)

def cosine_similarity(vec1, vec2):
    common_words = set(vec1.keys()) & set(vec2.keys())
    if not common_words:
        return 0.0
    dot_product = sum(vec1[word] * vec2[word] for word in common_words)
    norm1 = math.sqrt(sum(count ** 2 for count in vec1.values()))
    norm2 = math.sqrt(sum(count ** 2 for count in vec2.values()))
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

def search_subtitles(subtitle_data, query, top_k=2):
    query_words = query.lower().split()
    query_vec = vectorize_text(query_words)
    
    results = []
    for doc_id, content in subtitle_data.items():
        doc_words = preprocess_srt(content)
        doc_vec = vectorize_text(doc_words)
        similarity = cosine_similarity(query_vec, doc_vec)
        results.append((doc_id, similarity, " ".join(doc_words)))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

# --- Streamlit Frontend ---
def main():
    st.title("Subtitle Search Engine")
    
    # Load subtitle data
    db_path = r"D:\CRANES\python\eng_subtitles_database.db"
    with st.spinner("Loading subtitles..."):
        subtitle_data = extract_subtitles_from_db(db_path)
    
    if not subtitle_data:
        st.error("No subtitles loaded from database. Check the database path and content.")
        st.stop()
    
    st.success(f"Loaded {len(subtitle_data)} subtitles (30% of total)")
    
    # Search query input
    query = st.text_input("Search Query:", value="What a funny day")
    
    if st.button("Search"):
        if not query:
            st.warning("Please enter a search query!")
        else:
            with st.spinner("Searching..."):
                top_matches = search_subtitles(subtitle_data, query)
                
                if not top_matches or top_matches[0][1] == 0.0:
                    st.info(f"No matches found for '{query}'. Try a different query or check if the subtitle is in the sampled data.")
                else:
                    st.subheader(f"Query: '{query}'")
                    for doc_id, similarity, text in top_matches:
                        st.markdown(f"**Document:** {doc_id}")
                        st.markdown(f"**Similarity:** {similarity:.4f}")
                        st.markdown(f"**Text:** {text[:150]}...")
                        st.markdown("---")

if __name__ == "__main__":
    main()