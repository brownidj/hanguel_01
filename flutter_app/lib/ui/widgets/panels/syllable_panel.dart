import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../domain/models.dart';
import '../../../state/data_providers.dart';
import '../../../state/navigation_state.dart';
import '../../../state/audio_service_provider.dart';
import '../../../state/playback_state.dart';
import '../../../state/settings_state.dart';

class SyllablePanel extends ConsumerWidget {
  const SyllablePanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nav = ref.watch(navigationStateProvider);
    final playback = ref.watch(playbackStateProvider);
    final settings = ref.watch(settingsStateProvider);
    final itemsAsync = ref.watch(currentItemsProvider);
    final currentAsync = ref.watch(currentItemProvider);
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                itemsAsync.when(
                  data: (items) {
                    final count = items.length;
                    final index = count == 0 ? 0 : (nav.index % count) + 1;
                    return Text(
                      '$index of $count',
                      style: const TextStyle(fontSize: 12, color: Colors.black54),
                    );
                  },
                  loading: () => const SizedBox.shrink(),
                  error: (_, __) => const SizedBox.shrink(),
                ),
                Wrap(
                  spacing: 6,
                  children: [
                    Tooltip(
                      message: 'Auto-play items and advance using delay settings.',
                      waitDuration: const Duration(milliseconds: 300),
                      child: _chipIconButton(
                        icon: Icons.autorenew,
                        enabled: playback.controlsEnabled,
                        selected: playback.autoEnabled,
                        onPressed: () {
                          ref.read(playbackStateProvider.notifier).setAutoEnabled(!playback.autoEnabled);
                        },
                      ),
                    ),
                    Tooltip(
                      message: 'Slow mode reduces speed to 40 WPM.',
                      waitDuration: const Duration(milliseconds: 300),
                      child: _chipIconButton(
                        icon: Icons.hourglass_bottom,
                        enabled: playback.controlsEnabled,
                        selected: settings.slowEnabled,
                        onPressed: () {
                          ref.read(settingsStateProvider.notifier).setSlowEnabled(!settings.slowEnabled);
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (nav.mode == 'Syllables')
                  const Padding(
                    padding: EdgeInsets.fromLTRB(8, 8, 4, 8),
                    child: ConsonantStrip(),
                  ),
                Expanded(
                  child: Center(
                    child: currentAsync.when(
                      data: (item) {
                        return LayoutBuilder(
                          builder: (context, constraints) {
                            final fontSize = constraints.maxHeight * 0.6;
                            final size = fontSize > 180 ? 180.0 : fontSize;
                            return Text(
                              item.glyph.isEmpty ? nav.mode : item.glyph,
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: size,
                                height: 0.9,
                                fontWeight: FontWeight.w600,
                              ),
                            );
                          },
                        );
                      },
                      loading: () => const CircularProgressIndicator(),
                      error: (err, _) => Text('Error: $err'),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Align(
              alignment: Alignment.centerRight,
              child: Wrap(
                spacing: 6,
                runSpacing: 6,
                children: [
                  _chipIconButton(
                    icon: Icons.chevron_left,
                    enabled: playback.controlsEnabled,
                    onPressed: () {
                      final length = itemsAsync.maybeWhen(
                        data: (items) => items.length,
                        orElse: () => 0,
                      );
                      ref.read(navigationStateProvider.notifier).prev(length);
                      if (playback.heardOnce) {
                        Future<void>.delayed(Duration.zero, () {
                          _handleHear(ref, settings.effectiveWpm);
                        });
                      }
                    },
                  ),
                  _chipTextButton(
                    label: '',
                    enabled: true,
                    onPressed: () {
                      _handleHear(ref, settings.effectiveWpm);
                    },
                    icon: Icons.hearing,
                  ),
                  _chipIconButton(
                    icon: Icons.chevron_right,
                    enabled: playback.controlsEnabled,
                    onPressed: () {
                      final length = itemsAsync.maybeWhen(
                        data: (items) => items.length,
                        orElse: () => 0,
                      );
                      ref.read(navigationStateProvider.notifier).next(length);
                      if (playback.heardOnce) {
                        Future<void>.delayed(Duration.zero, () {
                          _handleHear(ref, settings.effectiveWpm);
                        });
                      }
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

void _handleHear(WidgetRef ref, int wpm) async {
  final item = ref.read(currentItemProvider).maybeWhen(
        data: (value) => value,
        orElse: () => const StudyItem.empty(),
      );
  if (item.glyph.isEmpty) return;
  ref.read(playbackStateProvider.notifier).setControlsEnabled(false);
  await ref.read(audioServiceProvider).playGlyph(item.glyph, wpm: wpm);
  ref.read(playbackStateProvider.notifier).setControlsEnabled(true);
  ref.read(playbackStateProvider.notifier).setHeardOnce(true);
}

Widget _chipIconButton({
  required IconData icon,
  required bool enabled,
  bool selected = false,
  required VoidCallback onPressed,
}) {
  return ElevatedButton(
    onPressed: enabled ? onPressed : null,
    style: ElevatedButton.styleFrom(
      visualDensity: const VisualDensity(horizontal: -3, vertical: -3),
      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      backgroundColor: selected ? const Color(0xFFCFD8DC) : null,
      foregroundColor: selected ? Colors.black87 : null,
    ),
    child: Icon(icon, size: 18),
  );
}

Widget _chipTextButton({
  required String label,
  required bool enabled,
  required VoidCallback onPressed,
  IconData? icon,
}) {
  return ElevatedButton(
    onPressed: enabled ? onPressed : null,
    style: ElevatedButton.styleFrom(
      visualDensity: const VisualDensity(horizontal: -3, vertical: -3),
      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
    ),
    child: icon == null ? Text(label) : Icon(icon, size: 18),
  );
}

class ConsonantStrip extends ConsumerWidget {
  const ConsonantStrip({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final consonantsAsync = ref.watch(consonantsProvider);
    final currentAsync = ref.watch(currentItemProvider);
    return LayoutBuilder(
      builder: (context, constraints) {
        const itemHeight = 16.0;
        final maxItems = (constraints.maxHeight / itemHeight).floor().clamp(3, 99);
        return consonantsAsync.when(
          data: (items) {
            final glyphs = items.map((raw) => '${raw['glyph'] ?? ''}').where((g) => g.isNotEmpty).toList();
            if (glyphs.isEmpty) return const SizedBox.shrink();
            final current = currentAsync.maybeWhen(
              data: (item) => item.consonant,
              orElse: () => '',
            );
            var currentIndex = glyphs.indexOf(current);
            if (currentIndex < 0) currentIndex = 0;
            final window = maxItems;
            final maxStart = (glyphs.length - window).clamp(0, glyphs.length);
            final start = (currentIndex - window ~/ 2).clamp(0, maxStart);
            final end = (start + window).clamp(0, glyphs.length);
            final visible = glyphs.sublist(start, end);
            return SizedBox(
              width: 24,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  for (var i = 0; i < visible.length; i++)
                    SizedBox(
                      height: itemHeight,
                      child: Center(
                        child: Text(
                          visible[i],
                          style: TextStyle(
                            fontSize: 12,
                            color: (start + i) == currentIndex ? const Color(0xFF222222) : const Color(0xFF8E8E8E),
                            fontWeight: (start + i) == currentIndex ? FontWeight.w700 : FontWeight.w400,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            );
          },
          loading: () => const SizedBox(width: 24),
          error: (err, _) => const SizedBox(width: 24),
        );
      },
    );
  }
}
