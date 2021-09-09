from opentracing_utils import trace_sqlalchemy, OPENTRACING_JAEGER, init_opentracing_tracer
import opentracing

def operation_name(conn, cursor, statement, parameters, context, executemany):
    if statement.lower().split(' ')[0] == 'select':
        return statement.lower().split('from ')[1].split(' ')[0]
    else:
        return statement.split(' ')[0].lower()

def enrich_span(span, conn, cursor, statement, parameters, context, executemany):
    span.set_tag('parameters', parameters)

def parent_span(conn, cursor, statement, parameters, context, executemany):
    span = opentracing.tracer.start_active_span(operation_name='parent_span').span
    return span

def start_tracing():
    init_opentracing_tracer(OPENTRACING_JAEGER, service_name='imdb-server')

    trace_sqlalchemy(operation_name=operation_name,
                     enrich_span=enrich_span,
                     span_extractor=parent_span)
