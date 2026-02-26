class StageModes {
  final bool vowels;
  final bool consonants;
  final bool syllables;

  const StageModes({
    required this.vowels,
    required this.consonants,
    required this.syllables,
  });

  const StageModes.all()
      : vowels = true,
        consonants = true,
        syllables = true;
}

class StageAdds {
  final List<String> vowels;
  final List<String> consonants;

  const StageAdds({
    required this.vowels,
    required this.consonants,
  });
}

class StageMasteryGate {
  final String type;
  final int cycles;

  const StageMasteryGate({
    required this.type,
    required this.cycles,
  });
}

class StageReviewOffer {
  final bool allowIncludePrevious;
  final String label;

  const StageReviewOffer({
    required this.allowIncludePrevious,
    required this.label,
  });
}

class StageDefinition {
  final String id;
  final String name;
  final String description;
  final StageModes allowModes;
  final StageAdds adds;
  final StageAdds? reviewPool;
  final StageMasteryGate? masteryGate;
  final StageReviewOffer? reviewOffer;

  const StageDefinition({
    required this.id,
    required this.name,
    required this.description,
    required this.allowModes,
    required this.adds,
    this.reviewPool,
    this.masteryGate,
    this.reviewOffer,
  });
}
