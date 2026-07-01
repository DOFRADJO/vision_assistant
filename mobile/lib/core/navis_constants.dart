import 'package:flutter/material.dart';

abstract final class NavisConstants {
  static const frenchLabels = <String, String>{
    'person': 'Personne',
    'car': 'Voiture',
    'bus': 'Bus',
    'truck': 'Camion',
    'bicycle': 'Velo',
    'motorcycle': 'Moto',
    'traffic_light': 'Feu tricolore',
    'stop_sign': 'Stop',
    'chair': 'Chaise',
    'bed': 'Lit',
    'table': 'Table',
    'dog': 'Chien',
    'handbag': 'Sac a main',
    'fire_hydrant': 'Borne incendie',
    'bench': 'Banc',
    'bottle': 'Bouteille',
    'backpack': 'Sac a dos',
    'train': 'Train',
  };

  static final classIcons = <String, IconData>{
    'person': Icons.person_rounded,
    'car': Icons.directions_car_rounded,
    'bus': Icons.directions_bus_rounded,
    'truck': Icons.local_shipping_rounded,
    'bicycle': Icons.pedal_bike_rounded,
    'motorcycle': Icons.two_wheeler_rounded,
    'traffic_light': Icons.traffic_rounded,
    'stop_sign': Icons.stop_circle_rounded,
    'chair': Icons.chair_rounded,
    'bed': Icons.bed_rounded,
    'table': Icons.table_restaurant_rounded,
    'dog': Icons.pets_rounded,
    'handbag': Icons.shopping_bag_rounded,
    'fire_hydrant': Icons.water_drop_rounded,
    'bench': Icons.weekend_rounded,
    'bottle': Icons.local_drink_rounded,
    'backpack': Icons.backpack_rounded,
    'train': Icons.train_rounded,
  };
}
