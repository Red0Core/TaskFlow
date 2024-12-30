import 'package:frontend/api/tasks_api.dart';

class Task {
  final int id;
  String title;
  String description;
  bool isCompleted;

  final TasksApi _api;

  Task({
    required this.id,
    required this.title,
    required this.description,
    this.isCompleted = false,
    required TasksApi api,
  }) : _api = api;

  // Создание задачи
  static Future<Task> create(String title, String description, TasksApi api) async {
    final data = {'title': title, 'description': description};
    final response = await api.createTask(data);
    return Task(
      id: response['id'],
      title: response['title'],
      description: response['description'],
      isCompleted: response['is_completed'],
      api: api,
    );
  }

  // Обновление задачи
  Future<void> update({String? newTitle, String? newDescription, bool? newIsCompleted}) async {
    final data = <String, dynamic>{};
    if (newTitle != null) {
      data['title'] = newTitle;
      title = newTitle;
    }
    if (newDescription != null) {
      data['description'] = newDescription;
      description = newDescription;
    }
    if (newIsCompleted != null) {
      data['is_completed'] = newIsCompleted;
      isCompleted = newIsCompleted;
    }

    await _api.patchTask(id, data);
  }

  // Удаление задачи
  Future<void> delete() async {
    await _api.deleteTask(id);
  }

  // Загрузка всех задач
  static Future<List<Task>> fetchAll(TasksApi api, {bool? showOnlyCompleted}) async {
    final tasksData = await api.fetchTasks(showOnlyCompleted: showOnlyCompleted);
    return tasksData.map((data) => Task(
      id: data['id'],
      title: data['title'],
      description: data['description'],
      isCompleted: data['is_completed'],
      api: api,
    )).toList();
  }
}
