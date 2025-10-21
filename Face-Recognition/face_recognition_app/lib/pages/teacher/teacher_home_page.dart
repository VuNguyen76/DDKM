import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import '../../services/auth_service.dart';
import '../../constants/api_constants.dart';
import '../../widgets/custom_loading.dart';
import '../login_page.dart';
import 'teacher_class_detail_page.dart';

class TeacherHomePage extends StatefulWidget {
  const TeacherHomePage({super.key});

  @override
  State<TeacherHomePage> createState() => _TeacherHomePageState();
}

class _TeacherHomePageState extends State<TeacherHomePage> {
  final _authService = AuthService();
  bool _isLoading = true;
  Map<String, dynamic>? _userInfo;
  List<dynamic> _myClasses = [];
  DateTime _selectedDate = DateTime.now();
  String _calendarView = 'Month'; // Month, Week, Day

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final sessionId = await _authService.getSessionId();
      if (sessionId == null) {
        _logout();
        return;
      }

      // Get user info
      final userResponse = await http.get(
        Uri.parse('${ApiConstants.baseUrl}/auth/me'),
        headers: {'session-id': sessionId},
      );

      if (userResponse.statusCode == 200) {
        _userInfo = json.decode(userResponse.body);
      }

      // Get my classes
      final classesResponse = await http.get(
        Uri.parse('${ApiConstants.baseUrl}/teacher/my-classes'),
        headers: {'session-id': sessionId},
      );

      if (classesResponse.statusCode == 200) {
        _myClasses = json.decode(classesResponse.body);
      }
    } catch (e) {
      // ignore: avoid_print
      print('Error loading data: $e');
    }

    setState(() {
      _isLoading = false;
    });
  }

  Future<void> _logout() async {
    await _authService.logout();
    if (mounted) {
      Navigator.of(
        context,
      ).pushReplacement(MaterialPageRoute(builder: (_) => const LoginPage()));
    }
  }

  // Get classes for selected date
  List<Map<String, dynamic>> _getTodayClasses() {
    final dayOfWeek = _selectedDate.weekday == 7
        ? 7
        : _selectedDate.weekday; // 1=Mon, 7=Sun

    List<Map<String, dynamic>> todayClasses = [];

    for (var classItem in _myClasses) {
      final schedules = classItem['schedules'] as List? ?? [];
      for (var schedule in schedules) {
        if (schedule['day_of_week'] == dayOfWeek) {
          todayClasses.add({
            'class_id': classItem['class_id'],
            'class_name': classItem['class_name'],
            'class_code': classItem['class_code'],
            'subject_name': classItem['subject_name'],
            'start_time': schedule['start_time'],
            'end_time': schedule['end_time'],
            'room': schedule['room'],
            'mode': schedule['mode'],
            'student_count': classItem['student_count'],
            'schedules': schedules,
          });
        }
      }
    }

    // Sort by start_time
    todayClasses.sort((a, b) => a['start_time'].compareTo(b['start_time']));

    return todayClasses;
  }

  // Get status of a class (Hoàn thành, Đang giảng dạy, Sắp tới)
  String _getClassStatus(String startTime, String endTime) {
    final now = DateTime.now();
    final start = _parseTime(startTime);
    final end = _parseTime(endTime);

    if (now.isAfter(end)) {
      return 'Hoàn thành';
    } else if (now.isAfter(start) && now.isBefore(end)) {
      return 'Đang giảng dạy';
    } else {
      return 'Sắp tới';
    }
  }

  DateTime _parseTime(String timeStr) {
    final parts = timeStr.split(':');
    final now = DateTime.now();
    return DateTime(
      now.year,
      now.month,
      now.day,
      int.parse(parts[0]),
      int.parse(parts[1]),
      parts.length > 2 ? int.parse(parts[2]) : 0,
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          const DrawerHeader(
            decoration: BoxDecoration(color: Color(0xFF0066FF)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Icon(Icons.person, size: 48, color: Colors.white),
                SizedBox(height: 8),
                Text(
                  'Giáo viên',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.home),
            title: const Text('Trang chủ'),
            onTap: () => Navigator.pop(context),
          ),
          ListTile(
            leading: const Icon(Icons.class_),
            title: const Text('Lớp học của tôi'),
            onTap: () {
              Navigator.pop(context);
              // Already on home page showing classes
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Đăng xuất'),
            onTap: () {
              Navigator.pop(context);
              _logout();
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final todayClasses = _getTodayClasses();

    return Scaffold(
      backgroundColor: const Color(0xFFEAF7FF),
      drawer: _buildDrawer(),
      body: _isLoading
          ? const CustomLoading()
          : SafeArea(
              child: RefreshIndicator(
                onRefresh: _loadData,
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header
                      Row(
                        children: [
                          Builder(
                            builder: (context) => IconButton(
                              icon: const Icon(
                                Icons.menu,
                                size: 20,
                                color: Colors.black,
                              ),
                              onPressed: () =>
                                  Scaffold.of(context).openDrawer(),
                            ),
                          ),
                          const Expanded(
                            child: Text(
                              'Trang chủ',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFFC7C7C7),
                              ),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.logout, size: 20),
                            onPressed: _logout,
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),

                      // Calendar widget
                      _buildCalendarWidget(),
                      const SizedBox(height: 16),

                      // Today's classes card
                      _buildTodayClassesCard(todayClasses),
                    ],
                  ),
                ),
              ),
            ),
    );
  }

  Widget _buildCalendarWidget() {
    final firstDayOfMonth = DateTime(
      _selectedDate.year,
      _selectedDate.month,
      1,
    );
    final lastDayOfMonth = DateTime(
      _selectedDate.year,
      _selectedDate.month + 1,
      0,
    );
    final daysInMonth = lastDayOfMonth.day;
    final startWeekday = firstDayOfMonth.weekday; // 1=Mon, 7=Sun

    return Container(
      width: 394,
      height: 416,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFBEE5FF)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.chevron_left, size: 20),
                    onPressed: () {
                      setState(() {
                        _selectedDate = DateTime(
                          _selectedDate.year,
                          _selectedDate.month - 1,
                        );
                      });
                    },
                  ),
                  Text(
                    DateFormat('MMMM yyyy').format(_selectedDate),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.chevron_right, size: 20),
                    onPressed: () {
                      setState(() {
                        _selectedDate = DateTime(
                          _selectedDate.year,
                          _selectedDate.month + 1,
                        );
                      });
                    },
                  ),
                ],
              ),
              const Icon(Icons.settings, size: 20),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'Today is ${DateFormat('MMM dd').format(DateTime.now())}',
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
          const SizedBox(height: 12),

          // Tab selector (bên trái)
          Row(
            children: [
              _buildTabButton('Month'),
              const SizedBox(width: 8),
              _buildTabButton('Week'),
              const SizedBox(width: 8),
              _buildTabButton('Day'),
            ],
          ),
          const SizedBox(height: 16),

          // Calendar grid
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 7,
                mainAxisSpacing: 8,
                crossAxisSpacing: 8,
              ),
              itemCount: daysInMonth + startWeekday - 1,
              itemBuilder: (context, index) {
                if (index < startWeekday - 1) {
                  return Container(); // Empty cells before first day
                }
                final day = index - startWeekday + 2;
                final isToday =
                    day == DateTime.now().day &&
                    _selectedDate.month == DateTime.now().month &&
                    _selectedDate.year == DateTime.now().year;
                final isSelected = day == _selectedDate.day;

                return GestureDetector(
                  onTap: () {
                    setState(() {
                      _selectedDate = DateTime(
                        _selectedDate.year,
                        _selectedDate.month,
                        day,
                      );
                    });
                  },
                  child: Container(
                    width: 15,
                    height: 15,
                    decoration: BoxDecoration(
                      color: isToday
                          ? const Color(0xFF0066FF)
                          : isSelected
                          ? Colors.blue.shade100
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(4),
                      border: isSelected && !isToday
                          ? Border.all(color: Colors.blue)
                          : null,
                    ),
                    child: Center(
                      child: Text(
                        '$day',
                        style: TextStyle(
                          fontSize: 12,
                          color: isToday ? Colors.white : Colors.black,
                          fontWeight: isToday || isSelected
                              ? FontWeight.bold
                              : FontWeight.normal,
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabButton(String label) {
    final isSelected = _calendarView == label;
    return GestureDetector(
      onTap: () {
        setState(() {
          _calendarView = label;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue : Colors.transparent,
          border: Border.all(color: Colors.blue),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 13,
            color: isSelected ? Colors.white : Colors.blue,
          ),
        ),
      ),
    );
  }

  Widget _buildTodayClassesCard(List<Map<String, dynamic>> todayClasses) {
    final isToday =
        _selectedDate.year == DateTime.now().year &&
        _selectedDate.month == DateTime.now().month &&
        _selectedDate.day == DateTime.now().day;
    final title = isToday
        ? 'Buổi học hôm nay'
        : 'Buổi học ngày ${DateFormat('dd/MM/yyyy').format(_selectedDate)}';

    return Container(
      width: 394,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFBEE5FF)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          if (todayClasses.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(24.0),
                child: Text('Không có buổi học nào'),
              ),
            )
          else
            ...todayClasses.map((classItem) => _buildClassCard(classItem)),
        ],
      ),
    );
  }

  Widget _buildClassCard(Map<String, dynamic> classItem) {
    final status = _getClassStatus(
      classItem['start_time'],
      classItem['end_time'],
    );
    Color chipColor;
    Color chipTextColor;

    if (status == 'Hoàn thành') {
      chipColor = const Color(0xFFD7FAD2);
      chipTextColor = const Color(0xFF1E9E3F);
    } else if (status == 'Đang giảng dạy') {
      chipColor = const Color(0xFFD2E4FA);
      chipTextColor = const Color(0xFF007AFF);
    } else {
      chipColor = const Color(0xFFF0F0F0);
      chipTextColor = const Color(0xFF555555);
    }

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => TeacherClassDetailPage(
              classId: classItem['class_id'],
              className: classItem['class_name'],
              subjectName: classItem['subject_name'],
              startTime: classItem['start_time'],
              endTime: classItem['end_time'],
              room: classItem['room'],
              mode: classItem['mode'],
              studentCount: classItem['student_count'],
            ),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFFE0E0E0)),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    classItem['subject_name'].toUpperCase(),
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '⏰ Thời gian: ${classItem['start_time']} – ${classItem['end_time']}',
                  ),
                  Text('📍 Phòng học: ${classItem['room']}'),
                  Text('👨‍🎓 Sinh viên: ${classItem['student_count']}'),
                  Text(
                    '💻 Hình thức: ${classItem['mode'] == 'online' ? 'Online' : 'Offline'}',
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: chipColor,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      status,
                      style: TextStyle(fontSize: 12, color: chipTextColor),
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, size: 20),
          ],
        ),
      ),
    );
  }
}
