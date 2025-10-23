# Patrones de diseño reutilizables
class Singleton:
    _instances = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls)
        return cls._instances[cls]

class Observable:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        self._observers.remove(observer)
    
    def notify_observers(self, message):
        for observer in self._observers:
            observer.update(message)