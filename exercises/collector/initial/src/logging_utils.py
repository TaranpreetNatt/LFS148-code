from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import ConsoleLogExporter, SimpleLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

logger_provider = LoggerProvider(
    resource=Resource.create(
        {
            "service.name": "example-app",
        }
    ),
)

logger_provider.add_log_record_processor(
    SimpleLogRecordProcessor(exporter=OTLPLogExporter(insecure=True))
)
handler = LoggingHandler(logger_provider=logger_provider)
