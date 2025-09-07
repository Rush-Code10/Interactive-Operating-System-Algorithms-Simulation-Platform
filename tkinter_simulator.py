#!/usr/bin/env python3
"""
OS Algorithms Simulator - Tkinter GUI Application

A comprehensive GUI application for simulating CPU scheduling and page replacement algorithms.
Includes all major algorithms with visualization and detailed results.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
from typing import List, Dict, Any
import json

# Import algorithm classes
from algorithms.cpu_scheduling import (
    FCFSScheduler, SJFScheduler, RoundRobinScheduler, 
    PriorityScheduler, MLFQScheduler, EDFScheduler
)
from algorithms.page_replacement import (
    FIFOAlgorithm, LRUAlgorithm, OptimalAlgorithm, ClockAlgorithm
)
from models.data_models import Process, SimulationResult, IOOperation
import random
import math


class OSAlgorithmSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Algorithms Simulator")
        self.root.geometry("1200x800")
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_cpu_scheduling_tab()
        self.create_page_replacement_tab()
        self.create_algorithm_duel_tab()
        self.create_hybrid_simulation_tab()
        self.create_workload_generator_tab()
        
        # Results storage
        self.last_result = None
        self.duel_results = {}
        self.hybrid_results = {}
        self.generated_workload = None
    
    def create_cpu_scheduling_tab(self):
        """Create the CPU scheduling algorithms tab."""
        cpu_frame = ttk.Frame(self.notebook)
        self.notebook.add(cpu_frame, text="CPU Scheduling")
        
        # Left panel for input
        left_panel = ttk.Frame(cpu_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Algorithm selection
        ttk.Label(left_panel, text="Select Algorithm:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        
        self.cpu_algorithm_var = tk.StringVar(value="FCFS")
        algorithms = [
            ("FCFS", "FCFS"),
            ("SJF (Non-preemptive)", "SJF_NP"),
            ("SJF (Preemptive)", "SJF_P"),
            ("Round Robin", "RR"),
            ("Priority (Non-preemptive)", "PRIORITY_NP"),
            ("Priority (Preemptive)", "PRIORITY_P"),
            ("Multi-Level Feedback Queue", "MLFQ"),
            ("EDF (Earliest Deadline First)", "EDF")
        ]
        
        for text, value in algorithms:
            ttk.Radiobutton(left_panel, text=text, variable=self.cpu_algorithm_var, 
                           value=value, command=self.on_cpu_algorithm_change).pack(anchor=tk.W)
        
        # Algorithm parameters
        params_frame = ttk.LabelFrame(left_panel, text="Algorithm Parameters")
        params_frame.pack(fill=tk.X, pady=10)
        
        # Time quantum for Round Robin
        ttk.Label(params_frame, text="Time Quantum (for RR):").pack(anchor=tk.W)
        self.time_quantum_var = tk.StringVar(value="2")
        ttk.Entry(params_frame, textvariable=self.time_quantum_var, width=10).pack(anchor=tk.W, pady=2)
        
        # Process input
        process_frame = ttk.LabelFrame(left_panel, text="Process Input")
        process_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(process_frame, text="Format: PID,Arrival,Burst,Priority[,Deadline]").pack(anchor=tk.W)
        ttk.Label(process_frame, text="Example: 1,0,5,2,10 (deadline optional for EDF)").pack(anchor=tk.W)
        
        self.cpu_process_text = scrolledtext.ScrolledText(process_frame, height=8, width=30)
        self.cpu_process_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Default processes
        default_processes = """1,0,5,2
2,1,3,1
3,2,8,3
4,3,6,2"""
        self.cpu_process_text.insert(tk.END, default_processes)
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Run Simulation", 
                  command=self.run_cpu_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", 
                  command=lambda: self.cpu_process_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=2)
        
        # Right panel for results
        right_panel = ttk.Frame(cpu_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Results notebook
        self.cpu_results_notebook = ttk.Notebook(right_panel)
        self.cpu_results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Gantt chart tab
        self.cpu_gantt_frame = ttk.Frame(self.cpu_results_notebook)
        self.cpu_results_notebook.add(self.cpu_gantt_frame, text="Gantt Chart")
        
        # Metrics tab
        self.cpu_metrics_frame = ttk.Frame(self.cpu_results_notebook)
        self.cpu_results_notebook.add(self.cpu_metrics_frame, text="Metrics")
        
        self.cpu_metrics_text = scrolledtext.ScrolledText(self.cpu_metrics_frame)
        self.cpu_metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Steps tab
        self.cpu_steps_frame = ttk.Frame(self.cpu_results_notebook)
        self.cpu_results_notebook.add(self.cpu_steps_frame, text="Execution Steps")
        
        self.cpu_steps_text = scrolledtext.ScrolledText(self.cpu_steps_frame)
        self.cpu_steps_text.pack(fill=tk.BOTH, expand=True)
    
    def create_page_replacement_tab(self):
        """Create the page replacement algorithms tab."""
        page_frame = ttk.Frame(self.notebook)
        self.notebook.add(page_frame, text="Page Replacement")
        
        # Left panel for input
        left_panel = ttk.Frame(page_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Algorithm selection
        ttk.Label(left_panel, text="Select Algorithm:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        
        self.page_algorithm_var = tk.StringVar(value="FIFO")
        algorithms = [
            ("FIFO", "FIFO"),
            ("LRU", "LRU"),
            ("Optimal", "OPTIMAL"),
            ("Clock", "CLOCK")
        ]
        
        for text, value in algorithms:
            ttk.Radiobutton(left_panel, text=text, variable=self.page_algorithm_var, 
                           value=value).pack(anchor=tk.W)
        
        # Parameters
        params_frame = ttk.LabelFrame(left_panel, text="Parameters")
        params_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(params_frame, text="Number of Frames:").pack(anchor=tk.W)
        self.frame_count_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.frame_count_var, width=10).pack(anchor=tk.W, pady=2)
        
        # Page sequence input
        sequence_frame = ttk.LabelFrame(left_panel, text="Page Reference Sequence")
        sequence_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(sequence_frame, text="Enter page numbers separated by commas:").pack(anchor=tk.W)
        ttk.Label(sequence_frame, text="Example: 1,2,3,4,1,2,5,1,2,3,4,5").pack(anchor=tk.W)
        
        self.page_sequence_text = scrolledtext.ScrolledText(sequence_frame, height=6, width=30)
        self.page_sequence_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Default sequence
        default_sequence = "1,2,3,4,1,2,5,1,2,3,4,5"
        self.page_sequence_text.insert(tk.END, default_sequence)
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Run Simulation", 
                  command=self.run_page_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", 
                  command=lambda: self.page_sequence_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=2)
        
        # Right panel for results
        right_panel = ttk.Frame(page_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Results notebook
        self.page_results_notebook = ttk.Notebook(right_panel)
        self.page_results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Visualization tab
        self.page_viz_frame = ttk.Frame(self.page_results_notebook)
        self.page_results_notebook.add(self.page_viz_frame, text="Frame States")
        
        # Metrics tab
        self.page_metrics_frame = ttk.Frame(self.page_results_notebook)
        self.page_results_notebook.add(self.page_metrics_frame, text="Metrics")
        
        self.page_metrics_text = scrolledtext.ScrolledText(self.page_metrics_frame)
        self.page_metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Steps tab
        self.page_steps_frame = ttk.Frame(self.page_results_notebook)
        self.page_results_notebook.add(self.page_steps_frame, text="Execution Steps")
        
        self.page_steps_text = scrolledtext.ScrolledText(self.page_steps_frame)
        self.page_steps_text.pack(fill=tk.BOTH, expand=True)
    
    def on_cpu_algorithm_change(self):
        """Handle CPU algorithm selection change."""
        pass  # Could be used to show/hide relevant parameters
    
    def parse_processes(self, text: str) -> List[Process]:
        """Parse process input text into Process objects."""
        processes = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = [int(x.strip()) for x in line.split(',')]
                if len(parts) >= 3:
                    pid, arrival, burst = parts[:3]
                    priority = parts[3] if len(parts) > 3 else 0
                    deadline = parts[4] if len(parts) > 4 else None
                    processes.append(Process(pid=pid, arrival_time=arrival, 
                                           burst_time=burst, priority=priority, deadline=deadline))
            except ValueError as e:
                messagebox.showerror("Input Error", f"Invalid process format in line: {line}")
                return []
        
        return processes
    
    def run_cpu_simulation(self):
        """Run the selected CPU scheduling algorithm."""
        try:
            # Parse processes
            process_text = self.cpu_process_text.get(1.0, tk.END)
            processes = self.parse_processes(process_text)
            
            if not processes:
                messagebox.showerror("Error", "No valid processes found!")
                return
            
            # Get algorithm
            algorithm_type = self.cpu_algorithm_var.get()
            
            if algorithm_type == "FCFS":
                scheduler = FCFSScheduler()
            elif algorithm_type == "SJF_NP":
                scheduler = SJFScheduler(preemptive=False)
            elif algorithm_type == "SJF_P":
                scheduler = SJFScheduler(preemptive=True)
            elif algorithm_type == "RR":
                try:
                    quantum = int(self.time_quantum_var.get())
                    scheduler = RoundRobinScheduler(time_quantum=quantum)
                except ValueError:
                    messagebox.showerror("Error", "Invalid time quantum!")
                    return
            elif algorithm_type == "PRIORITY_NP":
                scheduler = PriorityScheduler(preemptive=False)
            elif algorithm_type == "PRIORITY_P":
                scheduler = PriorityScheduler(preemptive=True)
            elif algorithm_type == "MLFQ":
                scheduler = MLFQScheduler()
            elif algorithm_type == "EDF":
                scheduler = EDFScheduler()
            
            # Run simulation
            result = scheduler.execute(processes)
            self.display_cpu_results(result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def display_cpu_results(self, result: SimulationResult):
        """Display CPU scheduling results."""
        # Clear previous results
        for widget in self.cpu_gantt_frame.winfo_children():
            widget.destroy()
        
        # Display Gantt chart
        self.create_gantt_chart(result, self.cpu_gantt_frame)
        
        # Display metrics
        self.cpu_metrics_text.delete(1.0, tk.END)
        metrics_text = f"Algorithm: {result.algorithm_name}\n\n"
        metrics_text += "Performance Metrics:\n"
        metrics_text += "=" * 30 + "\n"
        
        for key, value in result.metrics.items():
            if isinstance(value, float):
                metrics_text += f"{key}: {value:.2f}\n"
            else:
                metrics_text += f"{key}: {value}\n"
        
        self.cpu_metrics_text.insert(tk.END, metrics_text)
        
        # Display execution steps
        self.cpu_steps_text.delete(1.0, tk.END)
        steps_text = f"Execution Steps for {result.algorithm_name}\n"
        steps_text += "=" * 50 + "\n\n"
        
        for step in result.execution_steps:
            steps_text += f"Step {step.step_number} (Time {step.timestamp}): {step.action}\n"
        
        self.cpu_steps_text.insert(tk.END, steps_text)
    
    def create_gantt_chart(self, result: SimulationResult, parent_frame):
        """Create and display Gantt chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        gantt_data = result.visualization_data.get('gantt_chart', [])
        
        if not gantt_data:
            ax.text(0.5, 0.5, 'No Gantt chart data available', 
                   horizontalalignment='center', verticalalignment='center')
        else:
            # Create Gantt chart
            colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF', '#FFB366']
            process_colors = {}
            
            for i, entry in enumerate(gantt_data):
                pid = entry['process_id']
                if pid not in process_colors:
                    process_colors[pid] = colors[len(process_colors) % len(colors)]
                
                ax.barh(0, entry['duration'], left=entry['start_time'], 
                       color=process_colors[pid], alpha=0.7, edgecolor='black')
                
                # Add process label
                ax.text(entry['start_time'] + entry['duration']/2, 0, f'P{pid}', 
                       ha='center', va='center', fontweight='bold')
            
            ax.set_xlabel('Time')
            ax.set_ylabel('CPU')
            ax.set_title(f'Gantt Chart - {result.algorithm_name}')
            ax.set_ylim(-0.5, 0.5)
            ax.set_yticks([0])
            ax.set_yticklabels(['CPU'])
            ax.grid(True, alpha=0.3)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def run_page_simulation(self):
        """Run the selected page replacement algorithm."""
        try:
            # Parse page sequence
            sequence_text = self.page_sequence_text.get(1.0, tk.END).strip()
            page_sequence = [int(x.strip()) for x in sequence_text.split(',') if x.strip()]
            
            if not page_sequence:
                messagebox.showerror("Error", "No valid page sequence found!")
                return
            
            # Get frame count
            try:
                frame_count = int(self.frame_count_var.get())
                if frame_count <= 0:
                    raise ValueError("Frame count must be positive")
            except ValueError:
                messagebox.showerror("Error", "Invalid frame count!")
                return
            
            # Get algorithm
            algorithm_type = self.page_algorithm_var.get()
            
            if algorithm_type == "FIFO":
                algorithm = FIFOAlgorithm()
            elif algorithm_type == "LRU":
                algorithm = LRUAlgorithm()
            elif algorithm_type == "OPTIMAL":
                algorithm = OptimalAlgorithm()
            elif algorithm_type == "CLOCK":
                algorithm = ClockAlgorithm()
            
            # Run simulation
            result = algorithm.execute(page_sequence, frame_count)
            self.display_page_results(result, page_sequence, frame_count)
            
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def display_page_results(self, result: SimulationResult, page_sequence: List[int], frame_count: int):
        """Display page replacement results."""
        # Clear previous results
        for widget in self.page_viz_frame.winfo_children():
            widget.destroy()
        
        # Display frame states visualization
        self.create_page_visualization(result, page_sequence, frame_count, self.page_viz_frame)
        
        # Display metrics
        self.page_metrics_text.delete(1.0, tk.END)
        metrics_text = f"Algorithm: {result.algorithm_name}\n\n"
        metrics_text += "Performance Metrics:\n"
        metrics_text += "=" * 30 + "\n"
        
        for key, value in result.metrics.items():
            if isinstance(value, float):
                metrics_text += f"{key}: {value:.2f}\n"
            else:
                metrics_text += f"{key}: {value}\n"
        
        self.page_metrics_text.insert(tk.END, metrics_text)
        
        # Display execution steps
        self.page_steps_text.delete(1.0, tk.END)
        steps_text = f"Execution Steps for {result.algorithm_name}\n"
        steps_text += "=" * 50 + "\n\n"
        
        for step in result.execution_steps:
            hit_miss = "HIT" if step.is_hit else "FAULT"
            steps_text += f"Step {step.step_number}: Page {page_sequence[step.step_number]} - {hit_miss}\n"
        
        self.page_steps_text.insert(tk.END, steps_text)
    
    def create_page_visualization(self, result: SimulationResult, page_sequence: List[int], 
                                frame_count: int, parent_frame):
        """Create page replacement visualization."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create frame state table
        steps = len(page_sequence)
        
        # Create grid
        for i in range(frame_count + 1):  # +1 for header
            for j in range(steps + 1):  # +1 for frame labels
                rect = patches.Rectangle((j, frame_count - i), 1, 1, 
                                       linewidth=1, edgecolor='black', facecolor='white')
                ax.add_patch(rect)
        
        # Add headers
        for j in range(steps):
            ax.text(j + 0.5, frame_count + 0.5, str(page_sequence[j]), 
                   ha='center', va='center', fontweight='bold')
        
        # Add frame labels
        for i in range(frame_count):
            ax.text(0.5, frame_count - i - 0.5, f'F{i}', 
                   ha='center', va='center', fontweight='bold')
        
        # Fill frame states
        frame_states = result.visualization_data.get('frame_states_timeline', [])
        hit_miss_pattern = result.visualization_data.get('hit_miss_pattern', [])
        
        for step_idx, state in enumerate(frame_states):
            if step_idx >= steps:
                break
            
            frames = state.get('frames', [])
            is_hit = hit_miss_pattern[step_idx] if step_idx < len(hit_miss_pattern) else False
            
            # Color code: green for hit, red for fault
            bg_color = '#90EE90' if is_hit else '#FFB6C1'
            
            for frame_idx, frame in enumerate(frames):
                if frame_idx >= frame_count:
                    break
                
                page_num = frame.get('page_number')
                if page_num is not None:
                    rect = patches.Rectangle((step_idx + 1, frame_count - frame_idx - 1), 1, 1,
                                           linewidth=1, edgecolor='black', facecolor=bg_color)
                    ax.add_patch(rect)
                    ax.text(step_idx + 1.5, frame_count - frame_idx - 0.5, str(page_num),
                           ha='center', va='center', fontweight='bold')
        
        ax.set_xlim(0, steps + 1)
        ax.set_ylim(0, frame_count + 1)
        ax.set_aspect('equal')
        ax.set_title(f'Frame States - {result.algorithm_name}\n(Green=Hit, Pink=Fault)')
        ax.axis('off')
        
        # Add legend
        hit_patch = patches.Patch(color='#90EE90', label='Hit')
        fault_patch = patches.Patch(color='#FFB6C1', label='Fault')
        ax.legend(handles=[hit_patch, fault_patch], loc='upper right')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_algorithm_duel_tab(self):
        """Create the algorithm dueling tab for comparing algorithms."""
        duel_frame = ttk.Frame(self.notebook)
        self.notebook.add(duel_frame, text="Algorithm Duel")
        
        # Main container with paned window for better layout
        main_paned = ttk.PanedWindow(duel_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for configuration
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=1)
        
        # Right panel for results
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=2)
        
        # Duel type selection
        type_frame = ttk.LabelFrame(left_panel, text="Duel Type")
        type_frame.pack(fill=tk.X, pady=5)
        
        self.duel_type_var = tk.StringVar(value="cpu")
        ttk.Radiobutton(type_frame, text="CPU Scheduling Duel", 
                       variable=self.duel_type_var, value="cpu",
                       command=self.on_duel_type_change).pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Page Replacement Duel", 
                       variable=self.duel_type_var, value="page",
                       command=self.on_duel_type_change).pack(anchor=tk.W)
        
        # Algorithm selection frame
        algo_frame = ttk.LabelFrame(left_panel, text="Algorithm Selection")
        algo_frame.pack(fill=tk.X, pady=5)
        
        # Algorithm 1
        ttk.Label(algo_frame, text="Algorithm 1:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.algo1_var = tk.StringVar()
        self.algo1_combo = ttk.Combobox(algo_frame, textvariable=self.algo1_var, state="readonly")
        self.algo1_combo.pack(fill=tk.X, pady=2)
        
        # Algorithm 2
        ttk.Label(algo_frame, text="Algorithm 2:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        self.algo2_var = tk.StringVar()
        self.algo2_combo = ttk.Combobox(algo_frame, textvariable=self.algo2_var, state="readonly")
        self.algo2_combo.pack(fill=tk.X, pady=2)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(left_panel, text="Parameters")
        params_frame.pack(fill=tk.X, pady=5)
        
        # Time quantum for Round Robin
        ttk.Label(params_frame, text="Time Quantum (for RR):").pack(anchor=tk.W)
        self.duel_time_quantum_var = tk.StringVar(value="2")
        ttk.Entry(params_frame, textvariable=self.duel_time_quantum_var, width=10).pack(anchor=tk.W, pady=2)
        
        # Frame count for page replacement
        ttk.Label(params_frame, text="Frame Count (for Paging):").pack(anchor=tk.W)
        self.duel_frame_count_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.duel_frame_count_var, width=10).pack(anchor=tk.W, pady=2)
        
        # Input data frame
        input_frame = ttk.LabelFrame(left_panel, text="Input Data")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.duel_input_text = scrolledtext.ScrolledText(input_frame, height=10, width=30)
        self.duel_input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Default data
        default_cpu_data = """1,0,5,2
2,1,3,1
3,2,8,3
4,3,6,2"""
        self.duel_input_text.insert(tk.END, default_cpu_data)
        
        # Control buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Start Duel", 
                  command=self.start_algorithm_duel).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_duel_input).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Load Example", 
                  command=self.load_duel_example).pack(side=tk.LEFT, padx=2)
        
        # Results panel
        results_notebook = ttk.Notebook(right_panel)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Comparison tab
        self.duel_comparison_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.duel_comparison_frame, text="Comparison")
        
        # Algorithm 1 results tab
        self.duel_algo1_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.duel_algo1_frame, text="Algorithm 1")
        
        # Algorithm 2 results tab
        self.duel_algo2_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.duel_algo2_frame, text="Algorithm 2")
        
        # Initialize algorithm options
        self.on_duel_type_change()
    
    def on_duel_type_change(self):
        """Handle duel type change to update algorithm options."""
        duel_type = self.duel_type_var.get()
        
        if duel_type == "cpu":
            algorithms = [
                "FCFS", "SJF (Non-preemptive)", "SJF (Preemptive)", 
                "Round Robin", "Priority (Non-preemptive)", "Priority (Preemptive)", "MLFQ", "EDF"
            ]
            # Update input example
            self.duel_input_text.delete(1.0, tk.END)
            example_data = """1,0,5,2
2,1,3,1
3,2,8,3
4,3,6,2"""
            self.duel_input_text.insert(tk.END, example_data)
        else:  # page
            algorithms = ["FIFO", "LRU", "Optimal", "Clock"]
            # Update input example
            self.duel_input_text.delete(1.0, tk.END)
            example_data = "1,2,3,4,1,2,5,1,2,3,4,5"
            self.duel_input_text.insert(tk.END, example_data)
        
        self.algo1_combo['values'] = algorithms
        self.algo2_combo['values'] = algorithms
        
        # Set default selections
        if algorithms:
            self.algo1_var.set(algorithms[0])
            self.algo2_var.set(algorithms[1] if len(algorithms) > 1 else algorithms[0])
    
    def clear_duel_input(self):
        """Clear the duel input text."""
        self.duel_input_text.delete(1.0, tk.END)
    
    def load_duel_example(self):
        """Load example data for the current duel type."""
        self.on_duel_type_change()  # This will load the appropriate example
    
    def start_algorithm_duel(self):
        """Start the algorithm duel comparison."""
        try:
            duel_type = self.duel_type_var.get()
            algo1_name = self.algo1_var.get()
            algo2_name = self.algo2_var.get()
            
            if not algo1_name or not algo2_name:
                messagebox.showerror("Error", "Please select both algorithms!")
                return
            
            if algo1_name == algo2_name:
                messagebox.showwarning("Warning", "Selected algorithms are the same. Results will be identical.")
            
            input_data = self.duel_input_text.get(1.0, tk.END).strip()
            if not input_data:
                messagebox.showerror("Error", "Please provide input data!")
                return
            
            if duel_type == "cpu":
                self.run_cpu_duel(algo1_name, algo2_name, input_data)
            else:
                self.run_page_duel(algo1_name, algo2_name, input_data)
                
        except Exception as e:
            messagebox.showerror("Error", f"Duel failed: {str(e)}")
    
    def run_cpu_duel(self, algo1_name: str, algo2_name: str, input_data: str):
        """Run CPU scheduling algorithm duel."""
        # Parse processes
        processes = self.parse_processes(input_data)
        if not processes:
            return
        
        # Create algorithm instances
        algo1 = self.create_cpu_algorithm(algo1_name)
        algo2 = self.create_cpu_algorithm(algo2_name)
        
        if not algo1 or not algo2:
            messagebox.showerror("Error", "Failed to create algorithm instances!")
            return
        
        # Run simulations
        result1 = algo1.execute(processes)
        result2 = algo2.execute(processes)
        
        # Store results
        self.duel_results = {
            'type': 'cpu',
            'algo1': {'name': algo1_name, 'result': result1},
            'algo2': {'name': algo2_name, 'result': result2}
        }
        
        # Display results
        self.display_cpu_duel_results(result1, result2, algo1_name, algo2_name)
    
    def run_page_duel(self, algo1_name: str, algo2_name: str, input_data: str):
        """Run page replacement algorithm duel."""
        try:
            # Parse page sequence
            page_sequence = [int(x.strip()) for x in input_data.split(',') if x.strip()]
            frame_count = int(self.duel_frame_count_var.get())
            
            if not page_sequence:
                messagebox.showerror("Error", "Invalid page sequence!")
                return
            
            # Create algorithm instances
            algo1 = self.create_page_algorithm(algo1_name)
            algo2 = self.create_page_algorithm(algo2_name)
            
            if not algo1 or not algo2:
                messagebox.showerror("Error", "Failed to create algorithm instances!")
                return
            
            # Run simulations
            result1 = algo1.execute(page_sequence, frame_count)
            result2 = algo2.execute(page_sequence, frame_count)
            
            # Store results
            self.duel_results = {
                'type': 'page',
                'algo1': {'name': algo1_name, 'result': result1},
                'algo2': {'name': algo2_name, 'result': result2},
                'page_sequence': page_sequence,
                'frame_count': frame_count
            }
            
            # Display results
            self.display_page_duel_results(result1, result2, algo1_name, algo2_name, page_sequence, frame_count)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input format! Use comma-separated numbers for page sequence.")
    
    def create_cpu_algorithm(self, algo_name: str):
        """Create CPU scheduling algorithm instance."""
        algo_map = {
            "FCFS": FCFSScheduler,
            "SJF (Non-preemptive)": lambda: SJFScheduler(preemptive=False),
            "SJF (Preemptive)": lambda: SJFScheduler(preemptive=True),
            "Round Robin": lambda: RoundRobinScheduler(time_quantum=int(self.duel_time_quantum_var.get())),
            "Priority (Non-preemptive)": lambda: PriorityScheduler(preemptive=False),
            "Priority (Preemptive)": lambda: PriorityScheduler(preemptive=True),
            "MLFQ": MLFQScheduler,
            "EDF": EDFScheduler
        }
        
        if algo_name in algo_map:
            return algo_map[algo_name]()
        return None
    
    def create_page_algorithm(self, algo_name: str):
        """Create page replacement algorithm instance."""
        algo_map = {
            "FIFO": FIFOAlgorithm,
            "LRU": LRUAlgorithm,
            "Optimal": OptimalAlgorithm,
            "Clock": ClockAlgorithm
        }
        
        if algo_name in algo_map:
            return algo_map[algo_name]()
        return None
    
    def display_cpu_duel_results(self, result1: SimulationResult, result2: SimulationResult, 
                                algo1_name: str, algo2_name: str):
        """Display CPU scheduling duel results."""
        # Clear previous results
        for widget in self.duel_comparison_frame.winfo_children():
            widget.destroy()
        for widget in self.duel_algo1_frame.winfo_children():
            widget.destroy()
        for widget in self.duel_algo2_frame.winfo_children():
            widget.destroy()
        
        # Create comparison view
        self.create_cpu_comparison_view(result1, result2, algo1_name, algo2_name)
        
        # Create individual algorithm views
        self.create_gantt_chart(result1, self.duel_algo1_frame)
        self.create_gantt_chart(result2, self.duel_algo2_frame)
        
        # Add metrics to individual tabs
        self.add_metrics_to_frame(result1, self.duel_algo1_frame, algo1_name)
        self.add_metrics_to_frame(result2, self.duel_algo2_frame, algo2_name)
    
    def display_page_duel_results(self, result1: SimulationResult, result2: SimulationResult,
                                 algo1_name: str, algo2_name: str, page_sequence: List[int], frame_count: int):
        """Display page replacement duel results."""
        # Clear previous results
        for widget in self.duel_comparison_frame.winfo_children():
            widget.destroy()
        for widget in self.duel_algo1_frame.winfo_children():
            widget.destroy()
        for widget in self.duel_algo2_frame.winfo_children():
            widget.destroy()
        
        # Create comparison view
        self.create_page_comparison_view(result1, result2, algo1_name, algo2_name)
        
        # Create individual algorithm views
        self.create_page_visualization(result1, page_sequence, frame_count, self.duel_algo1_frame)
        self.create_page_visualization(result2, page_sequence, frame_count, self.duel_algo2_frame)
        
        # Add metrics to individual tabs
        self.add_metrics_to_frame(result1, self.duel_algo1_frame, algo1_name)
        self.add_metrics_to_frame(result2, self.duel_algo2_frame, algo2_name)
    
    def create_cpu_comparison_view(self, result1: SimulationResult, result2: SimulationResult,
                                  algo1_name: str, algo2_name: str):
        """Create CPU scheduling comparison view."""
        # Main comparison frame
        main_frame = ttk.Frame(self.duel_comparison_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Algorithm Duel: {algo1_name} vs {algo2_name}", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Metrics comparison table
        metrics_frame = ttk.LabelFrame(main_frame, text="Performance Comparison")
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for comparison
        columns = ('Metric', algo1_name, algo2_name, 'Winner')
        tree = ttk.Treeview(metrics_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')
        
        # Compare metrics
        metrics_to_compare = [
            ('Average Turnaround Time', 'average_turnaround_time', 'lower'),
            ('Average Waiting Time', 'average_waiting_time', 'lower'),
            ('Average Response Time', 'average_response_time', 'lower'),
            ('Throughput', 'throughput', 'higher'),
            ('CPU Utilization', 'cpu_utilization', 'higher'),
            ('Total Execution Time', 'total_execution_time', 'lower')
        ]
        
        for display_name, metric_key, better in metrics_to_compare:
            val1 = result1.metrics.get(metric_key, 0)
            val2 = result2.metrics.get(metric_key, 0)
            
            if better == 'lower':
                winner = algo1_name if val1 < val2 else algo2_name if val2 < val1 else "Tie"
            else:
                winner = algo1_name if val1 > val2 else algo2_name if val2 > val1 else "Tie"
            
            tree.insert('', 'end', values=(
                display_name,
                f"{val1:.2f}" if isinstance(val1, float) else str(val1),
                f"{val2:.2f}" if isinstance(val2, float) else str(val2),
                winner
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Overall winner
        winner_frame = ttk.Frame(main_frame)
        winner_frame.pack(fill=tk.X, pady=10)
        
        # Simple scoring system
        score1 = sum(1 for _, metric_key, better in metrics_to_compare
                    if ((better == 'lower' and result1.metrics.get(metric_key, 0) < result2.metrics.get(metric_key, 0)) or
                        (better == 'higher' and result1.metrics.get(metric_key, 0) > result2.metrics.get(metric_key, 0))))
        
        score2 = len(metrics_to_compare) - score1
        
        if score1 > score2:
            overall_winner = algo1_name
            winner_color = "green"
        elif score2 > score1:
            overall_winner = algo2_name
            winner_color = "green"
        else:
            overall_winner = "It's a tie!"
            winner_color = "orange"
        
        winner_label = ttk.Label(winner_frame, text=f"🏆 Overall Winner: {overall_winner}", 
                                font=('Arial', 12, 'bold'))
        winner_label.pack()
    
    def create_page_comparison_view(self, result1: SimulationResult, result2: SimulationResult,
                                   algo1_name: str, algo2_name: str):
        """Create page replacement comparison view."""
        # Main comparison frame
        main_frame = ttk.Frame(self.duel_comparison_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Algorithm Duel: {algo1_name} vs {algo2_name}", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Metrics comparison table
        metrics_frame = ttk.LabelFrame(main_frame, text="Performance Comparison")
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for comparison
        columns = ('Metric', algo1_name, algo2_name, 'Winner')
        tree = ttk.Treeview(metrics_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')
        
        # Compare metrics
        metrics_to_compare = [
            ('Total References', 'total_references', 'neutral'),
            ('Page Faults', 'page_faults', 'lower'),
            ('Page Hits', 'page_hits', 'higher'),
            ('Hit Ratio', 'hit_ratio', 'higher'),
            ('Fault Ratio', 'fault_ratio', 'lower')
        ]
        
        for display_name, metric_key, better in metrics_to_compare:
            val1 = result1.metrics.get(metric_key, 0)
            val2 = result2.metrics.get(metric_key, 0)
            
            if better == 'lower':
                winner = algo1_name if val1 < val2 else algo2_name if val2 < val1 else "Tie"
            elif better == 'higher':
                winner = algo1_name if val1 > val2 else algo2_name if val2 > val1 else "Tie"
            else:
                winner = "N/A"
            
            tree.insert('', 'end', values=(
                display_name,
                f"{val1:.2f}" if isinstance(val1, float) else str(val1),
                f"{val2:.2f}" if isinstance(val2, float) else str(val2),
                winner
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Overall winner based on page faults (primary metric)
        winner_frame = ttk.Frame(main_frame)
        winner_frame.pack(fill=tk.X, pady=10)
        
        faults1 = result1.metrics.get('page_faults', 0)
        faults2 = result2.metrics.get('page_faults', 0)
        
        if faults1 < faults2:
            overall_winner = f"{algo1_name} (Fewer page faults: {faults1} vs {faults2})"
        elif faults2 < faults1:
            overall_winner = f"{algo2_name} (Fewer page faults: {faults2} vs {faults1})"
        else:
            overall_winner = f"It's a tie! (Both had {faults1} page faults)"
        
        winner_label = ttk.Label(winner_frame, text=f"🏆 Winner: {overall_winner}", 
                                font=('Arial', 12, 'bold'))
        winner_label.pack()
    
    def add_metrics_to_frame(self, result: SimulationResult, frame: ttk.Frame, algo_name: str):
        """Add metrics display to a frame."""
        # Create a text widget for metrics at the bottom
        metrics_text = tk.Text(frame, height=8, wrap=tk.WORD)
        metrics_text.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        # Add metrics
        metrics_content = f"{algo_name} - Performance Metrics:\n"
        metrics_content += "=" * 40 + "\n"
        
        for key, value in result.metrics.items():
            if isinstance(value, float):
                metrics_content += f"{key}: {value:.2f}\n"
            else:
                metrics_content += f"{key}: {value}\n"
        
        metrics_text.insert(tk.END, metrics_content)
        metrics_text.config(state=tk.DISABLED)
    
    def create_hybrid_simulation_tab(self):
        """Create the hybrid simulation tab combining CPU scheduling and page replacement."""
        hybrid_frame = ttk.Frame(self.notebook)
        self.notebook.add(hybrid_frame, text="Hybrid Simulation")
        
        # Main container with paned window
        main_paned = ttk.PanedWindow(hybrid_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for configuration
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=1)
        
        # Right panel for results
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=2)
        
        # Algorithm selection
        algo_frame = ttk.LabelFrame(left_panel, text="Algorithm Selection")
        algo_frame.pack(fill=tk.X, pady=5)
        
        # CPU Scheduling Algorithm
        ttk.Label(algo_frame, text="CPU Scheduling Algorithm:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.hybrid_cpu_var = tk.StringVar(value="FCFS")
        cpu_algorithms = ["FCFS", "SJF (Non-preemptive)", "SJF (Preemptive)", "Round Robin", "Priority", "EDF"]
        self.hybrid_cpu_combo = ttk.Combobox(algo_frame, textvariable=self.hybrid_cpu_var, 
                                           values=cpu_algorithms, state="readonly")
        self.hybrid_cpu_combo.pack(fill=tk.X, pady=2)
        
        # Page Replacement Algorithm
        ttk.Label(algo_frame, text="Page Replacement Algorithm:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        self.hybrid_page_var = tk.StringVar(value="LRU")
        page_algorithms = ["FIFO", "LRU", "Optimal", "Clock"]
        self.hybrid_page_combo = ttk.Combobox(algo_frame, textvariable=self.hybrid_page_var,
                                            values=page_algorithms, state="readonly")
        self.hybrid_page_combo.pack(fill=tk.X, pady=2)
        
        # Parameters
        params_frame = ttk.LabelFrame(left_panel, text="Parameters")
        params_frame.pack(fill=tk.X, pady=5)
        
        # Time quantum
        ttk.Label(params_frame, text="Time Quantum (for RR):").pack(anchor=tk.W)
        self.hybrid_quantum_var = tk.StringVar(value="2")
        ttk.Entry(params_frame, textvariable=self.hybrid_quantum_var, width=10).pack(anchor=tk.W, pady=2)
        
        # Frame count
        ttk.Label(params_frame, text="Memory Frames:").pack(anchor=tk.W)
        self.hybrid_frames_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.hybrid_frames_var, width=10).pack(anchor=tk.W, pady=2)
        
        # Process input with memory pages
        input_frame = ttk.LabelFrame(left_panel, text="Process Input (with Memory Pages)")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(input_frame, text="Format: PID,Arrival,Burst,Priority,Pages").pack(anchor=tk.W)
        ttk.Label(input_frame, text="Pages format: [1,2,3,4] or 1,2,3,4").pack(anchor=tk.W)
        
        self.hybrid_input_text = scrolledtext.ScrolledText(input_frame, height=8, width=30)
        self.hybrid_input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Default hybrid data
        default_hybrid = """1,0,5,2,[1,2,3,4,1,2]
2,1,3,1,[2,3,4,5,2,3]
3,2,8,3,[1,3,5,1,3,5,1,3]
4,3,6,2,[4,5,6,4,5,6]"""
        self.hybrid_input_text.insert(tk.END, default_hybrid)
        
        # Control buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Run Hybrid Simulation", 
                  command=self.run_hybrid_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", 
                  command=lambda: self.hybrid_input_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Load Example", 
                  command=self.load_hybrid_example).pack(side=tk.LEFT, padx=2)
        
        # Results panel
        results_notebook = ttk.Notebook(right_panel)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Combined results tab
        self.hybrid_combined_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.hybrid_combined_frame, text="Combined Results")
        
        # CPU scheduling results tab
        self.hybrid_cpu_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.hybrid_cpu_frame, text="CPU Scheduling")
        
        # Page replacement results tab
        self.hybrid_page_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.hybrid_page_frame, text="Page Replacement")
        
        # Analysis tab
        self.hybrid_analysis_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.hybrid_analysis_frame, text="Analysis")
    
    def create_workload_generator_tab(self):
        """Create the workload generator tab."""
        workload_frame = ttk.Frame(self.notebook)
        self.notebook.add(workload_frame, text="Workload Generator")
        
        # Main container
        main_paned = ttk.PanedWindow(workload_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for configuration
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=1)
        
        # Right panel for generated workload
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=2)
        
        # Basic parameters
        basic_frame = ttk.LabelFrame(left_panel, text="Basic Parameters")
        basic_frame.pack(fill=tk.X, pady=5)
        
        # Number of processes
        ttk.Label(basic_frame, text="Number of Processes:").pack(anchor=tk.W)
        self.num_processes_var = tk.StringVar(value="5")
        ttk.Scale(basic_frame, from_=1, to=20, orient=tk.HORIZONTAL, 
                 variable=self.num_processes_var, command=self.update_process_count).pack(fill=tk.X, pady=2)
        self.process_count_label = ttk.Label(basic_frame, text="5 processes")
        self.process_count_label.pack(anchor=tk.W)
        
        # Workload characteristics
        char_frame = ttk.LabelFrame(left_panel, text="Workload Characteristics")
        char_frame.pack(fill=tk.X, pady=5)
        
        # CPU vs I/O bound ratio
        ttk.Label(char_frame, text="CPU-bound vs I/O-bound Ratio:").pack(anchor=tk.W)
        self.cpu_io_ratio_var = tk.DoubleVar(value=0.5)
        cpu_io_scale = ttk.Scale(char_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                               variable=self.cpu_io_ratio_var, command=self.update_cpu_io_ratio)
        cpu_io_scale.pack(fill=tk.X, pady=2)
        self.cpu_io_label = ttk.Label(char_frame, text="50% CPU-bound, 50% I/O-bound")
        self.cpu_io_label.pack(anchor=tk.W)
        
        # Burst time range
        ttk.Label(char_frame, text="Burst Time Range:").pack(anchor=tk.W, pady=(10,0))
        burst_frame = ttk.Frame(char_frame)
        burst_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(burst_frame, text="Min:").pack(side=tk.LEFT)
        self.min_burst_var = tk.StringVar(value="1")
        ttk.Entry(burst_frame, textvariable=self.min_burst_var, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(burst_frame, text="Max:").pack(side=tk.LEFT, padx=(10,0))
        self.max_burst_var = tk.StringVar(value="20")
        ttk.Entry(burst_frame, textvariable=self.max_burst_var, width=5).pack(side=tk.LEFT, padx=2)
        
        # Arrival time range
        ttk.Label(char_frame, text="Arrival Time Range:").pack(anchor=tk.W, pady=(10,0))
        arrival_frame = ttk.Frame(char_frame)
        arrival_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(arrival_frame, text="Min:").pack(side=tk.LEFT)
        self.min_arrival_var = tk.StringVar(value="0")
        ttk.Entry(arrival_frame, textvariable=self.min_arrival_var, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(arrival_frame, text="Max:").pack(side=tk.LEFT, padx=(10,0))
        self.max_arrival_var = tk.StringVar(value="10")
        ttk.Entry(arrival_frame, textvariable=self.max_arrival_var, width=5).pack(side=tk.LEFT, padx=2)
        
        # Memory characteristics
        memory_frame = ttk.LabelFrame(left_panel, text="Memory Characteristics")
        memory_frame.pack(fill=tk.X, pady=5)
        
        # Memory locality
        ttk.Label(memory_frame, text="Memory Locality:").pack(anchor=tk.W)
        self.locality_var = tk.DoubleVar(value=0.7)
        locality_scale = ttk.Scale(memory_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                 variable=self.locality_var, command=self.update_locality)
        locality_scale.pack(fill=tk.X, pady=2)
        self.locality_label = ttk.Label(memory_frame, text="70% locality")
        self.locality_label.pack(anchor=tk.W)
        
        # Page range
        ttk.Label(memory_frame, text="Page Range:").pack(anchor=tk.W, pady=(10,0))
        page_frame = ttk.Frame(memory_frame)
        page_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(page_frame, text="Min Pages:").pack(side=tk.LEFT)
        self.min_pages_var = tk.StringVar(value="5")
        ttk.Entry(page_frame, textvariable=self.min_pages_var, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(page_frame, text="Max Pages:").pack(side=tk.LEFT, padx=(10,0))
        self.max_pages_var = tk.StringVar(value="20")
        ttk.Entry(page_frame, textvariable=self.max_pages_var, width=5).pack(side=tk.LEFT, padx=2)
        
        # Real-time parameters
        rt_frame = ttk.LabelFrame(left_panel, text="Real-time Parameters")
        rt_frame.pack(fill=tk.X, pady=5)
        
        # Include real-time processes
        self.include_rt_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(rt_frame, text="Include Real-time Processes", 
                       variable=self.include_rt_var, command=self.toggle_rt_options).pack(anchor=tk.W)
        
        # RT percentage
        self.rt_percentage_frame = ttk.Frame(rt_frame)
        ttk.Label(self.rt_percentage_frame, text="RT Process Percentage:").pack(anchor=tk.W)
        self.rt_percentage_var = tk.DoubleVar(value=0.2)
        ttk.Scale(self.rt_percentage_frame, from_=0.1, to=0.5, orient=tk.HORIZONTAL,
                 variable=self.rt_percentage_var, command=self.update_rt_percentage).pack(fill=tk.X, pady=2)
        self.rt_percentage_label = ttk.Label(self.rt_percentage_frame, text="20% real-time")
        self.rt_percentage_label.pack(anchor=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Generate Workload", 
                  command=self.generate_workload).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Export to CPU Tab", 
                  command=self.export_to_cpu_tab).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Export to Hybrid Tab", 
                  command=self.export_to_hybrid_tab).pack(side=tk.LEFT, padx=2)
        
        # Results panel
        results_notebook = ttk.Notebook(right_panel)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Generated workload tab
        self.workload_display_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.workload_display_frame, text="Generated Workload")
        
        self.workload_text = scrolledtext.ScrolledText(self.workload_display_frame)
        self.workload_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Statistics tab
        self.workload_stats_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.workload_stats_frame, text="Statistics")
        
        self.workload_stats_text = scrolledtext.ScrolledText(self.workload_stats_frame)
        self.workload_stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Visualization tab
        self.workload_viz_frame = ttk.Frame(results_notebook)
        results_notebook.add(self.workload_viz_frame, text="Visualization")
        
        # Initialize RT options as hidden
        self.toggle_rt_options()
    
    def update_process_count(self, value):
        """Update process count label."""
        count = int(float(value))
        self.process_count_label.config(text=f"{count} processes")
    
    def update_cpu_io_ratio(self, value):
        """Update CPU/I/O ratio label."""
        ratio = float(value)
        cpu_percent = int(ratio * 100)
        io_percent = 100 - cpu_percent
        self.cpu_io_label.config(text=f"{cpu_percent}% CPU-bound, {io_percent}% I/O-bound")
    
    def update_locality(self, value):
        """Update locality label."""
        locality = float(value)
        percent = int(locality * 100)
        self.locality_label.config(text=f"{percent}% locality")
    
    def update_rt_percentage(self, value):
        """Update real-time percentage label."""
        rt_percent = float(value)
        percent = int(rt_percent * 100)
        self.rt_percentage_label.config(text=f"{percent}% real-time")
    
    def toggle_rt_options(self):
        """Toggle real-time options visibility."""
        if self.include_rt_var.get():
            self.rt_percentage_frame.pack(fill=tk.X, pady=2)
        else:
            self.rt_percentage_frame.pack_forget()
    
    def load_hybrid_example(self):
        """Load example data for hybrid simulation."""
        self.hybrid_input_text.delete(1.0, tk.END)
        example_data = """1,0,5,2,[1,2,3,4,1,2]
2,1,3,1,[2,3,4,5,2,3]
3,2,8,3,[1,3,5,1,3,5,1,3]
4,3,6,2,[4,5,6,4,5,6]"""
        self.hybrid_input_text.insert(tk.END, example_data)
    
    def run_hybrid_simulation(self):
        """Run hybrid simulation combining CPU scheduling and page replacement."""
        try:
            # Parse input
            input_data = self.hybrid_input_text.get(1.0, tk.END).strip()
            if not input_data:
                messagebox.showerror("Error", "Please provide process data!")
                return
            
            processes = self.parse_hybrid_processes(input_data)
            if not processes:
                return
            
            # Get parameters
            cpu_algo = self.hybrid_cpu_var.get()
            page_algo = self.hybrid_page_var.get()
            frame_count = int(self.hybrid_frames_var.get())
            
            # Run CPU scheduling
            cpu_scheduler = self.create_cpu_algorithm_for_hybrid(cpu_algo)
            if not cpu_scheduler:
                messagebox.showerror("Error", "Failed to create CPU scheduler!")
                return
            
            cpu_result = cpu_scheduler.execute(processes)
            
            # Run page replacement for each process
            page_results = {}
            total_page_faults = 0
            
            for process in processes:
                if process.memory_pages:
                    page_algo_instance = self.create_page_algorithm(page_algo)
                    if page_algo_instance:
                        page_result = page_algo_instance.execute(process.memory_pages, frame_count)
                        page_results[process.pid] = page_result
                        total_page_faults += page_result.metrics.get('page_faults', 0)
            
            # Store results
            self.hybrid_results = {
                'cpu_result': cpu_result,
                'page_results': page_results,
                'total_page_faults': total_page_faults,
                'processes': processes,
                'frame_count': frame_count
            }
            
            # Display results
            self.display_hybrid_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Hybrid simulation failed: {str(e)}")
    
    def parse_hybrid_processes(self, input_data: str) -> List[Process]:
        """Parse hybrid process input with memory pages."""
        processes = []
        lines = input_data.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Split by comma, but handle the pages part specially
                if '[' in line and ']' in line:
                    # Format: PID,Arrival,Burst,Priority,[pages]
                    parts = line.split('[')
                    main_parts = parts[0].rstrip(',').split(',')
                    pages_part = parts[1].rstrip(']')
                    pages = [int(x.strip()) for x in pages_part.split(',') if x.strip()]
                else:
                    # Format: PID,Arrival,Burst,Priority,page1,page2,page3...
                    all_parts = [x.strip() for x in line.split(',')]
                    main_parts = all_parts[:4]
                    pages = [int(x) for x in all_parts[4:] if x.isdigit()]
                
                if len(main_parts) >= 3:
                    pid = int(main_parts[0])
                    arrival = int(main_parts[1])
                    burst = int(main_parts[2])
                    priority = int(main_parts[3]) if len(main_parts) > 3 else 0
                    
                    process = Process(
                        pid=pid,
                        arrival_time=arrival,
                        burst_time=burst,
                        priority=priority,
                        memory_pages=pages
                    )
                    processes.append(process)
                    
            except (ValueError, IndexError) as e:
                messagebox.showerror("Input Error", f"Invalid process format in line: {line}")
                return []
        
        return processes
    
    def create_cpu_algorithm_for_hybrid(self, algo_name: str):
        """Create CPU scheduling algorithm for hybrid simulation."""
        if algo_name == "FCFS":
            return FCFSScheduler()
        elif algo_name == "SJF (Non-preemptive)":
            return SJFScheduler(preemptive=False)
        elif algo_name == "SJF (Preemptive)":
            return SJFScheduler(preemptive=True)
        elif algo_name == "Round Robin":
            quantum = int(self.hybrid_quantum_var.get())
            return RoundRobinScheduler(time_quantum=quantum)
        elif algo_name == "Priority":
            return PriorityScheduler(preemptive=False)
        elif algo_name == "EDF":
            return EDFScheduler()
        return None
    
    def display_hybrid_results(self):
        """Display hybrid simulation results."""
        if not self.hybrid_results:
            return
        
        # Clear previous results
        for widget in self.hybrid_combined_frame.winfo_children():
            widget.destroy()
        for widget in self.hybrid_cpu_frame.winfo_children():
            widget.destroy()
        for widget in self.hybrid_page_frame.winfo_children():
            widget.destroy()
        for widget in self.hybrid_analysis_frame.winfo_children():
            widget.destroy()
        
        # Display combined results
        self.create_hybrid_combined_view()
        
        # Display CPU scheduling results
        cpu_result = self.hybrid_results['cpu_result']
        self.create_gantt_chart(cpu_result, self.hybrid_cpu_frame)
        self.add_metrics_to_frame(cpu_result, self.hybrid_cpu_frame, "CPU Scheduling")
        
        # Display page replacement results
        self.create_hybrid_page_view()
        
        # Display analysis
        self.create_hybrid_analysis()
    
    def create_hybrid_combined_view(self):
        """Create combined view for hybrid results."""
        main_frame = ttk.Frame(self.hybrid_combined_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Hybrid Simulation Results", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Summary metrics
        summary_frame = ttk.LabelFrame(main_frame, text="Summary Metrics")
        summary_frame.pack(fill=tk.X, pady=10)
        
        cpu_result = self.hybrid_results['cpu_result']
        total_faults = self.hybrid_results['total_page_faults']
        
        summary_text = f"""CPU Scheduling: {cpu_result.algorithm_name}
Average Turnaround Time: {cpu_result.metrics.get('average_turnaround_time', 0):.2f}
Average Waiting Time: {cpu_result.metrics.get('average_waiting_time', 0):.2f}
CPU Utilization: {cpu_result.metrics.get('cpu_utilization', 0):.2f}

Memory Management:
Total Page Faults: {total_faults}
Processes with Memory: {len(self.hybrid_results['page_results'])}
Average Faults per Process: {total_faults / max(len(self.hybrid_results['page_results']), 1):.2f}"""
        
        summary_label = ttk.Label(summary_frame, text=summary_text, justify=tk.LEFT)
        summary_label.pack(padx=10, pady=10)
    
    def create_hybrid_page_view(self):
        """Create page replacement view for hybrid results."""
        main_frame = ttk.Frame(self.hybrid_page_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Page Replacement Results by Process", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=5)
        
        # Create treeview for process results
        columns = ('Process', 'Pages Accessed', 'Page Faults', 'Hit Ratio', 'Fault Ratio')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        
        # Add process results
        for pid, result in self.hybrid_results['page_results'].items():
            tree.insert('', 'end', values=(
                f"P{pid}",
                result.metrics.get('total_references', 0),
                result.metrics.get('page_faults', 0),
                f"{result.metrics.get('hit_ratio', 0):.2f}",
                f"{result.metrics.get('fault_ratio', 0):.2f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_hybrid_analysis(self):
        """Create analysis view for hybrid results."""
        main_frame = ttk.Frame(self.hybrid_analysis_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Analysis text
        analysis_text = scrolledtext.ScrolledText(main_frame)
        analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Generate analysis
        cpu_result = self.hybrid_results['cpu_result']
        page_results = self.hybrid_results['page_results']
        processes = self.hybrid_results['processes']
        
        analysis = f"""HYBRID SIMULATION ANALYSIS
{'=' * 50}

CPU SCHEDULING ANALYSIS:
Algorithm: {cpu_result.algorithm_name}
Total Execution Time: {cpu_result.metrics.get('total_execution_time', 0):.2f}
Average Turnaround Time: {cpu_result.metrics.get('average_turnaround_time', 0):.2f}
Average Waiting Time: {cpu_result.metrics.get('average_waiting_time', 0):.2f}
CPU Utilization: {cpu_result.metrics.get('cpu_utilization', 0):.2f}%

MEMORY MANAGEMENT ANALYSIS:
Total Page Faults: {self.hybrid_results['total_page_faults']}
Processes with Memory Access: {len(page_results)}

PROCESS-BY-PROCESS ANALYSIS:
"""
        
        for process in processes:
            analysis += f"\nProcess P{process.pid}:\n"
            analysis += f"  CPU: Arrival={process.arrival_time}, Burst={process.burst_time}, Priority={process.priority}\n"
            
            if process.pid in page_results:
                page_result = page_results[process.pid]
                analysis += f"  Memory: {len(process.memory_pages)} page accesses, "
                analysis += f"{page_result.metrics.get('page_faults', 0)} faults "
                analysis += f"({page_result.metrics.get('fault_ratio', 0):.2f} fault ratio)\n"
            else:
                analysis += f"  Memory: No memory access pattern\n"
        
        analysis += f"""
PERFORMANCE INSIGHTS:
• CPU scheduling efficiency: {cpu_result.metrics.get('throughput', 0):.2f} processes/time unit
• Memory pressure: {self.hybrid_results['total_page_faults'] / len(processes):.2f} avg faults/process
• System overhead: Page faults can cause additional CPU scheduling delays
• Workload characteristics: {len([p for p in processes if p.memory_pages])} of {len(processes)} processes access memory

RECOMMENDATIONS:
"""
        
        # Add recommendations based on results
        avg_faults = self.hybrid_results['total_page_faults'] / max(len(page_results), 1)
        if avg_faults > 5:
            analysis += "• Consider increasing memory frames to reduce page faults\n"
        if cpu_result.metrics.get('average_waiting_time', 0) > 10:
            analysis += "• CPU scheduling shows high waiting times - consider preemptive algorithms\n"
        if cpu_result.metrics.get('cpu_utilization', 0) < 80:
            analysis += "• Low CPU utilization - workload may be I/O bound\n"
        
        analysis_text.insert(tk.END, analysis)
        analysis_text.config(state=tk.DISABLED)
    
    def generate_workload(self):
        """Generate workload based on parameters."""
        try:
            # Get parameters
            num_processes = int(float(self.num_processes_var.get()))
            cpu_io_ratio = self.cpu_io_ratio_var.get()
            min_burst = int(self.min_burst_var.get())
            max_burst = int(self.max_burst_var.get())
            min_arrival = int(self.min_arrival_var.get())
            max_arrival = int(self.max_arrival_var.get())
            locality = self.locality_var.get()
            min_pages = int(self.min_pages_var.get())
            max_pages = int(self.max_pages_var.get())
            include_rt = self.include_rt_var.get()
            rt_percentage = self.rt_percentage_var.get() if include_rt else 0
            
            # Generate processes
            processes = []
            current_time = 0
            
            for i in range(num_processes):
                # Determine process type
                is_cpu_bound = random.random() < cpu_io_ratio
                is_rt = include_rt and random.random() < rt_percentage
                
                # Generate basic parameters
                pid = i + 1
                arrival_time = random.randint(min_arrival, max_arrival)
                
                if is_cpu_bound:
                    burst_time = random.randint(max(min_burst, 3), max_burst)
                else:
                    burst_time = random.randint(min_burst, min(max_burst, 8))
                
                priority = random.randint(1, 10)
                
                # Generate memory access pattern
                num_page_accesses = random.randint(min_pages, max_pages)
                memory_pages = self.generate_memory_pattern(num_page_accesses, locality, is_cpu_bound)
                
                # Generate deadline for real-time processes
                deadline = None
                if is_rt:
                    deadline = arrival_time + burst_time + random.randint(5, 15)
                
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
            
            # Store generated workload
            self.generated_workload = {
                'processes': processes,
                'metadata': {
                    'num_processes': num_processes,
                    'cpu_bound_count': sum(1 for p in processes if not p.io_operations),
                    'io_bound_count': sum(1 for p in processes if p.io_operations),
                    'rt_count': sum(1 for p in processes if p.deadline is not None),
                    'avg_burst_time': sum(p.burst_time for p in processes) / num_processes,
                    'avg_memory_accesses': sum(len(p.memory_pages) for p in processes) / num_processes,
                    'parameters': {
                        'cpu_io_ratio': cpu_io_ratio,
                        'locality': locality,
                        'burst_range': (min_burst, max_burst),
                        'arrival_range': (min_arrival, max_arrival),
                        'page_range': (min_pages, max_pages)
                    }
                }
            }
            
            # Display results
            self.display_generated_workload()
            
        except Exception as e:
            messagebox.showerror("Error", f"Workload generation failed: {str(e)}")
    
    def generate_memory_pattern(self, num_accesses: int, locality: float, is_cpu_bound: bool) -> List[int]:
        """Generate memory access pattern with locality."""
        pages = []
        
        if is_cpu_bound:
            # CPU-bound processes have high locality
            base_pages = list(range(1, 6))  # Small working set
            for _ in range(num_accesses):
                if random.random() < locality:
                    # Access within working set
                    pages.append(random.choice(base_pages))
                else:
                    # Random access
                    pages.append(random.randint(1, 20))
        else:
            # I/O-bound processes have more scattered access
            for _ in range(num_accesses):
                if random.random() < locality * 0.7:  # Lower locality
                    # Some locality
                    if pages:
                        last_page = pages[-1]
                        pages.append(max(1, last_page + random.randint(-2, 2)))
                    else:
                        pages.append(random.randint(1, 20))
                else:
                    # Random access
                    pages.append(random.randint(1, 30))
        
        return pages
    
    def display_generated_workload(self):
        """Display the generated workload."""
        if not self.generated_workload:
            return
        
        processes = self.generated_workload['processes']
        metadata = self.generated_workload['metadata']
        
        # Clear previous results
        self.workload_text.delete(1.0, tk.END)
        self.workload_stats_text.delete(1.0, tk.END)
        
        # Display workload
        workload_content = "GENERATED WORKLOAD\n"
        workload_content += "=" * 50 + "\n\n"
        workload_content += "Format: PID,Arrival,Burst,Priority,[Memory_Pages],Deadline,Type\n\n"
        
        for process in processes:
            process_type = "RT" if process.deadline else ("CPU" if not process.io_operations else "I/O")
            pages_str = str(process.memory_pages) if process.memory_pages else "[]"
            deadline_str = str(process.deadline) if process.deadline else "None"
            
            workload_content += f"{process.pid},{process.arrival_time},{process.burst_time},"
            workload_content += f"{process.priority},{pages_str},{deadline_str},{process_type}\n"
        
        self.workload_text.insert(tk.END, workload_content)
        
        # Display statistics
        stats_content = f"""WORKLOAD STATISTICS
{'=' * 50}

Process Distribution:
• Total Processes: {metadata['num_processes']}
• CPU-bound: {metadata['cpu_bound_count']} ({metadata['cpu_bound_count']/metadata['num_processes']*100:.1f}%)
• I/O-bound: {metadata['io_bound_count']} ({metadata['io_bound_count']/metadata['num_processes']*100:.1f}%)
• Real-time: {metadata['rt_count']} ({metadata['rt_count']/metadata['num_processes']*100:.1f}%)

Timing Characteristics:
• Average Burst Time: {metadata['avg_burst_time']:.2f}
• Burst Time Range: {metadata['parameters']['burst_range']}
• Arrival Time Range: {metadata['parameters']['arrival_range']}

Memory Characteristics:
• Average Memory Accesses: {metadata['avg_memory_accesses']:.2f}
• Page Range: {metadata['parameters']['page_range']}
• Locality Factor: {metadata['parameters']['locality']:.2f}

Generation Parameters:
• CPU/I/O Ratio: {metadata['parameters']['cpu_io_ratio']:.2f}
• Memory Locality: {metadata['parameters']['locality']:.2f}
"""
        
        self.workload_stats_text.insert(tk.END, stats_content)
        
        # Create visualization
        self.create_workload_visualization()
    
    def create_workload_visualization(self):
        """Create workload visualization."""
        if not self.generated_workload:
            return
        
        # Clear previous visualization
        for widget in self.workload_viz_frame.winfo_children():
            widget.destroy()
        
        processes = self.generated_workload['processes']
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # 1. Arrival time distribution
        arrival_times = [p.arrival_time for p in processes]
        ax1.hist(arrival_times, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('Arrival Time Distribution')
        ax1.set_xlabel('Arrival Time')
        ax1.set_ylabel('Number of Processes')
        
        # 2. Burst time distribution
        burst_times = [p.burst_time for p in processes]
        ax2.hist(burst_times, bins=10, alpha=0.7, color='lightgreen', edgecolor='black')
        ax2.set_title('Burst Time Distribution')
        ax2.set_xlabel('Burst Time')
        ax2.set_ylabel('Number of Processes')
        
        # 3. Process type distribution
        cpu_count = sum(1 for p in processes if not p.io_operations and not p.deadline)
        io_count = sum(1 for p in processes if p.io_operations)
        rt_count = sum(1 for p in processes if p.deadline)
        
        labels = ['CPU-bound', 'I/O-bound', 'Real-time']
        sizes = [cpu_count, io_count, rt_count]
        colors = ['#ff9999', '#66b2ff', '#99ff99']
        
        ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax3.set_title('Process Type Distribution')
        
        # 4. Memory access pattern
        memory_accesses = [len(p.memory_pages) for p in processes if p.memory_pages]
        if memory_accesses:
            ax4.hist(memory_accesses, bins=10, alpha=0.7, color='orange', edgecolor='black')
            ax4.set_title('Memory Accesses per Process')
            ax4.set_xlabel('Number of Memory Accesses')
            ax4.set_ylabel('Number of Processes')
        else:
            ax4.text(0.5, 0.5, 'No Memory Access Data', ha='center', va='center')
            ax4.set_title('Memory Accesses per Process')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.workload_viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_to_cpu_tab(self):
        """Export generated workload to CPU scheduling tab."""
        if not self.generated_workload:
            messagebox.showwarning("Warning", "No workload generated yet!")
            return
        
        processes = self.generated_workload['processes']
        
        # Format for CPU tab (without memory pages)
        cpu_data = ""
        for process in processes:
            cpu_data += f"{process.pid},{process.arrival_time},{process.burst_time},{process.priority}\n"
        
        # Insert into CPU tab
        self.cpu_process_text.delete(1.0, tk.END)
        self.cpu_process_text.insert(tk.END, cpu_data.strip())
        
        # Switch to CPU tab
        self.notebook.select(0)
        messagebox.showinfo("Success", "Workload exported to CPU Scheduling tab!")
    
    def export_to_hybrid_tab(self):
        """Export generated workload to hybrid simulation tab."""
        if not self.generated_workload:
            messagebox.showwarning("Warning", "No workload generated yet!")
            return
        
        processes = self.generated_workload['processes']
        
        # Format for hybrid tab (with memory pages)
        hybrid_data = ""
        for process in processes:
            pages_str = str(process.memory_pages) if process.memory_pages else "[]"
            hybrid_data += f"{process.pid},{process.arrival_time},{process.burst_time},{process.priority},{pages_str}\n"
        
        # Insert into hybrid tab
        self.hybrid_input_text.delete(1.0, tk.END)
        self.hybrid_input_text.insert(tk.END, hybrid_data.strip())
        
        # Switch to hybrid tab
        self.notebook.select(3)  # Hybrid tab is index 3
        messagebox.showinfo("Success", "Workload exported to Hybrid Simulation tab!")


def main():
    root = tk.Tk()
    app = OSAlgorithmSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()