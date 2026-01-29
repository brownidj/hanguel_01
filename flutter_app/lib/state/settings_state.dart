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
  final String activePreset;
  final int savedWpm;
  final int savedRepeats;
  final double savedDelayBeforeFirstPlay;
  final double savedDelayBetweenRepeats;
  final double savedDelayBeforeAutoAdvance;

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
    required this.activePreset,
    required this.savedWpm,
    required this.savedRepeats,
    required this.savedDelayBeforeFirstPlay,
    required this.savedDelayBetweenRepeats,
    required this.savedDelayBeforeAutoAdvance,
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
          activePreset: '',
          savedWpm: 80,
          savedRepeats: 1,
          savedDelayBeforeFirstPlay: 0.0,
          savedDelayBetweenRepeats: 1.0,
          savedDelayBeforeAutoAdvance: 0.0,
        ));

  final SettingsStore _store;
  Timer? _persistTimer;

  SettingsStore get store => _store;

  void _schedulePersist() {
    _persistTimer?.cancel();
    _persistTimer = Timer(const Duration(milliseconds: 300), () {
      _store.saveAll(state);
    });
  }

  void hydrate(SettingsSnapshot snapshot) {
    state = snapshot;
    final preset = presetValues[snapshot.activePreset];
    if (preset == null) return;
    if (snapshot.wpm == preset.wpm &&
        snapshot.repeats == preset.repeats &&
        snapshot.delayBeforeFirstPlay == preset.delayBeforeFirstPlay &&
        snapshot.delayBetweenRepeats == preset.delayBetweenRepeats &&
        snapshot.delayBeforeAutoAdvance == preset.delayBeforeAutoAdvance) {
      return;
    }
    state = SettingsSnapshot(
      showCues: snapshot.showCues,
      wpm: preset.wpm,
      slowEnabled: snapshot.slowEnabled,
      includeRare: snapshot.includeRare,
      advancedVowels: snapshot.advancedVowels,
      repeats: preset.repeats,
      delayBeforeFirstPlay: preset.delayBeforeFirstPlay,
      delayBetweenRepeats: preset.delayBetweenRepeats,
      delayBeforeHints: snapshot.delayBeforeHints,
      delayBeforeExtras: snapshot.delayBeforeExtras,
      delayBeforeAutoAdvance: preset.delayBeforeAutoAdvance,
      theme: snapshot.theme,
      activePreset: snapshot.activePreset,
      savedWpm: snapshot.savedWpm,
      savedRepeats: snapshot.savedRepeats,
      savedDelayBeforeFirstPlay: snapshot.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: snapshot.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: snapshot.savedDelayBeforeAutoAdvance,
    );
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
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
      activePreset: state.activePreset,
      savedWpm: state.savedWpm,
      savedRepeats: state.savedRepeats,
      savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
    );
    _schedulePersist();
  }

  void applyPreset(String name) {
    if (name.isEmpty) {
      state = SettingsSnapshot(
        showCues: state.showCues,
        wpm: state.savedWpm,
        slowEnabled: state.slowEnabled,
        includeRare: state.includeRare,
        advancedVowels: state.advancedVowels,
        repeats: state.savedRepeats,
        delayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
        delayBetweenRepeats: state.savedDelayBetweenRepeats,
        delayBeforeHints: state.delayBeforeHints,
        delayBeforeExtras: state.delayBeforeExtras,
        delayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
        theme: state.theme,
        activePreset: '',
        savedWpm: state.savedWpm,
        savedRepeats: state.savedRepeats,
        savedDelayBeforeFirstPlay: state.savedDelayBeforeFirstPlay,
        savedDelayBetweenRepeats: state.savedDelayBetweenRepeats,
        savedDelayBeforeAutoAdvance: state.savedDelayBeforeAutoAdvance,
      );
      _schedulePersist();
      return;
    }

    final preset = presetValues[name];
    if (preset == null) return;
    final savedWpm = state.wpm;
    final savedRepeats = state.repeats;
    final savedDelayBeforeFirstPlay = state.delayBeforeFirstPlay;
    final savedDelayBetweenRepeats = state.delayBetweenRepeats;
    final savedDelayBeforeAutoAdvance = state.delayBeforeAutoAdvance;
    state = SettingsSnapshot(
      showCues: state.showCues,
      wpm: preset.wpm,
      slowEnabled: state.slowEnabled,
      includeRare: state.includeRare,
      advancedVowels: state.advancedVowels,
      repeats: preset.repeats,
      delayBeforeFirstPlay: preset.delayBeforeFirstPlay,
      delayBetweenRepeats: preset.delayBetweenRepeats,
      delayBeforeHints: state.delayBeforeHints,
      delayBeforeExtras: state.delayBeforeExtras,
      delayBeforeAutoAdvance: preset.delayBeforeAutoAdvance,
      theme: state.theme,
      activePreset: name,
      savedWpm: savedWpm,
      savedRepeats: savedRepeats,
      savedDelayBeforeFirstPlay: savedDelayBeforeFirstPlay,
      savedDelayBetweenRepeats: savedDelayBetweenRepeats,
      savedDelayBeforeAutoAdvance: savedDelayBeforeAutoAdvance,
    );
    _schedulePersist();
  }

  @override
  void dispose() {
    _persistTimer?.cancel();
    super.dispose();
  }
}

class PresetValues {
  final int wpm;
  final int repeats;
  final double delayBeforeFirstPlay;
  final double delayBetweenRepeats;
  final double delayBeforeAutoAdvance;

  const PresetValues({
    required this.wpm,
    required this.repeats,
    required this.delayBeforeFirstPlay,
    required this.delayBetweenRepeats,
    required this.delayBeforeAutoAdvance,
  });
}

const Map<String, PresetValues> presetValues = {
  'Beginner': PresetValues(
    wpm: 40,
    repeats: 3,
    delayBeforeFirstPlay: 1.0,
    delayBetweenRepeats: 2.0,
    delayBeforeAutoAdvance: 2.0,
  ),
  'Default': PresetValues(
    wpm: 80,
    repeats: 1,
    delayBeforeFirstPlay: 0.0,
    delayBetweenRepeats: 1.0,
    delayBeforeAutoAdvance: 0.0,
  ),
  'Advanced': PresetValues(
    wpm: 80,
    repeats: 1,
    delayBeforeFirstPlay: 0.0,
    delayBetweenRepeats: 1.0,
    delayBeforeAutoAdvance: 0.0,
  ),
};
