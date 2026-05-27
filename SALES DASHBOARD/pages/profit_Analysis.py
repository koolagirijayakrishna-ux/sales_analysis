import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------------------------------------------------------
st.set_page_config(page_title="Profitability & Margin Analysis", layout="wide")

st.title("Profitability & Margin Analysis")
st.write(
    "This page provides deep insights into the profitability of our sales operations. "
    "Use this dashboard to analyze profit margins, understand the impact of discounts on profitability, "
    "and audit loss-making transactions."
)

# -----------------------------------------------------------------------------
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    # Strip any potential leading/trailing whitespace from column names
    df.columns = df.columns.str.strip()
    return df

# Load the dataset
data_path = r"C:\Users\Jaya krishna\SALES DASHBOARD\data\sales.xls"
df = load_data(data_path)

# Preprocessing & calculations
if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month_name()
    df["Month Number"] = df["Order Date"].dt.month
    df["Year Month"] = df["Order Date"].dt.to_period("M").astype(str)

# Calculate Profit Margin (%) safely to avoid division by zero
# Profit Margin = (Profit / Sales) * 100
df["Profit Margin (%)"] = np.where(df["Sales"] > 0, (df["Profit"] / df["Sales"]) * 100, 0)

# Binary column to flag unprofitable transactions
df["Is Loss"] = df["Profit"] < 0

# -----------------------------------------------------------------------------
st.subheader("Filters")
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    if "Year" in df.columns:
        selected_years = st.multiselect(
            "Select Year",
            options=sorted(df["Year"].dropna().unique()),
            default=sorted(df["Year"].dropna().unique())
        )
    else:
        selected_years = []

with filter_col2:
    if "Region" in df.columns:
        selected_regions = st.multiselect(
            "Select Region",
            options=sorted(df["Region"].dropna().unique()),
            default=sorted(df["Region"].dropna().unique())
        )
    else:
        selected_regions = []

with filter_col3:
    if "Segment" in df.columns:
        selected_segments = st.multiselect(
            "Select Segment",
            options=sorted(df["Segment"].dropna().unique()),
            default=sorted(df["Segment"].dropna().unique())
        )
    else:
        selected_segments = []

with filter_col4:
    if "Category" in df.columns:
        selected_categories = st.multiselect(
            "Select Category",
            options=sorted(df["Category"].dropna().unique()),
            default=sorted(df["Category"].dropna().unique())
        )
    else:
        selected_categories = []

# Apply filters
filtered_df = df.copy()

if "Year" in filtered_df.columns and selected_years:
    filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]

if "Region" in filtered_df.columns and selected_regions:
    filtered_df = filtered_df[filtered_df["Region"].isin(selected_regions)]

if "Segment" in filtered_df.columns and selected_segments:
    filtered_df = filtered_df[filtered_df["Segment"].isin(selected_segments)]

if "Category" in filtered_df.columns and selected_categories:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

# -----------------------------------------------------------------------------
st.subheader("Key Profit Metrics")

# Core metrics calculations
total_sales = filtered_df["Sales"].sum() if "Sales" in filtered_df.columns else 0
total_profit = filtered_df["Profit"].sum() if "Profit" in filtered_df.columns else 0
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

total_transactions = len(filtered_df)
loss_transactions = filtered_df["Is Loss"].sum() if "Is Loss" in filtered_df.columns else 0
loss_percentage = (loss_transactions / total_transactions * 100) if total_transactions > 0 else 0

avg_profit_per_order = filtered_df["Profit"].mean() if "Profit" in filtered_df.columns else 0

# Visual KPI Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Total Net Profit",
        value=f"${total_profit:,.2f}",
        delta=f"{(total_profit/total_sales * 100):.1f}% Margin" if total_sales > 0 else None
    )

with kpi2:
    st.metric(
        label="Average Profit Margin",
        value=f"{profit_margin:.2f}%",
        delta="Target is > 10.0%"
    )

with kpi3:
    st.metric(
        label="Loss-making Transactions",
        value=f"{loss_transactions:,}",
        delta=f"{loss_percentage:.1f}% of orders",
        delta_color="inverse"
    )

with kpi4:
    st.metric(
        label="Average Profit per Order",
        value=f"${avg_profit_per_order:,.2f}"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
st.subheader("Profitability Trends")

if "Year Month" in filtered_df.columns and "Profit" in filtered_df.columns:
    # Aggregate monthly profit, sales, and margin
    monthly_stats = filtered_df.groupby("Year Month", as_index=False).agg({
        "Sales": "sum",
        "Profit": "sum"
    })
    monthly_stats["Profit Margin (%)"] = np.where(
        monthly_stats["Sales"] > 0,
        (monthly_stats["Profit"] / monthly_stats["Sales"]) * 100,
        0
    )
    monthly_stats = monthly_stats.sort_values("Year Month")

    trend_tab1, trend_tab2 = st.tabs(["Profit vs. Sales Trend", "Profit Margin (%) Trend"])

    with trend_tab1:
        fig_trend1 = px.line(
            monthly_stats,
            x="Year Month",
            y=["Sales", "Profit"],
            labels={"value": "Amount ($)", "variable": "Metric"},
            title="Monthly Sales & Profit Comparison",
            markers=True,
            color_discrete_map={"Sales": "#1f77b4", "Profit": "#2ca02c"}
        )
        st.plotly_chart(fig_trend1, use_container_width=True)

    with trend_tab2:
        fig_trend2 = px.area(
            monthly_stats,
            x="Year Month",
            y="Profit Margin (%)",
            title="Monthly Profit Margin (%) Trend",
            markers=True,
            color_discrete_sequence=["#ff7f0e"]
        )
        # Add a baseline helper line at 0%
        fig_trend2.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even Line")
        st.plotly_chart(fig_trend2, use_container_width=True)

# -----------------------------------------------------------------------------
st.subheader("Product & Category Profitability")

col_cat1, col_cat2 = st.columns(2)

with col_cat1:
    if "Category" in filtered_df.columns:
        cat_stats = filtered_df.groupby("Category", as_index=False).agg({
            "Sales": "sum",
            "Profit": "sum"
        })
        cat_stats["Profit Margin (%)"] = (cat_stats["Profit"] / cat_stats["Sales"]) * 100
        cat_stats = cat_stats.sort_values("Profit", ascending=False)

        fig_cat = px.bar(
            cat_stats,
            x="Category",
            y="Profit",
            color="Profit Margin (%)",
            color_continuous_scale=px.colors.sequential.Viridis,
            title="Net Profit by Product Category",
            text_auto=".2s"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

with col_cat2:
    if "Sub-Category" in filtered_df.columns:
        sub_stats = filtered_df.groupby("Sub-Category", as_index=False).agg({
            "Sales": "sum",
            "Profit": "sum"
        })
        sub_stats["Profit Margin (%)"] = (sub_stats["Profit"] / sub_stats["Sales"]) * 100
        sub_stats = sub_stats.sort_values("Profit", ascending=True)  # Ascending so biggest loss or smallest profit is at the bottom/top

        fig_sub = px.bar(
            sub_stats,
            y="Sub-Category",
            x="Profit",
            orientation="h",
            color="Profit",
            color_continuous_scale=px.colors.diverging.RdYlGn,
            color_continuous_midpoint=0,
            title="Net Profit by Sub-Category (Diverging Color Scale)",
            labels={"Profit": "Net Profit ($)"}
        )
        st.plotly_chart(fig_sub, use_container_width=True)

#-----------------------------------------------------------------------------
st.subheader("Discount Analysis & Margin Erosion")
st.write(
    "One of the most critical factors impacting retail profitability is discounting. "
    "The visualizations below demonstrate how higher discount rates impact our margins."
)

col_disc1, col_disc2 = st.columns(2)

with col_disc1:
    if "Discount" in filtered_df.columns and "Profit Margin (%)" in filtered_df.columns:
        # Group by Discount Rate and compute average Profit Margin
        disc_grouped = filtered_df.groupby("Discount", as_index=False).agg({
            "Profit Margin (%)": "mean",
            "Profit": "sum",
            "Order ID": "count"
        }).rename(columns={"Order ID": "Total Orders"})
        disc_grouped = disc_grouped.sort_values("Discount")

        # Format Discount as percentage for labels
        disc_grouped["Discount Rate (%)"] = (disc_grouped["Discount"] * 100).astype(str) + "%"

        fig_disc_line = px.bar(
            disc_grouped,
            x="Discount Rate (%)",
            y="Profit Margin (%)",
            color="Profit Margin (%)",
            color_continuous_scale=px.colors.diverging.RdYlGn,
            color_continuous_midpoint=0,
            title="Average Profit Margin (%) at Different Discount Rates",
            text_auto=".1f"
        )
        st.plotly_chart(fig_disc_line, use_container_width=True)

with col_disc2:
    if "Discount" in filtered_df.columns and "Profit" in filtered_df.columns:
        fig_disc_scatter = px.scatter(
            filtered_df,
            x="Discount",
            y="Profit",
            color="Category" if "Category" in filtered_df.columns else None,
            hover_data=["Sub-Category", "Product Name", "Sales"],
            opacity=0.6,
            title="Transaction Level: Discount vs. Net Profit"
        )
        # Draw a horizontal baseline at 0 profit
        fig_disc_scatter.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig_disc_scatter, use_container_width=True)

# -----------------------------------------------------------------------------
st.subheader("Regional & Segment Performance")

col_geo1, col_geo2 = st.columns(2)

with col_geo1:
    if "State" in filtered_df.columns and "Profit" in filtered_df.columns:
        state_stats = filtered_df.groupby("State", as_index=False).agg({
            "Sales": "sum",
            "Profit": "sum"
        })
        state_stats = state_stats.sort_values("Profit", ascending=False)

        # Show Top 10 States
        fig_state = px.bar(
            state_stats.head(10),
            x="Profit",
            y="State",
            orientation="h",
            title="Top 10 Most Profitable States",
            color="Profit",
            color_continuous_scale=px.colors.sequential.Greens
        )
        fig_state.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_state, use_container_width=True)

with col_geo2:
    if "Segment" in filtered_df.columns and "Profit" in filtered_df.columns:
        segment_stats = filtered_df.groupby("Segment", as_index=False).agg({
            "Sales": "sum",
            "Profit": "sum"
        })
        segment_stats["Profit Margin (%)"] = (segment_stats["Profit"] / segment_stats["Sales"]) * 100

        fig_seg = px.pie(
            segment_stats,
            names="Segment",
            values="Profit",
            color="Segment",
            title="Net Profit Distribution by Segment",
            hole=0.4
        )
        st.plotly_chart(fig_seg, use_container_width=True)

# ------------------------------------------------------------------------
st.subheader("Operational Audit: Unprofitable Transactions")
st.write(
    "Investigate transactions that resulted in financial losses. "
    "Audit these records to identify products or customers requiring pricing reviews."
)

# Extract loss-making transactions
loss_df = filtered_df[filtered_df["Is Loss"] == True].copy()

if not loss_df.empty:
    # Sort by greatest loss first
    loss_df = loss_df.sort_values("Profit", ascending=True)

    # Let the user filter by category or text search
    search_term = st.text_input("Search Unprofitable Transactions by Product Name or Customer Name")

    display_df = loss_df.copy()
    if search_term:
        display_df = display_df[
            display_df["Product Name"].str.contains(search_term, case=False, na=False) |
            display_df["Customer Name"].str.contains(search_term, case=False, na=False)
        ]

    # Show summary metric
    st.info(f"Showing {len(display_df)} unprofitable transactions with a combined loss of **${display_df['Profit'].sum():,.2f}**")

    # Pick key columns for display to keep it clear and focused
    cols_to_show = [
        "Order ID", "Order Date", "Customer Name", "Segment", "Region", "State", 
        "Category", "Sub-Category", "Product Name", "Sales", "Discount", "Profit"
    ]
    # Only show columns that exist in the dataframe
    cols_to_show = [col for col in cols_to_show if col in display_df.columns]
    st.dataframe(display_df[cols_to_show], use_container_width=True)

    # Allow downloading the loss audit data
    loss_csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Unprofitable Transactions Audit Log (CSV)",
        data=loss_csv,
        file_name="unprofitable_orders_audit.csv",
        mime="text/csv"
    )
else:
    st.success("Excellent! No unprofitable transactions found with current filters.")