import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Expense Splitter Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }
    .credit-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .debt-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .settled-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .settlement-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'expense_history' not in st.session_state:
    st.session_state.expense_history = []

def calculate_split(total_amount, people_data):
    """Calculate expense split and settlements"""
    num_people = len(people_data)
    per_person = total_amount / num_people
    
    # Calculate balances
    balances = []
    total_paid = 0
    
    for person in people_data:
        name = person['name']
        paid = person['contribution']
        total_paid += paid
        balance = paid - per_person
        
        status = 'settled'
        if balance > 0.01:
            status = 'credit'
        elif balance < -0.01:
            status = 'debt'
        
        balances.append({
            'name': name,
            'paid': paid,
            'should_pay': per_person,
            'balance': balance,
            'status': status
        })
    
    # Calculate settlements (minimize transactions)
    creditors = sorted([b for b in balances if b['balance'] > 0.01], 
                      key=lambda x: x['balance'], reverse=True)
    debtors = sorted([b for b in balances if b['balance'] < -0.01], 
                     key=lambda x: x['balance'])
    
    settlements = []
    creditors = [{**c} for c in creditors]
    debtors = [{**d} for d in debtors]
    
    ci, di = 0, 0
    while ci < len(creditors) and di < len(debtors):
        amount = min(creditors[ci]['balance'], -debtors[di]['balance'])
        settlements.append({
            'from': debtors[di]['name'],
            'to': creditors[ci]['name'],
            'amount': amount
        })
        creditors[ci]['balance'] -= amount
        debtors[di]['balance'] += amount
        
        if abs(creditors[ci]['balance']) < 0.01:
            ci += 1
        if abs(debtors[di]['balance']) < 0.01:
            di += 1
    
    return {
        'per_person': per_person,
        'total_paid': total_paid,
        'balances': balances,
        'settlements': settlements,
        'is_balanced': abs(total_paid - total_amount) < 0.01
    }

def export_to_text(total_amount, results, expense_name):
    """Export results to formatted text"""
    text = f"{'='*50}\n"
    text += f"💰 EXPENSE SPLIT SUMMARY\n"
    text += f"{'='*50}\n\n"
    text += f"Expense: {expense_name}\n"
    text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += f"Total Amount: ₹{total_amount:.2f}\n"
    text += f"Per Person: ₹{results['per_person']:.2f}\n"
    text += f"Total Paid: ₹{results['total_paid']:.2f}\n\n"
    
    text += f"{'='*50}\n"
    text += f"📊 INDIVIDUAL BALANCES\n"
    text += f"{'='*50}\n\n"
    
    for balance in results['balances']:
        if balance['status'] == 'credit':
            text += f"✅ {balance['name']}:\n"
            text += f"   Paid: ₹{balance['paid']:.2f}\n"
            text += f"   Should Pay: ₹{balance['should_pay']:.2f}\n"
            text += f"   Gets Back: ₹{balance['balance']:.2f}\n\n"
        elif balance['status'] == 'debt':
            text += f"❌ {balance['name']}:\n"
            text += f"   Paid: ₹{balance['paid']:.2f}\n"
            text += f"   Should Pay: ₹{balance['should_pay']:.2f}\n"
            text += f"   Owes: ₹{abs(balance['balance']):.2f}\n\n"
        else:
            text += f"⚖️ {balance['name']}:\n"
            text += f"   Paid: ₹{balance['paid']:.2f}\n"
            text += f"   Status: Settled\n\n"
    
    if results['settlements']:
        text += f"{'='*50}\n"
        text += f"💸 SETTLEMENT INSTRUCTIONS\n"
        text += f"{'='*50}\n\n"
        
        for i, settlement in enumerate(results['settlements'], 1):
            text += f"{i}. {settlement['from']} → {settlement['to']}: ₹{settlement['amount']:.2f}\n"
    
    return text

# Main App
st.title("💰 Expense Splitter Pro")
st.markdown("### Split bills fairly and efficiently with advanced features")

# Sidebar for additional features
with st.sidebar:
    st.header("⚙️ Settings & Features")
    
    # Currency selector
    currency = st.selectbox(
        "Currency",
        ["₹ INR", "$ USD", "€ EUR", "£ GBP", "¥ JPY"],
        index=0
    )
    currency_symbol = currency.split()[0]
    
    # Theme toggle
    st.markdown("---")
    st.subheader("📊 Statistics")
    if st.session_state.expense_history:
        total_expenses = len(st.session_state.expense_history)
        total_amount_all = sum(exp['total_amount'] for exp in st.session_state.expense_history)
        st.metric("Total Expenses Tracked", total_expenses)
        st.metric("Total Amount Managed", f"{currency_symbol}{total_amount_all:,.2f}")
    else:
        st.info("No expenses tracked yet")
    
    st.markdown("---")
    st.subheader("💾 Export Options")
    export_format = st.radio("Export Format", ["Text", "JSON", "CSV"])
    
    st.markdown("---")
    st.subheader("📖 Quick Guide")
    st.markdown("""
    1. Enter expense name & amount
    2. Add number of people
    3. Enter names & contributions
    4. View instant calculations
    5. Export & share results
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Expense Details")
    
    # Expense name
    expense_name = st.text_input(
        "Expense Name",
        placeholder="e.g., Dinner at Restaurant, Movie Tickets, Rent",
        help="Give your expense a descriptive name"
    )
    
    # Total amount and number of people
    subcol1, subcol2 = st.columns(2)
    
    with subcol1:
        total_amount = st.number_input(
            f"Total Amount ({currency_symbol})",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            help="Enter the total expense amount"
        )
    
    with subcol2:
        num_people = st.number_input(
            "Number of People",
            min_value=1,
            max_value=50,
            value=2,
            step=1,
            help="How many people are splitting this expense?"
        )

with col2:
    st.subheader("📅 Expense Info")
    st.info(f"**Date:** {datetime.now().strftime('%d %B %Y')}")
    st.info(f"**Time:** {datetime.now().strftime('%I:%M %p')}")
    if total_amount > 0 and num_people > 0:
        st.success(f"**Per Person:** {currency_symbol}{total_amount/num_people:.2f}")

# Dynamic people input
if num_people > 0:
    st.markdown("---")
    st.subheader("👥 People & Contributions")
    
    # Split type selector
    split_type = st.radio(
        "Split Type",
        ["Equal Split", "Custom Contributions"],
        horizontal=True,
        help="Choose how to split the expense"
    )
    
    people_data = []
    
    if split_type == "Equal Split":
        st.info("💡 Each person will pay equally. Just add their names!")
        
        # Create columns for better layout
        cols = st.columns(min(3, num_people))
        for i in range(num_people):
            with cols[i % len(cols)]:
                name = st.text_input(
                    f"Person {i+1}",
                    value=f"Person {i+1}",
                    key=f"name_{i}",
                    placeholder="Enter name"
                )
                people_data.append({
                    'name': name,
                    'contribution': 0.0
                })
    else:
        st.warning("⚠️ Make sure total contributions match the total amount!")
        
        # Create expandable sections for each person
        for i in range(num_people):
            with st.expander(f"👤 Person {i+1}", expanded=True):
                pcol1, pcol2 = st.columns(2)
                with pcol1:
                    name = st.text_input(
                        "Name",
                        value=f"Person {i+1}",
                        key=f"custom_name_{i}",
                        placeholder="Enter name"
                    )
                with pcol2:
                    contribution = st.number_input(
                        f"Amount Paid ({currency_symbol})",
                        min_value=0.0,
                        value=0.0,
                        step=0.01,
                        key=f"contribution_{i}",
                        format="%.2f"
                    )
                people_data.append({
                    'name': name,
                    'contribution': contribution
                })
    
    # Calculate button
    st.markdown("---")
    col_calc1, col_calc2, col_calc3 = st.columns([1, 1, 1])
    
    with col_calc2:
        calculate_btn = st.button("🔢 Calculate Split", use_container_width=True, type="primary")
    
    # Perform calculations
    if calculate_btn or (total_amount > 0 and split_type == "Equal Split"):
        if total_amount <= 0:
            st.error("❌ Please enter a valid total amount!")
        elif not expense_name:
            st.warning("⚠️ Please enter an expense name!")
        else:
            # For equal split, set contributions
            if split_type == "Equal Split":
                per_person = total_amount / num_people
                for person in people_data:
                    person['contribution'] = per_person
            
            results = calculate_split(total_amount, people_data)
            
            # Display results
            st.markdown("---")
            st.markdown("## 📊 Results & Analysis")
            
            # Summary metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric(
                    "Total Amount",
                    f"{currency_symbol}{total_amount:.2f}",
                    delta=None
                )
            
            with metric_col2:
                st.metric(
                    "Per Person",
                    f"{currency_symbol}{results['per_person']:.2f}",
                    delta=None
                )
            
            with metric_col3:
                st.metric(
                    "Total Paid",
                    f"{currency_symbol}{results['total_paid']:.2f}",
                    delta=f"{results['total_paid'] - total_amount:.2f}" if abs(results['total_paid'] - total_amount) > 0.01 else "Balanced"
                )
            
            with metric_col4:
                num_settlements = len(results['settlements'])
                st.metric(
                    "Transactions",
                    num_settlements,
                    delta=None
                )
            
            # Balance warning
            if not results['is_balanced']:
                st.warning(f"⚠️ **Balance Mismatch:** Total paid ({currency_symbol}{results['total_paid']:.2f}) doesn't match total amount ({currency_symbol}{total_amount:.2f}). Difference: {currency_symbol}{abs(results['total_paid'] - total_amount):.2f}")
            else:
                st.success("✅ **Perfectly Balanced!** All contributions match the total amount.")
            
            # Individual balances
            st.markdown("### 💳 Individual Balances")
            
            bal_cols = st.columns(min(3, len(results['balances'])))
            for idx, balance in enumerate(results['balances']):
                with bal_cols[idx % len(bal_cols)]:
                    if balance['status'] == 'credit':
                        st.markdown(f"""
                        <div class="credit-card">
                            <h3>✅ {balance['name']}</h3>
                            <p style="font-size: 14px; opacity: 0.9;">Paid: {currency_symbol}{balance['paid']:.2f}</p>
                            <p style="font-size: 14px; opacity: 0.9;">Should Pay: {currency_symbol}{balance['should_pay']:.2f}</p>
                            <h2 style="margin-top: 10px;">+{currency_symbol}{balance['balance']:.2f}</h2>
                            <p style="font-size: 12px; opacity: 0.8;">Gets Back</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif balance['status'] == 'debt':
                        st.markdown(f"""
                        <div class="debt-card">
                            <h3>❌ {balance['name']}</h3>
                            <p style="font-size: 14px; opacity: 0.9;">Paid: {currency_symbol}{balance['paid']:.2f}</p>
                            <p style="font-size: 14px; opacity: 0.9;">Should Pay: {currency_symbol}{balance['should_pay']:.2f}</p>
                            <h2 style="margin-top: 10px;">-{currency_symbol}{abs(balance['balance']):.2f}</h2>
                            <p style="font-size: 12px; opacity: 0.8;">Owes</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="settled-card">
                            <h3>⚖️ {balance['name']}</h3>
                            <p style="font-size: 14px; opacity: 0.9;">Paid: {currency_symbol}{balance['paid']:.2f}</p>
                            <p style="font-size: 14px; opacity: 0.9;">Should Pay: {currency_symbol}{balance['should_pay']:.2f}</p>
                            <h2 style="margin-top: 10px;">SETTLED</h2>
                            <p style="font-size: 12px; opacity: 0.8;">No Action Needed</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Settlement instructions
            if results['settlements']:
                st.markdown("---")
                st.markdown("### 💸 Settlement Instructions")
                st.info(f"✨ Optimized to **{len(results['settlements'])} transaction(s)** only!")
                
                for i, settlement in enumerate(results['settlements'], 1):
                    st.markdown(f"""
                    <div class="settlement-card">
                        <h3>Step {i}</h3>
                        <p style="font-size: 18px; font-weight: bold;">
                            {settlement['from']} → {settlement['to']}
                        </p>
                        <h2 style="margin-top: 10px;">{currency_symbol}{settlement['amount']:.2f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("🎉 No settlements needed! Everyone has paid their share.")
            
            # Export section
            st.markdown("---")
            st.markdown("### 📤 Export Results")
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                text_export = export_to_text(total_amount, results, expense_name)
                st.download_button(
                    label="📄 Download as Text",
                    data=text_export,
                    file_name=f"expense_split_{expense_name.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with export_col2:
                json_export = json.dumps({
                    'expense_name': expense_name,
                    'date': datetime.now().isoformat(),
                    'total_amount': total_amount,
                    'currency': currency,
                    'results': results
                }, indent=2)
                st.download_button(
                    label="📋 Download as JSON",
                    data=json_export,
                    file_name=f"expense_split_{expense_name.replace(' ', '_')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with export_col3:
                df = pd.DataFrame(results['balances'])
                csv_export = df.to_csv(index=False)
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv_export,
                    file_name=f"expense_split_{expense_name.replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Add to history
            if st.button("💾 Save to History", use_container_width=False):
                st.session_state.expense_history.append({
                    'expense_name': expense_name,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_amount': total_amount,
                    'num_people': num_people,
                    'results': results
                })
                st.success("✅ Saved to history!")
                st.rerun()

# Expense history
if st.session_state.expense_history:
    st.markdown("---")
    st.markdown("## 📜 Expense History")
    
    for i, expense in enumerate(reversed(st.session_state.expense_history), 1):
        with st.expander(f"📌 {expense['expense_name']} - {expense['date']}"):
            hist_col1, hist_col2, hist_col3 = st.columns(3)
            with hist_col1:
                st.metric("Total Amount", f"{currency_symbol}{expense['total_amount']:.2f}")
            with hist_col2:
                st.metric("Number of People", expense['num_people'])
            with hist_col3:
                st.metric("Transactions", len(expense['results']['settlements']))
    
    if st.button("🗑️ Clear History"):
        st.session_state.expense_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Expense Splitter Pro</strong> v2.0 | Built with ❤️ using Python & Streamlit</p>
    <p>Split expenses fairly, save time, and keep everyone happy! 🎉</p>
</div>
""", unsafe_allow_html=True)