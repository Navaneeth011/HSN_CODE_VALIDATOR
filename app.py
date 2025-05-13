import streamlit as st
import pandas as pd
import time
from validator import HSNValidator
import io
import os

# Set page configuration
st.set_page_config(
    page_title="HSN Code Validator",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'validator' not in st.session_state:
    st.session_state.validator = None

if 'results' not in st.session_state:
    st.session_state.results = []

if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False

def display_result(result):
    """Display a single HSN code validation result with appropriate styling"""
    hsn_code = result["hsn_code"]
    is_valid = result["is_valid"]
    
    if is_valid:
        st.success(f"✅ HSN Code: {hsn_code} - VALID")
        st.write(f"**Description:** {result.get('description', 'N/A')}")
    else:
        st.error(f"❌ HSN Code: {hsn_code} - INVALID")
        
    # Display the specific validation messages
    for msg in result["messages"]:
        st.write(f"- {msg}")
    
    # Display hierarchical information if available
    if "hierarchy" in result and result["hierarchy"]:
        st.write("**Hierarchical Information:**")
        for parent in result["hierarchy"]:
            if parent["exists"]:
                st.write(f"- Parent code {parent['parent_code']}: ✅ Found - {parent.get('description', 'N/A')}")
            else:
                st.write(f"- Parent code {parent['parent_code']}: ❌ Not found")
    
    st.write("---")

def main():
    """Main function for the Streamlit application"""
    st.title("HSN Code Validation Agent")
    st.write("Upload HSN master data and validate HSN codes against the dataset.")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Single Validation", "Bulk Validation", "About HSN Codes"])
    
    # File uploader for master data
    with st.sidebar:
        st.header("Upload Master Data")
        uploaded_file = st.file_uploader("Choose HSN master data file (Excel or CSV)", type=['xlsx', 'csv'])
        
        if uploaded_file:
            try:
                # Display a message about processing
                with st.spinner("Loading and processing master data..."):
                    # Save the uploaded file to a temporary file
                    temp_file_path = "temp_hsn_data.csv" if uploaded_file.name.endswith('.csv') else "temp_hsn_data.xlsx"
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Initialize validator
                    st.session_state.validator = HSNValidator(temp_file_path)
                    
                    if st.session_state.validator.master_data.empty:
                        st.error("Failed to load or process the master data file. Please check the file format.")
                        st.session_state.file_uploaded = False
                    else:
                        # Display success message with file details
                        st.success(f"✅ Master data loaded successfully!")
                        st.write(f"Total HSN codes: {len(st.session_state.validator.master_data)}")
                        
                        # Display valid HSN code lengths
                        valid_lengths = st.session_state.validator.valid_lengths
                        if valid_lengths:
                            st.write(f"Valid HSN code lengths: {', '.join(map(str, valid_lengths))}")
                        
                        st.session_state.file_uploaded = True
                        
                        # Show sample data
                        st.write("Sample data:")
                        st.dataframe(st.session_state.validator.master_data.head(5))
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                st.session_state.file_uploaded = False
        
        # Display warning if no file is uploaded
        if not st.session_state.file_uploaded:
            st.warning("Please upload an HSN master data file to start validation.")
    
    # Tab 1: Single Validation
    with tab1:
        st.header("Validate HSN Code")
        
        if st.session_state.file_uploaded:
            hsn_code = st.text_input("Enter HSN Code")
            
            if st.button("Validate", key="single_validate"):
                if hsn_code:
                    with st.spinner("Validating..."):
                        result = st.session_state.validator.validate(hsn_code)
                        display_result(result)
                else:
                    st.warning("Please enter an HSN code to validate.")
        else:
            st.info("Upload a master data file from the sidebar to start validation.")
    
    # Tab 2: Bulk Validation
    with tab2:
        st.header("Bulk HSN Code Validation")
        
        if st.session_state.file_uploaded:
            st.write("Enter multiple HSN codes (one per line) or upload a file:")
            
            # Text area for multiple codes
            bulk_codes = st.text_area("Enter HSN codes (one per line)")
            
            # File uploader for bulk validation
            bulk_file = st.file_uploader("Or upload a file with HSN codes", type=['csv', 'txt', 'xlsx'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                validate_button = st.button("Validate Codes", key="bulk_validate")
            
            with col2:
                download_results = st.button("Download Results", disabled=not st.session_state.results, key="download_results")
            
            if validate_button:
                hsn_codes = []
                
                # Process codes from text area
                if bulk_codes:
                    hsn_codes.extend([code.strip() for code in bulk_codes.split('\n') if code.strip()])
                
                # Process codes from file
                if bulk_file:
                    try:
                        if bulk_file.name.endswith('.csv') or bulk_file.name.endswith('.txt'):
                            df = pd.read_csv(bulk_file, header=None)
                            hsn_codes.extend(df[0].astype(str).tolist())
                        elif bulk_file.name.endswith('.xlsx'):
                            df = pd.read_excel(bulk_file, header=None)
                            hsn_codes.extend(df[0].astype(str).tolist())
                    except Exception as e:
                        st.error(f"Error reading file: {str(e)}")
                
                # Remove duplicates and empty values
                hsn_codes = list(set([code for code in hsn_codes if code]))
                
                if hsn_codes:
                    with st.spinner(f"Validating {len(hsn_codes)} HSN codes..."):
                        # Process in batches to show progress
                        results = []
                        progress_bar = st.progress(0)
                        
                        for i, code in enumerate(hsn_codes):
                            result = st.session_state.validator.validate(code)
                            results.append(result)
                            # Update progress
                            progress = (i + 1) / len(hsn_codes)
                            progress_bar.progress(progress)
                        
                        st.session_state.results = results
                        
                        # Display summary
                        valid_count = sum(1 for r in results if r["is_valid"])
                        invalid_count = len(results) - valid_count
                        
                        st.write("### Validation Summary")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Codes", len(results))
                        col2.metric("Valid Codes", valid_count)
                        col3.metric("Invalid Codes", invalid_count)
                        
                        # Convert results to DataFrame for display
                        results_df = pd.DataFrame([{
                            'HSN Code': r['hsn_code'],
                            'Valid': '✅' if r['is_valid'] else '❌',
                            'Format Valid': '✅' if r['format_valid'] else '❌',
                            'Exists in Database': '✅' if r['exists'] else '❌',
                            'Description': r.get('description', 'N/A'),
                            'Messages': '; '.join(r['messages'])
                        } for r in results])
                        
                        st.write("### Results")
                        st.dataframe(results_df)
                else:
                    st.warning("Please enter at least one HSN code to validate.")
            
            if download_results and st.session_state.results:
                # Convert results to DataFrame for download
                results_df = pd.DataFrame([{
                    'HSN Code': r['hsn_code'],
                    'Valid': 'Yes' if r['is_valid'] else 'No',
                    'Format Valid': 'Yes' if r['format_valid'] else 'No',
                    'Exists in Database': 'Yes' if r['exists'] else 'No',
                    'Description': r.get('description', 'N/A'),
                    'Messages': '; '.join(r['messages'])
                } for r in st.session_state.results])
                
                # Convert DataFrame to CSV
                csv = results_df.to_csv(index=False)
                
                # Create download button
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="hsn_validation_results.csv",
                    mime="text/csv",
                )
        else:
            st.info("Upload a master data file from the sidebar to start bulk validation.")
    
    # Tab 3: About HSN Codes
    with tab3:
        st.header("About HSN Codes")
        st.write("""
        ### What are HSN Codes?
        
        **Harmonized System Nomenclature (HSN)** codes are an internationally standardized system of names and numbers
        used to classify traded products. Developed by the World Customs Organization (WCO), this system is used
        by customs authorities around the world for the uniform classification of goods.
        
        ### Structure of HSN Codes:
        
        HSN codes typically vary in length from 2 to 8 digits, with each level providing more specific classification:
        
        - **First 2 digits (XX)**: Identify the chapter
        - **First 4 digits (XXXX)**: Identify the heading within a chapter
        - **First 6 digits (XXXXXX)**: Internationally standardized subheading
        - **8 digits (XXXXXXXX)**: Country-specific detailed classification
        
        ### Example:
        
        - **01**: Live animals (Chapter)
        - **0101**: Live horses, asses, mules and hinnies (Heading)
        - **010121**: Pure-bred breeding animals (Subheading)
        - **01012100**: Pure-bred breeding animals (Detailed classification)
        
        ### Importance:
        
        HSN codes are crucial for:
        - International trade documentation
        - Determining applicable customs duties and taxes
        - Collection of trade statistics
        - Application of trade regulations
        """)

if __name__ == "__main__":
    main()
    
    # Cleanup temporary files
    for temp_file in ["temp_hsn_data.csv", "temp_hsn_data.xlsx"]:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass