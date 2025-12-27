import streamlit as st
import streamlit.components.v1 as st_components
import time
import requests
import sys
import os

# Add parent dir to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from config import N8N_WEBHOOK_URL
except ImportError:
    N8N_WEBHOOK_URL = ""

def get_ai_response(prompt):
    """Sends prompt to n8n Webhook and returns response."""
    if not N8N_WEBHOOK_URL or "your-n8n-instance" in N8N_WEBHOOK_URL:
        time.sleep(1)
        return "⚠️ Configuration Missing: Please update 'N8N_WEBHOOK_URL' in config.py with your actual n8n Webhook URL."
    
    try:
        # Determine chat session status (new_chat or active_chat)
        current_time = time.time()
        
        if 'last_chat_timestamp' not in st.session_state:
            # First chat ever
            chat_status = "new_chat"
        else:
            # Calculate time difference in minutes
            time_diff_minutes = (current_time - st.session_state['last_chat_timestamp']) / 60
            if time_diff_minutes > 3:
                chat_status = "new_chat"
            else:
                chat_status = "active_chat"
        
        # Update the last chat timestamp
        st.session_state['last_chat_timestamp'] = current_time
        
        payload = {
            "input": prompt,
            "chat_status": chat_status
        }
        
        if 'latest_market_data' in st.session_state:
            df = st.session_state['latest_market_data']
            if not df.empty:
                # Convert to JSON records format for n8n (list of dictionaries)
                stock_records = df.head(50).to_dict('records')
                payload["market_data"] = stock_records
        
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            # Check for empty response
            if not response.text or not response.text.strip():
                return "⚠️ Error: The AI agent returned an empty response. Please check your n8n workflow to ensure the 'Respond to Webhook' node is sending data."

            try:
                data = response.json()
                if isinstance(data, dict):
                    # Look for common output keys
                    return data.get('output', data.get('text', data.get('response', data.get('message', str(data)))))
                elif isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        return first_item.get('output', first_item.get('text', str(first_item)))
                    return str(first_item)
                else:
                    return response.text
            except ValueError:
                # If not JSON, return raw text (we already checked it's not empty)
                return response.text
        else:
            return f"❌ Agent Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

def render_ai_assistant():
    """Professional AI Chat Assistant with robust mobile/desktop support."""
    
    # Session State
    if 'ai_messages' not in st.session_state:
        st.session_state.ai_messages = [
            {"role": "assistant", "content": "Hello! I am Stocky, your Stock Analysis Expert. How can I help you today?"}
        ]
    if 'chat_input_val' not in st.session_state:
        st.session_state.chat_input_val = ""

    # =====================================================
    # FLOATING ROBOT ICON (JavaScript Injection)
    # =====================================================
    st_components.html("""
        <script>
            const containerId = 'stocky-float-icon';
            let container = window.parent.document.getElementById(containerId);
            
            if (!container) {
                // Load Lottie Library
                const scriptId = 'lottie-lib';
                if (!window.parent.document.getElementById(scriptId)) {
                    const s = window.parent.document.createElement('script');
                    s.id = scriptId;
                    s.src = "https://unpkg.com/@lottiefiles/dotlottie-wc@0.8.5/dist/dotlottie-wc.js";
                    s.type = "module";
                    window.parent.document.head.appendChild(s);
                }

                // Create Floating Container
                container = window.parent.document.createElement('div');
                container.id = containerId;
                Object.assign(container.style, {
                    position: 'fixed', bottom: '15px', left: '15px',
                    width: '70px', height: '70px', zIndex: '99999',
                    cursor: 'pointer', display: 'flex',
                    alignItems: 'center', justifyContent: 'center'
                });
                container.innerHTML = `<dotlottie-wc src="https://lottie.host/a12e2d53-123d-4bed-aa33-94f211d79642/PYI9BcHk6P.lottie" 
                    style="width:100%;height:100%;pointer-events:none;" autoplay loop></dotlottie-wc>`;
                window.parent.document.body.appendChild(container);
                
                // Sync Click to Streamlit Popover Button
                function sync() {
                    const btns = Array.from(window.parent.document.querySelectorAll('button'));
                    const popBtn = btns.find(b => b.innerText.includes('🤖'));
                    if (!popBtn) return setTimeout(sync, 300);
                    
                    // Hide Original Button
                    Object.assign(popBtn.style, {
                        position: 'fixed', bottom: '15px', left: '15px',
                        width: '70px', height: '70px', opacity: '0', 
                        pointerEvents: 'none', zIndex: '0'
                    });
                    
                    container.onclick = () => popBtn.click();
                }
                sync();
            }

            // =====================================================
            // VOICE INPUT LOGIC - Inject Lottie Mic Button
            // =====================================================
            function initVoiceInput() {
                const doc = window.parent.document;
                
                const inject = () => {
                    // Find the mic button placeholder
                    const micBtns = Array.from(doc.querySelectorAll('button')).filter(b => b.innerText.includes('🎤'));
                    
                    micBtns.forEach(btn => {
                        if (btn.dataset.lottieInjected) return;
                        btn.dataset.lottieInjected = 'true';
                        
                        // Hide original text
                        btn.style.position = 'relative';
                        btn.style.overflow = 'visible';
                        const origContent = btn.innerHTML;
                        
                        // Create Lottie Element - Perfect Circle Shape
                        btn.innerHTML = `
                            <dotlottie-wc 
                                src="https://lottie.host/732a019b-9ba9-4732-887e-695f5cc73684/G1CTX7BJQu.lottie" 
                                style="width:40px; height:40px; transform: scale(1.3); transform-origin: center; pointer-events:none; display:block;" 
                                autoplay loop>
                            </dotlottie-wc>
                        `;
                        
                        // Voice Recording Handler
                        btn.onclick = (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            const Speech = window.webkitSpeechRecognition || window.SpeechRecognition;
                            if (!Speech) {
                                alert("Your browser does not support voice input.");
                                return;
                            }
                            
                            const rec = new Speech();
                            rec.lang = 'en-US';
                            rec.interimResults = false;
                            
                            // Visual Feedback
                            btn.style.opacity = '0.5';
                            
                            rec.onresult = (ev) => {
                                const text = ev.results[0][0].transcript;
                                
                                // Find the text input in the popover
                                const popover = doc.querySelector('div[data-testid="stPopoverBody"]');
                                if (popover) {
                                    const input = popover.querySelector('input[type="text"]');
                                    if (input) {
                                        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                        setter.call(input, text);
                                        input.dispatchEvent(new Event('input', { bubbles: true }));
                                        input.focus();
                                    }
                                }
                            };
                            
                            rec.onend = () => { btn.style.opacity = '1'; };
                            rec.onerror = (e) => { console.error(e); btn.style.opacity = '1'; };
                            
                            rec.start();
                        };
                    });
                };
                
                inject();
                setInterval(inject, 500);
            }
            initVoiceInput();

            // =====================================================
            // EDGE RESIZE LOGIC (Excel-Style)
            // =====================================================
            function initEdgeResize() {
                const doc = window.parent.document;
                
                // Helper to create resize handle
                const injectHandle = (popover) => {
                    if (popover.dataset.hasResizeHandle) return;
                    popover.dataset.hasResizeHandle = 'true';
                    
                    // Ensure positioning context & overflow
                    popover.style.setProperty('position', 'relative', 'important');
                    popover.style.setProperty('overflow', 'visible', 'important');
                    
                    const handle = doc.createElement('div');
                    Object.assign(handle.style, {
                        position: 'absolute',
                        top: '0', bottom: '0', right: '-5px', // Extend slightly outside
                        width: '15px', // Wider hit area
                        cursor: 'ew-resize',
                        zIndex: '2147483647', // Max z-index
                        background: 'transparent', // Change to 'rgba(255,0,0,0.1)' to debug
                        touchAction: 'none'
                    });
                    
                    popover.appendChild(handle);
                    
                    let isDragging = false;
                    let currentX;
                    let startX;
                    let startWidth;
                    let animationFrameId;
                    
                    const updateWidth = () => {
                        if (!isDragging) return;
                        
                        const dx = currentX - startX;
                        let newWidth = startWidth + dx;
                        
                        if (newWidth < 300) newWidth = 300;
                        if (newWidth > (window.innerWidth - 20)) newWidth = window.innerWidth - 20;
                        
                        // DEEP FIX: Resize the parent container (the Dialog itself)
                        // This handles the case where the parent is fixed/constrained
                        const container = popover.closest('[role="dialog"]') || popover.parentElement;
                        
                        if (container) {
                            container.style.setProperty('width', `${newWidth}px`, 'important');
                            container.style.setProperty('min-width', `${newWidth}px`, 'important');
                            container.style.setProperty('max-width', '95vw', 'important');
                        }
                        
                        // Also force body to follow
                        popover.style.setProperty('width', '100%', 'important');
                        popover.style.setProperty('min-width', '100%', 'important');
                        
                        animationFrameId = requestAnimationFrame(updateWidth);
                    };
                    
                    const onMouseDown = (e) => {
                        isDragging = true;
                        startX = e.clientX;
                        currentX = e.clientX;
                        startWidth = popover.getBoundingClientRect().width;
                        
                        const overlay = doc.createElement('div');
                        overlay.id = 'resize-overlay-capture';
                        Object.assign(overlay.style, {
                            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                            zIndex: '2147483647', cursor: 'ew-resize'
                        });
                        doc.body.appendChild(overlay);
                        
                        // Start Loop
                        animationFrameId = requestAnimationFrame(updateWidth);
                        
                        e.preventDefault();
                        e.stopPropagation();
                    };
                    
                    const onMouseMove = (e) => {
                        if (!isDragging) return;
                        e.preventDefault();
                        currentX = e.clientX; 
                        // Note: actual update happens in RAF loop
                    };
                    
                    const onMouseUp = () => {
                        if (isDragging) {
                            isDragging = false;
                            cancelAnimationFrame(animationFrameId);
                            const overlay = doc.getElementById('resize-overlay-capture');
                            if (overlay) overlay.remove();
                        }
                    };
                    
                    handle.addEventListener('mousedown', onMouseDown);
                    doc.addEventListener('mousemove', onMouseMove);
                    doc.addEventListener('mouseup', onMouseUp);
                };

                // Observer to catch the popover when it opens
                const observer = new MutationObserver(() => {
                    const popover = doc.querySelector('div[data-testid="stPopoverBody"]');
                    if (popover) {
                        injectHandle(popover);
                    }
                });
                
                observer.observe(doc.body, { childList: true, subtree: true });
            }
            initEdgeResize();
        </script>
    """, height=0, width=0)


    # =====================================================
    # PROFESSIONAL CSS STYLING
    # =====================================================
    st.markdown("""
        <style>
        /* ============================================= */
        /* POPOVER WINDOW - The "Jackpot Window"        */
        /* ============================================= */
        div[data-testid="stPopoverBody"] {
            width: 450px !important;
            max-width: 95vw !important;
            max-height: 80vh !important;
            /* Revert resize */
            border-radius: 20px !important;
            background: #FFFFFF !important;
            box-shadow: 0 12px 40px rgba(0,0,0,0.2) !important;
            border: 1px solid #E8E8E8 !important;
            padding: 0 !important;
            overflow: hidden !important; 
            display: flex !important;
            flex-direction: column !important;
        }

        /* ============================================= */
        /* CHAT MESSAGE BUBBLES                         */
        /* ============================================= */
        div[data-testid="stPopoverBody"] .stChatMessage {
            background: #F5F7FA !important;
            border-radius: 16px !important;
            margin: 8px 12px !important;
            padding: 12px 16px !important;
            border: none !important;
        }

        /* ============================================= */
        /* INPUT CAPSULE - CORE MOBILE/DESKTOP FIX      */
        /* ============================================= */
        
        /* The Horizontal Block holding Input + Buttons */
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 8px !important;
            padding: 8px 12px !important;
            background: #F0F2F5 !important;
            border-radius: 24px !important;
            margin: 8px 12px 4px 12px !important; /* Minimal bottom margin */
            width: calc(100% - 24px) !important;
            box-sizing: border-box !important;
            flex-shrink: 0 !important;
        }

        /* CRITICAL: Force All Columns to Shrink */
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            min-width: 0 !important;
            flex-shrink: 1 !important;
            padding: 0 !important;
        }

        /* Input Column - Takes remaining space */
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child {
            flex: 1 1 auto !important;
        }

        /* Button Columns - Fixed Size */
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2),
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) {
            flex: 0 0 40px !important;
            width: 40px !important;
            max-width: 40px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        /* ============================================= */
        /* TEXT INPUT STYLING                           */
        /* ============================================= */
        div[data-testid="stPopoverBody"] .stTextInput {
            margin: 0 !important;
        }
        div[data-testid="stPopoverBody"] .stTextInput > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        div[data-testid="stPopoverBody"] .stTextInput input {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 8px 0 !important;
            font-size: 15px !important;
            color: #333 !important;
        }
        div[data-testid="stPopoverBody"] .stTextInput input::placeholder {
            color: #888 !important;
        }
        /* Hide helper text */
        div[data-testid="stPopoverBody"] [data-testid="InputInstructions"] {
            display: none !important;
        }
        div[data-testid="stPopoverBody"] label {
            display: none !important;
        }

        /* ============================================= */
        /* BUTTON STYLING - Clean Icons                 */
        /* ============================================= */
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] button {
            background: transparent !important;
            border: none !important;
            border-radius: 50% !important;
            width: 36px !important;
            height: 36px !important;
            min-width: 36px !important;
            min-height: 36px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 18px !important;
            color: #007AFF !important;
            cursor: pointer !important;
            transition: background 0.2s ease !important;
        }
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] button:hover {
            background: rgba(0,122,255,0.1) !important;
        }
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] button:active {
            transform: scale(0.95) !important;
        }
        /* Button Text Styling (Emoji) */
        div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] button p {
            font-size: 20px !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1 !important;
        }

        /* ============================================= */
        /* MOBILE SPECIFIC OVERRIDES - AGGRESSIVE FIX   */
        /* ============================================= */
        @media (max-width: 640px) {
            /* Popover Window */
            div[data-testid="stPopoverBody"] {
                width: 95vw !important;
                max-width: 95vw !important;
                border-radius: 20px !important;
            }
            
            /* ================================================ */
            /* THE INPUT CAPSULE - FORCE HORIZONTAL LAYOUT      */
            /* ================================================ */
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                align-items: center !important;
                justify-content: flex-start !important;
                gap: 6px !important;
                padding: 6px 16px 6px 10px !important;
                margin: 6px 6px 10px 6px !important;
                width: calc(100% - 12px) !important;
                max-width: calc(100% - 12px) !important;
                overflow: visible !important;
                box-sizing: border-box !important;
            }
            
            /* ================================================ */
            /* ALL COLUMNS - RESET STREAMLIT DEFAULTS           */
            /* THIS IS THE CRITICAL FIX - stColumn not column   */
            /* ================================================ */
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 0px !important;
                width: auto !important;
                flex-shrink: 1 !important;
                flex-basis: auto !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            
            /* ================================================ */
            /* INPUT COLUMN - TAKES ALL REMAINING SPACE         */
            /* ================================================ */
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child {
                flex: 1 1 auto !important;
                min-width: 50px !important;
            }
            
            /* ================================================ */
            /* BUTTON COLUMNS - FIXED 44px EACH (MIC & SEND)    */
            /* ================================================ */
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2),
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {
                flex: 0 0 42px !important;
                width: 42px !important;
                min-width: 42px !important;
                max-width: 42px !important;
                height: 42px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                overflow: visible !important;
                flex-shrink: 0 !important;
            }
            
            /* ================================================ */
            /* BUTTONS THEMSELVES                               */
            /* ================================================ */
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] button {
                width: 38px !important;
                height: 38px !important;
                min-width: 38px !important;
                min-height: 38px !important;
                max-width: 40px !important;
                max-height: 40px !important;
                padding: 0 !important;
                margin: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                overflow: visible !important;
                flex-shrink: 0 !important;
            }
            
            /* Force inner button containers */
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) > div,
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) > div {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 44px !important;
                height: 44px !important;
                padding: 0 !important;
                margin: 0 !important;
                overflow: visible !important;
            }
            
            /* Text Input - Shrink to fit */
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] .stTextInput {
                width: 100% !important;
                max-width: 100% !important;
            }
            div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] .stTextInput input {
                width: 100% !important;
                padding: 6px 8px !important;
                font-size: 14px !important;
            }
        }

        /* Hide the floating popover button (we have our own) */
        div[data-testid="stPopover"] > button:first-child {
            position: fixed !important;
            bottom: 15px !important;
            left: 15px !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }


        </style>
    """, unsafe_allow_html=True)

    # =====================================================
    # UI STRUCTURE
    # =====================================================
    popover = st.popover("🤖")

    with popover:
        # Header
        st.markdown("""
            <div style="padding:12px 16px; font-weight:600; font-size:16px; 
                        border-bottom:1px solid #eee; color:#333; display:flex; 
                        justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span>🤖</span> Stocky AI
                </div>

            </div>
        """, unsafe_allow_html=True)

        # Chat History
        chat_area = st.container(height=320)
        with chat_area:
            for msg in st.session_state.ai_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
            # Show loading indicator if waiting for response
            if st.session_state.get('ai_loading', False):
                with st.chat_message("assistant"):
                    st.markdown("🤔 **Thinking...** _Please wait while I analyze your request_")

        # Input Row - Using proper column config for mobile
        def submit_message():
            val = st.session_state.chat_input_val
            if val.strip():
                # Add user message
                st.session_state.ai_messages.append({"role": "user", "content": val})
                # Set loading state
                st.session_state.ai_loading = True
                st.session_state.pending_prompt = val
                st.session_state.chat_input_val = ""
        
        # Process pending prompt after rerun (to show loading state)
        if st.session_state.get('ai_loading', False) and st.session_state.get('pending_prompt'):
            prompt = st.session_state.pending_prompt
            st.session_state.pending_prompt = None
            
            # Get AI response
            with st.spinner(""):
                response = get_ai_response(prompt)
            
            # Add response and clear loading state
            st.session_state.ai_messages.append({"role": "assistant", "content": response})
            st.session_state.ai_loading = False
            st.rerun()

        # Create columns with explicit gap
        col1, col2, col3 = st.columns([5, 1, 1], gap="small")
        
        with col1:
            st.text_input(
                "msg", 
                key="chat_input_val", 
                placeholder="Ask Stocky...", 
                label_visibility="collapsed",
                on_change=submit_message
            )
        
        with col2:
            st.button("🎤", key="mic_btn", help="Voice Input", use_container_width=True)
        
        with col3:
            st.button("➤", key="send_btn", on_click=submit_message, help="Send", use_container_width=True)
