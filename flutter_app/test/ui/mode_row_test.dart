import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hangul_flutter/domain/stages.dart';
import 'package:hangul_flutter/state/stage_state.dart';
import 'package:hangul_flutter/state/data_providers.dart';
import 'package:hangul_flutter/ui/widgets/panels/mode_row.dart';
import 'package:hangul_flutter/services/stage_store.dart';

void main() {
  testWidgets('lesson dropdown disables locked lessons', (tester) async {
    const stages = [
      StageDefinition(
        id: 'stage_01_vowels_starter',
        name: 'Starter vowels: ㅏ ㅓ ㅗ ㅜ ㅡ',
        description: 'Starter vowels',
        allowModes: StageModes(vowels: true, consonants: false, syllables: false),
        adds: StageAdds(vowels: ['ㅏ'], consonants: []),
      ),
      StageDefinition(
        id: 'stage_02_consonants_basic_1',
        name: 'Basic consonants: ㄱ ㄴ ㄷ ㄹ ㅁ',
        description: 'Basic consonants set 1',
        allowModes: StageModes(vowels: true, consonants: true, syllables: true),
        adds: StageAdds(vowels: [], consonants: ['ㄱ']),
      ),
      StageDefinition(
        id: 'stage_03_consonants_basic_2',
        name: 'Basic consonants: add ㅂ ㅅ ㅇ ㅈ ㅎ',
        description: 'Basic consonants set 2',
        allowModes: StageModes(vowels: true, consonants: true, syllables: true),
        adds: StageAdds(vowels: [], consonants: ['ㅂ']),
      ),
    ];

    final container = ProviderContainer(
      overrides: [
        stagesProvider.overrideWith((ref) async => stages),
        stageStateProvider.overrideWith((ref) => StageState(_TestStageStore())),
        stageCompletionProvider.overrideWith((ref) {
          final state = StageCompletionState();
          state.markCompleted('stage_02_consonants_basic_1');
          return state;
        }),
      ],
    );
    addTearDown(container.dispose);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: Scaffold(body: ModeRow())),
      ),
    );
    await tester.pump();

    final dropdown = tester.widget<DropdownButton<String>>(find.byType(DropdownButton<String>));
    final items = dropdown.items ?? <DropdownMenuItem<String>>[];
    expect(items.length, 3);
    expect(items[0].enabled, isTrue);
    expect(items[1].enabled, isTrue);
    expect(items[2].enabled, isFalse);
  });
}

class _TestStageStore extends StageStore {
  @override
  Future<void> saveStage(String stageId) async {}
}
