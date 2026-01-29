import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

final syllableOptionsStoreProvider = Provider<SyllableOptionsStore>(
  (ref) => SyllableOptionsStore(),
);

class SyllableOptionsStore {
  static const String _keySyllableVowelSet = 'syllable_vowel_set';

  Future<String?> loadRaw() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keySyllableVowelSet);
  }

  Future<void> saveRaw(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keySyllableVowelSet, value);
  }
}
