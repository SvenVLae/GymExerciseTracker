import streamlit as st
from data_handler import DataHandler
from components import render_workout_form, render_history_view
from utils import initialize_session_state

# Page config
st.set_page_config(
    page_title="Gym Exercise Tracker",
    page_icon="💪",
    layout="wide"
)

# Initialize data handler
data_handler = DataHandler()

# Initialize session state
initialize_session_state()

# Main title
st.title("💪 Gym Exercise Tracker")


# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Daily Workout", "Exercise History"])

if page == "Daily Workout":
    # Render workout form
    render_workout_form(data_handler)

elif page == "Exercise History":
    render_history_view(data_handler)

# Footer
st.markdown("---")
st.markdown("Built by Sven -- With the help of AI 💪")