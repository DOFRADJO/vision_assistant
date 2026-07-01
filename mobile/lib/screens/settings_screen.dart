import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:share_plus/share_plus.dart';

import '../config/app_config.dart';
import '../providers/app_providers.dart';
import '../services/settings_service.dart';
import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';
import '../widgets/navis_button.dart';
import '../widgets/voice_ui.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key, this.embedded = false});

  final bool embedded;

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> with VoiceGuidedScreen {
  bool _loaded = false;
  late bool _largeText;
  late bool _haptic;
  late bool _voice;
  late bool _notifications;
  late bool _voiceNav;
  late double _rate;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final s = SettingsService.instance.current;
    setState(() {
      _largeText = s.largeText;
      _haptic = s.haptic;
      _voice = s.voiceAnnounce;
      _notifications = s.notifications;
      _voiceNav = s.voiceNavigation;
      _rate = s.speechRate;
      _loaded = true;
    });
    _syncProvider();
    if (!widget.embedded) {
      await announceOnLoad('Parametres NAVIS. Voix, partage, accessibilite.');
    }
  }

  void _syncProvider() {
    final settings = AppSettings(
      largeText: _largeText,
      haptic: _haptic,
      voiceAnnounce: _voice,
      notifications: _notifications,
      speechRate: _rate,
      voiceNavigation: _voiceNav,
    );
    ref.read(settingsProvider.notifier).update(settings);
  }

  Future<void> _shareApp() async {
    await Share.share('Essayez NAVIS, vision assistee vocale pour personnes malvoyantes : ${AppConfig.appUrl}');
    await VoiceCoach.instance.speak('Partage de l application.');
  }

  @override
  Widget build(BuildContext context) {
    if (!_loaded) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final scale = _largeText ? 1.2 : 1.0;
    return MediaQuery(
      data: MediaQuery.of(context).copyWith(textScaler: TextScaler.linear(scale)),
      child: Scaffold(
        backgroundColor: NavisColors.offWhite,
        appBar: AppBar(
          automaticallyImplyLeading: !widget.embedded,
          title: const Text('Parametres'),
        ),
        body: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            _switch('Texte agrandi', _largeText, (v) => setState(() { _largeText = v; _syncProvider(); })),
            _switch('Vibrations', _haptic, (v) => setState(() { _haptic = v; _syncProvider(); })),
            _switch('Annonces vocales', _voice, (v) => setState(() { _voice = v; _syncProvider(); })),
            _switch('Notifications', _notifications, (v) => setState(() { _notifications = v; _syncProvider(); })),
            _switch('Guide vocal des ecrans', _voiceNav, (v) => setState(() { _voiceNav = v; _syncProvider(); })),
            const SizedBox(height: 8),
            Text('Vitesse de la voix', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontSize: 16)),
            Slider(
              value: _rate,
              min: 0.2,
              max: 1.0,
              activeColor: NavisColors.azure,
              onChanged: (v) => setState(() { _rate = v; _syncProvider(); }),
            ),
            const SizedBox(height: 16),
            VoiceButton(
              label: 'Partager NAVIS',
              voiceHint: 'Partage de l application avec vos proches.',
              icon: Icons.share_rounded,
              onPressed: _shareApp,
            ),
            const SizedBox(height: 12),
            VoiceButton(
              label: 'Diagnostic voix',
              voiceHint: 'Test du micro et de la voix.',
              icon: Icons.hearing_rounded,
              onPressed: () => context.push('/voice-diagnostic'),
            ),
            if (!widget.embedded) ...[
              const SizedBox(height: 12),
              VoiceButton(
                label: 'Tester la voix',
                voiceHint: 'Bonjour, je suis NAVIS, votre assistant de vision.',
                variant: NavisButtonVariant.outline,
                onPressed: () => VoiceCoach.instance.speak('Bonjour, je suis NAVIS, votre assistant de vision.'),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _switch(String title, bool value, ValueChanged<bool> onChanged) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: NavisColors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: NavisColors.borderSoft),
      ),
      child: SwitchListTile(
        title: Text(title),
        value: value,
        activeTrackColor: NavisColors.azure,
        onChanged: onChanged,
      ),
    );
  }
}
