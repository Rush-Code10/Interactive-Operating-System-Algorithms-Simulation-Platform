"""
Base classes for page replacement and CPU scheduling algorithms.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.data_models import SimulationResult, SimulationStep, Process

class PageReplacementBase(ABC):
    """Abstract base class for page replacement algorithms."""
    
    def __init__(self):
        self.simulation_steps: List[SimulationStep] = []
        self.metrics: Dict[str, float] = {}
        self.algorithm_name: str = self.__class__.__name__
    
    @abstractmethod
    def execute(self, page_sequence: List[int], frame_count: int) -> SimulationResult:
        """
        Execute the page replacement algorithm.
        
        Args:
            page_sequence: List of page numbers to be referenced
            frame_count: Number of available frames in memory
            
        Returns:
            SimulationResult containing execution steps and metrics
        """
        pass
    
    def get_step_by_step(self) -> List[SimulationStep]:
        """Return the step-by-step execution trace."""
        return self.simulation_steps
    
    def get_metrics(self) -> Dict[str, float]:
        """Return performance metrics for the algorithm."""
        return self.metrics
    
    def reset(self):
        """Reset the algorithm state for a new simulation."""
        self.simulation_steps.clear()
        self.metrics.clear()
    
    def _calculate_metrics(self, total_references: int, page_faults: int) -> Dict[str, float]:
        """Calculate standard page replacement metrics."""
        hit_ratio = (total_references - page_faults) / total_references if total_references > 0 else 0
        fault_ratio = page_faults / total_references if total_references > 0 else 0
        
        return {
            'total_references': total_references,
            'page_faults': page_faults,
            'page_hits': total_references - page_faults,
            'hit_ratio': hit_ratio,
            'fault_ratio': fault_ratio
        }

class SchedulingBase(ABC):
    """Abstract base class for CPU scheduling algorithms."""
    
    def __init__(self):
        self.simulation_steps: List[SimulationStep] = []
        self.metrics: Dict[str, float] = {}
        self.algorithm_name: str = self.__class__.__name__
        self.gantt_chart_data: List[Dict[str, Any]] = []
    
    @abstractmethod
    def execute(self, processes: List[Process]) -> SimulationResult:
        """
        Execute the CPU scheduling algorithm.
        
        Args:
            processes: List of processes to be scheduled
            
        Returns:
            SimulationResult containing execution timeline and metrics
        """
        pass
    
    def get_step_by_step(self) -> List[SimulationStep]:
        """Return the step-by-step execution trace."""
        return self.simulation_steps
    
    def get_metrics(self) -> Dict[str, float]:
        """Return performance metrics for the algorithm."""
        return self.metrics
    
    def get_gantt_chart_data(self) -> List[Dict[str, Any]]:
        """Return data for Gantt chart visualization."""
        return self.gantt_chart_data
    
    def reset(self):
        """Reset the algorithm state for a new simulation."""
        self.simulation_steps.clear()
        self.metrics.clear()
        self.gantt_chart_data.clear()
    
    def _calculate_metrics(self, processes: List[Process], completion_times: Dict[int, int]) -> Dict[str, float]:
        """Calculate standard scheduling metrics."""
        total_turnaround_time = 0
        total_waiting_time = 0
        total_response_time = 0
        
        for process in processes:
            completion_time = completion_times.get(process.pid, 0)
            turnaround_time = completion_time - process.arrival_time
            waiting_time = turnaround_time - process.burst_time
            
            total_turnaround_time += turnaround_time
            total_waiting_time += waiting_time
            # Response time calculation will be refined in specific algorithm implementations
            total_response_time += waiting_time  # Simplified for base class
        
        process_count = len(processes)
        if process_count == 0:
            return {}
        
        return {
            'average_turnaround_time': total_turnaround_time / process_count,
            'average_waiting_time': total_waiting_time / process_count,
            'average_response_time': total_response_time / process_count,
            'throughput': process_count / max(completion_times.values()) if completion_times else 0
        }