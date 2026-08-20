import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../models/expense.dart';
import '../../models/category.dart';
import '../../widgets/responsive_layout.dart';
import 'expense_form_screen.dart';
import 'package:intl/intl.dart';

class ExpenseListScreen extends StatefulWidget {
  const ExpenseListScreen({Key? key}) : super(key: key);

  @override
  _ExpenseListScreenState createState() => _ExpenseListScreenState();
}

class _ExpenseListScreenState extends State<ExpenseListScreen> {
  bool _isLoading = true;
  List<Expense> _expenses = [];
  List<Category> _categories = [];
  int? _selectedCategoryId;
  DateTime? _startDate;
  DateTime? _endDate;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final cats = await ApiService.getCategories();
      
      String? startStr = _startDate != null ? DateFormat('yyyy-MM-dd').format(_startDate!) : null;
      String? endStr = _endDate != null ? DateFormat('yyyy-MM-dd').format(_endDate!) : null;
      final exps = await ApiService.getExpenses(
        categoryId: _selectedCategoryId,
        startDate: startStr,
        endDate: endStr,
      );

      setState(() {
        _categories = cats;
        _expenses = exps;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Алдаа гарлаа: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _handleDelete(int id) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Баталгаажуулах'),
        content: const Text('Энэ зардлыг устгах уу?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Үгүй'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Устгах'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        final success = await ApiService.deleteExpense(id);
        if (success && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Зардал амжилттай устлаа')),
          );
          _fetchData();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Устгаж чадсангүй: $e')),
          );
        }
      }
    }
  }

  double get _totalSum => _expenses.fold(0.0, (sum, item) => sum + item.amount);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currencyFormat = NumberFormat.currency(locale: 'mn_MN', symbol: '₮', decimalDigits: 0);
    final dateFormat = DateFormat('yyyy-MM-dd');

    return ResponsiveLayout(
      currentIndex: 1,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Миний зардлууд'),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _fetchData,
            ),
          ],
        ),
        body: Column(
          children: [
            // Filter Bar
            _buildFilterBar(dateFormat, theme),
            
            // Total Sum Display
            _buildTotalSumBanner(currencyFormat, theme),

            // Main List
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _errorMessage != null
                      ? Center(child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)))
                      : _expenses.isEmpty
                          ? const Center(child: Text('Зардал бүртгэгдээгүй байна'))
                          : ListView.builder(
                              itemCount: _expenses.length,
                              padding: const EdgeInsets.symmetric(horizontal: 16),
                              itemBuilder: (context, index) {
                                final expense = _expenses[index];
                                final catColor = _parseColor(expense.categoryDetails?.color);

                                return Card(
                                  margin: const EdgeInsets.symmetric(vertical: 8),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                  child: ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: catColor.withOpacity(0.2),
                                      child: Icon(
                                        Icons.monetization_on_outlined,
                                        color: catColor,
                                      ),
                                    ),
                                    title: Text(
                                      expense.categoryDetails?.name ?? 'Ангилалгүй',
                                      style: const TextStyle(fontWeight: FontWeight.bold),
                                    ),
                                    subtitle: Text(
                                      '${expense.description.isNotEmpty ? expense.description + " • " : ""}${dateFormat.format(expense.date)}',
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    trailing: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Text(
                                          currencyFormat.format(expense.amount),
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 16,
                                            color: Colors.black87,
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        IconButton(
                                          icon: const Icon(Icons.edit_outlined, color: Colors.blue),
                                          onPressed: () async {
                                            final updated = await Navigator.push(
                                              context,
                                              MaterialPageRoute(
                                                builder: (context) => ExpenseFormScreen(expense: expense),
                                              ),
                                            );
                                            if (updated == true) _fetchData();
                                          },
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.delete_outline, color: Colors.red),
                                          onPressed: () => _handleDelete(expense.id),
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
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () async {
            final created = await Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const ExpenseFormScreen()),
            );
            if (created == true) _fetchData();
          },
          icon: const Icon(Icons.add),
          label: const Text('Шинэ зардал'),
        ),
      ),
    );
  }

  Widget _buildFilterBar(DateFormat dateFormat, ThemeData theme) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          // Category dropdown
          DropdownButton<int>(
            value: _selectedCategoryId,
            hint: const Text('Ангилал сонгох'),
            items: [
              const DropdownMenuItem<int>(
                value: null,
                child: Text('Бүх ангилал'),
              ),
              ..._categories.map((cat) {
                return DropdownMenuItem<int>(
                  value: cat.id,
                  child: Text(cat.name),
                );
              }),
            ],
            onChanged: (value) {
              setState(() {
                _selectedCategoryId = value;
              });
              _fetchData();
            },
          ),
          const SizedBox(width: 16),

          // Start Date Button
          OutlinedButton(
            onPressed: () async {
              final picked = await showDatePicker(
                context: context,
                initialDate: _startDate ?? DateTime.now(),
                firstDate: DateTime(2020),
                lastDate: DateTime(2030),
              );
              if (picked != null) {
                setState(() {
                  _startDate = picked;
                });
                _fetchData();
              }
            },
            child: Text(_startDate == null ? 'Эхлэх огноо' : dateFormat.format(_startDate!)),
          ),
          const SizedBox(width: 8),

          // End Date Button
          OutlinedButton(
            onPressed: () async {
              final picked = await showDatePicker(
                context: context,
                initialDate: _endDate ?? DateTime.now(),
                firstDate: DateTime(2020),
                lastDate: DateTime(2030),
              );
              if (picked != null) {
                setState(() {
                  _endDate = picked;
                });
                _fetchData();
              }
            },
            child: Text(_endDate == null ? 'Дуусах огноо' : dateFormat.format(_endDate!)),
          ),
          const SizedBox(width: 8),

          // Clear Filter Button
          if (_selectedCategoryId != null || _startDate != null || _endDate != null)
            IconButton(
              icon: const Icon(Icons.clear_all),
              onPressed: () {
                setState(() {
                  _selectedCategoryId = null;
                  _startDate = null;
                  _endDate = null;
                });
                _fetchData();
              },
            ),
        ],
      ),
    );
  }

  Widget _buildTotalSumBanner(NumberFormat format, ThemeData theme) {
    return Container(
      width: double.infinity,
      color: theme.colorScheme.primaryContainer.withOpacity(0.4),
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Text('Нийт шүүсэн зардал:', style: TextStyle(fontWeight: FontWeight.bold)),
          Text(
            format.format(_totalSum),
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
            ),
          )
        ],
      ),
    );
  }

  Color _parseColor(String? hexString) {
    if (hexString == null || hexString.isEmpty) return Colors.blue;
    try {
      final hex = hexString.replaceAll('#', '');
      return Color(int.parse('FF$hex', radix: 16));
    } catch (_) {
      return Colors.blue;
    }
  }
}
