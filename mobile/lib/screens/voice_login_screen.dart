import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/app_providers.dart';
import '../services/local_auth_service.dart';
import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';
import '../widgets/hold_to_speak_button.dart';
import '../widgets/navis_card.dart';

class VoiceLoginScreen extends ConsumerStatefulWidget {
  const VoiceLoginScreen({super.key});

  @override
  ConsumerState<VoiceLoginScreen> createState() => _VoiceLoginScreenState();
}

class _VoiceLoginScreenState extends ConsumerState<VoiceLoginScreen> {
  bool _needPin = false;
  String? _name;
  final _textCtrl = TextEditingController();

  @override
  void dispose() {
    _textCtrl.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await VoiceCoach.instance.init();
      await VoiceCoach.instance.speak('Dites votre prenom ou tapez au clavier.');
    });
  }

  Future<void> _process(String text) async {
    if (!_needPin) {
      _name = text;
      setState(() => _needPin = true);
      await VoiceCoach.instance.speak('Maintenant votre code a 4 chiffres.');
      return;
    }
    final pin = VoiceCoach.instance.parsePin(text) ?? text;
    try {
      await ref.read(authStateProvider.notifier).loginVoice(_name!, pin);
      await VoiceCoach.instance.speak('Connecte.');
      if (mounted) context.go('/home');
    } on AuthException catch (e) {
      setState(() => _needPin = false);
      await VoiceCoach.instance.speak(e.message);
    }
  }

  @override
  Widget build(BuildContext context) {
    return VoiceFlowScaffold(
      title: 'Connexion',
      onBack: () => context.pop(),
      onHeard: _process,
      child: Column(
        children: [
          NavisGradientCard(
            title: _needPin ? 'Code secret' : 'Prenom',
            subtitle: 'Voix ou clavier',
            trailing: const Icon(Icons.lock, color: NavisColors.white),
          ),
          const SizedBox(height: 20),
          TextField(
            controller: _textCtrl,
            obscureText: _needPin,
            keyboardType: _needPin ? TextInputType.number : TextInputType.text,
            style: const TextStyle(fontSize: 20),
            decoration: InputDecoration(
              filled: true,
              fillColor: NavisColors.white,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
            ),
            onSubmitted: (v) {
              if (v.trim().isNotEmpty) _process(v.trim());
              _textCtrl.clear();
            },
          ),
        ],
      ),
    );
  }
}
