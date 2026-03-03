import 'package:flutter/material.dart';

import '../debug/debug_logger.dart';
import '../debug/safe_mode.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({
    super.key,
    required this.onStart,
  });

  final VoidCallback onStart;

  @override
  Widget build(BuildContext context) {
    DebugLogger.log('SplashScreen build');
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.asset(
              'assets/splash_screen/portrait.png',
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                DebugLogger.log('Splash image load failed: $error');
                return const DecoratedBox(
                  decoration: BoxDecoration(color: Colors.black12),
                  child: Center(
                    child: Text(
                      'Missing splash image',
                      style: TextStyle(color: Colors.black54),
                    ),
                  ),
                );
              },
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
              child: Column(
                children: [
                  const Text.rich(
                    TextSpan(
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF1F2937),
                      ),
                      children: [
                        TextSpan(text: 'Learn to '),
                        TextSpan(
                          text: 'recognise',
                          style: TextStyle(fontWeight: FontWeight.w800),
                        ),
                        TextSpan(text: ' '),
                        TextSpan(text: 'Hangul'),
                        TextSpan(text: ',\nThe Korean '),
                        TextSpan(
                          text: 'alphabet',
                          style: TextStyle(fontWeight: FontWeight.w800),
                        ),
                        TextSpan(text: ', and\n'),
                        TextSpan(
                          text: 'pronounce',
                          style: TextStyle(fontWeight: FontWeight.w800),
                        ),
                        TextSpan(text: ' the syllables correctly.'),
                      ],
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const Spacer(),
                  Transform.translate(
                    offset: const Offset(0, -8),
                    child: GestureDetector(
                      onLongPress: () async {
                        await DebugLogger.log('Safe mode enabled from splash');
                        await SafeMode.setEnabled(true);
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Safe mode enabled. Restart app.'),
                          ),
                        );
                      },
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Image.asset(
                            'assets/images/icons/korea-flag-icon.png',
                            width: 50,
                            height: 50,
                            fit: BoxFit.cover,
                          ),
                          const SizedBox(width: 10),
                          const Text(
                            'Hangul: Say It',
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF1F2937),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  FilledButton(
                    onPressed: onStart,
                    style: FilledButton.styleFrom(
                      backgroundColor: const Color(0xFFF7F7F7),
                      foregroundColor: const Color(0xFF1F2937),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 32,
                        vertical: 14,
                      ),
                      shape: const StadiumBorder(),
                    ),
                    child: const Text(
                      'Start',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
