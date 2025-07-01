import streamlit as st
import os
from datetime import datetime

def clear_chat_history():
    """Clear the chat history and reset conversation."""
    st.session_state.chat_history = []
    st.rerun()

def save_chat_history():
    """Save chat history in a readable format."""
    if 'chat_history' not in st.session_state or not st.session_state.chat_history:
        return "No conversation history to save."
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_content = f"ISOM 550 DDA Virtual TA - Chat History\n"
    chat_content += f"Saved on: {timestamp}\n"
    chat_content += f"Total Messages: {len(st.session_state.chat_history)}\n"
    chat_content += "=" * 50 + "\n\n"
    for i, message in enumerate(st.session_state.chat_history, 1):
        if hasattr(message, 'content'):
            if "AI" in str(type(message)) or "Assistant" in str(type(message)):
                chat_content += f"🤖 AI Assistant:\n{message.content}\n\n"
            else:
                chat_content += f"👤 Student:\n{message.content}\n\n"
        chat_content += "-" * 30 + "\n\n"
    return chat_content

def sidebar():
    """Sidebar for ISOM 550 Virtual TA."""
    with st.sidebar:
        # Header and branding
        st.markdown("# 🤖 Virtual TA")
        st.markdown("**ISOM 550 - Data & Decision Analytics**")
        st.markdown("*Goizueta Business School*")
        st.markdown("---")
        
        # # App description
        # st.markdown("## 💡 About")
        # st.info("""
        # I'm your AI teaching assistant! I can help you with:
        
        # 📚 **Course Content**: Concepts, explanations, examples
        
        # 📋 **Course Logistics**: Syllabus, assignments, deadlines
        
        # 🔍 **Assignment Help**: Step-by-step guidance
        
        # 💻 **Technical Support**: Python, Excel, JMP, SQL
        # """)
        
        # Conversation management
        st.markdown("## 💬 Chat Management")
        if 'chat_history' in st.session_state:
            msg_count = len(st.session_state.chat_history)
            st.markdown(f"**Messages in conversation:** {msg_count}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True, help="Clear chat history"):
                clear_chat_history()
                st.success("Chat cleared!")
        
        with col2:
            if 'chat_history' in st.session_state and st.session_state.chat_history:
                chat_content = save_chat_history()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_history_{timestamp}.txt"
                st.download_button(
                    label="💾 Save",
                    data=chat_content,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True,
                    help="Download chat history"
                )
            else:
                st.button("💾 Save", disabled=True, use_container_width=True, help="No conversation to save")
        
        st.markdown("---")
        
        # Usage tips
        st.markdown("## 🎯 Tips for Better Results")
        with st.expander("💡 **How to Ask Questions**"):
            st.markdown("""
            **Be Specific:**
            - "Explain linear regression with an example"
            - "What's the deadline for Assignment 2?"
            - "How do I interpret R-squared values?"
            
            **Provide Context:**
            - Reference specific assignments or topics
            - Mention what you've already tried
            - Ask follow-up questions for clarification
            
            **Build Conversations:**
            - Ask "Can you elaborate on that?"
            - Request examples: "Show me how this works"
            - Ask for next steps: "What should I do next?"
            """)
        
        # Knowledge base status
        st.markdown("## 📊 System Status")
        if hasattr(st.session_state, 'db') and st.session_state.db:
            st.success("✅ Knowledge base loaded")
        else:
            # Check if database exists
            if os.path.exists("data/index.faiss"):
                st.success("✅ Knowledge base available")
            else:
                st.warning("⚠️ Knowledge base not found")
        
        st.markdown("---")
        
        # Footer
        st.markdown("## ⚠️ Important")
        st.markdown("""
        🎓 **Academic Integrity**: Use for learning, not copying
        
        🔒 **Privacy**: Don't share personal information
        
        📝 **Accuracy**: Always verify important information
        
        💬 **Feedback**: Report issues to your instructor
        """)
        
        # Admin section (only show if Knowledge Base Manager page exists)
        if len(st.session_state.get('pages', [])) > 0:
            st.markdown("---")
            st.markdown("### 👩‍🏫 For Instructors")
            st.caption("Access Knowledge Base Manager from the pages menu above")
