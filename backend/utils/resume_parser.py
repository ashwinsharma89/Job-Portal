import io
from fastapi import UploadFile
import pypdf
import docx
import logging

logger = logging.getLogger(__name__)

class ResumeParser:
    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        """
        Extracts text from an uploaded PDF or DOCX file.
        """
        filename = file.filename.lower()
        content = await file.read()
        file_stream = io.BytesIO(content)
        
        text = ""
        
        try:
            if filename.endswith(".pdf"):
                reader = pypdf.PdfReader(file_stream)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                    
            elif filename.endswith(".docx") or filename.endswith(".doc"):
                doc = docx.Document(file_stream)
                for para in doc.paragraphs:
                    text += para.text + "\n"
                    
            else:
                # Try UTF-8 decode for text files
                text = content.decode("utf-8")
                
        except Exception as e:
            logger.error(f"Failed to parse file {filename}: {e}")
            raise ValueError("Could not parse file. Ensure it is a valid PDF or DOCX.")
            
        return text.strip()
