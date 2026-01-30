import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../state/settings_state.dart';

final settingsStoreProvider = Provider<SettingsStore>((ref) => SettingsStore());

class SettingsStore {
  SettingsStore({SharedPreferences? prefs}) : _prefsOverride = prefs;

  final SharedPreferences? _prefsOverride;

  static const String _keyShowCues = 'show_cues';
  static const String _keyWpm = 'wpm';
  static const String _keySlow = 'slow_enabled';
  static const String _keyIncludeRare = 'include_special';
  static const String _legacyIncludeRare = 'include_rare';
  static const String _keyAdvancedVowels = 'advanced_vowels';
  static const String _keyRepeats = 'repeats';
  static const String _keyDelayBeforeFirstPlay = 'delay_before_first_play';
  static const String _keyDelayBetweenRepeats = 'delay_between_repeats';
  static const String _keyDelayBeforeHints = 'delay_before_hints';
  static const String _keyDelayBeforeExtras = 'delay_before_extras';
  static const String _keyDelayBeforeAutoAdvance = 'delay_before_auto_advance';
  static const String _keyTheme = 'theme';
  static const String _keyActivePreset = 'active_preset';
  static const String _keySavedWpm = 'saved_wpm';
  static const String _keySavedRepeats = 'saved_repeats';
  static const String _keySavedDelayBeforeFirstPlay = 'saved_delay_before_first_play';
  static const String _keySavedDelayBetweenRepeats = 'saved_delay_between_repeats';
  static const String _keySavedDelayBeforeAutoAdvance = 'saved_delay_before_auto_advance';

  Future<SettingsSnapshot> load() async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    final showCues = prefs.getBool(_keyShowCues) ?? true;
    final wpm = prefs.getInt(_keyWpm) ?? 80;
    final slowEnabled = prefs.getBool(_keySlow) ?? false;
    final includeRare = prefs.getBool(_keyIncludeRare) ?? prefs.getBool(_legacyIncludeRare) ?? false;
    final advancedVowels = prefs.getBool(_keyAdvancedVowels) ?? false;
    final repeats = prefs.getInt(_keyRepeats) ?? 1;
    final delayBeforeFirstPlay = prefs.getDouble(_keyDelayBeforeFirstPlay) ?? 0.0;
    final delayBetweenRepeats = prefs.getDouble(_keyDelayBetweenRepeats) ?? 1.0;
    final delayBeforeHints = prefs.getDouble(_keyDelayBeforeHints) ?? 0.0;
    final delayBeforeExtras = prefs.getDouble(_keyDelayBeforeExtras) ?? 0.0;
    final delayBeforeAutoAdvance = prefs.getDouble(_keyDelayBeforeAutoAdvance) ?? 0.0;
    final theme = prefs.getString(_keyTheme) ?? 'Taeguk';
    final activePreset = prefs.getString(_keyActivePreset) ?? '';
    final savedWpm = prefs.getInt(_keySavedWpm) ?? wpm;
    final savedRepeats = prefs.getInt(_keySavedRepeats) ?? 1;
    final savedDelayBeforeFirstPlay = prefs.getDouble(_keySavedDelayBeforeFirstPlay) ?? 0.0;
    final savedDelayBetweenRepeats = prefs.getDouble(_keySavedDelayBetweenRepeats) ?? 1.0;
    final savedDelayBeforeAutoAdvance = prefs.getDouble(_keySavedDelayBeforeAutoAdvance) ?? 0.0;
    return SettingsSnapshot(
      showCues: showCues,
      wpm: wpm,
      slowEnabled: slowEnabled,
      includeRare: includeRare,
      advancedVowels: advancedVowels,
      repeats: repeats,
      delayBeforeFirstPlay: delayBeforeFirstPlay,
      delayBetweenRepeats: delayBetweenRepeats,
      delayBeforeHints: delayBeforeHints,
      delayBeforeExtras: delayBeforeExtras,
      delayBeforeAutoAdvance: delayBeforeAutoAdvance,
      theme: theme == 'Hanji paper' ? 'Hanji' : theme,
      activePreset: activePreset,
      savedWpm: savedWpm,
      savedRepeats: savedRepeats,
      savedDelayBeforeFirstPlay: savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: savedDelayBeforeAutoAdvance,
    );
  }

  Future<void> saveShowCues(bool value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setBool(_keyShowCues, value);
  }

  Future<void> saveWpm(int value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setInt(_keyWpm, value);
  }

  Future<void> saveSlowEnabled(bool value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setBool(_keySlow, value);
  }

  Future<void> saveAll(SettingsSnapshot snapshot) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setBool(_keyShowCues, snapshot.showCues);
    await prefs.setInt(_keyWpm, snapshot.wpm);
    await prefs.setBool(_keySlow, snapshot.slowEnabled);
    await prefs.setBool(_keyIncludeRare, snapshot.includeRare);
    await prefs.setBool(_keyAdvancedVowels, snapshot.advancedVowels);
    await prefs.setInt(_keyRepeats, snapshot.repeats);
    await prefs.setDouble(_keyDelayBeforeFirstPlay, snapshot.delayBeforeFirstPlay);
    await prefs.setDouble(_keyDelayBetweenRepeats, snapshot.delayBetweenRepeats);
    await prefs.setDouble(_keyDelayBeforeHints, snapshot.delayBeforeHints);
    await prefs.setDouble(_keyDelayBeforeExtras, snapshot.delayBeforeExtras);
    await prefs.setDouble(_keyDelayBeforeAutoAdvance, snapshot.delayBeforeAutoAdvance);
    await prefs.setString(_keyTheme, snapshot.theme);
    await prefs.setString(_keyActivePreset, snapshot.activePreset);
    await prefs.setInt(_keySavedWpm, snapshot.savedWpm);
    await prefs.setInt(_keySavedRepeats, snapshot.savedRepeats);
    await prefs.setDouble(_keySavedDelayBeforeFirstPlay, snapshot.savedDelayBeforeFirstPlay);
    await prefs.setDouble(_keySavedDelayBetweenRepeats, snapshot.savedDelayBetweenRepeats);
    await prefs.setDouble(_keySavedDelayBeforeAutoAdvance, snapshot.savedDelayBeforeAutoAdvance);
  }

  Future<void> saveIncludeRare(bool value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setBool(_keyIncludeRare, value);
  }

  Future<void> saveAdvancedVowels(bool value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setBool(_keyAdvancedVowels, value);
  }

  Future<void> saveRepeats(int value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setInt(_keyRepeats, value);
  }

  Future<void> saveDelayBeforeFirstPlay(double value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setDouble(_keyDelayBeforeFirstPlay, value);
  }

  Future<void> saveDelayBetweenRepeats(double value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setDouble(_keyDelayBetweenRepeats, value);
  }

  Future<void> saveDelayBeforeHints(double value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setDouble(_keyDelayBeforeHints, value);
  }

  Future<void> saveDelayBeforeExtras(double value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setDouble(_keyDelayBeforeExtras, value);
  }

  Future<void> saveDelayBeforeAutoAdvance(double value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setDouble(_keyDelayBeforeAutoAdvance, value);
  }

  Future<void> saveTheme(String value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setString(_keyTheme, value);
  }

  Future<void> saveActivePreset(String value) async {
    final prefs = _prefsOverride ?? await SharedPreferences.getInstance();
    await prefs.setString(_keyActivePreset, value);
  }
}
