import sys
import os
from pathlib import Path

# Fix python path to find backend
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.append(str(BACKEND_DIR))

import streamlit as st

# =========================================================
# LAZY LOAD COMPONENTS
# =========================================================

@st.cache_resource
def load_rag_components():
    from rag.retriever import retrieve
    from rag.context_assembler import ContextAssembler
    from rag.analysis import RepositoryAnalyzer
    from llm.answer_generator import generate_answer
    
    return retrieve, ContextAssembler, RepositoryAnalyzer, generate_answer

retrieve, ContextAssembler, RepositoryAnalyzer, generate_answer = load_rag_components()

# =========================================================
# STYLING & PREMIUM LAYOUT
# =========================================================

st.set_page_config(
    page_title="Code RAG - Repository Intelligence Platform",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for premium design
st.markdown("""
<style>
    /* Dark glassmorphic container headers */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00ADB5;
    }
    .metric-label {
        font-size: 12px;
        color: #EEEEEE;
    }
    /* Intent badge styling */
    .intent-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .intent-ARCHITECTURE { background-color: #9b5de5; color: white; }
    .intent-DEPENDENCY { background-color: #f15bb5; color: white; }
    .intent-FLOW { background-color: #fee440; color: black; }
    .intent-CONFIGURATION { background-color: #00bbf9; color: white; }
    .intent-SYMBOL { background-color: #00f5d4; color: black; }
    .intent-GENERAL { background-color: #6c757d; color: white; }
</style>
""", unsafe_allow_html=True)

# Fetch stats for Sidebar
@st.cache_data(ttl=60)
def get_repository_stats():
    try:
        analysis = RepositoryAnalyzer.analyze_repository()
        return analysis
    except Exception:
        return None

repo_analysis = get_repository_stats()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/artificial-intelligence.png", width=80)
    st.title("Repo Intelligence")
    st.markdown("---")
    
    if repo_analysis:
        st.subheader("📊 Repository Overview")
        stats = repo_analysis["statistics"]
        
        # Display nicely in 2x3 grid
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["files"]}</div><div class="metric-label">Files</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["classes"]}</div><div class="metric-label">Classes</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["tables"]}</div><div class="metric-label">SQL Tables</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["functions"]}</div><div class="metric-label">Methods</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["endpoints"]}</div><div class="metric-label">API Routes</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["configs"]}</div><div class="metric-label">Configs</div></div>', unsafe_allow_html=True)
    else:
        st.warning("No repository stats available. Run indexing first.")
        
    st.markdown("---")
    st.markdown("Designed with **Antigravity V2**.")

# =========================================================
# MAIN APP BODY
# =========================================================

st.title("🔍 Code RAG Platform (V2)")
st.caption("Unlock deep semantics, call dependencies, and architecture relationships of your workspace.")

# Use tabs for layout
tab_qa, tab_analysis, tab_config = st.tabs(["🤖 Code Assistant", "📊 Repository Static Analysis", "⚙️ Indexing & Settings"])

# =========================================================
# TAB 1: QA CODE ASSISTANT
# =========================================================
with tab_qa:
    st.markdown("#### Ask questions about the codebase")
    st.markdown(
        """
    * *How does the camera manager work?*
    * *Trace the execution path of the face validation pipeline.*
    * *Where is the configuration loaded?*
    * *What API endpoints are registered?*
    """
    )
    
    query = st.text_input("Enter your request:", placeholder="e.g. How does the pipeline run inference?")
    
    if st.button("Query Repository", use_container_width=True):
        if not query.strip():
            st.warning("Please input a search query.")
        else:
            with st.spinner("Ingesting query, running hybrid search, and expanding graph neighbors..."):
                try:
                    # 1. Retrieval
                    retrieval_data = retrieve(query)
                    qtype = retrieval_data["query_type"]
                    results = retrieval_data["results"]
                    stats = retrieval_data["statistics"]
                    
                    # 2. Assemble context
                    context_str = ContextAssembler.assemble_context(retrieval_data)
                    
                    # Display Intent Badge
                    st.markdown(f'Query Classification: <span class="intent-badge intent-{qtype}">{qtype} QUERY</span>', unsafe_allow_html=True)
                    
                    col_ans, col_evid = st.columns([3, 2])
                    
                    # LLM Generation
                    with col_ans:
                        st.subheader("🤖 AI Response")
                        with st.spinner("LLM generating explanation..."):
                            answer = generate_answer(query, context_str)
                            st.markdown(answer)
                            
                    # Retrieved Chunks / Evidences
                    with col_evid:
                        st.subheader("📂 Code & Text Evidence")
                        st.caption(f"Retrieved {len(results)} chunks. Fused via RRF + CrossEncoder Rerank.")
                        
                        for idx, chunk in enumerate(results, 1):
                            filename = chunk.get("file", "File")
                            stype = chunk.get("type", "Entity")
                            name = chunk.get("name", "name")
                            score = chunk.get("rrf_score", 0.0)
                            
                            title = f"[{stype}] {filename} -> {name}"
                            if chunk.get("graph_expanded"):
                                title += " (🕸️ Graph Extended)"
                                
                            with st.expander(title):
                                st.markdown(f"**Path**: `{chunk.get('path')}` (Lines {chunk.get('start_line')}-{chunk.get('end_line')})")
                                if chunk.get("expanded_relation"):
                                    st.info(f"Relation: {chunk.get('expanded_relation')}")
                                st.code(chunk.get("content", ""), language="python" if filename.endswith(".py") else "text")
                                
                    # Traversal edges display
                    if results and "graph_relationships" in results[0]:
                        st.divider()
                        st.subheader("🕸️ Graph Dependency Trails Explored")
                        rels = results[0]["graph_relationships"]
                        if rels:
                            cols = st.columns(3)
                            for i, rel in enumerate(rels[:9]):  # display top 9
                                with cols[i % 3]:
                                    st.code(rel, language="text")
                        else:
                            st.info("No cross-file graph traversal paths needed for this query.")
                            
                except Exception as e:
                    st.error(f"Error executing retrieval or query generation: {e}")
                    st.exception(e)

# =========================================================
# TAB 2: STATIC REPOSITORY SUMMARY
# =========================================================
with tab_analysis:
    st.subheader("📊 Auto-generated Architecture Report")
    
    if st.button("Generate Live Repository Overview", use_container_width=True):
        with st.spinner("Analyzing graph nodes, API decorators, and SQL schemas..."):
            try:
                analysis = RepositoryAnalyzer.analyze_repository()
                md_summary = RepositoryAnalyzer.generate_markdown_summary(analysis)
                st.markdown(md_summary)
            except Exception as e:
                st.error(f"Could not generate report: {e}")
    elif repo_analysis:
        # Pre-rendered cache
        md_summary = RepositoryAnalyzer.generate_markdown_summary(repo_analysis)
        st.markdown(md_summary)
    else:
        st.info("Click the button above to generate a static architecture summary.")

# =========================================================
# TAB 3: INDEXING & SETTINGS
# =========================================================
with tab_config:
    st.subheader("⚙️ Database & Repository Ingestion")
    st.markdown("Index the repository source files, extract AST tags, construct the NetworkX graph, and populate vectors to Qdrant.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Configured Repositories")
        from rag.config import REPOSITORIES as conf_repos
        for r in conf_repos:
            st.code(f"Name: {r['name']}\nPath: {r['path']}", language="text")
            
    with col2:
        st.markdown("### Actions")
        if st.button("Run Full Re-indexing", use_container_width=True):
            with st.spinner("Scanning source code, generating embeddings, creating Qdrant collections..."):
                try:
                    from rag.indexer import run_indexing_pipeline
                    run_indexing_pipeline()
                    st.success("Re-indexing complete! Refresh page to update stats.")
                    # Force reload analysis stats next time
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Re-indexing failed: {e}")