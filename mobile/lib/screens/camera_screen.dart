import 'dart:async';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image/image.dart' as img;
import 'package:permission_handler/permission_handler.dart';

import '../core/navis_text.dart';
import '../models/app_models.dart';
import '../services/app_voice_guide.dart';
import '../services/detection_agent.dart';
import '../services/notification_service.dart';
import '../services/scene_interpreter.dart';
import '../services/scene_recorder.dart';
import '../services/settings_service.dart';
import '../services/voice_coach.dart';
import '../services/voice_command_service.dart';
import '../services/yolo_detector.dart';
import '../widgets/detection_scene_view.dart';

class CameraScreen extends ConsumerStatefulWidget {
  const CameraScreen({super.key});

  @override
  ConsumerState<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends ConsumerState<CameraScreen> {
  CameraController? _controller;
  bool _initializing = true;
  bool _running = false;
  bool _saving = false;
  String _status = 'Initialisation camera...';
  List<DetectionBox> _lastBoxes = [];
  String _lastSceneText = '';
  Uint8List? _lastFrameBytes;
  int _frameW = 0;
  int _frameH = 0;
  bool _voiceBusy = false;
  bool _sessionClosed = false;
  bool _continuousListening = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      AppVoiceGuide.announceRoute('/camera');
      _setup();
    });
  }

  Future<void> _setup() async {
    try {
      if (!await Permission.camera.request().isGranted) {
        setState(() {
          _status = 'Autorisez la camera';
          _initializing = false;
        });
        return;
      }
      await YoloDetector.instance.init();
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        setState(() {
          _status = 'Aucune camera';
          _initializing = false;
        });
        return;
      }
      _controller = CameraController(cameras.first, ResolutionPreset.medium, enableAudio: false);
      await _controller!.initialize();
      setState(() {
        _status = 'Camera active';
        _initializing = false;
        _lastSceneText = 'Analyse...';
      });
      _running = true;
      final s = SettingsService.instance.current;
      if (s.notifications) {
        unawaited(
          NotificationService.instance.notifyDetection(
            title: 'NAVIS Camera',
            body: 'Demarrage de la camera en direct',
            vibrate: false,
          ),
        );
      }
      unawaited(_detectionLoop());
    } catch (e) {
      setState(() {
        _status = 'Erreur: $e';
        _initializing = false;
      });
    }
  }

  Future<void> _detectionLoop() async {
    while (_running && mounted) {
      await _captureAndDetect();
      if (!_running || !mounted) break;
      await Future<void>.delayed(const Duration(milliseconds: 180));
    }
  }

  Future<void> _captureAndDetect() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    try {
      final file = await _controller!.takePicture();
      final bytes = await file.readAsBytes();
      final decoded = img.decodeImage(bytes);
      if (decoded == null) {
        setState(() {
          _lastBoxes = [];
          _lastSceneText = 'Analyse image suivante...';
        });
        return;
      }

      final boxes = await YoloDetector.instance.detectFromImage(decoded, confThreshold: 0.18);
      if (!mounted) return;

      final analysis = boxes.isEmpty
          ? const SceneAnalysis.empty()
          : SceneInterpreter.instance.analyze(boxes, frameWidth: decoded.width, frameHeight: decoded.height);

      setState(() {
        _lastBoxes = boxes;
        _lastFrameBytes = bytes;
        _frameW = decoded.width;
        _frameH = decoded.height;
        _lastSceneText = boxes.isEmpty
            ? 'Analyse en cours...'
            : NavisText.clean(analysis.spokenText);
      });

      if (boxes.isNotEmpty) {
        final s = SettingsService.instance.current;
        unawaited(
          DetectionAgent(
            ttsEnabled: true,
            notificationsEnabled: false,
            hapticEnabled: s.haptic,
          ).processDetections(boxes, frameWidth: decoded.width, frameHeight: decoded.height),
        );
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _lastBoxes = [];
          _lastSceneText = 'Analyse image suivante...';
        });
      }
    }
  }

  Future<void> _recordScene() async {
    if (_saving || _lastFrameBytes == null) {
      await AppVoiceGuide.announceAction('Rien a enregistrer.');
      return;
    }
    setState(() => _saving = true);
    try {
      final snap = await SceneRecorder.instance.save(
        imageBytes: _lastFrameBytes!,
        frameWidth: _frameW,
        frameHeight: _frameH,
        boxes: _lastBoxes,
        summary: _lastSceneText,
        source: 'camera',
      );
      if (snap != null) {
        await AppVoiceGuide.announceAction('Scene enregistree avec ${snap.objectCount} objets.');
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _stopSession({bool pop = true}) async {
    if (_sessionClosed) return;
    _sessionClosed = true;
    _running = false;
    final s = SettingsService.instance.current;
    if (s.notifications) {
      await NotificationService.instance.notifyDetection(
        title: 'NAVIS Camera',
        body: 'Fin de la session camera',
        vibrate: false,
      );
    }
    if (mounted && pop) {
      Navigator.of(context).pop();
    }
  }

  Future<void> _listenCommand() async {
    if (_voiceBusy) return;
    setState(() => _voiceBusy = true);
    try {
      await VoiceCoach.instance.speak(
        'Commande camera. Dites enregistrer, arreter camera ou retour accueil.',
      );
      final result = await VoiceCommandService.instance.listenForAction();
      await _executeVoiceAction(result.action);
    } finally {
      if (mounted) setState(() => _voiceBusy = false);
    }
  }

  Future<void> _toggleContinuousListening() async {
    if (_continuousListening) {
      setState(() => _continuousListening = false);
      await VoiceCoach.instance.speak('Mains libres camera arrete.');
      return;
    }
    setState(() => _continuousListening = true);
    await VoiceCoach.instance.speak(
      'Mains libres camera actif. Dites enregistrer, arreter camera, ou arrete ecoute.',
    );
    unawaited(_continuousLoop());
  }

  Future<void> _continuousLoop() async {
    while (mounted && _continuousListening && _running) {
      if (_voiceBusy) {
        await Future<void>.delayed(const Duration(milliseconds: 250));
        continue;
      }
      setState(() => _voiceBusy = true);
      try {
        final result = await VoiceCommandService.instance.listenForAction(listenSeconds: 5);
        await _executeVoiceAction(result.action);
      } finally {
        if (mounted) setState(() => _voiceBusy = false);
      }
      await Future<void>.delayed(const Duration(milliseconds: 350));
    }
  }

  Future<void> _executeVoiceAction(NavisVoiceAction action) async {
    switch (action) {
      case NavisVoiceAction.recordScene:
        await _recordScene();
        return;
      case NavisVoiceAction.stopSession:
      case NavisVoiceAction.goHome:
        await _stopSession();
        return;
      case NavisVoiceAction.stopListening:
        setState(() => _continuousListening = false);
        await VoiceCoach.instance.speak('Mains libres camera desactive.');
        return;
      default:
        await VoiceCoach.instance.speak('Commande non reconnue.');
        return;
    }
  }

  @override
  void dispose() {
    _running = false;
    _continuousListening = false;
    _controller?.dispose();
    unawaited(_stopSession(pop: false));
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: NavisSceneAppBar(
        title: 'Camera NAVIS',
        actions: [
          IconButton(
            tooltip: 'Commande vocale',
            onPressed: _listenCommand,
            onLongPress: _toggleContinuousListening,
            icon: Icon(
              _voiceBusy
                  ? Icons.mic_off_rounded
                  : (_continuousListening ? Icons.hearing_rounded : Icons.mic_rounded),
            ),
          ),
        ],
      ),
      body: _initializing
          ? Center(child: Text(_status, style: const TextStyle(color: Colors.white, fontSize: 16)))
          : _controller == null || !_controller!.value.isInitialized
              ? Center(child: Text(_status, style: const TextStyle(color: Colors.white)))
              : Column(
                  children: [
                    Expanded(
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          CameraPreview(_controller!),
                          DetectionSceneOverlay(
                            boxes: _lastBoxes,
                            sourceWidth: _frameW.toDouble(),
                            sourceHeight: _frameH.toDouble(),
                          ),
                        ],
                      ),
                    ),
                    SceneToolbar(
                      sceneText: _lastSceneText.isNotEmpty ? _lastSceneText : _status,
                      objectCount: _lastBoxes.length,
                      isRecording: _saving,
                      onBack: _stopSession,
                      onRecord: _recordScene,
                    ),
                  ],
                ),
    );
  }
}
