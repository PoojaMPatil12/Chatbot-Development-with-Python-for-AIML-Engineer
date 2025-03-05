################ first code without Docker #########################################
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
import fitz  # PyMuPDF for better PDF text extraction
from ollama import chat
import re
import requests
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

def ds_info(user_query, pdf_content):
    print("User Query:", user_query)
    
    combined_query = f"Based on the following content: {pdf_content}\nAnswer this: {user_query}"
    
    response = chat(model="deepseek-r1:1.5b",
        messages=[
            {
                "role": "system",
                "content": "Provide a concise and relevant answer in 2 sentences or less.",
            },
            {
                "role": "user",
                "content": combined_query,
            }
        ]
    )
    
    print(response.message.content)

    return response.message.content


# Function to extract text using PyMuPDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to clean text by removing non-alphanumeric characters
def clean_text(text):
    # Keep only alphanumeric characters and basic punctuation
    cleaned_text = re.sub(r"[^a-zA-Z0-9.,?!\s]", "", text)
    return cleaned_text

# Function to limit text to the first 200 words
def limit_text_to_200_words(text):
    words = text.split()
    limited_text = ' '.join(words[:200])  # Get the first 200 words
    return limited_text

# Endpoint to upload PDF, extract text, and get chatbot response
@app.post("/upload/")
async def upload_document(file: UploadFile = File(...), user_query: str = Form(...)):
    # Check if the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Save the uploaded file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Extract text using PyMuPDF
    extracted_text = extract_text_from_pdf(file_location)
    
    # Clean the extracted text
    cleaned_text = clean_text(extracted_text)

    # Limit the text to the first 200 words for better performance
    # limited_text = limit_text_to_200_words(cleaned_text)
    
    # Send the user query and the limited PDF text to ds_info
    chatbot_response = ds_info(user_query, cleaned_text)
    # Extract the concise answer after </think> or remove the <think> section entirely
    cleaned_response = re.sub(r"<think>.*?</think>\s*", "", chatbot_response, flags=re.DOTALL).strip()
    # Return the chatbot's response as a JSON response
    return {
        "filename": file.filename,
        "user_query": user_query,
        "chatbot_response": cleaned_response
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


############################## 2nd code with Docker ############################################
# from fastapi import FastAPI, UploadFile, File, HTTPException, Form
# import fitz  # PyMuPDF for better PDF text extraction
# import re
# import requests
# import os
# from fastapi.staticfiles import StaticFiles

# app = FastAPI()
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

# def ds_info(user_query, pdf_content):
#     print("User Query:", user_query)
#     ollama_url = "http://ollama:11434/api/generate"
    
#     combined_query = f"Based on the following content: {pdf_content}\nAnswer this: {user_query}"
    
#     payload = {
#         "model": "deepseek-r1:1.5b",
#         "prompt": combined_query,
#         "stream": False
#     }
    
#     headers = {
#         "Content-Type": "application/json"
#     }

#     try:
#         print("Using Ollama URL:", ollama_url)
#         print("Payload:", payload)
#         response = requests.post(ollama_url, json=payload, headers=headers, timeout=500)
#         print("Status Code:", response.status_code)
#         print("Response Text:", response.text)
#         response.raise_for_status()
#         chatbot_response = response.json().get('response', 'No response')
#     except requests.exceptions.Timeout:
#         print("Request to Ollama timed out.")
#         chatbot_response = "The request to the language model timed out."
#     except requests.exceptions.RequestException as e:
#         print("Error connecting to Ollama:", e)
#         chatbot_response = "Sorry, there was an issue processing your request."
#     except ValueError as e:
#         print("Error parsing response:", e)
#         chatbot_response = "Sorry, there was an issue understanding the response."

#     print("Chatbot Response:", chatbot_response)
#     return chatbot_response


# def extract_text_from_pdf(file_path):
#     doc = fitz.open(file_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     return text

# @app.post("/upload/")
# async def upload_document(file: UploadFile = File(...), user_query: str = Form(...)):
#     if file.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
#     file_location = f"temp_{file.filename}"
#     with open(file_location, "wb") as f:
#         f.write(await file.read())
    
#     extracted_text = extract_text_from_pdf(file_location)
#     chatbot_response = ds_info(user_query, extracted_text)
#     cleaned_response = re.sub(r"<think>.*?</think>\s*", "", chatbot_response, flags=re.DOTALL).strip()
    
#     return {
#         "filename": file.filename,
#         "user_query": user_query,
#         "chatbot_response": cleaned_response
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

