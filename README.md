# 🧠 Vision Assistant

## Intelligent Multi-Agent Vision System for Visually Impaired People

![Python](https://img.shields.io/badge/Python-3.11-blue)
![YOLO](https://img.shields.io/badge/YOLO-v8-success)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![ONNX](https://img.shields.io/badge/ONNX-Compatible-orange)
![React Native](https://img.shields.io/badge/React-Native-61DAFB)

---

# 📖 Table of Contents

* Introduction
* Project Objectives
* Problem Statement
* System Overview
* General Architecture
* Multi-Agent Architecture
* AI Models
* Project Structure
* Technologies Used
* Development Workflow
* Installation Guide
* First Execution
* Git Workflow
* Team Organization
* Contribution Guide
* Roadmap

---

# 1. Introduction

Vision Assistant est un système intelligent destiné à assister les personnes malvoyantes grâce à la Vision par Ordinateur, au Deep Learning et aux Systèmes Multi-Agents.

Le système observe l'environnement à travers une caméra, détecte les objets présents, analyse leur importance, prend une décision intelligente puis fournit une assistance vocale en temps réel.

L'objectif n'est pas uniquement de détecter des objets mais de comprendre une scène afin d'aider efficacement une personne malvoyante.

---

# 2. Problem Statement

Les personnes malvoyantes rencontrent quotidiennement plusieurs difficultés :

* Identifier les objets autour d'elles.
* Reconnaître les véhicules.
* Éviter les obstacles.
* Traverser une route.
* Identifier une porte.
* Reconnaître un escalier.
* Détecter une personne qui approche.
* Comprendre leur environnement.

Notre système répond à ces besoins grâce à plusieurs modèles d'intelligence artificielle spécialisés.

---

# 3. Project Objectives

Le projet poursuit plusieurs objectifs.

## Objectif principal

Développer un assistant intelligent capable de comprendre son environnement grâce à la Vision par Ordinateur.

## Objectifs spécifiques

* Détecter les personnes
* Détecter les véhicules
* Détecter les objets du quotidien
* Détecter les obstacles
* Détecter les animaux
* Détecter les panneaux
* Estimer le danger
* Générer des descriptions vocales
* Fonctionner en temps réel
* Être déployable sur mobile

---

# 4. Global System Overview

Le fonctionnement général est le suivant :

```text
Camera
    │
    ▼
Video Stream
    │
    ▼
Vision Agent
    │
    ▼
Specialized AI Models
    │
    ▼
Reasoning Agent
    │
    ▼
Memory Agent
    │
    ▼
Speech Agent
    │
    ▼
Voice Feedback
```

Chaque module possède une responsabilité unique.

---

# 5. Why a Multi-Agent System?

Une seule intelligence artificielle est rarement suffisante pour résoudre un problème complexe.

Nous avons donc choisi une architecture Multi-Agent.

Chaque agent possède une mission précise.

Cela présente plusieurs avantages :

* Modularité
* Facilité de maintenance
* Évolutivité
* Réutilisation
* Développement collaboratif
* Facilité de test

---

# 6. System Architecture

```
                         USER

                           │

                     Smartphone Camera

                           │

                   Video Acquisition

                           │

                Coordinator Agent

                           │

 ┌──────────────┬──────────────┬──────────────┐
 │              │              │              │
Vision      Memory       Reasoning      Speech
Agent        Agent          Agent         Agent

                           │

────────────────────────────────────────────────────────

                AI MODELS

People Detector

Vehicle Detector

Furniture Detector

Obstacle Detector

Traffic Detector

Food Detector

Animal Detector

Emergency Detector
```

---

# 7. AI Models

Le système est composé de plusieurs modèles spécialisés.

Chaque modèle peut être développé indépendamment.

| Model              | Responsibility                    |
| ------------------ | --------------------------------- |
| people_detector    | Détection des personnes           |
| vehicle_detector   | Détection des véhicules           |
| furniture_detector | Détection du mobilier             |
| obstacle_detector  | Détection des obstacles           |
| traffic_detector   | Détection de la signalisation     |
| food_detector      | Détection de nourriture           |
| animal_detector    | Détection des animaux             |
| emergency_detector | Détection des véhicules d'urgence |

Cette séparation permet un développement collaboratif.

Chaque étudiant peut entraîner un modèle différent.

---

# 8. Project Structure

```
vision_assistant/

├── datasets/
├── training/
├── models/
├── agents/
├── core/
├── app/
├── exports/
├── docs/
├── tests/
├── scripts/
│
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

Chaque dossier possède une responsabilité unique.

---

# 9. Technologies

Le projet repose sur les technologies suivantes.

## Artificial Intelligence

* YOLOv8
* PyTorch
* ONNX
* OpenCV

## Programming

* Python

## Mobile

* React Native

## Speech

* pyttsx3
* Android TTS

## Tracking

* ByteTrack

## Version Control

* Git
* GitHub

---

# 10. Development Workflow

Le développement suit plusieurs étapes.

```
Dataset

↓

Training

↓

Validation

↓

Export ONNX

↓

Integration

↓

Tests

↓

Deployment
```

Chaque étudiant peut suivre ce workflow.

---

# 11. Installation

## Clone repository

```bash
git clone https://github.com/DOFRADJO/vision_assistant.git

cd vision_assistant
```

## Create virtual environment

```bash
python3.11 -m venv .venv

source .venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# 12. First Execution

Le projet pourra être lancé simplement avec :

```bash
python run.py
```

---

# 13. Git Workflow

Chaque étudiant travaille dans une branche.

Exemple :

```
main

people_detector

vehicle_detector

food_detector

reasoning_agent

speech_agent

mobile_app
```

Les Pull Requests seront fusionnées dans la branche principale après validation.

---

# 14. Team Organization

Le projet est organisé autour de plusieurs équipes.

## Team AI

Responsable des modèles.

## Team Vision

Responsable de YOLO.

## Team Agent

Responsable des agents.

## Team Mobile

Responsable de React Native.

## Team Integration

Responsable de l'assemblage.

---

# 15. Coding Standards

Chaque étudiant doit respecter les règles suivantes.

* Python PEP8
* Commentaires obligatoires
* Type Hint
* Docstrings
* Tests unitaires

---

# 16. Branch Naming

```
feature/people_detector

feature/vehicle_detector

feature/memory_agent

feature/mobile

bugfix/tracker

release/v1.0
```

---

# 17. Commit Messages

Exemples :

```
feat: add people detector

feat: implement reasoning agent

fix: tracker bug

docs: update installation

refactor: improve memory agent
```

---

# 18. Roadmap

Phase 1

* Architecture

Phase 2

* AI Models

Phase 3

* Multi-Agent System

Phase 4

* Mobile Application

Phase 5

* ONNX Export

Phase 6

* Deployment

Phase 7

* Optimization

---

# 19. Future Improvements

* Face Recognition
* OCR
* GPS Navigation
* Voice Commands
* Cloud Synchronization
* Edge AI
* Multilingual Support
* Object Relationship Analysis

---

# 20. License

Ce projet est développé dans un cadre académique.

Tous les contributeurs doivent respecter les règles du dépôt GitHub.

---

# 🚀 Next Documentation

Les prochaines sections détailleront :

* Le fonctionnement interne de chaque modèle.
* Les datasets.
* L'entraînement complet.
* Les hyperparamètres.
* Les scripts.
* L'export ONNX.
* Les tests.
* Le système Multi-Agent.
* Le fonctionnement interne du Coordinateur.
* L'API Python.
* L'intégration React Native.

Chaque partie sera documentée de manière détaillée afin qu'un nouveau développeur puisse contribuer au projet sans connaissance préalable.
