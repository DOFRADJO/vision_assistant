import 'package:flutter/material.dart';
import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';
import 'navis_button.dart';

mixin VoiceGuidedScreen<T extends StatefulWidget> on State<T> {
  Future<void> announceOnLoad(String title, {List<String> actions = const []}) async {
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) return;
      await VoiceCoach.instance.announceScreen(title, actions: actions);
    });
  }
}

/// Bouton premium NAVIS + annonce vocale au toucher.
class VoiceButton extends StatelessWidget {
  const VoiceButton({
    super.key,
    required this.label,
    required this.voiceHint,
    required this.onPressed,
    this.icon,
    this.subtitle,
    this.variant = NavisButtonVariant.primary,
  });

  final String label;
  final String voiceHint;
  final VoidCallback? onPressed;
  final IconData? icon;
  final String? subtitle;
  final NavisButtonVariant variant;

  Future<void> _tap() async {
    await VoiceCoach.instance.speak(voiceHint);
    onPressed?.call();
  }

  @override
  Widget build(BuildContext context) {
    if (subtitle != null) {
      return Semantics(
        button: true,
        label: '$label. $voiceHint',
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onPressed == null ? null : _tap,
            borderRadius: BorderRadius.circular(24),
            child: Ink(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 18),
              decoration: BoxDecoration(
                gradient: NavisColors.primaryGradient,
                borderRadius: BorderRadius.circular(24),
                boxShadow: NavisColors.softShadow(blur: 20, y: 8),
              ),
              child: Row(
                children: [
                  if (icon != null) ...[
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: NavisColors.white.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Icon(icon, color: NavisColors.white, size: 26),
                    ),
                    const SizedBox(width: 16),
                  ],
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(label, style: const TextStyle(color: NavisColors.white, fontSize: 18, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 4),
                        Text(subtitle!, style: TextStyle(color: NavisColors.white.withValues(alpha: 0.88), fontSize: 13)),
                      ],
                    ),
                  ),
                  const Icon(Icons.chevron_right_rounded, color: NavisColors.white),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return NavisButton(
      label: label,
      icon: icon,
      variant: variant,
      semanticsLabel: '$label. $voiceHint',
      onPressed: onPressed == null ? null : _tap,
    );
  }
}

/// Indicateur micro anime pendant l ecoute.
class ListeningIndicator extends StatefulWidget {
  const ListeningIndicator({super.key, required this.active});

  final bool active;

  @override
  State<ListeningIndicator> createState() => _ListeningIndicatorState();
}

class _ListeningIndicatorState extends State<ListeningIndicator> with SingleTickerProviderStateMixin {
  late final AnimationController _pulse;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _pulse,
      builder: (context, child) {
        final scale = widget.active ? 1.0 + _pulse.value * 0.12 : 1.0;
        return Transform.scale(
          scale: scale,
          child: Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: NavisColors.primaryGradient,
              boxShadow: widget.active
                  ? NavisColors.softShadow(blur: 32 + _pulse.value * 20, y: 12)
                  : NavisColors.softShadow(blur: 16, y: 6),
            ),
            child: Icon(
              widget.active ? Icons.mic_rounded : Icons.hearing_rounded,
              color: NavisColors.white,
              size: 52,
            ),
          ),
        );
      },
    );
  }
}
