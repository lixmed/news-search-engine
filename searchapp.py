import streamlit as st
import requests
import time

# Configure the page
st.set_page_config(
    page_title="Search Bar Gamed Gedan", 
    page_icon="🔭", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Custom CSS with animations and modern styling
st.markdown(
    """
    <style>
    /* Main theme colors and fonts */
    :root {
        --background: #0f1924;
        --card-bg: #1a2634;
        --accent: #3d8bfd;
        --accent-hover: #5c9fff;
        --text: #e6edf3;
        --text-secondary: #a3b9cc;
        --input-bg: #141f2d;
        --result-border: #2a3a4d;
    }
    
    /* Base styling */
    body {
        background-color: var(--background);
        color: var(--text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: var(--background);
    }
    
    /* Header styling */
    .search-header {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 2.5rem 0 2rem 0;
    }
    
    .logo-text {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #3d8bfd, #7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(61, 139, 253, 0.3);
        margin: 0;
        letter-spacing: -0.03em;
    }
    
    .logo-icon {
        font-size: 3.2rem;
        margin-right: 0.8rem;
        animation: pulse 2s infinite ease-in-out;
    }
    
    /* Search input styling */
    .stTextInput {
        margin-bottom: 2rem;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: var(--input-bg);
        color: var(--text);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem 1.2rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 2px rgba(61, 139, 253, 0.25);
    }
    
    .stTextInput > label {
        color: var(--text);
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0.8rem;
    }
    
    /* Results styling */
    .result-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--result-border);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border-color: rgba(61, 139, 253, 0.3);
    }
    
    .result-url {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--accent);
        margin-bottom: 0.8rem;
        display: block;
        text-decoration: none;
        transition: color 0.2s ease;
    }
    
    .result-url:hover {
        color: var(--accent-hover);
        text-decoration: underline;
    }
    
    .result-preview {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .result-meta {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 1rem;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
    }
    
    .meta-icon {
        margin-right: 0.4rem;
    }
    
    /* Status messages */
    .stWarning, .stError, .stInfo {
        border-radius: 12px;
        font-size: 1rem;
        padding: 1rem;
        background: var(--card-bg) !important;
        border: 1px solid;
    }
    
    .stWarning {
        border-color: #ffab2d !important;
        color: #ffca80 !important;
    }
    
    .stError {
        border-color: #ff4e4e !important;
        color: #ff7e7e !important;
    }
    
    .stInfo {
        border-color: var(--accent) !important;
        color: #a3c8ff !important;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .loading-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: var(--accent);
        display: inline-block;
        margin: 0 4px;
        animation: bounce 1.5s infinite ease-in-out;
    }
    
    .loading-dot:nth-child(1) {
        animation-delay: 0s;
    }
    
    .loading-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .loading-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    .loading-text {
        margin-top: 1rem;
        font-size: 1rem;
        color: var(--text-secondary);
    }
    
    /* Animations */
    @keyframes pulse {
        0% {
            opacity: 1;
        }
        50% {
            opacity: 0.6;
        }
        100% {
            opacity: 1;
        }
    }
    
    @keyframes bounce {
        0%, 80%, 100% {
            transform: scale(0);
        }
        40% {
            transform: scale(1);
        }
    }
    
    /* Additional UI components */
    .stProgress > div > div > div {
        background-color: var(--accent);
    }
    
    .stProgress {
        height: 6px;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--text-secondary);
        font-size: 0.9rem;
        opacity: 0.7;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Custom header with logo animation
st.markdown(
    """
    <div class="search-header">
        <span class="logo-icon">🔭</span>
        <h1 class="logo-text">Search Now!!</h1>
    </div>
    """, 
    unsafe_allow_html=True
)

# Simple search input without container wrapper
query = st.text_input("Search the universe of information", placeholder="Enter your query...")

# Handle search functionality
if query:
    # Show a progress bar to indicate loading
    progress_placeholder = st.empty()
    progress_bar = progress_placeholder.progress(0)
    
    # Display loading animation
    loading_placeholder = st.empty()
    loading_placeholder.markdown(
        """
        <div class="loading-container">
            <div>
                <span class="loading-dot"></span>
                <span class="loading-dot"></span>
                <span class="loading-dot"></span>
            </div>
            <div class="loading-text">Searching across the stars...</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Simulate progress
    for i in range(100):
        progress_bar.progress(i + 1)
        time.sleep(0.01)
    
    # Try to fetch results
    try:
        url = f'http://127.0.0.1:5000/search?q={query}'
        response = requests.get(url)
        
        # Clear loading indicators
        progress_placeholder.empty()
        loading_placeholder.empty()
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            
            if results:
                st.markdown(f"<h3 style='color: var(--text); margin-bottom: 1.5rem;'>Found {len(results)} results for '{query}'</h3>", unsafe_allow_html=True)
                
                for result in results:
                    # Create a card for each result
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <a href="{result['url']}" target="_blank" class="result-url">
                                {result['url']}
                            </a>
                            <div class="result-preview">
                                {result['content']}
                            </div>
                            <div class="result-meta">
                                <span class="meta-item">
                                    <span class="meta-icon">🔎</span>
                                    {result.get('search_word_count', 'N/A')} matches
                                </span>
                                <span class="meta-item">
                                    <span class="meta-icon">📊</span>
                                    Relevance: {int((result.get('search_word_count', 1) / 10) * 100) if result.get('search_word_count') else 50}%
                                </span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    """
                    <div style="text-align: center; padding: 3rem 1rem;">
                        <span style="font-size: 3rem;">🔍</span>
                        <h3 style="color: var(--text-secondary); margin-top: 1rem;">No results found</h3>
                        <p style="color: var(--text-secondary);">Try different keywords or broaden your search</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div style="text-align: center; padding: 3rem 1rem; color: #ff7e7e;">
                    <span style="font-size: 3rem;">⚠️</span>
                    <h3 style="margin-top: 1rem;">Error connecting to search service</h3>
                    <p>Please make sure the search server is running at http://127.0.0.1:5000</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 3rem 1rem; color: #ff7e7e;">
                <span style="font-size: 3rem;">❗</span>
                <h3 style="margin-top: 1rem;">Something went wrong</h3>
                <p>Error: {str(e)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# If no search query, show welcome message
if not query:
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 1rem;">
            <span style="font-size: 4rem; display: block; margin-bottom: 1.5rem;">✨</span>
            <h2 style="color: var(--text); margin-bottom: 1rem;">Discover the universe of information</h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
                Enter keywords above to explore. Our advanced search algorithm will find the most relevant results for you.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Footer
st.markdown(
    """
    <div class="footer">
        <p>Powered Ahmed, Mohamed, Eslam and Magdy • © 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)