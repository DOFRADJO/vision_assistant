import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/app_providers.dart';
import '../screens/demo_screen.dart';
import '../screens/notifications_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/voice_diagnostic_screen.dart';
import '../services/app_voice_guide.dart';
import '../services/voice_command_service.dart';
import '../services/voice_coach.dart';
import '../services/yolo_detector.dart';
import '../theme/navis_theme.dart';
import '../widgets/navis_button.dart';
import '../widgets/navis_card.dart';
import '../widgets/navis_logo.dart';
import '../widgets/voice_ui.dart';
import '../widgets/wave_header.dart';
import 'camera_screen.dart';
import 'classes_screen.dart';
import 'history_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> with VoiceGuidedScreen {
  int _tab = 0;
  List<String> _classNames = [];
  bool _modelReady = false;
  bool _voiceBusy = false;
  bool _continuousListening = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  Future<void> _bootstrap() async {
    try {
      final jsonStr = await rootBundle.loadString('assets/config/navis_labels.json');
      final data = json.decode(jsonStr) as Map<String, dynamic>;
      await YoloDetector.instance.init();
      if (!mounted) return;
      setState(() {
        _classNames = (data['names'] as List).cast<String>();
        _modelReady = YoloDetector.instance.isReady;
      });
      final user = ref.read(localAuthProvider).currentUser?.displayName ?? 'utilisateur';
      await announceOnLoad(
        'Accueil NAVIS. Bonjour $user. Menu en bas : Accueil, Historique, Objets, Reglages. '
        'Boutons Camera et Demo video au centre.',
      );
    } catch (_) {
      if (mounted) setState(() => _modelReady = false);
    }
  }

  Future<void> _openDemo() async {
    await AppVoiceGuide.announceAction('Ouverture video demonstration.');
    if (!mounted) return;
    await Navigator.of(context).push<void>(MaterialPageRoute(builder: (_) => const DemoScreen()));
  }

  Future<void> _openCamera() async {
    await AppVoiceGuide.announceAction('Ouverture camera NAVIS.');
    if (!mounted) return;
    await Navigator.of(context).push<void>(MaterialPageRoute(builder: (_) => const CameraScreen()));
  }

  void _onTab(int i) {
    setState(() => _tab = i);
    final voice = switch (i) {
      0 => 'Accueil NAVIS.',
      1 => 'Historique de vos detections.',
      2 => 'Liste des objets reconnus par NAVIS.',
      3 => 'Parametres, voix, partage et accessibilite.',
      _ => '',
    };
    if (voice.isNotEmpty) AppVoiceGuide.announceAction(voice);
  }

  Future<void> _listenCommand() async {
    if (_voiceBusy) return;
    setState(() => _voiceBusy = true);
    try {
      await VoiceCoach.instance.speak(
        'Commande vocale. Dites une action comme ouvrir camera, ouvrir demo, historique, objets, reglages, notifications ou profil.',
      );
      final result = await VoiceCommandService.instance.listenForAction();
      await _executeCommand(result.action);
    } finally {
      if (mounted) setState(() => _voiceBusy = false);
    }
  }

  Future<void> _toggleContinuousListening() async {
    if (_continuousListening) {
      setState(() => _continuousListening = false);
      await VoiceCoach.instance.speak('Mode mains libres arrete.');
      return;
    }

    setState(() => _continuousListening = true);
    await VoiceCoach.instance.speak(
      'Mode mains libres actif. Dites une commande, ou dites arrete ecoute pour quitter.',
    );
    unawaited(_continuousLoop());
  }

  Future<void> _continuousLoop() async {
    while (mounted && _continuousListening) {
      if (_voiceBusy) {
        await Future<void>.delayed(const Duration(milliseconds: 250));
        continue;
      }

      setState(() => _voiceBusy = true);
      try {
        final result = await VoiceCommandService.instance.listenForAction(listenSeconds: 5);
        if (!_continuousListening || !mounted) return;
        if (result.action == NavisVoiceAction.stopListening) {
          setState(() => _continuousListening = false);
          await VoiceCoach.instance.speak('Mode mains libres desactive.');
          return;
        }
        await _executeCommand(result.action);
      } finally {
        if (mounted) setState(() => _voiceBusy = false);
      }

      await Future<void>.delayed(const Duration(milliseconds: 350));
    }
  }

  Future<void> _executeCommand(NavisVoiceAction action) async {
    switch (action) {
      case NavisVoiceAction.openCamera:
        if (_modelReady) {
          await _openCamera();
        } else {
          await VoiceCoach.instance.speak('Le modele est encore en chargement.');
        }
        return;
      case NavisVoiceAction.openDemo:
        if (_modelReady) {
          await _openDemo();
        } else {
          await VoiceCoach.instance.speak('Le modele est encore en chargement.');
        }
        return;
      case NavisVoiceAction.openHistory:
        _onTab(1);
        return;
      case NavisVoiceAction.openObjects:
        _onTab(2);
        return;
      case NavisVoiceAction.openSettings:
        _onTab(3);
        return;
      case NavisVoiceAction.openNotifications:
        if (!mounted) return;
        await Navigator.of(context).push(MaterialPageRoute(builder: (_) => const NotificationsScreen()));
        return;
      case NavisVoiceAction.openProfile:
        if (!mounted) return;
        await Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ProfileScreen()));
        return;
      case NavisVoiceAction.goHome:
        _onTab(0);
        return;
      case NavisVoiceAction.stopSession:
      case NavisVoiceAction.recordScene:
      case NavisVoiceAction.stopListening:
      case NavisVoiceAction.unknown:
        await VoiceCoach.instance.speak('Commande non reconnue. Reessayez.');
        return;
    }
  }

  @override
  Widget build(BuildContext context) {
    final topPad = MediaQuery.paddingOf(context).top;
    final userName = ref.watch(localAuthProvider).currentUser?.displayName ?? '';

    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      body: IndexedStack(
        index: _tab,
        children: [
          _buildAccueil(context, topPad, userName),
          const HistoryScreen(embedded: true),
          ClassesScreen(classNames: _classNames, embedded: true),
          const SettingsScreen(embedded: true),
        ],
      ),
      floatingActionButton: GestureDetector(
        onLongPress: _toggleContinuousListening,
        child: FloatingActionButton.extended(
          onPressed: _listenCommand,
          backgroundColor: NavisColors.azure,
          icon: Icon(
            _voiceBusy
                ? Icons.mic_off_rounded
                : (_continuousListening ? Icons.hearing_rounded : Icons.mic_rounded),
            color: NavisColors.white,
          ),
          label: Text(_voiceBusy ? 'Ecoute...' : (_continuousListening ? 'Mains libres' : 'Commande vocale')),
          tooltip: 'Appui long pour mains libres',
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: _onTab,
        backgroundColor: NavisColors.white,
        indicatorColor: NavisColors.azure.withValues(alpha: 0.15),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_rounded), label: 'Accueil'),
          NavigationDestination(icon: Icon(Icons.history_rounded), label: 'Historique'),
          NavigationDestination(icon: Icon(Icons.category_rounded), label: 'Objets'),
          NavigationDestination(icon: Icon(Icons.settings_rounded), label: 'Reglages'),
        ],
      ),
    );
  }

  Widget _buildAccueil(BuildContext context, double topPad, String userName) {
    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(
          child: WaveHeader(
            height: 200 + topPad,
            child: Padding(
              padding: EdgeInsets.fromLTRB(24, topPad + 12, 24, 0),
              child: Row(
                children: [
                  const NavisLogo(size: 48, showShadow: false),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Bonjour $userName', style: const TextStyle(color: NavisColors.white, fontSize: 22, fontWeight: FontWeight.w700)),
                        Text('Vision assistee vocale', style: TextStyle(color: NavisColors.white.withValues(alpha: 0.9), fontSize: 13)),
                      ],
                    ),
                  ),
                  IconButton(
                    tooltip: 'Notifications',
                    onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const NotificationsScreen()),
                    ),
                    icon: const Icon(Icons.notifications_rounded, color: NavisColors.white),
                  ),
                  IconButton(
                    tooltip: 'Profil',
                    onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const ProfileScreen()),
                    ),
                    icon: const Icon(Icons.person_rounded, color: NavisColors.white),
                  ),
                ],
              ),
            ),
          ),
        ),
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
          sliver: SliverList(
            delegate: SliverChildListDelegate([
              Transform.translate(
                offset: const Offset(0, -28),
                child: NavisGradientCard(
                  title: _modelReady ? 'Detection en direct' : 'Chargement...',
                  subtitle: 'Personnes, vehicules, dangers, distances',
                  trailing: const Icon(Icons.visibility_rounded, color: NavisColors.white),
                  child: Row(
                    children: [
                      Expanded(
                        child: NavisButton(
                          label: 'Camera',
                          icon: Icons.videocam_rounded,
                          variant: NavisButtonVariant.onDark,
                          onPressed: _modelReady ? _openCamera : null,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: NavisButton(
                          label: 'Demo video',
                          icon: Icons.play_circle_rounded,
                          variant: NavisButtonVariant.onDark,
                          onPressed: _modelReady ? _openDemo : null,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: NavisColors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: NavisColors.borderSoft),
                ),
                child: Text(
                  'NAVIS estime le nombre de personnes, detecte les vehicules, signale les dangers '
                  'et annonce les approches avec position et distance estimee.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.5),
                ),
              ),
              const SizedBox(height: 12),
              NavisTile(
                icon: Icons.notifications_active_rounded,
                title: 'Alertes recentes',
                subtitle: 'Consulter les alertes detectees par NAVIS',
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const NotificationsScreen()),
                ),
              ),
              const SizedBox(height: 10),
              NavisTile(
                icon: Icons.person_pin_circle_rounded,
                title: 'Mon profil',
                subtitle: 'Partager l application, noter NAVIS, deconnexion',
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const ProfileScreen()),
                ),
              ),
              const SizedBox(height: 10),
              NavisTile(
                icon: Icons.support_agent_rounded,
                title: 'Aide rapide',
                subtitle: 'Conseils pour detection, voix et navigation',
                onTap: () => AppVoiceGuide.announceAction(
                  'Pour une meilleure detection, placez la camera devant vous avec bonne lumiere.',
                ),
              ),
              const SizedBox(height: 10),
              NavisTile(
                icon: Icons.hearing_rounded,
                title: 'Diagnostic voix',
                subtitle: 'Verifier micro, reconnaissance vocale et synthese',
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const VoiceDiagnosticScreen()),
                ),
              ),
            ]),
          ),
        ),
      ],
    );
  }
}
