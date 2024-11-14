import pickle

from PyPDF2 import PdfReader
from io import BytesIO
from langchain.schema import AIMessage, BaseMessage
from typing import List

def save_interview(conversation_data: List[BaseMessage], session_id):
    
    messages_list = []
    
    for msg in conversation_data:
        role = 'AI' if isinstance(msg, AIMessage) else 'User'
        messages_list.append({
            'role': role,
            'message': msg.content
        })
    
    return {
        'session_id': session_id,
        'messages': messages_list,
        'evaluation': None
    }
    
import pickle

def save_dict(my_dict, filename):
    
    """Append a dictionary to a pickle file by loading and saving it back"""
    try:
        # Try to load the existing data
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                
            # Ensure data is a list of dictionaries and not a nested list
            if isinstance(data, list) and any(isinstance(i, list) for i in data):
                data = [item for sublist in data for item in sublist]
        except (FileNotFoundError, EOFError):
            data = []  # Initialize an empty list if the file does not exist or is empty

        # Append the new dictionary
        data.append(my_dict)

        # Save back to file
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        print(f"Dictionary successfully appended to {filename}.")
        
    except Exception as e:
        print(f"Error appending to pickle file: {e}")

        
def resume_reader(resume_bytes):
    # Create a BytesIO object to simulate a file from the bytes data
    resume_stream = BytesIO(resume_bytes)
    pdf_reader = PdfReader(resume_stream)  # Create a PDF reader object using the BytesIO stream
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()  # Extract text from each page of the PDF
    return text