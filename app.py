import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain.globals import set_verbose
import utils.llm_models as llms
from utils.sidebar import sidebar
import utils.chains_lcel as chains

# Enable verbose logging
set_verbose(True)

# Set the page_title and configure the main page
st.set_page_config(
    page_title="ISOM 550 DDA Virtual TA - Beta",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# # Add admin note in sidebar
# st.sidebar.markdown("---")
# st.sidebar.info("👩‍🏫 **For Instructors**: Access the Knowledge Base Manager from the pages menu above to upload and manage course materials.")

# Cache the vectorized embedding database
@st.cache_resource
def load_db(db_path='data/'):
    """Load the FAISS database."""
    try:
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        st.error(f"Error loading database: {str(e)}")
        return None

# Load the database
db = load_db()
if db:
    retriever = db.as_retriever(search_kwargs={"k": 3})

# Setup LLM and chain
# llm = llms.openai_gpt4o_mini
llm = llms.claude_sonnet_with_fallback
rag_chain = chains.rag_chain(llm, retriever) if db else None

def main():
    st.header("🦜 Virtual TA - ISOM 550 DDA")
    sidebar()

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage("Hello! I'm your Virtual TA for ISOM 550. How can I help you today?")
        ]

    # Display conversation statistics
    if len(st.session_state.chat_history) > 1:
        st.caption(f"💬 Conversation: {len(st.session_state.chat_history)} messages")

    # Display chat history
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("AI", avatar="🦜"):
                st.markdown(message.content)

    # Get user input
    if user_query := st.chat_input("Enter your question here...", key="user_query"):
        # Display user message
        with st.chat_message("Human"):
            st.markdown(user_query)

        # Generate AI response
        with st.chat_message("AI", avatar="🦜"):
            if not db or not rag_chain:
                st.error("Knowledge base not available. Please contact your instructor.")
                return

            # Get recent chat history
            recent_history = (
                st.session_state.chat_history[-4:] 
                if len(st.session_state.chat_history) > 4 
                else st.session_state.chat_history
            )
            history_text = "\n".join([f"{'Human' if i % 2 == 0 else 'AI'}: {msg.content}" 
                                    for i, msg in enumerate(recent_history)])

            # Stream the response using the RAG chain
            response = st.write_stream(
                rag_chain.stream({
                    "query": user_query,
                    "chat_history": history_text
                })
            )

            # Update chat history
            st.session_state.chat_history.extend([
                HumanMessage(user_query),
                AIMessage(response)
            ])

if __name__ == '__main__':
    main()
