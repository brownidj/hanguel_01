import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/stages.dart';
import 'data_providers.dart';
import 'navigation_state.dart';
import '../services/stage_store.dart';

class StageSnapshot {
  final String stageId;

  const StageSnapshot({required this.stageId});
}

class StageInventory {
  final List<String> vowels;
  final List<String> consonants;
  final Set<String> vowelSet;
  final Set<String> consonantSet;

  StageInventory({
    required this.vowels,
    required this.consonants,
  })  : vowelSet = Set<String>.from(vowels),
        consonantSet = Set<String>.from(consonants);

  const StageInventory.empty()
      : vowels = const [],
        consonants = const [],
        vowelSet = const {},
        consonantSet = const {};
}

class StageState extends StateNotifier<StageSnapshot> {
  StageState(this._store) : super(const StageSnapshot(stageId: ''));

  final StageStore _store;

  void setStage(String stageId) {
    if (stageId.isEmpty || stageId == state.stageId) return;
    state = StageSnapshot(stageId: stageId);
    _store.saveStage(stageId);
  }

  void hydrateStage(String stageId) {
    if (stageId.isEmpty || stageId == state.stageId) return;
    state = StageSnapshot(stageId: stageId);
  }

  void reset() {
    const stageId = 'stage_01_vowels_starter';
    state = const StageSnapshot(stageId: stageId);
    _store.saveStage(stageId);
  }
}

final stageStateProvider = StateNotifierProvider<StageState, StageSnapshot>(
  (ref) => StageState(ref.read(stageStoreProvider)),
);

final currentStageProvider = Provider<StageDefinition?>((ref) {
  final stages = ref.watch(stagesProvider).maybeWhen(
        data: (items) => items,
        orElse: () => const <StageDefinition>[],
      );
  if (stages.isEmpty) return null;
  final stageId = ref.watch(stageStateProvider).stageId;
  if (stageId.isEmpty) {
    return stages.first;
  }
  return stages.firstWhere(
    (stage) => stage.id == stageId,
    orElse: () => stages.first,
  );
});

final stageInventoryProvider = Provider<StageInventory>((ref) {
  final stages = ref.watch(stagesProvider).maybeWhen(
        data: (items) => items,
        orElse: () => const <StageDefinition>[],
      );
  final currentStage = ref.watch(currentStageProvider);
  if (stages.isEmpty || currentStage == null) {
    return const StageInventory.empty();
  }
  final reviewPool = currentStage.reviewPool;
  if (reviewPool != null) {
    return StageInventory(vowels: reviewPool.vowels, consonants: reviewPool.consonants);
  }
  final vowels = <String>[];
  final consonants = <String>[];
  final vowelSet = <String>{};
  final consonantSet = <String>{};
  for (final stage in stages) {
    for (final vowel in stage.adds.vowels) {
      if (vowelSet.add(vowel)) {
        vowels.add(vowel);
      }
    }
    for (final consonant in stage.adds.consonants) {
      if (consonantSet.add(consonant)) {
        consonants.add(consonant);
      }
    }
    if (stage.id == currentStage.id) {
      break;
    }
  }
  return StageInventory(vowels: vowels, consonants: consonants);
});

class StageCompletionState extends StateNotifier<Set<String>> {
  StageCompletionState() : super(<String>{});

  void markCompleted(String stageId) {
    if (stageId.isEmpty) return;
    state = Set<String>.from(state)..add(stageId);
  }

  void revertFrom(String stageId, List<StageDefinition> stages) {
    if (stageId.isEmpty) return;
    final index = stages.indexWhere((stage) => stage.id == stageId);
    if (index < 0) {
      state = Set<String>.from(state)..remove(stageId);
      return;
    }
    final removeIds = stages.sublist(index).map((stage) => stage.id).toSet();
    state = Set<String>.from(state)..removeAll(removeIds);
  }

  void reset() {
    state = <String>{};
  }
}

final stageCompletionProvider = StateNotifierProvider<StageCompletionState, Set<String>>(
  (ref) => StageCompletionState(),
);

final stageNavigationListenerProvider = Provider<void>((ref) {
  ref.listen<StageDefinition?>(currentStageProvider, (previous, next) {
    if (next == null || previous?.id == next.id) return;
    final nav = ref.read(navigationStateProvider);
    final modes = next.allowModes;
    String? nextMode;
    if (next.adds.consonants.isNotEmpty && modes.consonants) {
      nextMode = 'Consonants';
    } else if (next.adds.vowels.isNotEmpty && modes.vowels) {
      nextMode = 'Vowels';
    }
    if (nav.mode == 'Vowels' && !modes.vowels) {
      nextMode = modes.consonants
          ? 'Consonants'
          : modes.syllables
              ? 'Syllables'
              : null;
    } else if (nav.mode == 'Consonants' && !modes.consonants) {
      nextMode = modes.vowels
          ? 'Vowels'
          : modes.syllables
              ? 'Syllables'
              : null;
    } else if (nav.mode == 'Syllables' && !modes.syllables) {
      nextMode = modes.vowels
          ? 'Vowels'
          : modes.consonants
              ? 'Consonants'
              : null;
    }
    if (nextMode != null) {
      ref.read(navigationStateProvider.notifier).setMode(nextMode);
    } else {
      ref.read(navigationStateProvider.notifier).setIndex(0);
    }
  });
});
