import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/category.dart';
import '../models/expense.dart';
import '../models/budget.dart';
import '../models/dashboard_stats.dart';

class ApiService {
  // Use 10.0.2.2 for Android emulator to connect to localhost on host machine
  // Use 127.0.0.1 for iOS emulator or desktop builds (macOS, Windows)
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  
  static String? _token;

  // Initialize and load saved token
  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
  }

  static bool get isAuthenticated => _token != null;

  static String? get token => _token;

  // Save token locally
  static Future<void> _saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  // Clear token locally
  static Future<void> _clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  // Common Headers
  static Map<String, String> _headers({bool multipart = false}) {
    final Map<String, String> headers = {};
    if (!multipart) {
      headers['Content-Type'] = 'application/json';
    }
    if (_token != null) {
      headers['Authorization'] = 'Token $_token';
    }
    return headers;
  }

  // --- AUTH API ---

  static Future<User?> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      await _saveToken(data['token'] as String);
      return User.fromJson(data['user'] as Map<String, dynamic>);
    } else {
      throw Exception(jsonDecode(utf8.decode(response.bodyBytes))['non_field_errors']?[0] ?? 'Login failed');
    }
  }

  static Future<User?> register(String username, String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'email': email, 'password': password}),
    );

    if (response.statusCode == 201) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      await _saveToken(data['token'] as String);
      return User.fromJson(data['user'] as Map<String, dynamic>);
    } else {
      throw Exception(jsonDecode(utf8.decode(response.bodyBytes)).toString());
    }
  }

  static Future<void> logout() async {
    if (_token == null) return;
    await http.post(
      Uri.parse('$baseUrl/auth/logout/'),
      headers: _headers(),
    );
    await _clearToken();
  }

  static Future<User?> getProfile() async {
    final response = await http.get(
      Uri.parse('$baseUrl/auth/profile/'),
      headers: _headers(),
    );

    if (response.statusCode == 200) {
      return User.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    }
    return null;
  }

  static Future<User?> updateProfile(Map<String, dynamic> data) async {
    final response = await http.put(
      Uri.parse('$baseUrl/auth/profile/'),
      headers: _headers(),
      body: jsonEncode(data),
    );

    if (response.statusCode == 200) {
      return User.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    }
    return null;
  }

  // --- DASHBOARD API ---

  static Future<DashboardStats?> getDashboardStats() async {
    final response = await http.get(
      Uri.parse('$baseUrl/dashboard/'),
      headers: _headers(),
    );

    if (response.statusCode == 200) {
      return DashboardStats.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    }
    return null;
  }

  // --- CATEGORY API ---

  static Future<List<Category>> getCategories() async {
    final response = await http.get(
      Uri.parse('$baseUrl/categories/'),
      headers: _headers(),
    );

    if (response.statusCode == 200) {
      final List data = jsonDecode(utf8.decode(response.bodyBytes)) as List;
      return data.map((c) => Category.fromJson(c as Map<String, dynamic>)).toList();
    }
    return [];
  }

  static Future<Category?> createCategory(Category category) async {
    final response = await http.post(
      Uri.parse('$baseUrl/categories/'),
      headers: _headers(),
      body: jsonEncode(category.toJson()),
    );

    if (response.statusCode == 201) {
      return Category.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    }
    return null;
  }

  static Future<bool> deleteCategory(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/categories/$id/'),
      headers: _headers(),
    );
    return response.statusCode == 204;
  }

  // --- EXPENSE API ---

  static Future<List<Expense>> getExpenses({int? categoryId, String? startDate, String? endDate}) async {
    String query = '';
    final List<String> params = [];
    if (categoryId != null) params.add('category=$categoryId');
    if (startDate != null) params.add('start_date=$startDate');
    if (endDate != null) params.add('end_date=$endDate');
    if (params.isNotEmpty) query = '?' + params.join('&');

    final response = await http.get(
      Uri.parse('$baseUrl/expenses/$query'),
      headers: _headers(),
    );

    if (response.statusCode == 200) {
      final List data = jsonDecode(utf8.decode(response.bodyBytes)) as List;
      return data.map((e) => Expense.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }

  static Future<Expense?> createExpense(Expense expense) async {
    final response = await http.post(
      Uri.parse('$baseUrl/expenses/'),
      headers: _headers(),
      body: jsonEncode(expense.toJson()),
    );

    if (response.statusCode == 201) {
      return Expense.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    }
    return null;
  }

  static Future<Expense?> updateExpense(int id, Expense expense) async {
    final response = await http.put(
      Uri.parse('$baseUrl/expenses/$id/'),
      headers: _headers(),
      body: jsonEncode(expense.toJson()),
    );

    if (response.statusCode == 200) {
      return Expense.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    }
    return null;
  }

  static Future<bool> deleteExpense(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/expenses/$id/'),
      headers: _headers(),
    );
    return response.statusCode == 204;
  }

  // --- BUDGET API ---

  static Future<List<Budget>> getBudgets() async {
    final response = await http.get(
      Uri.parse('$baseUrl/budgets/'),
      headers: _headers(),
    );

    if (response.statusCode == 200) {
      final List data = jsonDecode(utf8.decode(response.bodyBytes)) as List;
      return data.map((b) => Budget.fromJson(b as Map<String, dynamic>)).toList();
    }
    return [];
  }

  static Future<Budget?> createBudget(Budget budget) async {
    final response = await http.post(
      Uri.parse('$baseUrl/budgets/'),
      headers: _headers(),
      body: jsonEncode(budget.toJson()),
    );

    if (response.statusCode == 201) {
      return Budget.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    }
    return null;
  }

  static Future<bool> deleteBudget(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/budgets/$id/'),
      headers: _headers(),
    );
    return response.statusCode == 204;
  }
}
