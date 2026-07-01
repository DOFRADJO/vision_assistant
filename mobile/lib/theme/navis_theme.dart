import 'package:flutter/material.dart';

abstract final class NavisColors {
  static const azureLight = Color(0xFF4DA3FF);
  static const azure = Color(0xFF1E7BFF);
  static const azureDeep = Color(0xFF0B5BD4);
  static const azureDark = Color(0xFF0847A8);
  static const white = Color(0xFFFFFFFF);
  static const offWhite = Color(0xFFF4F8FF);
  static const textDark = Color(0xFF1A2B4A);
  static const textMuted = Color(0xFF7A8FA8);
  static const borderSoft = Color(0xFFE3ECF8);

  static const primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [azureLight, azure, azureDeep],
  );

  static const cardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF3D96FF), azureDeep],
  );

  static List<BoxShadow> softShadow({double blur = 24, double y = 10}) => [
        BoxShadow(
          color: azure.withValues(alpha: 0.18),
          blurRadius: blur,
          offset: Offset(0, y),
        ),
      ];

  static List<BoxShadow> cardShadow = [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.06),
      blurRadius: 20,
      offset: const Offset(0, 8),
    ),
  ];
}

const _font = 'Poppins';

ThemeData buildNavisTheme() {
  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    fontFamily: _font,
    scaffoldBackgroundColor: NavisColors.offWhite,
    colorScheme: ColorScheme.fromSeed(
      seedColor: NavisColors.azure,
      primary: NavisColors.azure,
      surface: NavisColors.white,
    ),
    textTheme: const TextTheme(
      displayLarge: TextStyle(
        fontFamily: _font,
        fontSize: 32,
        fontWeight: FontWeight.w700,
        color: NavisColors.white,
        letterSpacing: -0.5,
      ),
      headlineMedium: TextStyle(
        fontFamily: _font,
        fontSize: 22,
        fontWeight: FontWeight.w600,
        color: NavisColors.textDark,
      ),
      titleLarge: TextStyle(
        fontFamily: _font,
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: NavisColors.textDark,
      ),
      bodyLarge: TextStyle(
        fontFamily: _font,
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: NavisColors.textMuted,
      ),
      labelLarge: TextStyle(
        fontFamily: _font,
        fontSize: 16,
        fontWeight: FontWeight.w600,
      ),
    ),
    appBarTheme: const AppBarTheme(
      elevation: 0,
      scrolledUnderElevation: 0,
      backgroundColor: Colors.transparent,
      foregroundColor: NavisColors.textDark,
      titleTextStyle: TextStyle(
        fontFamily: _font,
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: NavisColors.textDark,
      ),
    ),
  );
}
