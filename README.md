# HSN Code Validation Agent

A user-friendly web application to validate Harmonized System Nomenclature (HSN) codes against a master dataset. Built with Python and Streamlit.

![HSN Code Validator Screenshot](![alt text](image.png))

## Features

- **Upload Master Data**: Support for Excel (.xlsx) and CSV (.csv) files containing HSN codes and descriptions
- **Single Code Validation**: Validate individual HSN codes with detailed results
- **Bulk Validation**: Process multiple HSN codes at once through text input or file upload
- **Hierarchical Validation**: Check if parent codes exist in the master data
- **Export Results**: Download validation results as CSV files
- **Informative Interface**: Learn about HSN codes and their importance

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone the repository or download the source code:

```bash
git clone https://github.com/yourusername/hsn-code-validator.git
cd hsn-code-validator
```

2. Create and activate a virtual environment (optional but recommended):

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Upload your HSN master data file through the sidebar

4. Use the different tabs to validate HSN codes:
   - **Single Validation**: Enter one HSN code and click "Validate"
   - **Bulk Validation**: Enter multiple codes or upload a file, then click "Validate Codes"
   - **About HSN Codes**: Learn about the HSN code system

## File Format Requirements

The application supports two primary formats for the master data:

1. **Standard Format**: Excel or CSV file with separate columns for HSN codes and descriptions
   - Column headers should ideally be "HSNCode" and "Description" (case-insensitive)
   - If column names are different, the application will attempt to identify them based on content

2. **Single Column Format**: A file with HSN codes and descriptions in a single column
   - HSN codes should be at the beginning of each row (numeric part)
   - Descriptions should follow the HSN code in the same cell

## Validation Logic

The application validates HSN codes using multiple criteria:

1. **Format Validation**: Checks if the code follows the expected format (digits only)
2. **Existence Validation**: Verifies if the code exists in the master data
3. **Hierarchical Validation**: For longer codes, checks if parent codes exist in the master data

## Troubleshooting

If you encounter issues with the application, please refer to the [troubleshooting guide](troubleshooting_guide.md).

Common issues include:
- File format problems
- Encoding issues with CSV files
- HSN code formatting discrepancies

## Project Structure

```
hsn_code_validator/
├── app.py             # Main Streamlit application
├── validator.py       # HSN code validation logic
├── requirements.txt   # Project dependencies
├── README.md          # Project documentation
└── troubleshooting_guide.md  # Help for common issues
```

## Extending the Application

The application can be extended in several ways:

- Add user authentication
- Implement caching for better performance with large datasets
- Create a batch processing system for very large files
- Add API endpoints for programmatic access
- Implement more sophisticated validation rules

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Harmonized System Nomenclature (HSN) is maintained by the World Customs Organization (WCO)
- Built with [Streamlit](https://streamlit.io/) - The fastest way to build data apps in Python
- Uses [Pandas](https://pandas.pydata.org/) for efficient data processing