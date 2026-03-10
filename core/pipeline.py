class ExecutionPipeline:

    def __init__(self, engine):
        self._engine = engine

    def execute(self, job):
        self._engine.process(job)
