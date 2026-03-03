import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:hangul_flutter/app.dart';
import 'package:hangul_flutter/data/repositories/examples_repository.dart';
import 'package:hangul_flutter/data/repositories/vowels_repository.dart';
import 'package:hangul_flutter/domain/models.dart';
import 'package:hangul_flutter/state/data_providers.dart';
import 'package:hangul_flutter/state/settings_state.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  Future<void> pumpToMainScreen(WidgetTester tester, {List<Override> overrides = const []}) async {
    await tester.pumpWidget(ProviderScope(overrides: overrides, child: const App()));
    await tester.pump();
    if (find.text('Start').evaluate().isNotEmpty) {
      await tester.tap(find.text('Start'));
      await tester.pump();
    }
    await tester.pump(const Duration(milliseconds: 500));
  }

  Future<void> pumpUntilFound(WidgetTester tester, Finder finder) async {
    for (var i = 0; i < 20; i += 1) {
      if (finder.evaluate().isNotEmpty) {
        return;
      }
      await tester.runAsync(() async {
        await Future<void>.delayed(const Duration(milliseconds: 100));
      });
      await tester.pump();
    }
  }

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
    await pumpToMainScreen(tester);
    await tester.tap(find.byIcon(Icons.menu));
    await tester.pump(const Duration(milliseconds: 200));
    expect(find.text('Words per minute'), findsOneWidget);
    expect(find.text('Presets'), findsOneWidget);
    expect(find.text('Repeats'), findsOneWidget);
    expect(find.text('About'), findsNothing);
  });

  testWidgets('example panel uses vowel examples', (tester) async {
    await pumpToMainScreen(tester, overrides: [
      examplesRepositoryProvider.overrideWithValue(FakeExamplesRepository()),
      vowelsRepositoryProvider.overrideWithValue(FakeVowelsRepository()),
    ]);
    await pumpUntilFound(tester, find.text('아기'));

    expect(find.text('아기'), findsOneWidget);

    final imageFinder = find.byWidgetPredicate((widget) {
      if (widget is! Image) return false;
      final image = widget.image;
      return image is AssetImage &&
          image.assetName == 'assets/images/examples/아기-baby.png';
    });
    expect(imageFinder, findsOneWidget);
  });
}

class FakeExamplesRepository extends ExamplesRepository {
  @override
  Future<List<ExampleItem>> loadExamplesForMode(String mode) async {
    return [
      const ExampleItem(
        hangul: '아기',
        rr: 'agi',
        glossEn: 'baby',
        startsWithSyllable: '아',
        startsWithConsonant: '',
        startsWithVowel: 'ㅏ',
        imagePrompt: 'Baby',
        imageFilename: '아기-baby.png',
      ),
    ];
  }

  @override
  Future<ExamplesIndex> loadIndexedExamplesForMode(String mode) async {
    return ExamplesIndex.fromItems(await loadExamplesForMode(mode));
  }

  @override
  Future<ExamplesIndex> loadIndexedExamples() async {
    return ExamplesIndex.fromItems(await loadExamplesForMode('Vowels'));
  }
}

class FakeVowelsRepository extends VowelsRepository {
  @override
  Future<List<Map<String, dynamic>>> loadVowels() async {
    return [
      {'glyph': 'ㅏ'},
    ];
  }
}
