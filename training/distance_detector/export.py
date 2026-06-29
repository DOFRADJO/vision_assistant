"""
=============================================================
Distance Detector — Script d'export ONNX
=============================================================
Auteur  : MBIDA NGUELE Paul Loïc
Projet  : Vision Assistant — ENSPY ANI-IA
Mission : Exporter le modèle entraîné best.pt vers le
          format ONNX pour intégration dans le système
          multi-agents Vision Assistant.

Usage :
    python export.py
    python export.py --weights path/to/best.pt

Sortie :
    best.onnx  → à copier dans models/distance_detector/
    best.pt    → à copier dans models/distance_detector/
=============================================================
"""

from ultralytics import YOLO
import argparse
import shutil
import os


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

DEFAULT_WEIGHTS = "runs/detect/distance_detector/weights/best.pt"
OUTPUT_DIR      = "../../models/distance_detector"
IMAGE_SIZE      = 640


# ─────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────

def export(weights_path: str = DEFAULT_WEIGHTS):
    """
    Exporte le modèle best.pt vers ONNX et copie
    les livrables dans models/distance_detector/.
    """

    print("=" * 60)
    print("  Distance Detector — Export ONNX")
    print("=" * 60)

    # Vérification des poids
    if not os.path.exists(weights_path):
        raise FileNotFoundError(
            f"[ERREUR] Poids introuvables : {weights_path}\n"
            "Lancez d'abord python train.py pour entraîner le modèle."
        )

    print(f"  Poids source : {weights_path}")
    print(f"  Taille image : {IMAGE_SIZE}x{IMAGE_SIZE}")

    # Chargement du modèle entraîné
    model = YOLO(weights_path)

    # Export au format ONNX
    print("\n  Export en cours...")
    export_path = model.export(
        format  = "onnx",
        imgsz   = IMAGE_SIZE,
        dynamic = False,        # Taille fixe pour inférence mobile
        simplify= True,         # Simplification du graphe ONNX
        opset   = 12,           # Version opset compatible mobile
    )

    print(f"  ONNX exporté : {export_path}")

    # Copie des livrables vers models/distance_detector/
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Copie best.pt
    dst_pt = os.path.join(OUTPUT_DIR, "best.pt")
    shutil.copy2(weights_path, dst_pt)
    print(f"  Copié : {weights_path} → {dst_pt}")

    # Copie best.onnx
    onnx_src = weights_path.replace(".pt", ".onnx")
    dst_onnx = os.path.join(OUTPUT_DIR, "best.onnx")
    if os.path.exists(onnx_src):
        shutil.copy2(onnx_src, dst_onnx)
        print(f"  Copié : {onnx_src} → {dst_onnx}")

    print("\n" + "=" * 60)
    print("  Export terminé !")
    print(f"  Livrables disponibles dans : {OUTPUT_DIR}")
    print("=" * 60)


# ─────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export du modèle distance_detector vers ONNX"
    )
    parser.add_argument(
        "--weights",
        type=str,
        default=DEFAULT_WEIGHTS,
        help=f"Chemin vers best.pt (défaut: {DEFAULT_WEIGHTS})"
    )
    args = parser.parse_args()
    export(args.weights)
