class ICompressionEngine:
    def process(self, job):
        raise NotImplementedError("Engine must implement process(job)")
