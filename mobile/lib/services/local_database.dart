import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

import '../models/app_models.dart';
import '../models/user_model.dart';

class LocalDatabase {
  LocalDatabase._();
  static final LocalDatabase instance = LocalDatabase._();

  Database? _db;
  static const _dbVersion = 3;

  Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await openDatabase(
      join(await getDatabasesPath(), 'navis_local.db'),
      version: _dbVersion,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
    return _db!;
  }

  Future<void> _onCreate(Database db, int version) async {
    await _createTables(db);
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          display_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
          pin_hash TEXT NOT NULL,
          created_at TEXT NOT NULL
        )
      ''');
      await db.execute('''
        CREATE TABLE IF NOT EXISTS active_session (
          id INTEGER PRIMARY KEY CHECK (id = 1),
          user_id INTEGER NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id)
        )
      ''');
    }
    if (oldVersion < 3) {
      await db.execute('ALTER TABLE users ADD COLUMN age INTEGER');
      await db.execute('ALTER TABLE users ADD COLUMN city TEXT');
    }
  }

  Future<void> _createTables(Database db) async {
    await db.execute('''
      CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        display_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
        pin_hash TEXT NOT NULL,
        age INTEGER,
        city TEXT,
        created_at TEXT NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE active_session (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    ''');
    await db.execute('''
      CREATE TABLE detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label_fr TEXT NOT NULL,
        label_en TEXT NOT NULL,
        confidence REAL NOT NULL,
        created_at TEXT NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL,
        read INTEGER NOT NULL DEFAULT 0
      )
    ''');
    await db.execute('''
      CREATE TABLE settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
      )
    ''');
  }

  Future<LocalUser> createUser({
    required String displayName,
    required String pinHash,
    int? age,
    String? city,
  }) async {
    final db = await database;
    final id = await db.insert('users', {
      'display_name': displayName,
      'pin_hash': pinHash,
      'age': age,
      'city': city,
      'created_at': DateTime.now().toIso8601String(),
    });
    return LocalUser(
      id: id,
      displayName: displayName,
      pinHash: pinHash,
      age: age,
      city: city,
      createdAt: DateTime.now(),
    );
  }

  Future<LocalUser?> getUserByName(String name) async {
    final db = await database;
    final rows = await db.query('users', where: 'display_name = ? COLLATE NOCASE', whereArgs: [name], limit: 1);
    if (rows.isEmpty) return null;
    return LocalUser.fromMap(rows.first);
  }

  Future<LocalUser?> getUserById(int id) async {
    final db = await database;
    final rows = await db.query('users', where: 'id = ?', whereArgs: [id], limit: 1);
    if (rows.isEmpty) return null;
    return LocalUser.fromMap(rows.first);
  }

  Future<void> setActiveUserId(int userId) async {
    final db = await database;
    await db.insert('active_session', {'id': 1, 'user_id': userId}, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<int?> getActiveUserId() async {
    final db = await database;
    final rows = await db.query('active_session', limit: 1);
    if (rows.isEmpty) return null;
    return rows.first['user_id'] as int?;
  }

  Future<void> clearActiveUser() async {
    final db = await database;
    await db.delete('active_session');
  }

  Future<int> insertDetection(DetectionRecord record) async {
    final db = await database;
    return db.insert('detections', record.toMap());
  }

  Future<List<DetectionRecord>> getDetections({int limit = 100}) async {
    final db = await database;
    final rows = await db.query('detections', orderBy: 'created_at DESC', limit: limit);
    return rows.map(DetectionRecord.fromMap).toList();
  }

  Future<void> clearDetections() async {
    final db = await database;
    await db.delete('detections');
  }

  Future<int> insertNotification(AppNotificationRecord record) async {
    final db = await database;
    return db.insert('notifications', record.toMap());
  }

  Future<List<AppNotificationRecord>> getNotifications({int limit = 50}) async {
    final db = await database;
    final rows = await db.query('notifications', orderBy: 'created_at DESC', limit: limit);
    return rows.map(AppNotificationRecord.fromMap).toList();
  }

  Future<void> markAllNotificationsRead() async {
    final db = await database;
    await db.update('notifications', {'read': 1});
  }

  Future<int> unreadNotificationCount() async {
    final db = await database;
    final result = await db.rawQuery('SELECT COUNT(*) as c FROM notifications WHERE read = 0');
    return Sqflite.firstIntValue(result) ?? 0;
  }

  Future<void> setSetting(String key, String value) async {
    final db = await database;
    await db.insert('settings', {'key': key, 'value': value}, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<String?> getSetting(String key) async {
    final db = await database;
    final rows = await db.query('settings', where: 'key = ?', whereArgs: [key], limit: 1);
    if (rows.isEmpty) return null;
    return rows.first['value'] as String?;
  }
}
