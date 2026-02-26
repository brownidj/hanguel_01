import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

final stageStoreProvider = Provider<StageStore>((ref) => StageStore());

class StageStore {
  static const String _keyStage = 'active_stage';

  Future<String> loadStage() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyStage) ?? '';
  }

  Future<void> saveStage(String stageId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyStage, stageId);
  }
}
