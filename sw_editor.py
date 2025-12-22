import os
import json
import re
from huggingface_hub import InferenceClient

# --- CONFIGURATION ---
INPUT_FILENAME = "wd_input.dat"
OUTPUT_FILENAME = "wd_input_new.dat"

# Access the environment variable 'HF_TOKEN'
HF_TOKEN = os.getenv("HF_TOKEN")
client = InferenceClient(api_key=HF_TOKEN)

def safe_extract_json(text):
    """Finds and extracts JSON structure from model response text."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        return None
    return None

def format_saver(old_str, new_val):
    """Maintains WD-specific precision and scientific notation (e.g., D+00)."""
    sci_char = next((c for c in ['D', 'd', 'E', 'e'] if c in old_str), None)
    try: 
        val = float(new_val)
    except: 
        return str(new_val)
    
    if sci_char:
        precision = len(old_str.split('.')[1].split(sci_char)[0]) if '.' in old_str else 6
        res = f"{{:.{precision}E}}".format(val).replace('E', sci_char)
        if '+' in old_str and '+' not in res and '-' not in res:
             parts = res.split(sci_char)
             res = f"{parts[0]}{sci_char}+{parts[1]}"
        return res
    else:
        decimals = len(old_str.split('.')[1]) if '.' in old_str else 0
        return f"{{:.{decimals}f}}".format(val)

def process_updates(updates_list, current_lines):
    """Coordinates and Aliases for Wilson-Devinney input files."""
    # Mapping keys are case-sensitive here to follow astronomical convention
    MAPPING = {
        # Line 1-3: Sigmas and Step Sizes (Del's)
        "DEL_A": (1, 0), "DEL_E": (1, 1), "DEL_PER": (1, 2), "DEL_I": (1, 6),
        "DEL_T1": (1, 9), "DEL_T2": (1, 10), "DEL_Q": (2, 4),

        # Line 8: Ephemeris & Phase Controls
        "HJD0": (7, 1), "P0": (7, 2), "DPDT": (7, 3), "PHS": (7, 4), 
        "DELPH": (7, 5), "NGA": (7, 6),

        # Line 9: Configuration & Grids
        "MODE": (8, 0), "IPB": (8, 1), "IFAT1": (8, 2), "IFAT2": (8, 3),
        "N1": (8, 4), "N2": (8, 5), "VUNIT": (8, 11), "VFAC": (8, 12),

        # Line 10: Main Orbital & Radiative Parameters
        "ECC": (9, 0), "A": (9, 1), "F1": (9, 2), "F2": (9, 3),
        "VGAM": (9, 4), "INCL": (9, 5), "G1": (9, 6), "G2": (9, 7), "MH": (9, 8),

        # Line 11: Surface & Thermodynamics
        "T1": (10, 0), "T2": (10, 1), "ALB1": (10, 2), "ALB2": (10, 3),
        "POT1": (10, 4), "POT2": (10, 5), "q": (10, 6),

        # Line 12: Third Body & Apparent Motion
        "A3B": (11, 0), "P3B": (11, 1), "INCL3B": (11, 2), "E3B": (11, 3),

        # Line 13: Flux & Limb Darkening (Curve specific)
        "L1": (12, 1), "L2": (12, 2), "X1": (12, 3), "X2": (12, 4), "EL3": (12, 7),
    }

    # --- EXTENDED ALIASES ---
    ALIASES = {
        # Orbital Geometry & Axis
        "SEMI_MAJOR_AXIS": "A", "SEMI_MAJ_AXIS": "A", "SMA": "A", "AXIS": "A", "A1_PLUS_A2": "A",
        "INCLINATION": "INCL", "INCL": "INCL", "ORBITAL_INCLINATION": "INCL", "I": "INCL",
        "ECCENTRICITY": "ECC", "ECC": "ECC", "E": "ECC",
        "VGAM": "VGAM", "V_GAMMA": "VGAM", "SYSTEMIC_VELOCITY": "VGAM", "GAMMA_VEL": "VGAM", "GAMMA": "VGAM",

        # Mass & Potential
        "MASS_RATIO": "q", "q": "q", "M2_M1": "q", "M2/M1": "q",
        "POTENTIAL1": "POT1", "POTENTIAL2": "POT2", "POT1": "POT1", "POT2": "POT2",
        "OMEGA1": "POT1", "OMEGA2": "POT2", "ROCHE_POTENTIAL1": "POT1", "ROCHE_POTENTIAL2": "POT2",
        "SURFACE_POTENTIAL1": "POT1", "SURFACE_POTENTIAL2": "POT2",

        # Temperatures & Albedo
        "TEMPERATURE1": "T1", "TEMPERATURE2": "T2", "TEMP1": "T1", "TEMP2": "T2", "T_EFF1": "T1", "T_EFF2": "T2",
        "ALBEDO1": "ALB1", "ALBEDO2": "ALB2", "ALB1": "ALB1", "ALB2": "ALB2",
        "GRAVITY_DARKENING1": "G1", "GRAVITY_DARKENING2": "G2", "G1": "G1", "G2": "G2",
        "METALLICITY": "MH", "MH": "MH", "[M/H]": "MH", "FE/H": "MH",

        # Timing & Ephemeris
        "PERIOD": "P0", "P0": "P0", "ORBITAL_PERIOD": "P0",
        "EPOCH": "HJD0", "HJD0": "HJD0", "T0": "HJD0", "REFERENCE_EPOCH": "HJD0",
        "PHASE_SHIFT": "PHS", "PHS": "PHS", "PSHIFT": "PHS",
        "DPDT": "DPDT", "DP/DT": "DPDT", "PERIOD_CHANGE": "DPDT",
        "DWDOT": "DWDOT", "PERIASTRON_ADVANCE": "DWDOT", "DW/DT": "DWDOT",

        # Rotation & Atmosphere
        "SYNC1": "F1", "SYNC2": "F2", "SYNCHRONICITY1": "F1", "SYNCHRONICITY2": "F2",
        "ROTATION1": "F1", "ROTATION2": "F2", "F1": "F1", "F2": "F2",
        "ATMOSPHERE1": "IFAT1", "ATMOSPHERE2": "IFAT2", "IFAT1": "IFAT1", "IFAT2": "IFAT2",

        # Luminosity & Limb Darkening (Curve Specific)
        "LUMINOSITY1": "L1", "LUMINOSITY2": "L2", "L1": "L1", "L2": "L2", "BRIGHTNESS1": "L1", "BRIGHTNESS2": "L2",
        "LIMB_DARKENING1": "X1", "LIMB_DARKENING2": "X2", "X1": "X1", "X2": "X2",
        "BOLOMETRIC_LD1": "X1BOLO", "BOLOMETRIC_LD2": "X2BOLO", "X1BOLO": "X1BOLO", "X2BOLO": "X2BOLO",
        "THIRD_LIGHT": "EL3", "L3": "EL3", "EL3": "EL3",

        # 3rd Body Parameters
        "3B_PERIOD": "P3B", "P3B": "P3B", "3RD_BODY_PERIOD": "P3B",
        "3B_INCLINATION": "INCL3B", "I3B": "INCL3B", "INCL3B": "INCL3B",
        "3B_ECCENTRICITY": "E3B", "E3B": "E3B", "3B_ECC": "E3B",
        "3B_SMA": "A3B", "A3B": "A3B", "3B_AXIS": "A3B",

        # Numerical Controls
        "SMEARING": "DELPH", "PHASE_INTEGRATION": "DELPH", "DELPH": "DELPH",
        "GRID1": "N1", "GRID2": "N2", "N1": "N1", "N2": "N2",
        "GAUSSIAN_POINTS": "NGA", "NGA": "NGA",

        # Step Sizes (Differential Corrections)
        "STEP_A": "DEL_A", "STEP_E": "DEL_E", "STEP_I": "DEL_I", "STEP_Q": "DEL_Q",
        "DEL_A": "DEL_A", "DEL_E": "DEL_E", "DEL_I": "DEL_I", "DEL_Q": "DEL_Q"
    }


    for update in updates_list:
        raw_name = str(update.get('parameter_name', ''))
        # First, try exact match (to catch lowercase 'q')
        target = ALIASES.get(raw_name, raw_name)
        
        # If not in mapping, try uppercase version for standard parameters
        if target not in MAPPING:
            target = ALIASES.get(raw_name.upper(), raw_name.upper())

        mode = update.get('mode', 'set') 
        val = update.get('value', update.get('new_value'))

        if target in MAPPING:
            r, c = MAPPING[target]
            tokens = current_lines[r].split()
            try:
                old_val_str = tokens[c]
                old_val_float = float(old_val_str.replace('D', 'E').replace('d', 'e'))
                
                if mode == 'add': new_val = old_val_float + float(val)
                elif mode == 'sub': new_val = old_val_float - float(val)
                else: new_val = float(val)
                
                formatted = format_saver(old_val_str, new_val)
                tokens[c] = formatted
                current_lines[r] = "   ".join(tokens) + "\n"
                print(f" [SUCCESS] {target}: {old_val_str} -> {formatted} ({mode})")
            except (IndexError, ValueError):
                print(f" [ERROR] Could not parse line {r} for {target}")
        else:
            print(f" [SKIP] Parameter '{target}' not found in mapping.")
            
    return current_lines

def main():
    if not os.path.exists(INPUT_FILENAME):
        print(f"Error: {INPUT_FILENAME} not found!"); return
    
    with open(INPUT_FILENAME, "r") as f: 
        session_lines = f.readlines()
    
    print("\n>>> WD Smart Editor (Cloud Mode) Ready.")
    print(">>> Note: 'q' is treated as mass ratio unless entered alone to quit.")
    
    while True:
        cmd = input("\nCommand (q for exit): ").strip()
        
        # Fixed Quit Logic: Only exit if the input is exactly 'q' or 'exit'
        if cmd.lower() in ['q', 'exit']: 
            print(f">>> Finalizing {OUTPUT_FILENAME} and exiting.")
            break
        if not cmd:
            continue
        
        try:
            response = client.chat_completion(
                model="google/gemma-2-2b-it",
                messages=[
                    {"role": "system", "content": "Return JSON ONLY. Format: {\"updates\": [{\"parameter_name\": \"q\", \"mode\": \"set\", \"value\": 0.5}]}. Use lowercase 'q' for mass ratio."},
                    {"role": "user", "content": cmd}
                ],
                max_tokens=100
            )
            data = safe_extract_json(response.choices[0].message.content)
            
            if data and 'updates' in data:
                session_lines = process_updates(data['updates'], session_lines)
                with open(OUTPUT_FILENAME, "w") as f: 
                    f.writelines(session_lines)
            else:
                print("Could not parse command. The AI returned unexpected text.")
        except Exception as e:
            print(f"API Error: {e}")

if __name__ == "__main__":
    main()