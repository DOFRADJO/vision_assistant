import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../theme/navis_theme.dart';

/// Logo NAVIS : carre arrondi blanc, N stylise + oeil (vision assistee).
class NavisLogo extends StatelessWidget {
  const NavisLogo({
    super.key,
    this.size = 96,
    this.showShadow = true,
    this.animated = false,
  });

  final double size;
  final bool showShadow;
  final bool animated;

  @override
  Widget build(BuildContext context) {
    final tile = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: NavisColors.white,
        borderRadius: BorderRadius.circular(size * 0.28),
        boxShadow: showShadow ? NavisColors.softShadow(blur: size * 0.28, y: size * 0.12) : null,
      ),
      child: Padding(
        padding: EdgeInsets.all(size * 0.18),
        child: CustomPaint(
          painter: _NavisMarkPainter(),
        ),
      ),
    );

    if (!animated) return tile;

    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.85, end: 1),
      duration: const Duration(milliseconds: 900),
      curve: Curves.easeOutBack,
      builder: (context, scale, child) => Transform.scale(scale: scale, child: child),
      child: tile,
    );
  }
}

class NavisLogoWithTitle extends StatelessWidget {
  const NavisLogoWithTitle({
    super.key,
    this.logoSize = 96,
    this.lightText = true,
    this.animated = true,
  });

  final double logoSize;
  final bool lightText;
  final bool animated;

  @override
  Widget build(BuildContext context) {
    final titleColor = lightText ? NavisColors.white : NavisColors.textDark;
    final subtitleColor = lightText
        ? NavisColors.white.withValues(alpha: 0.85)
        : NavisColors.textMuted;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        NavisLogo(size: logoSize, animated: animated),
        SizedBox(height: logoSize * 0.22),
        Text(
          'NAVIS',
          style: Theme.of(context).textTheme.displayLarge?.copyWith(
                color: titleColor,
                fontSize: logoSize * 0.38,
                letterSpacing: 4,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          'Vision Assistee',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: subtitleColor,
                fontSize: logoSize * 0.15,
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }
}

class _NavisMarkPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final gradient = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [NavisColors.azureLight, NavisColors.azureDeep],
      ).createShader(Rect.fromLTWH(0, 0, w, h));

    final stroke = w * 0.17;
    final cap = StrokeCap.round;
    final join = StrokeJoin.round;

    // N stylise — traits epais arrondis
    final nPath = Path()
      ..moveTo(w * 0.18, h * 0.82)
      ..lineTo(w * 0.18, h * 0.18)
      ..lineTo(w * 0.72, h * 0.82)
      ..lineTo(w * 0.72, h * 0.18);

    canvas.drawPath(
      nPath,
      Paint()
        ..shader = gradient.shader
        ..style = PaintingStyle.stroke
        ..strokeWidth = stroke
        ..strokeCap = cap
        ..strokeJoin = join,
    );

    // Oeil : arc + pupille (theme vision)
    final eyeCenter = Offset(w * 0.78, h * 0.38);
    final eyeRx = w * 0.22;
    final eyeRy = h * 0.14;

    canvas.drawOval(
      Rect.fromCenter(center: eyeCenter, width: eyeRx * 2, height: eyeRy * 2),
      Paint()
        ..shader = gradient.shader
        ..style = PaintingStyle.stroke
        ..strokeWidth = stroke * 0.65,
    );

    canvas.drawCircle(
      eyeCenter + Offset(eyeRx * 0.15, 0),
      w * 0.055,
      Paint()..color = NavisColors.azureDeep,
    );

    // Reflet lumineux sur l'oeil
    canvas.drawCircle(
      eyeCenter + Offset(-eyeRx * 0.25, -eyeRy * 0.35),
      w * 0.028,
      Paint()..color = NavisColors.azureLight.withValues(alpha: 0.9),
    );

    // Petit arc radar sous le N (signal intelligent)
    final radarRect = Rect.fromCircle(center: Offset(w * 0.5, h * 0.88), radius: w * 0.12);
    canvas.drawArc(
      radarRect,
      math.pi,
      math.pi * 0.55,
      false,
      Paint()
        ..color = NavisColors.azure.withValues(alpha: 0.35)
        ..style = PaintingStyle.stroke
        ..strokeWidth = stroke * 0.35
        ..strokeCap = cap,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
