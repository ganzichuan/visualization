
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

DATASET_PAGE = "https://open.toronto.ca/dataset/dinesafe/"
RAW_CSV_URL = "https://github.com/benwebber/open-data-toronto-dinesafe/raw/refs/heads/main/data/dinesafe.2022.csv"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FIG_DIR = BASE_DIR / "figures"
LOCAL_CSV = DATA_DIR / "dinesafe.2022.csv"

DATA_DIR.mkdir(exist_ok=True)
FIG_DIR.mkdir(exist_ok=True)


def load_dinesafe() -> pd.DataFrame:
    """Load the DineSafe CSV from a local copy when available, otherwise from the web."""
    if LOCAL_CSV.exists():
        source = LOCAL_CSV
    else:
        source = RAW_CSV_URL
    df = pd.read_csv(source)
    df["Inspection Date"] = pd.to_datetime(df["Inspection Date"], errors="coerce")
    return df


def make_inspection_level(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse infraction-level rows into one row per inspection ID."""
    df = df.copy()
    df["Severity"] = df["Severity"].fillna("").astype(str).str.strip()
    df["has_infraction"] = df["Severity"].ne("") & ~df["Severity"].str.contains(
        "Not Applicable", case=False, na=False
    )

    inspection = (
        df.sort_values("Rec #")
        .groupby("Inspection ID", as_index=False)
        .agg(
            Establishment_Type=("Establishment Type", "first"),
            Establishment_Status=("Establishment Status", "first"),
            Inspection_Date=("Inspection Date", "first"),
            Has_Infraction=("has_infraction", "max"),
        )
    )
    inspection = inspection.dropna(subset=["Inspection_Date"])
    return inspection


def create_visualization_1(inspection: pd.DataFrame) -> pd.DataFrame:
    """Create a horizontal bar chart of inspections and recorded infractions by type."""
    summary = (
        inspection.groupby("Establishment_Type", as_index=False)
        .agg(
            Inspection_Records=("Inspection ID", "count"),
            Records_With_Infractions=("Has_Infraction", "sum"),
        )
        .assign(
            Records_Without_Recorded_Infractions=lambda x: x["Inspection_Records"]
            - x["Records_With_Infractions"],
            Infraction_Share=lambda x: x["Records_With_Infractions"] / x["Inspection_Records"],
        )
        .sort_values("Inspection_Records", ascending=False)
        .head(10)
        .sort_values("Inspection_Records", ascending=True)
    )
    summary.to_csv(DATA_DIR / "establishment_type_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(
        summary["Establishment_Type"],
        summary["Records_Without_Recorded_Infractions"],
        label="No recorded infraction",
        color="#D9D9D9",
    )
    ax.barh(
        summary["Establishment_Type"],
        summary["Records_With_Infractions"],
        left=summary["Records_Without_Recorded_Infractions"],
        label="At least one recorded infraction",
        color="#2A6FBB",
    )

    for _, row in summary.iterrows():
        ax.text(
            row["Inspection_Records"] + 80,
            row["Establishment_Type"],
            f"{row['Infraction_Share']:.0%}",
            va="center",
            fontsize=9,
        )

    ax.set_title("DineSafe inspections by establishment type, Toronto, 2022", fontsize=15, pad=14)
    ax.set_xlabel("Number of inspection records; labels show share with recorded infractions")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "visualization_1_python_establishment_type.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return summary


def create_visualization_2(inspection: pd.DataFrame) -> pd.DataFrame:
    """Create a monthly conditional-pass-rate line chart and export the summary table."""
    monthly = (
        inspection.assign(Month=inspection["Inspection_Date"].dt.to_period("M"))
        .groupby(["Month", "Establishment_Status"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .sort_values("Month")
    )
    for col in ["Pass", "Conditional Pass", "Closed"]:
        if col not in monthly.columns:
            monthly[col] = 0
    monthly["Total Inspections"] = monthly[["Pass", "Conditional Pass", "Closed"]].sum(axis=1)
    monthly["Conditional Pass Rate"] = monthly["Conditional Pass"] / monthly["Total Inspections"]
    monthly["Month_Label"] = monthly["Month"].dt.strftime("%b")
    monthly = monthly[
        ["Month_Label", "Pass", "Conditional Pass", "Closed", "Total Inspections", "Conditional Pass Rate"]
    ].rename(columns={"Month_Label": "Month"})
    monthly.to_csv(DATA_DIR / "monthly_status_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(monthly["Month"], monthly["Conditional Pass Rate"], marker="o", linewidth=2.5)
    ax.set_title("Monthly share of DineSafe inspections with Conditional Pass status, 2022", fontsize=14, pad=14)
    ax.set_ylabel("Conditional Pass rate")
    ax.set_xlabel("Month of inspection")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.grid(axis="y", alpha=0.3)
    for x, y in zip(monthly["Month"], monthly["Conditional Pass Rate"]):
        ax.text(x, y + 0.0008, f"{y:.1%}", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "visualization_2_monthly_rate_reference.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return monthly


def main() -> None:
    raw_df = load_dinesafe()
    inspection = make_inspection_level(raw_df)
    create_visualization_1(inspection)
    create_visualization_2(inspection)
    print("Saved figures and summary CSVs to:", BASE_DIR)


if __name__ == "__main__":
    main()
