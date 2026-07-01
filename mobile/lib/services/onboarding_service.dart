import 'package:shared_preferences/shared_preferences.dart';

class OnboardingService {
  static const _keyDone = 'onboarding_done_v1';

  static Future<bool> isDone() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_keyDone) ?? false;
  }

  static Future<void> markDone() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyDone, true);
  }
}
