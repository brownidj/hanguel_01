import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:hangul_flutter/services/navigation_store.dart';
import 'package:hangul_flutter/services/settings_store.dart';
import 'package:hangul_flutter/services/syllable_options_store.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('settings store loads and saves values', () async {
    final store = SettingsStore();
    await store.saveShowCues(false);
    await store.saveWpm(160);
    await store.saveSlowEnabled(true);
    await store.saveIncludeRare(true);
    await store.saveAdvancedVowels(true);
    await store.saveRepeats(3);
    await store.saveDelayBeforeFirstPlay(0.5);
    await store.saveDelayBetweenRepeats(1.5);
    await store.saveDelayBeforeHints(0.0);
    await store.saveDelayBeforeExtras(2.0);
    await store.saveDelayBeforeAutoAdvance(0.0);
    await store.saveTheme('Hanji');
    await store.saveActivePreset('Beginner');

    final snapshot = await store.load();
    expect(snapshot.showCues, isFalse);
    expect(snapshot.wpm, 160);
    expect(snapshot.slowEnabled, isTrue);
    expect(snapshot.includeRare, isTrue);
    expect(snapshot.advancedVowels, isTrue);
    expect(snapshot.repeats, 3);
    expect(snapshot.delayBeforeFirstPlay, 0.5);
    expect(snapshot.delayBetweenRepeats, 1.5);
    expect(snapshot.delayBeforeHints, 0.0);
    expect(snapshot.delayBeforeExtras, 2.0);
    expect(snapshot.delayBeforeAutoAdvance, 0.0);
    expect(snapshot.theme, 'Hanji');
    expect(snapshot.activePreset, 'Beginner');
    expect(snapshot.savedWpm, 160);
    expect(snapshot.savedRepeats, 1);
    expect(snapshot.savedDelayBeforeFirstPlay, 0.0);
    expect(snapshot.savedDelayBetweenRepeats, 1.0);
    expect(snapshot.savedDelayBeforeAutoAdvance, 0.0);
  });

  test('navigation store loads mode', () async {
    final store = NavigationStore();
    await store.saveMode('Syllables');
    final mode = await store.loadMode();
    expect(mode, 'Syllables');
  });

  test('syllable vowel set persists', () async {
    final store = SyllableOptionsStore();
    await store.saveRaw('corePlusAeE');
    final raw = await store.loadRaw();
    expect(raw, 'corePlusAeE');
  });
}
