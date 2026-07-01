import 'package:flutter/material.dart';
import 'package:vibration/vibration.dart';

import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';

class HoldToSpeakButton extends StatefulWidget {
  const HoldToSpeakButton({super.key, required this.onHeard});

  final ValueChanged<String> onHeard;

  @override
  State<HoldToSpeakButton> createState() => _HoldToSpeakButtonState();
}

class _HoldToSpeakButtonState extends State<HoldToSpeakButton> {
  bool _holding = false;

  Future<void> _onDown() async {
    if (_holding) return;
    setState(() => _holding = true);
    final ok = await VoiceCoach.instance.startListening();
    if (!ok && mounted) setState(() => _holding = false);
  }

  Future<void> _onUp() async {
    if (!_holding) return;
    final text = await VoiceCoach.instance.stopListeningAndGetText();
    if (mounted) setState(() => _holding = false);
    if (text != null && text.isNotEmpty) {
      if (await Vibration.hasVibrator()) await Vibration.vibrate(duration: 40);
      widget.onHeard(text);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<String>(
      valueListenable: VoiceCoach.instance.transcriptNotifier,
      builder: (context, transcript, _) {
        return ValueListenableBuilder<String>(
          valueListenable: VoiceCoach.instance.statusNotifier,
          builder: (context, status, _) {
            return Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: double.infinity,
                  constraints: const BoxConstraints(minHeight: 72),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: NavisColors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: _holding ? NavisColors.azure : NavisColors.borderSoft,
                      width: _holding ? 2 : 1,
                    ),
                  ),
                  child: Text(
                    transcript.isNotEmpty ? transcript : status,
                    style: TextStyle(
                      fontSize: transcript.isNotEmpty ? 22 : 16,
                      fontWeight: FontWeight.w600,
                      color: transcript.isNotEmpty ? NavisColors.azureDeep : NavisColors.textDark,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 16),
                Semantics(
                  button: true,
                  label: 'Maintenir pour parler',
                  child: GestureDetector(
                    onLongPressStart: (_) => _onDown(),
                    onLongPressEnd: (_) => _onUp(),
                    onLongPressCancel: () => _onUp(),
                    child: Container(
                      width: 180,
                      height: 180,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: _holding ? NavisColors.cardGradient : NavisColors.primaryGradient,
                        border: Border.all(color: NavisColors.white, width: 5),
                        boxShadow: NavisColors.softShadow(blur: 16, y: 6),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            _holding ? Icons.mic_rounded : Icons.mic_none_rounded,
                            color: NavisColors.white,
                            size: 48,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _holding ? 'Relachez' : 'Maintenir',
                            style: const TextStyle(
                              color: NavisColors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Gardez le doigt appuye, parlez, relachez',
                  style: TextStyle(fontSize: 14, color: NavisColors.textMuted),
                  textAlign: TextAlign.center,
                ),
              ],
            );
          },
        );
      },
    );
  }
}

class VoiceFlowScaffold extends StatelessWidget {
  const VoiceFlowScaffold({
    super.key,
    required this.title,
    required this.onHeard,
    required this.child,
    this.onBack,
  });

  final String title;
  final ValueChanged<String> onHeard;
  final Widget child;
  final VoidCallback? onBack;

  @override
  Widget build(BuildContext context) {
    final top = MediaQuery.paddingOf(context).top;
    final bottom = MediaQuery.paddingOf(context).bottom;

    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      body: Column(
        children: [
          Container(
            width: double.infinity,
            padding: EdgeInsets.fromLTRB(8, top + 8, 20, 18),
            decoration: const BoxDecoration(
              gradient: NavisColors.primaryGradient,
              borderRadius: BorderRadius.vertical(bottom: Radius.circular(24)),
            ),
            child: Row(
              children: [
                if (onBack != null)
                  IconButton(
                    onPressed: onBack,
                    icon: const Icon(Icons.arrow_back_rounded, color: NavisColors.white),
                  ),
                Expanded(
                  child: Text(title, style: const TextStyle(color: NavisColors.white, fontSize: 20, fontWeight: FontWeight.w600)),
                ),
              ],
            ),
          ),
          Expanded(
            child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: child),
          ),
          Container(
            width: double.infinity,
            padding: EdgeInsets.fromLTRB(20, 16, 20, 16 + bottom),
            color: NavisColors.white,
            child: HoldToSpeakButton(onHeard: onHeard),
          ),
        ],
      ),
    );
  }
}
