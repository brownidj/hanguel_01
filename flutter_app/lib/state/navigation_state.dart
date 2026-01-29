import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../services/navigation_store.dart';

final navigationStateProvider = StateNotifierProvider<NavigationState, NavigationSnapshot>(
  (ref) => NavigationState(ref.read(navigationStoreProvider)),
);

class NavigationSnapshot {
  final String mode;
  final int index;

  const NavigationSnapshot({required this.mode, required this.index});
}

class NavigationState extends StateNotifier<NavigationSnapshot> {
  NavigationState(this._store) : super(const NavigationSnapshot(mode: 'Vowels', index: 0));

  final NavigationStore _store;

  void hydrateMode(String mode) {
    if (mode.isEmpty || mode == state.mode) return;
    state = NavigationSnapshot(mode: mode, index: 0);
  }

  void setMode(String mode) {
    state = NavigationSnapshot(mode: mode, index: 0);
    _store.saveMode(mode);
  }

  void setIndex(int index) {
    state = NavigationSnapshot(mode: state.mode, index: index);
  }

  void next(int length) {
    if (length <= 0) return;
    final nextIndex = (state.index + 1) % length;
    state = NavigationSnapshot(mode: state.mode, index: nextIndex);
  }

  void prev(int length) {
    if (length <= 0) return;
    final prevIndex = (state.index - 1) % length;
    state = NavigationSnapshot(mode: state.mode, index: prevIndex);
  }
}
