import 'package:flutter/material.dart';

/// Garbage classification categories
enum GarbageCategory {
  recycle('Recyclable', Colors.blue, 'Items that can be recycled'),
  organic('Organic', Colors.green, 'Biodegradable organic matter'),
  trash('Trash', Colors.grey, 'Non-recyclable general waste'),
  hazardous('Hazardous', Colors.red, 'Harmful to environment and health');

  final String displayName;
  final Color color;
  final String description;

  const GarbageCategory(this.displayName, this.color, this.description);
}

/// Garbage item data model
class GarbageItem {
  final String name;
  final String type;
  final GarbageCategory category;
  final String description;
  final String disposal;
  final List<String> examples;

  GarbageItem({
    required this.name,
    required this.type,
    required this.category,
    required this.description,
    required this.disposal,
    required this.examples,
  });

  factory GarbageItem.fromJson(Map<String, dynamic> json) {
    return GarbageItem(
      name: json['name'] as String,
      type: json['type'] as String,
      category: _getCategoryFromString(json['category'] as String),
      description: json['description'] as String,
      disposal: json['disposal'] as String,
      examples: (json['examples'] as List<dynamic>).map((e) => e as String).toList(),
    );
  }

  static GarbageCategory _getCategoryFromString(String category) {
    switch (category.toLowerCase()) {
      case 'recycle':
      case 'recyclable':
        return GarbageCategory.recycle;
      case 'organic':
      case 'biodegradable':
        return GarbageCategory.organic;
      case 'hazardous':
      case 'harmful':
        return GarbageCategory.hazardous;
      default:
        return GarbageCategory.trash;
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'type': type,
      'category': category.name,
      'description': description,
      'disposal': disposal,
      'examples': examples,
    };
  }
}
