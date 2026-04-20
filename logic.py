from pyscript import document
from pyscript import window
import numpy as np
import json
from pyodide.http import pyfetch

chat_history_state = []

def sync_headers(event):
    try:
        target_id = event.target.id # e.g. "name_0"
        idx = target_id.split('_')[1]
        val = event.target.value
        col_header = document.getElementById(f"col_header_{idx}")
        if not val.strip():
            col_header.innerText = f"Sector {int(idx)+1}"
        else:
            col_header.innerText = val
    except Exception as e:
        print("Error syncing header:", e)

def generate_fields(event=None):
    size_entry = document.getElementById("size_entry")
    try:
        n = int(size_entry.value)
    except Exception:
        return
    
    if n < 1 or n > 20:
        window.alert("Please enter a valid number of sectors (1-20).")
        return
        
    matrix_card = document.getElementById("matrix_card")
    
    # We construct the HTML for the dynamically scalable matrix grid
    html = f"<div style='display: grid; grid-template-columns: auto repeat({n}, 1fr) auto; gap: 10px; align-items: center;'>"
    html += "<div></div>" # Top left corner empty
    
    # Column Headers
    for j in range(n):
        html += f"<div class='grid-header' id='col_header_{j}'>Sector {j+1}</div>"
    html += "<div class='grid-header-demand'>Demand</div>"
    
    # Rows for the Matrix
    for i in range(n):
        # Row Header (Sector Name)
        html += f"<div><input type='text' id='name_{i}' class='input-field sector-name' placeholder='Sector {i+1}' py-input='sync_headers'></div>"
        
        # A_ij fields
        for j in range(n):
            html += f"<div><input type='number' step='any' id='A_{i}_{j}' class='input-field mat-val' placeholder='0.0'></div>"
            
        # Demand field for row i
        html += f"<div><input type='number' step='any' id='D_{i}' class='input-field dem-val' placeholder='0.0'></div>"
        
    html += "</div>"
    
    matrix_card.innerHTML = html

def load_sample(event=None):
    size_entry = document.getElementById("size_entry")
    size_entry.value = "4"
    generate_fields()
    
    # Hardcoded sample matching Python desktop app
    names = ["Agriculture", "Mining", "Food", "Industry"]
    A = [[0.2, 0.1, 0.0, 0.1],
         [0.1, 0.2, 0.1, 0.2],
         [0.3, 0.1, 0.2, 0.1],
         [0.2, 0.2, 0.1, 0.2]]
    D = [120, 100, 180, 200]
    
    for i in range(4):
        document.getElementById(f"name_{i}").value = names[i]
        document.getElementById(f"col_header_{i}").innerText = names[i]
        for j in range(4):
            document.getElementById(f"A_{i}_{j}").value = str(A[i][j])
        document.getElementById(f"D_{i}").value = str(D[i])

async def calculate(event=None):
    try:
        size_entry = document.getElementById("size_entry")
        try:
            n = int(size_entry.value)
        except:
            window.alert("Please generate the matrix first.")
            return

        A = []
        for i in range(n):
            row = []
            for j in range(n):
                el = document.getElementById(f"A_{i}_{j}")
                if not el:
                    window.alert("Please generate the matrix first.")
                    return
                val_str = el.value
                val = float(val_str) if val_str else 0.0
                row.append(val)
            A.append(row)
            
        D = []
        for i in range(n):
            val_str = document.getElementById(f"D_{i}").value
            val = float(val_str) if val_str else 0.0
            D.append(val)
            
        names = []
        for i in range(n):
            name_val = document.getElementById(f"name_{i}").value
            names.append(name_val if name_val else f"Sector {i+1}")
            
        A_np = np.array(A)
        D_np = np.array(D)
        
        # Leontief Inverse calculation: L = (I - A)^-1
        I = np.eye(n)
        L = np.linalg.inv(I - A_np)
        
        # Total Output calculation: X = L @ D
        X = L @ D_np
        
        # ---- Render Basic Output Report ----
        basic = f"<ul class='report-list'>"
        for i in range(n):
            ripple = X[i] - D[i]
            basic += f"<li><strong>{names[i]}</strong>: Output = {X[i]:.2f} <span style='color: var(--accent-emerald); font-weight:bold; margin-left:10px;'>(+{ripple:.2f} Ripple Effect)</span></li>"
        basic += "</ul>"
        document.getElementById("basic_report").innerHTML = basic
        
        # ---- Render Full Interactive Report (Ripple explanation) ----
        full = "<h3>How Your Economy Interacts (The Ripple Effect)</h3>"
        full += "<p style='margin-bottom: 1rem; color: var(--text-secondary); line-height: 1.6;'>"
        full += "When you ask for a product, that industry doesn't work alone. It has to buy raw materials and services from other sectors, who then buy from others. "
        full += "This creates a chain reaction. Below is exactly what happens behind the scenes if society demands <strong>just 1 extra unit</strong> of a specific sector's goods.</p>"
        
        for j in range(n):
            total_footprint = L[:, j].sum()
            full += f"<div class='explanation-card'><h4>If demand for <span style='color:#f59e0b;'>{names[j]}</span> goes up by 1 unit:</h4>"
            full += f"<p style='margin-bottom: 0.5rem; color: var(--text-secondary);'>To satisfy this single request, the entire economy must scramble and produce a massive total footprint of <strong>{total_footprint:.2f} units</strong> across all sectors combined!</p>"
            full += "<ul>"
            for i in range(n):
                if L[i][j] > 0.0001:
                    if i == j:
                        extra = L[i][j] - 1
                        if extra > 0.001:
                            full += f"<li>The <strong>{names[i]}</strong> sector builds the <strong>1 core unit</strong> you asked for, plus an extra <strong>{extra:.4f} units</strong> just to feed back into its own supply chain.</li>"
                        else:
                            full += f"<li>The <strong>{names[i]}</strong> sector builds the <strong>1 core unit</strong> you asked for.</li>"
                    else:
                        full += f"<li>The <strong>{names[i]}</strong> sector is heavily affected and is forced to produce an extra <strong>{L[i][j]:.4f} units</strong> of supplies.</li>"
            full += "</ul></div>"
            
        document.getElementById("full_report").innerHTML = full

        # ---- Render AI Summary ----
        env_api_key = "GEMINI_API_KEY_PLACEHOLDER"
        api_key = env_api_key if env_api_key != "GEMINI_API_KEY_PLACEHOLDER" else window.localStorage.getItem("gemini_api_key")
        
        if not api_key:
            document.getElementById("ai_summary").innerHTML = "<p class='placeholder-text' style='color: var(--accent-gold);'>Please enter and save a Gemini API Key above to enable AI summaries.</p>"
            return

        document.getElementById("ai_summary").innerHTML = "<p class='placeholder-text' style='opacity: 0.8;'>Generating AI summary using Gemini Flash... please wait.</p>"
        
        chat_el = document.getElementById("chat_section")
        if chat_el: chat_el.style.display = "none"

        report_text = f"Economy Size: {n} sectors. Sectors: {', '.join(names)}.\n"
        for i in range(n):
            ripple = X[i] - D[i]
            report_text += f"Sector {names[i]}: Demand={D[i]}, Total Output={X[i]:.2f}, Ripple Effect={ripple:.2f}\n"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        prompt_text = f"Here is an economic ripple effect report:\n\n{report_text}\n\nPlease provide a short, concise, and insightful plain-text summary (no markdown formatting please, or just simple text). Highlight the sectors with the biggest ripple effects."
        
        global chat_history_state
        chat_history_state = [{"role": "user", "parts": [{"text": prompt_text}]}]

        payload = {
            "contents": chat_history_state,
            "systemInstruction": {
                "parts": [{"text": "You are a helpful and expert economics tutor. Use plain text or HTML <br> tags instead of markdown asterisks. Keep answers conversational, straightforward, and no longer than a few paragraphs."}]
            }
        }

        try:
            response = await pyfetch(
                url,
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps(payload)
            )
            data = await response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                summary_text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Convert newlines to HTML breaks
                summary_html = summary_text.replace('\n', '<br>')
                document.getElementById("ai_summary").innerHTML = f"<p style='color: var(--text-secondary); line-height: 1.6;'>{summary_html}</p>"
                
                chat_history_state.append({"role": "model", "parts": [{"text": summary_text}]})
                if chat_el:
                    chat_el.style.display = "block"
                    document.getElementById("chat_history").innerHTML = f"<div class='chat-bubble model'>I have finished analyzing the report! What questions do you have about the ripple effects or the Leontief model?</div>"
            else:
                document.getElementById("ai_summary").innerHTML = "<p style='color: #ef4444;'>Failed to generate AI summary: Unexpected response format.</p>"
        except Exception as e:
            document.getElementById("ai_summary").innerHTML = f"<p style='color: #ef4444;'>Failed to call Gemini API: {str(e)}</p>"
        
    except Exception as e:
        window.alert(f"Calculation Error: {str(e)}\n\nMake sure all fields are filled with valid numbers and that the matrix represents a viable productive economy.")

def save_api_key(event=None):
    key_input = document.getElementById("api_key_input").value
    if key_input and key_input.strip():
        window.localStorage.setItem("gemini_api_key", key_input.strip())
        window.alert("API Key saved securely in your browser's local storage!")
        document.getElementById("api_key_input").value = ""
    else:
        window.alert("Please enter a valid API Key.")

def clear_api_key(event=None):
    window.localStorage.removeItem("gemini_api_key")
    window.alert("API Key removed from browser.")

# Hide API Key UI immediately if environment key is provided by GitHub Actions
env_api_key = "GEMINI_API_KEY_PLACEHOLDER"
if env_api_key != "GEMINI_API_KEY_PLACEHOLDER":
    ui_el = document.getElementById("ai_key_ui")
    if ui_el:
        ui_el.style.display = "none"

async def send_chat_message(event=None):
    global chat_history_state
    input_el = document.getElementById("chat_input")
    message = input_el.value.strip()
    if not message:
        return
        
    input_el.value = ""
    
    chat_hist_el = document.getElementById("chat_history")
    user_bubble = f"<div class='chat-bubble user'>{message}</div>"
    chat_hist_el.innerHTML += user_bubble
    chat_hist_el.scrollTo(0, chat_hist_el.scrollHeight)
    
    env_api_key = "GEMINI_API_KEY_PLACEHOLDER"
    api_key = env_api_key if env_api_key != "GEMINI_API_KEY_PLACEHOLDER" else window.localStorage.getItem("gemini_api_key")
    if not api_key:
        return
        
    chat_history_state.append({"role": "user", "parts": [{"text": message}]})
    
    loading_id = f"loading_{np.random.randint(1000, 9999)}"
    chat_hist_el.innerHTML += f"<div id='{loading_id}' class='chat-bubble model typing-indicator'>...</div>"
    chat_hist_el.scrollTo(0, chat_hist_el.scrollHeight)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": chat_history_state,
        "systemInstruction": {
            "parts": [{"text": "You are a helpful and expert economics tutor. Answer the user's questions about the previous economic report. Use plain text or HTML <br> tags instead of markdown asterisks. Keep answers conversational, straightforward, and no longer than a few paragraphs."}]
        }
    }
    
    try:
        response = await pyfetch(
            url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload)
        )
        data = await response.json()
        doc_loading = document.getElementById(loading_id)
        if doc_loading: doc_loading.remove()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
            chat_history_state.append({"role": "model", "parts": [{"text": reply_text}]})
            
            reply_html = reply_text.replace('\n', '<br>')
            chat_hist_el.innerHTML += f"<div class='chat-bubble model'>{reply_html}</div>"
            chat_hist_el.scrollTo(0, chat_hist_el.scrollHeight)
        else:
            chat_hist_el.innerHTML += f"<div class='chat-bubble model error'>I encountered an error understanding that.</div>"
    except Exception as e:
        doc_loading = document.getElementById(loading_id)
        if doc_loading: doc_loading.remove()
        chat_hist_el.innerHTML += f"<div class='chat-bubble model error'>API Error: {str(e)}</div>"

def handle_chat_keydown(event):
    if getattr(event, 'key', '') == 'Enter':
        import asyncio
        asyncio.ensure_future(send_chat_message())



