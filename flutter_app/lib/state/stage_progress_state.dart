import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/stages.dart';
import 'data_providers.dart';
import 'navigation_state.dart';
import 'stage_state.dart';

class StageProgressSnapshot {
  final String stageId;
  final int cyclesCompleted;
  final int cyclesTarget;
  final bool isComplete;
  final int itemCount;
  final Set<String> playedGlyphs;

  const StageProgressSnapshot({
    required this.stageId,
    required this.cyclesCompleted,
    required this.cyclesTarget,
    required this.isComplete,
    required this.itemCount,
    required this.playedGlyphs,
  });

  const StageProgressSnapshot.empty()
      : stageId = '',
        cyclesCompleted = 0,
        cyclesTarget = 0,
        isComplete = false,
        itemCount = 0,
        playedGlyphs = const {};
}

class StageProgressState extends StateNotifier<StageProgressSnapshot> {
  StageProgressState() : super(const StageProgressSnapshot.empty());

  void resetForStage(String stageId, StageMasteryGate? gate) {
    final cycles = gate?.type == 'full_cycles' ? gate?.cycles ?? 0 : 0;
    state = StageProgressSnapshot(
      stageId: stageId,
      cyclesCompleted: 0,
      cyclesTarget: cycles,
      isComplete: false,
      itemCount: 0,
      playedGlyphs: const {},
    );
  }

  void recordPlay(String glyph, int itemCount) {
    if (state.cyclesTarget <= 0 || itemCount <= 0) return;
    final normalizedItemCount = itemCount < 0 ? 0 : itemCount;
    var cyclesCompleted = state.cyclesCompleted;
    var played = state.playedGlyphs;
    if (state.itemCount != normalizedItemCount) {
      played = <String>{};
    }
    if (glyph.isNotEmpty) {
      played = Set<String>.from(played)..add(glyph);
    }
    if (played.length >= normalizedItemCount) {
      played = <String>{};
      cyclesCompleted += 1;
    }
    state = StageProgressSnapshot(
      stageId: state.stageId,
      cyclesCompleted: cyclesCompleted,
      cyclesTarget: state.cyclesTarget,
      isComplete: cyclesCompleted >= state.cyclesTarget,
      itemCount: normalizedItemCount,
      playedGlyphs: played,
    );
  }

  void reset() {
    state = const StageProgressSnapshot.empty();
  }
}

final stageProgressProvider = StateNotifierProvider<StageProgressState, StageProgressSnapshot>(
  (ref) => StageProgressState(),
);

final stageProgressListenerProvider = Provider<void>((ref) {
  ref.listen<StageDefinition?>(currentStageProvider, (previous, next) {
    if (next == null) return;
    if (previous?.id == next.id) return;
    ref.read(stageProgressProvider.notifier).resetForStage(next.id, next.masteryGate);
  });
});

final stageModeCycleListenerProvider = Provider<void>((ref) {
  ref.listen<StageProgressSnapshot>(stageProgressProvider, (previous, next) {
    if (previous == null) return;
    if (next.isComplete) return;
    if (next.cyclesCompleted <= previous.cyclesCompleted) return;
    final stage = ref.read(currentStageProvider);
    if (stage == null) return;
    if (stage.id != 'stage_11_full_review') return;
    final mode = ref.read(navigationStateProvider).mode;
    if (mode == 'Consonants' && stage.allowModes.vowels) {
      ref.read(navigationStateProvider.notifier).setMode('Vowels');
    } else if (mode == 'Vowels' && stage.allowModes.consonants) {
      ref.read(navigationStateProvider.notifier).setMode('Consonants');
    }
  });
});
