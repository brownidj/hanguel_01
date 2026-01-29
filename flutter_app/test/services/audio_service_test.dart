import 'package:flutter_test/flutter_test.dart';

import 'package:hangul_flutter/services/audio_service.dart';

void main() {
  test('nearestWpmBucket selects closest bucket', () {
    expect(nearestWpmBucket(40), 40);
    expect(nearestWpmBucket(45), 40);
    expect(nearestWpmBucket(79), 80);
    expect(nearestWpmBucket(81), 80);
    expect(nearestWpmBucket(119), 120);
    expect(nearestWpmBucket(140), 120);
    expect(nearestWpmBucket(200), 160);
  });

  test('buildAudioFilename includes glyph and bucket', () {
    expect(buildAudioFilename('\uAC00', 120), '\uAC00__ko-KR-Wavenet-A__120.wav');
    expect(buildAudioFilename('\uC57C\uAD6C', 81), '\uC57C\uAD6C__ko-KR-Wavenet-A__80.wav');
  });
}
