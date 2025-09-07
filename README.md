# OS Algorithms Simulator 🖥️

Interactive desktop app for visualizing CPU scheduling and page replacement algorithms.

## Quick Start

```bash
pip install matplotlib
python tkinter_simulator.py
```

## What's Inside

**CPU Scheduling**: FCFS • SJF • Round Robin • Priority • MLFQ • EDF  
**Page Replacement**: FIFO • LRU • Optimal • Clock  
**Advanced**: Algorithm Duel • Hybrid Simulation • Workload Generator

## Features

1. **Visual Results** - Gantt charts and frame state diagrams  
2. **Algorithm Comparison** - Side-by-side performance analysis  
3. **Real-time Scheduling** - EDF with deadline visualization  
4. **Workload Generator** - Create realistic test scenarios  
5. **No Web Server** - Pure desktop app, works offline

## Example Input

```
CPU: 1,0,5,2,10    (PID, Arrival, Burst, Priority, Deadline)
Page: 1,2,3,4,1,2,5,1,2,3,4,5
```

## Try the Demos

```bash
python demos/demo_cpu_scheduling.py      # Basic algorithms
python demos/demo_algorithm_duel.py      # Compare algorithms  
python demos/demo_hybrid_workload.py     # Advanced features
```

Perfect for students, educators, and anyone learning operating systems! 🎓