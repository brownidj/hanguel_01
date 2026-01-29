import '../../core/config.dart';
import '../yaml_loader.dart';

class VowelsRepository {
  Future<List<Map<String, dynamic>>> loadVowels() async {
    final data = await loadYamlAsset('${AppConfig.assetsDataPath}/vowels.yaml');
    final items = data['vowels'];
    if (items is List) {
      return items
          .whereType<Map>()
          .map((raw) => Map<String, dynamic>.from(raw))
          .toList();
    }
    return [];
  }
}
