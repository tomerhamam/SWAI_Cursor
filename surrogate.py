#!/usr/bin/env python3
"""
Surrogate execution system for module placeholder behaviors.

This module provides a pluggable interface for executing module surrogates,
including static stubs and mock LLM-backed implementations.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Type


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Surrogate(ABC):
    """
    Abstract base class for module surrogate implementations.
    
    Surrogates provide placeholder behavior for modules that are not yet
    implemented or need to be simulated during development and testing.
    """
    
    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the surrogate behavior.
        
        Args:
            inputs: Dictionary of input data for the module
            
        Returns:
            Dictionary of output data from the module
        """
        pass
    
    def get_info(self) -> Dict[str, str]:
        """
        Get information about this surrogate.
        
        Returns:
            Dictionary with surrogate metadata
        """
        return {
            "type": self.__class__.__name__,
            "description": self.__doc__ or "No description available"
        }


class SurrogateRegistry:
    """Registry for managing surrogate implementations."""
    
    def __init__(self):
        self._surrogates: Dict[str, Type[Surrogate]] = {}
    
    def register(self, name: str, surrogate_class: Type[Surrogate]) -> None:
        """
        Register a surrogate implementation.
        
        Args:
            name: Name to register the surrogate under
            surrogate_class: Surrogate class to register
        """
        if not issubclass(surrogate_class, Surrogate):
            raise ValueError(f"Class {surrogate_class} must inherit from Surrogate")
        
        self._surrogates[name] = surrogate_class
        logger.info(f"Registered surrogate: {name}")
    
    def get(self, name: str) -> Optional[Type[Surrogate]]:
        """
        Get a surrogate class by name.
        
        Args:
            name: Name of the surrogate to retrieve
            
        Returns:
            Surrogate class or None if not found
        """
        return self._surrogates.get(name)
    
    def list_surrogates(self) -> Dict[str, str]:
        """
        List all registered surrogates.
        
        Returns:
            Dictionary mapping names to class names
        """
        return {name: cls.__name__ for name, cls in self._surrogates.items()}
    
    def create(self, name: str, **kwargs) -> Optional[Surrogate]:
        """
        Create an instance of a registered surrogate.
        
        Args:
            name: Name of the surrogate to create
            **kwargs: Arguments to pass to surrogate constructor
            
        Returns:
            Surrogate instance or None if not found
        """
        surrogate_class = self.get(name)
        if surrogate_class:
            return surrogate_class(**kwargs)
        return None


# Global registry instance
registry = SurrogateRegistry()


class StaticStubSurrogate(Surrogate):
    """
    Static stub surrogate that returns fixed output.
    
    Useful for testing and early integration when actual implementation
    is not yet available.
    """
    
    def __init__(self, output_data: Optional[Dict[str, Any]] = None):
        """
        Initialize static stub surrogate.
        
        Args:
            output_data: Fixed output to return. If None, returns default stub data.
        """
        self.output_data = output_data or {"result": "stub", "timestamp": "placeholder"}
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute static stub behavior.
        
        Args:
            inputs: Input data (logged but not used)
            
        Returns:
            Fixed output data
        """
        logger.info(f"StaticStubSurrogate received inputs: {inputs}")
        
        # Add some dynamic data
        result = self.output_data.copy()
        result["execution_time"] = datetime.now().isoformat()
        result["inputs_received"] = list(inputs.keys())
        
        logger.info(f"StaticStubSurrogate returning: {result}")
        return result


class MockLLMSurrogate(Surrogate):
    """
    Mock LLM surrogate that simulates LLM-backed behavior.
    
    Logs prompts to file and returns dummy responses for development
    and testing without requiring actual LLM API calls.
    """
    
    def __init__(self, prompt_template: str = "Process {inputs} and generate output", 
                 log_file: str = "build_logs/llm_prompts.log"):
        """
        Initialize mock LLM surrogate.
        
        Args:
            prompt_template: Template string for generating prompts
            log_file: Path to log file for storing prompts
        """
        self.prompt_template = prompt_template
        self.log_file = Path(log_file)
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute mock LLM behavior.
        
        Args:
            inputs: Input data to process
            
        Returns:
            Mock LLM response data
        """
        # Format the prompt
        try:
            prompt = self.prompt_template.format(inputs=json.dumps(inputs, indent=2))
        except Exception as e:
            logger.warning(f"Error formatting prompt template: {e}")
            prompt = f"Process inputs: {inputs}"
        
        # Log the prompt
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] MockLLM Prompt:\n{prompt}\n\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        logger.info(f"MockLLMSurrogate logged prompt to {self.log_file}")
        
        # Generate mock response
        response = {
            "response": f"<mock-llm-response-for-{len(inputs)}-inputs>",
            "prompt_logged": str(self.log_file),
            "execution_time": timestamp,
            "model": "mock-gpt-4",
            "tokens_used": len(str(inputs)) * 2  # Mock token count
        }
        
        logger.info(f"MockLLMSurrogate returning: {response}")
        return response


# Register default surrogates
registry.register("static_stub", StaticStubSurrogate)
registry.register("mock_llm", MockLLMSurrogate)


def main():
    """Demo/test function for surrogate system."""
    print("Surrogate System Demo")
    print("=" * 50)
    
    # List available surrogates
    print("\nAvailable surrogates:")
    for name, class_name in registry.list_surrogates().items():
        print(f"  {name}: {class_name}")
    
    # Test static stub
    print("\n1. Testing StaticStubSurrogate:")
    static_stub = registry.create("static_stub")
    if static_stub:
        test_inputs = {"sensor_data": [1, 2, 3], "timestamp": "2024-01-01T00:00:00"}
        result = static_stub.run(test_inputs)
        print(f"   Input: {test_inputs}")
        print(f"   Output: {result}")
    
    # Test mock LLM
    print("\n2. Testing MockLLMSurrogate:")
    mock_llm = registry.create("mock_llm", 
                               prompt_template="Analyze this sensor data: {inputs}")
    if mock_llm:
        test_inputs = {"lidar_points": 1000, "camera_frame": "frame_001"}
        result = mock_llm.run(test_inputs)
        print(f"   Input: {test_inputs}")
        print(f"   Output: {result}")
    
    print("\nDemo complete!")


if __name__ == "__main__":
    main() 