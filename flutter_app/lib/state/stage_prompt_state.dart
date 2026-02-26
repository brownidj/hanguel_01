import 'package:flutter_riverpod/flutter_riverpod.dart';

class StagePromptSnapshot {
  final String lastPromptedStageId;

  const StagePromptSnapshot({required this.lastPromptedStageId});
}

class StagePromptState extends StateNotifier<StagePromptSnapshot> {
  StagePromptState() : super(const StagePromptSnapshot(lastPromptedStageId: ''));

  bool shouldPrompt(String stageId) {
    return stageId.isNotEmpty && stageId != state.lastPromptedStageId;
  }

  void markPrompted(String stageId) {
    if (stageId.isEmpty || stageId == state.lastPromptedStageId) return;
    state = StagePromptSnapshot(lastPromptedStageId: stageId);
  }

  void reset() {
    state = const StagePromptSnapshot(lastPromptedStageId: '');
  }
}

final stagePromptProvider = StateNotifierProvider<StagePromptState, StagePromptSnapshot>(
  (ref) => StagePromptState(),
);
