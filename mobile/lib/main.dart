import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'providers/app_providers.dart';
import 'router/app_router.dart';
import 'services/notification_service.dart';
import 'services/settings_service.dart';
import 'services/tts_service.dart';
import 'services/voice_coach.dart';
import 'theme/navis_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
    ),
  );
  await NotificationService.instance.init();
  final settings = await SettingsService.instance.load();
  await TtsService.instance.init(rate: settings.speechRate);
  await VoiceCoach.instance.init();
  runApp(
    ProviderScope(
      overrides: [
        settingsProvider.overrideWith((ref) => SettingsNotifier(settings)),
      ],
      child: const NavisApp(),
    ),
  );
}

class NavisApp extends ConsumerWidget {
  const NavisApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'NAVIS',
      debugShowCheckedModeBanner: false,
      theme: buildNavisTheme(),
      routerConfig: router,
    );
  }
}
