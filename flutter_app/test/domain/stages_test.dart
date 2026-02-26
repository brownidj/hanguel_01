import 'package:flutter_test/flutter_test.dart';

import 'package:hangul_flutter/data/repositories/stages_repository.dart';
import 'package:hangul_flutter/data/repositories/vowels_repository.dart';
import 'package:hangul_flutter/data/repositories/consonants_repository.dart';
import 'package:hangul_flutter/domain/stages.dart';
import 'package:hangul_flutter/state/stage_state.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('stages repository loads stages with review_pool', () async {
    final repo = StagesRepository();
    final stages = await repo.loadStages();
    expect(stages.isNotEmpty, isTrue);
    final stage10 = stages.firstWhere((s) => s.id == 'stage_10_aspirated_consonants');
    expect(stage10.reviewPool, isNotNull);
    expect(stage10.reviewPool?.vowels.isNotEmpty, isTrue);
  });

  test('stage inventory accumulates adds in order', () async {
    final repo = StagesRepository();
    final stages = await repo.loadStages();
    final index = stages.indexWhere((s) => s.id == 'stage_03_consonants_basic_2');
    expect(index >= 0, isTrue);
    final inventory = _accumulateInventory(stages, index);
    expect(inventory.vowels, contains('ㅏ'));
    expect(inventory.consonants, contains('ㄷ'));
    expect(inventory.consonants, contains('ㅈ'));
    expect(inventory.consonants, isNot(contains('ㅋ')));
  });

  test('review pool overrides accumulated inventory', () async {
    final repo = StagesRepository();
    final stages = await repo.loadStages();
    final stage10 = stages.firstWhere((s) => s.id == 'stage_10_aspirated_consonants');
    final inventory = stage10.reviewPool ?? const StageAdds(vowels: [], consonants: []);
    expect(inventory.vowels.contains('ㅘ'), isFalse);
    expect(inventory.vowels.contains('ㅏ'), isTrue);
    expect(inventory.consonants.contains('ㄲ'), isTrue);
  });

  test('stage inventory is subset of vowel and consonant inventories', () async {
    final vowelsRepo = VowelsRepository();
    final consonantsRepo = ConsonantsRepository();
    final stagesRepo = StagesRepository();
    final vowels = await vowelsRepo.loadVowels();
    final consonants = await consonantsRepo.loadConsonants();
    final stages = await stagesRepo.loadStages();

    final vowelSet = vowels.map((v) => '${v['glyph'] ?? ''}').where((g) => g.isNotEmpty).toSet();
    final consonantSet = consonants.map((c) => '${c['glyph'] ?? ''}').where((g) => g.isNotEmpty).toSet();

    final lastIndex = stages.length - 1;
    final inventory = _accumulateInventory(stages, lastIndex);
    expect(vowelSet.containsAll(inventory.vowels), isTrue);
    expect(consonantSet.containsAll(inventory.consonants), isTrue);
  });

  test('stage completion tracks completed lessons', () {
    final state = StageCompletionState();
    expect(state.state, isEmpty);
    state.markCompleted('stage_01_vowels_starter');
    state.markCompleted('stage_02_consonants_basic_1');
    expect(state.state.contains('stage_01_vowels_starter'), isTrue);
    expect(state.state.contains('stage_02_consonants_basic_1'), isTrue);
    const stages = [
      StageDefinition(
        id: 'stage_01_vowels_starter',
        name: 'Starter vowels',
        description: '',
        allowModes: StageModes.all(),
        adds: StageAdds(vowels: ['ㅏ'], consonants: []),
      ),
      StageDefinition(
        id: 'stage_02_consonants_basic_1',
        name: 'Basic consonants 1',
        description: '',
        allowModes: StageModes.all(),
        adds: StageAdds(vowels: [], consonants: ['ㄱ']),
      ),
      StageDefinition(
        id: 'stage_03_consonants_basic_2',
        name: 'Basic consonants 2',
        description: '',
        allowModes: StageModes.all(),
        adds: StageAdds(vowels: [], consonants: ['ㅂ']),
      ),
    ];
    state.markCompleted('stage_03_consonants_basic_2');
    state.revertFrom('stage_02_consonants_basic_1', stages);
    expect(state.state.contains('stage_01_vowels_starter'), isTrue);
    expect(state.state.contains('stage_02_consonants_basic_1'), isFalse);
    expect(state.state.contains('stage_03_consonants_basic_2'), isFalse);
    state.reset();
    expect(state.state, isEmpty);
  });
}

StageAdds _accumulateInventory(List<StageDefinition> stages, int index) {
  final vowels = <String>{};
  final consonants = <String>{};
  for (var i = 0; i <= index && i < stages.length; i += 1) {
    vowels.addAll(stages[i].adds.vowels);
    consonants.addAll(stages[i].adds.consonants);
  }
  return StageAdds(vowels: vowels.toList(), consonants: consonants.toList());
}
