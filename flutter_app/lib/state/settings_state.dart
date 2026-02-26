import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../services/settings_store.dart';

final settingsStateProvider = StateNotifierProvider<SettingsState, SettingsSnapshot>(
  (ref) => SettingsState(ref.read(settingsStoreProvider)),
);

class SettingsSnapshot {
  final bool showCues;
  final int wpm;
  final bool slowEnabled;
  final bool includeRare;
  final bool advancedVowels;
  final int repeats;
  final double delayBeforeFirstPlay;
  final double delayBetweenRepeats;
  final double delayBeforeHints;
  final double delayBeforeExtras;
  final double delayBeforeAutoAdvance;
  final String theme;

  const SettingsSnapshot({
    required this.showCues,
    required this.wpm,
    required this.slowEnabled,
    required this.includeRare,
    required this.advancedVowels,
    required this.repeats,
    required this.delayBeforeFirstPlay,
    required this.delayBetweenRepeats,
    required this.delayBeforeHints,
    required this.delayBeforeExtras,
    required this.delayBeforeAutoAdvance,
    required this.theme,
  });

  int get effectiveWpm => slowEnabled ? 40 : wpm;
}

class SettingsState extends StateNotifier<SettingsSnapshot> {
  SettingsState(this._store)
      : super(const SettingsSnapshot(
          showCues: true,
          wpm: 80,
          slowEnabled: false,
          includeRare: false,
          advancedVowels: false,
          repeats: 1,
          delayBeforeFirstPlay: 0.0,
          delayBetweenRepeats: 1.0,
          delayBeforeHints: 0.0,
          delayBeforeExtras: 0.0,
          delayBeforeAutoAdvance: 0.0,
          theme: 'Taeguk',
        ));

  final SettingsStore _store;
  Timer? _persistTimer;

  SettingsStore get store => _store;

  void resetDefaults() {
    _persistTimer?.cancel();
    state = const SettingsSnapshot(
      showCues: true,
      wpm: 80,
      slowEnabled: false,
      includeRare: false,
      advancedVowels: false,
      repeats: 1,
      delayBeforeFirstPlay: 0.0,
      delayBetweenRepeats: 1.0,
      delayBeforeHints: 0.0,
      delayBeforeExtras: 0.0,
      delayBeforeAutoAdvance: 0.0,
      theme: 'Taeguk',
    );
    _store.saveAll(state);
  }

  void _schedulePersist() {
    _persistTimer?.cancel();
    _persistTimer = Timer(const Duration(milliseconds: 300), () {
      _store.saveAll(state);
    });
  }

  void hydrate(SettingsSnapshot snapshot) {
    state = snapshot;
  }

  void setShowCues(bool value) {
    state = SettingsSnapshot(
      showCues: value,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setWpm(int wpm) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setSlowEnabled(bool enabled) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: enabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setIncludeRare(bool value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: value,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setAdvancedVowels(bool value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: value,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setRepeats(int value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: value,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setDelayBeforeFirstPlay(double value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: value,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setDelayBetweenRepeats(double value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: value,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setDelayBeforeHints(double value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: value,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setDelayBeforeExtras(double value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: value,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setDelayBeforeAutoAdvance(double value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: value,
      theme: state.theme,
    );
    _schedulePersist();
  }

  void setTheme(String value) {
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: state.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: state.repeats,
      delayBeforeFirstPlay: state.delayBeforeFirstPlay,
      delayBetweenRepeats: state.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: state.delayBeforeAutoAdvance,
      theme: value,
    );
    _schedulePersist();
  }

  @override
  void dispose() {
    _persistTimer?.cancel();
    super.dispose();
  }
}
