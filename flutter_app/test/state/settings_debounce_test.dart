import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:hangul_flutter/state/settings_state.dart';
import 'package:hangul_flutter/services/settings_store.dart';

void main() {
  test('settings debounce batches persistence', () async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    final store = SettingsStore(prefs: prefs);
    final container = ProviderContainer(
      overrides: [
        settingsStoreProvider.overrideWithValue(store),
      ],
    );
    addTearDown(container.dispose);

    final notifier = container.read(settingsStateProvider.notifier);
    notifier.setWpm(120);
    notifier.setIncludeRare(true);
    notifier.setAdvancedVowels(true);
    notifier.setRepeats(3);

    await Future<void>.delayed(const Duration(milliseconds: 350));

    expect(prefs.getInt('wpm'), 120);
    expect(prefs.getBool('include_rare'), true);
    expect(prefs.getBool('advanced_vowels'), true);
    expect(prefs.getInt('repeats'), 3);
  });
}
