import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../models/budget.dart';
import '../../models/category.dart';
import '../../widgets/responsive_layout.dart';
import 'package:intl/intl.dart';

class BudgetScreen extends StatefulWidget {
  const BudgetScreen({Key? key}) : super(key: key);

  @override
  _BudgetScreenState createState() => _BudgetScreenState();
}

class _BudgetScreenState extends State<BudgetScreen> {
  bool _isLoading = true;
  List<Budget> _budgets = [];
  List<Category> _categories = [];
  String? _errorMessage;

  // New Budget Form state
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _amountController = TextEditingController();
  final _notesController = TextEditingController();
  int? _selectedCategoryId;
  DateTime _startDate = DateTime.now();
  DateTime _endDate = DateTime.now().add(const Duration(days: 30));

  @override
  void initState() {
    super.initState();
    _fetchBudgets();
  }

  Future<void> _fetchBudgets() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final buds = await ApiService.getBudgets();
      final cats = await ApiService.getCategories();
      setState(() {
        _budgets = buds;
        _categories = cats;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Төсвийн мэдээлэл авахад алдаа гарлаа: $e';
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
        title: const Text('Төсөв устгах уу?'),
        content: const Text('Энэ төсвийг устгахдаа итгэлтэй байна уу?'),
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
        final success = await ApiService.deleteBudget(id);
        if (success && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Төсөв амжилттай устлаа')),
          );
          _fetchBudgets();
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

  Future<void> _showAddBudgetDialog() async {
    _nameController.clear();
    _amountController.clear();
    _notesController.clear();
    _selectedCategoryId = null;
    _startDate = DateTime.now();
    _endDate = DateTime.now().add(const Duration(days: 30));

    await showDialog(
      context: context,
      builder: (context) {
        final dateFormat = DateFormat('yyyy-MM-dd');
        return StatefulBuilder(
          builder: (context, setStateDialog) {
            return AlertDialog(
              title: const Text('Шинэ төсөв үүсгэх'),
              content: SingleChildScrollView(
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Name
                      TextFormField(
                        controller: _nameController,
                        decoration: const InputDecoration(labelText: 'Төсвийн нэр'),
                        validator: (v) => v == null || v.trim().isEmpty ? 'Нэр оруулна уу' : null,
                      ),
                      const SizedBox(height: 12),
                      
                      // Amount
                      TextFormField(
                        controller: _amountController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(labelText: 'Нийт дүн (Төгрөгөөр)'),
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return 'Дүн оруулна уу';
                          if (double.tryParse(v) == null) return 'Тоо оруулна уу';
                          return null;
                        },
                      ),
                      const SizedBox(height: 12),

                      // Category (Optional)
                      DropdownButtonFormField<int>(
                        value: _selectedCategoryId,
                        decoration: const InputDecoration(labelText: 'Холбох ангилал (Сонголтоор)'),
                        items: [
                          const DropdownMenuItem<int>(value: null, child: Text('Бүх ангилал')),
                          ..._categories.map((c) => DropdownMenuItem<int>(value: c.id, child: Text(c.name))),
                        ],
                        onChanged: (val) {
                          setStateDialog(() {
                            _selectedCategoryId = val;
                          });
                        },
                      ),
                      const SizedBox(height: 16),

                      // Start Date
                      Row(
                        children: [
                          Expanded(child: Text('Эхлэх: ${dateFormat.format(_startDate)}')),
                          TextButton(
                            onPressed: () async {
                              final picked = await showDatePicker(
                                context: context,
                                initialDate: _startDate,
                                firstDate: DateTime(2020),
                                lastDate: DateTime(2030),
                              );
                              if (picked != null) {
                                setStateDialog(() {
                                  _startDate = picked;
                                });
                              }
                            },
                            child: const Text('Сонгох'),
                          ),
                        ],
                      ),

                      // End Date
                      Row(
                        children: [
                          Expanded(child: Text('Дуусах: ${dateFormat.format(_endDate)}')),
                          TextButton(
                            onPressed: () async {
                              final picked = await showDatePicker(
                                context: context,
                                initialDate: _endDate,
                                firstDate: DateTime(2020),
                                lastDate: DateTime(2030),
                              );
                              if (picked != null) {
                                setStateDialog(() {
                                  _endDate = picked;
                                });
                              }
                            },
                            child: const Text('Сонгох'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),

                      // Notes
                      TextFormField(
                        controller: _notesController,
                        maxLines: 2,
                        decoration: const InputDecoration(labelText: 'Тэмдэглэл / Тайлбар'),
                      ),
                    ],
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Цуцлах'),
                ),
                ElevatedButton(
                  onPressed: () async {
                    if (!_formKey.currentState!.validate()) return;
                    
                    final newBudget = Budget(
                      id: 0,
                      user: 0,
                      name: _nameController.text.trim(),
                      totalAmount: double.parse(_amountController.text.trim()),
                      startDate: _startDate,
                      endDate: _endDate,
                      notes: _notesController.text.trim(),
                      categoryId: _selectedCategoryId,
                      createdAt: DateTime.now(),
                      allocations: [],
                    );

                    try {
                      final saved = await ApiService.createBudget(newBudget);
                      if (saved != null && mounted) {
                        Navigator.pop(context);
                        _fetchBudgets();
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Төсөв амжилттай үүслээ!')),
                        );
                      }
                    } catch (e) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Алдаа гарлаа: $e')),
                      );
                    }
                  },
                  child: const Text('Үүсгэх'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currencyFormat = NumberFormat.currency(locale: 'mn_MN', symbol: '₮', decimalDigits: 0);
    final dateFormat = DateFormat('yyyy-MM-dd');

    return ResponsiveLayout(
      currentIndex: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Миний төсөвлөлтүүд'),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _fetchBudgets,
            ),
          ],
        ),
        body: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _errorMessage != null
                ? Center(child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)))
                : _budgets.isEmpty
                    ? const Center(child: Text('Тохируулсан төсөв одоогоор байхгүй байна.'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _budgets.length,
                        itemBuilder: (context, index) {
                          final budget = _budgets[index];

                          return Card(
                            margin: const EdgeInsets.symmetric(vertical: 10),
                            elevation: 3,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                            child: Padding(
                              padding: const EdgeInsets.all(20.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          budget.name,
                                          style: theme.textTheme.titleMedium?.copyWith(
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                      IconButton(
                                        icon: const Icon(Icons.delete_outline, color: Colors.red),
                                        onPressed: () => _handleDelete(budget.id),
                                      )
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Нийт дүн: ${currencyFormat.format(budget.totalAmount)}',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                      color: theme.colorScheme.primary,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Row(
                                    children: [
                                      const Icon(Icons.date_range_outlined, size: 16, color: Colors.grey),
                                      const SizedBox(width: 8),
                                      Text(
                                        'Хугацаа: ${dateFormat.format(budget.startDate)} - ${dateFormat.format(budget.endDate)}',
                                        style: const TextStyle(color: Colors.grey, fontSize: 13),
                                      ),
                                    ],
                                  ),
                                  if (budget.categoryDetails != null) ...[
                                    const SizedBox(height: 8),
                                    Chip(
                                      avatar: const Icon(Icons.category_outlined, size: 16),
                                      label: Text(budget.categoryDetails!.name),
                                    ),
                                  ],
                                  if (budget.notes.isNotEmpty) ...[
                                    const SizedBox(height: 12),
                                    Text(
                                      budget.notes,
                                      style: TextStyle(color: Colors.grey[700], fontStyle: FontStyle.italic),
                                    ),
                                  ]
                                ],
                              ),
                            ),
                          );
                        },
                      ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _showAddBudgetDialog,
          icon: const Icon(Icons.add),
          label: const Text('Шинэ төсөв'),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _amountController.dispose();
    _notesController.dispose();
    super.dispose();
  }
}
