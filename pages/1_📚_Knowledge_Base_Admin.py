import streamlit as st
import os
from typing import List
import tempfile
from pathlib import Path
import hashlib

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredFileLoader,
)

# Import utilities
import utils.llm_models as llms
import utils.chains_lcel as chains

# Set page config
st.set_page_config(
    page_title="Knowledge Base Manager",
    page_icon="📚",
    layout="wide"
)

# Authentication
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets['general']['admin_password']:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False
            print()

    # Return True if the password is validated
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password
    st.markdown("# 🔐 Authentication Required")
    st.markdown("**Knowledge Base Manager - Admin Access Only**")
    st.markdown("---")
    
    st.text_input(
        "Enter admin password:", 
        type="password", 
        on_change=password_entered, 
        key="password",
        help="Contact your instructor for the admin password"
    )
    
    if "password_correct" in st.session_state:
        if not st.session_state["password_correct"]:
            st.error("❌ Incorrect password. Please contact your instructor.")
    
    st.markdown("---")
    st.info("💡 **For Students**: Return to the main Virtual TA page to ask questions about course content.")
    
    return False

# Check authentication before showing the main content
if not check_password():
    st.stop()

# Main app content (only shown after authentication)
def get_file_loader(file_path: str):
    """Return appropriate loader based on file extension."""
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == ".pdf":
        return PyPDFLoader(file_path)
    elif file_extension == ".docx":
        return Docx2txtLoader(file_path)
    elif file_extension == ".txt":
        return TextLoader(file_path)
    else:
        return UnstructuredFileLoader(file_path)

def process_file(file, text_splitter) -> List:
    """Process a file and return chunks of text."""
    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Load and split the document
        loader = get_file_loader(tmp_file_path)
        documents = loader.load()
        chunks = text_splitter.split_documents(documents)
        return chunks
    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)

def update_or_create_faiss_index(chunks: List, db_path: str = "data/"):
    """Update existing FAISS index or create a new one."""
    embeddings = OpenAIEmbeddings()
    
    if os.path.exists(os.path.join(db_path, "index.faiss")):
        # Load existing index
        db = FAISS.load_local(db_path, embeddings)
        # Add new documents
        db.add_documents(chunks)
    else:
        # Create new index
        db = FAISS.from_documents(chunks, embeddings)
    
    # Save the updated index
    os.makedirs(db_path, exist_ok=True)
    db.save_local(db_path)
    return db

def test_embedding_search(query: str, k: int = 3):
    """Test embedding search against the database."""
    db_path = "data/"
    embeddings = OpenAIEmbeddings()
    try:
        db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        docs = db.similarity_search_with_relevance_scores(query, k=k)
        return [(doc, score) for doc, score in docs], db.as_retriever(search_kwargs={"k": k})
    except Exception as e:
        st.error(f"Error searching database: {str(e)}")
        return [], None

def main():
    # Add logout option in sidebar
    with st.sidebar:
        st.markdown("### 🔐 Admin Session")
        st.success("✅ Authenticated as admin")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["password_correct"] = False
            st.rerun()
        st.markdown("---")
    
    st.title("📚 Knowledge Base Manager")
    st.markdown("*Admin Interface - Manage course materials and test the knowledge base*")
    
    # Create tabs for upload and test
    upload_tab, test_tab = st.tabs(["📤 Upload Files", "🔍 Test Knowledge Base"])
    
    with upload_tab:
        st.write("Upload files to update or create the knowledge base.")

        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt"],
        )

        # Configuration options
        with st.expander("Advanced Configuration"):
            col1, col2 = st.columns(2)
            with col1:
                chunk_size = st.number_input(
                    "Chunk Size",
                    min_value=100,
                    max_value=2000,
                    value=2000,
                    step=100,
                    help="Number of characters per chunk. Larger chunks provide more context but may be less precise."
                )
            
            with col2:
                chunk_overlap = st.number_input(
                    "Chunk Overlap",
                    min_value=0,
                    max_value=500,
                    value=200,
                    step=100,
                    help="Number of characters overlap between chunks. Higher overlap helps maintain context."
                )

            # Add configuration tips
            st.info("""
            **Configuration Tips:**
            - Chunk Size: Larger chunks (800-1000) work better for technical documents
            - Chunk Overlap: Usually 10-20% of chunk size is optimal
            - For most cases, the default values work well
            """)

        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if uploaded_files and st.button("Process Files"):
            with st.spinner("Processing files..."):
                try:
                    all_chunks = []
                    
                    # Process each file
                    for file in uploaded_files:
                        st.write(f"Processing {file.name}...")
                        chunks = process_file(file, text_splitter)
                        all_chunks.extend(chunks)
                        st.write(f"✅ Extracted {len(chunks)} chunks from {file.name}")

                    if all_chunks:
                        # Update or create FAISS index
                        st.write("Updating knowledge base...")
                        db = update_or_create_faiss_index(all_chunks)
                        st.success(f"Successfully processed {len(all_chunks)} chunks and updated the knowledge base!")
                        
                        # Display some statistics
                        st.write("### Summary")
                        st.write(f"- Total files processed: {len(uploaded_files)}")
                        st.write(f"- Total chunks added: {len(all_chunks)}")
                        st.write("- Database location: data/")
                        
                        # Add a button to switch to test tab
                        if st.button("🔍 Test the Updated Knowledge Base"):
                            test_tab.active = True

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    with test_tab:
        st.write("Test your knowledge base with queries.")
        
        # Query input
        test_query = st.text_input(
            "Enter your test query:",
            placeholder="e.g., What is regression analysis?",
            help="Enter any question you want to test against the knowledge base"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            k_results = st.number_input(
                "Number of results:",
                min_value=1,
                max_value=10,
                value=3,
                help="How many similar documents to retrieve"
            )
        
        if st.button("🔍 Search", type="primary") and test_query:
            with st.spinner("Searching knowledge base..."):
                results, retriever = test_embedding_search(test_query, k_results)
                
                if results and retriever:
                    st.subheader("Search Results")
                    
                    # Display results
                    for i, (doc, score) in enumerate(results, 1):
                        with st.expander(f"Result {i} (Similarity: {score:.3f})"):
                            st.markdown("**Content:**")
                            st.write(doc.page_content)
                            if hasattr(doc, 'metadata'):
                                st.markdown("**Metadata:**")
                                st.json(doc.metadata)
                    
                    # Generate LLM response using the RAG chain
                    st.subheader("AI Assistant Response")
                    
                    # Setup LLM and chain
                    llm = llms.openai_gpt4o_mini
                    rag_chain = chains.rag_chain(llm, retriever)
                    
                    with st.spinner("Generating response..."):
                        response = st.write_stream(
                            rag_chain.stream({
                                "query": test_query,
                                "chat_history": "No previous conversation"
                            })
                        )
                        
                        with st.expander("View source context"):
                            st.markdown("The response was generated using these retrieved documents:")
                            for i, (doc, _) in enumerate(results[:3], 1):
                                st.markdown(f"**Source {i}:**")
                                st.write(doc.page_content)
                                st.markdown("---")
                else:
                    st.warning("No results found in the knowledge base.")

if __name__ == "__main__":
    main() 