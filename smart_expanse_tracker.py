import streamlit as st
import pandas as pd
import datetime


#=============Configuration=============
st.set_page_config(page_title="💰smart Expanse Tracker", layout="wide")
st.title("💰Smart Expense Tracker with AI Categorization")
st.markdown("---")


#=============Initialize Session State=============
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame({
        'Date': [datetime.datetime.now().date() - datetime.timedelta(days=i) for i in range(5)],
        'Category': ["Food", "Transport", "Entertainment", "Bills", "Shopping"],
        'Amount': [25.50, 15.75, 45.00, 120.30, 65.20],
        'Description': ['Lunch', 'Uber', 'Movie', 'Electricity', 'Clothes'],
        'Payment Method':['Credit', 'Cash','Credit', 'Cash', 'Credit']
    })

#=============Categories Emojis=============
Category_Emojis = {
    "Food":"🍔", "Transport": "🚗", "Entertainment": "🎬", "Bills": "💡", "Shopping": "🛍️",
    "Education": "📚", "Health": "💊", "Other": "📦"
}


#=============Sidebar: Add New Expense=============
with st.sidebar:
    st.header("➕ Add New Expense")

    with st.form("expense_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.date.today())
        amount = st.number_input("Amount ($)", min_value=0.01, max_value=10000.0, step=0.01, format="%.2f")

        category = st.selectbox("Category", list(Category_Emojis.keys()))
        st.caption(f"Selected: {Category_Emojis[category]}{category}")

        description = st.text_input("Description", placeholder="Coffee, Uber, etc.")
        payment = st.selectbox("Payment Method", ['Credit', 'Cash','Debit', 'PayPal', 'Crypto'])

        submitted = st.form_submit_button("💰 Add Expense")

        if submitted and amount > 0 and description:
            new_expenses = pd.DataFrame([{
                'Date': date,
                'Category': category,
                'Amount': amount,
                'Description': description,
                'Payment Method': payment
            }])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_expenses], ignore_index=True)
            st.success("✅ Expense Added!")


#=============Main Panel:Expense Table=============
# create 3 columns
# column1: Total Spent
# column2: Daily Average
# column3: Top Category

#st.session_state.expenses.groupby('Category')["Amount"].sum().idxmax()

col1, col2, col3 = st.columns(3)
with col1:
    total_spent = st.session_state.expenses['Amount'].sum()
    # Only calculate delta if there are expenses
    if len(st.session_state.expenses) > 0:
        last_amount = st.session_state.expenses['Amount'].iloc[-1]
        st.metric("Total Spent", f"${total_spent:.2f}", delta=f"${last_amount:.2f} last")
    else:
        st.metric("Total Spent", f"${total_spent:.2f}")

with col2:
    if len(st.session_state.expenses) > 0:
        unique_days = st.session_state.expenses['Date'].nunique()
        avg_daily = total_spent / unique_days
        st.metric("Daily Average", f"${avg_daily:.2f}")
    else:
        st.metric("Daily Average", "$0.00")

with col3:
    if len(st.session_state.expenses) > 0:
        top_category = st.session_state.expenses.groupby("Category")["Amount"].sum().idxmax()
        st.metric("Top Category", f"{category_emojis.get(top_category, '')} {top_category}")
    else:
        st.metric("Top Category", "No data")

#=============Editable Expense Table with column config=============
st.subheader("🗃️ Your Expenses (Editable)")

edited_df = st.data_editor(
    st.session_state.expenses,
    column_config={
        "Date": st.column_config.DateColumn("Date", format="MM/DD/YYYY", width="small"),
        "Category": st.column_config.SelectboxColumn("Category", options=list(Category_Emojis.keys()),
                                                     required=True, width="medium"),
        "Amount": st.column_config.NumberColumn("Amount ($)", min_value=0.01, max_value=10000.0,
                                                step=0.01, format="$%.2f", width="small"),
        "Description": st.column_config.TextColumn("Description", width="large"),
        "Payment Method": st.column_config.SelectboxColumn("Payment Method",
                                                           options=['Credit', 'Cash','Debit', 'PayPal', 'Crypto'],
                                                           width="medium")

    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic"
)

st.session_state.expenses = edited_df

#=============Expanse Analysis=============
st.markdown("---")
st.subheader("📊 Spending Analysis")

tab1, tab2, tab3 = st.tabs(["By Category", "Timeline", "Payment Method"])

with tab1:
    category_summery = edited_df.groupby("Category")["Amount"].sum().reset_index()
    category_summery["Percentage"] = (category_summery['Amount'] / category_summery['Amount'].sum() * 100).round(1)
    category_summery['Emoji'] = category_summery['Category'].map(Category_Emojis)
    category_summery['Display'] = category_summery['Emoji'] + "" + category_summery['Category']

    st.dataframe(
        category_summery,
        column_config={
            "Display": "Category",
            "Amount": st.column_config.NumberColumn("Total Spent", format="$%.2f"),
            "Percentage": st.column_config.ProgressColumn(
                "Budget Usage",
                format="%.2f%%",
                min_value=0,
                max_value=100,
            )
        },
        hide_index=True,
    )

with tab2:
    daily = edited_df.groupby('Date')['Amount'].sum().reset_index()
    st.line_chart(daily.set_index('Date')['Amount'])

with tab3:
    payment_summery = edited_df.groupby("Payment Method")['Amount'].sum().reset_index()
    st.bar_chart(payment_summery.set_index("Payment Method")['Amount'])


#=============Export Functionality=============
st.markdown("---")
left_col, right_col = st.columns([1,1], gap="large")

with left_col:
    if len(edited_df) > 0:
        csv = edited_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📩📥Download CSV",
            data=csv,
            file_name=f"expenses_{datetime.date.today()}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=False
        )

with right_col:

    if st.button("🧹 Clear All Expanses", use_container_width=False):
        st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description", "Payment Method"])
        st.rerun()


print(f"Streamlit: {st.__version__}")
print(f"Pandas: {pd.__version__}")

