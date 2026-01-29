import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:hangul_flutter/app.dart';
import 'package:hangul_flutter/state/settings_state.dart';

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
    expect(find.text('Presets'), findsOneWidget);
    expect(find.text('Repeats'), findsOneWidget);
    expect(find.text('About'), findsNothing);
  });

  testWidgets('example panel uses vowel examples', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: App()));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

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
