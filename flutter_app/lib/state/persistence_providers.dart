import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../services/navigation_store.dart';
import '../services/settings_store.dart';
import 'navigation_state.dart';
import 'settings_state.dart';
import 'syllable_options_state.dart';
import '../services/syllable_options_store.dart';

final settingsHydrationProvider = FutureProvider<void>((ref) async {
  final store = ref.read(settingsStoreProvider);
  final snapshot = await store.load();
  ref.read(settingsStateProvider.notifier).hydrate(snapshot);
});

final navigationHydrationProvider = FutureProvider<void>((ref) async {
  final store = ref.read(navigationStoreProvider);
  final mode = await store.loadMode();
  ref.read(navigationStateProvider.notifier).hydrateMode(mode);
});

final syllableVowelSetHydrationProvider = FutureProvider<void>((ref) async {
  final store = ref.read(syllableOptionsStoreProvider);
  final raw = await store.loadRaw();
  final value = decodeSyllableVowelSet(raw);
  ref.read(syllableVowelSetProvider.notifier).hydrate(value);
});
