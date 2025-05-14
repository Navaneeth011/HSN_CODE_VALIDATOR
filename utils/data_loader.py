import pandas as pd
from typing import List, Dict, Tuple, Union

class HSNDataLoader:
    """
    Utility class to load and process HSN code master data
    """
    def __init__(self, file_path: str):
        """
        Initialize the data loader with the path to the HSN master data file
        
        Args:
            file_path: Path to the CSV/Excel file containing HSN codes
        """
        self.file_path = file_path
        self.hsn_data = None
        self.load_data()
        
    def load_data(self) -> None:
        """
        Load the HSN master data from the file
        """
        try:
            # Check file extension to determine loading method
            if self.file_path.endswith('.xlsx'):
                self.hsn_data = pd.read_excel(self.file_path)
            elif self.file_path.endswith('.csv'):
                self.hsn_data = pd.read_csv(self.file_path)
            else:
                raise ValueError("Unsupported file format. Please provide an Excel (.xlsx) or CSV (.csv) file.")
            
            print(f"Loaded file with columns: {self.hsn_data.columns.tolist()}")
            
            # Handle the case where we have a single column with combined data
            if len(self.hsn_data.columns) == 1 and 'HSNCodeDescription' in self.hsn_data.columns:
                # Extract HSN Code and Description from the combined column
                self.hsn_data[['HSNCode', 'Description']] = self.hsn_data['HSNCodeDescription'].str.extract(r'(\d+)(.*)')
            
            # Handle the case where we have just the raw text split by space
            elif len(self.hsn_data.columns) == 1:
                column_name = self.hsn_data.columns[0]
                # Extract HSN Code and Description from the combined column
                self.hsn_data[['HSNCode', 'Description']] = self.hsn_data[column_name].str.extract(r'(\d+)(.*)')
            
            # Alternatively, try to find columns that might contain HSN code and description
            else:
                hsn_col = None
                desc_col = None
                
                # Look for likely column names
                for col in self.hsn_data.columns:
                    col_lower = col.lower()
                    if 'hsn' in col_lower or 'code' in col_lower or col_lower.startswith('code'):
                        hsn_col = col
                    elif 'desc' in col_lower or 'name' in col_lower or 'product' in col_lower:
                        desc_col = col
                
                if hsn_col and desc_col:
                    # Rename to our expected column names
                    self.hsn_data = self.hsn_data.rename(columns={hsn_col: 'HSNCode', desc_col: 'Description'})
                
            # If we still don't have our expected columns, make a best effort with what we have
            if 'HSNCode' not in self.hsn_data.columns:
                # If we still don't have HSNCode column, take the first column as HSNCode
                if len(self.hsn_data.columns) >= 1:
                    self.hsn_data = self.hsn_data.rename(columns={self.hsn_data.columns[0]: 'HSNCode'})
            
            if 'Description' not in self.hsn_data.columns:
                # If we still don't have Description column, take the second column as Description
                # or create an empty Description column if there isn't a second column
                if len(self.hsn_data.columns) >= 2:
                    self.hsn_data = self.hsn_data.rename(columns={self.hsn_data.columns[1]: 'Description'})
                else:
                    self.hsn_data['Description'] = 'No description available'
            
            # Ensure both columns exist
            if 'HSNCode' not in self.hsn_data.columns or 'Description' not in self.hsn_data.columns:
                raise ValueError(f"Required columns 'HSNCode' and 'Description' not found in the data. Available columns: {self.hsn_data.columns.tolist()}")
                
            # Clean the data
            self.hsn_data['HSNCode'] = self.hsn_data['HSNCode'].astype(str).str.strip()
            self.hsn_data['Description'] = self.hsn_data['Description'].astype(str).str.strip()
            
            # Create a dictionary for fast lookup
            self.hsn_dict = dict(zip(self.hsn_data['HSNCode'], self.hsn_data['Description']))
            
            print(f"Successfully loaded {len(self.hsn_data)} HSN codes")
            
        except Exception as e:
            print(f"Error loading HSN data: {str(e)}")
            raise
    
    def get_hsn_dict(self) -> Dict[str, str]:
        """
        Get the HSN code dictionary
        
        Returns:
            Dict: Dictionary mapping HSN codes to descriptions
        """
        return self.hsn_dict
    
    def get_unique_code_lengths(self) -> List[int]:
        """
        Get a list of all unique HSN code lengths in the dataset
        
        Returns:
            List[int]: List of unique HSN code lengths
        """
        return sorted(list(set(len(code) for code in self.hsn_dict.keys())))
    
    def get_hsn_data(self) -> pd.DataFrame:
        """
        Get the HSN data as a pandas DataFrame
        
        Returns:
            DataFrame: HSN data
        """
        return self.hsn_data
