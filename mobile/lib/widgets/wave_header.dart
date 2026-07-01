import 'package:flutter/material.dart';
import '../theme/navis_theme.dart';

class WaveClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final path = Path()
      ..lineTo(0, size.height * 0.72)
      ..quadraticBezierTo(
        size.width * 0.25,
        size.height * 0.92,
        size.width * 0.5,
        size.height * 0.78,
      )
      ..quadraticBezierTo(
        size.width * 0.78,
        size.height * 0.64,
        size.width,
        size.height * 0.82,
      )
      ..lineTo(size.width, 0)
      ..close();
    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) => false;
}

class WaveHeader extends StatelessWidget {
  const WaveHeader({
    super.key,
    required this.height,
    this.child,
    this.gradient = NavisColors.primaryGradient,
  });

  final double height;
  final Widget? child;
  final Gradient gradient;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      width: double.infinity,
      child: height.isFinite
          ? ClipPath(
              clipper: WaveClipper(),
              child: DecoratedBox(
                decoration: BoxDecoration(gradient: gradient),
                child: child,
              ),
            )
          : DecoratedBox(
              decoration: BoxDecoration(gradient: gradient),
              child: child,
            ),
    );
  }
}
