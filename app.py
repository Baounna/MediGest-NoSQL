import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from db_manager import DBManager

# --- Configuration de la page ---
st.set_page_config(
    page_title="MediGest - Gestion Cabinet Medical",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Theme ---
st.markdown("""
<style>
    /* === Global Theme === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary: #0077B6;
        --primary-dark: #005F8A;
        --primary-light: #90E0EF;
        --accent: #00B4D8;
        --accent-glow: rgba(0, 180, 216, 0.15);
        --bg-main: #F0F4F8;
        --bg-card: #FFFFFF;
        --bg-sidebar-top: #023E58;
        --bg-sidebar-mid: #035E7B;
        --bg-sidebar-bot: #0077B6;
        --text-primary: #1B2A4A;
        --text-secondary: #5A6A85;
        --text-muted: #8896AB;
        --border: #E2E8F0;
        --border-light: #EDF2F7;
        --success: #059669;
        --success-bg: #ECFDF5;
        --danger: #DC2626;
        --danger-bg: #FEF2F2;
        --warning: #D97706;
        --warning-bg: #FFFBEB;
        --neutral: #6B7280;
        --neutral-bg: #F3F4F6;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 14px rgba(0,0,0,0.08);
        --shadow-lg: 0 10px 30px rgba(0,0,0,0.1);
        --radius: 12px;
        --radius-sm: 8px;
        --radius-lg: 16px;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--bg-main);
    }

    /* === Sidebar === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(175deg, var(--bg-sidebar-top) 0%, var(--bg-sidebar-mid) 45%, var(--bg-sidebar-bot) 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio label span,
    section[data-testid="stSidebar"] .stRadio label p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {
        color: #CAE9F5 !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        padding: 10px 16px !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: rgba(0,180,216,0.2) !important;
        border-color: rgba(0,180,216,0.4) !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,255,255,0.1) !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12) !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        color: white !important;
        backdrop-filter: blur(8px);
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.22);
        border-color: rgba(255,255,255,0.35);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    section[data-testid="stSidebar"] input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        color: white !important;
        border-radius: var(--radius-sm) !important;
    }
    section[data-testid="stSidebar"] input::placeholder {
        color: rgba(255,255,255,0.4) !important;
    }
    section[data-testid="stSidebar"] input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    /* === Metric Cards === */
    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-left: 4px solid var(--primary);
        padding: 20px 24px;
        border-radius: var(--radius);
        box-shadow: var(--shadow-sm);
        transition: all 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    div[data-testid="stMetric"] label {
        color: var(--text-muted) !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
    }

    /* === Buttons === */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white !important;
        border: none;
        border-radius: var(--radius-sm);
        padding: 0.55rem 1.4rem;
        font-weight: 600;
        font-size: 0.88rem;
        letter-spacing: 0.2px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0,119,182,0.25);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,119,182,0.35);
        background: linear-gradient(135deg, var(--primary-dark) 0%, #004A6E 100%);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* === Expanders === */
    details, details[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow-sm) !important;
        overflow: hidden !important;
        margin-bottom: 8px !important;
    }
    summary, details > summary, details[data-testid="stExpander"] > summary {
        font-weight: 600 !important;
        padding: 14px 20px !important;
        background: linear-gradient(135deg, #0077B6 0%, #035E7B 100%) !important;
    }
    summary *, details > summary *, details[data-testid="stExpander"] > summary * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }
    summary:hover, details > summary:hover {
        background: linear-gradient(135deg, #005F8A 0%, #023E58 100%) !important;
    }
    /* Expander body content */
    details > div, details[data-testid="stExpander"] > div {
        background: #FFFFFF !important;
    }

    /* === Forms === */
    div[data-testid="stForm"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 28px;
        box-shadow: var(--shadow-sm);
    }

    /* === Force light mode on main content === */
    .stApp, .main, .main .block-container {
        color: var(--text-primary) !important;
    }
    /* All text in main area */
    .main p, .main span, .main label, .main li, .main div,
    .main .stMarkdown, .main .stMarkdown p, .main .stMarkdown span,
    div[data-testid="stForm"] label,
    div[data-testid="stForm"] p,
    div[data-testid="stForm"] span,
    div[data-testid="stForm"] div,
    div[data-testid="stExpander"] div p,
    div[data-testid="stExpander"] div span,
    div[data-testid="stExpander"] div label,
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] span,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stMarkdownContainer"] strong,
    .stApp [data-testid="stMarkdownContainer"] em,
    .stApp [data-testid="stMarkdownContainer"] h1,
    .stApp [data-testid="stMarkdownContainer"] h2,
    .stApp [data-testid="stMarkdownContainer"] h3,
    .stApp [data-testid="stMarkdownContainer"] h4,
    .stApp [data-testid="stMarkdownContainer"] h5 {
        color: var(--text-primary) !important;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: var(--text-primary) !important;
    }
    .stCaption, .stApp .stCaption, .stApp .stCaption p {
        color: var(--text-muted) !important;
    }

    /* Override sidebar text back to light (since main override is too broad) */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] li {
        color: #CAE9F5 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        color: #FFFFFF !important;
    }

    /* Expander summary text stays white */
    details[data-testid="stExpander"] summary span,
    details[data-testid="stExpander"] summary p,
    details[data-testid="stExpander"] summary div {
        color: #FFFFFF !important;
    }

    /* === Inputs — force white background everywhere === */
    input, textarea, select {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stNumberInput input,
    .stDateInput > div > div > input,
    .stDateInput input,
    .stTimeInput > div > div > input,
    .stTimeInput input {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-sm) !important;
        border: 1.5px solid var(--border) !important;
        transition: all 0.2s ease;
    }
    /* Date input wrapper divs */
    .stDateInput > div,
    .stDateInput > div > div,
    .stDateInput [data-baseweb="input"],
    .stDateInput [data-baseweb="input"] div,
    .stTimeInput > div,
    .stTimeInput > div > div,
    .stTimeInput [data-baseweb="input"],
    .stTimeInput [data-baseweb="input"] div,
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="base-input"] > div {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
    }
    /* Number input wrapper */
    .stNumberInput > div,
    .stNumberInput > div > div,
    .stNumberInput [data-baseweb="input"],
    .stNumberInput [data-baseweb="input"] div {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
    }
    /* Focus states */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus,
    input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
        background-color: #FFFFFF !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder,
    input::placeholder {
        color: var(--text-muted) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stNumberInput label, .stDateInput label, .stTimeInput label,
    .stRadio label, .stCheckbox label {
        color: var(--text-primary) !important;
    }

    /* Form submit button */
    .stFormSubmitButton > button,
    div[data-testid="stForm"] .stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
    }

    /* === Override sidebar inputs back to dark style === */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-baseweb="input"] div,
    section[data-testid="stSidebar"] div[data-baseweb="base-input"],
    section[data-testid="stSidebar"] div[data-baseweb="base-input"] div {
        background-color: rgba(255,255,255,0.08) !important;
        color: white !important;
        border-color: rgba(255,255,255,0.18) !important;
    }

    /* === Selectbox === */
    .stSelectbox > div > div,
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-sm) !important;
        border: 1.5px solid var(--border) !important;
    }
    div[data-baseweb="select"] span {
        color: var(--text-primary) !important;
    }
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="menu"] li {
        color: var(--text-primary) !important;
    }
    div[data-baseweb="menu"] li:hover {
        background-color: var(--bg-main) !important;
    }

    /* === Dataframe === */
    .stDataFrame, .stDataFrame div, .stDataFrame table,
    .stDataFrame th, .stDataFrame td,
    .stDataFrame [data-testid="stDataFrameResizable"],
    div[data-testid="stDataFrame"] > div,
    div[data-testid="stDataFrame"] div[class*="glide"],
    div[data-testid="stDataFrame"] div[class*="cell"],
    div[data-testid="stDataFrame"] div[class*="header"] {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
    }

    /* === KILL ALL DARK BACKGROUNDS === */
    .main, .main .block-container,
    .stApp > div, .stApp > div > div,
    div[data-testid="stAppViewContainer"],
    div[data-testid="stAppViewContainer"] > div,
    div[data-testid="stHeader"],
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    .appview-container,
    .main > div {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
    }

    /* Force all generic dark divs to be light */
    .stApp [data-testid] {
        color: var(--text-primary);
    }

    /* Popover / dropdown menus */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > div,
    ul[role="listbox"],
    ul[role="listbox"] li,
    div[data-baseweb="select"] div[class*="option"] {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
    }

    /* Date picker / time picker */
    div[data-baseweb="calendar"],
    div[data-baseweb="calendar"] div,
    div[data-baseweb="datepicker"],
    div[data-baseweb="datepicker"] div {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
    }

    /* Tooltips / popovers */
    div[data-baseweb="tooltip"],
    div[data-baseweb="tooltip"] div {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }

    /* Streamlit popover content */
    div[data-testid="stPopover"] > div,
    div[data-testid="stPopoverBody"],
    div[data-testid="stPopoverBody"] > div {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
    }

    /* Bottom toolbar / footer bar */
    .stBottom, div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {
        background-color: var(--bg-main) !important;
    }

    /* Toast notifications */
    div[data-testid="stToast"],
    div[data-testid="stToast"] > div {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }

    /* Tabs content area */
    .stTabs, .stTabs > div,
    div[data-baseweb="tab-panel"] {
        background-color: transparent !important;
        color: var(--text-primary) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: var(--text-secondary) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
    }

    /* Number input buttons */
    .stNumberInput button {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        border-color: var(--border) !important;
    }

    /* Info/Success/Error/Warning boxes */
    div[data-testid="stAlert"] {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {
        color: var(--text-primary) !important;
    }

    /* Dividers */
    div[data-testid="stDivider"], .stDivider {
        background-color: var(--border) !important;
    }

    /* Deploy button area */
    div[data-testid="stToolbar"] button,
    div[data-testid="stToolbar"] span {
        color: var(--text-secondary) !important;
    }

    /* Table inside expanders */
    .stTable, .stTable th, .stTable td,
    table, table th, table td {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
        border-color: var(--border) !important;
    }
    table th {
        background-color: var(--bg-main) !important;
        font-weight: 600 !important;
    }

    /* Multiselect / tags */
    div[data-baseweb="tag"] {
        background-color: var(--primary) !important;
        color: white !important;
    }

    /* Radio button circles in main content */
    .main .stRadio > div > label > div:first-child {
        color: var(--primary) !important;
    }

    /* Any remaining svg icons */
    .main svg {
        fill: var(--text-secondary);
    }

    /* Streamlit column gaps */
    div[data-testid="stHorizontalBlock"] {
        color: var(--text-primary) !important;
    }

    /* Write text in columns */
    div[data-testid="stColumn"] p,
    div[data-testid="stColumn"] span,
    div[data-testid="stColumn"] label,
    div[data-testid="stColumn"] div {
        color: var(--text-primary) !important;
    }

    /* Fix sidebar column text back to light */
    section[data-testid="stSidebar"] div[data-testid="stColumn"] p,
    section[data-testid="stSidebar"] div[data-testid="stColumn"] span {
        color: #CAE9F5 !important;
    }

    /* === Custom Card === */
    .med-card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 28px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
        margin-bottom: 20px;
        transition: box-shadow 0.25s ease;
    }
    .med-card:hover {
        box-shadow: var(--shadow-md);
    }
    .med-card-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* === Status Badges === */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge::before {
        content: '';
        width: 7px;
        height: 7px;
        border-radius: 50%;
        display: inline-block;
    }
    .badge-confirmed {
        background: var(--success-bg);
        color: var(--success);
        border: 1px solid #A7F3D0;
    }
    .badge-confirmed::before { background: var(--success); }
    .badge-cancelled {
        background: var(--danger-bg);
        color: var(--danger);
        border: 1px solid #FECACA;
    }
    .badge-cancelled::before { background: var(--danger); }
    .badge-pending {
        background: var(--warning-bg);
        color: var(--warning);
        border: 1px solid #FDE68A;
    }
    .badge-pending::before { background: var(--warning); }
    .badge-absent {
        background: var(--neutral-bg);
        color: var(--neutral);
        border: 1px solid #D1D5DB;
    }
    .badge-absent::before { background: var(--neutral); }

    /* === KPI Grid === */
    .kpi-card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 24px 20px;
        text-align: center;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }
    .kpi-icon {
        font-size: 2rem;
        margin-bottom: 8px;
        filter: grayscale(0.1);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.78rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
        margin-top: 6px;
    }

    /* === Login Card === */
    .login-card {
        max-width: 440px;
        margin: 0 auto;
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 44px;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border);
        position: relative;
        overflow: hidden;
    }
    .login-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--accent), var(--primary-light));
    }
    .login-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    .login-subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1rem;
        margin-bottom: 24px;
        line-height: 1.5;
    }

    /* === Feature Cards (Landing) === */
    .feature-card {
        text-align: center;
        padding: 32px 20px;
        background: var(--bg-card);
        border-radius: var(--radius);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .feature-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 40px;
        height: 3px;
        background: var(--primary);
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-light);
    }
    .feature-card:hover::after {
        width: 60px;
    }
    .feature-icon {
        font-size: 2.8rem;
        margin-bottom: 14px;
    }
    .feature-title {
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 10px;
        font-size: 1.05rem;
    }
    .feature-desc {
        color: var(--text-secondary);
        font-size: 0.88rem;
        line-height: 1.5;
    }

    /* === Sidebar User Card === */
    .user-card {
        background: rgba(255,255,255,0.08);
        border-radius: var(--radius);
        padding: 18px;
        margin: 12px 0;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(12px);
        transition: background 0.2s ease;
    }
    .user-card:hover {
        background: rgba(255,255,255,0.12);
    }
    .user-avatar {
        width: 46px;
        height: 46px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent), var(--primary));
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 10px;
        box-shadow: 0 3px 10px rgba(0,180,216,0.3);
    }
    .user-name {
        color: #ffffff;
        font-weight: 600;
        font-size: 1rem;
    }
    .user-role {
        color: var(--primary-light);
        font-size: 0.82rem;
        font-weight: 500;
    }

    /* === Page Header === */
    .page-header {
        padding: 4px 0 20px 0;
        margin-bottom: 28px;
        border-bottom: none;
        position: relative;
    }
    .page-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        border-radius: 3px;
    }
    .page-header h2 {
        margin: 0;
        color: var(--text-primary);
        font-weight: 800;
        font-size: 1.6rem;
    }
    .page-header p {
        color: var(--text-secondary);
        margin: 6px 0 0 0;
        font-size: 0.95rem;
    }

    /* === Activity Log === */
    .activity-item {
        display: flex;
        align-items: flex-start;
        padding: 12px 0;
        border-bottom: 1px solid var(--border-light);
    }
    .activity-item:last-child {
        border-bottom: none;
    }
    .activity-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--primary);
        margin-top: 7px;
        margin-right: 14px;
        flex-shrink: 0;
        box-shadow: 0 0 0 3px var(--accent-glow);
    }
    .activity-text {
        font-size: 0.88rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }
    .activity-text strong {
        color: var(--text-primary);
    }
    .activity-time {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 3px;
    }

    /* === Footer === */
    .footer {
        text-align: center;
        padding: 24px 0;
        color: var(--text-muted);
        font-size: 0.82rem;
        margin-top: 48px;
        border-top: 1px solid var(--border);
        letter-spacing: 0.2px;
    }

    /* === Tabs/Radio Horizontal styling === */
    div[data-testid="stRadio"] > div {
        gap: 0 !important;
    }
    div[data-testid="stRadio"] > div > label {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        padding: 10px 22px !important;
        margin: 0 !important;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        color: var(--text-secondary) !important;
    }
    div[data-testid="stRadio"] > div > label:first-child {
        border-radius: var(--radius-sm) 0 0 var(--radius-sm);
    }
    div[data-testid="stRadio"] > div > label:last-child {
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    }
    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        border-color: var(--primary);
        box-shadow: 0 2px 8px rgba(0,119,182,0.3);
    }
    div[data-testid="stRadio"] > div > label:hover:not([data-checked="true"]) {
        background: var(--bg-main);
        border-color: var(--primary-light);
    }

    /* === Tabs === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        font-weight: 500;
        color: var(--text-secondary);
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
        font-weight: 600;
    }

    /* === Dataframe — force light === */
    .stDataFrame {
        border-radius: var(--radius) !important;
        overflow: hidden;
        border: 1px solid var(--border);
    }
    .stDataFrame iframe,
    .stDataFrame > div,
    .stDataFrame canvas,
    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrame"] > div,
    div[data-testid="stDataFrame"] > div > div,
    div[data-testid="stDataFrame"] [role="grid"],
    div[data-testid="stDataFrame"] [role="gridcell"],
    div[data-testid="stDataFrame"] [role="columnheader"],
    div[data-testid="stDataFrame"] [role="row"] {
        background-color: #FFFFFF !important;
        color: #1B2A4A !important;
    }

    /* === Plotly charts — force white === */
    .stPlotlyChart, .stPlotlyChart > div,
    .stPlotlyChart iframe,
    div[data-testid="stPlotlyChart"],
    div[data-testid="stPlotlyChart"] > div {
        background-color: #FFFFFF !important;
    }
    .js-plotly-plot, .plotly, .plot-container {
        background-color: #FFFFFF !important;
    }
    .modebar, .modebar-group {
        background-color: #FFFFFF !important;
    }
    .modebar-btn path {
        fill: #5A6A85 !important;
    }

    /* === Divider === */
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 20px 0;
    }

    /* === Scrollbar === */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-main);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }

    /* === Toast / Alerts === */
    .stAlert {
        border-radius: var(--radius-sm) !important;
        border-left-width: 4px !important;
    }

    /* === Popover === */
    div[data-testid="stPopover"] > div,
    div[data-testid="stPopover"] > div > div,
    div[data-testid="stPopoverBody"],
    div[data-testid="stPopoverBody"] > div,
    div[data-testid="stPopoverBody"] div {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    /* Popover trigger button */
    div[data-testid="stPopover"] > button,
    button[data-testid="stPopoverButton"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
    }

    /* === Hero gradient text === */
    .hero-title {
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.1;
    }
</style>
""", unsafe_allow_html=True)


# --- Initialisation ---
if 'db' not in st.session_state:
    st.session_state.db = DBManager()

if 'user' not in st.session_state:
    st.session_state.user = None

# --- Utility: Status Badge ---
def status_badge(statut):
    """Returns styled HTML badge for appointment status."""
    if statut == "Confirme":
        return '<span class="badge badge-confirmed">Confirme</span>'
    elif "Annule" in statut or statut == "Annulé":
        return f'<span class="badge badge-cancelled">{statut}</span>'
    elif statut == "Absent":
        return '<span class="badge badge-absent">Absent</span>'
    else:
        return f'<span class="badge badge-pending">{statut}</span>'

# --- Fonctions Utilitaires UI ---

def login_form():
    """Affiche le formulaire de connexion dans la sidebar."""
    st.sidebar.markdown("### Connexion")
    username = st.sidebar.text_input("Identifiant", placeholder="Votre identifiant")
    password = st.sidebar.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")

    if st.sidebar.button("Se connecter", use_container_width=True):
        user = st.session_state.db.check_user(username, password)
        if user:
            st.session_state.user = {
                "username": user["username"],
                "role": user["role"]
            }
            st.rerun()
        else:
            st.sidebar.error("Identifiants incorrects")

def logout():
    """Deconnecte l'utilisateur."""
    st.session_state.db.log_action(st.session_state.user["username"], "LOGOUT", "Deconnexion utilisateur")
    st.session_state.user = None
    st.rerun()

def sidebar_user_card(user):
    """Displays styled user info in sidebar."""
    initials = user["username"][:2].upper()
    st.sidebar.markdown(f"""
    <div class="user-card">
        <div class="user-avatar">{initials}</div>
        <div class="user-name">{user["username"]}</div>
        <div class="user-role">{user["role"]}</div>
    </div>
    """, unsafe_allow_html=True)

def page_header(title, description=""):
    """Displays a styled page header."""
    desc_html = f"<p>{description}</p>" if description else ""
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)

# --- Dashboard View ---

def view_dashboard():
    """Dashboard with KPIs and recent activity."""
    page_header("Tableau de Bord", "Vue d'ensemble de votre cabinet")

    stats = st.session_state.db.get_dashboard_stats()

    # KPI Cards
    k1, k2, k3, k4 = st.columns(4)

    k1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">👥</div>
        <div class="kpi-value">{stats['total_patients']}</div>
        <div class="kpi-label">Patients</div>
    </div>
    """, unsafe_allow_html=True)

    k2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📅</div>
        <div class="kpi-value">{stats['today_appointments']}</div>
        <div class="kpi-label">RDV Aujourd'hui</div>
    </div>
    """, unsafe_allow_html=True)

    k3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🩺</div>
        <div class="kpi-value">{stats['active_practitioners']}</div>
        <div class="kpi-label">Praticiens</div>
    </div>
    """, unsafe_allow_html=True)

    k4.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📊</div>
        <div class="kpi-value">{stats['cancellation_rate']:.1f}%</div>
        <div class="kpi-label">Taux d'Annulation</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two columns: Quick Actions + Recent Activity
    col_actions, col_activity = st.columns([1, 2])

    with col_actions:
        st.markdown('<div class="med-card"><div class="med-card-header">Actions Rapides</div>', unsafe_allow_html=True)
        if st.button("📅 Nouveau Rendez-vous", use_container_width=True, key="dash_new_rdv"):
            st.session_state.current_accueil_tab = "➕ Nouveau Rendez-vous"
            if "nav_choice" in st.session_state:
                st.session_state.nav_choice = "Accueil"
            st.rerun()
        if st.button("👤 Ajouter un Patient", use_container_width=True, key="dash_new_pat"):
            st.session_state.current_accueil_tab = "👤 Gestion Patients"
            if "nav_choice" in st.session_state:
                st.session_state.nav_choice = "Accueil"
            st.rerun()
        if st.button("📋 Voir l'Agenda", use_container_width=True, key="dash_agenda"):
            st.session_state.current_accueil_tab = "📅 Agenda"
            if "nav_choice" in st.session_state:
                st.session_state.nav_choice = "Accueil"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_activity:
        st.markdown('<div class="med-card"><div class="med-card-header">Activite Recente</div>', unsafe_allow_html=True)
        if stats['recent_logs']:
            for log in stats['recent_logs']:
                ts = log.get('timestamp', '')
                if ts:
                    time_str = ts.strftime("%d/%m %H:%M")
                else:
                    time_str = ""
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-dot"></div>
                    <div>
                        <div class="activity-text"><strong>{log.get('user', '')}</strong> — {log.get('action', '')} : {log.get('details', '')}</div>
                        <div class="activity-time">{time_str}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune activite recente.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- Vues par Role ---

def view_accueil():
    page_header("Accueil & Secretariat", "Gestion des rendez-vous et des patients")

    # Navigation avec etat
    tabs_options = ["📅 Agenda", "👤 Gestion Patients", "➕ Nouveau Rendez-vous", "📋 Liste Globale"]

    if "current_accueil_tab" not in st.session_state:
        st.session_state.current_accueil_tab = tabs_options[0]

    try:
        current_index = tabs_options.index(st.session_state.current_accueil_tab)
    except ValueError:
        current_index = 0

    selected_tab = st.radio(
        "Navigation",
        tabs_options,
        horizontal=True,
        label_visibility="collapsed",
        index=current_index
    )

    if selected_tab != st.session_state.current_accueil_tab:
        st.session_state.current_accueil_tab = selected_tab
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Onglet Agenda ---
    if st.session_state.current_accueil_tab == "📅 Agenda":
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_date = st.date_input("Choisir une date", datetime.date.today())
            is_today = selected_date == datetime.date.today()
            if is_today:
                st.markdown('<span class="badge badge-confirmed">Aujourd\'hui</span>', unsafe_allow_html=True)

        appts = st.session_state.db.get_appointments(selected_date)

        if appts:
            df_appts = pd.DataFrame(appts)
            df_display = df_appts[["date_heure_debut", "date_heure_fin", "practitioner_name", "patient_nom", "motif", "statut", "_id", "duree_minutes"]]
            df_display["Heure"] = df_display["date_heure_debut"].dt.strftime("%H:%M")

            for index, row in df_display.iterrows():
                badge = status_badge(row['statut'])

                with st.expander(f"🕐 {row['Heure']} — {row['patient_nom']} (Dr. {row['practitioner_name']})"):
                    c_info1, c_info2, c_info3 = st.columns(3)
                    c_info1.markdown(f"**Motif:** {row['motif']}")
                    c_info2.markdown(f"**Statut:** {badge}", unsafe_allow_html=True)
                    c_info3.markdown(f"**Fin prevue:** {row['date_heure_fin'].strftime('%H:%M')}")

                    st.markdown("---")

                    c1, c2, c3 = st.columns(3)
                    if row['statut'] != "Annulé":
                        if c1.button("Annuler RDV", key=f"cancel_{row['_id']}"):
                            st.session_state.db.update_appointment_status(row['_id'], "Annulé", st.session_state.user["username"])
                            st.rerun()
                        if c2.button("Marquer Absent", key=f"absent_{row['_id']}"):
                            st.session_state.db.update_appointment_status(row['_id'], "Absent", st.session_state.user["username"])
                            st.rerun()

                    if c3.button("Supprimer", key=f"del_{row['_id']}"):
                        success, msg = st.session_state.db.delete_appointment(row['_id'], st.session_state.user["username"])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

                    st.markdown("#### Modifier / Decaler")
                    with st.form(key=f"edit_form_{row['_id']}"):
                        new_date = st.date_input("Nouvelle date", value=row['date_heure_debut'].date())
                        new_time = st.time_input("Nouvelle heure", value=row['date_heure_debut'].time())
                        new_duree = st.number_input("Duree (min)", value=int(row['duree_minutes']), step=15)

                        if st.form_submit_button("Sauvegarder les changements"):
                            new_start = datetime.datetime.combine(new_date, new_time)
                            success, msg = st.session_state.db.reschedule_appointment(
                                row['_id'], new_start, new_duree, st.session_state.user["username"]
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Aucun rendez-vous pour cette date.")

    # --- Onglet Gestion Patients ---
    elif st.session_state.current_accueil_tab == "👤 Gestion Patients":
        search_query = st.text_input("Rechercher un patient (Nom, Prenom)", "", placeholder="Tapez un nom ou prenom...")

        if search_query:
            results = st.session_state.db.search_patients(search_query)
            if results:
                st.success(f"{len(results)} patient(s) trouve(s)")
                for pat in results:
                    with st.expander(f"📂 {pat['nom']} {pat['prenom']}"):
                        if st.button("📅 Prendre RDV pour ce patient", key=f"btn_nav_rdv_{pat['_id']}"):
                            st.session_state.rdv_patient_results = [pat]
                            st.session_state.rdv_search_performed = True
                            st.session_state.current_accueil_tab = "➕ Nouveau Rendez-vous"
                            st.rerun()

                        ci1, ci2, ci3 = st.columns(3)
                        ci1.markdown(f"**Tel:** {pat.get('telephone', 'N/A')}")
                        ci2.markdown(f"**Email:** {pat.get('email', 'N/A')}")
                        ci3.markdown(f"**Assurance:** {pat.get('assurance', 'N/A')}")

                        st.markdown("**Notes Medicales:**")
                        st.info(pat.get('notes_medicales', 'Aucune note'))
                        st.markdown("**Historique Visites:**")
                        hist = pat.get('historique_visites', [])
                        if hist:
                            st.table(pd.DataFrame(hist))
                        else:
                            st.caption("Aucune visite enregistree")

                        with st.expander("Modifier les informations"):
                            with st.form(key=f"edit_patient_{pat['_id']}"):
                                e_nom = st.text_input("Nom", value=pat['nom'])
                                e_prenom = st.text_input("Prenom", value=pat['prenom'])
                                e_tel = st.text_input("Telephone", value=pat.get('telephone', ''))
                                e_email = st.text_input("Email", value=pat.get('email', ''))
                                e_assurance = st.text_input("Assurance", value=pat.get('assurance', ''))
                                e_notes = st.text_area("Notes Medicales", value=pat.get('notes_medicales', ''))

                                if st.form_submit_button("Enregistrer les modifications"):
                                    updated_data = {
                                        "nom": e_nom.upper(),
                                        "prenom": e_prenom.capitalize(),
                                        "telephone": e_tel,
                                        "email": e_email,
                                        "assurance": e_assurance,
                                        "notes_medicales": e_notes
                                    }
                                    success, msg = st.session_state.db.update_patient(pat['_id'], updated_data, st.session_state.user["username"])
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
            else:
                st.warning("Aucun patient trouve.")

        st.markdown("---")
        st.markdown('<div class="med-card"><div class="med-card-header">Creer un nouveau patient</div>', unsafe_allow_html=True)
        with st.form("new_patient_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom")
            prenom = c2.text_input("Prenom")
            tel = c1.text_input("Telephone")
            email = c2.text_input("Email")
            assurance = st.text_input("Numero Assurance / Secu")
            notes = st.text_area("Notes initiales")

            submitted = st.form_submit_button("Enregistrer Patient", use_container_width=True)
            if submitted:
                if nom and prenom:
                    success, msg = st.session_state.db.create_patient(
                        nom, prenom, tel, email, assurance, notes, st.session_state.user["username"]
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("Nom et Prenom obligatoires.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Onglet Nouveau RDV ---
    elif st.session_state.current_accueil_tab == "➕ Nouveau Rendez-vous":
        if 'rdv_patient_results' not in st.session_state:
            st.session_state.rdv_patient_results = []
        if 'rdv_search_performed' not in st.session_state:
            st.session_state.rdv_search_performed = False

        selected_patient_id = None

        st.markdown("##### 1. Rechercher et Selectionner le Patient")
        col_search, col_btn = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("Rechercher par Nom, Prenom ou ID", key="search_pat_input", placeholder="Ex: Dupont ou 65b...")
        with col_btn:
            st.write("")
            st.write("")
            if st.button("Rechercher", key="btn_search_trigger"):
                st.session_state.rdv_search_performed = True
                if search_query:
                    st.session_state.rdv_patient_results = st.session_state.db.search_patients(search_query)
                else:
                    st.session_state.rdv_patient_results = []
                    st.warning("Veuillez saisir une recherche.")

        if st.session_state.rdv_patient_results:
            pat_options = {f"{p['nom']} {p['prenom']} (Tel: {p.get('telephone', 'N/A')})": p['_id'] for p in st.session_state.rdv_patient_results}

            selected_label = st.selectbox("Patient selectionne :", list(pat_options.keys()), key="select_pat_final")
            selected_patient_id = pat_options[selected_label]

            if len(st.session_state.rdv_patient_results) == 1:
                st.info(f"Patient selectionne : **{selected_label}**")
        elif st.session_state.rdv_search_performed:
            st.error("Aucun patient trouve. Verifiez l'orthographe ou l'ID.")

        st.markdown("---")
        st.markdown("##### 2. Details du Rendez-vous")

        practitioners = st.session_state.db.get_practitioners()
        practitioner_names = [p["nom"] for p in practitioners]

        with st.form("new_appt_form"):
            practitioner = st.selectbox("Praticien", practitioner_names)
            col_d, col_t = st.columns(2)
            date_rdv = col_d.date_input("Date", datetime.date.today())
            time_rdv = col_t.time_input("Heure de debut", datetime.time(9, 0))
            duree = st.number_input("Duree (minutes)", min_value=15, max_value=120, value=30, step=15)
            motif = st.text_input("Motif de la consultation")

            submit_rdv = st.form_submit_button("Confirmer le Rendez-vous", use_container_width=True)

            if submit_rdv:
                if selected_patient_id:
                    start_datetime = datetime.datetime.combine(date_rdv, time_rdv)

                    success, msg = st.session_state.db.create_appointment(
                        selected_patient_id, practitioner, start_datetime, duree, motif, st.session_state.user["username"]
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("Veuillez selectionner un patient dans la liste ci-dessus.")

    # --- Onglet Liste Globale ---
    elif st.session_state.current_accueil_tab == "📋 Liste Globale":
        all_appts = st.session_state.db.get_appointments()
        practitioners = st.session_state.db.get_practitioners()

        if all_appts:
            df_all = pd.DataFrame(all_appts)

            for prac in practitioners:
                prac_name = prac["nom"]
                with st.expander(f"🩺 {prac_name} — {prac.get('specialite', 'Generaliste')}", expanded=True):
                    df_prac = df_all[df_all["practitioner_name"] == prac_name]

                    if not df_prac.empty:
                        df_prac = df_prac.sort_values(by="date_heure_debut")

                        h1, h2, h3, h4, h5 = st.columns([2, 3, 3, 2, 3])
                        h1.markdown("**Horaire**")
                        h2.markdown("**Patient**")
                        h3.markdown("**Motif**")
                        h4.markdown("**Statut**")
                        h5.markdown("**Actions**")
                        st.divider()

                        for idx, row in df_prac.iterrows():
                            c1, c2, c3, c4, c5 = st.columns([2, 3, 3, 2, 3])

                            start_str = row["date_heure_debut"].strftime("%d/%m %H:%M")
                            c1.write(f"{start_str}")
                            c2.write(f"{row['patient_nom']}")
                            c3.write(f"{row['motif']}")
                            c4.markdown(status_badge(row['statut']), unsafe_allow_html=True)

                            if "Annulé" not in row['statut']:
                                with c5:
                                    now = datetime.datetime.now()
                                    time_diff = row["date_heure_debut"] - now
                                    is_too_close = time_diff.total_seconds() < 1800

                                    if is_too_close:
                                        st.caption("Modification bloquee (<30min)")

                                    with st.popover("🕒 Retard"):
                                        delay_min = st.number_input("Minutes de retard", min_value=1, max_value=120, value=15, step=5, key=f"val_delay_{row['_id']}")
                                        if st.button("Appliquer", key=f"btn_apply_{row['_id']}"):
                                            new_start = row["date_heure_debut"] + datetime.timedelta(minutes=delay_min)
                                            success, msg = st.session_state.db.reschedule_appointment(
                                                row['_id'], new_start, row['duree_minutes'], st.session_state.user["username"]
                                            )
                                            if success:
                                                st.toast(f"Retard de {delay_min} min applique.")
                                                st.rerun()
                                            else:
                                                st.error(msg)

                                    if st.button("Absence Med.", key=f"doc_abs_{row['_id']}"):
                                        st.session_state.db.update_appointment_status(row['_id'], "Annulé (Medecin Absent)", st.session_state.user["username"])
                                        st.toast("RDV annule pour absence medecin.")
                                        st.rerun()
                            else:
                                c5.caption("Cloture")

                            st.divider()
                    else:
                        st.info(f"Aucun rendez-vous pour Dr. {prac_name}.")
        else:
            st.info("Aucun rendez-vous dans le systeme.")

def view_responsable():
    page_header("Statistiques & Analyses", "Indicateurs de performance du cabinet")

    stats = st.session_state.db.get_dashboard_stats()
    cancel_rate = stats['cancellation_rate']
    workload_data = st.session_state.db.get_stats_workload()

    # KPI Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Patients", stats['total_patients'])
    kpi2.metric("Total RDV", stats['total_appointments'])
    kpi3.metric("Taux d'Annulation", f"{cancel_rate:.1f}%")
    kpi4.metric("Praticiens Actifs", stats['active_practitioners'])

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="med-card"><div class="med-card-header">Charge par Medecin</div>', unsafe_allow_html=True)
        if workload_data:
            df_workload = pd.DataFrame(workload_data)
            fig = px.bar(
                df_workload, x="_id", y="count",
                labels={"_id": "Medecin", "count": "Nombre de RDV"},
                color_discrete_sequence=["#0077B6"]
            )
            fig.update_layout(
                template="plotly_white",
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(family="Inter", color="#1B2A4A", size=13),
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(tickfont=dict(color="#1B2A4A", size=12), title_font=dict(color="#1B2A4A", size=13), gridcolor="#E2E8F0", linecolor="#1B2A4A"),
                yaxis=dict(tickfont=dict(color="#1B2A4A", size=12), title_font=dict(color="#1B2A4A", size=13), gridcolor="#E2E8F0", linecolor="#1B2A4A"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de donnees.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="med-card"><div class="med-card-header">RDV par Jour de la Semaine</div>', unsafe_allow_html=True)
        if stats['appts_by_day']:
            df_dow = pd.DataFrame(stats['appts_by_day'])
            fig2 = px.bar(
                df_dow, x="jour", y="count",
                labels={"jour": "Jour", "count": "Nombre de RDV"},
                color_discrete_sequence=["#0077B6"]
            )
            fig2.update_layout(
                template="plotly_white",
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(family="Inter", color="#1B2A4A", size=13),
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(tickfont=dict(color="#1B2A4A", size=12), title_font=dict(color="#1B2A4A", size=13), gridcolor="#E2E8F0", linecolor="#1B2A4A"),
                yaxis=dict(tickfont=dict(color="#1B2A4A", size=12), title_font=dict(color="#1B2A4A", size=13), gridcolor="#E2E8F0", linecolor="#1B2A4A"),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Pas assez de donnees pour la repartition.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Patient Growth
    st.markdown('<div class="med-card"><div class="med-card-header">Croissance des Patients</div>', unsafe_allow_html=True)
    if stats['patient_growth']:
        df_growth = pd.DataFrame(stats['patient_growth'])
        df_growth['period'] = df_growth['_id'].apply(lambda x: f"{x['year']}-{x['month']:02d}")
        df_growth['cumulative'] = df_growth['count'].cumsum()
        fig3 = px.area(
            df_growth, x="period", y="cumulative",
            labels={"period": "Periode", "cumulative": "Total Patients"},
            color_discrete_sequence=["#0077B6"]
        )
        fig3.update_layout(
            template="plotly_white",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Inter", color="#1B2A4A", size=13),
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(tickfont=dict(color="#1B2A4A", size=12), title_font=dict(color="#1B2A4A", size=13), gridcolor="#E2E8F0", linecolor="#1B2A4A"),
            yaxis=dict(tickfont=dict(color="#1B2A4A", size=12), title_font=dict(color="#1B2A4A", size=13), gridcolor="#E2E8F0", linecolor="#1B2A4A"),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Pas assez de donnees pour la croissance.")
    st.markdown('</div>', unsafe_allow_html=True)

def view_admin():
    page_header("Administration", "Gestion des utilisateurs, praticiens et logs")

    tab_users, tab_practitioners, tab_logs = st.tabs(["Utilisateurs", "Praticiens", "Logs Systeme"])

    with tab_users:
        st.markdown('<div class="med-card"><div class="med-card-header">Utilisateurs existants</div>', unsafe_allow_html=True)
        users = st.session_state.db.get_all_users()
        st.dataframe(pd.DataFrame(users), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="med-card"><div class="med-card-header">Creer un nouvel utilisateur</div>', unsafe_allow_html=True)
        with st.form("create_user"):
            new_user = st.text_input("Nouvel Identifiant")
            new_pass = st.text_input("Mot de passe", type="password")
            new_role = st.selectbox("Role", ["Accueil", "Responsable", "Administrateur"])

            if st.form_submit_button("Creer", use_container_width=True):
                if st.session_state.db.create_user(new_user, new_pass, new_role, st.session_state.user["username"]):
                    st.success(f"Utilisateur {new_user} cree !")
                    st.rerun()
                else:
                    st.error("Erreur lors de la creation.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_practitioners:
        st.markdown('<div class="med-card"><div class="med-card-header">Praticiens</div>', unsafe_allow_html=True)
        practitioners = st.session_state.db.get_practitioners()

        if practitioners:
            for p in practitioners:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.write(f"**{p['nom']}**")
                col2.write(f"_{p['specialite']}_")

                with col3.popover("Editer"):
                    with st.form(key=f"edit_prac_{p['_id']}"):
                        e_nom = st.text_input("Nom", value=p['nom'])
                        e_spec = st.text_input("Specialite", value=p['specialite'])
                        if st.form_submit_button("Enregistrer"):
                            updated_data = {"nom": e_nom, "specialite": e_spec}
                            success, msg = st.session_state.db.update_practitioner(p['_id'], updated_data, st.session_state.user["username"])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                if col4.button("Supprimer", key=f"del_prac_{p['_id']}"):
                    success, msg = st.session_state.db.delete_practitioner(p['_id'], st.session_state.user["username"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.info("Aucun praticien enregistre.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="med-card"><div class="med-card-header">Ajouter un Praticien</div>', unsafe_allow_html=True)
        with st.form("add_practitioner"):
            nom_prac = st.text_input("Nom (ex: Dr. House)")
            spec_prac = st.text_input("Specialite (ex: Diagnosticien)")

            if st.form_submit_button("Ajouter", use_container_width=True):
                if nom_prac and spec_prac:
                    success, msg = st.session_state.db.create_practitioner(nom_prac, spec_prac, st.session_state.user["username"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Tous les champs sont requis.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_logs:
        st.markdown('<div class="med-card"><div class="med-card-header">Journal d\'audit</div>', unsafe_allow_html=True)
        logs = st.session_state.db.get_logs()
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("Aucun log disponible.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- Point d'entree Principal ---

def main():
    if st.session_state.db.db is None:
        st.error("Impossible de se connecter a la base de donnees. Verifiez que MongoDB est lance.")
        return

    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 20px 0 12px 0;">
            <div style="width: 52px; height: 52px; border-radius: 14px; background: linear-gradient(135deg, #00B4D8, #90E0EF); display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px; box-shadow: 0 4px 14px rgba(0,180,216,0.3);">
                <span style="font-size: 1.6rem;">🏥</span>
            </div>
            <h1 style="margin: 0; font-size: 1.5rem; font-weight: 800; color: white; letter-spacing: -0.3px;">MediGest</h1>
            <p style="color: #90E0EF; font-size: 0.8rem; margin: 4px 0 0 0; font-weight: 400; letter-spacing: 0.5px;">GESTION DE CABINET</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.user:
            sidebar_user_card(st.session_state.user)
            st.markdown("---")

            role = st.session_state.user["role"]

            if role == "Administrateur":
                nav_options = ["Dashboard", "Accueil", "Statistiques", "Administration"]
            elif role == "Responsable":
                nav_options = ["Dashboard", "Accueil", "Statistiques"]
            else:
                nav_options = ["Dashboard", "Accueil"]

            view_choice = st.radio("Navigation", nav_options, key="nav_choice", label_visibility="collapsed")

            st.markdown("---")
            if st.button("Deconnexion", use_container_width=True):
                logout()
        else:
            login_form()

    # Routing
    if st.session_state.user:
        view_choice = st.session_state.get("nav_choice", "Dashboard")

        if view_choice == "Dashboard":
            view_dashboard()
        elif view_choice == "Accueil":
            view_accueil()
        elif view_choice == "Statistiques":
            view_responsable()
        elif view_choice == "Administration":
            view_admin()
    else:
        # Landing page
        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            st.markdown("""
            <div style="text-align: center; padding: 40px 0 20px 0;">
                <div style="width: 72px; height: 72px; border-radius: 18px; background: linear-gradient(135deg, #0077B6, #00B4D8); display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px; box-shadow: 0 8px 24px rgba(0,119,182,0.25);">
                    <span style="font-size: 2.2rem; filter: brightness(1.1);">🏥</span>
                </div>
                <h1 class="hero-title" style="margin: 8px 0 0 0;">MediGest</h1>
                <p style="font-size: 1.1rem; color: #5A6A85; margin-top: 8px; font-weight: 400;">Plateforme intelligente de gestion de cabinet medical</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="login-card">
                <div class="login-subtitle">Connectez-vous via le panneau lateral pour acceder au systeme</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("""
            <div style="background: linear-gradient(135deg, #EFF6FF, #F0F9FF); border-radius: 10px; padding: 16px 20px; border: 1px solid #BFDBFE; text-align: center;">
                <p style="margin: 0; color: #1E40AF; font-size: 0.88rem; font-weight: 500;">
                    Identifiants par defaut : <code style="background: rgba(0,119,182,0.1); padding: 2px 8px; border-radius: 4px; font-weight: 600;">admin</code> / <code style="background: rgba(0,119,182,0.1); padding: 2px 8px; border-radius: 4px; font-weight: 600;">admin123</code>
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Feature highlights
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📅</div>
                <div class="feature-title">Gestion d'Agenda</div>
                <div class="feature-desc">Planifiez et gerez les rendez-vous avec detection automatique des conflits</div>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">👥</div>
                <div class="feature-title">Dossiers Patients</div>
                <div class="feature-desc">Base de donnees complete avec historique des visites et notes medicales</div>
            </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Analyses & KPIs</div>
                <div class="feature-desc">Tableaux de bord temps reel avec indicateurs de performance</div>
            </div>
            """, unsafe_allow_html=True)

        # Footer
        st.markdown("""
        <div class="footer">
            <span style="font-weight: 600; color: #5A6A85;">MediGest</span> v2.0 &bull; MongoDB &bull; Streamlit &bull; Python
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
