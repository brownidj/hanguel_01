import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:hangul_flutter/state/navigation_state.dart';
import 'package:hangul_flutter/state/playback_state.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('playback state resets on mode change', () async {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    container.read(playbackModeResetProvider);
    container.read(playbackStateProvider.notifier).setControlsEnabled(true);
    container.read(playbackStateProvider.notifier).setAutoEnabled(true);

    container.read(navigationStateProvider.notifier).setMode('Consonants');
    await Future<void>.delayed(Duration.zero);

    final snapshot = container.read(playbackStateProvider);
    expect(snapshot.controlsEnabled, isFalse);
    expect(snapshot.autoEnabled, isFalse);
  });
}
