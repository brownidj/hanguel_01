import 'package:flutter/material.dart';

class AppColors {
  static const Color background = Color(0xFFE6F2F8);
  static const Color panelPink = Color(0xFFFBEFEF);
  static const Color text = Colors.black;
}

class ThemePalette {
  final Color background;
  final Color jamoBackground;

  const ThemePalette({required this.background, required this.jamoBackground});
}

const ThemePalette taegukPalette = ThemePalette(
  background: Color(0xFFE6F2F8),
  jamoBackground: Color(0xFFFBEFEF),
);

const ThemePalette hanjiPalette = ThemePalette(
  background: Color(0xFFFEFCF8),
  jamoBackground: Color(0xFFF5EAD8),
);

ThemePalette paletteForTheme(String themeName) {
  if (themeName == 'Hanji') {
    return hanjiPalette;
  }
  return taegukPalette;
}
