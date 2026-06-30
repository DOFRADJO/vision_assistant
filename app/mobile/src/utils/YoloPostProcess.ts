import { Detection } from '../agents/ReasoningAgent';

// Helper for Intersection Over Union (IoU) calculation
function calculateIoU(box1: Detection['bbox'], box2: Detection['bbox']) {
  const x1 = Math.max(box1.x, box2.x);
  const y1 = Math.max(box1.y, box2.y);
  const x2 = Math.min(box1.x + box1.width, box2.x + box2.width);
  const y2 = Math.min(box1.y + box1.height, box2.y + box2.height);

  const intersectionArea = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
  const box1Area = box1.width * box1.height;
  const box2Area = box2.width * box2.height;

  return intersectionArea / (box1Area + box2Area - intersectionArea);
}

export function parseYoloOutput(
  outputData: Float32Array,
  dimensions: readonly number[],
  labels: string[],
  confidenceThreshold = 0.3,
  iouThreshold = 0.45
): Detection[] {
  // output is typically [1, num_classes + 4, 8400]
  if (dimensions.length !== 3) return [];
  const channels = dimensions[1];
  const numAnchors = dimensions[2];
  const numClasses = channels - 4;

  const rawDetections: Detection[] = [];

  // Data layout is [channels, numAnchors] (flattened)
  // row 0: x_center
  // row 1: y_center
  // row 2: width
  // row 3: height
  // row 4+: class confidences

  for (let a = 0; a < numAnchors; a++) {
    let maxConf = 0;
    let maxClassIdx = -1;

    // Find class with maximum confidence for this anchor
    for (let c = 0; c < numClasses; c++) {
      const conf = outputData[(4 + c) * numAnchors + a];
      if (conf > maxConf) {
        maxConf = conf;
        maxClassIdx = c;
      }
    }

    if (maxConf >= confidenceThreshold) {
      const cx = outputData[0 * numAnchors + a];
      const cy = outputData[1 * numAnchors + a];
      const w = outputData[2 * numAnchors + a];
      const h = outputData[3 * numAnchors + a];

      // Convert center to top-left
      const x = cx - w / 2;
      const y = cy - h / 2;

      const labelName = maxClassIdx >= 0 && maxClassIdx < labels.length 
        ? labels[maxClassIdx] 
        : `class_${maxClassIdx}`;

      rawDetections.push({
        label: labelName,
        confidence: maxConf,
        bbox: { x, y, width: w, height: h }
      });
    }
  }

  // Sort by confidence descending
  rawDetections.sort((a, b) => b.confidence - a.confidence);

  // Apply Non-Maximum Suppression (NMS)
  const finalDetections: Detection[] = [];
  const active = new Array(rawDetections.length).fill(true);

  for (let i = 0; i < rawDetections.length; i++) {
    if (!active[i]) continue;
    
    finalDetections.push(rawDetections[i]);
    
    for (let j = i + 1; j < rawDetections.length; j++) {
      if (!active[j]) continue;
      
      // Only apply NMS between same classes
      if (rawDetections[i].label === rawDetections[j].label) {
        const iou = calculateIoU(rawDetections[i].bbox, rawDetections[j].bbox);
        if (iou > iouThreshold) {
          active[j] = false;
        }
      }
    }
  }

  return finalDetections;
}
