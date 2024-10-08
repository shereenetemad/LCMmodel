class Scheduler:
    
    def __init__(self):
        pass
        
    def get_snapshot(self) -> dict[int, tuple[tuple[float,float],str]]:
        pass

    def generate_event(self) -> None:
        pass
    
    def handle_event(self, event: tuple[int, str, float]) -> None:
        pass

        