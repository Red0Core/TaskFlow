import 'package:flutter/material.dart';
import 'package:frontend/api/api_client.dart';
import 'package:frontend/api/auth_api.dart';
import 'package:frontend/api/tasks_api.dart';
import 'package:frontend/screens/login_screen.dart';
import 'package:frontend/screens/register_screen.dart';
import 'screens/task_list_screen.dart';
import 'package:logging/logging.dart';

void _setupLogging() {
  Logger.root.level = Level.ALL; // Установите уровень логирования
  Logger.root.onRecord.listen((LogRecord record) {
    debugPrint('${record.level.name}: ${record.time}: ${record.message}');
  });
}


void main() async {
  _setupLogging();
  final apiClient = ApiClient(baseUrl: "${Uri.base.scheme}://${Uri.base.host}${(Uri.base.hasPort ? ":${Uri.base.port}" : "")}/api");
  String initialRoute = "/login";
  if (await apiClient.refreshAccessToken()) {
    initialRoute = "/tasks";
  }
  runApp(TaskApp(authApi: AuthApi(apiClient), tasksApi: TasksApi(apiClient), initialRoute: initialRoute));
}

class TaskApp extends StatelessWidget {
  final TasksApi tasksApi;
  final AuthApi authApi;
  final String initialRoute;

  const TaskApp({required this.authApi, required this.tasksApi, required this.initialRoute, super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Task Manager',
      theme: ThemeData(primarySwatch: Colors.blue),
      initialRoute: initialRoute,
      routes: {
        '/login': (context) => LoginScreen(authApi: authApi),
        '/register': (context) => RegisterScreen(authApi: authApi),
        '/tasks': (context) => TaskListScreen(tasksApi: tasksApi, authApi: authApi),
      },
    );
  }
}
