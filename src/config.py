# Geographic level mappings and configurations
GEO_LEVELS = ["Country", "State", "Metro", "County", "Zip"]

GEO_MAPPINGS = {
    "Country": {"display_name": "Country", "help_text": "National level data"},
    "State": {"display_name": "State", "help_text": "State level data"},
    "Metro": {"display_name": "Metro Area", "help_text": "Metropolitan Statistical Area data"},
    "County": {"display_name": "County", "help_text": "County level data"},
    "Zip": {"display_name": "ZIP Code", "help_text": "ZIP Code level data"}
}

# Style configurations for UI components
STYLE_OVERRIDES = {
    "clear": {
        "width": 20,
        "height": 20,
        "icon": "circle-filled",
        "clearable": "always"
    },
    "dropdown": {
        "rotate": False,
        "width": 0,
        "height": 0,
    },
    "searchbox": {
        "menuList": {
            "backgroundColor": "white",
            "maxHeight": "300px",
            "border": "1px solid #E5E7EB",
            "borderRadius": "12px",
            "marginTop": "4px",
            "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            "fontSize": "14px",
            "&::before": {
                "content": "'Suggestions'",
                "display": "block",
                "padding": "8px 12px",
                "color": "#6B7280",
                "fontSize": "12px",
                "fontWeight": "500",
                "borderBottom": "1px solid #E5E7EB",
                "backgroundColor": "#F9FAFB"
            }
        },
        "control": {
            "backgroundColor": "#F3F4F6",
            "border": "none",
            "borderRadius": "24px",
            "fontSize": "14px",
            "padding": "2px 8px"
        },
        "option": {
            "color": "#374151",
            "backgroundColor": "white",
            "highlightColor": "#fcf3cf",
            "fontSize": "14px",
            "&:hover": {
                "backgroundColor": "#F3F4F6"
            }
        },
        "singleValue": {
            "color": "#374151",
            "fontSize": "14px"
        },
        "placeholder": {
            "color": "#9CA3AF",
            "fontSize": "14px"
        }
    }
}

DEFAULT_LOCATIONS = [
    "National - United States",
    "State - California",
    "Metro - Los Angeles-Long Beach-Anaheim, CA",
    "County - Los Angeles, CA",
    "Zip - 90001, Los Angeles, CA"
]
