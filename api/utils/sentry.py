import logging
import os

import sentry_sdk

# from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

from app.libs.config import settings

ignore_logger('uvicorn.error')
sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)
sentry_sdk.init(
    environment=os.getenv('LAIN_CLUSTER', 'test'),
    dsn=settings.SENTRY_DSN,
    ignore_errors=[KeyboardInterrupt],
    integrations=[
        sentry_logging,
        # RedisIntegration(),
        ExcepthookIntegration(always_run=True),
    ],
    release=os.getenv('LAIN_META', '').split('-')[-1] or None,
    traces_sample_rate=settings.SENTRY_APM_SAMPLE_RATE,
    send_default_pii=True,
)
