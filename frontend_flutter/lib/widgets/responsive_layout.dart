import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ResponsiveLayout extends StatefulWidget {
  final Widget child;
  final int currentIndex;

  const ResponsiveLayout({
    Key? key,
    required this.child,
    required this.currentIndex,
  }) : super(key: key);

  @override
  _ResponsiveLayoutState createState() => _ResponsiveLayoutState();
}

class _ResponsiveLayoutState extends State<ResponsiveLayout> {
  void _onNavigationItemTapped(int index) {
    if (index == widget.currentIndex) return;

    String routeName = '/dashboard';
    switch (index) {
      case 0:
        routeName = '/dashboard';
        break;
      case 1:
        routeName = '/expenses';
        break;
      case 2:
        routeName = '/budgets';
        break;
      case 3:
        routeName = '/profile';
        break;
    }
    Navigator.pushReplacementNamed(context, routeName);
  }

  Future<void> _handleLogout() async {
    final theme = Theme.of(context);
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Үйлдэл баталгаажуулах'),
        content: const Text('Та системээс гарахдаа итгэлтэй байна уу?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Үгүй'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Гарах'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await ApiService.logout();
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/login');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final size = MediaQuery.of(context).size;
    final isDesktop = size.width >= 800;

    if (isDesktop) {
      // Desktop Layout: Sidebar + Main Content
      return Scaffold(
        body: Row(
          children: [
            // Sidebar Navigation
            Container(
              width: 260,
              color: theme.colorScheme.surfaceVariant.withOpacity(0.4),
              child: Column(
                children: [
                  const SizedBox(height: 40),
                  // App Title
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.account_balance_wallet, size: 28, color: theme.colorScheme.primary),
                      const SizedBox(width: 10),
                      const Text(
                        'Зардлын Бүртгэл',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 40),
                  
                  // Navigation Items
                  _buildSidebarItem(0, Icons.dashboard_outlined, 'Хянах самбар'),
                  _buildSidebarItem(1, Icons.receipt_long_outlined, 'Зарлагууд'),
                  _buildSidebarItem(2, Icons.pie_chart_outline, 'Төсөвлөлт'),
                  _buildSidebarItem(3, Icons.person_outline, 'Хэрэглэгч'),
                  
                  const Spacer(),
                  // Logout Button
                  ListTile(
                    leading: const Icon(Icons.logout, color: Colors.red),
                    title: const Text('Системээс гарах', style: TextStyle(color: Colors.red)),
                    onTap: _handleLogout,
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
            // Vertical Divider
            VerticalDivider(width: 1, thickness: 1, color: theme.dividerColor),
            // Main Content Area
            Expanded(
              child: widget.child,
            ),
          ],
        ),
      );
    } else {
      // Mobile Layout: Bottom Nav + Main Content
      return Scaffold(
        body: widget.child,
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: widget.currentIndex,
          onTap: _onNavigationItemTapped,
          type: BottomNavigationBarType.fixed,
          selectedItemColor: theme.colorScheme.primary,
          unselectedItemColor: Colors.grey,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.dashboard_outlined),
              activeIcon: Icon(Icons.dashboard),
              label: 'Хянах самбар',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.receipt_long_outlined),
              activeIcon: Icon(Icons.receipt_long),
              label: 'Зарлагууд',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.pie_chart_outline),
              activeIcon: Icon(Icons.pie_chart),
              label: 'Төсөв',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline),
              activeIcon: Icon(Icons.person),
              label: 'Хэрэглэгч',
            ),
          ],
        ),
      );
    }
  }

  Widget _buildSidebarItem(int index, IconData icon, String label) {
    final theme = Theme.of(context);
    final isSelected = widget.currentIndex == index;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 4.0),
      child: ListTile(
        leading: Icon(
          icon,
          color: isSelected ? theme.colorScheme.primary : Colors.grey[700],
        ),
        title: Text(
          label,
          style: TextStyle(
            color: isSelected ? theme.colorScheme.primary : Colors.black87,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        selected: isSelected,
        selectedTileColor: theme.colorScheme.primary.withOpacity(0.12),
        onTap: () => _onNavigationItemTapped(index),
      ),
    );
  }
}
