import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../state/navigation_state.dart';
import '../../../state/syllable_options_state.dart';
import '../../screens/settings_screen.dart';

class ModeRow extends ConsumerWidget {
  const ModeRow({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nav = ref.watch(navigationStateProvider);
    final syllableSet = ref.watch(syllableVowelSetProvider);
    return Row(
      children: [
        DropdownButton<String>(
          value: nav.mode,
          items: const [
            DropdownMenuItem(value: 'Vowels', child: Text('Vowels')),
            DropdownMenuItem(value: 'Consonants', child: Text('Consonants')),
            DropdownMenuItem(value: 'Syllables', child: Text('Syllables')),
            DropdownMenuItem(value: 'Words', child: Text('Words')),
          ],
          onChanged: (value) {
            if (value == null) return;
            ref.read(navigationStateProvider.notifier).setMode(value);
          },
        ),
        if (nav.mode == 'Syllables') ...[
          const SizedBox(width: 8),
          Tooltip(
            message: syllableVowelSetHint(syllableSet),
            waitDuration: const Duration(milliseconds: 300),
            child: DropdownButton<SyllableVowelSet>(
              value: syllableSet,
              items: SyllableVowelSet.values
                  .map(
                    (set) => DropdownMenuItem(
                      value: set,
                      child: Text(syllableVowelSetLabel(set, compact: true)),
                    ),
                  )
                  .toList(),
              onChanged: (value) {
                if (value == null) return;
                ref.read(syllableVowelSetProvider.notifier).set(value);
              },
            ),
          ),
        ],
        const Spacer(),
        IconButton(
          icon: const Icon(Icons.settings),
          tooltip: 'Settings',
          onPressed: () {
            Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const SettingsScreen()),
            );
          },
        ),
        Builder(
          builder: (context) {
            return Tooltip(
              message: 'Open or close the settings drawer',
              waitDuration: const Duration(milliseconds: 300),
              child: IconButton(
                icon: const Icon(Icons.menu),
                tooltip: 'Open or close the settings drawer',
                onPressed: () {
                  Scaffold.of(context).openDrawer();
                },
              ),
            );
          },
        ),
      ],
    );
  }
}
