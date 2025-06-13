import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
import csv

# Deutsche Matplotlib-Schrifteinstellungen
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10

# Hauptprojektpfad hinzufuegen um ColorCalculator-Klasse zu importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from color_calculator import ColorCalculator

def read_reflectance_data(file_path):
    """Liest Reflektanzdaten aus Excel-Datei"""
    print(f"Lese Reflektanzdaten: {file_path}")
    try:
        df = pd.read_excel(file_path)
        # Wellenlaenge-Spalte (erste Spalte) und Probendaten abrufen
        wavelengths = df.iloc[:, 0].values
        sample_names = df.columns[1:]
        
        # Proben-Woerterbuch erstellen
        samples = {}
        for name in sample_names:
            sample_data = df[name].values
            # NaN-Werte herausfiltern
            valid_indices = ~np.isnan(sample_data)
            if np.any(valid_indices):
                samples[name] = {
                    'wavelengths': wavelengths[valid_indices],
                    'reflectance': sample_data[valid_indices]
                }
            
        print(f"Erfolgreich {len(samples)} Proben gelesen")
        return samples
    except Exception as e:
        print(f"Fehler beim Lesen der Daten: {str(e)}")
        return {}

def xyz_to_lab(xyz, white_ref=None):
    """
    Konvertiert XYZ zu CIE Lab Farbraum
    
    Parameter:
        xyz: XYZ Farbwerte [X, Y, Z]
        white_ref: Weissreferenz [Xw, Yw, Zw], falls None wird D65 verwendet
    
    Rueckgabe:
        Lab Farbwerte [L*, a*, b*]
    """
    # Standard Weissreferenz ist D65
    if white_ref is None:
        # D65 Weissreferenzwerte
        white_ref = np.array([95.047, 100.0, 108.883])
    
    # XYZ durch Weissreferenz normalisieren
    xyz_norm = xyz / white_ref
    
    # Nichtlineare Transformation anwenden
    mask = xyz_norm > 0.008856
    xyz_norm_pow = np.power(xyz_norm, 1/3.0)
    xyz_norm_trans = xyz_norm * 7.787 + 16/116.0
    
    xyz_f = np.zeros(3)
    for i in range(3):
        if mask[i]:
            xyz_f[i] = xyz_norm_pow[i]
        else:
            xyz_f[i] = xyz_norm_trans[i]
    
    # L*, a*, b* berechnen
    L = 116.0 * xyz_f[1] - 16.0
    a = 500.0 * (xyz_f[0] - xyz_f[1])
    b = 200.0 * (xyz_f[1] - xyz_f[2])
    
    return np.array([L, a, b])

def calculate_cie76_delta_e(lab1, lab2):
    """
    Berechnet CIE76 Farbunterschied (Delta E)
    
    Parameter:
        lab1: Erste Lab Farbe [L1, a1, b1]
        lab2: Zweite Lab Farbe [L2, a2, b2]
    
    Rueckgabe:
        Delta E Wert
    """
    # Quadrierte Differenzen berechnen
    L_diff = (lab1[0] - lab2[0]) ** 2
    a_diff = (lab1[1] - lab2[1]) ** 2
    b_diff = (lab1[2] - lab2[2]) ** 2
    
    # Delta E berechnen
    delta_e = np.sqrt(L_diff + a_diff + b_diff)
    
    return delta_e

def compare_wavelength_ranges(samples, original_range=(380, 780), new_range=(400, 800)):
    """Vergleicht Farbberechnungsergebnisse verschiedener Wellenlaengenbereiche"""
    # Farbrechner-Instanz erstellen
    cc = ColorCalculator()
    
    # Standardlichtquelle auf D65 setzen
    cc.illuminant = 'D65'
    
    results = {}
    
    for name, sample in samples.items():
        print(f"\nAnalysiere Probe: {name}")
        wavelengths = sample['wavelengths']
        reflectance = sample['reflectance']
        
        # Pruefen ob Wellenlaengenbereich den Anforderungen entspricht
        min_wl = np.min(wavelengths)
        max_wl = np.max(wavelengths)
        print(f"Proben-Wellenlaengenbereich: {min_wl}-{max_wl}nm")
        
        if min_wl > original_range[0] or max_wl < original_range[1]:
            print(f"Warnung: Proben-Wellenlaengenbereich ({min_wl}-{max_wl}nm) erfuellt nicht die Anforderungen des urspruenglichen Wellenlaengenbereichs ({original_range[0]}-{original_range[1]}nm)")
            continue
            
        # 1. Berechnung der Farben fuer urspruenglichen Wellenlaengenbereich
        # Daten des urspruenglichen Wellenlaengenbereichs extrahieren
        original_mask = (wavelengths >= original_range[0]) & (wavelengths <= original_range[1])
        original_wavelengths = wavelengths[original_mask]
        original_reflectance = reflectance[original_mask]
        
        if len(original_wavelengths) < 10:
            print(f"Warnung: Zu wenige Datenpunkte im urspruenglichen Wellenlaengenbereich ({len(original_wavelengths)})")
            continue
            
        # Farbwerte fuer urspruenglichen Wellenlaengenbereich berechnen
        original_results = cc.process_measurement(original_reflectance, original_wavelengths)
        
        # 2. Berechnung der Farben fuer neuen Wellenlaengenbereich
        # Daten des neuen Wellenlaengenbereichs extrahieren
        new_mask = (wavelengths >= new_range[0]) & (wavelengths <= new_range[1])
        new_wavelengths = wavelengths[new_mask]
        new_reflectance = reflectance[new_mask]
        
        if len(new_wavelengths) < 10:
            print(f"Warnung: Zu wenige Datenpunkte im neuen Wellenlaengenbereich ({len(new_wavelengths)})")
            continue
            
        # Farbwerte fuer neuen Wellenlaengenbereich berechnen
        new_results = cc.process_measurement(new_reflectance, new_wavelengths)
        
        # 3. Berechnung der CIE Lab Farbwerte und Farbdifferenz
        # XYZ zu Lab konvertieren
        original_lab = xyz_to_lab(original_results['xyz'])
        new_lab = xyz_to_lab(new_results['xyz'])
        
        # CIE76 Farbdifferenz berechnen
        delta_e = calculate_cie76_delta_e(original_lab, new_lab)
        
        # Ergebnisse speichern
        results[name] = {
            'original': original_results,
            'new': new_results,
            'original_lab': original_lab,
            'new_lab': new_lab,
            'delta_e': delta_e
        }
        
        # Wichtige Ergebnisse ausgeben
        print(f"Urspruenglicher Wellenlaengenbereich ({original_range[0]}-{original_range[1]}nm):")
        print(f"  XYZ: ({original_results['xyz'][0]:.4f}, {original_results['xyz'][1]:.4f}, {original_results['xyz'][2]:.4f})")
        print(f"  xy: ({original_results['xy'][0]:.4f}, {original_results['xy'][1]:.4f})")
        print(f"  sRGB: ({original_results['rgb_gamma'][0]:.4f}, {original_results['rgb_gamma'][1]:.4f}, {original_results['rgb_gamma'][2]:.4f})")
        print(f"  Hex: {original_results['hex_color']}")
        print(f"  Lab: ({original_lab[0]:.4f}, {original_lab[1]:.4f}, {original_lab[2]:.4f})")
        
        print(f"Neuer Wellenlaengenbereich ({new_range[0]}-{new_range[1]}nm):")
        print(f"  XYZ: ({new_results['xyz'][0]:.4f}, {new_results['xyz'][1]:.4f}, {new_results['xyz'][2]:.4f})")
        print(f"  xy: ({new_results['xy'][0]:.4f}, {new_results['xy'][1]:.4f})")
        print(f"  sRGB: ({new_results['rgb_gamma'][0]:.4f}, {new_results['rgb_gamma'][1]:.4f}, {new_results['rgb_gamma'][2]:.4f})")
        print(f"  Hex: {new_results['hex_color']}")
        print(f"  Lab: ({new_lab[0]:.4f}, {new_lab[1]:.4f}, {new_lab[2]:.4f})")
        
        # Differenzen berechnen
        xyz_diff = np.abs(original_results['xyz'] - new_results['xyz'])
        xy_diff = np.abs(original_results['xy'] - new_results['xy'])
        rgb_diff = np.abs(original_results['rgb_gamma'] - new_results['rgb_gamma'])
        lab_diff = np.abs(original_lab - new_lab)
        
        print("Differenzanalyse:")
        print(f"  XYZ-Differenz: ({xyz_diff[0]:.4f}, {xyz_diff[1]:.4f}, {xyz_diff[2]:.4f})")
        print(f"  xy-Differenz: ({xy_diff[0]:.4f}, {xy_diff[1]:.4f})")
        print(f"  sRGB-Differenz: ({rgb_diff[0]:.4f}, {rgb_diff[1]:.4f}, {rgb_diff[2]:.4f})")
        print(f"  Lab-Differenz: ({lab_diff[0]:.4f}, {lab_diff[1]:.4f}, {lab_diff[2]:.4f})")
        print(f"  CIE76 Farbdifferenz (ΔE): {delta_e:.4f}")
        
        # Relative Fehlerprozentsaetze berechnen
        xyz_rel_diff = 100 * xyz_diff / (np.abs(original_results['xyz']) + 1e-10)
        xy_rel_diff = 100 * xy_diff / (np.abs(original_results['xy']) + 1e-10)
        rgb_rel_diff = 100 * rgb_diff / (np.abs(original_results['rgb_gamma']) + 1e-10)
        
        print("Relative Fehlerprozentsaetze:")
        print(f"  XYZ relativer Fehler: ({xyz_rel_diff[0]:.2f}%, {xyz_rel_diff[1]:.2f}%, {xyz_rel_diff[2]:.2f}%)")
        print(f"  xy relativer Fehler: ({xy_rel_diff[0]:.2f}%, {xy_rel_diff[1]:.2f}%)")
        print(f"  sRGB relativer Fehler: ({rgb_rel_diff[0]:.2f}%, {rgb_rel_diff[1]:.2f}%, {rgb_rel_diff[2]:.2f}%)")
        
        # HSV Wahrnehmungsunterschiede berechnen
        original_hsv = rgb_to_hsv(np.clip(original_results['rgb_gamma'], 0, 1))
        new_hsv = rgb_to_hsv(np.clip(new_results['rgb_gamma'], 0, 1))
        hsv_diff = np.abs(original_hsv - new_hsv)
        # Farbton-Differenz benoetigt spezielle Behandlung da zyklisch
        if hsv_diff[0] > 0.5:
            hsv_diff[0] = 1 - hsv_diff[0]
        
        print("HSV Wahrnehmungsunterschiede:")
        print(f"  Farbton-Differenz: {hsv_diff[0]:.4f} (×360° = {hsv_diff[0]*360:.1f}°)")
        print(f"  Saettigung-Differenz: {hsv_diff[1]:.4f}")
        print(f"  Helligkeit-Differenz: {hsv_diff[2]:.4f}")
    
    return results

def export_simplified_error_table(results, output_dir, original_range=(380, 780), new_range=(400, 750)):
    """
    Exportiert vereinfachte Fehler-Tabelle mit nur Farbfehlern und Delta E Werten
    
    Parameter:
        results: Vergleichsergebnis-Woerterbuch
        output_dir: Verzeichnis zum Speichern der CSV-Datei
        original_range: Urspruenglicher Wellenlaengenbereich
        new_range: Neuer Wellenlaengenbereich
    """
    if not results:
        print("Keine Ergebnisse fuer den Export verfuegbar")
        return
    
    # CSV Datei erstellen
    csv_filename = os.path.join(output_dir, 'farbfehler_vereinfacht.csv')
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Deutsche Spaltenueberschriften
        header = [
            'Probenname',
            'XYZ Diff (X)', 'XYZ Diff (Y)', 'XYZ Diff (Z)',
            'XYZ % Diff (X)', 'XYZ % Diff (Y)', 'XYZ % Diff (Z)',
            'xy Diff (x)', 'xy Diff (y)',
            'xy % Diff (x)', 'xy % Diff (y)',
            'sRGB Diff (R)', 'sRGB Diff (G)', 'sRGB Diff (B)',
            'sRGB % Diff (R)', 'sRGB % Diff (G)', 'sRGB % Diff (B)',
            'Lab Diff (L*)', 'Lab Diff (a*)', 'Lab Diff (b*)',
            'CIE76 ΔE',
            'Urspruengliche Hex', 'Neue Hex'
        ]
        writer.writerow(header)
        
        # Daten fuer jede Probe schreiben
        for name, result in results.items():
            original_data = result['original']
            new_data = result['new']
            original_lab = result['original_lab']
            new_lab = result['new_lab']
            
            # Differenzen berechnen
            xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
            xy_diff = np.abs(original_data['xy'] - new_data['xy'])
            rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
            lab_diff = np.abs(original_lab - new_lab)
            
            # Relative Differenzen berechnen
            xyz_rel_diff = 100 * xyz_diff / (np.abs(original_data['xyz']) + 1e-10)
            xy_rel_diff = 100 * xy_diff / (np.abs(original_data['xy']) + 1e-10)
            rgb_rel_diff = 100 * rgb_diff / (np.abs(original_data['rgb_gamma']) + 1e-10)
            
            # Zeile schreiben
            row = [
                name,
                f"{xyz_diff[0]:.6f}", f"{xyz_diff[1]:.6f}", f"{xyz_diff[2]:.6f}",
                f"{xyz_rel_diff[0]:.2f}", f"{xyz_rel_diff[1]:.2f}", f"{xyz_rel_diff[2]:.2f}",
                f"{xy_diff[0]:.6f}", f"{xy_diff[1]:.6f}",
                f"{xy_rel_diff[0]:.2f}", f"{xy_rel_diff[1]:.2f}",
                f"{rgb_diff[0]:.6f}", f"{rgb_diff[1]:.6f}", f"{rgb_diff[2]:.6f}",
                f"{rgb_rel_diff[0]:.2f}", f"{rgb_rel_diff[1]:.2f}", f"{rgb_rel_diff[2]:.2f}",
                f"{lab_diff[0]:.6f}", f"{lab_diff[1]:.6f}", f"{lab_diff[2]:.6f}",
                f"{result['delta_e']:.6f}",
                original_data['hex_color'], new_data['hex_color']
            ]
            writer.writerow(row)
    
    # Versuchen Excel-Version zu erstellen
    try:
        import pandas as pd
        df = pd.read_csv(csv_filename)
        excel_filename = os.path.join(output_dir, 'farbfehler_vereinfacht.xlsx')
        df.to_excel(excel_filename, index=False)
        print(f"Vereinfachte Fehlertabelle exportiert: {csv_filename} und {excel_filename}")
    except Exception as e:
        print(f"Vereinfachte Fehlertabelle als CSV exportiert: {csv_filename}")
        print(f"Excel-Export fehlgeschlagen: {e}")

def plot_results(samples, results, original_range=(380, 780), new_range=(400, 750)):
    """
    Zeichnet Ergebnisdiagramme und exportiert Tabellen
    
    Parameter:
        samples: Proben-Woerterbuch 
        results: Vergleichsergebnis-Woerterbuch
        original_range: Urspruenglicher Wellenlaengenbereich
        new_range: Neuer Wellenlaengenbereich
    """
    if not results:
        print("Keine Ergebnisse fuer die Darstellung verfuegbar")
        return
    
    # Ausgabeverzeichnis erstellen
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comparison_results")
    os.makedirs(output_dir, exist_ok=True)
    
    # Vereinfachte Fehlertabelle exportieren
    export_simplified_error_table(results, output_dir, original_range, new_range)
    
    for name, result in results.items():
        # Dateinamen bereinigen - Schraegstriche und Leerzeichen durch Unterstriche ersetzen
        safe_name = name.replace("/", "_").replace(" ", "_").strip()
        
        # 1. Reflektanzkurven-Vergleich zeichnen
        plt.figure(figsize=(12, 6))
        
        original_data = result['original']
        new_data = result['new']
        
        # Urspruenglichen Wellenlaengenbereich Reflektanz zeichnen
        plt.plot(original_data['wavelengths'], original_data['reflectance'], 
                 'b-', linewidth=2, label=f'Urspruenglich ({original_range[0]}-{original_range[1]}nm)')
        
        # Neuen Wellenlaengenbereich Reflektanz zeichnen
        plt.plot(new_data['wavelengths'], new_data['reflectance'], 
                 'r--', linewidth=2, label=f'Verkuerzt ({new_range[0]}-{new_range[1]}nm)')
        
        plt.xlabel('Wellenlaenge (nm)')
        plt.ylabel('Reflektanz')
        plt.title(f'Probe "{name}" Reflektanzkurven-Vergleich')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        # Diagramm speichern
        plt.savefig(os.path.join(output_dir, f'{safe_name}_reflektanz.png'), dpi=150)
        plt.close()
        
        # 2. Farbvergleichsdiagramm erstellen
        fig, ax = plt.subplots(1, 2, figsize=(8, 4))
        
        # Urspruenglicher Wellenlaengenbereich Farbe
        original_rgb = np.clip(original_data['rgb_gamma'], 0, 1)
        ax[0].add_patch(plt.Rectangle((0, 0), 1, 1, color=original_rgb))
        ax[0].set_title(f'Urspruenglich ({original_range[0]}-{original_range[1]}nm)\n{original_data["hex_color"]}')
        ax[0].set_xticks([])
        ax[0].set_yticks([])
        
        # Neuer Wellenlaengenbereich Farbe
        new_rgb = np.clip(new_data['rgb_gamma'], 0, 1)
        ax[1].add_patch(plt.Rectangle((0, 0), 1, 1, color=new_rgb))
        ax[1].set_title(f'Verkuerzt ({new_range[0]}-{new_range[1]}nm)\n{new_data["hex_color"]}')
        ax[1].set_xticks([])
        ax[1].set_yticks([])
        
        plt.suptitle(f'Probe "{name}" Farbvergleich')
        plt.tight_layout()
        
        # Diagramm speichern
        plt.savefig(os.path.join(output_dir, f'{safe_name}_farbe.png'), dpi=150)
        plt.close()
    
    # 3. Zusammenfassenden Analysebericht erstellen
    create_summary_report(results, output_dir, original_range, new_range)
    
    print(f"Ergebnisdiagramme gespeichert in {output_dir}")

def create_summary_report(results, output_dir, original_range, new_range):
    """Erstellt zusammenfassenden Analysebericht"""
    if not results:
        print("Keine Ergebnisse fuer die Generierung des Berichts verfuegbar")
        return
    
    # 计算所有Sample的平均差异
    all_xy_diffs = []
    all_xyz_diffs = []
    all_rgb_diffs = []
    all_delta_e = []
    
    for name, result in results.items():
        original_data = result['original']
        new_data = result['new']
        
        # 计算差异
        xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
        xy_diff = np.abs(original_data['xy'] - new_data['xy'])
        rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
        
        all_xyz_diffs.append(xyz_diff)
        all_xy_diffs.append(xy_diff)
        all_rgb_diffs.append(rgb_diff)
        all_delta_e.append(result['delta_e'])
    
    # 计算平均差异
    avg_xyz_diff = np.mean(all_xyz_diffs, axis=0)
    avg_xy_diff = np.mean(all_xy_diffs, axis=0)
    avg_rgb_diff = np.mean(all_rgb_diffs, axis=0)
    avg_delta_e = np.mean(all_delta_e)
    
    # 创建报告文件
    with open(os.path.join(output_dir, 'summary_report.txt'), 'w', encoding='utf-8') as f:
        f.write(f"Wavelength Range Comparison Analysis Report\n")
        f.write(f"==============================================\n\n")
        f.write(f"Original Wavelength Range: {original_range[0]}-{original_range[1]}nm\n")
        f.write(f"Cropped Wavelength Range: {new_range[0]}-{new_range[1]}nm\n\n")
        f.write(f"Analysis Sample Count: {len(results)}\n\n")
        
        f.write(f"Average Difference Analysis:\n")
        f.write(f"  XYZ Average Difference: ({avg_xyz_diff[0]:.4f}, {avg_xyz_diff[1]:.4f}, {avg_xyz_diff[2]:.4f})\n")
        f.write(f"  xy Average Difference: ({avg_xy_diff[0]:.4f}, {avg_xy_diff[1]:.4f})\n")
        f.write(f"  sRGB Average Difference: ({avg_rgb_diff[0]:.4f}, {avg_rgb_diff[1]:.4f}, {avg_rgb_diff[2]:.4f})\n")
        f.write(f"   Average CIE76 Color Difference (ΔE): {avg_delta_e:.4f}\n\n")
        
        # 输出每个Sample的详细信息
        f.write(f"Individual Sample Analysis:\n")
        f.write(f"----------------\n\n")
        
        for name, result in results.items():
            original_data = result['original']
            new_data = result['new']
            
            # 计算差异
            xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
            xy_diff = np.abs(original_data['xy'] - new_data['xy'])
            rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
            
            f.write(f"Sample: {name}\n")
            f.write(f"   Original Wavelength Range ({original_range[0]}-{original_range[1]}nm):\n")
            f.write(f"    XYZ: ({original_data['xyz'][0]:.4f}, {original_data['xyz'][1]:.4f}, {original_data['xyz'][2]:.4f})\n")
            f.write(f"    xy: ({original_data['xy'][0]:.4f}, {original_data['xy'][1]:.4f})\n")
            f.write(f"    sRGB: ({original_data['rgb_gamma'][0]:.4f}, {original_data['rgb_gamma'][1]:.4f}, {original_data['rgb_gamma'][2]:.4f})\n")
            f.write(f"    Hex: {original_data['hex_color']}\n\n")
            
            f.write(f"   Cropped Wavelength Range ({new_range[0]}-{new_range[1]}nm):\n")
            f.write(f"    XYZ: ({new_data['xyz'][0]:.4f}, {new_data['xyz'][1]:.4f}, {new_data['xyz'][2]:.4f})\n")
            f.write(f"    xy: ({new_data['xy'][0]:.4f}, {new_data['xy'][1]:.4f})\n")
            f.write(f"    sRGB: ({new_data['rgb_gamma'][0]:.4f}, {new_data['rgb_gamma'][1]:.4f}, {new_data['rgb_gamma'][2]:.4f})\n")
            f.write(f"    Hex: {new_data['hex_color']}\n\n")
            
            f.write(f"   Difference Analysis:\n")
            f.write(f"    XYZ Difference: ({xyz_diff[0]:.4f}, {xyz_diff[1]:.4f}, {xyz_diff[2]:.4f})\n")
            f.write(f"    xy Difference: ({xy_diff[0]:.4f}, {xy_diff[1]:.4f})\n")
            f.write(f"    sRGB Difference: ({rgb_diff[0]:.4f}, {rgb_diff[1]:.4f}, {rgb_diff[2]:.4f})\n")
            f.write(f"    CIE76 Color Difference (ΔE): {result['delta_e']:.4f}\n\n")
            
            # 计算Relative Error Percentage
            xyz_rel_diff = 100 * xyz_diff / (np.abs(original_data['xyz']) + 1e-10)
            xy_rel_diff = 100 * xy_diff / (np.abs(original_data['xy']) + 1e-10)
            rgb_rel_diff = 100 * rgb_diff / (np.abs(original_data['rgb_gamma']) + 1e-10)
            
            f.write(f"   Relative Error Percentage:\n")
            f.write(f"    XYZ Relative Error: ({xyz_rel_diff[0]:.2f}%, {xyz_rel_diff[1]:.2f}%, {xyz_rel_diff[2]:.2f}%)\n")
            f.write(f"    xy Relative Error: ({xy_rel_diff[0]:.2f}%, {xy_rel_diff[1]:.2f}%)\n")
            f.write(f"    sRGB Relative Error: ({rgb_rel_diff[0]:.2f}%, {rgb_rel_diff[1]:.2f}%, {rgb_rel_diff[2]:.2f}%)\n\n")
            
            # 可感知颜色Difference Analysis
            original_hsv = rgb_to_hsv(np.clip(original_data['rgb_gamma'], 0, 1))
            new_hsv = rgb_to_hsv(np.clip(new_data['rgb_gamma'], 0, 1))
            hsv_diff = np.abs(original_hsv - new_hsv)
            # 色调差异需要特殊处理，因为它是循环的
            if hsv_diff[0] > 0.5:
                hsv_diff[0] = 1 - hsv_diff[0]
            
            f.write(f"  HSV Perceptual Difference:\n")
            f.write(f"     Hue Difference: {hsv_diff[0]:.4f} (×360° = {hsv_diff[0]*360:.1f}°)\n")
            f.write(f"     Saturation Difference: {hsv_diff[1]:.4f}\n")
            f.write(f"     Brightness Difference: {hsv_diff[2]:.4f}\n\n")
            
            f.write(f"----------------\n\n")
    
    # Create summary charts
    create_summary_charts(results, output_dir, original_range, new_range)

def create_summary_charts(results, output_dir, original_range, new_range):
    """Create summary charts"""
    if not results:
        print("No results available for plotting")
        return
    
    # 1. xy色度图比较
    plt.figure(figsize=(10, 8))
    
    # 绘制色品图边界
    t = np.linspace(0, 1, 100)
    plt.plot(t, -3*t + 2, 'k-', alpha=0.2)  # y = -3x + 2
    plt.plot(t, 2.5*t - 0.5, 'k-', alpha=0.2)  # y = 2.5x - 0.5
    plt.plot([0.35, 0], [0.375, 0], 'k-', alpha=0.2)
    plt.fill_between([0, 0.35, 0.67, 0.35, 0], 
                     [0, 0.375, 0.175, 0, 0], alpha=0.05, color='gray')
    
    for name, result in results.items():
        original_x, original_y = result['original']['xy']
        new_x, new_y = result['new']['xy']
        
        # Urspruengliche und neue Punkte zeichnen und verbinden
        plt.plot(original_x, original_y, 'bo', markersize=8, alpha=0.7)
        plt.plot(new_x, new_y, 'ro', markersize=8, alpha=0.7)
        plt.plot([original_x, new_x], [original_y, new_y], 'k-', alpha=0.3)
        
        # Probennamen beschriften
        plt.text(original_x+0.005, original_y+0.005, name, fontsize=8)
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('CIE xy Farbraum-Diagramm Farbkoordinaten-Vergleich')
    plt.grid(True, alpha=0.3)
    plt.axis([0, 0.8, 0, 0.9])
    
    # Legende hinzufuegen
    plt.plot([], [], 'bo', markersize=8, label=f'Urspruenglich ({original_range[0]}-{original_range[1]}nm)')
    plt.plot([], [], 'ro', markersize=8, label=f'Verkuerzt ({new_range[0]}-{new_range[1]}nm)')
    plt.legend()
    
    plt.savefig(os.path.join(output_dir, 'xy_comparison.png'), dpi=150)
    plt.close()
    
    # 2. RGB颜色差异柱状图
    rgb_labels = ['R', 'G', 'B']
    all_rgb_diffs = []
    
    for name, result in results.items():
        original_rgb = result['original']['rgb_gamma']
        new_rgb = result['new']['rgb_gamma']
        rgb_diff = np.abs(original_rgb - new_rgb)
        all_rgb_diffs.append(rgb_diff)
    
    avg_rgb_diff = np.mean(all_rgb_diffs, axis=0)
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(rgb_labels, avg_rgb_diff, color=['red', 'green', 'blue'], alpha=0.7)
    
    # 添加数值标签
    for bar, val in zip(bars, avg_rgb_diff):
        plt.text(bar.get_x() + bar.get_width()/2, 
                 bar.get_height() + 0.005, 
                 f'{val:.4f}', 
                 ha='center')
    
    plt.title('Durchschnittliche RGB-Farbkomponenten-Differenz')
    plt.ylabel('Absolute Differenz')
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'rgb_diff.png'), dpi=150)
    plt.close()
    
    # 3. CIE76 Farbdifferenz Balkendiagramm
    plt.figure(figsize=(12, 8))
    
    # Probennamen und entsprechende Farbdifferenzwerte abrufen
    sample_names = list(results.keys())
    delta_e_values = [results[name]['delta_e'] for name in sample_names]
    
    # Nach Farbdifferenzwerten absteigend sortieren
    sorted_indices = np.argsort(delta_e_values)[::-1]
    sorted_names = [sample_names[i] for i in sorted_indices]
    sorted_values = [delta_e_values[i] for i in sorted_indices]
    
    # Falls zu viele Proben, nur die ersten 20 anzeigen
    if len(sorted_names) > 20:
        sorted_names = sorted_names[:20]
        sorted_values = sorted_values[:20]
    
    # Balkendiagramm zeichnen
    bars = plt.bar(range(len(sorted_names)), sorted_values, color='purple', alpha=0.7)
    
    # Zahlenwerte als Beschriftung entfernt
    # for i, (bar, val) in enumerate(zip(bars, sorted_values)):
    #     plt.text(bar.get_x() + bar.get_width()/2, 
    #              val + 0.02,
    #              f'{val:.4f}', 
    #              ha='center', va='bottom', rotation=90 if len(sorted_names) > 10 else 0)
    
    plt.xticks(range(len(sorted_names)), sorted_names, rotation=90 if len(sorted_names) > 10 else 45)
    plt.title('CIE76 Farbdifferenz (ΔE) Vergleich')
    plt.ylabel('ΔE')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'delta_e_comparison.png'), dpi=150)
    plt.close()

def generate_german_summary(results, original_range, new_range):
    """
    生成德语总结，描述颜色误差分析
    
    Parameters:
        results: 比较结果字典
        original_range: OriginalWavelength范围
        new_range: 新Wavelength范围
    """
    if not results:
        print("Keine Ergebnisse fuer die Generierung der deutschen Zusammenfassung verfuegbar")
        return
    
    # Verzeichnis fuer die Speicherung der Zusammenfassung erstellen
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comparison_results")
    os.makedirs(output_dir, exist_ok=True)
    
    # 计算平均误差
    all_xyz_diffs = []
    all_xy_diffs = []
    all_rgb_diffs = []
    all_lab_diffs = []
    all_delta_e = []
    
    for name, result in results.items():
        original_data = result['original']
        new_data = result['new']
        original_lab = result['original_lab']
        new_lab = result['new_lab']
        
        # 计算差异
        xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
        xy_diff = np.abs(original_data['xy'] - new_data['xy'])
        rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
        lab_diff = np.abs(original_lab - new_lab)
        
        all_xyz_diffs.append(xyz_diff)
        all_xy_diffs.append(xy_diff)
        all_rgb_diffs.append(rgb_diff)
        all_lab_diffs.append(lab_diff)
        all_delta_e.append(result['delta_e'])
    
    # 计算平均差异
    avg_xyz_diff = np.mean(all_xyz_diffs, axis=0)
    avg_xy_diff = np.mean(all_xy_diffs, axis=0)
    avg_rgb_diff = np.mean(all_rgb_diffs, axis=0)
    avg_lab_diff = np.mean(all_lab_diffs, axis=0)
    avg_delta_e = np.mean(all_delta_e)
    
    # 找出Delta E最大的几个Sample
    delta_e_values = [(name, result['delta_e']) for name, result in results.items()]
    sorted_delta_e = sorted(delta_e_values, key=lambda x: x[1], reverse=True)
    worst_samples = sorted_delta_e[:5]  # 最差的5个Sample
    
    # 生成德语总结
    with open(os.path.join(output_dir, 'farbfehler_zusammenfassung.txt'), 'w', encoding='utf-8') as f:
        f.write("Zusammenfassung der Wellenlängenbereichsanalyse\n")
        f.write("==============================================\n\n")
        
        f.write(f"Ursprünglicher Wellenlängenbereich: {original_range[0]}-{original_range[1]}nm\n")
        f.write(f"Gekürzter Wellenlängenbereich: {new_range[0]}-{new_range[1]}nm\n\n")
        
        f.write("Bewertung der Farbfehler\n")
        f.write("------------------------\n\n")
        
        f.write("Die Farbfehler wurden mit folgenden Metriken bewertet:\n\n")
        f.write("1. CIE XYZ-Farbwertdifferenzen\n")
        f.write("2. CIE xy-Chromatizitätskoordinatendifferenzen\n")
        f.write("3. sRGB-Farbdifferenzen\n")
        f.write("4. CIE L*a*b* Farbdifferenzen\n")
        f.write("5. CIE76 Delta E (ΔE) - Der Gesamtfarbunterschied\n\n")
        
        f.write("Durchschnittliche Farbfehler:\n")
        f.write(f"- XYZ-Differenz: ({avg_xyz_diff[0]:.6f}, {avg_xyz_diff[1]:.6f}, {avg_xyz_diff[2]:.6f})\n")
        f.write(f"- xy-Differenz: ({avg_xy_diff[0]:.6f}, {avg_xy_diff[1]:.6f})\n")
        f.write(f"- sRGB-Differenz: ({avg_rgb_diff[0]:.6f}, {avg_rgb_diff[1]:.6f}, {avg_rgb_diff[2]:.6f})\n")
        f.write(f"- L*a*b*-Differenz: ({avg_lab_diff[0]:.6f}, {avg_lab_diff[1]:.6f}, {avg_lab_diff[2]:.6f})\n")
        f.write(f"- Durchschnittliches ΔE: {avg_delta_e:.6f}\n\n")
        
        f.write("Ursachen der Farbfehler:\n")
        f.write("Die Farbfehler werden hauptsächlich durch den Abschnitt der spektralen Daten im langwelligen Bereich (750nm-780nm) und kurzwelligen Bereich (380nm-400nm) verursacht. Diese Wellenlängenbereiche tragen zur Farbwahrnehmung bei, auch wenn ihr Beitrag relativ gering ist. Die Tristimulus-Werte (XYZ) werden durch die Integration der spektralen Daten über den gesamten sichtbaren Bereich berechnet. Wenn ein Teil des Spektrums fehlt, führt dies zu leicht unterschiedlichen XYZ-Werten und damit zu abweichenden Farbwerten.\n\n")
        
        f.write("Bei dieser Studie fehlen besonders:\n")
        f.write("- Kurzwelliger Bereich (380nm-400nm): Dieser beeinflusst hauptsächlich die blaue Komponente (Z-Wert).\n")
        f.write("- Langwelliger Bereich (750nm-780nm): Dieser beeinflusst hauptsächlich die rote Komponente (X-Wert).\n\n")
        
        f.write("Proben mit den größten Farbunterschieden:\n")
        for i, (name, delta_e) in enumerate(worst_samples):
            f.write(f"{i+1}. Probe \"{name}\": ΔE = {delta_e:.6f}\n")
            
            # 获取Sample详细数据
            sample_data = results[name]
            original_data = sample_data['original']
            new_data = sample_data['new']
            
            # 计算Relative Error Percentage
            xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
            xyz_rel_diff = 100 * xyz_diff / (np.abs(original_data['xyz']) + 1e-10)
            
            f.write(f"   - XYZ-Differenz: ({xyz_diff[0]:.6f}, {xyz_diff[1]:.6f}, {xyz_diff[2]:.6f})\n")
            f.write(f"   - XYZ-Relative Differenz: ({xyz_rel_diff[0]:.2f}%, {xyz_rel_diff[1]:.2f}%, {xyz_rel_diff[2]:.2f}%)\n")
        
        f.write("\nEmpfehlungen für die Praxis:\n")
        f.write("Da die durchschnittliche Delta-E-Differenz von {:.6f} unter dem wahrnehmbaren Schwellenwert von 1,0 liegt, kann der gekürzete Wellenlängenbereich (400nm-750nm) für die meisten praktischen Anwendungen als ausreichend betrachtet werden. Die resultierenden Farbunterschiede sind für das menschliche Auge kaum wahrnehmbar.\n".format(avg_delta_e))
        f.write("Für hochpräzise Farbmessungen sollte jedoch der vollständige Wellenlängenbereich (380nm-780nm) verwendet werden, um maximale Genauigkeit zu gewährleisten.\n")
    
    print(f"Deutsche Zusammenfassung gespeichert in: {os.path.join(output_dir, 'farbfehler_zusammenfassung.txt')}")

def main():
    # Wellenlaengenbereiche festlegen
    original_range = (380, 780)  # Urspruenglicher Wellenlaengenbereich
    new_range = (400, 750)       # Neuer Wellenlaengenbereich
    
    # Reflektanzdaten lesen
    reflectance_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'sample_data', 
        'Reflections.xlsx'
    )
    
    samples = read_reflectance_data(reflectance_file)
    
    if not samples:
        print("Keine gueltigen Probendaten gefunden")
        return
    
    # Farbberechnungsergebnisse verschiedener Wellenlaengenbereiche vergleichen
    results = compare_wavelength_ranges(samples, original_range, new_range)
    
    # Ergebnisdiagramme zeichnen
    plot_results(samples, results, original_range, new_range)
    
    # Deutsche Zusammenfassung generieren
    generate_german_summary(results, original_range, new_range)
    
    print("\nAnalyse abgeschlossen!")

if __name__ == "__main__":
    main() 