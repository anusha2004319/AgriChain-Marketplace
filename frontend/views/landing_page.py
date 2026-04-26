import streamlit as st

def show_landing_page():
    st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .hero-container { text-align: center; padding: 3rem 1rem 1rem 1rem; }
    .hero-title { font-size: 3.8rem; font-weight: 800; color: #1e3932; margin-bottom: 0.5rem; line-height: 1.1; }
    .hero-subtitle { font-size: 1.3rem; color: #444; margin-bottom: 2.5rem; max-width: 850px; margin-left: auto; margin-right: auto; }
    .trust-bar { 
        display: flex; justify-content: center; gap: 40px; margin-bottom: 3rem; 
        color: #7f8c8d; font-weight: 600; font-size: 0.9rem; text-transform: uppercase;
        flex-wrap: wrap;
    }
    .section-header { text-align: center; font-size: 2.5rem; font-weight: 700; color: #1e3932; margin-bottom: 2rem; }
    .benefit-card h3 { color: #2e7d32; margin-bottom: 1rem; }
    .comp-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    .comp-table th { background-color: #1e3932; color: white; padding: 15px; text-align: left; }
    .comp-table td { padding: 15px; border-bottom: 1px solid #eee; }
    .highlight { background-color: #e8f5e9; font-weight: bold; color: #1b5e20; }
    .testimonial { border-left: 4px solid #2ecc71; padding-left: 15px; font-style: italic; color: #555; background: #f9f9f9; padding: 15px; border-radius: 0 8px 8px 0; }
    button[kind="secondary"] { border: none !important; background: transparent !important; color: #bdc3c7 !important; box-shadow: none !important; padding: 0 !important; font-size: 0.8rem !important; }
    button[kind="secondary"]:hover { color: #7f8c8d !important; text-decoration: underline !important; background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Direct from Farm Marketplace <br>Powered by AI Pricing</div>
        <div class="hero-subtitle">Farmers earn up to 30% more. Consumers pay less for fresher produce—without middlemen.</div>
    </div>
    """, unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if st.button(" Get Started Now", type="primary", use_container_width=True):
    # Setting user_role to 'selecting' breaks the loop and moves to the bridge page
           st.session_state.user_role = "selecting" 
           st.session_state.auth_step = "role_selection"
           st.rerun()
        
        st.markdown("<div style='text-align: center; color: #7f8c8d; font-size: 0.9rem; margin-top: 10px;'>No signup required to browse • Start selling in under 2 minutes</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="trust-bar">
        <span>📍 1,200+ Farmers Across India</span>
        <span>💰 ₹2.5 Cr+ Produce Traded</span>
        <span>⭐ 4.9/5 User Rating</span>
    </div>
    """, unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="section-header">How AgriChain Works</div>', unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown("### 📝 1. List\n**List produce in minutes.** <br>Upload crops and availability directly.", unsafe_allow_html=True)
        with s2:
            st.markdown("### 🤖 2. Price\n**AI sets optimal prices.** <br>Automatically maximize margins based on market data.", unsafe_allow_html=True)
        with s3:
            st.markdown("### 🤝 3. Trade\n**Buyers purchase directly.** <br>Eliminate middlemen and hidden fees.", unsafe_allow_html=True)
        with s4:
            st.markdown("### 💳 4. Settle\n**Instant settlements.** <br>Secure payments and automated bank transfers.", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Empowering the Entire Ecosystem</div>', unsafe_allow_html=True)
    v1, v2 = st.columns(2)
    with v1:
        with st.container():
            st.markdown("""
            <div class="benefit-card">
                <h3>🌾 For Farmers</h3>
                <ul>
                    <li><b>Earn 20–30% higher margins</b> per crop</li>
                    <li>AI-driven real-time pricing recommendations</li>
                    <li>Direct access to a national network of verified buyers</li>
                    <li>Predictive demand forecasting to reduce waste</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    with v2:
        with st.container():
            st.markdown("""
            <div class="benefit-card">
                <h3>🛒 For Buyers</h3>
                <ul>
                    <li><b>Farm-fresh produce</b> harvested to order</li>
                    <li>Transparent, fair-market pricing via AI</li>
                    <li>Support local agricultural communities directly</li>
                    <li>Better quality at significantly lower costs</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="section-header">Real-Time Market Intelligence</div>', unsafe_allow_html=True)
        p1, p2 = st.columns([2, 1])
        with p1:
            st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop")
        with p2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.success("**📈 Live Price Trends**\n\nMonitor daily fluctuations and adjust supply instantly.")
            st.info("**🎯 Demand Signals**\n\nSee what buyers are searching for in your region.")
            st.warning("**💰 Performance Tracking**\n\nComprehensive history of your sales and earnings.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="section-header">Why AgriChain Wins</div>', unsafe_allow_html=True)
        st.markdown("""
        <table class="comp-table">
            <tr><th>Feature</th><th>Traditional Market</th><th class="highlight">AgriChain (AI)</th></tr>
            <tr><td>Supply Chain</td><td>3-5 Middlemen</td><td class="highlight">Direct Connection</td></tr>
            <tr><td>Pricing</td><td>Buyer-Dictated / Static</td><td class="highlight">AI-Optimized / Dynamic</td></tr>
            <tr><td>Reach</td><td>Limited Local Mandis</td><td class="highlight">National Digital Reach</td></tr>
            <tr><td>Data</td><td>None / Historical</td><td class="highlight">Real-time Predictive</td></tr>
        </table>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("## Join the Future of Agricultural Commerce")
        st.markdown("Experience a marketplace built for transparency and profit.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        cl, cm, cr = st.columns([1, 2, 1])
        with cm:
            if st.button("🌟 Join AgriChain Today", key="final_cta_btn", type="primary", use_container_width=True):
                # 1. We set the role to "selecting" so app.py knows we left the Hero page
                st.session_state.user_role = "selecting" 
                # 2. We set the step to role_selection
                st.session_state.auth_step = "role_selection"
                # 3. We rerun to refresh the screen and show the two big cards!
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    with st.expander("Explore AgriChain: About • Privacy • Terms • Contact", expanded=False):
        t1, t2, t3, t4 = st.tabs(["🌾 About Us", "🔒 Privacy Policy", "⚖️ Terms & Conditions", "📞 Contact Us"])
        
        with t1:
            st.write("**AgriChain** is a Direct-from-Farm marketplace. We empower farmers by removing middlemen and using AI to provide fair, real-time pricing. Consumers get fresher produce at significantly lower costs.")
        with t2:
            st.write("**Privacy Policy:** Your data is strictly secured. We use end-to-end encryption for all transactions. Verified farmer details are only used for marketplace transparency and are never sold to third parties.")
        with t3:
            st.write("**Terms of Service:** By using AgriChain, you agree to fair-trade practices. Misuse of the platform or fraudulent listings will result in immediate account termination.")
        with t4:
            st.write("**Email:** support@agrichain.com")
            st.write("**Phone:** +91 1800-AGRI-FARM")
            st.write("**Office:** AgriChain Headquarters, Cyber City, Gurugram")

    st.markdown("<br>", unsafe_allow_html=True)
    bottom_left, bottom_right = st.columns([10, 1])
    
    with bottom_left: 
        st.caption("© 2026 AgriChain Marketplace. Empowering farmers via Machine Learning.")
        
    with bottom_right:
        st.markdown("""
        <style>
        div[data-testid="column"]:nth-of-type(2) button {
            border: none !important;
            background: transparent !important;
            color: #b0b0b0 !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        div[data-testid="column"]:nth-of-type(2) button:hover {
            color: #333 !important;
            text-decoration: underline !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("Admin", key="landing_admin_btn", use_container_width=True):
            st.session_state.user_role = "Admin" 
            st.session_state.auth_step = "login"
            st.rerun()