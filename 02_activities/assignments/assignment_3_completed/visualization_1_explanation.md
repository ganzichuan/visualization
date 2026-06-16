# Visualization 1: DineSafe Inspections by Establishment Type

**Dataset:** City of Toronto DineSafe Open Data  
Official dataset page: <https://open.toronto.ca/dataset/dinesafe/>  
Reproducible CSV source used in the code: <https://github.com/benwebber/open-data-toronto-dinesafe/raw/refs/heads/main/data/dinesafe.2022.csv>

**Software used:** Python 3, pandas, and Matplotlib.

**Intended audience:** Toronto residents, students learning data visualization, and public-health staff who want a quick overview of where food-safety inspection activity is concentrated.

**Message:** This visualization shows the ten establishment types with the most DineSafe inspection records in 2022. Restaurants and food take-out businesses account for the largest number of inspections. The blue segment shows inspections with at least one recorded infraction, while the grey segment shows inspections without a recorded infraction. The percentage label at the end of each bar helps the audience compare both scale and share.

**Design choices:** I used a horizontal stacked bar chart because the establishment-type names are long and would be hard to read on a vertical axis. The bars are sorted by total inspection volume, so the main pattern is visible immediately. I kept the title direct, used clear axis labels, added a legend, and included percentage labels so the interpretation does not depend only on colour.

**Reproducibility:** The Python script downloads or reads the 2022 DineSafe CSV, converts the inspection date to a date format, collapses duplicate infraction-level rows into one row per inspection ID, and then recreates the summary table and figure. A local copy of the CSV is also included so the code can still run if the online source is temporarily unavailable.

**Accessibility:** The chart uses a high-resolution PNG export, readable text size, a descriptive title, and direct labels. It does not rely only on colour because the legend and percentage labels explain the meaning of each segment.

**Impacted individuals and communities:** This visualization may affect Toronto diners, food-service workers, restaurant owners, inspectors, and communities that rely on local food businesses. To reduce harm, I aggregated by establishment type rather than naming individual businesses.

**Feature selection:** I used inspection ID, establishment type, inspection date, and severity. I excluded business names, addresses, and coordinates because they were unnecessary for this argument and could make the visualization feel punitive toward specific establishments.

**Underwater labour:** The final chart depends on data cleaning, checking duplicate inspection rows, deciding what counts as a recorded infraction, testing chart layouts, exporting readable files, and writing documentation so another person can reproduce the work.
