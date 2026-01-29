import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

final navigationStoreProvider = Provider<NavigationStore>((ref) => NavigationStore());

class NavigationStore {
  static const String _keyMode = 'mode';

  Future<String> loadMode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyMode) ?? 'Vowels';
  }

  Future<void> saveMode(String mode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyMode, mode);
  }
}
