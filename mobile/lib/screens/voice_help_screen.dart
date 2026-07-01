import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';
import '../widgets/voice_ui.dart';

class VoiceHelpScreen extends StatefulWidget {
  const VoiceHelpScreen({super.key});

  @override
  State<VoiceHelpScreen> createState() => _VoiceHelpScreenState();
}

class _VoiceHelpScreenState extends State<VoiceHelpScreen> with VoiceGuidedScreen {
  @override
  void initState() {
    super.initState();
    announceOnLoad(
      'Aide NAVIS.',
      actions: ['comment utiliser la camera', 'comment se deconnecter', 'confidentialite'],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      appBar: AppBar(
        title: const Text('Aide vocale'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => context.pop(),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          VoiceButton(
            label: 'Utiliser la camera',
            voiceHint: 'Ouvrez la camera depuis l accueil. NAVIS detecte les objets et les annonce a voix haute. '
                'Vous pouvez marcher en ecoutant les alertes.',
            icon: Icons.videocam_rounded,
            onPressed: () => VoiceCoach.instance.speak(
              'Depuis l accueil, touchez Ouvrir la camera. NAVIS analyse l image et parle.',
            ),
          ),
          const SizedBox(height: 12),
          VoiceButton(
            label: 'Mon compte local',
            voiceHint: 'Votre compte est stocke uniquement sur ce telephone. Aucun email, aucun serveur.',
            icon: Icons.phone_android_rounded,
            onPressed: () => VoiceCoach.instance.speak(
              'Votre prenom et code secret sont enregistres localement sur cet appareil.',
            ),
          ),
          const SizedBox(height: 12),
          VoiceButton(
            label: 'Confidentialite',
            voiceHint: 'Vos images ne quittent jamais le telephone.',
            icon: Icons.shield_rounded,
            onPressed: () => context.push('/privacy'),
          ),
        ],
      ),
    );
  }
}
