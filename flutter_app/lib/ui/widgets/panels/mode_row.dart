import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../state/data_providers.dart';
import '../../../state/stage_state.dart';
import '../../../state/stage_testing_mode.dart';
import '../../screens/settings_screen.dart';

class ModeRow extends ConsumerWidget {
  const ModeRow({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stagesAsync = ref.watch(stagesProvider);
    final currentStage = ref.watch(currentStageProvider);
    final completedStages = ref.watch(stageCompletionProvider);
    final testingMode = ref.watch(stageTestingModeProvider);
    return Row(
      children: [
        SizedBox(
          width: MediaQuery.of(context).size.width * 0.65,
          child: stagesAsync.when(
            data: (stages) {
              if (stages.isEmpty) {
                return const SizedBox.shrink();
              }
              final selected = currentStage ?? stages.first;
              return Tooltip(
                message: selected.description,
                waitDuration: const Duration(milliseconds: 300),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 0),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF2F2F2),
                    border: Border.all(color: const Color(0xFFBDBDBD)),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: selected.id,
                      isExpanded: true,
                      isDense: true,
                      items: stages
                          .map(
                            (stage) {
                              final isActive = stage.id == selected.id;
                              final isCompleted = completedStages.contains(stage.id);
                              final enabled = testingMode || isActive || isCompleted;
                              return DropdownMenuItem(
                                value: stage.id,
                                enabled: enabled,
                                child: Text(
                              stage.name,
                              style: enabled
                                  ? const TextStyle(color: Colors.black87)
                                  : const TextStyle(color: Color(0xFFBDBDBD)),
                            ),
                          );
                            },
                          )
                          .toList(),
                      onChanged: (value) {
                        if (value == null) return;
                        if (!testingMode &&
                            completedStages.contains(value) &&
                            value != selected.id) {
                          ref.read(stageCompletionProvider.notifier).revertFrom(value, stages);
                        }
                        ref.read(stageStateProvider.notifier).setStage(value);
                      },
                    ),
                  ),
                ),
              );
            },
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
        ),
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
