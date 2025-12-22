import tkinter as tk
from tkinter import font as tkfont

# Modalità di default
APPEARANCE_MODE = "dark" # "dark" o "light"

# Colori base
COLORS = {
    # (Light Mode, Dark Mode)
    
    # Sfondo
    "bg_dark": ("#F3F4F6", "#1E1E1E"),      # Light: Grigio chiarissimo (Cool Grey) / Dark: Scuro
    "bg_sidebar": ("#FFFFFF", "#2D2D2D"),   # Light: Bianco puro / Dark: Grigio scuro
    "bg_card": ("#FFFFFF", "#3D3D3D"),      # Light: Bianco / Dark: Grigio medio
    "btn_ghost": ("#E5E7EB", "#2a2a2a"),    # Light: Grigio chiaro bordi / Dark: Scuro
    
    # Testo
    "text_primary": ("#374151", "#FFFFFF"), # Light: Grigio Scuro (Gray 700) / Dark: Bianco
    "text_secondary": ("#6B7280", "#A0A0A0"), # Light: Grigio medio / Dark: Grigio chiaro
    "text_on_accent": ("#1E1E1E", "#1E1E1E"), # Antracite caldo (meno aggressivo del nero puro)
    
    # Accenti (Rosa Centro Estetico)
    # Nel tema chiaro usiamo un rosa leggermente più saturo per leggibilità, se necessario
    "accent": ("#E8B4B8", "#E8B4B8"),       # Rosa principale (Pastello)
    "accent_hover": ("#D88EA3", "#F48FB1"), # Light: Rosa più scuro / Dark: Rosa acceso
    
    # Stati
    "success": ("#34D399", "#81C784"),      # Verde
    "success_hover": ("#10B981", "#66BB6A"), # Verde scuro per hover
    "warning": ("#FBBF24", "#FFB74D"),      # Arancione
    "error": ("#F87171", "#E57373"),        # Rosso
    
    # Bordi
    "border": ("#E5E7EB", "#404040"),       # Light: Grigio chiaro / Dark: Grigio scuro
    
    # Elementi Specifici
    "sidebar_hover": ("#F3F4F6", "#3D3D3D"), # Light: Grigio chiarissimo / Dark: Come bg_card
}

# Font 
FONTS = {
    "title": ("Helvetica Neue", -32, "bold"),
    "display": ("Helvetica Neue", -28, "bold"),
    "heading": ("Helvetica Neue", -18, "bold"),
    "body": ("Helvetica Neue", -17),
    "body_bold": ("Helvetica Neue", -17, "bold"),
    "small": ("Helvetica Neue", -14),
    "small_bold": ("Helvetica Neue", -14, "bold"),
    "button": ("Helvetica Neue", -15, "bold"),
}

# Dimensioni
SIZES = {
    "sidebar_width": 220,
    "header_height": 60,
    "card_padding": 20,
    "corner_radius": 12,         # Angoli arrotondati stile macOS
    "button_height": 40,
}
# Icone (emoji per ora)
ICONS = {
    "dashboard": "📊",
    "calendar": "📅",
    "clients": "👥",
    "staff": "👩‍💼",
    "services": "💅",
    "time": "⏱️",
    "cash": "💰",
    "phone": "📞",
    "email": "✉️",
    "reports": "📈",
    "settings": "⚙️",
    "backup": "💾",
    "accesso": "🔐",
    "logout": "🚪",
    "history": "📜",
    "notes": "📝",
    "alert": "⚠️",
    "notifications": "🔔",
    "success": "✅",
    "prev": "‹",
    "next": "›",
    "cancel_reason": "🛑",
    "status": "🏷️",
}

# Icone metodi di pagamento
PAYMENT_ICONS = {
    'contanti': '💵',
    'carta': '💳',
    'bonifico': '🏦',
    'satispay': '📱',
    'altro': '📋'
}

def get_font(font_key):
    """
    Restituisce il font primario se disponibile, 
    altrimenti il fallback standard (Arial).
    """
    try:
        # Ottiene la lista dei font disponibili nel sistema
        root = tk._default_root
        # Se non esiste una finestra, ne crea una temporanea, per ottenere la lista dei font.
        if root is None: 
            root = tk.Tk()
            # Nasconde la finestra temporanea.
            root.withdraw()
        avaible_fonts = tkfont.families()
    except:
        avaible_fonts = []

    # Prova il font primario
    primary = FONTS.get(font_key)
    if primary and primary[0] in avaible_fonts:
        return primary

    # Ultimo fallback: Arial esiste sempre
    return ("Arial", 14, "normal")