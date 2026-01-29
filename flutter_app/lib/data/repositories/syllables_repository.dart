import '../../core/config.dart';
import '../../domain/models.dart';
import '../yaml_loader.dart';

class SyllablesRepository {
  Future<List<StudyItem>> loadSyllables() async {
    final data = await loadYamlAsset('${AppConfig.assetsDataPath}/syllables.yaml');
    final items = data['syllables'];
    if (items is! List) return [];
    return items
        .whereType<Map>()
        .map((raw) => Map<String, dynamic>.from(raw))
        .map((raw) => StudyItem(
              mode: 'Syllables',
              glyph: '${raw['glyph'] ?? ''}',
              consonant: '${raw['consonant'] ?? ''}',
              vowel: '${raw['vowel'] ?? ''}',
              blockType: '${raw['block_type'] ?? ''}',
            ))
        .toList();
  }
}
