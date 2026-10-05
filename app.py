"""LabelLens AI - Super UI edition.  Run with:  streamlit run app.py"""
import json
from html import escape

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

import ai_explainer
import database
import guides
import unknown_explainer
import nutrition
from ingredient_matcher import SAFE_LABEL, analyze, compare, load_db, safety_verdict, search
from ocr_engine import read_text
from personalization import CONCERNS, FOOD_GOALS, SKIN_TONES, Profile, apply_kids, personal_notes
from text_processor import extract_ingredients, extract_nutrition_block

st.set_page_config(page_title="LabelLens AI", page_icon="🔍", layout="centered")
database.init_db()

CSS = """
<style>
.block-container{padding-top:1rem;max-width:860px}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#f6f7fd !important;color:#1e1b4b !important}
[data-testid="stHeader"]{background:transparent !important}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label,.stApp li,.stApp summary,.stApp [data-testid="stWidgetLabel"] p{color:#1e1b4b !important}
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *{color:#64748b !important}
.stApp [data-baseweb="select"]>div,.stApp [data-baseweb="input"]>div,.stApp [data-baseweb="textarea"],.stApp textarea,.stApp input{background:#fff !important;color:#1e1b4b !important;border-color:#d9def0 !important;border-radius:12px !important}
.stApp [data-baseweb="select"] *{color:#1e1b4b !important}
[data-baseweb="popover"],[data-baseweb="popover"] ul,[data-baseweb="popover"] li,[data-baseweb="menu"]{background:#fff !important;color:#1e1b4b !important}
[data-testid="stFileUploaderDropzone"]{background:#fff !important;border:2px dashed #a5b4fc !important;border-radius:18px !important}
[data-testid="stFileUploaderDropzone"] *{color:#475569 !important}
[data-testid="stExpander"]{background:#fff !important;border:1px solid #e0e7ff !important;border-radius:16px !important}
.stApp .stButton>button{background:#fff !important;border:1.5px solid #c7d2fe !important;border-radius:12px !important;transition:.15s}
.stApp .stButton>button:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(79,70,229,.18)}
.stApp .stButton>button p{color:#4f46e5 !important;font-weight:700}
.stApp .stButton>button[kind="primary"],.stApp .stButton>button[data-testid="stBaseButton-primary"]{background:linear-gradient(90deg,#4f46e5,#9333ea) !important;border:0 !important}
.stApp .stButton>button[kind="primary"] p,.stApp .stButton>button[data-testid="stBaseButton-primary"] p{color:#fff !important}
.stApp [role="tablist"]{gap:6px !important;background:#e9ebfb !important;padding:6px !important;border-radius:16px !important;border:0 !important;overflow-x:auto}
.stApp button[role="tab"]{border-radius:12px !important;padding:8px 14px !important;background:transparent !important;height:auto !important}
.stApp button[role="tab"] p{color:#64748b !important;font-weight:600}
.stApp button[role="tab"][aria-selected="true"]{background:#fff !important;box-shadow:0 2px 8px rgba(79,70,229,.25) !important}
.stApp button[role="tab"][aria-selected="true"] p{color:#4f46e5 !important;font-weight:800 !important}
.stApp [data-baseweb="tab-highlight"],.stApp [data-baseweb="tab-border"]{display:none !important}

.hero{display:flex;align-items:center;justify-content:space-between;gap:16px;background:linear-gradient(120deg,#4f46e5,#9333ea,#ec4899,#f59e0b,#4f46e5);background-size:300% 300%;animation:grad 9s ease infinite;position:relative;border-radius:26px;padding:26px 28px;margin-bottom:16px;box-shadow:0 14px 34px rgba(79,70,229,.35);overflow:hidden}
.stApp .hero h1{margin:0;font-size:38px;font-weight:900;letter-spacing:-1px;color:#fff !important}
.stApp .hero h1 span{color:#fde68a !important}
.stApp .hero p{margin:6px 0 12px;font-size:16px;color:#f5f3ff !important}
.badges span{display:inline-block;background:rgba(255,255,255,.2);color:#fff;border-radius:99px;padding:4px 12px;margin:3px 4px 0 0;font-size:13px;font-weight:600}
.phone{position:relative;flex:none;width:112px;height:150px;background:#fff;border-radius:18px;padding:16px 12px;box-shadow:0 8px 20px rgba(0,0,0,.25);transform:rotate(6deg);animation:float 3s ease-in-out infinite}
.phone i{display:block;height:8px;border-radius:4px;background:#e0e7ff;margin-bottom:9px}
.phone i:nth-child(2){width:70%}.phone i:nth-child(4){width:85%;background:#fecdd3}.phone i:nth-child(6){width:55%}
.scan{position:absolute;left:6px;right:6px;height:3px;border-radius:3px;background:#22c55e;box-shadow:0 0 12px #22c55e;animation:scan 2s ease-in-out infinite}
@keyframes scan{0%{top:14px}50%{top:128px}100%{top:14px}}
@keyframes float{0%,100%{transform:rotate(6deg) translateY(0)}50%{transform:rotate(6deg) translateY(-8px)}}
@media(max-width:560px){.phone{display:none}.stApp .hero h1{font-size:30px}}

.result{display:flex;align-items:center;gap:20px;background:#fff;border-radius:22px;padding:18px 22px;margin:10px 0;box-shadow:0 8px 24px rgba(30,27,75,.08);border:1px solid #eceffa}
.ringfill{animation:ring 1.2s ease-out}
@keyframes ring{from{stroke-dashoffset:339.3}}
.result h2{margin:0;font-size:24px;font-weight:900}.result .sub{margin:4px 0 0;color:#475569;font-size:14px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0}
.stat{background:#fff;border-radius:16px;padding:12px 6px;text-align:center;border:1px solid #eceffa;box-shadow:0 4px 12px rgba(30,27,75,.05)}
.stat b{display:block;font-size:28px;font-weight:900;line-height:1.1}.stat span{font-size:12px;color:#64748b}
.stat.bad b{color:#e11d48}.stat.warn b{color:#f59e0b}.stat.good b{color:#10b981}.stat.unk b{color:#64748b}
@media(max-width:560px){.stats{grid-template-columns:repeat(2,1fr)}.result{flex-direction:column;text-align:center}}

details.row{background:#fff;border:1px solid #eceffa;border-left:6px solid #94a3b8;border-radius:16px;margin:9px 0;padding:0 16px;box-shadow:0 4px 12px rgba(30,27,75,.05)}
details.row.good{border-left-color:#10b981}details.row.warn{border-left-color:#f59e0b}details.row.bad{border-left-color:#e11d48;animation:shake .5s}
@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-6px)}40%{transform:translateX(6px)}60%{transform:translateX(-4px)}80%{transform:translateX(4px)}}
details.row summary{cursor:pointer;padding:13px 0;font-weight:800;list-style:none;display:flex;align-items:center;gap:10px}
details.row summary::-webkit-details-marker{display:none}
.pill{margin-left:auto;font-size:12px;font-weight:800;padding:4px 11px;border-radius:99px}
.p-good{background:#d1fae5;color:#047857}.p-warn{background:#fef3c7;color:#92400e}.p-bad{background:#ffe4e6;color:#be123c}.p-ok{background:#eef2f6;color:#64748b}
.stApp .body{padding:0 0 14px 4px;font-size:14px}.stApp .body p{margin:5px 0;color:#334155 !important}
.stApp .body p.adv{color:#047857 !important}.stApp .body p.dis{color:#be123c !important}

.banner{border-radius:16px;padding:14px 18px;font-weight:800;margin:8px 0}
.stApp .banner.bad{background:#ffe4e6;color:#be123c !important}.stApp .banner.warn{background:#fef3c7;color:#92400e !important}.stApp .banner.good{background:#d1fae5;color:#047857 !important}
.tip{background:#eef2ff;border-left:5px solid #6366f1;border-radius:14px;padding:11px 15px;margin:8px 0;font-size:14px;color:#1e1b4b}
.chip{display:inline-block;background:#eef2ff;color:#4338ca;border-radius:99px;padding:4px 13px;margin:3px;font-size:13px;font-weight:600}

.bar{margin:10px 0}.bar-top{display:flex;justify-content:space-between;font-size:14px;font-weight:700;margin-bottom:4px}
.track{height:12px;background:#e9ebfb;border-radius:8px;overflow:hidden}.fill{height:100%;border-radius:8px;transition:width 1s}
.sw{display:flex;gap:14px;justify-content:center;margin:8px 0 14px}
.sw div{text-align:center;font-size:12px;color:#64748b;width:72px}
.sw i{display:block;width:52px;height:52px;border-radius:50%;margin:0 auto 5px;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.2)}
.sw .on i{box-shadow:0 0 0 4px #6366f1}.sw .on{color:#4f46e5;font-weight:800}
.hist{background:#fff;border:1px solid #eceffa;border-radius:16px;padding:10px 16px;margin:8px 0;font-size:14px}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:12px}.cmpbox{background:#fff;border-radius:20px;padding:14px;text-align:center;border:2px solid #eceffa}
.cmpbox.win{border-color:#10b981;box-shadow:0 8px 22px rgba(16,185,129,.2)}

@property --n{syntax:"<integer>";inherits:false;initial-value:0}
.ringwrap{position:relative;flex:none}
.ringwrap .num{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:900;counter-reset:n var(--n);animation:cnt 1.3s ease-out forwards}
.ringwrap .num:before{content:counter(n)}
@keyframes cnt{from{--n:0}to{--n:var(--t)}}
@keyframes grad{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.hero:before,.hero:after{content:"";position:absolute;border-radius:50%;background:rgba(255,255,255,.14);animation:drift 7s ease-in-out infinite}
.hero:before{width:130px;height:130px;left:-30px;bottom:-50px}
.hero:after{width:90px;height:90px;right:150px;top:-30px;animation-delay:-3s}
.hero>*{position:relative;z-index:1}
@keyframes drift{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(18px,-16px) scale(1.15)}}
.badges span{animation:bob 3s ease-in-out infinite}.badges span:nth-child(2){animation-delay:.3s}.badges span:nth-child(3){animation-delay:.6s}.badges span:nth-child(4){animation-delay:.9s}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.ticker{overflow:hidden;white-space:nowrap;background:#fff;border-radius:99px;border:1px solid #e0e7ff;padding:8px 0;margin-bottom:14px}
.track2{display:inline-block;animation:marq 40s linear infinite}
.track2 span{display:inline-block;margin:0 28px;font-size:13px;font-weight:600;color:#4338ca}
@keyframes marq{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes slidein{from{opacity:0;transform:translateY(16px)}}
@keyframes pop{from{opacity:0;transform:scale(.88)}}
@keyframes glow{0%,100%{box-shadow:0 0 0 0 rgba(225,29,72,.4)}50%{box-shadow:0 0 0 10px rgba(225,29,72,0)}}
@keyframes grow{from{width:0}}
@keyframes btnpulse{0%,100%{box-shadow:0 0 0 0 rgba(147,51,234,.45)}50%{box-shadow:0 0 0 10px rgba(147,51,234,0)}}
details.row{animation:slidein .5s var(--d,0s) both}
details.row.bad{animation:slidein .5s var(--d,0s) both,shake .5s calc(var(--d,0s) + .55s),glow 2s calc(var(--d,0s) + 1.2s) infinite}
details.row.unk{border-left-color:#94a3b8}
.result{animation:pop .6s both}
.stat{animation:pop .5s both}.stat:nth-child(2){animation-delay:.1s}.stat:nth-child(3){animation-delay:.2s}.stat:nth-child(4){animation-delay:.3s}
.banner{animation:slidein .5s both}
.fill{animation:grow 1.2s ease-out}
.cmpbox{animation:pop .6s both}
.sw i{transition:transform .2s}.sw .on i{transform:scale(1.18)}
.stApp .stButton>button[kind="primary"],.stApp .stButton>button[data-testid="stBaseButton-primary"]{animation:btnpulse 2.4s infinite}

.p-ok{background:#d1fae5;color:#047857}.p-unk{background:#eef2f6;color:#64748b}
.safe{display:flex;align-items:center;gap:18px;border-radius:24px;padding:18px 24px;margin:10px 0;animation:pop .6s both;box-shadow:0 10px 26px rgba(30,27,75,.12)}
.safe .big{font-size:56px;line-height:1;animation:bounce 1.6s ease-in-out infinite}
.stApp .safe h2{margin:0;font-size:28px;font-weight:900;letter-spacing:.5px}
.stApp .safe p{margin:4px 0 0;font-size:14px}
.safe.good{background:#d1fae5}.stApp .safe.good h2,.stApp .safe.good p{color:#047857 !important}
.safe.mid{background:#ecfccb}.stApp .safe.mid h2,.stApp .safe.mid p{color:#4d7c0f !important}
.safe.warn{background:#fef3c7}.stApp .safe.warn h2,.stApp .safe.warn p{color:#92400e !important}
.safe.bad{background:#ffe4e6}.stApp .safe.bad h2,.stApp .safe.bad p{color:#be123c !important}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none !important;transition:none !important}.ringwrap .num{--n:var(--t)}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

LABEL = SAFE_LABEL
CAT_F, CAT_S = "🍜 Food", "🧴 Skincare / makeup / haircare"
SWATCH = {"Fair": "#f6dcc8", "Medium / wheatish": "#e0b48e", "Tan / brown": "#b27b52", "Deep / dark brown": "#6b4226"}
DEMOS = {
    "🍜 Noodles": ("Wheat flour, Palm oil, Salt, Sugar, Monosodium glutamate, Tartrazine (E102), Sodium benzoate, Disodium inosinate, Acidity regulator (E501), Spirulina extract, Spices", CAT_F),
    "🥤 Soft drink": ("Carbonated water, Sugar, High fructose corn syrup, Citric acid, Sodium benzoate, Aspartame, Flavour", CAT_F),
    "🧴 Face cream": ("Water, Glycerin, Niacinamide, Hyaluronic acid, Zinc oxide, Dimethicone, Fragrance, Methylparaben, Bakuchiol, Centella asiatica extract, Ceteareth-20", CAT_S),
    "⚠️ Fairness cream": ("Water, Hydroquinone, Mercury chloride, Glycerin, Fragrance", CAT_S),
}


@st.cache_data
def get_db():
    return load_db()


DB = get_db()


def label_score(hits):
    s = 100 + sum({"bad": -25, "warn": -8, "good": 3, "ok": 0}[h["level"]] for h in hits)
    return max(0, min(100, s))


def grade(s):
    if s >= 80:
        return "Great pick 🎉", "#10b981"
    if s >= 60:
        return "Okay, use with care 🙂", "#84cc16"
    if s >= 40:
        return "Be careful ⚠️", "#f59e0b"
    return "Better avoided 🚫", "#e11d48"


def ring(score, color, size=150):
    off = 339.3 * (1 - score / 100)
    return (f'<div class="ringwrap" style="width:{size}px;height:{size}px"><svg width="{size}" height="{size}" viewBox="0 0 150 150">'
            f'<circle cx="75" cy="75" r="54" fill="none" stroke="#e9ebfb" stroke-width="14"/>'
            f'<circle class="ringfill" cx="75" cy="75" r="54" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" '
            f'stroke-dasharray="339.3" stroke-dashoffset="{off:.1f}" transform="rotate(-90 75 75)"/></svg>'
            f'<div class="num" style="--t:{score};color:{color};font-size:{int(size * 0.27)}px"></div></div>')


def row(r, open_=False, idx=0):
    lvl = r["level"]
    st.markdown(
        f'<details class="row {lvl}" style="--d:{idx * 0.08:.2f}s" {"open" if open_ else ""}><summary>{escape(r["name"])}<span class="pill p-{lvl}">{LABEL[lvl]}</span></summary>'
        f'<div class="body"><p><b>What it is:</b> {escape(r["what"])}</p><p class="adv"><b>Advantage:</b> {escape(r["advantage"])}</p>'
        f'<p class="dis"><b>Disadvantage:</b> {escape(r["disadvantage"])}</p></div></details>',
        unsafe_allow_html=True,
    )


def unknown_row(u, cat, idx=0):
    info = unknown_explainer.explain(u, cat)
    pill = {"ok": "p-ok", "limit": "p-warn", "check": "p-unk"}[info["skey"]]
    icon = {"ok": "✅", "limit": "⚠️", "check": "❓"}[info["skey"]]
    st.markdown(
        f'<details class="row unk" style="--d:{idx * 0.08:.2f}s"><summary>{escape(u)}<span class="pill {pill}">{icon} {escape(info["safety"])}</span></summary>'
        f'<div class="body"><p><b>Looks like:</b> {escape(info["kind"])}</p><p><b>What it does:</b> {escape(info["text"])}</p>'
        f'<p><b>Confidence:</b> {escape(info["conf"])} (pattern-based guess, not from our database)</p>'
        f'<p><b>What to do:</b> {escape(info["advice"])}</p></div></details>',
        unsafe_allow_html=True,
    )


def speak_buttons(en, ta):
    """Read-aloud buttons. Texts are passed as JS variables (not inside HTML attributes) so quotes cannot break them."""
    safe = lambda t: json.dumps(t).replace("</", "<\\/")
    html = r"""
<div style="display:flex;gap:10px;flex-wrap:wrap;font-family:sans-serif">
<button id="en" style="padding:10px 16px;border:0;border-radius:12px;color:#fff;font-weight:700;background:linear-gradient(90deg,#4f46e5,#9333ea);cursor:pointer">🔊 Read in English</button>
<button id="ta" style="padding:10px 16px;border:0;border-radius:12px;color:#fff;font-weight:700;background:linear-gradient(90deg,#ec4899,#f59e0b);cursor:pointer">🔊 தமிழில் கேளுங்கள்</button>
<button id="stop" style="padding:10px 16px;border:1px solid #c7d2fe;border-radius:12px;color:#4f46e5;font-weight:700;background:#fff;cursor:pointer">⏹ Stop</button>
</div>
<div id="msg" style="font:13px sans-serif;color:#64748b;margin-top:8px;min-height:18px"></div>
<script>
const EN = %%EN%%, TA = %%TA%%;
const msg = document.getElementById('msg');
function getVoices(){return new Promise(function(res){
  var v = speechSynthesis.getVoices(); if (v.length) return res(v);
  speechSynthesis.onvoiceschanged = function(){res(speechSynthesis.getVoices());};
  setTimeout(function(){res(speechSynthesis.getVoices());}, 1500);});}
async function say(text, lang, label){
  if (!('speechSynthesis' in window)) { msg.textContent = 'This browser cannot read aloud. Try Chrome or Edge.'; return; }
  var vs = await getVoices(), base = lang.split('-')[0];
  var v = vs.find(function(x){return x.lang.replace('_','-').toLowerCase() === lang.toLowerCase();}) ||
          vs.find(function(x){return x.lang.toLowerCase().indexOf(base) === 0;});
  if (!v && base === 'ta') { msg.textContent = 'No Tamil voice found on this device. Try Microsoft Edge (it has online Tamil voices), or add Tamil speech in Windows Settings > Time & language > Speech.'; return; }
  speechSynthesis.cancel();
  var parts = text.split(/(?<=[.!?\u0964])\s+/).filter(Boolean);
  parts.forEach(function(p, i){
    var u = new SpeechSynthesisUtterance(p);
    if (v) { u.voice = v; u.lang = v.lang; } else { u.lang = lang; }
    if (i === 0) u.onstart = function(){msg.textContent = 'Reading ' + label + '...';};
    if (i === parts.length - 1) u.onend = function(){msg.textContent = '';};
    u.onerror = function(e){msg.textContent = 'Could not play audio (' + e.error + '). Check the tab is not muted.';};
    speechSynthesis.speak(u);
  });
}
document.getElementById('en').addEventListener('click', function(){say(EN, 'en-IN', 'English');});
document.getElementById('ta').addEventListener('click', function(){say(TA, 'ta-IN', 'Tamil');});
document.getElementById('stop').addEventListener('click', function(){speechSynthesis.cancel(); msg.textContent = '';});
</script>
"""
    components.html(html.replace("%%EN%%", safe(en)).replace("%%TA%%", safe(ta)), height=110)


def banner(level, msg):
    st.markdown(f'<div class="banner {level}">{escape(msg)}</div>', unsafe_allow_html=True)


def tip(msg):
    st.markdown(f'<div class="tip">{escape(msg)}</div>', unsafe_allow_html=True)


def stats(hits, unknown):
    n = lambda l: sum(h["level"] == l for h in hits)
    st.markdown(
        f'<div class="stats"><div class="stat bad"><b>{n("bad")}</b><span>🚨 Alerts</span></div><div class="stat warn"><b>{n("warn")}</b><span>⚠️ Care</span></div>'
        f'<div class="stat good"><b>{n("good")}</b><span>✅ Beneficial</span></div><div class="stat unk"><b>{len(unknown)}</b><span>❓ Unknown</span></div></div>',
        unsafe_allow_html=True,
    )


def result_card(hits):
    s = label_score(hits)
    title, color = grade(s)
    st.markdown(
        f'<div class="result">{ring(s, color)}<div><h2 style="color:{color} !important">{title}</h2>'
        f'<p class="sub">LabelScore out of 100, based on the ingredients we recognise. Amounts are not on labels, so treat it as a guide.</p></div></div>',
        unsafe_allow_html=True,
    )
    return s


def bars(eaten_vals):
    good_high = {"protein", "fibre"}
    html = ""
    for k, v in eaten_vals.items():
        if k not in nutrition.DAILY:
            continue
        pct = v / nutrition.DAILY[k] * 100
        color = "#6366f1" if k in good_high else ("#10b981" if pct < 30 else "#f59e0b" if pct < 60 else "#e11d48")
        html += (f'<div class="bar"><div class="bar-top"><span>{nutrition.NAMES[k]}</span><span>{v:.1f} · {pct:.0f}% of day</span></div>'
                 f'<div class="track"><div class="fill" style="width:{min(pct, 100):.0f}%;background:{color}"></div></div></div>')
    st.markdown(html, unsafe_allow_html=True)


def load_demo(text, cat):
    st.session_state["ocr_text"] = text
    st.session_state["cat"] = cat
    st.session_state["run_check"] = True


# ---------- hero ----------
st.markdown(
    '<div class="hero"><div><h1>Label<span>Lens</span> AI</h1><p>Point. Scan. Know what is inside.</p>'
    '<div class="badges"><span>🍜 Food</span><span>🧴 Skincare</span><span>🎨 Skin-tone smart</span><span>🚨 Danger alerts</span></div></div>'
    '<div class="phone"><div class="scan"></div><i></i><i></i><i></i><i></i><i></i><i></i></div></div>',
    unsafe_allow_html=True,
)

TIPS = ["🧴 Patch-test new skincare on your wrist first", "🍜 Check sodium per serving, not per pack", "☀️ Sunscreen every morning, even on cloudy days",
        "🔴 Red alert means: look closer before you buy", "🥤 Sugar hides under many names: dextrose, syrup, sucrose", "🎨 Deeper skin tones: go slow with strong acids"]
st.markdown('<div class="ticker"><div class="track2">' + "".join(f"<span>{t}</span>" for t in TIPS * 2) + "</div></div>", unsafe_allow_html=True)

saved = database.load_profile()
with st.expander("👤 Your profile"):
    c1, c2, c3 = st.columns(3)
    tone = c1.selectbox("Skin tone", SKIN_TONES, index=SKIN_TONES.index(saved.get("skin_tone", "Medium / wheatish")))
    concern = c2.selectbox("Skin concern", CONCERNS, index=CONCERNS.index(saved.get("concern", CONCERNS[0])))
    goal = c3.selectbox("Food goal", FOOD_GOALS, index=FOOD_GOALS.index(saved.get("food_goal", "None")))
    kids = st.toggle("👶 Kids mode (stricter alerts for children)", value=bool(saved.get("kids_mode", False)))
    profile = Profile(tone, concern, goal, kids)
    if st.button("💾 Save profile"):
        database.save_profile(profile.to_dict())
        st.toast("Profile saved ✅")

tabs = st.tabs(["📷 Scan", "🥗 Nutrition", "⚖️ Compare", "🔎 Search", "🎨 Skin tone", "🕘 History"])

# ---------- Scan ----------
with tabs[0]:
    st.caption("No label handy? Tap a demo:")
    dcols = st.columns(len(DEMOS))
    for col, (name, (txt, cat)) in zip(dcols, DEMOS.items()):
        col.button(name, key=f"demo_{name}", on_click=load_demo, args=(txt, cat), use_container_width=True)

    cat_name = st.radio("Product type", [CAT_F, CAT_S], horizontal=True, key="cat")
    category = "f" if cat_name == CAT_F else "s"
    source = st.radio("Image source", ["📁 Upload image", "📸 Use camera"], horizontal=True)
    file = st.file_uploader("Drop a label photo here", type=["png", "jpg", "jpeg", "webp"]) if source.startswith("📁") else st.camera_input("Photo of the ingredient list")
    if file is not None:
        img = Image.open(file)
        st.image(img, caption="Your label", use_container_width=True)
        if st.button("🔍 Read label", type="primary"):
            try:
                with st.spinner("Reading text..."):
                    raw, conf = read_text(img)
                st.session_state.update(raw_text=raw, ocr_text=extract_ingredients(raw), ocr_conf=conf)
            except Exception as e:
                st.error(f"OCR failed: {e}. Check that Tesseract is installed (see README).")
    if "ocr_conf" in st.session_state:
        c = st.session_state["ocr_conf"]
        (st.warning if c < 60 else st.success)(f"OCR confidence {c:.0f}%." + (" Low: please verify the label manually." if c < 60 else ""))

    text = st.text_area("Ingredients (edit OCR mistakes, or paste text)", key="ocr_text", height=120)
    go = st.button("✨ Check ingredients", type="primary", use_container_width=True)
    if go or st.session_state.pop("run_check", False):
        if not text.strip():
            st.warning("Add an image or paste an ingredient list first.")
        else:
            hits, unknown = analyze(text, category, DB)
            if profile.kids_mode:
                hits = apply_kids(hits, category)
            infos = [unknown_explainer.explain(u, category) for u in unknown]
            sk = safety_verdict(hits, [i["skey"] for i in infos])
            st.session_state["res"] = dict(hits=hits, unknown=unknown, cat=category, sk=sk, kids=profile.kids_mode)
            st.session_state.pop("ai_unknown", None)
            database.save_scan(category, text, {"bad": "bad", "warn": "warn", "mid": "warn", "good": "good"}[sk[0]],
                               [h["name"] for h in hits if h["level"] in ("bad", "warn")])
            if sk[0] == "bad":
                st.toast("🚨 Danger ingredient found!")
            elif sk[0] == "good" and label_score(hits) >= 85:
                st.balloons()

    res = st.session_state.get("res")
    if res:
        hits, unknown, rcat = res["hits"], res["unknown"], res["cat"]
        key, emoji, title, sub = res["sk"]
        kids_txt = " · 👶 Kids mode" if res["kids"] else ""
        st.markdown(f'<div class="safe {key}"><div class="big">{emoji}</div><div><h2>{escape(title)}</h2><p>{escape(sub)}{kids_txt}</p></div></div>', unsafe_allow_html=True)
        result_card(hits)
        stats(hits, unknown)
        conf_level, conf_reason = ai_explainer.confidence(len(hits), len(unknown), st.session_state.get("ocr_conf"))
        en = ai_explainer.summarize(hits, unknown, key, rcat)
        st.write(en)
        st.caption(f"Confidence: **{conf_level}**. {conf_reason}")
        for n in personal_notes(hits, rcat, profile):
            tip("🎯 For you: " + n)
        for i, h in enumerate(hits):
            row(h, open_=h["level"] == "bad", idx=i)

        swaps = guides.swaps_for(hits)
        if swaps:
            st.subheader("💡 Healthier swaps")
            for name, text_ in swaps:
                tip(f"Instead of {name}: {text_}")

        if unknown:
            st.subheader("❓ Unknown ingredients, explained")
            st.caption("These are not in our database. Each one gets a guess of what it is, with a confidence level. It is a guide, not a safety ruling.")
            for i, u in enumerate(unknown):
                unknown_row(u, rcat, i)
            if ai_explainer.llm_available():
                if st.button("🤖 Ask AI to explain these in detail"):
                    with st.spinner("Asking the AI..."):
                        st.session_state["ai_unknown"] = ai_explainer.llm_explain_unknown(unknown, rcat)
                if "ai_unknown" in st.session_state:
                    st.markdown(st.session_state["ai_unknown"])
            else:
                st.caption("Optional: set ANTHROPIC_API_KEY (and pip install anthropic) for detailed AI explanations.")

        st.subheader("🗣️ தமிழ் summary")
        ta = ai_explainer.tamil_summary(hits, unknown, rcat, key)
        st.info(ta)
        speak_buttons(en, ta)
        st.download_button("📄 Download report", ai_explainer.build_report(hits, unknown, rcat, title, sub, swaps), file_name="labellens_report.txt")


# ---------- Nutrition ----------
with tabs[1]:
    st.write("Read the nutrition table from the image on the Scan tab, or paste it here.")
    if st.button("📥 Fill from last scan") and "raw_text" in st.session_state:
        st.session_state["nut_text"] = extract_nutrition_block(st.session_state["raw_text"])
    ntext = st.text_area("Nutrition table text", key="nut_text", height=140, placeholder="Energy 520 kcal\nProtein 7 g\nSugar 30 g\nSodium 480 mg")
    parsed = nutrition.parse_nutrition(ntext) if ntext.strip() else {"values": {}, "serving_g": None, "per100_hint": False}
    if ntext.strip() and not parsed["values"]:
        st.warning("No nutrient values found. Edit the text above.")
    if parsed["values"]:
        basis = st.radio("Values on the label are per", ["100 g", "1 serving"], horizontal=True, index=0 if parsed["per100_hint"] or not parsed["serving_g"] else 1)
        default_basis = 100.0 if basis == "100 g" else float(parsed["serving_g"] or 30.0)
        c1, c2 = st.columns(2)
        basis_amt = c1.number_input("That amount in grams", min_value=1.0, value=default_basis)
        eaten = c2.number_input("How much will you eat (grams)?", min_value=1.0, value=float(parsed["serving_g"] or 50.0))
        with st.expander("✏️ Fix any OCR mistakes"):
            key = str(hash(ntext))
            cols = st.columns(2)
            vals = {k: cols[i % 2].number_input(nutrition.NAMES[k], min_value=0.0, value=float(v), key=f"{k}_{key}") for i, (k, v) in enumerate(parsed["values"].items())}
        eaten_vals = nutrition.scale(vals, basis_amt, eaten)
        st.subheader(f"🍽️ For {eaten:.0f} g")
        bars(eaten_vals)
        for nutr, (band, v100) in nutrition.traffic_lights(vals, basis_amt).items():
            icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}[band]
            st.write(f"{icon} {nutrition.NAMES[nutr]}: {v100} per 100 g is **{band}**")
        for n in nutrition.excess_notes(eaten_vals):
            st.warning(n)
        st.caption("General adult guidance (2000 kcal diet). Not personal dietary advice.")

# ---------- Compare ----------
with tabs[2]:
    c_name = st.radio("Type", [CAT_F, CAT_S], horizontal=True, key="cmp_cat")
    ccat = "f" if c_name == CAT_F else "s"
    col1, col2 = st.columns(2)
    ta = col1.text_area("Product A ingredients", height=130)
    tb = col2.text_area("Product B ingredients", height=130)
    if st.button("⚔️ Compare products", type="primary", use_container_width=True) and ta.strip() and tb.strip():
        ha, _ = analyze(ta, ccat, DB)
        hb, _ = analyze(tb, ccat, DB)
        r = compare(ha, hb)
        sa, sb = label_score(ha), label_score(hb)
        win = r["fewer_concerns"]
        boxes = ""
        for name, s, w in (("A", sa, win == "A"), ("B", sb, win == "B")):
            title, color = grade(s)
            boxes += f'<div class="cmpbox {"win" if w else ""}"><b>{"👑 " if w else ""}Product {name}</b>{ring(s, color, 120)}<div style="color:{color};font-weight:800">{title}</div></div>'
        st.markdown(f'<div class="cmp">{boxes}</div>', unsafe_allow_html=True)
        st.caption("Based on recognised ingredients only; not a full safety verdict.")
        a, b = st.columns(2)
        a.markdown("**Only in A**")
        for h in r["only_a"]:
            a.write(f"{ {'bad': '🔴', 'warn': '🟠', 'good': '🟢', 'ok': '⚪'}[h['level']] } {h['name']}")
        b.markdown("**Only in B**")
        for h in r["only_b"]:
            b.write(f"{ {'bad': '🔴', 'warn': '🟠', 'good': '🟢', 'ok': '⚪'}[h['level']] } {h['name']}")
        st.markdown("**In both:** " + ("".join(f'<span class="chip">{escape(h["name"])}</span>' for h in r["common"]) or "none"), unsafe_allow_html=True)

# ---------- Search ----------
with tabs[3]:
    st.text_input("Search an ingredient or product type", key="q", placeholder="niacinamide, sunscreen, instant noodles...")
    scols = st.columns(4)
    for col, s in zip(scols, ["sunscreen", "niacinamide", "noodles", "fairness cream"]):
        col.button(s, key=f"sq_{s}", on_click=lambda v=s: st.session_state.update(q=v), use_container_width=True)
    q = st.session_state.get("q", "")
    if q:
        ql, found = q.lower(), False
        for name, (keys, pro, con, look) in guides.PRODUCTS.items():
            if ql in name.lower() or any(ql in k or k in ql for k in keys):
                found = True
                st.subheader(name)
                a, b = st.columns(2)
                a.success("**👍 Advantages**\n\n" + "\n".join(f"- {x}" for x in pro))
                b.error("**👎 Disadvantages**\n\n" + "\n".join(f"- {x}" for x in con))
                tip("🔖 What to look for on the label: " + look)
        for r in search(q, DB):
            found = True
            row(r, open_=True)
        if not found:
            st.info("No match in the starter database. Unknown is shown instead of guessing.")

# ---------- Skin tone ----------
with tabs[4]:
    c1, c2 = st.columns(2)
    t = c1.selectbox("Your skin tone", list(guides.TONES), index=SKIN_TONES.index(profile.skin_tone), key="k_tone")
    cc = c2.selectbox("Main concern", list(guides.CONCERNS), index=CONCERNS.index(profile.concern), key="k_con")
    st.markdown('<div class="sw">' + "".join(f'<div class="{"on" if n == t else ""}"><i style="background:{c}"></i>{n.split(" /")[0]}</div>' for n, c in SWATCH.items()) + "</div>", unsafe_allow_html=True)
    use, avoid = guides.CONCERNS[cc]
    tip("🌟 " + guides.TONES[t])
    a, b = st.columns(2)
    a.success("**✅ Look for**\n\n" + "\n".join(f"- {x}" for x in use))
    b.error("**🚫 Avoid**\n\n" + "\n".join(f"- {x}" for x in avoid))
    tip("☀️ Sunscreen tip for your tone: " + guides.SUNSCREEN_TIP[t])

# ---------- History ----------
with tabs[5]:
    rows = database.recent_scans()
    if rows:
        for ts, cat, res, flagged, ingr in rows:
            icon = {"bad": "🔴", "warn": "🟠", "good": "🟢"}.get(res, "⚪")
            st.markdown(f'<div class="hist">{icon} <b>{"🍜 Food" if cat == "f" else "🧴 Skin"}</b> · {escape(ts)}<br>'
                        f'<span style="color:#64748b">{escape(flagged) if flagged else "No flagged ingredients"}</span></div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear history"):
            database.clear_history()
            st.rerun()
    else:
        st.info("No scans yet. Check a label and it will appear here.")

st.divider()
"""LabelLens AI - Super UI edition.  Run with:  streamlit run app.py"""
import json
from html import escape

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

import ai_explainer
import database
import guides
import unknown_explainer
import nutrition
from ingredient_matcher import SAFE_LABEL, analyze, compare, load_db, safety_verdict, search
from ocr_engine import read_text
from personalization import CONCERNS, FOOD_GOALS, SKIN_TONES, Profile, apply_kids, personal_notes
from text_processor import extract_ingredients, extract_nutrition_block

st.set_page_config(page_title="LabelLens AI", page_icon="🔍", layout="centered")
database.init_db()

CSS = """
<style>
.block-container{padding-top:1rem;max-width:860px}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#f6f7fd !important;color:#1e1b4b !important}
[data-testid="stHeader"]{background:transparent !important}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label,.stApp li,.stApp summary,.stApp [data-testid="stWidgetLabel"] p{color:#1e1b4b !important}
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *{color:#64748b !important}
.stApp [data-baseweb="select"]>div,.stApp [data-baseweb="input"]>div,.stApp [data-baseweb="textarea"],.stApp textarea,.stApp input{background:#fff !important;color:#1e1b4b !important;border-color:#d9def0 !important;border-radius:12px !important}
.stApp [data-baseweb="select"] *{color:#1e1b4b !important}
[data-baseweb="popover"],[data-baseweb="popover"] ul,[data-baseweb="popover"] li,[data-baseweb="menu"]{background:#fff !important;color:#1e1b4b !important}
[data-testid="stFileUploaderDropzone"]{background:#fff !important;border:2px dashed #a5b4fc !important;border-radius:18px !important}
[data-testid="stFileUploaderDropzone"] *{color:#475569 !important}
[data-testid="stExpander"]{background:#fff !important;border:1px solid #e0e7ff !important;border-radius:16px !important}
.stApp .stButton>button{background:#fff !important;border:1.5px solid #c7d2fe !important;border-radius:12px !important;transition:.15s}
.stApp .stButton>button:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(79,70,229,.18)}
.stApp .stButton>button p{color:#4f46e5 !important;font-weight:700}
.stApp .stButton>button[kind="primary"],.stApp .stButton>button[data-testid="stBaseButton-primary"]{background:linear-gradient(90deg,#4f46e5,#9333ea) !important;border:0 !important}
.stApp .stButton>button[kind="primary"] p,.stApp .stButton>button[data-testid="stBaseButton-primary"] p{color:#fff !important}
.stApp [role="tablist"]{gap:6px !important;background:#e9ebfb !important;padding:6px !important;border-radius:16px !important;border:0 !important;overflow-x:auto}
.stApp button[role="tab"]{border-radius:12px !important;padding:8px 14px !important;background:transparent !important;height:auto !important}
.stApp button[role="tab"] p{color:#64748b !important;font-weight:600}
.stApp button[role="tab"][aria-selected="true"]{background:#fff !important;box-shadow:0 2px 8px rgba(79,70,229,.25) !important}
.stApp button[role="tab"][aria-selected="true"] p{color:#4f46e5 !important;font-weight:800 !important}
.stApp [data-baseweb="tab-highlight"],.stApp [data-baseweb="tab-border"]{display:none !important}

.hero{display:flex;align-items:center;justify-content:space-between;gap:16px;background:linear-gradient(120deg,#4f46e5,#9333ea,#ec4899,#f59e0b,#4f46e5);background-size:300% 300%;animation:grad 9s ease infinite;position:relative;border-radius:26px;padding:26px 28px;margin-bottom:16px;box-shadow:0 14px 34px rgba(79,70,229,.35);overflow:hidden}
.stApp .hero h1{margin:0;font-size:38px;font-weight:900;letter-spacing:-1px;color:#fff !important}
.stApp .hero h1 span{color:#fde68a !important}
.stApp .hero p{margin:6px 0 12px;font-size:16px;color:#f5f3ff !important}
.badges span{display:inline-block;background:rgba(255,255,255,.2);color:#fff;border-radius:99px;padding:4px 12px;margin:3px 4px 0 0;font-size:13px;font-weight:600}
.phone{position:relative;flex:none;width:112px;height:150px;background:#fff;border-radius:18px;padding:16px 12px;box-shadow:0 8px 20px rgba(0,0,0,.25);transform:rotate(6deg);animation:float 3s ease-in-out infinite}
.phone i{display:block;height:8px;border-radius:4px;background:#e0e7ff;margin-bottom:9px}
.phone i:nth-child(2){width:70%}.phone i:nth-child(4){width:85%;background:#fecdd3}.phone i:nth-child(6){width:55%}
.scan{position:absolute;left:6px;right:6px;height:3px;border-radius:3px;background:#22c55e;box-shadow:0 0 12px #22c55e;animation:scan 2s ease-in-out infinite}
@keyframes scan{0%{top:14px}50%{top:128px}100%{top:14px}}
@keyframes float{0%,100%{transform:rotate(6deg) translateY(0)}50%{transform:rotate(6deg) translateY(-8px)}}
@media(max-width:560px){.phone{display:none}.stApp .hero h1{font-size:30px}}

.result{display:flex;align-items:center;gap:20px;background:#fff;border-radius:22px;padding:18px 22px;margin:10px 0;box-shadow:0 8px 24px rgba(30,27,75,.08);border:1px solid #eceffa}
.ringfill{animation:ring 1.2s ease-out}
@keyframes ring{from{stroke-dashoffset:339.3}}
.result h2{margin:0;font-size:24px;font-weight:900}.result .sub{margin:4px 0 0;color:#475569;font-size:14px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0}
.stat{background:#fff;border-radius:16px;padding:12px 6px;text-align:center;border:1px solid #eceffa;box-shadow:0 4px 12px rgba(30,27,75,.05)}
.stat b{display:block;font-size:28px;font-weight:900;line-height:1.1}.stat span{font-size:12px;color:#64748b}
.stat.bad b{color:#e11d48}.stat.warn b{color:#f59e0b}.stat.good b{color:#10b981}.stat.unk b{color:#64748b}
@media(max-width:560px){.stats{grid-template-columns:repeat(2,1fr)}.result{flex-direction:column;text-align:center}}

details.row{background:#fff;border:1px solid #eceffa;border-left:6px solid #94a3b8;border-radius:16px;margin:9px 0;padding:0 16px;box-shadow:0 4px 12px rgba(30,27,75,.05)}
details.row.good{border-left-color:#10b981}details.row.warn{border-left-color:#f59e0b}details.row.bad{border-left-color:#e11d48;animation:shake .5s}
@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-6px)}40%{transform:translateX(6px)}60%{transform:translateX(-4px)}80%{transform:translateX(4px)}}
details.row summary{cursor:pointer;padding:13px 0;font-weight:800;list-style:none;display:flex;align-items:center;gap:10px}
details.row summary::-webkit-details-marker{display:none}
.pill{margin-left:auto;font-size:12px;font-weight:800;padding:4px 11px;border-radius:99px}
.p-good{background:#d1fae5;color:#047857}.p-warn{background:#fef3c7;color:#92400e}.p-bad{background:#ffe4e6;color:#be123c}.p-ok{background:#eef2f6;color:#64748b}
.stApp .body{padding:0 0 14px 4px;font-size:14px}.stApp .body p{margin:5px 0;color:#334155 !important}
.stApp .body p.adv{color:#047857 !important}.stApp .body p.dis{color:#be123c !important}

.banner{border-radius:16px;padding:14px 18px;font-weight:800;margin:8px 0}
.stApp .banner.bad{background:#ffe4e6;color:#be123c !important}.stApp .banner.warn{background:#fef3c7;color:#92400e !important}.stApp .banner.good{background:#d1fae5;color:#047857 !important}
.tip{background:#eef2ff;border-left:5px solid #6366f1;border-radius:14px;padding:11px 15px;margin:8px 0;font-size:14px;color:#1e1b4b}
.chip{display:inline-block;background:#eef2ff;color:#4338ca;border-radius:99px;padding:4px 13px;margin:3px;font-size:13px;font-weight:600}

.bar{margin:10px 0}.bar-top{display:flex;justify-content:space-between;font-size:14px;font-weight:700;margin-bottom:4px}
.track{height:12px;background:#e9ebfb;border-radius:8px;overflow:hidden}.fill{height:100%;border-radius:8px;transition:width 1s}
.sw{display:flex;gap:14px;justify-content:center;margin:8px 0 14px}
.sw div{text-align:center;font-size:12px;color:#64748b;width:72px}
.sw i{display:block;width:52px;height:52px;border-radius:50%;margin:0 auto 5px;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.2)}
.sw .on i{box-shadow:0 0 0 4px #6366f1}.sw .on{color:#4f46e5;font-weight:800}
.hist{background:#fff;border:1px solid #eceffa;border-radius:16px;padding:10px 16px;margin:8px 0;font-size:14px}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:12px}.cmpbox{background:#fff;border-radius:20px;padding:14px;text-align:center;border:2px solid #eceffa}
.cmpbox.win{border-color:#10b981;box-shadow:0 8px 22px rgba(16,185,129,.2)}

@property --n{syntax:"<integer>";inherits:false;initial-value:0}
.ringwrap{position:relative;flex:none}
.ringwrap .num{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:900;counter-reset:n var(--n);animation:cnt 1.3s ease-out forwards}
.ringwrap .num:before{content:counter(n)}
@keyframes cnt{from{--n:0}to{--n:var(--t)}}
@keyframes grad{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.hero:before,.hero:after{content:"";position:absolute;border-radius:50%;background:rgba(255,255,255,.14);animation:drift 7s ease-in-out infinite}
.hero:before{width:130px;height:130px;left:-30px;bottom:-50px}
.hero:after{width:90px;height:90px;right:150px;top:-30px;animation-delay:-3s}
.hero>*{position:relative;z-index:1}
@keyframes drift{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(18px,-16px) scale(1.15)}}
.badges span{animation:bob 3s ease-in-out infinite}.badges span:nth-child(2){animation-delay:.3s}.badges span:nth-child(3){animation-delay:.6s}.badges span:nth-child(4){animation-delay:.9s}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.ticker{overflow:hidden;white-space:nowrap;background:#fff;border-radius:99px;border:1px solid #e0e7ff;padding:8px 0;margin-bottom:14px}
.track2{display:inline-block;animation:marq 40s linear infinite}
.track2 span{display:inline-block;margin:0 28px;font-size:13px;font-weight:600;color:#4338ca}
@keyframes marq{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes slidein{from{opacity:0;transform:translateY(16px)}}
@keyframes pop{from{opacity:0;transform:scale(.88)}}
@keyframes glow{0%,100%{box-shadow:0 0 0 0 rgba(225,29,72,.4)}50%{box-shadow:0 0 0 10px rgba(225,29,72,0)}}
@keyframes grow{from{width:0}}
@keyframes btnpulse{0%,100%{box-shadow:0 0 0 0 rgba(147,51,234,.45)}50%{box-shadow:0 0 0 10px rgba(147,51,234,0)}}
details.row{animation:slidein .5s var(--d,0s) both}
details.row.bad{animation:slidein .5s var(--d,0s) both,shake .5s calc(var(--d,0s) + .55s),glow 2s calc(var(--d,0s) + 1.2s) infinite}
details.row.unk{border-left-color:#94a3b8}
.result{animation:pop .6s both}
.stat{animation:pop .5s both}.stat:nth-child(2){animation-delay:.1s}.stat:nth-child(3){animation-delay:.2s}.stat:nth-child(4){animation-delay:.3s}
.banner{animation:slidein .5s both}
.fill{animation:grow 1.2s ease-out}
.cmpbox{animation:pop .6s both}
.sw i{transition:transform .2s}.sw .on i{transform:scale(1.18)}
.stApp .stButton>button[kind="primary"],.stApp .stButton>button[data-testid="stBaseButton-primary"]{animation:btnpulse 2.4s infinite}

.p-ok{background:#d1fae5;color:#047857}.p-unk{background:#eef2f6;color:#64748b}
.safe{display:flex;align-items:center;gap:18px;border-radius:24px;padding:18px 24px;margin:10px 0;animation:pop .6s both;box-shadow:0 10px 26px rgba(30,27,75,.12)}
.safe .big{font-size:56px;line-height:1;animation:bounce 1.6s ease-in-out infinite}
.stApp .safe h2{margin:0;font-size:28px;font-weight:900;letter-spacing:.5px}
.stApp .safe p{margin:4px 0 0;font-size:14px}
.safe.good{background:#d1fae5}.stApp .safe.good h2,.stApp .safe.good p{color:#047857 !important}
.safe.mid{background:#ecfccb}.stApp .safe.mid h2,.stApp .safe.mid p{color:#4d7c0f !important}
.safe.warn{background:#fef3c7}.stApp .safe.warn h2,.stApp .safe.warn p{color:#92400e !important}
.safe.bad{background:#ffe4e6}.stApp .safe.bad h2,.stApp .safe.bad p{color:#be123c !important}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none !important;transition:none !important}.ringwrap .num{--n:var(--t)}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

LABEL = SAFE_LABEL
CAT_F, CAT_S = "🍜 Food", "🧴 Skincare / makeup / haircare"
SWATCH = {"Fair": "#f6dcc8", "Medium / wheatish": "#e0b48e", "Tan / brown": "#b27b52", "Deep / dark brown": "#6b4226"}
DEMOS = {
    "🍜 Noodles": ("Wheat flour, Palm oil, Salt, Sugar, Monosodium glutamate, Tartrazine (E102), Sodium benzoate, Disodium inosinate, Acidity regulator (E501), Spirulina extract, Spices", CAT_F),
    "🥤 Soft drink": ("Carbonated water, Sugar, High fructose corn syrup, Citric acid, Sodium benzoate, Aspartame, Flavour", CAT_F),
    "🧴 Face cream": ("Water, Glycerin, Niacinamide, Hyaluronic acid, Zinc oxide, Dimethicone, Fragrance, Methylparaben, Bakuchiol, Centella asiatica extract, Ceteareth-20", CAT_S),
    "⚠️ Fairness cream": ("Water, Hydroquinone, Mercury chloride, Glycerin, Fragrance", CAT_S),
}


@st.cache_data
def get_db():
    return load_db()


DB = get_db()


def label_score(hits):
    s = 100 + sum({"bad": -25, "warn": -8, "good": 3, "ok": 0}[h["level"]] for h in hits)
    return max(0, min(100, s))


def grade(s):
    if s >= 80:
        return "Great pick 🎉", "#10b981"
    if s >= 60:
        return "Okay, use with care 🙂", "#84cc16"
    if s >= 40:
        return "Be careful ⚠️", "#f59e0b"
    return "Better avoided 🚫", "#e11d48"


def ring(score, color, size=150):
    off = 339.3 * (1 - score / 100)
    return (f'<div class="ringwrap" style="width:{size}px;height:{size}px"><svg width="{size}" height="{size}" viewBox="0 0 150 150">'
            f'<circle cx="75" cy="75" r="54" fill="none" stroke="#e9ebfb" stroke-width="14"/>'
            f'<circle class="ringfill" cx="75" cy="75" r="54" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" '
            f'stroke-dasharray="339.3" stroke-dashoffset="{off:.1f}" transform="rotate(-90 75 75)"/></svg>'
            f'<div class="num" style="--t:{score};color:{color};font-size:{int(size * 0.27)}px"></div></div>')


def row(r, open_=False, idx=0):
    lvl = r["level"]
    st.markdown(
        f'<details class="row {lvl}" style="--d:{idx * 0.08:.2f}s" {"open" if open_ else ""}><summary>{escape(r["name"])}<span class="pill p-{lvl}">{LABEL[lvl]}</span></summary>'
        f'<div class="body"><p><b>What it is:</b> {escape(r["what"])}</p><p class="adv"><b>Advantage:</b> {escape(r["advantage"])}</p>'
        f'<p class="dis"><b>Disadvantage:</b> {escape(r["disadvantage"])}</p></div></details>',
        unsafe_allow_html=True,
    )


def unknown_row(u, cat, idx=0):
    info = unknown_explainer.explain(u, cat)
    pill = {"ok": "p-ok", "limit": "p-warn", "check": "p-unk"}[info["skey"]]
    icon = {"ok": "✅", "limit": "⚠️", "check": "❓"}[info["skey"]]
    st.markdown(
        f'<details class="row unk" style="--d:{idx * 0.08:.2f}s"><summary>{escape(u)}<span class="pill {pill}">{icon} {escape(info["safety"])}</span></summary>'
        f'<div class="body"><p><b>Looks like:</b> {escape(info["kind"])}</p><p><b>What it does:</b> {escape(info["text"])}</p>'
        f'<p><b>Confidence:</b> {escape(info["conf"])} (pattern-based guess, not from our database)</p>'
        f'<p><b>What to do:</b> {escape(info["advice"])}</p></div></details>',
        unsafe_allow_html=True,
    )


def speak_buttons(en, ta):
    """Read-aloud buttons. Texts are passed as JS variables (not inside HTML attributes) so quotes cannot break them."""
    safe = lambda t: json.dumps(t).replace("</", "<\\/")
    html = r"""
<div style="display:flex;gap:10px;flex-wrap:wrap;font-family:sans-serif">
<button id="en" style="padding:10px 16px;border:0;border-radius:12px;color:#fff;font-weight:700;background:linear-gradient(90deg,#4f46e5,#9333ea);cursor:pointer">🔊 Read in English</button>
<button id="ta" style="padding:10px 16px;border:0;border-radius:12px;color:#fff;font-weight:700;background:linear-gradient(90deg,#ec4899,#f59e0b);cursor:pointer">🔊 தமிழில் கேளுங்கள்</button>
<button id="stop" style="padding:10px 16px;border:1px solid #c7d2fe;border-radius:12px;color:#4f46e5;font-weight:700;background:#fff;cursor:pointer">⏹ Stop</button>
</div>
<div id="msg" style="font:13px sans-serif;color:#64748b;margin-top:8px;min-height:18px"></div>
<script>
const EN = %%EN%%, TA = %%TA%%;
const msg = document.getElementById('msg');
function getVoices(){return new Promise(function(res){
  var v = speechSynthesis.getVoices(); if (v.length) return res(v);
  speechSynthesis.onvoiceschanged = function(){res(speechSynthesis.getVoices());};
  setTimeout(function(){res(speechSynthesis.getVoices());}, 1500);});}
async function say(text, lang, label){
  if (!('speechSynthesis' in window)) { msg.textContent = 'This browser cannot read aloud. Try Chrome or Edge.'; return; }
  var vs = await getVoices(), base = lang.split('-')[0];
  var v = vs.find(function(x){return x.lang.replace('_','-').toLowerCase() === lang.toLowerCase();}) ||
          vs.find(function(x){return x.lang.toLowerCase().indexOf(base) === 0;});
  if (!v && base === 'ta') { msg.textContent = 'No Tamil voice found on this device. Try Microsoft Edge (it has online Tamil voices), or add Tamil speech in Windows Settings > Time & language > Speech.'; return; }
  speechSynthesis.cancel();
  var parts = text.split(/(?<=[.!?\u0964])\s+/).filter(Boolean);
  parts.forEach(function(p, i){
    var u = new SpeechSynthesisUtterance(p);
    if (v) { u.voice = v; u.lang = v.lang; } else { u.lang = lang; }
    if (i === 0) u.onstart = function(){msg.textContent = 'Reading ' + label + '...';};
    if (i === parts.length - 1) u.onend = function(){msg.textContent = '';};
    u.onerror = function(e){msg.textContent = 'Could not play audio (' + e.error + '). Check the tab is not muted.';};
    speechSynthesis.speak(u);
  });
}
document.getElementById('en').addEventListener('click', function(){say(EN, 'en-IN', 'English');});
document.getElementById('ta').addEventListener('click', function(){say(TA, 'ta-IN', 'Tamil');});
document.getElementById('stop').addEventListener('click', function(){speechSynthesis.cancel(); msg.textContent = '';});
</script>
"""
    components.html(html.replace("%%EN%%", safe(en)).replace("%%TA%%", safe(ta)), height=110)


def banner(level, msg):
    st.markdown(f'<div class="banner {level}">{escape(msg)}</div>', unsafe_allow_html=True)


def tip(msg):
    st.markdown(f'<div class="tip">{escape(msg)}</div>', unsafe_allow_html=True)


def stats(hits, unknown):
    n = lambda l: sum(h["level"] == l for h in hits)
    st.markdown(
        f'<div class="stats"><div class="stat bad"><b>{n("bad")}</b><span>🚨 Alerts</span></div><div class="stat warn"><b>{n("warn")}</b><span>⚠️ Care</span></div>'
        f'<div class="stat good"><b>{n("good")}</b><span>✅ Beneficial</span></div><div class="stat unk"><b>{len(unknown)}</b><span>❓ Unknown</span></div></div>',
        unsafe_allow_html=True,
    )


def result_card(hits):
    s = label_score(hits)
    title, color = grade(s)
    st.markdown(
        f'<div class="result">{ring(s, color)}<div><h2 style="color:{color} !important">{title}</h2>'
        f'<p class="sub">LabelScore out of 100, based on the ingredients we recognise. Amounts are not on labels, so treat it as a guide.</p></div></div>',
        unsafe_allow_html=True,
    )
    return s


def bars(eaten_vals):
    good_high = {"protein", "fibre"}
    html = ""
    for k, v in eaten_vals.items():
        if k not in nutrition.DAILY:
            continue
        pct = v / nutrition.DAILY[k] * 100
        color = "#6366f1" if k in good_high else ("#10b981" if pct < 30 else "#f59e0b" if pct < 60 else "#e11d48")
        html += (f'<div class="bar"><div class="bar-top"><span>{nutrition.NAMES[k]}</span><span>{v:.1f} · {pct:.0f}% of day</span></div>'
                 f'<div class="track"><div class="fill" style="width:{min(pct, 100):.0f}%;background:{color}"></div></div></div>')
    st.markdown(html, unsafe_allow_html=True)


def load_demo(text, cat):
    st.session_state["ocr_text"] = text
    st.session_state["cat"] = cat
    st.session_state["run_check"] = True


# ---------- hero ----------
st.markdown(
    '<div class="hero"><div><h1>Label<span>Lens</span> AI</h1><p>Point. Scan. Know what is inside.</p>'
    '<div class="badges"><span>🍜 Food</span><span>🧴 Skincare</span><span>🎨 Skin-tone smart</span><span>🚨 Danger alerts</span></div></div>'
    '<div class="phone"><div class="scan"></div><i></i><i></i><i></i><i></i><i></i><i></i></div></div>',
    unsafe_allow_html=True,
)

TIPS = ["🧴 Patch-test new skincare on your wrist first", "🍜 Check sodium per serving, not per pack", "☀️ Sunscreen every morning, even on cloudy days",
        "🔴 Red alert means: look closer before you buy", "🥤 Sugar hides under many names: dextrose, syrup, sucrose", "🎨 Deeper skin tones: go slow with strong acids"]
st.markdown('<div class="ticker"><div class="track2">' + "".join(f"<span>{t}</span>" for t in TIPS * 2) + "</div></div>", unsafe_allow_html=True)

saved = database.load_profile()
with st.expander("👤 Your profile"):
    c1, c2, c3 = st.columns(3)
    tone = c1.selectbox("Skin tone", SKIN_TONES, index=SKIN_TONES.index(saved.get("skin_tone", "Medium / wheatish")))
    concern = c2.selectbox("Skin concern", CONCERNS, index=CONCERNS.index(saved.get("concern", CONCERNS[0])))
    goal = c3.selectbox("Food goal", FOOD_GOALS, index=FOOD_GOALS.index(saved.get("food_goal", "None")))
    kids = st.toggle("👶 Kids mode (stricter alerts for children)", value=bool(saved.get("kids_mode", False)))
    profile = Profile(tone, concern, goal, kids)
    if st.button("💾 Save profile"):
        database.save_profile(profile.to_dict())
        st.toast("Profile saved ✅")

tabs = st.tabs(["📷 Scan", "🥗 Nutrition", "⚖️ Compare", "🔎 Search", "🎨 Skin tone", "🕘 History"])

# ---------- Scan ----------
with tabs[0]:
    st.caption("No label handy? Tap a demo:")
    dcols = st.columns(len(DEMOS))
    for col, (name, (txt, cat)) in zip(dcols, DEMOS.items()):
        col.button(name, key=f"demo_{name}", on_click=load_demo, args=(txt, cat), use_container_width=True)

    cat_name = st.radio("Product type", [CAT_F, CAT_S], horizontal=True, key="cat")
    category = "f" if cat_name == CAT_F else "s"
    source = st.radio("Image source", ["📁 Upload image", "📸 Use camera"], horizontal=True)
    file = st.file_uploader("Drop a label photo here", type=["png", "jpg", "jpeg", "webp"]) if source.startswith("📁") else st.camera_input("Photo of the ingredient list")
    if file is not None:
        img = Image.open(file)
        st.image(img, caption="Your label", use_container_width=True)
        if st.button("🔍 Read label", type="primary"):
            try:
                with st.spinner("Reading text..."):
                    raw, conf = read_text(img)
                st.session_state.update(raw_text=raw, ocr_text=extract_ingredients(raw), ocr_conf=conf)
            except Exception as e:
                st.error(f"OCR failed: {e}. Check that Tesseract is installed (see README).")
    if "ocr_conf" in st.session_state:
        c = st.session_state["ocr_conf"]
        (st.warning if c < 60 else st.success)(f"OCR confidence {c:.0f}%." + (" Low: please verify the label manually." if c < 60 else ""))

    text = st.text_area("Ingredients (edit OCR mistakes, or paste text)", key="ocr_text", height=120)
    go = st.button("✨ Check ingredients", type="primary", use_container_width=True)
    if go or st.session_state.pop("run_check", False):
        if not text.strip():
            st.warning("Add an image or paste an ingredient list first.")
        else:
            hits, unknown = analyze(text, category, DB)
            if profile.kids_mode:
                hits = apply_kids(hits, category)
            infos = [unknown_explainer.explain(u, category) for u in unknown]
            sk = safety_verdict(hits, [i["skey"] for i in infos])
            st.session_state["res"] = dict(hits=hits, unknown=unknown, cat=category, sk=sk, kids=profile.kids_mode)
            st.session_state.pop("ai_unknown", None)
            database.save_scan(category, text, {"bad": "bad", "warn": "warn", "mid": "warn", "good": "good"}[sk[0]],
                               [h["name"] for h in hits if h["level"] in ("bad", "warn")])
            if sk[0] == "bad":
                st.toast("🚨 Danger ingredient found!")
            elif sk[0] == "good" and label_score(hits) >= 85:
                st.balloons()

    res = st.session_state.get("res")
    if res:
        hits, unknown, rcat = res["hits"], res["unknown"], res["cat"]
        key, emoji, title, sub = res["sk"]
        kids_txt = " · 👶 Kids mode" if res["kids"] else ""
        st.markdown(f'<div class="safe {key}"><div class="big">{emoji}</div><div><h2>{escape(title)}</h2><p>{escape(sub)}{kids_txt}</p></div></div>', unsafe_allow_html=True)
        result_card(hits)
        stats(hits, unknown)
        conf_level, conf_reason = ai_explainer.confidence(len(hits), len(unknown), st.session_state.get("ocr_conf"))
        en = ai_explainer.summarize(hits, unknown, key, rcat)
        st.write(en)
        st.caption(f"Confidence: **{conf_level}**. {conf_reason}")
        for n in personal_notes(hits, rcat, profile):
            tip("🎯 For you: " + n)
        for i, h in enumerate(hits):
            row(h, open_=h["level"] == "bad", idx=i)

        swaps = guides.swaps_for(hits)
        if swaps:
            st.subheader("💡 Healthier swaps")
            for name, text_ in swaps:
                tip(f"Instead of {name}: {text_}")

        if unknown:
            st.subheader("❓ Unknown ingredients, explained")
            st.caption("These are not in our database. Each one gets a guess of what it is, with a confidence level. It is a guide, not a safety ruling.")
            for i, u in enumerate(unknown):
                unknown_row(u, rcat, i)
            if ai_explainer.llm_available():
                if st.button("🤖 Ask AI to explain these in detail"):
                    with st.spinner("Asking the AI..."):
                        st.session_state["ai_unknown"] = ai_explainer.llm_explain_unknown(unknown, rcat)
                if "ai_unknown" in st.session_state:
                    st.markdown(st.session_state["ai_unknown"])
            else:
                st.caption("Optional: set ANTHROPIC_API_KEY (and pip install anthropic) for detailed AI explanations.")

        st.subheader("🗣️ தமிழ் summary")
        ta = ai_explainer.tamil_summary(hits, unknown, rcat, key)
        st.info(ta)
        speak_buttons(en, ta)
        st.download_button("📄 Download report", ai_explainer.build_report(hits, unknown, rcat, title, sub, swaps), file_name="labellens_report.txt")


# ---------- Nutrition ----------
with tabs[1]:
    st.write("Read the nutrition table from the image on the Scan tab, or paste it here.")
    if st.button("📥 Fill from last scan") and "raw_text" in st.session_state:
        st.session_state["nut_text"] = extract_nutrition_block(st.session_state["raw_text"])
    ntext = st.text_area("Nutrition table text", key="nut_text", height=140, placeholder="Energy 520 kcal\nProtein 7 g\nSugar 30 g\nSodium 480 mg")
    parsed = nutrition.parse_nutrition(ntext) if ntext.strip() else {"values": {}, "serving_g": None, "per100_hint": False}
    if ntext.strip() and not parsed["values"]:
        st.warning("No nutrient values found. Edit the text above.")
    if parsed["values"]:
        basis = st.radio("Values on the label are per", ["100 g", "1 serving"], horizontal=True, index=0 if parsed["per100_hint"] or not parsed["serving_g"] else 1)
        default_basis = 100.0 if basis == "100 g" else float(parsed["serving_g"] or 30.0)
        c1, c2 = st.columns(2)
        basis_amt = c1.number_input("That amount in grams", min_value=1.0, value=default_basis)
        eaten = c2.number_input("How much will you eat (grams)?", min_value=1.0, value=float(parsed["serving_g"] or 50.0))
        with st.expander("✏️ Fix any OCR mistakes"):
            key = str(hash(ntext))
            cols = st.columns(2)
            vals = {k: cols[i % 2].number_input(nutrition.NAMES[k], min_value=0.0, value=float(v), key=f"{k}_{key}") for i, (k, v) in enumerate(parsed["values"].items())}
        eaten_vals = nutrition.scale(vals, basis_amt, eaten)
        st.subheader(f"🍽️ For {eaten:.0f} g")
        bars(eaten_vals)
        for nutr, (band, v100) in nutrition.traffic_lights(vals, basis_amt).items():
            icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}[band]
            st.write(f"{icon} {nutrition.NAMES[nutr]}: {v100} per 100 g is **{band}**")
        for n in nutrition.excess_notes(eaten_vals):
            st.warning(n)
        st.caption("General adult guidance (2000 kcal diet). Not personal dietary advice.")

# ---------- Compare ----------
with tabs[2]:
    c_name = st.radio("Type", [CAT_F, CAT_S], horizontal=True, key="cmp_cat")
    ccat = "f" if c_name == CAT_F else "s"
    col1, col2 = st.columns(2)
    ta = col1.text_area("Product A ingredients", height=130)
    tb = col2.text_area("Product B ingredients", height=130)
    if st.button("⚔️ Compare products", type="primary", use_container_width=True) and ta.strip() and tb.strip():
        ha, _ = analyze(ta, ccat, DB)
        hb, _ = analyze(tb, ccat, DB)
        r = compare(ha, hb)
        sa, sb = label_score(ha), label_score(hb)
        win = r["fewer_concerns"]
        boxes = ""
        for name, s, w in (("A", sa, win == "A"), ("B", sb, win == "B")):
            title, color = grade(s)
            boxes += f'<div class="cmpbox {"win" if w else ""}"><b>{"👑 " if w else ""}Product {name}</b>{ring(s, color, 120)}<div style="color:{color};font-weight:800">{title}</div></div>'
        st.markdown(f'<div class="cmp">{boxes}</div>', unsafe_allow_html=True)
        st.caption("Based on recognised ingredients only; not a full safety verdict.")
        a, b = st.columns(2)
        a.markdown("**Only in A**")
        for h in r["only_a"]:
            a.write(f"{ {'bad': '🔴', 'warn': '🟠', 'good': '🟢', 'ok': '⚪'}[h['level']] } {h['name']}")
        b.markdown("**Only in B**")
        for h in r["only_b"]:
            b.write(f"{ {'bad': '🔴', 'warn': '🟠', 'good': '🟢', 'ok': '⚪'}[h['level']] } {h['name']}")
        st.markdown("**In both:** " + ("".join(f'<span class="chip">{escape(h["name"])}</span>' for h in r["common"]) or "none"), unsafe_allow_html=True)

# ---------- Search ----------
with tabs[3]:
    st.text_input("Search an ingredient or product type", key="q", placeholder="niacinamide, sunscreen, instant noodles...")
    scols = st.columns(4)
    for col, s in zip(scols, ["sunscreen", "niacinamide", "noodles", "fairness cream"]):
        col.button(s, key=f"sq_{s}", on_click=lambda v=s: st.session_state.update(q=v), use_container_width=True)
    q = st.session_state.get("q", "")
    if q:
        ql, found = q.lower(), False
        for name, (keys, pro, con, look) in guides.PRODUCTS.items():
            if ql in name.lower() or any(ql in k or k in ql for k in keys):
                found = True
                st.subheader(name)
                a, b = st.columns(2)
                a.success("**👍 Advantages**\n\n" + "\n".join(f"- {x}" for x in pro))
                b.error("**👎 Disadvantages**\n\n" + "\n".join(f"- {x}" for x in con))
                tip("🔖 What to look for on the label: " + look)
        for r in search(q, DB):
            found = True
            row(r, open_=True)
        if not found:
            st.info("No match in the starter database. Unknown is shown instead of guessing.")

# ---------- Skin tone ----------
with tabs[4]:
    c1, c2 = st.columns(2)
    t = c1.selectbox("Your skin tone", list(guides.TONES), index=SKIN_TONES.index(profile.skin_tone), key="k_tone")
    cc = c2.selectbox("Main concern", list(guides.CONCERNS), index=CONCERNS.index(profile.concern), key="k_con")
    st.markdown('<div class="sw">' + "".join(f'<div class="{"on" if n == t else ""}"><i style="background:{c}"></i>{n.split(" /")[0]}</div>' for n, c in SWATCH.items()) + "</div>", unsafe_allow_html=True)
    use, avoid = guides.CONCERNS[cc]
    tip("🌟 " + guides.TONES[t])
    a, b = st.columns(2)
    a.success("**✅ Look for**\n\n" + "\n".join(f"- {x}" for x in use))
    b.error("**🚫 Avoid**\n\n" + "\n".join(f"- {x}" for x in avoid))
    tip("☀️ Sunscreen tip for your tone: " + guides.SUNSCREEN_TIP[t])

# ---------- History ----------
with tabs[5]:
    rows = database.recent_scans()
    if rows:
        for ts, cat, res, flagged, ingr in rows:
            icon = {"bad": "🔴", "warn": "🟠", "good": "🟢"}.get(res, "⚪")
            st.markdown(f'<div class="hist">{icon} <b>{"🍜 Food" if cat == "f" else "🧴 Skin"}</b> · {escape(ts)}<br>'
                        f'<span style="color:#64748b">{escape(flagged) if flagged else "No flagged ingredients"}</span></div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear history"):
            database.clear_history()
            st.rerun()
    else:
        st.info("No scans yet. Check a label and it will appear here.")

st.divider()
