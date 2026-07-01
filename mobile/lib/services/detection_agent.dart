import '../models/app_models.dart';
import 'local_database.dart';
import 'scene_interpreter.dart';
import 'tts_service.dart';

/// Agent : interprete la scene complete et annonce de facon utile.
class DetectionAgent {
  DetectionAgent({
    required this.ttsEnabled,
    required this.notificationsEnabled,
    required this.hapticEnabled,
  });

  final bool ttsEnabled;
  final bool notificationsEnabled;
  final bool hapticEnabled;

  final _interpreter = SceneInterpreter.instance;
  static String _lastSignature = '';
  static DateTime? _lastAnnouncedAt;

  Future<void> processDetections(
    List<DetectionBox> boxes, {
    required int frameWidth,
    required int frameHeight,
  }) async {
    if (boxes.isEmpty) return;

    final analysis = _interpreter.analyze(
      boxes,
      frameWidth: frameWidth,
      frameHeight: frameHeight,
    );
    if (analysis.spokenText.isEmpty) return;
    if (!_interpreter.shouldAnnounce(analysis)) return;

    final signature = '${analysis.summary}|${analysis.peopleCount}|${analysis.vehicleCount}|${analysis.hasDanger}';
    final now = DateTime.now();
    final lastAt = _lastAnnouncedAt;
    if (signature == _lastSignature && lastAt != null && now.difference(lastAt) < const Duration(milliseconds: 2500)) {
      return;
    }
    if (lastAt != null && now.difference(lastAt) < const Duration(milliseconds: 900)) {
      return;
    }
    _lastSignature = signature;
    _lastAnnouncedAt = now;

    await LocalDatabase.instance.insertDetection(
      DetectionRecord(
        labelFr: analysis.summary,
        labelEn: 'scene',
        confidence: 1.0,
        createdAt: now,
      ),
    );

    if (ttsEnabled) {
      await TtsService.instance.speak(
        analysis.spokenText,
        cooldown: analysis.isUrgent ? const Duration(milliseconds: 1200) : const Duration(seconds: 2),
        waitForCompletion: false,
        interrupt: false,
      );
    }

    // Notifications detaillees desactivees ici.
    // Les notifications sont envoyees uniquement au debut et a la fin
    // des sessions camera/demo selon la demande produit.
  }
}
