import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../state/settings_state.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  bool _showThemeHelp = false;
  bool _showDelaysHelp = false;
  bool _showAdvancedHelp = false;
  Timer? _themeTimer;
  Timer? _delaysTimer;
  Timer? _advancedTimer;

  @override
  void dispose() {
    _themeTimer?.cancel();
    _delaysTimer?.cancel();
    _advancedTimer?.cancel();
    super.dispose();
  }

  void _toggleHelper({
    required bool current,
    required ValueChanged<bool> update,
    required Timer? timer,
    required ValueChanged<Timer?> saveTimer,
    required Duration duration,
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
    const delayOptions = [0.0, 0.5, 1.0, 1.5, 2.0];
    const titleStyle = TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.black87);
    const labelStyle = TextStyle(fontSize: 12, color: Colors.black87);
    const helperStyle = TextStyle(fontSize: 11, color: Colors.black54);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(0, 8, 0, 16),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 6, 12, 0),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Themes', style: titleStyle),
                  const SizedBox(width: 4),
                  IconButton(
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 20, minHeight: 20),
                    icon: const Icon(Icons.info_outline, size: 13, color: Colors.black54),
                    onPressed: () {
                      _toggleHelper(
                        current: _showThemeHelp,
                        update: (value) => setState(() => _showThemeHelp = value),
                        timer: _themeTimer,
                        saveTimer: (timer) => _themeTimer = timer,
                        duration: const Duration(seconds: 7),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
          if (_showThemeHelp)
            const Padding(
              padding: EdgeInsets.fromLTRB(12, 0, 12, 4),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text('Choose the visual theme for the app.', style: helperStyle),
              ),
            ),
          if (!_showThemeHelp) const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Wrap(
              spacing: 8,
              children: ['Taeguk', 'Hanji'].map((theme) {
                return ChoiceChip(
                  label: Text(theme, style: labelStyle),
                  selected: settings.theme == theme,
                  showCheckmark: false,
                  selectedColor: const Color(0xFFE0E0E0),
                  backgroundColor: const Color(0xFFF5F5F5),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  onSelected: (_) {
                    ref.read(settingsStateProvider.notifier).setTheme(theme);
                  },
                );
              }).toList(),
            ),
          ),
          const Divider(height: 8, thickness: 0.5),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 6, 12, 0),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Pauses', style: titleStyle),
                  const SizedBox(width: 4),
                  IconButton(
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 20, minHeight: 20),
                    icon: const Icon(Icons.info_outline, size: 13, color: Colors.black54),
                    onPressed: () {
                      _toggleHelper(
                        current: _showDelaysHelp,
                        update: (value) => setState(() => _showDelaysHelp = value),
                        timer: _delaysTimer,
                        saveTimer: (timer) => _delaysTimer = timer,
                        duration: const Duration(seconds: 15),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
          if (_showDelaysHelp)
            const Padding(
              padding: EdgeInsets.fromLTRB(12, 0, 12, 4),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Sets various pauses to allow you to look at and understand stuff on the screen before moving on. '
                  'Presets in the Drawer provide some useful sets of pauses. Changing a value here will override any '
                  'Preset you have chosen.',
                  style: helperStyle,
                ),
              ),
            ),
          if (!_showDelaysHelp) const SizedBox(height: 4),
          _DelayRow(
            label: 'Before first play',
            value: settings.delayBeforeFirstPlay,
            options: delayOptions,
            onChanged: (value) {
              ref.read(settingsStateProvider.notifier).setDelayBeforeFirstPlay(value);
            },
          ),
          _DelayRow(
            label: 'Between repeats',
            value: settings.delayBetweenRepeats,
            options: delayOptions,
            onChanged: (value) {
              ref.read(settingsStateProvider.notifier).setDelayBetweenRepeats(value);
            },
          ),
          _DelayRow(
            label: 'Before auto-advance',
            value: settings.delayBeforeAutoAdvance,
            options: delayOptions,
            onChanged: (value) {
              ref.read(settingsStateProvider.notifier).setDelayBeforeAutoAdvance(value);
            },
          ),
          const Divider(height: 8, thickness: 0.5),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 6, 12, 0),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Advanced Vowels', style: titleStyle),
                  const SizedBox(width: 4),
                  IconButton(
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 20, minHeight: 20),
                    icon: const Icon(Icons.info_outline, size: 13, color: Colors.black54),
                    onPressed: () {
                      _toggleHelper(
                        current: _showAdvancedHelp,
                        update: (value) => setState(() => _showAdvancedHelp = value),
                        timer: _advancedTimer,
                        saveTimer: (timer) => _advancedTimer = timer,
                        duration: const Duration(seconds: 7),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
          if (_showAdvancedHelp)
            const Padding(
              padding: EdgeInsets.fromLTRB(12, 0, 12, 4),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text('Controls which rare/advanced vowels are included.', style: helperStyle),
              ),
            ),
          if (!_showAdvancedHelp) const SizedBox(height: 4),
          ListTile(
            title: const Text('Include rare', style: labelStyle),
            dense: true,
            visualDensity: const VisualDensity(horizontal: -3, vertical: -3),
            minVerticalPadding: 0,
            contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 0),
            trailing: Transform.scale(
              scale: 0.75,
              child: Switch(
                value: settings.includeRare,
                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                onChanged: (value) {
                  ref.read(settingsStateProvider.notifier).setIncludeRare(value);
                },
              ),
            ),
          ),
          ListTile(
            title: const Text('Advanced', style: labelStyle),
            dense: true,
            visualDensity: const VisualDensity(horizontal: -3, vertical: -3),
            minVerticalPadding: 0,
            contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 0),
            trailing: Transform.scale(
              scale: 0.75,
              child: Switch(
                value: settings.advancedVowels,
                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                onChanged: (value) {
                  ref.read(settingsStateProvider.notifier).setAdvancedVowels(value);
                },
              ),
            ),
          ),
          const Divider(),
          const ListTile(
            title: Text('About'),
            subtitle: Text('Hangul Say It v1.0 • © topository • 260127'),
          ),
        ],
      ),
    );
  }
}

class _DelayRow extends StatelessWidget {
  const _DelayRow({
    required this.label,
    required this.value,
    required this.options,
    required this.onChanged,
  });

  final String label;
  final double value;
  final List<double> options;
  final ValueChanged<double> onChanged;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(label, style: const TextStyle(fontSize: 12, color: Colors.black87)),
      dense: true,
      visualDensity: const VisualDensity(horizontal: -2, vertical: -2),
      trailing: DropdownButton<double>(
        value: value,
        isDense: true,
        style: const TextStyle(fontSize: 12, color: Colors.black87),
        dropdownColor: Colors.white,
        items: options
            .map((option) => DropdownMenuItem<double>(
                  value: option,
                  child: Text(
                    '${option.toStringAsFixed(option == 0 ? 0 : 1)} s',
                    style: const TextStyle(fontSize: 12, color: Colors.black87),
                  ),
                ))
            .toList(),
        onChanged: (value) {
          if (value != null) onChanged(value);
        },
      ),
    );
  }
}
