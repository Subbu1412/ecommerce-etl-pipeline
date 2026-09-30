import os

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
)


DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "database": os.getenv("PGDATABASE", "ecommerce"),
    "user": os.getenv("PGUSER", "etl_user"),
    "password": os.getenv("PGPASSWORD", "etl_password"),
}


# ============================================================
# DATABASE
# ============================================================

@st.cache_resource
def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@st.cache_data(ttl=60)
def load_query(query):
    conn = get_connection()
    return pd.read_sql_query(query, conn)


# ============================================================
# HEADER
# ============================================================

st.title("🛒 E-Commerce Analytics Dashboard")
st.caption("Airflow + PySpark + PostgreSQL + Streamlit")

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Dashboard Filters")

category_filter = st.sidebar.multiselect(
    "Category",
    options=[
        "Clothing",
        "Electronics",
        "Books",
        "Home & Kitchen",
        "Beauty",
        "Sports",
    ],
)


# ============================================================
# KPI QUERIES
# ============================================================

kpi_query = """
SELECT
    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE LOWER(status) = 'completed'
    ) AS completed_orders,

    COUNT(*) FILTER (
        WHERE LOWER(status) = 'cancelled'
    ) AS cancelled_orders,

    COALESCE(
        ROUND(
            SUM(total_amount)
            FILTER (
                WHERE LOWER(status) <> 'cancelled'
            ),
            2
        ),
        0
    ) AS total_revenue,

    COALESCE(
        ROUND(
            AVG(total_amount)
            FILTER (
                WHERE LOWER(status) <> 'cancelled'
            ),
            2
        ),
        0
    ) AS average_order_value

FROM analytics.fact_orders;
"""

kpis = load_query(kpi_query).iloc[0]


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Orders",
    f"{int(kpis['total_orders']):,}"
)

col2.metric(
    "Completed Orders",
    f"{int(kpis['completed_orders']):,}"
)

col3.metric(
    "Cancelled Orders",
    f"{int(kpis['cancelled_orders']):,}"
)

col4.metric(
    "Revenue",
    f"₹{kpis['total_revenue']:,.0f}"
)

col5.metric(
    "Average Order Value",
    f"₹{kpis['average_order_value']:,.0f}"
)


st.divider()


# ============================================================
# CATEGORY SALES
# ============================================================

category_query = """
SELECT
    category,
    order_count,
    units_sold,
    revenue
FROM analytics.v_category_sales
ORDER BY revenue DESC;
"""

category_df = load_query(category_query)

if category_filter:
    category_df = category_df[
        category_df["category"].isin(category_filter)
    ]


# ============================================================
# CATEGORY CHARTS
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader("Revenue by Category")

    if not category_df.empty:

        fig = px.bar(
            category_df,
            x="category",
            y="revenue",
            text_auto=".2s",
            title="Revenue by Product Category",
        )

        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Revenue",
            showlegend=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info("No data available for the selected category.")


with col2:

    st.subheader("Units Sold by Category")

    if not category_df.empty:

        fig = px.pie(
            category_df,
            names="category",
            values="units_sold",
            title="Units Sold Distribution",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info("No data available for the selected category.")


# ============================================================
# DAILY SALES
# ============================================================

st.subheader("Daily Sales Trend")

daily_query = """
SELECT
    order_date,
    order_count,
    units_sold,
    revenue
FROM analytics.v_daily_sales
ORDER BY order_date;
"""

daily_df = load_query(daily_query)

fig = px.line(
    daily_df,
    x="order_date",
    y="revenue",
    markers=True,
    title="Daily Revenue",
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Revenue",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# ORDER STATUS BREAKDOWN
# ============================================================

st.subheader("Order Status Distribution")

status_query = """
SELECT
    INITCAP(LOWER(status)) AS status,
    COUNT(*) AS order_count
FROM analytics.fact_orders
GROUP BY LOWER(status)
ORDER BY order_count DESC;
"""

status_df = load_query(status_query)

col1, col2 = st.columns(2)


with col1:

    fig = px.bar(
        status_df,
        x="status",
        y="order_count",
        text_auto=True,
        title="Orders by Status",
    )

    fig.update_layout(
        xaxis_title="Order Status",
        yaxis_title="Orders",
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


with col2:

    fig = px.pie(
        status_df,
        names="status",
        values="order_count",
        title="Order Status Distribution",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# TOP PRODUCTS
# ============================================================

st.subheader("Top 10 Products by Revenue")

top_products_query = """
SELECT
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM analytics.fact_order_items oi

JOIN analytics.dim_products p
    ON oi.product_id = p.product_id

JOIN analytics.fact_orders o
    ON oi.order_id = o.order_id

WHERE LOWER(o.status) <> 'cancelled'

GROUP BY
    p.product_id,
    p.product_name,
    p.category

ORDER BY revenue DESC

LIMIT 10;
"""

top_products_df = load_query(top_products_query)

top_products_df["revenue"] = top_products_df["revenue"].apply(
    lambda x: f"₹{x:,.2f}"
)

st.dataframe(
    top_products_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# CATEGORY PERFORMANCE TABLE
# ============================================================

st.subheader("Category Performance")

display_category = category_df.copy()

if not display_category.empty:

    display_category["revenue"] = display_category[
        "revenue"
    ].apply(
        lambda x: f"₹{x:,.2f}"
    )

    st.dataframe(
        display_category,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info("No category data available.")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "E-Commerce ETL Pipeline • "
    "Python | PySpark | PostgreSQL | Airflow | Streamlit"
)