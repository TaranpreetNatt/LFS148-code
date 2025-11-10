from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from resource_utils import create_resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def create_tracing_pipeline() -> BatchSpanProcessor:
    exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    return span_processor


def create_tracer(name: str, version: str) -> trace.Tracer:
    rc = create_resource(name, version)
    processor = create_tracing_pipeline()
    provider = TracerProvider(resource=rc)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(name, version)
    return tracer

