import sqlite3
from datetime import datetime

class SimulationDatabase:
    def __init__(self, db_path='vending_simulation.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create simulation tracking tables"""
        cursor = self.conn.cursor()
        
        # Main simulation state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulation_state (
                timestamp TEXT NOT NULL,
                simulation_id TEXT NOT NULL,
                balance REAL NOT NULL,
                PRIMARY KEY (timestamp, simulation_id)
            )
        ''')
        
        self.conn.commit()
    
    def log_state(self, simulation_id, timestamp, balance):
        """Log current simulation state"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO simulation_state (timestamp, simulation_id, balance)
            VALUES (?, ?, ?)
        ''', (timestamp.isoformat(), simulation_id, balance))
        self.conn.commit()
    
    def get_simulation_history(self, simulation_id):
        """Get all states for a simulation"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT timestamp, balance FROM simulation_state
            WHERE simulation_id = ?
            ORDER BY timestamp
        ''', (simulation_id,))
        return cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.conn.close()