import '../../core/config.dart';
import '../../domain/stages.dart';
import '../yaml_loader.dart';

class StagesRepository {
  Future<List<StageDefinition>> loadStages() async {
    final data = await loadYamlAsset('${AppConfig.assetsDataPath}/stages.yaml');
    final items = data['stages'];
    if (items is! List) return [];
    return items
        .whereType<Map>()
        .map((raw) => Map<String, dynamic>.from(raw))
        .map(_stageFromRaw)
        .whereType<StageDefinition>()
        .toList();
  }
}

StageDefinition? _stageFromRaw(Map<String, dynamic> raw) {
  final id = '${raw['id'] ?? ''}'.trim();
  if (id.isEmpty) return null;
  final name = '${raw['name'] ?? ''}'.trim();
  final description = '${raw['description'] ?? ''}'.trim();
  final allowModes = _parseModes(raw['allow_modes']);
  final adds = _parseAdds(raw['adds']);
  final reviewPool = raw.containsKey('review_pool') ? _parseAdds(raw['review_pool']) : null;
  final masteryGate = _parseMasteryGate(raw['mastery_gate']);
  final reviewOffer = _parseReviewOffer(raw['review_offer']);
  return StageDefinition(
    id: id,
    name: name,
    description: description,
    allowModes: allowModes,
    adds: adds,
    reviewPool: reviewPool,
    masteryGate: masteryGate,
    reviewOffer: reviewOffer,
  );
}

StageModes _parseModes(dynamic raw) {
  if (raw is Map) {
    final modes = Map<String, dynamic>.from(raw);
    return StageModes(
      vowels: modes['vowels'] == true,
      consonants: modes['consonants'] == true,
      syllables: modes['syllables'] == true,
    );
  }
  return const StageModes.all();
}

StageAdds _parseAdds(dynamic raw) {
  if (raw is Map) {
    final adds = Map<String, dynamic>.from(raw);
    final vowels = _parseList(adds['vowels']);
    final consonants = _parseList(adds['consonants']);
    return StageAdds(vowels: vowels, consonants: consonants);
  }
  return const StageAdds(vowels: [], consonants: []);
}

List<String> _parseList(dynamic raw) {
  if (raw is List) {
    return raw.map((item) => '${item ?? ''}'.trim()).where((v) => v.isNotEmpty).toList();
  }
  return [];
}

StageMasteryGate? _parseMasteryGate(dynamic raw) {
  if (raw is Map) {
    final gate = Map<String, dynamic>.from(raw);
    final type = '${gate['type'] ?? ''}'.trim();
    final cycles = gate['cycles'];
    if (type.isEmpty || cycles is! int) return null;
    return StageMasteryGate(type: type, cycles: cycles);
  }
  return null;
}

StageReviewOffer? _parseReviewOffer(dynamic raw) {
  if (raw is Map) {
    final offer = Map<String, dynamic>.from(raw);
    final label = '${offer['label'] ?? ''}'.trim();
    final allow = offer['allow_include_previous'] == true;
    if (label.isEmpty) return null;
    return StageReviewOffer(allowIncludePrevious: allow, label: label);
  }
  return null;
}
