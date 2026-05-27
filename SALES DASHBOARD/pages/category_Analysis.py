import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Sales Category Analysis", layout="wide")

# -----------------------------
# Read Excel File
# -----------------------------
@st.cache_data
def read_excel(file):
    df = pd.read_excel(file)
    return df

df = read_excel("data/sales.xls")

# -----------------------------
# Page Title
# -----------------------------
st.title("Sales Data Analysis")
st.write("This is a simple Streamlit app to analyze sales data.")

# -----------------------------
# Dataset Overview
# -----------------------------
st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Rows", df.shape[0])

with col2:
    st.metric("Total Columns", df.shape[1])

with col3:
    st.metric("Total Records", len(df))

st.dataframe(df.head(), use_container_width=True)

# -----------------------------
# Data Cleaning
# -----------------------------
df.columns = df.columns.str.strip()

if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month_name()

# -----------------------------
# Main Page Filters
# -----------------------------
st.subheader("Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    if "Category" in df.columns:
        selected_category = st.multiselect(
            "Select Category",
            options=df["Category"].dropna().unique(),
            default=df["Category"].dropna().unique()
        )
    else:
        selected_category = []

with filter_col2:
    if "Sub-Category" in df.columns:
        selected_sub_category = st.multiselect(
            "Select Sub-Category",
            options=df["Sub-Category"].dropna().unique(),
            default=df["Sub-Category"].dropna().unique()
        )
    else:
        selected_sub_category = []

with filter_col3:
    if "Region" in df.columns:
        selected_region = st.multiselect(
            "Select Region",
            options=df["Region"].dropna().unique(),
            default=df["Region"].dropna().unique()
        )
    else:
        selected_region = []

filtered_df = df.copy()

if "Category" in df.columns and selected_category:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_category)]

if "Sub-Category" in df.columns and selected_sub_category:
    filtered_df = filtered_df[filtered_df["Sub-Category"].isin(selected_sub_category)]

if "Region" in df.columns and selected_region:
    filtered_df = filtered_df[filtered_df["Region"].isin(selected_region)]

# -----------------------------
# KPI Cards
# -----------------------------
st.subheader("Key Metrics")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    if "Sales" in filtered_df.columns:
        st.metric("Total Sales", f"{filtered_df['Sales'].sum():,.2f}")

with kpi2:
    if "Profit" in filtered_df.columns:
        st.metric("Total Profit", f"{filtered_df['Profit'].sum():,.2f}")

with kpi3:
    if "Quantity" in filtered_df.columns:
        st.metric("Total Quantity", int(filtered_df["Quantity"].sum()))

with kpi4:
    if "Order ID" in filtered_df.columns:
        st.metric("Total Orders", filtered_df["Order ID"].nunique())

# -----------------------------
# Category Wise Sales
# -----------------------------
st.subheader("Category Wise Sales")

if "Category" in filtered_df.columns and "Sales" in filtered_df.columns:
    category_sales = filtered_df.groupby("Category", as_index=False)["Sales"].sum()

    fig1 = px.bar(
        category_sales,
        x="Category",
        y="Sales",
        text_auto=True,
        title="Category Wise Sales"
    )

    st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# Category Wise Profit
# -----------------------------
st.subheader("Category Wise Profit")

if "Category" in filtered_df.columns and "Profit" in filtered_df.columns:
    category_profit = filtered_df.groupby("Category", as_index=False)["Profit"].sum()

    fig2 = px.pie(
        category_profit,
        names="Category",
        values="Profit",
        title="Category Wise Profit Share"
    )

    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Sub-Category Wise Sales and Profit
# -----------------------------
st.subheader("Sub-Category Wise Sales and Profit")

if "Sub-Category" in filtered_df.columns:
    sub_category_data = filtered_df.groupby("Sub-Category", as_index=False).agg({
        "Sales": "sum",
        "Profit": "sum"
    })

    fig3 = px.bar(
        sub_category_data,
        x="Sub-Category",
        y=["Sales", "Profit"],
        barmode="group",
        title="Sub-Category Wise Sales and Profit"
    )

    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Region Wise Sales
# -----------------------------
st.subheader("Region Wise Sales")

if "Region" in filtered_df.columns and "Sales" in filtered_df.columns:
    region_sales = filtered_df.groupby("Region", as_index=False)["Sales"].sum()

    fig4 = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        text_auto=True,
        title="Region Wise Sales"
    )

    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# Discount vs Profit
# -----------------------------
st.subheader("Discount vs Profit")

if "Discount" in filtered_df.columns and "Profit" in filtered_df.columns:
    fig5 = px.scatter(
        filtered_df,
        x="Discount",
        y="Profit",
        color="Category" if "Category" in filtered_df.columns else None,
        title="Discount vs Profit"
    )

    st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# Monthly Sales Trend
# -----------------------------
st.subheader("Monthly Sales Trend")

if "Order Date" in filtered_df.columns and "Sales" in filtered_df.columns:
    monthly_sales = filtered_df.groupby(
        filtered_df["Order Date"].dt.to_period("M")
    )["Sales"].sum().reset_index()

    monthly_sales["Order Date"] = monthly_sales["Order Date"].astype(str)

    fig6 = px.line(
        monthly_sales,
        x="Order Date",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend"
    )

    st.plotly_chart(fig6, use_container_width=True)

# -----------------------------
# Summary Table
# -----------------------------
st.subheader("Category Summary Table")

if "Category" in filtered_df.columns and "Sub-Category" in filtered_df.columns:
    summary_table = filtered_df.groupby(
        ["Category", "Sub-Category"],
        as_index=False
    ).agg({
        "Sales": "sum",
        "Profit": "sum",
        "Quantity": "sum",
        "Discount": "mean"
    })

    st.dataframe(summary_table, use_container_width=True)

# -----------------------------
# Download Filtered Data
# -----------------------------
st.subheader("Download Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)