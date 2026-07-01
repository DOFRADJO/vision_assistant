import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';
import '../widgets/navis_button.dart';
import '../widgets/navis_logo.dart';
import '../widgets/wave_header.dart';

class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await VoiceCoach.instance.speak(
        'Bienvenue sur NAVIS. Application de vision assistee pour personnes malvoyantes. '
        'Creez un compte ou connectez vous.',
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final h = MediaQuery.sizeOf(context).height;
    return Scaffold(
      backgroundColor: NavisColors.white,
      body: Stack(
        children: [
          WaveHeader(
            height: h * 0.52,
            child: SafeArea(
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 40),
                  child: NavisLogoWithTitle(logoSize: 96, animated: false),
                ),
              ),
            ),
          ),
          Align(
            alignment: Alignment.bottomCenter,
            child: SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(28, 0, 28, 28),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: NavisColors.white,
                        borderRadius: BorderRadius.circular(22),
                        border: Border.all(color: NavisColors.borderSoft),
                        boxShadow: NavisColors.cardShadow,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Votre environnement, explique a voix haute',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            'NAVIS analyse la camera en temps reel pour detecter personnes, vehicules, '
                            'objets du quotidien et dangers. Elle vous oriente, gauche, devant, droite, '
                            'et estime les distances. Fonctionne 100 % hors ligne.',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.5, color: NavisColors.textDark),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),
                    NavisButton(
                      label: 'Creer un compte',
                      icon: Icons.person_add_rounded,
                      onPressed: () => context.push('/voice-signup'),
                    ),
                    const SizedBox(height: 12),
                    NavisButton(
                      label: 'Me connecter',
                      variant: NavisButtonVariant.outline,
                      icon: Icons.login_rounded,
                      onPressed: () => context.push('/voice-login'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
