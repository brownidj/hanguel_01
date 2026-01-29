import 'package:flutter_test/flutter_test.dart';

import 'package:hangul_flutter/domain/romanization_rr.dart';

void main() {
  test('romanizeCv basic', () {
    final result = romanizeCv('ㄱ', 'ㅏ');
    expect(result.rr, 'ga');
    expect(result.hint.contains('ㄱ'), isTrue);
  });

  test('romanizeText handles syllables', () {
    final result = romanizeText('가나');
    expect(result.rr, 'gana');
  });
}
