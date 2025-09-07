"""
Page replacement algorithm implementations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from algorithms.base import PageReplacementBase
from models.data_models import SimulationResult, SimulationStep, FrameState, PageReference, AccessType


class FIFOAlgorithm(PageReplacementBase):
    """First-In-First-Out page replacement algorithm."""
    
    def __init__(self):
        super().__init__()
        self.algorithm_name = "FIFO"
        self.frames: List[FrameState] = []
        self.insertion_order: List[int] = []  # Track insertion order for FIFO
    
    def execute(self, page_sequence: List[int], frame_count: int) -> SimulationResult:
        """Execute FIFO page replacement algorithm."""
        self.reset()
        
        # Initialize frames
        self.frames = [FrameState(frame_id=i) for i in range(frame_count)]
        self.insertion_order = []
        
        page_faults = 0
        
        for step_num, page_num in enumerate(page_sequence):
            timestamp = step_num
            
            # Check if page is already in memory (hit)
            hit_frame = self._find_page_in_frames(page_num)
            
            if hit_frame is not None:
                # Page hit - update access time
                hit_frame.last_access_time = timestamp
                self._record_step(step_num, timestamp, page_num, True, False)
            else:
                # Page fault
                page_faults += 1
                
                # Find empty frame or use FIFO replacement
                empty_frame = self._find_empty_frame()
                
                if empty_frame is not None:
                    # Use empty frame
                    empty_frame.load_page(page_num, timestamp)
                    self.insertion_order.append(empty_frame.frame_id)
                else:
                    # Replace using FIFO policy
                    victim_frame_id = self.insertion_order.pop(0)
                    victim_frame = self.frames[victim_frame_id]
                    victim_frame.load_page(page_num, timestamp)
                    self.insertion_order.append(victim_frame_id)
                
                self._record_step(step_num, timestamp, page_num, False, True)
        
        # Calculate metrics
        self.metrics = self._calculate_metrics(len(page_sequence), page_faults)
        
        # Prepare visualization data
        visualization_data = {
            'frame_states_timeline': [step.state_after for step in self.simulation_steps],
            'hit_miss_pattern': [step.is_hit for step in self.simulation_steps],
            'algorithm_specific': {
                'insertion_order': self.insertion_order.copy()
            }
        }
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps.copy(),
            metrics=self.metrics.copy(),
            visualization_data=visualization_data,
            input_parameters={'page_sequence': page_sequence, 'frame_count': frame_count}
        )
    
    def _find_page_in_frames(self, page_num: int) -> Optional[FrameState]:
        """Find if page is already loaded in any frame."""
        for frame in self.frames:
            if frame.page_number == page_num:
                return frame
        return None
    
    def _find_empty_frame(self) -> Optional[FrameState]:
        """Find an empty frame."""
        for frame in self.frames:
            if frame.is_empty():
                return frame
        return None
    
    def _record_step(self, step_num: int, timestamp: int, page_num: int, is_hit: bool, is_fault: bool):
        """Record a simulation step."""
        state_before = self._get_current_state()
        
        step = SimulationStep(
            step_number=step_num,
            timestamp=timestamp,
            action=f"Access page {page_num} - {'HIT' if is_hit else 'FAULT'}",
            state_before=state_before,
            state_after=self._get_current_state(),
            is_hit=is_hit,
            is_fault=is_fault
        )
        
        self.simulation_steps.append(step)
    
    def _get_current_state(self) -> Dict[str, Any]:
        """Get current state of all frames."""
        return {
            'frames': [
                {
                    'frame_id': frame.frame_id,
                    'page_number': frame.page_number,
                    'last_access_time': frame.last_access_time,
                    'is_empty': frame.is_empty()
                }
                for frame in self.frames
            ],
            'insertion_order': self.insertion_order.copy()
        }


class LRUAlgorithm(PageReplacementBase):
    """Least Recently Used page replacement algorithm."""
    
    def __init__(self):
        super().__init__()
        self.algorithm_name = "LRU"
        self.frames: List[FrameState] = []
    
    def execute(self, page_sequence: List[int], frame_count: int) -> SimulationResult:
        """Execute LRU page replacement algorithm."""
        self.reset()
        
        # Initialize frames
        self.frames = [FrameState(frame_id=i) for i in range(frame_count)]
        
        page_faults = 0
        
        for step_num, page_num in enumerate(page_sequence):
            timestamp = step_num
            
            # Check if page is already in memory (hit)
            hit_frame = self._find_page_in_frames(page_num)
            
            if hit_frame is not None:
                # Page hit - update access time
                hit_frame.last_access_time = timestamp
                self._record_step(step_num, timestamp, page_num, True, False)
            else:
                # Page fault
                page_faults += 1
                
                # Find empty frame or use LRU replacement
                empty_frame = self._find_empty_frame()
                
                if empty_frame is not None:
                    # Use empty frame
                    empty_frame.load_page(page_num, timestamp)
                else:
                    # Replace using LRU policy
                    lru_frame = self._find_lru_frame()
                    lru_frame.load_page(page_num, timestamp)
                
                self._record_step(step_num, timestamp, page_num, False, True)
        
        # Calculate metrics
        self.metrics = self._calculate_metrics(len(page_sequence), page_faults)
        
        # Prepare visualization data
        visualization_data = {
            'frame_states_timeline': [step.state_after for step in self.simulation_steps],
            'hit_miss_pattern': [step.is_hit for step in self.simulation_steps],
            'algorithm_specific': {
                'access_times': {frame.frame_id: frame.last_access_time for frame in self.frames}
            }
        }
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps.copy(),
            metrics=self.metrics.copy(),
            visualization_data=visualization_data,
            input_parameters={'page_sequence': page_sequence, 'frame_count': frame_count}
        )
    
    def _find_page_in_frames(self, page_num: int) -> Optional[FrameState]:
        """Find if page is already loaded in any frame."""
        for frame in self.frames:
            if frame.page_number == page_num:
                return frame
        return None
    
    def _find_empty_frame(self) -> Optional[FrameState]:
        """Find an empty frame."""
        for frame in self.frames:
            if frame.is_empty():
                return frame
        return None
    
    def _find_lru_frame(self) -> FrameState:
        """Find the least recently used frame."""
        lru_frame = None
        oldest_time = float('inf')
        
        for frame in self.frames:
            if not frame.is_empty() and frame.last_access_time < oldest_time:
                oldest_time = frame.last_access_time
                lru_frame = frame
        
        return lru_frame
    
    def _record_step(self, step_num: int, timestamp: int, page_num: int, is_hit: bool, is_fault: bool):
        """Record a simulation step."""
        state_before = self._get_current_state()
        
        step = SimulationStep(
            step_number=step_num,
            timestamp=timestamp,
            action=f"Access page {page_num} - {'HIT' if is_hit else 'FAULT'}",
            state_before=state_before,
            state_after=self._get_current_state(),
            is_hit=is_hit,
            is_fault=is_fault
        )
        
        self.simulation_steps.append(step)
    
    def _get_current_state(self) -> Dict[str, Any]:
        """Get current state of all frames."""
        return {
            'frames': [
                {
                    'frame_id': frame.frame_id,
                    'page_number': frame.page_number,
                    'last_access_time': frame.last_access_time,
                    'is_empty': frame.is_empty()
                }
                for frame in self.frames
            ]
        }


class OptimalAlgorithm(PageReplacementBase):
    """Optimal (Belady's) page replacement algorithm."""
    
    def __init__(self):
        super().__init__()
        self.algorithm_name = "Optimal"
        self.frames: List[FrameState] = []
        self.page_sequence: List[int] = []
    
    def execute(self, page_sequence: List[int], frame_count: int) -> SimulationResult:
        """Execute Optimal page replacement algorithm."""
        self.reset()
        
        # Store page sequence for future reference lookup
        self.page_sequence = page_sequence.copy()
        
        # Initialize frames
        self.frames = [FrameState(frame_id=i) for i in range(frame_count)]
        
        page_faults = 0
        
        for step_num, page_num in enumerate(page_sequence):
            timestamp = step_num
            
            # Check if page is already in memory (hit)
            hit_frame = self._find_page_in_frames(page_num)
            
            if hit_frame is not None:
                # Page hit - update access time
                hit_frame.last_access_time = timestamp
                self._record_step(step_num, timestamp, page_num, True, False)
            else:
                # Page fault
                page_faults += 1
                
                # Find empty frame or use Optimal replacement
                empty_frame = self._find_empty_frame()
                
                if empty_frame is not None:
                    # Use empty frame
                    empty_frame.load_page(page_num, timestamp)
                else:
                    # Replace using Optimal policy
                    victim_frame = self._find_optimal_victim(step_num)
                    victim_frame.load_page(page_num, timestamp)
                
                self._record_step(step_num, timestamp, page_num, False, True)
        
        # Calculate metrics
        self.metrics = self._calculate_metrics(len(page_sequence), page_faults)
        
        # Prepare visualization data
        visualization_data = {
            'frame_states_timeline': [step.state_after for step in self.simulation_steps],
            'hit_miss_pattern': [step.is_hit for step in self.simulation_steps],
            'algorithm_specific': {
                'future_references': self._get_future_reference_info()
            }
        }
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps.copy(),
            metrics=self.metrics.copy(),
            visualization_data=visualization_data,
            input_parameters={'page_sequence': page_sequence, 'frame_count': frame_count}
        )
    
    def _find_page_in_frames(self, page_num: int) -> Optional[FrameState]:
        """Find if page is already loaded in any frame."""
        for frame in self.frames:
            if frame.page_number == page_num:
                return frame
        return None
    
    def _find_empty_frame(self) -> Optional[FrameState]:
        """Find an empty frame."""
        for frame in self.frames:
            if frame.is_empty():
                return frame
        return None
    
    def _find_optimal_victim(self, current_step: int) -> FrameState:
        """Find the frame to replace using optimal policy."""
        farthest_next_use = -1
        victim_frame = None
        
        for frame in self.frames:
            if frame.is_empty():
                continue
            
            # Find next use of this page
            next_use = self._find_next_use(frame.page_number, current_step + 1)
            
            if next_use == -1:  # Page never used again
                return frame
            elif next_use > farthest_next_use:
                farthest_next_use = next_use
                victim_frame = frame
        
        return victim_frame if victim_frame else self.frames[0]
    
    def _find_next_use(self, page_num: int, start_index: int) -> int:
        """Find the next use of a page starting from start_index."""
        for i in range(start_index, len(self.page_sequence)):
            if self.page_sequence[i] == page_num:
                return i
        return -1  # Page never used again
    
    def _get_future_reference_info(self) -> Dict[str, Any]:
        """Get information about future references for visualization."""
        future_info = {}
        for step_num in range(len(self.page_sequence)):
            page_num = self.page_sequence[step_num]
            next_use = self._find_next_use(page_num, step_num + 1)
            future_info[f"step_{step_num}"] = {
                'page': page_num,
                'next_use': next_use
            }
        return future_info
    
    def _record_step(self, step_num: int, timestamp: int, page_num: int, is_hit: bool, is_fault: bool):
        """Record a simulation step."""
        state_before = self._get_current_state()
        
        step = SimulationStep(
            step_number=step_num,
            timestamp=timestamp,
            action=f"Access page {page_num} - {'HIT' if is_hit else 'FAULT'}",
            state_before=state_before,
            state_after=self._get_current_state(),
            is_hit=is_hit,
            is_fault=is_fault
        )
        
        self.simulation_steps.append(step)
    
    def _get_current_state(self) -> Dict[str, Any]:
        """Get current state of all frames."""
        return {
            'frames': [
                {
                    'frame_id': frame.frame_id,
                    'page_number': frame.page_number,
                    'last_access_time': frame.last_access_time,
                    'is_empty': frame.is_empty()
                }
                for frame in self.frames
            ]
        }


class ClockAlgorithm(PageReplacementBase):
    """Clock (Second Chance) page replacement algorithm."""
    
    def __init__(self):
        super().__init__()
        self.algorithm_name = "Clock"
        self.frames: List[FrameState] = []
        self.clock_hand: int = 0  # Points to current position in circular buffer
    
    def execute(self, page_sequence: List[int], frame_count: int) -> SimulationResult:
        """Execute Clock page replacement algorithm."""
        self.reset()
        
        # Initialize frames
        self.frames = [FrameState(frame_id=i) for i in range(frame_count)]
        self.clock_hand = 0
        
        page_faults = 0
        
        for step_num, page_num in enumerate(page_sequence):
            timestamp = step_num
            
            # Check if page is already in memory (hit)
            hit_frame = self._find_page_in_frames(page_num)
            
            if hit_frame is not None:
                # Page hit - set reference bit
                hit_frame.last_access_time = timestamp
                hit_frame.reference_bit = True
                self._record_step(step_num, timestamp, page_num, True, False)
            else:
                # Page fault
                page_faults += 1
                
                # Find empty frame or use Clock replacement
                empty_frame = self._find_empty_frame()
                
                if empty_frame is not None:
                    # Use empty frame
                    empty_frame.load_page(page_num, timestamp)
                else:
                    # Replace using Clock policy
                    victim_frame = self._find_clock_victim()
                    victim_frame.load_page(page_num, timestamp)
                
                self._record_step(step_num, timestamp, page_num, False, True)
        
        # Calculate metrics
        self.metrics = self._calculate_metrics(len(page_sequence), page_faults)
        
        # Prepare visualization data
        visualization_data = {
            'frame_states_timeline': [step.state_after for step in self.simulation_steps],
            'hit_miss_pattern': [step.is_hit for step in self.simulation_steps],
            'algorithm_specific': {
                'clock_hand_positions': self._get_clock_hand_history(),
                'reference_bits': {frame.frame_id: frame.reference_bit for frame in self.frames}
            }
        }
        
        return SimulationResult(
            algorithm_name=self.algorithm_name,
            execution_steps=self.simulation_steps.copy(),
            metrics=self.metrics.copy(),
            visualization_data=visualization_data,
            input_parameters={'page_sequence': page_sequence, 'frame_count': frame_count}
        )
    
    def _find_page_in_frames(self, page_num: int) -> Optional[FrameState]:
        """Find if page is already loaded in any frame."""
        for frame in self.frames:
            if frame.page_number == page_num:
                return frame
        return None
    
    def _find_empty_frame(self) -> Optional[FrameState]:
        """Find an empty frame."""
        for frame in self.frames:
            if frame.is_empty():
                return frame
        return None
    
    def _find_clock_victim(self) -> FrameState:
        """Find victim frame using clock algorithm."""
        while True:
            current_frame = self.frames[self.clock_hand]
            
            if current_frame.reference_bit:
                # Give second chance - clear reference bit and move clock hand
                current_frame.reference_bit = False
                self.clock_hand = (self.clock_hand + 1) % len(self.frames)
            else:
                # Found victim - don't move clock hand yet (will be moved after replacement)
                victim_frame = current_frame
                self.clock_hand = (self.clock_hand + 1) % len(self.frames)
                return victim_frame
    
    def _get_clock_hand_history(self) -> List[int]:
        """Get history of clock hand positions for visualization."""
        # This is a simplified version - in a full implementation,
        # we would track this throughout the simulation
        return [self.clock_hand]
    
    def _record_step(self, step_num: int, timestamp: int, page_num: int, is_hit: bool, is_fault: bool):
        """Record a simulation step."""
        state_before = self._get_current_state()
        
        step = SimulationStep(
            step_number=step_num,
            timestamp=timestamp,
            action=f"Access page {page_num} - {'HIT' if is_hit else 'FAULT'}",
            state_before=state_before,
            state_after=self._get_current_state(),
            is_hit=is_hit,
            is_fault=is_fault
        )
        
        self.simulation_steps.append(step)
    
    def _get_current_state(self) -> Dict[str, Any]:
        """Get current state of all frames."""
        return {
            'frames': [
                {
                    'frame_id': frame.frame_id,
                    'page_number': frame.page_number,
                    'last_access_time': frame.last_access_time,
                    'reference_bit': frame.reference_bit,
                    'is_empty': frame.is_empty()
                }
                for frame in self.frames
            ],
            'clock_hand': self.clock_hand
        }