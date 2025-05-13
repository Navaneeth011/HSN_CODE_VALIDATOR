import streamlit as st
import pandas as pd
import time
import altair as alt
from validator import HSNValidator
import io
import os

# Set page configuration
st.set_page_config(
    page_title="HSN Code Validator",
    page_icon="🔍",
    layout="wide"
)

# Load custom CSS
def load_css():
    st.markdown("""
    <style>
        /* Main app styling */
        .main-container {
            padding: 2rem;
            border-radius: 10px;
        }
        
        /* Card styling */
        .card {
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Custom header styling */
        .custom-header {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(90deg, #4F46E5, #7C3AED);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }
        
        /* Status indicators */
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .status-valid {
            background-color: #10B981;
        }
        
        .status-invalid {
            background-color: #EF4444;
        }
        
        /* Custom button styling */
        .stButton>button {
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            border: none;
            transition: all 0.3s;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            padding: 1rem;
            font-size: 0.8rem;
            margin-top: 2rem;
            opacity: 0.8;
        }
        
        /* Dark mode toggle */
        .toggle-container {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            margin-bottom: 1rem;
        }
        
        /* Custom metrics display */
        .metric-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .metric-card {
            flex: 1;
            text-align: center;
            padding: 1rem;
            border-radius: 10px;
            margin: 0 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.7;
        }
        
        /* Animation for loading */
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .pulse-animation {
            animation: pulse 1.5s infinite ease-in-out;
        }
        
        /* Light mode */
        .light-mode {
            background-color: #F9FAFB;
            color: #1F2937;
        }
        
        .light-mode .card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
        }
        
        .light-mode .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
        }
        
        /* Dark mode */
        .dark-mode {
            background-color: #1F2937;
            color: #F9FAFB;
        }
        
        .dark-mode .card {
            background-color: #374151;
            border: 1px solid #4B5563;
        }
        
        .dark-mode .metric-card {
            background-color: #374151;
            border: 1px solid #4B5563;
        }
        
        /* Chart legend styling */
        .chart-legend {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Glowing effect for success messages */
        .success-glow {
            box-shadow: 0 0 10px #10B981;
            animation: glow 2s infinite alternate;
        }
        
        @keyframes glow {
            from {
                box-shadow: 0 0 5px #10B981;
            }
            to {
                box-shadow: 0 0 20px #10B981;
            }
        }
        
        /* File upload styling */
        .upload-container {
            border: 2px dashed #CBD5E1;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .upload-container:hover {
            border-color: #3B82F6;
        }
        
        /* Banner styling */
        .banner {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .banner-icon {
            font-size: 2rem;
        }
        
        .banner-success {
            background-color: rgba(16, 185, 129, 0.2);
            border: 1px solid #10B981;
        }
        
        .banner-warning {
            background-color: rgba(245, 158, 11, 0.2);
            border: 1px solid #F59E0B;
        }
        
        .banner-error {
            background-color: rgba(239, 68, 68, 0.2);
            border: 1px solid #EF4444;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'validator' not in st.session_state:
    st.session_state.validator = None

if 'results' not in st.session_state:
    st.session_state.results = []

if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False

if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # Default theme

def display_result(result):
    """Display a single HSN code validation result with appropriate styling"""
    hsn_code = result["hsn_code"]
    is_valid = result["is_valid"]
    
    # Create card with dynamic styling based on validation result
    card_class = "success-glow" if is_valid else ""
    
    st.markdown(f"""
    <div class="card {card_class}">
        <h3>
            <span class="status-indicator {'status-valid' if is_valid else 'status-invalid'}"></span>
            HSN Code: {hsn_code} - {'VALID' if is_valid else 'INVALID'}
        </h3>
    """, unsafe_allow_html=True)
    
    # Display description if available
    if is_valid:
        st.markdown(f"**Description:** {result.get('description', 'N/A')}")
    
    # Display the specific validation messages
    st.write("#### Validation Messages:")
    for msg in result["messages"]:
        st.markdown(f"- {msg}")
    
    # Display hierarchical information if available
    if "hierarchy" in result and result["hierarchy"]:
        st.write("#### Hierarchical Information:")
        for parent in result["hierarchy"]:
            icon = "✅" if parent["exists"] else "❌"
            if parent["exists"]:
                st.markdown(f"- Parent code {parent['parent_code']}: {icon} Found - {parent.get('description', 'N/A')}")
            else:
                st.markdown(f"- Parent code {parent['parent_code']}: {icon} Not found")
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_chart(results_df):
    """Create a visualization of validation results"""
    # Count the number of valid and invalid codes
    status_counts = results_df['Valid'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    # Replace Unicode symbols with text for better chart labels
    status_counts['Status'] = status_counts['Status'].replace('✅', 'Valid').replace('❌', 'Invalid')
    
    # Create a color scale
    color_scale = alt.Scale(domain=['Valid', 'Invalid'], range=['#10B981', '#EF4444'])
    
    # Create a bar chart
    chart = alt.Chart(status_counts).mark_bar().encode(
        x=alt.X('Status:N', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Count:Q', title='Number of HSN Codes'),
        color=alt.Color('Status:N', scale=color_scale),
        tooltip=['Status', 'Count']
    ).properties(
        title='HSN Code Validation Results',
        width=300,
        height=300
    )
    
    return chart

def create_format_chart(results_df):
    """Create a visualization of format validation results"""
    # Count the number of valid and invalid format codes
    format_counts = results_df['Format Valid'].value_counts().reset_index()
    format_counts.columns = ['Status', 'Count']
    
    # Replace Unicode symbols with text for better chart labels
    format_counts['Status'] = format_counts['Status'].replace('✅', 'Valid Format').replace('❌', 'Invalid Format')
    
    # Create a color scale
    color_scale = alt.Scale(domain=['Valid Format', 'Invalid Format'], range=['#10B981', '#EF4444'])
    
    # Create a bar chart
    chart = alt.Chart(format_counts).mark_bar().encode(
        x=alt.X('Status:N', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Count:Q', title='Number of HSN Codes'),
        color=alt.Color('Status:N', scale=color_scale),
        tooltip=['Status', 'Count']
    ).properties(
        title='HSN Code Format Validation',
        width=300,
        height=300
    )
    
    return chart

def create_hierarchical_chart(results):
    """Create a visualization of hierarchical validation"""
    # Extract hierarchical information
    hierarchical_data = []
    
    for result in results:
        if "hierarchy" in result and result["hierarchy"]:
            for parent in result["hierarchy"]:
                hierarchical_data.append({
                    'HSN Code': result['hsn_code'],
                    'Parent Code': parent['parent_code'],
                    'Exists': 'Yes' if parent['exists'] else 'No'
                })
    
    if not hierarchical_data:
        return None
    
    # Convert to DataFrame
    hierarchical_df = pd.DataFrame(hierarchical_data)
    
    # Count existence by parent code
    parent_counts = hierarchical_df.groupby(['Parent Code', 'Exists']).size().reset_index(name='Count')
    
    # Create a color scale
    color_scale = alt.Scale(domain=['Yes', 'No'], range=['#10B981', '#EF4444'])
    
    # Create a stacked bar chart
    chart = alt.Chart(parent_counts).mark_bar().encode(
        x=alt.X('Parent Code:N', sort='-y', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Count:Q', title='Number of Child HSN Codes'),
        color=alt.Color('Exists:N', scale=color_scale),
        tooltip=['Parent Code', 'Exists', 'Count']
    ).properties(
        title='Parent Code Existence in Validation',
        width=500,
        height=300
    )
    
    return chart

def toggle_theme():
    """Toggle between light and dark mode"""
    if st.session_state.theme == 'dark':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'dark'

def main():
    """Main function for the Streamlit application"""
    # Load custom CSS
    load_css()
    
    # Theme toggle
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<h1 class="custom-header">HSN Code Validation System</h1>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
        theme_toggle = st.button("🔃 Refresh", key="theme_toggle", on_click=toggle_theme)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply theme class to the main container
    st.markdown(f"""
    <div class="{st.session_state.theme}-mode main-container">
    """, unsafe_allow_html=True)
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Single Validation", "📑 Bulk Validation", "ℹ️ About HSN Codes"])
    
    # Set up sidebar
    with st.sidebar:
        st.markdown('<h2>📂 Master Data</h2>', unsafe_allow_html=True)
        
        # Create a custom upload container
        st.markdown("""
        <div class="upload-container">
            <div class="banner-icon">📤</div>
            <h3>Upload Master Data</h3>
            <p>Choose HSN master data file (Excel or CSV)</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=['xlsx', 'csv'], label_visibility="collapsed")
        
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
                        st.markdown("""
                        <div class="banner banner-error">
                            <div class="banner-icon">❌</div>
                            <div>Failed to load or process the master data file. Please check the file format.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state.file_uploaded = False
                    else:
                        # Display success message with file details
                        st.markdown(f"""
                        <div class="banner banner-success">
                            <div class="banner-icon">✅</div>
                            <div>
                                <strong>Master data loaded successfully!</strong><br>
                                Total HSN codes: {len(st.session_state.validator.master_data)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display valid HSN code lengths
                        valid_lengths = st.session_state.validator.valid_lengths
                        if valid_lengths:
                            st.markdown(f"**Valid HSN code lengths:** {', '.join(map(str, valid_lengths))}")
                        
                        st.session_state.file_uploaded = True
                        
                        # Show sample data with expander
                        with st.expander("View Sample Data"):
                            st.dataframe(st.session_state.validator.master_data.head(5))
            except Exception as e:
                st.markdown(f"""
                <div class="banner banner-error">
                    <div class="banner-icon">❌</div>
                    <div>Error loading file: {str(e)}</div>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.file_uploaded = False
        
        # Display warning if no file is uploaded
        if not st.session_state.file_uploaded:
            st.markdown("""
            <div class="banner banner-warning">
                <div class="banner-icon">⚠️</div>
                <div>Please upload an HSN master data file to start validation.</div>
            </div>
            """, unsafe_allow_html=True)

        # Add a quick guide
        with st.expander("Quick Guide"):
            st.markdown("""
            ### How to use:
            1. Upload your HSN master data file (Excel or CSV)
            2. Use the "Single Validation" tab to check individual HSN codes
            3. Use the "Bulk Validation" tab to check multiple codes at once
            4. View analytics in the "Dashboard" tab
            """)
    
    # Tab 1: Dashboard
    with tab1:
        st.markdown('<h2>HSN Validation Dashboard</h2>', unsafe_allow_html=True)
        
        if not st.session_state.file_uploaded:
            st.info("Upload a master data file from the sidebar to view the dashboard.")
        else:
            # Display overall stats if we have results
            if st.session_state.results:
                # Convert results to DataFrame for visualization
                results_df = pd.DataFrame([{
                    'HSN Code': r['hsn_code'],
                    'Valid': '✅' if r['is_valid'] else '❌',
                    'Format Valid': '✅' if r['format_valid'] else '❌',
                    'Exists in Database': '✅' if r['exists'] else '❌',
                    'Description': r.get('description', 'N/A')
                } for r in st.session_state.results])
                
                # Calculate metrics
                valid_count = sum(1 for r in st.session_state.results if r["is_valid"])
                invalid_count = len(st.session_state.results) - valid_count
                format_valid_count = sum(1 for r in st.session_state.results if r["format_valid"])
                exists_count = sum(1 for r in st.session_state.results if r["exists"])
                
                # Display metrics in a custom grid
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-card">
                        <div class="metric-value">{}</div>
                        <div class="metric-label">Total Codes</div>
                    </div>
                    <div class="metric-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));">
                        <div class="metric-value" style="color: #10B981;">{}</div>
                        <div class="metric-label">Valid Codes</div>
                    </div>
                    <div class="metric-card" style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));">
                        <div class="metric-value" style="color: #EF4444;">{}</div>
                        <div class="metric-label">Invalid Codes</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{}</div>
                        <div class="metric-label">Format Valid</div>
                    </div>
                </div>
                """.format(
                    len(st.session_state.results),
                    valid_count,
                    invalid_count,
                    format_valid_count
                ), unsafe_allow_html=True)
                
                # Create visualizations
                st.markdown("### Validation Results Visualization")
                
                # Create two columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Overall validation results chart
                    chart = create_chart(results_df)
                    st.altair_chart(chart, use_container_width=True)
                
                with col2:
                    # Format validation chart
                    format_chart = create_format_chart(results_df)
                    st.altair_chart(format_chart, use_container_width=True)
                
                # Add hierarchical chart if available
                hierarchical_chart = create_hierarchical_chart(st.session_state.results)
                if hierarchical_chart:
                    st.markdown("### Hierarchical Validation Analysis")
                    st.altair_chart(hierarchical_chart, use_container_width=True)
                
                # Display data table with results
                st.markdown("### Detailed Results")
                st.dataframe(results_df, use_container_width=True)
            else:
                st.markdown("""
                <div class="card">
                    <h3>No validation data yet</h3>
                    <p>Use the "Single Validation" or "Bulk Validation" tabs to validate HSN codes and see the results here.</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Tab 2: Single Validation
    with tab2:
        st.markdown('<h2>Single HSN Code Validation</h2>', unsafe_allow_html=True)
        
        if st.session_state.file_uploaded:
            st.markdown("""
            <div class="card">
                <p>Enter an HSN code below to validate against the master data.</p>
            </div>
            """, unsafe_allow_html=True)
            
            hsn_code = st.text_input("Enter HSN Code", placeholder="e.g., 85423100")
            
            validate_button = st.button("🔍 Validate", key="single_validate", use_container_width=True)
            
            if validate_button:
                if hsn_code:
                    with st.spinner("Validating..."):
                        # Add a small delay for UX
                        time.sleep(0.5)
                        result = st.session_state.validator.validate(hsn_code)
                        
                        # Add to results for dashboard visualization
                        if st.session_state.results and any(r["hsn_code"] == hsn_code for r in st.session_state.results):
                            # Replace existing result for this code
                            st.session_state.results = [r for r in st.session_state.results if r["hsn_code"] != hsn_code]
                        st.session_state.results.append(result)
                        
                        display_result(result)
                else:
                    st.warning("Please enter an HSN code to validate.")
        else:
            st.info("Upload a master data file from the sidebar to start validation.")
    
    # Tab 3: Bulk Validation
    with tab3:
        st.markdown('<h2>Bulk HSN Code Validation</h2>', unsafe_allow_html=True)
        
        if st.session_state.file_uploaded:
            st.markdown("""
            <div class="card">
                <p>Enter multiple HSN codes (one per line) or upload a file with HSN codes to validate in bulk.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create two columns for input options
            col1, col2 = st.columns(2)
            
            with col1:
                # Text area for multiple codes
                bulk_codes = st.text_area("Enter HSN codes (one per line)", placeholder="e.g.,\n85423100\n84717030\n73269099")
            
            with col2:
                # File uploader for bulk validation
                st.markdown("<p>Or upload a file with HSN codes</p>", unsafe_allow_html=True)
                bulk_file = st.file_uploader("", type=['csv', 'txt', 'xlsx'], key="bulk_uploader", label_visibility="collapsed")
            
            col1, col2 = st.columns(2)
            
            with col1:
                validate_button = st.button("🔍 Validate Codes", key="bulk_validate", use_container_width=True)
            
            with col2:
                download_results = st.button("📥 Download Results", disabled=not st.session_state.results, key="download_results", use_container_width=True)
            
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
                            
                            # Small delay for UI responsiveness
                            time.sleep(0.05)
                        
                        st.session_state.results = results
                        
                        # Display summary
                        valid_count = sum(1 for r in results if r["is_valid"])
                        invalid_count = len(results) - valid_count
                        
                        st.markdown("### Validation Summary")
                        st.markdown("""
                        <div class="metric-container">
                            <div class="metric-card">
                                <div class="metric-value">{}</div>
                                <div class="metric-label">Total Codes</div>
                            </div>
                            <div class="metric-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));">
                                <div class="metric-value" style="color: #10B981;">{}</div>
                                <div class="metric-label">Valid Codes</div>
                            </div>
                            <div class="metric-card" style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));">
                                <div class="metric-value" style="color: #EF4444;">{}</div>
                                <div class="metric-label">Invalid Codes</div>
                            </div>
                        </div>
                        """.format(
                            len(results),
                            valid_count,
                            invalid_count
                        ), unsafe_allow_html=True)
                        
                        # Create visualization
                        chart = create_chart(pd.DataFrame([{
                            'HSN Code': r['hsn_code'],
                            'Valid': '✅' if r['is_valid'] else '❌'
                        } for r in results]))
                        
                        st.altair_chart(chart, use_container_width=True)
                        
                        # Convert results to DataFrame for display
                        results_df = pd.DataFrame([{
                            'HSN Code': r['hsn_code'],
                            'Valid': '✅' if r['is_valid'] else '❌',
                            'Format Valid': '✅' if r['format_valid'] else '❌',
                            'Exists in Database': '✅' if r['exists'] else '❌',
                            'Description': r.get('description', 'N/A'),
                            'Messages': '; '.join(r['messages'])
                        } for r in results])
                        
                        st.markdown("### Detailed Results")
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Show individual results in expander
                        with st.expander("View Individual Validation Results"):
                            for result in results:
                                display_result(result)
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
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name="hsn_validation_results.csv",
                    mime="text/csv",
                )
        else:
            st.info("Upload a master data file from the sidebar to start bulk validation.")
    
    # Tab 4: About HSN Codes
    with tab4:
        st.markdown('<h2>About HSN Codes</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>What are HSN Codes?</h3>
            <p><strong>Harmonized System Nomenclature (HSN)</strong> codes are an internationally standardized system of names and numbers
            used to classify traded products. Developed by the World Customs Organization (WCO), this system is used
            by customs authorities around the world for the uniform classification of goods.</p>
            
            <h3>Structure of HSN Codes:</h3>
            <p>HSN codes typically vary in length from 2 to 8 digits, with each level providing more specific classification:</p>
            
            <ul>
                <li><strong>First 2 digits (XX)</strong>: Identify the chapter</li>
                <li><strong>First 4 digits (XXXX)</strong>: Identify the heading within a chapter</li>
                <li><strong>First 6 digits (XXXXXX)</strong>: Internationally standardized subheading</li>
                <li><strong>8 digits (XXXXXXXX)</strong>: Country-specific detailed classification</li>
            </ul>
            
            <h3>Example:</h3>
            <div style="margin-left: 20px;">
                <p>
                <strong>01</strong>: Live animals (Chapter)<br>
                <strong>0101</strong>: Live horses, asses, mules and hinnies (Heading)<br>
                <strong>010121</strong>: Pure-bred breeding animals (Subheading)<br>
                <strong>01012100</strong>: Pure-bred breeding animals (Detailed classification)
                </p>
            </div>
            
            <h3>Importance:</h3>
            <p>HSN codes are crucial for:</p>
            <ul>
                <li>International trade documentation</li>
                <li>Determining applicable customs duties and taxes</li>
                <li>Collection of trade statistics</li>
                <li>Application of trade regulations</li>
            </ul>
        </div>
        
        <div class="card">
            <h3>HSN Code Validation Process</h3>
            <p>Our validation system performs the following checks:</p>
            <ol>
                <li><strong>Format Validation</strong>: Checks if the HSN code format is correct (proper length and only digits)</li>
                <li><strong>Existence Validation</strong>: Verifies if the HSN code exists in the master database</li>
                <li><strong>Hierarchical Validation</strong>: For codes with more than 2 digits, checks if parent codes exist</li>
            </ol>
            <p>This comprehensive validation helps ensure that your HSN codes are accurate and compliant with international standards.</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Close the theme container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>HSN Code Validation System © 2025 | Designed for efficient customs classification</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
    # Cleanup temporary files
    for temp_file in ["temp_hsn_data.csv", "temp_hsn_data.xlsx"]:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass