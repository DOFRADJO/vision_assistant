import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:speech_to_text/speech_recognition_error.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:vibration/vibration.dart';

import 'tts_service.dart';
import '../core/navis_text.dart';

/// STT francais — mode hors ligne (onDevice) en priorite pour eviter error_network.
class VoiceCoach {
  VoiceCoach._();
  static final VoiceCoach instance = VoiceCoach._();

  final SpeechToText _stt = SpeechToText();
  bool _sttReady = false;
  bool _listening = false;
  bool _retrying = false;
  String _lastError = '';
  String _bestText = '';
  List<_ListenProfile> _profiles = [];
  int _profileIndex = 0;

  static const _blacklistedLocales = {'fr_BE', 'fr-be', 'fr_be'};

  bool get isListening => _listening;
  String get lastError => _lastError;

  final ValueNotifier<String> transcriptNotifier = ValueNotifier('');
  final ValueNotifier<String> statusNotifier = ValueNotifier('Pret');

  Future<bool> init() async {
    final mic = await Permission.microphone.request();
    if (!mic.isGranted) {
      _lastError = 'Autorisez le microphone dans Reglages Android';
      statusNotifier.value = _lastError;
      return false;
    }

    if (!_sttReady) {
      _sttReady = await _stt.initialize(
        onStatus: _onStatus,
        onError: _onError,
        debugLogging: kDebugMode,
      );
    }

    if (!_sttReady) {
      _lastError = 'Reconnaissance vocale indisponible. Installez ou mettez a jour Google.';
      statusNotifier.value = _lastError;
      return false;
    }

    _profiles = await _buildProfiles();
    _profileIndex = 0;
    debugPrint('NAVIS STT profiles: $_profiles');
    statusNotifier.value = 'Micro pret (mode hors ligne)';
    return true;
  }

  Future<List<_ListenProfile>> _buildProfiles() async {
    final available = await _stt.locales();
    final frIds = <String>[];
    for (final l in available) {
      final id = l.localeId;
      if (id.startsWith('fr') && !_blacklistedLocales.contains(id) && !frIds.contains(id)) {
        frIds.add(id);
      }
    }
    for (final id in ['fr_FR', 'fr-FR', 'fr_CA']) {
      if (!frIds.contains(id) && available.any((l) => l.localeId == id)) {
        frIds.insert(0, id);
      }
    }
    if (frIds.isEmpty) frIds.add('fr_FR');

    final profiles = <_ListenProfile>[
      // Hors ligne d abord — pas de error_network
      for (final id in frIds) _ListenProfile(locale: id, onDevice: true),
      const _ListenProfile(locale: null, onDevice: true),
      // Repli cloud si internet disponible
      for (final id in frIds) _ListenProfile(locale: id, onDevice: false),
      const _ListenProfile(locale: null, onDevice: false),
    ];
    return profiles;
  }

  _ListenProfile get _currentProfile =>
      _profiles[_profileIndex.clamp(0, _profiles.length - 1)];

  void _onError(SpeechRecognitionError error) {
    _lastError = error.errorMsg;
    debugPrint('NAVIS STT error: ${error.errorMsg}');
    final msg = error.errorMsg.toLowerCase();
    final isNetwork = msg.contains('network') || msg.contains('reseau');
    final isLang = msg.contains('language') || msg.contains('langue');

    if ((isNetwork || isLang) && _listening && !_retrying && _profileIndex < _profiles.length - 1) {
      _retryNextProfile(isNetwork ? 'Mode hors ligne...' : 'Autre langue...');
      return;
    }

    if (isNetwork) {
      statusNotifier.value =
          'Voix hors ligne indisponible. Telechargez Francais hors ligne dans Google, ou utilisez le clavier.';
    } else if (isLang) {
      statusNotifier.value = 'Langue francaise non installee. Utilisez le clavier en attendant.';
    } else {
      statusNotifier.value = 'Erreur: ${error.errorMsg}';
    }
  }

  Future<void> _retryNextProfile(String label) async {
    if (_retrying) return;
    _retrying = true;
    _profileIndex++;
    statusNotifier.value = label;
    await _stt.stop();
    await Future<void>.delayed(const Duration(milliseconds: 350));
    await _startListenInternal();
    _retrying = false;
  }

  void _onStatus(String status) {
    debugPrint('NAVIS STT status: $status');
    if (status == SpeechToText.listeningStatus) {
      statusNotifier.value = 'Parlez en francais';
    }
  }

  Future<void> speak(String text, {bool interrupt = true}) async {
    if (interrupt) await TtsService.instance.stop();
    await TtsService.instance.speak(text, waitForCompletion: true, cooldown: Duration.zero);
  }

  Future<void> announceScreen(String title, {List<String> actions = const []}) async {
    await speak(title);
  }

  Future<bool> startListening() async {
    if (!_sttReady && !await init()) return false;
    if (_listening) await _stt.stop();

    await TtsService.instance.stop();
    await Future<void>.delayed(const Duration(milliseconds: 600));

    _lastError = '';
    _bestText = '';
    transcriptNotifier.value = '';
    statusNotifier.value = 'Ouverture du micro...';

    return _startListenInternal();
  }

  Future<bool> _startListenInternal() async {
    if (_profiles.isEmpty) _profiles = await _buildProfiles();

    for (var i = _profileIndex; i < _profiles.length; i++) {
      _profileIndex = i;
      final p = _currentProfile;
      debugPrint('NAVIS STT try: locale=${p.locale ?? "system"} onDevice=${p.onDevice}');

      try {
        await _stt.listen(
          onResult: _onResult,
          listenOptions: SpeechListenOptions(
            localeId: p.locale,
            listenMode: ListenMode.dictation,
            partialResults: true,
            cancelOnError: false,
            listenFor: const Duration(seconds: 30),
            pauseFor: const Duration(seconds: 4),
            onDevice: p.onDevice,
          ),
        );
        _listening = true;
        statusNotifier.value = p.onDevice ? 'Parlez (hors ligne)' : 'Parlez maintenant';
        if (await Vibration.hasVibrator()) await Vibration.vibrate(duration: 50);
        return true;
      } catch (e) {
        _lastError = e.toString();
        debugPrint('NAVIS STT listen catch: $e');
      }
    }

    _listening = false;
    statusNotifier.value = 'Micro impossible. Utilisez le champ texte ci dessus.';
    return false;
  }

  void _onResult(SpeechRecognitionResult result) {
    final words = result.recognizedWords.trim();
    if (words.isEmpty) return;
    _bestText = words;
    transcriptNotifier.value = NavisText.clean(words);
    statusNotifier.value = NavisText.clean(words);
    debugPrint('NAVIS STT heard: $words');
  }

  Future<String?> stopListeningAndGetText() async {
    if (_listening) {
      await _stt.stop();
      await Future<void>.delayed(const Duration(milliseconds: 350));
    }
    _listening = false;
    final text = _bestText.trim();
    if (text.isEmpty) {
      statusNotifier.value = _lastError.isNotEmpty ? _friendlyError(_lastError) : 'Rien entendu, reessayez ou tapez au clavier';
      return null;
    }
    return text;
  }

  String _friendlyError(String raw) {
    final l = raw.toLowerCase();
    if (l.contains('network')) {
      return 'Pas de reseau pour la voix cloud. Tapez votre prenom au clavier, ou installez Francais hors ligne dans Google.';
    }
    return raw;
  }

  Future<void> stopListening() async {
    if (_listening) await _stt.stop();
    _listening = false;
  }

  String? parsePin(String? speech) {
    if (speech == null || speech.isEmpty) return null;
    final digits = StringBuffer();
    for (final m in RegExp(r'\d').allMatches(speech)) {
      digits.write(m.group(0));
    }
    if (digits.length >= 4) return digits.toString().substring(0, 4);

    const map = {
      'zero': '0', 'zéro': '0', 'un': '1', 'une': '1', 'deux': '2', 'trois': '3',
      'quatre': '4', 'cinq': '5', 'six': '6', 'sept': '7', 'huit': '8', 'neuf': '9',
    };
    for (final w in speech.toLowerCase().split(RegExp(r'\s+'))) {
      final d = map[w.trim()];
      if (d != null) digits.write(d);
    }
    if (digits.length >= 4) return digits.toString().substring(0, 4);
    return null;
  }

  Future<void> stop() async {
    await stopListening();
    await TtsService.instance.stop();
  }
}

class _ListenProfile {
  const _ListenProfile({required this.locale, required this.onDevice});

  final String? locale;
  final bool onDevice;

  @override
  String toString() => '{${locale ?? "sys"}, onDevice=$onDevice}';
}
