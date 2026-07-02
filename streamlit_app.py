import html
import re
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from utils.data_loader import load_energy_data, load_occupancy_data
from agents.context_agent import ContextAgent
from agents.investigation_agent import InvestigationAgent
from agents.rootcause_agent import RootCauseAgent
from agents.recommendation_agent import RecommendationAgent
from agents.savings_agent import SavingsAgent
from agents.sustainability_score_agent import SustainabilityScoreAgent
from agents.executive_summary_agent import ExecutiveSummaryAgent
from agents.gemini_report_agent import GeminiReportAgent
from agents.confidence_agent import ConfidenceAgent

st.set_page_config(
    page_title="EcoMind AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  DESIGN SYSTEM & GLOBAL CSS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

    /* ── Reset & base ── */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stApp {
        background: linear-gradient(145deg, #0d1117 0%, #0a1628 40%, #061c12 100%) !important;
        min-height: 100vh;
    }
    #MainMenu, footer, header { visibility: hidden; }
    section[data-testid="stSidebar"]      { display: none !important; }
    button[data-testid="collapsedControl"] { display: none !important; }
    .block-container {
        padding-top: 1.5rem !important;
        max-width: 1400px !important;
    }
    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #1e4d34; border-radius: 99px; }

    /* ══════════════════════════════════════
       HEADER
    ══════════════════════════════════════ */
    .em-hero {
        position: relative;
        text-align: center;
        padding: 3rem 1rem 2.5rem;
        overflow: hidden;
        border-radius: 24px;
        margin-bottom: 1.75rem;
        background: linear-gradient(135deg, #062d1a 0%, #0a2540 55%, #062d1a 100%);
        border: 1px solid rgba(52, 211, 153, 0.15);
        box-shadow: 0 0 80px rgba(5, 150, 105, 0.18), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .em-hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background:
            radial-gradient(ellipse 600px 200px at 50% -60px, rgba(16,185,129,0.18) 0%, transparent 70%),
            radial-gradient(ellipse 300px 300px at 20% 120%, rgba(5,150,105,0.1) 0%, transparent 60%),
            radial-gradient(ellipse 300px 300px at 80% 120%, rgba(16,185,129,0.08) 0%, transparent 60%);
        pointer-events: none;
    }
    .em-hero-grid {
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(52,211,153,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(52,211,153,0.04) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
    }
    .em-hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 5px 14px;
        background: rgba(5, 150, 105, 0.18);
        border: 1px solid rgba(52, 211, 153, 0.35);
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #34d399;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
    }
    .em-hero h1 {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ecfdf5 30%, #6ee7b7 70%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.6rem;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .em-hero p {
        font-size: 1.05rem;
        color: rgba(167, 243, 208, 0.75);
        font-weight: 400;
        margin: 0;
        letter-spacing: 0.01em;
    }
    .em-live-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 20px;
        background: rgba(5, 150, 105, 0.15);
        border: 1px solid rgba(52, 211, 153, 0.3);
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        color: #6ee7b7;
        margin-top: 1.25rem;
        backdrop-filter: blur(10px);
        letter-spacing: 0.03em;
    }
    .em-live-dot {
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 8px #22c55e;
        animation: em-pulse 2s infinite;
    }
    @keyframes em-pulse {
        0%, 100% { opacity: 1; transform: scale(1);   box-shadow: 0 0 8px  #22c55e; }
        50%       { opacity: 0.6; transform: scale(1.3); box-shadow: 0 0 16px #22c55e; }
    }

    /* ══════════════════════════════════════
       STATUS STRIP
    ══════════════════════════════════════ */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 20px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        font-size: 0.84rem;
        font-weight: 600;
        color: rgba(167,243,208,0.8);
        backdrop-filter: blur(12px);
        transition: border-color 0.2s;
    }
    .status-pill b { color: #ecfdf5; }
    .status-pill:hover { border-color: rgba(52,211,153,0.35); }

    /* ══════════════════════════════════════
       METRIC CARDS
    ══════════════════════════════════════ */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(52, 211, 153, 0.15) !important;
        border-radius: 18px !important;
        padding: 1.2rem 1.3rem !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04) !important;
        backdrop-filter: blur(16px) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
        position: relative;
        overflow: hidden;
    }
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #059669, #10b981, transparent);
        opacity: 0.6;
        border-radius: 18px 18px 0 0;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 16px 48px rgba(5,150,105,0.2), 0 4px 16px rgba(0,0,0,0.4) !important;
        border-color: rgba(52, 211, 153, 0.4) !important;
    }
    div[data-testid="stMetric"] label {
        color: rgba(167,243,208,0.65) !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ecfdf5 !important;
        font-weight: 800 !important;
        font-size: 1.75rem !important;
        letter-spacing: -0.02em !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: rgba(167,243,208,0.6) !important;
        font-size: 0.8rem !important;
    }

    /* ══════════════════════════════════════
       CONTAINERS / CARDS
    ══════════════════════════════════════ */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.7) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(52, 211, 153, 0.12) !important;
        box-shadow: 0 4px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04) !important;
        padding: 0.75rem 1rem !important;
        backdrop-filter: blur(16px) !important;
        transition: border-color 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(52, 211, 153, 0.25) !important;
    }

    /* ══════════════════════════════════════
       TABS
    ══════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15,23,42,0.6);
        justify-content: center;
        width: 100%;
        border-bottom: none;
        padding: 6px;
        border-radius: 18px;
        border: 1px solid rgba(52,211,153,0.1);
        backdrop-filter: blur(12px);
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] { display: none; }
    .stTabs [data-baseweb="tab"] {
        flex: 1;
        max-width: 230px;
        height: auto !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        padding: 0.85rem 0.5rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: rgba(167,243,208,0.55) !important;
        justify-content: center;
        transition: all 0.25s ease;
        letter-spacing: 0.01em;
    }
    .stTabs [data-baseweb="tab"]:hover {
        border-color: rgba(52,211,153,0.25) !important;
        color: #6ee7b7 !important;
        background: rgba(5,150,105,0.08) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #059669 0%, #0d9488 50%, #10b981 100%) !important;
        color: #ffffff !important;
        border-color: transparent !important;
        box-shadow: 0 4px 20px rgba(5,150,105,0.4), 0 0 0 1px rgba(52,211,153,0.3) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
        animation: em-fadein 0.4s cubic-bezier(0.22, 1, 0.36, 1);
    }
    @keyframes em-fadein {
        from { opacity: 0; transform: translateY(10px) scale(0.99); }
        to   { opacity: 1; transform: translateY(0)   scale(1); }
    }

    /* ══════════════════════════════════════
       SECTION TITLE
    ══════════════════════════════════════ */
    .section-title {
        color: #ecfdf5 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-left: 3px solid #10b981;
        padding-left: 0.65rem;
        margin: 0.5rem 0 1rem !important;
        letter-spacing: 0.01em;
    }

    /* ══════════════════════════════════════
       TEXT ELEMENTS
    ══════════════════════════════════════ */
    h5, h4, h3, h2 { color: #ecfdf5 !important; }
    p, li, span { color: rgba(203,213,225,0.85) !important; }
    .stCaption, [data-testid="stCaptionContainer"] {
        color: rgba(167,243,208,0.55) !important;
        font-size: 0.78rem !important;
    }

    /* ══════════════════════════════════════
       PROGRESS BAR
    ══════════════════════════════════════ */
    .stProgress > div > div {
        background: linear-gradient(90deg, #059669 0%, #10b981 50%, #34d399 100%) !important;
        border-radius: 999px;
        box-shadow: 0 0 12px rgba(16,185,129,0.4);
    }
    .stProgress > div {
        background: rgba(15,23,42,0.6) !important;
        border-radius: 999px;
        border: 1px solid rgba(52,211,153,0.15);
    }

    /* ══════════════════════════════════════
       ALERTS / INFO BOXES
    ══════════════════════════════════════ */
    .stAlert {
        border-radius: 14px !important;
        background: rgba(15,23,42,0.6) !important;
        border: 1px solid rgba(52,211,153,0.2) !important;
        backdrop-filter: blur(12px) !important;
    }
    .stAlert p { color: #d1fae5 !important; }
    .stAlert[data-baseweb="notification"][kind="positive"],
    [data-testid="stNotificationContent"].success {
        background: rgba(5,46,22,0.7) !important;
        border-color: rgba(16,185,129,0.35) !important;
    }
    .stAlert[kind="negative"]  { border-color: rgba(239,68,68,0.3) !important; }
    .stAlert[kind="warning"]   { border-color: rgba(245,158,11,0.3) !important; }

    /* ══════════════════════════════════════
       SLIDER & INPUTS  — teal/cyan accent
    ══════════════════════════════════════ */
    .stSlider [data-baseweb="slider"] div { background: #0891b2 !important; }
    .stSlider [data-baseweb="thumb"] {
        background: linear-gradient(135deg, #06b6d4, #0891b2) !important;
        box-shadow: 0 0 0 3px rgba(6,182,212,0.25), 0 0 12px rgba(6,182,212,0.5) !important;
        border: 2px solid #22d3ee !important;
    }
    .stSlider [data-baseweb="track"] { background: rgba(6,182,212,0.15) !important; }
    div[data-baseweb="input"] {
        background: rgba(15,23,42,0.7) !important;
        border: 1px solid rgba(6,182,212,0.3) !important;
        border-radius: 10px !important;
        color: #ecfdf5 !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: rgba(6,182,212,0.65) !important;
        box-shadow: 0 0 0 3px rgba(6,182,212,0.15) !important;
    }
    input[type="number"], input[type="text"] {
        color: #ecfdf5 !important;
        background: transparent !important;
    }
    label[data-testid="stWidgetLabel"] p { color: rgba(167,243,208,0.75) !important; }

    /* ══════════════════════════════════════
       CONTROL PANEL — highlighted card
    ══════════════════════════════════════ */
    .control-card {
        background: linear-gradient(135deg, rgba(8,28,50,0.85), rgba(4,30,22,0.85)) !important;
        border: 1px solid rgba(6,182,212,0.25) !important;
        border-radius: 20px !important;
        padding: 1.25rem 1.4rem !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 4px 32px rgba(6,182,212,0.08), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    }
    .control-header {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #22d3ee;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .control-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(6,182,212,0.3), transparent);
    }
    .whatif-card {
        background: linear-gradient(135deg, rgba(8,28,50,0.85), rgba(15,10,40,0.85)) !important;
        border: 1px solid rgba(139,92,246,0.25) !important;
        border-radius: 20px !important;
        padding: 1.25rem 1.4rem !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 4px 32px rgba(139,92,246,0.08), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    }
    .whatif-header {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #a78bfa;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .whatif-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(139,92,246,0.3), transparent);
    }

    /* ══════════════════════════════════════
       STATUS / EXPANDER
    ══════════════════════════════════════ */
    [data-testid="stExpander"] {
        background: rgba(15,23,42,0.6) !important;
        border: 1px solid rgba(52,211,153,0.15) !important;
        border-radius: 14px !important;
    }
    [data-testid="stStatusWidget"] {
        background: rgba(15,23,42,0.6) !important;
        border: 1px solid rgba(52,211,153,0.2) !important;
        border-radius: 14px !important;
    }

    /* ══════════════════════════════════════
       KV ROW
    ══════════════════════════════════════ */
    .kv-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(52,211,153,0.07);
    }
    .kv-row:last-child { border-bottom: none; }
    .kv-key {
        font-size: 0.78rem;
        font-weight: 600;
        color: rgba(167,243,208,0.55);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kv-val {
        font-size: 0.9rem;
        font-weight: 700;
        color: #d1fae5;
    }

    /* ══════════════════════════════════════
       RECOMMENDATION CARD
    ══════════════════════════════════════ */
    .rec-card {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 14px;
        background: rgba(5,46,22,0.4);
        border: 1px solid rgba(52,211,153,0.18);
        border-radius: 12px;
        margin-bottom: 8px;
        transition: border-color 0.2s, transform 0.2s;
    }
    .rec-card:hover {
        border-color: rgba(52,211,153,0.4);
        transform: translateX(4px);
    }
    .rec-num {
        flex-shrink: 0;
        width: 26px;
        height: 26px;
        border-radius: 8px;
        background: linear-gradient(135deg, #059669, #10b981);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 800;
        color: #fff;
        box-shadow: 0 2px 8px rgba(5,150,105,0.4);
    }
    .rec-text {
        font-size: 0.875rem;
        font-weight: 500;
        color: #a7f3d0;
        line-height: 1.5;
    }

    /* ══════════════════════════════════════
       SCENARIO CARDS  (Simulator)
    ══════════════════════════════════════ */
    .scenario-card {
        background: rgba(10,20,40,0.7);
        border: 1px solid rgba(6,182,212,0.2);
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .scenario-card::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #06b6d4, #8b5cf6);
        border-radius: 3px 0 0 3px;
    }
    .scenario-card:hover {
        border-color: rgba(6,182,212,0.45);
        transform: translateX(3px);
        box-shadow: 0 4px 20px rgba(6,182,212,0.12);
    }
    .scenario-tag {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .kv-key {
    color: rgba(255,255,255,0.85);
    }

    .pipeline-desc {
        color: rgba(255,255,255,0.90);
    }

    .rec-text {
        color: #FFFFFF;
    }
    .scenario-tag-save   { background: rgba(6,182,212,0.15); color: #22d3ee; border: 1px solid rgba(6,182,212,0.3); }
    .scenario-tag-good   { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
    .scenario-tag-warn   { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
    .scenario-tag-bad    { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

    /* ══════════════════════════════════════
       REPORT PIPELINE
    ══════════════════════════════════════ */
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 18px;
        background: rgba(10,20,40,0.5);
        border: 1px solid rgba(52,211,153,0.1);
        border-radius: 14px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .pipeline-step::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        border-radius: 3px 0 0 3px;
    }
    .pipeline-step.complete::before { background: #10b981; }
    .pipeline-step.anomaly::before  { background: #ef4444; }
    .pipeline-step.warn::before     { background: #f59e0b; }
    .pipeline-step:hover {
        border-color: rgba(52,211,153,0.3);
        transform: translateX(4px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .pipeline-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
        background: rgba(15,23,42,0.6);
        border: 1px solid rgba(52,211,153,0.15);
    }
    .pipeline-label {
        font-size: 0.82rem;
        font-weight: 700;
        color: #6ee7b7;
        min-width: 160px;
        letter-spacing: 0.01em;
    }
    .pipeline-desc {
        font-size: 0.8rem;
        color: rgba(167,243,208,0.6);
        flex: 1;
    }
    .pipeline-badge {
        padding: 4px 12px;
        border-radius: 99px;
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(5,150,105,0.2);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        white-space: nowrap;
    }

    /* ══════════════════════════════════════
       REPORT SUMMARY CARD
    ══════════════════════════════════════ */
    .report-kv-card {
        background: rgba(10,20,40,0.6);
        border: 1px solid rgba(52,211,153,0.15);
        border-radius: 16px;
        padding: 18px 20px;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .report-kv-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(52,211,153,0.4), transparent);
        border-radius: 16px 16px 0 0;
    }
    .report-kv-card:hover {
        border-color: rgba(52,211,153,0.3);
        transform: translateY(-3px);
        box-shadow: 0 12px 36px rgba(0,0,0,0.3);
    }
    .report-key {
        font-size: 0.7rem;
        font-weight: 700;
        color: rgba(167,243,208,0.45);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .report-val {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ecfdf5;
        line-height: 1.4;
    }

    /* ══════════════════════════════════════
       FOOTER
    ══════════════════════════════════════ */
    .em-footer {
        text-align: center;
        color: rgba(167,243,208,0.35) !important;
        font-size: 0.8rem;
        margin-top: 2.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid rgba(52,211,153,0.1);
        letter-spacing: 0.02em;
    }

    /* ══════════════════════════════════════
       JSON VIEWER
    ══════════════════════════════════════ */
    .stJson {
        background: rgba(15,23,42,0.8) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(52,211,153,0.12) !important;
    }

    /* ══════════════════════════════════════
       SELECTBOX / DROPDOWN — visible blue arrow
    ══════════════════════════════════════ */
    div[data-baseweb="select"] > div {
        background: rgba(15,23,42,0.75) !important;
        border: 1px solid rgba(6,182,212,0.45) !important;
        border-radius: 10px !important;
        color: #ecfdf5 !important;
    }
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="select"] > div:hover {
        border-color: #22d3ee !important;
        box-shadow: 0 0 0 3px rgba(6,182,212,0.18) !important;
    }
    /* The dropdown arrow SVG icon */
    div[data-baseweb="select"] svg {
        fill: #22d3ee !important;
        color: #22d3ee !important;
        opacity: 1 !important;
        width: 18px !important;
        height: 18px !important;
        filter: drop-shadow(0 0 4px rgba(6,182,212,0.6)) !important;
    }
    /* Selected value text */
    div[data-baseweb="select"] [data-testid="stSelectboxValue"],
    div[data-baseweb="select"] span {
        color: #ecfdf5 !important;
    }
    /* Dropdown menu list */
    ul[data-baseweb="menu"] {
        background: rgba(10,18,38,0.98) !important;
        border: 1px solid rgba(6,182,212,0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(20px) !important;
    }
    li[role="option"] {
        color: #a7f3d0 !important;
        border-radius: 8px !important;
    }
    li[role="option"]:hover,
    li[aria-selected="true"] {
        background: rgba(6,182,212,0.15) !important;
        color: #22d3ee !important;
    }

    /* ══════════════════════════════════════
       SLIDER THUMB — bright visible blue
    ══════════════════════════════════════ */
    .stSlider [data-baseweb="thumb"] {
        background: #22d3ee !important;
        border: 3px solid #ffffff !important;
        box-shadow: 0 0 0 4px rgba(6,182,212,0.35), 0 0 16px rgba(6,182,212,0.7) !important;
        width: 22px !important;
        height: 22px !important;
    }
    .stSlider [data-baseweb="thumb"]:hover {
        background: #67e8f9 !important;
        box-shadow: 0 0 0 5px rgba(6,182,212,0.45), 0 0 22px rgba(6,182,212,0.9) !important;
    }
    .stSlider [data-baseweb="track"] div:first-child {
        background: rgba(6,182,212,0.18) !important;
    }
    .stSlider [data-baseweb="track"] div[data-testid] {
        background: linear-gradient(90deg, #0891b2, #22d3ee) !important;
    }
    /* Slider value tooltip */
    .stSlider [role="slider"] {
        background: #22d3ee !important;
        border: 3px solid #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CHART STYLING
# ─────────────────────────────────────────────
def style_figure(fig, height=340, y_title=None, x_title=None):
    fig.update_layout(
        title="",
        showlegend=False,
        hovermode="closest",
        height=height,
        font=dict(family="Plus Jakarta Sans", color="#a7f3d0", size=13),
        title_font=dict(color="#ecfdf5", size=15),
        plot_bgcolor="rgba(10,20,40,0.0)",
        paper_bgcolor="rgba(10,20,40,0.0)",
        margin=dict(l=50, r=30, t=40, b=50),
        legend=dict(
            font=dict(color="#a7f3d0", size=12),
            bgcolor="rgba(15,23,42,0.7)",
            bordercolor="rgba(52,211,153,0.2)",
            borderwidth=1,
        ),
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>",
        hoverinfo="skip"
    )
    axis_cfg = dict(
        title_font=dict(color="#6ee7b7", size=13),
        tickfont=dict(color="#a7f3d0", size=12),
        gridcolor="rgba(52,211,153,0.06)",
        linecolor="rgba(52,211,153,0.15)",
        zerolinecolor="rgba(52,211,153,0.1)",
    )
    fig.update_xaxes(title_text=x_title or "", **axis_cfg)
    fig.update_yaxes(title_text=y_title or "", **axis_cfg)
    return fig


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def section_title(text: str):
    st.markdown(f"<div class='section-title'>{text}</div>", unsafe_allow_html=True)

def is_api_error(text: str) -> bool:
    return bool(re.search(r"(error|quota|429|failed)", text, re.I))

def parse_summary(summary: str) -> list[tuple[str, str]]:
    lines = []
    for raw in summary.strip().splitlines():
        line = raw.strip()
        if not line:
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            lines.append((key.strip(), val.strip()))
        else:
            lines.append(("Note", line))
    return lines


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="em-hero">
        <div class="em-hero-grid"></div>
        <div style="position:relative;z-index:2;">
            <div class="em-hero-badge">
                🤖 &nbsp; Multi-Agent AI System
            </div>
            <h1>🌱 EcoMind AI</h1>
            <p>Intelligent Sustainability & Energy Analysis Platform</p>
            <div style="display:flex;justify-content:center;gap:10px;margin-top:1rem;flex-wrap:wrap;">
                <span class="em-live-pill">
                    <span class="em-live-dot"></span>
                    Live Multi-Agent Analysis
                </span>
                <span class="em-live-pill" style="background:rgba(14,116,144,0.15);border-color:rgba(34,211,238,0.25);color:#67e8f9;">
                    ⚡ Real-time Monitoring
                </span>
                <span class="em-live-pill" style="background:rgba(91,33,182,0.15);border-color:rgba(167,139,250,0.25);color:#c4b5fd;">
                    🧠 Gemini Powered
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  STATUS STRIP
# ─────────────────────────────────────────────
def render_status_strip(record_index: int, confidence: int, score: int, anomaly: bool):
    status_text   = "⚠️ Anomaly Detected" if anomaly else "✅ Normal Operation"
    status_bg     = "rgba(127,29,29,0.5)"  if anomaly else "rgba(5,46,22,0.5)"
    status_border = "rgba(239,68,68,0.35)" if anomaly else "rgba(52,211,153,0.3)"
    status_color  = "#fca5a5"              if anomaly else "#6ee7b7"
    score_color   = "#ef4444" if score < 40 else "#f59e0b" if score < 70 else "#10b981"
    st.markdown(f"""
    <div style="display:flex;justify-content:center;flex-wrap:wrap;gap:10px;margin:0 0 1.5rem;">
        <div class="status-pill">📍 Record <b>#{record_index}</b></div>
        <div class="status-pill">
            🎯 Confidence&nbsp;
            <b style="color:{'#10b981' if confidence>=70 else '#f59e0b' if confidence>=40 else '#ef4444'}">
                {confidence}%
            </b>
        </div>
        <div class="status-pill">
            🌍 Score&nbsp;<b style="color:{score_color};">{score}/100</b>
        </div>
        <div class="status-pill" style="background:{status_bg};border-color:{status_border};">
            <span style="color:{status_color};font-weight:700;">{status_text}</span>
        </div>
        <div class="status-pill">
            🕐 <b>{datetime.now().strftime('%H:%M:%S')}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  RECORD SELECTOR  — clean card, no What-If
# ─────────────────────────────────────────────
def render_controls():
    st.markdown("""
    <div style="margin-bottom:0.25rem;">
        <div class="control-header">⚙️ &nbsp;Dataset Record Selector</div>
    </div>
    """, unsafe_allow_html=True)
    with st.container(border=True):
        rc1, rc2 = st.columns([3, 1], gap="medium")
        with rc1:
            selected_index = st.slider(
                "Dataset Record",
                0, len(energy_df) - 1, 100,
                help="Scrub through energy records",
                label_visibility="collapsed",
            )
        with rc2:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:center;
                        height:100%;padding:6px 0;">
                <div style="text-align:center;">
                    <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                                letter-spacing:0.08em;color:rgba(167,243,208,0.45);margin-bottom:3px;">
                        RECORD
                    </div>
                    <div style="font-size:1.55rem;font-weight:800;color:#22d3ee;
                                line-height:1;letter-spacing:-0.02em;">
                        #{selected_index}
                    </div>
                    <div style="font-size:0.68rem;color:rgba(167,243,208,0.35);margin-top:2px;">
                        of {len(energy_df)-1}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        # Progress track
        pct = selected_index / max(1, len(energy_df) - 1)
        st.markdown(f"""
        <div style="margin-top:2px;padding:0 2px;">
            <div style="display:flex;justify-content:space-between;
                        font-size:0.68rem;color:rgba(167,243,208,0.4);margin-bottom:4px;">
                <span>0</span>
                <span style="color:rgba(167,243,208,0.6);">
                    {selected_index / max(1, len(energy_df)-1)*100:.1f}% through dataset
                </span>
                <span>{len(energy_df)-1}</span>
            </div>
            <div style="width:100%;height:5px;background:rgba(6,182,212,0.08);
                        border-radius:99px;overflow:hidden;border:1px solid rgba(6,182,212,0.1);">
                <div style="width:{pct*100:.1f}%;height:100%;
                            background:linear-gradient(90deg,#0891b2,#22d3ee);
                            border-radius:99px;
                            box-shadow:0 0 10px rgba(6,182,212,0.45);
                            transition:width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Defaults for What-If (will be overridden inside Simulator tab)
    occupancy       = 20
    temperature     = 30
    hvac_efficiency = 80
    return selected_index, occupancy, temperature, hvac_efficiency


# ─────────────────────────────────────────────
#  KV CARD  (HTML version — dark theme)
# ─────────────────────────────────────────────
def render_kv_card(title: str, data: dict):
    with st.container(border=True):
        section_title(title)
        rows_html = ""
        for key, value in data.items():
            k = html.escape(str(key).replace("_", " ").title())
            v = html.escape(str(value))
            rows_html += f"""
            <div class="kv-row">
                <span class="kv-key">{k}</span>
                <span class="kv-val">{v}</span>
            </div>"""
        st.markdown(rows_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  RECOMMENDATION CARD
# ─────────────────────────────────────────────
def render_recommendation(rec_index: int, text: str):
    st.markdown(f"""
    <div class="rec-card">
        <div class="rec-num">{rec_index}</div>
        <div class="rec-text">{html.escape(text)}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CONFIDENCE GAUGE  (SVG + animated ring)
# ─────────────────────────────────────────────
def render_confidence_gauge(score: int, level: str):
    if score >= 70:
        color, glow, bg = "#10b981", "#10b981", "rgba(5,46,22,0.5)"
    elif score >= 40:
        color, glow, bg = "#f59e0b", "#f59e0b", "rgba(62,33,0,0.5)"
    else:
        color, glow, bg = "#ef4444", "#ef4444", "rgba(69,10,10,0.5)"
    circumference = 314.159   # 2π × r50
    offset = circumference - (score / 100) * circumference
    components.html(f"""
    <!DOCTYPE html><html>
    <head>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
            background: transparent;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 12px 8px;
        }}
        .gauge-wrap {{ position: relative; width: 160px; height: 160px; }}
        .gauge-wrap svg {{
            transform: rotate(-90deg);
            filter: drop-shadow(0 0 12px {glow}66);
        }}
        .gauge-center {{
            position: absolute; inset: 0;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
        }}
        .gauge-pct  {{ font-size: 2.1rem; font-weight: 800; color: #ecfdf5; line-height: 1; }}
        .gauge-sub  {{ font-size: 0.68rem; font-weight: 600; color: rgba(167,243,208,0.55);
                       text-transform: uppercase; letter-spacing: 0.06em; margin-top: 3px; }}
        .gauge-label {{
            margin-top: 10px; padding: 5px 16px;
            background: {bg}; border: 1px solid {color}44; border-radius: 99px;
            font-size: 0.82rem; font-weight: 700; color: {color}; letter-spacing: 0.04em;
        }}
        .bar-wrap {{
            width: 140px; height: 6px; background: rgba(15,23,42,0.8);
            border-radius: 99px; margin-top: 14px; overflow: hidden;
            border: 1px solid rgba(52,211,153,0.15);
        }}
        .bar-fill {{
            height: 100%; width: {score}%;
            background: linear-gradient(90deg, {color}, {color}cc);
            border-radius: 99px; box-shadow: 0 0 8px {glow}88;
            transition: width 1.2s cubic-bezier(0.22,1,0.36,1);
        }}
        circle.track {{ stroke: rgba(52,211,153,0.1); }}
        circle.ring  {{
            stroke: {color};
            stroke-dasharray: {circumference};
            stroke-dashoffset: {circumference};
            stroke-linecap: round;
            animation: fill-ring 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards 0.3s;
        }}
        @keyframes fill-ring {{ to {{ stroke-dashoffset: {offset}; }} }}
    </style>
    </head>
    <body>
        <div class="gauge-wrap">
            <svg viewBox="0 0 120 120" width="160" height="160">
                <circle class="track" cx="60" cy="60" r="50" fill="none" stroke-width="10"/>
                <circle class="ring"  cx="60" cy="60" r="50" fill="none" stroke-width="10"/>
            </svg>
            <div class="gauge-center">
                <span class="gauge-pct">{score}%</span>
                <span class="gauge-sub">confidence</span>
            </div>
        </div>
        <div class="gauge-label">{html.escape(level)}</div>
        <div class="bar-wrap"><div class="bar-fill"></div></div>
    </body></html>
    """, height=230)


# ─────────────────────────────────────────────
#  MINI SPARKLINE  (inline SVG)
# ─────────────────────────────────────────────
def render_sparkline(values: list, color="#10b981"):
    if not values:
        return
    mn, mx = min(values), max(values)
    rng = mx - mn or 1
    w, h = 200, 50
    pts = []
    for i, v in enumerate(values):
        x = i / (len(values) - 1) * w
        y = h - ((v - mn) / rng) * h
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    fill_pts = f"0,{h} " + polyline + f" {w},{h}"
    svg = f"""
    <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>
        </linearGradient>
      </defs>
      <polygon points="{fill_pts}" fill="url(#sg)"/>
      <polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="1.8"
                stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""
    st.markdown(svg, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA LOADER (cached)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data():
    return load_energy_data(), load_occupancy_data()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
inject_css()
render_header()
energy_df, occupancy_df = get_data()
selected_index, occupancy, temperature, hvac_efficiency = render_controls()
energy_row    = energy_df.iloc[selected_index]
occupancy_row = occupancy_df.iloc[0]

# ── Run agents ──────────────────────────────────────────────────────────────
with st.status("🔄 Running 9-agent sustainability analysis...", expanded=False) as status:
    context_agent        = ContextAgent()
    investigation_agent  = InvestigationAgent()
    rootcause_agent      = RootCauseAgent()
    recommendation_agent = RecommendationAgent()
    savings_agent        = SavingsAgent()
    score_agent          = SustainabilityScoreAgent()
    summary_agent        = ExecutiveSummaryAgent()
    gemini_agent         = GeminiReportAgent()
    confidence_agent     = ConfidenceAgent()

    context_result        = context_agent.analyze(energy_row, occupancy_row)
    investigation_result  = investigation_agent.investigate(energy_row)
    rootcause_result      = rootcause_agent.analyze(context_result, investigation_result)
    recommendation_result = recommendation_agent.recommend(rootcause_result)
    savings_result        = savings_agent.predict(recommendation_result)
    score_result          = score_agent.calculate(investigation_result, savings_result)
    summary               = summary_agent.generate(
        rootcause_result, recommendation_result, savings_result, score_result
    )
    ai_report             = gemini_agent.generate_report(
        context_result, investigation_result, rootcause_result,
        recommendation_result, savings_result, score_result,
    )
    confidence_result     = confidence_agent.calculate(
        context_result, investigation_result, rootcause_result
    )
    status.update(label="✅ Analysis complete — 9 agents processed", state="complete")

# ── Derived values ───────────────────────────────────────────────────────────
actual_energy   = investigation_result["actual_energy"]
expected_energy = investigation_result["expected_energy"]
energy_delta    = actual_energy - expected_energy
is_anomaly      = energy_delta > 0

render_status_strip(
    selected_index,
    confidence_result["confidence_score"],
    score_result["sustainability_score"],
    is_anomaly,
)

# ── KPI metrics ──────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("💰 Monthly Savings", f"₹{savings_result['monthly_savings']:,}",
              help="Projected monthly cost savings")
with k2:
    st.metric("📅 Annual Savings", f"₹{savings_result['annual_savings']:,}",
              help="Projected annual cost savings")
with k3:
    st.metric(
        "🌍 Sustainability Score",
        f"{score_result['sustainability_score']}/100",
        f"{energy_delta:+} Wh vs expected",
        delta_color="inverse" if is_anomaly else "normal",
        help="Composite environmental performance score",
    )
with k4:
    st.metric("🌿 Carbon Reduction", f"{savings_result['carbon_reduction_percent']}%",
              help="Estimated CO₂ reduction from recommendations")

# ── Sustainability Health Index — premium dashboard card ─────────────────────
score_val   = score_result["sustainability_score"]
shi_color   = "#10b981" if score_val >= 70 else "#f59e0b" if score_val >= 40 else "#ef4444"
shi_glow    = shi_color
shi_label   = "Excellent" if score_val >= 85 else "Good" if score_val >= 70 else "Moderate" if score_val >= 40 else "Poor"
shi_bg      = ("rgba(5,46,22,0.45)"   if score_val >= 70 else
               "rgba(62,33,0,0.45)"   if score_val >= 40 else "rgba(69,10,10,0.45)")
shi_border  = ("rgba(16,185,129,0.25)" if score_val >= 70 else
               "rgba(245,158,11,0.25)" if score_val >= 40 else "rgba(239,68,68,0.25)")
shi_icon    = "🌿" if score_val >= 70 else "⚡" if score_val >= 40 else "🔴"
shi_desc    = ("Building is operating at high sustainability standards." if score_val >= 85 else
               "Sustainability targets met with room for improvement." if score_val >= 70 else
               "Moderate performance — implement recommendations to improve." if score_val >= 40 else
               "Critical — immediate action required to improve sustainability.")
st.markdown(f"""
<div style="background:{shi_bg};border:1px solid {shi_border};border-radius:20px;
            padding:1.1rem 1.5rem;margin:0.75rem 0 1rem;
            box-shadow:0 4px 24px rgba(0,0,0,0.25),inset 0 1px 0 rgba(255,255,255,0.04);
            backdrop-filter:blur(16px);">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="width:46px;height:46px;border-radius:14px;
                        background:rgba(15,23,42,0.5);border:1px solid {shi_border};
                        display:flex;align-items:center;justify-content:center;font-size:1.4rem;
                        flex-shrink:0;box-shadow:0 0 16px {shi_glow}33;">
                {shi_icon}
            </div>
            <div>
                <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.1em;color:rgba(167,243,208,0.5);margin-bottom:2px;">
                    Sustainability Health Index
                </div>
                <div style="font-size:0.82rem;color:rgba(167,243,208,0.6);line-height:1.4;">
                    {shi_desc}
                </div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:16px;flex-shrink:0;">
            <div style="text-align:right;">
                <div style="font-size:2.4rem;font-weight:800;color:{shi_color};
                            line-height:1;letter-spacing:-0.03em;
                            text-shadow:0 0 20px {shi_glow}55;">
                    {score_val}
                    <span style="font-size:1rem;font-weight:600;color:rgba(167,243,208,0.4);">/100</span>
                </div>
                <div style="font-size:0.72rem;font-weight:700;color:{shi_color};
                            text-transform:uppercase;letter-spacing:0.06em;opacity:0.85;margin-top:1px;">
                    {shi_label}
                </div>
            </div>
        </div>
    </div>
    <div style="margin-top:14px;">
        <div style="display:flex;justify-content:space-between;
                    font-size:0.65rem;color:rgba(167,243,208,0.35);margin-bottom:5px;
                    text-transform:uppercase;letter-spacing:0.05em;">
            <span>0 · Critical</span>
            <span>40 · Moderate</span>
            <span>70 · Good</span>
            <span>100 · Excellent</span>
        </div>
        <div style="width:100%;height:8px;background:rgba(15,23,42,0.5);
                    border-radius:99px;overflow:hidden;border:1px solid rgba(52,211,153,0.08);">
            <div style="width:{score_val}%;height:100%;
                        background:linear-gradient(90deg,{shi_color}99,{shi_color});
                        border-radius:99px;
                        box-shadow:0 0 12px {shi_glow}66;
                        transition:width 0.8s cubic-bezier(0.22,1,0.36,1);"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:6px;gap:8px;">
            <div style="height:2px;flex:1;border-radius:99px;background:rgba(239,68,68,0.4);"></div>
            <div style="height:2px;flex:1.5;border-radius:99px;background:rgba(245,158,11,0.4);"></div>
            <div style="height:2px;flex:1.5;border-radius:99px;background:rgba(16,185,129,0.5);"></div>
            <div style="height:2px;flex:0.7;border-radius:99px;background:rgba(52,211,153,0.6);"></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════
tab_overview, tab_analysis, tab_ai, tab_sim, tab_reports = st.tabs([
    "📊  Overview",
    "🔍  Analysis",
    "🧠  AI Insights",
    "🔮  Simulator",
    "📄  Reports",
])

# ─────────────────────────────────────────────
#  TAB 1 — OVERVIEW
# ─────────────────────────────────────────────
with tab_overview:
    col_chart, col_snap = st.columns([2.2, 1], gap="large")
    with col_chart:
        with st.container(border=True):
            section_title("📈 Energy Consumption Trend (First 500 Records)")
            trend_df = energy_df["Appliances"].head(500).reset_index()
            trend_df.columns = ["Index", "Energy (Wh)"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_df["Index"], y=trend_df["Energy (Wh)"],
                fill="tozeroy",
                fillcolor="rgba(16,185,129,0.08)",
                line=dict(color="#10b981", width=2),
                name="Appliances",
                hovertemplate="<b>Record %{x}</b><br>Energy: %{y} Wh<extra></extra>",
                mode="lines",
            ))
            fig.add_hline(
                y=expected_energy,
                line_dash="dot",
                line_color="#f59e0b",
                line_width=1.5,
                annotation_text=f"  Expected ({expected_energy} Wh)",
                annotation_font_color="#f59e0b",
                annotation_font_size=12,
                annotation_position="top right",
            )
            if selected_index < 500:
                fig.add_vline(
                    x=selected_index,
                    line_dash="solid",
                    line_color="rgba(167,139,250,0.6)",
                    line_width=1.5,
                    annotation_text=f"  Selected #{selected_index}",
                    annotation_font_color="#c4b5fd",
                    annotation_font_size=11,
                )
            fig = style_figure(fig, height=380, y_title="Energy (Wh)", x_title="Record Index")
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
    with col_snap:
        section_title("⚡ Energy Snapshot")
        with st.container(border=True):
            st.metric("Actual Energy",   f"{actual_energy} Wh",  f"{energy_delta:+} Wh",
                      delta_color="inverse" if is_anomaly else "normal")
            st.metric("Expected Energy", f"{expected_energy} Wh")
            st.metric("Analysis Confidence", f"{confidence_result['confidence_score']}%")
        if is_anomaly:
            st.error("⚠️ **Anomaly Detected**  \nConsumption is above the expected threshold.")
        else:
            st.success("✅ **Within Expected Range**  \nEnergy usage is on target.")
        section_title("📉 Recent Trend")
        recent = energy_df["Appliances"].head(40).tolist()
        render_sparkline(recent)
        section_title("🏷️ Quick Stats")
        with st.container(border=True):
            rows = {
                "Mean (500 rec)": f"{energy_df['Appliances'].head(500).mean():.0f} Wh",
                "Peak":           f"{energy_df['Appliances'].head(500).max():.0f} Wh",
                "Trough":         f"{energy_df['Appliances'].head(500).min():.0f} Wh",
            }
            html_rows = ""
            for k, v in rows.items():
                html_rows += f"""<div class="kv-row">
                    <span class="kv-key">{k}</span>
                    <span class="kv-val">{v}</span>
                </div>"""
            st.markdown(html_rows, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TAB 2 — ANALYSIS
# ─────────────────────────────────────────────
with tab_analysis:
    left, right = st.columns(2, gap="large")
    with left:
        render_kv_card("📊 Context Report",       context_result)
        render_kv_card("🔍 Investigation Report", investigation_result)
    with right:
        with st.container(border=True):
            section_title("🎯 Root Cause Breakdown")
            root_df = pd.DataFrame({
                "Factor":       ["Weather", "Occupancy"],
                "Contribution": [
                    rootcause_result["weather_contribution"],
                    rootcause_result["occupancy_contribution"],
                ],
            })
            fig_bar = go.Figure()
            colors = ["#06b6d4", "#10b981"]
            for i, row in root_df.iterrows():
                fig_bar.add_trace(go.Bar(
                    x=[row["Contribution"]],
                    y=[row["Factor"]],
                    orientation="h",
                    name=row["Factor"],
                    marker=dict(
                        color=colors[i],
                        line=dict(color="rgba(0,0,0,0)", width=0),
                    ),
                    text=[f"{row['Contribution']}%"],
                    textposition="outside",
                    textfont=dict(color="#a7f3d0", size=14),
                    hovertemplate=f"<b>{row['Factor']}</b>: {row['Contribution']}%<extra></extra>",
                ))
            fig_bar = style_figure(fig_bar, height=260, x_title="Contribution (%)")
            fig_bar.update_layout(showlegend=False, bargap=0.35, xaxis_range=[0, 115])
            st.plotly_chart(fig_bar, use_container_width=True)
        render_kv_card("🎯 Root Cause Details", rootcause_result)
        with st.container(border=True):
            section_title("🍩 Contribution Distribution")
            wc    = rootcause_result.get("weather_contribution", 50)
            oc    = rootcause_result.get("occupancy_contribution", 50)
            other = max(0, 100 - wc - oc)
            labels = ["Weather", "Occupancy"]
            values = [wc, oc]
            if other > 0:
                labels.append("Other")
                values.append(other)
            fig_donut = go.Figure(go.Pie(
                labels=labels, values=values,
                hole=0.62,
                marker=dict(colors=["#06b6d4", "#10b981", "#8b5cf6"],
                            line=dict(color="rgba(0,0,0,0)", width=0)),
                textfont=dict(color="#ecfdf5", size=13),
                hovertemplate="<b>%{label}</b>: %{value}%<extra></extra>",
            ))
            fig_donut.update_layout(
                showlegend=True,
                legend=dict(font=dict(color="#a7f3d0", size=12),
                            bgcolor="rgba(15,23,42,0.0)"),
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=200,
                annotations=[dict(
                    text=f"{wc + oc}%<br><span style='font-size:11px'>explained</span>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=18, color="#ecfdf5"),
                )],
            )
            st.plotly_chart(fig_donut, use_container_width=True)


# ─────────────────────────────────────────────
#  TAB 3 — AI INSIGHTS
# ─────────────────────────────────────────────
with tab_ai:
    col_l, col_r = st.columns([1.6, 1], gap="large")
    with col_l:
        with st.container(border=True):
            section_title("🧠 AI Reasoning Engine")
            anomaly_icon = "🚨" if is_anomaly else "✅"
            direction    = "above" if is_anomaly else "below or at"
            delta_color  = "#fca5a5" if is_anomaly else "#6ee7b7"
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">
                <div style="background:rgba(15,23,42,0.5);border:1px solid rgba(52,211,153,0.15);
                            border-radius:12px;padding:14px;">
                    <div style="font-size:0.72rem;color:rgba(167,243,208,0.5);
                                text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">
                        ACTUAL ENERGY
                    </div>
                    <div style="font-size:1.5rem;font-weight:800;color:#ecfdf5;">
                        {actual_energy} <span style="font-size:0.9rem;color:#6ee7b7;">Wh</span>
                    </div>
                </div>
                <div style="background:rgba(15,23,42,0.5);border:1px solid rgba(52,211,153,0.15);
                            border-radius:12px;padding:14px;">
                    <div style="font-size:0.72rem;color:rgba(167,243,208,0.5);
                                text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">
                        EXPECTED ENERGY
                    </div>
                    <div style="font-size:1.5rem;font-weight:800;color:#ecfdf5;">
                        {expected_energy} <span style="font-size:0.9rem;color:#6ee7b7;">Wh</span>
                    </div>
                </div>
            </div>
            <div style="background:rgba(15,23,42,0.5);border:1px solid rgba(52,211,153,0.12);
                        border-radius:12px;padding:14px;margin-bottom:14px;">
                <div style="font-size:0.82rem;font-weight:600;color:rgba(167,243,208,0.6);margin-bottom:8px;">
                    {anomaly_icon} Energy is <b style="color:{delta_color};">{energy_delta:+} Wh</b>
                    {direction} expected threshold
                </div>
                <div style="display:flex;gap:16px;">
                    <div>
                        <span style="font-size:0.75rem;color:rgba(167,243,208,0.5);">WEATHER FACTOR</span>
                        <div style="font-size:1rem;font-weight:700;color:#67e8f9;">
                            {rootcause_result['weather_contribution']}%
                        </div>
                    </div>
                    <div>
                        <span style="font-size:0.75rem;color:rgba(167,243,208,0.5);">OCCUPANCY FACTOR</span>
                        <div style="font-size:1rem;font-weight:700;color:#a78bfa;">
                            {rootcause_result['occupancy_contribution']}%
                        </div>
                    </div>
                    <div>
                        <span style="font-size:0.75rem;color:rgba(167,243,208,0.5);">CONFIDENCE</span>
                        <div style="font-size:1rem;font-weight:700;color:#10b981;">
                            {confidence_result['confidence_score']}% ({confidence_result['confidence_level']})
                        </div>
                    </div>
                </div>
            </div>
            <div style="background:rgba(5,46,22,0.3);border:1px solid rgba(52,211,153,0.18);
                        border-radius:12px;padding:14px;">
                <div style="font-size:0.8rem;color:rgba(167,243,208,0.65);line-height:1.7;">
                    <b style="color:#6ee7b7;">Likely causes:</b> equipment inefficiency, HVAC malfunction,
                    or appliance overconsumption based on the pattern of energy deviation and contributing factors.
                </div>
            </div>
            """, unsafe_allow_html=True)
        section_title("🤖 Gemini AI Sustainability Assessment")
        if is_api_error(ai_report):
            st.warning(ai_report)
        else:
            with st.container(border=True):
                st.markdown(
                    f"<div style='color:#d1fae5;font-size:0.9rem;line-height:1.75;"
                    f"white-space:pre-wrap;'>{html.escape(ai_report)}</div>",
                    unsafe_allow_html=True,
                )
    with col_r:
        with st.container(border=True):
            section_title("🎯 Confidence Score")
            render_confidence_gauge(
                confidence_result["confidence_score"],
                confidence_result["confidence_level"],
            )
        section_title("💡 AI Recommendations")
        if recommendation_result["recommendations"]:
            for i, rec in enumerate(recommendation_result["recommendations"], 1):
                render_recommendation(i, rec)
        else:
            st.caption("No recommendations available for this record.")
        with st.container(border=True):
            section_title("🌍 Environmental Impact")
            carbon = savings_result["carbon_reduction_percent"]
            carbon_color = "#10b981" if carbon > 10 else "#f59e0b" if carbon > 5 else "#ef4444"
            st.markdown(f"""
            <div style="text-align:center;padding:16px 8px;">
                <div style="font-size:2.8rem;font-weight:800;color:{carbon_color};
                            text-shadow:0 0 20px {carbon_color}66;">
                    {carbon}%
                </div>
                <div style="font-size:0.8rem;color:rgba(167,243,208,0.55);
                            text-transform:uppercase;letter-spacing:0.05em;margin-top:4px;">
                    Carbon Reduction
                </div>
                <div style="width:100%;height:8px;background:rgba(15,23,42,0.6);
                            border-radius:99px;margin-top:12px;overflow:hidden;">
                    <div style="width:{min(carbon, 100)}%;height:100%;
                                background:linear-gradient(90deg,{carbon_color},{carbon_color}aa);
                                border-radius:99px;box-shadow:0 0 8px {carbon_color}66;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TAB 4 — SIMULATOR  (improved)
# ─────────────────────────────────────────────
with tab_sim:
    # ── Session state for saved scenarios ────────────────────────────────────
    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = []

    section_title("🔮 What-If Energy Scenario Predictor")

    # ── What-If Scenario Parameters ───────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.6rem;">
        <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:#a78bfa;">🎛️ &nbsp;Scenario Parameters</div>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(139,92,246,0.3),transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        sp1, sp2, sp3 = st.columns(3, gap="large")
        with sp1:
            st.markdown("""
            <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;color:rgba(167,243,208,0.5);margin-bottom:6px;">
                👥 Expected Occupancy
            </div>""", unsafe_allow_html=True)
            occupancy = st.number_input(
                "Occupancy", min_value=1, value=20,
                label_visibility="collapsed",
                help="Number of people expected in the building"
            )
            st.markdown(f"""
            <div style="font-size:0.72rem;color:rgba(167,243,208,0.4);margin-top:4px;">
                People in building
            </div>""", unsafe_allow_html=True)
        with sp2:
            st.markdown("""
            <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;color:rgba(167,243,208,0.5);margin-bottom:6px;">
                🌡️ Temperature (°C)
            </div>""", unsafe_allow_html=True)
            temperature = st.number_input(
                "Temperature", value=30,
                label_visibility="collapsed",
                help="Ambient outdoor temperature"
            )
            temp_icon = "🥵" if temperature > 35 else "😊" if temperature > 20 else "🥶"
            st.markdown(f"""
            <div style="font-size:0.72rem;color:rgba(167,243,208,0.4);margin-top:4px;">
                {temp_icon} Outdoor ambient
            </div>""", unsafe_allow_html=True)
        with sp3:
            st.markdown("""
            <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;color:rgba(167,243,208,0.5);margin-bottom:6px;">
                ⚙️ HVAC Efficiency (%)
            </div>""", unsafe_allow_html=True)
            hvac_efficiency = st.slider(
                "HVAC Efficiency",
                50, 100, 80,
                label_visibility="collapsed",
            )
            eff_color = "#10b981" if hvac_efficiency >= 80 else "#f59e0b" if hvac_efficiency >= 65 else "#ef4444"
            eff_label = "Optimal" if hvac_efficiency >= 80 else "Moderate" if hvac_efficiency >= 65 else "Low"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:7px;margin-top:4px;">
                <div style="width:7px;height:7px;border-radius:50%;
                            background:{eff_color};box-shadow:0 0 6px {eff_color};flex-shrink:0;"></div>
                <span style="font-size:0.72rem;font-weight:700;color:{eff_color};">
                    {eff_label} · {hvac_efficiency}%
                </span>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── Compute active scenario ───────────────────────────────────────────────
    base_energy      = investigation_result["actual_energy"]
    predicted_energy = base_energy * (occupancy / 20) * (temperature / 30) * (100 / hvac_efficiency)
    monthly_savings  = max(0, int((base_energy - predicted_energy) * 20))
    carbon_reduction = max(0, int(monthly_savings / 1000))
    future_score     = min(100, score_result["sustainability_score"] + carbon_reduction)
    savings_pct      = round(max(0, (base_energy - predicted_energy) / base_energy * 100), 1) if base_energy else 0

    # ── KPIs ─────────────────────────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("⚡ Predicted Energy", f"{int(predicted_energy)} Wh")
    with s2: st.metric("💰 Monthly Savings",  f"₹{monthly_savings:,}")
    with s3: st.metric("🌿 Carbon Reduction", f"{carbon_reduction}%")
    with s4: st.metric("📈 Future Score",     f"{future_score}/100")

    st.markdown("")

    # ── Main simulator layout ─────────────────────────────────────────────────
    col_left, col_mid, col_right = st.columns([2, 1.6, 1.2], gap="large")

    # ────────────────────────────────────────────
    # LEFT — comparison bar + sensitivity chart
    # ────────────────────────────────────────────
    with col_left:
        with st.container(border=True):
            section_title("📊 Current vs Predicted Comparison")
            st.caption(f"Potential energy reduction: **{savings_pct}%** under this scenario")

            compare_df = pd.DataFrame({
                "Scenario":    ["Current", "Predicted"],
                "Energy (Wh)": [base_energy, int(predicted_energy)],
            })
            fig_cmp = go.Figure()
            for _, row in compare_df.iterrows():
                clr = "#ef4444" if row["Scenario"] == "Current" else "#10b981"
                fig_cmp.add_trace(go.Bar(
                    x=[row["Scenario"]],
                    y=[row["Energy (Wh)"]],
                    name=row["Scenario"],
                    marker=dict(color=clr, line=dict(color="rgba(0,0,0,0)", width=0)),
                    text=[f"{row['Energy (Wh)']} Wh"],
                    textposition="outside",
                    textfont=dict(color="#a7f3d0", size=15),
                    hovertemplate=f"<b>{row['Scenario']}</b>: {row['Energy (Wh)']} Wh<extra></extra>",
                ))
            fig_cmp = style_figure(fig_cmp, height=300, y_title="Energy (Wh)", x_title="Scenario")
            fig_cmp.update_layout(showlegend=False, bargap=0.5)
            st.plotly_chart(fig_cmp, use_container_width=True)

        # Sensitivity analysis: sweep HVAC efficiency
        with st.container(border=True):
            section_title("📉 Sensitivity Analysis — HVAC Efficiency Sweep")
            st.caption("Energy consumption across the full HVAC efficiency range")

            hvac_range   = list(range(50, 101, 5))
            energy_sweep = [base_energy * (occupancy / 20) * (temperature / 30) * (100 / h)
                            for h in hvac_range]
            fig_sens = go.Figure()
            fig_sens.add_trace(go.Scatter(
                x=hvac_range, y=energy_sweep,
                mode="lines+markers",
                line=dict(color="#06b6d4", width=2.5),
                marker=dict(size=6, color="#22d3ee",
                            line=dict(color="#0891b2", width=1)),
                fill="tozeroy",
                fillcolor="rgba(6,182,212,0.07)",
                hovertemplate="<b>HVAC %{x}%</b><br>Predicted: %{y:.0f} Wh<extra></extra>",
            ))
            # Mark current setting
            fig_sens.add_vline(
                x=hvac_efficiency,
                line_dash="dot",
                line_color="#a78bfa",
                line_width=1.5,
                annotation_text=f" Current ({hvac_efficiency}%)",
                annotation_font_color="#c4b5fd",
                annotation_font_size=11,
            )
            fig_sens = style_figure(fig_sens, height=240,
                                    y_title="Predicted Energy (Wh)",
                                    x_title="HVAC Efficiency (%)")
            st.plotly_chart(fig_sens, use_container_width=True)

    # ────────────────────────────────────────────
    # MIDDLE — scenario save & comparison
    # ────────────────────────────────────────────
    with col_mid:
        with st.container(border=True):
            section_title("💾 Scenario Manager")

            # Save button
            col_sb, col_sc = st.columns([1.4, 1])
            with col_sb:
                scenario_name = st.text_input("Scenario name", value=f"Scenario {len(st.session_state.saved_scenarios)+1}",
                                              label_visibility="collapsed",
                                              placeholder="Enter scenario name…")
            with col_sc:
                if st.button("💾 Save", use_container_width=True):
                    st.session_state.saved_scenarios.append({
                        "name":       scenario_name,
                        "occupancy":  occupancy,
                        "temp":       temperature,
                        "hvac":       hvac_efficiency,
                        "energy":     int(predicted_energy),
                        "savings":    monthly_savings,
                        "carbon":     carbon_reduction,
                        "score":      future_score,
                        "savings_pct": savings_pct,
                    })
                    st.rerun()

            if st.session_state.saved_scenarios:
                st.caption(f"{len(st.session_state.saved_scenarios)} scenario(s) saved")
                for idx, sc in enumerate(st.session_state.saved_scenarios):
                    tag_cls = "scenario-tag-good" if sc["savings_pct"] > 10 else \
                              "scenario-tag-warn" if sc["savings_pct"] > 0  else "scenario-tag-bad"
                    tag_lbl = f"−{sc['savings_pct']}%" if sc["savings_pct"] > 0 else "No saving"
                    st.markdown(f"""
                    <div class="scenario-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <span style="font-weight:700;color:#ecfdf5;font-size:0.88rem;">{html.escape(sc['name'])}</span>
                            <span class="scenario-tag {tag_cls}">{tag_lbl}</span>
                        </div>
                        <div style="display:flex;gap:12px;flex-wrap:wrap;">
                            <span style="font-size:0.75rem;color:rgba(167,243,208,0.6);">👥 {sc['occupancy']} ppl</span>
                            <span style="font-size:0.75rem;color:rgba(167,243,208,0.6);">🌡 {sc['temp']}°C</span>
                            <span style="font-size:0.75rem;color:rgba(167,243,208,0.6);">⚙️ HVAC {sc['hvac']}%</span>
                        </div>
                        <div style="margin-top:8px;display:flex;gap:12px;">
                            <span style="font-size:0.8rem;font-weight:700;color:#22d3ee;">⚡ {sc['energy']} Wh</span>
                            <span style="font-size:0.8rem;font-weight:700;color:#34d399;">₹{sc['savings']:,}/mo</span>
                            <span style="font-size:0.8rem;font-weight:700;color:#a78bfa;">📈 {sc['score']}/100</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if st.button("🗑 Clear All Scenarios", use_container_width=True):
                    st.session_state.saved_scenarios = []
                    st.rerun()
            else:
                st.markdown("""
                <div style="text-align:center;padding:24px 16px;
                            color:rgba(167,243,208,0.35);font-size:0.82rem;">
                    No scenarios saved yet.<br>Adjust parameters and click 💾 Save.
                </div>
                """, unsafe_allow_html=True)

        # Scenario comparison chart (if ≥ 2 saved)
        if len(st.session_state.saved_scenarios) >= 2:
            with st.container(border=True):
                section_title("📊 Scenario Comparison")
                sc_names   = [s["name"]   for s in st.session_state.saved_scenarios]
                sc_energy  = [s["energy"] for s in st.session_state.saved_scenarios]
                sc_scores  = [s["score"]  for s in st.session_state.saved_scenarios]

                fig_comp = go.Figure()
                fig_comp.add_trace(go.Bar(
                    name="Energy (Wh)",
                    x=sc_names, y=sc_energy,
                    marker_color="#06b6d4",
                    yaxis="y",
                    hovertemplate="<b>%{x}</b><br>%{y} Wh<extra></extra>",
                ))
                fig_comp.add_trace(go.Scatter(
                    name="Future Score",
                    x=sc_names, y=sc_scores,
                    mode="lines+markers",
                    marker=dict(size=8, color="#a78bfa"),
                    line=dict(color="#a78bfa", width=2),
                    yaxis="y2",
                    hovertemplate="<b>%{x}</b><br>Score: %{y}<extra></extra>",
                ))
                fig_comp.update_layout(
                    yaxis=dict(title="Energy (Wh)", title_font=dict(color="#22d3ee"),
                               tickfont=dict(color="#a7f3d0"),
                               gridcolor="rgba(6,182,212,0.07)", linecolor="rgba(6,182,212,0.15)"),
                    yaxis2=dict(title="Future Score", title_font=dict(color="#a78bfa"),
                                tickfont=dict(color="#c4b5fd"),
                                overlaying="y", side="right", range=[0, 110]),
                    height=260,
                    font=dict(family="Plus Jakarta Sans", color="#a7f3d0", size=12),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=50, r=50, t=30, b=50),
                    legend=dict(font=dict(color="#a7f3d0", size=11),
                                bgcolor="rgba(15,23,42,0.7)",
                                bordercolor="rgba(52,211,153,0.2)", borderwidth=1),
                )
                st.plotly_chart(fig_comp, use_container_width=True)

    # ────────────────────────────────────────────
    # RIGHT — gauge + params + impact matrix
    # ────────────────────────────────────────────
    with col_right:
        with st.container(border=True):
            section_title("🎯 Scenario Efficiency")
            render_confidence_gauge(int(min(future_score, 100)), "Future Score")

        with st.container(border=True):
            st.markdown("""
            <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:rgba(167,243,208,0.45);
                        border-left:3px solid #a78bfa;padding-left:0.6rem;margin-bottom:12px;">
                📋 Active Scenario Parameters
            </div>
            """, unsafe_allow_html=True)
            params = {
                "👥 Occupancy":       f"{occupancy} people",
                "🌡️ Temperature":     f"{temperature}°C",
                "⚙️ HVAC Efficiency": f"{hvac_efficiency}%",
                "⚡ Base Energy":     f"{base_energy} Wh",
                "🔮 Predicted":       f"{int(predicted_energy)} Wh",
                "📉 Δ Energy":        f"{int(base_energy - predicted_energy):+} Wh",
            }
            html_rows = ""
            for k, v in params.items():
                delta_pos = int(base_energy - predicted_energy)
                if "Δ Energy" in k:
                    val_color = "#10b981" if delta_pos > 0 else "#ef4444" if delta_pos < 0 else "#a7f3d0"
                else:
                    val_color = "#ecfdf5"
                html_rows += f"""<div class="kv-row">
                    <span class="kv-key">{k}</span>
                    <span class="kv-val" style="color:{val_color};">{v}</span>
                </div>"""
            st.markdown(html_rows, unsafe_allow_html=True)

        # Impact matrix
        with st.container(border=True):
            section_title("🧮 Impact Matrix")
            impacts = [
                ("Cost Impact",    f"₹{monthly_savings:,}/mo",   "#10b981" if monthly_savings > 0 else "#ef4444"),
                ("Energy Δ",       f"{int(base_energy - predicted_energy):+} Wh", "#10b981" if predicted_energy < base_energy else "#ef4444"),
                ("Carbon",         f"{carbon_reduction}% less",  "#10b981" if carbon_reduction > 0 else "#f59e0b"),
                ("Score Δ",        f"+{carbon_reduction} pts",   "#a78bfa"),
            ]
            for label, val, col in impacts:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:9px 0;border-bottom:1px solid rgba(52,211,153,0.07);">
                    <span style="font-size:0.78rem;color:rgba(167,243,208,0.55);font-weight:600;
                                 text-transform:uppercase;letter-spacing:0.04em;">{label}</span>
                    <span style="font-size:0.88rem;font-weight:700;color:{col};">{val}</span>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TAB 5 — REPORTS  (improved)
# ─────────────────────────────────────────────
with tab_reports:

    # ── Top bar: title + download ─────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:flex-start;justify-content:space-between;
                flex-wrap:wrap;gap:12px;margin-bottom:1rem;">
        <div>
            <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:rgba(167,243,208,0.45);margin-bottom:4px;">
                📄 &nbsp;REPORT GENERATION
            </div>
            <div style="font-size:1.45rem;font-weight:800;color:#ecfdf5;
                        letter-spacing:-0.02em;line-height:1.2;">
                Executive Sustainability Report
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rp_meta_col, rp_dl_col = st.columns([3, 1])
    with rp_meta_col:
        st.markdown(f"""
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:0.5rem;">
            <span style="display:inline-flex;align-items:center;gap:6px;padding:5px 12px;
                         background:rgba(15,23,42,0.5);border:1px solid rgba(52,211,153,0.12);
                         border-radius:8px;font-size:0.76rem;color:rgba(167,243,208,0.65);">
                📅 &nbsp;{datetime.now().strftime('%B %d, %Y  %H:%M')}
            </span>
            <span style="display:inline-flex;align-items:center;gap:6px;padding:5px 12px;
                         background:rgba(15,23,42,0.5);border:1px solid rgba(52,211,153,0.12);
                         border-radius:8px;font-size:0.76rem;color:rgba(167,243,208,0.65);">
                🗂 &nbsp;Record #{selected_index}
            </span>
            <span style="display:inline-flex;align-items:center;gap:6px;padding:5px 12px;
                         background:rgba(5,46,22,0.4);border:1px solid rgba(52,211,153,0.2);
                         border-radius:8px;font-size:0.76rem;color:#6ee7b7;font-weight:700;">
                ✅ &nbsp;9 Agents Processed
            </span>
        </div>
        """, unsafe_allow_html=True)
    with rp_dl_col:
        # Build a well-formatted PDF report as bytes using reportlab if available,
        # otherwise fall back to an HTML file the browser can print-to-PDF
        def _build_pdf_report():
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import cm
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                import io

                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4,
                                        leftMargin=2*cm, rightMargin=2*cm,
                                        topMargin=2*cm, bottomMargin=2*cm)
                styles = getSampleStyleSheet()
                dark  = colors.HexColor("#000000")
                green = colors.HexColor("#10b981")
                teal  = colors.HexColor("#06b6d4")
                light = colors.HexColor("#000000")
                muted = colors.HexColor("#333333")
                h1 = ParagraphStyle(
                    "h1",
                    fontSize=22,
                    textColor=colors.black,
                    spaceAfter=6,
                    fontName="Helvetica-Bold"
                )

                h2 = ParagraphStyle(
                    "h2",
                    fontSize=13,
                    textColor=colors.HexColor("#0f766e"),
                    spaceAfter=4,
                    spaceBefore=12,
                    fontName="Helvetica-Bold"
                )

                body = ParagraphStyle(
                    "body",
                    fontSize=10,
                    textColor=colors.black,
                    spaceAfter=4,
                    leading=15,
                    fontName="Helvetica"
                )
                label_s = ParagraphStyle(
                    "label",
                    fontSize=8,
                    textColor=colors.HexColor("#444444"),
                    fontName="Helvetica-Bold",
                    spaceAfter=2
                )

                story = []
                # Title
                story.append(Paragraph("EcoMind AI", label_s))
                story.append(Paragraph("Executive Sustainability Report", h1))
                story.append(Paragraph(
                    f"Record #{selected_index}  ·  Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}  ·  9 Agents Processed",
                    label_s))
                story.append(Spacer(1, 0.4*cm))

                # KPI table
                story.append(Paragraph("Key Performance Indicators", h2))
                _sc  = score_result["sustainability_score"]
                _mo  = savings_result["monthly_savings"]
                _an  = savings_result["annual_savings"]
                _cr  = savings_result["carbon_reduction_percent"]
                _cf  = confidence_result["confidence_score"]
                _cfl = confidence_result["confidence_level"]
                kpi_data = [
                    ["Metric", "Value", "Note"],
                    ["Sustainability Score", f"{_sc}/100",
                     "Excellent" if _sc>=85 else "Good" if _sc>=70 else "Moderate" if _sc>=40 else "Poor"],
                    ["Monthly Savings",  f"₹{_mo:,}",  "Projected cost reduction"],
                    ["Annual Savings",   f"₹{_an:,}",  "12-month projection"],
                    ["Carbon Reduction", f"{_cr}%",    "CO₂ emissions avoided"],
                    ["Analysis Confidence", f"{_cf}%", _cfl],
                ]
                tbl = Table(kpi_data, colWidths=[5*cm, 4*cm, 7*cm])
                tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0,0), (-1,0), green),
                    ("TEXTCOLOR",     (0,0), (-1,0), dark),
                    ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
                    ("FONTSIZE",      (0,0), (-1,-1), 9),
                    ("TEXTCOLOR", (0,1), (-1,-1), colors.black),
                    ("BACKGROUND", (0,1), (-1,-1), colors.white),
                    ("ROWBACKGROUNDS",(0,1),(-1,-1),
                    [
                    colors.white,
                    colors.HexColor("#f5f5f5")
                    ]),
                    ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#1e4d34")),
                    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
                    ("TOPPADDING",    (0,0), (-1,-1), 6),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ]))
                story.append(tbl)

                # System status
                story.append(Paragraph("System Status & Energy Analysis", h2))
                _ae = investigation_result["actual_energy"]
                _ee = investigation_result["expected_energy"]
                _dlt = _ae - _ee
                status_txt = ("⚠ ANOMALY DETECTED" if _dlt > 0 else "✓ Normal Operation")
                delta_txt  = (f"+{_dlt} Wh above baseline" if _dlt > 0
                              else f"{abs(_dlt)} Wh below baseline (efficient)")
                story.append(Paragraph(f"<b>Status:</b> {status_txt}", body))
                story.append(Paragraph(f"<b>Actual Energy:</b> {_ae} Wh  ·  "
                                       f"<b>Expected Energy:</b> {_ee} Wh  ·  "
                                       f"<b>Delta:</b> {delta_txt}", body))

                # Root cause
                story.append(Paragraph("Root Cause Analysis", h2))
                _wc = rootcause_result.get("weather_contribution", 0)
                _oc = rootcause_result.get("occupancy_contribution", 0)
                primary = "weather patterns" if _wc >= _oc else "occupancy levels"
                primary_pct = max(_wc, _oc)
                secondary_pct = min(_wc, _oc)
                story.append(Paragraph(
                    f"The primary driver is <b>{primary}</b> ({primary_pct}%), "
                    f"with the secondary factor contributing {secondary_pct}% of variance.", body))
                story.append(Paragraph(
                    f"Weather Contribution: {_wc}%   |   Occupancy Contribution: {_oc}%", body))

                # Recommendations
                story.append(Paragraph("Recommendations", h2))
                recs = recommendation_result.get("recommendations", [])
                for i, rec in enumerate(recs, 1):
                    story.append(Paragraph(f"{i}. {rec}", body))
                if not recs:
                    story.append(Paragraph("No specific recommendations generated.", body))

                # Savings narrative
                story.append(Paragraph("Financial & Environmental Impact", h2))
                if _mo > 0:
                    story.append(Paragraph(
                        f"Implementing the {len(recs)} recommended action(s) could yield "
                        f"₹{_mo:,}/month (₹{_an:,}/year) in cost savings with a "
                        f"{_cr}% reduction in carbon emissions.", body))
                else:
                    story.append(Paragraph(
                        "System is already operating near optimal efficiency. "
                        "Minimal additional savings are projected.", body))

                # Footer
                story.append(Spacer(1, 0.5*cm))
                story.append(Paragraph(
                    "Generated by EcoMind AI  ·  Multi-Agent Sustainability Intelligence  ·  9 Agents Active",
                    label_s))

                doc.build(story)
                return buf.getvalue(), "application/pdf", ".pdf"

            except ImportError:
                # Fallback: styled HTML (browser printable as PDF)
                _sc  = score_result["sustainability_score"]
                _mo  = savings_result["monthly_savings"]
                _an  = savings_result["annual_savings"]
                _cr  = savings_result["carbon_reduction_percent"]
                _cf  = confidence_result["confidence_score"]
                _cfl = confidence_result["confidence_level"]
                _ae  = investigation_result["actual_energy"]
                _ee  = investigation_result["expected_energy"]
                _dlt = _ae - _ee
                recs = recommendation_result.get("recommendations", [])
                _wc  = rootcause_result.get("weather_contribution", 0)
                _oc  = rootcause_result.get("occupancy_contribution", 0)
                rec_html = "".join(f"<li>{r}</li>" for r in recs) or "<li>No recommendations generated.</li>"
                html_content = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>EcoMind AI — Executive Report #{selected_index}</title>
<style>
  body{{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#ecfdf5;margin:40px;line-height:1.6}}
  h1{{color:#34d399;font-size:2rem;margin-bottom:4px}}
  h2{{color:#6ee7b7;border-left:3px solid #10b981;padding-left:10px;margin-top:28px}}
  .meta{{color:#6ee7b7;font-size:0.85rem;margin-bottom:24px}}
  table{{border-collapse:collapse;width:100%;margin:12px 0}}
  th{{background:#10b981;color:#0d1117;padding:8px 12px;text-align:left}}
  td{{padding:8px 12px;border-bottom:1px solid #1e4d34;color:#d1fae5}}
  tr:nth-child(even) td{{background:#0a1628}}
  .footer{{margin-top:40px;font-size:0.75rem;color:#4b7c6a;border-top:1px solid #1e4d34;padding-top:12px}}
  li{{margin-bottom:6px}}
  @media print{{body{{background:#fff;color:#000}}h1,h2{{color:#000}}td,th{{color:#000}}}}
</style></head><body>
<p style="color:#6ee7b7;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;">EcoMind AI</p>
<h1>Executive Sustainability Report</h1>
<div class="meta">Record #{selected_index} &nbsp;·&nbsp; {datetime.now().strftime('%B %d, %Y at %H:%M')} &nbsp;·&nbsp; 9 Agents Processed</div>
<h2>Key Performance Indicators</h2>
<table><tr><th>Metric</th><th>Value</th><th>Note</th></tr>
<tr><td>Sustainability Score</td><td>{_sc}/100</td><td>{'Excellent' if _sc>=85 else 'Good' if _sc>=70 else 'Moderate' if _sc>=40 else 'Poor'}</td></tr>
<tr><td>Monthly Savings</td><td>₹{_mo:,}</td><td>Projected cost reduction</td></tr>
<tr><td>Annual Savings</td><td>₹{_an:,}</td><td>12-month projection</td></tr>
<tr><td>Carbon Reduction</td><td>{_cr}%</td><td>CO₂ emissions avoided</td></tr>
<tr><td>Analysis Confidence</td><td>{_cf}%</td><td>{_cfl}</td></tr>
</table>
<h2>System Status & Energy Analysis</h2>
<p><b>Status:</b> {'⚠ Anomaly Detected' if _dlt>0 else '✓ Normal Operation'}</p>
<p><b>Actual Energy:</b> {_ae} Wh &nbsp;·&nbsp; <b>Expected:</b> {_ee} Wh &nbsp;·&nbsp;
   <b>Delta:</b> {'+' if _dlt>0 else ''}{_dlt} Wh</p>
<h2>Root Cause Analysis</h2>
<p>Weather contribution: <b>{_wc}%</b> &nbsp;·&nbsp; Occupancy contribution: <b>{_oc}%</b></p>
<h2>Recommendations</h2><ol>{rec_html}</ol>
<h2>Financial & Environmental Impact</h2>
<p>{'Implementing '+str(len(recs))+' recommended action(s) could yield ₹'+f'{_mo:,}'+'/month (₹'+f'{_an:,}'+'/year) with '+str(_cr)+'% carbon reduction.' if _mo>0 else 'System is operating near optimal efficiency. Minimal additional savings projected.'}</p>
<div class="footer">Generated by EcoMind AI &nbsp;·&nbsp; Multi-Agent Sustainability Intelligence &nbsp;·&nbsp; 9 Agents Active</div>
</body></html>"""
                return html_content.encode("utf-8"), "text/html", ".html"

        _pdf_bytes, _pdf_mime, _pdf_ext = _build_pdf_report()
        _pdf_label = "⬇️ Download PDF Report" if _pdf_ext == ".pdf" else "⬇️ Download HTML Report (print to PDF)"
        st.download_button(
            label=_pdf_label,
            data=_pdf_bytes,
            file_name=f"ecomind_report_{selected_index}_{datetime.now().strftime('%Y%m%d_%H%M')}{_pdf_ext}",
            mime=_pdf_mime,
            use_container_width=True,
        )

    st.markdown("")

    # ── Executive Summary heading + rich cards ───────────────────────────────
    with st.container(border=True):
        st.markdown("""
        <div style="margin-bottom:1rem;">
            <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:rgba(167,243,208,0.45);margin-bottom:4px;">
                🧠 AI-Generated
            </div>
            <div style="font-size:1.15rem;font-weight:800;color:#ecfdf5;
                        border-left:3px solid #10b981;padding-left:0.7rem;letter-spacing:-0.01em;">
                Executive Summary
            </div>
            <div style="font-size:0.78rem;color:rgba(167,243,208,0.5);
                        margin-top:4px;padding-left:0.9rem;">
                Key findings synthesised across all 9 analysis agents
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Derive all values from actual agent results ──────────────────────
        _score    = score_result["sustainability_score"]
        _monthly  = savings_result["monthly_savings"]
        _annual   = savings_result["annual_savings"]
        _carbon   = savings_result["carbon_reduction_percent"]
        _conf     = confidence_result["confidence_score"]
        _conf_lvl = confidence_result["confidence_level"]
        _weath    = rootcause_result.get("weather_contribution", 0)
        _occ_c    = rootcause_result.get("occupancy_contribution", 0)
        _act_e    = investigation_result["actual_energy"]
        _exp_e    = investigation_result["expected_energy"]
        _delta    = _act_e - _exp_e
        _anomaly  = _delta > 0
        _recs     = recommendation_result.get("recommendations", [])
        _n_recs   = len(_recs)
        _pri_rec  = _recs[0] if _recs else "No recommendations generated."

        # Status labels
        _score_lbl   = "Excellent" if _score >= 85 else "Good" if _score >= 70 else "Moderate" if _score >= 40 else "Poor"
        _score_color = "#10b981" if _score >= 70 else "#f59e0b" if _score >= 40 else "#ef4444"
        _status_lbl  = "⚠️ Anomaly Detected" if _anomaly else "✅ Normal Operation"
        _status_col  = "#f87171" if _anomaly else "#34d399"
        _status_bg   = "rgba(127,29,29,0.35)" if _anomaly else "rgba(5,46,22,0.35)"
        _status_brd  = "rgba(239,68,68,0.3)" if _anomaly else "rgba(52,211,153,0.25)"
        _rootcause_txt = (
            f"Weather patterns are the primary driver ({_weath}%), with occupancy levels "
            f"contributing {_occ_c}% of the observed variance."
            if _weath >= _occ_c
            else f"Occupancy levels are the primary driver ({_occ_c}%), with weather patterns "
                 f"contributing {_weath}% of the observed variance."
        )
        _delta_txt = f"+{_delta} Wh above baseline" if _anomaly else f"{abs(_delta)} Wh below baseline (efficient)"
        _savings_narrative = (
            f"Implementing the {_n_recs} recommended action(s) could yield ₹{_monthly:,}/month "
            f"(₹{_annual:,}/year) in cost savings with a {_carbon}% reduction in carbon emissions."
            if _monthly > 0
            else "System is already operating near optimal efficiency. Minimal additional savings are projected."
        )

        # ── Row 1 — Status + Score + Energy delta ───────────────────────────
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            st.markdown(f"""
            <div style="background:{_status_bg};border:1px solid {_status_brd};border-radius:16px;
                        padding:1rem 1.1rem;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.08em;color:rgba(167,243,208,0.45);margin-bottom:6px;">
                    System Status
                </div>
                <div style="font-size:1.05rem;font-weight:800;color:{_status_col};margin-bottom:6px;">
                    {_status_lbl}
                </div>
                <div style="font-size:0.78rem;color:rgba(167,243,208,0.65);line-height:1.5;">
                    Record #{selected_index} &nbsp;·&nbsp; Energy delta: <b style="color:{_status_col};">{_delta_txt}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background:rgba(5,46,22,0.35);border:1px solid rgba(52,211,153,0.25);
                        border-radius:16px;padding:1rem 1.1rem;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.08em;color:rgba(167,243,208,0.45);margin-bottom:6px;">
                    Sustainability Score
                </div>
                <div style="display:flex;align-items:baseline;gap:6px;margin-bottom:6px;">
                    <span style="font-size:2rem;font-weight:800;color:{_score_color};line-height:1;">
                        {_score}
                    </span>
                    <span style="font-size:0.85rem;color:rgba(167,243,208,0.4);">/100</span>
                    <span style="font-size:0.78rem;font-weight:700;color:{_score_color};
                                 background:rgba(16,185,129,0.12);padding:2px 8px;border-radius:99px;
                                 border:1px solid {_score_color}44;">
                        {_score_lbl}
                    </span>
                </div>
                <div style="width:100%;height:6px;background:rgba(15,23,42,0.5);
                            border-radius:99px;overflow:hidden;">
                    <div style="width:{_score}%;height:100%;background:{_score_color};
                                border-radius:99px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.5);border:1px solid rgba(167,243,208,0.1);
                        border-radius:16px;padding:1rem 1.1rem;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.08em;color:rgba(167,243,208,0.45);margin-bottom:6px;">
                    Analysis Confidence
                </div>
                <div style="display:flex;align-items:baseline;gap:6px;margin-bottom:4px;">
                    <span style="font-size:2rem;font-weight:800;color:#a78bfa;line-height:1;">
                        {_conf}%
                    </span>
                    <span style="font-size:0.78rem;color:rgba(167,243,208,0.5);">{_conf_lvl}</span>
                </div>
                <div style="font-size:0.78rem;color:rgba(167,243,208,0.55);">
                    Based on {_n_recs} recommendation(s) across 9 agents
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Row 2 — Savings + Carbon ─────────────────────────────────────────
        s1, s2, s3, s4 = st.columns(4, gap="medium")
        for _col, _lbl, _val, _sub, _clr in [
            (s1, "Monthly Savings",   f"₹{_monthly:,}",    "Projected cost reduction",    "#06b6d4"),
            (s2, "Annual Savings",    f"₹{_annual:,}",     "12-month projection",          "#10b981"),
            (s3, "Carbon Reduction",  f"{_carbon}%",        "CO₂ emissions avoided",        "#34d399"),
            (s4, "Actions Available", str(_n_recs),         "Optimisation recommendations", "#a78bfa"),
        ]:
            with _col:
                st.markdown(f"""
                <div style="background:rgba(15,23,42,0.55);border:1px solid rgba(52,211,153,0.12);
                            border-radius:14px;padding:0.85rem 1rem;text-align:center;">
                    <div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;
                                letter-spacing:0.08em;color:rgba(167,243,208,0.4);margin-bottom:4px;">
                        {_lbl}
                    </div>
                    <div style="font-size:1.5rem;font-weight:800;color:{_clr};line-height:1.1;">
                        {_val}
                    </div>
                    <div style="font-size:0.7rem;color:rgba(167,243,208,0.4);margin-top:4px;">
                        {_sub}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Row 3 — Root Cause narrative + Primary Recommendation ────────────
        n1, n2 = st.columns(2, gap="medium")
        with n1:
            st.markdown(f"""
            <div style="background:rgba(6,182,212,0.06);border:1px solid rgba(6,182,212,0.18);
                        border-radius:14px;padding:1rem 1.1rem;">
                <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.08em;color:#22d3ee;margin-bottom:6px;">
                    🔍 Root Cause Analysis
                </div>
                <div style="font-size:0.85rem;color:#d1fae5;line-height:1.6;">
                    {html.escape(_rootcause_txt)}
                </div>
                <div style="margin-top:8px;display:flex;gap:10px;">
                    <span style="font-size:0.72rem;color:rgba(167,243,208,0.55);
                                 background:rgba(6,182,212,0.1);padding:3px 10px;border-radius:99px;">
                        🌦 Weather {_weath}%
                    </span>
                    <span style="font-size:0.72rem;color:rgba(167,243,208,0.55);
                                 background:rgba(16,185,129,0.1);padding:3px 10px;border-radius:99px;">
                        👥 Occupancy {_occ_c}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with n2:
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.18);
                        border-radius:14px;padding:1rem 1.1rem;">
                <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.08em;color:#34d399;margin-bottom:6px;">
                    💡 Top Recommendation
                </div>
                <div style="font-size:0.85rem;color:#d1fae5;line-height:1.6;">
                    {html.escape(str(_pri_rec))}
                </div>
                {f'<div style="margin-top:8px;font-size:0.72rem;color:rgba(167,243,208,0.45);">+ {_n_recs - 1} more action(s) in the Analysis tab</div>' if _n_recs > 1 else ""}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Row 4 — Savings narrative ────────────────────────────────────────
        st.markdown(f"""
        <div style="background:rgba(167,243,208,0.04);border:1px solid rgba(52,211,153,0.12);
                    border-radius:14px;padding:0.9rem 1.1rem;
                    display:flex;align-items:center;gap:14px;">
            <div style="font-size:1.6rem;flex-shrink:0;">💰</div>
            <div style="font-size:0.85rem;color:#d1fae5;line-height:1.6;">
                {html.escape(_savings_narrative)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ── Charts row ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.6rem;">
        <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:rgba(167,243,208,0.4);">📊 &nbsp;Visual Analytics</div>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(52,211,153,0.2),transparent);"></div>
    </div>
    """, unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns(3, gap="large")

    with ch1:
        with st.container(border=True):
            section_title("💰 Savings Overview")
            fig_sav = go.Figure(go.Bar(
                x=["Monthly", "Annual"],
                y=[savings_result["monthly_savings"], savings_result["annual_savings"]],
                marker=dict(
                    color=["rgba(6,182,212,0.8)", "rgba(16,185,129,0.8)"],
                    line=dict(color="rgba(0,0,0,0)", width=0),
                ),
                text=[f"₹{savings_result['monthly_savings']:,}", f"₹{savings_result['annual_savings']:,}"],
                textposition="outside",
                textfont=dict(color="#a7f3d0", size=12),
                hovertemplate="<b>%{x}</b>: ₹%{y:,}<extra></extra>",
            ))
            fig_sav = style_figure(fig_sav, height=220, y_title="₹ Savings")
            fig_sav.update_layout(showlegend=False, bargap=0.45)
            st.plotly_chart(fig_sav, use_container_width=True)

    with ch2:
        with st.container(border=True):
            section_title("🌍 Root Cause Pie")
            wc_r = rootcause_result.get("weather_contribution", 50)
            oc_r = rootcause_result.get("occupancy_contribution", 50)
            oth  = max(0, 100 - wc_r - oc_r)
            lbs  = ["Weather", "Occupancy"] + (["Other"] if oth > 0 else [])
            vls  = [wc_r, oc_r] + ([oth] if oth > 0 else [])
            fig_pie = go.Figure(go.Pie(
                labels=lbs, values=vls, hole=0.55,
                marker=dict(colors=["#06b6d4", "#10b981", "#8b5cf6"],
                            line=dict(color="rgba(0,0,0,0)", width=0)),
                textfont=dict(color="#ecfdf5", size=12),
                hovertemplate="<b>%{label}</b>: %{value}%<extra></extra>",
            ))
            fig_pie.update_layout(
                height=220, showlegend=True,
                legend=dict(font=dict(color="#a7f3d0", size=11), bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with ch3:
        with st.container(border=True):
            section_title("🎯 Score vs Confidence")
            fig_rad = go.Figure(go.Scatterpolar(
                r=[
                    score_result["sustainability_score"],
                    confidence_result["confidence_score"],
                    savings_result["carbon_reduction_percent"],
                    min(100, savings_result["monthly_savings"] // 100),
                    future_score,
                ],
                theta=["Sustain.","Confidence","Carbon","Savings","Future"],
                fill="toself",
                fillcolor="rgba(16,185,129,0.12)",
                line=dict(color="#10b981", width=2),
                marker=dict(size=6, color="#34d399"),
            ))
            fig_rad.update_layout(
                polar=dict(
                    radialaxis=dict(range=[0, 100], tickfont=dict(color="#a7f3d0", size=10),
                                    gridcolor="rgba(52,211,153,0.1)", linecolor="rgba(52,211,153,0.15)"),
                    angularaxis=dict(tickfont=dict(color="#6ee7b7", size=11),
                                     gridcolor="rgba(52,211,153,0.08)"),
                    bgcolor="rgba(0,0,0,0)",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                height=220,
                margin=dict(l=30, r=30, t=30, b=30),
                showlegend=False,
            )
            st.plotly_chart(fig_rad, use_container_width=True)

    st.markdown("")

    # ── Agent Pipeline — improved visual ─────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.6rem;">
        <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:rgba(167,243,208,0.4);">🔗 &nbsp;Agent Pipeline</div>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(52,211,153,0.2),transparent);"></div>
    </div>
    """, unsafe_allow_html=True)
    with st.container(border=True):

        def _badge(txt, color="#10b981", bg="rgba(5,150,105,0.18)", border="rgba(52,211,153,0.25)"):
            return (f"<span style='padding:3px 10px;border-radius:99px;font-size:0.72rem;"
                    f"font-weight:700;background:{bg};color:{color};border:1px solid {border};'>"
                    f"{txt}</span>")

        pipeline = [
            ("🌍", "Context Agent",       "Environment & occupancy context analysis",
             _badge("Complete"), "complete"),
            ("🔍", "Investigation",        f"Δ {energy_delta:+} Wh",
             _badge("⚠️ Anomaly", "#fca5a5", "rgba(127,29,29,0.4)", "rgba(239,68,68,0.3)") if is_anomaly
             else _badge("Normal"), "anomaly" if is_anomaly else "complete"),
            ("🎯", "Root Cause",           f"Weather {rootcause_result['weather_contribution']}% · Occupancy {rootcause_result['occupancy_contribution']}%",
             _badge("Analysed"), "complete"),
            ("💡", "Recommendations",      f"{len(recommendation_result.get('recommendations', []))} actions generated",
             _badge(f"{len(recommendation_result.get('recommendations', []))} Actions"), "complete"),
            ("💰", "Savings Projection",   f"₹{savings_result['monthly_savings']:,}/mo · ₹{savings_result['annual_savings']:,}/yr",
             _badge(f"₹{savings_result['annual_savings']:,}/yr"), "complete"),
            ("🌿", "Sustainability Score", f"{score_result['sustainability_score']}/100",
             _badge(f"{score_result['sustainability_score']}/100",
                    "#10b981" if score_result['sustainability_score'] >= 70 else
                    "#f59e0b" if score_result['sustainability_score'] >= 40 else "#ef4444",
                    "rgba(5,46,22,0.4)", "rgba(52,211,153,0.3)"), "complete"),
            ("📄", "Executive Summary",    "Multi-agent synthesis complete",
             _badge("Synthesised"), "complete"),
            ("🤖", "Gemini AI Report",     "Narrative generated",
             _badge("AI Generated", "#a78bfa", "rgba(91,33,182,0.2)", "rgba(139,92,246,0.3)"), "complete"),
            ("🎯", "Confidence Engine",    f"{confidence_result['confidence_score']}% — {confidence_result['confidence_level']}",
             _badge(f"{confidence_result['confidence_score']}%"), "complete"),
        ]

        for icon, step, desc, badge, cls in pipeline:
            st.markdown(f"""
            <div class="pipeline-step {cls}">
                <div class="pipeline-icon">{icon}</div>
                <div class="pipeline-label">{step}</div>
                <div class="pipeline-desc">{html.escape(desc)}</div>
                {badge}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ── Raw outputs expander ──────────────────────────────────────────────────
    with st.expander("📋 Raw Agent Outputs (Debug)"):
        st.json({
            "context":         context_result,
            "investigation":   investigation_result,
            "rootcause":       rootcause_result,
            "recommendations": recommendation_result,
            "savings":         savings_result,
            "score":           score_result,
            "confidence":      confidence_result,
        })

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(
    f"<div class='em-footer'>"
    f"🌱 EcoMind AI &nbsp;·&nbsp; Multi-Agent Sustainability Intelligence &nbsp;·&nbsp; "
    f"9 Agents Active &nbsp;·&nbsp; Last updated {datetime.now().strftime('%H:%M:%S')}"
    f"</div>",
    unsafe_allow_html=True,
)