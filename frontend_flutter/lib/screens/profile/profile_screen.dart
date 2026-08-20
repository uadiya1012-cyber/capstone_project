import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../models/user.dart';
import '../../widgets/responsive_layout.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  _ProfileScreenState createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isLoading = true;
  User? _user;
  String? _errorMessage;

  // Edit fields controller
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();
  final _currencyController = TextEditingController();
  final _dailyLimitController = TextEditingController();
  final _savingsGoalController = TextEditingController();
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final user = await ApiService.getProfile();
      if (user != null) {
        setState(() {
          _user = user;
          _phoneController.text = user.phoneNumber ?? '';
          _currencyController.text = user.currency;
          _dailyLimitController.text = user.dailyLimit.toString();
          _savingsGoalController.text = user.monthlySavingsGoal.toString();
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Хэрэглэгчийн мэдээлэл авахад алдаа гарлаа: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _handleSave() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSaving = true;
      _errorMessage = null;
    });

    try {
      final updatedUser = await ApiService.updateProfile({
        'phone_number': _phoneController.text.trim(),
        'currency': _currencyController.text.trim(),
        'daily_limit': double.parse(_dailyLimitController.text.trim()),
        'monthly_savings_goal': double.parse(_savingsGoalController.text.trim()),
      });

      if (updatedUser != null && mounted) {
        setState(() {
          _user = updatedUser;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Мэдээлэл амжилттай шинэчлэгдлээ!')),
        );
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Хадгалахад алдаа гарлаа: $e';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return ResponsiveLayout(
      currentIndex: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Хэрэглэгчийн тохиргоо'),
        ),
        body: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _errorMessage != null && _user == null
                ? Center(child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)))
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
                              // Avatar / Initials
                              Center(
                                child: CircleAvatar(
                                  radius: 50,
                                  backgroundColor: theme.colorScheme.primary.withOpacity(0.2),
                                  child: Text(
                                    (_user?.username ?? 'U').substring(0, 1).toUpperCase(),
                                    style: TextStyle(
                                      fontSize: 36,
                                      fontWeight: FontWeight.bold,
                                      color: theme.colorScheme.primary,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 16),
                              
                              // Username and Email
                              Text(
                                _user?.username ?? '',
                                textAlign: TextAlign.center,
                                style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
                              ),
                              Text(
                                _user?.email ?? '',
                                textAlign: TextAlign.center,
                                style: const TextStyle(color: Colors.grey),
                              ),
                              const SizedBox(height: 32),

                              if (_errorMessage != null) ...[
                                Text(
                                  _errorMessage!,
                                  style: const TextStyle(color: Colors.red),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 16),
                              ],

                              // Phone number
                              TextFormField(
                                controller: _phoneController,
                                decoration: InputDecoration(
                                  labelText: 'Утасны дугаар',
                                  prefixIcon: const Icon(Icons.phone_outlined),
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                              ),
                              const SizedBox(height: 20),

                              // Currency Symbol
                              TextFormField(
                                controller: _currencyController,
                                decoration: InputDecoration(
                                  labelText: 'Мөнгөн тэмдэгт (₮, \$, €, г.м)',
                                  prefixIcon: const Icon(Icons.money_outlined),
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                                validator: (v) => v == null || v.trim().isEmpty ? 'Мөнгөн тэмдэгт оруулна уу' : null,
                              ),
                              const SizedBox(height: 20),

                              // Daily limit
                              TextFormField(
                                controller: _dailyLimitController,
                                keyboardType: TextInputType.number,
                                decoration: InputDecoration(
                                  labelText: 'Өдрийн зарцуулалтын хязгаар',
                                  prefixIcon: const Icon(Icons.warning_amber_outlined),
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                                validator: (v) {
                                  if (v == null || v.trim().isEmpty) return 'Хязгаар оруулах эсвэл 0 гэж бичнэ үү';
                                  if (double.tryParse(v) == null) return 'Тоо оруулна уу';
                                  return null;
                                },
                              ),
                              const SizedBox(height: 20),

                              // Monthly savings goal
                              TextFormField(
                                controller: _savingsGoalController,
                                keyboardType: TextInputType.number,
                                decoration: InputDecoration(
                                  labelText: 'Сарын хуримтлалын зорилт',
                                  prefixIcon: const Icon(Icons.track_changes_outlined),
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                                validator: (v) {
                                  if (v == null || v.trim().isEmpty) return 'Зорилт оруулах эсвэл 0 гэж бичнэ үү';
                                  if (double.tryParse(v) == null) return 'Тоо оруулна уу';
                                  return null;
                                },
                              ),
                              const SizedBox(height: 32),

                              // Save Button
                              ElevatedButton(
                                onPressed: _isSaving ? null : _handleSave,
                                style: ElevatedButton.styleFrom(
                                  padding: const EdgeInsets.symmetric(vertical: 16),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                                child: _isSaving
                                    ? const SizedBox(
                                        height: 20,
                                        width: 20,
                                        child: CircularProgressIndicator(strokeWidth: 2),
                                      )
                                    : const Text('Мэдээлэл хадгалах', style: TextStyle(fontSize: 16)),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
      ),
    );
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _currencyController.dispose();
    _dailyLimitController.dispose();
    _savingsGoalController.dispose();
    super.dispose();
  }
}
