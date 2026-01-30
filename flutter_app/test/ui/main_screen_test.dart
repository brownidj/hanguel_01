import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:hangul_flutter/app.dart';
import 'package:hangul_flutter/data/repositories/examples_repository.dart';
import 'package:hangul_flutter/domain/models.dart';
import 'package:hangul_flutter/state/data_providers.dart';
import 'package:hangul_flutter/state/navigation_state.dart';
import 'package:hangul_flutter/state/settings_state.dart';
import 'package:hangul_flutter/services/navigation_store.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('main screen renders', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: App()));
    expect(find.byType(MaterialApp), findsOneWidget);
  });

  testWidgets('theme switch updates scaffold background', (tester) async {
    final container = ProviderContainer();
    addTearDown(container.dispose);
    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const App(),
      ),
    );
    await tester.pump();
    final materialApp = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(materialApp.theme?.scaffoldBackgroundColor, const Color(0xFFE6F2F8));

    container.read(settingsStateProvider.notifier).setTheme('Hanji');
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 350));
    final updatedApp = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(updatedApp.theme?.scaffoldBackgroundColor, const Color(0xFFFEFCF8));
  });

  testWidgets('drawer shows settings controls', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: App()));
    await tester.pump();
    await tester.tap(find.byIcon(Icons.menu));
    await tester.pump(const Duration(milliseconds: 200));
    expect(find.text('Words per minute'), findsOneWidget);
    expect(find.text('Preset pauses'), findsOneWidget);
    expect(find.text('Repeats'), findsOneWidget);
    expect(find.text('About'), findsNothing);
  });

  testWidgets('example panel uses vowel examples', (tester) async {
    const example = ExampleItem(
      hangul: '아기',
      rr: 'agi',
      glossEn: 'baby',
      startsWithSyllable: '아',
      startsWithConsonant: 'ㅇ',
      startsWithVowel: 'ㅏ',
      imagePrompt: 'Baby',
      imageFilename: '아기-baby.png',
    );
    final index = ExamplesIndex.fromItems([example]);
    const item = StudyItem(
      mode: 'Vowels',
      glyph: 'ㅏ',
      consonant: '',
      vowel: 'ㅏ',
      blockType: '',
    );
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          navigationStateProvider.overrideWith((ref) {
            final state = NavigationState(NavigationStore());
            state.setMode('Vowels');
            return state;
          }),
          currentItemProvider.overrideWithValue(const AsyncValue.data(item)),
          examplesIndexProvider.overrideWith((ref) async => index),
        ],
        child: const App(),
      ),
    );
    await tester.pump();
    final hangulKey = find.byKey(const ValueKey('example-hangul'));
    expect(hangulKey, findsOneWidget);

    final hangulWidget = tester.widget<Text>(
      hangulKey,
    );
    expect(hangulWidget.textSpan?.toPlainText().contains('아기'), isTrue);

    final imageWidget = tester.widget<Image>(
      find.byKey(const ValueKey('example-image')),
    );
    final image = imageWidget.image;
    expect(
      image is AssetImage &&
          image.assetName == 'assets/images/examples/아기-baby.png',
      isTrue,
    );
  });
}
