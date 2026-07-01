/// Texte utilisateur sans tirets (virgules a la place).
abstract final class NavisText {
  static String clean(String input) {
    var s = input;
    s = s.replaceAll('—', ', ');
    s = s.replaceAll('–', ', ');
    s = s.replaceAll(RegExp(r'\s+-\s+'), ', ');
    s = s.replaceAllMapped(
      RegExp(r"([a-zA-ZàâäéèêëïîôùûüçÀÂÄÉÈÊËÏÎÔÙÛÜÇ']+)-([a-zA-ZàâäéèêëïîôùûüçÀÂÄÉÈÊËÏÎÔÙÛÜÇ]+)"),
      (m) => '${m[1]} ${m[2]}',
    );
    s = s.replaceAll(RegExp(r',\s*,+'), ', ');
    s = s.replaceAll(RegExp(r'\s{2,}'), ' ');
    return s.trim();
  }
}
