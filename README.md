# NSE Market Overview & Trading Tool 📊🚀

## 📖 Project Vision & Objective

**Objective:**  
To build a **professional-grade, real-time stock analysis dashboard** specifically tailored for Indian retail traders. The goal was to move beyond simple data display and create a tool that actively assists in decision-making through **psychological logic (Trader Zone)** and **AI-powered insights**.

**Vision:**  
Empower traders by fusing **institutional-grade data** with **behavioral finance**. We wanted a platform that doesn't just show prices, but asks: *"How are you feeling today?"* and tailors the experience (Safe vs. Risky, Bullish vs. Bearish) to match the trader's mindset.

---

## 🛠 Technology Stack

This project was built using a modern, Python-centric stack designed for speed and interactivity:

*   **Core Framework:** `Streamlit` (for rapid, interactive web UI)
*   **Data Processing:** `Pandas`, `NumPy` (for financial calculations)
*   **Data Source:** `NSEPython` & `yfinance` (Real-time Indian stock market data)
*   **Visualization:** `Plotly` (Interactive charts), `Matplotlib` (Static visualizations)
*   **AI Integration:** `OpenAI` / Custom `n8n` Webhook (via `requests`)
*   **Styling:** Custom CSS (Liquid Glass effects, Apple-style animations)
*   **Deployment:** Streamlit Community Cloud / GitHub

---

## ✨ Key Features

1.  **⚡ Trader Zone (Psychological Filtering):**
    *   A unique onboarding wizard ("Trader Mindset") that filters stocks based on your view (**Bullish/Bearish**) and risk appetite (**Safe/Risky**).
    *   **Persona Mapping:** Assigns you a trading persona (e.g., *"The Visionary"*, *"The Hedge Fund Manager"*) with tailored quotes and visuals.

2.  **💰 Capital & Leverage Calculator:**
    *   Real-time calculator to see your **Buying Power** (4x Broker Margin).
    *   Calculates **Estimated Profit** and **Stop Loss Risk** based on live resistance/support levels.
    *   Displays "Projected Invest", "Projected Return", and "Projected Loss" dynamically.

3.  **🤖 AI Trading Assistant (Stocky):**
    *   A floating chatbot (Robot Icon) that provides market insights.
    *   **Voice Input Support:** Talk to your dashboard using the microphone button.
    *   **Context Aware:** Can access the latest market data shown on screen to answer questions like *"Analyze the top gainers"*.

4.  **📈 Global Market Overview:**
    *   Live "Top Gainers" and "Top Losers" tables.
    *   Conditional formatting for immediate trend recognition (Green/Red coding).

---

## 🧩 Challenges & Solutions

### 1. **The "Dark Mode" Crisis 🌑**
*   **Challenge:** The app looked perfect in Light Mode, but Streamlit's auto-dark mode caused input fields to disappear (black text on black background) and gradients to look muddy.
*   **Solution:** We enforced a **Strict Light Mode** policy using `.streamlit/config.toml` and aggressive CSS overrides (`!important`) to ensure a premium, consistent "Corporate" look regardless of the user's system settings.

### 2. **Mobile Responsiveness 📱**
*   **Challenge:** The Chat Interface (Input + Mic + Send buttons) was breaking on mobile, with buttons stacking vertically and taking up too much space.
*   **Solution:** We implemented a custom CSS Flexbox container with media queries (`@media (max-width: 640px)`) to force the input capsule into a single, sleek horizontal row, ensuring the Mic and Send buttons remain accessible on small screens.

### 3. **Real-Time Data Latency ⏱️**
*   **Challenge:** Fetching data for 50+ tickers sequentially was too slow.
*   **Solution:** We implemented `st.cache_data` with a smart refresh logic and optimized the data fetching pipeline to batch requests where possible, adding a "Radar Scanner" loading animation to keep the user engaged during fetches.

### 4. **Complex UI Logic (Trader Zone) 🧠**
*   **Challenge:** Creating a multi-step "Wizard" inside a single-page app without page reloads.
*   **Solution:** Utilized `st.dialog` (Modals) and `st.session_state` to track the user's journey (Step 1: View -> Step 2: Risk -> Result) without losing context or refreshing the entire app.

---

## 🚀 How to Run Locally

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/your-username/nse-stock-website.git
    cd nse-stock-website
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run App:**
    ```bash
    streamlit run app.py
    ```

---

*Built with ❤️ by Ritesh Singh Bisht*
