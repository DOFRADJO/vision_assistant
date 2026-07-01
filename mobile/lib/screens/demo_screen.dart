import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image/image.dart' as img;
import 'package:video_player/video_player.dart';
import 'package:video_thumbnail/video_thumbnail.dart';

import '../core/navis_text.dart';
import '../models/app_models.dart';
import '../services/app_voice_guide.dart';
import '../services/demo_video_service.dart';
import '../services/detection_agent.dart';
import '../services/notification_service.dart';
import '../services/scene_interpreter.dart';
import '../services/scene_recorder.dart';
import '../services/settings_service.dart';
import '../services/voice_coach.dart';
import '../services/voice_command_service.dart';
import '../services/yolo_detector.dart';
import '../widgets/detection_scene_view.dart';

class DemoScreen extends ConsumerStatefulWidget {
  const DemoScreen({super.key});

  @override
  ConsumerState<DemoScreen> createState() => _DemoScreenState();
}

class _DemoScreenState extends ConsumerState<DemoScreen> {
  VideoPlayerController? _video;
  bool _loading = true;
  bool _saving = false;
  bool _running = false;
  String _status = 'Ouverture de la video...';
  String _sceneText = '';
  List<DetectionBox> _boxes = [];
  Uint8List? _lastFrameBytes;
  int _frameW = 0;
  int _frameH = 0;
  String? _videoPath;
  int _lastAnalyzedPosMs = -1;
  int _detectGeneration = 0;
  bool _voiceBusy = false;
  bool _sessionClosed = false;
  bool _continuousListening = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      AppVoiceGuide.announceRoute('/demo');
      _setup();
    });
  }

  Future<void> _setup() async {
    try {
      final file = await DemoVideoService.instance.getVideoFile();
      _videoPath = file.path;
      _video = VideoPlayerController.file(file);
      await _video!.initialize();
      if (!mounted) return;

      await _video!.setLooping(true);
      await _video!.play();

      setState(() {
        _loading = false;
        _status = 'Demonstration en direct';
        _sceneText = 'Analyse...';
      });

      _running = true;
      final s = SettingsService.instance.current;
      if (s.notifications) {
        unawaited(
          NotificationService.instance.notifyDetection(
            title: 'NAVIS Demo',
            body: 'Demarrage de la demonstration video',
            vibrate: false,
          ),
        );
      }
      unawaited(_detectionLoop());
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _status = NavisText.clean('Erreur: $e');
        });
      }
    }
  }

  Future<void> _detectionLoop() async {
    while (_running && mounted) {
      await _runDetection();
      if (!_running || !mounted) break;
      await Future<void>.delayed(const Duration(milliseconds: 180));
    }
  }

  Future<void> _runDetection() async {
    if (_video == null || !_video!.value.isInitialized || _videoPath == null) return;
    if (!_video!.value.isPlaying && _video!.value.position.inMilliseconds == 0) return;

    final pos = _video!.value.position.inMilliseconds;
    // Boucle video : position qui recule → re-analyser depuis le debut.
    if (pos < _lastAnalyzedPosMs - 500) {
      _lastAnalyzedPosMs = -1;
    }
    // Ne pas re-analyser la meme position video (evite doublons).
    if (pos == _lastAnalyzedPosMs) return;
    _lastAnalyzedPosMs = pos;

    final gen = ++_detectGeneration;
    if (mounted) {
      setState(() {
        _boxes = [];
        _sceneText = 'Analyse image en cours...';
      });
    }

    try {
      final bytes = await VideoThumbnail.thumbnailData(
        video: _videoPath!,
        imageFormat: ImageFormat.JPEG,
        timeMs: pos,
        quality: 90,
        maxWidth: 640,
      );
      if (!mounted || gen != _detectGeneration) return;

      if (bytes == null) {
        setState(() {
          _boxes = [];
          _sceneText = 'Aucun objet sur cette image';
        });
        return;
      }

      final decoded = img.decodeImage(bytes);
      if (decoded == null) {
        setState(() {
          _boxes = [];
          _sceneText = 'Aucun objet sur cette image';
        });
        return;
      }

      var boxes = await YoloDetector.instance.detectFromImage(decoded, confThreshold: 0.18);
      if (!mounted || gen != _detectGeneration) return;

      final analysis = boxes.isEmpty
          ? const SceneAnalysis.empty()
          : SceneInterpreter.instance.analyze(boxes, frameWidth: decoded.width, frameHeight: decoded.height);

      final text = boxes.isEmpty
          ? 'Aucun objet detecte sur cette image'
          : NavisText.clean(analysis.spokenText);

      setState(() {
        _boxes = List<DetectionBox>.from(boxes);
        _lastFrameBytes = bytes;
        _frameW = decoded.width;
        _frameH = decoded.height;
        _sceneText = text;
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
      if (!mounted || gen != _detectGeneration) return;
      setState(() {
        _boxes = [];
        _sceneText = 'Analyse image suivante...';
      });
    }
  }

  Future<void> _recordScene() async {
    if (_saving || _lastFrameBytes == null) {
      await AppVoiceGuide.announceAction('Rien a enregistrer pour le moment.');
      return;
    }
    setState(() => _saving = true);
    try {
      final snap = await SceneRecorder.instance.save(
        imageBytes: _lastFrameBytes!,
        frameWidth: _frameW,
        frameHeight: _frameH,
        boxes: _boxes,
        summary: _sceneText,
        source: 'demo',
      );
      if (snap != null) {
        await AppVoiceGuide.announceAction(
          'Scene enregistree, ${snap.objectCount} objets avec etiquettes.',
        );
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
        title: 'NAVIS Demo',
        body: 'Fin de la demonstration video',
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
        'Commande demo. Dites enregistrer, arreter video ou retour accueil.',
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
      await VoiceCoach.instance.speak('Mains libres demo arrete.');
      return;
    }
    setState(() => _continuousListening = true);
    await VoiceCoach.instance.speak(
      'Mains libres demo actif. Dites enregistrer, arreter video, ou arrete ecoute.',
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
        await VoiceCoach.instance.speak('Mains libres demo desactive.');
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
    _video?.dispose();
    unawaited(_stopSession(pop: false));
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: NavisSceneAppBar(
        title: 'Demo video',
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
      body: _loading
          ? const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(color: Color(0xFF4DA3FF)),
                  SizedBox(height: 16),
                  Text('Chargement video...', style: TextStyle(color: Colors.white, fontSize: 16)),
                ],
              ),
            )
          : _video == null || !_video!.value.isInitialized
              ? Center(child: Text(_status, style: const TextStyle(color: Colors.white)))
              : Column(
                  children: [
                    Expanded(
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          Center(
                            child: AspectRatio(
                              aspectRatio: _video!.value.aspectRatio,
                              child: VideoPlayer(_video!),
                            ),
                          ),
                          DetectionSceneOverlay(
                            key: ValueKey('demo_overlay_$_detectGeneration'),
                            boxes: _boxes,
                            sourceWidth: _frameW.toDouble(),
                            sourceHeight: _frameH.toDouble(),
                          ),
                        ],
                      ),
                    ),
                    SceneToolbar(
                      sceneText: _sceneText.isNotEmpty ? _sceneText : _status,
                      objectCount: _boxes.length,
                      isRecording: _saving,
                      onBack: _stopSession,
                      onRecord: _recordScene,
                    ),
                  ],
                ),
    );
  }
}
