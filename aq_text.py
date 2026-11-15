"""Objective statements and interpretations (written for PM2.5, full dataset, all 21 stations)."""

OBJECTIVES = {
    1: ("Objective 1 - Temporal patterns of particulate pollution",
        "Characterise how PM2.5 concentrations change over the long term, between seasons and across the "
        "hours of the day, and identify when air quality is worst relative to the WHO guideline."),
    2: ("Objective 2 - Meteorological drivers of pollution",
        "Examine how temperature, wind speed, humidity, pressure and rain relate to PM2.5 and PM10, "
        "to identify which weather conditions favour pollution build-up or removal."),
    3: ("Objective 3 - Spatial comparison of monitoring stations",
        "Compare the 21 monitoring stations to reveal where pollution is highest or lowest, how strongly "
        "the seasonal cycle differs between sites, and how coherent pollution episodes are across the network."),
}

VIZ_TITLES = {
    1: ["1.1 Daily mean PM2.5 (line plot)", "1.2 Hour-of-day x month heatmap", "1.3 Diurnal profile by season (line plot)"],
    2: ["2.1 Correlation heatmap", "2.2 PM2.5 vs temperature (scatter plot)", "2.3 PM2.5 over temperature x wind speed (surface plot)"],
    3: ["3.1 Mean PM2.5 by station (bar chart)", "3.2 Station x month heatmap", "3.3 Station-to-station correlation (heatmap)"],
}

INTERP = {
    1: [
        "Daily network-average PM2.5 follows a strong seasonal cycle: winter (Dec–Feb) averages 26.3 µg/m³ against "
        "9.4 µg/m³ in summer (about 2.8x). The monthly mean peaks in Feb 2025 (33.1) and bottoms out in Sep 2025 (6.0). "
        "167 of 589 days (28%) exceed the WHO 24-hour guideline of 15 µg/m³, 136 of them in winter and autumn. "
        "The sharpest spike is 31 Dec 2024 (61 µg/m³), coinciding with New Year celebrations (a likely, but untested, fireworks effect). "
        "Nov-Dec 2025 (16.5) was much cleaner than Nov-Dec 2024 (25.9), so year-to-year weather variability is large; "
        "with only one complete winter no long-term trend can be claimed.",

        "The heatmap shows that the pollution is concentrated in the evening and night hours of the cold months: "
        "the highest cell is 42 µg/m³ at 22:00 in Feb 2025, whereas from Apr to Sep almost every hour stays below about 12.5 µg/m³ "
        "(lowest cell 5.2 µg/m³, Sep 2025, 17:00). The evening build-up starting around 18:00-19:00 is consistent with "
        "residential heating emissions released into a shallow, stable nocturnal boundary layer.",

        "Winter has a large diurnal swing: 35.4 µg/m³ at 21:00 against 20.1 at 15:00 (amplitude 15.3), whereas summer is almost flat "
        "(1.4). Spring and autumn lie between. All seasons share an afternoon minimum (15:00-18:00) when convective mixing dilutes "
        "pollutants, and a small morning bump near 09:00-10:00 that fits the rush-hour traffic. Heating-related evening emissions "
        "therefore dominate the cold-season signal.",
    ],
    2: [
        "PM2.5 and PM10 are strongly correlated (r = 0.91) and PM2.5 makes up about 70% of PM10 mass, so fine combustion particles "
        "dominate. Among weather variables, temperature (r = -0.39) and pressure (r = +0.39) show the clearest links with PM2.5, "
        "followed by wind speed (-0.20), humidity (+0.16) and rain (-0.07). The weather variables are themselves correlated "
        "(temperature-humidity -0.53, temperature-pressure -0.41), so the coefficients describe association, not isolated causes. "
        "Note: the column labelled 'precipitation' (16-100) behaves like relative humidity and is treated as such.",

        "PM2.5 rises as temperature falls: the mean is about 31 µg/m³ between -6 and -2 °C, 25.6 below 5 °C and only 9.9 above 20 °C; the binned mean bottoms out near 15 °C (7.7) and drifts up again to 14 at 35 °C. "
        "The coldest bins (below -8 °C) contain few observations and are lower. Winter hours are widely scattered, so cold alone is not "
        "sufficient - dispersion matters. In summer the relation is weakly positive (r = +0.30), pointing to a different mechanism "
        "(e.g. secondary aerosol formation or dust) than winter heating emissions.",

        "The surface combines the two main drivers. The highest PM2.5 (about 32 µg/m³) occurs when it is cold (-8 to 0 °C) and the "
        "wind is calm; at -4 to 0 °C, raising wind speed from the 0-3 to the 9-12 band lowers the mean from 32.5 to 20.6 µg/m³ (-37%). Between 18 and 24 °C "
        "values stay around 7-10 µg/m³ whatever the wind. This reflects stagnation: low wind plus cold, stable air traps emissions near the "
        "ground. Supporting this, PM2.5 averages 31.7 µg/m³ when pressure exceeds 1030 hPa (anticyclonic, inversion-prone) "
        "versus 7.6 below 1000 hPa, and 9.7 during rain versus 13.6 in dry hours (wet removal). Wind speed units are not documented "
        "(assumed km/h).",
    ],
    3: [
        "All 21 stations exceed the WHO annual PM2.5 guideline of 5 µg/m³. Station means range from 7.4 (E420) to 16.5 µg/m³ (E803), "
        "a factor of 2.2. E803, E410 and E802 are the highest; E420 is by far the cleanest, with only 8% of days above 15 µg/m³ versus "
        "about 34% at E410. E803 has 11% missing PM2.5 data, so its mean is less certain.",

        "Every station shares the same winter-high seasonal shape, but the amplitude differs strongly. E410 averages 35.1 µg/m³ in winter "
        "against 9.7 in summer, while E420 changes only from 9.2 to 8.4, which is typical of a background site with little heating emission. "
        "E423 (warmest station, mean 17.6 °C) is also low. E802 stands out in Dec 2024 (mean 44.5 vs 26.1 at the other stations) "
        "because of midday spikes up to 384 µg/m³ with PM2.5 almost equal to PM10 - a local source or a sensor fault that should be verified.",

        "Hourly PM2.5 is highly synchronised across most stations (mean pairwise correlation 0.67), so pollution episodes are largely "
        "regional and weather-driven. The exceptions are E420 and E802 (r = 0.18 with each other) and E423, which behave "
        "independently and are influenced by local sources or a different local climate. Station coordinates are not included in the "
        "dataset, so a geospatial map could not be drawn.",
    ],
}

DATASET = {
    "source": "Vrbančič, G. (2026). Air quality dataset, Version 2. Mendeley Data. https://doi.org/10.17632/p86hnykz3d.2 (CC BY 4.0)",
    "title": "Hourly air-quality and weather measurements from 21 monitoring stations",
    "stations": "E403-E423 and E801-E804 (21 stations)",
    "period": "2 May 2024 20:00 - 11 Dec 2025 07:00 (14,100 hourly records per station)",
    "rows": "296,100 hourly records",
    "vars": "PM2.5, PM10 (µg/m³), temperature (°C), humidity (%, stored as 'precipitation'), rain, pressure (hPa), wind speed, "
            "cloud cover and wind direction (categorical, Slovene labels)",
    "missing": "about 1.5% missing in each measured variable; wind direction is missing for 49% of rows "
               "(absent before Feb 2025), so it was not used.",
}
