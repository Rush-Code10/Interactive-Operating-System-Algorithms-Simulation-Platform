"""
CPU Scheduling Algorithms Implementation.

This module implements various CPU scheduling algorithms including:
- FCFS (First-Come-First-Served)
- SJF (Shortest Job First) - both preemptive and non-preemptive
- Round Robin with configurable time quantum
- Priority Scheduling - both preemptive and non-preemptive
- MLFQ (Multi-Level Feedback Queue)
- EDF (Earliest Deadline First) for real-time scheduling
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import deque
import heapq
from copy import deepcopy

from .base import SchedulingBase
from models.data_models import Process, SimulationResult, SimulationStep, ProcessState


class FCFSScheduler(SchedulingBase):
    """First-Come-First-Served (FCFS) scheduling algorithm."""
    
    def __init__(self):
        super().__init__()
        self.algorithm_name = "FCFS"
    
    def execute(self, processes: List[Process]) -> SimulationResult:
        """Execute FCFS scheduling algorithm."""
        self.reset()
        
        if not processes:
            return self._create_empty_result()
        
        # Sort processes by arrival time
        sorted_processes = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
        
        current_time = 0
        completion_times = {}
        response_times = {}
        
        for i, process in enumerate(sorted_processes):
            # Wait for process arrival if necessary
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            # Record response time (first time process gets CPU)
            response_times[process.pid] = current_time - process.arrival_time
            
            # Create simulation step for process start
            self._add_simulation_step(
                step_number=len(self.simulation_steps),
                timestamp=current_time,
                action=f"Process P{process.pid} starts execution",
                process_id=process.pid,
                state_before={"current_time": current_time, "running_process": None},
                state_after={"current_time": current_time, "running_process": process.pid}
            )
            
            # Add Gantt chart entry
            self.gantt_chart_data.append({
                "process_id": process.pid,
                "start_time": current_time,
                "end_time": current_time + process.burst_time,
                "duration": process.burst_time
            })
            
            # Execute process
            current_time += process.burst_time
            completion_times[process.pid] = current_time
            
            # Create simulation step for process completion
            self._add_simulation_step(
                step_number=len(self.simulation_steps),
                timestamp=current_time,
                action=f"Process P{process.pid} completes execution",
                process_id=process.pid,
                state_before={"current_time": current_time - process.burst_time, "running_process": process.pid},
                state_after={"current_time": current_time, "running_process": None}
            )
        
        # Calculate metrics
        self.metrics = self._calculate_detailed_metrics(processes, completion_times, response_times)
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps,
            metrics=self.metrics,
            visualization_data={"gantt_chart": self.gantt_chart_data},
            input_parameters={"processes": len(processes)}
        )


class SJFScheduler(SchedulingBase):
    """Shortest Job First (SJF) scheduling algorithm."""
    
    def __init__(self, preemptive: bool = False):
        super().__init__()
        self.preemptive = preemptive
        self.algorithm_name = f"SJF ({'Preemptive' if preemptive else 'Non-preemptive'})"
    
    def execute(self, processes: List[Process]) -> SimulationResult:
        """Execute SJF scheduling algorithm."""
        self.reset()
        
        if not processes:
            return self._create_empty_result()
        
        if self.preemptive:
            return self._execute_preemptive_sjf(processes)
        else:
            return self._execute_non_preemptive_sjf(processes)
    
    def _execute_non_preemptive_sjf(self, processes: List[Process]) -> SimulationResult:
        """Execute non-preemptive SJF."""
        current_time = 0
        completed_processes = set()
        completion_times = {}
        response_times = {}
        ready_queue = []
        
        # Create working copies of processes
        process_copies = [deepcopy(p) for p in processes]
        
        while len(completed_processes) < len(processes):
            # Add newly arrived processes to ready queue
            for process in process_copies:
                if (process.arrival_time <= current_time and 
                    process.pid not in completed_processes and 
                    process.pid not in [p.pid for p in ready_queue]):
                    ready_queue.append(process)
            
            if not ready_queue:
                # No processes ready, advance time to next arrival
                next_arrival = min(p.arrival_time for p in process_copies 
                                 if p.pid not in completed_processes)
                current_time = next_arrival
                continue
            
            # Select process with shortest burst time
            selected_process = min(ready_queue, key=lambda p: (p.burst_time, p.arrival_time, p.pid))
            ready_queue.remove(selected_process)
            
            # Record response time
            response_times[selected_process.pid] = current_time - selected_process.arrival_time
            
            # Execute process
            self._add_simulation_step(
                step_number=len(self.simulation_steps),
                timestamp=current_time,
                action=f"Process P{selected_process.pid} starts execution (burst: {selected_process.burst_time})",
                process_id=selected_process.pid,
                state_before={"current_time": current_time, "ready_queue": [p.pid for p in ready_queue]},
                state_after={"current_time": current_time, "running_process": selected_process.pid}
            )
            
            self.gantt_chart_data.append({
                "process_id": selected_process.pid,
                "start_time": current_time,
                "end_time": current_time + selected_process.burst_time,
                "duration": selected_process.burst_time
            })
            
            current_time += selected_process.burst_time
            completion_times[selected_process.pid] = current_time
            completed_processes.add(selected_process.pid)
            
            self._add_simulation_step(
                step_number=len(self.simulation_steps),
                timestamp=current_time,
                action=f"Process P{selected_process.pid} completes execution",
                process_id=selected_process.pid,
                state_before={"current_time": current_time - selected_process.burst_time, "running_process": selected_process.pid},
                state_after={"current_time": current_time, "running_process": None}
            )
        
        self.metrics = self._calculate_detailed_metrics(processes, completion_times, response_times)
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps,
            metrics=self.metrics,
            visualization_data={"gantt_chart": self.gantt_chart_data},
            input_parameters={"processes": len(processes), "preemptive": self.preemptive}
        )
    
    def _execute_preemptive_sjf(self, processes: List[Process]) -> SimulationResult:
        """Execute preemptive SJF (SRTF - Shortest Remaining Time First)."""
        current_time = 0
        completed_processes = set()
        completion_times = {}
        response_times = {}
        ready_queue = []
        current_process = None
        
        # Create working copies of processes
        process_copies = {p.pid: deepcopy(p) for p in processes}
        
        # Track when each process first gets CPU
        first_execution = set()
        
        while len(completed_processes) < len(processes):
            # Add newly arrived processes to ready queue
            for process in processes:
                if (process.arrival_time <= current_time and 
                    process.pid not in completed_processes and 
                    process.pid not in [p.pid for p in ready_queue] and
                    (current_process is None or process.pid != current_process.pid)):
                    ready_queue.append(process_copies[process.pid])
            
            # Check if current process should be preempted
            if current_process and ready_queue:
                shortest_ready = min(ready_queue, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
                if shortest_ready.remaining_time < current_process.remaining_time:
                    # Preempt current process
                    ready_queue.append(current_process)
                    current_process = None
            
            # Select next process if no current process
            if current_process is None:
                if not ready_queue:
                    # No processes ready, advance time to next arrival
                    next_arrival = min(p.arrival_time for p in processes 
                                     if p.pid not in completed_processes and p.arrival_time > current_time)
                    current_time = next_arrival
                    continue
                
                current_process = min(ready_queue, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
                ready_queue.remove(current_process)
                
                # Record response time on first execution
                if current_process.pid not in first_execution:
                    response_times[current_process.pid] = current_time - current_process.arrival_time
                    first_execution.add(current_process.pid)
            
            # Execute for 1 time unit
            execution_start = current_time
            current_time += 1
            current_process.remaining_time -= 1
            
            # Add to Gantt chart (merge consecutive executions of same process)
            if (self.gantt_chart_data and 
                self.gantt_chart_data[-1]["process_id"] == current_process.pid and
                self.gantt_chart_data[-1]["end_time"] == execution_start):
                self.gantt_chart_data[-1]["end_time"] = current_time
                self.gantt_chart_data[-1]["duration"] += 1
            else:
                self.gantt_chart_data.append({
                    "process_id": current_process.pid,
                    "start_time": execution_start,
                    "end_time": current_time,
                    "duration": 1
                })
            
            # Check if process completed
            if current_process.remaining_time == 0:
                completion_times[current_process.pid] = current_time
                completed_processes.add(current_process.pid)
                
                self._add_simulation_step(
                    step_number=len(self.simulation_steps),
                    timestamp=current_time,
                    action=f"Process P{current_process.pid} completes execution",
                    process_id=current_process.pid,
                    state_before={"current_time": current_time - 1, "running_process": current_process.pid},
                    state_after={"current_time": current_time, "running_process": None}
                )
                
                current_process = None
        
        self.metrics = self._calculate_detailed_metrics(processes, completion_times, response_times)
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps,
            metrics=self.metrics,
            visualization_data={"gantt_chart": self.gantt_chart_data},
            input_parameters={"processes": len(processes), "preemptive": self.preemptive}
        )


class RoundRobinScheduler(SchedulingBase):
    """Round Robin scheduling algorithm with configurable time quantum."""
    
    def __init__(self, time_quantum: int = 2):
        super().__init__()
        self.time_quantum = time_quantum
        self.algorithm_name = f"Round Robin (q={time_quantum})"
    
    def execute(self, processes: List[Process]) -> SimulationResult:
        """Execute Round Robin scheduling algorithm."""
        self.reset()
        
        if not processes:
            return self._create_empty_result()
        
        current_time = 0
        completed_processes = set()
        completion_times = {}
        response_times = {}
        ready_queue = deque()
        current_process = None
        quantum_remaining = 0
        
        # Create working copies of processes
        process_copies = {p.pid: deepcopy(p) for p in processes}
        
        # Track when each process first gets CPU
        first_execution = set()
        
        while len(completed_processes) < len(processes):
            # Add newly arrived processes to ready queue
            for process in processes:
                if (process.arrival_time <= current_time and 
                    process.pid not in completed_processes and 
                    process.pid not in [p.pid for p in ready_queue] and
                    (current_process is None or process.pid != current_process.pid)):
                    ready_queue.append(process_copies[process.pid])
            
            # Select next process if no current process or quantum expired
            if current_process is None or quantum_remaining == 0:
                if current_process and current_process.remaining_time > 0:
                    # Current process quantum expired, add back to queue
                    ready_queue.append(current_process)
                
                if not ready_queue:
                    # No processes ready, advance time to next arrival
                    if current_process is None:
                        next_arrival = min(p.arrival_time for p in processes 
                                         if p.pid not in completed_processes and p.arrival_time > current_time)
                        current_time = next_arrival
                        continue
                
                if ready_queue:
                    current_process = ready_queue.popleft()
                    quantum_remaining = self.time_quantum
                    
                    # Record response time on first execution
                    if current_process.pid not in first_execution:
                        response_times[current_process.pid] = current_time - current_process.arrival_time
                        first_execution.add(current_process.pid)
            
            if current_process:
                # Execute for 1 time unit
                execution_start = current_time
                current_time += 1
                current_process.remaining_time -= 1
                quantum_remaining -= 1
                
                # Add to Gantt chart (merge consecutive executions of same process)
                if (self.gantt_chart_data and 
                    self.gantt_chart_data[-1]["process_id"] == current_process.pid and
                    self.gantt_chart_data[-1]["end_time"] == execution_start):
                    self.gantt_chart_data[-1]["end_time"] = current_time
                    self.gantt_chart_data[-1]["duration"] += 1
                else:
                    self.gantt_chart_data.append({
                        "process_id": current_process.pid,
                        "start_time": execution_start,
                        "end_time": current_time,
                        "duration": 1
                    })
                
                # Check if process completed
                if current_process.remaining_time == 0:
                    completion_times[current_process.pid] = current_time
                    completed_processes.add(current_process.pid)
                    
                    self._add_simulation_step(
                        step_number=len(self.simulation_steps),
                        timestamp=current_time,
                        action=f"Process P{current_process.pid} completes execution",
                        process_id=current_process.pid,
                        state_before={"current_time": current_time - 1, "running_process": current_process.pid},
                        state_after={"current_time": current_time, "running_process": None}
                    )
                    
                    current_process = None
                    quantum_remaining = 0
        
        self.metrics = self._calculate_detailed_metrics(processes, completion_times, response_times)
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps,
            metrics=self.metrics,
            visualization_data={"gantt_chart": self.gantt_chart_data},
            input_parameters={"processes": len(processes), "time_quantum": self.time_quantum}
        )


class PriorityScheduler(SchedulingBase):
    """Priority scheduling algorithm (both preemptive and non-preemptive)."""
    
    def __init__(self, preemptive: bool = False):
        super().__init__()
        self.preemptive = preemptive
        self.algorithm_name = f"Priority ({'Preemptive' if preemptive else 'Non-preemptive'})"
    
    def execute(self, processes: List[Process]) -> SimulationResult:
        """Execute Priority scheduling algorithm."""
        self.reset()
        
        if not processes:
            return self._create_empty_result()
        
        if self.preemptive:
            return self._execute_preemptive_priority(processes)
        else:
            return self._execute_non_preemptive_priority(processes)
    
    def _execute_non_preemptive_priority(self, processes: List[Process]) -> SimulationResult:
        """Execute non-preemptive priority scheduling."""
        current_time = 0
        completed_processes = set()
        completion_times = {}
        response_times = {}
        ready_queue = []
        
        # Create working copies of processes
        process_copies = [deepcopy(p) for p in processes]
        
        while len(completed_processes) < len(processes):
            # Add newly arrived processes to ready queue
            for process in process_copies:
                if (process.arrival_time <= current_time and 
                    process.pid not in completed_processes and 
                    process.pid not in [p.pid for p in ready_queue]):
                    ready_queue.append(process)
            
            if not ready_queue:
                # No processes ready, advance time to next arrival
                next_arrival = min(p.arrival_time for p in process_copies 
                                 if p.pid not in completed_processes)
                current_time = next_arrival
                continue
            
            # Select process with highest priority (lower number = higher priority)
            selected_process = min(ready_queue, key=lambda p: (p.priority, p.arrival_time, p.pid))
            ready_queue.remove(selected_process)
            
            # Record response time
            response_times[selected_process.pid] = current_time - selected_process.arrival_time
            
            # Execute process
            self._add_simulation_step(
                step_number=len(self.simulation_steps),
                timestamp=current_time,
                action=f"Process P{selected_process.pid} starts execution (priority: {selected_process.priority})",
                process_id=selected_process.pid,
                state_before={"current_time": current_time, "ready_queue": [p.pid for p in ready_queue]},
                state_after={"current_time": current_time, "running_process": selected_process.pid}
            )
            
            self.gantt_chart_data.append({
                "process_id": selected_process.pid,
                "start_time": current_time,
                "end_time": current_time + selected_process.burst_time,
                "duration": selected_process.burst_time,
                "priority": selected_process.priority
            })
            
            current_time += selected_process.burst_time
            completion_times[selected_process.pid] = current_time
            completed_processes.add(selected_process.pid)
            
            self._add_simulation_step(
                step_number=len(self.simulation_steps),
                timestamp=current_time,
                action=f"Process P{selected_process.pid} completes execution",
                process_id=selected_process.pid,
                state_before={"current_time": current_time - selected_process.burst_time, "running_process": selected_process.pid},
                state_after={"current_time": current_time, "running_process": None}
            )
        
        self.metrics = self._calculate_detailed_metrics(processes, completion_times, response_times)
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps,
            metrics=self.metrics,
            visualization_data={"gantt_chart": self.gantt_chart_data},
            input_parameters={"processes": len(processes), "preemptive": self.preemptive}
        )
    
    def _execute_preemptive_priority(self, processes: List[Process]) -> SimulationResult:
        """Execute preemptive priority scheduling."""
        current_time = 0
        completed_processes = set()
        completion_times = {}
        response_times = {}
        ready_queue = []
        current_process = None
        
        # Create working copies of processes
        process_copies = {p.pid: deepcopy(p) for p in processes}
        
        # Track when each process first gets CPU
        first_execution = set()
        
        while len(completed_processes) < len(processes):
            # Add newly arrived processes to ready queue
            for process in processes:
                if (process.arrival_time <= current_time and 
                    process.pid not in completed_processes and 
                    process.pid not in [p.pid for p in ready_queue] and
                    (current_process is None or process.pid != current_process.pid)):
                    ready_queue.append(process_copies[process.pid])
            
            # Check if current process should be preempted
            if current_process and ready_queue:
                highest_priority = min(ready_queue, key=lambda p: (p.priority, p.arrival_time, p.pid))
                if highest_priority.priority < current_process.priority:
                    # Preempt current process
                    ready_queue.append(current_process)
                    current_process = None
            
            # Select next process if no current process
            if current_process is None:
                if not ready_queue:
                    # No processes ready, advance time to next arrival
                    next_arrival = min(p.arrival_time for p in processes 
                                     if p.pid not in completed_processes and p.arrival_time > current_time)
                    current_time = next_arrival
                    continue
                
                current_process = min(ready_queue, key=lambda p: (p.priority, p.arrival_time, p.pid))
                ready_queue.remove(current_process)
                
                # Record response time on first execution
                if current_process.pid not in first_execution:
                    response_times[current_process.pid] = current_time - current_process.arrival_time
                    first_execution.add(current_process.pid)
            
            # Execute for 1 time unit
            execution_start = current_time
            current_time += 1
            current_process.remaining_time -= 1
            
            # Add to Gantt chart (merge consecutive executions of same process)
            if (self.gantt_chart_data and 
                self.gantt_chart_data[-1]["process_id"] == current_process.pid and
                self.gantt_chart_data[-1]["end_time"] == execution_start):
                self.gantt_chart_data[-1]["end_time"] = current_time
                self.gantt_chart_data[-1]["duration"] += 1
            else:
                self.gantt_chart_data.append({
                    "process_id": current_process.pid,
                    "start_time": execution_start,
                    "end_time": current_time,
                    "duration": 1,
                    "priority": current_process.priority
                })
            
            # Check if process completed
            if current_process.remaining_time == 0:
                completion_times[current_process.pid] = current_time
                completed_processes.add(current_process.pid)
                
                self._add_simulation_step(
                    step_number=len(self.simulation_steps),
                    timestamp=current_time,
                    action=f"Process P{current_process.pid} completes execution",
                    process_id=current_process.pid,
                    state_before={"current_time": current_time - 1, "running_process": current_process.pid},
                    state_after={"current_time": current_time, "running_process": None}
                )
                
                current_process = None
        
        self.metrics = self._calculate_detailed_metrics(processes, completion_times, response_times)
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps,
            metrics=self.metrics,
            visualization_data={"gantt_chart": self.gantt_chart_data},
            input_parameters={"processes": len(processes), "preemptive": self.preemptive}
        )


class MLFQScheduler(SchedulingBase):
    """Multi-Level Feedback Queue (MLFQ) scheduling algorithm."""
    
    def __init__(self, num_queues: int = 3, time_quantums: List[int] = None, aging_threshold: int = 10):
        super().__init__()
        self.num_queues = num_queues
        self.time_quantums = time_quantums or [2, 4, 8]  # Default quantums for each level
        self.aging_threshold = aging_threshold  # Time units before aging up
        self.algorithm_name = f"MLFQ ({num_queues} levels)"
        
        # Ensure we have enough quantums for all queues
        while len(self.time_quantums) < self.num_queues:
            self.time_quantums.append(self.time_quantums[-1] * 2)
    
    def execute(self, processes: List[Process]) -> SimulationResult:
        """Execute MLFQ scheduling algorithm."""
        self.reset()
        
        if not processes:
            return self._create_empty_result()
        
        current_time = 0
        completed_processes = set()
        completion_times = {}
        response_times = {}
        
        # Initialize multiple queues (higher index = lower priority)
        queues = [deque() for _ in range(self.num_queues)]
        
        # Track process queue levels and waiting times
        process_queue_level = {}
        process_waiting_time = {}
        current_process = None
        quantum_remaining = 0
        current_queue_level = 0
        
        # Create working copies of processes
        process_copies = {p.pid: deepcopy(p) for p in processes}
        
        # Track when each process first gets CPU
        first_execution = set()
        
        while len(completed_processes) < len(processes):
            # Add newly arrived processes to highest priority queue (queue 0)
            for process in processes:
                if (process.arrival_time <= current_time and 
                    process.pid not in completed_processes and 
                    process.pid not in process_queue_level and
                    (current_process is None or process.pid != current_process.pid)):
                    queues[0].append(process_copies[process.pid])
                    process_queue_level[process.pid] = 0
                    process_waiting_time[process.pid] = 0
            
            # Age processes (move up in priority if waiting too long)
            for pid in list(process_waiting_time.keys()):
                if pid not in completed_processes and (current_process is None or pid != current_process.pid):
                    process_waiting_time[pid] += 1
                    if process_waiting_time[pid] >= self.aging_threshold:
                        current_level = process_queue_level[pid]
                        if current_level > 0:  # Can move to higher priority queue
                            # Find and remove process from current queue
                            for i, p in enumerate(queues[current_level]):
                                if p.pid == pid:
                                    process = queues[current_level][i]
                                    del queues[current_level][i]
                                    # Move to higher priority queue
                                    new_level = current_level - 1
                                    queues[new_level].append(process)
                                    process_queue_level[pid] = new_level
                                    process_waiting_time[pid] = 0
                                    break
            
            # Select next process if no current process or quantum expired
            if current_process is None or quantum_remaining == 0:
                if current_process and current_process.remaining_time > 0:
                    # Current process quantum expired, demote to lower priority queue
                    new_level = min(current_queue_level + 1, self.num_queues - 1)
                    queues[new_level].append(current_process)
                    process_queue_level[current_process.pid] = new_level
                    process_waiting_time[current_process.pid] = 0
                
                # Find highest priority non-empty queue
                current_process = None
                for level in range(self.num_queues):
                    if queues[level]:
                        current_process = queues[level].popleft()
                        current_queue_level = level
                        quantum_remaining = self.time_quantums[level]
                        
                        # Record response time on first execution
                        if current_process.pid not in first_execution:
                            response_times[current_process.pid] = current_time - current_process.arrival_time
                            first_execution.add(current_process.pid)
                        break
                
                if current_process is None:
                    # No processes ready, advance time to next arrival
                    next_arrival = min(p.arrival_time for p in processes 
                                     if p.pid not in completed_processes and p.arrival_time > current_time)
                    current_time = next_arrival
                    continue
            
            # Execute for 1 time unit
            execution_start = current_time
            current_time += 1
            current_process.remaining_time -= 1
            quantum_remaining -= 1
            
            # Add to Gantt chart (merge consecutive executions of same process)
            if (self.gantt_chart_data and 
                self.gantt_chart_data[-1]["process_id"] == current_process.pid and
                self.gantt_chart_data[-1]["end_time"] == execution_start):
                self.gantt_chart_data[-1]["end_time"] = current_time
                self.gantt_chart_data[-1]["duration"] += 1
            else:
                self.gantt_chart_data.append({
                    "process_id": current_process.pid,
                    "start_time": execution_start,
                    "end_time": current_time,
                    "duration": 1,
                    "queue_level": current_queue_level,
                    "quantum": self.time_quantums[current_queue_level]
                })
            
            # Check if process completed
            if current_process.remaining_time == 0:
                completion_times[current_process.pid] = current_time
                completed_processes.add(current_process.pid)
                
                self._add_simulation_step(
                    step_number=len(self.simulation_steps),
                    timestamp=current_time,
                    action=f"Process P{current_process.pid} completes execution (from queue {current_queue_level})",
                    process_id=current_process.pid,
                    state_before={"current_time": current_time - 1, "running_process": current_process.pid},
                    state_after={"current_time": current_time, "running_process": None}
                )
                
                current_process = None
                quantum_remaining = 0
        
        self.metrics = self._calculate_detailed_metrics(processes, completion_times, response_times)
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps,
            metrics=self.metrics,
            visualization_data={"gantt_chart": self.gantt_chart_data},
            input_parameters={
                "processes": len(processes), 
                "num_queues": self.num_queues,
                "time_quantums": self.time_quantums,
                "aging_threshold": self.aging_threshold
            }
        )


class EDFScheduler(SchedulingBase):
    """Earliest Deadline First (EDF) scheduling algorithm for real-time processes."""
    
    def __init__(self):
        super().__init__()
        self.algorithm_name = "EDF (Earliest Deadline First)"
    
    def execute(self, processes: List[Process]) -> SimulationResult:
        """Execute EDF scheduling algorithm."""
        self.reset()
        
        if not processes:
            return self._create_empty_result()
        
        # Validate that all processes have deadlines
        for process in processes:
            if process.deadline is None:
                raise ValueError(f"Process P{process.pid} must have a deadline for EDF scheduling")
        
        current_time = 0
        completed_processes = set()
        completion_times = {}
        response_times = {}
        ready_queue = []
        current_process = None
        missed_deadlines = set()
        
        # Create working copies of processes
        process_copies = {p.pid: deepcopy(p) for p in processes}
        
        # Track when each process first gets CPU
        first_execution = set()
        
        while len(completed_processes) < len(processes):
            # Add newly arrived processes to ready queue
            for process in processes:
                if (process.arrival_time <= current_time and 
                    process.pid not in completed_processes and 
                    process.pid not in [p.pid for p in ready_queue] and
                    (current_process is None or process.pid != current_process.pid)):
                    ready_queue.append(process_copies[process.pid])
            
            # Check if current process should be preempted by earlier deadline
            if current_process and ready_queue:
                earliest_deadline = min(ready_queue, key=lambda p: (p.deadline, p.arrival_time, p.pid))
                if earliest_deadline.deadline < current_process.deadline:
                    # Preempt current process
                    ready_queue.append(current_process)
                    current_process = None
            
            # Select next process if no current process
            if current_process is None:
                if not ready_queue:
                    # No processes ready, advance time to next arrival
                    next_arrival = min(p.arrival_time for p in processes 
                                     if p.pid not in completed_processes and p.arrival_time > current_time)
                    current_time = next_arrival
                    continue
                
                # Select process with earliest deadline
                current_process = min(ready_queue, key=lambda p: (p.deadline, p.arrival_time, p.pid))
                ready_queue.remove(current_process)
                
                # Record response time on first execution
                if current_process.pid not in first_execution:
                    response_times[current_process.pid] = current_time - current_process.arrival_time
                    first_execution.add(current_process.pid)
            
            # Check for deadline miss before execution
            if current_time >= current_process.deadline and current_process.pid not in missed_deadlines:
                missed_deadlines.add(current_process.pid)
                self._add_simulation_step(
                    step_number=len(self.simulation_steps),
                    timestamp=current_time,
                    action=f"Process P{current_process.pid} MISSED DEADLINE ({current_process.deadline})",
                    process_id=current_process.pid,
                    state_before={"current_time": current_time, "deadline": current_process.deadline},
                    state_after={"current_time": current_time, "deadline_missed": True}
                )
            
            # Execute for 1 time unit
            execution_start = current_time
            current_time += 1
            current_process.remaining_time -= 1
            
            # Add to Gantt chart (merge consecutive executions of same process)
            if (self.gantt_chart_data and 
                self.gantt_chart_data[-1]["process_id"] == current_process.pid and
                self.gantt_chart_data[-1]["end_time"] == execution_start):
                self.gantt_chart_data[-1]["end_time"] = current_time
                self.gantt_chart_data[-1]["duration"] += 1
            else:
                self.gantt_chart_data.append({
                    "process_id": current_process.pid,
                    "start_time": execution_start,
                    "end_time": current_time,
                    "duration": 1,
                    "deadline": current_process.deadline,
                    "deadline_missed": current_process.pid in missed_deadlines
                })
            
            # Check if process completed
            if current_process.remaining_time == 0:
                completion_times[current_process.pid] = current_time
                completed_processes.add(current_process.pid)
                
                # Check if completed before deadline
                deadline_met = current_time <= current_process.deadline
                
                self._add_simulation_step(
                    step_number=len(self.simulation_steps),
                    timestamp=current_time,
                    action=f"Process P{current_process.pid} completes execution ({'ON TIME' if deadline_met else 'LATE'})",
                    process_id=current_process.pid,
                    state_before={"current_time": current_time - 1, "running_process": current_process.pid},
                    state_after={"current_time": current_time, "running_process": None, "deadline_met": deadline_met}
                )
                
                current_process = None
        
        # Calculate EDF-specific metrics
        self.metrics = self._calculate_detailed_metrics(processes, completion_times, response_times)
        self.metrics.update({
            "missed_deadlines": len(missed_deadlines),
            "deadline_miss_ratio": len(missed_deadlines) / len(processes),
            "schedulability": 1.0 - (len(missed_deadlines) / len(processes))
        })
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps,
            metrics=self.metrics,
            visualization_data={"gantt_chart": self.gantt_chart_data},
            input_parameters={"processes": len(processes), "missed_deadlines": list(missed_deadlines)}
        )
    
    def _add_simulation_step(self, step_number: int, timestamp: int, action: str, 
                           process_id: int, state_before: Dict[str, Any], 
                           state_after: Dict[str, Any]):
        """Add a simulation step to the execution trace."""
        step = SimulationStep(
            step_number=step_number,
            timestamp=timestamp,
            action=action,
            process_id=process_id,
            state_before=state_before,
            state_after=state_after
        )
        self.simulation_steps.append(step)
    
    def _create_empty_result(self) -> SimulationResult:
        """Create an empty simulation result for edge cases."""
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=[],
            metrics={},
            visualization_data={"gantt_chart": []},
            input_parameters={"processes": 0}
        )
    
    def _calculate_detailed_metrics(self, processes: List[Process], 
                                  completion_times: Dict[int, int], 
                                  response_times: Dict[int, int]) -> Dict[str, float]:
        """Calculate detailed scheduling metrics."""
        if not processes or not completion_times:
            return {}
        
        total_turnaround_time = 0
        total_waiting_time = 0
        total_response_time = 0
        
        for process in processes:
            completion_time = completion_times.get(process.pid, 0)
            turnaround_time = completion_time - process.arrival_time
            waiting_time = turnaround_time - process.burst_time
            response_time = response_times.get(process.pid, 0)
            
            total_turnaround_time += turnaround_time
            total_waiting_time += waiting_time
            total_response_time += response_time
        
        process_count = len(processes)
        max_completion_time = max(completion_times.values()) if completion_times else 0
        
        return {
            'average_turnaround_time': total_turnaround_time / process_count,
            'average_waiting_time': total_waiting_time / process_count,
            'average_response_time': total_response_time / process_count,
            'throughput': process_count / max_completion_time if max_completion_time > 0 else 0,
            'total_execution_time': max_completion_time,
            'cpu_utilization': sum(p.burst_time for p in processes) / max_completion_time if max_completion_time > 0 else 0
        }


# Add the missing methods to the base SchedulingBase class methods
# These should be added to all scheduler classes that don't have them

def _add_simulation_step_to_schedulers():
    """Add missing methods to scheduler classes."""
    
    def _add_simulation_step(self, step_number: int, timestamp: int, action: str, 
                           process_id: int, state_before: Dict[str, Any], 
                           state_after: Dict[str, Any]):
        """Add a simulation step to the execution trace."""
        step = SimulationStep(
            step_number=step_number,
            timestamp=timestamp,
            action=action,
            process_id=process_id,
            state_before=state_before,
            state_after=state_after
        )
        self.simulation_steps.append(step)
    
    def _create_empty_result(self) -> SimulationResult:
        """Create an empty simulation result for edge cases."""
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=[],
            metrics={},
            visualization_data={"gantt_chart": []},
            input_parameters={"processes": 0}
        )
    
    def _calculate_detailed_metrics(self, processes: List[Process], 
                                  completion_times: Dict[int, int], 
                                  response_times: Dict[int, int]) -> Dict[str, float]:
        """Calculate detailed scheduling metrics."""
        if not processes or not completion_times:
            return {}
        
        total_turnaround_time = 0
        total_waiting_time = 0
        total_response_time = 0
        
        for process in processes:
            completion_time = completion_times.get(process.pid, 0)
            turnaround_time = completion_time - process.arrival_time
            waiting_time = turnaround_time - process.burst_time
            response_time = response_times.get(process.pid, 0)
            
            total_turnaround_time += turnaround_time
            total_waiting_time += waiting_time
            total_response_time += response_time
        
        process_count = len(processes)
        max_completion_time = max(completion_times.values()) if completion_times else 0
        
        return {
            'average_turnaround_time': total_turnaround_time / process_count,
            'average_waiting_time': total_waiting_time / process_count,
            'average_response_time': total_response_time / process_count,
            'throughput': process_count / max_completion_time if max_completion_time > 0 else 0,
            'total_execution_time': max_completion_time,
            'cpu_utilization': sum(p.burst_time for p in processes) / max_completion_time if max_completion_time > 0 else 0
        }
    
    # Add methods to all scheduler classes
    for scheduler_class in [FCFSScheduler, SJFScheduler, RoundRobinScheduler, PriorityScheduler, MLFQScheduler]:
        scheduler_class._add_simulation_step = _add_simulation_step
        scheduler_class._create_empty_result = _create_empty_result
        scheduler_class._calculate_detailed_metrics = _calculate_detailed_metrics

# Apply the methods
_add_simulation_step_to_schedulers()