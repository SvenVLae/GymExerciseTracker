import pandas as pd
import sqlite3 as sql
import os
from datetime import datetime

class DataHandler:
    def __init__(self):
        self.conn = sql.connect('data/data.db')
        self.cursor = self.conn.cursor()
        self.workouts = "data/workouts.csv"
        self.exercises = "data/exercises.csv"
        self.history = "data/history.csv"
        self._initialize_data_files()

    def _initialize_data_files(self):
        """Initialize data files if they don't exist"""
        # Create Workouts table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """)

        # Create Exercises table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            name TEXT NOT NULL UNIQUE,
            FOREIGN KEY (workout_id) REFERENCES Workouts(id) ON DELETE CASCADE
        )
        """)

        # Create History table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS History (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            workout_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES Workouts(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES Exercises(id) ON DELETE CASCADE,
            UNIQUE(date, workout_id, exercise_id) 
        )
        """)

        # Create Max table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Max (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            max INTEGER NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES Workouts(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES Exercises(id) ON DELETE CASCADE,
            UNIQUE(workout_id, exercise_id) 
        )
        """)

        # Commit and close connection
        self.conn.commit()

        # --- Prepopulate Data ---
        workouts_exercises = [
            ('Push', 'Shoulder'),
            ('Push', 'Bench'),
            ('Push', 'Incline bench'),
            ('Push', 'Triceps'),
            ('Push', 'Horizontal Raises'),
            ('Push', 'Fly-overs'),
            ('Push', 'Cable pull'),
            ('Push', 'Incline press'),
            ('Pull', 'Onderrug'),
            ('Pull', 'Bicep curl'),
            ('Pull', 'Pull-over'),
            ('Pull', 'Pull-down'),
            ('Pull', 'Seated row'),
            ('Pull', 'Row'),
            ('Pull', 'Hammer curls'),
            ('Pull', 'Pull-up'),
            ('Legs', 'Leg press'),
            ('Legs', 'Seated leg curls'),
            ('Legs', 'Back seated leg curls'),
            ('Legs', 'Kuiten'),
            ('Legs', 'Abductor'),
            ('Core', 'Abdominal crunch'),
            ('Core', 'Buikspier rood')
        ]

        # Insert Workouts
        for workout, _ in workouts_exercises:
            self.cursor.execute("INSERT OR IGNORE INTO Workouts (name) VALUES (?)", (workout,))
        
        # Commit changes
        self.conn.commit()
        
        # Insert Exercises
        for workout, exercise in workouts_exercises:
            workout_id = self.cursor.execute("SELECT id FROM Workouts WHERE name = ?", (workout,)).fetchall()[0][0]
            self.cursor.execute("""
            INSERT OR IGNORE INTO Exercises (workout_id, name) 
            VALUES (?, ?)
            """, (workout_id, exercise))
        
        # Commit changes
        self.conn.commit()

        # Insert Max
        for workout, exercise in workouts_exercises:
            workout_id, exercise_id = self.cursor.execute("SELECT workout_id, id FROM Exercises WHERE name = ?", (exercise,)).fetchall()[0]
            
            self.cursor.execute("""
            INSERT OR IGNORE INTO Max (workout_id, exercise_id, max) 
            VALUES (?, ?, 0)
            """, (workout_id, exercise_id))

        # Commit changes
        self.conn.commit()
    
    def get_workouts(self):
        """Get list of exercises for workout"""
        workouts = pd.DataFrame(columns=['Workout'], data=self.cursor.execute("SELECT name FROM Workouts").fetchall())
        return workouts['Workout']

    def get_exercises(self):
        """Get list of exercises for workout"""
        exercises = pd.DataFrame(columns=['Workout', 'Exercise'], data=self.cursor.execute("SELECT w.name, e.name FROM Exercises e JOIN Workouts w ON e.workout_id = w.id").fetchall())
        return exercises
    
    def get_exercises_by_workout(self, workout):
        """Get list of exercises for workout"""
        exercises = self.get_exercises()
        return exercises[exercises['Workout'] == workout]['Exercise']
    
    def get_last_workout(self, date, workout, exercise):
        """Get the last workout for a specific exercise"""
        query = """
        SELECT History.date, Workouts.name AS workout_name, Exercises.name AS exercise_name, 
            History.sets, History.reps, History.weight
        FROM History
        JOIN Workouts ON History.workout_id = Workouts.id
        JOIN Exercises ON History.exercise_id = Exercises.id
        WHERE History.date < ? AND Workouts.name = ? AND Exercises.name = ? 
        ORDER BY History.date DESC
        LIMIT 1;
        """

        data = self.cursor.execute(query, (date, workout, exercise)).fetchall()
        if len(data) > 0:
            return pd.DataFrame(data = data, columns=['Date', 'Workout', 'Exercise', 'Sets', 'Reps', 'Weight'])
        return None
    
    def get_current_workout(self, date, workout, exercise):
        """Get the last workout for a specific exercise"""
        query = """
        SELECT History.date, Workouts.name AS workout_name, Exercises.name AS exercise_name, 
            History.sets, History.reps, History.weight
        FROM History
        JOIN Workouts ON History.workout_id = Workouts.id
        JOIN Exercises ON History.exercise_id = Exercises.id
        WHERE History.date = ? AND Workouts.name = ? AND Exercises.name = ? 
        ORDER BY History.date DESC
        LIMIT 1;
        """

        data = self.cursor.execute(query, (date, workout, exercise)).fetchall()
        if len(data) > 0:
            return pd.DataFrame(data = data, columns=['Date', 'Workout', 'Exercise', 'Sets', 'Reps', 'Weight'])
        return None
    
    def save_workout(self, date, workout, exercise, sets, reps, weight):
        """Add new workout entry"""
        # Define the SQL query to insert or update history
        query = """
        INSERT INTO History (date, workout_id, exercise_id, sets, reps, weight)
        SELECT ?, 
            Workouts.id, 
            Exercises.id, 
            ?, ?, ?
        FROM Workouts, Exercises
        WHERE Workouts.name = ? AND Exercises.name = ?
        ON CONFLICT(date, workout_id, exercise_id) 
        DO UPDATE SET 
            sets = excluded.sets, 
            reps = excluded.reps, 
            weight = excluded.weight;
        """

        # Execute the query with the given parameters
        self.cursor.execute(query, (date, sets, reps, weight, workout, exercise))

        # Commit the transaction
        self.conn.commit()
    
    def delete_workout(self, date, workout, exercise):
        """Add new workout entry"""
        # Define the SQL query to insert or update history
        query = """
        DELETE FROM History 
        WHERE date = ? 
        AND workout_id = (SELECT id FROM Workouts WHERE name = ?) 
        AND exercise_id = (SELECT id FROM Exercises WHERE name = ?);
        """

        # Execute the query with the given parameters
        self.cursor.execute(query, (date, workout, exercise))

        # Commit the transaction
        self.conn.commit()

    def get_workout_history(self):
        """Get workout history"""
        """Get the last workout for a specific exercise"""
        query = """
        SELECT History.date, Workouts.name AS workout_name, Exercises.name AS exercise_name, 
            History.sets, History.reps, History.weight
        FROM History
        JOIN Workouts ON History.workout_id = Workouts.id
        JOIN Exercises ON History.exercise_id = Exercises.id
        ORDER BY History.date DESC;
        """

        data = self.cursor.execute(query).fetchall()
        if len(data) > 0:
            return pd.DataFrame(data = data, columns=['Date', 'Workout', 'Exercise', 'Sets', 'Reps', 'Weight'])
        return None

    def get_max(self, workout, exercise):
        """Get the max weight for an exercise"""
        query = """
        SELECT max
        FROM Max
        JOIN Workouts ON Max.workout_id = Workouts.id
        JOIN Exercises ON Max.exercise_id = Exercises.id
        WHERE Workouts.name = ? AND Exercises.name = ?
        """

        data = self.cursor.execute(query, (workout, exercise)).fetchall()
        if len(data) > 0:
            return data[0][0]
        return None
    
    def save_max(self, workout, exercise, max_weight):
        """Save the max weight for an exercise"""
        query = """
        INSERT INTO Max (workout_id, exercise_id, max)
        SELECT Workouts.id, Exercises.id, ?
        FROM Workouts, Exercises
        WHERE Workouts.name = ? AND Exercises.name = ?
        ON CONFLICT(workout_id, exercise_id) 
        DO UPDATE SET 
            max = ?;
        """

        # Execute the query with the given parameters
        self.cursor.execute(query, (max_weight, workout, exercise, max_weight))

        # Commit the transaction
        self.conn.commit()
    