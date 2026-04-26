page_bg_css = """
<style>
/* --- Custom Gradient Background (Soft Mint to Pale Blue) --- */
.stApp {
    background: linear-gradient(135deg, #e0fcf5 0%, #E6E6FA 40%, #ffffff 100%) !important;
    background-attachment: fixed !important;
}

/* --- STUBBORN SIDEBAR FIX --- */
/* Target the outer wrapper */
[data-testid="stSidebar"] {
    background-color: transparent !important;
}

/* Streamlit hides its default background color on this exact inner div. 
   We will force a matching vertical gradient onto it! */
[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, #e0fcf5 0%, #f9e6ff 100%) !important;
    border-right: 1px solid rgba(0,0,0,0.05) !important; 
}

/* --- STRICT SCROLLBAR REMOVAL --- */
::-webkit-scrollbar { 
    width: 0px !important; 
    height: 0px !important; 
    display: none !important; 
    background: transparent !important; 
}
html, body, .stApp, .main, .block-container { 
    -ms-overflow-style: none !important; 
    scrollbar-width: none !important; 
}

/* --- FORM BORDERS (For Login and Seller Dashboard) --- */
[data-testid="stForm"] {
    border: 2px solid #d5d9d9 !important;
    border-radius: 6px !important;
    background-color: #ffffff !important;
    padding: 1rem !important;
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    box-shadow: 0 2px 4px 0 rgba(0,0,0,.05) !important;
}

/* Make inputs look modern */
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    border-radius: 4px;
    border: 1px solid #e0e0e0;
}

/* --- "ADD TO CART" BUTTON --- */
.stButton > button[kind="primary"] {
    background-color: #ff9f00 !important;
    color: white !important;
    border: none !important;
    border-radius: 2px !important;
    font-size: 15px !important;
    font-weight: bold !important;
    box-shadow: 0 1px 2px 0 rgba(0,0,0,.2) !important;
    padding: 0.4rem 1rem !important;
    transition: box-shadow 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 2px 4px 0 rgba(0,0,0,.3) !important;
}

.block-container { 
    padding-top: 1rem !important; 
    padding-bottom: 0.9rem !important; 
}
[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Product Container */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: white;
    border-radius: 4px;
    border: 1px solid #e0e0e0 !important;
    box-shadow: 0 2px 4px 0 rgba(0,0,0,.05);
    margin-bottom: 5px;
}
</style>
"""