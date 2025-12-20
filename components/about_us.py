import streamlit as st
import streamlit.components.v1 as components

def show_about_us():
    """Professional About Us page with modern design."""
    
    # Generative Art Background Animation (p5.js) - Inject into parent document
    components.html("""
        <script>
            (function() {
                const doc = window.parent.document;
                const containerId = 'about-bg-canvas';
                
                // Check if already injected
                if (doc.getElementById(containerId)) return;
                
                // Load p5.js if not already loaded
                if (!doc.getElementById('p5-lib')) {
                    const script = doc.createElement('script');
                    script.id = 'p5-lib';
                    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js';
                    script.onload = initAnimation;
                    doc.head.appendChild(script);
                } else {
                    initAnimation();
                }
                
                function initAnimation() {
                    // Create container
                    const container = doc.createElement('div');
                    container.id = containerId;
                    Object.assign(container.style, {
                        position: 'fixed',
                        top: '0',
                        left: '0',
                        width: '100vw',
                        height: '100vh',
                        zIndex: '0',
                        pointerEvents: 'none',
                        overflow: 'hidden'
                    });
                    doc.body.insertBefore(container, doc.body.firstChild);
                    
                    // Initialize p5 sketch
                    new window.parent.p5(function(p) {
                        p.setup = function() {
                            let canvas = p.createCanvas(p.windowWidth, p.windowHeight);
                            canvas.parent(containerId);
                            canvas.style('position', 'fixed');
                            canvas.style('top', '0');
                            canvas.style('left', '0');
                        };

                        p.draw = function() {
                            p.clear();
                            p.background(248, 249, 250, 200);
                            p.translate(p.width / 2, p.height / 2);
                            
                            p.noFill();
                            p.stroke(102, 126, 234, 20);
                            p.strokeWeight(1);

                            const time = p.frameCount * 0.008;
                            const numLines = 50; 
                            const numPoints = 120; 

                            for (let i = 0; i < numLines; i++) {
                                const linePhase = (i / numLines) * p.TWO_PI; 

                                p.beginShape();
                                for (let j = 0; j <= numPoints; j++) {
                                    const pointPhase = j / numPoints;
                                    const y = p.map(pointPhase, 0, 1, -p.height / 2.5, p.height / 2.5);
                                    const envelope = p.sin(pointPhase * p.PI);
                                    const wave1 = p.sin(time + linePhase) * 60;
                                    const wave2 = p.sin(pointPhase * 8 + time * 2) * 40;
                                    const centerComplexity = p.pow(p.cos(pointPhase * p.PI - p.HALF_PI), 2) * 100;
                                    const wave3 = p.cos(linePhase * 4 - time) * centerComplexity;
                                    const x = envelope * (wave1 + wave2 + wave3 + 60);
                                    p.vertex(-x, y); 
                                }
                                p.endShape();

                                p.beginShape();
                                for (let j = 0; j <= numPoints; j++) {
                                    const pointPhase = j / numPoints;
                                    const y = p.map(pointPhase, 0, 1, -p.height / 2.5, p.height / 2.5);
                                    const envelope = p.sin(pointPhase * p.PI);
                                    const wave1 = p.sin(time + linePhase) * 60;
                                    const wave2 = p.sin(pointPhase * 8 + time * 2) * 40;
                                    const centerComplexity = p.pow(p.cos(pointPhase * p.PI - p.HALF_PI), 2) * 100;
                                    const wave3 = p.cos(linePhase * 4 - time) * centerComplexity;
                                    const x = envelope * (wave1 + wave2 + wave3 + 60);
                                    p.vertex(x, y); 
                                }
                                p.endShape();
                            }
                        };

                        p.windowResized = function() {
                            p.resizeCanvas(p.windowWidth, p.windowHeight);
                        };
                    });
                }
            })();
        </script>
    """, height=0, width=0)
    
    # Custom CSS for About Us page
    st.markdown("""
        <style>
        /* Make Streamlit containers transparent to show animation */
        .stApp, 
        .stAppViewContainer, 
        .stMain,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .main {
            background-color: transparent !important;
            background: transparent !important;
        }
        
        /* About Us Hero Section */
        .about-hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            margin-bottom: 40px;
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .about-hero::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
            animation: pulse 4s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .about-hero h1 {
            color: white !important;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }
        
        .about-hero p {
            color: rgba(255,255,255,0.9) !important;
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }
        
        /* Stats Cards */
        .stat-card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.12);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stat-label {
            color: #64748b;
            font-size: 0.95rem;
            font-weight: 500;
            margin-top: 8px;
        }
        
        /* Mission Section */
        .mission-section {
            background: #f8fafc;
            border-radius: 20px;
            padding: 50px 40px;
            margin: 40px 0;
        }
        
        .mission-section h2 {
            color: #0f172a !important;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 20px;
        }
        
        .mission-section p {
            color: #475569 !important;
            font-size: 1.1rem;
            line-height: 1.8;
        }
        
        /* Feature Cards Row - FORCE Equal Heights */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            align-items: stretch !important;
        }
        
        [data-testid="stColumn"] {
            display: flex !important;
            flex-direction: column !important;
        }
        
        [data-testid="stColumn"] > div {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
        }
        
        [data-testid="stColumn"] > div > div {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
        }
        
        /* Feature Cards */
        .feature-card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            border: 1px solid #e2e8f0;
            flex: 1 !important;
            min-height: 180px;
            display: flex !important;
            flex-direction: column !important;
            transition: all 0.3s ease;
            box-sizing: border-box;
        }
        
        .feature-card:hover {
            border-color: #667eea;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            flex-shrink: 0;
        }
        
        .feature-title {
            color: #0f172a !important;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 10px;
            flex-shrink: 0;
        }
        
        .feature-desc {
            color: #64748b !important;
            font-size: 0.95rem;
            line-height: 1.6;
            flex: 1 !important;
            min-height: 60px;
        }
        
        /* Team Section */
        .team-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }
        
        .team-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        }
        
        .team-avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
        }
        
        .team-name {
            color: #0f172a !important;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .team-role {
            color: #667eea;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .team-bio {
            color: #64748b !important;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        /* Contact Section */
        .contact-section {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-radius: 20px;
            padding: 50px 40px;
            text-align: center;
            margin-top: 50px;
        }
        
        .contact-section h2 {
            color: white !important;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 15px;
        }
        
        .contact-section p {
            color: rgba(255,255,255,0.7) !important;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }
        
        .contact-btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            padding: 15px 40px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1rem;
            text-decoration: none;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .contact-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
        <div class="about-hero">
            <h1>📈 Trading Tool</h1>
            <p>Empowering traders with real-time NSE market insights, AI-powered analysis, and professional-grade tools.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">50+</div>
                <div class="stat-label">Nifty 50 Stocks</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">Real-time</div>
                <div class="stat-label">Live Market Data</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">AI</div>
                <div class="stat-label">Powered Analysis</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Data Access</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Mission Section
    st.markdown("""
        <div class="mission-section">
            <h2>🎯 Our Mission</h2>
            <p>
                We believe that every trader deserves access to professional-grade market tools. 
                Our platform combines cutting-edge technology with intuitive design to provide 
                real-time NSE market data, technical analysis, and AI-powered insights — all in one place.
                <br><br>
                Whether you're a seasoned trader or just starting your investment journey, 
                Trading Tool is designed to help you make informed decisions with confidence.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("### ✨ What We Offer")
    st.markdown("")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Live Market Data</div>
                <div class="feature-desc">
                    Real-time stock prices, volume, and market indicators directly from NSE. 
                    Stay updated with the latest market movements.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI Assistant (Stocky)</div>
                <div class="feature-desc">
                    Ask questions about stocks, get analysis, and receive AI-powered 
                    recommendations based on current market conditions.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Trader Zone</div>
                <div class="feature-desc">
                    Personalized trading setups based on your market view and risk appetite. 
                    Calculate potential returns with leverage analysis.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    feat_col4, feat_col5, feat_col6 = st.columns(3)
    
    with feat_col4:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Technical Analysis</div>
                <div class="feature-desc">
                    RSI, VWAP, Support/Resistance levels, and trend indicators 
                    to help you identify the best entry and exit points with confidence.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col5:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🏆</div>
                <div class="feature-title">Top Gainers & Losers</div>
                <div class="feature-desc">
                    Quick overview of the day's best and worst performing stocks 
                    to spot trading opportunities at a glance easily.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col6:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🎨</div>
                <div class="feature-title">Modern Interface</div>
                <div class="feature-desc">
                    Clean, intuitive design optimized for both desktop and mobile. 
                    Trade analysis made beautiful and accessible for all.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Team Section
    st.markdown("")
    st.markdown("### 👨‍💻 Meet the Creator")
    st.markdown("")
    
    team_col1, team_col2, team_col3 = st.columns([1, 2, 1])
    
    with team_col2:
        # Use base64 to embed the image directly in HTML for better control
        import base64
        
        # Read the image and convert to base64
        try:
            with open("assets/images/creator_ritesh.jpg", "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            
            st.markdown(f"""
                <style>
                .creator-section {{
                    background: white;
                    border-radius: 24px;
                    padding: 40px 30px;
                    text-align: center;
                    border: 1px solid #e2e8f0;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
                    transition: all 0.3s ease;
                }}
                .creator-section:hover {{
                    transform: translateY(-8px);
                    box-shadow: 0 25px 60px rgba(0,0,0,0.12);
                }}
                .creator-img {{
                    width: 160px;
                    height: 160px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 5px solid transparent;
                    background: linear-gradient(white, white) padding-box,
                                linear-gradient(135deg, #667eea 0%, #764ba2 100%) border-box;
                    margin-bottom: 25px;
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
                }}
                .creator-name {{
                    color: #0f172a !important;
                    font-size: 1.5rem;
                    font-weight: 800;
                    margin-bottom: 8px;
                }}
                .creator-role {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    font-size: 1rem;
                    font-weight: 700;
                    margin-bottom: 20px;
                    display: inline-block;
                }}
                .creator-bio {{
                    color: #64748b !important;
                    font-size: 1rem;
                    line-height: 1.7;
                    max-width: 400px;
                    margin: 0 auto;
                }}
                .creator-socials {{
                    margin-top: 25px;
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                }}
                /* Social Icons */
                .social-icon {{
                    width: 45px;
                    height: 45px;
                    border-radius: 50%;
                    background: #f1f5f9;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.4rem;
                    text-decoration: none;
                    color: #64748b !important;
                    transition: all 0.3s ease;
                }}
                .social-icon:hover {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white !important;
                    transform: translateY(-3px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }}
                </style>
                
                <!-- FontAwesome CDN -->
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                
                <div class="creator-section">
                    <img src="data:image/jpeg;base64,{img_base64}" class="creator-img" alt="Ritesh Singh Bisht">
                    <div class="creator-name">Ritesh Singh Bisht</div>
                    <div class="creator-role">Developer & Data Analyst</div>
                    <div class="creator-bio">
                        Passionate about combining finance and technology to create 
                        tools that empower traders. Building data-driven solutions 
                        with expertise in Python, AI/ML, and financial analysis.
                    </div>
                    <div class="creator-socials">
                        <a href="mailto:workritesh21@gmail.com" class="social-icon" title="Email"><i class="fas fa-envelope"></i></a>
                        <a href="https://www.linkedin.com/in/ritesh-singh-bisht" target="_blank" class="social-icon" title="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
                        <a href="https://github.com/RiteshSinghBisht" target="_blank" class="social-icon" title="GitHub"><i class="fab fa-github"></i></a>
                        <a href="https://ritesh-singh-bisht-portfolio.lovable.app/" target="_blank" class="social-icon" title="Portfolio"><i class="fas fa-globe"></i></a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            # Fallback if image not found
            st.markdown("""
                <div class="creator-section">
                    <div style="font-size: 4rem; margin-bottom: 20px;">👨‍💻</div>
                    <div class="creator-name">Ritesh Singh Bisht</div>
                    <div class="creator-role">Developer & Data Analyst</div>
                    <div class="creator-bio">
                        Passionate about combining finance and technology to create 
                        tools that empower traders. Building data-driven solutions 
                        with expertise in Python, AI/ML, and financial analysis.
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Disclaimer Section
    st.markdown("")
    st.markdown("""
        <style>
            .disclaimer-box {
                background: white;
                border: 1px solid #e2e8f0;
                border-left: 4px solid #f59e0b; /* Warning color accent */
                border-radius: 12px;
                padding: 20px;
                margin-top: 40px;
                margin-bottom: 20px;
                text-align: center;
                color: #64748b;
                font-size: 0.9rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            }
        </style>
        <div class="disclaimer-box">
            <strong style="color: #d97706; display: block; margin-bottom: 8px; font-size: 1rem;">⚠️ Disclaimer</strong>
            This tool is for educational and informational purposes only. 
            The data and analysis provided should not be considered as financial advice. 
            Always do your own research and consult with a qualified financial advisor 
            before making investment decisions. Trading in the stock market involves risk, 
            and past performance is not indicative of future results.
        </div>
    """, unsafe_allow_html=True)
    
    # Contact Section
    st.markdown("""
        <div class="contact-section">
            <h2>💬 Get in Touch</h2>
            <p>Have questions or feedback? We'd love to hear from you!</p>
            <a href="mailto:workritesh21@gmail.com" class="contact-btn">Contact Us</a>
        </div>
    """, unsafe_allow_html=True)
