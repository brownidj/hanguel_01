import 'models.dart';

const Map<String, String> _vowelRr = {
  'ㅏ': 'a',
  'ㅓ': 'eo',
  'ㅗ': 'o',
  'ㅜ': 'u',
  'ㅡ': 'eu',
  'ㅣ': 'i',
  'ㅐ': 'ae',
  'ㅔ': 'e',
  'ㅚ': 'oe',
  'ㅟ': 'wi',
  'ㅘ': 'wa',
  'ㅝ': 'wo',
  'ㅙ': 'wae',
  'ㅞ': 'we',
  'ㅢ': 'ui',
  'ㅑ': 'ya',
  'ㅕ': 'yeo',
  'ㅛ': 'yo',
  'ㅠ': 'yu',
  'ㅒ': 'yae',
  'ㅖ': 'ye',
};

const Map<String, String> _consRr = {
  'ㄱ': 'g',
  'ㄴ': 'n',
  'ㄷ': 'd',
  'ㄹ': 'r',
  'ㅁ': 'm',
  'ㅂ': 'b',
  'ㅅ': 's',
  'ㅇ': '',
  'ㅈ': 'j',
  'ㅊ': 'ch',
  'ㅋ': 'k',
  'ㅌ': 't',
  'ㅍ': 'p',
  'ㅎ': 'h',
  'ㄲ': 'kk',
  'ㄸ': 'tt',
  'ㅃ': 'pp',
  'ㅆ': 'ss',
  'ㅉ': 'jj',
};

const Map<String, String> _consHints = {
  'ㄱ': 'between g/k (unaspirated)',
  'ㄷ': 'between d/t (unaspirated)',
  'ㅂ': 'between b/p (unaspirated)',
  'ㄹ': 'r/l (light tap)',
  'ㅅ': 's',
  'ㅇ': 'silent at start',
  'ㅈ': 'j (unaspirated)',
};

const Map<String, String> _vowelHints = {
  'ㅏ': 'a',
  'ㅓ': 'eo (uh, more open)',
  'ㅗ': 'o',
  'ㅜ': 'u',
  'ㅡ': 'eu (close to "uh")',
  'ㅣ': 'i',
  'ㅐ': 'ae',
  'ㅔ': 'e',
  'ㅚ': 'oe',
  'ㅟ': 'wi',
  'ㅘ': 'wa',
  'ㅝ': 'wo',
  'ㅙ': 'wae',
  'ㅞ': 'we',
  'ㅢ': 'ui',
  'ㅑ': 'ya',
  'ㅕ': 'yeo',
  'ㅛ': 'yo',
  'ㅠ': 'yu',
  'ㅒ': 'yae',
  'ㅖ': 'ye',
};

const Map<String, String> _consExamples = {
  'ㄱ': 'go',
  'ㄴ': 'no',
  'ㄷ': 'day',
  'ㄹ': 'ladder',
  'ㅁ': 'man',
  'ㅂ': 'boy',
  'ㅅ': 'see',
  'ㅈ': 'jam',
  'ㅊ': 'chat',
  'ㅋ': 'kite',
  'ㅌ': 'tea',
  'ㅍ': 'pie',
  'ㅎ': 'hat',
  'ㄲ': 'skate',
  'ㄸ': 'stop',
  'ㅃ': 'spot',
  'ㅆ': 'sea',
  'ㅉ': 'jeep',
};

const Map<String, String> _vowelExamples = {
  'ㅏ': 'father',
  'ㅓ': 'sun',
  'ㅗ': 'go',
  'ㅜ': 'food',
  'ㅡ': 'sofa',
  'ㅣ': 'see',
  'ㅐ': 'cat',
  'ㅔ': 'bed',
  'ㅚ': 'way',
  'ㅟ': 'we',
  'ㅘ': 'waffle',
  'ㅝ': 'wonder',
  'ㅙ': 'wax',
  'ㅞ': 'wet',
  'ㅢ': 'we',
  'ㅑ': 'yard',
  'ㅕ': 'yawn',
  'ㅛ': 'yoga',
  'ㅠ': 'you',
  'ㅒ': 'yeah',
  'ㅖ': 'yes',
};

const Set<String> _sLikeVowels = {
  'ㅣ',
  'ㅑ',
  'ㅕ',
  'ㅛ',
  'ㅠ',
  'ㅖ',
  'ㅒ',
};

const List<String> _compatCho = [
  'ㄱ',
  'ㄲ',
  'ㄴ',
  'ㄷ',
  'ㄸ',
  'ㄹ',
  'ㅁ',
  'ㅂ',
  'ㅃ',
  'ㅅ',
  'ㅆ',
  'ㅇ',
  'ㅈ',
  'ㅉ',
  'ㅊ',
  'ㅋ',
  'ㅌ',
  'ㅍ',
  'ㅎ',
];

const List<String> _compatJung = [
  'ㅏ',
  'ㅐ',
  'ㅑ',
  'ㅒ',
  'ㅓ',
  'ㅔ',
  'ㅕ',
  'ㅖ',
  'ㅗ',
  'ㅘ',
  'ㅙ',
  'ㅚ',
  'ㅛ',
  'ㅜ',
  'ㅝ',
  'ㅞ',
  'ㅟ',
  'ㅠ',
  'ㅡ',
  'ㅢ',
  'ㅣ',
];

RRResult romanizeCv(String consonant, String vowel, [String? finalConsonant]) {
  var cons = consonant.trim();
  var vow = vowel.trim();

  if (cons == '∅') cons = '';
  if (vow == '∅') vow = '';

  final consRr = _consRr[cons] ?? cons;
  final vowRr = _vowelRr[vow] ?? vow;
  final rr = '$consRr$vowRr';

  final details = <String>[];
  final segments = <RRSegment>[];

  if (consRr.isNotEmpty) {
    segments.add(RRSegment(text: consRr, role: 'consonant'));
  }
  if (vowRr.isNotEmpty) {
    segments.add(RRSegment(text: vowRr, role: 'vowel'));
  }

  if (cons.isNotEmpty) {
    var consHint = _consHints[cons] ?? (consRr.isNotEmpty ? consRr : cons);
    if (cons == 'ㅅ' && _sLikeVowels.contains(vow)) {
      consHint = 's (can sound sh-like before i/y)';
    }
    final consExample = _consExamples[cons] ?? '';
    if (consExample.isNotEmpty) {
      details.add('$cons = $consHint, as in \'$consExample\'');
    } else {
      details.add('$cons = $consHint');
    }
  }
  if (vow.isNotEmpty) {
    final vowelHint = _vowelHints[vow] ?? (vowRr.isNotEmpty ? vowRr : vow);
    final vowelExample = _vowelExamples[vow] ?? '';
    if (vowelExample.isNotEmpty) {
      details.add('$vow = $vowelHint, as in \'$vowelExample\'');
    } else {
      details.add('$vow = $vowelHint');
    }
  }

  final hint = details.isNotEmpty ? details.join('; ') : rr;
  return RRResult(rr: rr, hint: hint, details: details, segments: segments);
}

RRResult romanizeText(String text) {
  if (text.isEmpty) {
    return const RRResult(rr: '', hint: '', details: []);
  }
  final parts = <String>[];
  for (final ch in text.runes) {
    final code = ch;
    if (code >= 0xAC00 && code <= 0xD7A3) {
      final idx = code - 0xAC00;
      final choIndex = idx ~/ 588;
      final jungIndex = (idx % 588) ~/ 28;
      if (choIndex >= 0 && choIndex < _compatCho.length && jungIndex >= 0 && jungIndex < _compatJung.length) {
        final cons = _compatCho[choIndex];
        final vow = _compatJung[jungIndex];
        parts.add(romanizeCv(cons, vow).rr);
        continue;
      }
    }
    parts.add(String.fromCharCode(code));
  }
  final rr = parts.join();
  final details = ['RR spelling: $rr', 'Pronunciation hint: $rr'];
  return RRResult(rr: rr, hint: details.join('\n'), details: details);
}
