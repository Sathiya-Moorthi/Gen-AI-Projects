import streamlit as st
from api_client import get_supported_currencies, convert_currency

# Page Config
st.set_page_config(
    page_title="Global Currency Converter",
    page_icon="💱",
    layout="centered"
)

# Inject Custom CSS
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# --- Main UI ---
st.markdown("<h1 style='text-align: center;'>💱 Currency Converter</h1>", unsafe_allow_html=True)

# Fetch data
currencies = get_supported_currencies()

if not currencies:
    st.warning("⚠️ Backend is offline. Retrying connection...")
else:
    # UI Container
    with st.container(border=True):
        amount = st.number_input("Amount", min_value=0.01, value=1.00, step=10.0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            from_curr = st.selectbox("From", currencies, index=currencies.index("USD") if "USD" in currencies else 0)
            
        with col2:
            to_curr = st.selectbox("To", currencies, index=currencies.index("INR") if "INR" in currencies else 0)

        # Conversion Trigger
        # We use a button, but you could also just let it run on change
        if st.button("Convert Now 🔄"):
            with st.spinner("Fetching rates..."):
                result = convert_currency(from_curr, to_curr, amount)
                
                if result.get("success"):
                    data = result["data"]
                    converted = data["converted_amount"]
                    
                    # Display Result
                    st.markdown("---")
                    st.markdown(f'<div class="sub-text">{amount} {from_curr} = </div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="result-text">{converted} {to_curr}</div>', unsafe_allow_html=True)
                else:
                    st.error(result.get("error", "Unknown error occurred"))
        

    # Footer
    st.markdown(
        """
        <div style='text-align: center; color: #888; margin-top: 20px;'>
            <small>Powered by Flask REST API & Streamlit</small>
        </div>
        """, 
        unsafe_allow_html=True
    )