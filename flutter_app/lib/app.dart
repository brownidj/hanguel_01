import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'ui/screens/main_screen.dart';
import 'ui/styles/theme.dart';
import 'state/settings_state.dart';

class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeName = ref.watch(settingsStateProvider).theme;
    return MaterialApp(
      title: 'Hangul Say It',
      theme: buildAppTheme(themeName),
      home: const MainScreen(),
    );
  }
}
