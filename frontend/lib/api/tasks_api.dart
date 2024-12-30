import 'api_client.dart';

class TasksApi {
  final ApiClient apiClient;

  TasksApi(this.apiClient);

  Future<List<Map<String, dynamic>>> fetchTasks({bool? showOnlyCompleted}) async {
    try {
      final response = await apiClient.client.get(
        '/tasks',
        queryParameters: showOnlyCompleted != null
            ? {"is_completed": showOnlyCompleted}
            : null,
      );
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      log.warning('Ошибка при получении задач: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> createTask(Map<String, dynamic> data) async {
    try {
      final response = await apiClient.client.post('/tasks', data: data);
      if (response.statusCode == 201) {
        log.info('Задача создана: ${response.data}');
      }
      else {
        log.warning('Задача не создана: ${response.data}');
      }
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      log.severe('Ошибка при создании задачи: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> putTask(int id, Map<String, dynamic> data) async {
    try {
      final response = await apiClient.client.put('/tasks/$id', data: data);
      if (response.statusCode == 200) {
        log.info('Задача обновлена: ${response.data}');
      }
      else {
        log.warning('Задача не обновлена: ${response.data}');
      }
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      log.severe('Ошибка при обновлении задачи: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> patchTask(int id, Map<String, dynamic> data) async {
    try {
      final response = await apiClient.client.patch(
        '/tasks/$id',
        data: data
      );
      if (response.statusCode == 200) {
        log.info('Задача частично обновлена: ${response.data}');  
      }
      else {
        log.warning('Задача частично не обновлена: ${response.data}');
      }
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      log.severe('Ошибка при частичном обновлении задачи: $e');
      rethrow;
    }
  }

  Future<bool> deleteTask(int id) async {
    try {
      final response = await apiClient.client.delete('/tasks/$id');
      if (response.statusCode == 204) {
        log.info('Задача удалена: ${response.data}');
        return true;
      }
      else {
        log.warning('Задача не удалена: ${response.data}');
        return false;
      }
    } catch (e) {
      log.severe('Ошибка при удалении задачи: $e');
      rethrow;
    }
  }

}
