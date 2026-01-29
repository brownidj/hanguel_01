import 'package:flutter/services.dart' show rootBundle;
import 'package:yaml/yaml.dart';

Future<dynamic> loadYamlAsset(String assetPath) async {
  final raw = await rootBundle.loadString(assetPath);
  final data = loadYaml(raw);
  return data is YamlList || data is YamlMap ? data : YamlMap();
}
