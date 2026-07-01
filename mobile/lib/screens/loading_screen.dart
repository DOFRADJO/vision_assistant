import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../services/app_voice_guide.dart';
import '../services/demo_video_service.dart';
import '../services/local_database.dart';
import '../services/onboarding_service.dart';
import '../services/settings_service.dart';
import '../services/tts_service.dart';
import '../services/voice_coach.dart';
import '../services/yolo_detector.dart';
import '../theme/navis_theme.dart';
import '../widgets/navis_logo.dart';

class LoadingScreen extends StatefulWidget {
  const LoadingScreen({super.key});

  @override
  State<LoadingScreen> createState() => _LoadingScreenState();
}

class _LoadingScreenState extends State<LoadingScreen> {
  String _label = 'Chargement de NAVIS...';

  @override
  void initState() {
    super.initState();
    _boot();
  }

  Future<void> _boot() async {
    try {
      setState(() => _label = 'Initialisation de la voix...');
      await TtsService.instance.init(rate: SettingsService.instance.current.speechRate);
      await VoiceCoach.instance.init();

      setState(() => _label = 'Chargement du modele IA...');
      await YoloDetector.instance.init();

      setState(() => _label = 'Preparation de la video demo...');
      await DemoVideoService.instance.prepare();

      setState(() => _label = 'Pret');
      await Future<void>.delayed(const Duration(milliseconds: 400));

      final onboardingDone = await OnboardingService.isDone();
      final userId = await LocalDatabase.instance.getActiveUserId();
      if (!mounted) return;
      if (userId != null) {
        context.go('/home');
      } else if (!onboardingDone) {
        context.go('/onboarding');
      } else {
        context.go('/welcome');
      }
    } catch (e) {
      if (mounted) {
        setState(() => _label = 'Erreur au demarrage');
        await Future<void>.delayed(const Duration(seconds: 2));
        if (mounted) context.go('/welcome');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NavisColors.azureDeep,
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const NavisLogo(size: 96, animated: false),
                const SizedBox(height: 24),
                const Text(
                  'NAVIS',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.w700,
                    color: NavisColors.white,
                    letterSpacing: 4,
                  ),
                ),
                const SizedBox(height: 32),
                const SizedBox(
                  width: 48,
                  height: 48,
                  child: CircularProgressIndicator(
                    color: NavisColors.white,
                    strokeWidth: 3,
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  _label,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w600,
                    color: NavisColors.white,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
