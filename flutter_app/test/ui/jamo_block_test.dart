import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:flutter/material.dart';

import 'package:hangul_flutter/domain/models.dart';
import 'package:hangul_flutter/state/data_providers.dart';
import 'package:hangul_flutter/ui/widgets/jamo_block/jamo_block.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('jamo block shows empty segment for vowels and syllables', (tester) async {
    const vowelItem = StudyItem(
      mode: 'Vowels',
      glyph: '아',
      consonant: '',
      vowel: 'ㅏ',
      blockType: 'A_RightBranch',
    );
    const syllableItem = StudyItem(
      mode: 'Syllables',
      glyph: '가',
      consonant: 'ㄱ',
      vowel: 'ㅏ',
      blockType: 'A_RightBranch',
    );

    await tester.pumpWidget(_buildWithItem(vowelItem));
    expect(find.text('Empty'), findsWidgets);

    await tester.pumpWidget(_buildWithItem(syllableItem));
    expect(find.text('Empty'), findsWidgets);
  });
}

Widget _buildWithItem(StudyItem item) {
  return ProviderScope(
    overrides: [
      currentItemProvider.overrideWithValue(AsyncValue.data(item)),
    ],
    child: const MaterialApp(
      home: Scaffold(
        body: SizedBox(width: 200, height: 200, child: JamoBlock()),
      ),
    ),
  );
}
