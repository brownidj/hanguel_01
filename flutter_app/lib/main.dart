import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app.dart';
import 'debug/debug_logger.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await DebugLogger.init();
  await DebugLogger.log('main() start');
  FlutterError.onError = (details) async {
    await DebugLogger.log('FlutterError: ${details.exception}');
    FlutterError.presentError(details);
  };
  runZonedGuarded(
    () {
      runApp(const ProviderScope(child: App()));
    },
    (error, stack) async {
      await DebugLogger.log('Zone error: $error');
    },
  );
}
