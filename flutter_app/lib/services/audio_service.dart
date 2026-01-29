import 'dart:async';

import 'package:audioplayers/audioplayers.dart' as ap;
import 'package:flutter/foundation.dart';
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
  Completer<void>? _activeCompleter;
  Future<void> _queue = Future<void>.value();
  late final _AudioBackend _backend = _resolveBackend();

  Future<void> playGlyph(String glyph, {required int wpm}) async {
    if (glyph.isEmpty) return;
    final filename = buildAudioFilename(glyph, wpm);
    await _enqueue(() => _playAssetInternal('audio/$filename'));
  }

  Future<void> stop() async {
    await _enqueue(_stopInternal);
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

  _AudioBackend _resolveBackend() {
    if (defaultTargetPlatform == TargetPlatform.iOS || defaultTargetPlatform == TargetPlatform.macOS) {
      return _JustAudioBackend();
    }
    return _AudioPlayersBackend();
  }
}

abstract class _AudioBackend {
  Future<void> playAsset(String assetPath);
  Future<void> stop();
  void dispose();
}

class _AudioPlayersBackend implements _AudioBackend {
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

class _JustAudioBackend implements _AudioBackend {
  final ja.AudioPlayer _player = ja.AudioPlayer();

  @override
  Future<void> playAsset(String assetPath) async {
    await _player.setAsset('assets/$assetPath');
    await _player.play();
    await _player.processingStateStream.firstWhere(
      (state) => state == ja.ProcessingState.completed || state == ja.ProcessingState.idle,
    );
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
