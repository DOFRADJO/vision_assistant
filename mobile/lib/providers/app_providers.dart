import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../services/local_auth_service.dart';
import '../services/settings_service.dart';

final localAuthProvider = Provider<LocalAuthService>((ref) => LocalAuthService.instance);

final authStateProvider = StateNotifierProvider<AuthNotifier, AsyncValue<bool>>((ref) {
  return AuthNotifier(ref.watch(localAuthProvider));
});

class AuthNotifier extends StateNotifier<AsyncValue<bool>> {
  AuthNotifier(this._auth) : super(const AsyncValue.loading()) {
    _init();
  }

  final LocalAuthService _auth;

  Future<void> _init() async {
    await _auth.restoreSession();
    state = AsyncValue.data(_auth.isLoggedIn);
  }

  Future<void> registerVoice(String name, String pin, {int? age, String? city}) async {
    await _auth.register(displayName: name, pin: pin, age: age, city: city);
    state = const AsyncValue.data(true);
  }

  Future<void> loginVoice(String name, String pin) async {
    await _auth.login(displayName: name, pin: pin);
    state = const AsyncValue.data(true);
  }

  Future<void> logout() async {
    await _auth.logout();
    state = const AsyncValue.data(false);
  }
}

final settingsProvider = StateNotifierProvider<SettingsNotifier, AppSettings>((ref) {
  return SettingsNotifier();
});

class AppSettings {
  const AppSettings({
    this.largeText = true,
    this.haptic = true,
    this.voiceAnnounce = true,
    this.notifications = true,
    this.speechRate = 0.5,
    this.voiceNavigation = true,
  });

  final bool largeText;
  final bool haptic;
  final bool voiceAnnounce;
  final bool notifications;
  final double speechRate;
  final bool voiceNavigation;

  AppSettings copyWith({
    bool? largeText,
    bool? haptic,
    bool? voiceAnnounce,
    bool? notifications,
    double? speechRate,
    bool? voiceNavigation,
  }) {
    return AppSettings(
      largeText: largeText ?? this.largeText,
      haptic: haptic ?? this.haptic,
      voiceAnnounce: voiceAnnounce ?? this.voiceAnnounce,
      notifications: notifications ?? this.notifications,
      speechRate: speechRate ?? this.speechRate,
      voiceNavigation: voiceNavigation ?? this.voiceNavigation,
    );
  }
}

class SettingsNotifier extends StateNotifier<AppSettings> {
  SettingsNotifier([AppSettings? initial]) : super(initial ?? const AppSettings());

  void update(AppSettings settings) {
    state = settings;
    SettingsService.instance.save(settings);
  }
}
