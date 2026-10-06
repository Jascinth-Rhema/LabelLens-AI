"""LabelLens AI - redesigned UI. Run with: streamlit run app.py"""

import json
import os
from html import escape
from textwrap import dedent

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import pytesseract

# Tesseract
TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT

# Project imports
import ai_explainer
import database
import diagnostics
import guides
import nutrition
import unknown_explainer

from ingredient_matcher import SAFE_LABEL, analyze, compare, load_db, safety_verdict
from ocr_engine import read_text
from personalization import CONCERNS, FOOD_GOALS, SKIN_TONES, Profile, apply_kids, personal_notes
from text_processor import extract_ingredients


# =====================================================================
# PAGE
# =====================================================================

st.set_page_config(
    page_title="LabelLens AI",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)
database.init_db()


# =====================================================================
# DESIGN SYSTEM - SAME UI
# =====================================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root{
--bg:#f3f6f4;
--card:#fff;
--ink:#0f1f19;
--mute:#5b6b63;
--line:#e2eae5;
--brand:#059669;
--brand-d:#047857;
--brand-l:#d1fae5;
--bad:#dc2626;
--warn:#d97706;
--good:#059669;
--r:18px;
--sh:0 1px 2px rgba(15,31,25,.05),0 8px 24px rgba(15,31,25,.06)
}

html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
background:var(--bg)!important;
color:var(--ink)!important;
font-family:"Plus Jakarta Sans",system-ui,-apple-system,"Segoe UI",sans-serif
}

[data-testid="stHeader"]{background:transparent!important}
#MainMenu,footer{visibility:hidden}
.block-container{max-width:820px;padding-top:1.1rem;padding-bottom:3rem}

.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label,.stApp li,.stApp summary,.stApp [data-testid="stWidgetLabel"] p{
color:var(--ink)!important;font-family:inherit
}

.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *{
color:var(--mute)!important
}

.stApp [data-baseweb="select"]>div,.stApp [data-baseweb="input"]>div,.stApp [data-baseweb="textarea"],.stApp textarea,.stApp input{
background:#fff!important;color:var(--ink)!important;border-color:var(--line)!important;border-radius:12px!important
}

.stApp textarea{font-size:15px!important;line-height:1.5}
.stApp [data-baseweb="select"] *{color:var(--ink)!important}

[data-baseweb="popover"],[data-baseweb="popover"] ul,[data-baseweb="popover"] li,[data-baseweb="menu"]{
background:#fff!important;color:var(--ink)!important
}

.stApp input:focus,.stApp textarea:focus{
box-shadow:0 0 0 3px rgba(5,150,105,.25)!important;border-color:var(--brand)!important
}

[data-testid="stFileUploaderDropzone"]{
background:#fff!important;border:2px dashed #86d1b5!important;border-radius:var(--r)!important;padding:26px!important;transition:.15s
}

[data-testid="stFileUploaderDropzone"]:hover{
background:#f0fdf8!important;border-color:var(--brand)!important
}

[data-testid="stFileUploaderDropzone"] *{color:var(--mute)!important}

[data-testid="stExpander"]{
background:#fff!important;border:1px solid var(--line)!important;border-radius:var(--r)!important;box-shadow:var(--sh)
}

[data-testid="stExpander"] summary p{font-weight:700}

.stApp .stButton>button,.stApp [data-testid="stDownloadButton"]>button,.stApp [data-testid="stPopover"]>button{
min-height:46px;background:#fff!important;border:1.5px solid var(--line)!important;border-radius:14px!important;transition:.15s
}

.stApp .stButton>button:hover,.stApp [data-testid="stDownloadButton"]>button:hover,.stApp [data-testid="stPopover"]>button:hover{
border-color:var(--brand)!important;transform:translateY(-1px);box-shadow:0 6px 16px rgba(5,150,105,.16)
}

.stApp .stButton>button p,.stApp [data-testid="stDownloadButton"]>button p,.stApp [data-testid="stPopover"]>button p{
color:var(--brand-d)!important;font-weight:700
}

.stApp .stButton>button[kind="primary"],.stApp .stButton>button[data-testid="stBaseButton-primary"]{
min-height:52px;background:linear-gradient(135deg,#10b981,#047857)!important;border:0!important;box-shadow:0 8px 20px rgba(4,120,87,.28)
}

.stApp .stButton>button[kind="primary"] p,.stApp .stButton>button[data-testid="stBaseButton-primary"] p{
color:#fff!important;font-size:16px
}

.stApp button:focus-visible{
outline:3px solid rgba(5,150,105,.45)!important;outline-offset:2px
}

.stApp [data-testid="stRadio"] [role="radiogroup"]{
gap:4px!important;background:#e6eee9;padding:4px;border-radius:14px;display:inline-flex!important;flex-wrap:wrap
}

.stApp [data-testid="stRadio"] label{
margin:0!important;padding:8px 16px;border-radius:10px;cursor:pointer;transition:.15s
}

.stApp [data-testid="stRadio"] label>div:first-child{display:none!important}
.stApp [data-testid="stRadio"] label p{font-weight:600;font-size:14px;color:var(--mute)!important}

.stApp [data-testid="stRadio"] label:has(input:checked){
background:#fff;box-shadow:0 1px 4px rgba(15,31,25,.18)
}

.stApp [data-testid="stRadio"] label:has(input:checked) p{
color:var(--brand-d)!important;font-weight:800
}

.stApp [role="tablist"]{
gap:4px!important;background:#e6eee9;padding:5px!important;border-radius:16px!important;border:0!important;overflow-x:auto
}

.stApp button[role="tab"]{
border-radius:12px!important;padding:9px 16px!important;background:transparent!important;height:auto!important
}

.stApp button[role="tab"] p{color:var(--mute)!important;font-weight:600}

.stApp button[role="tab"][aria-selected="true"]{
background:#fff!important;box-shadow:0 1px 5px rgba(15,31,25,.2)!important
}

.stApp button[role="tab"][aria-selected="true"] p{
color:var(--brand-d)!important;font-weight:800!important
}

.stApp [data-baseweb="tab-highlight"],.stApp [data-baseweb="tab-border"]{display:none!important}

.brand{display:flex;align-items:center;gap:10px;padding:4px 0}
.brand svg{flex:none}
.brand b{font-size:22px;font-weight:800;letter-spacing:-.5px}
.brand b span{color:var(--brand)}
.brand em{font-style:normal;font-size:11px;font-weight:800;background:var(--brand-l);color:var(--brand-d);padding:3px 8px;border-radius:99px}

.intro{margin:14px 0 18px}
.stApp .intro h1{font-size:clamp(26px,5vw,36px);line-height:1.12;font-weight:800;letter-spacing:-1px;margin:0 0 8px}
.stApp .intro p{font-size:16px;color:var(--mute)!important;margin:0 0 12px;max-width:560px}

.trust{display:flex;flex-wrap:wrap;gap:8px}
.trust span{font-size:13px;font-weight:600;color:var(--brand-d);background:#fff;border:1px solid var(--line);padding:5px 12px;border-radius:99px}

.steps{display:flex;gap:8px;list-style:none;margin:6px 0 16px;padding:0}
.steps li{flex:1;display:flex;align-items:center;gap:8px;font-size:13px;font-weight:700;color:#8a9a92;padding:8px 10px;border-radius:12px;background:#e9f0ec}
.steps li i{font-style:normal;width:22px;height:22px;border-radius:50%;display:grid;place-items:center;font-size:12px;background:#cfdcd5;color:#fff;flex:none}
.steps li.on{background:#fff;color:var(--ink);box-shadow:var(--sh)}
.steps li.on i{background:var(--brand)}
.steps li.done{color:var(--brand-d);background:var(--brand-l)}
.steps li.done i{background:var(--brand-d)}

.sec{margin:22px 0 8px}
.stApp .sec h3{font-size:18px;font-weight:800;margin:0}
.stApp .sec p{font-size:13px;color:var(--mute)!important;margin:2px 0 0}

.lbl{font-size:13px;font-weight:700;color:var(--mute);margin:14px 0 6px;text-transform:uppercase;letter-spacing:.6px}

.verdict{display:flex;align-items:center;justify-content:space-between;gap:16px;border-radius:24px;padding:22px 24px;margin:8px 0 12px;border:1px solid;animation:up .5s both;box-shadow:var(--sh)}
.verdict.good{background:linear-gradient(135deg,#ecfdf5,#d1fae5);border-color:#a7f3d0}
.verdict.mid{background:linear-gradient(135deg,#f7fee7,#ecfccb);border-color:#d9f99d}
.verdict.warn{background:linear-gradient(135deg,#fffbeb,#fef3c7);border-color:#fde68a}
.verdict.bad{background:linear-gradient(135deg,#fff1f2,#ffe4e6);border-color:#fecdd3}

.v-left{display:flex;align-items:center;gap:16px;min-width:0}
.v-icon{flex:none;width:64px;height:64px;border-radius:20px;display:grid;place-items:center;font-size:34px;background:rgba(255,255,255,.75)}
.verdict.bad .v-icon{animation:pulse 2.2s ease-in-out infinite}
.v-kicker{font-size:12px;font-weight:800;letter-spacing:1px;text-transform:uppercase;opacity:.75}
.stApp .verdict h2{margin:2px 0 4px;font-size:clamp(22px,4.5vw,30px);font-weight:800;letter-spacing:-.5px}
.stApp .verdict p{margin:0;font-size:14px;line-height:1.45}

.stApp .verdict.good h2,.stApp .verdict.good p,.stApp .verdict.good .v-kicker{color:#065f46!important}
.stApp .verdict.mid h2,.stApp .verdict.mid p,.stApp .verdict.mid .v-kicker{color:#3f6212!important}
.stApp .verdict.warn h2,.stApp .verdict.warn p,.stApp .verdict.warn .v-kicker{color:#92400e!important}
.stApp .verdict.bad h2,.stApp .verdict.bad p,.stApp .verdict.bad .v-kicker{color:#9f1239!important}

.v-ring{flex:none;text-align:center}
.v-ring small{display:block;font-size:12px;font-weight:700;color:var(--mute);margin-top:2px}

.ringwrap{position:relative;flex:none;margin:0 auto}
.ringfill{animation:ring 1.2s ease-out}

@property --n{syntax:"<integer>";inherits:false;initial-value:0}

.ringwrap .num{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:800;counter-reset:n var(--n);animation:cnt 1.3s ease-out forwards}
.ringwrap .num:before{content:counter(n)}

.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:8px 0}
.tile{background:#fff;border:1px solid var(--line);border-radius:16px;padding:12px 8px;text-align:center;box-shadow:var(--sh);animation:up .45s both}
.tile:nth-child(2){animation-delay:.06s}
.tile:nth-child(3){animation-delay:.12s}
.tile:nth-child(4){animation-delay:.18s}
.tile b{display:block;font-size:26px;font-weight:800;line-height:1.1}
.tile span{font-size:12px;color:var(--mute);font-weight:600}
.tile.bad b{color:var(--bad)}
.tile.warn b{color:var(--warn)}
.tile.good b{color:var(--good)}
.tile.unk b{color:#64748b}

.conf{display:inline-flex;gap:8px;align-items:center;font-size:13px;color:var(--mute);background:#fff;border:1px solid var(--line);border-radius:99px;padding:6px 14px;margin:2px 0 6px}
.conf b{color:var(--ink)}

.note{background:#ecfdf5;border:1px solid #a7f3d0;border-radius:14px;padding:11px 15px;margin:8px 0;font-size:14px;color:#065f46}
.stApp .note{color:#065f46!important}

details.row{background:#fff;border:1px solid var(--line);border-left:5px solid #94a3b8;border-radius:14px;margin:8px 0;padding:0 16px;box-shadow:0 1px 2px rgba(15,31,25,.04);animation:up .45s var(--d,0s) both}
details.row[open]{box-shadow:var(--sh)}
details.row.good{border-left-color:var(--good)}
details.row.warn{border-left-color:var(--warn)}
details.row.bad{border-left-color:var(--bad)}

details.row summary{cursor:pointer;padding:14px 0;font-weight:700;list-style:none;display:flex;align-items:center;gap:10px;min-height:44px}
details.row summary::-webkit-details-marker{display:none}
details.row summary:after{content:"+";margin-left:6px;color:var(--mute);font-weight:700}
details.row[open] summary:after{content:"–"}

.pill{margin-left:auto;font-size:12px;font-weight:800;padding:4px 11px;border-radius:99px;white-space:nowrap}
.p-good{background:#d1fae5;color:#065f46}
.p-ok{background:#e6eee9;color:#475569}
.p-warn{background:#fef3c7;color:#92400e}
.p-bad{background:#ffe4e6;color:#9f1239}
.p-unk{background:#e2e8f0;color:#475569}

.stApp .body{padding:0 0 14px;font-size:14px}
.stApp .body p{margin:6px 0;color:#334155!important;line-height:1.5}
.stApp .body p.adv{color:#065f46!important}
.stApp .body p.dis{color:#9f1239!important}

.swaps{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.swap{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;font-size:14px}
.swap b{display:block;color:var(--brand-d);margin-bottom:2px}

.bar{margin:12px 0}
.bar-top{display:flex;justify-content:space-between;font-size:14px;font-weight:700;margin-bottom:5px}
.track{height:12px;background:#e6eee9;border-radius:8px;overflow:hidden}
.fill{height:100%;border-radius:8px;animation:grow 1.1s ease-out}

.hist{background:#fff;border:1px solid var(--line);border-left:5px solid #94a3b8;border-radius:14px;padding:12px 16px;margin:8px 0;font-size:14px}
.hist.bad{border-left-color:var(--bad)}
.hist.warn{border-left-color:var(--warn)}
.hist.good{border-left-color:var(--good)}
.hist small{color:var(--mute)}

.cmp{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:8px 0}
.cmpbox{background:#fff;border:2px solid var(--line);border-radius:20px;padding:16px;text-align:center;animation:up .5s both}
.cmpbox.win{border-color:var(--brand);box-shadow:0 8px 22px rgba(5,150,105,.2)}

.empty{text-align:center;background:#fff;border:1px dashed #b6c9bf;border-radius:var(--r);padding:30px 18px;color:var(--mute)}
.empty big{display:block;font-size:40px;margin-bottom:6px}
.fine{font-size:12px;color:var(--mute);margin-top:22px;line-height:1.5}

@keyframes up{from{opacity:0;transform:translateY(10px)}}
@keyframes grow{from{width:0}}
@keyframes ring{from{stroke-dashoffset:339.3}}
@keyframes cnt{from{--n:0}to{--n:var(--t)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,.35)}50%{box-shadow:0 0 0 12px rgba(220,38,38,0)}}

@media(max-width:600px){
.tiles{grid-template-columns:repeat(2,1fr)}
.verdict{flex-direction:column;text-align:center;align-items:center}
.v-left{flex-direction:column}
.swaps,.cmp{grid-template-columns:1fr}
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# =====================================================================
# CONSTANTS
# =====================================================================

LABEL = SAFE_LABEL
CAT_F = "🍜 Food"
CAT_S = "🧴 Skincare / makeup / haircare"
SRC_UP, SRC_CAM, SRC_TYPE = "📁 Upload", "📸 Camera", "⌨️ Type / paste"
FILTERS = ["All", "Alerts", "Care", "Safe"]

VCOLOR = {
    "good": "#059669",
    "mid": "#65a30d",
    "warn": "#d97706",
    "bad": "#dc2626",
}

DEMOS = {
    "🍜 Noodles": (
        "Wheat flour, Palm oil, Salt, Sugar, Monosodium glutamate, "
        "Tartrazine (E102), Sodium benzoate, Disodium inosinate, "
        "Acidity regulator (E501), Spirulina extract, Spices",
        CAT_F,
    ),
    "🥤 Soft drink": (
        "Carbonated water, Sugar, High fructose corn syrup, Citric acid, "
        "Sodium benzoate, Aspartame, Flavour",
        CAT_F,
    ),
    "🧴 Face cream": (
        "Water, Glycerin, Niacinamide, Hyaluronic acid, Zinc oxide, "
        "Dimethicone, Fragrance, Methylparaben, Bakuchiol, "
        "Centella asiatica extract, Ceteareth-20",
        CAT_S,
    ),
    "⚠️ Fairness cream": (
        "Water, Hydroquinone, Mercury chloride, Glycerin, Fragrance",
        CAT_S,
    ),
}

SAMPLE_NUT = """Nutrition Information
Serving size 30 g
Energy 2092 kJ / 500 kcal
Protein 7 g
Carbohydrate 60 g
of which sugars 30 g
Total Fat 25 g
Saturated fat 12 g
Sodium 480 mg"""

LOGO = (
    '<svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true">'
    '<rect width="34" height="34" rx="10" fill="#059669"/>'
    '<circle cx="15" cy="15" r="6.5" fill="none" stroke="#fff" stroke-width="2.6"/>'
    '<line x1="20" y1="20" x2="26" y2="26" stroke="#fff" stroke-width="2.8" stroke-linecap="round"/>'
    '<line x1="11.5" y1="15" x2="18.5" y2="15" stroke="#a7f3d0" stroke-width="1.8" stroke-linecap="round"/>'
    '</svg>'
)


# =====================================================================
# DATABASE
# =====================================================================

@st.cache_data
def get_db():
    return load_db()


try:
    DB = get_db()
except FileNotFoundError:
    st.error(
        "data/ingredients.csv is missing from the project. "
        "Upload the data folder with ingredients.csv next to app.py."
    )
    st.stop()


# =====================================================================
# HELPERS
# =====================================================================

def label_score(hits):
    return max(
        0,
        min(
            100,
            100 + sum({
                "bad": -25,
                "warn": -8,
                "good": 3,
                "ok": 0,
            }.get(h["level"], 0) for h in hits),
        ),
    )


def grade(score):
    return (
        ("Great pick 🎉", "#059669")
        if score >= 80 else
        ("Okay, use with care 🙂", "#65a30d")
        if score >= 60 else
        ("Be careful ⚠️", "#d97706")
        if score >= 40 else
        ("Better avoided 🚫", "#dc2626")
    )


def ring(score, color, size=132):
    off = 339.3 * (1 - score / 100)
    return (
        f'<div class="ringwrap" role="img" aria-label="Score {score} out of 100" '
        f'style="width:{size}px;height:{size}px">'
        f'<svg width="{size}" height="{size}" viewBox="0 0 150 150">'
        f'<circle cx="75" cy="75" r="54" fill="none" stroke="rgba(15,31,25,.08)" stroke-width="13"/>'
        f'<circle class="ringfill" cx="75" cy="75" r="54" fill="none" stroke="{color}" '
        f'stroke-width="13" stroke-linecap="round" stroke-dasharray="339.3" '
        f'stroke-dashoffset="{off:.1f}" transform="rotate(-90 75 75)"/>'
        f'</svg><div class="num" style="--t:{score};color:{color};font-size:{int(size*.27)}px"></div></div>'
    )


def section(title, sub=""):
    st.markdown(
        f'<div class="sec"><h3>{escape(title)}</h3>'
        f'{f"<p>{escape(sub)}</p>" if sub else ""}</div>',
        unsafe_allow_html=True,
    )


def note(message):
    st.markdown(
        f'<div class="note">{escape(message)}</div>',
        unsafe_allow_html=True,
    )


def empty(icon, message):
    st.markdown(
        f'<div class="empty"><big>{icon}</big>{escape(message)}</div>',
        unsafe_allow_html=True,
    )


def stepper(step):
    names = ["Scan", "Review text", "Result"]
    items = "".join(
        f'<li class="{"done" if i < step else "on" if i == step else ""}">'
        f'<i>{"✓" if i < step else i}</i>{escape(name)}</li>'
        for i, name in enumerate(names, 1)
    )
    return f'<ol class="steps" aria-label="Progress">{items}</ol>'


def row(result, open_=False, idx=0):
    level = result["level"]
    st.markdown(
        f'<details class="row {level}" style="--d:{idx*.05:.2f}s" {"open" if open_ else ""}>'
        f'<summary>{escape(result["name"])}<span class="pill p-{level}">{LABEL[level]}</span></summary>'
        f'<div class="body">'
        f'<p><b>What it is:</b> {escape(result["what"])}</p>'
        f'<p class="adv"><b>Good:</b> {escape(result["advantage"])}</p>'
        f'<p class="dis"><b>Watch out:</b> {escape(result["disadvantage"])}</p>'
        f'</div></details>',
        unsafe_allow_html=True,
    )


def unknown_row(unknown, category, idx=0):
    info = unknown_explainer.explain(unknown, category)
    key = info["skey"]
    pill = {"ok": "p-ok", "limit": "p-warn", "check": "p-unk"}.get(key, "p-unk")
    icon = {"ok": "✅", "limit": "⚠️", "check": "❓"}.get(key, "❓")

    st.markdown(
        f'<details class="row" style="--d:{idx*.05:.2f}s">'
        f'<summary>{escape(unknown)}<span class="pill {pill}">{icon} {escape(info["safety"])}</span></summary>'
        f'<div class="body">'
        f'<p><b>Looks like:</b> {escape(info["kind"])}</p>'
        f'<p><b>What it does:</b> {escape(info["text"])}</p>'
        f'<p><b>Confidence:</b> {escape(info["conf"])} (pattern-based guess, not from our database)</p>'
        f'<p><b>What to do:</b> {escape(info["advice"])}</p>'
        f'</div></details>',
        unsafe_allow_html=True,
    )


def speak_buttons(en, ta):
    safe = lambda x: json.dumps(x).replace("</", "<\\/")
    html = r"""
<div style="display:flex;gap:10px;flex-wrap:wrap;font-family:system-ui,sans-serif">
<button id="en" style="padding:12px 18px;border:0;border-radius:14px;color:#fff;font-weight:700;font-size:15px;background:linear-gradient(135deg,#10b981,#047857);cursor:pointer">🔊 Read in English</button>
<button id="ta" style="padding:12px 18px;border:0;border-radius:14px;color:#fff;font-weight:700;font-size:15px;background:linear-gradient(135deg,#0ea5e9,#0369a1);cursor:pointer">🔊 தமிழில் கேளுங்கள்</button>
<button id="stop" style="padding:12px 18px;border:1.5px solid #cfdcd5;border-radius:14px;color:#334155;font-weight:700;font-size:15px;background:#fff;cursor:pointer">⏹ Stop</button>
</div>
<div id="msg" style="font:13px system-ui,sans-serif;color:#5b6b63;margin-top:8px;min-height:18px"></div>
<script>
const EN=%%EN%%,TA=%%TA%%,msg=document.getElementById('msg');
var token=0,keep=[];
function getVoices(){return new Promise(function(res){var v=speechSynthesis.getVoices();if(v.length)return res(v);speechSynthesis.onvoiceschanged=function(){res(speechSynthesis.getVoices())};setTimeout(function(){res(speechSynthesis.getVoices())},1500)})}
async function say(text,lang,label){
if(!('speechSynthesis'in window)){msg.textContent='This browser cannot read aloud. Try Chrome or Edge.';return}
var vs=await getVoices(),base=lang.split('-')[0],v=vs.find(x=>x.lang.replace('_','-').toLowerCase()===lang.toLowerCase())||vs.find(x=>x.lang.toLowerCase().indexOf(base)===0);
if(!v&&base==='ta'){msg.textContent='No Tamil voice found on this device.';return}
var mine=++token;speechSynthesis.cancel();
setTimeout(function(){
if(mine!==token)return;speechSynthesis.resume();
var parts=text.split(/(?<=[.!?\u0964])\s+/).filter(Boolean);
keep=parts.map(function(p,i){var u=new SpeechSynthesisUtterance(p);if(v){u.voice=v;u.lang=v.lang}else u.lang=lang;
u.onstart=function(){if(mine===token)msg.textContent='Reading '+label+'...'};
if(i===parts.length-1)u.onend=function(){if(mine===token)msg.textContent=''};
u.onerror=function(e){if(mine===token&&e.error!=='interrupted'&&e.error!=='canceled')msg.textContent='Could not play audio ('+e.error+').'};return u});
keep.forEach(function(u){speechSynthesis.speak(u)});
},200)}
document.getElementById('en').onclick=function(){say(EN,'en-IN','English')};
document.getElementById('ta').onclick=function(){say(TA,'ta-IN','Tamil')};
document.getElementById('stop').onclick=function(){token++;speechSynthesis.cancel();msg.textContent=''};
</script>
"""
    components.html(
        html.replace("%%EN%%", safe(en)).replace("%%TA%%", safe(ta)),
        height=112,
    )


def bars(values):
    html = ""
    for key, value in values.items():
        if key not in nutrition.DAILY:
            continue
        pct = value / nutrition.DAILY[key] * 100
        color = (
            "#0ea5e9" if key in {"protein", "fibre"} else
            "#059669" if pct < 30 else
            "#d97706" if pct < 60 else
            "#dc2626"
        )
        html += (
            f'<div class="bar"><div class="bar-top">'
            f'<span>{escape(nutrition.NAMES[key])}</span>'
            f'<span>{value:.1f} · {pct:.0f}% of day</span></div>'
            f'<div class="track"><div class="fill" style="width:{min(pct,100):.0f}%;background:{color}"></div></div></div>'
        )
    if html:
        st.markdown(html, unsafe_allow_html=True)


def load_demo(text, category):
    st.session_state.update(ocr_text=text, cat=category, run_check=True)


def load_nut():
    st.session_state["nut_text"] = SAMPLE_NUT


def reset_scan():
    for key in ("res", "ocr_text", "ocr_conf", "raw_text", "ai_unknown"):
        st.session_state.pop(key, None)


# =====================================================================
# BEAUTY PRODUCTS
# =====================================================================

BEAUTY_PRODUCTS = [
    {
        "name": "Cetaphil Gentle Skin Cleanser",
        "brand": "Cetaphil",
        "category": "Skin Care",
        "price": 399,
        "skin_types": ["Normal","Dry","Combination","Sensitive"],
        "concerns": ["Dryness","Sensitive Skin"],
        "tones": ["Very Fair","Fair","Medium","Tan","Deep"],
        "ingredients": ["Glycerin"],
        "rating": 4.6,
        "why": "Gentle cleanser option for dry or sensitive skin.",
    },
    {
        "name": "CeraVe Moisturising Cream",
        "brand": "CeraVe",
        "category": "Skin Care",
        "price": 799,
        "skin_types": ["Normal","Dry","Sensitive"],
        "concerns": ["Dryness","Sensitive Skin"],
        "tones": ["Very Fair","Fair","Medium","Tan","Deep"],
        "ingredients": ["Ceramides","Hyaluronic Acid"],
        "rating": 4.6,
        "why": "Barrier-focused moisturiser with ceramides.",
    },
    {
        "name": "Re'equil Oxybenzone & OMC Free Sunscreen",
        "brand": "Re'equil",
        "category": "Skin Care",
        "price": 695,
        "skin_types": ["Normal","Dry","Combination","Sensitive"],
        "concerns": ["Uneven Tone","Sensitive Skin","Dark Spots"],
        "tones": ["Very Fair","Fair","Medium","Tan","Deep"],
        "ingredients": ["UV Filters"],
        "rating": 4.5,
        "why": "Broad-spectrum sunscreen option when sun protection is a priority.",
    },
    {
        "name": "Dot & Key Watermelon Sunscreen",
        "brand": "Dot & Key",
        "category": "Skin Care",
        "price": 499,
        "skin_types": ["Oily","Combination","Normal"],
        "concerns": ["Uneven Tone","Dullness"],
        "tones": ["Very Fair","Fair","Medium","Tan","Deep"],
        "ingredients": ["UV Filters"],
        "rating": 4.4,
        "why": "Lightweight sunscreen option for normal, combination and oily skin.",
    },
    {
        "name": "The Derma Co 10% Niacinamide Face Serum",
        "brand": "The Derma Co",
        "category": "Serum",
        "price": 499,
        "skin_types": ["Oily","Combination","Normal"],
        "concerns": ["Acne","Dark Spots","Uneven Tone"],
        "tones": ["Very Fair","Fair","Medium","Tan","Deep"],
        "ingredients": ["Niacinamide","Zinc"],
        "rating": 4.4,
        "why": "Niacinamide-focused serum for oiliness and uneven appearance.",
    },
    {
        "name": "Minimalist 10% Niacinamide Serum",
        "brand": "Minimalist",
        "category": "Serum",
        "price": 599,
        "skin_types": ["Oily","Combination","Normal"],
        "concerns": ["Acne","Dark Spots","Uneven Tone"],
        "tones": ["Very Fair","Fair","Medium","Tan","Deep"],
        "ingredients": ["Niacinamide","Zinc"],
        "rating": 4.5,
        "why": "Niacinamide-based option for oily/combination skin and uneven tone.",
    },
    {
        "name": "L'Oreal Paris Total Repair 5 Shampoo",
        "brand": "L'Oreal Paris",
        "category": "Hair Care",
        "price": 399,
        "hair_types": ["Straight","Wavy","Curly"],
        "hair_concerns": ["Dryness","Damage","Frizz"],
        "ingredients": ["Conditioning Agents"],
        "rating": 4.5,
        "why": "Repair-focused shampoo option for dry or damaged hair.",
    },
    {
        "name": "Vaseline Rosy Lip Therapy",
        "brand": "Vaseline",
        "category": "Lip Care",
        "price": 185,
        "skin_types": ["Normal","Dry","Sensitive"],
        "concerns": ["Dryness"],
        "tones": ["Very Fair","Fair","Medium","Tan","Deep"],
        "ingredients": ["Petrolatum"],
        "rating": 4.7,
        "why": "Simple occlusive lip-care option for dry lips.",
    },
]


def recommend_beauty_products(
    category,
    budget_min,
    budget_max,
    skin_tone=None,
    skin_type=None,
    skin_concern=None,
):
    results = []

    type_key, concern_key = (
        ("hair_types", "hair_concerns")
        if category == "Hair Care"
        else ("skin_types", "concerns")
    )

    for product in BEAUTY_PRODUCTS:
        if product["category"] != category or not budget_min <= product["price"] <= budget_max:
            continue

        score, reasons = 50, []

        if skin_type and skin_type in product.get(type_key, []):
            score += 25
            reasons.append(
                f"Matches your {skin_type.lower()} "
                f"{'hair' if category == 'Hair Care' else 'skin'}"
            )

        if skin_concern and skin_concern in product.get(concern_key, []):
            score += 20
            reasons.append(f"Targets {skin_concern.lower()}")

        if skin_tone and skin_tone in product.get("tones", []):
            score += 5
            reasons.append(f"Suitable for {skin_tone.lower()} skin tone")

        if not reasons:
            reasons.append("Matches your selected category and budget")

        results.append({
            **product,
            "match_score": min(score, 100),
            "reasons": reasons,
        })

    return sorted(
        results,
        key=lambda x: (x["match_score"], x["rating"]),
        reverse=True,
    )


def recommendation_card(product, rank):
    reasons = "".join(
        f"<li>{escape(reason)}</li>"
        for reason in product["reasons"]
    )

    border = "#059669" if rank == 1 else "#e2eae5"
    bg = "#f0fdf8" if rank == 1 else "#ffffff"

    return dedent(f"""
    <div style="background:{bg};border:2px solid {border};border-radius:20px;padding:20px;margin:10px 0;box-shadow:0 6px 20px rgba(15,31,25,.06);">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
        <div>
          <div style="font-size:12px;font-weight:800;color:#059669;">
            {"🏆 TOP MATCH" if rank == 1 else f"#{rank} MATCH"}
          </div>
          <div style="font-size:21px;font-weight:800;color:#0f1f19;margin-top:4px;">
            {escape(product["name"])}
          </div>
          <div style="font-size:14px;color:#5b6b63;margin-top:3px;">
            {escape(product["brand"])} · {escape(product["category"])}
          </div>
        </div>
        <div style="text-align:right;white-space:nowrap;">
          <div style="font-size:23px;font-weight:800;color:#047857;">₹{product["price"]}</div>
          <div style="font-size:13px;color:#5b6b63;">⭐ {product["rating"]}</div>
        </div>
      </div>

      <div style="margin-top:14px;padding:10px 12px;background:#ffffff;border-radius:12px;font-size:14px;color:#334155;">
        <b>LabelLens Match Score: {product["match_score"]}/100</b>
      </div>

      <div style="margin-top:12px;font-size:14px;color:#334155;">
        <b>Why it matches you</b>
        <ul style="margin:6px 0 8px 20px;">{reasons}</ul>
      </div>

      <div style="font-size:13px;color:#475569;">
        <b>Key ingredients:</b> {escape(", ".join(product["ingredients"]))}
      </div>

      <div style="margin-top:10px;padding-top:10px;border-top:1px solid #e2eae5;font-size:13px;color:#5b6b63;">
        {escape(product["why"])}
      </div>
    </div>
    """).strip()


# =====================================================================
# HEADER + PROFILE
# =====================================================================

saved = database.load_profile() or {}

h1, h2 = st.columns([5, 2])

h1.markdown(
    f'<div class="brand">{LOGO}<b>Label<span>Lens</span></b><em>AI</em></div>',
    unsafe_allow_html=True,
)

with h2.popover("👤 My profile", width="stretch"):
    st.caption("Used to personalise alerts.")

    saved_tone = saved.get("skin_tone", "Medium / wheatish")
    if saved_tone not in SKIN_TONES:
        saved_tone = "Medium / wheatish"

    saved_concern = saved.get("concern", CONCERNS[0])
    if saved_concern not in CONCERNS:
        saved_concern = CONCERNS[0]

    saved_goal = saved.get("food_goal", "None")
    if saved_goal not in FOOD_GOALS:
        saved_goal = "None"

    tone = st.selectbox(
        "Skin tone", SKIN_TONES,
        index=SKIN_TONES.index(saved_tone),
        key="profile_tone",
    )

    concern = st.selectbox(
        "Skin concern", CONCERNS,
        index=CONCERNS.index(saved_concern),
        key="profile_concern",
    )

    goal = st.selectbox(
        "Food goal", FOOD_GOALS,
        index=FOOD_GOALS.index(saved_goal),
        key="profile_goal",
    )

    kids = st.toggle(
        "👶 Kids mode",
        value=bool(saved.get("kids_mode", False)),
        key="profile_kids",
    )

    profile = Profile(tone, concern, goal, kids)

    if st.button("💾 Save profile", width="stretch", key="save_profile"):
        p = profile.to_dict()
        database.save_profile(
            skin_tone=p.get("skin_tone", tone),
            concern=p.get("concern", concern),
            food_goal=p.get("food_goal", goal),
            kids_mode=p.get("kids_mode", kids),
        )
        st.toast("Profile saved ✅")


# =====================================================================
# TABS
# =====================================================================

tabs = st.tabs([
    "📷 Scan",
    "🥗 Nutrition",
    "⚖️ Compare",
    "🔎 Explore",
    "🛍️ Recommendations",
    "🕘 History",
])


# =====================================================================
# TAB 1 - SCAN
# =====================================================================

with tabs[0]:

    result = st.session_state.get("res")
    step = 3 if result else 2 if st.session_state.get("ocr_text", "").strip() else 1

    st.markdown(stepper(step), unsafe_allow_html=True)

    if not result:
        st.markdown(
            '<div class="intro"><h1>What is really inside your product?</h1>'
            "<p>Scan a food or skincare label. Get a clear verdict and every ingredient explained in plain words.</p>"
            '<div class="trust"><span>🔒 Photos are not saved</span>'
            '<span>🗣️ English + தமிழ்</span><span>🎯 Personal alerts</span></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="lbl">1 · What are you checking?</div>', unsafe_allow_html=True)

    cat_name = st.radio(
        "Product type",
        [CAT_F, CAT_S],
        horizontal=True,
        key="scan_cat",
        label_visibility="collapsed",
    )
    category = "f" if cat_name == CAT_F else "s"

    st.markdown('<div class="lbl">2 · Add the label</div>', unsafe_allow_html=True)

    source = st.radio(
        "How to add",
        [SRC_UP, SRC_CAM, SRC_TYPE],
        horizontal=True,
        label_visibility="collapsed",
    )

    file = None

    if source == SRC_UP:
        file = st.file_uploader(
            "Drop a clear photo of the ingredient list",
            type=["png", "jpg", "jpeg", "webp"],
        )
    elif source == SRC_CAM:
        file = st.camera_input("Photo of the ingredient list")

    if file is not None:
        img = Image.open(file)
        st.image(img, caption="Your label", width="stretch")

        if st.button("🔍 Read text from photo", type="primary", width="stretch"):
            try:
                with st.spinner("Reading text..."):
                    raw, confidence = read_text(img)

                st.session_state.update(
                    raw_text=raw,
                    ocr_text=extract_ingredients(raw),
                    ocr_conf=confidence,
                )
            except Exception as error:
                st.error(f"OCR failed: {error}")

    st.caption("Or try a sample demo:")

    for column, (name, demo) in zip(
        st.columns(len(DEMOS)),
        DEMOS.items(),
    ):
        column.button(
            name,
            key=f"demo_{name}",
            on_click=load_demo,
            args=demo,
            width="stretch",
        )

    st.markdown('<div class="lbl">3 · Review ingredients</div>', unsafe_allow_html=True)

    text = st.text_area(
        "Ingredients",
        key="ocr_text",
        height=120,
        label_visibility="collapsed",
        placeholder="Type or paste ingredient list here...",
    )

    analyse_button = st.button(
        "✨ Analyse this label",
        type="primary",
        width="stretch",
    )

    automatic = st.session_state.pop("run_check", False)

    if analyse_button or automatic:
        if not text.strip():
            st.warning("Add a photo or type ingredients first.")
        else:
            hits, unknown = analyze(text, category, DB)

            if profile.kids_mode:
                hits = apply_kids(hits, category)

            infos = [unknown_explainer.explain(x, category) for x in unknown]
            safety = safety_verdict(hits, [x["skey"] for x in infos])

            st.session_state["res"] = {
                "hits": hits,
                "unknown": unknown,
                "cat": category,
                "sk": safety,
                "kids": profile.kids_mode,
            }

            st.session_state.pop("ai_unknown", None)

            database.save_scan(
                "",
                category,
                text,
                {"bad": "bad", "warn": "warn", "mid": "warn", "good": "good"}.get(safety[0], "good"),
                "",
            )

    result = st.session_state.get("res")

    if result:
        hits = result["hits"]
        unknown = result["unknown"]
        result_category = result["cat"]
        key, emoji, title, sub = result["sk"]

        kids_text = " · 👶 Kids mode" if result["kids"] else ""

        st.markdown(
            f'<div class="verdict {key}"><div class="v-left">'
            f'<div class="v-icon">{emoji}</div><div>'
            f'<div class="v-kicker">Safety Verdict{kids_text}</div>'
            f'<h2>{escape(title)}</h2><p>{escape(sub)}</p>'
            f'</div></div><div class="v-ring">{ring(label_score(hits), VCOLOR[key])}'
            f'<small>LabelScore / 100</small></div></div>',
            unsafe_allow_html=True,
        )

        count = lambda level: sum(x["level"] == level for x in hits)

        st.markdown(
            f'<div class="tiles">'
            f'<div class="tile bad"><b>{count("bad")}</b><span>🚨 Alerts</span></div>'
            f'<div class="tile warn"><b>{count("warn")}</b><span>⚠️ Care</span></div>'
            f'<div class="tile good"><b>{count("good")}</b><span>✅ Beneficial</span></div>'
            f'<div class="tile unk"><b>{len(unknown)}</b><span>❓ Unknown</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        confidence_level, confidence_reason = ai_explainer.confidence(
            len(hits),
            len(unknown),
            st.session_state.get("ocr_conf"),
        )

        st.markdown(
            f'<div class="conf"><b>Confidence: {escape(str(confidence_level))}</b> · '
            f'{escape(str(confidence_reason))}</div>',
            unsafe_allow_html=True,
        )

        english_summary = ai_explainer.summarize(
            hits, unknown, key, result_category
        )
        note(english_summary)

        for personal_note in personal_notes(hits, result_category, profile):
            st.markdown(
                f'<div class="note">🎯 For you: {escape(personal_note)}</div>',
                unsafe_allow_html=True,
            )

        filter_option = st.radio(
            "Filter ingredients",
            FILTERS,
            horizontal=True,
            key="ingredient_filter",
        )

        filtered_hits = [
            item for item in hits
            if filter_option == "All"
            or filter_option == "Alerts" and item["level"] == "bad"
            or filter_option == "Care" and item["level"] in ("warn", "mid")
            or filter_option == "Safe" and item["level"] == "good"
        ]

        section("Recognised ingredients", f"Showing {len(filtered_hits)} of {len(hits)}")

        for index, item in enumerate(filtered_hits):
            row(item, open_=item["level"] == "bad", idx=index)

        swaps = guides.swaps_for(hits)

        if swaps:
            section("Healthier swaps", "Suggested alternatives")
            swap_html = "".join(
                f'<div class="swap"><b>Instead of {escape(name)}:</b> {escape(value)}</div>'
                for name, value in swaps
            )
            st.markdown(
                f'<div class="swaps">{swap_html}</div>',
                unsafe_allow_html=True,
            )

        if unknown:
            section("Unknown ingredients", "Items not found in our database")
            for index, item in enumerate(unknown):
                unknown_row(item, result_category, index)

        section("Tamil summary & Audio", "தமிழ் சுருக்கம்")

        tamil_summary = ai_explainer.tamil_summary(
            hits, unknown, result_category, key
        )

        st.info(tamil_summary)
        speak_buttons(english_summary, tamil_summary)

        st.download_button(
            "📄 Download report",
            ai_explainer.build_report(
                hits, unknown, result_category, title, sub, swaps
            ),
            file_name="labellens_report.txt",
            width="stretch",
        )

        if st.button(
            "🔄 Scan another product",
            on_click=reset_scan,
            width="stretch",
        ):
            st.rerun()


# =====================================================================
# TAB 2 - NUTRITION
# =====================================================================

with tabs[1]:

    section(
        "Nutrition facts checker",
        "Analyze calories, sugar, sodium, and fats per serving.",
    )

    if st.button("📥 Load sample nutrition table"):
        load_nut()

    nutrition_text = st.text_area(
        "Nutrition text",
        key="nut_text",
        height=130,
        placeholder="Paste nutrition facts here...",
    )

    parsed = (
        nutrition.parse_nutrition(nutrition_text)
        if nutrition_text.strip()
        else {"values": {}, "serving_g": None, "per100_hint": False}
    )

    if parsed["values"]:

        basis = st.radio(
            "Values are per",
            ["100 g", "1 serving"],
            horizontal=True,
            key="nutrition_basis",
        )

        basis_amount = 100.0 if basis == "100 g" else float(parsed["serving_g"] or 30)

        eaten = st.number_input(
            "Portion you will eat (grams)",
            min_value=1.0,
            value=float(parsed["serving_g"] or 50),
            key="nutrition_portion",
        )

        section(f"For {eaten:.0f} g portion")
        bars(nutrition.scale(parsed["values"], basis_amount, eaten))


# =====================================================================
# TAB 3 - COMPARE
# =====================================================================

with tabs[2]:

    section(
        "Product Comparison",
        "Compare two ingredient lists side by side.",
    )

    compare_name = st.radio(
        "Type",
        [CAT_F, CAT_S],
        horizontal=True,
        key="cmp_cat",
    )

    compare_category = "f" if compare_name == CAT_F else "s"

    col1, col2 = st.columns(2)

    product_a = col1.text_area(
        "Product A ingredients",
        height=120,
        key="product_a",
    )

    product_b = col2.text_area(
        "Product B ingredients",
        height=120,
        key="product_b",
    )

    compare_button = st.button(
        "⚔️ Compare",
        type="primary",
        width="stretch",
        key="compare_button",
    )

    if compare_button and product_a.strip() and product_b.strip():

        hits_a, _ = analyze(product_a, compare_category, DB)
        hits_b, _ = analyze(product_b, compare_category, DB)

        comparison = compare(hits_a, hits_b)
        score_a, score_b = label_score(hits_a), label_score(hits_b)
        winner = comparison["fewer_concerns"]

        boxes = ""

        for name, score, is_winner in (
            ("A", score_a, winner == "A"),
            ("B", score_b, winner == "B"),
        ):
            title_text, color = grade(score)
            boxes += (
                f'<div class="cmpbox {"win" if is_winner else ""}">'
                f'<b>{"👑 " if is_winner else ""}Product {name}</b>'
                f'{ring(score, color, 110)}'
                f'<div style="color:{color};font-weight:800">{title_text}</div>'
                f'</div>'
            )

        st.markdown(
            f'<div class="cmp">{boxes}</div>',
            unsafe_allow_html=True,
        )


# =====================================================================
# TAB 4 - EXPLORE
# =====================================================================

with tabs[3]:

    section(
        "Explore",
        "Choose your care goal and get personalised product recommendations.",
    )

    care_type = st.radio(
        "What are you looking for?",
        ["🧴 Skin Care", "💇 Hair Care", "💋 Lip Care"],
        horizontal=True,
        key="explore_care",
    )

    if care_type == "🧴 Skin Care":

        recommendation_category = st.selectbox(
            "Product type",
            ["Skin Care", "Serum"],
            key="explore_skin_product",
        )

        selected_type = st.selectbox(
            "Your skin type",
            ["Normal", "Oily", "Dry", "Combination", "Sensitive"],
            key="explore_skin_type",
        )

        selected_problem = st.selectbox(
            "Your skin problem",
            ["None", "Acne", "Dark Spots", "Uneven Tone", "Dullness", "Dryness", "Sensitive Skin"],
            key="explore_skin_problem",
        )

        selected_tone = st.selectbox(
            "Your skin colour",
            ["Very Fair", "Fair", "Medium", "Tan", "Deep"],
            index=2,
            key="explore_skin_tone",
        )

    elif care_type == "💇 Hair Care":

        recommendation_category = "Hair Care"

        selected_type = st.selectbox(
            "Your hair type",
            ["Straight", "Wavy", "Curly"],
            key="explore_hair_type",
        )

        selected_problem = st.selectbox(
            "Your hair problem",
            ["Dryness", "Damage", "Frizz"],
            key="explore_hair_problem",
        )

        selected_tone = None

    else:

        recommendation_category = "Lip Care"

        selected_type = st.selectbox(
            "Your lip type",
            ["Normal", "Dry", "Sensitive"],
            key="explore_lip_type",
        )

        selected_problem = st.selectbox(
            "Your lip problem",
            ["Dryness"],
            key="explore_lip_problem",
        )

        selected_tone = st.selectbox(
            "Your skin colour",
            ["Very Fair", "Fair", "Medium", "Tan", "Deep"],
            index=2,
            key="explore_lip_tone",
        )

    price_col1, price_col2 = st.columns(2)

    minimum_price = price_col1.number_input(
        "Min Price (₹)",
        min_value=0,
        value=100,
        key="explore_min_price",
    )

    maximum_price = price_col2.number_input(
        "Max Price (₹)",
        min_value=50,
        value=1000,
        key="explore_max_price",
    )

    if st.button(
        "🔍 Explore Products",
        type="primary",
        width="stretch",
        key="explore_products",
    ):

        if minimum_price > maximum_price:
            st.error("Minimum price cannot be greater than maximum price.")

        else:

            matches = recommend_beauty_products(
                recommendation_category,
                minimum_price,
                maximum_price,
                skin_tone=selected_tone,
                skin_type=selected_type,
                skin_concern=None if selected_problem == "None" else selected_problem,
            )

            if matches:

                st.markdown("### 🏆 Recommended for you")

                st.caption(
                    f"Based on {selected_type} and {selected_problem.lower()}."
                )

                for index, product in enumerate(matches[:3], 1):
                    st.markdown(
                        recommendation_card(product, index),
                        unsafe_allow_html=True,
                    )

            else:
                empty(
                    "🛍️",
                    "No matching products found. Try increasing your budget.",
                )


# =====================================================================
# TAB 5 - RECOMMENDATIONS
# =====================================================================

with tabs[4]:

    section(
        "Personalised Product Recommendations",
        "Quick recommendations using your saved profile.",
    )

    rec_category = st.selectbox(
        "Category",
        ["Skin Care", "Serum", "Hair Care", "Lip Care"],
        key="recommend_category",
    )

    price1, price2 = st.columns(2)

    rec_min = price1.number_input(
        "Min Price (₹)",
        min_value=0,
        value=100,
        key="recommend_min",
    )

    rec_max = price2.number_input(
        "Max Price (₹)",
        min_value=50,
        value=1000,
        key="recommend_max",
    )

    if st.button(
        "🔍 Find Top Matches",
        type="primary",
        width="stretch",
        key="find_matches",
    ):

        if rec_min > rec_max:
            st.error("Minimum price cannot be greater than maximum price.")

        else:

            # FIX: correct selection based on category
            selection_map = {
                "Hair Care": (
                    "explore_hair_type",
                    "explore_hair_problem",
                    "Straight",
                    "Dryness",
                ),
                "Lip Care": (
                    "explore_lip_type",
                    "explore_lip_problem",
                    "Normal",
                    "Dryness",
                ),
                "Skin Care": (
                    "explore_skin_type",
                    "explore_skin_problem",
                    "Normal",
                    profile.concern,
                ),
                "Serum": (
                    "explore_skin_type",
                    "explore_skin_problem",
                    "Normal",
                    profile.concern,
                ),
            }

            type_key, problem_key, default_type, default_problem = selection_map[rec_category]

            saved_type = st.session_state.get(
                type_key,
                default_type,
            )

            saved_problem = st.session_state.get(
                problem_key,
                default_problem,
            )

            # Hair doesn't need skin tone.
            rec_tone = (
                None
                if rec_category == "Hair Care"
                else profile.skin_tone
            )

            matches = recommend_beauty_products(
                rec_category,
                rec_min,
                rec_max,
                skin_tone=rec_tone,
                skin_type=saved_type,
                skin_concern=saved_problem,
            )

            if matches:

                st.markdown("### 🏆 Top matches for you")

                for index, product in enumerate(matches[:3], 1):
                    st.markdown(
                        recommendation_card(product, index),
                        unsafe_allow_html=True,
                    )

            else:
                empty(
                    "🛍️",
                    "No products found. Try a wider price range.",
                )


# =====================================================================
# TAB 6 - HISTORY
# =====================================================================

with tabs[5]:

    section(
        "Scan History",
        "Recent products you have checked.",
    )

    rows = database.get_scans()

    if rows:

        for scan in rows:

            timestamp = scan.get("created_at", "")
            scan_category = scan.get("category", "")
            verdict = scan.get("verdict", "")
            ingredients = scan.get("ingredients", "")

            icon = {
                "bad": "🔴",
                "warn": "🟠",
                "good": "🟢",
            }.get(verdict, "⚪")

            category_label = "🍜 Food" if scan_category == "f" else "🧴 Skin"
            display_text = str(ingredients) if ingredients else "No ingredients saved"

            st.markdown(
                f'<div class="hist {escape(str(verdict))}">'
                f'{icon} <b>{category_label}</b> · '
                f'<small>{escape(str(timestamp))}</small><br>'
                f'{escape(display_text)}</div>',
                unsafe_allow_html=True,
            )

        if st.button("🗑️ Clear history", key="clear_history"):
            database.clear_scans()
            st.rerun()

    else:
        empty(
            "🕘",
            "No scans yet. Check a label in the Scan tab.",
        )


# =====================================================================
# FOOTER
# =====================================================================

st.divider()

st.caption(
    "General information only, not medical advice. "
    "Patch-test new skincare products."
)