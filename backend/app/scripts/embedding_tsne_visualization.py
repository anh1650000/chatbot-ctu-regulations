#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
t-SNE Embedding Visualization
- Load embeddings từ data/index.faiss (đã save rồi)
- Load metadata từ MySQL (doc_title, chapter_title, article_title)
- Apply t-SNE: 384D → 2D
- Hiển thị interactive HTML plot dùng Plotly
"""

import numpy as np
import json
import faiss
from pathlib import Path
import sys
from sklearn.manifold import TSNE
import plotly.graph_objects as go
import plotly.express as px

# Add parent path để import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.db import get_db_connection


def load_faiss_index_and_mapping():
    """Load FAISS index từ data/index.faiss"""
    try:
        index_path = Path(__file__).parent.parent / "data" / "index.faiss"
        mapping_path = Path(__file__).parent.parent / "data" / "id_mapping.json"
        
        if not index_path.exists() or not mapping_path.exists():
            print(f"❌ Index files not found:")
            print(f"   - {index_path}")
            print(f"   - {mapping_path}")
            return None, None
        
        # Load FAISS index
        index = faiss.read_index(str(index_path))
        print(f"✅ Loaded FAISS index: {index.ntotal} vectors")
        
        # Load ID mapping
        with open(mapping_path, 'r', encoding='utf-8') as f:
            id_mapping = json.load(f)
        print(f"✅ Loaded ID mapping: {len(id_mapping)} entries")
        
        return index, id_mapping
    except Exception as e:
        print(f"❌ Error loading FAISS files: {e}")
        return None, None


def extract_embeddings_from_faiss(index):
    """Lấy vectors từ FAISS index"""
    try:
        # Reconstruct all vectors từ index
        embeddings = index.reconstruct_n(0, index.ntotal)
        print(f"✅ Extracted embeddings: {embeddings.shape}")
        return embeddings
    except Exception as e:
        print(f"❌ Error extracting embeddings: {e}")
        return None


def load_metadata_from_mysql(id_mapping):
    """Load chunk metadata từ MySQL (1 clause = 1 chunk)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query tất cả data giống text_splitter() trong utils.py
        cursor.execute("""
            SELECT 
                d.doc_id,
                d.title as doc_title,
                ch.chapter_id,
                ch.title as chapter_title,
                a.article_id,
                a.title as article_title,
                cl.clause_id,
                cl.content as clause_content
            FROM documents d
            JOIN chapters ch ON d.doc_id = ch.doc_id
            JOIN articles a ON ch.chapter_id = a.chapter_id
            JOIN clauses cl ON a.article_id = cl.article_id
            ORDER BY d.doc_id, ch.chapter_number, a.article_number, cl.clause_number
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"✅ Loaded {len(rows)} clauses from MySQL")
        
        # Split thành chunks giống text_splitter()
        from backend.app.services.utils import text_splitter
        
        text_chunks, meta_data_list = text_splitter(rows)
        print(f"✅ Split into {len(text_chunks)} chunks")
        
        # Map chunks theo index trong id_mapping
        metadata = {}
        for i in range(len(text_chunks)):
            if i < len(rows):
                row = rows[i]
                metadata[i] = {
                    'doc_title': row['doc_title'],
                    'chapter_title': row['chapter_title'],
                    'article_title': row['article_title'],
                    'content': text_chunks[i]
                }
        
        print(f"✅ Mapped metadata for {len(metadata)} chunks")
        return metadata
    except Exception as e:
        print(f"❌ Error loading metadata from MySQL: {e}")
        import traceback
        traceback.print_exc()
        return {}


def apply_tsne(embeddings, perplexity=30, max_iter=1000):
    """Apply t-SNE dimensionality reduction"""
    print(f"\n🔄 Applying t-SNE (may take a few minutes)...")
    print(f"   Input: {embeddings.shape[0]} samples × {embeddings.shape[1]} dimensions")
    print(f"   Perplexity: {perplexity}, Iterations: {max_iter}")
    
    tsne = TSNE(
        n_components=2,
        random_state=42,
        perplexity=min(perplexity, embeddings.shape[0] - 1),
        max_iter=max_iter,
        verbose=1
    )
    
    tsne_results = tsne.fit_transform(embeddings.astype(np.float32))
    print(f"✅ t-SNE completed. Output: {tsne_results.shape}")
    
    return tsne_results


def create_interactive_plot(tsne_results, metadata, output_file):
    """Create interactive Plotly visualization"""
    print(f"\n📊 Creating interactive plot...")
    
    x = tsne_results[:, 0]
    y = tsne_results[:, 1]
    
    # Prepare data for plot
    doc_titles = []
    chapter_titles = []
    article_titles = []
    content_previews = []
    
    for idx in range(len(x)):
        if idx in metadata:
            m = metadata[idx]
            doc_titles.append(m['doc_title'])
            chapter_titles.append(m['chapter_title'])
            article_titles.append(m['article_title'])
            
            # Preview: first 150 chars
            content = m['content'].replace('\n', ' ')[:150]
            if len(m['content']) > 150:
                content += "..."
            content_previews.append(content)
        else:
            doc_titles.append("Unknown")
            chapter_titles.append("Unknown")
            article_titles.append("Unknown")
            content_previews.append("N/A")
    
    # Create hover text
    hover_texts = []
    for i in range(len(x)):
        hover_text = f"""
        <b>{doc_titles[i]}</b><br>
        📚 {chapter_titles[i]}<br>
        📄 {article_titles[i]}<br>
        <br>
        <i>{content_previews[i]}</i>
        """
        hover_texts.append(hover_text)
    
    # Create scatter plot
    fig = go.Figure(data=go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=8,
            color=np.arange(len(x)),  # Color by index
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Article Index",
                thickness=15,
                len=0.7
            ),
            opacity=0.8,
            line=dict(width=1, color='white')
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        name='Articles'
    ))
    
    fig.update_layout(
        title={
            'text': 't-SNE Visualization: CTU Regulations Embeddings (384D → 2D)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis=dict(
            title='t-SNE Component 1',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title='t-SNE Component 2',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        width=1400,
        height=900,
        hovermode='closest',
        plot_bgcolor='rgba(240,240,240,0.9)',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    # Save to HTML
    fig.write_html(output_file)
    print(f"✅ Visualization saved to: {output_file}")


def main():
    print("="*80)
    print("t-SNE EMBEDDING VISUALIZATION")
    print("="*80)
    
    # 1. Load FAISS index + mapping
    index, id_mapping = load_faiss_index_and_mapping()
    if index is None:
        return
    
    # 2. Extract embeddings
    embeddings = extract_embeddings_from_faiss(index)
    if embeddings is None:
        return
    
    # 3. Load metadata từ MySQL
    print("\n📊 Loading metadata from MySQL...")
    metadata = load_metadata_from_mysql(id_mapping)
    if not metadata:
        print("⚠️  Warning: No metadata loaded from MySQL")
    
    # 4. Apply t-SNE
    tsne_results = apply_tsne(embeddings, perplexity=30, max_iter=1000)
    
    # 5. Create visualization
    output_file = Path(__file__).parent.parent / "charts" / "embedding_tsne_interactive.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    create_interactive_plot(tsne_results, metadata, str(output_file))
    
    print("\n" + "="*80)
    print(f"✅ Done! Open in browser: {output_file}")
    print("="*80)


if __name__ == "__main__":
    main()
