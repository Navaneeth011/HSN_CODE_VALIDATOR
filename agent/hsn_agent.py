from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from typing import List, Dict, Any, Optional, Union
import re

from utils.data_loader import HSNDataLoader

class HSNValidationTool(BaseTool):
    """Tool for validating HSN codes against a master dataset"""
    
    def __init__(self, hsn_data_loader: HSNDataLoader):
        """
        Initialize the HSN Validation Tool
        
        Args:
            hsn_data_loader: Instance of HSNDataLoader containing the master data
        """
        super().__init__(
            name="hsn_code_validator",
            description="Validates HSN codes against a master dataset and provides descriptions",
            
        )
        self.hsn_data = hsn_data_loader
        self.hsn_dict = hsn_data_loader.get_hsn_dict()
        self.valid_lengths = hsn_data_loader.get_unique_code_lengths()
    
    def _execute(self, hsn_code: str) -> Dict[str, Any]:
        """
        Execute the HSN code validation
        
        Args:
            hsn_code: The HSN code to validate
            
        Returns:
            Dict: Validation result containing validity, description, and details
        """
        hsn_code = str(hsn_code).strip()
        validation_details = {
            "format_check": self._check_format(hsn_code),
            "length_check": self._check_length(hsn_code),
            "existence_check": self._check_existence(hsn_code),
            "hierarchical_check": self._check_hierarchical(hsn_code)
        }
        
        # Determine overall validity
        is_valid = validation_details["format_check"]["valid"] and \
                   validation_details["existence_check"]["valid"]
        
        if is_valid:
            description = self.hsn_dict[hsn_code]
            result_message = f"Valid HSN code: {description}"
        else:
            # Compile error reasons
            errors = []
            if not validation_details["format_check"]["valid"]:
                errors.append(validation_details["format_check"]["message"])
            if not validation_details["existence_check"]["valid"]:
                errors.append(validation_details["existence_check"]["message"])
            
            result_message = f"Invalid HSN code: {', '.join(errors)}"
            
            # Check if any parent codes exist (for partial validity)
            if validation_details["hierarchical_check"]["valid_parent_codes"]:
                parent_info = []
                for parent in validation_details["hierarchical_check"]["valid_parent_codes"]:
                    parent_info.append(f"{parent}: {self.hsn_dict[parent]}")
                    
                result_message += f"\nRelated parent codes found: {'; '.join(parent_info)}"
        
        return {
            "is_valid": is_valid,
            "description": result_message,
            "validation_details": validation_details
        }
    
    def _check_format(self, hsn_code: str) -> Dict[str, Any]:
        """Check if the HSN code has the correct format (numbers only)"""
        if not hsn_code:
            return {"valid": False, "message": "HSN code cannot be empty"}
        
        if not re.match(r'^\d+$', hsn_code):
            return {"valid": False, "message": "HSN code must contain only digits"}
            
        return {"valid": True, "message": "Format is valid"}
    
    def _check_length(self, hsn_code: str) -> Dict[str, Any]:
        """Check if the HSN code has an acceptable length"""
        code_length = len(hsn_code)
        
        if code_length in self.valid_lengths:
            return {"valid": True, "message": "Length is valid"}
        else:
            valid_lengths_str = ", ".join(map(str, self.valid_lengths))
            return {
                "valid": False, 
                "message": f"Invalid length. Expected lengths: {valid_lengths_str}"
            }
    
    def _check_existence(self, hsn_code: str) -> Dict[str, Any]:
        """Check if the HSN code exists in the master data"""
        if hsn_code in self.hsn_dict:
            return {"valid": True, "message": "Code exists in master data"}
        else:
            return {"valid": False, "message": "Code not found in master data"}
    
    def _check_hierarchical(self, hsn_code: str) -> Dict[str, Any]:
        """Check if parent codes of the given HSN code exist in the master data"""
        valid_parent_codes = []
        
        # Generate all possible parent codes
        length = len(hsn_code)
        for i in range(2, length, 2):  # Check at 2, 4, 6, etc. digits
            parent_code = hsn_code[:i]
            if parent_code in self.hsn_dict:
                valid_parent_codes.append(parent_code)
        
        return {
            "valid": len(valid_parent_codes) > 0,
            "valid_parent_codes": valid_parent_codes,
            "message": f"Found {len(valid_parent_codes)} valid parent codes"
        }


class HSNValidator:
    """HSN Code Validator class using Google ADK"""
    
    def __init__(self, data_path: str):
        """
        Initialize the HSN Validator with data path
        
        Args:
            data_path: Path to the HSN master data file
        """
        # Load HSN data
        self.data_loader = HSNDataLoader(data_path)
        
        # Create HSN validation tool
        self.validation_tool = HSNValidationTool(self.data_loader)
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _create_agent(self) -> LlmAgent:
        """
        Create the HSN validation agent using Google ADK
        
        Returns:
            LlmAgent: Configured agent for HSN validation
        """
        agent = LlmAgent(
            model="gemini-2.0-flash",  # Or other appropriate Gemini model
            name="hsn_validator",
            description="An agent that validates HSN (Harmonized System Nomenclature) codes against a master dataset",
            instruction="""You are a specialized HSN (Harmonized System Nomenclature) code validation assistant.
            
Your primary function is to validate HSN codes provided by users against a master dataset.

When a user provides an HSN code:
1. Validate if the format is correct (digits only)
2. Check if the code exists in the master dataset
3. If invalid, check for valid parent codes in the hierarchy
4. Provide clear explanations about the validity status

For valid codes, provide the corresponding description from the master data.
For invalid codes, explain why they are invalid and suggest any relevant parent codes if they exist.

Be precise, informative, and always explain the validation result in a clear manner.
            """,
            tools=[self.validation_tool]
        )
        
        return agent
    
    def validate_hsn_code(self, hsn_code: str) -> Dict[str, Any]:
        """
        Validate a single HSN code directly using the validation tool
        
        Args:
            hsn_code: HSN code to validate
            
        Returns:
            Dict: Validation result
        """
        return self.validation_tool._execute(hsn_code)
    
    def validate_multiple_hsn_codes(self, hsn_codes: List[str]) -> List[Dict[str, Any]]:
        """
        Validate multiple HSN codes
        
        Args:
            hsn_codes: List of HSN codes to validate
            
        Returns:
            List[Dict]: List of validation results for each code
        """
        results = []
        for code in hsn_codes:
            results.append(self.validate_hsn_code(code))
        return results
    
    def get_agent(self) -> LlmAgent:
        """
        Get the configured ADK agent
        
        Returns:
            LlmAgent: The HSN validation agent
        """
        return self.agent
