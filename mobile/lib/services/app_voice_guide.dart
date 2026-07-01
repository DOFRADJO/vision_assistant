import 'package:flutter/material.dart';

import 'voice_coach.dart';
import 'settings_service.dart';

/// Annonces vocales a chaque ecran — guide l utilisateur partout.
class AppVoiceGuide {
  AppVoiceGuide._();

  static String? _lastRoute;
  static DateTime? _lastAt;

  static Future<void> announceRoute(String? routeName, {String? path}) async {
    final key = routeName ?? path ?? '';
    if (key.isEmpty) return;

    final now = DateTime.now();
    if (_lastRoute == key && _lastAt != null && now.difference(_lastAt!) < const Duration(seconds: 2)) {
      return;
    }
    _lastRoute = key;
    _lastAt = now;

    final msg = _messageFor(key, path);
    if (msg != null && SettingsService.instance.current.voiceNavigation) {
      await VoiceCoach.instance.speak(msg);
    }
  }

  static String? _messageFor(String name, String? path) {
    final k = name.startsWith('/') ? name : '/$name';
    return switch (k) {
      '/loading' => 'Chargement de NAVIS. Patientez quelques secondes.',
      '/onboarding' => 'Presentation de NAVIS en trois etapes. Appuyez sur Continuer en bas.',
      '/welcome' =>
        'Accueil NAVIS. Deux boutons en bas : Creer un compte, ou Me connecter. NAVIS vous guide a la voix.',
      '/voice-signup' =>
        'Creation de compte. Etape par etape : prenom, confirmation, code a quatre chiffres. '
        'Maintenez le bouton micro bleu en bas pour parler, ou tapez au clavier.',
      '/voice-login' =>
        'Connexion. Dites ou tapez votre prenom, puis votre code secret a quatre chiffres.',
      '/home' =>
        'Accueil. Bouton Camera pour filmer en direct. Bouton Demo video pour tester sans camera. '
        'Historique, parametres et aide sont plus bas.',
      '/camera' =>
        'Camera activee. NAVIS decrit la scene : personnes, vehicules, positions et distances. '
        'Bouton Enregistrer en bas pour sauver la scene detectee.',
      '/demo' =>
        'Video demonstration. NAVIS analyse chaque image et annonce les objets. '
        'Bouton Enregistrer pour sauver une capture annotee.',
      '/history' => 'Historique de vos scenes et detections enregistrees.',
      '/classes' => 'Liste des objets que NAVIS peut reconnaitre.',
      '/settings' => 'Parametres : voix, vibrations, notifications.',
      '/profile' => 'Votre profil NAVIS.',
      '/notifications' => 'Vos notifications recentes.',
      '/help' => 'Aide vocale NAVIS.',
      _ => path == '/demo'
          ? 'Video demonstration NAVIS.'
          : null,
    };
  }

  static Future<void> announceAction(String action) async {
    if (!SettingsService.instance.current.voiceNavigation) return;
    await VoiceCoach.instance.speak(action);
  }

  static Future<void> announceError(String error) async {
    if (!SettingsService.instance.current.voiceNavigation) return;
    await VoiceCoach.instance.speak(error);
  }
}

class NavisVoiceObserver extends NavigatorObserver {
  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPush(route, previousRoute);
    final name = route.settings.name;
    final path = route.settings.arguments is String ? route.settings.arguments as String : null;
    AppVoiceGuide.announceRoute(name, path: path);
  }
}
