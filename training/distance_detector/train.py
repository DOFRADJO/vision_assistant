"""
=============================================================
Distance Detector — Script d'entraînement YOLOv8
=============================================================
Auteur  : MBIDA NGUELE Paul Loïc
Projet  : Vision Assistant — ENSPY ANI-IA
Mission : Entraîner un modèle YOLOv8 capable d'estimer
          si une personne est proche ou loin de la caméra.

Classes :
    0 — close_person  (personne proche, grande bounding box)
    1 — far_person    (personne éloignée, petite bounding box)

Workflow :
    1. Préparer le dataset dans ./dataset/
    2. Configurer data.yaml
    3. Lancer : python train.py
    4. Récupérer best.pt dans runs/detect/distance_detector/weights/
=============================================================
"""

from ultralytics import YOLO
import os

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

DATA_CONFIG   = "data.yaml"       # Chemin vers le fichier de configuration dataset
MODEL_BASE    = "yolov8n.pt"      # Modèle de base (nano = léger, idéal mobile)
PROJECT_NAME  = "runs/detect"     # Dossier de sortie des runs
RUN_NAME      = "distance_detector"

EPOCHS        = 50                # Nombre d'époques
IMAGE_SIZE    = 640               # Taille des images (640x640)
BATCH_SIZE    = 16                # Taille du batch
WORKERS       = 4                 # Nombre de workers DataLoader
PATIENCE      = 10                # Early stopping patience
DEVICE        = 0                 # 0 = GPU, "cpu" = CPU


# ─────────────────────────────────────────────
# ENTRAÎNEMENT
# ─────────────────────────────────────────────

def train():
    """Entraîne le modèle distance_detector avec YOLOv8."""

    print("=" * 60)
    print("  Distance Detector — Démarrage de l'entraînement")
    print("=" * 60)
    print(f"  Modèle de base  : {MODEL_BASE}")
    print(f"  Dataset config  : {DATA_CONFIG}")
    print(f"  Époques         : {EPOCHS}")
    print(f"  Taille image    : {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"  Batch size      : {BATCH_SIZE}")
    print("=" * 60)

    # Vérification que le fichier de config existe
    if not os.path.exists(DATA_CONFIG):
        raise FileNotFoundError(
            f"[ERREUR] data.yaml introuvable : {DATA_CONFIG}\n"
            "Vérifiez que vous êtes dans le bon dossier et que "
            "le dataset est correctement configuré."
        )

    # Chargement du modèle de base
    model = YOLO(MODEL_BASE)

    # Lancement de l'entraînement
    results = model.train(
        data      = DATA_CONFIG,
        epochs    = EPOCHS,
        imgsz     = IMAGE_SIZE,
        batch     = BATCH_SIZE,
        workers   = WORKERS,
        patience  = PATIENCE,
        device    = DEVICE,
        project   = PROJECT_NAME,
        name      = RUN_NAME,
        exist_ok  = True,         # Écraser si le run existe déjà
        pretrained= True,         # Utiliser les poids pré-entraînés COCO
        optimizer = "Adam",
        lr0       = 0.001,        # Learning rate initial
        augment   = True,         # Data augmentation activée
        verbose   = True,
    )

    print("\n" + "=" * 60)
    print("  Entraînement terminé !")
    best_weights = os.path.join(PROJECT_NAME, RUN_NAME, "weights", "best.pt")
    print(f"  Meilleurs poids : {best_weights}")
    print("  Lancez maintenant : python export.py")
    print("=" * 60)

    return results


if __name__ == "__main__":
    train()
