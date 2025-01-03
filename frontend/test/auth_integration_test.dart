import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/api/api_client.dart';
import 'package:frontend/api/auth_api.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:logging/logging.dart';

void _setupLogging() {
  Logger.root.level = Level.ALL; // Установите уровень логирования
  Logger.root.onRecord.listen((LogRecord record) {
    debugPrint('${record.level.name}: ${record.time}: ${record.message}');
  });
}

void main() {
  _setupLogging();
  late ApiClient apiClient;
  late AuthApi authApi;

  setUp(() {
    // Настройка реального клиента
    apiClient = ApiClient(baseUrl: 'http://127.0.0.1:8000');
    authApi = AuthApi(apiClient);

    // Очистка SharedPreferences перед каждым тестом
    SharedPreferences.setMockInitialValues({});
  });

  test('Успешный логин сохраняет токены', () async {
    // Выполняем реальный запрос к вашему API
    await authApi.login('testuser', 'password123');

    final prefs = await SharedPreferences.getInstance();
    final accessToken = prefs.getString('access_token');
    final refreshToken = prefs.getString('refresh_token');

    expect(accessToken, isNotNull, reason: 'Access token должен быть сохранён');
    expect(refreshToken, isNotNull, reason: 'Refresh token должен быть сохранён');

    log.info('Access Token: $accessToken');
    log.info('Refresh Token: $refreshToken');
  });

  test('Логин с неверными данными возвращает ошибку', () async {
    // Проверяем, что неверный логин вызывает исключение
    expect(
      () async => await authApi.login('testuser', 'wrongpassword'),
      throwsException,
    );
  });

  test('Успешный логин сохраняет токены и вызывает refresh', () async {
    // Выполняем реальный запрос к вашему API
    await authApi.login('testuser', 'password123');

    final prefs = await SharedPreferences.getInstance();
    final accessTokenOld = prefs.getString('access_token');
    final refreshTokenOld = prefs.getString('refresh_token');

    expect(accessTokenOld, isNotNull, reason: 'Access token должен быть сохранён');
    expect(refreshTokenOld, isNotNull, reason: 'Refresh token должен быть сохранён');

    log.info('Access Token: $accessTokenOld');
    log.info('Refresh Token: $refreshTokenOld');

    await apiClient.refreshAccessToken();

    final accessToken = prefs.getString('access_token');
    final refreshToken = prefs.getString('refresh_token');

    expect(accessToken, isNotNull, reason: 'Access token должен быть сохранён');
    expect(refreshToken, isNotNull, reason: 'Refresh token должен быть сохранён');

    log.info('Access Token: $accessToken');
    log.info('Refresh Token: $refreshToken');
  });
}
