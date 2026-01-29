import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:hangul_flutter/data/repositories/examples_repository.dart';
import 'package:hangul_flutter/data/repositories/consonants_repository.dart';
import 'package:hangul_flutter/data/repositories/vowels_repository.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('consonants repository loads data', () async {
    final repo = ConsonantsRepository();
    final items = await repo.loadConsonants();
    expect(items.isNotEmpty, isTrue);
    expect(items.first.containsKey('glyph'), isTrue);
  });

  test('vowels repository loads data', () async {
    final repo = VowelsRepository();
    final items = await repo.loadVowels();
    expect(items.isNotEmpty, isTrue);
    expect(items.first.containsKey('glyph'), isTrue);
  });

  test('examples repository builds indices', () async {
    final repo = ExamplesRepository();
    final index = await repo.loadIndexedExamples();
    expect(index.bySyllable.isNotEmpty, isTrue);
    expect(index.byConsonant.isNotEmpty, isTrue);
    expect(index.byVowel.isNotEmpty, isTrue);
  });

  test('examples repository loads consonant examples from example_consonants', () async {
    final repo = ExamplesRepository();
    final index = await repo.loadIndexedExamplesForMode('Consonants');
    final items = index.byConsonant['ㄲ'] ?? [];
    final hasMagpie = items.any(
      (item) => item.hangul == '까치' && item.imageFilename == '까치-magpie.png',
    );
    expect(hasMagpie, isTrue);
  });

  test('examples repository loads vowel examples from example_vowels', () async {
    final repo = ExamplesRepository();
    final index = await repo.loadIndexedExamplesForMode('Vowels');
    final items = index.byVowel['ㅏ'] ?? [];
    final hasBaby = items.any(
      (item) => item.hangul == '아기' && item.imageFilename == '아기-baby.png',
    );
    expect(hasBaby, isTrue);
  });

  test('vowel example audio asset exists for example word', () async {
    const word = '아기';
    const buckets = [40, 80, 120, 160];
    final found = buckets.any((bucket) {
      final path = 'assets/audio/${word}__ko-KR-Wavenet-A__$bucket.wav';
      return File(path).existsSync();
    });
    expect(found, isTrue);
  });

  test('consonant example audio asset exists for example word', () async {
    const word = '까치';
    const buckets = [40, 80, 120, 160];
    final found = buckets.any((bucket) {
      final path = 'assets/audio/${word}__ko-KR-Wavenet-A__$bucket.wav';
      return File(path).existsSync();
    });
    expect(found, isTrue);
  });
}
