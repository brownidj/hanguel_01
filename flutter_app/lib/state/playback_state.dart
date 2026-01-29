import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/models.dart';
import 'data_providers.dart';
import 'navigation_state.dart';
import 'settings_state.dart';
import 'audio_service_provider.dart';
import '../services/audio_service.dart';

final playbackStateProvider = StateNotifierProvider<PlaybackState, PlaybackSnapshot>(
  (ref) => PlaybackState(ref),
);

final playbackModeResetProvider = Provider<void>((ref) {
  ref.listen<NavigationSnapshot>(navigationStateProvider, (previous, next) {
    if (previous == null || previous.mode != next.mode) {
      ref.read(playbackStateProvider.notifier).resetForMode();
    }
  });
});

class PlaybackSnapshot {
  final bool controlsEnabled;
  final bool autoEnabled;
  final bool heardOnce;

  const PlaybackSnapshot({
    required this.controlsEnabled,
    required this.autoEnabled,
    required this.heardOnce,
  });
}

class PlaybackState extends StateNotifier<PlaybackSnapshot> {
  PlaybackState(this._ref)
      : _audio = _ref.read(audioServiceProvider),
        super(const PlaybackSnapshot(controlsEnabled: false, autoEnabled: false, heardOnce: false));

  final Ref _ref;
  final AudioService _audio;
  bool _autoRunning = false;
  bool _autoHasStarted = false;
  bool _disposed = false;

  void setControlsEnabled(bool enabled) {
    state = PlaybackSnapshot(
      controlsEnabled: enabled,
      autoEnabled: state.autoEnabled,
      heardOnce: state.heardOnce,
    );
  }

  void setAutoEnabled(bool enabled) {
    state = PlaybackSnapshot(
      controlsEnabled: state.controlsEnabled,
      autoEnabled: enabled,
      heardOnce: state.heardOnce,
    );
    if (enabled) {
      _runAutoLoop();
    } else {
      _autoHasStarted = false;
    }
  }

  void setHeardOnce(bool value) {
    state = PlaybackSnapshot(
      controlsEnabled: state.controlsEnabled,
      autoEnabled: state.autoEnabled,
      heardOnce: value,
    );
  }

  void resetForMode() {
    state = const PlaybackSnapshot(controlsEnabled: false, autoEnabled: false, heardOnce: false);
    _autoHasStarted = false;
    _audio.stop();
  }

  Future<void> _runAutoLoop() async {
    if (_autoRunning) return;
    _autoRunning = true;
    while (state.autoEnabled && !_disposed) {
      await _autoStep();
    }
    _autoRunning = false;
  }

  Future<void> _autoStep() async {
    if (_disposed) return;
    final settings = _ref.read(settingsStateProvider);
    if (!_autoHasStarted) {
      await _delaySeconds(settings.delayBeforeFirstPlay);
      _autoHasStarted = true;
    }
    if (_disposed || !state.autoEnabled) return;
    final item = _currentItem();
    if (item.glyph.isEmpty) {
      await Future<void>.delayed(const Duration(milliseconds: 200));
      return;
    }
    final repeats = settings.repeats < 1 ? 1 : settings.repeats;
    for (var i = 0; i < repeats; i += 1) {
      if (!state.autoEnabled || _disposed) return;
      await _ref.read(audioServiceProvider).playGlyph(item.glyph, wpm: settings.effectiveWpm);
      if (i < repeats - 1) {
        await _delaySeconds(settings.delayBetweenRepeats);
      }
    }
    if (!state.autoEnabled || _disposed) return;
    // await _delaySeconds(settings.delayBeforeHints);
    // await _delaySeconds(settings.delayBeforeExtras);
    await _delaySeconds(settings.delayBeforeAutoAdvance);
    if (!state.autoEnabled || _disposed) return;
    final length = _itemsLength();
    if (length <= 0) return;
    _ref.read(navigationStateProvider.notifier).next(length);
  }

  StudyItem _currentItem() {
    return _ref.read(currentItemProvider).maybeWhen(
          data: (value) => value,
          orElse: () => const StudyItem.empty(),
        );
  }

  int _itemsLength() {
    return _ref.read(currentItemsProvider).maybeWhen(
          data: (items) => items.length,
          orElse: () => 0,
        );
  }

  Future<void> _delaySeconds(double seconds) async {
    if (seconds <= 0) return;
    await Future<void>.delayed(Duration(milliseconds: (seconds * 1000).round()));
  }

  @override
  void dispose() {
    _disposed = true;
    _audio.stop();
    super.dispose();
  }
}
