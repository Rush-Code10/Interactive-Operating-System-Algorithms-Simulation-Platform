#!/usr/bin/env python3
"""
Demonstration script for page replacement algorithms.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.page_replacement import FIFOAlgorithm, LRUAlgorithm, OptimalAlgorithm, ClockAlgorithm


def demonstrate_algorithms():
    """Demonstrate all page replacement algorithms with a common example."""
    
    # Classic example from operating systems textbooks
    page_sequence = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    frame_count = 3
    
    print("Page Replacement Algorithms Demonstration")
    print("=" * 50)
    print(f"Page sequence: {page_sequence}")
    print(f"Number of frames: {frame_count}")
    print()
    
    # Test all algorithms
    algorithms = [
        FIFOAlgorithm(),
        LRUAlgorithm(), 
        OptimalAlgorithm(),
        ClockAlgorithm()
    ]
    
    results = {}
    
    for algorithm in algorithms:
        print(f"\n{algorithm.algorithm_name} Algorithm:")
        print("-" * 30)
        
        result = algorithm.execute(page_sequence, frame_count)
        results[algorithm.algorithm_name] = result
        
        # Print metrics
        metrics = result.metrics
        print(f"Total references: {metrics['total_references']}")
        print(f"Page faults: {metrics['page_faults']}")
        print(f"Page hits: {metrics['page_hits']}")
        print(f"Hit ratio: {metrics['hit_ratio']:.3f}")
        print(f"Fault ratio: {metrics['fault_ratio']:.3f}")
        
        # Show first few steps
        print("\nFirst 5 simulation steps:")
        for i, step in enumerate(result.execution_steps[:5]):
            status = "HIT" if step.is_hit else "FAULT"
            print(f"  Step {step.step_number}: Page {page_sequence[i]} -> {status}")
    
    # Comparison
    print("\n" + "=" * 50)
    print("ALGORITHM COMPARISON")
    print("=" * 50)
    
    for name, result in results.items():
        faults = result.metrics['page_faults']
        hit_ratio = result.metrics['hit_ratio']
        print(f"{name:10}: {faults:2d} faults, {hit_ratio:.3f} hit ratio")
    
    # Find best performing algorithm
    best_algorithm = min(results.items(), key=lambda x: x[1].metrics['page_faults'])
    print(f"\nBest performing: {best_algorithm[0]} with {best_algorithm[1].metrics['page_faults']} page faults")


def demonstrate_step_by_step():
    """Demonstrate step-by-step tracking with a simple example."""
    
    print("\n" + "=" * 50)
    print("STEP-BY-STEP TRACKING DEMONSTRATION")
    print("=" * 50)
    
    # Simple example for detailed tracking
    page_sequence = [1, 2, 3, 1, 4, 2]
    frame_count = 3
    
    print(f"Page sequence: {page_sequence}")
    print(f"Frames: {frame_count}")
    
    # Use LRU for detailed demonstration
    lru = LRUAlgorithm()
    result = lru.execute(page_sequence, frame_count)
    
    print(f"\nDetailed LRU execution:")
    print("-" * 40)
    
    for step in result.execution_steps:
        page_num = page_sequence[step.step_number]
        status = "HIT" if step.is_hit else "FAULT"
        
        print(f"Step {step.step_number}: Access page {page_num} -> {status}")
        
        # Show frame states after this step
        frames = step.state_after['frames']
        frame_contents = []
        for frame in frames:
            if frame['page_number'] is not None:
                frame_contents.append(f"F{frame['frame_id']}:P{frame['page_number']}")
            else:
                frame_contents.append(f"F{frame['frame_id']}:Empty")
        
        print(f"         Frames: [{', '.join(frame_contents)}]")
        print()


if __name__ == "__main__":
    demonstrate_algorithms()
    demonstrate_step_by_step()