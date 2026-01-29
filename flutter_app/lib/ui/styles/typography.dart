import 'package:flutter/material.dart';

TextTheme buildTextTheme() {
  return const TextTheme(
    bodyMedium: TextStyle(fontSize: 12, color: Colors.black),
    bodyLarge: TextStyle(fontSize: 16, color: Colors.black),
    titleMedium: TextStyle(fontSize: 14, color: Colors.black, fontWeight: FontWeight.w600),
    titleLarge: TextStyle(fontSize: 16, color: Colors.black, fontWeight: FontWeight.w600),
  );
}
