import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page config
st.set_page_config(page_title="💰 Expense Tracker", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
    .big-metric {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'budget' not in st.session_state:
    st.session_state.budget = 1000.0

# Categories with emojis
CATEGORIES = {
    "🍔 Food & Dining": "#FF6B6B",
    "🚗 Transportation": "#4ECDC4",
    "🏠 Housing": "#45B7D1",
    "💊 Healthcare": "#96CEB4",
    "🎮 Entertainment": "#FFEAA7",
    "🛍️ Shopping": "#DFE6E9",
    "💳 Bills & Utilities": "#74B9FF",
    "✈️ Travel": "#A29BFE",
    "📚 Education": "#FD79A8",
    "💰 Other": "#636E72"
}

# Sidebar - Add Expense
st.sidebar.header("➕ Add New Expense")

with st.sidebar.form("expense_form"):
    expense_name = st.text_input("Description", placeholder="e.g., Lunch at cafe")
    expense_amount = st.number_input("Amount (₹)", min_value=0.01, step=1.0, format="%.2f")
    expense_category = st.selectbox("Category", list(CATEGORIES.keys()))
    expense_date = st.date_input("Date", value=datetime.now())
    
    submitted = st.form_submit_button("💾 Add Expense", use_container_width=True)
    
    if submitted:
        if expense_name.strip():
            new_expense = {
                "name": expense_name,
                "amount": expense_amount,
                "category": expense_category,
                "date": expense_date.strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.expenses.append(new_expense)
            st.success(f"✅ Added ₹{expense_amount:.2f} for {expense_name}")
            st.rerun()
        else:
            st.error("Please enter a description!")

# Sidebar - Budget Settings
st.sidebar.divider()
st.sidebar.header("🎯 Monthly Budget")
new_budget = st.sidebar.number_input("Set Budget (₹)", min_value=0.0, value=st.session_state.budget, step=500.0)
if st.sidebar.button("Update Budget", use_container_width=True):
    st.session_state.budget = new_budget
    st.sidebar.success("Budget updated!")

# Sidebar - Data Management
st.sidebar.divider()
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.expenses = []
        st.rerun()

with col2:
    if st.session_state.expenses:
        expense_data = json.dumps(st.session_state.expenses, indent=2)
        st.download_button(
            label="📥 Export",
            data=expense_data,
            file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

# Main content
st.title("💰 Personal Expense Tracker")
st.markdown("Track your spending, visualize patterns, and stay within budget!")

# Convert to DataFrame
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].astype(float)
    
    # Calculate metrics
    total_spent = df['amount'].sum()
    budget_remaining = st.session_state.budget - total_spent
    budget_percent = (total_spent / st.session_state.budget * 100) if st.session_state.budget > 0 else 0
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
    
    with col2:
        st.metric("🎯 Monthly Budget", f"₹{st.session_state.budget:,.2f}")
    
    with col3:
        st.metric("💵 Remaining", f"₹{budget_remaining:,.2f}", 
                 delta=f"{budget_percent:.1f}% used",
                 delta_color="inverse")
    
    with col4:
        avg_expense = df['amount'].mean()
        st.metric("📊 Avg Expense", f"₹{avg_expense:,.2f}")
    
    # Budget progress bar with surprise!
    if budget_percent > 100:
        st.error(f"⚠️ You've exceeded your budget by ₹{total_spent - st.session_state.budget:.2f}!")
    elif budget_percent > 80:
        st.warning(f"⚡ You've used {budget_percent:.1f}% of your budget. Slow down!")
    else:
        st.success(f"✨ Great job! You've used {budget_percent:.1f}% of your budget.")
    
    st.progress(min(budget_percent / 100, 1.0))
    
    st.divider()
    
    # Visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🏆 Top Expenses", "📝 All Expenses"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Category breakdown
            category_totals = df.groupby('category')['amount'].sum().reset_index()
            category_totals = category_totals.sort_values('amount', ascending=False)
            
            fig_pie = px.pie(
                category_totals, 
                values='amount', 
                names='category',
                title='💳 Spending by Category',
                color='category',
                color_discrete_map=CATEGORIES,
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Top categories bar chart
            fig_bar = px.bar(
                category_totals.head(5),
                x='amount',
                y='category',
                orientation='h',
                title='🔝 Top 5 Categories',
                color='category',
                color_discrete_map=CATEGORIES,
                text='amount'
            )
            fig_bar.update_traces(texttemplate='₹%{text:.2f}', textposition='outside')
            fig_bar.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        # Daily spending trend
        daily_spending = df.groupby('date')['amount'].sum().reset_index()
        daily_spending = daily_spending.sort_values('date')
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=daily_spending['date'],
            y=daily_spending['amount'],
            mode='lines+markers',
            name='Daily Spending',
            line=dict(color='#FF6B6B', width=3),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.2)'
        ))
        
        fig_line.update_layout(
            title='📅 Daily Spending Trend',
            xaxis_title='Date',
            yaxis_title='Amount (₹)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Weekly comparison
        df['week'] = df['date'].dt.isocalendar().week
        weekly_spending = df.groupby('week')['amount'].sum().reset_index()
        
        col1, col2 = st.columns(2)
        with col1:
            if len(weekly_spending) > 1:
                current_week = weekly_spending.iloc[-1]['amount']
                prev_week = weekly_spending.iloc[-2]['amount']
                week_change = current_week - prev_week
                st.metric("📆 This Week", f"₹{current_week:.2f}", 
                         delta=f"₹{week_change:.2f} vs last week")
            else:
                st.metric("📆 This Week", f"₹{weekly_spending.iloc[-1]['amount']:.2f}")
        
        with col2:
            avg_daily = df.groupby('date')['amount'].sum().mean()
            st.metric("📉 Avg Daily Spend", f"₹{avg_daily:.2f}")
    
    with tab3:
        # Top 10 individual expenses
        top_expenses = df.nlargest(10, 'amount')[['name', 'amount', 'category', 'date']]
        
        st.subheader("🏆 Your Biggest Expenses")
        
        for idx, row in top_expenses.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{row['name']}**")
            with col2:
                st.markdown(row['category'])
            with col3:
                st.markdown(f"**₹{row['amount']:.2f}**")
        
        # Surprise insight!
        st.divider()
        most_frequent_cat = df['category'].mode()[0]
        cat_count = len(df[df['category'] == most_frequent_cat])
        st.info(f"💡 **Insight**: You spend most frequently on **{most_frequent_cat}** ({cat_count} transactions)")
    
    with tab4:
        st.subheader("📝 All Expenses")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.multiselect("Filter by Category", options=list(CATEGORIES.keys()), default=list(CATEGORIES.keys()))
        with col2:
            sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Amount (High to Low)", "Amount (Low to High)"])
        
        # Apply filters
        filtered_df = df[df['category'].isin(filter_category)].copy()
        
        # Apply sorting
        if sort_by == "Date (Newest)":
            filtered_df = filtered_df.sort_values('date', ascending=False)
        elif sort_by == "Date (Oldest)":
            filtered_df = filtered_df.sort_values('date', ascending=True)
        elif sort_by == "Amount (High to Low)":
            filtered_df = filtered_df.sort_values('amount', ascending=False)
        else:
            filtered_df = filtered_df.sort_values('amount', ascending=True)
        
        # Display as cards
        for idx, row in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.markdown(f"**{row['name']}**")
                with col2:
                    st.markdown(row['category'])
                with col3:
                    st.markdown(f"**₹{row['amount']:.2f}**")
                with col4:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.expenses = [e for e in st.session_state.expenses if e['timestamp'] != row['timestamp']]
                        st.rerun()
                
                st.caption(f"📅 {row['date'].strftime('%b %d, %Y')}")
                st.divider()

else:
    # Empty state
    st.info("👋 Welcome! Start by adding your first expense using the sidebar.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📝 Track")
        st.write("Add all your daily expenses quickly and easily")
    with col2:
        st.markdown("### 📊 Visualize")
        st.write("See beautiful charts and insights about your spending")
    with col3:
        st.markdown("### 🎯 Budget")
        st.write("Set goals and stay within your monthly budget")

# Footer
st.divider()
st.caption("💡 Tip: All data is stored in your browser session. Export regularly to save your expenses!")