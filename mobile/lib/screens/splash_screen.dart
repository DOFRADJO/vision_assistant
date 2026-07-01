import 'package:flutter/material.dart';
import '../theme/navis_theme.dart';
import '../widgets/navis_button.dart';
import '../widgets/navis_logo.dart';
import '../widgets/wave_header.dart';
import 'home_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  bool _visible = false;

  @override
  void initState() {
    super.initState();
    Future<void>.delayed(const Duration(milliseconds: 120), () {
      if (mounted) setState(() => _visible = true);
    });
  }

  void _goHome() {
    Navigator.of(context).pushReplacement(
      PageRouteBuilder<void>(
        pageBuilder: (context, animation, secondaryAnimation) => const HomeScreen(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(opacity: animation, child: child);
        },
        transitionDuration: const Duration(milliseconds: 450),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NavisColors.white,
      body: Stack(
        children: [
          WaveHeader(
            height: MediaQuery.sizeOf(context).height * 0.58,
            child: SafeArea(
              child: AnimatedOpacity(
                opacity: _visible ? 1 : 0,
                duration: const Duration(milliseconds: 700),
                curve: Curves.easeOut,
                child: Center(
                  child: Padding(
                    padding: const EdgeInsets.only(bottom: 48),
                    child: NavisLogoWithTitle(logoSize: 108, animated: false),
                  ),
                ),
              ),
            ),
          ),
          Align(
            alignment: Alignment.bottomCenter,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(28, 0, 28, 32),
                child: AnimatedSlide(
                  offset: _visible ? Offset.zero : const Offset(0, 0.15),
                  duration: const Duration(milliseconds: 700),
                  curve: Curves.easeOutCubic,
                  child: AnimatedOpacity(
                    opacity: _visible ? 1 : 0,
                    duration: const Duration(milliseconds: 700),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Comprenez votre environnement\ngrace a la vision assistee',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                color: NavisColors.textDark,
                                fontSize: 15,
                                height: 1.5,
                              ),
                        ),
                        const SizedBox(height: 28),
                        NavisButton(
                          label: 'Commencer',
                          icon: Icons.arrow_forward_rounded,
                          onPressed: _goHome,
                          semanticsLabel: 'Commencer l application NAVIS',
                        ),
                        const SizedBox(height: 14),
                        NavisButton(
                          label: 'En savoir plus',
                          variant: NavisButtonVariant.outline,
                          onPressed: _goHome,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
