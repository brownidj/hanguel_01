import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../services/syllable_options_store.dart';

enum SyllableVowelSet {
  core,
  corePlusAeE,
  addYaYeYoYu,
  addCompounds,
}

final syllableVowelSetProvider = StateNotifierProvider<SyllableVowelSetState, SyllableVowelSet>(
  (ref) => SyllableVowelSetState(ref.read(syllableOptionsStoreProvider)),
);

class SyllableVowelSetState extends StateNotifier<SyllableVowelSet> {
  SyllableVowelSetState(this._store) : super(SyllableVowelSet.core);

  final SyllableOptionsStore _store;

  void hydrate(SyllableVowelSet value) {
    state = value;
  }

  void set(SyllableVowelSet value) {
    state = value;
    _store.saveRaw(_encode(value));
  }
}

String syllableVowelSetLabel(SyllableVowelSet set, {bool compact = false}) {
  if (compact) {
    switch (set) {
      case SyllableVowelSet.core:
        return 'Core vowels';
      case SyllableVowelSet.corePlusAeE:
        return 'Add mid-front';
      case SyllableVowelSet.addYaYeYoYu:
        return 'Add y-glides';
      case SyllableVowelSet.addCompounds:
        return 'Add compounds';
    }
  }
  switch (set) {
    case SyllableVowelSet.core:
      return 'Core vowels (ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ)';
    case SyllableVowelSet.corePlusAeE:
      return 'Mid-front vowels (ㅐ ㅔ)';
    case SyllableVowelSet.addYaYeYoYu:
      return 'Y-glide vowels (ㅑ ㅕ ㅛ ㅠ)';
    case SyllableVowelSet.addCompounds:
      return 'Compound vowels (ㅘ ㅝ ㅚ ㅟ ㅢ)';
  }
}

String syllableVowelSetHint(SyllableVowelSet set) {
  switch (set) {
    case SyllableVowelSet.core:
      return 'Core vowels only';
    case SyllableVowelSet.corePlusAeE:
      return 'Core + mid-front vowels';
    case SyllableVowelSet.addYaYeYoYu:
      return 'Core + mid-front + y-glide vowels';
    case SyllableVowelSet.addCompounds:
      return 'Core + mid-front + y-glide + compounds';
  }
}

String _encode(SyllableVowelSet set) {
  return set.name;
}

SyllableVowelSet decodeSyllableVowelSet(String? raw) {
  switch (raw) {
    case 'corePlusAeE':
      return SyllableVowelSet.corePlusAeE;
    case 'addYaYeYoYu':
      return SyllableVowelSet.addYaYeYoYu;
    case 'addCompounds':
      return SyllableVowelSet.addCompounds;
    case 'core':
    default:
      return SyllableVowelSet.core;
  }
}
