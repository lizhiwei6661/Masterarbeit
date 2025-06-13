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

def linear_extrapolation(wavelengths, reflectance, target_range=(380, 780), source_range=(400, 750)):
    """
    Fuehrt lineare Extrapolation an den Raendern des Spektrums durch
    
    Parameter:
        wavelengths: Urspruengliche Wellenlaengenwerte
        reflectance: Urspruengliche Reflektanzwerte
        target_range: Ziel-Wellenlaengenbereich fuer Extrapolation
        source_range: Quell-Wellenlaengenbereich der vorhandenen Daten
    
    Rueckgabe:
        extrapolated_wavelengths: Extrapolierte Wellenlaengenwerte
        extrapolated_reflectance: Extrapolierte Reflektanzwerte
    """
    print(f"Starte lineare Extrapolation von {source_range[0]}-{source_range[1]}nm zu {target_range[0]}-{target_range[1]}nm")
    
    # Neue Wellenlaengenwerte im 5nm-Schritt erstellen
    new_wavelengths = np.arange(target_range[0], target_range[1] + 5, 5)
    new_reflectance = np.zeros_like(new_wavelengths, dtype=float)
    
    # Indices fuer verschiedene Bereiche finden
    source_mask = (new_wavelengths >= source_range[0]) & (new_wavelengths <= source_range[1])
    lower_extrap_mask = new_wavelengths < source_range[0]
    upper_extrap_mask = new_wavelengths > source_range[1]
    
    # Originaldaten interpolieren fuer den Quellbereich
    for i, wl in enumerate(new_wavelengths):
        if source_mask[i]:
            # Interpolation der vorhandenen Daten
            new_reflectance[i] = np.interp(wl, wavelengths, reflectance)
    
    # Untere Extrapolation (380-395nm)
    if np.any(lower_extrap_mask):
        print("Extrapoliere unteren Bereich (380-400nm)...")
        # Verwende die ersten beiden Punkte im Quellbereich fuer lineare Extrapolation
        x1, x2 = source_range[0], source_range[0] + 5  # 400nm, 405nm
        y1 = np.interp(x1, wavelengths, reflectance)
        y2 = np.interp(x2, wavelengths, reflectance)
        
        # Lineare Steigung berechnen
        slope = (y2 - y1) / (x2 - x1)
        
        # Extrapolation durchfuehren
        for i, wl in enumerate(new_wavelengths):
            if lower_extrap_mask[i]:
                new_reflectance[i] = y1 + slope * (wl - x1)
                # Sicherstellen, dass Reflektanz nicht negativ wird
                new_reflectance[i] = max(0.0, new_reflectance[i])
    
    # Obere Extrapolation (755-780nm)
    if np.any(upper_extrap_mask):
        print("Extrapoliere oberen Bereich (750-780nm)...")
        # Verwende die letzten beiden Punkte im Quellbereich fuer lineare Extrapolation
        x1, x2 = source_range[1] - 5, source_range[1]  # 745nm, 750nm
        y1 = np.interp(x1, wavelengths, reflectance)
        y2 = np.interp(x2, wavelengths, reflectance)
        
        # Lineare Steigung berechnen
        slope = (y2 - y1) / (x2 - x1)
        
        # Extrapolation durchfuehren
        for i, wl in enumerate(new_wavelengths):
            if upper_extrap_mask[i]:
                new_reflectance[i] = y2 + slope * (wl - x2)
                # Sicherstellen, dass Reflektanz nicht ueber 1.0 geht
                new_reflectance[i] = min(1.0, max(0.0, new_reflectance[i]))
    
    print(f"Extrapolation abgeschlossen. Neue Datenanzahl: {len(new_wavelengths)} Punkte")
    return new_wavelengths, new_reflectance

def compare_extrapolation_methods(samples, original_range=(380, 780), truncated_range=(400, 750)):
    """Vergleicht verschiedene Methoden: Original vs Verkuerzt vs Extrapoliert"""
    # Farbrechner-Instanz erstellen
    cc = ColorCalculator()
    
    # Standardlichtquelle auf D65 setzen
    cc.illuminant = 'D65'
    
    results = {}
    
    for name, sample in samples.items():
        print(f"\n=== Analysiere Probe: {name} ===")
        wavelengths = sample['wavelengths']
        reflectance = sample['reflectance']
        
        # Pruefen ob Wellenlaengenbereich den Anforderungen entspricht
        min_wl = np.min(wavelengths)
        max_wl = np.max(wavelengths)
        print(f"Proben-Wellenlaengenbereich: {min_wl}-{max_wl}nm")
        
        if min_wl > original_range[0] or max_wl < original_range[1]:
            print(f"Warnung: Proben-Wellenlaengenbereich ({min_wl}-{max_wl}nm) erfuellt nicht die Anforderungen")
            continue
            
        # 1. Berechnung fuer urspruenglichen Wellenlaengenbereich (380-780nm)
        print("1. Berechne urspruengliche Daten (380-780nm)...")
        original_mask = (wavelengths >= original_range[0]) & (wavelengths <= original_range[1])
        original_wavelengths = wavelengths[original_mask]
        original_reflectance = reflectance[original_mask]
        
        if len(original_wavelengths) < 10:
            print(f"Warnung: Zu wenige Datenpunkte ({len(original_wavelengths)})")
            continue
            
        original_results = cc.process_measurement(original_reflectance, original_wavelengths)
        
        # 2. Berechnung fuer verkuerzten Wellenlaengenbereich (400-750nm)
        print("2. Berechne verkuerzte Daten (400-750nm)...")
        truncated_mask = (wavelengths >= truncated_range[0]) & (wavelengths <= truncated_range[1])
        truncated_wavelengths = wavelengths[truncated_mask]
        truncated_reflectance = reflectance[truncated_mask]
        
        if len(truncated_wavelengths) < 10:
            print(f"Warnung: Zu wenige Datenpunkte im verkuerzten Bereich")
            continue
            
        truncated_results = cc.process_measurement(truncated_reflectance, truncated_wavelengths)
        
        # 3. Lineare Extrapolation durchfuehren
        print("3. Fuehre lineare Extrapolation durch...")
        extrap_wavelengths, extrap_reflectance = linear_extrapolation(
            truncated_wavelengths, truncated_reflectance, 
            target_range=original_range, source_range=truncated_range
        )
        
        # Berechnung fuer extrapolierte Daten
        print("4. Berechne extrapolierte Daten...")
        extrap_results = cc.process_measurement(extrap_reflectance, extrap_wavelengths)
        
        # Lab-Werte berechnen
        original_lab = xyz_to_lab(original_results['xyz'])
        truncated_lab = xyz_to_lab(truncated_results['xyz'])
        extrap_lab = xyz_to_lab(extrap_results['xyz'])
        
        # Delta E berechnen
        delta_e_truncated = calculate_cie76_delta_e(original_lab, truncated_lab)
        delta_e_extrap = calculate_cie76_delta_e(original_lab, extrap_lab)
        
        # Ergebnisse speichern
        results[name] = {
            'original': original_results,
            'truncated': truncated_results,
            'extrapolated': extrap_results,
            'original_lab': original_lab,
            'truncated_lab': truncated_lab,
            'extrapolated_lab': extrap_lab,
            'delta_e_truncated': delta_e_truncated,
            'delta_e_extrapolated': delta_e_extrap,
            'extrap_wavelengths': extrap_wavelengths,
            'extrap_reflectance': extrap_reflectance,
            'original_wavelengths': original_wavelengths,
            'original_full_reflectance': original_reflectance,
            'truncated_wavelengths': truncated_wavelengths,
            'truncated_full_reflectance': truncated_reflectance
        }
        
        # Ergebnisse ausgeben
        print(f"\nErgebnisse fuer Probe {name}:")
        print(f"Original (380-780nm): XYZ=({original_results['xyz'][0]:.4f}, {original_results['xyz'][1]:.4f}, {original_results['xyz'][2]:.4f})")
        print(f"Verkuerzt (400-750nm): XYZ=({truncated_results['xyz'][0]:.4f}, {truncated_results['xyz'][1]:.4f}, {truncated_results['xyz'][2]:.4f})")
        print(f"Extrapoliert: XYZ=({extrap_results['xyz'][0]:.4f}, {extrap_results['xyz'][1]:.4f}, {extrap_results['xyz'][2]:.4f})")
        print(f"ΔE (Verkuerzt vs Original): {delta_e_truncated:.6f}")
        print(f"ΔE (Extrapoliert vs Original): {delta_e_extrap:.6f}")
        
        # Verbesserung bewerten
        improvement = delta_e_truncated - delta_e_extrap
        if improvement > 0:
            print(f"✓ Extrapolation verbessert ΔE um {improvement:.6f}")
        else:
            print(f"✗ Extrapolation verschlechtert ΔE um {abs(improvement):.6f}")
    
    return results

def export_extrapolation_comparison_table(results, output_dir, original_range=(380, 780), truncated_range=(400, 750)):
    """
    Exportiert Vergleichstabelle fuer Extrapolationsergebnisse
    """
    if not results:
        print("Keine Ergebnisse fuer den Export verfuegbar")
        return
    
    # CSV Datei erstellen
    csv_filename = os.path.join(output_dir, 'extrapolations_vergleich.csv')
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Deutsche Spaltenueberschriften
        header = [
            'Probenname',
            'Original XYZ (X)', 'Original XYZ (Y)', 'Original XYZ (Z)',
            'Verkuerzt XYZ (X)', 'Verkuerzt XYZ (Y)', 'Verkuerzt XYZ (Z)',
            'Extrapoliert XYZ (X)', 'Extrapoliert XYZ (Y)', 'Extrapoliert XYZ (Z)',
            'ΔE Verkuerzt vs Original', 'ΔE Extrapoliert vs Original',
            'Verbesserung durch Extrapolation',
            'Original Hex', 'Verkuerzt Hex', 'Extrapoliert Hex'
        ]
        writer.writerow(header)
        
        # Daten fuer jede Probe schreiben
        for name, result in results.items():
            original_data = result['original']
            truncated_data = result['truncated']
            extrap_data = result['extrapolated']
            
            # Verbesserung berechnen
            improvement = result['delta_e_truncated'] - result['delta_e_extrapolated']
            
            # Zeile schreiben
            row = [
                name,
                f"{original_data['xyz'][0]:.6f}", f"{original_data['xyz'][1]:.6f}", f"{original_data['xyz'][2]:.6f}",
                f"{truncated_data['xyz'][0]:.6f}", f"{truncated_data['xyz'][1]:.6f}", f"{truncated_data['xyz'][2]:.6f}",
                f"{extrap_data['xyz'][0]:.6f}", f"{extrap_data['xyz'][1]:.6f}", f"{extrap_data['xyz'][2]:.6f}",
                f"{result['delta_e_truncated']:.6f}",
                f"{result['delta_e_extrapolated']:.6f}",
                f"{improvement:.6f}",
                original_data['hex_color'], truncated_data['hex_color'], extrap_data['hex_color']
            ]
            writer.writerow(row)
    
    # Excel-Version erstellen
    try:
        import pandas as pd
        df = pd.read_csv(csv_filename)
        excel_filename = os.path.join(output_dir, 'extrapolations_vergleich.xlsx')
        df.to_excel(excel_filename, index=False)
        print(f"Extrapolations-Vergleichstabelle exportiert: {csv_filename} und {excel_filename}")
    except Exception as e:
        print(f"Extrapolations-Vergleichstabelle als CSV exportiert: {csv_filename}")
        print(f"Excel-Export fehlgeschlagen: {e}")

def plot_extrapolation_results(results, output_dir, original_range=(380, 780), truncated_range=(400, 750)):
    """
    Zeichnet Diagramme fuer Extrapolationsergebnisse
    """
    if not results:
        print("Keine Ergebnisse fuer die Darstellung verfuegbar")
        return
    
    for name, result in results.items():
        # Dateinamen bereinigen
        safe_name = name.replace("/", "_").replace(" ", "_").strip()
        
        # 1. Reflektanzkurven-Vergleich
        plt.figure(figsize=(14, 8))
        
        # Urspruengliche Daten
        plt.plot(result['original_wavelengths'], result['original_full_reflectance'], 
                'b-', linewidth=2, label=f'Original ({original_range[0]}-{original_range[1]}nm)', alpha=0.8)
        
        # Verkuerzte Daten
        plt.plot(result['truncated_wavelengths'], result['truncated_full_reflectance'], 
                'r-', linewidth=3, label=f'Verkuerzt ({truncated_range[0]}-{truncated_range[1]}nm)')
        
        # Extrapolierte Daten
        plt.plot(result['extrap_wavelengths'], result['extrap_reflectance'], 
                'g--', linewidth=2, label='Linear extrapoliert', alpha=0.7)
        
        # Extrapolationsbereiche markieren
        plt.axvspan(original_range[0], truncated_range[0], alpha=0.2, color='orange', 
                   label='Extrapolationsbereich (380-400nm)')
        plt.axvspan(truncated_range[1], original_range[1], alpha=0.2, color='orange',
                   label='Extrapolationsbereich (750-780nm)')
        
        plt.xlabel('Wellenlaenge (nm)')
        plt.ylabel('Reflektanz')
        plt.title(f'Probe "{name}" - Lineare Extrapolation der Reflektanzkurve')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xlim(original_range[0]-10, original_range[1]+10)
        plt.tight_layout()
        
        # Diagramm speichern
        plt.savefig(os.path.join(output_dir, f'{safe_name}_extrapolation_reflektanz.png'), dpi=150)
        plt.close()
        
        # 2. Farbvergleich (3-fach)
        fig, ax = plt.subplots(1, 3, figsize=(12, 4))
        
        # Original
        original_rgb = np.clip(result['original']['rgb_gamma'], 0, 1)
        ax[0].add_patch(plt.Rectangle((0, 0), 1, 1, color=original_rgb))
        ax[0].set_title(f'Original\n{result["original"]["hex_color"]}\nΔE: 0.000000')
        ax[0].set_xticks([])
        ax[0].set_yticks([])
        
        # Verkuerzt
        truncated_rgb = np.clip(result['truncated']['rgb_gamma'], 0, 1)
        ax[1].add_patch(plt.Rectangle((0, 0), 1, 1, color=truncated_rgb))
        ax[1].set_title(f'Verkuerzt\n{result["truncated"]["hex_color"]}\nΔE: {result["delta_e_truncated"]:.6f}')
        ax[1].set_xticks([])
        ax[1].set_yticks([])
        
        # Extrapoliert
        extrap_rgb = np.clip(result['extrapolated']['rgb_gamma'], 0, 1)
        ax[2].add_patch(plt.Rectangle((0, 0), 1, 1, color=extrap_rgb))
        improvement = result['delta_e_truncated'] - result['delta_e_extrapolated']
        ax[2].set_title(f'Extrapoliert\n{result["extrapolated"]["hex_color"]}\nΔE: {result["delta_e_extrapolated"]:.6f}')
        ax[2].set_xticks([])
        ax[2].set_yticks([])
        
        plt.suptitle(f'Probe "{name}" - Farbvergleich\nVerbesserung durch Extrapolation: {improvement:.6f}')
        plt.tight_layout()
        
        # Diagramm speichern
        plt.savefig(os.path.join(output_dir, f'{safe_name}_extrapolation_farben.png'), dpi=150)
        plt.close()

def create_extrapolation_summary(results, output_dir, original_range=(380, 780), truncated_range=(400, 750)):
    """Erstellt zusammenfassenden Bericht ueber Extrapolationsergebnisse"""
    if not results:
        print("Keine Ergebnisse fuer die Zusammenfassung verfuegbar")
        return
    
    # Statistiken berechnen
    all_delta_e_truncated = []
    all_delta_e_extrapolated = []
    improvements = []
    
    for name, result in results.items():
        all_delta_e_truncated.append(result['delta_e_truncated'])
        all_delta_e_extrapolated.append(result['delta_e_extrapolated'])
        improvements.append(result['delta_e_truncated'] - result['delta_e_extrapolated'])
    
    avg_delta_e_truncated = np.mean(all_delta_e_truncated)
    avg_delta_e_extrapolated = np.mean(all_delta_e_extrapolated)
    avg_improvement = np.mean(improvements)
    
    # Anzahl verbesserter Proben
    improved_count = sum(1 for imp in improvements if imp > 0)
    worsened_count = sum(1 for imp in improvements if imp < 0)
    unchanged_count = len(improvements) - improved_count - worsened_count
    
    # Deutsche Zusammenfassung erstellen
    with open(os.path.join(output_dir, 'extrapolations_zusammenfassung.txt'), 'w', encoding='utf-8') as f:
        f.write("Zusammenfassung der linearen Extrapolationsanalyse\n")
        f.write("=================================================\n\n")
        
        f.write(f"Urspruenglicher Wellenlaengenbereich: {original_range[0]}-{original_range[1]}nm\n")
        f.write(f"Verkuerzter Wellenlaengenbereich: {truncated_range[0]}-{truncated_range[1]}nm\n")
        f.write(f"Extrapolationsmethode: Lineare Randextrapolation\n\n")
        
        f.write("Extrapolationsstrategie:\n")
        f.write("-------------------------\n")
        f.write(f"- Unterer Bereich ({original_range[0]}-{truncated_range[0]}nm): Lineare Extrapolation basierend auf {truncated_range[0]}-{truncated_range[0]+5}nm\n")
        f.write(f"- Oberer Bereich ({truncated_range[1]}-{original_range[1]}nm): Lineare Extrapolation basierend auf {truncated_range[1]-5}-{truncated_range[1]}nm\n\n")
        
        f.write("Statistische Auswertung:\n")
        f.write("-------------------------\n")
        f.write(f"Analysierte Proben: {len(results)}\n")
        f.write(f"Durchschnittliches ΔE (verkuerzt vs original): {avg_delta_e_truncated:.6f}\n")
        f.write(f"Durchschnittliches ΔE (extrapoliert vs original): {avg_delta_e_extrapolated:.6f}\n")
        f.write(f"Durchschnittliche Verbesserung: {avg_improvement:.6f}\n\n")
        
        f.write("Erfolgsrate der Extrapolation:\n")
        f.write("-------------------------------\n")
        f.write(f"Verbesserte Proben: {improved_count} ({improved_count/len(results)*100:.1f}%)\n")
        f.write(f"Verschlechterte Proben: {worsened_count} ({worsened_count/len(results)*100:.1f}%)\n")
        f.write(f"Unveraenderte Proben: {unchanged_count} ({unchanged_count/len(results)*100:.1f}%)\n\n")
        
        f.write("Bewertung der Extrapolationsmethode:\n")
        f.write("------------------------------------\n")
        if avg_improvement > 0:
            f.write(f"✓ Die lineare Extrapolation fuehrt im Durchschnitt zu einer Verbesserung der Farbgenauigkeit.\n")
            f.write(f"✓ Das durchschnittliche ΔE wird um {avg_improvement:.6f} reduziert.\n")
        elif avg_improvement < 0:
            f.write(f"✗ Die lineare Extrapolation verschlechtert im Durchschnitt die Farbgenauigkeit.\n")
            f.write(f"✗ Das durchschnittliche ΔE steigt um {abs(avg_improvement):.6f}.\n")
        else:
            f.write("○ Die lineare Extrapolation zeigt keine signifikante Veraenderung der Farbgenauigkeit.\n")
        
        f.write("\nEinzelne Probenergebnisse:\n")
        f.write("---------------------------\n")
        
        # Sortiere nach Verbesserung
        sorted_results = sorted(results.items(), 
                              key=lambda x: x[1]['delta_e_truncated'] - x[1]['delta_e_extrapolated'], 
                              reverse=True)
        
        for name, result in sorted_results:
            improvement = result['delta_e_truncated'] - result['delta_e_extrapolated']
            status = "✓" if improvement > 0 else "✗" if improvement < 0 else "○"
            f.write(f"{status} {name}:\n")
            f.write(f"   ΔE verkuerzt: {result['delta_e_truncated']:.6f}\n")
            f.write(f"   ΔE extrapoliert: {result['delta_e_extrapolated']:.6f}\n")
            f.write(f"   Verbesserung: {improvement:.6f}\n\n")
        
        f.write("Empfehlungen:\n")
        f.write("-------------\n")
        if avg_improvement > 0.001:
            f.write("Die lineare Extrapolation zeigt signifikante Verbesserungen und kann fuer praktische Anwendungen empfohlen werden.\n")
        elif avg_improvement > 0:
            f.write("Die lineare Extrapolation zeigt geringe Verbesserungen. Der Nutzen ist marginal.\n")
        else:
            f.write("Die lineare Extrapolation ist nicht empfehlenswert, da sie die Farbgenauigkeit nicht verbessert oder sogar verschlechtert.\n")
            f.write("Erwaegenswert waeren komplexere Extrapolationsmethoden oder die Akzeptanz der verkürzten Daten.\n")
    
    print(f"Extrapolations-Zusammenfassung gespeichert in: {os.path.join(output_dir, 'extrapolations_zusammenfassung.txt')}")

def create_comparison_charts(results, output_dir):
    """Erstellt Vergleichsdiagramme fuer alle Proben"""
    if not results:
        print("Keine Ergebnisse fuer Vergleichsdiagramme verfuegbar")
        return
    
    # 1. Delta E Vergleichsdiagramm
    sample_names = list(results.keys())
    delta_e_truncated = [results[name]['delta_e_truncated'] for name in sample_names]
    delta_e_extrapolated = [results[name]['delta_e_extrapolated'] for name in sample_names]
    
    # Falls zu viele Proben, nur die ersten 20 (nach Delta E sortiert) anzeigen
    if len(sample_names) > 20:
        # Nach hoechstem Delta E (verkuerzt) sortieren
        sorted_indices = np.argsort(delta_e_truncated)[::-1]
        sample_names = [sample_names[i] for i in sorted_indices[:20]]
        delta_e_truncated = [delta_e_truncated[i] for i in sorted_indices[:20]]
        delta_e_extrapolated = [delta_e_extrapolated[i] for i in sorted_indices[:20]]
    
    plt.figure(figsize=(14, 8))
    x = np.arange(len(sample_names))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, delta_e_truncated, width, label='Verkuerzt (400-750nm)', color='red', alpha=0.7)
    bars2 = plt.bar(x + width/2, delta_e_extrapolated, width, label='Linear extrapoliert', color='green', alpha=0.7)
    
    plt.xlabel('Proben')
    plt.ylabel('ΔE (vs Original)')
    plt.title('Vergleich der Farbgenauigkeit: Verkuerzt vs Linear Extrapoliert')
    plt.xticks(x, sample_names, rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    # Zahlenwerte als Beschriftung entfernt
    # for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
    #     plt.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + 0.001,
    #             f'{delta_e_truncated[i]:.3f}', ha='center', va='bottom', fontsize=6)
    #     plt.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height() + 0.001,
    #             f'{delta_e_extrapolated[i]:.3f}', ha='center', va='bottom', fontsize=6)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'delta_e_vergleich_alle_proben.png'), dpi=150)
    plt.close()
    
    # 2. Verbesserungsdiagramm
    improvements = [delta_e_truncated[i] - delta_e_extrapolated[i] for i in range(len(sample_names))]
    
    plt.figure(figsize=(14, 6))
    colors = ['green' if imp > 0 else 'red' for imp in improvements]
    bars = plt.bar(sample_names, improvements, color=colors, alpha=0.7)
    
    plt.xlabel('Proben')
    plt.ylabel('Verbesserung durch Extrapolation (ΔE)')
    plt.title('Verbesserung der Farbgenauigkeit durch lineare Extrapolation')
    plt.xticks(rotation=45, ha='right')
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    plt.grid(axis='y', alpha=0.3)
    
    # Zahlenwerte als Beschriftung entfernt
    # for bar, imp in zip(bars, improvements):
    #     plt.text(bar.get_x() + bar.get_width()/2, 
    #             bar.get_height() + (0.005 if imp >= 0 else -0.015),
    #             f'{imp:.4f}', ha='center', va='bottom' if imp >= 0 else 'top', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'extrapolations_verbesserung.png'), dpi=150)
    plt.close()
    
    # 3. xy Chromatizitaetsdiagramm-Vergleich (wie in wavelength_comparison.py)
    plt.figure(figsize=(10, 8))
    
    # Farbraumgrenzen zeichnen
    t = np.linspace(0, 1, 100)
    plt.plot(t, -3*t + 2, 'k-', alpha=0.2)  # y = -3x + 2
    plt.plot(t, 2.5*t - 0.5, 'k-', alpha=0.2)  # y = 2.5x - 0.5
    plt.plot([0.35, 0], [0.375, 0], 'k-', alpha=0.2)
    plt.fill_between([0, 0.35, 0.67, 0.35, 0], 
                     [0, 0.375, 0.175, 0, 0], alpha=0.05, color='gray')
    
    for name, result in results.items():
        original_x, original_y = result['original']['xy']
        truncated_x, truncated_y = result['truncated']['xy']
        extrap_x, extrap_y = result['extrapolated']['xy']
        
        # Original, verkuerzt und extrapoliert Punkte zeichnen
        plt.plot(original_x, original_y, 'bo', markersize=8, alpha=0.7)
        plt.plot(truncated_x, truncated_y, 'ro', markersize=8, alpha=0.7)
        plt.plot(extrap_x, extrap_y, 'go', markersize=8, alpha=0.7)
        
        # Linien zwischen den Punkten
        plt.plot([original_x, truncated_x], [original_y, truncated_y], 'r-', alpha=0.3)
        plt.plot([original_x, extrap_x], [original_y, extrap_y], 'g--', alpha=0.3)
        
        # Probennamen beschriften
        plt.text(original_x+0.005, original_y+0.005, name, fontsize=6)
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('CIE xy Chromatizitaetsdiagramm - Extrapolationsvergleich')
    plt.grid(True, alpha=0.3)
    plt.axis([0, 0.8, 0, 0.9])
    
    # Legende hinzufuegen
    plt.plot([], [], 'bo', markersize=8, label='Original (380-780nm)')
    plt.plot([], [], 'ro', markersize=8, label='Verkuerzt (400-750nm)')
    plt.plot([], [], 'go', markersize=8, label='Linear extrapoliert')
    plt.legend()
    
    plt.savefig(os.path.join(output_dir, 'xy_extrapolation_comparison.png'), dpi=150)
    plt.close()
    
    # 4. RGB Farbkomponenten-Differenzdiagramm
    rgb_labels = ['R', 'G', 'B']
    
    # RGB Differenzen berechnen
    all_rgb_diff_truncated = []
    all_rgb_diff_extrap = []
    
    for name, result in results.items():
        original_rgb = result['original']['rgb_gamma']
        truncated_rgb = result['truncated']['rgb_gamma']
        extrap_rgb = result['extrapolated']['rgb_gamma']
        
        rgb_diff_truncated = np.abs(original_rgb - truncated_rgb)
        rgb_diff_extrap = np.abs(original_rgb - extrap_rgb)
        
        all_rgb_diff_truncated.append(rgb_diff_truncated)
        all_rgb_diff_extrap.append(rgb_diff_extrap)
    
    avg_rgb_diff_truncated = np.mean(all_rgb_diff_truncated, axis=0)
    avg_rgb_diff_extrap = np.mean(all_rgb_diff_extrap, axis=0)
    
    plt.figure(figsize=(10, 6))
    
    x = np.arange(len(rgb_labels))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, avg_rgb_diff_truncated, width, 
                     label='Verkuerzt (400-750nm)', color=['darkred', 'darkgreen', 'darkblue'], alpha=0.7)
    bars2 = plt.bar(x + width/2, avg_rgb_diff_extrap, width, 
                     label='Linear extrapoliert', color=['red', 'green', 'blue'], alpha=0.7)
    
    # Zahlenwerte entfernt
    # for bar1, bar2, val1, val2 in zip(bars1, bars2, avg_rgb_diff_truncated, avg_rgb_diff_extrap):
    #     plt.text(bar1.get_x() + bar1.get_width()/2, 
    #              bar1.get_height() + 0.001, 
    #              f'{val1:.4f}', ha='center', va='bottom', fontsize=8)
    #     plt.text(bar2.get_x() + bar2.get_width()/2, 
    #              bar2.get_height() + 0.001, 
    #              f'{val2:.4f}', ha='center', va='bottom', fontsize=8)
    
    plt.title('Durchschnittliche RGB-Farbkomponenten-Differenz')
    plt.ylabel('Absolute Differenz')
    plt.xticks(x, rgb_labels)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rgb_diff_comparison.png'), dpi=150)
    plt.close()

def main():
    # Wellenlaengenbereiche festlegen
    original_range = (380, 780)     # Urspruenglicher Wellenlaengenbereich
    truncated_range = (400, 750)    # Verkuerzter Wellenlaengenbereich
    
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
    
    print(f"\n=== LINEARE EXTRAPOLATIONSANALYSE ===")
    print(f"Vergleiche: Original ({original_range[0]}-{original_range[1]}nm) vs Verkuerzt ({truncated_range[0]}-{truncated_range[1]}nm) vs Linear Extrapoliert")
    
    # Extrapolationsvergleich durchfuehren
    results = compare_extrapolation_methods(samples, original_range, truncated_range)
    
    # Ausgabeverzeichnis erstellen
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extrapolation_ergebnisse")
    os.makedirs(output_dir, exist_ok=True)
    
    # Ergebnisse exportieren und visualisieren
    export_extrapolation_comparison_table(results, output_dir, original_range, truncated_range)
    plot_extrapolation_results(results, output_dir, original_range, truncated_range)
    create_comparison_charts(results, output_dir)
    create_extrapolation_summary(results, output_dir, original_range, truncated_range)
    
    print(f"\n=== EXTRAPOLATIONSANALYSE ABGESCHLOSSEN ===")
    print(f"Alle Ergebnisse gespeichert in: {output_dir}")

if __name__ == "__main__":
    main()
 