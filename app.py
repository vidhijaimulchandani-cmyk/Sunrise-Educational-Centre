
try:
    from notifications_routes import notifications_bp
    app.register_blueprint(notifications_bp)
except Exception as _e:
    pass

try:
    from batch_routes import batch_bp
    app.register_blueprint(batch_bp)
except Exception as _e:
    pass