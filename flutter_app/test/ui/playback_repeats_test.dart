import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:hangul_flutter/domain/models.dart';
import 'package:hangul_flutter/services/audio_service.dart';
import 'package:hangul_flutter/state/audio_service_provider.dart';
import 'package:hangul_flutter/state/data_providers.dart';
import 'package:hangul_flutter/state/navigation_state.dart';
import 'package:hangul_flutter/state/settings_state.dart';
import 'package:hangul_flutter/state/stage_state.dart';
import 'package:hangul_flutter/ui/widgets/panels/syllable_panel.dart';
import 'package:hangul_flutter/services/navigation_store.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('hear button repeats using selected repeats', (tester) async {
    final playCalls = <String>[];
    final audioService = AudioService.testing(
      playAsset: (assetPath) async {
        playCalls.add(assetPath);
      },
    );

    const item = StudyItem(
      mode: 'Vowels',
      glyph: 'ㅏ',
      consonant: '',
      vowel: 'ㅏ',
      blockType: '',
    );

    final container = ProviderContainer(
      overrides: [
        audioServiceProvider.overrideWithValue(audioService),
        currentItemProvider.overrideWithValue(const AsyncValue.data(item)),
        currentItemsProvider.overrideWithValue(const AsyncValue.data([item])),
        currentStageProvider.overrideWithValue(null),
        stageInventoryProvider.overrideWithValue(const StageInventory.empty()),
        navigationStateProvider.overrideWith((ref) {
          final nav = NavigationState(NavigationStore());
          nav.setMode('Vowels');
          return nav;
        }),
      ],
    );
    addTearDown(container.dispose);

    container.read(settingsStateProvider.notifier).setRepeats(3);
    container.read(settingsStateProvider.notifier).setDelayBeforeFirstPlay(0.0);
    container.read(settingsStateProvider.notifier).setDelayBetweenRepeats(0.0);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: Scaffold(
            body: SyllablePanel(),
          ),
        ),
      ),
    );
    await tester.pump();

    await tester.tap(find.byIcon(Icons.hearing));
    await tester.pumpAndSettle();

    expect(playCalls.length, 3);
  });
}
