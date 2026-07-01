import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/app_models.dart';
import '../services/local_database.dart';
import '../theme/navis_theme.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<AppNotificationRecord> _items = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final items = await LocalDatabase.instance.getNotifications();
    await LocalDatabase.instance.markAllNotificationsRead();
    setState(() => _items = items);
  }

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('dd/MM HH:mm');
    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      appBar: AppBar(title: const Text('Notifications')),
      body: _items.isEmpty
          ? Center(child: Text('Aucune notification', style: Theme.of(context).textTheme.bodyLarge))
          : ListView.separated(
              padding: const EdgeInsets.all(20),
              itemCount: _items.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, i) {
                final n = _items[i];
                return Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: NavisColors.white,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: n.read ? NavisColors.borderSoft : NavisColors.azure.withValues(alpha: 0.4)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(n.title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontSize: 15)),
                      const SizedBox(height: 4),
                      Text(n.body, style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontSize: 13)),
                      const SizedBox(height: 6),
                      Text(fmt.format(n.createdAt), style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontSize: 11)),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
