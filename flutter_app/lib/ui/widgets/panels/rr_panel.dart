import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../domain/romanization_rr.dart';
import '../../../state/data_providers.dart';
import '../../../state/navigation_state.dart';
import '../../../state/settings_state.dart';

class RrPanel extends ConsumerWidget {
  const RrPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nav = ref.watch(navigationStateProvider);
    final itemAsync = ref.watch(currentItemProvider);
    final showCues = ref.watch(settingsStateProvider).showCues;
    final consonantsAsync = ref.watch(consonantsProvider);
    final vowelsAsync = ref.watch(vowelsProvider);
    final content = itemAsync.when(
      data: (item) {
        final result = romanizeCv(item.consonant, item.vowel);
        final consRr = _findRr(consonantsAsync, item.consonant);
        final vowelRr = _findRr(vowelsAsync, item.vowel);
        if (!showCues) {
          return _rrContent(rrValue: result.rr, hint: result.hint);
        }
        return _rrStructuredContent(
          mode: nav.mode,
          rrValue: result.rr,
          compactHint: result.hint,
          consonant: item.consonant,
          vowel: item.vowel,
          consRr: consRr,
          vowelRr: vowelRr,
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(child: Text('RR error: $err')),
    );

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Text(
              'Pronunciation Hints',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
              child: content,
            ),
          ),
          SwitchListTile(
            title: const Text('Show cues'),
            value: showCues,
            onChanged: (value) {
              ref.read(settingsStateProvider.notifier).setShowCues(value);
            },
          ),
        ],
      ),
    );
  }
}

Widget _rrContent({required String rrValue, required String hint}) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(rrValue, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600)),
      const SizedBox(height: 8),
      Text(hint),
    ],
  );
}

Widget _rrStructuredContent({
  required String mode,
  required String rrValue,
  required String compactHint,
  required String consonant,
  required String vowel,
  required Map<String, String> consRr,
  required Map<String, String> vowelRr,
}) {
  final blocks = <Widget>[];
  if (mode == 'Syllables') {
    if (consonant.isNotEmpty) {
      final heading = _compactWithBest(romanizeCv(consonant, '').hint, consRr);
      blocks.add(_rrBlock(heading: heading, rr: consRr));
    }
    if (vowel.isNotEmpty) {
      final heading = _compactWithBest(romanizeCv('', vowel).hint, vowelRr);
      blocks.add(_rrBlock(heading: heading, rr: vowelRr));
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(rrValue, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        ..._intersperse(blocks, const SizedBox(height: 12)),
      ],
    );
  }

  Map<String, String> rrData = {};
  if (mode == 'Vowels') {
    rrData = vowelRr;
  } else if (mode == 'Consonants') {
    rrData = consRr;
  }

  if (mode != 'Vowels' && consonant.isNotEmpty) {
    blocks.add(_rrBlock(rr: consRr));
  }
  if (mode != 'Consonants' && vowel.isNotEmpty) {
    blocks.add(_rrBlock(rr: vowelRr));
  }

  if (blocks.isEmpty) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(rrValue, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        Text(compactHint),
      ],
    );
  }

  final heading = _compactWithBest(compactHint, rrData);

  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(rrValue, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600)),
      const SizedBox(height: 8),
      Text(heading, style: const TextStyle(fontWeight: FontWeight.w600)),
      const SizedBox(height: 8),
      ..._intersperse(blocks, const SizedBox(height: 12)),
    ],
  );
}

Widget _rrBlock({String? heading, required Map<String, String> rr}) {
  final target = rr['target_sound'] ?? '';
  final alt = rr['alternative'] ?? '';
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      if (heading != null && heading.isNotEmpty)
        Text(
          heading,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
      if (target.isNotEmpty) Text('Target sound: $target'),
      if (alt.isNotEmpty) Text('Alternative (less good): $alt'),
    ],
  );
}

List<Widget> _intersperse(List<Widget> items, Widget spacer) {
  if (items.isEmpty) return items;
  final out = <Widget>[];
  for (var i = 0; i < items.length; i++) {
    out.add(items[i]);
    if (i != items.length - 1) out.add(spacer);
  }
  return out;
}

Map<String, String> _findRr(AsyncValue<List<Map<String, dynamic>>> itemsAsync, String glyph) {
  if (glyph.isEmpty) return {};
  return itemsAsync.maybeWhen(
    data: (items) {
      for (final item in items) {
        if ('${item['glyph'] ?? ''}' == glyph) {
          final rr = item['rr'];
          if (rr is Map) {
            return Map<String, String>.from(rr);
          }
          return {};
        }
      }
      return {};
    },
    orElse: () => {},
  );
}

String _compactWithBest(String hint, Map<String, String> rr) {
  final best = rr['best_approx'] ?? '';
  if (best.isEmpty || !hint.contains('as in')) return hint;
  return hint.replaceFirst(RegExp(r'as in\\s+[^,.]+'), best);
}
