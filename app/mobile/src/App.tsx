import React, { useEffect, useState, useRef, useCallback } from 'react';
import { StyleSheet, Text, View, ActivityIndicator, Platform, Dimensions, LayoutChangeEvent } from 'react-native';
import { useCameraDevice, useCameraPermission, Camera, useFrameProcessor } from 'react-native-vision-camera';
import { InferenceSession, Tensor } from 'onnxruntime-react-native';
import Tts from 'react-native-tts';
import { useResizePlugin } from 'vision-camera-resize-plugin';
import { Worklets } from 'react-native-worklets-core';
import RNFS from 'react-native-fs';

import { parseYoloOutput } from './utils/YoloPostProcess';
import { BoundingBoxOverlay } from './components/BoundingBoxOverlay';
import { ReasoningAgent, Detection } from './agents/ReasoningAgent';

async function copyModelFromAssets(assetPath: string, destFileName: string): Promise<string> {
  const destPath = `${RNFS.DocumentDirectoryPath}/${destFileName}`;
  const exists = await RNFS.exists(destPath);
  if (!exists) {
    if (Platform.OS === 'android') {
      await RNFS.copyFileAssets(assetPath, destPath);
    } else {
      await RNFS.copyFile(`${RNFS.MainBundlePath}/${assetPath}`, destPath);
    }
  }
  return destPath;
}

export default function App() {
  const device = useCameraDevice('back');
  const { hasPermission, requestPermission } = useCameraPermission();
  
  const [isReady, setIsReady] = useState(false);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [cameraDims, setCameraDims] = useState({ width: Dimensions.get('window').width, height: Dimensions.get('window').height });

  // Refs for logic that needs to be accessed in the JS callback without recreating worklets
  const sessionRef = useRef<InferenceSession | null>(null);
  const labelsRef = useRef<string[]>([]);
  const isProcessingRef = useRef(false);
  const reasoningAgentRef = useRef(new ReasoningAgent());
  const lastSpeechTimeRef = useRef(0);

  useEffect(() => {
    async function init() {
      // 1. Permissions
      if (!hasPermission) {
        await requestPermission();
      }
      
      // 2. Init TTS
      Tts.setDefaultLanguage('fr-FR');
      Tts.setDefaultRate(0.5);
      
      // 3. Load Models
      try {
        console.log("Loading models...");
        const peopleModelPath = await copyModelFromAssets('models/people_detector/best.onnx', 'people_detector.onnx');
        // Load other models as needed, for now we will focus on people_detector

        let labelsText = "";
        if (Platform.OS === 'android') {
          labelsText = await RNFS.readFileAssets('models/people_detector/labels.txt');
        } else {
          labelsText = await RNFS.readFile(`${RNFS.MainBundlePath}/models/people_detector/labels.txt`, 'utf8');
        }
        labelsRef.current = labelsText.split('\n').map(l => l.trim()).filter(Boolean);

        const peopleSession = await InferenceSession.create(peopleModelPath);
        sessionRef.current = peopleSession;
        
        setIsReady(true);
        Tts.speak("Assistant visuel prêt");
      } catch (e) {
        console.error("Error loading ONNX models", e);
        Tts.speak("Erreur de chargement des modèles");
      }
    }
    init();
  }, [hasPermission]);

  const { resize } = useResizePlugin();
  
  // The JS function called by the worklet to run inference
  const processFrameOnJS = useCallback(async (frameData: Uint8Array) => {
    if (isProcessingRef.current || !sessionRef.current) return;
    isProcessingRef.current = true;

    try {
      const session = sessionRef.current;
      
      // Convert RGB Uint8Array to Float32Array and normalize to [0, 1]
      // Layout required by ONNX: NCHW [1, 3, 640, 640]
      const numPixels = 640 * 640;
      const floatData = new Float32Array(3 * numPixels);
      for (let i = 0; i < numPixels; i++) {
        floatData[i] = frameData[i * 3] / 255.0;                 // R
        floatData[i + numPixels] = frameData[i * 3 + 1] / 255.0;     // G
        floatData[i + 2 * numPixels] = frameData[i * 3 + 2] / 255.0; // B
      }

      const tensor = new Tensor('float32', floatData, [1, 3, 640, 640]);
      
      // Assume the input name is the first input name from session
      const inputName = session.inputNames[0];
      const feeds: Record<string, Tensor> = {};
      feeds[inputName] = tensor;

      const results = await session.run(feeds);
      
      // Assume the output name is the first output name
      const outputName = session.outputNames[0];
      const outputTensor = results[outputName];
      const outputData = outputTensor.data as Float32Array;
      const dimensions = outputTensor.dims;

      const rawDetections = parseYoloOutput(outputData, dimensions, labelsRef.current, 0.4, 0.45);
      
      // Update UI
      setDetections(rawDetections);

      // Analyze and Speak
      const message = reasoningAgentRef.current.analyze(rawDetections);
      if (message) {
        const now = Date.now();
        // Debounce speech to avoid talking continuously (e.g., every 5 seconds)
        if (now - lastSpeechTimeRef.current > 5000) {
          Tts.speak(message);
          lastSpeechTimeRef.current = now;
        }
      }

    } catch (e) {
      console.warn('Inference error:', e);
    } finally {
      isProcessingRef.current = false;
    }
  }, []);

  // Make processFrameOnJS callable from the worklet
  const runOnJS = Worklets.createRunOnJS(processFrameOnJS);

  const frameProcessor = useFrameProcessor((frame) => {
    'worklet';
    if (!isReady) return;

    // Resize frame for YOLO (640x640)
    const resized = resize(frame, {
      scale: { width: 640, height: 640 },
      pixelFormat: 'rgb',
      dataType: 'uint8'
    });

    // Pass data to JS thread
    runOnJS(resized);
  }, [isReady]);

  const onLayout = (event: LayoutChangeEvent) => {
    setCameraDims({
      width: event.nativeEvent.layout.width,
      height: event.nativeEvent.layout.height,
    });
  };

  if (!hasPermission) {
    return <View style={styles.container}><Text style={styles.text}>Autorisation caméra requise</Text></View>;
  }
  if (!device) {
    return <View style={styles.container}><Text style={styles.text}>Caméra introuvable</Text></View>;
  }

  return (
    <View style={styles.container} onLayout={onLayout}>
      <Camera
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={true}
        frameProcessor={frameProcessor}
        pixelFormat="yuv"
      />
      
      {isReady && (
        <BoundingBoxOverlay 
          detections={detections}
          cameraWidth={cameraDims.width}
          cameraHeight={cameraDims.height}
          modelInputWidth={640}
          modelInputHeight={640}
        />
      )}

      <View style={styles.overlay}>
        {!isReady ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color="#ffffff" />
            <Text style={styles.loadingText}>Initialisation de l'IA...</Text>
          </View>
        ) : (
          <View style={styles.statusBox}>
            <Text style={styles.statusText}>IA Active</Text>
            <Text style={styles.statusSubText}>{detections.length} objet(s) détecté(s)</Text>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    color: '#fff',
    fontSize: 24,
    textAlign: 'center',
    padding: 20,
  },
  overlay: {
    position: 'absolute',
    bottom: 50,
    width: '100%',
    alignItems: 'center',
  },
  loadingBox: {
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    marginTop: 10,
    fontSize: 18,
    fontWeight: 'bold',
  },
  statusBox: {
    backgroundColor: 'rgba(0, 200, 0, 0.7)',
    padding: 15,
    borderRadius: 15,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#0f0',
  },
  statusText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '900',
  },
  statusSubText: {
    color: '#fff',
    fontSize: 16,
  }
});
