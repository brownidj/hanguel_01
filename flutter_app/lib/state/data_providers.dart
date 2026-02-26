import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/repositories/consonants_repository.dart';
import '../data/repositories/examples_repository.dart';
import '../data/repositories/stages_repository.dart';
import '../data/repositories/vowels_repository.dart';
import '../data/repositories/syllables_repository.dart';
import '../domain/models.dart';
import '../domain/stages.dart';
import 'navigation_state.dart';
import 'stage_state.dart';
import 'syllable_options_state.dart';

final consonantsRepositoryProvider = Provider<ConsonantsRepository>(
  (ref) => ConsonantsRepository(),
);

final stagesRepositoryProvider = Provider<StagesRepository>(
  (ref) => StagesRepository(),
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

final stagesProvider = FutureProvider<List<StageDefinition>>(
  (ref) async => ref.read(stagesRepositoryProvider).loadStages(),
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
  await ref.watch(stagesProvider.future);
  final inventory = ref.watch(stageInventoryProvider);
  final vowelSetSelection = ref.watch(syllableVowelSetProvider);
  final allowedVowels = syllableVowelSetGlyphs(vowelSetSelection);
  final hasInventoryVowels = inventory.vowelSet.isNotEmpty;
  final hasInventoryConsonants = inventory.consonantSet.isNotEmpty;
  return syllables.where((item) {
    if (!allowedVowels.contains(item.vowel)) return false;
    if (hasInventoryVowels && !inventory.vowelSet.contains(item.vowel)) return false;
    if (hasInventoryConsonants && !inventory.consonantSet.contains(item.consonant)) return false;
    return true;
  }).toList();
});

final currentItemsProvider = Provider<AsyncValue<List<StudyItem>>>((ref) {
  final mode = ref.watch(navigationStateProvider).mode;
  final stagesAsync = ref.watch(stagesProvider);
  return stagesAsync.when(
    data: (_) {
      if (mode == 'Vowels') {
        final inventory = ref.watch(stageInventoryProvider);
        if (inventory.vowels.isEmpty) {
          return const AsyncValue.data(<StudyItem>[]);
        }
        return ref.watch(vowelsProvider).whenData(
          (items) {
            final byGlyph = <String, Map<String, dynamic>>{};
            for (final raw in items) {
              final glyph = '${raw['glyph'] ?? ''}';
              if (glyph.isNotEmpty) {
                byGlyph[glyph] = raw;
              }
            }
            return inventory.vowels
                .map((glyph) => byGlyph[glyph])
                .whereType<Map<String, dynamic>>()
                .map(
                  (raw) => StudyItem(
                    mode: 'Vowels',
                    glyph: '${raw['glyph'] ?? ''}',
                    consonant: '',
                    vowel: '${raw['glyph'] ?? ''}',
                    blockType: '',
                  ),
                )
                .toList();
          },
        );
      }
      if (mode == 'Consonants') {
        final inventory = ref.watch(stageInventoryProvider);
        if (inventory.consonants.isEmpty) {
          return const AsyncValue.data(<StudyItem>[]);
        }
        return ref.watch(consonantsProvider).whenData(
          (items) {
            final byGlyph = <String, Map<String, dynamic>>{};
            for (final raw in items) {
              final glyph = '${raw['glyph'] ?? ''}';
              if (glyph.isNotEmpty) {
                byGlyph[glyph] = raw;
              }
            }
            return inventory.consonants
                .map((glyph) => byGlyph[glyph])
                .whereType<Map<String, dynamic>>()
                .map(
                  (raw) => StudyItem(
                    mode: 'Consonants',
                    glyph: '${raw['glyph'] ?? ''}',
                    consonant: '${raw['glyph'] ?? ''}',
                    vowel: '',
                    blockType: '',
                  ),
                )
                .toList();
          },
        );
      }
      return ref.watch(filteredSyllablesProvider);
    },
    loading: () => const AsyncValue.loading(),
    error: (err, stack) => AsyncValue.error(err, stack),
  );
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
