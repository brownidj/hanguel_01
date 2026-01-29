const List<String> _choseong = [
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

const List<String> _jungseong = [
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

const List<String> _jongseong = [
  '',
  'ㄱ',
  'ㄲ',
  'ㄳ',
  'ㄴ',
  'ㄵ',
  'ㄶ',
  'ㄷ',
  'ㄹ',
  'ㄺ',
  'ㄻ',
  'ㄼ',
  'ㄽ',
  'ㄾ',
  'ㄿ',
  'ㅀ',
  'ㅁ',
  'ㅂ',
  'ㅄ',
  'ㅅ',
  'ㅆ',
  'ㅇ',
  'ㅈ',
  'ㅊ',
  'ㅋ',
  'ㅌ',
  'ㅍ',
  'ㅎ',
];

String composeLvt(String lead, String vowel, [String tail = '']) {
  final l = lead.trim();
  final v = vowel.trim();
  final t = tail.trim();
  if (l.isEmpty || v.isEmpty) {
    return '';
  }
  final li = _choseong.indexOf(l);
  final vi = _jungseong.indexOf(v);
  final ti = _jongseong.indexOf(t);
  if (li == -1 || vi == -1 || ti == -1) {
    return '';
  }
  const int sBase = 0xAC00;
  const int vCount = 21;
  const int tCount = 28;
  final codepoint = sBase + (li * vCount + vi) * tCount + ti;
  return String.fromCharCode(codepoint);
}

String composeCv(String consonant, String vowel) {
  return composeLvt(consonant, vowel, '');
}
