import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../state/data_providers.dart';
import '../../../state/navigation_state.dart';

class NotesPanel extends ConsumerWidget {
  const NotesPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mode = ref.watch(navigationStateProvider).mode;
    if (mode != 'Vowels') {
      return const SizedBox.shrink();
    }
    final itemAsync = ref.watch(currentItemProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: itemAsync.when(
          data: (item) {
            final vowel = item.vowel.isEmpty ? 'ㅏ' : item.vowel;
            final syllable = item.glyph.isEmpty ? '아' : item.glyph;
            return Text(
              'Standalone vowels are written with a silent ㅇ onset, so $vowel is written as $syllable (ㅇ + $vowel).',
            );
          },
          loading: () => const SizedBox.shrink(),
          error: (err, _) => Text('Notes error: $err'),
        ),
      ),
    );
  }
}
