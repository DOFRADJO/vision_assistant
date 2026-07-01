import 'package:crypto/crypto.dart';
import 'dart:convert';

import '../models/user_model.dart';
import 'local_database.dart';

/// Authentification 100 % locale — aucun serveur, aucun email.
class LocalAuthService {
  LocalAuthService._();
  static final LocalAuthService instance = LocalAuthService._();

  LocalUser? _current;

  LocalUser? get currentUser => _current;
  bool get isLoggedIn => _current != null;

  Future<void> restoreSession() async {
    final userId = await LocalDatabase.instance.getActiveUserId();
    if (userId == null) {
      _current = null;
      return;
    }
    _current = await LocalDatabase.instance.getUserById(userId);
  }

  Future<LocalUser> register({
    required String displayName,
    required String pin,
    int? age,
    String? city,
  }) async {
    final name = _normalizeName(displayName);
    if (name.length < 2) throw AuthException('Prenom trop court');
    if (!_isValidPin(pin)) throw AuthException('Le code doit contenir 4 chiffres');
    if (age != null && (age < 5 || age > 120)) throw AuthException('Age invalide');

    final existing = await LocalDatabase.instance.getUserByName(name);
    if (existing != null) throw AuthException('Ce prenom existe deja. Connectez vous ou choisissez un autre prenom.');

    final user = await LocalDatabase.instance.createUser(
      displayName: name,
      pinHash: _hashPin(name, pin),
      age: age,
      city: city?.trim().isEmpty == true ? null : city?.trim(),
    );
    await LocalDatabase.instance.setActiveUserId(user.id);
    _current = user;
    return user;
  }

  Future<LocalUser> login({
    required String displayName,
    required String pin,
  }) async {
    final name = _normalizeName(displayName);
    final user = await LocalDatabase.instance.getUserByName(name);
    if (user == null) throw AuthException('Prenom inconnu. Creez un compte d abord.');
    if (user.pinHash != _hashPin(name, pin)) throw AuthException('Code secret incorrect');

    await LocalDatabase.instance.setActiveUserId(user.id);
    _current = user;
    return user;
  }

  Future<void> logout() async {
    await LocalDatabase.instance.clearActiveUser();
    _current = null;
  }

  String _hashPin(String name, String pin) {
    final bytes = utf8.encode('$name::$pin::navis-local');
    return sha256.convert(bytes).toString();
  }

  String _normalizeName(String raw) {
    return raw.trim().split(RegExp(r'\s+')).map((w) {
      if (w.isEmpty) return w;
      return w[0].toUpperCase() + w.substring(1).toLowerCase();
    }).join(' ');
  }

  bool _isValidPin(String pin) => RegExp(r'^\d{4}$').hasMatch(pin);
}

class AuthException implements Exception {
  AuthException(this.message);
  final String message;
  @override
  String toString() => message;
}
