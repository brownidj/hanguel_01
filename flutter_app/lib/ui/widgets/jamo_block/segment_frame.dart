import 'package:flutter/material.dart';

class SegmentFrame extends StatelessWidget {
  const SegmentFrame({super.key, this.child});

  final Widget? child;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: const DashedRectPainter(
        color: Color(0xFFAAAAAA),
        strokeWidth: 1,
        dashLength: 3,
        gapLength: 3,
      ),
      child: Container(
        color: Colors.white,
        alignment: Alignment.center,
        child: child,
      ),
    );
  }
}

class DashedRectPainter extends CustomPainter {
  const DashedRectPainter({
    required this.color,
    required this.strokeWidth,
    required this.dashLength,
    required this.gapLength,
  });

  final Color color;
  final double strokeWidth;
  final double dashLength;
  final double gapLength;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke;

    final rect = Rect.fromLTWH(
      strokeWidth / 2,
      strokeWidth / 2,
      size.width - strokeWidth,
      size.height - strokeWidth,
    );

    _drawDashedLine(canvas, paint, rect.topLeft, rect.topRight);
    _drawDashedLine(canvas, paint, rect.topRight, rect.bottomRight);
    _drawDashedLine(canvas, paint, rect.bottomRight, rect.bottomLeft);
    _drawDashedLine(canvas, paint, rect.bottomLeft, rect.topLeft);
  }

  void _drawDashedLine(Canvas canvas, Paint paint, Offset start, Offset end) {
    final totalLength = (end - start).distance;
    if (totalLength <= 0) return;
    final direction = (end - start) / totalLength;
    double progress = 0;
    while (progress < totalLength) {
      final dashEnd = (progress + dashLength).clamp(0, totalLength).toDouble();
      final p1 = start + direction * progress;
      final p2 = start + direction * dashEnd;
      canvas.drawLine(p1, p2, paint);
      progress += dashLength + gapLength;
    }
  }

  @override
  bool shouldRepaint(covariant DashedRectPainter oldDelegate) {
    return oldDelegate.color != color ||
        oldDelegate.strokeWidth != strokeWidth ||
        oldDelegate.dashLength != dashLength ||
        oldDelegate.gapLength != gapLength;
  }
}
