import 'package:flutter/material.dart';
import '../theme/navis_theme.dart';

enum NavisButtonVariant { primary, secondary, outline, onDark }

class NavisButton extends StatelessWidget {
  const NavisButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = NavisButtonVariant.primary,
    this.icon,
    this.semanticsLabel,
    this.expand = true,
  });

  final String label;
  final VoidCallback? onPressed;
  final NavisButtonVariant variant;
  final IconData? icon;
  final String? semanticsLabel;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final child = Semantics(
      button: true,
      label: semanticsLabel ?? label,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(28),
          child: Ink(
            height: 56,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(28),
              gradient: variant == NavisButtonVariant.primary
                  ? NavisColors.primaryGradient
                  : null,
              color: variant == NavisButtonVariant.secondary
                  ? NavisColors.white
                  : variant == NavisButtonVariant.onDark
                      ? NavisColors.white.withValues(alpha: 0.15)
                      : null,
              border: variant == NavisButtonVariant.outline
                  ? Border.all(color: NavisColors.azure, width: 2)
                  : variant == NavisButtonVariant.onDark
                      ? Border.all(color: NavisColors.white, width: 2)
                      : null,
              boxShadow: variant != NavisButtonVariant.outline && variant != NavisButtonVariant.onDark
                  ? NavisColors.softShadow(blur: 16, y: 6)
                  : null,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: expand ? MainAxisSize.max : MainAxisSize.min,
              children: [
                if (icon != null) ...[
                  Icon(
                    icon,
                    color: _foreground,
                    size: 22,
                  ),
                  const SizedBox(width: 10),
                ],
                Text(
                  label,
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: _foreground,
                      ),
                ),
              ],
            ),
          ),
        ),
      ),
    );

    return expand ? SizedBox(width: double.infinity, child: child) : child;
  }

  Color get _foreground {
    switch (variant) {
      case NavisButtonVariant.primary:
        return NavisColors.white;
      case NavisButtonVariant.secondary:
        return NavisColors.azure;
      case NavisButtonVariant.outline:
        return NavisColors.azure;
      case NavisButtonVariant.onDark:
        return NavisColors.white;
    }
  }
}
