import fitz
import re

def generiere_stundenplan_final(pdf_pfad, output_html):
    doc = fitz.open(pdf_pfad)
    
    html_content = """
    <html><head><style>
        body { background-color: #0d0d0d; color: #4ade80; font-family: 'Consolas', 'Courier New', monospace; padding: 30px; }
        .container { max-width: 1100px; margin: auto; border: 1px solid #1f2937; padding: 20px; background: #050505; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        h1 { font-size: 1.2em; letter-spacing: 4px; color: #166534; border-bottom: 1px solid #1f2937; padding-bottom: 10px; margin-bottom: 30px; }
        .week-block { margin-bottom: 50px; }
        .week-title { color: #ca8a04; font-size: 0.9em; margin-bottom: 10px; opacity: 0.8; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #1f2937; padding: 12px; text-align: left; font-size: 0.85em; }
        th { color: #9ca3af; background: #111827; font-weight: normal; text-transform: uppercase; }
        .zeit-col { color: #854d0e; width: 110px; }
        .modul-box { color: #4ade80; }
        .cancelled { color: #ef4444; text-decoration: line-through; opacity: 0.7; }
        .empty { color: #1a1a1a; }
        .cursor { display: inline-block; width: 8px; height: 15px; background: #4ade80; margin-left: 5px; animation: blink 1s infinite; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    </style></head><body>
    <div class="container">
    <h1>Stundenplan<span class="cursor"></span></h1>
    """

    block_labels = {"1": "0800-0930", "2": "0945-1115", "3": "1130-1300", "4": "1400-1530"}

    for page in doc:
        text = page.get_text("text")
        zeitraum = re.search(r'vom \d{2}\.\d{2}\.\d{4} bis \d{2}\.\d{2}\.\d{4}', text)
        woche_label = zeitraum.group(0) if zeitraum else "STASH_UNDEFINED"
        
        html_content += f'<div class="week-block"><div class="week-title">> ADDR: {woche_label}</div>'
        html_content += '<table><tr><th>Time</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th></tr>'
        
        tables = page.find_tables()
        for table in tables:
            df = table.to_pandas()
            
            # Wir füllen eine Matrix (4 Blöcke x 5 Tage)
            # Wichtig für Doppelstunden: Wir merken uns den letzten Inhalt pro Spalte
            matrix = {b: [""] * 5 for b in block_labels.keys()}
            last_content = [""] * 5 
            
            for _, row in df.iterrows():
                row_indicator = str(row.iloc[0])
                blocks_in_row = re.findall(r'[1-4]', row_indicator)
                
                if not blocks_in_row: continue
                
                for day_idx in range(1, 6):
                    if day_idx < len(row):
                        content = str(row.iloc[day_idx]).strip()
                        
                        # Wenn Zelle leer ist und es eine Doppelstunde (1 2) ist, 
                        # nimm den Inhalt von oben
                        if (not content or content == "None" or len(content) < 3) and len(blocks_in_row) > 1:
                            current_val = last_content[day_idx-1]
                        elif content and content != "None":
                            line = content.split('\n')[0].strip()
                            if re.search(r'M\d', line):
                                is_entf = "entfällt" in content.lower()
                                style = 'class="cancelled"' if is_entf else 'class="modul-box"'
                                current_val = f'<span {style}>{line}</span>'
                                last_content[day_idx-1] = current_val
                            else:
                                current_val = ""
                        else:
                            current_val = ""
                            last_content[day_idx-1] = ""
                            
                        for b in blocks_in_row:
                            matrix[b][day_idx-1] = current_val

            for b_nr in ["1", "2", "3", "4"]:
                html_content += f'<tr><td class="zeit-col">[{block_labels[b_nr]}]</td>'
                for d in range(5):
                    val = matrix[b_nr][d]
                    html_content += f'<td>{val if val else "<span class=\'empty\'>..</span>"}</td>'
                html_content += '</tr>'
        
        html_content += '</table></div>'

    html_content += "</div></body></html>"
    
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

generiere_stundenplan_final("januar-mitte-februar.pdf", "stundenplan.html")
print("SUCCESS: stundenplan.html generiert.")