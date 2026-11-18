import os
import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================================================
# 3. DATABASE CONFIGURATION (Secure)
# ==================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),       # Loaded safely from .env
    "database": os.getenv("DB_NAME", "crm_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}
# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Enterprise CRM Admin Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2. CUSTOM CSS DESIGN
# ==================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
    }
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }
    .main-title {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 2px;
    }
    .main-description {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
    }
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 40px;
    }
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 24px;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Form Input Borders & Focus Bold Styling */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        background-color: #FAFAFA !important;
        transition: all 0.2s ease-in-out;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: #0284C7 !important;
        font-weight: 600 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.15) !important;
    }
    
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)




# ==================================================
# 4. DATABASE CONNECTION & INITIALIZATION
# ==================================================

def init_db():
    """Ensure database and table exist."""
    try:
        temp_config = DB_CONFIG.copy()
        db_name = temp_config.pop("database")
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.close()
        conn.close()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                gender VARCHAR(20),
                age INT,
                city VARCHAR(50),
                state VARCHAR(50),
                address VARCHAR(255),
                company VARCHAR(100),
                job_title VARCHAR(100),
                product VARCHAR(100) NOT NULL,
                product_category VARCHAR(50),
                purchase_amount DECIMAL(10, 2) DEFAULT 0.00,
                customer_status VARCHAR(20) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        st.error(f"Database Initialization Error: {e}")

init_db()

def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        raise RuntimeError(f"MySQL Connection Error: {e}")
    raise RuntimeError("Unable to connect to MySQL database.")

# ==================================================
# 5. DATABASE HELPER FUNCTIONS
# ==================================================

def get_customers():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM customers ORDER BY id DESC"
        cursor.execute(query)
        records = cursor.fetchall()
        return pd.DataFrame(records)
    except (Error, RuntimeError) as e:
        st.error(str(e))
        return pd.DataFrame()
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

def get_customer_by_id(customer_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM customers WHERE id = %s"
        cursor.execute(query, (customer_id,))
        return cursor.fetchone()
    except (Error, RuntimeError) as e:
        st.error(str(e))
        return None
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

def add_customer(data):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO customers
            (name, email, phone, gender, age, city, state, address, company, job_title, product, product_category, purchase_amount, customer_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, data)
        connection.commit()
        return True, "Customer added successfully."
    except (Error, RuntimeError) as e:
        if connection and connection.is_connected(): connection.rollback()
        return False, str(e)
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

def update_customer(customer_id, data):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            UPDATE customers SET
                name = %s, email = %s, phone = %s, gender = %s, age = %s,
                city = %s, state = %s, address = %s, company = %s, job_title = %s,
                product = %s, product_category = %s, purchase_amount = %s, customer_status = %s
            WHERE id = %s
        """
        values = data + (customer_id,)
        cursor.execute(query, values)
        connection.commit()
        if cursor.rowcount == 0:
            return False, "No changes made or customer not found."
        return True, "Customer updated successfully."
    except (Error, RuntimeError) as e:
        if connection and connection.is_connected(): connection.rollback()
        return False, str(e)
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

def delete_customer(customer_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "DELETE FROM customers WHERE id = %s"
        cursor.execute(query, (customer_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Customer not found."
        return True, "Customer deleted successfully."
    except (Error, RuntimeError) as e:
        if connection and connection.is_connected(): connection.rollback()
        return False, str(e)
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

# ==================================================
# 6. COMMON PAGE HEADER & FORM
# ==================================================

def page_header(title, description):
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-description">{description}</div>', unsafe_allow_html=True)

def customer_form(customer=None, form_key="customer_form"):
    if customer is None: customer = {}
    with st.form(form_key):
        st.subheader("👤 Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer Name *", value=customer.get("name") or "")
            email = st.text_input("Email Address *", value=customer.get("email") or "")
            phone = st.text_input("Phone Number *", value=customer.get("phone") or "")
            gender_options = ["Male", "Female", "Other"]
            current_gender = customer.get("gender")
            gender_index = gender_options.index(current_gender) if current_gender in gender_options else 0
            gender = st.selectbox("Gender", gender_options, index=gender_index)
        with col2:
            age = st.number_input("Age", min_value=0, max_value=120, value=int(customer.get("age") or 18))
            city = st.text_input("City", value=customer.get("city") or "")
            state = st.text_input("State", value=customer.get("state") or "")
            address = st.text_input("Address", value=customer.get("address") or "")

        st.divider()
        st.subheader("🏢 Professional & Product Information")
        col3, col4 = st.columns(2)
        with col3:
            company = st.text_input("Company", value=customer.get("company") or "")
            job_title = st.text_input("Job Title", value=customer.get("job_title") or "")
        with col4:
            product = st.text_input("Product *", value=customer.get("product") or "")
            categories = ["Electronics", "Accessories", "Office Equipment", "Software", "Other"]
            current_cat = customer.get("product_category")
            cat_index = categories.index(current_cat) if current_cat in categories else 0
            category = st.selectbox("Product Category", categories, index=cat_index)

        st.divider()
        st.subheader("💰 Purchase & Status")
        col5, col6 = st.columns(2)
        with col5:
            purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, value=float(customer.get("purchase_amount") or 0), step=500.0)
        with col6:
            status_options = ["Active", "Inactive", "Potential"]
            current_status = customer.get("customer_status")
            status_index = status_options.index(current_status) if current_status in status_options else 0
            customer_status = st.selectbox("Customer Status", status_options, index=status_index)

        st.caption("* Required fields")
        submitted = st.form_submit_button("💾 Save Customer Record", use_container_width=True)

    data = (
        name.strip(), email.strip(), phone.strip(), gender,
        int(age) if age > 0 else None, city.strip(), state.strip(), address.strip(),
        company.strip(), job_title.strip(), product.strip(), category,
        float(purchase_amount), customer_status
    )
    return submitted, data

# ==================================================
# 7. SIDEBAR NAVIGATION
# ==================================================

st.sidebar.markdown("""
    <div style="padding: 10px 0px 15px 0px;">
        <div style="font-size: 22px; font-weight: 700; color: #FFFFFF;">⚡ CRM ADMIN</div>
        <div style="font-size: 11px; color: #94A3B8;">Enterprise Operations</div>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "NAVIGATION",
    ["Dashboard", "Add Customer", "View Customers", "Search Customer", "Update Customer", "Delete Customer"]
)

st.sidebar.divider()
st.sidebar.caption("CRM Admin Dashboard | v2.0")

# ==================================================
# 8. DASHBOARD
# ==================================================

if menu == "Dashboard":
    page_header("Dashboard Overview", "Real-time metrics and customer activity summary.")
    df = get_customers()

    if not df.empty:
        total_customers = len(df)
        active_customers = (df["customer_status"] == "Active").sum()
        inactive_customers = (df["customer_status"] == "Inactive").sum()
        potential_customers = (df["customer_status"] == "Potential").sum()
        total_sales = df["purchase_amount"].fillna(0).sum()
        total_products = df["product"].nunique()
    else:
        total_customers = active_customers = inactive_customers = potential_customers = total_sales = total_products = 0

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-card"><div class="metric-label">Total Customers</div><div class="metric-value">{total_customers}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div class="metric-label">Active Customers</div><div class="metric-value">{active_customers}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><div class="metric-label">Total Revenue</div><div class="metric-value">₹{total_sales:,.2f}</div></div>', unsafe_allow_html=True)

    st.write("")
    c4, c5, c6 = st.columns(3)
    c4.markdown(f'<div class="metric-card"><div class="metric-label">Inactive Customers</div><div class="metric-value">{inactive_customers}</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="metric-card"><div class="metric-label">Potential Leads</div><div class="metric-value">{potential_customers}</div></div>', unsafe_allow_html=True)
    c6.markdown(f'<div class="metric-card"><div class="metric-label">Unique Products</div><div class="metric-value">{total_products}</div></div>', unsafe_allow_html=True)

    st.write("")
    if not df.empty:
        ch1, ch2 = st.columns(2)
        with ch1:
            st.subheader("Customer Status Breakdown")
            st.bar_chart(df["customer_status"].value_counts())
        with ch2:
            st.subheader("Top Product Demand")
            st.bar_chart(df["product"].value_counts().head(5))

        st.subheader("Recent Customer Activity")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    else:
        st.info("No records found in the database yet. Add some customers to see analytics.")

# ==================================================
# 9. ADD CUSTOMER
# ==================================================

elif menu == "Add Customer":
    page_header("Add New Customer", "Register a new client profile into the system.")
    submitted, data = customer_form(form_key="add_customer_form")

    if submitted:
        if not data[0] or not data[1] or not data[2] or not data[10]:
            st.warning("Please fill in all mandatory fields (*).")
        elif "@" not in data[1] or "." not in data[1]:
            st.warning("Please provide a valid email address.")
        elif len(data[2]) < 7:
            st.warning("Please provide a valid phone number.")
        else:
            success, message = add_customer(data)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

# ==================================================
# 10. VIEW CUSTOMERS
# ==================================================

elif menu == "View Customers":
    page_header("Customer Directory", "Filter, inspect, and export customer database records.")
    df = get_customers()

    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1: search_text = st.text_input("🔍 Search Keyword")
        with col2: status_filter = st.selectbox("Status Filter", ["All", "Active", "Inactive", "Potential"])
        with col3: product_filter = st.selectbox("Product Filter", ["All"] + sorted(df["product"].dropna().unique().tolist()))

        filtered = df.copy()
        if search_text:
            mask = filtered.astype(str).apply(lambda col: col.str.contains(search_text, case=False, na=False)).any(axis=1)
            filtered = filtered[mask]
        if status_filter != "All":
            filtered = filtered[filtered["customer_status"] == status_filter]
        if product_filter != "All":
            filtered = filtered[filtered["product"] == product_filter]

        st.write(f"Showing **{len(filtered)}** of **{len(df)}** total records")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

        st.download_button(
            "📥 Export Filtered Data as CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="crm_filtered_customers.csv",
            mime="text/csv"
        )
    else:
        st.info("No records available.")

# ==================================================
# 11. SEARCH CUSTOMER
# ==================================================

elif menu == "Search Customer":
    page_header("Lookup Customer", "Retrieve specific profile details via Customer ID.")
    cid = st.number_input("Customer ID", min_value=1, step=1)
    if st.button("Search"):
        customer = get_customer_by_id(int(cid))
        if customer:
            st.success("Customer record located.")
            col1, col2 = st.columns(2)
            with col1:
                for k in ["id", "name", "email", "phone", "gender", "age", "city", "state", "address"]:
                    st.write(f"**{k.replace('_', ' ').title()}:** {customer[k]}")
            with col2:
                for k in ["company", "job_title", "product", "product_category", "purchase_amount", "customer_status", "created_at", "updated_at"]:
                    val = f"₹{customer[k]:,.2f}" if k == "purchase_amount" else customer[k]
                    st.write(f"**{k.replace('_', ' ').title()}:** {val}")
        else:
            st.warning("Customer ID not found.")

# ==================================================
# 12. UPDATE CUSTOMER
# ==================================================

elif menu == "Update Customer":
    page_header("Update Customer Information", "Modify records for an existing client.")
    cid = st.number_input("Enter Customer ID to Edit", min_value=1, step=1)
    
    if st.button("Fetch Record"):
        cust = get_customer_by_id(int(cid))
        if cust:
            st.session_state["edit_cust"] = cust
        else:
            st.session_state.pop("edit_cust", None)
            st.warning("Customer not found.")

    if "edit_cust" in st.session_state:
        cust = st.session_state["edit_cust"]
        submitted, data = customer_form(customer=cust, form_key="update_form")
        if submitted:
            success, msg = update_customer(cust["id"], data)
            if success:
                st.success(msg)
                st.session_state.pop("edit_cust", None)
                st.rerun()
            else:
                st.error(msg)

# ==================================================
# 13. DELETE CUSTOMER
# ==================================================

elif menu == "Delete Customer":
    page_header("Delete Customer", "Permanently remove a customer entry.")
    cid = st.number_input("Enter Customer ID to Delete", min_value=1, step=1)

    if st.button("Lookup Record"):
        cust = get_customer_by_id(int(cid))
        if cust:
            st.session_state["del_cust"] = cust
        else:
            st.session_state.pop("del_cust", None)
            st.warning("Customer not found.")

    if "del_cust" in st.session_state:
        cust = st.session_state["del_cust"]
        st.warning(f"Preparing to delete **{cust['name']}** (ID: {cust['id']}). This action is irreversible.")
        confirm = st.checkbox("I confirm that I want to delete this record.")
        if st.button("Confirm Deletion", type="primary"):
            if confirm:
                success, msg = delete_customer(cust["id"])
                if success:
                    st.success(msg)
                    st.session_state.pop("del_cust", None)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Please check the confirmation box.")