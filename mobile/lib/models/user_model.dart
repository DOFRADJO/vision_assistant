/// Utilisateur stocke localement sur l appareil.
class LocalUser {
  const LocalUser({
    required this.id,
    required this.displayName,
    required this.pinHash,
    this.age,
    this.city,
    required this.createdAt,
  });

  final int id;
  final String displayName;
  final String pinHash;
  final int? age;
  final String? city;
  final DateTime createdAt;

  factory LocalUser.fromMap(Map<String, Object?> map) {
    return LocalUser(
      id: map['id'] as int,
      displayName: map['display_name'] as String,
      pinHash: map['pin_hash'] as String,
      age: map['age'] as int?,
      city: map['city'] as String?,
      createdAt: DateTime.parse(map['created_at'] as String),
    );
  }
}
