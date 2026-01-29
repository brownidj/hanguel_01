import 'package:flutter/material.dart';

import 'colors.dart';
import 'typography.dart';

ThemeData buildAppTheme(String themeName) {
  final palette = paletteForTheme(themeName);
  return ThemeData(
    scaffoldBackgroundColor: palette.background,
    textTheme: buildTextTheme(),
    useMaterial3: true,
  );
}
