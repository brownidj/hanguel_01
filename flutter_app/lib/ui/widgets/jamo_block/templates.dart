import 'package:flutter/material.dart';

import 'segment_frame.dart';

class RightBranchTemplate extends StatelessWidget {
  const RightBranchTemplate({
    super.key,
    required this.topText,
    required this.middleText,
    required this.bottomText,
    required this.topTooltip,
    required this.middleTooltip,
    required this.bottomTooltip,
    this.topStyle,
    this.middleStyle,
    this.bottomStyle,
  });

  final String topText;
  final String middleText;
  final String bottomText;
  final String topTooltip;
  final String middleTooltip;
  final String bottomTooltip;
  final TextStyle? topStyle;
  final TextStyle? middleStyle;
  final TextStyle? bottomStyle;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(child: SegmentFrame(child: _glyph(topText, topTooltip, style: topStyle))),
        const SizedBox(height: 4),
        Expanded(child: SegmentFrame(child: _glyph(middleText, middleTooltip, style: middleStyle))),
        const SizedBox(height: 4),
        Expanded(child: SegmentFrame(child: _glyph(bottomText, bottomTooltip, style: bottomStyle))),
      ],
    );
  }
}

class TopBranchTemplate extends StatelessWidget {
  const TopBranchTemplate({
    super.key,
    required this.topText,
    required this.middleText,
    required this.bottomText,
    required this.topTooltip,
    required this.middleTooltip,
    required this.bottomTooltip,
    this.topStyle,
    this.middleStyle,
    this.bottomStyle,
  });

  final String topText;
  final String middleText;
  final String bottomText;
  final String topTooltip;
  final String middleTooltip;
  final String bottomTooltip;
  final TextStyle? topStyle;
  final TextStyle? middleStyle;
  final TextStyle? bottomStyle;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(child: SegmentFrame(child: _glyph(topText, topTooltip, style: topStyle))),
        const SizedBox(height: 4),
        Expanded(child: SegmentFrame(child: _glyph(middleText, middleTooltip, style: middleStyle))),
        const SizedBox(height: 4),
        Expanded(child: SegmentFrame(child: _glyph(bottomText, bottomTooltip, style: bottomStyle))),
      ],
    );
  }
}

class BottomBranchTemplate extends StatelessWidget {
  const BottomBranchTemplate({
    super.key,
    required this.topText,
    required this.middleText,
    required this.bottomText,
    required this.topTooltip,
    required this.middleTooltip,
    required this.bottomTooltip,
    this.topStyle,
    this.middleStyle,
    this.bottomStyle,
  });

  final String topText;
  final String middleText;
  final String bottomText;
  final String topTooltip;
  final String middleTooltip;
  final String bottomTooltip;
  final TextStyle? topStyle;
  final TextStyle? middleStyle;
  final TextStyle? bottomStyle;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(child: SegmentFrame(child: _glyph(topText, topTooltip, style: topStyle))),
        const SizedBox(height: 4),
        Expanded(child: SegmentFrame(child: _glyph(middleText, middleTooltip, style: middleStyle))),
        const SizedBox(height: 4),
        Expanded(child: SegmentFrame(child: _glyph(bottomText, bottomTooltip, style: bottomStyle))),
      ],
    );
  }
}

class HorizontalTemplate extends StatelessWidget {
  const HorizontalTemplate({
    super.key,
    required this.topText,
    required this.middleText,
    required this.bottomText,
    required this.topTooltip,
    required this.middleTooltip,
    required this.bottomTooltip,
    this.topStyle,
    this.middleStyle,
    this.bottomStyle,
  });

  final String topText;
  final String middleText;
  final String bottomText;
  final String topTooltip;
  final String middleTooltip;
  final String bottomTooltip;
  final TextStyle? topStyle;
  final TextStyle? middleStyle;
  final TextStyle? bottomStyle;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(child: SegmentFrame(child: _glyph(topText, topTooltip, style: topStyle))),
        const SizedBox(height: 4),
        Expanded(child: SegmentFrame(child: _glyph(middleText, middleTooltip, style: middleStyle))),
        const SizedBox(height: 4),
        Expanded(child: SegmentFrame(child: _glyph(bottomText, bottomTooltip, style: bottomStyle))),
      ],
    );
  }
}

Widget _glyph(String text, String tooltip, {TextStyle? style}) {
  if (text.isEmpty) {
    return const Center(
      child: FittedBox(
        fit: BoxFit.contain,
        child: Text(
          'Empty',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w500,
            color: Color(0xFFB0B0B0),
          ),
        ),
      ),
    );
  }
  final glyph = Center(
    child: FittedBox(
      fit: BoxFit.contain,
      child: Text(
        text,
        style: style ?? const TextStyle(fontSize: 64, fontWeight: FontWeight.w600),
      ),
    ),
  );
  if (tooltip.isEmpty) return glyph;
  return Tooltip(
    message: tooltip,
    waitDuration: const Duration(milliseconds: 300),
    child: glyph,
  );
}
