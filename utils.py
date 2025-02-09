import streamlit as st
import pandas as pd

def initialize_session_state():
    """Initialize session state variables"""
    if 'workout_added' not in st.session_state:
        st.session_state.workout_added = False

def calculate_progress(history_df, workout, exercise):
    """Calculate progress metrics for an exercise"""
    if history_df.empty:
        return None, None
    
    exercise_data = history_df[(history_df['Workout'] == workout) & (history_df['Exercise'] == exercise)].sort_values('Date')
    if len(exercise_data) < 2:
        return None, None
    
    first_weight = exercise_data.iloc[0]['Weight']
    last_weight = exercise_data.iloc[-1]['Weight']
    progress = ((last_weight - first_weight) / first_weight) * 100
    
    return last_weight, progress

def format_date(date_str):
    """Format date string for display"""
    return pd.to_datetime(date_str).strftime('%d/%m/%Y')