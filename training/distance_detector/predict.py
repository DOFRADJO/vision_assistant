"""
=============================================================
Distance Detector — Script d'inférence / prédiction
=============================================================
Auteur  : MBIDA NGUELE Paul Loïc
Projet  : Vision Assistant — ENSPY ANI-IA
Mission : Tester le modèle entraîné sur une image ou
          un flux vidéo et retourner les détections
          au format standard du projet Vision Assistant.

Format de sortie standard (contrat d'interface) :
{
    "model": "distance_detector",
    "detections": [
        {
            "label": "close_person",
            "confidence": 0.91,
            "bbox": [x1, y1, x2, y2]
        }
    ]
}

Usage :
    python predict.py --source image.jpg
    python predict.py --source video.mp4
    python predict.py --source 0            # webcam
    python predict.py --source image.jpg --model path/to/best.pt
=============================================================
"""

from ultralytics import YOLO
import argparse
import json
import cv2


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

DEFAULT_MODEL      = "../../models/distance_detector/best.pt"
CONFIDENCE_THRESH  = 0.5         # Seuil de confiance minimum
IMAGE_SIZE         = 640

# Labels — doivent correspondre à labels.txt
LABELS = {
    0: "close_person",
    1: "far_person"
}


# ─────────────────────────────────────────────
# INFÉRENCE
# ─────────────────────────────────────────────

def predict(source: str, model_path: str = DEFAULT_MODEL) -> dict:
    """
    Lance la détection sur une source (image, vidéo, webcam).

    Args:
        source     : Chemin vers l'image/vidéo, ou index webcam (ex: "0")
        model_path : Chemin vers best.pt

    Returns:
        dict : Résultat au format standard Vision Assistant
    """

    print(f"  Chargement du modèle : {model_path}")
    model = YOLO(model_path)

    print(f"  Inférence sur : {source}")
    results = model.predict(
        source    = source,
        imgsz     = IMAGE_SIZE,
        conf      = CONFIDENCE_THRESH,
        verbose   = False,
    )

    # Construction de la réponse au format standard
    output = {
        "model": "distance_detector",
        "detections": []
    }

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            class_id    = int(box.cls[0])
            confidence  = float(box.conf[0])
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]

            label = LABELS.get(class_id, f"class_{class_id}")

            detection = {
                "label"     : label,
                "confidence": round(confidence, 2),
                "bbox"      : [x1, y1, x2, y2]
            }
            output["detections"].append(detection)

    return output


def visualize(source: str, model_path: str = DEFAULT_MODEL):
    """
    Lance la détection avec affichage visuel des bounding boxes.
    Appuyez sur 'q' pour quitter.
    """
    model = YOLO(model_path)

    results = model.predict(
        source  = source,
        imgsz   = IMAGE_SIZE,
        conf    = CONFIDENCE_THRESH,
        show    = True,           # Affiche la fenêtre de visualisation
        verbose = True,
    )

    return results


# ─────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inférence du modèle distance_detector"
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Image, vidéo, ou index webcam (ex: 0)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Chemin vers best.pt (défaut: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Afficher les détections visuellement"
    )
    args = parser.parse_args()

    if args.show:
        visualize(source=args.source, model_path=args.model)
    else:
        result = predict(source=args.source, model_path=args.model)
        print("\n  Résultat :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
