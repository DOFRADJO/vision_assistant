export interface Detection {
  label: string;
  confidence: number;
  bbox: { x: number; y: number; width: number; height: number };
}

export class ReasoningAgent {
  /**
   * Analyse les détections et retourne le message le plus prioritaire
   */
  public analyze(detections: Detection[]): string | null {
    if (detections.length === 0) return null;

    // Trier par priorité (exemple basique)
    // On pourrait attribuer un niveau de dangerosité selon le label
    const priorityMap: { [key: string]: number } = {
      'person': 1,
      'car': 2,
      'truck': 2,
      'bus': 2,
      'traffic light': 3,
      'stop sign': 3,
      'chair': 0,
      'table': 0,
    };

    let highestPriorityItem = detections[0];
    let highestPriority = priorityMap[highestPriorityItem.label] ?? 0;

    for (const det of detections) {
      const p = priorityMap[det.label] ?? 0;
      // Plus la box est grande, plus l'objet est proche
      const area = det.bbox.width * det.bbox.height;
      
      if (p > highestPriority || (p === highestPriority && area > (highestPriorityItem.bbox.width * highestPriorityItem.bbox.height))) {
        highestPriorityItem = det;
        highestPriority = p;
      }
    }

    // Traduction simple (à étendre)
    const translations: { [key: string]: string } = {
      'person': 'Personne',
      'car': 'Voiture',
      'truck': 'Camion',
      'bus': 'Bus',
      'traffic light': 'Feu de signalisation',
      'stop sign': 'Panneau stop',
      'chair': 'Chaise',
      'table': 'Table'
    };

    const labelFr = translations[highestPriorityItem.label] || highestPriorityItem.label;
    
    if (highestPriority > 0) {
       return `Attention, ${labelFr} détecté(e) devant vous.`;
    }

    return `${labelFr} détecté(e).`;
  }
}
