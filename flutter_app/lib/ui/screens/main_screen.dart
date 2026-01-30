import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../state/persistence_providers.dart';
import '../../state/playback_state.dart';
import '../../state/settings_state.dart';
import '../widgets/jamo_block/jamo_block.dart';
import '../widgets/panels/examples_panel.dart';
import '../widgets/panels/mode_row.dart';
import '../widgets/panels/notes_panel.dart';
import '../widgets/panels/rr_panel.dart';
import '../widgets/panels/syllable_panel.dart';

class MainScreen extends ConsumerWidget {
  const MainScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(playbackModeResetProvider);
    ref.watch(settingsHydrationProvider);
    ref.watch(navigationHydrationProvider);
    ref.watch(syllableVowelSetHydrationProvider);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!kDebugMode) return;
      final size = MediaQuery.of(context).size;
      final dpr = MediaQuery.of(context).devicePixelRatio;
      // ignore: avoid_print
      print(
          '[DEBUG] screen logical=$size dpr=$dpr physical=${size.width * dpr}x${size.height * dpr}');
    });
    return Scaffold(
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: const [
            SizedBox(height: 86),
            Padding(
              padding: EdgeInsets.fromLTRB(12, 0, 12, 6),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Quick changes',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
              ),
            ),
            _DrawerSettings(),
          ],
        ),
      ),
      body: const SafeArea(
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 6),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ModeRow(),
              SizedBox(height: 6),
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(
                      flex: 9,
                      child: _SizedPanelDebug(
                          name: 'JamoPanel', child: JamoBlock()),
                    ),
                    SizedBox(width: 6),
                    Expanded(
                      flex: 11,
                      child: _SizedPanelDebug(
                          name: 'SyllablePanel', child: SyllablePanel()),
                    ),
                  ],
                ),
              ),
              SizedBox(height: 6),
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(
                      flex: 1,
                      child:
                          _SizedPanelDebug(name: 'RrPanel', child: RrPanel()),
                    ),
                    SizedBox(width: 6),
                    Expanded(
                      flex: 1,
                      child: _SizedPanelDebug(
                          name: 'ExamplesPanel', child: ExamplesPanel()),
                    ),
                  ],
                ),
              ),
              SizedBox(height: 6),
              _SizedPanelDebug(name: 'NotesPanel', child: NotesPanel()),
            ],
          ),
        ),
      ),
    );
  }
}

class _SizedPanelDebug extends StatelessWidget {
  const _SizedPanelDebug({required this.name, required this.child});

  final String name;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (!kDebugMode) return;
          final dpr = MediaQuery.of(context).devicePixelRatio;
          final w = constraints.maxWidth;
          final h = constraints.maxHeight;
          // ignore: avoid_print
          print(
              '[DEBUG] $name logical=${w.toStringAsFixed(1)}x${h.toStringAsFixed(1)} '
              'physical=${(w * dpr).toStringAsFixed(1)}x${(h * dpr).toStringAsFixed(1)}');
        });
        return child;
      },
    );
  }
}

class _DrawerSettings extends ConsumerStatefulWidget {
  const _DrawerSettings();

  @override
  ConsumerState<_DrawerSettings> createState() => _DrawerSettingsState();
}

class _DrawerSettingsState extends ConsumerState<_DrawerSettings> {
  bool _showWpmHelp = false;
  bool _showPresetsHelp = false;
  bool _showRepeatsHelp = false;
  Timer? _wpmTimer;
  Timer? _presetsTimer;
  Timer? _repeatsTimer;

  @override
  void dispose() {
    _wpmTimer?.cancel();
    _presetsTimer?.cancel();
    _repeatsTimer?.cancel();
    super.dispose();
  }

  void _toggleHelper({
    required bool current,
    required ValueChanged<bool> update,
    required Timer? timer,
    required ValueChanged<Timer?> saveTimer,
    Duration duration = const Duration(seconds: 7),
  }) {
    timer?.cancel();
    final next = !current;
    update(next);
    if (next) {
      saveTimer(Timer(duration, () {
        if (!mounted) return;
        update(false);
      }));
    } else {
      saveTimer(null);
    }
  }

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsStateProvider);
    const compactDensity = VisualDensity(horizontal: -2, vertical: -2);
    const titleStyle = TextStyle(
        fontSize: 13, fontWeight: FontWeight.w600, color: Colors.black87);
    const labelStyle = TextStyle(fontSize: 12, color: Colors.black87);
    const helperStyle = TextStyle(fontSize: 11, color: Colors.black54);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 6, 12, 0),
          child: Align(
            alignment: Alignment.centerLeft,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('Words per minute', style: titleStyle),
                const SizedBox(width: 4),
                IconButton(
                  padding: EdgeInsets.zero,
                  constraints:
                      const BoxConstraints(minWidth: 20, minHeight: 20),
                  icon: const Icon(Icons.info_outline,
                      size: 13, color: Colors.black54),
                  onPressed: () {
                    _toggleHelper(
                      current: _showWpmHelp,
                      update: (value) => setState(() => _showWpmHelp = value),
                      timer: _wpmTimer,
                      saveTimer: (timer) => _wpmTimer = timer,
                    );
                  },
                ),
              ],
            ),
          ),
        ),
        if (_showWpmHelp)
          const Padding(
            padding: EdgeInsets.fromLTRB(12, 0, 12, 4),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text('The rate at which the words are spoken.',
                  style: helperStyle),
            ),
          ),
        if (!_showWpmHelp) const SizedBox(height: 4),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Wrap(
            spacing: 8,
            children: [40, 80, 120, 160].map((wpm) {
              final selected = settings.wpm == wpm;
              return ChoiceChip(
                label: Text('$wpm', style: labelStyle),
                selected: selected,
                showCheckmark: false,
                selectedColor: const Color(0xFFE0E0E0),
                backgroundColor: const Color(0xFFF5F5F5),
                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                onSelected: (_) {
                  ref.read(settingsStateProvider.notifier).setWpm(wpm);
                },
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 8),
        const Divider(height: 8, thickness: 0.5),
        ListTile(
          title: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Repeats', style: titleStyle),
              const SizedBox(width: 4),
              IconButton(
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(minWidth: 20, minHeight: 20),
                icon: const Icon(Icons.info_outline,
                    size: 13, color: Colors.black54),
                onPressed: () {
                  _toggleHelper(
                    current: _showRepeatsHelp,
                    update: (value) => setState(() => _showRepeatsHelp = value),
                    timer: _repeatsTimer,
                    saveTimer: (timer) => _repeatsTimer = timer,
                  );
                },
              ),
            ],
          ),
          dense: true,
          visualDensity: compactDensity,
          trailing: DropdownButton<int>(
            value: settings.repeats,
            isDense: true,
            style: labelStyle,
            dropdownColor: Colors.white,
            items: List.generate(10, (index) => index + 1)
                .map((value) => DropdownMenuItem(
                    value: value, child: Text('$value×', style: labelStyle)))
                .toList(),
            onChanged: (value) {
              if (value == null) return;
              ref.read(settingsStateProvider.notifier).setRepeats(value);
            },
          ),
        ),
        if (_showRepeatsHelp)
          const Padding(
            padding: EdgeInsets.fromLTRB(12, 0, 12, 4),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'The number of times you will hear the vowel, consonant or syllable spoken.',
                style: helperStyle,
              ),
            ),
          ),
        if (!_showRepeatsHelp) const SizedBox(height: 4),
        const Divider(height: 8, thickness: 0.5),
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 6, 12, 0),
          child: Align(
            alignment: Alignment.centerLeft,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('Preset pauses', style: titleStyle),
                const SizedBox(width: 4),
                IconButton(
                  padding: EdgeInsets.zero,
                  constraints:
                      const BoxConstraints(minWidth: 20, minHeight: 20),
                  icon: const Icon(Icons.info_outline,
                      size: 13, color: Colors.black54),
                  onPressed: () {
                    _toggleHelper(
                      current: _showPresetsHelp,
                      update: (value) =>
                          setState(() => _showPresetsHelp = value),
                      timer: _presetsTimer,
                      saveTimer: (timer) => _presetsTimer = timer,
                    );
                  },
                ),
              ],
            ),
          ),
        ),
        if (_showPresetsHelp)
          const Padding(
            padding: EdgeInsets.fromLTRB(12, 0, 12, 4),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Useful sets of predetermined delays - use Settings for a more detailed way of doing this.',
                style: helperStyle,
              ),
            ),
          ),
        if (!_showPresetsHelp) const SizedBox(height: 4),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    const Text('Default',
                        style: labelStyle, textAlign: TextAlign.center),
                    Transform.scale(
                      scale: 0.75,
                      child: Switch(
                        value: settings.activePreset == 'Default',
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        onChanged: (value) {
                          if (value) {
                            ref
                                .read(settingsStateProvider.notifier)
                                .applyPreset('Default');
                          } else {
                            ref
                                .read(settingsStateProvider.notifier)
                                .applyPreset('');
                          }
                        },
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  children: [
                    const Text('Beginner',
                        style: labelStyle, textAlign: TextAlign.center),
                    Transform.scale(
                      scale: 0.75,
                      child: Switch(
                        value: settings.activePreset == 'Beginner',
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        onChanged: (value) {
                          if (value) {
                            ref
                                .read(settingsStateProvider.notifier)
                                .applyPreset('Beginner');
                          } else {
                            ref
                                .read(settingsStateProvider.notifier)
                                .applyPreset('');
                          }
                        },
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  children: [
                    const Text('Advanced',
                        style: labelStyle, textAlign: TextAlign.center),
                    Transform.scale(
                      scale: 0.75,
                      child: Switch(
                        value: settings.activePreset == 'Advanced',
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        onChanged: (value) {
                          if (value) {
                            ref
                                .read(settingsStateProvider.notifier)
                                .applyPreset('Advanced');
                          } else {
                            ref
                                .read(settingsStateProvider.notifier)
                                .applyPreset('');
                          }
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const Divider(),
      ],
    );
  }
}
