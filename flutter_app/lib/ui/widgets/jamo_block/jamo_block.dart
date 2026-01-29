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
            return IndexedStack(
              index: index,
              children: [
                RightBranchTemplate(
                  topText: item.consonant,
                  middleText: item.vowel,
                  bottomText: '',
                  topTooltip: item.consonant.isEmpty ? '' : 'Leading consonant',
                  middleTooltip: item.vowel.isEmpty ? '' : 'Vowel',
                  bottomTooltip: '',
                ),
                TopBranchTemplate(
                  topText: item.consonant,
                  middleText: item.vowel,
                  bottomText: '',
                  topTooltip: item.consonant.isEmpty ? '' : 'Leading consonant',
                  middleTooltip: item.vowel.isEmpty ? '' : 'Vowel',
                  bottomTooltip: '',
                ),
                BottomBranchTemplate(
                  topText: item.consonant,
                  middleText: item.vowel,
                  bottomText: '',
                  topTooltip: item.consonant.isEmpty ? '' : 'Leading consonant',
                  middleTooltip: item.vowel.isEmpty ? '' : 'Vowel',
                  bottomTooltip: '',
                ),
                HorizontalTemplate(
                  topText: item.consonant,
                  middleText: item.vowel,
                  bottomText: '',
                  topTooltip: item.consonant.isEmpty ? '' : 'Leading consonant',
                  middleTooltip: item.vowel.isEmpty ? '' : 'Vowel',
                  bottomTooltip: '',
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
