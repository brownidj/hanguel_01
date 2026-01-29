import 'package:flutter_test/flutter_test.dart';

import 'package:hangul_flutter/domain/compose.dart';

void main() {
  test('composeCv composes basic syllable', () {
    expect(composeCv('ㄱ', 'ㅏ'), '가');
  });

  test('composeCv returns empty on invalid input', () {
    expect(composeCv('', 'ㅏ'), '');
    expect(composeCv('ㄱ', ''), '');
  });
}
