
# Credit Card Statement Parser Chatbot 💳

A multi-turn conversational chatbot built with **Streamlit** that utilizes advanced PDF parsing libraries like **PyMuPDF** and **Camelot** to extract five key data points from credit card statements across five major US issuers.

## 🌟 Features

  * **Multi-Issuer Support:** Handles statements from **Chase, American Express, Citi, Bank of America,** and **Capital One**.
  * **Key Data Extraction:** Parses and extracts the following 5 critical data points:
      * **Total Balance Due**
      * **Payment Due Date**
      * **Statement/Billing Cycle End Date**
      * **Card Last 4 Digits**
      * **Transaction Summary** (Total charges and count)
  * **Conversational Interface:** Allows for follow-up questions in a chatbot format after the initial PDF parsing.
  * **Robust Parsing:** Employs a hybrid approach of **Regular Expressions (Regex)** and **Table/Layout Analysis (Camelot)** to handle various real-world PDF formats.

## 🛠️ Technology Stack

| Category | Tool/Library | Purpose |
| :--- | :--- | :--- |
| **Frontend/Chatbot** | `streamlit` | Creates the interactive, multi-turn web interface. |
| **PDF Text Extraction** | `PyMuPDF` (fitz) | High-speed, low-level text and metadata extraction. |
| **Table Extraction** | `camelot-py` | Extracts structured transaction data from PDF tables. |
| **Data Structure** | `pydantic` | Defines and validates the structured output (`StatementData`). |
| **Fuzzy Matching** | `fuzzywuzzy` | Increases robustness when searching for varying label names. |
| **Core Dependency** | **Ghostscript** | System library required by `camelot` for PDF processing. |

## 🚀 Installation and Setup

### 1\. Prerequisite: Install Ghostscript

Before installing Python libraries, you must install the **Ghostscript** system dependency.

  * **Windows/macOS:** Download and install the latest 64-bit installer from the official Ghostscript website.

### 2\. Python Environment Setup

```bash
# Create project folder
mkdir credit-card-parser-bot
cd credit-card-parser-bot

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3\. Install Python Dependencies

Create a `requirements.txt` file and install the necessary packages:

```bash
# requirements.txt
camelot-py[cv]
pydantic
PyMuPDF
streamlit
pandas
fuzzywuzzy
python-levenshtein
```

```bash
pip install -r requirements.txt
```

### 4\. Project Structure

Ensure you have the following files in your root directory:

```
credit-card-parser-bot/
├── venv/
├── requirements.txt
├── parser_engine.py  # Core extraction logic
└── app.py            # Streamlit chatbot interface
```

## ▶️ How to Run the Application

1.  Ensure your virtual environment is activated.
2.  Run the Streamlit application from your terminal:

<!-- end list -->

```bash
streamlit run app.py
```

3.  The application will open in your browser (usually at `http://localhost:8501`).

## 💬 Usage

1.  **Upload:** Use the **sidebar upload button** to select a credit card statement PDF.
2.  **Parse:** Click the **"Parse Statement"** button. The bot will confirm processing is complete.
3.  **Chat:** Ask the bot questions about your statement data, such as:
      * "What's my total balance due?"
      * "When is the payment date?"
      * "How many new transactions were there?"
      * "Tell me the full summary."

## ☁️ Deployment (Streamlit Cloud)

Due to the complex dependency on Ghostscript, the recommended deployment platform is **Streamlit Cloud**.

1.  Ensure your project files (`app.py`, `parser_engine.py`, `requirements.txt`) are committed to a public **GitHub repository**.

2.  Add a **`setup.sh`** file to the root of your repository to install Ghostscript on the cloud host:

    ```bash
    #!/bin/bash
    apt-get update
    apt-get install -y ghostscript
    ```

3.  Deploy the application directly via the Streamlit Cloud dashboard, pointing it to your GitHub repository and specifying `app.py` as the main file.

## 📝 Licensing

This project is intended for educational purposes under the **GNU Affero General Public License (AGPL)**. If you intend to use or distribute this software commercially, you must comply with the AGPL or seek appropriate commercial licensing for its dependencies (like Ghostscript).
