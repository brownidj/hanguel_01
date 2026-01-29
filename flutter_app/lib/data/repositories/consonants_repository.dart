import '../../core/config.dart';
import '../yaml_loader.dart';

class ConsonantsRepository {
  Future<List<Map<String, dynamic>>> loadConsonants() async {
    final data = await loadYamlAsset('${AppConfig.assetsDataPath}/consonants.yaml');
    final items = data['consonants'];
    if (items is List) {
      return items
          .whereType<Map>()
          .map((raw) => Map<String, dynamic>.from(raw))
          .toList();
    }
    return [];
  }
}
