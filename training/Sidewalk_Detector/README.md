# Projet  Agent Intelligent de Vision Assistée pour Personnes Malvoyantes

Détection du chemin praticable (trottoir) et alerte vocale en cas de déviation
(gauche / droite) pour assister la navigation des personnes malvoyantes.

## Structure du projet

```
projet-blind-navigation/
├── README.md
├── requirements.txt
├── models/
│   ├── best.pt           # modèle entraîné (PyTorch)
│   └── best.onnx          # modèle exporté (déploiement mobile)
├── notebooks/
│   └── blind_navigation_detection.ipynb   # notebook Colab (entraînement)
├── src/
│   ├── detect_realtime.py   # détection temps réel via webcam
│   └── detect_image.py      # test sur une image unique
├── data/
│   └── test_images/         # images de test
└── results/
    └── (captures d'écran, métriques)
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Détection sur une image 
```bash
cd src
python detect_image.py ../data/test_images/sidewalk.png
```

### Détection en temps réel (webcam)
```bash
cd src
python detect_realtime.py
```
Appuie sur `q` pour quitter.

## Modèle

- **Architecture** : YOLOv8n (nano), entraîné en détection d'objets (bounding boxes)
- **Dataset** : "Blind-Navigation" (Roboflow), classes orientées trottoir/chemin
- **Entraînement** : 50 epochs, Google Colab (GPU T4)
- **Export** : ONNX pour déploiement mobile (React Native)

## Logique de déviation

Le modèle détecte la zone de chemin praticable (boîte englobante).
On compare le centre horizontal de cette boîte au centre de l'image :
- Si le centre du chemin est décalé à droite → "Vous déviez vers la droite"
- Si décalé à gauche → "Vous déviez vers la gauche"
- Sinon → "Vous êtes bien centré"

Un message vocal (gTTS, français) est généré pour chaque alerte.

## Auteur

NGONO VANINA — AIA-4,ENSPY 
