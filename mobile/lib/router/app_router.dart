import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/app_providers.dart';
import '../screens/camera_screen.dart';
import '../screens/classes_screen.dart';
import '../screens/demo_screen.dart';
import '../screens/history_screen.dart';
import '../screens/home_screen.dart';
import '../screens/legal_screen.dart';
import '../screens/loading_screen.dart';
import '../screens/notifications_screen.dart';
import '../screens/onboarding_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/settings_screen.dart';
import '../screens/voice_help_screen.dart';
import '../screens/voice_login_screen.dart';
import '../screens/voice_signup_screen.dart';
import '../screens/welcome_screen.dart';
import '../screens/voice_diagnostic_screen.dart';
import '../services/app_voice_guide.dart';
import '../services/onboarding_service.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/loading',
    observers: [NavisVoiceObserver()],
    redirect: (context, state) async {
      if (authState.isLoading) return null;

      final loc = state.matchedLocation;
      final bootRoutes = {'/loading', '/onboarding'};
      if (bootRoutes.contains(loc)) return null;

      final loggedIn = authState.value ?? false;
      final public = {
        '/loading',
        '/onboarding',
        '/welcome',
        '/voice-signup',
        '/voice-login',
        '/privacy',
        '/terms',
      };

      if (!loggedIn && !public.contains(loc)) return '/welcome';
      if (loggedIn && (loc == '/welcome' || loc.startsWith('/voice-'))) return '/home';

      if (!loggedIn && loc == '/welcome') {
        final done = await OnboardingService.isDone();
        if (!done) return '/onboarding';
      }

      return null;
    },
    errorBuilder: (context, state) {
      final path = state.uri.path;
      if (path == '/demo') return const DemoScreen();
      if (path == '/camera') return const CameraScreen();
      WidgetsBinding.instance.addPostFrameCallback((_) {
        AppVoiceGuide.announceError('Page introuvable. Retour a l accueil.');
        context.go('/home');
      });
      return const LoadingScreen();
    },
    routes: [
      GoRoute(path: '/loading', name: 'loading', builder: (context, state) => const LoadingScreen()),
      GoRoute(path: '/onboarding', name: 'onboarding', builder: (context, state) => const OnboardingScreen()),
      GoRoute(path: '/welcome', name: 'welcome', builder: (context, state) => const WelcomeScreen()),
      GoRoute(path: '/voice-signup', name: 'voice-signup', builder: (context, state) => const VoiceSignupScreen()),
      GoRoute(path: '/voice-login', name: 'voice-login', builder: (context, state) => const VoiceLoginScreen()),
      GoRoute(path: '/home', name: 'home', builder: (context, state) => const HomeScreen()),
      GoRoute(path: '/camera', name: 'camera', builder: (context, state) => const CameraScreen()),
      GoRoute(path: '/demo', name: 'demo', builder: (context, state) => const DemoScreen()),
      GoRoute(
        path: '/classes',
        name: 'classes',
        builder: (context, state) => ClassesScreen(classNames: (state.extra as List<String>?) ?? []),
      ),
      GoRoute(path: '/history', name: 'history', builder: (context, state) => const HistoryScreen()),
      GoRoute(path: '/profile', name: 'profile', builder: (context, state) => const ProfileScreen()),
      GoRoute(path: '/settings', name: 'settings', builder: (context, state) => const SettingsScreen()),
      GoRoute(path: '/notifications', name: 'notifications', builder: (context, state) => const NotificationsScreen()),
      GoRoute(path: '/help', name: 'help', builder: (context, state) => const VoiceHelpScreen()),
      GoRoute(path: '/voice-diagnostic', name: 'voice-diagnostic', builder: (context, state) => const VoiceDiagnosticScreen()),
      GoRoute(path: '/privacy', name: 'privacy', builder: (context, state) => const PrivacyScreen()),
      GoRoute(path: '/terms', name: 'terms', builder: (context, state) => const TermsScreen()),
    ],
  );
});
