from datetime import datetime
from step_counter.edMQ_client.event import EdMQEvent
from step_counter.edMQ_client import edm_queue

from step_counter.model.models import StepCounter, StepCounterSchema

class StepCounterService:

    def __init__(self) -> None:
        self.step_schema = StepCounterSchema()

    def get_steps(self):
        steps = self._get_all()
        self.sort_data_by_date(steps)
        return steps

    def save_steps(self, step):
        step = StepCounter(step)
        step.save()

        steps = self.step_schema.dump(step)
        self.publish(steps)

        return steps

    @EdMQEvent(exchange='e.default', routing_key='testKey')
    def publish(self, data):
        return data

    def sort_data_by_date(self, data):
        data.sort(key=lambda step: (datetime.strptime(step['date'], '%d-%m-%Y'), step['name']))

    def _get_all(self):
        steps =  StepCounter.get_all()
        print(list(edm_queue))
        return [self.step_schema.dump(step) for step in steps]

    def validate_input(self, step: dict):
        assert step.get('name') is not None, 'Name must be set'
        assert step.get('date') is not None, 'Date must be set'
        assert step.get('steps') is not None, 'Steps must be set'
