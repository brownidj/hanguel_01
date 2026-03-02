import 'dart:async';

import 'package:audioplayers/audioplayers.dart' as ap;
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:just_audio/just_audio.dart' as ja;

const String _defaultVoiceName = 'ko-KR-Wavenet-A';
const List<int> _wpmBuckets = [40, 80, 120, 160];

int nearestWpmBucket(int wpm) {
  final target = wpm;
  var best = _wpmBuckets.first;
  var bestDelta = (best - target).abs();
  for (final bucket in _wpmBuckets.skip(1)) {
    final delta = (bucket - target).abs();
    if (delta < bestDelta) {
      best = bucket;
      bestDelta = delta;
    }
  }
  return best;
}

String buildAudioFilename(String glyph, int wpm) {
  final bucket = nearestWpmBucket(wpm);
  return '${glyph}__${_defaultVoiceName}__$bucket.wav';
}

class AudioService {
  AudioService({AudioBackend? backend}) : _backend = backend ?? AudioService._resolveBackend();

  factory AudioService.testing({
    Future<void> Function(String assetPath)? playAsset,
    Future<void> Function()? stop,
  }) {
    return AudioService(
      backend: _CallbackAudioBackend(
        playAsset: playAsset ?? ((_) async {}),
        stop: stop ?? (() async {}),
      ),
    );
  }

  Completer<void>? _activeCompleter;
  Future<void> _queue = Future<void>.value();
  final AudioBackend _backend;
  final Set<String> _preloaded = <String>{};

  Future<void> playGlyph(String glyph, {required int wpm}) async {
    if (glyph.isEmpty) return;
    final filename = buildAudioFilename(glyph, wpm);
    await _enqueue(() => _playAssetInternal('audio/$filename'));
  }

  Future<void> playGlyphRepeated(
    String glyph, {
    required int wpm,
    int repeats = 1,
    double delayBetweenSeconds = 0.0,
    double delayBeforeFirstSeconds = 0.0,
  }) async {
    if (glyph.isEmpty) return;
    final safeRepeats = repeats < 1 ? 1 : repeats;
    final delayBetweenMs = (delayBetweenSeconds * 1000).round();
    final delayBeforeMs = (delayBeforeFirstSeconds * 1000).round();
    final filename = buildAudioFilename(glyph, wpm);
    await _enqueue(() async {
      if (delayBeforeMs > 0) {
        await Future<void>.delayed(Duration(milliseconds: delayBeforeMs));
      }
      for (var i = 0; i < safeRepeats; i += 1) {
        await _playAssetInternal('audio/$filename');
        if (i < safeRepeats - 1 && delayBetweenMs > 0) {
          await Future<void>.delayed(Duration(milliseconds: delayBetweenMs));
        }
      }
    });
  }

  Future<void> stop() async {
    await _enqueue(_stopInternal);
  }

  Future<void> preloadGlyphs(List<String> glyphs, {required int wpm}) async {
    if (glyphs.isEmpty) return;
    for (final glyph in glyphs) {
      if (glyph.isEmpty) continue;
      final filename = buildAudioFilename(glyph, wpm);
      if (!_preloaded.add(filename)) continue;
      try {
        await rootBundle.load('assets/audio/$filename');
      } catch (_) {
        // ignore: avoid_print
        print('[WARN] Audio preload failed: $filename');
      }
    }
  }

  Future<void> _playAssetInternal(String assetPath) async {
    await _stopInternal();
    final completer = Completer<void>();
    _activeCompleter = completer;
    try {
      await Future.any<void>([
        _backend.playAsset(assetPath),
        completer.future,
      ]);
      if (_activeCompleter == completer && !completer.isCompleted) {
        completer.complete();
      }
    } catch (error) {
      // ignore: avoid_print
      print('[WARN] Audio playback failed: $assetPath ($error)');
    } finally {
      _activeCompleter = null;
    }
  }

  Future<void> _stopInternal() async {
    try {
      final completer = _activeCompleter;
      if (completer != null && !completer.isCompleted) {
        completer.complete();
      }
      _activeCompleter = null;
      await _backend.stop();
    } catch (error) {
      // ignore: avoid_print
      print('[WARN] Audio stop failed: $error');
    }
  }

  Future<void> _enqueue(Future<void> Function() action) {
    _queue = _queue.then((_) => action());
    return _queue;
  }

  void dispose() {
    _backend.dispose();
  }

  static AudioBackend _resolveBackend() {
    if (defaultTargetPlatform == TargetPlatform.iOS || defaultTargetPlatform == TargetPlatform.macOS) {
      return _JustAudioBackend();
    }
    return _AudioPlayersBackend();
  }
}

abstract class AudioBackend {
  Future<void> playAsset(String assetPath);
  Future<void> stop();
  void dispose();
}

class _AudioPlayersBackend implements AudioBackend {
  final ap.AudioPlayer _player = ap.AudioPlayer();

  @override
  Future<void> playAsset(String assetPath) async {
    await _player.play(ap.AssetSource(assetPath));
    await _player.onPlayerComplete.first;
  }

  @override
  Future<void> stop() async {
    await _player.stop();
  }

  @override
  void dispose() {
    _player.dispose();
  }
}

class _JustAudioBackend implements AudioBackend {
  final ja.AudioPlayer _player = ja.AudioPlayer();

  @override
  Future<void> playAsset(String assetPath) async {
    await _player.setAsset('assets/$assetPath');
    await _player.play();
  }

  @override
  Future<void> stop() async {
    await _player.stop();
  }

  @override
  void dispose() {
    _player.dispose();
  }
}

class _CallbackAudioBackend implements AudioBackend {
  _CallbackAudioBackend({
    required Future<void> Function(String assetPath) playAsset,
    required Future<void> Function() stop,
  })  : _playAsset = playAsset,
        _stop = stop;

  final Future<void> Function(String assetPath) _playAsset;
  final Future<void> Function() _stop;

  @override
  Future<void> playAsset(String assetPath) => _playAsset(assetPath);

  @override
  Future<void> stop() => _stop();

  @override
  void dispose() {}
}
