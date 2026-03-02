import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'ui/screens/main_screen.dart';
import 'ui/splash_screen.dart';
import 'ui/styles/theme.dart';
import 'state/settings_state.dart';

class App extends ConsumerStatefulWidget {
  const App({super.key});

  @override
  ConsumerState<App> createState() => _AppState();
}

class _AppState extends ConsumerState<App> {
  bool _showSplash = true;

  @override
  Widget build(BuildContext context) {
    final themeName = ref.watch(settingsStateProvider).theme;
    return MaterialApp(
      title: "Hanguel Tutor",
      theme: buildAppTheme(themeName),
      home: _showSplash
          ? SplashScreen(
              onStart: () {
                setState(() {
                  _showSplash = false;
                });
              },
            )
          : const MainScreen(),
    );
  }
}
