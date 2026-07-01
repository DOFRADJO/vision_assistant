import 'package:shared_preferences/shared_preferences.dart';

import '../providers/app_providers.dart';
import 'tts_service.dart';

class SettingsService {
  SettingsService._();
  static final SettingsService instance = SettingsService._();

  AppSettings current = const AppSettings();

  Future<AppSettings> load() async {
    final prefs = await SharedPreferences.getInstance();
    current = AppSettings(
      largeText: prefs.getBool('large_text') ?? true,
      haptic: prefs.getBool('haptic') ?? true,
      voiceAnnounce: prefs.getBool('voice') ?? true,
      notifications: prefs.getBool('notifications') ?? true,
      speechRate: prefs.getDouble('speech_rate') ?? 0.5,
      voiceNavigation: prefs.getBool('voice_nav') ?? true,
    );
    await TtsService.instance.setRate(current.speechRate);
    return current;
  }

  Future<void> save(AppSettings settings) async {
    current = settings;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('large_text', settings.largeText);
    await prefs.setBool('haptic', settings.haptic);
    await prefs.setBool('voice', settings.voiceAnnounce);
    await prefs.setBool('notifications', settings.notifications);
    await prefs.setBool('voice_nav', settings.voiceNavigation);
    await prefs.setDouble('speech_rate', settings.speechRate);
    await TtsService.instance.setRate(settings.speechRate);
  }
}
