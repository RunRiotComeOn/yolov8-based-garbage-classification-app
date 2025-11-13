import 'package:flutter/material.dart';
import 'detection_screen.dart';
import 'guide_screen.dart';

/// Home screen with bottom navigation
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const DetectionScreen(),
    const GuideScreen(),
    const AboutScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.camera_alt),
            label: 'Detection',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.book),
            label: 'Guide',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.info),
            label: 'About',
          ),
        ],
      ),
    );
  }
}

/// About screen
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('About'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // App icon and title
            Center(
              child: Column(
                children: [
                  Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      color: Colors.green,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Icon(
                      Icons.recycling,
                      size: 64,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Garbage Classification AI',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Version 1.0.0',
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 32),

            // Features section
            Text(
              'Features',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            _buildFeatureCard(
              icon: Icons.camera_alt,
              title: 'AI Detection',
              description: 'Use YOLOv8 model for real-time garbage detection and classification',
            ),
            _buildFeatureCard(
              icon: Icons.photo_library,
              title: 'Photo & Gallery',
              description: 'Take photos or select from gallery for analysis',
            ),
            _buildFeatureCard(
              icon: Icons.show_chart,
              title: 'Visual Results',
              description: 'Display bounding boxes and labels on detected objects',
            ),
            _buildFeatureCard(
              icon: Icons.book,
              title: 'Classification Guide',
              description: 'Learn how to properly sort and dispose of garbage',
            ),

            const SizedBox(height: 24),

            // Supported categories
            Text(
              'Supported Categories',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildCategoryChip('Plastic', Colors.blue),
                _buildCategoryChip('Paper', Colors.brown),
                _buildCategoryChip('Glass', Colors.cyan),
                _buildCategoryChip('Metal', Colors.grey),
                _buildCategoryChip('Biodegradable', Colors.green),
                _buildCategoryChip('Cardboard', Colors.orange),
              ],
            ),

            const SizedBox(height: 24),

            // Technology stack
            Text(
              'Technology',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildTechRow('Frontend', 'Flutter 3.0+'),
                    _buildTechRow('Backend', 'FastAPI + YOLOv8'),
                    _buildTechRow('AI Model', 'YOLOv8 (Roboflow dataset)'),
                    _buildTechRow('Image Processing', 'OpenCV'),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // How to use
            Text(
              'How to Use',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            _buildStepCard(1, 'Take a photo or select from gallery'),
            _buildStepCard(2, 'Wait for AI analysis'),
            _buildStepCard(3, 'View detection results with bounding boxes'),
            _buildStepCard(4, 'Check classification guide for disposal info'),

            const SizedBox(height: 24),

            // Footer
            Center(
              child: Column(
                children: [
                  const Text(
                    'Made with Flutter',
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.eco, color: Colors.green, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'Help save the environment',
                        style: TextStyle(
                          color: Colors.green[700],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureCard({
    required IconData icon,
    required String title,
    required String description,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.green[100],
          child: Icon(icon, color: Colors.green),
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(description),
      ),
    );
  }

  Widget _buildCategoryChip(String label, Color color) {
    return Chip(
      label: Text(label),
      backgroundColor: color.withOpacity(0.2),
      labelStyle: TextStyle(color: color.withOpacity(0.8)),
    );
  }

  Widget _buildTechRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Widget _buildStepCard(int step, String description) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.green,
          child: Text(
            '$step',
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ),
        title: Text(description),
      ),
    );
  }
}
