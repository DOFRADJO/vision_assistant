import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/app_providers.dart';
import '../services/local_auth_service.dart';
import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';
import '../widgets/hold_to_speak_button.dart';
import '../widgets/navis_button.dart';
import '../widgets/navis_card.dart';

enum _Step { name, confirmName, age, city, pin, confirmPin }

class VoiceSignupScreen extends ConsumerStatefulWidget {
  const VoiceSignupScreen({super.key});

  @override
  ConsumerState<VoiceSignupScreen> createState() => _VoiceSignupScreenState();
}

class _VoiceSignupScreenState extends ConsumerState<VoiceSignupScreen> {
  _Step _step = _Step.name;
  String? _name;
  int? _age;
  String? _city;
  String? _pin;
  final _textCtrl = TextEditingController();

  @override
  void dispose() {
    _textCtrl.dispose();
    super.dispose();
  }

  String get _hint => switch (_step) {
        _Step.name => 'Prenom (voix ou clavier)',
        _Step.confirmName => 'Dites oui ou non',
        _Step.age => 'Votre age',
        _Step.city => 'Votre ville',
        _Step.pin => 'Code 4 chiffres',
        _Step.confirmPin => 'Repetez le code',
      };

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await VoiceCoach.instance.init();
      await VoiceCoach.instance.speak(
        'Dites votre prenom en maintenant le bouton micro, ou tapez le au clavier. '
        'La voix fonctionne hors ligne si le pack francais est installe dans Google.',
      );
    });
  }

  Future<void> _process(String text) async {
    if (_step == _Step.name) {
      _name = text;
      setState(() => _step = _Step.confirmName);
      await VoiceCoach.instance.speak('Vous avez dit $text. Dites oui pour confirmer.');
      return;
    }
    if (_step == _Step.confirmName) {
      final n = text.toLowerCase();
      if (n.contains('oui') || n.contains('ok')) {
        setState(() => _step = _Step.age);
        await VoiceCoach.instance.speak('Quel est votre age ?');
      } else {
        setState(() => _step = _Step.name);
        await VoiceCoach.instance.speak('Redites votre prenom.');
      }
      return;
    }
    if (_step == _Step.age) {
      final digits = RegExp(r'\d+').firstMatch(text)?.group(0);
      final age = int.tryParse(digits ?? text.trim());
      if (age == null || age < 5 || age > 120) {
        await VoiceCoach.instance.speak('Age invalide. Dites un nombre entre 5 et 120.');
        return;
      }
      _age = age;
      setState(() => _step = _Step.city);
      await VoiceCoach.instance.speak('Quelle est votre ville ?');
      return;
    }
    if (_step == _Step.city) {
      final city = text.trim();
      if (city.length < 2) {
        await VoiceCoach.instance.speak('Ville invalide. Reessayez.');
        return;
      }
      _city = city;
      setState(() => _step = _Step.pin);
      await VoiceCoach.instance.speak('Choisissez 4 chiffres.');
      return;
    }
    if (_step == _Step.pin) {
      final pin = VoiceCoach.instance.parsePin(text) ?? (text.length == 4 && int.tryParse(text) != null ? text : null);
      if (pin == null) {
        await VoiceCoach.instance.speak('4 chiffres requis.');
        return;
      }
      _pin = pin;
      setState(() => _step = _Step.confirmPin);
      await VoiceCoach.instance.speak('Repetez le code.');
      return;
    }
    if (_step == _Step.confirmPin) {
      final pin2 = VoiceCoach.instance.parsePin(text) ?? text;
      if (pin2 != _pin) {
        setState(() => _step = _Step.pin);
        await VoiceCoach.instance.speak('Code different. Recommencez.');
        return;
      }
      try {
        await ref.read(authStateProvider.notifier).registerVoice(_name!, _pin!, age: _age, city: _city);
        await VoiceCoach.instance.speak('Compte cree.');
        if (mounted) context.go('/home');
      } on AuthException catch (e) {
        setState(() => _step = _Step.name);
        await VoiceCoach.instance.speak(e.message);
      }
    }
  }

  void _submitKeyboard() {
    final t = _textCtrl.text.trim();
    _textCtrl.clear();
    if (t.isNotEmpty) _process(t);
  }

  @override
  Widget build(BuildContext context) {
    return VoiceFlowScaffold(
      title: 'Creer un compte',
      onBack: () => context.pop(),
      onHeard: _process,
      child: Column(
        children: [
          NavisGradientCard(title: 'Etape ${_step.index + 1}/6', subtitle: _hint, trailing: const Icon(Icons.mic, color: NavisColors.white)),
          const SizedBox(height: 20),
          TextField(
            controller: _textCtrl,
            keyboardType: _step == _Step.age
                ? TextInputType.number
                : (_step == _Step.pin || _step == _Step.confirmPin ? TextInputType.number : TextInputType.text),
            obscureText: _step == _Step.pin || _step == _Step.confirmPin,
            style: const TextStyle(fontSize: 20),
            decoration: InputDecoration(
              hintText: _hint,
              filled: true,
              fillColor: NavisColors.white,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
            ),
            onSubmitted: (_) => _submitKeyboard(),
          ),
          const SizedBox(height: 12),
          NavisButton(label: 'Valider au clavier', variant: NavisButtonVariant.secondary, onPressed: _submitKeyboard),
        ],
      ),
    );
  }
}
