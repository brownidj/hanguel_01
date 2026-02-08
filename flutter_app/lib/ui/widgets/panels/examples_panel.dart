import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../domain/models.dart';
import '../../../domain/compose.dart';
import '../../../data/repositories/examples_repository.dart';
import '../../../state/data_providers.dart';
import '../../../state/navigation_state.dart';
import '../../../state/audio_service_provider.dart';
import '../../../state/settings_state.dart';
import '../../../state/playback_state.dart';

class ExamplesPanel extends ConsumerWidget {
  const ExamplesPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nav = ref.watch(navigationStateProvider);
    final examplesIndexAsync = ref.watch(examplesIndexProvider);
    final itemAsync = ref.watch(currentItemProvider);
    final settings = ref.watch(settingsStateProvider);
    final playback = ref.watch(playbackStateProvider);
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Text(
              'Example',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: examplesIndexAsync.when(
              data: (index) {
                return itemAsync.when(
                  data: (item) {
                    final example = _pickExample(index, nav.mode, item, nav.index);
                    // ignore: avoid_print
                    print('[DEBUG] Example pick mode=${nav.mode} glyph=${item.glyph} consonant=${item.consonant} '
                        'vowel=${item.vowel} result=${example?.hangul ?? "none"}');
                    if (example == null) {
                      return const Center(child: Text('No example'));
                    }
                    return LayoutBuilder(
                      builder: (context, constraints) {
                        final maxByHeight = constraints.maxHeight * 0.4;
                        final maxByWidth = constraints.maxWidth * 0.8;
                        final imageSize = [160.0, maxByHeight, maxByWidth].reduce((a, b) => a < b ? a : b);
                        const buttonHeight = 36.0;
                        return Padding(
                          padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
                          child: Stack(
                            children: [
                              Positioned.fill(
                                child: LayoutBuilder(
                                  builder: (context, innerConstraints) {
                                    const hangulStyle = TextStyle(fontSize: 30, fontWeight: FontWeight.bold);
                                    const metaStyle = TextStyle(fontSize: 14);
                                    const spacing = 6.0;

                                    double measureLineHeight(String text, TextStyle style) {
                                      final painter = TextPainter(
                                        text: TextSpan(text: text, style: style),
                                        maxLines: 1,
                                        textDirection: TextDirection.ltr,
                                      )..layout(maxWidth: innerConstraints.maxWidth);
                                      return painter.height;
                                    }

                                    final hangulHeight = measureLineHeight(example.hangul, hangulStyle);
                                    final rrHeight = measureLineHeight('Say it: ${example.rr}', metaStyle);
                                    final glossHeight = measureLineHeight(example.glossEn, metaStyle);
                                    final reserved = hangulHeight +
                                        rrHeight +
                                        glossHeight +
                                        spacing * 3 +
                                        buttonHeight +
                                        spacing;
                                    final availableHeight = innerConstraints.maxHeight - reserved;
                                    final maxByWidth = innerConstraints.maxWidth * 0.8;
                                    final maxImage = [
                                      imageSize,
                                      maxByWidth,
                                      availableHeight,
                                    ].reduce((a, b) => a < b ? a : b);
                                    final imageEdge = maxImage.isFinite && maxImage > 0 ? maxImage : 0.0;

                                    return SingleChildScrollView(
                                      padding: const EdgeInsets.only(bottom: buttonHeight + spacing),
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                    Text.rich(
                                      _buildHighlightedHangul(
                                        example.hangul,
                                        _highlightTarget(nav.mode, item.consonant, item.vowel, example),
                                        true,
                                      ),
                                      key: const ValueKey('example-hangul'),
                                      style: hangulStyle,
                                    ),
                                          const SizedBox(height: spacing),
                                          Center(
                                            child: Tooltip(
                                              message: example.imagePrompt,
                                              waitDuration: const Duration(milliseconds: 300),
                                              child: SizedBox(
                                                width: imageEdge,
                                                height: imageEdge,
                                                child: example.imageFilename.isEmpty
                                                    ? const SizedBox.shrink()
                                                    : Image.asset(
                                                        'assets/images/examples/${example.imageFilename}',
                                                        key: const ValueKey('example-image'),
                                                        fit: BoxFit.contain,
                                                      ),
                                              ),
                                            ),
                                          ),
                                          const SizedBox(height: spacing),
                                          Text(example.glossEn, style: metaStyle),
                                          Text('Say it: ${example.rr}', style: metaStyle),
                                        ],
                                      ),
                                    );
                                  },
                                ),
                              ),
                              Positioned(
                                right: 0,
                                bottom: 0,
                                child: SizedBox(
                                  height: buttonHeight,
                                  child: ElevatedButton(
                                    onPressed: playback.autoEnabled || !playback.controlsEnabled || !playback.heardOnce
                                        ? null
                                        : () async {
                                            await ref
                                                .read(audioServiceProvider)
                                                .playGlyph(example.hangul, wpm: settings.effectiveWpm);
                                          },
                                    child: const Icon(Icons.hearing, size: 18),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    );
                  },
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (err, _) => Center(child: Text('Examples error: $err')),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, _) => Center(child: Text('Examples error: $err')),
            ),
          ),
        ],
      ),
    );
  }
}

ExampleItem? _pickExample(ExamplesIndex index, String mode, StudyItem item, int currentIndex) {
  if (mode == 'Vowels') {
    final list = index.byVowel[item.vowel] ?? const [];
    final vowelFirst = list.where((entry) => entry.startsWithConsonant == 'ㅇ').toList();
    final candidates = vowelFirst.isNotEmpty ? vowelFirst : list;
    return _pickFromCandidates(candidates, key: item.vowel, baseIndex: currentIndex);
  }
  if (mode == 'Consonants') {
    final list = index.byConsonant[item.consonant] ?? const [];
    return _pickFromCandidates(list, key: item.consonant, baseIndex: currentIndex);
  }
  final syllable = item.glyph.isNotEmpty ? item.glyph : composeCv(item.consonant, item.vowel);
  final syllableList = index.bySyllable[syllable] ?? const [];
  if (syllableList.isNotEmpty) {
    return _pickFromCandidates(syllableList, key: syllable, baseIndex: currentIndex);
  }
  final consonantList = index.byConsonant[item.consonant] ?? const [];
  if (consonantList.isNotEmpty) {
    return _pickFromCandidates(consonantList, key: item.consonant, baseIndex: currentIndex);
  }
  final vowelList = index.byVowel[item.vowel] ?? const [];
  return _pickFromCandidates(vowelList, key: item.vowel, baseIndex: currentIndex);
}

ExampleItem? _pickFromCandidates(
  List<ExampleItem> candidates, {
  required String key,
  required int baseIndex,
  int offset = 0,
}) {
  if (candidates.isEmpty) return null;
  final keyWeight = key.runes.fold<int>(0, (sum, value) => sum + value);
  final idx = (baseIndex + keyWeight + offset) % candidates.length;
  return candidates[idx];
}

TextSpan _buildHighlightedHangul(String hangul, String syllable, bool highlight) {
  if (!highlight || hangul.isEmpty || syllable.isEmpty) {
    return TextSpan(text: hangul);
  }
  final index = hangul.indexOf(syllable);
  if (index < 0) {
    return TextSpan(text: hangul);
  }
  final before = hangul.substring(0, index);
  final target = hangul.substring(index, index + syllable.length);
  final after = hangul.substring(index + syllable.length);
  return TextSpan(
    children: [
      if (before.isNotEmpty) TextSpan(text: before),
      TextSpan(text: target, style: const TextStyle(color: Color(0xFFFF7A00))),
      if (after.isNotEmpty) TextSpan(text: after),
    ],
  );
}

String _highlightTarget(String mode, String consonant, String vowel, ExampleItem example) {
  if (mode == 'Consonants' && consonant.isNotEmpty) {
    final target = _findSyllableForConsonant(example.hangul, consonant);
    if (target.isNotEmpty) {
      return target;
    }
  }
  if (mode == 'Vowels' && vowel.isNotEmpty) {
    final target = _findSyllableForVowel(example.hangul, vowel);
    if (target.isNotEmpty) {
      return target;
    }
  }
  return example.startsWithSyllable;
}

String _findSyllableForConsonant(String word, String consonant) {
  for (final rune in word.runes) {
    final syllable = String.fromCharCode(rune);
    final components = _decomposeSyllable(syllable);
    if (components != null) {
      final initial = components.initial;
      final finalConsonant = components.finalConsonant;
      if (initial == consonant || finalConsonant == consonant) {
        return syllable;
      }
    }
  }
  return '';
}

String _findSyllableForVowel(String word, String vowel) {
  for (final rune in word.runes) {
    final syllable = String.fromCharCode(rune);
    final components = _decomposeSyllable(syllable);
    if (components != null) {
      final mid = components.vowel;
      if (mid == vowel) {
        return syllable;
      }
    }
  }
  return '';
}

({String initial, String vowel, String finalConsonant})? _decomposeSyllable(String syllable) {
  if (syllable.isEmpty) return null;
  final code = syllable.codeUnitAt(0);
  if (code < 0xAC00 || code > 0xD7A3) return null;
  final index = code - 0xAC00;
  final choIndex = index ~/ 588;
  final jungIndex = (index % 588) ~/ 28;
  final jongIndex = index % 28;
  if (choIndex < 0 || choIndex >= _compatCho.length) return null;
  if (jungIndex < 0 || jungIndex >= _compatJung.length) return null;
  if (jongIndex < 0 || jongIndex >= _compatJong.length) return null;
  return (
    initial: _compatCho[choIndex],
    vowel: _compatJung[jungIndex],
    finalConsonant: _compatJong[jongIndex],
  );
}

const List<String> _compatCho = [
  'ㄱ',
  'ㄲ',
  'ㄴ',
  'ㄷ',
  'ㄸ',
  'ㄹ',
  'ㅁ',
  'ㅂ',
  'ㅃ',
  'ㅅ',
  'ㅆ',
  'ㅇ',
  'ㅈ',
  'ㅉ',
  'ㅊ',
  'ㅋ',
  'ㅌ',
  'ㅍ',
  'ㅎ',
];

const List<String> _compatJung = [
  'ㅏ',
  'ㅐ',
  'ㅑ',
  'ㅒ',
  'ㅓ',
  'ㅔ',
  'ㅕ',
  'ㅖ',
  'ㅗ',
  'ㅘ',
  'ㅙ',
  'ㅚ',
  'ㅛ',
  'ㅜ',
  'ㅝ',
  'ㅞ',
  'ㅟ',
  'ㅠ',
  'ㅡ',
  'ㅢ',
  'ㅣ',
];

const List<String> _compatJong = [
  '',
  'ㄱ',
  'ㄲ',
  'ㄳ',
  'ㄴ',
  'ㄵ',
  'ㄶ',
  'ㄷ',
  'ㄹ',
  'ㄺ',
  'ㄻ',
  'ㄼ',
  'ㄽ',
  'ㄾ',
  'ㄿ',
  'ㅀ',
  'ㅁ',
  'ㅂ',
  'ㅄ',
  'ㅅ',
  'ㅆ',
  'ㅇ',
  'ㅈ',
  'ㅊ',
  'ㅋ',
  'ㅌ',
  'ㅍ',
  'ㅎ',
];
