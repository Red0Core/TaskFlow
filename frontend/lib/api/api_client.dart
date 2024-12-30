import 'package:dio/dio.dart';
import 'package:logging/logging.dart';
import 'package:shared_preferences/shared_preferences.dart';

final log = Logger("ApiClient");

class ApiClient {
  final Dio _dio;
  
  ApiClient({String baseUrl = "http://localhost:8000"})
      : _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: Duration(seconds: 5),
          receiveTimeout: Duration(seconds: 3),
        )) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // Логика перед отправкой запроса
        log.info('Запрос: ${options.method} ${options.path}');
        return handler.next(options);
      },
      onError: (error, handler) async {
        // Логика обработки ошибок
        if (error.response?.statusCode == 401) {
          log.warning('Токен истёк. идет процесс обновления...');
          final success = await refreshAccessToken();
          if (success) {
            final retryResponse = await _dio.request(
              error.requestOptions.path,
              options: Options(
                method: error.requestOptions.method,
                headers: error.requestOptions.headers,
              ),
              data: error.requestOptions.data,
              queryParameters: error.requestOptions.queryParameters,
            );
            return handler.resolve(retryResponse);
          }
        }
        return handler.next(error);
      },
      onResponse: (response, handler) {
        // Логика обработки ответа
        log.fine('Ответ: ${response.statusCode}');
        return handler.next(response);
      },
    ));
  }

  Dio get client => _dio;

  void addToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
    log.info('Access token установлен');
  }

  void removeToken() {
    _dio.options.headers.remove('Authorization');
    log.info('Access token очищен');
  }

  Future<bool> refreshAccessToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final refreshToken = prefs.getString('refresh_token');
      if (refreshToken == null) {
        log.severe('Refresh token отсутствует');
        return false;
      }

      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      final String newAccessToken = response.data['access_token'];
      addToken(newAccessToken);
      await prefs.setString('access_token', newAccessToken);
      log.info('Access token успешно обновлён');
      return true;
    } catch (e) {
      log.severe('Ошибка обновления access_token: $e');
      return false;
    }
  }
}
