import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/app_models.dart';
import '../services/local_database.dart';
import '../theme/navis_theme.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key, this.embedded = false});

  final bool embedded;

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<DetectionRecord> _records = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final records = await LocalDatabase.instance.getDetections();
    setState(() {
      _records = records;
      _loading = false;
    });
  }

  Future<void> _clear() async {
    await LocalDatabase.instance.clearDetections();
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('dd/MM/yyyy HH:mm');
    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      appBar: AppBar(
        automaticallyImplyLeading: !widget.embedded,
        title: const Text('Historique'),
        actions: [
          if (_records.isNotEmpty)
            IconButton(onPressed: _clear, icon: const Icon(Icons.delete_outline_rounded), tooltip: 'Effacer'),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _records.isEmpty
              ? Center(
                  child: Text('Aucune detection enregistree', style: Theme.of(context).textTheme.bodyLarge),
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(20),
                  itemCount: _records.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 10),
                  itemBuilder: (context, i) {
                    final r = _records[i];
                    return Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: NavisColors.white,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: NavisColors.borderSoft),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 44,
                            height: 44,
                            decoration: BoxDecoration(
                              gradient: NavisColors.primaryGradient,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(Icons.visibility_rounded, color: NavisColors.white),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(r.labelFr, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontSize: 16)),
                                Text(
                                  '${(r.confidence * 100).round()}%, ${fmt.format(r.createdAt)}',
                                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontSize: 12),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}
