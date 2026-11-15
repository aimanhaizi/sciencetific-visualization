"""Data loading + all calculations behind the three pages (pandas/numpy only)."""
import numpy as np
import pandas as pd

SEASONS = ["Winter", "Spring", "Summer", "Autumn"]
WHO_24H = 15.0   # WHO 2021 24-hour PM2.5 guideline (µg/m³)
WHO_ANNUAL = 5.0 # WHO 2021 annual PM2.5 guideline (µg/m³)
GUIDE = {"PM2.5": {"day": 15.0, "year": 5.0}, "PM10": {"day": 45.0, "year": 15.0}}  # WHO 2021
MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _season(m):
    return {12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring",
            6: "Summer", 7: "Summer", 8: "Summer"}.get(m, "Autumn")


def load(path):
    df = pd.read_csv(path, parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.normalize()
    df["hour"] = df["datetime"].dt.hour
    df["month"] = df["datetime"].dt.month
    df["ym"] = df["datetime"].dt.to_period("M").dt.to_timestamp()
    df["season"] = df["month"].map(_season)
    return df


def pol(df, p):
    """column name of the selected pollutant"""
    return "PM25" if p == "PM2.5" else "PM10"


# ---------------------------------------------------------------- objective 1
def daily_mean(df, p):
    c = pol(df, p)
    d = df.groupby("date")[c].mean().rename("value").reset_index()
    d["rolling7"] = d["value"].rolling(7, center=True, min_periods=4).mean()
    return d


def hour_month_matrix(df, p):
    c = pol(df, p)
    m = df.pivot_table(index="hour", columns="ym", values=c, aggfunc="mean")
    return m


def diurnal_by_season(df, p):
    c = pol(df, p)
    return df.groupby(["season", "hour"])[c].mean().rename("value").reset_index()


def obj1_summary(df, p):
    c = pol(df, p)
    dm = df.groupby("date")[c].mean()
    mm = df.groupby("ym")[c].mean()
    hh = df.groupby("hour")[c].mean()
    ss = df.groupby("season")[c].mean()
    return {
        "mean": df[c].mean(),
        "peak_month": mm.idxmax(), "peak_month_val": mm.max(),
        "low_month": mm.idxmin(), "low_month_val": mm.min(),
        "peak_hour": int(hh.idxmax()), "peak_hour_val": hh.max(),
        "low_hour": int(hh.idxmin()), "low_hour_val": hh.min(),
        "winter": ss.get("Winter", np.nan), "summer": ss.get("Summer", np.nan),
        "ratio": ss.get("Winter", np.nan) / ss.get("Summer", np.nan),
        "exceed_days": (dm > GUIDE[p]["day"]).mean() * 100,
        "n_days": len(dm),
        "worst_day": dm.idxmax(), "worst_day_val": dm.max(),
    }


# ---------------------------------------------------------------- objective 2
MET_COLS = ["temperature", "humidity", "wind_speed", "pressure", "rain"]
MET_LABEL = {"PM25": "PM2.5", "PM10": "PM10", "temperature": "Temperature", "humidity": "Humidity",
             "wind_speed": "Wind speed", "pressure": "Pressure", "rain": "Rain"}


def corr_matrix(df):
    cols = ["PM25", "PM10"] + MET_COLS
    m = df[cols].corr()
    m.index = [MET_LABEL[i] for i in m.index]
    m.columns = [MET_LABEL[i] for i in m.columns]
    return m


def binned_mean(df, xcol, ycol, bins):
    b = pd.cut(df[xcol], bins=bins)
    g = df.groupby(b, observed=True)[ycol].agg(["mean", "count"]).reset_index()
    g["x"] = g[xcol].apply(lambda i: i.mid).astype(float)
    return g[g["count"] >= 50]


def scatter_sample(df, p, n=20000, seed=42):
    c = pol(df, p)
    s = df.dropna(subset=[c, "temperature", "wind_speed"])
    return s.sample(min(n, len(s)), random_state=seed)


def surface_grid(df, p, tstep=4, wstep=3, wmax=24, min_n=100):
    """mean pollutant over temperature x wind-speed bins (NaN where too few obs)"""
    c = pol(df, p)
    d = df.dropna(subset=[c, "temperature", "wind_speed"])
    tb = np.arange(np.floor(d["temperature"].min() / tstep) * tstep, d["temperature"].max() + tstep, tstep)
    wb = np.arange(0, wmax + wstep, wstep)
    d = d.assign(tb=pd.cut(d["temperature"], tb), wb=pd.cut(d["wind_speed"], wb, include_lowest=True))
    g = d.groupby(["wb", "tb"], observed=False)[c].agg(["mean", "count"])
    z = g["mean"].where(g["count"] >= min_n).unstack("tb")
    xs = [i.mid for i in z.columns]
    ys = [i.mid for i in z.index]
    return np.array(xs), np.array(ys), z.values


def obj2_summary(df, p):
    c = pol(df, p)
    r = lambda a: df[[c, a]].corr().iloc[0, 1]
    calm = df.loc[df["wind_speed"] <= 2, c].mean()
    windy = df.loc[df["wind_speed"] >= 10, c].mean()
    cold = df.loc[df["temperature"] < 5, c].mean()
    warm = df.loc[df["temperature"] >= 20, c].mean()
    return {"r_temp": r("temperature"), "r_wind": r("wind_speed"), "r_hum": r("humidity"),
            "r_press": r("pressure"), "calm": calm, "windy": windy, "cold": cold, "warm": warm,
            "ratio25_10": (df["PM25"].sum() / df.loc[df["PM25"].notna() & df["PM10"].notna(), "PM10"].sum())}


# ---------------------------------------------------------------- objective 3
def station_stats(df, p):
    c = pol(df, p)
    dd = df.groupby(["station", "date"])[c].mean().reset_index()
    exc = dd.groupby("station")[c].apply(lambda s: (s > GUIDE[p]["day"]).mean() * 100).rename("exceed")
    g = df.groupby("station").agg(mean=(c, "mean"), p95=(c, lambda s: s.quantile(.95)),
                                  temp=("temperature", "mean"), valid=(c, lambda s: s.notna().mean() * 100))
    return g.join(exc).reset_index().sort_values("mean", ascending=False).reset_index(drop=True)


def station_month_matrix(df, p, order):
    c = pol(df, p)
    m = df.pivot_table(index="station", columns="ym", values=c, aggfunc="mean")
    return m.loc[[s for s in order if s in m.index]]


def station_corr(df, p, order):
    c = pol(df, p)
    w = df.pivot_table(index="datetime", columns="station", values=c)
    o = [s for s in order if s in w.columns]
    return w[o].corr()


def obj3_summary(df, p):
    st = station_stats(df, p)
    sc = station_corr(df, p, st["station"].tolist())
    off = sc.values[~np.eye(len(sc), dtype=bool)]
    return {"n": len(st), "top": st.iloc[0]["station"], "top_val": st.iloc[0]["mean"],
            "low": st.iloc[-1]["station"], "low_val": st.iloc[-1]["mean"],
            "spread": st.iloc[0]["mean"] / st.iloc[-1]["mean"],
            "mean_corr": float(np.nanmean(off)), "min_corr": float(np.nanmin(off)),
            "min_pair": None if len(sc) < 2 else _minpair(sc),
            "above_annual": int((st["mean"] > GUIDE[p]["year"]).sum()),
            "stations": st}


def _minpair(sc):
    v = sc.where(~np.eye(len(sc), dtype=bool))
    s = v.stack()
    a, b = s.idxmin()
    return a, b
