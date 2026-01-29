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
          final startsWithSyllable = '${raw['starts_with_syllable'] ?? (mode == 'Syllables' ? raw['hangul'] ?? '' : _firstGlyph(exampleWord))}';
          final startsWithConsonant = '${raw['starts_with_consonant'] ?? (mode == 'Consonants' ? raw['hangul'] ?? '' : '')}';
          final startsWithVowel = '${raw['starts_with_vowel'] ?? (mode == 'Vowels' ? raw['hangul'] ?? '' : '')}';
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
