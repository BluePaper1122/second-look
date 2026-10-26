"""Public error contract. Messages describe recovery without exposing internals."""
class AppError(ValueError):
    def __init__(self, code, message, status=400, retryable=False):
        super().__init__(message)
        self.code, self.status, self.retryable = code, status, retryable


def error_payload(error, request_id):
    return {'error': str(error), 'code': error.code, 'retryable': error.retryable, 'request_id': request_id}
