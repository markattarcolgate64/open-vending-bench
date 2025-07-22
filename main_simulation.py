#Main program entry point to run the economic agent simulation 
from datetime import datetime, timezone, timedelta
import uuid
from database import SimulationDatabase

STARTING_BALANCE = 500
DAILY_FEE = 2

class VendingMachineSimulation:
    def __init__(self):
        self.simulation_id = str(uuid.uuid4())
        self.balance = STARTING_BALANCE
        self.inventory = {}
        # Start at the beginning of the current day in UTC
        now = datetime.now(timezone.utc)
        self.current_time = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
        # Initialize database
        self.db = SimulationDatabase()
        self.log_state()

    def log_state(self):
        """Log current state to database"""
        self.db.log_state(self.simulation_id, self.current_time, self.balance)
    
    def advance_time(self, days=0, minutes=0):
        """Advance simulation time by specified days and minutes"""
        self.current_time += timedelta(days=days, minutes=minutes)
        return self.current_time
    
    def get_day_report(self):
        print(f"Day {self.current_time.strftime('%Y-%m-%d %H:%M UTC')} - Balance: ${self.balance}, Inventory: {self.inventory}")

    def run_day(self):
        # Advance to next day first
        
        self.balance = self.balance - DAILY_FEE
        self.log_state()
        self.get_day_report()
        self.advance_time(days=1)


    def start_simulation(self, days):
        self.advance_time(days=1)
        for _ in range(days):
            self.run_day()







def run_simulation():
    simulation = VendingMachineSimulation()
    print(f"Starting simulation {simulation.simulation_id} at {simulation.current_time.strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Test the time system with database logging
    simulation.start_simulation(3)
    
    # Show database history
    print("\nSimulation History:")
    history = simulation.db.get_simulation_history(simulation.simulation_id)
    for timestamp, balance in history:
        print(f"{timestamp}: ${balance}")
    
    simulation.db.close()


if __name__ == "__main__":
    run_simulation()