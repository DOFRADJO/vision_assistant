import 'package:flutter/material.dart';

import '../models/app_models.dart';

/// Cadres + etiquettes sur la vue camera / video.
class DetectionSceneOverlay extends StatelessWidget {
  const DetectionSceneOverlay({
    super.key,
    required this.boxes,
    required this.sourceWidth,
    required this.sourceHeight,
  });

  final List<DetectionBox> boxes;
  final double sourceWidth;
  final double sourceHeight;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final dw = constraints.maxWidth;
        final dh = constraints.maxHeight;
        if (sourceWidth <= 0 || sourceHeight <= 0) return const SizedBox.shrink();

        final scale = (dw / sourceWidth).clamp(0, double.infinity);
        final scaleY = (dh / sourceHeight).clamp(0, double.infinity);
        final s = scale < scaleY ? scale : scaleY;
        final offsetX = (dw - sourceWidth * s) / 2;
        final offsetY = (dh - sourceHeight * s) / 2;

        return Stack(
          children: [
            for (final b in boxes)
              Positioned(
                left: offsetX + b.x1 * s,
                top: offsetY + b.y1 * s,
                width: (b.x2 - b.x1) * s,
                height: (b.y2 - b.y1) * s,
                child: _BoxLabel(label: b.labelFr, confidence: b.confidence),
              ),
          ],
        );
      },
    );
  }
}

class _BoxLabel extends StatelessWidget {
  const _BoxLabel({required this.label, required this.confidence});

  final String label;
  final double confidence;

  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0xFF4DA3FF), width: 3),
            borderRadius: BorderRadius.circular(6),
            color: const Color(0x331E7BFF),
          ),
        ),
        Positioned(
          top: -26,
          left: 0,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF0B5BD4),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              '$label ${(confidence * 100).round()}%',
              style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w600),
            ),
          ),
        ),
      ],
    );
  }
}

class SceneToolbar extends StatelessWidget {
  const SceneToolbar({
    super.key,
    required this.sceneText,
    required this.objectCount,
    required this.onRecord,
    required this.onBack,
    this.isRecording = false,
  });

  final String sceneText;
  final int objectCount;
  final VoidCallback onRecord;
  final VoidCallback onBack;
  final bool isRecording;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF0B5BD4), Color(0xFF0847A8)],
        ),
      ),
      padding: EdgeInsets.fromLTRB(12, 8, 12, 8 + MediaQuery.paddingOf(context).bottom),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Text(
              sceneText,
              style: const TextStyle(color: Color(0xFF1A2B4A), fontSize: 14, height: 1.4, fontWeight: FontWeight.w500),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              IconButton(
                onPressed: onBack,
                icon: const Icon(Icons.arrow_back_rounded, color: Colors.white),
                tooltip: 'Retour',
              ),
              Expanded(
                child: Text(
                  '$objectCount objet${objectCount > 1 ? 's' : ''} detecte${objectCount > 1 ? 's' : ''}',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                  textAlign: TextAlign.center,
                ),
              ),
              FilledButton.icon(
                onPressed: isRecording ? null : onRecord,
                style: FilledButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: const Color(0xFF0B5BD4),
                ),
                icon: Icon(isRecording ? Icons.hourglass_top : Icons.save_alt_rounded),
                label: Text(isRecording ? 'Sauve...' : 'Enregistrer'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class NavisSceneAppBar extends StatelessWidget implements PreferredSizeWidget {
  const NavisSceneAppBar({super.key, required this.title, this.actions});

  final String title;
  final List<Widget>? actions;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
      centerTitle: true,
      actions: actions,
      iconTheme: const IconThemeData(color: Colors.white),
      flexibleSpace: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(colors: [Color(0xFF1E7BFF), Color(0xFF0847A8)]),
        ),
      ),
      backgroundColor: Colors.transparent,
      elevation: 0,
    );
  }
}
