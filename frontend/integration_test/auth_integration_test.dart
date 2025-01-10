import 'package:flutter/foundation.dart';
import 'package:frontend/api/api_client.dart';
import 'package:frontend/api/auth_api.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:logging/logging.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

void _setupLogging() {
  Logger.root.level = Level.ALL; // Установите уровень логирования
  Logger.root.onRecord.listen((LogRecord record) {
    debugPrint('${record.level.name}: ${record.time}: ${record.message}');
  });
}

void main() async {
  _setupLogging();
  late ApiClient apiClient;
  late AuthApi authApi;

  final prefs = SharedPreferencesAsync();

  group("Auth integration tests", () {
    setUp(() async {
      // Настройка реального клиента
      apiClient = ApiClient(baseUrl: 'http://127.0.0.1:8000/api', prefs);
      authApi = AuthApi(apiClient);
      // Аутентификация пользователя
      try {
        await authApi.login('testuser', 'password123');
      } on AuthenticationException {
        await authApi.register('testuser', 'password123');
      }
    });

    test('Успешный логин сохраняет токены', () async {
      // Аутентификация пользователя
      await authApi.login('testuser', 'password123');

      final accessToken = await prefs.getString('access_token');
      final refreshToken = await prefs.getString('refresh_token');

      expect(accessToken, contains("ey"), reason: 'Access token должен быть сохранён');
      expect(refreshToken, contains("ey"), reason: 'Refresh token должен быть сохранён');

      log.info('Access Token: $accessToken');
      log.info('Refresh Token: $refreshToken');

      await authApi.logout();
    });

    test('Логин с неверными данными возвращает ошибку', () async {
      // Проверяем, что неверный логин вызывает исключение
      expect(
        () async => await authApi.login('testuser', 'wrongpassword'),
        throwsException,
      );

      await authApi.logout();
    });

    test('Успешный логин сохраняет токены и вызывает refresh', () async {
      final accessTokenOld = await prefs.getString('access_token');
      final refreshTokenOld = await prefs.getString('refresh_token');

      expect(accessTokenOld, contains("ey"), reason: 'Access token должен быть сохранён');
      expect(refreshTokenOld, contains("ey"), reason: 'Refresh token должен быть сохранён');

      log.info('Access Token: $accessTokenOld');
      log.info('Refresh Token: $refreshTokenOld');

      await Future.delayed(const Duration(seconds: 2), apiClient.refreshAccessToken);

      final accessToken = await prefs.getString('access_token');
      final refreshToken = await prefs.getString('refresh_token');

      expect(accessToken, contains("ey"), reason: 'Access token должен быть сохранён');
      expect(refreshToken, contains("ey"), reason: 'Refresh token должен быть сохранён');
      expect(accessToken != accessTokenOld, isTrue, reason: 'Access token должен был поменяться');

      log.info('Access Token: $accessToken');
      log.info('Refresh Token: $refreshToken');

      await authApi.logout();
    });
  });
}
