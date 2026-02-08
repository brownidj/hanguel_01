import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../state/data_providers.dart';
import '../../../state/settings_state.dart';
import '../../styles/colors.dart';
import 'templates.dart';

class JamoBlock extends ConsumerWidget {
  const JamoBlock({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final itemAsync = ref.watch(currentItemProvider);
    final themeName = ref.watch(settingsStateProvider).theme;
    final palette = paletteForTheme(themeName);
    return Card(
      color: palette.jamoBackground,
      child: AspectRatio(
        aspectRatio: 1.0,
        child: itemAsync.when(
          data: (item) {
            final index = _blockIndex(item.blockType);
            final isVowelMode = item.mode == 'Vowels';
            final leadingConsonant = isVowelMode ? 'ㅇ' : item.consonant;
            const silentStyle = TextStyle(
              fontSize: 64,
              fontWeight: FontWeight.w600,
              color: Color(0xFFF0F0F0),
            );
            final leadingStyle = isVowelMode ? silentStyle : null;
            final leadingTooltip = isVowelMode
                ? 'Silent leading consonant'
                : item.consonant.isEmpty
                    ? ''
                    : 'Leading consonant';
            return IndexedStack(
              index: index,
              children: [
                RightBranchTemplate(
                  topText: leadingConsonant,
                  middleText: item.vowel,
                  bottomText: '',
                  topTooltip: leadingTooltip,
                  middleTooltip: item.vowel.isEmpty ? '' : 'Vowel',
                  bottomTooltip: '',
                  topStyle: leadingStyle,
                ),
                TopBranchTemplate(
                  topText: leadingConsonant,
                  middleText: item.vowel,
                  bottomText: '',
                  topTooltip: leadingTooltip,
                  middleTooltip: item.vowel.isEmpty ? '' : 'Vowel',
                  bottomTooltip: '',
                  topStyle: leadingStyle,
                ),
                BottomBranchTemplate(
                  topText: leadingConsonant,
                  middleText: item.vowel,
                  bottomText: '',
                  topTooltip: leadingTooltip,
                  middleTooltip: item.vowel.isEmpty ? '' : 'Vowel',
                  bottomTooltip: '',
                  topStyle: leadingStyle,
                ),
                HorizontalTemplate(
                  topText: leadingConsonant,
                  middleText: item.vowel,
                  bottomText: '',
                  topTooltip: leadingTooltip,
                  middleTooltip: item.vowel.isEmpty ? '' : 'Vowel',
                  bottomTooltip: '',
                  topStyle: leadingStyle,
                ),
              ],
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (err, _) => Center(child: Text('Error: $err')),
        ),
      ),
    );
  }
}

int _blockIndex(String blockType) {
  switch (blockType) {
    case 'B_TopBranch':
      return 1;
    case 'C_BottomBranch':
      return 2;
    case 'D_Horizontal':
      return 3;
    case 'A_RightBranch':
    default:
      return 0;
  }
}
