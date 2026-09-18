import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime

from database import init_db, get_connection
from auth import register_user, login_user, update_user_profile
from utils import apply_custom_css, init_session, add_to_cart

st.set_page_config(
    page_title="Sweet Crumbs Bakery",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
init_session()
apply_custom_css()

# Navigation Sidebar
st.sidebar.markdown(
    "<h1 style='text-align: center; color: #5C3A21;'>🍰 Sweet Crumbs</h1>",
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<p style='text-align: center; font-size: 0.9rem;'>Artisanal Bakery & Confectionery</p>",
    unsafe_allow_html=True
)
st.sidebar.divider()

user = st.session_state.user
if user:
    st.sidebar.success(
        f"Logged in as: **{user['name']}** ({user['role'].capitalize()})"
    )
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.user = None
        st.rerun()
else:
    st.sidebar.info("👋 Welcome Guest! Login for personal order history.")

pages = [
    "🏠 Home",
    "🧁 Menu & Products",
    "🎂 Custom Cake Designer",
    "🛒 Shopping Cart",
    "⭐ Reviews & Ratings",
    "📞 Contact Us"
]

if user and user["role"] in ["customer", "admin"]:
    pages.insert(4, "👤 My Account")

if user and user["role"] == "admin":
    pages.append("👨‍💼 Admin Dashboard")

selected_page = st.sidebar.radio("Navigate Page", pages)


# -------------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------------
def fetch_products(
    category=None,
    search="",
    min_p=0,
    max_p=10000,
    sort_by="Default"
):
    conn = get_connection()

    query = """
        SELECT * FROM products
        WHERE price BETWEEN ? AND ?
    """
    params = [min_p, max_p]

    if category and category != "All Categories":
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if sort_by == "Price: Low to High":
        query += " ORDER BY price ASC"
    elif sort_by == "Price: High to Low":
        query += " ORDER BY price DESC"
    elif sort_by == "Popularity":
        query += " ORDER BY sales_count DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def render_product_grid(df):
    if df.empty:
        st.warning("No bakery items found matching your filter options.")
        return

    cols = st.columns(3)

    for idx, row in df.iterrows():
        with cols[idx % 3]:
            image_url = row.get("image_url", "")

            st.markdown(
                f"""
                <div class="product-card">
                    <img src="{image_url}"
                         style="width:100%; height:200px;
                                object-fit:cover; border-radius:12px;">
                    <h3 style="margin-top:10px; color:#5C3A21;">
                        {row['name']}
                    </h3>
                    <p style="font-size:0.85rem; color:#777;
                              height:40px; overflow:hidden;">
                        {row['description']}
                    </p>
                    <div style="display:flex;
                                justify-content:space-between;
                                align-items:center;
                                margin-top:10px;">
                        <span style="font-size:1.2rem;
                                     font-weight:bold;
                                     color:#D4A373;">
                            PKR {row['price']:,.0f}
                        </span>
                        <span style="font-size:0.8rem;
                                     color:{'green' if row['stock'] > 0 else 'red'};">
                            Stock: {row['stock']}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if row["stock"] > 0:
                if st.button(
                    "Add to Cart 🛒",
                    key=f"btn_prod_{row['id']}"
                ):
                    add_to_cart(
                        row["id"],
                        row["name"],
                        row["price"],
                        row["stock"]
                    )
                    st.success(f"{row['name']} added to cart!")
            else:
                st.button(
                    "Out of Stock ❌",
                    key=f"btn_prod_out_{row['id']}",
                    disabled=True
                )


# -------------------------------------------------------------------------
# PAGE 1: HOME
# -------------------------------------------------------------------------
if selected_page == "🏠 Home":
    st.markdown(
        """
        <div class="hero-box">
            <h1 class="main-header"
                style="font-size:2.8rem; margin-bottom:10px;">
                Freshly Baked, Made With Love ❤️
            </h1>
            <p style="font-size:1.1rem; color:#6C584C;
                      max-width:700px; margin:0 auto 20px auto;">
                Indulge in our delicious selection of freshly baked
                artisanal cakes, pastries, cookies, and handcrafted
                desserts made daily with organic premium ingredients.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🔥 Today's Special Offers")
    specials = fetch_products()
    if "is_today_special" in specials.columns:
        specials = specials[specials["is_today_special"] == 1]
    render_product_grid(specials.head(3))

    st.divider()
    st.subheader("⭐ Best-Selling Favorites")
    best_sellers = fetch_products(sort_by="Popularity")
    render_product_grid(best_sellers.head(3))

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🕒 Opening Hours")
        st.markdown(
            """
            - **Monday - Friday:** 8:00 AM – 10:00 PM
            - **Saturday - Sunday:** 9:00 AM – 11:00 PM
            - **Fresh Bakes Out:** Every morning at 8:30 AM!
            """
        )

    with c2:
        st.subheader("📍 Quick Info")
        st.markdown(
            """
            - **Location:** Block 5, Clifton, Karachi, Pakistan
            - **Call Us:** +92 (300) 123-4567
            - **Email:** hello@sweetcrumbs.com
            - **Delivery:** Express delivery within 45 mins in Karachi.
            """
        )


# -------------------------------------------------------------------------
# PAGE 2: MENU
# -------------------------------------------------------------------------
elif selected_page == "🧁 Menu & Products":
    st.markdown(
        "<h2 class='main-header'>Our Bakery Menu 🥐</h2>",
        unsafe_allow_html=True
    )

    categories = [
        "All Categories",
        "Cakes 🎂",
        "Cupcakes 🧁",
        "Pastries 🥐",
        "Donuts 🍩",
        "Cookies 🍪",
        "Bread & Buns 🍞",
        "Desserts 🍮",
        "Birthday Cakes 🎉"
    ]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cat_filter = st.selectbox("Category", categories)

    with col2:
        search_query = st.text_input(
            "Search item",
            placeholder="Chocolate, Croissant..."
        )

    with col3:
        sort_opt = st.selectbox(
            "Sort By",
            [
                "Default",
                "Price: Low to High",
                "Price: High to Low",
                "Popularity"
            ]
        )

    with col4:
        max_price = st.slider(
            "Max Price (PKR)",
            200,
            5000,
            5000,
            step=100
        )

    products_df = fetch_products(
        category=cat_filter,
        search=search_query,
        max_p=max_price,
        sort_by=sort_opt
    )
    render_product_grid(products_df)


# -------------------------------------------------------------------------
# PAGE 3: CUSTOM CAKE DESIGNER
# -------------------------------------------------------------------------
elif selected_page == "🎂 Custom Cake Designer":
    st.markdown(
        "<h2 class='main-header'>Design Your Dream Cake 🎨</h2>",
        unsafe_allow_html=True
    )
    st.write(
        "Customize every layer of your cake and get an instant cost calculation."
    )

    col1, col2 = st.columns(2)

    with col1:
        flavor = st.selectbox(
            "Cake Flavor Base",
            [
                "Belgian Dark Chocolate",
                "Vanilla Bean",
                "Red Velvet",
                "Salted Caramel",
                "Mango Passion",
                "Lotus Biscoff"
            ]
        )

        size = st.selectbox(
            "Cake Size (Weight)",
            [
                "2 Lbs (Serves 6-8)",
                "4 Lbs (Serves 12-15)",
                "6 Lbs Tiered (Serves 20-25)"
            ]
        )

        cream = st.selectbox(
            "Cream & Filling",
            [
                "Swiss Buttercream",
                "Cream Cheese Frosting",
                "Dark Chocolate Ganache",
                "Whipped Chantilly"
            ]
        )

        shape = st.selectbox(
            "Cake Shape",
            [
                "Classic Round",
                "Heart Shape",
                "Square",
                "2-Tiered Custom"
            ]
        )

    with col2:
        theme = st.text_input(
            "Theme / Colors",
            value="Pastel Pink & Floral"
        )

        message = st.text_input(
            "Message on Cake Base",
            value="Happy Birthday!"
        )

        desc = st.text_area(
            "Detailed Custom Design Request",
            placeholder="Describe sprinkles, toppers, color palette or references..."
        )

        del_date = st.date_input("Delivery Date")

    base_price = 2000

    if "4 Lbs" in size:
        base_price += 1800
    elif "6 Lbs" in size:
        base_price += 3500

    if flavor in ["Lotus Biscoff", "Belgian Dark Chocolate"]:
        base_price += 500

    if shape == "2-Tiered Custom":
        base_price += 1000

    st.divider()
    st.markdown(
        f"### Estimated Price: **PKR {base_price:,.0f}**"
    )

    if st.button("Add Custom Cake to Cart 🛒"):
        custom_id = f"custom_{random.randint(1000, 9999)}"
        custom_name = f"Custom Cake ({flavor}, {size})"

        add_to_cart(
            custom_id,
            custom_name,
            base_price,
            stock=10
        )

        st.success(
            "Custom Cake specifications saved and added to cart!"
        )


# -------------------------------------------------------------------------
# PAGE 4: SHOPPING CART
# -------------------------------------------------------------------------
elif selected_page == "🛒 Shopping Cart":
    st.markdown(
        "<h2 class='main-header'>Your Shopping Cart 🛒</h2>",
        unsafe_allow_html=True
    )

    if not st.session_state.cart:
        st.info(
            "Your shopping cart is currently empty. "
            "Visit the Menu to add fresh items!"
        )
    else:
        cart_items = st.session_state.cart
        subtotal = 0

        for item_id, item in list(cart_items.items()):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])

            with c1:
                st.write(f"**{item['name']}**")

            with c2:
                st.write(f"PKR {item['price']:,.0f}")

            with c3:
                new_qty = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=item["stock"],
                    value=item["quantity"],
                    key=f"qty_{item_id}"
                )
                st.session_state.cart[item_id]["quantity"] = new_qty

            with c4:
                item_total = (
                    item["price"]
                    * st.session_state.cart[item_id]["quantity"]
                )
                subtotal += item_total
                st.write(f"**PKR {item_total:,.0f}**")

            with c5:
                if st.button("❌", key=f"del_{item_id}"):
                    del st.session_state.cart[item_id]
                    st.rerun()

        st.divider()

        del_option = st.radio(
            "Delivery Type",
            [
                "Home Delivery (PKR 250)",
                "Store Pickup (Free)"
            ],
            horizontal=True
        )

        delivery_fee = 250 if "Home Delivery" in del_option else 0
        grand_total = subtotal + delivery_fee

        st.markdown(
            f"""
            * **Subtotal:** PKR {subtotal:,.0f}
            * **Delivery Charges:** PKR {delivery_fee:,.0f}
            ### **Grand Total: PKR {grand_total:,.0f}**
            """
        )

        c_clear, c_check = st.columns([1, 4])

        with c_clear:
            if st.button("Clear Cart 🗑️"):
                st.session_state.cart = {}
                st.rerun()

        st.divider()
        st.markdown("### 📦 Delivery & Checkout Information")

        with st.form("checkout_form"):
            default_name = user["name"] if user else ""
            default_phone = user["phone"] if user else ""
            default_email = user["email"] if user else ""

            fc1, fc2 = st.columns(2)

            with fc1:
                cust_name = st.text_input(
                    "Full Name",
                    value=default_name
                )
                cust_phone = st.text_input(
                    "Phone Number",
                    value=default_phone
                )
                cust_email = st.text_input(
                    "Email Address",
                    value=default_email
                )
                pay_method = st.selectbox(
                    "Payment Method",
                    [
                        "Cash on Delivery",
                        "Easypaisa",
                        "JazzCash",
                        "Bank Transfer"
                    ]
                )

            with fc2:
                address = st.text_area(
                    "Delivery Address",
                    value=(
                        "Clifton Block 5, Karachi"
                        if "Home Delivery" in del_option
                        else "N/A - Store Pickup"
                    )
                )

                pref_date = st.date_input("Preferred Delivery Date")

                pref_time = st.selectbox(
                    "Preferred Time Slot",
                    [
                        "Morning (9 AM - 12 PM)",
                        "Afternoon (1 PM - 5 PM)",
                        "Evening (6 PM - 9 PM)"
                    ]
                )

                notes = st.text_input(
                    "Special Instructions",
                    placeholder="e.g. Ring bell twice, deliver to reception..."
                )

            submit_order = st.form_submit_button(
                "Place Order Now 🚀"
            )

            if submit_order:
                if not cust_name or not cust_phone or not address:
                    st.error(
                        "Please fill in all required contact and delivery fields."
                    )
                else:
                    conn = get_connection()
                    cursor = conn.cursor()

                    order_code = (
                        f"SCB-{random.randint(10000, 99999)}"
                    )

                    user_id = user["id"] if user else None

                    cursor.execute(
                        """
                        INSERT INTO orders (
                            order_code, user_id, customer_name, phone,
                            email, delivery_address, delivery_type,
                            preferred_date, preferred_time, payment_method,
                            subtotal, delivery_fee, total_amount,
                            special_instructions
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            order_code,
                            user_id,
                            cust_name,
                            cust_phone,
                            cust_email,
                            address,
                            del_option,
                            str(pref_date),
                            pref_time,
                            pay_method,
                            subtotal,
                            delivery_fee,
                            grand_total,
                            notes
                        )
                    )

                    order_id = cursor.lastrowid

                    for item_id, item in st.session_state.cart.items():
                        product_id = (
                            item_id if isinstance(item_id, int)
                            else None
                        )

                        cursor.execute(
                            """
                            INSERT INTO order_items (
                                order_id, product_id, product_name,
                                price, quantity
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                order_id,
                                product_id,
                                item["name"],
                                item["price"],
                                item["quantity"]
                            )
                        )

                        if isinstance(item_id, int):
                            cursor.execute(
                                """
                                UPDATE products
                                SET stock = stock - ?,
                                    sales_count = sales_count + ?
                                WHERE id = ?
                                """,
                                (
                                    item["quantity"],
                                    item["quantity"],
                                    item_id
                                )
                            )

                    conn.commit()
                    conn.close()

                    st.session_state.cart = {}

                    st.success("🎉 Order Placed Successfully!")
                    st.balloons()

                    st.markdown(
                        f"""
                        **Order Receipt Summary:**
                        * **Order ID:** `{order_code}`
                        * **Customer:** {cust_name}
                        * **Total Paid/Due:** PKR {grand_total:,.0f}
                          ({pay_method})
                        * **Estimated Delivery Date:** {pref_date}
                          ({pref_time})
                        """
                    )


# -------------------------------------------------------------------------
# PAGE 5: ACCOUNT
# -------------------------------------------------------------------------
elif selected_page == "👤 My Account":
    st.markdown(
        "<h2 class='main-header'>Customer Account & Portal 👤</h2>",
        unsafe_allow_html=True
    )

    if not st.session_state.user:
        tab_login, tab_reg = st.tabs(["Login", "Register"])

        with tab_login:
            with st.form("login_form"):
                l_email = st.text_input("Email")
                l_pass = st.text_input(
                    "Password",
                    type="password"
                )

                if st.form_submit_button("Login"):
                    u = login_user(l_email, l_pass)

                    if u:
                        st.session_state.user = u
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with tab_reg:
            with st.form("reg_form"):
                r_name = st.text_input("Full Name")
                r_email = st.text_input("Email")
                r_phone = st.text_input("Phone Number")
                r_pass = st.text_input(
                    "Password",
                    type="password"
                )

                if st.form_submit_button("Register"):
                    ok, msg = register_user(
                        r_name,
                        r_email,
                        r_phone,
                        r_pass
                    )

                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

    else:
        st.subheader(
            f"Welcome back, {st.session_state.user['name']}!"
        )

        tab_profile, tab_orders = st.tabs(
            ["Profile Details", "Order History"]
        )

        with tab_profile:
            with st.form("prof_form"):
                p_name = st.text_input(
                    "Full Name",
                    value=st.session_state.user["name"]
                )

                p_phone = st.text_input(
                    "Phone Number",
                    value=st.session_state.user["phone"]
                )

                if st.form_submit_button("Update Profile"):
                    update_user_profile(
                        st.session_state.user["id"],
                        p_name,
                        p_phone
                    )

                    st.session_state.user["name"] = p_name
                    st.session_state.user["phone"] = p_phone

                    st.success(
                        "Profile details updated successfully!"
                    )

        with tab_orders:
            conn = get_connection()

            orders_df = pd.read_sql_query(
                """
                SELECT * FROM orders
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                conn,
                params=[st.session_state.user["id"]]
            )

            conn.close()

            if orders_df.empty:
                st.info("You haven't placed any orders yet.")
            else:
                for idx, row in orders_df.iterrows():
                    with st.expander(
                        f"Order #{row['order_code']} - "
                        f"{row['status']} "
                        f"(PKR {row['total_amount']:,.0f})"
                    ):
                        st.write(
                            f"**Date:** {row['created_at']}"
                        )
                        st.write(
                            f"**Delivery Date:** "
                            f"{row['preferred_date']} "
                            f"({row['preferred_time']})"
                        )
                        st.write(
                            f"**Payment:** {row['payment_method']}"
                        )
                        st.write(
                            f"**Address:** {row['delivery_address']}"
                        )


# -------------------------------------------------------------------------
# PAGE 6: REVIEWS
# -------------------------------------------------------------------------
elif selected_page == "⭐ Reviews & Ratings":
    st.markdown(
        "<h2 class='main-header'>Customer Reviews & Ratings ⭐</h2>",
        unsafe_allow_html=True
    )

    st.write(
        "Share your experience with Sweet Crumbs Bakery."
    )

    rating = st.slider(
        "Your Rating",
        min_value=1,
        max_value=5,
        value=5
    )

    review = st.text_area(
        "Your Review",
        placeholder="Tell us about your bakery experience..."
    )

    if st.button("Submit Review ⭐"):
        if not review.strip():
            st.warning("Please write a review first.")
        else:
            st.success(
                f"Thank you! Your {rating}/5 review has been submitted."
            )

    st.divider()
    st.subheader("What Our Customers Say")

    review_cols = st.columns(3)

    sample_reviews = [
        ("Ayesha Khan", 5, "The chocolate cake was absolutely delicious!"),
        ("Hamza Ali", 5, "Fresh pastries and excellent presentation."),
        ("Sara Ahmed", 4, "Great taste and fast delivery.")
    ]

    for col, (name, stars, text) in zip(review_cols, sample_reviews):
        with col:
            st.info(
                f"**{name}**\n\n"
                f"{'⭐' * stars}\n\n"
                f"{text}"
            )


# -------------------------------------------------------------------------
# PAGE 7: CONTACT
# -------------------------------------------------------------------------
elif selected_page == "📞 Contact Us":
    st.markdown(
        "<h2 class='main-header'>Contact Sweet Crumbs Bakery 📞</h2>",
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📍 Visit Us")
        st.write("Block 5, Clifton, Karachi, Pakistan")
        st.write("📞 +92 (300) 123-4567")
        st.write("✉️ hello@sweetcrumbs.com")
        st.write("🚚 Express delivery available in Karachi.")

    with c2:
        st.subheader("💬 Send Us a Message")

        with st.form("contact_form"):
            contact_name = st.text_input("Your Name")
            contact_email = st.text_input("Your Email")
            contact_message = st.text_area("Message")

            if st.form_submit_button("Send Message"):
                if contact_name and contact_email and contact_message:
                    st.success(
                        "Thank you! Your message has been received."
                    )
                else:
                    st.error("Please complete all fields.")


# -------------------------------------------------------------------------
# PAGE 8: ADMIN DASHBOARD
# -------------------------------------------------------------------------
elif selected_page == "👨‍💼 Admin Dashboard":
    if not user or user["role"] != "admin":
        st.error("Access denied. Admin login is required.")
        st.stop()

    st.markdown(
        "<h2 class='main-header'>Admin Management Dashboard 👨‍💼</h2>",
        unsafe_allow_html=True
    )

    conn = get_connection()

    orders_df = pd.read_sql_query(
        "SELECT * FROM orders ORDER BY id DESC",
        conn
    )

    products_df = pd.read_sql_query(
        "SELECT * FROM products",
        conn
    )

    users_df = pd.read_sql_query(
        "SELECT * FROM users",
        conn
    )

    conn.close()

    m1, m2, m3, m4 = st.columns(4)

    total_revenue = (
        orders_df["total_amount"].sum()
        if not orders_df.empty and "total_amount" in orders_df.columns
        else 0
    )

    m1.metric(
        "Total Revenue",
        f"PKR {total_revenue:,.0f}"
    )
    m2.metric("Total Orders", len(orders_df))
    m3.metric("Total Products", len(products_df))

    customer_count = (
        len(users_df[users_df["role"] == "customer"])
        if not users_df.empty and "role" in users_df.columns
        else 0
    )

    m4.metric(
        "Registered Customers",
        customer_count
    )

    st.divider()

    admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs(
        [
            "📦 Order Management",
            "🧁 Product Catalog Control",
            "📊 Sales Analytics",
            "👥 Customer Accounts"
        ]
    )

    with admin_tab1:
        st.subheader("Manage Customer Orders")

        if orders_df.empty:
            st.info("No orders available.")
        else:
            statuses = [
                "Pending",
                "Confirmed",
                "Preparing",
                "Out for Delivery",
                "Delivered"
            ]

            for idx, o in orders_df.iterrows():
                col_o1, col_o2, col_o3 = st.columns([3, 2, 2])

                with col_o1:
                    st.write(
                        f"**{o['order_code']}** - "
                        f"{o['customer_name']} ({o['phone']})"
                    )
                    st.caption(
                        f"Amount: PKR {o['total_amount']:,.0f} | "
                        f"Date: {o['preferred_date']}"
                    )

                with col_o2:
                    st.write(
                        f"Current Status: **{o['status']}**"
                    )

                with col_o3:
                    current_status = (
                        o["status"]
                        if o["status"] in statuses
                        else "Pending"
                    )

                    new_status = st.selectbox(
                        "Update",
                        statuses,
                        key=f"status_sel_{o['id']}",
                        index=statuses.index(current_status)
                    )

                    if new_status != o["status"]:
                        conn = get_connection()

                        conn.execute(
                            """
                            UPDATE orders
                            SET status = ?
                            WHERE id = ?
                            """,
                            (new_status, o["id"])
                        )

                        conn.commit()
                        conn.close()

                        st.success("Updated status!")
                        st.rerun()

    with admin_tab2:
        st.subheader("Add / Edit Bakery Products")

        with st.form("add_product_form"):
            st.markdown("#### Add New Product")

            p_name = st.text_input("Product Name")

            p_cat = st.selectbox(
                "Category",
                [
                    "Cakes 🎂",
                    "Cupcakes 🧁",
                    "Pastries 🥐",
                    "Donuts 🍩",
                    "Cookies 🍪",
                    "Bread & Buns 🍞",
                    "Desserts 🍮",
                    "Birthday Cakes 🎉"
                ]
            )

            p_desc = st.text_area("Description")

            p_price = st.number_input(
                "Price (PKR)",
                min_value=10.0,
                value=500.0
            )

            p_stock = st.number_input(
                "Stock",
                min_value=0,
                value=20
            )

            p_img = st.text_input(
                "Image URL",
                value=(
                    "https://images.unsplash.com/"
                    "photo-1578985545062-69928b1d9587?"
                    "auto=format&fit=crop&w=600&q=80"
                )
            )

            save_product = st.form_submit_button(
                "Save Product"
            )

            if save_product:
                if not p_name.strip():
                    st.error("Product name is required.")
                else:
                    conn = get_connection()

                    conn.execute(
                        """
                        INSERT INTO products (
                            name, category, description,
                            price, stock, image_url
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            p_name,
                            p_cat,
                            p_desc,
                            p_price,
                            p_stock,
                            p_img
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success("New product saved!")
                    st.rerun()

    with admin_tab3:
        st.subheader("Sales & Inventory Performance")

        if products_df.empty:
            st.info("No product data available.")
        else:
            chart_df = products_df.copy()

            if "sales_count" in chart_df.columns:
                fig = px.bar(
                    chart_df.sort_values(
                        "sales_count",
                        ascending=False
                    ).head(10),
                    x="name",
                    y="sales_count",
                    title="Top Products by Sales"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            if "stock" in chart_df.columns:
                inventory_fig = px.bar(
                    chart_df.sort_values(
                        "stock",
                        ascending=True
                    ).head(10),
                    x="name",
                    y="stock",
                    title="Current Product Inventory"
                )

                st.plotly_chart(
                    inventory_fig,
                    use_container_width=True
                )

    with admin_tab4:
        st.subheader("Customer Accounts")

        if users_df.empty:
            st.info("No users registered yet.")
        else:
            customer_df = users_df[
                users_df["role"] == "customer"
            ]

            if customer_df.empty:
                st.info("No customer accounts found.")
            else:
                display_columns = [
                    c for c in
                    ["id", "name", "email", "phone", "role"]
                    if c in customer_df.columns
                ]

                st.dataframe(
                    customer_df[display_columns],
                    use_container_width=True,
                    hide_index=True
                )
