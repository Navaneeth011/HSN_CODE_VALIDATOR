# HSN Code Validation Agent

A comprehensive system for validating Harmonized System Nomenclature (HSN) codes against a master dataset using Google's Agent Development Kit (ADK) and Streamlit.

HSN Code Validator Screenshot(

IMAGE 1:
(![image](https://github.com/user-attachments/assets/11d8e114-c6f2-4f40-85c6-43ea4c8706b3)
)

IMAGE 2:
(![image](https://github.com/user-attachments/assets/ac59f46b-af8f-403b-a524-769f29da2687)
)

)

## Project Overview

This project implements an intelligent agent that validates HSN codes, which are internationally standardized codes used to classify traded products. The system offers:

1. **Single HSN Code Validation** - Validate individual HSN codes
2. **Batch Validation** - Process multiple HSN codes at once
3. **Conversational Interface** - Chat with an AI assistant about HSN codes

## Features

- **Format Validation**: Checks if the input code adheres to expected structural characteristics
- **Existence Validation**: Verifies if the exact HSN code exists in the master dataset
- **Hierarchical Validation**: Checks if parent codes of a given HSN code exist in the dataset
- **Detailed Results**: Provides comprehensive validation details for each code
- **Batch Processing**: Support for validating multiple codes through text input or file upload
- **Intuitive UI**: User-friendly Streamlit interface with different validation modes

## Technical Architecture

The project uses the Google Agent Development Kit (ADK) to create an intelligent agent with the following components:

1. **HSNDataLoader**: Utility for loading and processing HSN code master data
2. **HSNValidationTool**: ADK tool that implements the validation logic
3. **HSNValidator**: Main class that combines the data loader and validation tool into an ADK agent
4. **Streamlit UI**: Web interface for interacting with the validation system

## Installation

1. Clone the repository:
```
git clone https://github.com/Navaneeth011/HSN_CODE_VALIDATOR.git
cd HSN_CODE_VALIDATOR
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the requirements:
```
pip install -r requirements.txt
```

4. Place your HSN master data file in the `data/` directory:
```
HSN_CODE_VALIDATOR/data/HSN_SAC - MSTR.csv
```

## Usage

### Running the Application

Start the Streamlit web interface:

```
cd HSN_CODE_VALIDATOR/ui
streamlit run app.py
```

This will launch the application in your default web browser.

### Using the Application

1. **Single Validation Mode**
   - Enter a single HSN code in the input field
   - Click the "Validate" button to see the results

2. **Batch Validation Mode**
   - Enter multiple HSN codes separated by commas or upload a CSV/Excel file
   - Select the appropriate column if uploading a file
   - Click "Validate Batch" to process all codes at once

3. **Chat with Validator Mode**
   - Interact with the AI assistant conversationally
   - Ask questions about HSN codes or request validations

## Project Structure

```
HSN_CODE_VALIDATOR/
├── agent/
│   ├── __init__.py
│   ├── hsn_agent.py         # ADK agent implementation
├── data/
│   ├── HSN_SAC - MSTR.csv   # HSN master data
├── ui/
│   ├── app.py               # Streamlit web interface
├── utils/
│   ├── __init__.py
│   ├── data_loader.py       # Utility for loading HSN data
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
```

## ADK Components

The project leverages several key ADK components:

1. **LlmAgent**: The base agent class from ADK that provides the agent framework
2. **BaseTool**: Extended to create our custom HSN validation tool
3. **build_agent**: Factory function to construct the agent with appropriate configuration

## Extending the Project

To extend the functionality of this project, consider:

1. Adding more validation rules for HSN codes
2. Implementing a database backend for storing validation results
3. Adding user authentication for secure access
4. Incorporating API endpoints for programmatic access
5. Implementing notification systems for invalid codes

## License

This project is under the License process.

## Acknowledgments

- Google Agent Development Kit (ADK) team for providing the framework
- Streamlit for the interactive web interface capabilities
- The HSN classification system maintainers for standardizing product codes
