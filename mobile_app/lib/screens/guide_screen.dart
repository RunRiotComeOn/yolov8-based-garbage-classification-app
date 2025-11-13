import 'package:flutter/material.dart';
import '../models/garbage_guide.dart';
import '../services/guide_service.dart';

/// Garbage classification guide screen
class GuideScreen extends StatefulWidget {
  const GuideScreen({super.key});

  @override
  State<GuideScreen> createState() => _GuideScreenState();
}

class _GuideScreenState extends State<GuideScreen> {
  String _searchQuery = '';
  List<GarbageItem> _filteredItems = [];

  @override
  void initState() {
    super.initState();
    _filteredItems = GuideService.getAllItems();
  }

  void _onSearchChanged(String query) {
    setState(() {
      _searchQuery = query;
      _filteredItems = GuideService.searchItems(query);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Classification Guide'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              onChanged: _onSearchChanged,
              decoration: InputDecoration(
                hintText: 'Search garbage type...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _onSearchChanged('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),

          // Category chips
          SizedBox(
            height: 50,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: GarbageCategory.values.map((category) {
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(category.displayName),
                    avatar: CircleAvatar(
                      backgroundColor: category.color.withOpacity(0.3),
                      child: Icon(
                        _getCategoryIcon(category),
                        size: 16,
                        color: category.color,
                      ),
                    ),
                    onSelected: (selected) {
                      if (selected) {
                        setState(() {
                          _filteredItems = GuideService.getItemsByCategory(category);
                        });
                      } else {
                        setState(() {
                          _filteredItems = GuideService.getAllItems();
                        });
                      }
                    },
                  ),
                );
              }).toList(),
            ),
          ),

          const Divider(height: 1),

          // Items list
          Expanded(
            child: _filteredItems.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.search_off, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text(
                          'No items found',
                          style: TextStyle(color: Colors.grey, fontSize: 16),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _filteredItems.length,
                    itemBuilder: (context, index) {
                      final item = _filteredItems[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: ExpansionTile(
                          leading: CircleAvatar(
                            backgroundColor: item.category.color.withOpacity(0.2),
                            child: Icon(
                              _getCategoryIcon(item.category),
                              color: item.category.color,
                            ),
                          ),
                          title: Text(
                            item.name,
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Text(
                            item.type,
                            style: TextStyle(
                              color: item.category.color,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Category
                                  Row(
                                    children: [
                                      Icon(Icons.category, size: 20, color: Colors.grey[600]),
                                      const SizedBox(width: 8),
                                      Text(
                                        'Category: ${item.category.displayName}',
                                        style: const TextStyle(fontWeight: FontWeight.bold),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),

                                  // Description
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Icon(Icons.info, size: 20, color: Colors.grey[600]),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(item.description),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),

                                  // Disposal
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Icon(Icons.delete, size: 20, color: Colors.grey[600]),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(
                                          item.disposal,
                                          style: TextStyle(color: item.category.color),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),

                                  // Examples
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Icon(Icons.list, size: 20, color: Colors.grey[600]),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Wrap(
                                          spacing: 6,
                                          runSpacing: 6,
                                          children: item.examples.map((example) {
                                            return Chip(
                                              label: Text(
                                                example,
                                                style: const TextStyle(fontSize: 12),
                                              ),
                                              backgroundColor: item.category.color.withOpacity(0.1),
                                            );
                                          }).toList(),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  IconData _getCategoryIcon(GarbageCategory category) {
    switch (category) {
      case GarbageCategory.recycle:
        return Icons.recycling;
      case GarbageCategory.organic:
        return Icons.eco;
      case GarbageCategory.trash:
        return Icons.delete;
      case GarbageCategory.hazardous:
        return Icons.warning;
    }
  }
}
