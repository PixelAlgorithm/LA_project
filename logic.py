from pyscript import document
from pyscript import window
import numpy as np

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

def calculate(event=None):
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

        
    except Exception as e:
        window.alert(f"Calculation Error: {str(e)}\n\nMake sure all fields are filled with valid numbers and that the matrix represents a viable productive economy.")
