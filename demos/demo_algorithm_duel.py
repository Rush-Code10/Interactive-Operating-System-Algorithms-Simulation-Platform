#!/usr/bin/env python3
"""
Demo script showcasing the Algorithm Duel feature.
This script demonstrates how to compare different algorithms programmatically.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.cpu_scheduling import FCFSScheduler, SJFScheduler, RoundRobinScheduler
from algorithms.page_replacement import FIFOAlgorithm, LRUAlgorithm, OptimalAlgorithm
from models.data_models import Process

def demo_cpu_scheduling_duel():
    """Demonstrate CPU scheduling algorithm comparison."""
    print("=" * 60)
    print("CPU SCHEDULING ALGORITHM DUEL DEMO")
    print("=" * 60)
    
    # Create test processes
    processes = [
        Process(pid=1, arrival_time=0, burst_time=5, priority=2),
        Process(pid=2, arrival_time=1, burst_time=3, priority=1),
        Process(pid=3, arrival_time=2, burst_time=8, priority=3),
        Process(pid=4, arrival_time=3, burst_time=6, priority=2)
    ]
    
    print("Test Processes:")
    for p in processes:
        print(f"  P{p.pid}: Arrival={p.arrival_time}, Burst={p.burst_time}, Priority={p.priority}")
    print()
    
    # Compare FCFS vs SJF
    print("🥊 DUEL 1: FCFS vs SJF (Non-preemptive)")
    print("-" * 40)
    
    fcfs = FCFSScheduler()
    sjf = SJFScheduler(preemptive=False)
    
    fcfs_result = fcfs.execute(processes)
    sjf_result = sjf.execute(processes)
    
    print(f"FCFS Results:")
    print(f"  Average Turnaround Time: {fcfs_result.metrics['average_turnaround_time']:.2f}")
    print(f"  Average Waiting Time: {fcfs_result.metrics['average_waiting_time']:.2f}")
    print(f"  Throughput: {fcfs_result.metrics['throughput']:.2f}")
    
    print(f"\nSJF Results:")
    print(f"  Average Turnaround Time: {sjf_result.metrics['average_turnaround_time']:.2f}")
    print(f"  Average Waiting Time: {sjf_result.metrics['average_waiting_time']:.2f}")
    print(f"  Throughput: {sjf_result.metrics['throughput']:.2f}")
    
    # Determine winner
    if sjf_result.metrics['average_waiting_time'] < fcfs_result.metrics['average_waiting_time']:
        print(f"\n🏆 Winner: SJF (Lower average waiting time)")
    else:
        print(f"\n🏆 Winner: FCFS (Lower average waiting time)")
    
    print("\n" + "=" * 60)
    
    # Compare SJF vs Round Robin
    print("🥊 DUEL 2: SJF vs Round Robin (q=2)")
    print("-" * 40)
    
    rr = RoundRobinScheduler(time_quantum=2)
    rr_result = rr.execute(processes)
    
    print(f"SJF Results:")
    print(f"  Average Response Time: {sjf_result.metrics['average_response_time']:.2f}")
    print(f"  Average Turnaround Time: {sjf_result.metrics['average_turnaround_time']:.2f}")
    
    print(f"\nRound Robin Results:")
    print(f"  Average Response Time: {rr_result.metrics['average_response_time']:.2f}")
    print(f"  Average Turnaround Time: {rr_result.metrics['average_turnaround_time']:.2f}")
    
    # Determine winner
    if rr_result.metrics['average_response_time'] < sjf_result.metrics['average_response_time']:
        print(f"\n🏆 Winner: Round Robin (Better response time)")
    else:
        print(f"\n🏆 Winner: SJF (Better response time)")

def demo_page_replacement_duel():
    """Demonstrate page replacement algorithm comparison."""
    print("\n" + "=" * 60)
    print("PAGE REPLACEMENT ALGORITHM DUEL DEMO")
    print("=" * 60)
    
    # Test page sequence
    page_sequence = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frame_count = 3
    
    print(f"Page Sequence: {page_sequence}")
    print(f"Frame Count: {frame_count}")
    print()
    
    # Compare FIFO vs LRU
    print("🥊 DUEL 1: FIFO vs LRU")
    print("-" * 40)
    
    fifo = FIFOAlgorithm()
    lru = LRUAlgorithm()
    
    fifo_result = fifo.execute(page_sequence, frame_count)
    lru_result = lru.execute(page_sequence, frame_count)
    
    print(f"FIFO Results:")
    print(f"  Page Faults: {fifo_result.metrics['page_faults']}")
    print(f"  Hit Ratio: {fifo_result.metrics['hit_ratio']:.2f}")
    print(f"  Fault Ratio: {fifo_result.metrics['fault_ratio']:.2f}")
    
    print(f"\nLRU Results:")
    print(f"  Page Faults: {lru_result.metrics['page_faults']}")
    print(f"  Hit Ratio: {lru_result.metrics['hit_ratio']:.2f}")
    print(f"  Fault Ratio: {lru_result.metrics['fault_ratio']:.2f}")
    
    # Determine winner
    if lru_result.metrics['page_faults'] < fifo_result.metrics['page_faults']:
        print(f"\n🏆 Winner: LRU (Fewer page faults)")
    elif fifo_result.metrics['page_faults'] < lru_result.metrics['page_faults']:
        print(f"\n🏆 Winner: FIFO (Fewer page faults)")
    else:
        print(f"\n🏆 Result: It's a tie!")
    
    print("\n" + "=" * 60)
    
    # Compare LRU vs Optimal
    print("🥊 DUEL 2: LRU vs Optimal")
    print("-" * 40)
    
    optimal = OptimalAlgorithm()
    optimal_result = optimal.execute(page_sequence, frame_count)
    
    print(f"LRU Results:")
    print(f"  Page Faults: {lru_result.metrics['page_faults']}")
    print(f"  Hit Ratio: {lru_result.metrics['hit_ratio']:.2f}")
    
    print(f"\nOptimal Results:")
    print(f"  Page Faults: {optimal_result.metrics['page_faults']}")
    print(f"  Hit Ratio: {optimal_result.metrics['hit_ratio']:.2f}")
    
    # Optimal should always win or tie
    if optimal_result.metrics['page_faults'] < lru_result.metrics['page_faults']:
        print(f"\n🏆 Winner: Optimal (Theoretical minimum faults)")
    elif optimal_result.metrics['page_faults'] == lru_result.metrics['page_faults']:
        print(f"\n🏆 Result: Tie! LRU achieved optimal performance")
    else:
        print(f"\n🏆 Unexpected: LRU outperformed Optimal (this shouldn't happen)")

def demo_algorithm_comparison_tips():
    """Provide tips for algorithm comparison."""
    print("\n" + "=" * 60)
    print("ALGORITHM COMPARISON TIPS")
    print("=" * 60)
    
    print("🎯 CPU Scheduling Comparison Metrics:")
    print("  • Average Turnaround Time: Lower is better")
    print("  • Average Waiting Time: Lower is better")
    print("  • Average Response Time: Lower is better (important for interactive systems)")
    print("  • Throughput: Higher is better")
    print("  • CPU Utilization: Higher is better")
    
    print("\n🎯 Page Replacement Comparison Metrics:")
    print("  • Page Faults: Lower is better")
    print("  • Hit Ratio: Higher is better")
    print("  • Fault Ratio: Lower is better")
    
    print("\n🎯 When to Use Each CPU Algorithm:")
    print("  • FCFS: Simple, fair, but can cause convoy effect")
    print("  • SJF: Minimizes average waiting time, but can cause starvation")
    print("  • Round Robin: Good response time, fair for interactive systems")
    print("  • Priority: Important tasks first, but can cause starvation")
    print("  • MLFQ: Balances response time and turnaround time")
    
    print("\n🎯 When to Use Each Page Replacement Algorithm:")
    print("  • FIFO: Simple but suffers from Belady's anomaly")
    print("  • LRU: Good performance, exploits temporal locality")
    print("  • Optimal: Theoretical minimum (requires future knowledge)")
    print("  • Clock: Approximates LRU with less overhead")
    
    print("\n🎯 Testing Tips:")
    print("  • Test with different workload patterns")
    print("  • Consider both CPU-bound and I/O-bound processes")
    print("  • Vary arrival times and burst times")
    print("  • Test with different page reference patterns")
    print("  • Try different frame counts for page replacement")

def main():
    """Run the algorithm duel demo."""
    print("🔬 OS Algorithms Duel Demo")
    print("This demo shows how different algorithms perform on the same workload.")
    
    demo_cpu_scheduling_duel()
    demo_page_replacement_duel()
    demo_algorithm_comparison_tips()
    
    print("\n" + "=" * 60)
    print("💡 Try the GUI version for interactive comparisons!")
    print("   Run: python tkinter_simulator.py")
    print("   Then go to the 'Algorithm Duel' tab")
    print("=" * 60)

if __name__ == "__main__":
    main()