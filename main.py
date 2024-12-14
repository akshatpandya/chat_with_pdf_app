import streamlit as st
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI
import os
import tempfile
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def extract_pdf_text(uploaded_file):
    """Extract text from an uploaded PDF file."""
    text = ""
    pdf_reader = PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text += page.extract_text() if page.extract_text() else ""
    return text


def save_text_to_file(text, filename="data.txt"):
    """Save extracted text to a temporary file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def build_index(data_dir=".", index_name="index.json"):
    """Build a LlamaIndex index from the text file."""
    documents = SimpleDirectoryReader(data_dir).load_data()
    index = VectorStoreIndex(documents)
    return index



def main():
    st.title("PDF Chat with LlamaIndex")
    llm = OpenAI(temperature=0.1, api_key=os.getenv("OPENAI_API_KEY"), model=str(os.getenv("OPENAI_MODEL_NAME")))

    # Upload PDF File
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file:
        # Extract and display PDF text
        st.info("Extracting text from the PDF...")
        text = extract_pdf_text(uploaded_file)
        st.success("Text extraction complete!")

        # Save text to a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            text_file = os.path.join(temp_dir, "data.txt")
            save_text_to_file(text, text_file)

            # Build the index
            st.info("Building LlamaIndex...")
            index_file = os.path.join(temp_dir, "index.json")
            index = build_index(data_dir=temp_dir, index_name=index_file)
            st.success("Indexing complete!")

            # Query Section
            query_engine = index.as_query_engine(llm=llm, response_mode='tree_summarize')

            st.subheader("Ask a question about the PDF content:")
            query = st.text_input("Enter your query")

            if query:
                st.info("Querying the PDF...")
                response = query_engine.query(query)
                st.success(f"Answer: {response}")

if __name__ == "__main__":
    main()
