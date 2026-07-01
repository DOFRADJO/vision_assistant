import 'package:flutter_tts/flutter_tts.dart';

import '../core/navis_text.dart';

class TtsService {
  TtsService._();
  static final TtsService instance = TtsService._();

  final FlutterTts _tts = FlutterTts();
  bool _ready = false;
  bool _isSpeaking = false;
  DateTime? _speakStartedAt;
  double _rate = 0.5;

  Future<void> init({double rate = 0.5}) async {
    _rate = rate;
    try {
      await _tts.setLanguage('fr-FR');
    } catch (_) {
      try {
        await _tts.setLanguage('fr_FR');
      } catch (_) {
        await _tts.setLanguage('fr-CA');
      }
    }
    await _tts.setSpeechRate(_rate);
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);
    await _tts.awaitSpeakCompletion(true);
    _tts.setStartHandler(() {
      _isSpeaking = true;
      _speakStartedAt = DateTime.now();
    });
    _tts.setCompletionHandler(() {
      _isSpeaking = false;
      _speakStartedAt = null;
    });
    _tts.setCancelHandler(() {
      _isSpeaking = false;
      _speakStartedAt = null;
    });
    _tts.setErrorHandler((_) {
      _isSpeaking = false;
      _speakStartedAt = null;
    });
    _ready = true;
  }

  Future<void> setRate(double rate) async {
    _rate = rate;
    await _tts.setSpeechRate(rate);
  }

  String? _lastSpoken;
  DateTime? _lastAt;

  /// Parle et attend la fin avant de rendre la main (indispensable avant STT).
  Future<void> speak(
    String text, {
    Duration cooldown = const Duration(seconds: 3),
    bool waitForCompletion = true,
    bool interrupt = true,
  }) async {
    if (!_ready) await init();
    final now = DateTime.now();
    if (_lastSpoken == text && _lastAt != null && now.difference(_lastAt!) < cooldown) {
      return;
    }
    if (!interrupt && _isSpeaking) {
      final startedAt = _speakStartedAt;
      if (startedAt != null && DateTime.now().difference(startedAt) > const Duration(seconds: 8)) {
        _isSpeaking = false;
        _speakStartedAt = null;
      } else {
        return;
      }
    }
    if (!interrupt && _isSpeaking) {
      return;
    }
    _lastSpoken = text;
    _lastAt = now;
    if (interrupt) {
      await _tts.stop();
    }
    if (waitForCompletion) {
      await _tts.awaitSpeakCompletion(true);
    }
    await _tts.speak(NavisText.clean(text));
    if (waitForCompletion) {
      // Laisser l echo se dissiper avant d ouvrir le micro
      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
  }

  Future<void> stop() async {
    await _tts.stop();
    _isSpeaking = false;
    _speakStartedAt = null;
    await Future<void>.delayed(const Duration(milliseconds: 200));
  }
}
