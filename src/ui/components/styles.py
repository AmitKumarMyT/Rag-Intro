"""
CSS and styling functions for the Smart Knowledge Agent UI
"""
import streamlit as st

def apply_custom_css():
    """Apply custom CSS for frosted glass dark theme"""
    st.markdown("""
    <style>
        /* Main background with subtle gradient animation */
        .stApp {
            background: linear-gradient(-45deg, #0f0f1a, #1a1a2e, #21213a, #262645);
            background-size: 400% 400%;
            animation: gradient-shift 15s ease infinite;
            color: rgba(255, 255, 255, 0.9);
        }
        
        @keyframes gradient-shift {
            0% { background-position: 0% 50% }
            50% { background-position: 100% 50% }
            100% { background-position: 0% 50% }
        }
        
        /* Frosted glass card styling */
        .glass-card {
            background: rgba(30, 30, 50, 0.35);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px;
            padding: 22px;
            margin: 12px 0;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        /* Knowledge source card styling */
        .source-card {
            background: rgba(40, 40, 70, 0.35);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 16px;
            margin: 8px;
            box-shadow: 0 6px 20px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            cursor: pointer;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .source-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px 0 rgba(69, 104, 220, 0.3);
            border: 1px solid rgba(106, 48, 147, 0.3);
            background: rgba(45, 45, 75, 0.45);
        }
        
        .source-icon {
            font-size: 30px;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .source-title {
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 16px;
        }
        
        .source-info {
            font-size: 12px;
            opacity: 0.7;
            margin-top: auto;
        }
        
        /* Chat input field styling */
        .stTextInput > div > div > input {
            background-color: rgba(60, 60, 80, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 16px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border: 1px solid rgba(106, 48, 147, 0.5);
            box-shadow: 0 4px 20px rgba(69, 104, 220, 0.3);
            background-color: rgba(60, 60, 80, 0.3);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(90deg, #4568dc, #6a3093);
            color: white;
            border: none;
            border-radius: 24px;
            padding: 10px 24px;
            transition: all 0.3s ease;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(106, 48, 147, 0.4);
            background: linear-gradient(90deg, #4568dc, #7a359f);
        }
        
        /* Progress bar styling */
        .stProgress > div > div {
            background-color: #6a3093;
        }
        
        /* Message container styling */
        .message-container {
            display: flex;
            margin: 18px 0;
            align-items: flex-start;
            position: relative;
        }
        
        .avatar {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            margin-top: 5px;
        }
        
        .user-avatar {
            background: linear-gradient(135deg, #4568dc, #5f82e2);
            margin-left: 12px;
            order: 2;
        }
        
        .assistant-avatar {
            background: linear-gradient(135deg, #6a3093, #a044c5);
            margin-right: 12px;
        }
        
        .user-message {
            background: rgba(69, 104, 220, 0.15);
            border-radius: 18px 3px 18px 18px;
            padding: 16px 18px;
            margin-right: 8px;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            animation: slide-in-right 0.3s ease;
            max-width: calc(85% - 38px);
            margin-left: auto;
            color: rgba(255, 255, 255, 0.95);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 1px solid rgba(255, 255, 255, 0.05);
            position: relative;
            order: 1;
        }
        
        .user-message::after {
            content: '';
            position: absolute;
            right: -10px;
            top: 15px;
            width: 0;
            height: 0;
            border-left: 10px solid rgba(69, 104, 220, 0.15);
            border-top: 10px solid transparent;
            border-bottom: 10px solid transparent;
        }
        
        .assistant-message {
            background: rgba(106, 48, 147, 0.15);
            border-radius: 3px 18px 18px 18px;
            padding: 16px 18px;
            margin-left: 8px;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            animation: slide-in-left 0.3s ease;
            max-width: calc(85% - 38px);
            margin-right: auto;
            color: rgba(255, 255, 255, 0.95);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            position: relative;
        }
        
        .assistant-message::after {
            content: '';
            position: absolute;
            left: -10px;
            top: 15px;
            width: 0;
            height: 0;
            border-right: 10px solid rgba(106, 48, 147, 0.15);
            border-top: 10px solid transparent;
            border-bottom: 10px solid transparent;
        }
        
        .message-timestamp {
            position: absolute;
            bottom: -18px;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.5);
            padding: 2px 6px;
            border-radius: 10px;
        }
        
        .user-timestamp {
            right: 20px;
        }
        
        .assistant-timestamp {
            left: 20px;
        }
        
        @keyframes slide-in-right {
            from { transform: translateX(20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slide-in-left {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Section title styling */
        .section-title {
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0 15px 0;
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }
        
        /* Source preview container */
        .source-preview {
            background: rgba(20, 20, 35, 0.3);
            padding: 12px;
            border-radius: 12px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 12px;
            max-height: 100px;
            overflow-y: auto;
            white-space: pre-wrap;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-1wrcr25, .st-c8, .st-bq, section[data-testid="stSidebar"] {
            background: rgba(20, 20, 35, 0.4) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
        }
        
        /* Sidebar header */
        .sidebar-header {
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 24px;
            letter-spacing: 0.5px;
        }
        
        /* Sidebar nav item */
        .sidebar-nav-item {
            background: rgba(30, 30, 50, 0.4);
            border-radius: 12px;
            padding: 12px 16px;
            margin: 6px 0;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
        }
        
        .sidebar-nav-item:hover {
            background: rgba(40, 40, 60, 0.6);
            transform: translateX(3px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .sidebar-nav-icon {
            margin-right: 10px;
            font-size: 18px;
        }
        
        /* Selected source highlight */
        .selected-source {
            border-left: 4px solid #6a3093;
            background: rgba(50, 50, 80, 0.4);
            box-shadow: 0 4px 15px rgba(106, 48, 147, 0.2);
        }
        
        /* Action buttons for sources */
        .source-actions {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 8px;
        }
        
        .action-btn {
            background: rgba(40, 40, 70, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 5px 10px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .action-btn:hover {
            background: rgba(70, 70, 100, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        /* Source items in collection */
        .collection-items {
            margin-top: 10px;
            padding: 10px;
            background: rgba(20, 20, 35, 0.2);
            border-radius: 10px;
            font-size: 12px;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .collection-item {
            padding: 4px 8px;
            margin: 3px 0;
            border-radius: 6px;
            background: rgba(60, 60, 90, 0.2);
            transition: all 0.2s ease;
        }
        
        .collection-item:hover {
            background: rgba(60, 60, 90, 0.4);
        }
        
        /* Form elements */
        .stTextInput, .stTextArea, .stSelectbox {
            filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
        }
        
        /* Chat welcome message styling */
        .stMarkdown h3 {
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Typing indicator animation */
        @keyframes typing-dot {
            0%, 20% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
            80%, 100% { transform: translateY(0); }
        }
        
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.7);
            margin: 0 2px;
        }
        
        .typing-indicator span:nth-child(1) {
            animation: typing-dot 1s infinite 0s;
        }
        
        .typing-indicator span:nth-child(2) {
            animation: typing-dot 1s infinite 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
            animation: typing-dot 1s infinite 0.4s;
        }
        
        /* Streaming message animation */
        @keyframes blink-cursor {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
        
        .typing-message::after {
            content: "|";
            margin-left: 2px;
            animation: blink-cursor 0.8s infinite;
            color: rgba(255, 255, 255, 0.7);
        }

        /* Chat input container */
        .chat-input-container {
            background: rgba(30, 30, 50, 0.5);
            border-radius: 24px;
            padding: 10px 15px;
            margin-top: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
        }

        /* Override default form styling */
        .chat-input-container .stForm {
            border: none;
            background: transparent;
            padding: 0;
        }

        .chat-input-container .stForm > div > div:first-child {
            display: none; /* Hide form header */
        }

        .chat-input-container .stFormSubmit {
            margin: 0;
        }

        /* Chat header styling */
        .chat-header {
            background: rgba(40, 40, 70, 0.5);
            padding: 16px 20px;
            border-radius: 16px 16px 0 0;
            margin-bottom: 0;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            display: flex;
            align-items: center;
            border-bottom: 1px solid rgba(106, 48, 147, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .source-name {
            font-weight: bold;
            color: white;
            margin-right: 5px;
        }

        .source-type {
            opacity: 0.7;
            font-size: 0.9em;
        }

        .source-icon-header {
            font-size: 24px;
            margin-left: auto;
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Welcome message styling */
        .welcome-message {
            text-align: center;
            padding: 40px 20px;
            background: rgba(40, 40, 70, 0.3);
            border-radius: 18px;
            margin: 20px 0;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .welcome-icon {
            font-size: 48px;
            margin-bottom: 20px;
            animation: bounce 2s ease infinite;
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-20px); }
            60% { transform: translateY(-10px); }
        }

        .welcome-tips {
            margin-top: 30px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        }

        .tip {
            background: rgba(50, 50, 80, 0.4);
            padding: 10px 15px;
            border-radius: 12px;
            font-size: 14px;
            display: flex;
            align-items: center;
            text-align: left;
        }

        .tip-icon {
            margin-right: 8px;
            font-size: 16px;
        }

        /* Additional styling for agent badge */
        .agent-badge {
            background: linear-gradient(90deg, #4568dc, #6a3093);
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            margin-left: 10px;
            vertical-align: middle;
        }
    </style>
    """, unsafe_allow_html=True)
