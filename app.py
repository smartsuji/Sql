# =========================================================
# REAL ESTATE STREAMLIT DASHBOARD
# SAVE FILE AS: app.py
# RUN: streamlit run app.py
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

# =========================================================
# MYSQL CONNECTION
# =========================================================

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Royal@26",
    database="real_estate_db"
)

cursor = conn.cursor()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Real Estate Dashboard",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    listings = pd.read_sql("SELECT * FROM listings", conn)
    agents = pd.read_sql("SELECT * FROM agents", conn)
    property_attributes = pd.read_sql("SELECT * FROM property_attributes", conn)
    sales_data = pd.read_sql("SELECT * FROM sales_data", conn)
    buyers = pd.read_sql("SELECT * FROM buyers", conn)

    # -------------------------------------
    # STANDARDIZE COLUMNS
    # -------------------------------------

    dfs = [
        listings,
        agents,
        property_attributes,
        sales_data,
        buyers
    ]

    for df in dfs:
        df.columns = (
            df.columns
            .str.lower()
            .str.strip()
            .str.replace(" ", "_")
        )

    # -------------------------------------
    # MERGE TABLES
    # -------------------------------------

    merged = listings.merge(
        property_attributes,
        on="listing_id",
        how="left"
    )

    merged = merged.merge(
        sales_data,
        on="listing_id",
        how="left"
    )

    merged = merged.merge(
        buyers,
        left_on="listing_id",
        right_on="sale_id",
        how="left"
    )

    merged = merged.merge(
        agents,
        on="agent_id",
        how="left"
    )

    # -------------------------------------
    # DATE FORMAT
    # -------------------------------------

    if "date_listed" in merged.columns:
        merged["date_listed"] = pd.to_datetime(
            merged["date_listed"],
            errors="coerce"
        )

    if "date_sold" in merged.columns:
        merged["date_sold"] = pd.to_datetime(
            merged["date_sold"],
            errors="coerce"
        )

    return merged


df = load_data()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏠 Real Estate Dashboard")

page = st.sidebar.selectbox(
    "Select Page",
    [
        "Filters",
        "Visualizations",
        "CRUD Operations",
        "SQL Queries"
    ]
)

# =========================================================
# FILTER PAGE
# =========================================================

if page == "Filters":

    st.title("🎛️ Filters Dashboard")

    # -------------------------------------
    # FILTERS
    # -------------------------------------

    city = st.sidebar.multiselect(
        "Select City",
        df["city"].dropna().unique()
    )

    property_type = st.sidebar.selectbox(
        "Property Type",
        ["All"] + list(df["property_type"].dropna().unique())
    )

    agent = st.sidebar.selectbox(
        "Agent",
        ["All"] + list(df["agent_id"].dropna().unique())
    )

    # -------------------------------------
    # PRICE RANGE
    # -------------------------------------

    min_price = int(df["price"].min())
    max_price = int(df["price"].max())

    price_range = st.sidebar.slider(
        "Price Range",
        min_price,
        max_price,
        (min_price, max_price)
    )

    # -------------------------------------
    # DATE RANGE
    # -------------------------------------

    if "date_listed" in df.columns:

        min_date = df["date_listed"].min()
        max_date = df["date_listed"].max()

        date_range = st.sidebar.date_input(
            "Date Range",
            [min_date, max_date]
        )

    # -------------------------------------
    # APPLY FILTERS
    # -------------------------------------

    filtered = df.copy()

    if city:
        filtered = filtered[
            filtered["city"].isin(city)
        ]

    if property_type != "All":
        filtered = filtered[
            filtered["property_type"] == property_type
        ]

    if agent != "All":
        filtered = filtered[
            filtered["agent_id"] == agent
        ]

    filtered = filtered[
        (filtered["price"] >= price_range[0]) &
        (filtered["price"] <= price_range[1])
    ]

    st.dataframe(
        filtered,
        use_container_width=True
    )

# =========================================================
# VISUALIZATION PAGE
# =========================================================

elif page == "Visualizations":

    st.title("📈 Visualizations Dashboard")

    # -------------------------------------
    # MAP
    # -------------------------------------

    st.subheader("🗺️ Property Locations")

    map_df = df.dropna(
        subset=["latitude", "longitude"]
    )

    st.map(map_df[["latitude", "longitude"]])

    # -------------------------------------
    # BAR CHART
    # -------------------------------------

    st.subheader("🏙️ Average Prices by City")

    city_price = (
        df.groupby("city")["price"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        city_price,
        x="city",
        y="price"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -------------------------------------
    # PIE CHART
    # -------------------------------------

    st.subheader("🏠 Property Type Distribution")

    property_count = (
        df["property_type"]
        .value_counts()
        .reset_index()
    )

    property_count.columns = [
        "property_type",
        "count"
    ]

    fig = px.pie(
        property_count,
        names="property_type",
        values="count"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -------------------------------------
    # LINE CHART
    # -------------------------------------

    st.subheader("📅 Monthly Listings Trend")

    trend = (
        df.groupby(
            df["date_listed"].dt.to_period("M")
        )
        .size()
        .reset_index(name="count")
    )

    trend["date_listed"] = trend["date_listed"].astype(str)

    fig = px.line(
        trend,
        x="date_listed",
        y="count"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# CRUD OPERATIONS
# =========================================================

elif page == "CRUD Operations":

    st.title("🛠️ CRUD Operations")

    table_name = st.selectbox(
        "Select Table",
        [
            "agents",
            "listings",
            "sales_data",
            "buyers",
            "property_attributes"
        ]
    )

    # -------------------------------------
    # VIEW RECORDS
    # -------------------------------------

    st.subheader("📄 View Records")

    view_df = pd.read_sql(
        f"SELECT * FROM {table_name}",
        conn
    )

    st.dataframe(
        view_df,
        use_container_width=True
    )

    # =====================================================
    # LISTINGS CRUD
    # =====================================================

    if table_name == "listings":

        st.subheader("➕ Add Listing")

        listing_id = st.text_input("Listing ID")
        city = st.text_input("City")
        property_type = st.text_input("Property Type")
        price = st.number_input("Price")
        sqft = st.number_input("Sqft")
        agent_id = st.text_input("Agent ID")

        if st.button("Add Listing"):

            query = """
            INSERT INTO listings
            (
                listing_id,
                city,
                property_type,
                price,
                sqft,
                agent_id
            )

            VALUES (%s,%s,%s,%s,%s,%s)
            """

            values = (
                listing_id,
                city,
                property_type,
                price,
                sqft,
                agent_id
            )

            cursor.execute(query, values)

            conn.commit()

            st.success("✅ Listing Added")

        # ---------------------------------

        st.subheader("✏️ Update Listing Price")

        update_id = st.text_input(
            "Listing ID to Update"
        )

        new_price = st.number_input(
            "New Price"
        )

        if st.button("Update Price"):

            query = """
            UPDATE listings
            SET price=%s
            WHERE listing_id=%s
            """

            cursor.execute(
                query,
                (new_price, update_id)
            )

            conn.commit()

            st.success("✅ Updated Successfully")

        # ---------------------------------

        st.subheader("❌ Delete Listing")

        delete_id = st.text_input(
            "Listing ID to Delete"
        )

        if st.button("Delete Listing"):

            query = """
            DELETE FROM listings
            WHERE listing_id=%s
            """

            cursor.execute(
                query,
                (delete_id,)
            )

            conn.commit()

            st.success("✅ Deleted Successfully")
            
    # =====================================================
    # AGENTS CRUD
    # =====================================================

    elif table_name == "agents":

        # ---------------- ADD ----------------

        st.subheader("➕ Add Agent")

        agent_id = st.text_input("Agent ID")
        name = st.text_input("Agent Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        if st.button("Add Agent"):

            query = """
            INSERT INTO agents
            (
                agent_id,
                name,
                phone,
                email
            )
            VALUES (%s,%s,%s,%s)
            """

            values = (
                agent_id,
                name,
                phone,
                email
            )

            cursor.execute(query, values)
            conn.commit()

            st.success("✅ Agent Added")

        # ---------------- UPDATE ----------------

        st.subheader("✏️ Update Agent Phone")

        update_id = st.text_input("Agent ID to Update")

        new_phone = st.text_input("New Phone")

        if st.button("Update Agent"):

            query = """
            UPDATE agents
            SET phone=%s
            WHERE agent_id=%s
            """

            cursor.execute(query, (new_phone, update_id))
            conn.commit()

            st.success("✅ Agent Updated")

        # ---------------- DELETE ----------------

        st.subheader("❌ Delete Agent")

        delete_id = st.text_input("Agent ID to Delete")

        if st.button("Delete Agent"):

            query = """
            DELETE FROM agents
            WHERE agent_id=%s
            """

            cursor.execute(query, (delete_id,))
            conn.commit()

            st.success("✅ Agent Deleted")

    # =====================================================
    # BUYERS CRUD
    # =====================================================

    elif table_name == "buyers":

        # ---------------- ADD ----------------

        st.subheader("➕ Add Buyer")

        buyer_id = st.number_input("Buyer ID", step=1)
        sale_id = st.text_input("Sale ID")
        buyer_type = st.text_input("Buyer Type")
        payment_mode = st.text_input("Payment Mode")
        loan_taken = st.selectbox("Loan Taken", [True, False])
        loan_provider = st.text_input("Loan Provider")
        loan_amount = st.number_input("Loan Amount")

        if st.button("Add Buyer"):

            query = """
            INSERT INTO buyers
            (
                buyer_id,
                sale_id,
                buyer_type,
                payment_mode,
                loan_taken,
                loan_provider,
                loan_amount
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """

            values = (
                buyer_id,
                sale_id,
                buyer_type,
                payment_mode,
                loan_taken,
                loan_provider,
                loan_amount
            )

            cursor.execute(query, values)
            conn.commit()

            st.success("✅ Buyer Added")

        # ---------------- UPDATE ----------------

        st.subheader("✏️ Update Loan Amount")

        update_buyer = st.number_input(
            "Buyer ID to Update",
            step=1
        )

        new_loan = st.number_input(
            "New Loan Amount"
        )

        if st.button("Update Buyer"):

            query = """
            UPDATE buyers
            SET loan_amount=%s
            WHERE buyer_id=%s
            """

            cursor.execute(
                query,
                (new_loan, update_buyer)
            )

            conn.commit()

            st.success("✅ Buyer Updated")

        # ---------------- DELETE ----------------

        st.subheader("❌ Delete Buyer")

        delete_buyer = st.number_input(
            "Buyer ID to Delete",
            step=1
        )

        if st.button("Delete Buyer"):

            query = """
            DELETE FROM buyers
            WHERE buyer_id=%s
            """

            cursor.execute(
                query,
                (delete_buyer,)
            )

            conn.commit()

            st.success("✅ Buyer Deleted")

    # =====================================================
    # PROPERTY ATTRIBUTES CRUD
    # =====================================================

    elif table_name == "property_attributes":

        # ---------------- ADD ----------------

        st.subheader("➕ Add Property Attribute")

        attribute_id = st.number_input(
            "Attribute ID",
            step=1
        )

        listing_id = st.text_input("Listing ID")

        bedrooms = st.number_input("Bedrooms", step=1)

        bathrooms = st.number_input("Bathrooms", step=1)

        furnishing_status = st.text_input(
            "Furnishing Status"
        )

        parking_available = st.selectbox(
            "Parking Available",
            [True, False]
        )

        if st.button("Add Property Attribute"):

            query = """
            INSERT INTO property_attributes
            (
                attribute_id,
                listing_id,
                bedrooms,
                bathrooms,
                furnishing_status,
                parking_available
            )
            VALUES (%s,%s,%s,%s,%s,%s)
            """

            values = (
                attribute_id,
                listing_id,
                bedrooms,
                bathrooms,
                furnishing_status,
                parking_available
            )

            cursor.execute(query, values)
            conn.commit()

            st.success("✅ Property Attribute Added")

        # ---------------- UPDATE ----------------

        st.subheader("✏️ Update Bedrooms")

        update_attr = st.number_input(
            "Attribute ID to Update",
            step=1
        )

        new_bed = st.number_input(
            "New Bedrooms",
            step=1
        )

        if st.button("Update Property"):

            query = """
            UPDATE property_attributes
            SET bedrooms=%s
            WHERE attribute_id=%s
            """

            cursor.execute(
                query,
                (new_bed, update_attr)
            )

            conn.commit()

            st.success("✅ Updated Successfully")

        # ---------------- DELETE ----------------

        st.subheader("❌ Delete Property Attribute")

        delete_attr = st.number_input(
            "Attribute ID to Delete",
            step=1
        )

        if st.button("Delete Property"):

            query = """
            DELETE FROM property_attributes
            WHERE attribute_id=%s
            """

            cursor.execute(
                query,
                (delete_attr,)
            )

            conn.commit()

            st.success("✅ Deleted Successfully")

    # =====================================================
    # SALES DATA CRUD
    # =====================================================

    elif table_name == "sales_data":

        # ---------------- ADD ----------------

        st.subheader("➕ Add Sales Data")

        listing_id = st.text_input("Listing ID")

        sale_price = st.number_input("Sale Price")

        date_sold = st.date_input("Date Sold")

        days_on_market = st.number_input(
            "Days on Market"
        )

        if st.button("Add Sale"):

            query = """
            INSERT INTO sales_data
            (
                listing_id,
                sale_price,
                date_sold,
                days_on_market
            )
            VALUES (%s,%s,%s,%s)
            """

            values = (
                listing_id,
                sale_price,
                date_sold,
                days_on_market
            )

            cursor.execute(query, values)
            conn.commit()

            st.success("✅ Sale Added")

        # ---------------- UPDATE ----------------

        st.subheader("✏️ Update Sale Price")

        update_sale = st.text_input(
            "Listing ID to Update"
        )

        new_sale_price = st.number_input(
            "New Sale Price"
        )

        if st.button("Update Sale"):

            query = """
            UPDATE sales_data
            SET sale_price=%s
            WHERE listing_id=%s
            """

            cursor.execute(
                query,
                (new_sale_price, update_sale)
            )

            conn.commit()

            st.success("✅ Sale Updated")

        # ---------------- DELETE ----------------

        st.subheader("❌ Delete Sale")

        delete_sale = st.text_input(
            "Listing ID to Delete"
        )

        if st.button("Delete Sale"):

            query = """
            DELETE FROM sales_data
            WHERE listing_id=%s
            """

            cursor.execute(
                query,
                (delete_sale,)
            )

            conn.commit()

            st.success("✅ Sales Data Deleted")

# =========================================================
# SQL QUERIES PAGE
# =========================================================

elif page == "SQL Queries":

    st.title("📊 SQL Query Dashboard")

    # =========================================================
# SQL QUERIES DICTIONARY FOR STREAMLIT
# =========================================================

queries = {

# =========================================================
# 📊 PROPERTY & PRICING ANALYSIS
# =========================================================

"1. Average Listing Price by City":
"""
SELECT
    city,
    ROUND(AVG(price),2) AS avg_listing_price
FROM listings
GROUP BY city
ORDER BY avg_listing_price DESC
""",

"2. Average Price per Sqft by Property Type":
"""
SELECT
    property_type,
    ROUND(AVG(price/sqft),2) AS avg_price_per_sqft
FROM listings
GROUP BY property_type
""",

"3. Furnishing Status Impact on Price":
"""
SELECT
    p.furnishing_status,
    ROUND(AVG(l.price),2) AS avg_price
FROM listings l
JOIN property_attributes p
ON l.listing_id = p.listing_id
GROUP BY p.furnishing_status
""",

"4. Metro Distance vs Property Price":
"""
SELECT
    ROUND(p.metro_distance_km,1) AS metro_distance,
    ROUND(AVG(l.price),2) AS avg_price
FROM listings l
JOIN property_attributes p
ON l.listing_id = p.listing_id
GROUP BY ROUND(p.metro_distance_km,1)
ORDER BY metro_distance
""",

"5. Rented vs Non-Rented Property Prices":
"""
SELECT
    p.is_rented,
    ROUND(AVG(l.price),2) AS avg_price
FROM listings l
JOIN property_attributes p
ON l.listing_id = p.listing_id
GROUP BY p.is_rented
""",

"6. Bedrooms & Bathrooms Effect on Pricing":
"""
SELECT
    p.bedrooms,
    p.bathrooms,
    ROUND(AVG(l.price),2) AS avg_price
FROM listings l
JOIN property_attributes p
ON l.listing_id = p.listing_id
GROUP BY p.bedrooms, p.bathrooms
ORDER BY avg_price DESC
""",

"7. Parking & Power Backup vs Price":
"""
SELECT
    p.parking_available,
    p.power_backup,
    ROUND(AVG(l.price),2) AS avg_price
FROM listings l
JOIN property_attributes p
ON l.listing_id = p.listing_id
GROUP BY p.parking_available, p.power_backup
""",

"8. Year Built Influence on Price":
"""
SELECT
    p.year_built,
    ROUND(AVG(l.price),2) AS avg_price
FROM listings l
JOIN property_attributes p
ON l.listing_id = p.listing_id
GROUP BY p.year_built
ORDER BY p.year_built
""",

"9. Cities with Highest Average Property Prices":
"""
SELECT
    city,
    ROUND(AVG(price),2) AS avg_price
FROM listings
GROUP BY city
ORDER BY avg_price DESC
LIMIT 10
""",

"10. Property Distribution Across Price Buckets":
"""
SELECT
    CASE
        WHEN price < 500000 THEN 'Low'
        WHEN price BETWEEN 500000 AND 1000000 THEN 'Medium'
        ELSE 'High'
    END AS price_bucket,

    COUNT(*) AS total_properties

FROM listings
GROUP BY price_bucket
""",

# =========================================================
# ⏱️ SALES & MARKET PERFORMANCE
# =========================================================

"11. Average Days on Market by City":
"""
SELECT
    l.city,
    ROUND(AVG(s.days_on_market),2) AS avg_days
FROM listings l
JOIN sales_data s
ON l.listing_id = s.listing_id
GROUP BY l.city
ORDER BY avg_days
""",

"12. Fastest Selling Property Types":
"""
SELECT
    l.property_type,
    ROUND(AVG(s.days_on_market),2) AS avg_days
FROM listings l
JOIN sales_data s
ON l.listing_id = s.listing_id
GROUP BY l.property_type
ORDER BY avg_days ASC
""",

"13. Percentage of Properties Sold Above Listing Price":
"""
SELECT
    ROUND(
        SUM(
            CASE
                WHEN s.sale_price > l.price THEN 1
                ELSE 0
            END
        ) * 100 / COUNT(*),
    2) AS percentage_above_listing
FROM listings l
JOIN sales_data s
ON l.listing_id = s.listing_id
""",

"14. Sale-to-List Price Ratio by City":
"""
SELECT
    l.city,
    ROUND(AVG(s.sale_price/l.price),2) AS sale_to_list_ratio
FROM listings l
JOIN sales_data s
ON l.listing_id = s.listing_id
GROUP BY l.city
""",

"15. Listings Taking More Than 90 Days to Sell":
"""
SELECT
    l.listing_id,
    l.city,
    s.days_on_market
FROM listings l
JOIN sales_data s
ON l.listing_id = s.listing_id
WHERE s.days_on_market > 90
ORDER BY s.days_on_market DESC
""",

"16. Metro Distance vs Time on Market":
"""
SELECT
    ROUND(p.metro_distance_km,1) AS metro_distance,
    ROUND(AVG(s.days_on_market),2) AS avg_days
FROM property_attributes p
JOIN sales_data s
ON p.listing_id = s.listing_id
GROUP BY ROUND(p.metro_distance_km,1)
ORDER BY metro_distance
""",

"17. Monthly Sales Trend":
"""
SELECT
    DATE_FORMAT(date_sold,'%Y-%m') AS month,
    COUNT(*) AS total_sales
FROM sales_data
GROUP BY month
ORDER BY month
""",

"18. Currently Unsold Properties":
"""
SELECT
    l.listing_id,
    l.city,
    l.property_type,
    l.price
FROM listings l
LEFT JOIN sales_data s
ON l.listing_id = s.listing_id
WHERE s.listing_id IS NULL
""",

# =========================================================
# 🧑‍💼 AGENT PERFORMANCE
# =========================================================

"19. Agents with Most Sales":
"""
SELECT
    l.agent_id,
    COUNT(*) AS total_sales
FROM listings l
JOIN sales_data s
ON l.listing_id = s.listing_id
GROUP BY l.agent_id
ORDER BY total_sales DESC
""",

"20. Top Agents by Sales Revenue":
"""
SELECT
    l.agent_id,
    ROUND(SUM(s.sale_price),2) AS total_revenue
FROM listings l
JOIN sales_data s
ON l.listing_id = s.listing_id
GROUP BY l.agent_id
ORDER BY total_revenue DESC
""",

"21. Agents Closing Deals Fastest":
"""
SELECT
    l.agent_id,
    ROUND(AVG(s.days_on_market),2) AS avg_closing_days
FROM listings l
JOIN sales_data s
ON l.listing_id = s.listing_id
GROUP BY l.agent_id
ORDER BY avg_closing_days
""",

"22. Experience vs Deals Closed":
"""
SELECT
    experience_years,
    AVG(deals_closed) AS avg_deals_closed
FROM agents_enhanced
GROUP BY experience_years
ORDER BY experience_years
""",

"23. Ratings vs Closing Speed":
"""
SELECT
    ae.rating,
    ROUND(AVG(s.days_on_market),2) AS avg_days
FROM agents_enhanced ae
JOIN listings l
ON ae.agent_id = l.agent_id
JOIN sales_data s
ON l.listing_id = s.listing_id
GROUP BY ae.rating
ORDER BY ae.rating DESC
""",

"24. Average Commission Earned by Agent":
"""
SELECT
    ae.agent_id,
    ROUND(
        AVG(
            s.sale_price * ae.commission_rate/100
        ),2
    ) AS avg_commission
FROM agents_enhanced ae
JOIN listings l
ON ae.agent_id = l.agent_id
JOIN sales_data s
ON l.listing_id = s.listing_id
GROUP BY ae.agent_id
ORDER BY avg_commission DESC
""",

"25. Agents with Most Active Listings":
"""
SELECT
    l.agent_id,
    COUNT(*) AS active_listings
FROM listings l
LEFT JOIN sales_data s
ON l.listing_id = s.listing_id
WHERE s.listing_id IS NULL
GROUP BY l.agent_id
ORDER BY active_listings DESC
""",

# =========================================================
# 🧍 BUYER & FINANCING BEHAVIOR
# =========================================================

"26. Investor vs End User Percentage":
"""
SELECT
    buyer_type,
    ROUND(COUNT(*)*100/
    (SELECT COUNT(*) FROM buyers),2)
    AS percentage
FROM buyers
GROUP BY buyer_type
""",

"27. Cities with Highest Loan Uptake":
"""
SELECT
    l.city,
    ROUND(AVG(b.loan_taken)*100,2)
    AS loan_uptake_percentage
FROM buyers b
JOIN listings l
ON b.sale_id = l.listing_id
GROUP BY l.city
ORDER BY loan_uptake_percentage DESC
""",

"28. Average Loan Amount by Buyer Type":
"""
SELECT
    buyer_type,
    ROUND(AVG(loan_amount),2)
    AS avg_loan_amount
FROM buyers
GROUP BY buyer_type
""",

"29. Most Common Payment Mode":
"""
SELECT
    payment_mode,
    COUNT(*) AS total_transactions
FROM buyers
GROUP BY payment_mode
ORDER BY total_transactions DESC
""",

"30. Loan-backed Purchases vs Closing Time":
"""
SELECT
    b.loan_taken,
    ROUND(AVG(s.days_on_market),2)
    AS avg_closing_days
FROM buyers b
JOIN sales_data s
ON b.sale_id = s.listing_id
GROUP BY b.loan_taken
"""
}

# =========================================================
# STREAMLIT DISPLAY
# =========================================================

st.title("📊 SQL Query Dashboard")

selected_query = st.selectbox(
    "Select SQL Query",
    list(queries.keys())
)

# SHOW QUERY
st.subheader("📝 SQL Query")

st.code(
    queries[selected_query],
    language="sql"
)

# EXECUTE QUERY
result = pd.read_sql(
    queries[selected_query],
    conn
)

# SHOW OUTPUT
st.subheader("📋 Query Output")

st.dataframe(
    result,
    use_container_width=True
)