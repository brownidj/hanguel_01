import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'debug/debug_logger.dart';
import 'debug/safe_mode.dart';
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
  bool _safeMode = false;
  bool _safeLoaded = false;

  @override
  void initState() {
    super.initState();
    _loadSafeMode();
  }

  Future<void> _loadSafeMode() async {
    final enabled = await SafeMode.isEnabled();
    await DebugLogger.log('safe mode = $enabled');
    if (!mounted) return;
    setState(() {
      _safeMode = enabled;
      _safeLoaded = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    final themeName = ref.watch(settingsStateProvider).theme;
    final home = _safeLoaded
        ? (_safeMode
            ? _SafeModeScreen(
                onDisable: () async {
                  await SafeMode.setEnabled(false);
                  await DebugLogger.log('safe mode disabled');
                  if (!mounted) return;
                  setState(() {
                    _safeMode = false;
                  });
                },
              )
            : (_showSplash
                ? SplashScreen(
                    onStart: () async {
                      await DebugLogger.log('splash start pressed');
                      if (!mounted) return;
                      setState(() {
                        _showSplash = false;
                      });
                    },
                  )
                : const MainScreen()))
        : const _LoadingScreen();

    DebugLogger.log('App build: safeLoaded=$_safeLoaded safe=$_safeMode splash=$_showSplash');

    return MaterialApp(
      title: 'Hangul Say It',
      theme: buildAppTheme(themeName),
      home: home,
    );
  }
}

class _LoadingScreen extends StatelessWidget {
  const _LoadingScreen();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: CircularProgressIndicator()),
    );
  }
}

class _SafeModeScreen extends StatefulWidget {
  const _SafeModeScreen({required this.onDisable});

  final VoidCallback onDisable;

  @override
  State<_SafeModeScreen> createState() => _SafeModeScreenState();
}

class _SafeModeScreenState extends State<_SafeModeScreen> {
  String _log = '';

  Future<void> _refreshLog() async {
    final text = await DebugLogger.read();
    if (!mounted) return;
    setState(() {
      _log = text;
    });
  }

  @override
  void initState() {
    super.initState();
    _refreshLog();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Safe Mode'),
        actions: [
          IconButton(
            onPressed: _refreshLog,
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh log',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              'Safe Mode is enabled. This bypasses the main UI.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: widget.onDisable,
              child: const Text('Disable Safe Mode'),
            ),
            const SizedBox(height: 16),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Startup log',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.black12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(12),
                  child: Text(_log.isEmpty ? '(no log data)' : _log),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
