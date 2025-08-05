import pdfplumber

def extract_text_from_pdf(pdf_path):
    all_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")
    
    return all_text.strip()
