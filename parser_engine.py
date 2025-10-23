import fitz
import camelot
import re
import pandas as pd
from pydantic import BaseModel
from fuzzywuzzy import fuzz

class StatementData(BaseModel):
    issuer: str = "Unknown"
    card_last_4_digits: str = "N/A"
    billing_cycle_end: str = "N/A"
    payment_due_date: str = "N/A"
    total_balance_due: float = 0.00
    total_new_charges_amount: float = 0.00
    transaction_count: int = 0

def _extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def _identify_issuer(text):
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in ["chase", "sapphire"]):
        return "Chase Bank"
    if any(keyword in text_lower for keyword in ["american express", "amex"]):
        return "American Express"
    if any(keyword in text_lower for keyword in ["citi"]):
        return "Citi Bank"
    if any(keyword in text_lower for keyword in ["bank of america", "boa"]):
        return "Bank of America"
    if any(keyword in text_lower for keyword in ["capital one"]):
        return "Capital One"
    return "Unknown"

def _clean_amount(text):
    text = str(text).replace('$', '').replace('₹', '').replace(',', '').strip()
    try:
        return float(text)
    except ValueError:
        return 0.00

def _extract_from_text(text, patterns):
    for label, regex in patterns.items():
        match = re.search(regex, text, re.IGNORECASE)
        if match:
            if len(match.groups()) >= 2:
                return match.group(2).strip()
            elif len(match.groups()) == 1:
                return match.group(1).strip()
            return match.group(0).strip()
    return "N/A"

def parse_statement(pdf_path):
    full_text = _extract_text_from_pdf(pdf_path)
    issuer = _identify_issuer(full_text)
    data = StatementData(issuer=issuer)

    patterns = {
        "due_date": r"(Payment Due Date|Due Date|PAYMENT DUE)[\s\S]{0,20}(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
        "billing_cycle": r"(Statement Closing Date|Billing Cycle Ends)[\s\S]{0,20}(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
        "last_4": r"(Last 4 Digits|Account Number Ending In|Card Ending)[\s\S]{0,10}(\d{4})",
        "balance_due": r"(Total Balance Due|New Balance|PAY THIS AMOUNT)[\s\S]{0,20}(\$?(\d{1,3}(?:,\d{3})*|\d+)\.\d{2})",
    }

    data.payment_due_date = _extract_from_text(full_text, {"pdd": patterns["due_date"]})
    data.billing_cycle_end = _extract_from_text(full_text, {"bce": patterns["billing_cycle"]})
    data.card_last_4_digits = _extract_from_text(full_text, {"l4": patterns["last_4"]})
    
    balance_str = _extract_from_text(full_text, {"tbd": patterns["balance_due"]})
    data.total_balance_due = _clean_amount(balance_str)

    try:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        
        transaction_count = 0
        total_charges = 0.00
        
        for table in tables:
            df = table.df
            col_names = [c.lower() for c in df.iloc[0].astype(str)]
            
            if (fuzz.partial_ratio("date", " ".join(col_names)) > 70 and
                fuzz.partial_ratio("amount", " ".join(col_names)) > 70):
                
                data_df = df.iloc[1:]
                desc_col = data_df.columns[col_names.index("description")] if "description" in col_names else 1
                amount_col_name = None
                for i, col in enumerate(col_names):
                    if fuzz.partial_ratio("amount", col) > 70 or fuzz.partial_ratio("charge", col) > 70:
                        amount_col_name = data_df.columns[i]
                        break

                if amount_col_name is not None:
                    amounts = data_df[amount_col_name].apply(_clean_amount)
                    total_charges += amounts[amounts > 0].sum()
                    transaction_count += len(amounts[amounts > 0])
        
        data.total_new_charges_amount = round(total_charges, 2)
        data.transaction_count = transaction_count

    except Exception as e:
        pass

    return data
