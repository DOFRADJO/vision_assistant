import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../services/onboarding_service.dart';
import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';
import '../widgets/navis_button.dart';
import '../widgets/navis_logo.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _page = PageController();
  int _index = 0;

  static const _steps = [
    _OnboardStep(
      icon: Icons.visibility_outlined,
      title: 'Comprenez votre environnement',
      body:
          'NAVIS utilise la camera de votre telephone pour observer la scene en temps reel et vous la decrire a voix haute en francais.',
    ),
    _OnboardStep(
      icon: Icons.directions_walk_rounded,
      title: 'Detection et orientation',
      body:
          'L application repere les personnes, vehicules, bus, objets du quotidien et signaux de danger. '
          'Elle indique la position, gauche, devant, droite, et estime la distance.',
    ),
    _OnboardStep(
      icon: Icons.warning_amber_rounded,
      title: 'Alertes et securite',
      body:
          'NAVIS compte les personnes autour de vous, detecte les approches de vehicules et signale les situations a risque '
          'comme un stop ou un feu tricolore. Tout fonctionne hors ligne sur votre appareil.',
    ),
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await VoiceCoach.instance.speak(_steps[0].voiceText);
    });
  }

  Future<void> _next() async {
    if (_index < _steps.length - 1) {
      setState(() => _index++);
      await _page.nextPage(duration: const Duration(milliseconds: 350), curve: Curves.easeOut);
      await VoiceCoach.instance.speak(_steps[_index].voiceText);
      return;
    }
    await OnboardingService.markDone();
    if (mounted) context.go('/welcome');
  }

  @override
  void dispose() {
    _page.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
              child: Row(
                children: [
                  const NavisLogo(size: 44, animated: false, showShadow: false),
                  const Spacer(),
                  Text('${_index + 1} / ${_steps.length}', style: const TextStyle(fontWeight: FontWeight.w600)),
                ],
              ),
            ),
            Expanded(
              child: PageView.builder(
                controller: _page,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _steps.length,
                onPageChanged: (i) => setState(() => _index = i),
                itemBuilder: (context, i) {
                  final s = _steps[i];
                  return Padding(
                    padding: const EdgeInsets.all(28),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 88,
                          height: 88,
                          decoration: BoxDecoration(
                            gradient: NavisColors.primaryGradient,
                            borderRadius: BorderRadius.circular(24),
                          ),
                          child: Icon(s.icon, color: NavisColors.white, size: 44),
                        ),
                        const SizedBox(height: 28),
                        Text(s.title, textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall),
                        const SizedBox(height: 16),
                        Text(
                          s.body,
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.55, color: NavisColors.textDark),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(28, 0, 28, 28),
              child: NavisButton(
                label: _index < _steps.length - 1 ? 'Continuer' : 'Commencer',
                icon: Icons.arrow_forward_rounded,
                onPressed: _next,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _OnboardStep {
  const _OnboardStep({required this.icon, required this.title, required this.body});

  final IconData icon;
  final String title;
  final String body;

  String get voiceText => '$title. $body';
}
