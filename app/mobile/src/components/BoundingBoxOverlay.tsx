import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Detection } from '../agents/ReasoningAgent';

interface Props {
  detections: Detection[];
  cameraWidth: number;
  cameraHeight: number;
  modelInputWidth?: number;
  modelInputHeight?: number;
}

export const BoundingBoxOverlay: React.FC<Props> = ({ 
  detections, 
  cameraWidth, 
  cameraHeight, 
  modelInputWidth = 640, 
  modelInputHeight = 640 
}) => {
  if (!cameraWidth || !cameraHeight) return null;

  // Scale factors to map from 640x640 model input to actual screen dimensions
  const scaleX = cameraWidth / modelInputWidth;
  const scaleY = cameraHeight / modelInputHeight;

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {detections.map((det, index) => {
        // Calculate on-screen coordinates
        const left = det.bbox.x * scaleX;
        const top = det.bbox.y * scaleY;
        const width = det.bbox.width * scaleX;
        const height = det.bbox.height * scaleY;

        return (
          <View
            key={`${det.label}-${index}`}
            style={[
              styles.box,
              { left, top, width, height }
            ]}
          >
            <View style={styles.labelContainer}>
              <Text style={styles.labelText}>
                {det.label} ({(det.confidence * 100).toFixed(0)}%)
              </Text>
            </View>
          </View>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  box: {
    position: 'absolute',
    borderWidth: 2,
    borderColor: '#0f0',
    backgroundColor: 'rgba(0, 255, 0, 0.1)',
  },
  labelContainer: {
    position: 'absolute',
    top: -20,
    left: -2,
    backgroundColor: '#0f0',
    paddingHorizontal: 4,
    paddingVertical: 2,
  },
  labelText: {
    color: '#000',
    fontSize: 12,
    fontWeight: 'bold',
  },
});
