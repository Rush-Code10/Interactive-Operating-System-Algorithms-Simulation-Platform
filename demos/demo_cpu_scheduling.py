#!/usr/bin/env python3
"""
Demonstration script for CPU scheduling algorithms.
Shows all implemented scheduling algorithms with sample processes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.cpu_scheduling import (
    FCFSScheduler, SJFScheduler, RoundRobinScheduler, 
    PriorityScheduler, MLFQScheduler, EDFScheduler
)
from models.data_models import Process


def print_gantt_chart(gantt_data, algorithm_name):
    """Print a simple text-based Gantt chart."""
    print(f"\n{algorithm_name} Gantt Chart:")
    print("-" * 50)
    
    for entry in gantt_data:
        pid = entry["process_id"]
        start = entry["start_time"]
        end = entry["end_time"]
        duration = entry["duration"]
        
        extra_info = ""
        if "priority" in entry:
            extra_info = f" (priority: {entry['priority']})"
        elif "queue_level" in entry:
            extra_info = f" (queue: {entry['queue_level']})"
        elif "deadline" in entry:
            missed = " MISSED" if entry.get("deadline_missed", False) else ""
            extra_info = f" (deadline: {entry['deadline']}{missed})"
        
        print(f"P{pid}: {start:2d}-{end:2d} ({duration} units){extra_info}")


def print_metrics(metrics, algorithm_name):
    """Print scheduling metrics."""
    print(f"\n{algorithm_name} Metrics:")
    print("-" * 30)
    
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")


def demo_basic_scheduling():
    """Demonstrate basic scheduling algorithms."""
    print("=== CPU SCHEDULING ALGORITHMS DEMONSTRATION ===\n")
    
    # Sample processes for basic algorithms
    processes = [
        Process(pid=1, arrival_time=0, burst_time=6, priority=2),
        Process(pid=2, arrival_time=1, burst_time=8, priority=1),
        Process(pid=3, arrival_time=2, burst_time=7, priority=3),
        Process(pid=4, arrival_time=3, burst_time=3, priority=2)
    ]
    
    print("Sample Processes:")
    print("PID | Arrival | Burst | Priority")
    print("----|---------|-------|----------")
    for p in processes:
        print(f" {p.pid:2d} |    {p.arrival_time:2d}   |   {p.burst_time:2d}  |    {p.priority:2d}")
    
    # Test FCFS
    print("\n" + "="*60)
    fcfs = FCFSScheduler()
    result = fcfs.execute(processes)
    print_gantt_chart(result.visualization_data["gantt_chart"], "FCFS")
    print_metrics(result.metrics, "FCFS")
    
    # Test SJF Non-preemptive
    print("\n" + "="*60)
    sjf = SJFScheduler(preemptive=False)
    result = sjf.execute(processes)
    print_gantt_chart(result.visualization_data["gantt_chart"], "SJF Non-preemptive")
    print_metrics(result.metrics, "SJF Non-preemptive")
    
    # Test SJF Preemptive
    print("\n" + "="*60)
    srtf = SJFScheduler(preemptive=True)
    result = srtf.execute(processes)
    print_gantt_chart(result.visualization_data["gantt_chart"], "SJF Preemptive (SRTF)")
    print_metrics(result.metrics, "SJF Preemptive")
    
    # Test Round Robin
    print("\n" + "="*60)
    rr = RoundRobinScheduler(time_quantum=3)
    result = rr.execute(processes)
    print_gantt_chart(result.visualization_data["gantt_chart"], "Round Robin (q=3)")
    print_metrics(result.metrics, "Round Robin")
    
    # Test Priority Non-preemptive
    print("\n" + "="*60)
    priority = PriorityScheduler(preemptive=False)
    result = priority.execute(processes)
    print_gantt_chart(result.visualization_data["gantt_chart"], "Priority Non-preemptive")
    print_metrics(result.metrics, "Priority Non-preemptive")
    
    # Test Priority Preemptive
    print("\n" + "="*60)
    priority_pre = PriorityScheduler(preemptive=True)
    result = priority_pre.execute(processes)
    print_gantt_chart(result.visualization_data["gantt_chart"], "Priority Preemptive")
    print_metrics(result.metrics, "Priority Preemptive")


def demo_advanced_scheduling():
    """Demonstrate advanced scheduling algorithms."""
    print("\n\n=== ADVANCED SCHEDULING ALGORITHMS ===\n")
    
    # Test MLFQ
    print("="*60)
    mlfq_processes = [
        Process(pid=1, arrival_time=0, burst_time=10),
        Process(pid=2, arrival_time=2, burst_time=3),
        Process(pid=3, arrival_time=4, burst_time=6)
    ]
    
    print("MLFQ Sample Processes:")
    print("PID | Arrival | Burst")
    print("----|---------|-------")
    for p in mlfq_processes:
        print(f" {p.pid:2d} |    {p.arrival_time:2d}   |   {p.burst_time:2d}")
    
    mlfq = MLFQScheduler(num_queues=3, time_quantums=[2, 4, 8], aging_threshold=8)
    result = mlfq.execute(mlfq_processes)
    print_gantt_chart(result.visualization_data["gantt_chart"], "MLFQ (3 levels)")
    print_metrics(result.metrics, "MLFQ")
    
    # Test EDF
    print("\n" + "="*60)
    edf_processes = [
        Process(pid=1, arrival_time=0, burst_time=3, deadline=7),
        Process(pid=2, arrival_time=1, burst_time=4, deadline=6),
        Process(pid=3, arrival_time=2, burst_time=2, deadline=9),
        Process(pid=4, arrival_time=3, burst_time=1, deadline=5)
    ]
    
    print("EDF Sample Processes:")
    print("PID | Arrival | Burst | Deadline")
    print("----|---------|-------|----------")
    for p in edf_processes:
        print(f" {p.pid:2d} |    {p.arrival_time:2d}   |   {p.burst_time:2d}  |    {p.deadline:2d}")
    
    edf = EDFScheduler()
    result = edf.execute(edf_processes)
    print_gantt_chart(result.visualization_data["gantt_chart"], "EDF (Earliest Deadline First)")
    print_metrics(result.metrics, "EDF")


def demo_algorithm_comparison():
    """Compare different algorithms with the same process set."""
    print("\n\n=== ALGORITHM COMPARISON ===\n")
    
    processes = [
        Process(pid=1, arrival_time=0, burst_time=5, priority=3),
        Process(pid=2, arrival_time=1, burst_time=3, priority=1),
        Process(pid=3, arrival_time=2, burst_time=8, priority=2),
        Process(pid=4, arrival_time=3, burst_time=6, priority=1)
    ]
    
    algorithms = [
        ("FCFS", FCFSScheduler()),
        ("SJF", SJFScheduler(preemptive=False)),
        ("RR (q=2)", RoundRobinScheduler(time_quantum=2)),
        ("Priority", PriorityScheduler(preemptive=False))
    ]
    
    print("Comparison Processes:")
    print("PID | Arrival | Burst | Priority")
    print("----|---------|-------|----------")
    for p in processes:
        print(f" {p.pid:2d} |    {p.arrival_time:2d}   |   {p.burst_time:2d}  |    {p.priority:2d}")
    
    print("\nAlgorithm Performance Comparison:")
    print("Algorithm        | Avg WT | Avg TAT | Avg RT | Throughput")
    print("-----------------|--------|---------|--------|------------")
    
    for name, scheduler in algorithms:
        result = scheduler.execute(processes)
        metrics = result.metrics
        
        print(f"{name:16s} | {metrics['average_waiting_time']:6.2f} | "
              f"{metrics['average_turnaround_time']:7.2f} | "
              f"{metrics['average_response_time']:6.2f} | "
              f"{metrics['throughput']:10.4f}")


if __name__ == "__main__":
    demo_basic_scheduling()
    demo_advanced_scheduling()
    demo_algorithm_comparison()
    
    print("\n" + "="*60)
    print("All CPU scheduling algorithms implemented successfully!")
    print("- FCFS (First-Come-First-Served)")
    print("- SJF (Shortest Job First) - both preemptive and non-preemptive")
    print("- Round Robin with configurable time quantum")
    print("- Priority Scheduling - both preemptive and non-preemptive")
    print("- MLFQ (Multi-Level Feedback Queue) with aging")
    print("- EDF (Earliest Deadline First) for real-time scheduling")
    print("="*60)