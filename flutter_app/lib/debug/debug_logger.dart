import 'dart:io';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

class DebugLogger {
  static File? _logFile;

  static Future<void> init() async {
    try {
      final dir = await getApplicationSupportDirectory();
      final file = File(p.join(dir.path, 'hangul_debug.log'));
      _logFile = file;
      await _logFile!.writeAsString(
        '--- app start ${DateTime.now().toIso8601String()} ---\n',
        mode: FileMode.append,
        flush: true,
      );
    } catch (_) {
      // ignore: avoid_print
      print('[DEBUG] Failed to init logger');
    }
  }

  static Future<void> log(String message) async {
    final line = '[${DateTime.now().toIso8601String()}] $message\n';
    // ignore: avoid_print
    print(line.trimRight());
    final file = _logFile;
    if (file == null) return;
    try {
      await file.writeAsString(line, mode: FileMode.append, flush: true);
    } catch (_) {
      // ignore: avoid_print
      print('[DEBUG] Failed to write log line');
    }
  }

  static Future<String> read() async {
    final file = _logFile;
    if (file == null) return '';
    try {
      return await file.readAsString();
    } catch (_) {
      return '';
    }
  }
}
