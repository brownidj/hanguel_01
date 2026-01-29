import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/repositories/consonants_repository.dart';
import '../data/repositories/examples_repository.dart';
import '../data/repositories/vowels_repository.dart';
import '../data/repositories/syllables_repository.dart';
import '../domain/models.dart';
import 'navigation_state.dart';
import 'syllable_options_state.dart';

final consonantsRepositoryProvider = Provider<ConsonantsRepository>(
  (ref) => ConsonantsRepository(),
);

final vowelsRepositoryProvider = Provider<VowelsRepository>(
  (ref) => VowelsRepository(),
);

final examplesRepositoryProvider = Provider<ExamplesRepository>(
  (ref) => ExamplesRepository(),
);

final syllablesRepositoryProvider = Provider<SyllablesRepository>(
  (ref) => SyllablesRepository(),
);

final consonantsProvider = FutureProvider<List<Map<String, dynamic>>>(
  (ref) async => ref.read(consonantsRepositoryProvider).loadConsonants(),
);

final vowelsProvider = FutureProvider<List<Map<String, dynamic>>>(
  (ref) async => ref.read(vowelsRepositoryProvider).loadVowels(),
);

final examplesProvider = FutureProvider<List<ExampleItem>>(
  (ref) async {
    final mode = ref.watch(navigationStateProvider.select((state) => state.mode));
    return ref.read(examplesRepositoryProvider).loadExamplesForMode(mode);
  },
);

final examplesIndexProvider = FutureProvider<ExamplesIndex>(
  (ref) async {
    final mode = ref.watch(navigationStateProvider.select((state) => state.mode));
    return ref.read(examplesRepositoryProvider).loadIndexedExamplesForMode(mode);
  },
);

final syllablesProvider = FutureProvider<List<StudyItem>>(
  (ref) async => ref.read(syllablesRepositoryProvider).loadSyllables(),
);

final filteredSyllablesProvider = FutureProvider<List<StudyItem>>((ref) async {
  final syllables = await ref.watch(syllablesProvider.future);
  final vowels = await ref.watch(vowelsProvider.future);
  final set = ref.watch(syllableVowelSetProvider);
  final vowelTypes = <String, String>{};
  for (final raw in vowels) {
    final glyph = raw['glyph'];
    final type = raw['vowel_type'];
    if (glyph is String && type is String) {
      vowelTypes[glyph] = type;
    }
  }
  final allowed = () {
    switch (set) {
      case SyllableVowelSet.core:
        return {'core'};
      case SyllableVowelSet.corePlusAeE:
        return {'core', 'mid_front'};
      case SyllableVowelSet.addYaYeYoYu:
        return {'core', 'mid_front', 'y_glide'};
      case SyllableVowelSet.addCompounds:
        return {'core', 'mid_front', 'y_glide', 'compound'};
    }
  }();
  return syllables.where((item) {
    final type = vowelTypes[item.vowel];
    return type != null && allowed.contains(type);
  }).toList();
});

final currentItemsProvider = Provider<AsyncValue<List<StudyItem>>>((ref) {
  final mode = ref.watch(navigationStateProvider).mode;
  if (mode == 'Vowels') {
    return ref.watch(vowelsProvider).whenData(
      (items) => items
          .map(
            (raw) => StudyItem(
              mode: 'Vowels',
              glyph: '${raw['glyph'] ?? ''}',
              consonant: '',
              vowel: '${raw['glyph'] ?? ''}',
              blockType: '',
            ),
          )
          .toList(),
    );
  }
  if (mode == 'Consonants') {
    return ref.watch(consonantsProvider).whenData(
      (items) => items
          .map(
            (raw) => StudyItem(
              mode: 'Consonants',
              glyph: '${raw['glyph'] ?? ''}',
              consonant: '${raw['glyph'] ?? ''}',
              vowel: '',
              blockType: '',
            ),
          )
          .toList(),
    );
  }
  return ref.watch(filteredSyllablesProvider);
});

final currentItemProvider = Provider<AsyncValue<StudyItem>>((ref) {
  final itemsAsync = ref.watch(currentItemsProvider);
  final index = ref.watch(navigationStateProvider).index;
  return itemsAsync.whenData((items) {
    if (items.isEmpty) return const StudyItem.empty();
    final safeIndex = index % items.length;
    return items[safeIndex];
  });
});
