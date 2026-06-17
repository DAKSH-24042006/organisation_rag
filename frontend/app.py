import sys
import os
from pathlib import Path
import time
import json
import uuid

# Fix python path to find backend
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.append(str(BACKEND_DIR))

import streamlit as st

def save_benchmark_entry(query, qtype, retrieval_time_ms, generation_time_ms, num_chunks, num_files, context_size):
    benchmarks_dir = ROOT_DIR / "data" / "benchmarks"
    benchmarks_dir.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "query": query,
        "query_type": qtype,
        "retrieval_time_ms": round(retrieval_time_ms, 2) if retrieval_time_ms is not None else 0.0,
        "generation_time_ms": round(generation_time_ms, 2) if generation_time_ms is not None else 0.0,
        "num_chunks": num_chunks,
        "num_files": num_files,
        "context_size": context_size
    }
    
    timestamp = int(time.time() * 1000)
    rand_id = uuid.uuid4().hex[:6]
    file_path = benchmarks_dir / f"benchmark_{timestamp}_{rand_id}.json"
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=4)


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
    .intent-OVERVIEW { background-color: #9b5de5; color: white; }
    .intent-DEBUG { background-color: #f15bb5; color: white; }
    .intent-CODE_SEARCH { background-color: #00bbf9; color: white; }
    .intent-FILE_RECOVERY { background-color: #00f5d4; color: black; }
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

st.title("🔍 Code RAG Platform (V3)")
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
    
    # Session State Initialization
    if "qa_query" not in st.session_state:
        st.session_state.qa_query = ""
    if "retrieved" not in st.session_state:
        st.session_state.retrieved = False
    if "retrieval_data" not in st.session_state:
        st.session_state.retrieval_data = None
    if "retrieval_time_ms" not in st.session_state:
        st.session_state.retrieval_time_ms = 0.0
    if "context_str" not in st.session_state:
        st.session_state.context_str = ""
    if "answer" not in st.session_state:
        st.session_state.answer = None
    if "generation_time_ms" not in st.session_state:
        st.session_state.generation_time_ms = None
    if "benchmark_mode" not in st.session_state:
        st.session_state.benchmark_mode = False
    if "preview_mode" not in st.session_state:
        st.session_state.preview_mode = False

    query = st.text_input("Enter your request:", placeholder="e.g. How does the pipeline run inference?")
    
    # Change detection: Reset retrieval/generation state if query changes
    if query != st.session_state.qa_query:
        st.session_state.qa_query = query
        st.session_state.retrieved = False
        st.session_state.retrieval_data = None
        st.session_state.retrieval_time_ms = 0.0
        st.session_state.context_str = ""
        st.session_state.answer = None
        st.session_state.generation_time_ms = None
        
    col_cb1, col_cb2 = st.columns(2)
    with col_cb1:
        st.session_state.benchmark_mode = st.checkbox("Benchmark Mode", value=st.session_state.benchmark_mode)
    with col_cb2:
        st.session_state.preview_mode = st.checkbox("Preview Retrieval Only (No LLM)", value=st.session_state.preview_mode)
    
    if st.button("Query Repository", use_container_width=True):
        if not query.strip():
            st.warning("Please input a search query.")
        else:
            with st.spinner("Retrieving repository context, performing hybrid search, and ranking..."):
                try:
                    retrieval_start = time.perf_counter()
                    retrieval_data = retrieve(query)
                    retrieval_end = time.perf_counter()
                    
                    st.session_state.retrieval_time_ms = (retrieval_end - retrieval_start) * 1000
                    st.session_state.retrieval_data = retrieval_data
                    st.session_state.context_str = ContextAssembler.assemble_context(retrieval_data)
                    st.session_state.retrieved = True
                    
                    # Clear any stale generation state
                    st.session_state.answer = None
                    st.session_state.generation_time_ms = None
                except Exception as e:
                    st.error(f"Error performing retrieval: {e}")
                    st.exception(e)
                    st.session_state.retrieved = False
                    
    if st.session_state.retrieved and st.session_state.retrieval_data:
        results = st.session_state.retrieval_data.get("results", [])
        qtype = st.session_state.retrieval_data.get("query_type", "GENERAL")
        
        # 1. AI Response Placeholder at the top
        ai_response_placeholder = st.empty()
        
        # 2. Display Intent Badge
        st.markdown(f'Query Classification: <span class="intent-badge intent-{qtype}">{qtype} QUERY</span>', unsafe_allow_html=True)
        
        # 3. Collapsible Implementation Details (expanded by default if answer not yet generated)
        is_expanded = (st.session_state.answer is None)
        with st.expander("🔍 View Retrieval & Context Details (Implementation Details)", expanded=is_expanded):
            # Metrics Section
            st.subheader("📈 Metrics Dashboard")
            num_chunks = len(results)
            retrieved_files = sorted(list({c.get("path") for c in results if c.get("path")}))
            num_files = len(retrieved_files)
            context_size = len(st.session_state.context_str)
            estimated_tokens = context_size // 4
            
            ret_time = st.session_state.retrieval_time_ms
            gen_time = st.session_state.generation_time_ms
            tot_time = (ret_time + gen_time) if gen_time is not None else None
            
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.metric("Query Type", qtype)
                st.metric("Estimated Tokens", f"{estimated_tokens}")
            with m_col2:
                st.metric("Retrieved Chunks", f"{num_chunks}")
                st.metric("Retrieval Time", f"{ret_time:.1f} ms")
            with m_col3:
                st.metric("Retrieved Files", f"{num_files}")
                st.metric("Generation Time", f"{gen_time:.1f} ms" if gen_time is not None else "N/A")
            with m_col4:
                st.metric("Context Size", f"{context_size} chars")
                st.metric("Total Time", f"{tot_time:.1f} ms" if tot_time is not None else "N/A")
                
            st.divider()
            
            # Retrieved Chunks Section
            st.subheader("📂 Retrieved Chunks")
            st.caption(f"Showing all {len(results)} chunks retrieved and ranked:")
            for idx, chunk in enumerate(results, 1):
                filename = chunk.get("file") or chunk.get("path") or "Unknown File"
                stype = chunk.get("type", "Entity")
                score = chunk.get("rerank_score") or chunk.get("rrf_score", 0.0)
                chunk_content = chunk.get("content", "")
                
                chunk_title = f"{idx}. {filename} (Score: {score:.4f})"
                with st.expander(chunk_title):
                    st.write(f"Type: {stype}")
                    st.write(f"Length: {len(chunk_content)} chars")
                    st.code(chunk_content, language="python" if filename.endswith(".py") else "text")
                    
            st.divider()
            
            # Retrieved Files Section
            st.subheader("📁 Retrieved Files")
            if retrieved_files:
                for f in retrieved_files:
                    st.markdown(f"- `{f}`")
            else:
                st.write("*No files retrieved.*")
                
            st.divider()
            
            # Context Inspection Panel
            st.subheader("🔍 Assembled Context Summary")
            # Files Included
            st.markdown("**Files Included:**")
            files_included = sorted(list({r.get("path") for r in results if r.get("type") not in {"CONFIG", "DATABASE", "DOCS"} and r.get("path")}))
            if files_included:
                for f in files_included:
                    st.markdown(f"- `{f}`")
            else:
                st.markdown("*None*")
                
            # Configs Included
            st.markdown("**Configs Included:**")
            configs_included = sorted(list({r.get("path") for r in results if r.get("type") in {"CONFIG", "DATABASE"} and r.get("path")}))
            if configs_included:
                for c in configs_included:
                    st.markdown(f"- `{c}`")
            else:
                st.markdown("*None*")
                
            # Dependencies Included
            st.markdown("**Dependencies Included:**")
            relationships = []
            for r in results:
                rels = r.get("graph_relationships", [])
                if rels:
                    relationships.extend(rels)
            unique_rels = list(dict.fromkeys(relationships))
            if unique_rels:
                for rel in unique_rels[:15]:
                    st.markdown(f"- `{rel}`")
                if len(unique_rels) > 15:
                    st.markdown(f"*... and {len(unique_rels) - 15} more*")
            else:
                st.markdown("*None*")
                
            # Documentation Included
            st.markdown("**Documentation Included:**")
            docs_included = sorted(list({r.get("path") for r in results if r.get("type") == "DOCS" and r.get("path")}))
            if docs_included:
                for d in docs_included:
                    st.markdown(f"- `{d}`")
            else:
                st.markdown("*None*")
                
            st.divider()
            
            # Repository Analysis Section (Inside Details Expander)
            st.subheader("📊 Repository Analysis Snapshot")
            if repo_analysis:
                md_summary = RepositoryAnalyzer.generate_markdown_summary(repo_analysis)
                st.markdown(md_summary)
            else:
                st.warning("No repository analysis available. Run indexing first.")
        
        # 4. Render AI Response if it exists
        if st.session_state.answer:
            with ai_response_placeholder.container():
                st.subheader("🤖 AI Response")
                st.markdown(st.session_state.answer)
                st.caption(f"⚡ Generation Latency: {st.session_state.generation_time_ms:.1f} ms | Retrieval Latency: {st.session_state.retrieval_time_ms:.1f} ms")
                st.divider()
        
        # 5. Trigger Generation if not in preview mode and not already generated
        if not st.session_state.preview_mode and st.session_state.answer is None:
            with st.spinner("LLM generating answer..."):
                try:
                    num_chunks = len(results)
                    retrieved_files = sorted(list({c.get("path") for c in results if c.get("path")}))
                    num_files = len(retrieved_files)
                    context_size = len(st.session_state.context_str)
                    
                    generation_start = time.perf_counter()
                    answer = generate_answer(query, st.session_state.context_str)
                    generation_end = time.perf_counter()
                    
                    st.session_state.answer = answer
                    st.session_state.generation_time_ms = (generation_end - generation_start) * 1000
                    
                    if st.session_state.benchmark_mode:
                        save_benchmark_entry(
                            query=query,
                            qtype=qtype,
                            retrieval_time_ms=st.session_state.retrieval_time_ms,
                            generation_time_ms=st.session_state.generation_time_ms,
                            num_chunks=num_chunks,
                            num_files=num_files,
                            context_size=context_size
                        )
                        st.success("Benchmark result saved successfully!")
                        
                    st.rerun()
                except Exception as e:
                    st.session_state.answer = f"Error generating answer: {e}"
                    st.session_state.generation_time_ms = 0.0
                    st.error(f"Error generating answer: {e}")
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