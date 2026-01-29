class RRResult {
  final String rr;
  final String hint;
  final List<String> details;
  final List<RRSegment> segments;

  const RRResult({
    required this.rr,
    required this.hint,
    this.details = const [],
    this.segments = const [],
  });
}

class RRSegment {
  final String text;
  final String role;

  const RRSegment({required this.text, required this.role});
}

class ExampleItem {
  final String hangul;
  final String rr;
  final String glossEn;
  final String startsWithSyllable;
  final String startsWithConsonant;
  final String startsWithVowel;
  final String imagePrompt;
  final String imageFilename;

  const ExampleItem({
    required this.hangul,
    required this.rr,
    required this.glossEn,
    required this.startsWithSyllable,
    required this.startsWithConsonant,
    required this.startsWithVowel,
    required this.imagePrompt,
    required this.imageFilename,
  });
}

class StudyItem {
  final String mode;
  final String glyph;
  final String consonant;
  final String vowel;
  final String blockType;

  const StudyItem({
    required this.mode,
    required this.glyph,
    required this.consonant,
    required this.vowel,
    required this.blockType,
  });

  const StudyItem.empty()
      : mode = '',
        glyph = '',
        consonant = '',
        vowel = '',
        blockType = '';
}
