import '../../core/config.dart';
import '../../domain/models.dart';
import '../yaml_loader.dart';

class ExamplesRepository {
  Future<List<ExampleItem>> loadExamples() async {
    return loadExamplesForMode('Syllables');
  }

  Future<List<ExampleItem>> loadExamplesForMode(String mode) async {
    final filename = switch (mode) {
      'Vowels' => 'example_vowels.yaml',
      'Consonants' => 'example_consonants.yaml',
      _ => 'example_syllables.yaml',
    };
    final data = await loadYamlAsset('${AppConfig.assetsDataPath}/$filename');
    final items = _extractItems(data);
    return items
        .whereType<Map>()
        .map((raw) => Map<String, dynamic>.from(raw))
        .map((raw) {
          final exampleWord = '${raw['example_word'] ?? raw['hangul'] ?? ''}';
          final exampleRr = '${raw['example_rr'] ?? raw['rr'] ?? ''}';
          final syllableKey = '${raw['hangul'] ?? ''}';
          final startsWithSyllable =
              '${raw['starts_with_syllable'] ?? (mode == 'Syllables' ? syllableKey : _firstGlyph(exampleWord))}';
          String startsWithConsonant = '${raw['starts_with_consonant'] ?? (mode == 'Consonants' ? syllableKey : '')}';
          String startsWithVowel = '${raw['starts_with_vowel'] ?? (mode == 'Vowels' ? syllableKey : '')}';
          if (mode == 'Syllables') {
            final decomposed = _decomposeSyllable(startsWithSyllable);
            if (decomposed != null) {
              startsWithConsonant = decomposed.$1;
              startsWithVowel = decomposed.$2;
            }
          }
          return ExampleItem(
            hangul: exampleWord,
            rr: exampleRr,
            glossEn: '${raw['gloss_en'] ?? ''}',
            startsWithSyllable: startsWithSyllable,
            startsWithConsonant: startsWithConsonant,
            startsWithVowel: startsWithVowel,
            imagePrompt: '${raw['image_prompt'] ?? ''}',
            imageFilename: '${raw['image_filename'] ?? ''}',
          );
        })
        .toList();
  }

  Future<ExamplesIndex> loadIndexedExamples() async {
    return loadIndexedExamplesForMode('Syllables');
  }

  Future<ExamplesIndex> loadIndexedExamplesForMode(String mode) async {
    final items = await loadExamplesForMode(mode);
    return ExamplesIndex.fromItems(items);
  }
}

class ExamplesIndex {
  final Map<String, List<ExampleItem>> bySyllable;
  final Map<String, List<ExampleItem>> byConsonant;
  final Map<String, List<ExampleItem>> byVowel;

  const ExamplesIndex({
    required this.bySyllable,
    required this.byConsonant,
    required this.byVowel,
  });

  factory ExamplesIndex.fromItems(List<ExampleItem> items) {
    final bySyllable = <String, List<ExampleItem>>{};
    final byConsonant = <String, List<ExampleItem>>{};
    final byVowel = <String, List<ExampleItem>>{};

    for (final item in items) {
      _add(bySyllable, item.startsWithSyllable, item);
      _add(byConsonant, item.startsWithConsonant, item);
      _add(byVowel, item.startsWithVowel, item);
    }

    return ExamplesIndex(
      bySyllable: bySyllable,
      byConsonant: byConsonant,
      byVowel: byVowel,
    );
  }

  static void _add(
    Map<String, List<ExampleItem>> target,
    String key,
    ExampleItem item,
  ) {
    if (key.isEmpty) return;
    final list = target.putIfAbsent(key, () => <ExampleItem>[]);
    list.add(item);
  }
}

List<dynamic> _extractItems(dynamic data) {
  if (data is Map && data['examples'] is List) {
    return data['examples'] as List;
  }
  if (data is Iterable) {
    return data.toList();
  }
  return const [];
}

String _firstGlyph(String text) {
  if (text.isEmpty) return '';
  return text.substring(0, 1);
}

(String, String)? _decomposeSyllable(String syllable) {
  if (syllable.isEmpty) return null;
  final code = syllable.codeUnitAt(0);
  if (code < 0xAC00 || code > 0xD7A3) return null;
  final index = code - 0xAC00;
  final choIndex = index ~/ 588;
  final jungIndex = (index % 588) ~/ 28;
  if (choIndex < 0 || choIndex >= _compatCho.length) return null;
  if (jungIndex < 0 || jungIndex >= _compatJung.length) return null;
  return (_compatCho[choIndex], _compatJung[jungIndex]);
}

const List<String> _compatCho = [
  'ㄱ',
  'ㄲ',
  'ㄴ',
  'ㄷ',
  'ㄸ',
  'ㄹ',
  'ㅁ',
  'ㅂ',
  'ㅃ',
  'ㅅ',
  'ㅆ',
  'ㅇ',
  'ㅈ',
  'ㅉ',
  'ㅊ',
  'ㅋ',
  'ㅌ',
  'ㅍ',
  'ㅎ',
];

const List<String> _compatJung = [
  'ㅏ',
  'ㅐ',
  'ㅑ',
  'ㅒ',
  'ㅓ',
  'ㅔ',
  'ㅕ',
  'ㅖ',
  'ㅗ',
  'ㅘ',
  'ㅙ',
  'ㅚ',
  'ㅛ',
  'ㅜ',
  'ㅝ',
  'ㅞ',
  'ㅟ',
  'ㅠ',
  'ㅡ',
  'ㅢ',
  'ㅣ',
];
