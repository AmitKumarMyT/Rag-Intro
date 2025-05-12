"""
Chat interface component for the Smart Knowledge Agent
"""
import streamlit as st
import time
import queue
import threading
from src.retrieval.response_generator import generate_response
from src.ui.utils.session_state import add_message

def generate_streaming_response(question, chunks):
    """
    Generate a streaming response by yielding words gradually
    
    Args:
        question: User's question
        chunks: Relevant document chunks for context
        
    Returns:
        A generator that yields words gradually
    """
    # Generate the full response text first
    full_answer = generate_response(question, chunks)
    
    # Create a queue for the streamed content
    q = queue.Queue()
    
    # Function to process and add the full response to the queue
    def process_response():
        words = full_answer.split(" ")
        # Add each word gradually to simulate typing
        for word in words:
            q.put(word + " ")
            # Adjust the sleep time to control the speed (shorter = faster)
            time.sleep(0.02)  
        # Signal that we're done
        q.put(None)
        # Store the complete response
        add_message("assistant", full_answer)
        # End streaming mode
        st.session_state.streaming = False
    
    # Start the processing in a background thread
    thread = threading.Thread(target=process_response)
    thread.start()
    
    # Return a generator that yields content from the queue
    return queue_generator(q)

def queue_generator(q):
    """
    Generate content from a queue
    
    Args:
        q: Queue containing text chunks
        
    Yields:
        Text chunks from the queue
    """
    while True:
        item = q.get()
        if item is None:
            break
        yield item
        q.task_done()

def show_chat_interface():
    """
    Display chat interface for active knowledge source with streaming response
    """
    # Source info header if available
    if st.session_state.active_source:
        source = st.session_state.active_source
        st.markdown(
            f"<div class='chat-header'>Chatting with: "
            f"<span class='source-name'>{source['name']}</span> "
            f"<span class='source-type'>({source['type']})</span>"
            f"<div class='source-icon-header'>{source['icon']}</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
    else:
        st.markdown("<div class='chat-header'>Smart Knowledge Agent <span class='agent-badge'>AI</span></div>", unsafe_allow_html=True)
    
    # Chat history container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-message">
            <div class="welcome-icon">👋</div>
            <h3>Hello there!</h3>
            <p>I'm your Smart Knowledge Agent. I've analyzed the available content and I'm ready to help.</p>
            <p>Feel free to ask me questions about the content I've analyzed.</p>
            <div class="welcome-tips">
                <div class="tip"><span class="tip-icon">💡</span> Try asking specific questions about the content</div>
                <div class="tip"><span class="tip-icon">📚</span> Add more sources from the sidebar</div>
                <div class="tip"><span class="tip-icon">🔍</span> Create collections to organize your knowledge</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display existing messages
    for message in st.session_state.messages:
        role = message.get("role", "")
        content = message.get("content", "")
        
        if role == "user":
            st.markdown(
                f'''
                <div class="message-container">
                    <div class="user-message">{content}</div>
                    <div class="avatar user-avatar">👤</div>
                </div>
                ''', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'''
                <div class="message-container">
                    <div class="avatar assistant-avatar">🤖</div>
                    <div class="assistant-message">{content}</div>
                </div>
                ''', 
                unsafe_allow_html=True
            )
    
    # Check if we're currently streaming a response
    if "streaming" in st.session_state and st.session_state.streaming:
        # Create a container for the streaming message
        with st.container():
            st.markdown(
                '''
                <div class="message-container">
                    <div class="avatar assistant-avatar">🤖</div>
                    <div class="assistant-message typing-message">
                ''', 
                unsafe_allow_html=True
            )
            st.write_stream(st.session_state.stream_container)
            st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area for new messages
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # Create columns for input and button
    input_col, button_col = st.columns([6, 1])
    
    # Create a form for user input to better handle submission
    with st.form(key="chat_form", clear_on_submit=True):
        # Make the input look more like a modern chat box
        user_input = st.text_input(
            "",
            key="user_input",
            placeholder="Type your question here...",
        )
        
        # Center align the button and make it more modern
        submit_button = st.form_submit_button("Send 💬")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process user input when the form is submitted
    if submit_button and user_input:
        # Add user message to chat
        add_message("user", user_input)
        
        if st.session_state.retriever:
            # Setup streaming
            if "streaming" not in st.session_state:
                st.session_state.streaming = False
            
            # Query for relevant documents
            relevant_chunks = st.session_state.retriever.query_documents(user_input, n_results=3)
            
            # Initialize streaming containers
            st.session_state.streaming = True
            st.session_state.stream_container = generate_streaming_response(user_input, relevant_chunks)
            
            # Force a rerun to start the streaming
            st.rerun()
        else:
            add_message("assistant", "I don't have any knowledge sources loaded yet. Please add a YouTube channel or select an existing knowledge source from the sidebar.")
            st.rerun()
