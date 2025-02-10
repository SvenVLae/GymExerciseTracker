import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from utils import calculate_progress, format_date

def update_workout_data(data_handler):
    for workout in data_handler.get_workouts():
        for exercise in data_handler.get_exercises_by_workout(workout):
            if f"save_{workout}_{exercise}" in st.session_state:
                if st.session_state[f"save_{workout}_{exercise}"]:
                    data_handler.save_workout(
                        st.session_state["workout_date"],
                        workout,
                        exercise,
                        st.session_state[f"sets_{workout}_{exercise}"],
                        st.session_state[f"reps_{workout}_{exercise}"],
                        st.session_state[f"weight_{workout}_{exercise}"]
                    )
                else:
                    data_handler.delete_workout(
                        st.session_state["workout_date"],
                        workout,
                        exercise
                    )

        

def render_workout_form(data_handler):
    # Date selector with European format
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now().date(),
            format="DD/MM/YYYY",
            key="workout_date",
            help="Choose a date of your workout"
        )

    for workout in data_handler.get_workouts():
        with st.expander(f"**💪 {workout}**"):
            for exercise in data_handler.get_exercises_by_workout(workout):
                with st.form(f"{exercise}"):
                    # Get last workout for this exercise
                    last_workout = data_handler.get_last_workout(selected_date, workout, exercise)
                    """
                    header_col, open_col = st.columns([12, 1])
                    with header_col:
                        # Workout details
                        if last_workout is not None:
                            st.subheader(f"**{exercise}** - Last: {last_workout['Date'].iloc[0]}")
                        else:
                            st.subheader(f"**{exercise}**")
                    
                    with open_col:
                        if st.form_submit_button("v", use_container_width=True):
                            
                    """
                    if st.form_submit_button(f"**{exercise}**", use_container_width=True):
                        if f"isOpened_{workout}_{exercise}" not in st.session_state:
                                st.session_state[f"isOpened_{workout}_{exercise}"] = False
                            st.session_state[f"isOpened_{workout}_{exercise}"] = not st.session_state[f"isOpened_{workout}_{exercise}"]

                    if last_workout is not None:
                        st.text("- Last: {last_workout['Date'].iloc[0]}")

                    
                    if f"isOpened_{workout}_{exercise}"in st.session_state and st.session_state[f"isOpened_{workout}_{exercise}"]:
                        save_col, del_col = st.columns([1, 1])
                        with save_col:
                            if st.form_submit_button("Save exercise", use_container_width=True):
                                data_handler.save_workout(
                                    selected_date,
                                    workout,
                                    exercise,
                                    st.session_state[f"sets_{workout}_{exercise}"],
                                    st.session_state[f"reps_{workout}_{exercise}"],
                                    st.session_state[f"weight_{workout}_{exercise}"]
                                )
                        

                        show_current = False
                        with del_col:
                            current_workout = data_handler.get_current_workout(selected_date, workout, exercise)
                            if current_workout is not None:
                                if not st.form_submit_button("Remove exercise", use_container_width=True):
                                    show_current = True     
                                else:
                                    data_handler.delete_workout(
                                        selected_date,
                                        workout,
                                        exercise
                                    )
                        current_workout = data_handler.get_current_workout(selected_date, workout, exercise)

                        if show_current:
                            st.write(f"Current workout: {current_workout['Sets'].iloc[0]} sets, {current_workout['Reps'].iloc[0]} reps, {current_workout['Weight'].iloc[0]} kg")
                        
                        # Set default values from last workout if available
                        default_sets = int(current_workout['Sets'].iloc[0]) if current_workout is not None else int(last_workout['Sets'].iloc[0]) if last_workout is not None else 3
                        default_reps = int(current_workout['Reps'].iloc[0]) if current_workout is not None else int(last_workout['Reps'].iloc[0]) if last_workout is not None else 10
                        default_weight = float(current_workout['Weight'].iloc[0]) if current_workout is not None else float(last_workout['Weight'].iloc[0]) if last_workout is not None else 20.0

                        # Workout details
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.number_input("Sets", min_value=1, value=default_sets, key=f"sets_{workout}_{exercise}")
                        with col2:
                            st.number_input("Reps", min_value=1, value=default_reps, key=f"reps_{workout}_{exercise}")
                        with col3:
                            st.number_input("Weight (kg)", min_value=0.0, value=default_weight, step=0.5, key=f"weight_{workout}_{exercise}")

                        

                        maxInput_col, saveMax_col = st.columns([3, 1], vertical_alignment="bottom")


                    
                        with saveMax_col:
                            if st.form_submit_button("Save max", use_container_width=True,):
                                data_handler.save_max(
                                    workout,
                                    exercise,
                                    st.session_state[f"max_{workout}_{exercise}"]
                                )

                        with maxInput_col:
                            max_weight = float(data_handler.get_max(workout, exercise))
                            st.number_input("Max Weight (kg)", min_value=0.0, value=max_weight, step=0.5, key=f"max_{workout}_{exercise}")

def render_history_view(data_handler):
    """Render the exercise history view"""
    history_df = data_handler.get_workout_history()

    if history_df is None:
        st.warning("No workout history available")
        return

    # Exercise selection for progress view
    workout = st.selectbox(
        "Select workout to view progress",
        history_df['Workout'].unique()
    )

    exercise = st.selectbox(
        "Select exercise to view progress",
        history_df[history_df['Workout'] == workout]['Exercise'].unique()
    )

    # Get exercise progress data
    exercise_data = history_df[(history_df['Workout'] == workout) & (history_df['Exercise'] == exercise)].sort_values('Date')

    if not exercise_data.empty:
        # Format the date column to remove time
        exercise_data['Date'] = pd.to_datetime(exercise_data['Date']).dt.date

        # Progress metrics
        last_weight, progress = calculate_progress(history_df, workout, exercise)

        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Weight", f"{last_weight}kg")
        with col2:
            if progress is not None:
                st.metric("Progress", f"{progress:.1f}%")

        # Progress chart
        fig = px.line(
            exercise_data,
            x='Date',
            y='Weight',
            title=f'{exercise} Progress Over Time'
        )
        # Update x-axis to show only dates in European format
        fig.update_xaxes(
            tickformat="%d/%m/%Y",
            dtick="D1"
        )
        st.plotly_chart(fig)

        # History table
        st.subheader("Exercise History")
        # Create a copy of the dataframe to avoid modifying the original
        display_data = exercise_data.copy()
        # Format the date column for display
        display_data['Date'] = display_data['Date'].apply(lambda x: x.strftime('%d/%m/%Y'))
        st.dataframe(
            display_data[['Date', 'Sets', 'Reps', 'Weight']]
            .sort_values('Date', ascending=False)
        )
