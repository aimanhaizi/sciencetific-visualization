import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import aq_core as core
from aq_text import OBJECTIVES, VIZ_TITLES, INTERP, DATASET

st.set_page_config(page_title="Air Quality Visualisation", page_icon="🌫️", layout="wide")

HERE = os.path.dirname(os.path.abspath(__file__))
SEASON_COL = {"Winter": "#3b6fb6", "Spring": "#4c9f70", "Summer": "#e0a030", "Autumn": "#c0562d"}
PAGES = ["Page 1 · Temporal patterns", "Page 2 · Weather drivers", "Page 3 · Station comparison"]

st.markdown("""
<style>
.kpi{border:1px solid rgba(128,128,128,.35);border-left:6px solid #c0562d;border-radius:8px;padding:10px 14px;height:100%}
.kpi .l{font-size:.72rem;letter-spacing:.04em;text-transform:uppercase;opacity:.7}
.kpi .v{font-size:1.65rem;font-weight:700;line-height:1.25}
.kpi .s{font-size:.8rem;opacity:.8}
.obj{border-radius:8px;padding:12px 16px;background:rgba(192,86,45,.10);border:1px solid rgba(192,86,45,.35)}
.interp{border-left:4px solid rgba(128,128,128,.5);padding:2px 12px;margin:4px 0 14px 0}
</style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading data…")
def get_data():
    return core.load(os.path.join(HERE, "data", "air_quality_clean.csv.gz"))


def show(fig):
    """st.plotly_chart across Streamlit versions"""
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def kpis(items):
    cols = st.columns(len(items))
    for col, (label, value, sub) in zip(cols, items):
        col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div>'
                     f'<div class="s">{sub}</div></div>', unsafe_allow_html=True)


def base(fig, h=420, **kw):
    fig.update_layout(template="plotly_white", height=h, margin=dict(l=10, r=10, t=50, b=10), **kw)
    return fig


def fmt_month(ts):
    return pd.Timestamp(ts).strftime("%b %Y")


def interp(page, i):
    st.markdown(f'<div class="interp">{INTERP[page][i]}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ sidebar
data = get_data()
st.sidebar.title("🌫️ Air Quality Explorer")
page = st.sidebar.radio("Navigate", PAGES)
pollutant = st.sidebar.radio("Pollutant", ["PM2.5", "PM10"], horizontal=True)
all_st = sorted(data["station"].unique())
stations = st.sidebar.multiselect("Stations", all_st, default=all_st)
dmin, dmax = data["date"].min().date(), data["date"].max().date()
rng = st.sidebar.date_input("Date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)
st.sidebar.caption("Hourly data from 21 stations, May 2024 – Dec 2025. The written interpretations "
                   "describe PM2.5 with all stations and the full period.")

if isinstance(rng, (tuple, list)) and len(rng) == 2:
    d0, d1 = rng
else:
    d0 = d1 = rng[0] if isinstance(rng, (tuple, list)) else rng
df = data[data["station"].isin(stations) & (data["date"] >= pd.Timestamp(d0)) & (data["date"] <= pd.Timestamp(d1))]
if df.empty or df[core.pol(df, pollutant)].notna().sum() < 100:
    st.warning("Not enough data for this selection – choose more stations or a wider date range.")
    st.stop()

c = core.pol(df, pollutant)
G = core.GUIDE[pollutant]
title, objective = OBJECTIVES[PAGES.index(page) + 1]
st.title(title)
st.markdown(f'<div class="obj"><b>Objective.</b> {objective}</div>', unsafe_allow_html=True)
st.write("")
st.subheader("Summary box")

# ================================================================== PAGE 1
if page == PAGES[0]:
    s = core.obj1_summary(df, pollutant)
    kpis([
        (f"Mean {pollutant}", f"{s['mean']:.1f} µg/m³", f"WHO annual guideline {G['year']:g}"),
        ("Days above WHO 24-h limit", f"{s['exceed_days']:.0f}%", f"limit {G['day']:g} µg/m³ · {s['n_days']} days"),
        ("Worst month", fmt_month(s["peak_month"]), f"{s['peak_month_val']:.1f} µg/m³ (best: {fmt_month(s['low_month'])} {s['low_month_val']:.1f})"),
        ("Winter ÷ summer", f"{s['ratio']:.1f}×" if np.isfinite(s["ratio"]) else "n/a", f"{s['winter']:.1f} vs {s['summer']:.1f} µg/m³"),
        ("Daily peak hour", f"{s['peak_hour']:02d}:00", f"{s['peak_hour_val']:.1f} µg/m³ (lowest {s['low_hour']:02d}:00, {s['low_hour_val']:.1f})"),
    ])
    st.write("")

    st.subheader(VIZ_TITLES[1][0])
    d = core.daily_mean(df, pollutant)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d["date"], y=d["value"], mode="lines", name="Daily mean",
                             line=dict(color="#c0562d", width=1), opacity=0.55))
    fig.add_trace(go.Scatter(x=d["date"], y=d["rolling7"], mode="lines", name="7-day rolling mean",
                             line=dict(color="#222222", width=2.2)))
    fig.add_hline(y=G["day"], line_dash="dash", line_color="red",
                  annotation_text=f"WHO 24-h guideline ({G['day']:g} µg/m³)", annotation_position="top left")
    base(fig, 400, yaxis_title=f"{pollutant} (µg/m³)", xaxis_title="Date", hovermode="x unified",
         legend=dict(orientation="h", y=1.12))
    show(fig)
    interp(1, 0)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(VIZ_TITLES[1][1])
        m = core.hour_month_matrix(df, pollutant)
        fig = go.Figure(go.Heatmap(z=m.values, x=[fmt_month(x) for x in m.columns], y=m.index,
                                   colorscale="YlOrRd", colorbar=dict(title="µg/m³"),
                                   hovertemplate="%{x}<br>%{y}:00<br>%{z:.1f} µg/m³<extra></extra>"))
        base(fig, 440, xaxis_title="Month", yaxis_title="Hour of day")
        fig.update_xaxes(tickangle=-60)
        show(fig)
        interp(1, 1)
    with c2:
        st.subheader(VIZ_TITLES[1][2])
        dd = core.diurnal_by_season(df, pollutant)
        fig = go.Figure()
        for sea in core.SEASONS:
            x = dd[dd["season"] == sea]
            if len(x):
                fig.add_trace(go.Scatter(x=x["hour"], y=x["value"], mode="lines+markers", name=sea,
                                         line=dict(color=SEASON_COL[sea], width=2.5), marker=dict(size=5)))
        base(fig, 440, xaxis_title="Hour of day", yaxis_title=f"Mean {pollutant} (µg/m³)",
             legend=dict(orientation="h", y=1.12))
        fig.update_xaxes(dtick=3)
        show(fig)
        interp(1, 2)

# ================================================================== PAGE 2
elif page == PAGES[1]:
    s = core.obj2_summary(df, pollutant)
    kpis([
        ("r with temperature", f"{s['r_temp']:+.2f}", "colder → more pollution"),
        ("r with pressure", f"{s['r_press']:+.2f}", "high pressure → stagnation"),
        ("r with wind speed", f"{s['r_wind']:+.2f}", f"calm {s['calm']:.1f} vs windy {s['windy']:.1f} µg/m³"),
        ("Cold vs warm", f"{s['cold']:.1f} vs {s['warm']:.1f}", "µg/m³ below 5 °C vs above 20 °C"),
        ("PM2.5 / PM10 mass", f"{s['ratio25_10']*100:.0f}%", "share of fine particles"),
    ])
    st.write("")

    st.subheader(VIZ_TITLES[2][0])
    cm = core.corr_matrix(df)
    fig = go.Figure(go.Heatmap(z=cm.values, x=list(cm.columns), y=list(cm.index), zmin=-1, zmax=1,
                               colorscale="RdBu_r", text=np.round(cm.values, 2), texttemplate="%{text}",
                               colorbar=dict(title="r")))
    base(fig, 450)
    fig.update_yaxes(autorange="reversed")
    show(fig)
    interp(2, 0)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(VIZ_TITLES[2][1])
        smp = core.scatter_sample(df, pollutant)
        fig = go.Figure()
        for sea in core.SEASONS:
            x = smp[smp["season"] == sea]
            if len(x):
                fig.add_trace(go.Scattergl(x=x["temperature"], y=x[c], mode="markers", name=sea,
                                           marker=dict(size=4, opacity=0.3, color=SEASON_COL[sea])))
        b = core.binned_mean(df, "temperature", c, list(range(-16, 42, 2)))
        fig.add_trace(go.Scatter(x=b["x"], y=b["mean"], mode="lines+markers", name="Binned mean (2 °C)",
                                 line=dict(color="black", width=3)))
        base(fig, 460, xaxis_title="Temperature (°C)", yaxis_title=f"{pollutant} (µg/m³)",
             legend=dict(orientation="h", y=1.15))
        fig.update_yaxes(range=[0, float(smp[c].quantile(0.995))])
        show(fig)
        st.caption("20,000 random hourly records are plotted; the black line uses all records.")
        interp(2, 1)
    with c2:
        st.subheader(VIZ_TITLES[2][2])
        xs, ys, z = core.surface_grid(df, pollutant)
        fig = go.Figure(go.Surface(x=xs, y=ys, z=z, colorscale="YlOrRd", colorbar=dict(title="µg/m³")))
        base(fig, 460, scene=dict(xaxis_title="Temperature (°C)", yaxis_title="Wind speed (km/h)",
                                  zaxis_title=f"Mean {pollutant} (µg/m³)",
                                  camera=dict(eye=dict(x=1.6, y=-1.6, z=0.9))))
        show(fig)
        st.caption("Bins with fewer than 100 hourly records are left blank. Drag to rotate.")
        interp(2, 2)

# ================================================================== PAGE 3
else:
    if len(stations) < 3:
        st.warning("Select at least 3 stations in the sidebar to compare stations.")
        st.stop()
    s = core.obj3_summary(df, pollutant)
    stn = s["stations"]
    order = stn["station"].tolist()
    kpis([
        ("Highest station", s["top"], f"{s['top_val']:.1f} µg/m³ mean"),
        ("Lowest station", s["low"], f"{s['low_val']:.1f} µg/m³ mean"),
        ("Spread", f"{s['spread']:.1f}×", "highest ÷ lowest station"),
        ("Above WHO annual limit", f"{s['above_annual']} of {s['n']}", f"limit {G['year']:g} µg/m³"),
        ("Mean station correlation", f"{s['mean_corr']:.2f}", f"weakest pair {s['min_pair'][0]}–{s['min_pair'][1]} ({s['min_corr']:.2f})"),
    ])
    st.write("")

    st.subheader(VIZ_TITLES[3][0])
    bar = stn.sort_values("mean")
    fig = go.Figure(go.Bar(x=bar["mean"], y=bar["station"], orientation="h",
                           marker=dict(color=bar["mean"], colorscale="YlOrRd", colorbar=dict(title="µg/m³")),
                           customdata=np.stack([bar["exceed"], bar["valid"]], axis=-1),
                           hovertemplate="%{y}<br>mean %{x:.1f} µg/m³<br>days above 24-h limit %{customdata[0]:.0f}%"
                                         "<br>valid data %{customdata[1]:.0f}%<extra></extra>"))
    fig.add_vline(x=G["year"], line_dash="dash", line_color="red",
                  annotation_text=f"WHO annual ({G['year']:g})", annotation_position="top")
    base(fig, 560, xaxis_title=f"Mean {pollutant} (µg/m³)", yaxis_title="Station")
    show(fig)
    interp(3, 0)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(VIZ_TITLES[3][1])
        m = core.station_month_matrix(df, pollutant, order)
        fig = go.Figure(go.Heatmap(z=m.values, x=[fmt_month(x) for x in m.columns], y=list(m.index),
                                   colorscale="YlOrRd", colorbar=dict(title="µg/m³"),
                                   hovertemplate="%{y} · %{x}<br>%{z:.1f} µg/m³<extra></extra>"))
        base(fig, 520, xaxis_title="Month", yaxis_title="Station (sorted by mean)")
        fig.update_xaxes(tickangle=-60)
        fig.update_yaxes(type="category", autorange="reversed")
        show(fig)
        interp(3, 1)
    with c2:
        st.subheader(VIZ_TITLES[3][2])
        sc = core.station_corr(df, pollutant, order)
        fig = go.Figure(go.Heatmap(z=sc.values, x=list(sc.columns), y=list(sc.index), zmin=0, zmax=1,
                                   colorscale="Viridis", colorbar=dict(title="r"),
                                   hovertemplate="%{y} vs %{x}<br>r = %{z:.2f}<extra></extra>"))
        base(fig, 520, xaxis_title="Station", yaxis_title="Station")
        fig.update_xaxes(type="category")
        fig.update_yaxes(type="category", autorange="reversed")
        show(fig)
        interp(3, 2)

with st.expander("About the data"):
    st.markdown(f"**Dataset:** {DATASET['title']}  \n**Stations:** {DATASET['stations']}  \n"
                f"**Period:** {DATASET['period']}  \n**Variables:** {DATASET['vars']}  \n"
                f"**Missing data:** {DATASET['missing']}  \n**Source:** {DATASET['source']}")
