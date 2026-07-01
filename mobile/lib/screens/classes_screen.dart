import 'package:flutter/material.dart';
import '../core/navis_constants.dart';
import '../theme/navis_theme.dart';
import '../widgets/wave_header.dart';

class ClassesScreen extends StatelessWidget {
  const ClassesScreen({super.key, required this.classNames, this.embedded = false});

  final List<String> classNames;
  final bool embedded;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 160,
            pinned: true,
            backgroundColor: NavisColors.azure,
            leading: embedded
                ? null
                : IconButton(
                    icon: const Icon(Icons.arrow_back_rounded, color: NavisColors.white),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
            automaticallyImplyLeading: !embedded,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(
                'Classes',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(color: NavisColors.white),
              ),
              background: WaveHeader(
                height: 160,
                child: Align(
                  alignment: Alignment.bottomLeft,
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 0, 24, 56),
                    child: Text(
                      '${classNames.length} objets reconnus',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: NavisColors.white.withValues(alpha: 0.9),
                            fontSize: 14,
                          ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.all(20),
            sliver: SliverList.separated(
              itemCount: classNames.length,
              separatorBuilder: (context, index) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final key = classNames[index];
                final french = NavisConstants.frenchLabels[key] ?? key;
                final icon = NavisConstants.classIcons[key] ?? Icons.category_rounded;

                return Semantics(
                  label: 'Classe ${index + 1}. $french',
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                    decoration: BoxDecoration(
                      color: NavisColors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: NavisColors.borderSoft),
                      boxShadow: NavisColors.cardShadow,
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: NavisColors.offWhite,
                            borderRadius: BorderRadius.circular(14),
                          ),
                          alignment: Alignment.center,
                          child: Text(
                            '${index + 1}',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                  color: NavisColors.azure,
                                  fontSize: 16,
                                ),
                          ),
                        ),
                        const SizedBox(width: 14),
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            gradient: NavisColors.primaryGradient,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(icon, color: NavisColors.white, size: 22),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(french, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontSize: 16)),
                              Text(key, style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontSize: 12)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
