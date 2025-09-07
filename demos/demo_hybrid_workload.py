#!/usr/bin/env python3
"""
Demo script showcasing the Hybrid Simulation and Workload Generator features.
This script demonstrates how to combine CPU scheduling with page replacement
and generate realistic workloads.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.cpu_scheduling import FCFSScheduler, SJFScheduler, RoundRobinScheduler, EDFScheduler
from algorithms.page_replacement import FIFOAlgorithm, LRUAlgorithm, OptimalAlgorithm
from models.data_models import Process, IOOperation
import random
import math

def demo_hybrid_simulation():
    """Demonstrate hybrid simulation combining CPU scheduling and page replacement."""
    print("=" * 70)
    print("HYBRID SIMULATION DEMO")
    print("=" * 70)
    
    # Create processes with memory access patterns
    processes = [
        Process(pid=1, arrival_time=0, burst_time=5, priority=2, 
               memory_pages=[1, 2, 3, 4, 1, 2]),  # CPU-bound with locality
        Process(pid=2, arrival_time=1, burst_time=3, priority=1,
               memory_pages=[2, 3, 4, 5, 2, 3]),  # Short job
        Process(pid=3, arrival_time=2, burst_time=8, priority=3,
               memory_pages=[1, 3, 5, 1, 3, 5, 1, 3]),  # I/O-bound scattered
        Process(pid=4, arrival_time=3, burst_time=6, priority=2,
               memory_pages=[4, 5, 6, 4, 5, 6])   # Medium job with locality
    ]
    
    print("Test Processes with Memory Access Patterns:")
    for p in processes:
        print(f"  P{p.pid}: Arrival={p.arrival_time}, Burst={p.burst_time}, "
              f"Priority={p.priority}, Pages={p.memory_pages}")
    print()
    
    # Test different combinations
    combinations = [
        ("FCFS", "FIFO"),
        ("SJF", "LRU"),
        ("Round Robin", "Optimal")
    ]
    
    frame_count = 3
    
    for cpu_algo_name, page_algo_name in combinations:
        print(f"🔄 HYBRID TEST: {cpu_algo_name} + {page_algo_name}")
        print("-" * 50)
        
        # Create CPU scheduler
        if cpu_algo_name == "FCFS":
            cpu_scheduler = FCFSScheduler()
        elif cpu_algo_name == "SJF":
            cpu_scheduler = SJFScheduler(preemptive=False)
        elif cpu_algo_name == "Round Robin":
            cpu_scheduler = RoundRobinScheduler(time_quantum=2)
        
        # Run CPU scheduling
        cpu_result = cpu_scheduler.execute(processes)
        
        # Run page replacement for each process
        if page_algo_name == "FIFO":
            page_algorithm = FIFOAlgorithm()
        elif page_algo_name == "LRU":
            page_algorithm = LRUAlgorithm()
        elif page_algo_name == "Optimal":
            page_algorithm = OptimalAlgorithm()
        
        total_page_faults = 0
        process_faults = {}
        
        for process in processes:
            if process.memory_pages:
                page_result = page_algorithm.execute(process.memory_pages, frame_count)
                faults = page_result.metrics['page_faults']
                process_faults[process.pid] = faults
                total_page_faults += faults
        
        # Display results
        print(f"CPU Scheduling ({cpu_algo_name}):")
        print(f"  Average Turnaround Time: {cpu_result.metrics['average_turnaround_time']:.2f}")
        print(f"  Average Waiting Time: {cpu_result.metrics['average_waiting_time']:.2f}")
        print(f"  CPU Utilization: {cpu_result.metrics['cpu_utilization']:.2f}%")
        
        print(f"\nMemory Management ({page_algo_name}):")
        print(f"  Total Page Faults: {total_page_faults}")
        print(f"  Average Faults per Process: {total_page_faults / len(processes):.2f}")
        
        print(f"  Process Breakdown:")
        for pid, faults in process_faults.items():
            print(f"    P{pid}: {faults} faults")
        
        # Calculate hybrid efficiency score
        cpu_efficiency = 100 - cpu_result.metrics['average_waiting_time']
        memory_efficiency = 100 - (total_page_faults * 5)  # Penalty for faults
        hybrid_score = (cpu_efficiency + memory_efficiency) / 2
        
        print(f"\n📊 Hybrid Efficiency Score: {hybrid_score:.2f}/100")
        print(f"   (CPU: {cpu_efficiency:.1f}, Memory: {memory_efficiency:.1f})")
        print()

def demo_real_time_scheduling():
    """Demonstrate EDF (Earliest Deadline First) scheduling with deadlines."""
    print("=" * 70)
    print("REAL-TIME SCHEDULING DEMO (EDF)")
    print("=" * 70)
    
    # Create real-time processes with deadlines
    rt_processes = [
        Process(pid=1, arrival_time=0, burst_time=3, priority=1, deadline=8),
        Process(pid=2, arrival_time=1, burst_time=2, priority=2, deadline=6),
        Process(pid=3, arrival_time=2, burst_time=4, priority=1, deadline=12),
        Process(pid=4, arrival_time=3, burst_time=1, priority=3, deadline=7)
    ]
    
    print("Real-time Processes with Deadlines:")
    for p in rt_processes:
        print(f"  P{p.pid}: Arrival={p.arrival_time}, Burst={p.burst_time}, "
              f"Deadline={p.deadline}, Slack={p.deadline - p.arrival_time - p.burst_time}")
    print()
    
    # Run EDF scheduling
    edf_scheduler = EDFScheduler()
    edf_result = edf_scheduler.execute(rt_processes)
    
    print("EDF Scheduling Results:")
    print(f"  Average Turnaround Time: {edf_result.metrics['average_turnaround_time']:.2f}")
    print(f"  Average Waiting Time: {edf_result.metrics['average_waiting_time']:.2f}")
    print(f"  Throughput: {edf_result.metrics['throughput']:.2f}")
    
    # Check for missed deadlines
    gantt_data = edf_result.visualization_data.get('gantt_chart', [])
    missed_deadlines = []
    
    for entry in gantt_data:
        process = next(p for p in rt_processes if p.pid == entry['process_id'])
        if entry['end_time'] > process.deadline:
            missed_deadlines.append(process.pid)
    
    if missed_deadlines:
        print(f"  ⚠️  Missed Deadlines: Processes {missed_deadlines}")
    else:
        print(f"  ✅ All Deadlines Met!")
    
    print("\nExecution Timeline:")
    for entry in gantt_data:
        process = next(p for p in rt_processes if p.pid == entry['process_id'])
        status = "✅" if entry['end_time'] <= process.deadline else "❌"
        print(f"  P{entry['process_id']}: {entry['start_time']}-{entry['end_time']} "
              f"(deadline: {process.deadline}) {status}")
    print()

def demo_workload_generation():
    """Demonstrate intelligent workload generation."""
    print("=" * 70)
    print("WORKLOAD GENERATION DEMO")
    print("=" * 70)
    
    # Generate different types of workloads
    workload_types = [
        ("CPU-intensive Server", 0.8, 0.9),  # 80% CPU-bound, high locality
        ("Interactive Desktop", 0.3, 0.6),   # 30% CPU-bound, medium locality
        ("Database System", 0.5, 0.4)        # 50% CPU-bound, low locality (random access)
    ]
    
    for workload_name, cpu_ratio, locality in workload_types:
        print(f"🔧 GENERATING: {workload_name}")
        print("-" * 50)
        
        processes = generate_workload(
            num_processes=6,
            cpu_bound_ratio=cpu_ratio,
            locality=locality,
            include_rt=workload_name == "Interactive Desktop"
        )
        
        print(f"Generated {len(processes)} processes:")
        
        cpu_bound_count = 0
        io_bound_count = 0
        rt_count = 0
        total_memory_accesses = 0
        
        for p in processes:
            process_type = "RT" if p.deadline else ("CPU" if not p.io_operations else "I/O")
            if process_type == "CPU":
                cpu_bound_count += 1
            elif process_type == "I/O":
                io_bound_count += 1
            elif process_type == "RT":
                rt_count += 1
            
            total_memory_accesses += len(p.memory_pages)
            
            print(f"  P{p.pid}: {process_type}-bound, Burst={p.burst_time}, "
                  f"Pages={len(p.memory_pages)}, Priority={p.priority}")
        
        print(f"\nWorkload Characteristics:")
        print(f"  CPU-bound: {cpu_bound_count} ({cpu_bound_count/len(processes)*100:.1f}%)")
        print(f"  I/O-bound: {io_bound_count} ({io_bound_count/len(processes)*100:.1f}%)")
        print(f"  Real-time: {rt_count} ({rt_count/len(processes)*100:.1f}%)")
        print(f"  Avg Memory Accesses: {total_memory_accesses/len(processes):.1f}")
        print(f"  Memory Locality: {locality*100:.0f}%")
        print()

def generate_workload(num_processes=5, cpu_bound_ratio=0.5, locality=0.7, include_rt=False):
    """Generate a realistic workload with specified characteristics."""
    processes = []
    
    for i in range(num_processes):
        pid = i + 1
        
        # Determine process type
        is_cpu_bound = random.random() < cpu_bound_ratio
        is_rt = include_rt and random.random() < 0.3  # 30% chance for RT if enabled
        
        # Generate timing parameters
        arrival_time = random.randint(0, 10)
        
        if is_cpu_bound:
            burst_time = random.randint(5, 15)  # Longer bursts for CPU-bound
        else:
            burst_time = random.randint(2, 8)   # Shorter bursts for I/O-bound
        
        priority = random.randint(1, 10)
        
        # Generate deadline for real-time processes
        deadline = None
        if is_rt:
            deadline = arrival_time + burst_time + random.randint(3, 10)
        
        # Generate memory access pattern
        memory_pages = generate_memory_pattern(
            num_accesses=random.randint(8, 20),
            locality=locality,
            is_cpu_bound=is_cpu_bound
        )
        
        # Generate I/O operations for I/O-bound processes
        io_operations = []
        if not is_cpu_bound and not is_rt:
            num_io_ops = random.randint(1, 3)
            for _ in range(num_io_ops):
                io_start = random.randint(0, max(burst_time - 1, 1))
                io_duration = random.randint(1, 3)
                io_operations.append(IOOperation(
                    start_time=io_start,
                    duration=io_duration,
                    operation_type=random.choice(['disk', 'network', 'keyboard'])
                ))
        
        process = Process(
            pid=pid,
            arrival_time=arrival_time,
            burst_time=burst_time,
            priority=priority,
            memory_pages=memory_pages,
            io_operations=io_operations,
            deadline=deadline
        )
        
        processes.append(process)
    
    return processes

def generate_memory_pattern(num_accesses, locality, is_cpu_bound):
    """Generate memory access pattern with specified locality."""
    pages = []
    
    if is_cpu_bound:
        # CPU-bound processes have high locality (working set)
        working_set = list(range(1, 8))  # Small working set
        for _ in range(num_accesses):
            if random.random() < locality:
                # Access within working set
                pages.append(random.choice(working_set))
            else:
                # Random access outside working set
                pages.append(random.randint(8, 25))
    else:
        # I/O-bound processes have more scattered access
        for _ in range(num_accesses):
            if random.random() < locality * 0.8:  # Reduced locality
                # Some locality - access near previous page
                if pages:
                    last_page = pages[-1]
                    pages.append(max(1, last_page + random.randint(-3, 3)))
                else:
                    pages.append(random.randint(1, 30))
            else:
                # Random access
                pages.append(random.randint(1, 30))
    
    return pages

def demo_performance_analysis():
    """Demonstrate performance analysis of hybrid systems."""
    print("=" * 70)
    print("PERFORMANCE ANALYSIS DEMO")
    print("=" * 70)
    
    # Generate a mixed workload
    mixed_processes = generate_workload(num_processes=8, cpu_bound_ratio=0.6, locality=0.7)
    
    print("Analyzing performance of different algorithm combinations...")
    print()
    
    # Test different combinations
    test_combinations = [
        ("FCFS", "FIFO", "Simple but fair"),
        ("SJF", "LRU", "Optimized for short jobs"),
        ("Round Robin", "Optimal", "Interactive with optimal memory")
    ]
    
    results = []
    
    for cpu_name, page_name, description in test_combinations:
        # Create schedulers
        if cpu_name == "FCFS":
            cpu_scheduler = FCFSScheduler()
        elif cpu_name == "SJF":
            cpu_scheduler = SJFScheduler(preemptive=False)
        elif cpu_name == "Round Robin":
            cpu_scheduler = RoundRobinScheduler(time_quantum=3)
        
        if page_name == "FIFO":
            page_algorithm = FIFOAlgorithm()
        elif page_name == "LRU":
            page_algorithm = LRUAlgorithm()
        elif page_name == "Optimal":
            page_algorithm = OptimalAlgorithm()
        
        # Run simulations
        cpu_result = cpu_scheduler.execute(mixed_processes)
        
        total_faults = 0
        for process in mixed_processes:
            if process.memory_pages:
                page_result = page_algorithm.execute(process.memory_pages, 4)
                total_faults += page_result.metrics['page_faults']
        
        # Calculate composite score
        cpu_score = 100 - cpu_result.metrics['average_waiting_time']
        memory_score = 100 - (total_faults * 3)
        composite_score = (cpu_score + memory_score) / 2
        
        results.append({
            'combination': f"{cpu_name} + {page_name}",
            'description': description,
            'cpu_score': cpu_score,
            'memory_score': memory_score,
            'composite_score': composite_score,
            'turnaround_time': cpu_result.metrics['average_turnaround_time'],
            'page_faults': total_faults
        })
    
    # Display results
    print("Performance Comparison:")
    print("-" * 70)
    print(f"{'Combination':<20} {'CPU Score':<10} {'Mem Score':<10} {'Overall':<10} {'Description'}")
    print("-" * 70)
    
    for result in results:
        print(f"{result['combination']:<20} {result['cpu_score']:<10.1f} "
              f"{result['memory_score']:<10.1f} {result['composite_score']:<10.1f} "
              f"{result['description']}")
    
    # Find best combination
    best_result = max(results, key=lambda x: x['composite_score'])
    print(f"\n🏆 Best Overall Performance: {best_result['combination']}")
    print(f"   Score: {best_result['composite_score']:.1f}/100")
    print(f"   {best_result['description']}")

def main():
    """Run all hybrid and workload generation demos."""
    print("🔬 OS Algorithms Hybrid Simulation & Workload Generator Demo")
    print("This demo showcases advanced features combining CPU scheduling with memory management.")
    
    demo_hybrid_simulation()
    demo_real_time_scheduling()
    demo_workload_generation()
    demo_performance_analysis()
    
    print("\n" + "=" * 70)
    print("💡 Try the GUI version for interactive hybrid simulations!")
    print("   Run: python tkinter_simulator.py")
    print("   Then explore the 'Hybrid Simulation' and 'Workload Generator' tabs")
    print("=" * 70)

if __name__ == "__main__":
    main()