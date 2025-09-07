"""
Data models for the OS Algorithms Simulator.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum

class AccessType(Enum):
    """Memory access types."""
    READ = "read"
    WRITE = "write"

class ProcessState(Enum):
    """Process states for scheduling."""
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    TERMINATED = "terminated"

@dataclass
class IOOperation:
    """Represents an I/O operation within a process."""
    start_time: int
    duration: int
    operation_type: str = "disk"

@dataclass
class Process:
    """Represents a process for CPU scheduling algorithms."""
    pid: int
    arrival_time: int
    burst_time: int
    priority: int = 0
    memory_pages: List[int] = field(default_factory=list)
    io_operations: List[IOOperation] = field(default_factory=list)
    deadline: Optional[int] = None  # For EDF scheduling
    remaining_time: int = 0  # For preemptive algorithms
    
    def __post_init__(self):
        """Initialize remaining time if not set."""
        if self.remaining_time == 0:
            self.remaining_time = self.burst_time
    
    def validate(self) -> bool:
        """Validate process data."""
        if self.pid < 0:
            raise ValueError("Process ID must be non-negative")
        if self.arrival_time < 0:
            raise ValueError("Arrival time must be non-negative")
        if self.burst_time <= 0:
            raise ValueError("Burst time must be positive")
        if self.deadline is not None and self.deadline < self.arrival_time:
            raise ValueError("Deadline must be after arrival time")
        return True

@dataclass
class PageReference:
    """Represents a page reference in memory."""
    page_number: int
    timestamp: int
    access_type: AccessType = AccessType.READ
    
    def validate(self) -> bool:
        """Validate page reference data."""
        if self.page_number < 0:
            raise ValueError("Page number must be non-negative")
        if self.timestamp < 0:
            raise ValueError("Timestamp must be non-negative")
        return True

@dataclass
class FrameState:
    """Represents the state of a memory frame."""
    frame_id: int
    page_number: Optional[int] = None
    last_access_time: int = 0
    reference_bit: bool = False  # For Clock algorithm
    dirty_bit: bool = False
    
    def is_empty(self) -> bool:
        """Check if frame is empty."""
        return self.page_number is None
    
    def load_page(self, page_number: int, timestamp: int, dirty: bool = False):
        """Load a page into this frame."""
        self.page_number = page_number
        self.last_access_time = timestamp
        self.reference_bit = True
        self.dirty_bit = dirty
    
    def clear(self):
        """Clear the frame."""
        self.page_number = None
        self.last_access_time = 0
        self.reference_bit = False
        self.dirty_bit = False

@dataclass
class SimulationStep:
    """Represents a single step in algorithm execution."""
    step_number: int
    timestamp: int
    action: str  # Description of what happened
    state_before: Dict[str, Any]
    state_after: Dict[str, Any]
    is_hit: Optional[bool] = None  # For page replacement algorithms
    is_fault: Optional[bool] = None  # For page replacement algorithms
    process_id: Optional[int] = None  # For scheduling algorithms
    
    def validate(self) -> bool:
        """Validate simulation step data."""
        if self.step_number < 0:
            raise ValueError("Step number must be non-negative")
        if self.timestamp < 0:
            raise ValueError("Timestamp must be non-negative")
        if not self.action:
            raise ValueError("Action description cannot be empty")
        return True

@dataclass
class SimulationResult:
    """Contains the complete results of an algorithm simulation."""
    algorithm_name: str
    execution_steps: List[SimulationStep]
    metrics: Dict[str, float]
    visualization_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    input_parameters: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate simulation result data."""
        if not self.algorithm_name:
            raise ValueError("Algorithm name cannot be empty")
        if not isinstance(self.execution_steps, list):
            raise ValueError("Execution steps must be a list")
        if not isinstance(self.metrics, dict):
            raise ValueError("Metrics must be a dictionary")
        if not isinstance(self.visualization_data, dict):
            raise ValueError("Visualization data must be a dictionary")
        
        # Validate all steps
        for step in self.execution_steps:
            step.validate()
        
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the simulation results."""
        return {
            'algorithm': self.algorithm_name,
            'total_steps': len(self.execution_steps),
            'key_metrics': self.metrics,
            'timestamp': self.timestamp.isoformat(),
            'input_parameters': self.input_parameters
        }