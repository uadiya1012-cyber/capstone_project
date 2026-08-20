import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../models/expense.dart';
import '../../models/category.dart';
import '../../models/budget.dart';
import 'package:intl/intl.dart';

class ExpenseFormScreen extends StatefulWidget {
  final Expense? expense;

  const ExpenseFormScreen({Key? key, this.expense}) : super(key: key);

  @override
  _ExpenseFormScreenState createState() => _ExpenseFormScreenState();
}

class _ExpenseFormScreenState extends State<ExpenseFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  
  List<Category> _categories = [];
  List<Budget> _budgets = [];
  int? _selectedCategoryId;
  int? _selectedBudgetId;
  DateTime _selectedDate = DateTime.now();
  bool _isRecurring = false;
  String _recurringInterval = '';

  bool _isLoading = false;
  bool _isDataFetching = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    if (widget.expense != null) {
      _amountController.text = widget.expense!.amount.toString();
      _descriptionController.text = widget.expense!.description;
      _selectedDate = widget.expense!.date;
      _selectedCategoryId = widget.expense!.categoryId;
      _selectedBudgetId = widget.expense!.budgetId;
      _isRecurring = widget.expense!.isRecurring;
      _recurringInterval = widget.expense!.recurringInterval;
    }
    _fetchFormData();
  }

  Future<void> _fetchFormData() async {
    try {
      final cats = await ApiService.getCategories();
      final buds = await ApiService.getBudgets();
      setState(() {
        _categories = cats;
        _budgets = buds;
        _isDataFetching = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Мэдээлэл авахад алдаа гарлаа: $e';
        _isDataFetching = false;
      });
    }
  }

  Future<void> _handleSave() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final double amount = double.parse(_amountController.text.trim());
      
      final expenseObj = Expense(
        id: widget.expense?.id ?? 0,
        user: widget.expense?.user ?? 0,
        amount: amount,
        categoryId: _selectedCategoryId,
        date: _selectedDate,
        description: _descriptionController.text.trim(),
        budgetId: _selectedBudgetId,
        isRecurring: _isRecurring,
        recurringInterval: _isRecurring ? _recurringInterval : '',
        createdAt: widget.expense?.createdAt ?? DateTime.now(),
      );

      Expense? saved;
      if (widget.expense == null) {
        saved = await ApiService.createExpense(expenseObj);
      } else {
        saved = await ApiService.updateExpense(widget.expense!.id, expenseObj);
      }

      if (saved != null && mounted) {
        Navigator.pop(context, true);
      } else {
        throw Exception('Хадгалж чадсангүй');
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Хадгалахад алдаа гарлаа: $e';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isEdit = widget.expense != null;
    final dateFormat = DateFormat('yyyy-MM-dd');

    return Scaffold(
      appBar: AppBar(
        title: Text(isEdit ? 'Зардал засах' : 'Шинэ зардал бүртгэх'),
      ),
      body: _isDataFetching
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Center(
                child: Container(
                  constraints: const BoxConstraints(maxWidth: 500),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (_errorMessage != null) ...[
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.red[50],
                              border: Border.all(color: Colors.red.shade200),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              _errorMessage!,
                              style: const TextStyle(color: Colors.red),
                              textAlign: TextAlign.center,
                            ),
                          ),
                          const SizedBox(height: 20),
                        ],

                        // Amount field
                        TextFormField(
                          controller: _amountController,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: InputDecoration(
                            labelText: 'Зардлын хэмжээ (Төгрөгөөр)',
                            prefixIcon: const Icon(Icons.attach_money),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          validator: (value) {
                            if (value == null || value.trim().isEmpty) {
                              return 'Зарлагын дүнг оруулна уу';
                            }
                            if (double.tryParse(value) == null) {
                              return 'Зөвхөн тоо оруулна уу';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 20),

                        // Category Dropdown
                        DropdownButtonFormField<int>(
                          value: _selectedCategoryId,
                          decoration: InputDecoration(
                            labelText: 'Категори ангилал',
                            prefixIcon: const Icon(Icons.category_outlined),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          items: _categories.map((cat) {
                            return DropdownMenuItem<int>(
                              value: cat.id,
                              child: Text(cat.name),
                            );
                          }).toList(),
                          onChanged: (value) {
                            setState(() {
                              _selectedCategoryId = value;
                            });
                          },
                          validator: (value) {
                            if (value == null) {
                              return 'Ангилал сонгоно уу';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 20),

                        // Budget Dropdown (Optional)
                        DropdownButtonFormField<int>(
                          value: _selectedBudgetId,
                          decoration: InputDecoration(
                            labelText: 'Төсөвт холбох (Сонголтоор)',
                            prefixIcon: const Icon(Icons.pie_chart_outline),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          items: [
                            const DropdownMenuItem<int>(
                              value: null,
                              child: Text('Төсөвт холбохгүй'),
                            ),
                            ..._budgets.map((b) {
                              return DropdownMenuItem<int>(
                                value: b.id,
                                child: Text(b.name),
                              );
                            }),
                          ],
                          onChanged: (value) {
                            setState(() {
                              _selectedBudgetId = value;
                            });
                          },
                        ),
                        const SizedBox(height: 20),

                        // Date Picker Button
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                'Зарлагын огноо: ${dateFormat.format(_selectedDate)}',
                                style: const TextStyle(fontSize: 16),
                              ),
                            ),
                            OutlinedButton.icon(
                              onPressed: () async {
                                final picked = await showDatePicker(
                                  context: context,
                                  initialDate: _selectedDate,
                                  firstDate: DateTime(2020),
                                  lastDate: DateTime(2030),
                                );
                                if (picked != null) {
                                  setState(() {
                                    _selectedDate = picked;
                                  });
                                }
                              },
                              icon: const Icon(Icons.calendar_today),
                              label: const Text('Сонгох'),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),

                        // Description field
                        TextFormField(
                          controller: _descriptionController,
                          maxLines: 3,
                          decoration: InputDecoration(
                            labelText: 'Тэмдэглэл / Тайлбар',
                            prefixIcon: const Icon(Icons.edit_note_outlined),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),

                        // Is Recurring Switch
                        SwitchListTile(
                          title: const Text('Давтамжтай зардал уу?'),
                          value: _isRecurring,
                          onChanged: (value) {
                            setState(() {
                              _isRecurring = value;
                              if (value && _recurringInterval.isEmpty) {
                                _recurringInterval = 'monthly';
                              }
                            });
                          },
                        ),

                        if (_isRecurring) ...[
                          const SizedBox(height: 12),
                          DropdownButtonFormField<String>(
                            value: _recurringInterval,
                            decoration: InputDecoration(
                              labelText: 'Давтах хугацаа',
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            items: const [
                              DropdownMenuItem(value: 'daily', child: Text('Өдөр бүр')),
                              DropdownMenuItem(value: 'weekly', child: Text('7 хоног бүр')),
                              DropdownMenuItem(value: 'monthly', child: Text('Сар бүр')),
                            ],
                            onChanged: (value) {
                              setState(() {
                                _recurringInterval = value ?? 'monthly';
                              });
                            },
                          ),
                        ],

                        const SizedBox(height: 32),

                        // Save Button
                        ElevatedButton(
                          onPressed: _isLoading ? null : _handleSave,
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : Text(isEdit ? 'Шинэчлэх' : 'Хадгалах', style: const TextStyle(fontSize: 16)),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
    );
  }

  @override
  void dispose() {
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }
}
