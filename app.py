import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ─────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────
df = pd.read_csv('cleaned_data.csv')
rfm = pd.read_csv('rfm_data.csv')

df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Month'] = df['InvoiceDate'].dt.month
df['Year'] = df['InvoiceDate'].dt.year

# ─────────────────────────────────────────
# Sidebar Navigation
# ─────────────────────────────────────────
st.sidebar.title("🛍️ Shopper Spectrum Retail Analytics")
st.sidebar.markdown("---")
st.sidebar.markdown("Created by")
st.sidebar.markdown("### Priyadharsini S")
page = st.sidebar.radio(
    "Navigate to",
    ["📊 KPI Dashboard", "📈 EDA Visualizations", "🔍 Product Recommendation", "🎯 Customer Segmentation"]
)

# ═════════════════════════════════════════
# PAGE 1 — KPI Dashboard
# ═════════════════════════════════════════
if page == "📊 KPI Dashboard":
    st.title("📊 KPI Dashboard")
    st.markdown("Key business metrics at a glance.")
    st.markdown("---")

    # Calculate KPIs
    total_revenue     = df['TotalPrice'].sum()
    total_orders      = df['InvoiceNo'].nunique()
    total_customers   = df['CustomerID'].nunique()
    total_products    = df['Description'].nunique()
    avg_order_value   = df.groupby('InvoiceNo')['TotalPrice'].sum().mean()
    top_country       = df.groupby('Country')['TotalPrice'].sum().idxmax()
    top_product       = df.groupby('Description')['Quantity'].sum().idxmax()
    high_value_count  = (rfm['Segment'] == 'High Value').sum()

    # Row 1
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue",    f"£{total_revenue:,.0f}")
    col2.metric("🧾 Total Orders",     f"{total_orders:,}")
    col3.metric("👥 Total Customers",  f"{total_customers:,}")
    col4.metric("📦 Total Products",   f"{total_products:,}")

    st.markdown("")

    # Row 2
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("🛒 Avg Order Value",  f"£{avg_order_value:,.2f}")
    col6.metric("🌍 Top Country",      top_country)
    col7.metric("⭐ Top Product",      top_product[:30] + "...")
    col8.metric("🏆 High Value Customers", f"{high_value_count:,}")

    st.markdown("---")

    # Segment summary table
    st.subheader("Customer Segment Summary")
    segment_summary = rfm.groupby('Segment').agg(
        Customers=('CustomerID', 'count'),
        Avg_Recency=('recency', 'mean'),
        Avg_Frequency=('frequency', 'mean'),
        Avg_Monetary=('monetary', 'mean')
    ).round(2).reset_index()
    st.dataframe(segment_summary, use_container_width=True)

# ═════════════════════════════════════════
# PAGE 2 — EDA Visualizations
# ═════════════════════════════════════════
elif page == "📈 EDA Visualizations":
    st.title("📈 EDA Visualizations")
    st.markdown("Explore sales trends and patterns.")
    st.markdown("---")

    # Chart selector
    chart = st.selectbox("Select Chart", [
        "Top 10 Selling Products",
        "Country-wise Revenue",
        "Monthly Sales Trend",
        "Customer Segment Distribution",
        "Revenue by Year",
        "Most Active Customers",
        "Customer Monetary Spend"
    ])

    # ── Chart 1
    if chart == "Top 10 Selling Products":
        st.subheader("📦 Top 10 Selling Products")
        top_products = (df.groupby('Description')['Quantity']
                        .sum().sort_values(ascending=False).head(10))
        fig, ax = plt.subplots(figsize=(10, 6))
        top_products.plot(kind='barh', ax=ax, color='steelblue')
        ax.set_xlabel("Total Quantity Sold")
        ax.set_title("Top 10 Best Selling Products")
        ax.invert_yaxis()
        st.pyplot(fig)
        st.dataframe(top_products.reset_index())

    # ── Chart 2
    elif chart == "Country-wise Revenue":
        st.subheader("🌍 Top 10 Countries by Revenue")
        country_sales = (df.groupby('Country')['TotalPrice']
                         .sum().sort_values(ascending=False).head(10))
        fig, ax = plt.subplots(figsize=(10, 6))
        country_sales.plot(kind='bar', ax=ax, color='coral')
        ax.set_ylabel("Total Revenue (£)")
        ax.set_title("Top 10 Countries by Revenue")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        st.dataframe(country_sales.reset_index())

    # ── Chart 3
    elif chart == "Monthly Sales Trend":
        st.subheader("📈 Monthly Sales Trend")
        monthly = (df.groupby(['Year', 'Month'])['TotalPrice']
                   .sum().reset_index())
        monthly['Period'] = (monthly['Year'].astype(str) + '-'
                             + monthly['Month'].astype(str).str.zfill(2))
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(monthly['Period'], monthly['TotalPrice'],
                marker='o', color='green', linewidth=2)
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue (£)")
        ax.set_title("Monthly Revenue Trend")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        st.dataframe(monthly[['Period', 'TotalPrice']])

    # ── Chart 4
    elif chart == "Customer Segment Distribution":
        st.subheader("👥 Customer Segment Distribution")
        segment_counts = rfm['Segment'].value_counts()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        colors = ['gold', 'lightblue', 'lightgreen', 'salmon']
        ax1.pie(segment_counts, labels=segment_counts.index,
                autopct='%1.1f%%', colors=colors)
        ax1.set_title("Segment Share (Pie)")
        segment_counts.plot(kind='bar', ax=ax2, color=colors)
        ax2.set_title("Segment Count (Bar)")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        st.dataframe(segment_counts.reset_index())

    # ── Chart 5
    elif chart == "Revenue by Year":
        st.subheader("📅 Revenue by Year")
        yearly = df.groupby('Year')['TotalPrice'].sum()
        fig, ax = plt.subplots(figsize=(8, 5))
        yearly.plot(kind='bar', ax=ax, color='mediumpurple')
        ax.set_ylabel("Revenue (£)")
        ax.set_title("Yearly Revenue")
        ax.tick_params(axis='x', rotation=0)
        st.pyplot(fig)
        st.dataframe(yearly.reset_index())

    # ── Chart 6
    elif chart == "Most Active Customers":
        st.subheader("🏃 Top 10 Most Active Customers")
        active = (df.groupby('CustomerID')['InvoiceNo']
                  .nunique().sort_values(ascending=False).head(10))
        fig, ax = plt.subplots(figsize=(10, 6))
        active.plot(kind='bar', ax=ax, color='darkorange')
        ax.set_ylabel("Number of Orders")
        ax.set_title("Top 10 Most Active Customers")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        st.dataframe(active.reset_index())
    elif chart == "Customer Monetary Spend":
        st.subheader("💰 Customer Monetary Spend Analysis")

        customer_spend = (df.groupby('CustomerID')['TotalPrice']
                          .sum()
                          .reset_index()
                          .rename(columns={'TotalPrice': 'TotalSpend'}))
         # ── Chart 1: Top 10 highest spending customers
        st.markdown("#### 🏆 Top 10 Highest Spending Customers")
        top_spenders = customer_spend.sort_values('TotalSpend', ascending=False).head(10)
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.bar(top_spenders['CustomerID'].astype(str),
                top_spenders['TotalSpend'], color='steelblue')
        ax1.set_xlabel("Customer ID")
        ax1.set_ylabel("Total Spent (£)")
        ax1.set_title("Top 10 Highest Spending Customers")
        ax1.tick_params(axis='x', rotation=45)
        st.pyplot(fig1)
        # ── Chart 2: Spend distribution histogram
        st.markdown("#### 📊 Spend Distribution Across All Customers")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.hist(customer_spend['TotalSpend'], bins=50,
                 color='coral', edgecolor='white')
        ax2.set_xlabel("Total Spend (£)")
        ax2.set_ylabel("Number of Customers")
        ax2.set_title("How Much Do Customers Typically Spend?")
        ax2.axvline(customer_spend['TotalSpend'].mean(),
                    color='red', linestyle='--', label=f"Average: £{customer_spend['TotalSpend'].mean():,.0f}")
        ax2.legend()
        st.pyplot(fig2)
        # ── Chart 3: Average spend by segment
        st.markdown("#### 🎯 Average Spend by Customer Segment")
        segment_spend = rfm.groupby('Segment')['monetary'].mean().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        segment_spend.plot(kind='bar', ax=ax3,
                           color=['gold', 'lightblue', 'lightgreen', 'salmon'])
        ax3.set_ylabel("Average Spend (£)")
        ax3.set_title("Average Monetary Value by Segment")
        ax3.tick_params(axis='x', rotation=45)
        st.pyplot(fig3)

        # ── Summary metrics
        st.markdown("---")
        st.markdown("#### 📌 Spend Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Total Revenue",   f"£{customer_spend['TotalSpend'].sum():,.0f}")
        c2.metric("📊 Avg Spend",       f"£{customer_spend['TotalSpend'].mean():,.0f}")
        c3.metric("⬆️ Highest Spender", f"£{customer_spend['TotalSpend'].max():,.0f}")
        c4.metric("⬇️ Lowest Spender",  f"£{customer_spend['TotalSpend'].min():,.0f}")
# ── Data table
        st.markdown("#### 📋 Top 20 Customers by Spend")
        st.dataframe(
            top_spenders.head(20).reset_index(drop=True),
            use_container_width=True
        )
# ═════════════════════════════════════════
# PAGE 3 — Product Recommendation
# ═════════════════════════════════════════
elif page == "🔍 Product Recommendation":
    st.title("🔍 Product Recommendation")
    st.markdown("Select a product to see what other customers bought together.")
    st.markdown("---")

    product_list = df['Description'].dropna().unique()
    selected_product = st.selectbox("Select a Product", sorted(product_list))

    if st.button("Get Recommendations"):
        invoices = df[df['Description'] == selected_product]['InvoiceNo'].unique()
        related = df[df['InvoiceNo'].isin(invoices)]
        recommendations = (
            related[related['Description'] != selected_product]
            .groupby('Description')['Quantity']
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        st.subheader(f"Customers who bought '{selected_product}' also bought:")
        for i, (product, qty) in enumerate(recommendations.items(), 1):
            st.write(f"**{i}.** {product}")

        # Bar chart of recommendations
        fig, ax = plt.subplots(figsize=(10, 4))
        recommendations.plot(kind='barh', ax=ax, color='teal')
        ax.set_xlabel("Times Bought Together")
        ax.set_title("Recommended Products")
        ax.invert_yaxis()
        st.pyplot(fig)

# ═════════════════════════════════════════
# PAGE 4 — Customer Segmentation
# ═════════════════════════════════════════
elif page == "🎯 Customer Segmentation":
    st.title("🎯 Customer Segmentation")
    st.markdown("Enter customer details to find their RFM segment.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        recency = st.number_input("📅 Recency\n(days since last purchase)", min_value=0, value=30)
    with col2:
        frequency = st.number_input("🔁 Frequency\n(number of orders)", min_value=1, value=5)
    with col3:
        monetary = st.number_input("💰 Monetary\n(total spent £)", min_value=0.0, value=500.0)

    if st.button("Find My Segment", use_container_width=True):

        # R Score
        if recency <= rfm['recency'].quantile(0.25):
            r_score = 4
        elif recency <= rfm['recency'].quantile(0.50):
            r_score = 3
        elif recency <= rfm['recency'].quantile(0.75):
            r_score = 2
        else:
            r_score = 1

        # F Score
        if frequency <= rfm['frequency'].quantile(0.25):
            f_score = 1
        elif frequency <= rfm['frequency'].quantile(0.50):
            f_score = 2
        elif frequency <= rfm['frequency'].quantile(0.75):
            f_score = 3
        else:
            f_score = 4

        # M Score
        if monetary <= rfm['monetary'].quantile(0.25):
            m_score = 1
        elif monetary <= rfm['monetary'].quantile(0.50):
            m_score = 2
        elif monetary <= rfm['monetary'].quantile(0.75):
            m_score = 3
        else:
            m_score = 4

        total_score = r_score + f_score + m_score

        if total_score >= 10:
            segment = "🏆 High Value"
            color = "green"
        elif total_score >= 7:
            segment = "✅ Medium Value"
            color = "blue"
        elif total_score >= 4:
            segment = "⚠️ Low Value"
            color = "orange"
        else:
            segment = "🔴 At Risk"
            color = "red"

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("R Score", r_score, help="Recency score (1-4)")
        c2.metric("F Score", f_score, help="Frequency score (1-4)")
        c3.metric("M Score", m_score, help="Monetary score (1-4)")
        c4.metric("RFM Total", total_score)

        st.markdown("---")
        st.success(f"### Customer Segment: {segment}")

        # RFM gauge bar
        fig, ax = plt.subplots(figsize=(8, 2))
        ax.barh(['RFM Score'], [total_score], color=color, height=0.4)
        ax.barh(['RFM Score'], [12], color='lightgrey', height=0.4, zorder=0)
        ax.set_xlim(0, 12)
        ax.set_xlabel("Score (max 12)")
        ax.set_title(f"RFM Score: {total_score}/12")
        st.pyplot(fig)