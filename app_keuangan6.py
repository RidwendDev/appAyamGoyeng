import sqlite3
import streamlit as st
import pandas as pd
import datetime

# Fungsi untuk membuat koneksi ke database SQLite
def create_connection():
    conn = sqlite3.connect('app_data3.db')
    return conn

# Fungsi untuk membuat tabel sales_data jika belum ada
def create_sales_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_data (
            id INTEGER PRIMARY KEY,
            date DATE,
            dada INTEGER,
            sayap INTEGER,
            paha INTEGER,
            nasi INTEGER
        )
    ''')
    conn.commit()

# Fungsi untuk membuat tabel expenses_data jika belum ada
def create_expenses_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses_data (
            id INTEGER PRIMARY KEY,
            date DATE,
            expenses INTEGER
        )
    ''')
    conn.commit()

# Fungsi untuk menyimpan data penjualan harian ke database
def save_daily_data(conn, date, dada, sayap, paha, nasi):
    cursor = conn.cursor()

    # Cek apakah data sudah ada untuk tanggal tersebut
    cursor.execute('''
        SELECT * FROM sales_data WHERE date=?
    ''', (date,))
    existing_data = cursor.fetchall()

    if existing_data:
        # Jika sudah ada, ambil data lama
        old_data = existing_data[0]
        # Update data lama dengan penambahan data baru
        cursor.execute('''
            UPDATE sales_data
            SET dada=?, sayap=?, paha=?, nasi=?
            WHERE date=?
        ''', (old_data[2] + dada, old_data[3] + sayap, old_data[4] + paha, old_data[5] + nasi, date))
    else:
        # Jika belum ada, insert data baru
        cursor.execute('''
            INSERT INTO sales_data (date, dada, sayap, paha, nasi)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, dada, sayap, paha, nasi))

    conn.commit()

# Fungsi untuk menghitung total pendapatan per hari
def calculate_total_income(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT date, SUM(dada*9000 + sayap*6000 + paha*8000 + nasi*2000) AS total_income FROM sales_data GROUP BY date')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['date', 'total_income'])
    return df

# Fungsi untuk menyimpan data pengeluaran harian ke database
def save_daily_expenses(conn, date, expenses):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO expenses_data (date, expenses)
        VALUES (?, ?)
    ''', (date, expenses))
    conn.commit()

# Fungsi untuk menampilkan data penjualan per hari
def show_sales_data(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sales_data')
    data = cursor.fetchall()
    return data

# Fungsi untuk menampilkan data pengeluaran per hari
def show_expenses_data(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses_data')
    data = cursor.fetchall()
    return data

# Fungsi untuk menghapus entri berdasarkan ID
def delete_entry(conn, table_name, entry_id):
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (entry_id,))
    conn.commit()

# Fungsi utama
def main():
    st.title("MFC Finance Tracker Apps 🐔")

    # Buat koneksi ke database dan buat tabel jika belum ada
    conn = create_connection()
    create_sales_table(conn)
    create_expenses_table(conn)

    # Navbar
    nav_selection = st.sidebar.radio("Navigation", ["Input Data", "Ringkasan Data", "Visualisasi"])

    # Initialize df_income
    df_income = pd.DataFrame(columns=['date', 'total_income'])
    df_expenses = pd.DataFrame(columns=['ID', 'Date', 'Expenses'])


    if nav_selection == "Input Data":
        # Form input penjualan harian
        st.header("Input Penjualan Harian")
        sales_date = st.date_input("Pilih Tanggal", datetime.date.today())
        dada = st.number_input("Jumlah Dada Terjual", min_value=0, value=0)
        sayap = st.number_input("Jumlah Sayap Terjual", min_value=0, value=0)
        paha = st.number_input("Jumlah Paha Terjual", min_value=0, value=0)
        nasi = st.number_input("Jumlah Nasi Terjual", min_value=0, value=0)

        if st.button("Simpan Penjualan"):
            save_daily_data(conn, sales_date, dada, sayap, paha, nasi)
            st.success("Data penjualan tersimpan!")
        
        # Menambahkan footer
        st.markdown("<div style='text-align: center;'><p>Made with 🥰 by Ridwan&Transformers</p></div>", unsafe_allow_html=True)

    elif nav_selection == "Ringkasan Data":
        # Menampilkan data penjualan per hari
        st.header("Data Penjualan Harian")
        sales_data = show_sales_data(conn)
        df_sales = pd.DataFrame(sales_data, columns=['ID', 'Date', 'Dada', 'Sayap', 'Paha', 'Nasi'])
        st.dataframe(df_sales)

        # Menampilkan total pendapatan per hari
        st.header("Total Pendapatan Harian")
        df_income = calculate_total_income(conn)
        st.dataframe(df_income)

        # Form input pengeluaran harian
        st.header("Input Pengeluaran Harian")
        expenses_date = st.date_input("Pilih Tanggal Pengeluaran", datetime.date.today())
        daily_expenses = st.number_input("Jumlah Pengeluaran", min_value=0, value=0)

        if st.button("Simpan Pengeluaran"):
            save_daily_expenses(conn, expenses_date, daily_expenses)
            st.success("Data pengeluaran tersimpan!")

        # Menampilkan data pengeluaran per hari
        st.header("Data Pengeluaran Harian")
        expenses_data = show_expenses_data(conn)
        df_expenses = pd.DataFrame(expenses_data, columns=['ID', 'Date', 'Expenses'])
        st.dataframe(df_expenses)

        # Tombol untuk menghapus entri
        if st.checkbox("Hapus Entri"):
            entry_id = st.number_input("Masukkan ID Entri yang akan dihapus", min_value=1)
            if st.button("Hapus"):
                delete_entry(conn, 'sales_data', entry_id)
                st.success("Entri berhasil dihapus!")
        # Menambahkan footer
        st.markdown("<div style='text-align: center;'><p>Made with 🥰 by Ridwan&Transformers</p></div>", unsafe_allow_html=True)

    elif nav_selection == "Visualisasi":
        # Page untuk visualisasi
        st.header("Inpo Plotting")

        # Bar plot ayam bagian mana yang paling laris
        st.subheader("Penjualan Ayam/Bagian")
        bar_data = pd.DataFrame(show_sales_data(conn), columns=['ID', 'Date', 'Dada', 'Sayap', 'Paha', 'Nasi'])
        st.bar_chart(bar_data.set_index('Date'))

        # Line plot total pemasukan dan pengeluaran per hari
        st.subheader("Total Pemasukan vs Pengeluaran")
        df_income = calculate_total_income(conn)
        df_expenses = pd.DataFrame(show_expenses_data(conn), columns=['ID', 'Date', 'Expenses'])
        line_data = pd.DataFrame({'Date': df_income['date'], 'Total Income': df_income['total_income'],
                                  'Total Expenses': df_expenses['Expenses']})
        st.line_chart(line_data.set_index('Date'))
        # Menambahkan footer
        st.markdown("<div style='text-align: center;'><p>Made with 🥰 by Ridwan&Transformers</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
