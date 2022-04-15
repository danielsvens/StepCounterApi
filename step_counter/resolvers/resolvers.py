from ariadne import QueryType, MutationType
from step_counter.application.step_counter_service import StepCounterService

query = QueryType()
mutation = MutationType()
step_counter_service = StepCounterService()


@query.field("listAllSteps")
def list_rows(*_):
    return step_counter_service.get_steps()


@mutation.field("createSteps")
def save_row(_, info, input):
    print(f'incoming request: {input}')
    step_counter_service.validate_input(input)
    
    return step_counter_service.save_steps(input)
