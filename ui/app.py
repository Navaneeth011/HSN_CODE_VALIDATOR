import streamlit as st
import pandas as pd
import sys
import os
import time
from typing import List, Dict, Any

# Add parent directory to path to import from agent and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.hsn_agent import HSNValidator
from utils.data_loader import HSNDataLoader

# Set page configuration
st.set_page_config(
    page_title="HSN Code Validator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-bottom: 20px;
    }
    .info-box {
        background-color: #000000;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #000000;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #4CAF50;
    }
    .error-box {
        background-color: #000000;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #F44336;
    }
    .partial-box {
        background-color: #000000;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #FFC107;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_hsn_validator(data_path: str) -> HSNValidator:
    """
    Load and cache the HSN Validator instance
    
    Args:
        data_path: Path to the HSN master data file
        
    Returns:
        HSNValidator: Initialized validator
    """
    with st.spinner("Loading HSN master data... This may take a moment."):
        validator = HSNValidator(data_path)
    return validator


def display_validation_result(result: Dict[str, Any]) -> None:
    """
    Display the validation result with appropriate styling
    
    Args:
        result: Validation result from the HSN validator
    """
    is_valid = result["is_valid"]
    description = result["description"]
    details = result["validation_details"]
    
    # Display result with appropriate styling
    if is_valid:
        st.markdown(f"""
        <div class="success-box">
            <h3>✅ Valid HSN Code</h3>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Check if there are parent codes (partial match)
        has_parent_codes = details["hierarchical_check"]["valid_parent_codes"]
        
        if has_parent_codes:
            st.markdown(f"""
            <div class="partial-box">
                <h3>⚠️ Invalid HSN Code (But Found Related Codes)</h3>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-box">
                <h3>❌ Invalid HSN Code</h3>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Show detailed validation information in an expandable section
    with st.expander("View Validation Details"):
        st.subheader("Format Check")
        st.write(f"Result: {'✅ Valid' if details['format_check']['valid'] else '❌ Invalid'}")
        st.write(f"Message: {details['format_check']['message']}")
        
        st.subheader("Length Check")
        st.write(f"Result: {'✅ Valid' if details['length_check']['valid'] else '❌ Invalid'}")
        st.write(f"Message: {details['length_check']['message']}")
        
        st.subheader("Existence Check")
        st.write(f"Result: {'✅ Valid' if details['existence_check']['valid'] else '❌ Invalid'}")
        st.write(f"Message: {details['existence_check']['message']}")
        
        st.subheader("Hierarchical Check")
        if details["hierarchical_check"]["valid_parent_codes"]:
            st.write("✅ Found valid parent codes:")
            for parent_code in details["hierarchical_check"]["valid_parent_codes"]:
                st.write(f"- {parent_code}")
        else:
            st.write("❌ No valid parent codes found")


def single_validation_ui(validator: HSNValidator) -> None:
    """
    UI section for validating a single HSN code
    
    Args:
        validator: HSN validator instance
    """
    st.markdown('<p class="sub-header">Single HSN Code Validation</p>', unsafe_allow_html=True)
    
    hsn_code = st.text_input("Enter HSN Code", placeholder="e.g., 01011010")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        validate_button = st.button("Validate", type="primary", use_container_width=True)
    
    if validate_button and hsn_code:
        with st.spinner("Validating HSN code..."):
            result = validator.validate_hsn_code(hsn_code)
        display_validation_result(result)
    elif validate_button and not hsn_code:
        st.error("Please enter an HSN code to validate")


def batch_validation_ui(validator: HSNValidator) -> None:
    """
    UI section for validating multiple HSN codes
    
    Args:
        validator: HSN validator instance
    """
    st.markdown('<p class="sub-header">Batch HSN Code Validation</p>', unsafe_allow_html=True)
    
    input_method = st.radio(
        "Select input method",
        ["Enter comma-separated HSN codes", "Upload a CSV/Excel file"]
    )
    
    results = None
    
    if input_method == "Enter comma-separated HSN codes":
        hsn_codes_text = st.text_area(
            "Enter HSN codes (comma or line separated)",
            placeholder="e.g., 01011010, 0101, 99999"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            validate_batch_button = st.button("Validate Batch", type="primary", use_container_width=True)
        
        if validate_batch_button and hsn_codes_text:
            # Split by either commas or newlines
            hsn_codes = [code.strip() for code in hsn_codes_text.replace('\n', ',').split(',') if code.strip()]
            
            if hsn_codes:
                with st.spinner(f"Validating {len(hsn_codes)} HSN codes..."):
                    results = validator.validate_multiple_hsn_codes(hsn_codes)
            else:
                st.error("Please enter at least one HSN code")
                
    else:  # Upload file option
        uploaded_file = st.file_uploader("Upload a CSV or Excel file with HSN codes", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                # Determine file type and read accordingly
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Look for a column containing HSN codes
                possible_columns = [col for col in df.columns if 'hsn' in col.lower() or 'code' in col.lower()]
                
                if possible_columns:
                    hsn_column = st.selectbox("Select the column containing HSN codes", possible_columns)
                else:
                    hsn_column = st.selectbox("Select the column containing HSN codes", df.columns)
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    process_file_button = st.button("Validate File", type="primary", use_container_width=True)
                
                if process_file_button:
                    hsn_codes = df[hsn_column].astype(str).tolist()
                    with st.spinner(f"Validating {len(hsn_codes)} HSN codes from file..."):
                        results = validator.validate_multiple_hsn_codes(hsn_codes)
                        
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    # Display batch results if available
    if results:
        st.markdown('<p class="sub-header">Validation Results</p>', unsafe_allow_html=True)
        
        # Calculate statistics
        total_codes = len(results)
        valid_codes = sum(1 for r in results if r["is_valid"])
        invalid_codes = total_codes - valid_codes
        
        # Create columns for statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total HSN Codes", total_codes)
        with col2:
            st.metric("Valid HSN Codes", valid_codes)
        with col3:
            st.metric("Invalid HSN Codes", invalid_codes)
        
        # Create a DataFrame for display
        result_data = []
        for i, result in enumerate(results):
            details = result["validation_details"]
            result_data.append({
                "HSN Code": details.get("hsn_code", f"Code {i+1}"),
                "Valid": "✅" if result["is_valid"] else "❌",
                "Description": result["description"],
                "Format Valid": "✅" if details["format_check"]["valid"] else "❌",
                "Exists in Master Data": "✅" if details["existence_check"]["valid"] else "❌",
                "Has Valid Parent Codes": "✅" if details["hierarchical_check"]["valid_parent_codes"] else "❌"
            })
        
        result_df = pd.DataFrame(result_data)
        st.dataframe(result_df, use_container_width=True)
        
        # Offer download option
        csv = result_df.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="hsn_validation_results.csv",
            mime="text/csv"
        )


def chatbot_ui(validator: HSNValidator) -> None:
    """
    UI section for chatbot interaction with the HSN validator agent
    
    Args:
        validator: HSN validator instance
    """
    st.markdown('<p class="sub-header">HSN Validator Chatbot</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        Chat with the AI assistant to validate HSN codes. You can ask questions like:
        <ul>
            <li>"Is 01011010 a valid HSN code?"</li>
            <li>"What does HSN code 0101 refer to?"</li>
            <li>"Validate these codes: 01, 0101, 99999"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your HSN Code Validation Assistant. How can I help you today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Get user input
    user_input = st.chat_input("Ask about HSN codes...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate response using the agent
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.write("Thinking...")
            
            # For a real implementation, this would use the ADK agent's run method
            # For simplicity, we'll mock a response based on HSN validation
            
            # Extract potential HSN codes from the message
            import re
            potential_codes = re.findall(r'\b\d{2,8}\b', user_input)
            
            if potential_codes:
                # Validate the extracted codes
                validation_results = validator.validate_multiple_hsn_codes(potential_codes)
                
                # Craft response based on validation results
                response = f"I've analyzed your message and found {len(potential_codes)} potential HSN code(s).\n\n"
                
                for code, result in zip(potential_codes, validation_results):
                    if result["is_valid"]:
                        response += f"✅ **{code}**: Valid - {result['description']}\n\n"
                    else:
                        response += f"❌ **{code}**: {result['description']}\n\n"
            
            else:
                # Generic response if no codes found
                response = """I don't see any specific HSN codes in your message. 

To validate an HSN code, please include the code in your message. HSN codes are typically 2-8 digits, like:
- 01 (LIVE ANIMALS)
- 0101 (LIVE HORSES, ASSES, MULES AND HINNIES)
- 01011010 (specific type under the LIVE HORSES category)

Feel free to ask me about specific HSN codes!"""
            
            # Simulate typing
            time.sleep(1)
            message_placeholder.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


def main() -> None:
    """Main function to run the Streamlit app"""
    st.markdown('<h1 class="main-header">HSN Code Validation System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        This application validates Harmonized System Nomenclature (HSN) codes against a master dataset.
        HSN codes are an internationally standardized system used to classify traded products.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("Settings")
    
    # In a real app, this would allow selecting different data files
    # For simplicity, we'll use a fixed path
    import os.path
    
    # Try different possible locations for the data file
    possible_paths = [
        "../data/HSN_SAC - MSTR.csv",  # Relative to UI folder
        "data/HSN_SAC - MSTR.csv",     # Relative to project root when running from UI folder
        "../HSN_SAC - MSTR.csv",       # Relative to UI folder (parent directory)
        "HSN_SAC - MSTR.csv",          # In current directory
    ]
    
    data_path = None
    for path in possible_paths:
        if os.path.exists(path):
            data_path = path
            st.sidebar.success(f"Found data file at: {path}")
            break
    
    if not data_path:
        st.error("Could not find the HSN data file. Please place it in one of these locations:")
        for path in possible_paths:
            st.write(f"- {os.path.abspath(path)}")
        st.stop()
    
    # Allow choosing different modes
    app_mode = st.sidebar.radio(
        "Choose Validation Mode",
        ["Single Validation", "Batch Validation", "Chat with Validator"]
    )
    
    # Load the validator (cached to prevent reloading)
    try:
        validator = load_hsn_validator(data_path)
        
        # Show dataset statistics in sidebar
        hsn_data = validator.data_loader.get_hsn_data()
        st.sidebar.subheader("Dataset Info")
        st.sidebar.info(f"""
        - Total HSN Codes: {len(hsn_data)}
        - Valid Code Lengths: {', '.join(map(str, validator.data_loader.get_unique_code_lengths()))}
        """)
        
        # Display different UIs based on selected mode
        if app_mode == "Single Validation":
            single_validation_ui(validator)
        elif app_mode == "Batch Validation":
            batch_validation_ui(validator)
        else:  # Chat mode
            chatbot_ui(validator)
            
    except Exception as e:
        st.error(f"Error loading HSN data: {str(e)}")
        st.info(f"""
        Make sure the HSN master data file exists at the expected location:
        - Current path: `{data_path}`
        - The file should be in CSV or Excel format
        - It should contain 'HSNCode' and 'Description' columns
        """)


if __name__ == "__main__":
    main()
