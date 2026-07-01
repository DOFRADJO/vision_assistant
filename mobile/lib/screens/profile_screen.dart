import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:in_app_review/in_app_review.dart';
import 'package:share_plus/share_plus.dart';

import '../config/app_config.dart';
import '../providers/app_providers.dart';
import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';
import '../widgets/voice_ui.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> with VoiceGuidedScreen {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final name = ref.read(localAuthProvider).currentUser?.displayName ?? '';
      announceOnLoad('Profil de $name.', actions: ['partager', 'noter l application', 'se deconnecter']);
    });
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(localAuthProvider).currentUser;

    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      appBar: AppBar(
        title: const Text('Mon profil'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => context.pop(),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: NavisColors.cardGradient,
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(user?.displayName ?? '', style: Theme.of(context).textTheme.titleLarge?.copyWith(color: NavisColors.white, fontSize: 24)),
                const SizedBox(height: 8),
                if (user?.age != null || (user?.city?.isNotEmpty ?? false))
                  Text(
                    'Age ${user?.age ?? '-'}, Ville ${user?.city ?? '-'}',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: NavisColors.white.withValues(alpha: 0.95), fontSize: 14),
                  ),
                if (user?.age != null || (user?.city?.isNotEmpty ?? false)) const SizedBox(height: 8),
                Text(
                  'Compte local, aucune donnee envoyee en ligne',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: NavisColors.white.withValues(alpha: 0.9), fontSize: 14),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          VoiceButton(
            label: 'Partager NAVIS',
            voiceHint: 'Partage de l application avec vos proches.',
            icon: Icons.share_rounded,
            onPressed: () => Share.share('NAVIS, vision assistee 100 % vocale et hors ligne : ${AppConfig.appUrl}'),
          ),
          const SizedBox(height: 12),
          VoiceButton(
            label: 'Noter l application',
            voiceHint: 'Ouverture de la note sur le store.',
            icon: Icons.star_rate_rounded,
            onPressed: () async {
              final review = InAppReview.instance;
              if (await review.isAvailable()) await review.requestReview();
            },
          ),
          const SizedBox(height: 12),
          VoiceButton(
            label: 'Confidentialite',
            voiceHint: 'Politique de confidentialite NAVIS.',
            icon: Icons.privacy_tip_rounded,
            onPressed: () => context.push('/privacy'),
          ),
          const SizedBox(height: 24),
          VoiceButton(
            label: 'Se deconnecter',
            voiceHint: 'Deconnexion de votre compte local.',
            icon: Icons.logout_rounded,
            onPressed: () async {
              await ref.read(authStateProvider.notifier).logout();
              await VoiceCoach.instance.speak('Deconnexion effectuee.');
              if (context.mounted) context.go('/welcome');
            },
          ),
        ],
      ),
    );
  }
}
