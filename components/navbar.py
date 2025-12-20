import streamlit as st
import textwrap

def inject_custom_navbar():
    # Force Light Mode Colors (As per user preference "Remove darkness")
    nav_bg = "rgba(255, 255, 255, 0.9)" # White transparent
    nav_border = "rgba(0, 0, 0, 0.1)"
    text_color = "#0f172a" # Dark Slate
    btn_hover_bg = "rgba(0, 0, 0, 0.05)"
    premium_border = "rgba(79, 70, 229, 0.5)" # Indigo tint

    # Get current page if needed for other logic, but removed theme toggling vars
    # current_page = st.query_params.get("page", "home")
    
    # Logic for Navigation Links (Simplified - no more theme params)
    
    navbar_html = f"""
<style>
    /* Hide Default Streamlit Header */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    
    /* Adjust Main Content Padding so it's not hidden behind navbar */
    .main .block-container {{
        padding-top: 90px !important; /* Navbar (70px) + 20px buffer */
        padding-bottom: 20px !important;
    }}

    /* Custom Navbar Container */
    .custom-navbar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background: {nav_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid {nav_border};
        z-index: 999999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 40px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: background 0.5s ease, border-color 0.5s ease;
    }}

    /* Brand Logo/Text as Link */
    .nav-brand {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: {text_color};
        letter-spacing: -0.5px;
        text-decoration: none !important;
        cursor: pointer;
        transition: opacity 0.2s;
    }}
    .nav-brand:hover {{
        opacity: 0.8;
        text-decoration: none !important;
    }}

    /* Menu Container */
    .nav-menu {{
        display: flex;
        gap: 12px;
        align-items: center;
        height: 40px; /* Explicit height for alignment */
    }}

    /* Pill Buttons */
    .nav-btn {{
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: {text_color};
        background: transparent;
        padding: 8px 18px;
        border-radius: 9999px; /* Pill Shape */
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid {premium_border};
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .nav-btn:hover {{
        background: {btn_hover_bg};
        transform: scale(1.05);
        color: {text_color} !important; /* Ensure text color stays */
        text-decoration: none !important;
    }}

    /* Premium Button */
    .nav-btn-premium {{
        font-weight: 600;
        border: 1px solid {premium_border};
        color: {text_color};
    }}
    
    .nav-btn-premium:hover {{
        background: {premium_border}; 
        color: white !important;
        border-color: transparent;
    }}

    /* Disclaimer Text */
    .nav-disclaimer {{
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        color: rgba(148, 163, 184, 0.8); /* Slate 400 with opacity */
        font-weight: 400;
        margin-top: -2px;
        letter-spacing: 0.2px;
        max-width: 400px;
        line-height: 1.2;
    }}

    /* Mobile Responsive Breakpoint */
    @media (max-width: 768px) {{
        .custom-navbar {{
            padding: 0 16px; /* Smaller horizontal padding */
            height: 60px; /* Slightly shorter navbar */
        }}
        
        .nav-brand {{
            font-size: 18px; /* Smaller brand text */
        }}
        
        .nav-disclaimer {{
            display: none; /* Hide disclaimer on mobile to save space, or make very small */
        }}

        .main .block-container {{
           padding-top: 80px !important; /* Adjust content padding for shorter navbar */
        }}

        /* Scrollable Menu for Mobile */
        .nav-menu {{
            gap: 8px;
            overflow-x: auto; /* Enable horizontal scrolling */
            padding-right: 4px;
            -ms-overflow-style: none;  /* Hide scrollbar IE/Edge */
            scrollbar-width: none;  /* Hide scrollbar Firefox */
        }}
        .nav-menu::-webkit-scrollbar {{
            display: none; /* Hide scrollbar Chrome/Safari/Opera */
        }}
        
        .nav-btn {{
            font-size: 13px;
            padding: 6px 12px;
            white-space: nowrap; /* Prevent button text wrapping */
        }}
    }}
</style>

<div class="custom-navbar">
        <a class="nav-brand" href="?page=home" target="_self">Trading Tool</a>
        <div class="nav-menu">
            <a class="nav-btn" href="?page=trader_zone" target="_self">₹ Trader Zone</a>
            <a class="nav-btn" href="?page=about_us" target="_self">About Us</a>
            <!-- Theme Toggle Removed -->
            <a class="nav-btn nav-btn-premium" href="#">Premium</a>
    </div>
</div>
"""
    st.markdown(navbar_html, unsafe_allow_html=True)
