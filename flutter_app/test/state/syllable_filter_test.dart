import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:hangul_flutter/state/data_providers.dart';
import 'package:hangul_flutter/state/syllable_options_state.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('core syllable filter uses only core vowels', (tester) async {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    container.read(syllableVowelSetProvider.notifier).hydrate(SyllableVowelSet.core);
    final items = await container.read(filteredSyllablesProvider.future);

    const coreVowels = {'ㅏ', 'ㅓ', 'ㅗ', 'ㅜ', 'ㅡ', 'ㅣ'};
    expect(items, isNotEmpty);
    for (final item in items) {
      expect(coreVowels.contains(item.vowel), isTrue, reason: 'Non-core vowel: ${item.vowel}');
    }
  });
}
