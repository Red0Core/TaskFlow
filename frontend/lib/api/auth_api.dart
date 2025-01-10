import 'package:dio/dio.dart';
import 'api_client.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthenticationException implements Exception {
  final String message;
  AuthenticationException(this.message);

  @override
  String toString() => 'AuthenticationException: $message';
}

class ServerException implements Exception {
  final String message;
  ServerException(this.message);

  @override
  String toString() => 'ServerException: $message';
}

class UnknownException implements Exception {
  final String message;
  UnknownException(this.message);

  @override
  String toString() => 'UnknownException: $message';
}

class AuthApi {
  final ApiClient apiClient;

  AuthApi(this.apiClient);

  Future<void> register(String username, String password) async {
    try {
      final response = await apiClient.client.post('/auth/register', data: {
        'username': username,
        'password': password,
      });
      if (response.data['username'] == username) {
        log.info("Успешная регистрация!");
      }
    } catch (e) {
      log.warning('Ошибка при входе: $e');
      if (e is DioException) {
        throw Exception('Ошибка сервера: ${e.response?.data}');
      }
    }
  }

  Future<void> login(String username, String password) async {
    try {
      final formData = FormData.fromMap({
        'username': username,
        'password': password,
        'grant_type': "password"
      });
      final response = await apiClient.client.post(
        '/token',
        data: formData
      );
      final accessToken = response.data['access_token'];
      apiClient.addToken(accessToken);
      log.info('Успешный вход!');

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('refresh_token', response.data['refresh_token']);
      await prefs.setString('access_token', response.data['access_token']);
      log.info('Refresh token сохранен');
    } on DioException catch (e) {
        log.warning('Ошибка при входе: $e');
        if (e.response?.statusCode == 401) {
          throw AuthenticationException('Неверные учетные данные');
        }
        throw ServerException(
            'Ошибка сервера: ${e.response?.data ?? 'Неизвестная ошибка'}');
    } catch (e) {
      throw UnknownException('Неизвестная ошибка: $e');
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    try {
      await apiClient.client.post('/auth/logout', data: {
        'refresh_token': prefs.get("refresh_token")
      });
    } catch (e) {
      log.warning('Ошибка при выходе: $e');
    }
    await prefs.remove('refresh_token');
    apiClient.removeToken();
    log.info('Пользователь вышел');
  }

}
