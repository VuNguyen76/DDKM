import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../services/auth_service.dart';
import '../../constants/api_constants.dart';
import '../../widgets/custom_loading.dart';
import '../login_page.dart';
import '../face_attendance_page.dart';

class StudentHomePage extends StatefulWidget {
  const StudentHomePage({super.key});

  @override
  State<StudentHomePage> createState() => _StudentHomePageState();
}

class _StudentHomePageState extends State<StudentHomePage>
    with SingleTickerProviderStateMixin {
  final _authService = AuthService();
  bool _isLoading = true;
  Map<String, dynamic>? _userInfo;
  List<dynamic> _todaySchedule = [];
  List<dynamic> _allClasses = [];
  List<dynamic> _attendanceHistory = [];
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
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

      // Get today's schedule - use Tuesday for testing
      final dateStr = '2025-10-21'; // Tuesday for testing

      try {
        final scheduleResponse = await http.get(
          Uri.parse(
            '${ApiConstants.baseUrl}/student/my-schedule?schedule_date=$dateStr',
          ),
          headers: {'session-id': sessionId},
        );

        if (scheduleResponse.statusCode == 200) {
          final data = json.decode(scheduleResponse.body);
          print('Schedule response: $data');
          _todaySchedule = data['schedules'] ?? [];
        }
      } catch (e) {
        print('Error loading schedule: $e');
      }

      // Get all classes
      try {
        print('About to load classes...');
        final classesResponse = await http.get(
          Uri.parse('${ApiConstants.baseUrl}/student/my-classes'),
          headers: {'session-id': sessionId},
        );

        print('Classes status code: ${classesResponse.statusCode}');
        if (classesResponse.statusCode == 200) {
          final data = json.decode(classesResponse.body);
          print('Classes response type: ${data.runtimeType}');
          if (data is List) {
            _allClasses = data;
            print('Loaded ${_allClasses.length} classes');
          } else {
            _allClasses = [];
          }
        }
      } catch (e, stackTrace) {
        print('Error loading classes: $e');
        print('Stack trace: $stackTrace');
      }

      // Get attendance history
      try {
        final attendanceResponse = await http.get(
          Uri.parse('${ApiConstants.baseUrl}/student/my-attendance'),
          headers: {'session-id': sessionId},
        );

        if (attendanceResponse.statusCode == 200) {
          final data = json.decode(attendanceResponse.body);
          if (data is List) {
            _attendanceHistory = data;
          } else {
            _attendanceHistory = [];
          }
        }
      } catch (e) {
        print('Error loading attendance: $e');
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFEAF4FB),
      appBar: AppBar(
        title: const Text('Trang sinh viên'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData),
          IconButton(icon: const Icon(Icons.logout), onPressed: _logout),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'Hôm nay'),
            Tab(text: 'Lịch sử'),
          ],
        ),
      ),
      body: _isLoading
          ? const CustomLoading()
          : TabBarView(
              controller: _tabController,
              children: [_buildTodayTab(), _buildHistoryTab()],
            ),
    );
  }

  Widget _buildTodayTab() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // User info card
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: InkWell(
                onTap: () {
                  // Navigate to profile page
                  Navigator.pushNamed(context, '/student-profile');
                },
                borderRadius: BorderRadius.circular(16),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 40,
                        backgroundColor: Colors.blue.shade100,
                        child: Icon(
                          Icons.person,
                          size: 45,
                          color: Colors.blue.shade700,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _userInfo?['full_name'] ?? 'Sinh viên',
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'MSSV: ${_userInfo?['student']?['student_code'] ?? ''}',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey.shade700,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Icon(
                        Icons.arrow_forward_ios,
                        color: Colors.grey.shade600,
                        size: 20,
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Today's schedule
            Text(
              'Lịch học hôm nay',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade900,
              ),
            ),
            const SizedBox(height: 12),
            _todaySchedule.isEmpty
                ? Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20.0),
                      child: Center(
                        child: Text(
                          'Không có lịch học hôm nay',
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ),
                    ),
                  )
                : Column(
                    children: _todaySchedule.map((schedule) {
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        elevation: 2,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: Colors.blue.shade100,
                            child: Icon(
                              Icons.schedule,
                              color: Colors.blue.shade700,
                            ),
                          ),
                          title: Text(
                            schedule['subject_name'] ?? '',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '${schedule['start_time']} - ${schedule['end_time']}',
                              ),
                              Text(
                                'Lớp: ${schedule['class_code']} | Phòng: ${schedule['room']}',
                              ),
                              Text(
                                'GV: ${schedule['teacher_name']} | ${schedule['mode']}',
                              ),
                            ],
                          ),
                          trailing: ElevatedButton(
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => FaceAttendancePage(
                                    classId: schedule['class_id'],
                                    className: schedule['subject_name'],
                                  ),
                                ),
                              );
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                              foregroundColor: Colors.white,
                            ),
                            child: const Text('Điểm danh'),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryTab() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: _attendanceHistory.length,
        itemBuilder: (context, index) {
          final record = _attendanceHistory[index];
          final status = record['status'] ?? '';
          Color statusColor = Colors.grey;
          String statusText = status;

          if (status == 'present') {
            statusColor = Colors.green;
            statusText = 'Có mặt';
          } else if (status == 'late') {
            statusColor = Colors.orange;
            statusText = 'Muộn';
          } else if (status == 'absent') {
            statusColor = Colors.red;
            statusText = 'Vắng';
          }

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: statusColor,
                child: Icon(
                  status == 'present'
                      ? Icons.check
                      : status == 'late'
                      ? Icons.access_time
                      : Icons.close,
                  color: Colors.white,
                ),
              ),
              title: Text(
                record['class_name'] ?? '',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text(
                'Ngày: ${record['session_date']}\n'
                'Giờ: ${record['start_time']} - ${record['end_time']}\n'
                'Điểm danh: ${record['check_in_time'] ?? 'Chưa điểm danh'}',
              ),
              trailing: Chip(
                label: Text(statusText),
                backgroundColor: statusColor.withOpacity(0.2),
                labelStyle: TextStyle(
                  color: statusColor,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
