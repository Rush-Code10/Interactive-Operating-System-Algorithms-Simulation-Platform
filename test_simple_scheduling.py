"""Simple test to verify basic scheduling functionality."""

from algorithms.base import SchedulingBase
from models.data_models import Process, SimulationResult

# Test just the FCFS scheduler first
class SimpleFCFS(SchedulingBase):
    def __init__(self):
        super().__init__()
        self.algorithm_name = "Simple FCFS"
    
    def execute(self, processes):
        self.reset()
        if not processes:
            return SimulationResult(
                algorithm_name=self.algorithm_name,
                execution_steps=[],
                metrics={},
                visualization_data={'gantt_chart': []},
                input_parameters={'processes': 0}
            )
        
        current_time = 0
        completion_times = {}
        
        # Sort by arrival time
        sorted_processes = sorted(processes, key=lambda p: p.arrival_time)
        
        for process in sorted_processes:
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            start_time = current_time
            end_time = current_time + process.burst_time
            
            self.gantt_chart_data.append({
                'process_id': process.pid,
                'start_time': start_time,
                'end_time': end_time,
                'duration': process.burst_time
            })
            
            current_time = end_time
            completion_times[process.pid] = current_time
        
        self.metrics = self._calculate_metrics(processes, completion_times)
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=[],
            metrics=self.metrics,
            visualization_data={'gantt_chart': self.gantt_chart_data},
            input_parameters={'processes': len(processes)}
        )

if __name__ == "__main__":
    # Test basic functionality
    processes = [
        Process(pid=1, arrival_time=0, burst_time=3, priority=0),
        Process(pid=2, arrival_time=1, burst_time=2, priority=0)
    ]
    
    scheduler = SimpleFCFS()
    result = scheduler.execute(processes)
    
    print(f"Algorithm: {result.algorithm_name}")
    print(f"Gantt chart: {result.visualization_data['gantt_chart']}")
    print(f"Metrics: {result.metrics}")
    print("Basic test passed!")