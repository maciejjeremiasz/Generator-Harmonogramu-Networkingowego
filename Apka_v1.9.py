import streamlit as st
import pandas as pd
import random
import math
import copy
import os
from collections import defaultdict
import plotly.graph_objects as go
import plotly.colors
import io

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==========================================
# KONFIGURACJA STRONY STREAMLIT
# ==========================================
st.set_page_config(page_title="Generator Networkingu", layout="wide", page_icon="🤝")

# ==========================================
# BEZPIECZNA TYPOGRAFIA I CSS (MINIMALIZM)
# ==========================================
st.markdown("""
    <style>
        /* Import nowoczesnej czcionki */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* 1. BEZPIECZNA ZMIANA CZCIONKI DLA TEKSTÓW */
        /* Celujemy tylko w tagi tekstowe, omijając span i div, aby nie zepsuć ikon Streamlita */
        html, body, p, li, label, input, button, h1, h2, h3, .stMarkdown {
            font-family: 'Inter', sans-serif !important;
        }

        /* OCHRONA IKON (Wymuszenie oryginalnej czcionki dla strzałek i menu) */
        .material-symbols-rounded, .stIcon,[data-testid="stExpanderToggleIcon"], [data-testid="stSidebarCollapseButton"] span {
            font-family: 'Material Symbols Rounded', sans-serif !important;
        }

        /* 2. BARDZO DUŻY ROZMIAR (1.5rem) - Tylko dla nagłówków */
        h1, h2, h3, .recommendation-title {
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            padding-bottom: 0.5rem;
        }

        /* 3. DUŻY ROZMIAR (1.0rem) - Dla tekstów, etykiet, inputów i przycisków */
        p, li, label, input, .stButton button {
            font-size: 1.0rem !important;
        }

        /* Pogrubienie etykiet nad polami do wpisywania */
        label {
            font-weight: 600 !important;
        }

        /* 4. BOX REKOMENDACJI (Dostosowany do jasnego/ciemnego motywu) */
        .recommendation-box {
            background-color: rgba(34, 197, 94, 0.15); 
            border-left: 0.4rem solid #22c55e;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1.5rem 0;
        }

/* ==========================================
           NADPISANIE ROZMIARÓW: KONFIGURACJA (st.number_input)
           ========================================== */
        
        /* Etykiety: "Miejsca przy stoliku", "Docelowa liczba rund" */
        div[data-testid="stNumberInput"] label p,
        div[data-testid="stNumberInput"] label {
            font-size: 1.2rem !important; /* Zmień na swój docelowy rozmiar */
        }
        
        /* Cyfry wewnątrz pola do wpisywania */
        div[data-testid="stNumberInput"] input {
            font-size: 1.2rem !important; /* Zmień na swój docelowy rozmiar */
        }

       /* ==========================================
           NADPISANIE ROZMIARÓW: OPISY METRYK (st.metric)
           ========================================== */
        
        /* Obejmujemy główny kontener metryki i każdy możliwy tekst (p, label, div, span) nad wartością */
        div[data-testid="stMetric"] label p,
        div[data-testid="stMetric"] label div,
        div[data-testid="stMetric"] label span,
        div[data-testid="stMetric"] label,
        div[data-testid="stMetricLabel"] p,
        div[data-testid="stMetricLabel"] {
            font-size: 1.5rem !important; /* <-- Tutaj ustaw swój rozmiar dla "Liczba stolików" itp. */
            
        }
        
        /* 2. Główne wartości (duże liczby, np. "10", "85.50%") */
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            font-size: 2.0rem !important; /* Zmień na swój docelowy rozmiar liczby */
        }

        /* 3. Wartość delty (tekst i strzałka pod wartością np. w "Konflikty firmowe") */
        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] * {
            font-size: 1.0rem !important; /* Zmień na swój docelowy rozmiar delty */
        }

/* ==========================================
           WYGLĄD KAFELKÓW METRYK (TŁO I KOLOR)
           ========================================== */
        
        /* 1. Jasnożółte tło, marginesy i zaokrąglenia dla całego kafelka metryki */
        div[data-testid="stMetric"] {
            background-color: #FEF9C3 !important; /* Jasnożółte tło */
            padding: 1rem !important;             /* Wewnętrzny odstęp, by tekst nie dotykał krawędzi */
            border-radius: 0.5rem !important;     /* Zaokrąglone rogi */
            border: 1px solid #FDE047 !important; /* Ciemniejsza, żółta ramka wokół (opcjonalnie) */
        }

        /* 2. Wymuszenie CZARNEJ czcionki dla opisu (etykiety) */
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] label p,
        div[data-testid="stMetric"] label div,
        div[data-testid="stMetric"] label span {
            color: #000000 !important;
        }

        /* 3. Wymuszenie CZARNEJ czcionki dla dużej wartości liczbowej */
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: #000000 !important;
        }

/* ==========================================
           NADPISANIE ROZMIARU: PASEK BOCZNY (SIDEBAR)
           ========================================== */
        
        /* Zmniejszenie nagłówka "Dane wejściowe" w panelu bocznym */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            font-size: 1.5rem !important; /* <-- Zmień na swój docelowy rozmiar, np. 1.2rem lub 1.5rem */
            padding-bottom: 1rem !important;
        }

/* ==========================================
           NADPISANIE ROZMIARU: GŁÓWNY TYTUŁ (st.title)
           ========================================== */
        
        /* Celujemy wyłącznie w tag <h1> w głównej części strony (omijając pasek boczny) */
        .block-container h1,
        div[data-testid="stMainBlockContainer"] h1 {
            font-size: 2.0rem !important; /* <-- Tutaj wpisz swój docelowy rozmiar (np. 3.0rem lub 4.0rem) */
            
            /* Opcjonalnie: możesz tu też zmienić kolor lub wyśrodkować główny tytuł */
            /* text-align: center !important; */
            /* color: #22c55e !important; */
        }

/* ==========================================
           NADPISANIE SZEROKOŚCI OKNA POPUP (DIALOG)
           ========================================== */
        
        /* Wymuszenie szerokości na 75% ekranu (75vw = 75% viewport width) */
        div[data-testid="stModal"] > div[role="dialog"],
        div[data-testid="stDialog"] {
            width: 85vw !important;
            min-width: 85vw !important;
            max-width: 95vw !important;
        }

    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNKCJE POMOCNICZE
# ==========================================
@st.cache_resource
def setup_fonts():
    # Ścieżki relatywne - wskazują na folder 'fonts' w Twoim repozytorium GitHub
    font_path = "Fonts/DejaVuSans.ttf"
    font_bold_path = "Fonts/DejaVuSans-Bold.ttf"
    
    try:
        if os.path.exists(font_path) and os.path.exists(font_bold_path):
            pdfmetrics.registerFont(TTFont('CustomFont', font_path))
            pdfmetrics.registerFont(TTFont('CustomFont-Bold', font_bold_path))
            return True
        return False
    except Exception as e:
        print(f"Błąd ładowania czcionki: {e}")
        return False

def generate_networking_schedule(participants, moderators, X, Y, Z):
    slots_needed = X * (Y - 1)
    participants_padded = participants + [["Wolne", "Miejsce", "Brak"]] * (slots_needed - len(participants))

    def calculate_cost(schedule):
        cost = 0
        meetings = defaultdict(int)
        mod_meetings = defaultdict(int)
        company_conflicts = 0
        
        for round_idx, round_tables in enumerate(schedule):
            for table_idx, table_participants in enumerate(round_tables):
                companies =[p[2] for p in table_participants if p[2] != "Brak"]
                for i in range(len(companies)):
                    for j in range(i+1, len(companies)):
                        if companies[i] == companies[j]:
                            company_conflicts += 1
                            cost += 500
                
                for i in range(len(table_participants)):
                    p1 = tuple(table_participants[i])
                    if p1[2] == "Brak": continue
                    
                    mod_meetings[(p1, table_idx)] += 1
                    if mod_meetings[(p1, table_idx)] > 1:
                        cost += 50
                    
                    for j in range(i+1, len(table_participants)):
                        p2 = tuple(table_participants[j])
                        if p2[2] == "Brak": continue
                        pair = tuple(sorted([p1, p2]))
                        meetings[pair] += 1
                        if meetings[pair] > 1:
                            cost += 100
                            
        return cost, company_conflicts

    def generate_initial_schedule():
        schedule =[]
        for _ in range(Z):
            round_participants = participants_padded[:]
            random.shuffle(round_participants)
            round_tables =[round_participants[i*(Y-1):(i+1)*(Y-1)] for i in range(X)]
            schedule.append(round_tables)
        return schedule

    def get_neighbor(schedule):
        new_schedule = copy.deepcopy(schedule)
        r = random.randint(0, Z-1)
        t1, t2 = random.randint(0, X-1), random.randint(0, X-1)
        while t1 == t2 and X > 1:
            t2 = random.randint(0, X-1)
        
        p1, p2 = random.randint(0, Y-2), random.randint(0, Y-2)
        new_schedule[r][t1][p1], new_schedule[r][t2][p2] = new_schedule[r][t2][p2], new_schedule[r][t1][p1]
        return new_schedule

    current_schedule = generate_initial_schedule()
    current_cost, _ = calculate_cost(current_schedule)
    best_schedule, best_cost = current_schedule, current_cost

    T = 1000.0
    cooling_rate = 0.995
    min_T = 0.1

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_iterations = math.log(min_T / T) / math.log(cooling_rate)
    current_iteration = 0

    while T > min_T:
        neighbor = get_neighbor(current_schedule)
        neighbor_cost, _ = calculate_cost(neighbor)
        
        if neighbor_cost < current_cost or random.random() < math.exp((current_cost - neighbor_cost) / T):
            current_schedule = neighbor
            current_cost = neighbor_cost
            
            if current_cost < best_cost:
                best_schedule = current_schedule
                best_cost = current_cost
                
        T *= cooling_rate
        current_iteration += 1
        
        if current_iteration % 100 == 0:
            progress = min(1.0, current_iteration / total_iterations)
            progress_bar.progress(progress)
            status_text.text(f"Optymalizacja w toku... (Koszt: {best_cost})")

    progress_bar.empty()
    status_text.empty()

    final_cost, company_conflicts = calculate_cost(best_schedule)
    
    unique_meetings_per_participant = defaultdict(set)
    for round_idx, round_tables in enumerate(best_schedule):
        for table_idx, table_participants in enumerate(round_tables):
            for p1 in table_participants:
                if p1[2] == "Brak": continue
                p1_tuple = tuple(p1)
                unique_meetings_per_participant[p1_tuple].add(f"Mod_{table_idx}")
                for p2 in table_participants:
                    if p1 == p2 or p2[2] == "Brak": continue
                    unique_meetings_per_participant[p1_tuple].add(tuple(p2))

    total_unique = sum(len(v) for v in unique_meetings_per_participant.values())
    expected_meetings = len(participants) * (Z * (Y - 2) + Z)
    unique_percentage = (total_unique / expected_meetings) * 100 if expected_meetings > 0 else 0

    return best_schedule, company_conflicts, unique_percentage

def visualize_schedule_plotly(schedule, moderators, participants_data, X, Y, Z):
    participant_ids = {}
    sorted_participants = sorted([p for p in participants_data if p[2] != "Brak"], key=lambda x: x[1])
    for i, p in enumerate(sorted_participants):
        participant_ids[tuple(p)] = f"P{i+1}"

    companies = set([p[2] for p in sorted_participants])
    palette = plotly.colors.qualitative.Pastel + plotly.colors.qualitative.Set3
    company_colors = {comp: palette[i % len(palette)] for i, comp in enumerate(companies)}

    figs =[]
    cols = math.ceil(math.sqrt(X))
    rows = math.ceil(X / cols)
    
    table_spacing_x = 5
    table_spacing_y = 5
    
    for r in range(Z):
        fig = go.Figure()
        
        for t in range(X):
            col = t % cols
            row = rows - 1 - (t // cols)
            
            center_x = col * table_spacing_x
            center_y = row * table_spacing_y
            
            fig.add_shape(type="circle",
                x0=center_x - 1, y0=center_y - 1,
                x1=center_x + 1, y1=center_y + 1,
                line_color="gray", fillcolor="lightgray", opacity=0.3
            )
            
            # Wymuszony czarny kolor i pogrubienie dla numeru stołu
            fig.add_annotation(
                x=center_x, y=center_y, 
                text=f"<b>STÓŁ {t+1}</b>", 
                showarrow=False, 
                font=dict(size=16, color="black")
            )
            
            participants = [p for p in schedule[r][t] if p[2] != "Brak"]
            K = len(participants)
            M = 1 + K 
            
            if M > 0:
                alpha = (2 * math.pi) / M 
                radius = 1.2 
                
                mod_angle = math.pi / 2
                mod_x = center_x + radius * math.cos(mod_angle)
                mod_y = center_y + radius * math.sin(mod_angle)
                
                mod = moderators[t]
                fig.add_trace(go.Scatter(
                    x=[mod_x], y=[mod_y],
                    mode='markers+text',
                    marker=dict(size=40, color='gold', symbol='star', line=dict(width=1, color='darkgoldenrod')),
                    text=["<b>M</b>"],
                    textposition="middle center",
                    hoverinfo="text",
                    hovertext=[f"<b>Moderator:</b><br>{mod[0]} {mod[1]}"],
                    showlegend=False,
                    textfont=dict(size=16, color="black") # Wymuszony czarny kolor
                ))
                
                for i, p in enumerate(participants):
                    p_angle = mod_angle - (i + 1) * alpha
                    
                    px = center_x + radius * math.cos(p_angle)
                    py = center_y + radius * math.sin(p_angle)
                    
                    comp = p[2]
                    color = company_colors[comp]
                    p_id = participant_ids[tuple(p)]
                    
                    hover_text = f"<b>{p[0]} {p[1]}</b><br>Firma: {comp}"
                    
                    fig.add_trace(go.Scatter(
                        x=[px], y=[py],
                        mode='markers+text',
                        marker=dict(size=40, color=color, symbol='circle', line=dict(width=1, color='black')),
                        text=[f"<b>{p_id}</b>"],
                        textposition="middle center",
                        hoverinfo="text",
                        hovertext=[hover_text],
                        showlegend=False,
                        textfont=dict(size=16, color="black") # Wymuszony czarny kolor
                    ))
        
        # Globalne wymuszenie czcionek i tła dla spójności z PDF/PNG
        fig.update_layout(
            title=dict(text=f"<b>Wizualizacja - Runda {r+1}</b>", font=dict(size=24, color="black"), x=0.5),
            xaxis=dict(visible=False, range=[-2, cols*table_spacing_x + 2]), 
            yaxis=dict(visible=False, range=[-2, rows*table_spacing_y]),
            width=max(800, cols * 300), 
            height=max(600, rows * 300),
            plot_bgcolor="white",
            paper_bgcolor="white", # Wymusza białe tło poza obszarem rysowania
            font=dict(color="black"), # Globalny fallback na czarny kolor
            margin=dict(l=40, r=40, t=80, b=40)
        )
        figs.append(fig)
        
    return figs



def generate_visual_plan_pdf_buffer(schedule, moderators, participants_data, X, Y, Z):
    fonts_ready = setup_fonts()
    font_regular = "CustomFont" if fonts_ready else "Helvetica"
    font_bold = "CustomFont-Bold" if fonts_ready else "Helvetica-Bold"

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    participant_ids = {}
    sorted_participants = sorted([p for p in participants_data if p[2] != "Brak"], key=lambda x: x[1])
    for i, p in enumerate(sorted_participants):
        participant_ids[tuple(p)] = f"P{i+1}"

    cols = math.ceil(math.sqrt(X))
    rows = math.ceil(X / cols)

    margin_x = 20 * mm
    margin_y = 20 * mm
    
    N = len(sorted_participants)
    draw_legend_on_side = N <= 30
    legend_width = 60 * mm if draw_legend_on_side else 0
    
    area_w = width - 2 * margin_x - legend_width
    area_h = height - 2 * margin_y - 15 * mm

    cell_w = area_w / cols
    cell_h = area_h / rows
    
    table_r = min(cell_w, cell_h) * 0.25
    person_r = table_r * 1.5

    for r in range(Z):
        c.setFont(font_bold, 24)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(width / 2, height - 15 * mm, f"Plan Sali - Runda {r+1}")

        for t in range(X):
            col = t % cols
            row = rows - 1 - (t // cols)
            
            cx = margin_x + col * cell_w + cell_w / 2
            cy = margin_y + row * cell_h + cell_h / 2
            
            c.setLineWidth(1)
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setFillColorRGB(0.95, 0.95, 0.95)
            c.circle(cx, cy, table_r, stroke=1, fill=1)
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont(font_bold, 12)
            c.drawCentredString(cx, cy - 4, f"STÓŁ {t+1}")
            
            participants =[p for p in schedule[r][t] if p[2] != "Brak"]
            K = len(participants)
            M = 1 + K
            
            if M > 0:
                alpha = (2 * math.pi) / M
                mod_angle = math.pi / 2
                
                mx = cx + person_r * math.cos(mod_angle)
                my = cy + person_r * math.sin(mod_angle)
                
                c.setFillColorRGB(1, 0.84, 0)
                c.setStrokeColorRGB(0.6, 0.5, 0)
                c.circle(mx, my, 14, stroke=1, fill=1)
                c.setFillColorRGB(0, 0, 0)
                c.setFont(font_bold, 10)
                c.drawCentredString(mx, my - 3, "M")
                
                for i, p in enumerate(participants):
                    p_angle = mod_angle - (i + 1) * alpha
                    px = cx + person_r * math.cos(p_angle)
                    py = cy + person_r * math.sin(p_angle)
                    
                    c.setFillColorRGB(0.9, 0.9, 0.9)
                    c.setStrokeColorRGB(0, 0, 0)
                    c.circle(px, py, 12, stroke=1, fill=1)
                    
                    p_id = participant_ids[tuple(p)]
                    c.setFillColorRGB(0, 0, 0)
                    c.setFont(font_bold, 8)
                    c.drawCentredString(px, py - 3, p_id)

        if draw_legend_on_side:
            legend_x = width - margin_x - legend_width + 10 * mm
            legend_y = height - 30 * mm
            
            c.setFont(font_bold, 12)
            c.drawString(legend_x, legend_y, "LEGENDA:")
            legend_y -= 20
            
            c.setFont(font_regular, 9)
            for p in sorted_participants:
                p_id = participant_ids[tuple(p)]
                comp = p[2] if len(p[2]) <= 20 else p[2][:17] + "..."
                text = f"{p_id}: {p[0]} {p[1]} ({comp})"
                c.drawString(legend_x, legend_y, text)
                legend_y -= 14
        
        c.showPage()
        
        if not draw_legend_on_side:
            c.setFont(font_bold, 24)
            c.drawCentredString(width / 2, height - 15 * mm, f"Listy Uczestników - Runda {r+1}")
            
            list_cols = min(X, 4)
            list_col_w = (width - 2 * margin_x) / list_cols
            
            for t in range(X):
                l_c = t % list_cols
                l_r = t // list_cols
                
                lx = margin_x + l_c * list_col_w
                ly = height - 35 * mm - l_r * (Y * 5 * mm + 15 * mm)
                
                c.setFont(font_bold, 12)
                c.drawString(lx, ly, f"STÓŁ {t+1}")
                ly -= 15
                
                mod = moderators[t]
                c.setFont(font_bold, 10)
                c.drawString(lx, ly, f"M: {mod[0]} {mod[1]}")
                ly -= 12
                
                c.setFont(font_regular, 10)
                table_parts = [p for p in schedule[r][t] if p[2] != "Brak"]
                for p in table_parts:
                    p_id = participant_ids[tuple(p)]
                    comp = p[2] if len(p[2]) <= 20 else p[2][:17] + "..."
                    c.drawString(lx, ly, f"{p_id}: {p[0]} {p[1]} ({comp})")
                    ly -= 12
            
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

def generate_badges_pdf_buffer(schedule, participants_data, Z):
    fonts_ready = setup_fonts()
    font_regular = "CustomFont" if fonts_ready else "Helvetica"
    font_bold = "CustomFont-Bold" if fonts_ready else "Helvetica-Bold"
    font_oblique = "CustomFont" if fonts_ready else "Helvetica-Oblique"

    history = defaultdict(list)
    for r in range(Z):
        for t in range(len(schedule[r])):
            for p in schedule[r][t]:
                if p[2] != "Brak":
                    history[tuple(p)].append(t + 1)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    badge_w = 90 * mm
    badge_h = 55 * mm
    margin_x = 15 * mm
    margin_y = 15 * mm
    
    cols = int((width - 2 * margin_x) // badge_w)
    rows = int((height - 2 * margin_y) // badge_h)
    
    spacing_x = (width - 2 * margin_x - cols * badge_w) / (cols - 1) if cols > 1 else 0
    spacing_y = (height - 2 * margin_y - rows * badge_h) / (rows - 1) if rows > 1 else 0

    col_idx = 0
    row_idx = 0

    sorted_participants = sorted([p for p in participants_data if p[2] != "Brak"], key=lambda x: x[1])

    for p in sorted_participants:
        p_tuple = tuple(p)
        if p_tuple not in history:
            continue
            
        x = margin_x + col_idx * (badge_w + spacing_x)
        y = height - margin_y - (row_idx + 1) * badge_h - row_idx * spacing_y
        
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.rect(x, y, badge_w, badge_h)
        
        c.setFillColorRGB(0, 0, 0)
        name_text = f"{p[0]} {p[1]}"
        
        if len(name_text) > 22:
            c.setFont(font_bold, 12)
        elif len(name_text) > 16:
            c.setFont(font_bold, 14)
        else:
            c.setFont(font_bold, 16)
            
        c.drawCentredString(x + badge_w/2, y + badge_h - 15*mm, name_text)
        
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.setFont(font_oblique, 11)
        
        company_name = p[2]
        if len(company_name) > 35:
            company_name = company_name[:32] + "..."
            
        c.drawCentredString(x + badge_w/2, y + badge_h - 22*mm, company_name)
        
        c.setLineWidth(1)
        c.setStrokeColorRGB(0, 0, 0)
        c.line(x + 10*mm, y + badge_h - 28*mm, x + badge_w - 10*mm, y + badge_h - 28*mm)
        
        c.setFont(font_bold, 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(x + badge_w/2, y + badge_h - 35*mm, "TWÓJ HARMONOGRAM:")
        
        c.setFont(font_regular, 10)
        
        history_list = history[p_tuple]
        rounds_per_row = 4
        start_y = y + badge_h - 42*mm
        line_height = 5 * mm
        
        for i in range(0, len(history_list), rounds_per_row):
            chunk = history_list[i:i+rounds_per_row]
            schedule_text = " | ".join([f"R{i+j+1}: Stół {table}" for j, table in enumerate(chunk)])
            current_y = start_y - (i // rounds_per_row) * line_height
            c.drawCentredString(x + badge_w/2, current_y, schedule_text)
        
        col_idx += 1
        if col_idx >= cols:
            col_idx = 0
            row_idx += 1
            
        if row_idx >= rows:
            c.showPage()
            col_idx = 0
            row_idx = 0

    c.save()
    buffer.seek(0)
    return buffer

def generate_export_dataframe(schedule, moderators_data):
    export_data =[]
    for r_idx, round_tables in enumerate(schedule):
        for t_idx, table_participants in enumerate(round_tables):
            mod = moderators_data[t_idx]
            export_data.append({
                "Runda": r_idx + 1,
                "Stolik": t_idx + 1,
                "Rola": "Moderator",
                "Imię": mod[0],
                "Nazwisko": mod[1],
                "Firma": "N/A"
            })
            for p in table_participants:
                if p[2] != "Brak":
                    export_data.append({
                        "Runda": r_idx + 1,
                        "Stolik": t_idx + 1,
                        "Rola": "Uczestnik",
                        "Imię": p[0],
                        "Nazwisko": p[1],
                        "Firma": p[2]
                    })
    return pd.DataFrame(export_data)

# ==========================================
# INTERFEJS UŻYTKOWNIKA (STREAMLIT)
# ==========================================

# 1. Definicja okna popup (Dialog)
@st.dialog("ℹ️ Informacje o aplikacji", width="large")
def show_app_info():
    st.markdown("""
## Witaj w Generatorze Harmonogramu Networkingowego! 🤝

*(Aby wyjść z tego okna, kliknij "X" w prawym górnym rogu lub kliknij gdziekolwiek poza oknem.)*

Ten generator pomoże Ci optymalnie rozplanować usadzenie uczestników podczas wydarzenia networkingowego.

W lewym panelu bocznym załaduj plik excel z dwiema zakładkami:

1. Zakładka „Lista Uczestników” w układzie kolumn: Imię, Nazwisko, Firma
2. Zakładka „Moderatorzy” w układzie kolumn: Imię Nazwisko

**Liczba Moderatorów jest równoznaczna z ilością stolików.**

Następnie podaj liczbę miejsc przy stoliku oraz planowaną liczbę rund.

Liczbę miejsc przy stoliku należy rozumieć jako całkowitą liczbę miejsc (w tym miejsce dla Moderatora)

Aplikacja podpowie Ci optymalną liczbę rund na podstawie ilości uczestników oraz ilości dostępnych miejsc przy stoliku.

Rozplanowując usadzenie uczestników generator kieruje się następującymi priorytetami:

- zmaksymalizować ilość poznanych osób dla każdego uczestnika (unikalne spotkania)
- ograniczyć do minimum ilość powtórzonych spotkań tych samych uczestników
- unikać sytuacji usadzenia osób z tej samej firmy przy jednym stoliku

W sytuacji gdy liczba uczestników z pliku przekroczy dostępną liczbę miejsc przy stolikach N, Generator rozplanuje usadzenie pierwszych N osób z listy oraz dodatkowo wyświetli listę osób, które nie zostały uwzględnione w wydarzeniu.

Po podaniu wszystkich parametrów kliknij czerwony przycisk “Generuj plan usadzenia”

Aplikacja wygeneruje plan usadzenia uczestników dla wszystkich rund, poda statystyki:

- Liczba stolików - podsumowanie ilości stolików w wydarzeniu (równe liczbie moderatorów)
- Konflikty firmowe - ilość sytuacji w których osoby z tej samej firmy spotykają się przy jednym stoliku
- Procent unikalnych spotkań - udział spotkań z nowymi osobami pośród wszystkich spotkań.

Dla wygenerowanego harmonogramu, na samym dole strony możesz pobrać:

- Harmonogram wydarzenia (excel)
- Plakietki dla każdego uczestnika wskazujące indywidualny harmonogram (pdf)
- Plany graficzne usadzenia uczestników przy stołach dla każdej rundy (pdf)

## Bezpieczeństwo danych

Aplikacja działa w środowisku Streamlit, w którym każdy użytkownik ma swoją własną, odizolowaną sesję.

- Dane wgrane przez Użytkownika A (plik Excel) trafiają do pamięci RAM instancji aplikacji przypisanej tylko do jego sesji. Użytkownik B, łącząc się z tym samym adresem URL, nie ma technicznej możliwości podejrzenia zawartości sesji Użytkownika A.
- **Brak bazy danych:** Aplikacja nie zapisuje danych na dysku ani w bazie, ryzyko ich przejęcia w wyniku ataku na składowisko danych praktycznie nie istnieje. Dane znikają w momencie zamknięcia karty lub odświeżenia strony.
    """)

# 2. Logika wyświetlania na starcie (Session State zapamiętuje, czy już to pokazano)
if "info_shown" not in st.session_state:
    st.session_state.info_shown = False

if not st.session_state.info_shown:
    show_app_info()
    st.session_state.info_shown = True

# 3. Główny Tytuł
st.title("🤝 Generator Harmonogramu Networkingowego")

# 4. Przycisk wywołujący popup ręcznie (umieszczony tuż pod głównym tytułem)
if st.button("ℹ️ Informacje o aplikacji"):
    show_app_info()


# --- SIDEBAR (Tylko wgrywanie pliku) ---
st.sidebar.header("📁 Dane wejściowe")
uploaded_file = st.sidebar.file_uploader("Wgraj plik z danymi (Excel)", type=["xlsx"])

st.sidebar.markdown("""
---
**Wymagany format pliku Excel:**
Plik musi zawierać dwa arkusze:
1. **Uczestnicy**: Kolumny `Imię`, `Nazwisko`, `Firma`
2. **Moderatorzy**: Kolumny `Imię`, `Nazwisko`
""")

# --- GŁÓWNA LOGIKA ---
if uploaded_file is not None:
    try:
        df_participants = pd.read_excel(uploaded_file, sheet_name='Uczestnicy')
        df_moderators = pd.read_excel(uploaded_file, sheet_name='Moderatorzy')
            
        df_participants = df_participants.dropna(subset=['Imię', 'Nazwisko', 'Firma'])
        df_moderators = df_moderators.dropna(subset=['Imię'])
        
        participants = [[str(row['Imię']).strip(), str(row['Nazwisko']).strip(), str(row['Firma']).strip()] for _, row in df_participants.iterrows()]
        moderators = [[str(row['Imię']).strip(), str(row['Nazwisko']).strip() if pd.notna(row['Nazwisko']) else ""] for _, row in df_moderators.iterrows()]
        
        X = len(moderators)
        
        if X == 0:
            st.error("Błąd: Brak moderatorów w pliku Excel. Liczba stolików (X) wynosi 0.")
            st.stop()
            
        st.sidebar.success(f"Wczytano {len(participants)} uczestników i {X} moderatorów.")
        
    except Exception as e:
        st.error(f"Błąd podczas wczytywania pliku: {e}")
        st.stop()

    # --- KONTENER KONFIGURACYJNY (DASHBOARD) ---
    with st.container(border=True):
        st.subheader("⚙️ Konfiguracja Wydarzenia")
        
        col_y, col_z, col_empty = st.columns([1, 1, 2])
        
        with col_y:
            Y = st.number_input("Miejsca przy stoliku", min_value=3, value=4, help="Wliczając 1 moderatora")
            
        unique_companies = set([p[2] for p in participants if p[2] != "Brak"])
        F = len(unique_companies)
        N = len(participants)
        
        Z_min = math.ceil((F - 1) / (Y - 2)) if Y > 2 else float('inf')
        
        st.markdown(f"""
            <div class="recommendation-box">
                <span class="recommendation-title">💡 Rekomendowana liczba rund: {Z_min}</span>
                <p style="margin:0;">
                    Na podstawie listy <b>{N}</b> uczestników z <b>{F}</b> różnych firm, aby każdy miał szansę poznać przedstawiciela każdej firmy, teoretyczna minimalna liczba rund wynosi <b>{Z_min}</b>.
                </p>
            </div>
        """, unsafe_allow_html=True)

        with col_z:
            Z = st.number_input("Docelowa liczba rund", min_value=1, value=Z_min)
        
        if Z < Z_min:
            max_met = Z * (Y - 2)
            percentage = min(100, int((max_met / (F - 1)) * 100)) if F > 1 else 100
            st.warning(f"⚠️ **Uwaga:** Przy {Z} rundach uczestnicy poznają średnio **{percentage}%** dostępnych firm. Rozważ zwiększenie liczby rund dla lepszego efektu networkingowego.")

    # --- OBSŁUGA LIMITU MIEJSC (HARD LIMIT) ---
    M = X * (Y - 1)
    L = len(participants)
    
    if L > M:
        required_tables = math.ceil(L / (Y - 1))
        st.error(f"**UWAGA: Przekroczono limit miejsc przy stolikach!**\n\nSystem rozmieści tylko pierwszych {M} uczestników z listy. Aby uwzględnić wszystkich, musisz ograniczyć listę uczestników do {M} osób lub zwiększyć liczbę stołów (moderatorów) do co najmniej {required_tables}.")
        
        with st.expander(f"Uczestnicy nieuwzględnieni (Liczba: {L - M})"):
            excluded_df = pd.DataFrame(participants[M:], columns=["Imię", "Nazwisko", "Firma"])
            # Zmiana indeksowania, aby zaczynało się od 1 zamiast od 0
            excluded_df.index = excluded_df.index + 1
            st.dataframe(excluded_df, use_container_width=True)
            
        participants = participants[:M]

    # --- PRZYCISK AKCJI I ZAPIS DO SESSION STATE ---
    if st.button("🚀 Generuj Plan Usadzenia", type="primary", use_container_width=True):
        with st.spinner("Trwa optymalizacja harmonogramu..."):
            schedule, conflicts, unique_pct = generate_networking_schedule(participants, moderators, X, Y, Z)
            
            st.session_state['schedule'] = schedule
            st.session_state['conflicts'] = conflicts
            st.session_state['unique_pct'] = unique_pct
            st.session_state['plan_ready'] = True

    # --- WYŚWIETLANIE WYNIKÓW (Jeśli plan został wygenerowany) ---
    if st.session_state.get('plan_ready', False):
        
        schedule = st.session_state['schedule']
        conflicts = st.session_state['conflicts']
        unique_pct = st.session_state['unique_pct']
        
        st.success("✅ Harmonogram wygenerowany pomyślnie!")
        
        # --- METRYKI ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Liczba Stolików", X)
        col2.metric("Konflikty firmowe", conflicts, delta_color="inverse")
        col3.metric("Procent unikalnych spotkań", f"{unique_pct:.2f}%")

        # --- WIZUALIZACJA I TABELE ---
        st.header("📊 Wizualizacja i Listy")
        
        figs = visualize_schedule_plotly(schedule, moderators, participants, X, Y, Z)
        
        tabs = st.tabs([f"Runda {r+1}" for r in range(Z)])
        
        participant_ids = {}
        sorted_participants = sorted([p for p in participants if p[2] != "Brak"], key=lambda x: x[1])
        for i, p in enumerate(sorted_participants):
            participant_ids[tuple(p)] = f"P{i+1}"
            
        for r, tab in enumerate(tabs):
            with tab:
                st.plotly_chart(figs[r], use_container_width=True)
                
                st.subheader("Listy uczestników przy stolikach")
                
                cols_per_row = 3
                for i in range(0, X, cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        if i + j < X:
                            t_idx = i + j
                            with cols[j]:
                                mod = moderators[t_idx]
                                table_data =[{"ID": "M", "Imię i Nazwisko": f"{mod[0]} {mod[1]}", "Firma": "Moderator"}]
                                
                                for p in schedule[r][t_idx]:
                                    if p[2] != "Brak":
                                        p_id = participant_ids[tuple(p)]
                                        table_data.append({"ID": p_id, "Imię i Nazwisko": f"{p[0]} {p[1]}", "Firma": p[2]})
                                        
                                df_table = pd.DataFrame(table_data)
                                # Zmiana indeksowania tabel per stolik, aby zaczynało się od 1
                                df_table.index = df_table.index + 1
                                st.markdown(f"**Stolik {t_idx + 1}**")
                                st.dataframe(df_table, use_container_width=True)

        # --- EKSPORT ---
        st.header("💾 Eksport Danych")
        
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        
        df_export = generate_export_dataframe(schedule, moderators)
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Harmonogram')
        
        col_dl1.download_button(
            label="📥 Pobierz Harmonogram (Excel)",
            data=buffer_excel.getvalue(),
            file_name="harmonogram_networking.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        pdf_badges_buffer = generate_badges_pdf_buffer(schedule, participants, Z)
        col_dl2.download_button(
            label="🪪 Pobierz Plakietki (PDF)",
            data=pdf_badges_buffer,
            file_name="plakietki_uczestnikow.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        pdf_plan_buffer = generate_visual_plan_pdf_buffer(schedule, moderators, participants, X, Y, Z)
        col_dl3.download_button(
            label="🗺️ Pobierz Plan Sali (PDF)",
            data=pdf_plan_buffer,
            file_name="plan_sali_wizualizacja.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.info("👈 Aby rozpocząć, wgraj plik Excel z danymi w panelu bocznym.")
