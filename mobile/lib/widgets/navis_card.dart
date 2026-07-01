import 'package:flutter/material.dart';
import '../theme/navis_theme.dart';

class NavisGradientCard extends StatelessWidget {
  const NavisGradientCard({
    super.key,
    required this.title,
    required this.subtitle,
    this.trailing,
    this.child,
  });

  final String title;
  final String subtitle;
  final Widget? trailing;
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: NavisColors.cardGradient,
        borderRadius: BorderRadius.circular(28),
        boxShadow: NavisColors.softShadow(blur: 28, y: 12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: NavisColors.white,
                          ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: NavisColors.white.withValues(alpha: 0.88),
                            fontSize: 14,
                          ),
                    ),
                  ],
                ),
              ),
              if (trailing != null) trailing!,
            ],
          ),
          if (child case final extra?) ...[
            const SizedBox(height: 20),
            extra,
          ],
        ],
      ),
    );
  }
}

class NavisTile extends StatelessWidget {
  const NavisTile({
    super.key,
    required this.icon,
    required this.title,
    this.subtitle,
    this.onTap,
    this.trailingIcon = Icons.chevron_right_rounded,
  });

  final IconData icon;
  final String title;
  final String? subtitle;
  final VoidCallback? onTap;
  final IconData trailingIcon;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: onTap != null,
      label: subtitle != null ? '$title. $subtitle' : title,
      child: Material(
        color: NavisColors.white,
        borderRadius: BorderRadius.circular(22),
        elevation: 0,
        shadowColor: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(22),
          child: Ink(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(22),
              border: Border.all(color: NavisColors.borderSoft),
              boxShadow: NavisColors.cardShadow,
            ),
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    gradient: NavisColors.primaryGradient,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(icon, color: NavisColors.white, size: 24),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontSize: 16)),
                      if (subtitle != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          subtitle!,
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontSize: 13),
                        ),
                      ],
                    ],
                  ),
                ),
                Icon(trailingIcon, color: NavisColors.textMuted),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
