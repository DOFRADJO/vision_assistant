import 'dart:async';

import 'voice_coach.dart';

enum NavisVoiceAction {
  openCamera,
  openDemo,
  stopSession,
  recordScene,
  openHistory,
  openObjects,
  openSettings,
  openNotifications,
  openProfile,
  goHome,
  stopListening,
  unknown,
}

class VoiceCommandResult {
  const VoiceCommandResult({
    required this.rawText,
    required this.action,
  });

  final String? rawText;
  final NavisVoiceAction action;
}

class VoiceCommandService {
  VoiceCommandService._();
  static final VoiceCommandService instance = VoiceCommandService._();

  Future<VoiceCommandResult> listenForAction({int listenSeconds = 4}) async {
    final ok = await VoiceCoach.instance.startListening();
    if (!ok) {
      return const VoiceCommandResult(rawText: null, action: NavisVoiceAction.unknown);
    }

    await Future<void>.delayed(Duration(seconds: listenSeconds));
    final text = await VoiceCoach.instance.stopListeningAndGetText();
    final action = _parseAction(text);
    return VoiceCommandResult(rawText: text, action: action);
  }

  NavisVoiceAction _parseAction(String? raw) {
    final s = _normalize(raw);
    if (s.isEmpty) return NavisVoiceAction.unknown;

    if (_hasAny(s, ['ouvre camera', 'ouvrir camera', 'lance camera', 'demarre camera'])) {
      return NavisVoiceAction.openCamera;
    }
    if (_hasAny(s, ['ouvre demo', 'ouvrir demo', 'video demo', 'lance video'])) {
      return NavisVoiceAction.openDemo;
    }
    if (_hasAny(s, ['arrete video', 'arreter video', 'stop video', 'arrete camera', 'arreter camera', 'stop detection'])) {
      return NavisVoiceAction.stopSession;
    }
    if (_hasAny(s, ['enregistre', 'sauvegarde scene', 'capture scene'])) {
      return NavisVoiceAction.recordScene;
    }
    if (_hasAny(s, ['ouvre historique', 'historique'])) {
      return NavisVoiceAction.openHistory;
    }
    if (_hasAny(s, ['ouvre objets', 'liste objets', 'objets'])) {
      return NavisVoiceAction.openObjects;
    }
    if (_hasAny(s, ['ouvre parametres', 'ouvre reglages', 'parametres', 'reglages'])) {
      return NavisVoiceAction.openSettings;
    }
    if (_hasAny(s, ['ouvre notifications', 'notifications'])) {
      return NavisVoiceAction.openNotifications;
    }
    if (_hasAny(s, ['ouvre profil', 'mon profil', 'profil'])) {
      return NavisVoiceAction.openProfile;
    }
    if (_hasAny(s, ['retour accueil', 'aller accueil', 'ouvre accueil', 'accueil'])) {
      return NavisVoiceAction.goHome;
    }
    if (_hasAny(s, ['arrete ecoute', 'arreter ecoute', 'stop ecoute', 'coupe micro', 'desactive micro'])) {
      return NavisVoiceAction.stopListening;
    }
    return NavisVoiceAction.unknown;
  }

  bool _hasAny(String s, List<String> patterns) {
    for (final p in patterns) {
      if (s.contains(p)) return true;
    }
    return false;
  }

  String _normalize(String? raw) {
    if (raw == null) return '';
    return raw
        .toLowerCase()
        .replaceAll('é', 'e')
        .replaceAll('è', 'e')
        .replaceAll('ê', 'e')
        .replaceAll('ë', 'e')
        .replaceAll('à', 'a')
        .replaceAll('â', 'a')
        .replaceAll('î', 'i')
        .replaceAll('ï', 'i')
        .replaceAll('ô', 'o')
        .replaceAll('ù', 'u')
        .replaceAll('û', 'u')
        .replaceAll('ç', 'c')
        .replaceAll(RegExp(r'[^a-z0-9\s]'), ' ')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
  }
}

