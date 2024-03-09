import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os
from datetime import datetime, timedelta

# Importing Databases
path = os.path.dirname(__file__)
data1_path = os.path.join(path, r"fix_customers.csv")
fix_customers_df = pd.read_csv(data1_path)

path = os.path.dirname(__file__)
data2_path = os.path.join(path, r"fix_orders.csv")
fix_orders_df = pd.read_csv(data2_path)

path = os.path.dirname(__file__)
data3_path = os.path.join(path, r"orders_customers.csv")
orders_customers_df = pd.read_csv(data3_path)

path = os.path.dirname(__file__)
data4_path = os.path.join(path, r"fix_order_reviews.csv")
order_reviews_df = pd.read_csv(data4_path)

path = os.path.dirname(__file__)
data5_path = os.path.join(path, r"fix_order_payments.csv")
order_payments_df = pd.read_csv(data5_path)

sns.set(style='dark')

@st.cache_data()  # Caching function untuk peningkatan peforma saat data berubah
def calculate_rfm(fix_orders_df, fix_order_payments_df):
    fix_orders_df['order_purchase_timestamp'] = pd.to_datetime(fix_orders_df['order_purchase_timestamp'])

    # filter data untuk 90 hari terakhir
    end_date = fix_orders_df['order_purchase_timestamp'].max()
    start_date = end_date - timedelta(days=90)
    filtered_orders_df = fix_orders_df[(fix_orders_df['order_purchase_timestamp'] >= start_date) & (fix_orders_df['order_purchase_timestamp'] <= end_date)]

    # Recency
    max_purchase_date = filtered_orders_df['order_purchase_timestamp'].max()
    filtered_orders_df['recency'] = (max_purchase_date - filtered_orders_df['order_purchase_timestamp']).dt.days

    # Frequency
    frequency_df = filtered_orders_df.groupby('customer_id').size().reset_index(name='frequency')

    # Monetary
    monetary_df = fix_order_payments_df.groupby('order_id')['payment_value'].sum().reset_index()
    monetary_df = pd.merge(filtered_orders_df[['customer_id', 'order_id']], monetary_df, on='order_id', how='left')
    monetary_df = monetary_df.groupby('customer_id')['payment_value'].sum().reset_index(name='monetary')

    # Merge RFM values
    rfm_df = pd.merge(frequency_df, monetary_df, on='customer_id', how='left')
    rfm_df = pd.merge(rfm_df, filtered_orders_df[['customer_id', 'recency']], on='customer_id', how='left')

    # Shorten customer IDs
    rfm_df['customer_id_shortened'] = rfm_df['customer_id'].str.slice(0, 3) + '...' + rfm_df['customer_id'].str.slice(-3)

    return rfm_df

with st.sidebar:
    # Menambahkan judul dan developer
    st.header("Data Explanatory")
    st.markdown("Developer by Khoirun Niswa")

    # Menambahkan logo perusahaan
    st.image("logo.jpg", use_column_width=True)

    selected_dataset = st.sidebar.selectbox(
    "Select Dataset",
    ("Pelanggan Terbanyak", "Tingkat Keberhasilan", "Order Payments", "RFM Analysis")
    )

# Set page title
st.title("Tokopaedi Dashboard")

# Visualizations
def visualize_by_state(df):
    bystate_df = df.groupby(by="customer_state").size().reset_index(name='customer_count')
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)  # Sorting by customer_count

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(bystate_df["customer_state"], bystate_df["customer_count"], color='skyblue')
    ax.bar(bystate_df["customer_state"], bystate_df["customer_count"], color='skyblue')
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.set_title('Number of Customers by State')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    # Adding nominal values on each bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom', ha='center', fontsize=8)

    # Displaying the plot using Streamlit
    st.subheader("Pelanggan Terbanyak Berdasarkan Lokasi (State)")
    st.pyplot(fig)
    st.caption("pelangan dengan wilayah state code SP menempati peringkat pertama sebagai pelanggan terbanyak di wilayah tersebut dengan jumlah 41.746 pelanggan")

def visualize_by_payment_type(df):
    payment_counts_df = df.groupby(by="payment_type").size().reset_index(name='transaction_count')
    payment_counts_df = payment_counts_df.sort_values(by='transaction_count', ascending=False)  # Sorting by transaction_count

    # Plotting
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(payment_counts_df["payment_type"], payment_counts_df["transaction_count"], color='skyblue')
    ax.bar(payment_counts_df["payment_type"], payment_counts_df["transaction_count"], color='skyblue')
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.set_title('Number of Transactions by Payment Type')
    plt.tight_layout()

    # Adding nominal values on each bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom', ha='center', fontsize=8)

    # Displaying the plot using Streamlit
    st.subheader("Metode Pembayaran Pelanggan")
    st.pyplot(fig)
    st.caption("metode pembayaran yang paling banyak digunakan adalah metode pembayaran melalui credit card yakni sebanyak 76.795 kali.")

def visualize_by_order_status(df):
    bystatus_df = df.groupby(by="order_status").size().reset_index(name='customer_count')
    bystatus_df = bystatus_df.sort_values(by='customer_count', ascending=False)
    status_customer_count = df.groupby(by="order_status")["customer_id"].count()

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = status_customer_count.sort_values().plot(kind='barh', color='skyblue', ax=ax)
    status_customer_count.sort_values().plot(kind='barh', color='skyblue', ax=ax)
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.set_title('Number of Customers by Order Status')
    plt.tight_layout()

    # Adding nominal values on each bar
    for bar in bars.patches:
        xval = bar.get_width()
        ax.text(xval, bar.get_y() + bar.get_height()/2, round(xval, 2), va='center', ha='left', fontsize=8)

    # Displaying the plot using Streamlit
    st.subheader("Tingkat Kerberhasilan Pengiriman Berdasarkan Status")
    st.pyplot(fig)
    st.caption("sebanyak 96.478 pelangan dari total 99.441 telah ber status delivered yang menunjukkan tingkat keberhasilan yang tinggi dalam pengiriman pesanan kepada pelanggan.")

@st.cache_data()
def visualize_rfm_analysis(fix_orders_df, fix_order_payments_df):
    # Calculate RFM for the last 90 days
    rfm_df = calculate_rfm(fix_orders_df, fix_order_payments_df)

    # Display RFM metrics
    st.subheader("Best Customers Based on RFM Parameters")

    # Create tabs for Recency, Frequency, and Monetary
    tabs = st.tabs(["Recency", "Frequency", "Monetary"])

    # Recency tab
    with tabs[0]:
        st.subheader("Recency")
        st.metric("Average Recency (days)", value=round(rfm_df['recency'].mean(), 1))
        fig_recency, ax_recency = plt.subplots()
        sns.barplot(y="recency", x="customer_id_shortened", data=rfm_df.sort_values(by="recency", ascending=True).head(5), color='skyblue')
        ax_recency.set_ylabel("Recency (days)")
        ax_recency.set_xlabel("Customer ID")
        ax_recency.set_title("Top 5 Customers by Recency")
        for p in ax_recency.patches:
            ax_recency.annotate(str(round(p.get_height(), 1)), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', fontsize=10, color='black', xytext=(0, 5), textcoords='offset points')
        st.pyplot(fig_recency)
        with st.expander("See explanation"):
            st.write(
                """Grafik ini menampilkan 5 pelanggan dengan nilai recency terendah yang berarti mereka adalah pelanggan yang baru-baru ini melakukan pembelian, dengan nilai recency diurutkan dari terendah ke tertinggi. 
Barchart diatas menunjukkan bahwa rata-rata pelanggan terakhir kali melakukan pembelian sekitar 72 hari yang lalu dalam periode 90 hari terakhir.
""")

    # Frequency tab
    with tabs[1]:
        st.subheader("Frequency")
        st.metric("Average Frequency", value=round(rfm_df['frequency'].mean(), 2))
        fig_frequency, ax_frequency = plt.subplots()
        sns.barplot(y="frequency", x="customer_id_shortened", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), color='skyblue')
        ax_frequency.set_ylabel("Frequency")
        ax_frequency.set_xlabel("Customer ID")
        ax_frequency.set_title("Top 5 Customers by Frequency")
        for p in ax_frequency.patches:
            ax_frequency.annotate(str(round(p.get_height(), 2)), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', fontsize=10, color='black', xytext=(0, 5), textcoords='offset points')
        st.pyplot(fig_frequency)
        with st.expander("See explanation"):
            st.write(
                """Grafik ini menampilkan 5 pelanggan dengan frekuensi pembelian tertinggi, dengan frekuensi diurutkan dari tertinggi ke terendah.
Barchart diatas menunjukkan bahwa rata-rata frekuensi pembelian oleh pelanggan yaitu pelanggan hanya melakukan satu pembelian dalam periode 90 hari terakhir.
""")

    # Monetary tab
    with tabs[2]:
        st.subheader("Monetary")
        avg_monetary = round(rfm_df['monetary'].mean(), 2)
        st.metric("Average Monetary", value=format_currency(avg_monetary, 'USD', locale='en_US'))
        fig_monetary, ax_monetary = plt.subplots()
        sns.barplot(y="monetary", x="customer_id_shortened", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), color='skyblue')
        ax_monetary.set_ylabel("Monetary")
        ax_monetary.set_xlabel("Customer ID")
        ax_monetary.set_title("Top 5 Customers by Monetary")
        for p in ax_monetary.patches:
            ax_monetary.annotate(format_currency(p.get_height(), 'USD', locale='en_US'), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', fontsize=10, color='black', xytext=(0, 10), textcoords='offset points')
        st.pyplot(fig_monetary)
        with st.expander("See explanation"):
            st.write(
                """Grafik ini menampilkan 5 pelanggan dengan nilai total pembelian tertinggi, dengan nilai total pembelian diurutkan dari tertinggi ke terendah.
Barchart diatas menunjukkan bahwa rata-rata total nilai pembelian oleh pelanggan menunjukkan bahwa pelanggan menghabiskan sekitar 161 dollar dalam pembelian mereka dalam periode 90 hari terakhir.""")

# Check selected dataset
if selected_dataset == "Pelanggan Terbanyak":
    visualize_by_state(orders_customers_df)

elif selected_dataset == "Tingkat Keberhasilan":
   visualize_by_order_status(orders_customers_df)

elif selected_dataset == "Order Payments":
    visualize_by_payment_type(order_payments_df)

elif selected_dataset == "RFM Analysis":
    visualize_rfm_analysis(fix_orders_df, order_payments_df)
