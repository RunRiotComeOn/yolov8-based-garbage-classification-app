import '../models/garbage_guide.dart';

/// Garbage classification guide service
class GuideService {
  /// Get all garbage categories
  static List<GarbageCategory> getAllCategories() {
    return GarbageCategory.values;
  }

  /// Get all garbage items with classification guide
  static List<GarbageItem> getAllItems() {
    return [
      GarbageItem(
        name: 'Plastic Bottles',
        type: 'PLASTIC',
        category: GarbageCategory.recycle,
        description: 'Clean plastic bottles and containers',
        disposal: 'Rinse and recycle in blue bin',
        examples: ['Water bottles', 'Soda bottles', 'Detergent bottles'],
      ),
      GarbageItem(
        name: 'Paper',
        type: 'PAPER',
        category: GarbageCategory.recycle,
        description: 'Clean paper products',
        disposal: 'Keep dry and recycle in blue bin',
        examples: ['Newspapers', 'Office paper', 'Magazines', 'Cardboard boxes'],
      ),
      GarbageItem(
        name: 'Glass Bottles',
        type: 'GLASS',
        category: GarbageCategory.recycle,
        description: 'Glass bottles and jars',
        disposal: 'Rinse and recycle in blue bin',
        examples: ['Wine bottles', 'Beer bottles', 'Glass jars'],
      ),
      GarbageItem(
        name: 'Metal Cans',
        type: 'METAL',
        category: GarbageCategory.recycle,
        description: 'Aluminum and steel cans',
        disposal: 'Rinse and recycle in blue bin',
        examples: ['Aluminum cans', 'Steel cans', 'Tin cans'],
      ),
      GarbageItem(
        name: 'Food Waste',
        type: 'BIODEGRADABLE',
        category: GarbageCategory.organic,
        description: 'Organic food scraps',
        disposal: 'Compost in green bin',
        examples: ['Fruit peels', 'Vegetable scraps', 'Coffee grounds', 'Eggshells'],
      ),
      GarbageItem(
        name: 'Cardboard',
        type: 'CARDBOARD',
        category: GarbageCategory.recycle,
        description: 'Cardboard boxes and packaging',
        disposal: 'Flatten and recycle in blue bin',
        examples: ['Shipping boxes', 'Cereal boxes', 'Pizza boxes (if clean)'],
      ),
    ];
  }

  /// Search items by keyword
  static List<GarbageItem> searchItems(String query) {
    if (query.isEmpty) {
      return getAllItems();
    }

    final lowerQuery = query.toLowerCase();
    return getAllItems().where((item) {
      return item.name.toLowerCase().contains(lowerQuery) ||
             item.type.toLowerCase().contains(lowerQuery) ||
             item.description.toLowerCase().contains(lowerQuery) ||
             item.examples.any((ex) => ex.toLowerCase().contains(lowerQuery));
    }).toList();
  }

  /// Get items by category
  static List<GarbageItem> getItemsByCategory(GarbageCategory category) {
    return getAllItems().where((item) => item.category == category).toList();
  }
}
