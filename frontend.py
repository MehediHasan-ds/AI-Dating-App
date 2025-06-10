import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="AI Dating App",
    page_icon="💕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
        margin-top:0;
    }

    .main-header {
        color: #FF6B6B;
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
    }
    .user-card {
        border: 2px solid #f0f0f0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .match-score {
        background: #4CAF50;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def search_profiles(query, user_id=None, top_k=5):
    """Search for profiles using the API"""
    try:
        payload = {
            "query": query,
            "user_id": user_id,
            "top_k": top_k
        }
        response = requests.post(f"{API_BASE_URL}/api/v1/dating/search", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def get_all_users():
    """Get all users from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/dating/users")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except:
        return []

def generate_conversation_starter(target_user_id):
    """Generate conversation starter"""
    try:
        payload = {"target_user_id": target_user_id}
        response = requests.post(f"{API_BASE_URL}/api/v1/chat/opener", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def display_user_card(user, show_score=True):
    """Display a user card"""
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # User info
            st.markdown(f"""
            <div class="user-card">
                <h3>💫 {user.get('name', 'Unknown')}</h3>
                <p><strong>Age:</strong> {user.get('age', 'N/A')}</p>
                <p><strong>Location:</strong> {user.get('location', 'N/A')}</p>
                <p><strong>Profession:</strong> {user.get('profession', 'N/A')}</p>
                <p><strong>Interests:</strong> {', '.join(user.get('interests', []))}</p>
                <p><strong>Looking for:</strong> {user.get('relationship_type', 'N/A')} relationship</p>
                <p><strong>Bio:</strong> {user.get('bio', 'No bio available')}</p>
            </div>
            """, unsafe_allow_html=True)

            if show_score and 'match_percentage' in user:
                st.markdown(f"""
                <div class="match-score">
                    🎯 Match Score: {user['match_percentage']}%
                </div>
                <div style="margin-bottom: 1.5rem;"></div>  <!-- Add spacing -->
                """, unsafe_allow_html=True)


        # ✅ Move this outside `with col2:`
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button(f"💬 Chat with {user.get('name', 'User')}", key=f"chat_{user.get('id')}"):
                starter = generate_conversation_starter(user.get('id'))
                if starter:
                    st.success(f"💡 Conversation starter: {starter['starter']}")
                else:
                    st.info("💬 Start a conversation with this person!")

        with col_btn2:
            if st.button(f"👍 Like", key=f"like_{user.get('id')}"):
                st.success("❤️ Liked! They'll be notified if it's a match.")

        with col_btn3:
            if st.button(f"⭐ Super Like", key=f"super_{user.get('id')}"):
                st.success("⭐ Super Liked! You'll stand out in their feed.")


def main():
    # Header
    st.markdown("""
        <div class="main-header-wrapper">
            <div class="main-header">💕 AI Dating App</div>
        </div>
        """, unsafe_allow_html=True)

    
    # Check API health
    if not check_api_health():
        st.error("🚨 Backend API is not running! Please start the FastAPI server first.")
        st.info("Run: `uvicorn main:app --reload` in your terminal")
        st.stop()
    
    st.toast("✅ Connected to backend API")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔍 Search Settings")
        
        # Current user selection
        users = get_all_users()
        if users:
            user_options = {f"{user['name']} ({user['age']})": user['id'] for user in users}
            selected_user = st.selectbox(
                "👤 Search as user:",
                options=["Anonymous"] + list(user_options.keys()),
                help="Select which user you are to get personalized results"
            )
            current_user_id = user_options.get(selected_user) if selected_user != "Anonymous" else None
        else:
            current_user_id = None
            st.warning("No users loaded")
        
        # Search parameters
        st.markdown("### 🎯 Search Parameters")
        top_k = st.slider("Number of results", 1, 10, 5)
        
        # Quick search templates
        st.markdown("### 🚀 Quick Search Templates")
        template_queries = [
            "Software engineers in their late twenties who love outdoor activities",
            "Creative professionals who enjoy art and music",
            "Fitness enthusiasts looking for serious relationships",
            "Travel lovers in their thirties",
            "Coffee lovers who enjoy reading and quiet evenings",
            "Adventure seekers who love hiking and camping",
            "Foodies who love cooking and trying new restaurants"
        ]
        
        selected_template = st.selectbox(
            "Choose a template:",
            ["Custom Query"] + template_queries
        )
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # st.markdown("## 🔍 Natural Language Search")
        
        # Search query input
        if selected_template != "Custom Query":
            search_query = st.text_area(
                "What kind of person are you looking for?",
                value=selected_template,
                height=100,
                help="Describe your ideal match in natural language"
            )
        else:
            search_query = st.text_area(
                "What kind of person are you looking for?",
                placeholder="e.g., Looking for a creative professional in their twenties who loves travel and photography",
                height=100,
                help="Describe your ideal match in natural language"
            )
        
        # Search button
        if st.button("🔍 Search for Matches", type="primary", use_container_width=True):
            if search_query.strip():
                with st.spinner("🤖 AI is finding your perfect matches..."):
                    results = search_profiles(search_query, current_user_id, top_k)
                    
                if results and results.get('success'):
                    st.success(f"✨ Found {results['total_results']} matches!")
                    
                    # Display results
                    st.markdown("## 💫 Your Matches")
                    
                    for i, user in enumerate(results['results'], 1):
                        st.markdown(f"### Match #{i}")
                        display_user_card(user, show_score=True)
                        st.markdown("---")
                    
                    # Store results in session state for analytics
                    st.session_state['last_search'] = results
                else:
                    st.warning("🔍 No matches found. Try adjusting your search criteria.")
            else:
                st.warning("⚠️ Please enter a search query")
    
    with col2:
        st.markdown("## 📊 Search Analytics")
        
        if 'last_search' in st.session_state:
            results = st.session_state['last_search']
            
            # Match scores chart
            if results['results']:
                scores_data = [
                    {
                        'Name': user['name'],
                        'Match %': user['match_percentage'],
                        'Age': user['age']
                    }
                    for user in results['results']
                ]
                
                df = pd.DataFrame(scores_data)
                
                # Bar chart of match scores
                fig = px.bar(
                    df, 
                    x='Name', 
                    y='Match %',
                    title='Match Scores',
                    color='Match %',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Age distribution
                fig2 = px.histogram(
                    df,
                    x='Age',
                    title='Age Distribution of Matches',
                    nbins=10
                )
                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)
        
        # Recent searches (placeholder)
        st.markdown("### 🕒 Recent Searches")
        st.info("Search history will appear here")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👥 View All Users"):
            st.markdown("## 👥 All Users")
            users = get_all_users()
            for user in users:
                display_user_card(user, show_score=False)
                st.markdown("---")
    
    with col2:
        if st.button("🎲 Random Match"):
            import random
            users = get_all_users()
            if users:
                random_user = random.choice(users)
                st.markdown("## 🎲 Random Match")
                display_user_card(random_user, show_score=False)
    
    with col3:
        if st.button("📈 App Stats"):
            users = get_all_users()
            if users:
                st.markdown("## 📈 App Statistics")
                
                # Basic stats
                avg_age = sum(user['age'] for user in users) / len(users)
                locations = [user['location'] for user in users]
                professions = [user['profession'] for user in users]
                
                col_stat1, col_stat2 = st.columns(2)
                
                with col_stat1:
                    st.metric("Total Users", len(users))
                    st.metric("Average Age", f"{avg_age:.1f}")
                
                with col_stat2:
                    st.metric("Unique Locations", len(set(locations)))
                    st.metric("Unique Professions", len(set(professions)))

if __name__ == "__main__":
    main()