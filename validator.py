import pandas as pd
import re
from typing import Tuple, List, Dict, Optional
import time

class HSNValidator:
    """
    A class to validate HSN (Harmonized System Nomenclature) codes against a master dataset.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the HSN Validator with the master data file.
        
        Args:
            file_path: Path to the Excel/CSV file containing HSN codes and descriptions
        """
        # Load the master data (handling both Excel and CSV formats)
        self.load_master_data(file_path)
        
        # Extract valid HSN code lengths from the dataset
        self.valid_lengths = self._get_valid_lengths()
        
        # Format patterns for validation
        self.hsn_pattern = re.compile(r'^\d+$')  # HSN codes should be numeric

    def load_master_data(self, file_path: str) -> None:
        """
        Load the master data from the provided file path.
        
        Args:
            file_path: Path to the file containing HSN codes and descriptions
        """
        try:
            # Read the first few rows to inspect column structure
            if file_path.endswith('.xlsx'):
                sample = pd.read_excel(file_path, nrows=5)
            elif file_path.endswith('.csv'):
                # Try with different encoding options if needed
                try:
                    sample = pd.read_csv(file_path, nrows=5)
                except UnicodeDecodeError:
                    sample = pd.read_csv(file_path, nrows=5, encoding='latin1')
            else:
                raise ValueError("Unsupported file format. Please provide an Excel (.xlsx) or CSV (.csv) file.")
            
            # Check for single-column file with combined HSN code and description
            if len(sample.columns) == 1:
                # Read the entire file with a single column
                if file_path.endswith('.xlsx'):
                    data = pd.read_excel(file_path)
                else:
                    try:
                        data = pd.read_csv(file_path)
                    except UnicodeDecodeError:
                        data = pd.read_csv(file_path, encoding='latin1')
                
                # Rename the single column
                single_col_name = data.columns[0]
                data.rename(columns={single_col_name: 'CombinedData'}, inplace=True)
                
                # Extract HSN code and Description using a pattern
                # Assuming HSN codes are digits at the beginning of each row
                data['HSNCode'] = data['CombinedData'].str.extract(r'^(\d+)')
                data['Description'] = data['CombinedData'].str.replace(r'^\d+', '', regex=True).str.strip()
                
                # Drop the combined column
                data.drop('CombinedData', axis=1, inplace=True)
                
                self.master_data = data
            else:
                # Handle multi-column files
                if file_path.endswith('.xlsx'):
                    self.master_data = pd.read_excel(file_path)
                else:
                    try:
                        self.master_data = pd.read_csv(file_path)
                    except UnicodeDecodeError:
                        self.master_data = pd.read_csv(file_path, encoding='latin1')
                
                # Try to identify HSN code and description columns
                hsn_col = None
                desc_col = None
                
                # Look for column names containing keywords
                for col in self.master_data.columns:
                    col_lower = str(col).lower()
                    if any(keyword in col_lower for keyword in ['hsn', 'code', 'hsncode']):
                        hsn_col = col
                    elif any(keyword in col_lower for keyword in ['desc', 'description']):
                        desc_col = col
                
                # If can't find by name, try to infer from content (first column is likely HSN)
                if hsn_col is None and len(self.master_data.columns) >= 1:
                    hsn_col = self.master_data.columns[0]
                
                if desc_col is None and len(self.master_data.columns) >= 2:
                    desc_col = self.master_data.columns[1]
                
                # Rename columns to standard names
                column_mapping = {}
                if hsn_col:
                    column_mapping[hsn_col] = 'HSNCode'
                if desc_col:
                    column_mapping[desc_col] = 'Description'
                
                if column_mapping:
                    self.master_data.rename(columns=column_mapping, inplace=True)
            
            # Ensure required columns exist
            required_columns = ['HSNCode', 'Description']
            missing_columns = [col for col in required_columns if col not in self.master_data.columns]
            
            if missing_columns:
                # Try one more approach - maybe there's no header row
                if file_path.endswith('.xlsx'):
                    self.master_data = pd.read_excel(file_path, header=None)
                else:
                    try:
                        self.master_data = pd.read_csv(file_path, header=None)
                    except UnicodeDecodeError:
                        self.master_data = pd.read_csv(file_path, header=None, encoding='latin1')
                
                # Assign column names
                if len(self.master_data.columns) >= 2:
                    self.master_data.columns = ['HSNCode', 'Description'] + [f'Column{i+3}' for i in range(len(self.master_data.columns)-2)]
                else:
                    # Still having issues, create a description column from the first column
                    self.master_data.columns = ['CombinedData']
                    self.master_data['HSNCode'] = self.master_data['CombinedData'].str.extract(r'^(\d+)')
                    self.master_data['Description'] = self.master_data['CombinedData'].str.replace(r'^\d+', '', regex=True).str.strip()
                    self.master_data.drop('CombinedData', axis=1, inplace=True)
            
            # Remove rows with missing HSN codes
            self.master_data = self.master_data.dropna(subset=['HSNCode'])
            
            # Convert HSN codes to string format for consistent handling
            self.master_data['HSNCode'] = self.master_data['HSNCode'].astype(str)
            
            # Remove any whitespace in HSN codes
            self.master_data['HSNCode'] = self.master_data['HSNCode'].str.strip()
            
            # Remove any non-digit characters from HSN codes
            self.master_data['HSNCode'] = self.master_data['HSNCode'].str.replace(r'\D', '', regex=True)
            
            # Create a set of valid HSN codes for faster lookup
            self.valid_hsn_codes = set(self.master_data['HSNCode'])
            
            print(f"Successfully loaded {len(self.master_data)} HSN codes.")
            
        except Exception as e:
            print(f"Error loading master data: {str(e)}")
            # Initialize with empty DataFrame to avoid errors
            self.master_data = pd.DataFrame(columns=['HSNCode', 'Description'])
            self.valid_hsn_codes = set()
            
    def _get_valid_lengths(self) -> List[int]:
        """
        Extract the valid lengths of HSN codes from the master data.
        
        Returns:
            A list of valid HSN code lengths
        """
        if self.master_data.empty:
            return []
        
        lengths = self.master_data['HSNCode'].str.len().unique()
        return sorted(lengths)
    
    def format_validation(self, hsn_code: str) -> Tuple[bool, str]:
        """
        Validate if the HSN code follows the expected format.
        
        Args:
            hsn_code: The HSN code to validate
            
        Returns:
            A tuple containing (is_valid, reason)
        """
        # Check if the code is empty
        if not hsn_code:
            return False, "HSN code cannot be empty"
        
        # Check if the code is numeric
        if not self.hsn_pattern.match(hsn_code):
            return False, "HSN code must contain only digits"
            
        # Check if the length is valid based on the master data
        if self.valid_lengths and len(hsn_code) not in self.valid_lengths:
            valid_lengths_str = ", ".join(map(str, self.valid_lengths))
            return False, f"Invalid length. HSN codes should be {valid_lengths_str} digits long."
            
        return True, "Format is valid"
    
    def existence_validation(self, hsn_code: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate if the HSN code exists in the master data.
        
        Args:
            hsn_code: The HSN code to validate
            
        Returns:
            A tuple containing (exists, message, description)
        """
        # Simulate a slight delay to make the validation feel more realistic
        time.sleep(0.1)
        
        if hsn_code in self.valid_hsn_codes:
            description = self.master_data.loc[self.master_data['HSNCode'] == hsn_code, 'Description'].iloc[0]
            return True, "HSN code exists in master data", description
        
        return False, "HSN code not found in master data", None
    
    def hierarchical_validation(self, hsn_code: str) -> List[Dict[str, str]]:
        """
        Perform hierarchical validation by checking if parent codes exist.
        
        Args:
            hsn_code: The HSN code to validate
            
        Returns:
            A list of dictionaries containing parent code information
        """
        result = []
        
        # Generate parent codes
        for i in range(2, len(hsn_code), 2):
            parent_code = hsn_code[:i]
            
            # Check if parent code exists
            exists = parent_code in self.valid_hsn_codes
            
            parent_info = {
                "parent_code": parent_code,
                "exists": exists
            }
            
            if exists:
                description = self.master_data.loc[self.master_data['HSNCode'] == parent_code, 'Description'].iloc[0]
                parent_info["description"] = description
            
            result.append(parent_info)
        
        return result
    
    def validate(self, hsn_code: str) -> Dict:
        """
        Validate an HSN code.
        
        Args:
            hsn_code: The HSN code to validate
            
        Returns:
            A dictionary containing validation results
        """
        # Clean input
        hsn_code = hsn_code.strip()
        
        result = {
            "hsn_code": hsn_code,
            "is_valid": False,
            "format_valid": False,
            "exists": False,
            "messages": []
        }
        
        # Format validation
        format_valid, format_message = self.format_validation(hsn_code)
        result["format_valid"] = format_valid
        result["messages"].append(format_message)
        
        # If format is invalid, return early
        if not format_valid:
            return result
        
        # Existence validation
        exists, existence_message, description = self.existence_validation(hsn_code)
        result["exists"] = exists
        result["messages"].append(existence_message)
        
        if exists:
            result["description"] = description
            result["is_valid"] = True
        
        # Hierarchical validation (only for longer codes)
        if len(hsn_code) > 2:
            result["hierarchy"] = self.hierarchical_validation(hsn_code)
        
        return result
    
    def validate_multiple(self, hsn_codes: List[str]) -> List[Dict]:
        """
        Validate multiple HSN codes.
        
        Args:
            hsn_codes: List of HSN codes to validate
            
        Returns:
            A list of validation results
        """
        return [self.validate(code) for code in hsn_codes]